"""The Wikidata importer: match by exact English label, write only an id and new names, never guess, never overwrite."""

import json
import os
import unittest

from tests.small_kitchen import SmallKitchen
from tools import check, wikidata, wikidata_fetch

SOURCE = "source/kitchen-law"
LANGUAGES = ("es", "it", "tr", "fr")


def entity(label, qid, labels=None, food=True):
    return {"label": label, "qid": qid, "food": food, "labels": labels or {}}


BUTTER = entity("butter", "Q34172", {"es": "mantequilla", "it": "burro", "tr": "tereyağı", "fr": "beurre"})


class WikidataTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def things(self):
        things, issues = check.read_repository(self.kitchen.root)
        self.assertEqual([], issues)
        return things

    def plan(self, entities, languages=LANGUAGES):
        return wikidata.plan(self.things(), entities, SOURCE, languages)

    def apply(self, plan):
        return wikidata.apply(self.kitchen.root, self.things(), plan)

    def read(self, path):
        with open(os.path.join(self.kitchen.root, path), encoding="utf-8") as handle:
            return json.load(handle)

    def test_an_exact_english_label_matches_and_brings_an_id_and_names(self):
        plan = self.plan([BUTTER])
        self.assertEqual(1, len(plan.changes))
        change = plan.changes[0]
        self.assertEqual("ingredient/butter", change.thing)
        self.assertEqual({"source": SOURCE, "id": "Q34172", "tier": "sourced"}, change.same_as)
        self.assertEqual({"es": "mantequilla", "it": "burro", "tr": "tereyağı", "fr": "beurre"}, change.names)

    def test_the_label_is_compared_in_plain_form(self):
        plan = self.plan([entity("BUTTER", "Q34172")])
        self.assertEqual(["ingredient/butter"], [change.thing for change in plan.changes])

    def test_applying_writes_files_that_the_checker_accepts(self):
        self.apply(self.plan([BUTTER]))
        butter = self.read("graph/ingredient/butter.json")
        self.assertEqual([{"source": SOURCE, "id": "Q34172", "tier": "sourced"}], butter["same_as"])
        self.assertEqual("mantequilla", butter["names"]["es"])
        self.assertEqual("drafted", butter["tier"])
        self.assertEqual([], check.check_repository(self.kitchen.root))

    def test_a_second_run_changes_nothing(self):
        self.apply(self.plan([BUTTER]))
        again = self.plan([BUTTER])
        self.assertEqual([], again.changes)
        self.assertEqual(0, self.apply(again))

    def test_a_dry_run_writes_nothing(self):
        before = self.read("graph/ingredient/butter.json")
        self.assertEqual(1, wikidata.apply(self.kitchen.root, self.things(), self.plan([BUTTER]), dry_run=True))
        self.assertEqual(before, self.read("graph/ingredient/butter.json"))

    def test_two_different_items_for_one_label_are_ambiguous_and_skipped(self):
        plan = self.plan([entity("butter", "Q34172"), entity("butter", "Q99999")])
        self.assertEqual([], plan.changes)
        self.assertEqual("ambiguous", plan.skipped[0].why)

    def test_an_item_that_is_not_a_food_is_skipped(self):
        plan = self.plan([entity("butter", "Q1", food=False)])
        self.assertEqual([], plan.changes)

    def test_a_thing_with_no_match_is_only_counted(self):
        plan = self.plan([entity("nothing", "Q2")])
        self.assertEqual([], plan.changes)
        self.assertEqual([], plan.skipped)

    def test_two_things_that_match_one_item_are_both_skipped(self):
        plan = self.plan([entity("butter", "Q5"), entity("flour", "Q5")])
        self.assertEqual([], plan.changes)
        self.assertEqual({"one-id-for-two-things"}, {skip.why for skip in plan.skipped})

    def test_a_name_another_thing_already_holds_is_not_written(self):
        self.kitchen.change("graph/ingredient/flour.json", lambda food: food.update(aliases={"es": ["harina"]}))
        plan = self.plan([entity("butter", "Q34172", {"es": "harina"})])
        self.assertEqual({}, plan.changes[0].names)
        self.assertEqual(["name-held"], [skip.why for skip in plan.skipped])

    def test_a_new_name_two_things_would_both_get_goes_to_the_first_only(self):
        plan = self.plan([entity("butter", "Q34172", {"es": "grasa"}), entity("flour", "Q1", {"es": "grasa"})])
        names = {change.thing: change.names for change in plan.changes}
        self.assertEqual({"es": "grasa"}, names["ingredient/butter"])
        self.assertEqual({}, names["ingredient/flour"])
        self.assertIn("name-held", {skip.why for skip in plan.skipped})

    def test_a_label_in_another_script_is_not_written(self):
        plan = self.plan([entity("butter", "Q34172", {"ja": "バター", "es": "mantequilla"})], languages=("es", "ja"))
        self.assertEqual({"es": "mantequilla"}, plan.changes[0].names)

    def test_a_label_that_is_already_a_name_is_not_added(self):
        plan = self.plan([entity("butter", "Q34172", {"fr": "Butter"})])
        self.assertEqual({}, plan.changes[0].names)

    def test_a_different_name_in_a_language_that_has_one_becomes_an_alias(self):
        self.kitchen.change("graph/ingredient/butter.json", lambda food: food.update(names={"en": "Butter", "es": "manteca"}))
        plan = self.plan([entity("butter", "Q34172", {"es": "mantequilla"})])
        self.assertEqual({}, plan.changes[0].names)
        self.assertEqual({"es": ["mantequilla"]}, plan.changes[0].aliases)
        self.apply(plan)
        butter = self.read("graph/ingredient/butter.json")
        self.assertEqual("manteca", butter["names"]["es"])
        self.assertEqual(["mantequilla"], butter["aliases"]["es"])

    def test_a_source_that_may_not_be_used_commercially_is_refused(self):
        self.kitchen.change("graph/source/kitchen-law.json", lambda source: source.update(commercial_use="share-alike"))
        with self.assertRaises(ValueError):
            self.plan([BUTTER])

    def test_an_id_the_thing_already_has_from_another_item_is_a_conflict(self):
        self.kitchen.change("graph/ingredient/butter.json", lambda food: food.update(same_as=[{"source": SOURCE, "id": "Q1", "tier": "sourced"}]))
        plan = self.plan([BUTTER])
        self.assertEqual([], plan.changes)
        self.assertEqual("different-id-held", plan.skipped[0].why)

    def test_the_report_gives_counts_and_lists_every_skip(self):
        plan = self.plan([entity("butter", "Q34172"), entity("butter", "Q99999")])
        lines = wikidata.report(plan, total=5)
        self.assertTrue(any(line.startswith("matched: 0") for line in lines))
        self.assertTrue(any("ambiguous" in line and "ingredient/butter" in line for line in lines))

    def test_the_query_names_the_food_classes_and_escapes_a_label(self):
        text = wikidata_fetch.query(['crème "fraîche"', "butter"], ("es", "fr"))
        self.assertIn("wd:Q2095", text)
        self.assertIn("wd:Q25403900", text)
        self.assertIn("wd:Q19861951", text)
        self.assertIn("wd:Q136769237", text)
        self.assertIn("(wdt:P31|wdt:P279)/wdt:P279*", text)
        self.assertIn('"crème \\"fraîche\\""@en', text)
        self.assertIn('"es", "fr"', text)

    def test_a_label_is_asked_as_written_and_in_lower_case(self):
        self.assertEqual(["Butter", "butter"], wikidata_fetch.variants("Butter"))
        self.assertEqual(["butter"], wikidata_fetch.variants("butter"))

    def test_a_sparql_answer_becomes_one_entity_per_item(self):
        answer = {"results": {"bindings": [
            {"item": {"value": "http://www.wikidata.org/entity/Q34172"}, "enLabel": {"value": "butter"},
             "lang": {"value": "es"}, "name": {"value": "mantequilla"}},
            {"item": {"value": "http://www.wikidata.org/entity/Q34172"}, "enLabel": {"value": "butter"},
             "lang": {"value": "it"}, "name": {"value": "burro"}},
            {"item": {"value": "http://www.wikidata.org/entity/Q7"}, "enLabel": {"value": "salt"}},
        ]}}
        found = {one["qid"]: one for one in wikidata_fetch.entities(answer)}
        self.assertEqual({"es": "mantequilla", "it": "burro"}, found["Q34172"]["labels"])
        self.assertEqual({}, found["Q7"]["labels"])
        self.assertTrue(found["Q7"]["food"])
        self.assertEqual("salt", found["Q7"]["label"])


if __name__ == "__main__":
    unittest.main()
