"""./candidates lists swaps worth drafting, from groups and dish part options. It writes nothing."""

import json
import unittest

from tests.small_kitchen import SmallKitchen
from tools import candidates, check


class CandidatesTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def things(self):
        things, issues = check.read_repository(self.kitchen.root)
        self.assertEqual([], issues)
        return things

    def add_shallot(self, groups=("group/alliums",)):
        food = json.loads(json.dumps(self.kitchen.files["graph/ingredient/onion.json"]))
        food.update(id="ingredient/shallot", names={"en": "Shallot"}, aliases={}, is_a=[])
        food["groups"] = [{"thing": group, "tier": "drafted"} for group in groups]
        self.kitchen.files["graph/ingredient/shallot.json"] = food
        self.kitchen.write("graph/ingredient/shallot.json", food)

    def pairs(self):
        return {(one.first, one.second): one.reasons for one in candidates.find(self.things())}

    def test_two_things_of_one_group_are_a_candidate_pair(self):
        self.add_shallot()
        self.assertEqual(("group/alliums",), self.pairs()[("ingredient/onion", "ingredient/shallot")])

    def test_a_thing_in_no_shared_group_is_not_paired(self):
        self.add_shallot(groups=())
        self.assertNotIn(("ingredient/onion", "ingredient/shallot"), self.pairs())

    def test_a_pair_is_listed_once_in_a_fixed_order(self):
        self.add_shallot()
        listed = [pair for pair in self.pairs() if "ingredient/shallot" in pair and "ingredient/onion" in pair]
        self.assertEqual([("ingredient/onion", "ingredient/shallot")], listed)

    def test_an_ingredient_and_a_preparation_of_one_group_are_paired(self):
        self.assertIn(("ingredient/onion", "preparation/onion-juices"), self.pairs())

    def test_a_pair_with_a_stand_in_row_either_way_is_left_out(self):
        self.add_shallot()
        self.kitchen.change("graph/ingredient/shallot.json", lambda food: food["stands_in_for"].append({
            "thing": "ingredient/onion", "allows": True, "when": [], "not_when": [], "ratio": None,
            "caveat": "It is milder.", "tier": "drafted"}))
        self.assertNotIn(("ingredient/onion", "ingredient/shallot"), self.pairs())

    def test_an_exclusion_row_also_settles_a_pair(self):
        self.add_shallot()
        self.kitchen.change("graph/ingredient/onion.json", lambda food: food["stands_in_for"].append({
            "thing": "ingredient/shallot", "allows": False, "when": [], "not_when": ["technique/sweat"], "ratio": None,
            "caveat": "It burns sooner.", "tier": "drafted"}))
        self.assertNotIn(("ingredient/onion", "ingredient/shallot"), self.pairs())

    def test_two_options_of_one_dish_part_are_a_candidate_pair(self):
        self.add_shallot(groups=())
        self.kitchen.change("graph/dish/buttered-onions.json", lambda dish: dish["parts"][0].update(
            options=["ingredient/onion", "ingredient/shallot"]))
        self.assertEqual(("dish/buttered-onions part onion",), self.pairs()[("ingredient/onion", "ingredient/shallot")])

    def test_a_pair_found_two_ways_names_both(self):
        self.add_shallot()
        self.kitchen.change("graph/dish/buttered-onions.json", lambda dish: dish["parts"][0].update(
            options=["ingredient/onion", "ingredient/shallot"]))
        self.assertEqual(("group/alliums", "dish/buttered-onions part onion"),
                         self.pairs()[("ingredient/onion", "ingredient/shallot")])

    def test_the_summary_counts_open_pairs_by_group(self):
        self.add_shallot()
        lines = candidates.summary(candidates.find(self.things()))
        self.assertTrue(any(line.startswith("group/alliums: ") for line in lines))

    def test_the_listing_can_be_cut_to_one_group(self):
        self.add_shallot()
        found = candidates.find(self.things())
        listed = candidates.listing(found, group="group/alliums")
        self.assertIn("ingredient/onion and ingredient/shallot: group/alliums", listed)
        self.assertEqual([], candidates.listing(found, group="group/vegetables-that-do-not-exist"))


if __name__ == "__main__":
    unittest.main()
