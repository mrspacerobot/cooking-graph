"""Exclusion-only statements cannot accidentally assert a positive substitution."""

import unittest

from tests.small_kitchen import SmallKitchen
from tools import check

PATH = "graph/preparation/roux.json"


class StandInRuleTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def found(self, change):
        self.kitchen.change(PATH, lambda data: change(data["stands_in_for"][0]))
        return {issue.rule for issue in check.check_repository(self.kitchen.root) if issue.path == PATH}

    def test_exclusion_only_requires_a_negative_context(self):
        self.assertIn("exclusion-without-context", self.found(lambda row: row.update(allows=False, when=[])))

    def test_exclusion_only_cannot_carry_positive_contexts(self):
        change = lambda row: row.update(allows=False, not_when=["technique/mince"])
        self.assertIn("exclusion-with-positive-context", self.found(change))

    def test_an_exclusion_with_a_context_is_valid(self):
        change = lambda row: row.update(allows=False, when=[], not_when=["technique/sweat"])
        self.assertEqual(set(), self.found(change))

    def test_missing_flag_is_rejected(self):
        self.assertIn("missing-field", self.found(lambda row: row.pop("allows")))


FLOUR = "graph/ingredient/flour.json"


class RatioMeasureTest(unittest.TestCase):
    """Flour stands in for the butter, whose recipe line is in grams, so a ratio for it must be by weight."""

    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def found(self, ratio):
        row = {"thing": "ingredient/butter", "allows": True, "when": ["technique/sweat"], "not_when": [],
               "ratio": ratio, "caveat": "It is not a fat.", "tier": "drafted"}
        self.kitchen.change(FLOUR, lambda data: data["stands_in_for"].append(row))
        return {issue.rule for issue in check.check_repository(self.kitchen.root) if issue.path == FLOUR}

    def test_a_ratio_by_another_measure_than_its_line_is_rejected(self):
        self.assertIn("ratio-measure-mismatch", self.found({"stand_in": 2, "original": 1, "by": "volume"}))

    def test_a_ratio_by_the_measure_of_its_line_is_valid(self):
        self.assertEqual(set(), self.found({"stand_in": 2, "original": 1, "by": "weight"}))

    def test_a_one_to_one_ratio_leaves_the_amount_alone_whatever_it_is_by(self):
        self.assertEqual(set(), self.found({"stand_in": 1, "original": 1, "by": "volume"}))

    def test_no_ratio_is_valid(self):
        self.assertEqual(set(), self.found(None))


class UnsoundOptionTest(unittest.TestCase):
    """A broken file is reported by its own rule. The rules that read sound things must not stumble over its absence."""

    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def test_a_part_option_with_a_broken_file_is_reported_and_the_checker_goes_on(self):
        def two_fats(dish):
            dish["parts"][1]["options"] = ["ingredient/butter", "ingredient/flour"]
        self.kitchen.change("graph/dish/buttered-onions.json", two_fats)
        self.kitchen.change(FLOUR, lambda flour: flour.update(unknown_field=1))
        rules_broken = {issue.rule for issue in check.check_repository(self.kitchen.root)}
        self.assertIn("unknown-field", rules_broken)
