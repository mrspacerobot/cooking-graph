"""The probe runner: a probe the graph answers, one it does not, and the held-back rule."""

import unittest

from tests.small_kitchen import SmallKitchen
from tools import check, names, probes

ANSWERED = "probes/dish-probe/buttered-onions.json"
OTHER = "probes/dish-probe/creamed-onions.json"


class PlainWords(unittest.TestCase):
    def test_case_and_accents_do_not_matter(self):
        self.assertEqual("saute", names.plain("Sauté"))

    def test_a_joined_letter_is_read_as_two(self):
        self.assertEqual("boeuf bourguignon", names.plain("Bœuf Bourguignon"))

    def test_hyphens_and_apostrophes_are_spaces(self):
        self.assertEqual("soupe a l oignon", names.plain("Soupe à l'oignon"))
        self.assertEqual("court bouillon", names.plain("court-bouillon"))


class TheHeldBackRule(unittest.TestCase):
    def ids(self, count):
        return ["dish-probe/dish-%d" % number for number in range(count)]

    def test_one_in_five_is_held_back(self):
        self.assertEqual(2, len(probes.held_back_ids(self.ids(10))))
        self.assertEqual(1, len(probes.held_back_ids(self.ids(5))))
        self.assertEqual(1, len(probes.held_back_ids(self.ids(9))))

    def test_a_batch_under_five_holds_nothing_back(self):
        self.assertEqual(set(), probes.held_back_ids(self.ids(4)))

    def test_the_choice_does_not_depend_on_the_order(self):
        forwards = probes.held_back_ids(self.ids(10))
        backwards = probes.held_back_ids(list(reversed(self.ids(10))))
        self.assertEqual(forwards, backwards)

    def test_the_choice_is_the_same_every_time(self):
        chosen = probes.held_back_ids(["dish-probe/a", "dish-probe/b", "dish-probe/c", "dish-probe/d", "dish-probe/e"])
        self.assertEqual({"dish-probe/a"}, chosen)


class ProbeRunnerTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def run_probes(self):
        things, issues = check.read_repository(self.kitchen.root)
        self.assertEqual([], issues)
        return probes.run(things)

    def answer(self, result, path):
        probe_id = self.kitchen.files[path]["id"]
        for answer in result.growing + result.held_back:
            if answer.probe_id == probe_id:
                return answer
        raise AssertionError("no answer for " + probe_id)


class Answering(ProbeRunnerTest):
    def test_a_probe_the_graph_answers(self):
        answer = self.answer(self.run_probes(), ANSWERED)
        self.assertTrue(answer.answered)
        self.assertEqual([], answer.missing_techniques)
        self.assertEqual([], answer.missing_ingredients)

    def test_a_probe_the_graph_does_not_answer(self):
        def ask_for_more(probe):
            probe["techniques"] = ["sweat", "caramelize"]
            probe["ingredients"] = ["onion", "gruyere"]

        self.kitchen.change(OTHER, ask_for_more)
        answer = self.answer(self.run_probes(), OTHER)
        self.assertFalse(answer.answered)
        self.assertEqual(["caramelize"], answer.missing_techniques)
        self.assertEqual(["gruyere"], answer.missing_ingredients)

    def test_a_preparation_answers_for_an_ingredient(self):
        self.kitchen.change(OTHER, lambda probe: probe.update(ingredients=["Roux"]))
        self.assertTrue(self.answer(self.run_probes(), OTHER).answered)

    def test_an_ingredient_does_not_answer_for_a_technique(self):
        self.kitchen.change(OTHER, lambda probe: probe.update(techniques=["butter"]))
        self.assertEqual(["butter"], self.answer(self.run_probes(), OTHER).missing_techniques)

    def test_an_alias_and_a_name_in_another_language_answer(self):
        def rename(thing):
            thing["names"]["fr"] = "Suer"
            thing["aliases"] = {"en": ["soften without colour"]}

        self.kitchen.change("graph/technique/sweat.json", rename)
        self.kitchen.change(OTHER, lambda probe: probe.update(techniques=["SUER", "Soften without colour"]))
        self.assertTrue(self.answer(self.run_probes(), OTHER).answered)

    def test_a_dish_that_is_written_is_named(self):
        result = self.run_probes()
        self.assertEqual(["dish/buttered-onions"], self.answer(result, ANSWERED).dishes)
        self.assertEqual([], self.answer(result, OTHER).dishes)


class Reporting(ProbeRunnerTest):
    def test_the_two_sets_are_counted_apart(self):
        shares = probes.shares(self.run_probes())
        self.assertEqual((4, 4), shares["growing"])
        self.assertEqual((1, 1), shares["held-back"])

    def test_the_words_of_each_set_are_counted(self):
        path = self.kitchen.held_back_path()
        self.kitchen.change(path, lambda probe: probe.update(techniques=["sweat", "flambe"], ingredients=["onion", "butter", "truffle"]))
        words = probes.word_shares(self.run_probes())
        self.assertEqual({"techniques": (1, 2), "ingredients": (2, 3)}, words["held-back"])
        self.assertEqual({"techniques": (4, 4), "ingredients": (8, 8)}, words["growing"])

    def test_the_word_counts_are_in_the_report_and_no_word_is(self):
        path = self.kitchen.held_back_path()
        self.kitchen.change(path, lambda probe: probe.update(techniques=["sweat", "flambe"], ingredients=["onion", "butter", "truffle"]))
        report = probes.report(self.run_probes())
        self.assertIn("1 of 2", report)
        self.assertIn("2 of 3", report)
        self.assertNotIn("flambe", report)
        self.assertNotIn("truffle", report)

    def test_what_a_growing_probe_lacks_is_listed(self):
        self.kitchen.change(OTHER, lambda probe: probe.update(techniques=["caramelize"]))
        report = probes.report(self.run_probes())
        self.assertIn("caramelize", report)
        self.assertIn("3 of 4", report)

    def ask_for_new_words(self):
        """Two growing probes and the held-back one ask for words the graph has no name for."""
        self.kitchen.change(OTHER, lambda probe: probe.update(techniques=["sweat", "flambe"], ingredients=["onion", "truffle"]))
        self.kitchen.change(ANSWERED, lambda probe: probe.update(techniques=["Flambé"]))
        self.kitchen.change(self.kitchen.held_back_path(), lambda probe: probe.update(techniques=["flambe", "glaze"]))

    def test_a_batch_counts_each_new_word_once_whoever_asks(self):
        self.ask_for_new_words()
        batch = probes.by_batch(self.run_probes())["sweating-1"]
        self.assertEqual(5, batch["probes"])
        self.assertEqual(2, batch["new_technique_words"])
        self.assertEqual(1, batch["new_ingredient_words"])

    def test_a_batch_gives_its_new_words_for_every_fifty_probes(self):
        self.ask_for_new_words()
        batch = probes.by_batch(self.run_probes())["sweating-1"]
        self.assertEqual(20.0, batch["technique_words_per_50"])
        self.assertEqual(10.0, batch["ingredient_words_per_50"])

    def test_a_batch_counts_its_answered_probes_in_each_set(self):
        self.ask_for_new_words()
        batch = probes.by_batch(self.run_probes())["sweating-1"]
        self.assertEqual((2, 4), batch["growing"])
        self.assertEqual((0, 1), batch["held-back"])

    def test_the_numbers_of_a_batch_name_no_word(self):
        self.ask_for_new_words()
        table = "\n".join(probes.batch_lines(self.run_probes()))
        self.assertIn("sweating-1", table)
        self.assertNotIn("glaze", table)
        self.assertNotIn("flambe", table)

    def test_the_numbers_are_kept_apart_for_each_cuisine(self):
        self.kitchen.write("graph/cuisine/japanese.json", {
            "id": "cuisine/japanese", "tier": "drafted", "names": {"en": "Japanese"}, "aliases": {}, "within": None,
        })
        fresh = dict(self.kitchen.files[OTHER])
        fresh.update(id="dish-probe/miso-soup", batch="japanese-1", dish="Miso soup", cuisine="japanese",
                     written_for="soups", techniques=["simmer"], ingredients=["miso"])
        self.kitchen.write("probes/dish-probe/miso-soup.json", fresh)
        things, issues = check.read_repository(self.kitchen.root)
        self.assertEqual([], issues)
        result = probes.run(things)
        self.assertEqual((0, 1), probes.shares(result, cuisine="japanese")["growing"])
        self.assertEqual((4, 4), probes.shares(result, cuisine="french")["growing"])
        report = probes.report(result)
        self.assertIn("By cuisine:", report)
        self.assertIn("  japanese: growing 0 of 1 (0%), held back 0 of 0", report)

    def test_one_cuisine_can_be_run_alone(self):
        self.kitchen.write("graph/cuisine/japanese.json", {
            "id": "cuisine/japanese", "tier": "drafted", "names": {"en": "Japanese"}, "aliases": {}, "within": None,
        })
        fresh = dict(self.kitchen.files[OTHER])
        fresh.update(id="dish-probe/miso-soup", batch="japanese-1", dish="Miso soup", cuisine="japanese",
                     written_for="soups", techniques=["simmer"], ingredients=["miso"])
        self.kitchen.write("probes/dish-probe/miso-soup.json", fresh)
        things, issues = check.read_repository(self.kitchen.root)
        report = probes.report(probes.run(things, cuisine="japanese"))
        self.assertIn("miso", report)
        self.assertNotIn("By cuisine:\n  french", report)
        self.assertEqual((0, 1), probes.shares(probes.run(things, cuisine="japanese"))["growing"])

    def add_a_fresh_probe(self, technique):
        fresh = dict(self.kitchen.files[OTHER])
        fresh.update(id="dish-probe/onion-fritters", batch="fresh-1", dish="Onion fritters", techniques=[technique])
        self.kitchen.write("probes/dish-probe/onion-fritters.json", fresh)

    def test_one_batch_can_be_run_alone(self):
        self.add_a_fresh_probe("deep-fry")
        self.kitchen.change(OTHER, lambda probe: probe.update(techniques=["caramelize"]))
        things, issues = check.read_repository(self.kitchen.root)
        self.assertEqual([], issues)
        report = probes.report(probes.run(things, batch="fresh-1"))
        self.assertIn("deep fry", report)
        self.assertNotIn("caramelize", report)
        self.assertEqual((0, 1), probes.shares(probes.run(things, batch="fresh-1"))["growing"])

    def test_what_a_held_back_probe_lacks_is_never_listed(self):
        path = self.kitchen.held_back_path()
        self.kitchen.change(path, lambda probe: probe.update(techniques=["flambe"]))
        result = self.run_probes()
        report = probes.report(result)
        self.assertEqual((0, 1), probes.shares(result)["held-back"])
        self.assertNotIn("flambe", report)
        self.assertNotIn(self.kitchen.files[path]["dish"], report)
        self.assertIn("0 of 1", report)


if __name__ == "__main__":
    unittest.main()
