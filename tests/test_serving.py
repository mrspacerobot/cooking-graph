"""The serving section: for each recipe, which facts it is not free of as written, so a server only intersects."""

import itertools
import unittest

from tests.test_queries import kitchen
from tools import queries, serving

MILK, GLUTEN, DAIRY_FREE_OIL_FACTS = "fact/dairy", "fact/gluten", "fact/dairy"


class ServingTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()
        self.recipe_id = "recipe/buttered-onions"

    def section(self):
        return serving.serving_of(self.things)

    def test_a_recipe_is_unsafe_for_the_facts_one_of_its_required_foods_holds(self):
        entry = self.section()["recipes"][self.recipe_id]
        self.assertIn("fact/dairy", entry["unsafe_for"])

    def test_a_fact_the_recipe_is_free_of_is_not_listed(self):
        for thing in self.things.values():
            if thing.kind == "ingredient":
                thing.data["safety"]["free_of"] = ["fact/dairy", "fact/gluten"]
                thing.data["safety"]["contains"] = []
        entry = self.section()["recipes"][self.recipe_id]
        self.assertEqual([], entry["unsafe_for"])

    def test_a_food_with_no_answer_for_a_fact_makes_the_recipe_unsafe_for_it(self):
        self.things["ingredient/butter"].data["safety"]["free_of"] = []
        self.things["ingredient/butter"].data["safety"]["contains"] = []
        self.assertIn("fact/gluten", self.section()["recipes"][self.recipe_id]["unsafe_for"])

    def test_an_optional_part_is_reported_apart_and_does_not_make_the_recipe_unsafe(self):
        dish = self.things["dish/buttered-onions"].data
        dish["parts"][0]["optional"] = True
        entry = self.section()["recipes"][self.recipe_id]
        self.assertEqual("onion", entry["optional_parts"][0]["part"])

    def test_the_section_agrees_with_the_reference_for_every_set_of_avoided_facts(self):
        section = self.section()
        facts = section["facts"]
        for size in range(0, 3):
            for avoided in itertools.combinations(facts, size):
                reference = queries.as_written(self.things, self.recipe_id, list(avoided))
                entry = section["recipes"][self.recipe_id]
                offered = not set(avoided) & set(entry["unsafe_for"])
                self.assertEqual(reference["status"] == "ok", offered, avoided)

    def test_the_section_is_the_same_for_any_file_order(self):
        reversed_things = dict(reversed(list(self.things.items())))
        self.assertEqual(self.section(), serving.serving_of(reversed_things))

    def test_it_lists_the_techniques_ingredients_and_equipment_of_the_recipe(self):
        entry = self.section()["recipes"][self.recipe_id]
        self.assertEqual(["technique/sweat"], entry["techniques"])
        self.assertEqual(["ingredient/butter", "ingredient/onion"], entry["ingredients"])


if __name__ == "__main__":
    unittest.main()


class VectorsTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()

    def cases(self):
        return serving.vectors_of(self.things)["cases"]

    def test_the_cases_cover_nothing_avoided_each_fact_each_neighbouring_pair_and_everything(self):
        facts = serving.facts_in(self.things)
        avoids = [case["avoid"] for case in self.cases()]
        self.assertIn([], avoids)
        self.assertIn(facts, avoids)
        for fact in facts:
            self.assertIn([fact], avoids)
        for first, second in zip(facts, facts[1:]):
            self.assertIn([first, second], avoids)

    def test_each_case_lists_what_the_reference_offers_and_nothing_else(self):
        for case in self.cases():
            offered = [recipe for recipe in ("recipe/buttered-onions",)
                       if queries.as_written(self.things, recipe, case["avoid"])["status"] == "ok"]
            self.assertEqual(offered, case["offered"], case["avoid"])

    def test_the_vectors_are_the_same_for_any_file_order(self):
        reversed_things = dict(reversed(list(self.things.items())))
        self.assertEqual(serving.vectors_of(self.things), serving.vectors_of(reversed_things))
