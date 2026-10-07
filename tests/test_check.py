"""The checker's rules, one failing file per rule.

Every test starts from the small kitchen, which is valid, breaks one rule in
one file, and expects the checker to name that file and that rule and nothing
else.
"""

import unittest

from tests.small_kitchen import BATCH, DRAFTED, SmallKitchen, holds, link
from tools import check, reading
from tools.rules import names_of_the_model as check_names

SWEAT = "graph/technique/sweat.json"
MINCE = "graph/technique/mince.json"
BUTTER = "graph/ingredient/butter.json"
ONION = "graph/ingredient/onion.json"
ALLIUM = "graph/ingredient/allium.json"
SKIN = "graph/ingredient/onion-skin.json"
MINCED = "graph/form/minced.json"
FRENCH = "graph/cuisine/french.json"
DISH = "graph/dish/buttered-onions.json"
RECIPE = "graph/recipe/buttered-onions.json"
ROUX = "graph/preparation/roux.json"
JUICES = "preparation/onion-juices"
PROGRAM = "graph/program/small-program.json"
PROBE = "probes/dish-probe/creamed-onions.json"
EM_DASH = chr(0x2014)  # written as a number so that this file holds none


class CheckerTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def issues(self):
        return check.check_repository(self.kitchen.root)

    def expect(self, path, rule):
        """The checker reports this rule for this file, and reports nothing else."""
        found = [(issue.path, issue.rule) for issue in self.issues()]
        self.assertIn((path, rule), found)
        self.assertEqual({(path, rule)}, set(found))

    def break_file(self, path, change):
        self.kitchen.change(path, change)


class TheSmallKitchenIsValid(CheckerTest):
    def test_no_issue_before_anything_is_broken(self):
        self.assertEqual([], self.issues())


class ReadingFiles(CheckerTest):
    def test_a_file_that_is_not_json(self):
        self.kitchen.write_text(SWEAT, "{ not json")
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertIn((SWEAT, "not-json"), found)

    def test_a_field_written_twice(self):
        self.kitchen.write_text(FRENCH, '{"id": "cuisine/french", "id": "cuisine/french"}')
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertIn((FRENCH, "duplicate-field"), found)

    def test_a_folder_that_is_no_kind(self):
        self.kitchen.write("graph/gadget/whisk.json", {"id": "gadget/whisk"})
        self.expect("graph/gadget/whisk.json", "bad-path")

    def test_a_file_outside_a_kind_folder(self):
        self.kitchen.write("graph/loose.json", {"id": "loose"})
        self.expect("graph/loose.json", "bad-path")

    def test_a_kind_in_the_wrong_home(self):
        self.kitchen.write("probes/cuisine/italian.json", {"id": "cuisine/italian"})
        self.expect("probes/cuisine/italian.json", "bad-path")

    def test_an_id_that_is_not_the_path(self):
        self.break_file(SWEAT, lambda thing: thing.update(id="technique/sweating"))
        self.expect(SWEAT, "bad-id")

    def test_a_slug_that_is_not_lowercase(self):
        self.kitchen.write("graph/fact/Soy.json", {"id": "fact/Soy"})
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertIn(("graph/fact/Soy.json", "bad-id"), found)


class Shapes(CheckerTest):
    def test_an_unknown_field(self):
        self.break_file(SWEAT, lambda thing: thing.update(colour="blue"))
        self.expect(SWEAT, "unknown-field")

    def test_an_unknown_field_deep_inside(self):
        self.break_file(SWEAT, lambda thing: thing["cues"][0].update(loud=True))
        self.expect(SWEAT, "unknown-field")

    def test_a_missing_field(self):
        self.break_file(SWEAT, lambda thing: thing.pop("does"))
        self.expect(SWEAT, "missing-field")

    def test_a_missing_field_deep_inside(self):
        self.break_file(SWEAT, lambda thing: thing["mistakes"][0].pop("fix"))
        self.expect(SWEAT, "missing-field")

    def test_a_value_of_the_wrong_type(self):
        self.break_file(SWEAT, lambda thing: thing.update(how="Stir."))
        self.expect(SWEAT, "wrong-type")

    def test_null_where_null_is_not_allowed(self):
        self.break_file(SWEAT, lambda thing: thing.update(does=None))
        self.expect(SWEAT, "wrong-type")

    def test_an_empty_text(self):
        self.break_file(SWEAT, lambda thing: thing.update(does="  "))
        self.expect(SWEAT, "empty")

    def test_a_tier_that_is_not_one_of_the_five(self):
        self.break_file(SWEAT, lambda thing: thing.update(tier="approved"))
        self.expect(SWEAT, "not-in-tiers")

    def test_a_statement_tier_that_is_not_one_of_the_five(self):
        self.break_file(SWEAT, lambda thing: thing["works_on"][0].update(tier="fine"))
        self.expect(SWEAT, "not-in-tiers")

    def test_a_word_outside_its_closed_list(self):
        self.break_file(SWEAT, lambda thing: thing["cues"][0].update(sense="guess"))
        self.expect(SWEAT, "not-in-senses")

    def test_a_reference_to_nothing(self):
        self.break_file(SWEAT, lambda thing: thing.update(works_on=[link("ingredient/leek")]))
        self.expect(SWEAT, "missing-reference")

    def test_a_reference_to_the_wrong_kind(self):
        self.break_file(SWEAT, lambda thing: thing.update(works_on=[link("cuisine/french")]))
        self.expect(SWEAT, "wrong-kind")

    def test_a_reference_that_is_no_id(self):
        self.break_file(SWEAT, lambda thing: thing.update(works_on=[link("the onion")]))
        self.expect(SWEAT, "bad-id")

    def test_the_same_thing_listed_twice(self):
        self.break_file(RECIPE, lambda thing: thing.update(equipment=["equipment/pan", "equipment/pan"]))
        self.expect(RECIPE, "listed-twice")

    def test_a_need_with_a_role_outside_the_list(self):
        self.break_file(SWEAT, lambda thing: thing["needs"][0].update(role="gadget"))
        self.expect(SWEAT, "not-in-need_roles")

    def test_a_need_that_names_a_dish(self):
        self.break_file(SWEAT, lambda thing: thing["needs"][0].update(options=["dish/buttered-onions"]))
        self.expect(SWEAT, "wrong-kind")

    def test_a_safety_point_outside_the_list(self):
        def worry(thing):
            thing["steps"][0]["safety_points"] = ["looks-fine"]

        self.break_file(RECIPE, worry)
        self.expect(RECIPE, "not-in-safety_points")

    def test_a_size_in_a_unit_that_is_no_length(self):
        def weigh(thing):
            thing["size"][0]["length"] = {"value": 2, "unit": "gram"}

        self.break_file(MINCED, weigh)
        self.expect(MINCED, "not-in-length_units")

    def test_a_form_on_a_line_that_is_no_form(self):
        def name_a_technique(thing):
            thing["ingredients"][0]["forms"] = ["technique/mince"]

        self.break_file(RECIPE, name_a_technique)
        self.expect(RECIPE, "wrong-kind")

    def test_a_preparation_that_stands_in_without_a_caveat(self):
        self.break_file(ROUX, lambda thing: thing["stands_in_for"][0].pop("caveat"))
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertIn((ROUX, "missing-field"), found)

    def test_a_technique_without_a_cue(self):
        self.break_file(SWEAT, lambda thing: thing.update(cues=[]))
        self.expect(SWEAT, "too-few")

    def test_a_technique_without_a_mistake(self):
        self.break_file(SWEAT, lambda thing: thing.update(mistakes=[]))
        self.expect(SWEAT, "too-few")

    def test_a_technique_with_no_how(self):
        self.break_file(SWEAT, lambda thing: thing.update(how=[]))
        self.expect(SWEAT, "too-few")

    def test_an_amount_with_a_unit_outside_the_list(self):
        def use_a_handful(thing):
            thing["ingredients"][0]["amount"] = {"value": 1, "unit": "handful"}

        self.break_file(RECIPE, use_a_handful)
        self.expect(RECIPE, "not-in-amount_units")

    def test_an_amount_that_is_no_quantity(self):
        def use_words(thing):
            thing["ingredients"][0]["amount"] = {"value": "some", "unit": "gram"}

        self.break_file(RECIPE, use_words)
        self.expect(RECIPE, "bad-quantity")

    def test_a_range_that_runs_backwards(self):
        def reverse(thing):
            thing["steps"][0]["time"] = {"from": 10, "to": 8, "unit": "minute"}

        self.break_file(RECIPE, reverse)
        self.expect(RECIPE, "bad-quantity")

    def test_a_level_number_below_one(self):
        def zero(thing):
            thing["courses"][0]["skills"][0]["levels"][0]["number"] = 0

        self.break_file(PROGRAM, zero)
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertIn((PROGRAM, "too-small"), found)


class Names(CheckerTest):
    def test_no_english_name(self):
        self.break_file(SWEAT, lambda thing: thing.update(names={"fr": "Suer"}))
        self.expect(SWEAT, "english-name-missing")

    def test_a_language_outside_the_list(self):
        self.break_file(SWEAT, lambda thing: thing["names"].update(xx="Sweat"))
        self.expect(SWEAT, "not-in-languages")

    def test_another_script_without_its_romanization(self):
        self.break_file(SWEAT, lambda thing: thing["names"].update(fr="出汁"))
        self.expect(SWEAT, "romanization-missing")

    def test_another_script_with_its_romanization(self):
        def both(thing):
            thing["names"]["fr"] = "出汁"
            thing["names"]["fr-Latn"] = "dashi"

        self.break_file(SWEAT, both)
        self.assertEqual([], self.issues())

    def test_two_things_of_a_kind_with_one_name(self):
        self.break_file(MINCE, lambda thing: thing.update(aliases={"en": ["sweat"]}))
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertEqual({(MINCE, "same-name-twice"), (SWEAT, "same-name-twice")}, found)


class Sentences(CheckerTest):
    def test_a_number_in_a_sentence(self):
        self.break_file(SWEAT, lambda thing: thing.update(does="Softens onions in 10 turns."))
        self.expect(SWEAT, "number-in-sentence")

    def test_a_number_word_in_a_sentence(self):
        self.break_file(SWEAT, lambda thing: thing.update(does="Softens three onions."))
        self.expect(SWEAT, "number-in-sentence")

    def test_a_unit_in_a_sentence(self):
        self.break_file(SWEAT, lambda thing: thing.update(does="Softens onions for a few minutes."))
        self.expect(SWEAT, "unit-in-sentence")

    def test_a_temperature_in_a_sentence(self):
        self.break_file(SWEAT, lambda thing: thing.update(does="Softens onions at low degrees."))
        self.expect(SWEAT, "unit-in-sentence")

    def test_a_claim_that_food_is_cooked_through(self):
        self.break_file(SWEAT, lambda thing: thing.update(does="Cooks until cooked through."))
        self.expect(SWEAT, "claim-in-sentence")

    def test_a_claim_that_food_is_safe(self):
        def claim(thing):
            thing["steps"][0]["text"] = "Now it is safe to eat."

        self.break_file(RECIPE, claim)
        self.expect(RECIPE, "claim-in-sentence")

    def test_a_word_that_only_looks_like_a_unit(self):
        self.break_file(SWEAT, lambda thing: thing.update(does="Softens the second onion in a cupboard."))
        self.assertEqual([], self.issues())

    def test_an_em_dash_in_a_file_of_the_graph(self):
        self.break_file(SWEAT, lambda thing: thing.update(does="Softens" + EM_DASH + "slowly."))
        self.expect(SWEAT, "em-dash")

    def test_an_em_dash_in_any_other_file(self):
        self.kitchen.write_text("docs/notes.md", "A note " + EM_DASH + " with a dash.\n")
        self.expect("docs/notes.md", "em-dash")


class Trust(CheckerTest):
    def test_a_tier_nobody_earned(self):
        self.break_file(SWEAT, lambda thing: thing.update(tier="reviewed"))
        self.expect(SWEAT, "tier-not-earned")

    def test_a_statement_tier_nobody_earned(self):
        self.break_file(SWEAT, lambda thing: thing["works_on"][0].update(tier="sourced"))
        self.expect(SWEAT, "tier-not-earned")

    def test_a_safety_fact_nobody_verified(self):
        self.break_file(BUTTER, lambda thing: thing["safety"].update(state="verified"))
        self.expect(BUTTER, "safety-not-earned")


DAIRY = "graph/fact/dairy.json"
LAW = "graph/source/kitchen-law.json"


def regulated(tier="sourced", standing="mandatory"):
    return {
        "where": "european-union",
        "source": "source/kitchen-law",
        "name": "Milk and products thereof",
        "standing": standing,
        "exemptions": None,
        "note": None,
        "tier": tier,
    }


class Sources(CheckerTest):
    def test_a_fact_taken_from_a_source_may_be_sourced(self):
        self.break_file(DAIRY, lambda thing: thing.update(tier="sourced", regulated=[regulated()]))
        self.assertEqual([], self.issues())

    def test_a_fact_that_names_no_source_may_not_be_sourced(self):
        self.break_file(DAIRY, lambda thing: thing.update(tier="sourced"))
        self.expect(DAIRY, "tier-not-earned")

    def test_a_fact_whose_rows_are_all_drafted_may_not_be_sourced(self):
        self.break_file(DAIRY, lambda thing: thing.update(tier="sourced", regulated=[regulated("drafted")]))
        self.expect(DAIRY, "tier-not-earned")

    def test_a_drafted_fact_may_carry_a_sourced_row(self):
        self.break_file(DAIRY, lambda thing: thing.update(regulated=[regulated()]))
        self.assertEqual([], self.issues())

    def test_a_fact_may_be_mandatory_and_recommended_in_the_same_place(self):
        self.break_file(DAIRY, lambda thing: thing.update(regulated=[regulated(), regulated(standing="recommended")]))
        self.assertEqual([], self.issues())

    def test_a_fact_regulated_twice_in_the_same_place_with_the_same_standing(self):
        self.break_file(DAIRY, lambda thing: thing.update(regulated=[regulated(), regulated()]))
        self.expect(DAIRY, "regulated-twice")

    def test_a_standing_that_is_not_one_of_the_words(self):
        self.break_file(DAIRY, lambda thing: thing.update(regulated=[regulated(standing="advised")]))
        self.expect(DAIRY, "not-in-standings")

    def test_a_fact_that_does_not_say_what_it_concerns(self):
        self.break_file(DAIRY, lambda thing: thing.pop("concern"))
        self.expect(DAIRY, "missing-field")

    def test_a_fact_may_not_be_more_than_sourced(self):
        self.break_file(DAIRY, lambda thing: thing.update(tier="reviewed", regulated=[regulated()]))
        self.expect(DAIRY, "tier-not-earned")

    def test_nothing_but_a_fact_may_be_sourced(self):
        self.break_file(BUTTER, lambda thing: thing.update(tier="sourced"))
        self.expect(BUTTER, "tier-not-earned")

    def test_a_source_that_was_read_on_no_date(self):
        self.break_file(LAW, lambda thing: thing.update(read_on="last week"))
        self.expect(LAW, "bad-date")

    def test_a_source_read_on_a_day_that_does_not_exist(self):
        self.break_file(LAW, lambda thing: thing.update(read_on="2026-13-45"))
        self.expect(LAW, "bad-date")

    def test_a_source_whose_use_is_not_one_of_the_answers(self):
        self.break_file(LAW, lambda thing: thing.update(commercial_use="probably"))
        self.expect(LAW, "not-in-commercial_uses")

    def test_a_source_with_no_web_address(self):
        self.break_file(LAW, lambda thing: thing.update(url="the library"))
        self.expect(LAW, "bad-url")

    def test_a_note_about_a_source_may_hold_numbers(self):
        self.break_file(LAW, lambda thing: thing.update(reuse="Version 3.0 allows it, 14 items were taken."))
        self.assertEqual([], self.issues())

    def test_a_fact_regulated_under_a_source_that_does_not_exist(self):
        def nowhere(thing):
            thing["regulated"] = [dict(regulated("drafted"), source="source/hearsay")]

        self.break_file(DAIRY, nowhere)
        self.expect(DAIRY, "missing-reference")


class Safety(CheckerTest):
    def test_a_fact_left_unanswered(self):
        self.break_file(BUTTER, lambda thing: thing["safety"].update(free_of=[]))
        self.expect(BUTTER, "fact-not-answered")

    def test_a_fact_answered_both_ways(self):
        self.break_file(BUTTER, lambda thing: thing["safety"].update(free_of=["fact/gluten", "fact/dairy"]))
        self.expect(BUTTER, "fact-answered-twice")

    def test_a_member_that_holds_what_its_class_does_not(self):
        self.break_file(ONION, lambda thing: thing["safety"].update(contains=[holds("fact/gluten")], free_of=["fact/dairy"]))
        self.expect(ONION, "class-less-strict")

    def test_a_fact_held_without_its_basis(self):
        self.break_file(BUTTER, lambda thing: thing["safety"]["contains"][0].pop("basis"))
        self.expect(BUTTER, "missing-field")

    def test_a_fact_held_that_does_not_say_whether_it_is_certain(self):
        self.break_file(BUTTER, lambda thing: thing["safety"]["contains"][0].update(certain="maybe"))
        self.expect(BUTTER, "wrong-type")

    def test_a_part_that_holds_what_its_whole_does_not(self):
        self.break_file(SKIN, lambda thing: thing["safety"].update(contains=[holds("fact/gluten")], free_of=["fact/dairy"]))
        self.expect(SKIN, "whole-less-strict")


class Recipes(CheckerTest):
    def test_a_step_that_works_on_something_not_listed(self):
        def add_flour(thing):
            thing["steps"][0]["with"].append("ingredient/flour")

        self.break_file(RECIPE, add_flour)
        self.expect(RECIPE, "step-works-on-unlisted")

    def test_a_step_may_work_on_what_the_recipe_makes(self):
        def make_the_roux(thing):
            thing["makes"] = "preparation/roux"
            thing["ingredients"] = [
                {"thing": "ingredient/butter", "amount": {"value": 20, "unit": "gram"}, "forms": [], "part": "butter"},
                {"thing": "ingredient/flour", "amount": {"value": 20, "unit": "gram"}, "forms": [], "part": "flour"},
            ]
            thing["steps"][0]["works_on"] = []
            thing["steps"][0]["with"] = ["ingredient/butter", "ingredient/flour"]
            thing["steps"].append(dict(thing["steps"][0], works_on=[], **{"with": ["preparation/roux"]}))

        self.break_file(RECIPE, make_the_roux)
        self.assertEqual([], self.issues())

    def second_step_on_the_juices(self, thing, first_step_makes):
        thing["steps"][0]["makes"] = first_step_makes
        thing["steps"].append(dict(thing["steps"][0], works_on=[JUICES], makes=[]))

    def test_a_step_may_work_on_what_an_earlier_step_left_behind(self):
        self.break_file(RECIPE, lambda thing: self.second_step_on_the_juices(thing, [JUICES]))
        self.assertEqual([], self.issues())

    def test_a_step_that_works_on_what_no_step_left_behind(self):
        self.break_file(RECIPE, lambda thing: self.second_step_on_the_juices(thing, []))
        self.expect(RECIPE, "step-works-on-unlisted")

    def test_a_step_that_works_on_what_a_later_step_makes(self):
        def too_early(thing):
            thing["steps"][0]["works_on"].append(JUICES)
            thing["steps"].append(dict(thing["steps"][0], works_on=["ingredient/onion"], makes=[JUICES]))

        self.break_file(RECIPE, too_early)
        self.expect(RECIPE, "step-works-on-unlisted")

    def test_a_by_product_listed_as_an_ingredient(self):
        def list_the_juices(thing):
            juices = {"thing": JUICES, "amount": {"value": 1, "unit": "tablespoon"}, "forms": [], "part": "onion"}
            thing["ingredients"].append(juices)
            thing["steps"][0]["works_on"].append(JUICES)

        self.break_file(RECIPE, list_the_juices)
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertIn((RECIPE, "by-product-as-ingredient"), found)

    def test_a_by_product_named_as_a_part_of_a_dish(self):
        juices = {"id": "juices", "role": "liquid", "options": [JUICES], "optional": True, "tier": DRAFTED}
        self.break_file(DISH, lambda thing: thing["parts"].append(juices))
        self.expect(DISH, "by-product-as-part")

    def test_an_ingredient_no_step_uses(self):
        def forget_the_butter(thing):
            thing["steps"][0]["with"] = []

        self.break_file(RECIPE, forget_the_butter)
        self.expect(RECIPE, "ingredient-never-used")

    def test_a_line_that_fills_a_part_the_dish_does_not_have(self):
        def fill_the_sauce(thing):
            thing["ingredients"][1]["part"] = "sauce"

        self.break_file(RECIPE, fill_the_sauce)
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertIn((RECIPE, "part-unknown"), found)

    def test_a_line_that_is_no_option_of_its_part(self):
        def butter_as_the_onion(thing):
            thing["ingredients"][1]["part"] = "onion"

        self.break_file(RECIPE, butter_as_the_onion)
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertIn((RECIPE, "not-an-option-of-its-part"), found)

    def test_a_part_no_line_fills(self):
        def forget_the_roux(thing):
            thing["ingredients"] = thing["ingredients"][:1]
            thing["steps"][0]["with"] = []

        self.break_file(RECIPE, forget_the_roux)
        self.expect(RECIPE, "part-not-filled")

    def test_an_optional_part_may_stay_unfilled(self):
        self.assertEqual([], self.issues())
        self.break_file(DISH, lambda thing: thing["parts"][2].update(optional=False))
        self.expect(RECIPE, "part-not-filled")

    def test_two_parts_of_a_dish_with_one_id(self):
        self.break_file(DISH, lambda thing: thing["parts"][2].update(id="onion"))
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertIn((DISH, "part-id-twice"), found)

    def test_a_step_that_works_on_what_its_technique_does_not(self):
        def sweat_the_butter(thing):
            thing["steps"][0]["works_on"].append("ingredient/butter")

        self.break_file(RECIPE, sweat_the_butter)
        self.expect(RECIPE, "not-what-the-technique-works-on")

    def test_a_step_may_work_on_a_member_of_a_narrower_group(self):
        covered = [issue for issue in self.issues() if issue.rule == "not-what-the-technique-works-on"]
        self.assertEqual([], covered)

    def test_a_step_with_a_technique_that_does_not_exist(self):
        def name_a_ghost(thing):
            thing["steps"][0]["technique"] = "technique/caramelize"

        self.break_file(RECIPE, name_a_ghost)
        self.expect(RECIPE, "missing-reference")

    def test_a_step_that_works_on_an_equipment(self):
        def cook_the_pan(thing):
            thing["steps"][0]["works_on"].append("equipment/pan")

        self.break_file(RECIPE, cook_the_pan)
        self.expect(RECIPE, "wrong-kind")


class Order(CheckerTest):
    def test_two_techniques_that_each_come_after_the_other(self):
        def after_mince(thing):
            thing["comes_after"] = [link("technique/mince", why="It is a loop.")]

        self.break_file(SWEAT, after_mince)
        found = {issue.rule for issue in self.issues()}
        self.assertEqual({"cycle"}, found)

    def test_a_cuisine_within_itself(self):
        self.break_file(FRENCH, lambda thing: thing.update(within=link("cuisine/provencal")))
        found = {issue.rule for issue in self.issues()}
        self.assertEqual({"cycle"}, found)

    def test_a_whole_that_is_part_of_its_part(self):
        self.break_file(ONION, lambda thing: thing.update(part_of=[link("ingredient/onion-skin")]))
        found = {issue.rule for issue in self.issues()}
        self.assertEqual({"cycle"}, found)

    def test_a_class_that_is_its_own_member(self):
        self.break_file(ALLIUM, lambda thing: thing.update(is_a=[link("ingredient/onion")]))
        found = {issue.rule for issue in self.issues()}
        self.assertEqual({"cycle"}, found)


class Programs(CheckerTest):
    def skill(self, thing, index):
        return thing["courses"][0]["skills"][index]

    def test_a_skill_that_comes_after_an_unknown_skill(self):
        def after_nothing(thing):
            self.skill(thing, 1)["comes_after"] = [{"skill": "frying", "tier": DRAFTED}]

        self.break_file(PROGRAM, after_nothing)
        self.expect(PROGRAM, "skill-unknown")

    def test_two_skills_with_one_slug(self):
        def same_slug(thing):
            self.skill(thing, 1)["slug"] = "sweating"
            self.skill(thing, 1)["comes_after"] = []

        self.break_file(PROGRAM, same_slug)
        self.expect(PROGRAM, "slug-twice")

    def test_levels_that_skip_a_number(self):
        def skip(thing):
            self.skill(thing, 0)["levels"][0]["number"] = 2

        self.break_file(PROGRAM, skip)
        self.expect(PROGRAM, "level-numbers")

    def test_skills_that_each_come_after_the_other(self):
        def loop(thing):
            self.skill(thing, 0)["comes_after"] = [{"skill": "mincing", "tier": DRAFTED}]

        self.break_file(PROGRAM, loop)
        self.expect(PROGRAM, "cycle")


class TheModelDocument(CheckerTest):
    """docs/model.md describes the model. When it exists, it names every kind and every field."""

    def write_document(self, leave_out=()):
        model, _ = reading.read_schema(self.kitchen.root)
        words = [word for word in check_names(model) if word not in leave_out]
        self.kitchen.write_text("docs/model.md", "# The model\n\n" + " ".join("`%s`" % word for word in words) + "\n")

    def test_a_document_that_names_everything(self):
        self.write_document()
        self.assertEqual([], self.issues())

    def test_a_document_that_forgets_a_field(self):
        self.write_document(leave_out=["safety_points"])
        self.expect("docs/model.md", "not-in-the-model-document")

    def test_a_document_that_forgets_a_kind(self):
        self.write_document(leave_out=["cuisine"])
        self.expect("docs/model.md", "not-in-the-model-document")

    def test_no_document_yet_is_no_issue(self):
        self.assertEqual([], self.issues())


class Probes(CheckerTest):
    def test_a_probe_written_for_an_unknown_skill(self):
        self.break_file(PROBE, lambda probe: probe.update(written_for="frying"))
        self.expect(PROBE, "skill-unknown")

    def test_a_probe_for_a_cuisine_that_does_not_exist(self):
        self.break_file(PROBE, lambda probe: probe.update(cuisine="narnian"))
        self.expect(PROBE, "cuisine-unknown")

    def test_a_probe_for_a_cuisine_without_a_program_names_any_topic(self):
        self.kitchen.write("graph/cuisine/japanese.json", {
            "id": "cuisine/japanese", "tier": "drafted", "names": {"en": "Japanese"}, "aliases": {}, "within": None,
        })
        self.break_file(PROBE, lambda probe: probe.update(cuisine="japanese", written_for="rice"))
        self.assertEqual([], self.issues())

    def test_a_probe_for_a_cuisine_with_a_program_names_a_skill_of_that_program(self):
        self.kitchen.write("graph/cuisine/japanese.json", {
            "id": "cuisine/japanese", "tier": "drafted", "names": {"en": "Japanese"}, "aliases": {}, "within": None,
        })
        self.break_file(PROBE, lambda probe: probe.update(cuisine="japanese", written_for="sweating"))
        self.assertEqual([], self.issues())
        self.break_file(PROBE, lambda probe: probe.update(cuisine="french", written_for="rice"))
        self.expect(PROBE, "skill-unknown")

    def test_a_probe_moved_out_of_the_held_back_set(self):
        path = self.kitchen.held_back_path()
        self.break_file(path, lambda probe: probe.update(set="growing"))
        self.expect(path, "held-back-rule")

    def test_a_probe_moved_into_the_held_back_set(self):
        self.assertNotEqual(PROBE, self.kitchen.held_back_path())
        self.break_file(PROBE, lambda probe: probe.update(set="held-back"))
        self.expect(PROBE, "held-back-rule")

    def test_a_dish_drafted_towards_a_held_back_probe(self):
        path = self.kitchen.held_back_path()
        self.break_file(path, lambda probe: probe.update(dish="Buttered onions baked"))
        self.break_file(DISH, lambda thing: thing.update(aliases={"en": ["buttered onions baked"]}))
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertIn((DISH, "drafted-towards-held-back"), found)
        self.assertIn((path, "level-dish-held-back"), found)

    def test_a_preparation_drafted_towards_a_held_back_probe(self):
        path = self.kitchen.held_back_path()
        self.break_file(path, lambda probe: probe.update(dish="Brown roux"))
        self.break_file(ROUX, lambda thing: thing.update(aliases={"en": ["brown roux"]}))
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertIn((ROUX, "drafted-towards-held-back"), found)
        # The probe may no longer be held back either: what it asks about is written.
        self.assertIn((path, "held-back-rule"), found)

    def test_two_probes_about_one_dish(self):
        self.break_file(PROBE, lambda probe: probe.update(dish="Onion soup"))
        found = {issue.rule for issue in self.issues()}
        self.assertEqual({"same-dish-twice"}, found)

    def test_the_batch_of_the_small_kitchen_holds_one_probe_back(self):
        held_back = [f for f in self.kitchen.files.values() if f.get("set") == "held-back" and f["batch"] == BATCH]
        self.assertEqual(1, len(held_back))


if __name__ == "__main__":
    unittest.main()
