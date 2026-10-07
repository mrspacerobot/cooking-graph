"""./twins lists things that are probably one thing under two names. It never blocks."""

import json
import unittest

from tests.small_kitchen import SmallKitchen
from tools import check, twins


class TwinsTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def things(self):
        things, issues = check.read_repository(self.kitchen.root)
        self.assertEqual([], issues)
        return things

    def add_ingredient(self, slug, english, aliases=()):
        food = json.loads(json.dumps(self.kitchen.files["graph/ingredient/butter.json"]))
        food.update(id="ingredient/" + slug, names={"en": english}, aliases={"en": list(aliases)} if aliases else {})
        self.kitchen.write("graph/ingredient/" + slug + ".json", food)

    def found(self, synonyms=()):
        return {(one.first, one.second) for one in twins.find(self.things(), synonyms)}

    def test_a_small_kitchen_has_no_twins(self):
        self.assertEqual(set(), self.found())

    def test_the_same_words_in_another_order(self):
        self.add_ingredient("pork-shoulder", "Pork shoulder")
        self.add_ingredient("shoulder-of-pork", "Shoulder pork")
        self.assertEqual({("ingredient/pork-shoulder", "ingredient/shoulder-of-pork")}, self.found())

    def test_a_plural_is_the_same_word(self):
        self.add_ingredient("walnut", "Walnut")
        self.add_ingredient("walnuts", "Walnuts")
        self.assertEqual({("ingredient/walnut", "ingredient/walnuts")}, self.found())

    def test_two_names_the_list_of_synonyms_joins(self):
        self.add_ingredient("aubergine", "Aubergine")
        self.add_ingredient("eggplant", "Eggplant")
        self.assertEqual(set(), self.found())
        self.assertEqual({("ingredient/aubergine", "ingredient/eggplant")}, self.found(synonyms=[["aubergine", "eggplant"]]))

    def test_things_of_different_kinds_are_not_twins(self):
        self.assertEqual(set(), self.found(synonyms=[["sweat", "butter"]]))

    def test_an_ingredient_and_a_preparation_are_compared_together(self):
        self.assertEqual({("ingredient/butter", "preparation/roux")}, self.found(synonyms=[["roux", "butter"]]))

    def test_a_synonym_that_matches_an_alias(self):
        self.add_ingredient("coriander", "Coriander")
        self.add_ingredient("cilantro-leaf", "Fresh herb", aliases=["Cilantro"])
        self.assertEqual({("ingredient/cilantro-leaf", "ingredient/coriander")}, self.found(synonyms=[["coriander", "cilantro"]]))

    def test_the_report_names_each_pair_once(self):
        self.add_ingredient("walnut", "Walnut")
        self.add_ingredient("walnuts", "Walnuts")
        lines = twins.report(twins.find(self.things(), []))
        self.assertEqual(1, len([line for line in lines if "walnut" in line]))


if __name__ == "__main__":
    unittest.main()
