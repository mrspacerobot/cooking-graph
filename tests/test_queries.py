"""The three questions, including context, missing knowledge and strict avoidance."""

import copy
import json
import os
import subprocess
import unittest

from tests.small_kitchen import REPOSITORY, graph_files, ingredient, link, part
from tools import queries
from tools.reading import Thing


def kitchen():
    things = {}
    for path, data in graph_files().items():
        things[data["id"]] = Thing(path, data["id"].split("/")[0], data)
    dish = things["dish/buttered-onions"].data
    dish["parts"] = [part("onion", "main", ["ingredient/onion"]),
                     part("butter", "fat", ["ingredient/butter"]),
                     part("garnish", "garnish", ["ingredient/onion-skin"], optional=True)]
    recipe = things["recipe/buttered-onions"].data
    recipe["ingredients"] = [
        {"thing": "ingredient/onion", "part": "onion", "amount": {"value": 1, "unit": "piece"}, "forms": []},
        {"thing": "ingredient/butter", "part": "butter", "amount": {"value": 10, "unit": "gram"}, "forms": []}]
    recipe["steps"][0]["works_on"] = ["ingredient/onion"]
    recipe["steps"][0]["with"] = ["ingredient/butter"]
    oil = ingredient("oil", "Oil", [], ["fact/dairy", "fact/gluten"])
    oil["stands_in_for"] = [link("ingredient/butter", allows=True, when=["technique/sweat"], not_when=[],
                                  ratio={"stand_in": 1, "original": 1, "by": "weight"},
                                  caveat="The flavour changes.")]
    things[oil["id"]] = Thing("graph/ingredient/oil.json", "ingredient", oil)
    return things


class QueryTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()
        self.recipe = self.things["recipe/buttered-onions"].data

    def stand_ins(self, avoid=()):
        return queries.stand_ins(self.things, "recipe/buttered-onions", avoid)

    def fat(self, avoid=()):
        return self.stand_ins(avoid)["lines"][1]

    def test_stand_in_keeps_context_ratio_caveat_and_tier(self):
        choice = self.fat()["options"][0]
        self.assertEqual("ingredient/oil", choice["thing"])
        self.assertEqual(["technique/sweat"], choice["when"])
        self.assertEqual({"stand_in": 1, "original": 1, "by": "weight"}, choice["ratio"])
        self.assertEqual("The flavour changes.", choice["caveat"])
        self.assertEqual("drafted", choice["tier"])
        self.assertIn("unverified", self.stand_ins()["safety"])

    def test_other_part_options_are_returned_without_inventing_a_ratio(self):
        self.things["dish/buttered-onions"].data["parts"][1]["options"].append("ingredient/oil")
        self.things["ingredient/oil"].data["stands_in_for"] = []
        self.assertEqual("part-option", self.fat()["options"][0]["basis"])
        self.assertIsNone(self.fat()["options"][0]["ratio"])

    def test_not_when_wins_even_over_a_part_option(self):
        self.things["dish/buttered-onions"].data["parts"][1]["options"].append("ingredient/oil")
        self.things["ingredient/oil"].data["stands_in_for"][0]["not_when"] = ["technique/sweat"]
        self.assertEqual([], self.fat()["options"])
        self.assertEqual("not-in-this-context", self.fat()["excluded"][0]["reason"])

    def test_unrelated_technique_does_not_enable_a_stand_in(self):
        self.things["ingredient/oil"].data["stands_in_for"][0]["when"] = ["technique/mince"]
        self.recipe["steps"].append(dict(self.recipe["steps"][0], technique="technique/mince",
                                          works_on=["ingredient/onion"], **{"with": []}))
        self.assertEqual([], self.fat()["options"])

    def test_a_dish_context_matches(self):
        self.things["ingredient/oil"].data["stands_in_for"][0]["when"] = ["dish/buttered-onions"]
        self.assertEqual("ingredient/oil", self.fat()["options"][0]["thing"])

    def test_exclusion_only_statement_never_enables_other_contexts(self):
        row = self.things["ingredient/oil"].data["stands_in_for"][0]
        row.update(allows=False, when=[], not_when=["technique/mince"])
        self.assertEqual([], self.fat()["options"])
        row["not_when"] = ["technique/sweat"]
        self.assertEqual("not-in-this-context", self.fat()["excluded"][0]["reason"])

    def test_no_transitive_or_reverse_substitutions_are_invented(self):
        self.recipe["ingredients"][1]["thing"] = "ingredient/oil"
        self.assertEqual([], self.fat()["options"])

    def test_avoid_filters_strict_contains_and_checks_preparations_recursively(self):
        dish = self.things["dish/buttered-onions"].data
        dish["parts"][1]["options"].extend(["preparation/roux", "ingredient/flour"])
        self.things["ingredient/flour"].data["safety"]["contains"].append(
            {"fact": "fact/dairy", "basis": "Unknown processing.", "certain": False})
        self.things["ingredient/flour"].data["safety"]["free_of"] = []
        self.assertEqual(["ingredient/oil"], [one["thing"] for one in self.fat(["fact/dairy"])["options"]])

    def test_a_missing_fact_answer_and_preparation_cycle_fail_closed(self):
        oil = self.things["ingredient/oil"].data
        oil["safety"]["free_of"] = ["fact/gluten"]
        self.assertEqual([], self.fat(["fact/dairy"])["options"])
        self.things["preparation/roux"].data["parts"][0]["options"] = ["preparation/roux"]
        self.things["dish/buttered-onions"].data["parts"][1]["options"].append("preparation/roux")
        self.assertEqual([], self.fat(["fact/dairy"])["options"])

    def test_unknown_and_ambiguous_inputs_are_errors(self):
        with self.assertRaises(ValueError):
            self.stand_ins(["fact/future-allergen"])
        with self.assertRaises(ValueError):
            queries.kitchen(self.things, "sweat", ["future ingredient"])
        self.things["ingredient/oil"].data["aliases"] = {"en": ["butter"]}
        with self.assertRaises(ValueError):
            queries.resolve(self.things, "butter", ("ingredient",))

    def test_recipes_using_a_technique_are_ordered_teaching_first(self):
        extra = copy.deepcopy(self.recipe)
        extra["id"] = "recipe/a-onions"
        extra["makes"] = "dish/other-onions"
        dish = copy.deepcopy(self.things["dish/buttered-onions"].data)
        dish["id"] = "dish/other-onions"
        dish["teaches"] = []
        self.things[dish["id"]] = Thing("", "dish", dish)
        self.things[extra["id"]] = Thing("", "recipe", extra)
        result = queries.recipes(self.things, "sweat")["recipes"]
        self.assertEqual(["recipe/buttered-onions", "recipe/a-onions"], [one["recipe"] for one in result])
        self.recipe["steps"][0]["technique"] = "technique/mince"
        self.assertEqual(["recipe/a-onions"], [one["recipe"] for one in queries.recipes(self.things, "sweat")["recipes"]])

    def test_kitchen_uses_home_stand_ins_and_reports_missing_parts(self):
        answer = queries.kitchen(self.things, "sweat", ["ingredient/onion", "ingredient/oil"])["recipes"][0]
        self.assertEqual(0, answer["missing_count"])
        fat = answer["parts"][1]["lines"][0]
        self.assertEqual("stand-in", fat["status"])
        self.assertEqual("ingredient/oil", fat["choice"]["thing"])
        self.assertEqual("omitted", answer["parts"][2]["status"])
        empty = queries.kitchen(self.things, "sweat", [])["recipes"][0]
        self.assertEqual(2, empty["missing_count"])

    def test_kitchen_ranks_missing_before_teaching_with_stable_ties(self):
        extra = copy.deepcopy(self.recipe)
        extra["id"] = "recipe/a-onions"
        extra["ingredients"] = extra["ingredients"][:1]
        self.things[extra["id"]] = Thing("", "recipe", extra)
        result = queries.kitchen(self.things, "sweat", ["ingredient/onion"])["recipes"]
        self.assertEqual(["recipe/a-onions", "recipe/buttered-onions"], [one["recipe"] for one in result])

    def test_kitchen_rechecks_the_original_and_optional_missing_is_not_scored(self):
        self.things["dish/buttered-onions"].data["parts"][1]["optional"] = True
        answer = queries.kitchen(self.things, "sweat", ["onion", "butter"], ["milk"])["recipes"][0]
        self.assertEqual(0, answer["missing_count"])
        self.assertEqual("missing", answer["parts"][1]["lines"][0]["status"])

    def test_expanded_preparation_lines_are_not_replaced_by_a_whole_preparation(self):
        self.recipe["ingredients"][1]["part"] = "roux"
        self.things["dish/buttered-onions"].data["parts"][1] = part("roux", "fat", ["preparation/roux"])
        self.assertNotIn("preparation/roux", [one["thing"] for one in self.fat()["options"]])

    def test_queries_are_independent_of_file_order(self):
        reversed_things = dict(reversed(list(self.things.items())))
        self.assertEqual(self.stand_ins(), queries.stand_ins(reversed_things, "Buttered onions"))
        self.assertEqual(queries.kitchen(self.things, "sweat", ["oil", "onion"]),
                         queries.kitchen(reversed_things, "sweat", ["onion", "oil", "onion"]))

    def test_commands_produce_repeatable_json_and_reject_unknown_inputs(self):
        commands = [("stand-ins", "recipe/sole-meuniere"), ("recipes", "technique/sear"),
                    ("kitchen", "technique/sear", "ingredient/butter")]
        for command in commands:
            with self.subTest(command=command):
                path = os.path.join(REPOSITORY, command[0])
                first = subprocess.run([path, *command[1:]], capture_output=True, text=True)
                second = subprocess.run([path, *command[1:]], capture_output=True, text=True)
                self.assertEqual(0, first.returncode, first.stderr)
                self.assertEqual(first.stdout, second.stdout)
                self.assertIn("unverified", json.loads(first.stdout)["safety"])
                bad = subprocess.run([path, "unknown"], capture_output=True, text=True)
                self.assertNotEqual(0, bad.returncode)
                self.assertIn("unknown", bad.stderr)

    def test_command_rejects_oil_for_the_cold_butter_in_a_mounted_pan_sauce(self):
        path = os.path.join(REPOSITORY, "stand-ins")
        recipe = "recipe/seared-chicken-thighs-with-lemon-butter-pan-sauce"
        run = subprocess.run([path, recipe], capture_output=True, text=True, check=True)
        mounted = [line for line in json.loads(run.stdout)["lines"]
                   if line["original"] == "ingredient/butter" and "technique/mount-with-butter" in line["context"]]
        self.assertTrue(mounted)
        for line in mounted:
            self.assertNotIn("ingredient/olive-oil", [one["thing"] for one in line["options"]])
            self.assertIn("ingredient/olive-oil", [one["thing"] for one in line["excluded"]])
