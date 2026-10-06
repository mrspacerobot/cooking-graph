"""The writer: one way to write a file, so that every file of a kind reads the same."""

import json
import os
import unittest

from tests.small_kitchen import SmallKitchen
from tools import check, writing

SWEAT = "graph/technique/sweat.json"


class OneWayToWriteAFile(unittest.TestCase):
    def test_a_short_object_stays_on_one_line(self):
        text = writing.as_text({"amount": {"value": 2, "unit": "piece"}})
        self.assertEqual('{\n  "amount": {"value": 2, "unit": "piece"}\n}\n', text)

    def test_a_statement_takes_one_line_in_its_list(self):
        text = writing.as_text({"works_on": [{"thing": "ingredient/onion", "tier": "drafted"}]})
        self.assertEqual('{\n  "works_on": [\n    {"thing": "ingredient/onion", "tier": "drafted"}\n  ]\n}\n', text)

    def test_a_list_of_plain_words_stays_on_one_line(self):
        text = writing.as_text({"contains": ["fact/dairy", "fact/egg"], "free_of": []})
        self.assertEqual('{\n  "contains": ["fact/dairy", "fact/egg"],\n  "free_of": []\n}\n', text)

    def test_sentences_that_do_not_fit_on_a_line_take_a_line_each(self):
        first = "Warm the fat in a wide pan over low heat until it runs."
        second = "Stir now and then, so that nothing sits long enough to colour."
        text = writing.as_text({"how": [first, second]})
        self.assertEqual('{\n  "how": [\n    "%s",\n    "%s"\n  ]\n}\n' % (first, second), text)

    def test_a_part_with_its_options_stays_on_one_line(self):
        part = {"role": "fat", "options": ["ingredient/butter", "ingredient/olive-oil"], "tier": "drafted"}
        text = writing.as_text({"parts": [part]})
        expected = '{"role": "fat", "options": ["ingredient/butter", "ingredient/olive-oil"], "tier": "drafted"}'
        self.assertEqual('{\n  "parts": [\n    %s\n  ]\n}\n' % expected, text)

    def test_short_aliases_stay_on_one_line(self):
        text = writing.as_text({"aliases": {"en": ["chicken broth"], "fr": ["fond blanc de volaille"]}})
        self.assertEqual('{\n  "aliases": {"en": ["chicken broth"], "fr": ["fond blanc de volaille"]}\n}\n', text)

    def test_a_long_list_of_ids_is_wrapped_like_a_paragraph(self):
        facts = ["fact/number-%d" % number for number in range(12)]
        lines = writing.as_text({"free_of": facts}).split("\n")
        self.assertEqual('  "free_of": [', lines[1])
        self.assertTrue(lines[2].startswith('    "fact/number-0", "fact/number-1", '))
        self.assertTrue(all(len(line) <= writing.WIDTH for line in lines))

    def test_what_does_not_fit_on_a_line_is_broken_up(self):
        long_sentence = "A cue that runs on and on for so long that the object which holds it can never sit on a single line of the file."
        text = writing.as_text({"cue": {"sense": "see", "text": long_sentence}})
        self.assertEqual('{\n  "cue": {\n    "sense": "see",\n    "text": "%s"\n  }\n}\n' % long_sentence, text)

    def test_letters_with_accents_are_written_as_they_are(self):
        self.assertIn("Sauté", writing.as_text({"names": {"en": "Sauté"}}))

    def test_what_is_written_reads_back_the_same(self):
        thing = {"id": "dish/x", "parts": [{"role": "main", "options": ["ingredient/egg"], "tier": "drafted"}], "n": None}
        self.assertEqual(thing, json.loads(writing.as_text(thing)))


class TidyFiles(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def test_the_small_kitchen_is_tidy(self):
        self.assertEqual([], check.check_repository(self.kitchen.root))

    def test_a_file_written_another_way_is_an_issue(self):
        content = self.kitchen.files[SWEAT]
        self.kitchen.write_text(SWEAT, json.dumps(content, indent=4))
        found = {(issue.path, issue.rule) for issue in check.check_repository(self.kitchen.root)}
        self.assertEqual({(SWEAT, "not-tidy")}, found)

    def test_tidy_rewrites_it(self):
        content = self.kitchen.files[SWEAT]
        self.kitchen.write_text(SWEAT, json.dumps(content, indent=4))
        self.assertEqual([SWEAT], writing.tidy(self.kitchen.root))
        self.assertEqual([], check.check_repository(self.kitchen.root))

    def test_a_thing_is_written_to_the_place_its_id_names(self):
        leek = dict(self.kitchen.files["graph/ingredient/onion.json"])
        leek["id"] = "ingredient/leek"
        leek["names"] = {"en": "Leek"}
        path = writing.write_thing(self.kitchen.root, leek)
        self.assertEqual("graph/ingredient/leek.json", path)
        self.assertTrue(os.path.exists(os.path.join(self.kitchen.root, path)))
        self.assertEqual([], check.check_repository(self.kitchen.root))


class FieldOrder(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def test_fields_out_of_the_order_of_the_model(self):
        content = dict(self.kitchen.files[SWEAT])
        content["does"] = content.pop("does")
        self.kitchen.write(SWEAT, content)
        found = {(issue.path, issue.rule) for issue in check.check_repository(self.kitchen.root)}
        self.assertEqual({(SWEAT, "field-order")}, found)


if __name__ == "__main__":
    unittest.main()
