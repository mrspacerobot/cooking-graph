"""./vocabulary prints the closed list a photo step chooses from: ids and names of the graph, never a probe."""

import json
import os
import subprocess
import unittest

from tests.small_kitchen import REPOSITORY
from tests.test_queries import kitchen
from tests.test_question_probes import add, home_probe
from tools import vocabulary


class VocabularyTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()
        self.listed = vocabulary.closed_list(self.things)

    def ids(self, section):
        return [row["id"] for row in self.listed[section]]

    def test_foods_are_ingredients_and_preparations_sorted_by_id(self):
        self.assertEqual(sorted(self.ids("foods")), self.ids("foods"))
        for expected in ("ingredient/onion", "ingredient/butter", "ingredient/oil", "preparation/roux"):
            self.assertIn(expected, self.ids("foods"))

    def test_techniques_are_listed_apart(self):
        self.assertEqual(["technique/mince", "technique/sweat"], self.ids("techniques"))
        self.assertNotIn("technique/sweat", self.ids("foods"))

    def test_a_row_carries_the_english_name_the_aliases_and_the_groups(self):
        onion = next(row for row in self.listed["foods"] if row["id"] == "ingredient/onion")
        self.assertEqual("Onion", onion["name"])
        self.assertEqual(["group/alliums"], onion["groups"])
        self.assertEqual([], onion["aliases"])
        self.things["ingredient/onion"].data["aliases"] = {"en": ["bulb onion"], "fr": ["oignon"]}
        row = next(row for row in vocabulary.closed_list(self.things)["foods"] if row["id"] == "ingredient/onion")
        self.assertEqual(["bulb onion", "oignon"], row["aliases"])

    def test_nothing_but_the_graph_is_listed(self):
        add(self.things, home_probe())
        self.assertEqual(self.listed, vocabulary.closed_list(self.things))
        text = json.dumps(vocabulary.closed_list(self.things))
        self.assertNotIn("kitchen-probe", text)
        self.assertNotIn("dish/", text)

    def test_the_list_does_not_depend_on_file_order(self):
        self.assertEqual(self.listed, vocabulary.closed_list(dict(reversed(list(self.things.items())))))

    def test_the_command_prints_the_list_twice_the_same_and_says_a_label_is_never_an_id(self):
        path = os.path.join(REPOSITORY, "vocabulary")
        first = subprocess.run([path], capture_output=True, text=True)
        second = subprocess.run([path], capture_output=True, text=True)
        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        answer = json.loads(first.stdout)
        self.assertIn("never invent an id", answer["note"])
        self.assertIn("ingredient/butter", [row["id"] for row in answer["foods"]])
        self.assertFalse([row for section in ("foods", "techniques") for row in answer[section] if "-probe" in row["id"]])
        names_only = subprocess.run([path, "--names"], capture_output=True, text=True)
        self.assertEqual(0, names_only.returncode, names_only.stderr)
        self.assertIn("ingredient/butter\tButter", names_only.stdout)


if __name__ == "__main__":
    unittest.main()
