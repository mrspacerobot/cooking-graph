"""The numbers: counts by kind and tier, safety states, and the two probe shares."""

import unittest

from tests.small_kitchen import SmallKitchen
from tools import check, numbers, reading


class NumbersTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def count(self):
        things, issues = check.read_repository(self.kitchen.root)
        self.assertEqual([], issues)
        return numbers.count(things)

    def test_things_are_counted_by_kind_and_tier(self):
        counts = self.count()
        self.assertEqual({"drafted": 2}, counts["things"]["technique"])
        self.assertEqual({"drafted": 5}, counts["things"]["ingredient"])
        self.assertEqual({"drafted": 1}, counts["things"]["recipe"])
        self.assertEqual({"drafted": 5}, counts["things"]["dish-probe"])

    def test_statements_are_counted_by_tier(self):
        self.assertEqual({"drafted": 37}, self.count()["statements"])

    def test_safety_records_are_counted_by_state(self):
        self.assertEqual({"unverified": 5}, self.count()["safety"])

    def test_probe_shares_are_counted_apart(self):
        counts = self.count()
        self.assertEqual((4, 4), counts["probes"]["growing"])
        self.assertEqual((1, 1), counts["probes"]["held-back"])

    def test_probe_words_are_counted_apart(self):
        words = self.count()["probe_words"]
        self.assertEqual({"techniques": (4, 4), "ingredients": (8, 8)}, words["growing"])
        self.assertEqual({"techniques": (1, 1), "ingredients": (2, 2)}, words["held-back"])

    def test_levels_that_name_a_technique_are_counted(self):
        self.assertEqual((1, 2), self.count()["levels_with_a_technique"])

    def test_recipe_steps_are_counted(self):
        self.assertEqual(1, self.count()["recipe_steps"])

    def test_safety_points_that_wait_for_a_fact_are_counted(self):
        self.assertEqual(1, self.count()["safety_points"])

    def test_the_table_is_markdown(self):
        model, words = reading.read_schema(self.kitchen.root)
        table = numbers.render(self.count(), model, words)
        self.assertIn("| technique | 2 | 2 | 0 | 0 | 0 | 0 |", table)
        self.assertIn("| statements | 37 | 37 | 0 | 0 | 0 | 0 |", table)
        self.assertIn("Safety points in recipe steps that wait for a verified fact: 1", table)
        self.assertIn("growing", table)
        self.assertIn("held-back", table)
        self.assertIn("4 of 4", table)
        self.assertIn("100%", table)
        self.assertIn("| held-back | 1 of 1 | 100% | 1 of 1 | 2 of 2 |", table)


if __name__ == "__main__":
    unittest.main()
