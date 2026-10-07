"""Question probes measure explicit answers and never reveal the held-back cases."""

import copy
import unittest

from tests.small_kitchen import SmallKitchen
from tests.test_queries import kitchen
from tools import check, numbers, probes, question_probes
from tools.reading import Thing


def stand_probe(slug="oil", verdict="works-with-caveat", set_name="growing"):
    return {"id": "stand-in-probe/" + slug, "tier": "drafted", "batch": "stand-ins-1",
            "set": set_name, "written_by": "another-model", "recipe": "Buttered onions",
            "ingredient": "Butter", "candidate": "Oil", "verdict": verdict,
            "why": "It softens the onion, but the flavour changes."}


def home_probe(set_name="growing"):
    return {"id": "kitchen-probe/onions", "tier": "drafted", "batch": "kitchen-1",
            "set": set_name, "written_by": "another-model", "technique": "Sweat",
            "at_home": ["Onion", "Oil"], "dishes": ["Buttered onions"],
            "why": "The onion and fat are present."}


def add(things, data):
    kind = data["id"].split("/")[0]
    things[data["id"]] = Thing("probes/" + data["id"] + ".json", kind, data)


class QuestionProbeTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()

    def test_positive_needs_a_recorded_stand_in_and_caveat(self):
        self.assertEqual("answered", question_probes.answer_stand_in(stand_probe(), self.things)["status"])
        self.things["ingredient/oil"].data["stands_in_for"] = []
        self.assertEqual("not-answerable", question_probes.answer_stand_in(stand_probe(), self.things)["status"])

    def test_absence_is_not_a_negative_answer(self):
        self.things["ingredient/oil"].data["stands_in_for"] = []
        probe = stand_probe(verdict="does-not-work")
        self.assertEqual("not-answerable", question_probes.answer_stand_in(probe, self.things)["status"])
        self.things["ingredient/oil"].data["stands_in_for"] = [
            {"thing": "ingredient/butter", "when": [], "not_when": ["technique/sweat"],
             "ratio": None, "caveat": "It does not give this result.", "tier": "drafted"}]
        self.assertEqual("answered", question_probes.answer_stand_in(probe, self.things)["status"])

    def test_conflicting_expected_answer_is_a_disagreement(self):
        self.assertEqual("disagrees", question_probes.answer_stand_in(stand_probe(verdict="does-not-work"), self.things)["status"])

    def test_working_probe_accepts_an_offered_choice_with_a_caveat(self):
        self.assertEqual("answered", question_probes.answer_stand_in(stand_probe(verdict="works"), self.things)["status"])
        self.things["ingredient/oil"].data["stands_in_for"][0]["caveat"] = ""
        self.assertEqual("not-answerable", question_probes.answer_stand_in(stand_probe(), self.things)["status"])

    def test_unresolved_recipe_or_original_does_not_answer(self):
        probe = stand_probe()
        probe["recipe"] = "Unknown recipe"
        self.assertEqual("not-answerable", question_probes.answer_stand_in(probe, self.things)["status"])
        probe["recipe"] = "Buttered onions"
        probe["ingredient"] = "Flour"
        self.assertEqual("not-answerable", question_probes.answer_stand_in(probe, self.things)["status"])

    def test_kitchen_probe_checks_recipe_availability_not_only_names(self):
        probe = home_probe()
        self.assertEqual("answered", question_probes.answer_kitchen(probe, self.things)["status"])
        probe["at_home"] = ["Onion"]
        self.assertEqual("not-answerable", question_probes.answer_kitchen(probe, self.things)["status"])
        probe["dishes"] = ["Onion tart"]
        self.assertEqual("not-answerable", question_probes.answer_kitchen(probe, self.things)["status"])

    def test_only_aggregate_counts_of_held_back_cases_are_rendered(self):
        held = stand_probe("hidden-sentinel", set_name="held-back")
        held["why"] = "Hidden rationale sentinel"
        held["candidate"] = "Secret candidate sentinel"
        add(self.things, held)
        add(self.things, home_probe("held-back"))
        report = question_probes.report(question_probes.run(self.things))
        self.assertNotIn("sentinel", report)
        self.assertNotIn("kitchen-probe/onions", report)
        self.assertIn("held-back", report)

    def test_batch_filter_and_file_order_are_deterministic(self):
        add(self.things, stand_probe())
        add(self.things, home_probe())
        first = question_probes.run(self.things, batch="kitchen-1")
        self.assertEqual(0, question_probes.counts(first)["stand-in-probe"]["growing"][1])
        self.assertEqual(first, question_probes.run(dict(reversed(list(self.things.items()))), batch="kitchen-1"))

    def test_numbers_include_part_options_and_each_new_probe_kind(self):
        add(self.things, stand_probe())
        add(self.things, home_probe())
        counts = numbers.count(self.things)
        self.assertEqual((0, 5), counts["parts_with_options"])
        self.assertEqual((1, 1), counts["question_probes"]["stand-in-probe"]["growing"])
        self.assertEqual((1, 1), counts["question_probes"]["kitchen-probe"]["growing"])


class QuestionProbeSchemaTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)
        self.data = stand_probe()
        self.path = "probes/stand-in-probe/oil.json"

    def issues(self, data):
        self.kitchen.write(self.path, data)
        return {issue.rule for issue in check.check_repository(self.kitchen.root) if issue.path == self.path}

    def test_valid_question_probe_is_read_strictly(self):
        self.assertEqual(set(), self.issues(self.data))

    def test_unknown_missing_fields_and_verdicts_are_rejected(self):
        bad = dict(self.data, invented="field")
        self.assertIn("unknown-field", self.issues(bad))
        bad = copy.deepcopy(self.data)
        del bad["written_by"]
        self.assertIn("missing-field", self.issues(bad))
        bad = dict(self.data, verdict="maybe")
        self.assertIn("not-in-stand_in_verdicts", self.issues(bad))

    def test_each_kind_uses_the_hash_rule_and_cannot_be_assigned_by_hand(self):
        for kind in ("stand-in-probe", "kitchen-probe"):
            ids = [kind + "/case-" + name for name in ("a", "b", "c", "d", "e")]
            held = probes.held_back_ids(ids)
            for probe_id in ids:
                data = stand_probe() if kind == "stand-in-probe" else home_probe()
                data["id"] = probe_id
                data["set"] = "held-back" if probe_id in held else "growing"
                if kind == "stand-in-probe":
                    data["candidate"] = probe_id
                else:
                    data["at_home"] = [probe_id]
                self.kitchen.write("probes/" + probe_id + ".json", data)
            probe_id = sorted(held)[0]
            path = "probes/" + probe_id + ".json"
            data["id"] = probe_id
            data["set"] = "growing"
            self.kitchen.write(path, data)
            found = {issue.rule for issue in check.check_repository(self.kitchen.root) if issue.path == path}
            self.assertIn("held-back-rule", found)

    def test_kitchen_requires_nonempty_dishes(self):
        self.path = "probes/kitchen-probe/onions.json"
        self.assertEqual(set(), self.issues(home_probe()))
        self.assertIn("too-few", self.issues(dict(home_probe(), dishes=[])))

    def test_duplicate_question_in_the_same_batch_is_rejected(self):
        self.kitchen.write(self.path, self.data)
        other = dict(self.data, id="stand-in-probe/duplicate")
        self.path = "probes/stand-in-probe/duplicate.json"
        self.assertIn("same-question-twice", self.issues(other))
