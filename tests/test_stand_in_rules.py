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
