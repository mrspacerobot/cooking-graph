"""Compose: several techniques and what is at home in, an adapted recipe out. No model, same input same output."""

import copy
import json
import os
import subprocess
import unittest

from tests.small_kitchen import REPOSITORY
from tests.test_queries import kitchen
from tools import queries
from tools.reading import Thing


class ComposeTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()
        self.recipe = self.things["recipe/buttered-onions"].data
        self.oil = self.things["ingredient/oil"].data["stands_in_for"][0]

    def compose(self, techniques=("sweat",), at_home=("ingredient/onion", "ingredient/oil"), **more):
        return queries.compose(self.things, list(techniques), list(at_home), **more)

    def first(self, **more):
        return self.compose(**more)["recipes"][0]

    def fat(self, **more):
        return self.first(**more)["parts"][1]["lines"][0]

    def add_recipe_with_mince(self):
        both = copy.deepcopy(self.recipe)
        both["id"] = "recipe/z-onions"
        both["steps"].append(dict(both["steps"][0], technique="technique/mince", **{"with": []}))
        self.things[both["id"]] = Thing("", "recipe", both)
        return both

    def test_one_technique_returns_what_kitchen_returns(self):
        ours = [row["recipe"] for row in self.compose()["recipes"]]
        theirs = [row["recipe"] for row in queries.kitchen(self.things, "sweat", ["onion", "oil"])["recipes"]]
        self.assertEqual(theirs, ours)

    def test_a_recipe_covering_every_technique_ranks_before_a_complete_one_that_covers_fewer(self):
        self.add_recipe_with_mince()
        self.recipe["ingredients"] = self.recipe["ingredients"][:1]
        self.recipe["steps"][0]["text"] = "Soften the {onion}."
        answer = self.compose(("sweat", "mince"), ("ingredient/onion",))["recipes"]
        self.assertEqual(["recipe/z-onions", "recipe/buttered-onions"], [row["recipe"] for row in answer])
        self.assertEqual(([], ["technique/mince"]), (answer[0]["uncovered"], answer[1]["uncovered"]))
        self.assertEqual(["technique/mince", "technique/sweat"], answer[0]["covered"])

    def test_covered_and_uncovered_always_make_up_the_request(self):
        self.add_recipe_with_mince()
        for row in self.compose(("mince", "sweat"))["recipes"]:
            self.assertEqual(["technique/mince", "technique/sweat"], sorted(row["covered"] + row["uncovered"]))

    def test_no_recipe_uses_none_of_the_techniques(self):
        self.assertEqual([], self.compose(("mince",))["recipes"])

    def test_stand_in_amount_follows_the_recorded_ratio(self):
        self.oil["ratio"] = {"stand_in": 2, "original": 1, "by": "weight"}
        self.assertEqual({"value": 20, "unit": "gram"}, self.fat()["amount"]["for_home"])
        self.assertEqual({"value": 10, "unit": "gram"}, self.fat()["amount"]["original"])

    def test_a_ratio_for_another_measure_is_not_applied(self):
        self.oil["ratio"] = {"stand_in": 1, "original": 1, "by": "volume"}
        amount = self.fat()["amount"]
        self.assertIsNone(amount["for_home"])
        self.assertIn("ratio", amount["note"])

    def test_no_ratio_means_no_invented_amount(self):
        self.oil["ratio"] = None
        amount = self.fat()["amount"]
        self.assertEqual("stand-in", self.fat()["status"])
        self.assertIsNone(amount["for_home"])
        self.assertIn("No ratio", amount["note"])

    def test_a_pinch_is_not_converted_by_a_measure(self):
        self.recipe["ingredients"][1]["amount"] = {"value": 1, "unit": "pinch"}
        self.assertIsNone(self.fat()["amount"]["for_home"])

    def test_servings_scale_every_amount(self):
        answer = self.first(servings=4)
        self.assertEqual({"from": 2, "to": 4}, answer["servings"])
        self.assertEqual({"value": 2, "unit": "piece"}, answer["parts"][0]["lines"][0]["amount"]["for_home"])
        self.assertEqual({"value": 20, "unit": "gram"}, answer["parts"][1]["lines"][0]["amount"]["original"])

    def test_scaling_and_a_ratio_work_together(self):
        self.oil["ratio"] = {"stand_in": 1, "original": 2, "by": "weight"}
        self.assertEqual({"value": 10, "unit": "gram"}, self.fat(servings=4)["amount"]["for_home"])

    def test_amounts_are_rounded_the_same_way_every_time(self):
        self.recipe["yields"] = {"value": 3, "unit": "serving"}
        self.assertEqual({"value": 6.67, "unit": "gram"}, self.fat(servings=2)["amount"]["original"])
        self.assertEqual({"value": 6.67, "unit": "gram"}, self.fat(servings=2)["amount"]["for_home"])

    def test_servings_leave_a_recipe_that_does_not_yield_in_servings_alone(self):
        self.recipe["yields"] = {"value": 500, "unit": "millilitre"}
        answer = self.first(servings=4)
        self.assertIsNone(answer["servings"])
        self.assertEqual({"value": 10, "unit": "gram"}, answer["parts"][1]["lines"][0]["amount"]["original"])
        self.assertIn("servings", answer["scaling_note"])

    def test_servings_must_be_a_positive_number(self):
        for bad in (0, -2):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                self.compose(servings=bad)

    def test_a_step_says_how_to_read_a_replaced_ingredient(self):
        step = self.first()["steps"][0]
        self.assertEqual([{"original": "ingredient/butter", "instead": "ingredient/oil"}], step["read_as"])
        self.assertEqual("Soften the onion in the oil over low heat.", step["text"])
        self.assertEqual(["cooling-and-keeping"], step["safety_points"])

    def test_a_step_with_nothing_replaced_reads_as_written(self):
        answer = self.first(at_home=("ingredient/onion", "ingredient/butter"))
        self.assertEqual([], answer["steps"][0]["read_as"])
        self.assertEqual("Soften the onion in the butter over low heat.", answer["steps"][0]["text"])

    def test_a_step_of_a_part_left_out_is_dropped_and_its_clause_goes(self):
        self.recipe["steps"][0]["text"] = "Soften the {onion} in the {butter} [garnish: and add the {garnish}]."
        self.recipe["ingredients"].append({"thing": "ingredient/onion-skin", "part": "garnish", "forms": [],
                                           "amount": {"value": 1, "unit": "pinch"}})
        answer = self.first(at_home=("ingredient/onion", "ingredient/butter"), avoid=("milk",))
        self.assertTrue(all("garnish" not in step["text"] for step in answer["steps"]))

    def test_missing_lines_are_listed_and_keep_the_amount_needed(self):
        answer = self.first(at_home=("ingredient/onion",))
        self.assertEqual(1, answer["missing_count"])
        self.assertEqual([{"part": "butter", "original": "ingredient/butter"}], answer["missing"])
        self.assertEqual({"value": 10, "unit": "gram"}, answer["parts"][1]["lines"][0]["amount"]["original"])

    def test_avoid_rejects_an_original_that_holds_the_fact_and_a_stand_in_that_may(self):
        answer = self.first(at_home=("ingredient/onion", "ingredient/butter", "ingredient/oil"), avoid=("milk",))
        self.assertEqual("stand-in", answer["parts"][1]["lines"][0]["status"])
        self.things["ingredient/oil"].data["safety"] = {
            "state": "unverified", "free_of": ["fact/gluten"], "note": None,
            "contains": [{"fact": "fact/dairy", "basis": "Unknown processing.", "certain": False}]}
        home = ("ingredient/onion", "ingredient/butter", "ingredient/oil")
        answer = queries.kitchen(self.things, "sweat", list(home), ["milk"])["recipes"][0]
        self.assertEqual("refused", answer["parts"][1]["lines"][0]["status"])
        self.assertEqual("refused", answer["status"])
        self.assertEqual([], self.compose(at_home=home, avoid=("milk",))["recipes"])

    def test_every_answer_says_the_safety_records_are_unverified(self):
        self.assertIn("unverified", self.compose()["safety"])

    def test_top_limits_the_list_and_keeps_the_best_first(self):
        self.add_recipe_with_mince()
        everything = self.compose(("sweat", "mince"), top=5)["recipes"]
        self.assertEqual(everything[:1], self.compose(("sweat", "mince"), top=1)["recipes"])
        with self.assertRaises(ValueError):
            self.compose(top=0)

    def test_unknown_inputs_are_errors(self):
        with self.assertRaises(ValueError):
            self.compose(("future technique",))
        with self.assertRaises(ValueError):
            self.compose(at_home=("future ingredient",))
        with self.assertRaises(ValueError):
            self.compose(avoid=("future allergen",))
        with self.assertRaises(ValueError):
            queries.compose(self.things, [], [])

    def test_the_same_question_gives_the_same_answer_whatever_the_order(self):
        self.add_recipe_with_mince()
        reversed_things = dict(reversed(list(self.things.items())))
        one = queries.compose(self.things, ["mince", "sweat"], ["oil", "onion"], servings=3)
        two = queries.compose(reversed_things, ["sweat", "mince", "sweat"], ["onion", "oil", "onion"], servings=3)
        self.assertEqual(one, two)

    def test_the_command_is_repeatable_and_rejects_unknown_inputs(self):
        path = os.path.join(REPOSITORY, "compose")
        base = [path, "--technique", "technique/sear", "--technique", "technique/saute",
                "--servings", "4", "ingredient/butter", "ingredient/salt"]
        first = subprocess.run(base, capture_output=True, text=True)
        second = subprocess.run(base, capture_output=True, text=True)
        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        answer = json.loads(first.stdout)
        self.assertIn("unverified", answer["safety"])
        for row in answer["recipes"]:
            self.assertEqual(["technique/saute", "technique/sear"], sorted(row["covered"] + row["uncovered"]))
        bad = subprocess.run([path, "--technique", "unknown"], capture_output=True, text=True)
        self.assertNotEqual(0, bad.returncode)
        self.assertIn("unknown", bad.stderr)
        none = subprocess.run([path, "ingredient/butter"], capture_output=True, text=True)
        self.assertNotEqual(0, none.returncode)


class PluralTest(unittest.TestCase):
    """A cook types lemons and onions. An exact name always wins, and a guess must be unique."""

    def setUp(self):
        self.things = kitchen()

    def resolve(self, word, kinds=("ingredient", "preparation")):
        return queries.resolve(self.things, word, kinds)

    def test_a_plural_reads_as_the_one_thing_it_names(self):
        self.assertEqual("ingredient/onion", self.resolve("onions"))
        self.assertEqual("ingredient/onion", self.resolve("Onions"))

    def test_the_other_plural_endings(self):
        for plural, slug in (("berries", "berry"), ("tomatoes", "tomato"), ("peaches", "peach")):
            food = copy.deepcopy(self.things["ingredient/onion"].data)
            food.update(id="ingredient/" + slug, names={"en": slug.capitalize()}, aliases={})
            self.things[food["id"]] = Thing("", "ingredient", food)
            with self.subTest(plural=plural):
                self.assertEqual("ingredient/" + slug, self.resolve(plural))

    def test_an_exact_name_wins_over_a_plural_reading(self):
        food = copy.deepcopy(self.things["ingredient/butter"].data)
        food.update(id="ingredient/onions-pickled", names={"en": "Onions"}, aliases={})
        self.things[food["id"]] = Thing("", "ingredient", food)
        self.assertEqual("ingredient/onions-pickled", self.resolve("onions"))

    def test_a_plural_that_could_be_two_things_is_an_error(self):
        food = copy.deepcopy(self.things["ingredient/onion"].data)
        food.update(id="ingredient/onion-red", names={"en": "Onion"}, aliases={})
        self.things[food["id"]] = Thing("", "ingredient", food)
        with self.assertRaises(ValueError):
            self.resolve("onions")

    def test_a_word_that_names_nothing_stays_an_error_and_a_short_word_is_not_cut(self):
        with self.assertRaises(ValueError):
            self.resolve("futures")
        food = copy.deepcopy(self.things["ingredient/onion"].data)
        food.update(id="ingredient/ca", names={"en": "Ca"}, aliases={})
        self.things[food["id"]] = Thing("", "ingredient", food)
        with self.assertRaises(ValueError):
            self.resolve("cas")

    def test_compose_takes_a_plural_in_the_pantry(self):
        answer = queries.compose(self.things, ["sweat"], ["onions", "oil"])
        self.assertEqual(["ingredient/oil", "ingredient/onion"], answer["at_home"])


BUTTER_CHICKEN = ["--technique", "technique/marinate-in-yogurt", "--technique", "technique/fry-masala-base",
                  "--technique", "technique/cook-in-masala-gravy"]


class ButterChickenTest(unittest.TestCase):
    """The real graph: a cook with no butter still gets the fat of the masala base."""

    def butter_line(self, at_home, *more):
        run = subprocess.run([os.path.join(REPOSITORY, "compose"), *BUTTER_CHICKEN, *more, *at_home],
                             capture_output=True, text=True, check=True)
        recipe = next(row for row in json.loads(run.stdout)["recipes"] if row["recipe"] == "recipe/butter-chicken")
        return next(line for part in recipe["parts"] for line in part["lines"] if line["original"] == "ingredient/butter")

    def test_ghee_stands_in_for_the_butter_with_its_amount(self):
        line = self.butter_line(["ingredient/ghee"])
        self.assertEqual(("stand-in", "ingredient/ghee"), (line["status"], line["choice"]["thing"]))
        self.assertEqual({"value": 50, "unit": "gram"}, line["amount"]["for_home"])

    def test_oil_stands_in_without_an_invented_amount(self):
        line = self.butter_line(["ingredient/oil"])
        self.assertEqual(("stand-in", "ingredient/oil"), (line["status"], line["choice"]["thing"]))
        self.assertIsNone(line["amount"]["for_home"])
        self.assertIn("No ratio", line["amount"]["note"])

    def test_avoiding_milk_refuses_ghee_and_keeps_oil(self):
        """Asked of the stand-ins, not of compose: the yoghurt has no safe alternative, so compose refuses the whole dish."""
        run = subprocess.run([os.path.join(REPOSITORY, "stand-ins"), "recipe/butter-chicken", "--avoid", "fact/milk"],
                             capture_output=True, text=True, check=True)
        line = next(row for row in json.loads(run.stdout)["lines"] if row["original"] == "ingredient/butter")
        self.assertEqual(["ingredient/oil"], [one["thing"] for one in line["options"]])
        self.assertIn("ingredient/ghee", [one["thing"] for one in line["excluded"]])

    def test_avoiding_milk_refuses_the_whole_butter_chicken_because_the_yoghurt_has_no_safe_alternative(self):
        run = subprocess.run([os.path.join(REPOSITORY, "compose"), *BUTTER_CHICKEN, "--avoid", "fact/milk",
                              "ingredient/ghee", "ingredient/oil"], capture_output=True, text=True, check=True)
        answer = json.loads(run.stdout)
        self.assertNotIn("recipe/butter-chicken", [row["recipe"] for row in answer["recipes"]])
        self.assertIn("recipe/butter-chicken", answer["refused"])

    def test_with_neither_the_butter_is_missing(self):
        self.assertEqual("missing", self.butter_line(["ingredient/cream"])["status"])


if __name__ == "__main__":
    unittest.main()
