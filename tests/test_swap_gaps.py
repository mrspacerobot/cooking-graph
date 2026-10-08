"""./swap-gaps lists recipe lines where a swap is plausible and not offered, and foods with no stand-in row at all."""

import copy
import os
import subprocess
import unittest

from tests.small_kitchen import REPOSITORY
from tests.test_queries import kitchen
from tools import swap_gaps
from tools.reading import Thing


class SwapGapsTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()
        self.recipe = self.things["recipe/buttered-onions"].data
        self.oil = self.things["ingredient/oil"].data["stands_in_for"][0]

    def gaps(self):
        return {(row["original"], row["candidate"]): row for row in swap_gaps.analyse(self.things)["gaps"]}

    def test_an_alternative_the_technique_card_names_and_the_graph_does_not_offer_is_a_gap(self):
        row = self.gaps()[("ingredient/butter", "preparation/roux")]
        self.assertEqual(["card"], row["why"])
        self.assertEqual(["recipe/buttered-onions"], row["recipes"])
        self.assertEqual(["technique/sweat"], row["techniques"])

    def test_an_offered_swap_is_not_a_gap(self):
        self.assertNotIn(("ingredient/butter", "ingredient/oil"), self.gaps())

    def test_a_row_whose_context_never_matches_is_a_gap(self):
        self.oil["when"] = ["technique/mince"]
        self.assertEqual(["row-context"], self.gaps()[("ingredient/butter", "ingredient/oil")]["why"])

    def test_card_gaps_come_before_row_context_only_ones_at_equal_counts(self):
        self.oil["when"] = ["technique/mince"]
        rows = swap_gaps.analyse(self.things)["gaps"]
        self.assertEqual([("preparation/roux", ["card"]), ("ingredient/oil", ["row-context"])],
                         [(row["candidate"], row["why"]) for row in rows])

    def test_a_line_with_only_a_row_context_gap_is_not_counted_as_a_gap(self):
        self.oil["when"] = ["technique/mince"]
        self.things["technique/sweat"].data["needs"][1]["options"] = ["ingredient/butter"]
        totals = swap_gaps.analyse(self.things)
        self.assertEqual((0, 1), (totals["with_gap"], totals["with_broader"]))
        self.assertEqual(0, swap_gaps.counts(self.things)["gap_pairs"])

    def test_a_card_that_names_a_swap_with_a_row_in_the_wrong_context_says_both(self):
        self.things["technique/sweat"].data["needs"][1]["options"].append("ingredient/oil")
        self.oil["when"] = ["technique/mince"]
        self.assertEqual(["card", "row-context"], self.gaps()[("ingredient/butter", "ingredient/oil")]["why"])

    def test_an_explicit_exclusion_settles_the_pair(self):
        self.oil.update(allows=False, when=[], not_when=["technique/sweat"])
        self.assertNotIn(("ingredient/butter", "ingredient/oil"), self.gaps())

    def test_equipment_on_a_card_is_never_a_candidate(self):
        self.assertFalse([pair for pair in self.gaps() if any(one.startswith("equipment/") for one in pair)])

    def test_a_card_that_names_only_the_original_makes_no_gap(self):
        self.things["technique/sweat"].data["needs"][1]["options"] = ["ingredient/butter"]
        self.assertNotIn(("ingredient/butter", "preparation/roux"), self.gaps())

    def test_the_same_pair_in_two_recipes_is_one_entry_that_counts_both_and_comes_first(self):
        other = copy.deepcopy(self.recipe)
        other["id"] = "recipe/a-onions"
        self.things[other["id"]] = Thing("", "recipe", other)
        rows = swap_gaps.analyse(self.things)["gaps"]
        self.assertEqual(["recipe/a-onions", "recipe/buttered-onions"], rows[0]["recipes"])
        self.assertEqual(2, rows[0]["count"])

    def test_the_totals_count_lines_lines_with_a_swap_and_lines_with_a_gap(self):
        totals = swap_gaps.analyse(self.things)
        self.assertEqual((2, 1, 1, 0), (totals["lines"], totals["with_swap"], totals["with_gap"], totals["with_broader"]))

    def test_the_listing_cuts_a_long_list_of_techniques(self):
        row = {"count": 3, "original": "ingredient/water", "candidate": "ingredient/stock", "why": ["card"],
               "techniques": ["technique/a", "technique/b", "technique/c", "technique/d", "technique/e"]}
        line = swap_gaps.listing({"gaps": [row]}, 5)[0]
        self.assertIn("technique/a, technique/b, technique/c and 2 more", line)
        self.assertNotIn("technique/d", line)

    def test_foods_in_no_stand_in_row_are_new(self):
        self.assertEqual(["ingredient/allium", "ingredient/onion", "ingredient/onion-skin", "preparation/onion-juices"],
                         swap_gaps.new_foods(self.things))

    def test_a_food_named_by_a_row_is_not_new_even_if_it_has_no_rows_of_its_own(self):
        self.things["ingredient/oil"].data["stands_in_for"][0]["thing"] = "ingredient/onion"
        self.assertNotIn("ingredient/onion", swap_gaps.new_foods(self.things))
        self.assertIn("ingredient/butter", swap_gaps.new_foods(self.things))

    def test_the_answer_does_not_depend_on_file_order(self):
        reversed_things = dict(reversed(list(self.things.items())))
        self.assertEqual(swap_gaps.analyse(self.things), swap_gaps.analyse(reversed_things))

    def test_the_command_lists_gaps_new_foods_and_writes_nothing(self):
        path = os.path.join(REPOSITORY, "swap-gaps")
        before = subprocess.run(["git", "status", "--porcelain"], cwd=REPOSITORY, capture_output=True, text=True).stdout
        summary = subprocess.run([path], capture_output=True, text=True)
        self.assertEqual(0, summary.returncode, summary.stderr)
        self.assertIn("recipe lines", summary.stdout)
        listed = subprocess.run([path, "--list", "--top", "3"], capture_output=True, text=True)
        self.assertEqual(0, listed.returncode, listed.stderr)
        self.assertLessEqual(len(listed.stdout.strip().splitlines()), 4)
        new = subprocess.run([path, "--new"], capture_output=True, text=True)
        self.assertEqual(0, new.returncode, new.stderr)
        self.assertIn("foods", new.stdout)
        after = subprocess.run(["git", "status", "--porcelain"], cwd=REPOSITORY, capture_output=True, text=True).stdout
        self.assertEqual(before, after)

    def test_the_counts_for_the_numbers_are_the_totals_and_the_new_foods(self):
        self.assertEqual({"lines": 2, "with_swap": 1, "with_gap": 1, "gap_pairs": 1, "new_foods": 4},
                         swap_gaps.counts(self.things))


if __name__ == "__main__":
    unittest.main()
