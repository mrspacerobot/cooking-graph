"""The serving section: for each recipe, which facts it is not free of as written, so a server only intersects."""

import itertools
import unittest

from tests.small_kitchen import REPOSITORY
from tests.test_queries import kitchen
from tools import check, queries, release, serving

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
                reference = queries.can_make(self.things, self.recipe_id, list(avoided))
                offered = serving.offered(section["recipes"][self.recipe_id], set(avoided))
                self.assertEqual(reference["status"] == "ok", offered, avoided)

    def line(self, thing_id):
        lines = self.section()["recipes"][self.recipe_id]["lines"]
        return next(one for one in lines if one["thing"] == thing_id)

    def test_a_line_lists_the_swaps_the_graph_allows_with_what_each_is_unsafe_for(self):
        swap = self.line("ingredient/butter")["swaps"][0]
        self.assertEqual("ingredient/oil", swap["thing"])
        self.assertEqual("The flavour changes.", swap["caveat"])
        self.assertEqual({"stand_in": 1, "original": 1, "by": "weight"}, swap["ratio"])
        self.assertNotIn("fact/dairy", swap["unsafe_for"])

    def test_a_recipe_is_offered_to_a_cook_who_avoids_a_fact_when_a_safe_swap_exists(self):
        entry = self.section()["recipes"][self.recipe_id]
        self.assertIn("fact/dairy", entry["unsafe_for"])
        self.assertTrue(serving.offered(entry, {"fact/dairy"}))

    def test_a_recipe_is_refused_when_the_swap_is_unsafe_too(self):
        self.things["ingredient/oil"].data["safety"]["free_of"] = ["fact/gluten"]
        entry = self.section()["recipes"][self.recipe_id]
        self.assertFalse(serving.offered(entry, {"fact/dairy"}))

    def test_a_swap_the_graph_forbids_in_this_dish_is_not_listed(self):
        self.things["ingredient/oil"].data["stands_in_for"][0]["not_when"] = ["technique/sweat"]
        self.assertEqual([], self.line("ingredient/butter")["swaps"])

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
                       if queries.can_make(self.things, recipe, case["avoid"])["status"] == "ok"]
            self.assertEqual(offered, case["offered"], case["avoid"])

    def test_the_vectors_are_the_same_for_any_file_order(self):
        reversed_things = dict(reversed(list(self.things.items())))
        self.assertEqual(serving.vectors_of(self.things), serving.vectors_of(reversed_things))


class RealGraphTest(unittest.TestCase):
    """The shipped graph: what the server would offer from the section is what the reference offers, for every case."""

    @classmethod
    def setUpClass(cls):
        things, issues = check.read_repository(REPOSITORY)
        assert not issues
        cls.things = release.included_things(things)

    def test_the_section_offers_exactly_what_the_reference_offers_in_every_case(self):
        section = serving.serving_of(self.things)
        for case in serving.vectors_of(self.things)["cases"]:
            avoided = set(case["avoid"])
            from_section = [recipe_id for recipe_id, entry in section["recipes"].items()
                            if serving.offered(entry, avoided)]
            self.assertEqual(case["offered"], from_section, case["avoid"])

    def test_swaps_make_more_recipes_available_than_the_food_as_written(self):
        section = serving.serving_of(self.things)
        avoided = {"fact/milk"}
        as_written = [one for one, entry in section["recipes"].items() if not avoided & set(entry["unsafe_for"])]
        with_swaps = [one for one, entry in section["recipes"].items() if serving.offered(entry, avoided)]
        self.assertGreater(len(with_swaps), len(as_written))


class StepTextCasesTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()
        self.recipe_id = "recipe/buttered-onions"

    def cases(self):
        return serving.vectors_of(self.things)["step_text_cases"]

    def test_a_recipe_has_a_case_as_written(self):
        written = [one for one in self.cases() if one["recipe"] == self.recipe_id and not one["left_out"] and not one["swaps"]]
        self.assertEqual("Soften the onion in the butter over low heat.", written[0]["steps"][0]["text"])

    def test_a_swap_case_writes_the_name_of_the_stand_in(self):
        swapped = [one for one in self.cases() if one["recipe"] == self.recipe_id and one["swaps"]]
        self.assertEqual("ingredient/oil", swapped[0]["swaps"][0]["instead"])
        self.assertIn("oil", swapped[0]["steps"][0]["text"])

    def test_the_section_carries_the_capital_list(self):
        self.assertIn("Dijon", serving.serving_of(self.things)["step_text"]["proper_name_words"])

    def test_the_artifact_schema_is_version_three(self):
        self.assertEqual(3, release.ARTIFACT_SCHEMA_VERSION)


class PluralCasesTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()
        self.recipe_id = "recipe/buttered-onions"
        self.things[self.recipe_id].data["steps"][0]["text"] = "Soften the {onion:plural} in the {butter:plural}."

    def cases(self):
        return [one for one in serving.vectors_of(self.things)["step_text_cases"] if one["recipe"] == self.recipe_id]

    def test_a_plural_placeholder_prints_the_plural_of_a_countable_food(self):
        self.assertEqual("Soften the onions in the butter.", self.cases()[0]["steps"][0]["text"])

    def test_a_plural_placeholder_of_an_uncountable_stand_in_prints_its_name(self):
        swapped = [one for one in self.cases() if one["swaps"]]
        self.assertTrue(swapped)
        self.assertEqual("Soften the onions in the oil.", swapped[-1]["steps"][0]["text"])

    def test_a_countable_stand_in_prints_its_plural(self):
        self.things["ingredient/oil"].data["uncountable"] = False
        self.things["ingredient/oil"].data["plurals"] = {"en": "Oils"}
        swapped = [one for one in self.cases() if one["swaps"]]
        self.assertEqual("Soften the onions in the oils.", swapped[0]["steps"][0]["text"])
