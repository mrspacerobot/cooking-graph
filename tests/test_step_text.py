"""The reference for the text of a step: how it is read and how it is written for the foods in use."""

import unittest

from tools import step_text

NAMES = {"egg": "Egg", "butter": "Butter", "cream": "Cream", "mustard": "Dijon mustard", "onion": "Onion", "shallot": "Shallot"}


def written(text, left_out=(), swaps=None):
    swaps = swaps or {}

    def name_of(mention):
        return swaps.get(mention.part, NAMES[mention.part])

    pieces, problems = step_text.parse(text)
    assert not problems, problems
    return step_text.render(pieces, name_of, left_out, step_text.PROPER_NAME_WORDS)


class ReadingTest(unittest.TestCase):
    def problems(self, text):
        return step_text.parse(text)[1]

    def test_good_text_has_no_problem(self):
        self.assertEqual([], self.problems("Melt the {butter} [cream: and the {cream}] now."))

    def test_an_unclosed_placeholder_is_a_problem(self):
        self.assertTrue(self.problems("Melt the {butter now."))

    def test_a_stray_bracket_is_a_problem(self):
        self.assertTrue(self.problems("Melt the butter] now."))

    def test_an_unclosed_clause_is_a_problem(self):
        self.assertTrue(self.problems("Melt [cream: the {cream} now."))

    def test_a_clause_inside_a_clause_is_a_problem(self):
        self.assertTrue(self.problems("[cream: a [egg: b] c]"))

    def test_a_placeholder_must_be_a_part_and_perhaps_an_ingredient(self):
        self.assertTrue(self.problems("Melt the {Butter}."))
        self.assertEqual([], self.problems("Melt the {roux.butter}."))


class RenderingTest(unittest.TestCase):
    TEXT = "Stir in the cold {butter} [cream: and the {cream}] to stop the cooking."

    def test_a_kept_clause_reads_without_its_brackets(self):
        self.assertEqual("Stir in the cold butter and the cream to stop the cooking.", written(self.TEXT))

    def test_a_left_out_clause_goes_with_the_space_before_it(self):
        self.assertEqual("Stir in the cold butter to stop the cooking.", written(self.TEXT, left_out=["cream"]))

    def test_a_swapped_food_is_written_by_its_name(self):
        text = written(self.TEXT, swaps={"cream": "Creme fraiche"})
        self.assertEqual("Stir in the cold butter and the creme fraiche to stop the cooking.", text)

    def test_a_proper_name_keeps_its_capital_inside_a_sentence(self):
        self.assertEqual("Whisk in the Dijon mustard.", written("Whisk in the {mustard}."))

    def test_a_name_at_the_start_of_a_sentence_gets_a_capital(self):
        self.assertEqual("Done. Butter melts.", written("Done. {butter} melts.", swaps={"butter": "butter"}))

    def test_an_article_agrees_with_the_name_in_use(self):
        self.assertEqual("Add an onion.", written("Add a {onion}."))
        self.assertEqual("Add a shallot.", written("Add an {onion}.", swaps={"onion": "Shallot"}))

    def test_a_whole_step_that_is_a_clause_is_empty_when_left_out(self):
        self.assertEqual("", written("[cream: Whip the {cream}.]", left_out=["cream"]))

    def test_a_clause_after_a_comma_keeps_the_sentence_whole(self):
        text = "Serve at once[cream: , with a swirl of {cream}]."
        self.assertEqual("Serve at once.", written(text, left_out=["cream"]))
        self.assertEqual("Serve at once, with a swirl of cream.", written(text))

    def test_a_chain_of_optional_items_closes_up(self):
        text = "Put in the {egg}[butter: , {butter}] [cream: and {cream}] now."
        self.assertEqual("Put in the egg, butter and cream now.", written(text))
        self.assertEqual("Put in the egg and cream now.", written(text, left_out=["butter"]))
        self.assertEqual("Put in the egg, butter now.", written(text, left_out=["cream"]))


class PluralTest(unittest.TestCase):
    def plural_name(self, mention):
        names = {"egg": ("Egg", "Eggs"), "butter": ("Butter", "Butter")}
        single, plural = names[mention.part]
        return plural if mention.plural else single

    def written(self, text):
        pieces, problems = step_text.parse(text)
        self.assertEqual([], problems)
        return step_text.render(pieces, self.plural_name, [], step_text.PROPER_NAME_WORDS)

    def test_a_plural_placeholder_reads_with_a_colon(self):
        pieces, problems = step_text.parse("Crack the {egg:plural} and the {egg.sunny:plural}.")
        self.assertEqual([], problems)
        self.assertEqual([(True, None), (True, "sunny")], [(one.plural, one.slug) for one, _ in step_text.mentions_of(pieces)])

    def test_another_word_after_the_colon_is_a_problem(self):
        self.assertTrue(step_text.parse("Crack the {egg:many}.")[1])

    def test_the_plural_is_written_for_a_plural_placeholder(self):
        self.assertEqual("While the eggs still look wet, stir in the butter.", self.written("While the {egg:plural} still look wet, stir in the {butter}."))

    def test_the_plural_keeps_the_capital_at_the_start_of_a_sentence(self):
        self.assertEqual("Done. Eggs go in.", self.written("Done. {egg:plural} go in."))

    def test_an_uncountable_food_asked_in_plural_prints_its_name(self):
        self.assertEqual("Add the butter.", self.written("Add the {butter:plural}."))
