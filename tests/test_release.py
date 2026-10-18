"""The release artifact: what goes in, how it is checked, and when a production build is refused."""

import hashlib
import json
import os
import unittest

from tests.small_kitchen import REPOSITORY, SmallKitchen
from tools import check, numbers, release, serving
from tools.reading import Thing

SOURCE = release.Source(commit="1102817abcdef1234567890abcdef1234567890a", date="2026-10-11", built_at="2026-10-11T12:00:00Z")


def thing(kind, data):
    return Thing("graph/%s/x.json" % kind, kind, data)


def passing_things():
    """The least a production build accepts: reviewed things, verified safety, no open point, one live review."""
    return {
        "technique/sear": thing("technique", {"tier": "reviewed"}),
        "ingredient/egg": thing("ingredient", {"tier": "reviewed", "safety": {"state": "verified"}}),
        "recipe/omelette": thing("recipe", {"tier": "reviewed", "steps": [{"safety_points": []}]}),
        "review/one": thing("review", {"supersedes": []}),
    }


class KitchenCase(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)
        self.things, issues = check.read_repository(self.kitchen.root)
        self.assertEqual([], issues)

    def read_out(self, name):
        with open(os.path.join(self.kitchen.root, "out", "release", name), "rb") as handle:
            return handle.read()


class ContentTest(KitchenCase):
    def test_only_files_of_the_graph_are_included(self):
        probes = [thing_id for thing_id, one in self.things.items() if one.path.startswith("probes/")]
        self.assertTrue(probes, "the small kitchen must hold probes for this test to mean anything")
        included = release.artifact_of(self.things)["things"]
        self.assertEqual([], [thing_id for thing_id in probes if thing_id in included])
        self.assertTrue(included)

    def test_every_included_thing_is_a_file_of_the_graph(self):
        included = release.artifact_of(self.things)["things"]
        for thing_id in included:
            self.assertTrue(self.things[thing_id].path.startswith("graph/"), thing_id)

    def test_the_artifact_carries_its_schema_version_and_the_data_unchanged(self):
        artifact = release.artifact_of(self.things)
        self.assertEqual(release.ARTIFACT_SCHEMA_VERSION, artifact["artifactSchemaVersion"])
        self.assertEqual(serving.serving_of(self.things), artifact["serving"])
        for thing_id, data in artifact["things"].items():
            self.assertEqual(self.things[thing_id].data, data)

    def test_the_artifact_carries_its_channel_so_that_its_hash_covers_it(self):
        draft = release.encode(release.artifact_of(self.things, "draft"))
        production = release.encode(release.artifact_of(self.things, "production"))
        self.assertEqual("draft", json.loads(draft)["channel"])
        self.assertEqual("production", json.loads(production)["channel"])
        self.assertNotEqual(hashlib.sha256(draft).hexdigest(), hashlib.sha256(production).hexdigest())

    def test_the_manifest_and_the_artifact_name_the_same_channel(self):
        release.write_release(self.kitchen.root, "draft", SOURCE)
        self.assertEqual(json.loads(self.read_out("manifest.json"))["channel"], json.loads(self.read_out("graph-artifact.json"))["channel"])

    def test_the_same_content_gives_the_same_bytes_in_two_folders(self):
        other = SmallKitchen()
        self.addCleanup(other.close)
        things, _ = check.read_repository(other.root)
        first = release.encode(release.artifact_of(self.things))
        self.assertEqual(first, release.encode(release.artifact_of(things)))

    def test_changing_one_thing_changes_the_hash(self):
        before = release.encode(release.artifact_of(self.things))
        changed = dict(self.things)
        some_id = sorted(release.artifact_of(self.things)["things"])[0]
        old = changed[some_id]
        changed[some_id] = Thing(old.path, old.kind, dict(old.data, tier="reviewed"))
        self.assertNotEqual(before, release.encode(release.artifact_of(changed)))


class ManifestTest(KitchenCase):
    def manifest(self, channel="draft"):
        encoded = release.encode(release.artifact_of(self.things, channel))
        return release.manifest_of(self.things, encoded, channel, SOURCE), encoded

    def test_it_names_the_version_the_commit_the_channel_and_the_hash(self):
        manifest, encoded = self.manifest()
        self.assertEqual(2, manifest["artifactSchemaVersion"])
        self.assertEqual("2026.10.11-1102817", manifest["graphVersion"])
        self.assertEqual(SOURCE.commit, manifest["sourceCommit"])
        self.assertEqual("draft", manifest["channel"])
        self.assertEqual(hashlib.sha256(encoded).hexdigest(), manifest["contentSha256"])
        self.assertEqual("2026-10-11T12:00:00Z", manifest["builtAt"])

    def test_it_counts_what_is_included_by_kind_and_tier(self):
        manifest, _ = self.manifest()
        included = {thing_id: one for thing_id, one in self.things.items() if one.path.startswith("graph/")}
        self.assertEqual(numbers.count_things(included), manifest["counts"]["things"])
        self.assertEqual(numbers.count_safety(included), manifest["counts"]["safety"])

    def test_it_lists_the_facts_the_graph_knows(self):
        manifest, _ = self.manifest()
        facts = sorted(thing_id for thing_id, one in self.things.items() if one.kind == "fact")
        self.assertTrue(facts)
        self.assertEqual(facts, manifest["facts"])

    def test_it_reports_every_gate_and_whether_it_passed(self):
        manifest, _ = self.manifest()
        self.assertEqual([gate.name for gate in release.gates_of(self.things)], [gate["name"] for gate in manifest["gates"]])
        self.assertTrue(all(isinstance(gate["passed"], bool) for gate in manifest["gates"]))


class GatesTest(unittest.TestCase):
    def failing(self, things):
        return [gate.name for gate in release.gates_of(things) if not gate.passed]

    def test_things_that_pass_every_gate_pass(self):
        self.assertEqual([], self.failing(passing_things()))

    def test_a_drafted_thing_fails_the_tier_gate(self):
        things = passing_things()
        things["technique/sear"] = thing("technique", {"tier": "drafted"})
        self.assertEqual([release.GATE_TIERS], self.failing(things))

    def test_drafted_learning_content_on_a_reviewed_technique_fails_the_tier_gate(self):
        for field, value in (("intro", {"tier": "drafted"}), ("quiz", [{"tier": "drafted"}])):
            with self.subTest(field=field):
                things = passing_things()
                things["technique/sear"] = thing("technique", {"tier": "reviewed", field: value})
                self.assertEqual([release.GATE_TIERS], self.failing(things))

    def test_an_unverified_ingredient_fails_the_safety_gate(self):
        things = passing_things()
        things["ingredient/egg"] = thing("ingredient", {"tier": "reviewed", "safety": {"state": "unverified"}})
        self.assertEqual([release.GATE_SAFETY], self.failing(things))

    def test_an_open_safety_point_fails_its_gate(self):
        things = passing_things()
        things["recipe/omelette"] = thing("recipe", {"tier": "reviewed", "steps": [{"safety_points": ["rest"]}]})
        self.assertEqual([release.GATE_SAFETY_POINTS], self.failing(things))

    def test_no_live_review_fails_the_review_gate(self):
        things = passing_things()
        del things["review/one"]
        self.assertEqual([release.GATE_REVIEW], self.failing(things))

    def test_a_review_that_a_later_one_replaces_is_not_live(self):
        things = passing_things()
        things["review/one"] = thing("review", {"supersedes": []})
        things["review/two"] = thing("review", {"supersedes": ["review/one"]})
        self.assertEqual([], self.failing(things))
        things["review/two"] = thing("review", {"supersedes": ["review/one", "review/two"]})
        self.assertEqual([release.GATE_REVIEW], self.failing(things))

    def test_a_thing_without_a_tier_is_history_and_does_not_fail_the_tier_gate(self):
        things = passing_things()
        things["reviewer/owner"] = thing("reviewer", {"kind": "person"})
        self.assertEqual([], self.failing(things))

    def test_the_small_kitchen_fails_every_production_gate_that_it_can(self):
        kitchen = SmallKitchen()
        self.addCleanup(kitchen.close)
        things, _ = check.read_repository(kitchen.root)
        failing = self.failing(things)
        for name in (release.GATE_TIERS, release.GATE_SAFETY, release.GATE_REVIEW):
            self.assertIn(name, failing)


class WriteTest(KitchenCase):
    def out(self):
        return os.path.join(self.kitchen.root, "out", "release")

    def test_a_draft_release_writes_the_artifact_the_manifest_the_vectors_and_the_sums(self):
        release.write_release(self.kitchen.root, "draft", SOURCE)
        self.assertEqual(["SHA256SUMS", "graph-artifact.json", "manifest.json", "serving-vectors.json"],
                         sorted(os.listdir(self.out())))

    def test_the_manifest_hash_matches_the_artifact_file(self):
        release.write_release(self.kitchen.root, "draft", SOURCE)
        manifest = json.loads(self.read_out("manifest.json"))
        self.assertEqual(hashlib.sha256(self.read_out("graph-artifact.json")).hexdigest(), manifest["contentSha256"])

    def test_the_sums_file_checks_the_artifact_the_manifest_and_the_vectors(self):
        release.write_release(self.kitchen.root, "draft", SOURCE)
        for line in self.read_out("SHA256SUMS").decode("utf-8").splitlines():
            digest, name = line.split("  ")
            self.assertEqual(digest, hashlib.sha256(self.read_out(name)).hexdigest(), name)

    def test_the_sums_list_every_file_but_itself(self):
        release.write_release(self.kitchen.root, "draft", SOURCE)
        names = [line.split("  ")[1] for line in self.read_out("SHA256SUMS").decode("utf-8").splitlines()]
        self.assertEqual(["graph-artifact.json", "manifest.json", "serving-vectors.json"], names)

    def test_releasing_twice_gives_the_same_artifact_and_hash(self):
        release.write_release(self.kitchen.root, "draft", SOURCE)
        first = self.read_out("graph-artifact.json")
        release.write_release(self.kitchen.root, "draft", SOURCE)
        self.assertEqual(first, self.read_out("graph-artifact.json"))

    def test_a_production_release_of_this_graph_is_refused_and_names_the_gates(self):
        with self.assertRaises(release.Refused) as refused:
            release.write_release(self.kitchen.root, "production", SOURCE)
        self.assertIn(release.GATE_TIERS, [gate.name for gate in refused.exception.gates])
        self.assertFalse(os.path.exists(self.out()))

    def test_a_graph_with_an_issue_is_not_released(self):
        path = next(path for path in sorted(self.kitchen.files) if path.startswith("graph/"))
        self.kitchen.write_text(path, "{")
        with self.assertRaises(release.Unreadable) as unreadable:
            release.write_release(self.kitchen.root, "draft", SOURCE)
        self.assertTrue(unreadable.exception.issues)
        self.assertFalse(os.path.exists(self.out()))

    def test_an_unknown_channel_is_refused(self):
        with self.assertRaises(ValueError):
            release.write_release(self.kitchen.root, "preview", SOURCE)


class CommandTest(KitchenCase):
    def test_a_draft_release_exits_zero(self):
        self.assertEqual(0, release.main(self.kitchen.root, [], SOURCE))
        self.assertTrue(os.path.exists(os.path.join(self.kitchen.root, "out", "release", "manifest.json")))

    def test_a_production_release_exits_one(self):
        self.assertEqual(1, release.main(self.kitchen.root, ["--channel", "production"], SOURCE))

    def test_a_folder_that_is_no_git_checkout_exits_one(self):
        self.assertEqual(1, release.main(self.kitchen.root, [], None))


class SourceTest(unittest.TestCase):
    def test_the_source_of_this_checkout_names_a_commit_and_a_day(self):
        source = release.source_from_git(REPOSITORY, "2026-10-11T12:00:00Z")
        self.assertRegex(source.commit, r"^[0-9a-f]{40}$")
        self.assertRegex(source.date, r"^\d{4}-\d{2}-\d{2}$")

    def test_a_folder_without_git_has_no_source(self):
        kitchen = SmallKitchen()
        self.addCleanup(kitchen.close)
        self.assertIsNone(release.source_from_git(kitchen.root, "2026-10-11T12:00:00Z"))


if __name__ == "__main__":
    unittest.main()
