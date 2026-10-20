"""Steps name foods through placeholders and mark the text of optional parts."""

import unittest

from tests.small_kitchen import SmallKitchen
from tools import check

PATH = "graph/recipe/buttered-onions.json"
SKIN_LINE = {"thing": "ingredient/onion-skin", "amount": {"value": 1, "unit": "pinch"}, "forms": [], "part": "garnish"}


class StepRuleTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def rules_for(self, text, garnish=False):
        def change(data):
            data["steps"][0]["text"] = text
            if garnish:
                data["ingredients"].append(dict(SKIN_LINE))

        self.kitchen.change(PATH, change)
        return {issue.rule for issue in check.check_repository(self.kitchen.root) if issue.path == PATH and issue.rule.startswith("step-")}

    def test_placeholders_for_the_parts_of_the_lines_are_valid(self):
        self.assertEqual(set(), self.rules_for("Soften the {onion} in the {roux}."))

    def test_a_food_named_in_plain_words_is_rejected(self):
        self.assertIn("step-plain-ingredient", self.rules_for("Soften the {onion} in the butter."))

    def test_a_plural_in_plain_words_is_rejected(self):
        self.assertIn("step-plain-ingredient", self.rules_for("Soften the onions in the {roux}."))

    def test_a_food_the_recipe_has_no_line_for_is_not_rejected(self):
        self.assertEqual(set(), self.rules_for("Soften the {onion} in the {roux} with some flour."))

    def test_a_placeholder_for_a_part_the_recipe_lacks_is_rejected(self):
        self.assertIn("step-part-unknown", self.rules_for("Soften the {onion} in the {sauce}."))

    def test_a_part_the_dish_has_but_the_recipe_has_no_line_for_is_rejected(self):
        self.assertIn("step-part-unknown", self.rules_for("Soften the {onion} in the {roux}, then {garnish}."))

    def test_an_ingredient_the_part_lacks_is_rejected(self):
        self.assertIn("step-ingredient-unknown", self.rules_for("Soften the {onion} in the {roux.flour}."))

    def test_an_ingredient_named_by_its_slug_is_valid(self):
        self.assertEqual(set(), self.rules_for("Soften the {onion.onion} in the {roux.butter}."))

    def test_a_part_holding_two_foods_needs_the_ingredient(self):
        def change(data):
            data["ingredients"].append({"thing": "ingredient/flour", "amount": {"value": 1, "unit": "pinch"}, "forms": [], "part": "roux"})
            data["steps"][0]["text"] = "Soften the {onion} in the {roux}."

        self.kitchen.change(PATH, change)
        rules = {issue.rule for issue in check.check_repository(self.kitchen.root) if issue.path == PATH}
        self.assertIn("step-ingredient-ambiguous", rules)

    def test_an_optional_part_in_a_clause_is_valid(self):
        text = "Soften the {onion} in the {roux} [garnish: and add the {garnish}]."
        self.assertEqual(set(), self.rules_for(text, garnish=True))

    def test_text_of_an_optional_part_outside_a_clause_is_rejected(self):
        self.assertIn("step-optional-unmarked", self.rules_for("Soften the {onion} in the {roux} and add the {garnish}.", garnish=True))

    def test_an_optional_food_in_plain_words_is_rejected(self):
        self.assertIn("step-plain-ingredient", self.rules_for("Soften the {onion} in the {roux} and add the onion skin.", garnish=True))

    def test_a_clause_on_a_required_part_is_rejected(self):
        self.assertIn("step-clause-on-required-part", self.rules_for("Soften the {onion} [roux: in the {roux}]."))

    def test_a_clause_for_a_part_the_recipe_lacks_is_rejected(self):
        self.assertIn("step-part-unknown", self.rules_for("Soften the {onion} in the {roux} [sauce: and the {sauce}]."))

    def test_broken_brackets_are_rejected(self):
        self.assertIn("step-text-malformed", self.rules_for("Soften the {onion in the {roux}."))
        self.assertIn("step-text-malformed", self.rules_for("Soften the {onion} in the {roux}]."))
