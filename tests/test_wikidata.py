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


class WikidataBase(unittest.TestCase):
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


class WikidataTest(WikidataBase):
    def test_an_exact_english_label_matches_and_brings_an_id_and_names(self):
        plan = self.plan([BUTTER])
        self.assertEqual(1, len(plan.changes))
        change = plan.changes[0]
        self.assertEqual("ingredient/butter", change.thing)
        self.assertEqual({"source": SOURCE, "id": "Q34172", "tier": "sourced"}, change.same_as)
        self.assertEqual({"es": "mantequilla", "it": "burro", "tr": "tereyağı", "fr": "beurre"}, change.names)

    def test_a_match_through_an_alias_alone_is_not_taken(self):
        self.kitchen.change("graph/ingredient/butter.json", lambda food: food.update(aliases={"en": ["cooking fat"]}))
        plan = self.plan([entity("cooking fat", "Q77")])
        self.assertEqual([], plan.changes)

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

    def test_a_label_with_a_note_in_brackets_a_digit_or_a_full_stop_is_not_a_plain_name(self):
        labels = {"es": "mantequilla (alimento)", "it": "burro 2", "tr": "tereyağı sp."}
        plan = self.plan([entity("butter", "Q34172", labels)])
        self.assertEqual({}, plan.changes[0].names)
        self.assertEqual({"not-a-plain-name"}, {skip.why for skip in plan.skipped})

    def test_a_very_long_label_is_not_a_plain_name(self):
        plan = self.plan([entity("butter", "Q34172", {"es": "Denominación de Origen Protegida Mantequilla de la Región Antigua"})])
        self.assertEqual({}, plan.changes[0].names)

    def test_a_name_that_was_read_and_refused_is_not_written_again(self):
        refused = [{"thing": "ingredient/butter", "language": "es", "label": "mantequilla", "why": "Read and refused in a test."}]
        plan = wikidata.plan(self.things(), [BUTTER], SOURCE, LANGUAGES, refused)
        self.assertNotIn("es", plan.changes[0].names)
        self.assertIn("it", plan.changes[0].names)
        self.assertIn("read-and-refused", {skip.why for skip in plan.skipped})

    def test_a_scientific_name_written_the_same_in_two_languages_is_not_a_name(self):
        plan = self.plan([entity("butter", "Q34172", {"es": "Bos taurus", "it": "Bos taurus", "tr": "tereyağı"})])
        self.assertEqual({"tr": "tereyağı"}, plan.changes[0].names)
        self.assertIn("scientific-name", {skip.why for skip in plan.skipped})

    def test_a_two_word_name_in_one_language_only_is_kept(self):
        plan = self.plan([entity("butter", "Q34172", {"es": "Arroz negro"})])
        self.assertEqual({"es": "Arroz negro"}, plan.changes[0].names)

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


def candidate(label, qid, description, labels=None):
    return {"label": label, "qid": qid, "food": False, "description": description, "labels": labels or {}}


class ProposeAndChooseTest(WikidataBase):
    """A second pass: items that are no food by class are proposed from their description, and a person chooses."""

    def test_a_description_that_names_a_food_passes(self):
        for text in ("edible tuber", "culinary or medicinal herb", "spice of a plant", "fish, ambiguous vernacular name", "Thai salad"):
            self.assertTrue(wikidata.sounds_like_food(text), text)

    def test_a_description_that_names_something_else_does_not_pass(self):
        for text in ("family name", "painting by Charles Jacque", "Wikimedia disambiguation page", "town in Alaska, United States", "restaurant in Peel en Maas", ""):
            self.assertFalse(wikidata.sounds_like_food(text), text)

    def test_a_thing_with_no_match_gets_a_proposal_when_a_description_sounds_like_food(self):
        found = wikidata.propose(self.things(), [candidate("flour", "Q9", "edible tuber"), candidate("flour", "Q8", "family name")])
        self.assertEqual([("ingredient/flour", "Q9")], [(one.thing, one.qid) for one in found])

    def test_a_thing_that_already_has_an_id_gets_no_proposal(self):
        self.kitchen.change("graph/ingredient/flour.json", lambda food: food.update(same_as=[{"source": SOURCE, "id": "Q36465", "tier": "sourced"}]))
        self.assertEqual([], wikidata.propose(self.things(), [candidate("flour", "Q9", "edible tuber")]))

    def test_a_proposal_through_an_alias_says_so(self):
        self.kitchen.change("graph/ingredient/flour.json", lambda food: food.update(aliases={"en": ["wheat powder"]}))
        found = wikidata.propose(self.things(), [candidate("wheat powder", "Q9", "edible powder")])
        self.assertEqual("wheat powder", found[0].via)

    def test_a_chosen_item_is_taken_even_when_it_is_no_food_by_class(self):
        chosen = [{"thing": "ingredient/flour", "id": "Q9", "why": "Read and chosen."}]
        plan = wikidata.plan(self.things(), [candidate("grain powder", "Q9", "edible powder", {"es": "harina"})], SOURCE, LANGUAGES, (), chosen)
        self.assertEqual("Q9", plan.changes[0].same_as["id"])
        self.assertEqual({"es": "harina"}, plan.changes[0].names)

    def test_a_chosen_item_that_was_not_fetched_is_reported(self):
        chosen = [{"thing": "ingredient/flour", "id": "Q9", "why": "Read and chosen."}]
        plan = wikidata.plan(self.things(), [], SOURCE, LANGUAGES, (), chosen)
        self.assertEqual("chosen-not-fetched", plan.skipped[0].why)

    def test_a_choice_settles_an_ambiguous_label(self):
        entities = [entity("butter", "Q34172"), entity("butter", "Q99999")]
        chosen = [{"thing": "ingredient/butter", "id": "Q34172", "why": "The dairy product."}]
        plan = wikidata.plan(self.things(), entities, SOURCE, LANGUAGES, (), chosen)
        self.assertEqual("Q34172", plan.changes[0].same_as["id"])
        self.assertEqual([], [skip for skip in plan.skipped if skip.why == "ambiguous"])

    def test_the_query_for_a_second_pass_asks_for_descriptions_and_any_class(self):
        text = wikidata_fetch.query_any(["dill"], ("es",))
        self.assertIn("schema:description", text)
        self.assertNotIn("wd:Q2095", text)

    def test_a_sparql_answer_keeps_the_description(self):
        answer = {"results": {"bindings": [
            {"item": {"value": "http://www.wikidata.org/entity/Q59659860"}, "enLabel": {"value": "dill"}, "desc": {"value": "herb"}}]}}
        found = wikidata_fetch.entities(answer, food=False)
        self.assertEqual("herb", found[0]["description"])
        self.assertFalse(found[0]["food"])


if __name__ == "__main__":
    unittest.main()
