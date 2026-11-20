import unittest

from tools import names


class PlainNamesTests(unittest.TestCase):
    def test_distinct_names_in_their_own_script_stay_distinct(self):
        self.assertNotEqual(names.plain("蛋炒饭"), names.plain("麻婆豆腐"))
        self.assertEqual(names.plain("Γύρος, πίτα"), "γύροσ πίτα")
        self.assertEqual(names.plain("ผัดไทย"), "ผัดไทย")

    def test_latin_names_keep_their_existing_plain_spelling(self):
        self.assertEqual(names.plain("Cœur d’Artichaut"), "coeur d artichaut")
