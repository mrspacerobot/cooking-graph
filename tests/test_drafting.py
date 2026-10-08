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
        row = drafting.part("fat", "fat", "ingredient/butter", "ingredient/olive-oil")
        expected = {"id": "fat", "role": "fat", "options": ["ingredient/butter", "ingredient/olive-oil"], "optional": False, "tier": "drafted"}
        self.assertEqual(expected, row)

    def test_an_amount_and_a_range(self):
        self.assertEqual({"value": 30, "unit": "gram"}, drafting.amount(30, "gram"))
        self.assertEqual({"from": 8, "to": 10, "unit": "minute"}, drafting.span(8, 10, "minute"))


class SafetyRecords(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def test_every_fact_of_the_graph_is_answered_and_nothing_is_verified(self):
        record = drafting.safety(self.kitchen.root, [("fact/dairy", "A milk product.", True)], note="Made from cream.")
        expected = {
            "state": "unverified",
            "contains": [{"fact": "fact/dairy", "basis": "A milk product.", "certain": True}],
            "free_of": ["fact/gluten"],
            "note": "Made from cream.",
        }
        self.assertEqual(expected, record)

    def test_a_fact_the_graph_does_not_hold_is_refused(self):
        with self.assertRaises(ValueError):
            drafting.safety(self.kitchen.root, [("fact/mustard", "It is mustard.", True)])

    def test_a_drafted_thing_is_written_and_passes_the_check(self):
        cream = drafting.thing("ingredient/cream", "Cream", fr="Crème")
        cream["is_a"] = []
        cream["part_of"] = []
        cream["groups"] = []
        cream["forms"] = []
        cream["behaviour"] = "Thickens as it boils down."
        cream["safety"] = drafting.safety(self.kitchen.root, [("fact/dairy", "A milk product.", True)])
        cream["stands_in_for"] = []
        cream["in_pantry_of"] = drafting.links("cuisine/french")
        cream["same_as"] = []
        self.assertEqual("graph/ingredient/cream.json", drafting.put(self.kitchen.root, cream))
        self.assertEqual([], check.check_repository(self.kitchen.root))


if __name__ == "__main__":
    unittest.main()


class ShortIds(unittest.TestCase):
    def test_a_short_id_is_written_out(self):
        self.assertEqual("ingredient/butter", drafting.full("i/butter"))
        self.assertEqual("technique/sweat", drafting.full("t/sweat"))
        self.assertEqual("fact/dairy", drafting.full("x/dairy"))

    def test_a_full_id_stays_as_it_is(self):
        self.assertEqual("ingredient/butter", drafting.full("ingredient/butter"))


class OneOfEachKind(unittest.TestCase):
    """Whatever the helpers build has the shape the model asks for."""

    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def test_everything_the_helpers_build_passes_the_check(self):
        root = self.kitchen.root
        built = [
            drafting.equipment("whisk", "Whisk", "Beats air into a liquid.", fr="Fouet"),
            drafting.form("diced", "Diced", "Even cubes.", size=[("side", drafting.span(8, 12, "millimetre"))]),
            drafting.group("roots", "Roots", "They hold a clean cut.", within="g/vegetables", stands_alone="Only the leek is in it yet."),
            drafting.ingredient(root, "leek", "Leek", "Softens slowly.", is_a=["i/allium"], groups=["g/roots"], pantry=["c/french"]),
            drafting.ingredient(
                root, "ghee", "Ghee", "Stands high heat.", contains=[("x/dairy", "Made from butter.", True)],
                stands=[drafting.stand_in("i/butter", "Tastes nuttier.", when=["t/sweat"], ratio=(1, 1, "weight"))],
            ),
            drafting.technique(
                "dice", "Dice", "Cuts food into even cubes.",
                how=["Square off the piece.", "Cut it into planks, then sticks, then cubes."],
                cues=[("see", "The cubes are all one size.")],
                mistakes=[("The pieces are uneven.", "Cut the planks to one thickness first.")],
                works_on=["g/roots"], makes=["f/diced"], needs=[("tool", ["e/pan"])],
                comes_after=[("t/mince", "A steady grip comes first.")], variant_of=[("t/mince", "Larger pieces.")],
                belongs_to=["c/french"],
            ),
            drafting.preparation(
                "leek-butter", "Leek butter", "Leeks softened in butter.",
                parts=[drafting.part("leek", "main", "i/leek"), drafting.part("butter", "fat", "i/butter")], teaches=["t/dice"],
                stands=[drafting.stand_in("i/leek", "It is richer.", not_when=["t/sweat"])],
            ),
            drafting.dish(
                "buttered-leeks", "Buttered leeks", "Leeks softened in butter.",
                parts=[drafting.part("leeks", "main", "p/leek-butter")], teaches=["t/dice"], belongs_to=["c/french"],
            ),
            drafting.recipe(
                "buttered-leeks", "Buttered leeks", "d/buttered-leeks", drafting.amount(2, "serving"),
                ingredients=[drafting.line("i/leek", 2, "piece", "f/diced", part="leeks"), drafting.line("i/butter", 20, "gram", part="leeks")],
                equipment=["e/pan"],
                steps=[
                    drafting.step("t/dice", ["i/leek"], "Cut the leeks into even cubes."),
                    drafting.step(
                        "t/sweat", ["i/leek"], "Soften the leeks in the butter.", using=["i/butter"],
                        time=drafting.span(8, 10, "minute"), safety=["cooling-and-keeping"], makes=["p/roux"],
                    ),
                ],
            ),
        ]
        for thing in built:
            drafting.put(root, thing)
        self.assertEqual([], check.check_repository(root))
