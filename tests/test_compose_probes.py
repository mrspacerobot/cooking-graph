"""Compose probes: several techniques and a pantry, and the dishes a good cook would make. Held-back ones stay secret."""

import unittest

from tests.small_kitchen import SmallKitchen
from tests.test_queries import kitchen
from tests.test_question_probes import add
from tools import check, numbers, probes, question_probes
from tools.reading import Thing


def compose_probe(set_name="growing", slug="onions", **more):
    data = {"id": "compose-probe/" + slug, "tier": "drafted", "batch": "compose-1", "set": set_name,
            "written_by": "another-model", "techniques": ["Sweat", "Mince"], "at_home": ["Onion", "Butter"],
            "dishes": ["Buttered onions"], "why": "A cook sweats onions in butter after mincing them."}
    data.update(more)
    return data


class ComposeProbeTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()
        recipe = self.things["recipe/buttered-onions"].data
        recipe["steps"].append(dict(recipe["steps"][0], technique="technique/mince", **{"with": []}))

    def answer(self, probe=None):
        return question_probes.answer_compose(probe or compose_probe(), self.things)

    def test_a_dish_that_covers_every_technique_with_nothing_missing_answers(self):
        self.assertEqual("answered", self.answer()["status"])

    def test_a_missing_required_part_does_not_answer(self):
        self.assertEqual("not-answerable", self.answer(compose_probe(at_home=["Onion"]))["status"])

    def test_a_recipe_that_leaves_a_requested_technique_out_does_not_answer(self):
        self.things["recipe/buttered-onions"].data["steps"].pop()
        self.assertEqual("not-answerable", self.answer()["status"])

    def test_a_stand_in_at_home_fills_a_part(self):
        self.assertEqual("answered", self.answer(compose_probe(at_home=["Onion", "Oil"]))["status"])

    def test_every_expected_dish_must_be_made(self):
        self.assertEqual("not-answerable", self.answer(compose_probe(dishes=["Buttered onions", "Onion tart"]))["status"])

    def test_unknown_words_do_not_answer_and_say_why(self):
        for probe in (compose_probe(techniques=["Future technique"]), compose_probe(at_home=["Future food"])):
            answer = self.answer(probe)
            self.assertEqual("not-answerable", answer["status"])
            self.assertTrue(answer["gaps"])

    def test_the_best_five_are_not_the_only_ones_that_count(self):
        # An expected dish made by a lower-ranked recipe still answers: the probe asks whether the graph can make it.
        for index in range(7):
            other = Thing("", "recipe", dict(self.things["recipe/buttered-onions"].data, id="recipe/a-%d" % index,
                                                makes="dish/buttered-onions"))
            self.things[other.data["id"]] = other
        self.assertEqual("answered", self.answer()["status"])

    def test_the_report_counts_compose_probes_and_never_lists_a_held_back_one(self):
        held = compose_probe("held-back", slug="hidden-sentinel", why="Hidden rationale sentinel")
        add(self.things, held)
        add(self.things, compose_probe())
        report = question_probes.report(question_probes.run(self.things))
        self.assertNotIn("sentinel", report)
        self.assertIn("compose-probe", report)
        self.assertEqual((1, 1), numbers.count(self.things)["question_probes"]["compose-probe"]["growing"])
        self.assertEqual((1, 1), numbers.count(self.things)["question_probes"]["compose-probe"]["held-back"])


class ComposeProbeSchemaTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)
        self.path = "probes/compose-probe/onions.json"

    def issues(self, data):
        self.kitchen.write(self.path, data)
        return {issue.rule for issue in check.check_repository(self.kitchen.root) if issue.path == self.path}

    def test_a_valid_compose_probe_is_read_strictly(self):
        self.assertEqual(set(), self.issues(compose_probe()))

    def test_unknown_and_missing_fields_and_an_empty_list_of_techniques_are_rejected(self):
        self.assertIn("unknown-field", self.issues(dict(compose_probe(), technique="Sweat")))
        bad = compose_probe()
        del bad["techniques"]
        self.assertIn("missing-field", self.issues(bad))
        self.assertIn("too-few", self.issues(compose_probe(techniques=[])))
        self.assertIn("too-few", self.issues(compose_probe(dishes=[])))

    def test_the_hash_rule_holds_probes_back_and_a_hand_set_is_refused(self):
        ids = ["compose-probe/case-" + name for name in ("a", "b", "c", "d", "e")]
        held = probes.held_back_ids(ids)
        for probe_id in ids:
            self.kitchen.write("probes/%s.json" % probe_id, compose_probe("held-back" if probe_id in held else "growing",
                                                                         slug=probe_id.split("/")[1], at_home=[probe_id]))
        self.assertNotIn("held-back-rule", {issue.rule for issue in check.check_repository(self.kitchen.root)})
        first = sorted(held)[0]
        self.kitchen.write("probes/%s.json" % first, compose_probe("growing", slug=first.split("/")[1], at_home=[first]))
        self.assertIn("held-back-rule", {issue.rule for issue in check.check_repository(self.kitchen.root)})

    def test_the_same_question_twice_in_a_batch_is_rejected(self):
        self.kitchen.write(self.path, compose_probe())
        self.path = "probes/compose-probe/again.json"
        self.assertIn("same-question-twice", self.issues(compose_probe(slug="again")))

    def test_the_order_of_the_techniques_and_the_pantry_do_not_make_a_new_question(self):
        self.kitchen.write(self.path, compose_probe())
        self.path = "probes/compose-probe/again.json"
        again = compose_probe(slug="again", techniques=["Mince", "sweat"], at_home=["butter", "ONION"])
        self.assertIn("same-question-twice", self.issues(again))


if __name__ == "__main__":
    unittest.main()
