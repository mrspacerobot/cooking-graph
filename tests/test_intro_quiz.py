"""A technique card's introduction and quiz, one failing file per rule.

A card meets a home cook with what the move is and why it matters, then a few
questions that test the idea behind it. Each test gives the small kitchen's
sweat card a sound intro and quiz, breaks one thing, and expects the checker
to name that file and that rule and nothing else.
"""

import unittest

from tests.small_kitchen import DRAFTED, SmallKitchen
from tools import check, drafting

SWEAT = "graph/technique/sweat.json"


def sound_intro():
    return {
        "what": "Sweating softens vegetables gently in a little fat without browning them.",
        "why": "Gentle heat draws out sweetness and water, so the vegetables melt into a dish instead of tasting fried.",
        "idea": "Gentle heat",
        "tier": DRAFTED,
    }


def sound_question():
    return {
        "id": "gentle-heat",
        "question": "Why is the heat kept low when you sweat an onion?",
        "choices": ["So it softens and turns sweet without browning.", "So it cooks faster.", "So the fat burns off."],
        "answer": 0,
        "because": "Low heat softens the onion and draws out its sweetness before any browning can start.",
        "tier": DRAFTED,
    }


class IntroAndQuizTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

        def fill(thing):
            thing["intro"] = sound_intro()
            thing["quiz"] = [sound_question(), sound_question()]
            thing["quiz"][1]["id"] = "recognize-result"
            thing["quiz"][1].update(
                question="Which appearance matches a sweated onion?",
                choices=["Glassy and limp without brown edges.", "Brown and crisp.", "Blackened at the edges."],
                because="Sweating softens the onion without browning it.",
            )
        fill(self.kitchen.files[SWEAT])
        self.kitchen.write(SWEAT, self.kitchen.files[SWEAT])

    def issues(self):
        return check.check_repository(self.kitchen.root)

    def expect(self, rule):
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertEqual({(SWEAT, rule)}, found)

    def break_card(self, change):
        self.kitchen.change(SWEAT, change)

    def test_a_sound_intro_and_quiz_pass(self):
        self.assertEqual([], self.issues())

    def test_an_empty_intro_and_quiz_pass(self):
        self.break_card(lambda thing: thing.update(intro=None, quiz=[]))
        self.assertEqual([], self.issues())

    def test_an_answer_past_the_last_choice(self):
        self.break_card(lambda thing: thing["quiz"][0].update(answer=3))
        self.expect("quiz-answer-out-of-range")

    def test_question_id_is_required(self):
        self.break_card(lambda thing: thing["quiz"][0].pop("id"))
        self.expect("missing-field")

    def test_question_id_is_a_slug(self):
        self.break_card(lambda thing: thing["quiz"][0].update(id="Not a slug"))
        self.expect("bad-slug")

    def test_question_ids_cannot_be_repeated(self):
        self.break_card(lambda thing: thing["quiz"][1].update(id="gentle-heat"))
        self.expect("quiz-id-twice")

    def test_a_negative_answer(self):
        self.break_card(lambda thing: thing["quiz"][0].update(answer=-1))
        self.expect("too-small")

    def test_an_answer_that_is_not_a_whole_number(self):
        self.break_card(lambda thing: thing["quiz"][0].update(answer="first"))
        self.expect("wrong-type")

    def test_fewer_than_two_choices(self):
        self.break_card(lambda thing: thing["quiz"][0].update(choices=["So it softens."], answer=0))
        self.expect("too-few")

    def test_more_than_four_choices(self):
        choices = ["It softens.", "It browns.", "It burns.", "It dries.", "It shrinks."]
        self.break_card(lambda thing: thing["quiz"][0].update(choices=choices))
        self.expect("quiz-too-many-choices")

    def test_a_choice_written_twice(self):
        self.break_card(lambda thing: thing["quiz"][0].update(choices=["It softens.", "It softens."]))
        self.expect("listed-twice")

    def test_an_empty_explanation(self):
        self.break_card(lambda thing: thing["quiz"][0].update(because=" "))
        self.expect("empty")

    def test_a_missing_explanation(self):
        self.break_card(lambda thing: thing["quiz"][0].pop("because"))
        self.expect("missing-field")

    def test_an_unknown_field_in_a_question(self):
        self.break_card(lambda thing: thing["quiz"][0].update(hint="Think of the heat."))
        self.expect("unknown-field")

    def test_a_quiz_without_an_intro(self):
        self.break_card(lambda thing: thing.update(intro=None))
        self.expect("quiz-without-intro")

    def test_an_intro_without_why(self):
        self.break_card(lambda thing: thing["intro"].pop("why"))
        self.expect("missing-field")

    def test_an_empty_named_idea(self):
        self.break_card(lambda thing: thing["intro"].update(idea=""))
        self.expect("empty")

    def test_an_intro_with_no_named_idea_passes(self):
        self.break_card(lambda thing: thing["intro"].update(idea=None))
        self.assertEqual([], self.issues())

    def test_a_number_in_a_choice(self):
        self.break_card(lambda thing: thing["quiz"][0]["choices"].append("At 150 degrees."))
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertEqual({(SWEAT, "number-in-sentence"), (SWEAT, "unit-in-sentence")}, found)

    def test_a_claim_that_food_is_safe_in_an_explanation(self):
        self.break_card(lambda thing: thing["quiz"][0].update(because="Low heat makes the onion safe to eat."))
        self.expect("claim-in-sentence")

    def test_a_doneness_claim_in_an_intro(self):
        self.break_card(lambda thing: thing["intro"].update(why="It is how you know the meat is cooked through."))
        self.expect("claim-in-sentence")

    def test_a_question_tier_that_is_not_one_of_the_five(self):
        self.break_card(lambda thing: thing["quiz"][0].update(tier="checked"))
        self.expect("not-in-tiers")

    def test_a_quiz_question_marked_reviewed_with_no_record(self):
        self.break_card(lambda thing: thing["quiz"][0].update(tier="reviewed"))
        self.expect("tier-not-earned")

    def test_an_intro_marked_reviewed_with_no_record(self):
        self.break_card(lambda thing: thing["intro"].update(tier="reviewed"))
        self.expect("tier-not-earned")

    def test_the_intro_must_come_in_the_model_order(self):
        def move_intro_last(thing):
            intro = thing.pop("intro")
            thing["intro"] = intro
        self.break_card(move_intro_last)
        found = {(issue.path, issue.rule) for issue in self.issues()}
        self.assertIn((SWEAT, "field-order"), found)


class DraftingHelpers(unittest.TestCase):
    def test_a_card_drafted_without_intro_or_quiz_has_empty_ones(self):
        card = drafting.technique("dice", "Dice", "Cuts food into even cubes.", how=["Square it.", "Cut it."],
                                  cues=[("see", "Even cubes.")], mistakes=[("Uneven.", "Cut planks first.")])
        self.assertIsNone(card["intro"])
        self.assertEqual([], card["quiz"])
        self.assertEqual(["does", "intro", "how"], list(card)[4:7])
        self.assertEqual(["mistakes", "quiz", "works_on"], list(card)[8:11])

    def test_intro_and_question_are_drafted(self):
        intro = drafting.intro("It is a cut.", "Even pieces cook evenly.", idea="Even size")
        question = drafting.question("even-size", "Why cut evenly?", ["So they cook alike.", "So they look big."], 0, "Even pieces cook alike.")
        self.assertEqual({"what": "It is a cut.", "why": "Even pieces cook evenly.", "idea": "Even size", "tier": DRAFTED}, intro)
        self.assertEqual(["id", "question", "choices", "answer", "because", "tier"], list(question))
        self.assertEqual(DRAFTED, question["tier"])
