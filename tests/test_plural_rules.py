"""A food is uncountable or has a plural for every language it is named in; never neither."""

import unittest

from tests.small_kitchen import SmallKitchen
from tools import check

ONION = "graph/ingredient/onion.json"
BUTTER = "graph/ingredient/butter.json"
ROUX = "graph/preparation/roux.json"


class PluralRuleTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def found(self, path, change):
        self.kitchen.change(path, change)
        return {issue.rule for issue in check.check_repository(self.kitchen.root) if issue.path == path}

    def test_the_shipped_shape_is_valid(self):
        self.assertEqual(set(), self.found(ONION, lambda data: None))
        self.assertEqual(set(), self.found(BUTTER, lambda data: None))

    def test_a_countable_food_without_a_plural_is_rejected(self):
        self.assertIn("plural-missing", self.found(ONION, lambda data: data.update(plurals={})))

    def test_a_plural_is_needed_for_each_language_of_the_names(self):
        def add_french_name(data):
            data["names"]["fr"] = "Oignon"

        self.assertIn("plural-missing", self.found(ONION, add_french_name))

    def test_a_plural_in_a_language_the_food_has_no_name_in_is_rejected(self):
        self.assertIn("plural-without-name", self.found(ONION, lambda data: data["plurals"].update(fr="Oignons")))

    def test_an_uncountable_food_with_a_plural_is_rejected(self):
        self.assertIn("uncountable-with-plural", self.found(BUTTER, lambda data: data.update(plurals={"en": "Butters"})))

    def test_a_preparation_answers_too(self):
        self.assertIn("plural-missing", self.found(ROUX, lambda data: data.update(uncountable=False)))

    def test_a_food_that_does_not_say_is_rejected(self):
        self.assertIn("missing-field", self.found(ONION, lambda data: data.pop("uncountable")))
        self.assertIn("missing-field", self.found(BUTTER, lambda data: data.pop("plurals")))
