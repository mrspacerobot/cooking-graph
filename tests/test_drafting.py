"""The drafting helpers: the rows a drafter writes most, written one way, always as drafted."""

import unittest

from tests.small_kitchen import SmallKitchen
from tools import check, drafting


class Rows(unittest.TestCase):
    def test_a_thing_starts_drafted_with_its_names(self):
        thing = drafting.thing("technique/sweat", "Sweat", fr="Suer", also={"en": ["soften"]})
        expected = {
            "id": "technique/sweat",
            "tier": "drafted",
            "names": {"en": "Sweat", "fr": "Suer"},
            "aliases": {"en": ["soften"]},
        }
        self.assertEqual(expected, thing)
        self.assertEqual(["id", "tier", "names", "aliases"], list(thing))

    def test_a_thing_without_a_french_name_has_none(self):
        self.assertEqual({"en": "Pan"}, drafting.thing("equipment/pan", "Pan")["names"])

    def test_a_link_is_drafted_and_ends_with_its_tier(self):
        row = drafting.link("technique/sweat", why="It is gentler.")
        self.assertEqual({"thing": "technique/sweat", "why": "It is gentler.", "tier": "drafted"}, row)
        self.assertEqual(["thing", "why", "tier"], list(row))

    def test_links_makes_one_row_per_thing(self):
        rows = drafting.links("cuisine/french", "cuisine/provencal")
        self.assertEqual([drafting.link("cuisine/french"), drafting.link("cuisine/provencal")], rows)

    def test_a_part_names_its_role_and_options(self):
        row = drafting.part("fat", "ingredient/butter", "ingredient/olive-oil")
        expected = {"role": "fat", "options": ["ingredient/butter", "ingredient/olive-oil"], "tier": "drafted"}
        self.assertEqual(expected, row)

    def test_an_amount_and_a_range(self):
        self.assertEqual({"value": 30, "unit": "gram"}, drafting.amount(30, "gram"))
        self.assertEqual({"from": 8, "to": 10, "unit": "minute"}, drafting.span(8, 10, "minute"))


class SafetyRecords(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def test_every_fact_of_the_graph_is_answered_and_nothing_is_verified(self):
        record = drafting.safety(self.kitchen.root, ["fact/dairy"], note="Made from cream.")
        expected = {
            "state": "unverified",
            "contains": ["fact/dairy"],
            "free_of": ["fact/gluten"],
            "note": "Made from cream.",
        }
        self.assertEqual(expected, record)

    def test_a_fact_the_graph_does_not_hold_is_refused(self):
        with self.assertRaises(ValueError):
            drafting.safety(self.kitchen.root, ["fact/mustard"])

    def test_a_drafted_thing_is_written_and_passes_the_check(self):
        cream = drafting.thing("ingredient/cream", "Cream", fr="Crème")
        cream["is_a"] = []
        cream["forms"] = []
        cream["behaviour"] = "Thickens as it boils down."
        cream["safety"] = drafting.safety(self.kitchen.root, ["fact/dairy"])
        cream["stands_in_for"] = []
        cream["in_pantry_of"] = drafting.links("cuisine/french")
        self.assertEqual("graph/ingredient/cream.json", drafting.put(self.kitchen.root, cream))
        self.assertEqual([], check.check_repository(self.kitchen.root))


if __name__ == "__main__":
    unittest.main()
