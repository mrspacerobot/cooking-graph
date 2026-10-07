"""The hash a reviewer's record carries: what was seen, so that an edit made afterwards is noticed."""

import copy
import unittest

from tests.small_kitchen import SmallKitchen
from tools import check, review_hash, review_tool


class ReviewHashTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)
        self.sweat = copy.deepcopy(self.kitchen.files["graph/technique/sweat.json"])
        self.butter = copy.deepcopy(self.kitchen.files["graph/ingredient/butter.json"])

    def test_the_hash_is_twelve_hex_digits(self):
        seen = review_hash.seen(self.sweat)
        self.assertEqual(12, len(seen))
        int(seen, 16)

    def test_a_tier_is_not_part_of_what_was_seen(self):
        before = review_hash.seen(self.sweat)
        self.sweat["tier"] = "reviewed"
        self.sweat["works_on"][0]["tier"] = "reviewed"
        self.assertEqual(before, review_hash.seen(self.sweat))

    def test_a_changed_word_changes_the_hash(self):
        before = review_hash.seen(self.sweat)
        self.sweat["does"] = "Softens cut vegetables in fat over gentle heat."
        self.assertNotEqual(before, review_hash.seen(self.sweat))

    def test_the_order_of_the_fields_in_a_file_does_not_matter(self):
        reordered = dict(reversed(list(self.sweat.items())))
        self.assertEqual(review_hash.seen(self.sweat), review_hash.seen(reordered))

    def test_a_whole_ingredient_is_seen_without_its_safety_record(self):
        before = review_hash.seen(self.butter)
        self.butter["safety"]["note"] = "A new note."
        self.assertEqual(before, review_hash.seen(self.butter))

    def test_the_safety_record_has_a_hash_of_its_own_without_its_state(self):
        before = review_hash.seen(self.butter, field="safety")
        self.butter["safety"]["state"] = "verified"
        self.assertEqual(before, review_hash.seen(self.butter, field="safety"))
        self.butter["safety"]["note"] = "A new note."
        self.assertNotEqual(before, review_hash.seen(self.butter, field="safety"))

    def test_one_statement_is_seen_alone(self):
        row = review_hash.seen(self.sweat, field="works_on", target="group/vegetables")
        self.sweat["does"] = "Softens cut vegetables in fat over gentle heat."
        self.assertEqual(row, review_hash.seen(self.sweat, field="works_on", target="group/vegetables"))
        self.sweat["works_on"][0]["tier"] = "reviewed"
        self.assertEqual(row, review_hash.seen(self.sweat, field="works_on", target="group/vegetables"))

    def test_a_part_of_a_dish_is_found_by_its_id(self):
        dish = copy.deepcopy(self.kitchen.files["graph/dish/buttered-onions.json"])
        self.assertIsNotNone(review_hash.seen(dish, field="parts", target="onion"))

    def test_a_statement_that_is_not_there_has_no_hash(self):
        self.assertIsNone(review_hash.seen(self.sweat, field="works_on", target="group/nothing"))


class ReviewToolTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)
        self.things, issues = check.read_repository(self.kitchen.root)
        self.assertEqual([], issues)

    def test_show_names_the_tier_and_the_hash_and_prints_the_card(self):
        lines = review_tool.show(self.things, "technique/sweat")
        text = "\n".join(lines)
        self.assertIn("technique/sweat", text)
        self.assertIn("tier: drafted", text)
        self.assertIn("seen: " + review_hash.seen(self.things["technique/sweat"].data), text)
        self.assertIn("Softens cut vegetables", text)

    def test_seal_prints_only_the_hash(self):
        self.assertEqual(review_hash.seen(self.things["technique/sweat"].data), review_tool.seal(self.things, "technique/sweat"))

    def test_seal_of_a_statement(self):
        expected = review_hash.seen(self.things["technique/sweat"].data, field="works_on", target="group/vegetables")
        self.assertEqual(expected, review_tool.seal(self.things, "technique/sweat", "works_on", "group/vegetables"))

    def test_a_thing_that_does_not_exist(self):
        with self.assertRaises(ValueError):
            review_tool.show(self.things, "technique/nothing")


if __name__ == "__main__":
    unittest.main()
