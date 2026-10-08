"""Asking for a technique also finds its variants: a kind of boil is a boil. The other way round it is not."""

import copy
import json
import os
import subprocess
import unittest

from tests.small_kitchen import REPOSITORY
from tests.test_queries import kitchen
from tools import queries
from tools.reading import Thing


def variant(things, slug, of, recipe_id=None):
    """A technique that is a variant of `of`, and optionally a recipe whose only step uses it."""
    card = copy.deepcopy(things[of].data)
    card.update(id="technique/" + slug, names={"en": slug}, aliases={},
                variant_of=[{"thing": of, "differs": "It differs.", "tier": "drafted"}])
    things[card["id"]] = Thing("", "technique", card)
    if recipe_id:
        recipe = copy.deepcopy(things["recipe/buttered-onions"].data)
        recipe.update(id=recipe_id)
        recipe["steps"][0]["technique"] = card["id"]
        things[recipe_id] = Thing("", "recipe", recipe)
    return card["id"]


class FamilyTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()

    def test_a_technique_is_in_its_own_family(self):
        self.assertEqual({"technique/sweat"}, queries.family(self.things, "technique/sweat"))

    def test_children_and_grandchildren_are_in_the_family_and_the_parent_is_not_in_theirs(self):
        child = variant(self.things, "gentle-sweat", "technique/sweat")
        grandchild = variant(self.things, "slow-gentle-sweat", child)
        self.assertEqual({"technique/sweat", child, grandchild}, queries.family(self.things, "technique/sweat"))
        self.assertEqual({child, grandchild}, queries.family(self.things, child))
        self.assertEqual({grandchild}, queries.family(self.things, grandchild))

    def test_an_unrelated_technique_is_not_in_the_family(self):
        variant(self.things, "gentle-sweat", "technique/sweat")
        self.assertNotIn("technique/mince", queries.family(self.things, "technique/sweat"))

    def test_a_cycle_ends(self):
        child = variant(self.things, "gentle-sweat", "technique/sweat")
        self.things["technique/sweat"].data["variant_of"] = [{"thing": child, "differs": "Loop.", "tier": "drafted"}]
        self.assertEqual({"technique/sweat", child}, queries.family(self.things, "technique/sweat"))


class VariantQueryTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()
        self.child = variant(self.things, "gentle-sweat", "technique/sweat", "recipe/gentle-onions")

    def ids(self, answer):
        return [row["recipe"] for row in answer["recipes"]]

    def test_recipes_for_a_technique_include_those_that_use_a_variant_with_exact_use_first(self):
        answer = queries.recipes(self.things, "sweat")
        self.assertEqual(["recipe/buttered-onions", "recipe/gentle-onions"], self.ids(answer))
        first, second = answer["recipes"]
        self.assertEqual((True, []), (first["exact"], first["variants_used"]))
        self.assertEqual((False, [self.child]), (second["exact"], second["variants_used"]))

    def test_exact_use_beats_a_teaching_dish_that_only_uses_a_variant(self):
        self.things["dish/buttered-onions"].data["teaches"] = []
        self.things["recipe/gentle-onions"].data["makes"] = "dish/buttered-onions"
        self.things["dish/buttered-onions"].data["teaches"] = [{"thing": self.child, "tier": "drafted"}]
        self.assertEqual("recipe/buttered-onions", queries.recipes(self.things, "sweat")["recipes"][0]["recipe"])

    def test_a_dish_that_teaches_a_variant_teaches_the_family(self):
        self.things["dish/buttered-onions"].data["teaches"] = [{"thing": self.child, "tier": "drafted"}]
        rows = {row["recipe"]: row for row in queries.recipes(self.things, "sweat")["recipes"]}
        self.assertTrue(rows["recipe/gentle-onions"]["teaches"])

    def test_asking_for_the_variant_does_not_find_the_parents_recipes(self):
        self.assertEqual(["recipe/gentle-onions"], self.ids(queries.recipes(self.things, "gentle-sweat")))

    def test_kitchen_ranks_by_what_is_missing_then_exact_use(self):
        answer = queries.kitchen(self.things, "sweat", ["ingredient/onion", "ingredient/butter"])
        self.assertEqual(["recipe/buttered-onions", "recipe/gentle-onions"], self.ids(answer))

    def test_compose_covers_a_requested_technique_through_a_variant_and_says_so(self):
        answer = queries.compose(self.things, ["sweat"], ["ingredient/onion", "ingredient/butter"])
        rows = {row["recipe"]: row for row in answer["recipes"]}
        row = rows["recipe/gentle-onions"]
        self.assertEqual((["technique/sweat"], []), (row["covered"], row["uncovered"]))
        self.assertEqual({"technique/sweat": [self.child]}, row["covered_by_variant"])
        self.assertEqual({}, rows["recipe/buttered-onions"]["covered_by_variant"])

    def test_compose_prefers_the_recipe_that_uses_the_technique_itself_at_equal_cover(self):
        answer = queries.compose(self.things, ["sweat"], ["ingredient/onion", "ingredient/butter"])
        self.assertEqual("recipe/buttered-onions", answer["recipes"][0]["recipe"])

    def test_compose_with_two_techniques_needs_both_exactly_or_through_variants(self):
        recipe = self.things["recipe/gentle-onions"].data
        recipe["steps"].append(dict(recipe["steps"][0], technique="technique/mince", **{"with": []}))
        answer = queries.compose(self.things, ["sweat", "mince"], ["ingredient/onion", "ingredient/butter"])
        self.assertEqual("recipe/gentle-onions", answer["recipes"][0]["recipe"])
        self.assertEqual([], answer["recipes"][0]["uncovered"])


class RealGraphTest(unittest.TestCase):
    def run_command(self, *arguments):
        run = subprocess.run([os.path.join(REPOSITORY, arguments[0]), *arguments[1:]], capture_output=True, text=True)
        self.assertEqual(0, run.returncode, run.stderr)
        return json.loads(run.stdout)

    def test_boil_finds_a_recipe_that_boils_pasta(self):
        rows = {row["recipe"]: row for row in self.run_command("recipes", "technique/boil")["recipes"]}
        self.assertIn("recipe/spaghetti-alla-carbonara", rows)
        self.assertIn("technique/boil-pasta", rows["recipe/spaghetti-alla-carbonara"]["variants_used"])

    def test_emulsify_finds_the_tahini_sauce(self):
        rows = self.run_command("recipes", "technique/emulsify")["recipes"]
        used = {one for row in rows for one in row["variants_used"]}
        self.assertIn("technique/beat-tahini-sauce", used)


if __name__ == "__main__":
    unittest.main()
