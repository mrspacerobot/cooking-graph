"""The merge guard: files from another worktree are copied in only when nothing clashes."""

import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest

from tests.small_kitchen import SmallKitchen
from tools import merge


class MergeTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)
        self.source = tempfile.mkdtemp(prefix="merge-source-")
        self.addCleanup(shutil.rmtree, self.source, True)

    def put(self, slug, english, aliases=(), kind="ingredient", at=None):
        template = json.loads(json.dumps(self.kitchen.files["graph/ingredient/butter.json"]))
        template.update(id=kind + "/" + slug, names={"en": english}, aliases={"en": list(aliases)} if aliases else {})
        path = os.path.join(at or self.source, "graph", kind, slug + ".json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(template, handle, indent=2)
        return path

    def run_merge(self, dry_run=False):
        return merge.merge(self.source, self.kitchen.root, dry_run=dry_run)

    def exists(self, relative):
        return os.path.exists(os.path.join(self.kitchen.root, relative))

    def test_a_new_thing_is_copied(self):
        self.put("sorrel", "Sorrel")
        result = self.run_merge()
        self.assertEqual(["graph/ingredient/sorrel.json"], result.copied)
        self.assertEqual([], result.refused)
        self.assertTrue(self.exists("graph/ingredient/sorrel.json"))

    def test_a_dry_run_copies_nothing(self):
        self.put("sorrel", "Sorrel")
        result = self.run_merge(dry_run=True)
        self.assertEqual(["graph/ingredient/sorrel.json"], result.copied)
        self.assertFalse(self.exists("graph/ingredient/sorrel.json"))

    def test_a_name_the_graph_already_holds_is_refused(self):
        self.put("unsalted-butter", "Butter")
        result = self.run_merge()
        self.assertEqual([], result.copied)
        self.assertEqual(["graph/ingredient/unsalted-butter.json"], [path for path, _ in result.refused])
        self.assertFalse(self.exists("graph/ingredient/unsalted-butter.json"))

    def test_an_alias_the_graph_already_holds_is_refused(self):
        self.put("cooking-fat", "Cooking fat", aliases=["butter"])
        self.assertEqual([], self.run_merge().copied)

    def test_a_preparation_taking_the_name_of_an_ingredient_is_refused(self):
        self.put("flour-mix", "Flour", kind="preparation")
        self.assertEqual([], self.run_merge().copied)

    def test_two_incoming_files_with_one_name_are_both_refused(self):
        self.put("sorrel", "Sorrel")
        self.put("garden-sorrel", "Sorrel")
        result = self.run_merge()
        self.assertEqual([], result.copied)
        self.assertEqual(2, len(result.refused))

    def test_a_file_that_already_exists_is_never_overwritten(self):
        self.put("butter", "Butter", aliases=["a different alias"])
        before = Path(self.kitchen.root, "graph/ingredient/butter.json").read_text(encoding="utf-8")
        result = self.run_merge()
        self.assertEqual(["graph/ingredient/butter.json"], result.changed)
        self.assertEqual([], result.copied)
        after = Path(self.kitchen.root, "graph/ingredient/butter.json").read_text(encoding="utf-8")
        self.assertEqual(before, after)

    def test_an_identical_file_is_not_news(self):
        path = self.put("sorrel", "Sorrel")
        self.run_merge()
        result = self.run_merge()
        self.assertEqual([], result.copied)
        self.assertEqual([], result.changed)
        self.assertEqual([], result.refused)

    def test_a_dish_and_a_recipe_may_share_a_name(self):
        self.put("sorrel-soup", "Sorrel soup", kind="dish")
        self.put("sorrel-soup", "Sorrel soup", kind="recipe")
        self.assertEqual(2, len(self.run_merge().copied))


if __name__ == "__main__":
    unittest.main()
