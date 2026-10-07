"""The safety probe runner: what a dish holds, worked out from its recipe, against what a probe says."""

import unittest

from tests.small_kitchen import SmallKitchen
from tools import check, safety_probes

BUTTERED = "probes/safety-probe/buttered-onions.json"
RECIPE = "graph/recipe/buttered-onions.json"
BUTTER = "graph/ingredient/butter.json"


class SafetyProbeTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def run_probes(self):
        things, issues = check.read_repository(self.kitchen.root)
        self.assertEqual([], issues)
        return safety_probes.run(things)

    def answer(self, path):
        probe_id = self.kitchen.files[path]["id"]
        result = self.run_probes()
        return [one for one in result.growing + result.held_back if one.probe_id == probe_id][0]

    def other_growing(self):
        for path, content in sorted(self.kitchen.files.items()):
            if path.startswith("probes/safety-probe/") and path != BUTTERED and content["set"] == "growing":
                return path
        raise AssertionError("no other growing safety probe")

    def held_back(self):
        for path, content in sorted(self.kitchen.files.items()):
            if path.startswith("probes/safety-probe/") and content["set"] == "held-back":
                return path
        raise AssertionError("no held-back safety probe")


class WhatADishHolds(SafetyProbeTest):
    def test_a_dish_holds_what_the_ingredients_of_its_recipe_hold(self):
        answer = self.answer(BUTTERED)
        self.assertEqual("agrees", answer.verdict)
        self.assertEqual(["fact/dairy"], sorted(answer.graph_holds))

    def test_a_preparation_on_a_line_brings_what_its_parts_hold(self):
        def use_a_roux(recipe):
            recipe["ingredients"][1]["thing"] = "preparation/roux"
            recipe["steps"][0]["with"] = ["preparation/roux"]

        self.kitchen.change(RECIPE, use_a_roux)
        self.assertEqual(["fact/dairy", "fact/gluten"], sorted(self.answer(BUTTERED).graph_holds))

    def test_each_fact_names_the_ingredient_it_comes_from_and_whether_it_is_certain(self):
        self.kitchen.change(BUTTER, lambda thing: thing["safety"]["contains"][0].update(certain=False))
        answer = self.answer(BUTTERED)
        self.assertEqual([("ingredient/butter", "It is made of it.", False)], answer.graph_holds["fact/dairy"])


class Verdicts(SafetyProbeTest):
    def test_a_dish_that_is_not_in_the_graph_is_not_answerable_and_not_wrong(self):
        answer = self.answer(self.other_growing())
        self.assertEqual("not answerable", answer.verdict)
        self.assertEqual([], answer.disagreements)

    def test_a_probe_that_says_the_dish_holds_what_the_graph_says_it_does_not(self):
        self.kitchen.change(BUTTERED, lambda probe: probe.update(holds=["milk", "gluten"], does_not_hold=[]))
        answer = self.answer(BUTTERED)
        self.assertEqual("disagrees", answer.verdict)
        self.assertEqual([("the probe says it holds", "gluten", "fact/gluten")], answer.disagreements)

    def test_a_probe_that_says_the_dish_does_not_hold_what_the_graph_says_it_does(self):
        self.kitchen.change(BUTTERED, lambda probe: probe.update(holds=[], does_not_hold=["milk"]))
        answer = self.answer(BUTTERED)
        self.assertEqual("disagrees", answer.verdict)
        self.assertEqual([("the probe says it does not hold", "milk", "fact/dairy")], answer.disagreements)

    def test_a_word_that_names_no_fact_is_set_apart(self):
        self.kitchen.change(BUTTERED, lambda probe: probe.update(holds=["milk", "onions"]))
        answer = self.answer(BUTTERED)
        self.assertEqual(["onions"], answer.unknown_words)
        self.assertEqual("agrees", answer.verdict)

    def test_a_fact_the_probe_does_not_mention_is_no_disagreement(self):
        self.kitchen.change(BUTTERED, lambda probe: probe.update(holds=[], does_not_hold=["gluten"]))
        self.assertEqual("agrees", self.answer(BUTTERED).verdict)


class Reporting(SafetyProbeTest):
    def test_the_counts_are_given_for_each_set(self):
        counts = safety_probes.counts(self.run_probes())
        self.assertEqual({"probes": 4, "answerable": 1, "agreeing": 1, "disagreeing": 0}, counts["growing"])
        self.assertEqual({"probes": 1, "answerable": 0, "agreeing": 0, "disagreeing": 0}, counts["held-back"])

    def test_a_disagreement_is_written_with_both_sides(self):
        self.kitchen.change(BUTTERED, lambda probe: probe.update(holds=[], does_not_hold=["milk"]))
        document = safety_probes.disagreements_document(self.run_probes())
        self.assertIn("Buttered onions", document)
        self.assertIn("It is made with butter and no flour.", document)
        self.assertIn("ingredient/butter", document)
        self.assertIn("the probe says it does not hold", document)

    def test_a_held_back_probe_is_counted_and_never_shown(self):
        path = self.held_back()
        dish = self.kitchen.files[path]["dish"]
        self.kitchen.change(path, lambda probe: probe.update(dish="Buttered onions", holds=[], does_not_hold=["milk"], why="A secret reason."))
        self.kitchen.change(BUTTERED, lambda probe: probe.update(dish="Onions in butter"))
        result = self.run_probes()
        self.assertEqual(1, safety_probes.counts(result)["held-back"]["disagreeing"])
        document = safety_probes.disagreements_document(result)
        self.assertNotIn("A secret reason.", document)
        self.assertNotIn(dish, document)


if __name__ == "__main__":
    unittest.main()
