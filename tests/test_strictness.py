"""The list of answers that are strict and not certain, which the owner rules on."""

import unittest

from tests.small_kitchen import SmallKitchen
from tools import check, strictness

BUTTER = "graph/ingredient/butter.json"
FLOUR = "graph/ingredient/flour.json"


class StrictAnswers(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def document(self):
        things, issues = check.read_repository(self.kitchen.root)
        self.assertEqual([], issues)
        return strictness.document(things)

    def unsure(self, path, basis):
        self.kitchen.change(path, lambda thing: thing["safety"]["contains"][0].update(certain=False, basis=basis))

    def test_with_every_answer_certain_it_says_so(self):
        self.assertIn("0 of the 2 facts that ingredients hold are strict", self.document())

    def test_a_strict_answer_is_listed_with_its_fact_its_basis_and_its_ingredient(self):
        self.unsure(BUTTER, "It may be made with it.")
        document = self.document()
        self.assertIn("1 of the 2 facts that ingredients hold are strict", document)
        self.assertIn("| `fact/dairy` | It may be made with it. | butter |", document)

    def test_a_certain_answer_is_not_listed(self):
        self.unsure(BUTTER, "It may be made with it.")
        self.assertNotIn("flour", self.document().split("| Fact |")[1])

    def test_ingredients_that_share_a_fact_and_a_basis_share_a_row(self):
        self.kitchen.change(FLOUR, lambda thing: thing["safety"].update(
            contains=[{"fact": "fact/dairy", "basis": "It may be made with it.", "certain": False}, thing["safety"]["contains"][0]],
            free_of=[],
        ))
        self.unsure(BUTTER, "It may be made with it.")
        self.assertIn("| `fact/dairy` | It may be made with it. | butter, flour |", self.document())


if __name__ == "__main__":
    unittest.main()
