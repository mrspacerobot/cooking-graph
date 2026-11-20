"""A retired id is never used again. schema/retired.json lists them."""

import json
import os
import unittest

from tests.small_kitchen import SmallKitchen
from tools import check


class RetiredTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def retire(self, *thing_ids):
        rows = [{"id": thing_id, "why": "a test retired it"} for thing_id in thing_ids]
        self.kitchen.write_text("schema/retired.json", json.dumps(rows))

    def rules_broken(self):
        return [issue.rule for issue in check.check_repository(self.kitchen.root)]

    def test_a_kitchen_with_no_retired_ids_passes(self):
        self.retire()
        self.assertEqual([], self.rules_broken())

    def test_a_missing_list_retires_nothing(self):
        os.remove(os.path.join(self.kitchen.root, "schema", "retired.json"))
        self.assertEqual([], self.rules_broken())

    def test_a_retired_id_that_is_unused_passes(self):
        self.retire("dish/cuisses-de-grenouilles")
        self.assertEqual([], self.rules_broken())

    def test_a_thing_that_reuses_a_retired_id_fails(self):
        self.retire("dish/buttered-onions")
        self.assertIn("retired-id", self.rules_broken())

    def test_a_probe_that_reuses_a_retired_id_fails(self):
        probe_path = sorted(path for path in self.kitchen.files if path.startswith("probes/dish-probe/"))[0]
        probe_id = self.kitchen.files[probe_path]["id"]
        self.retire(probe_id)
        self.assertIn("retired-id", self.rules_broken())


if __name__ == "__main__":
    unittest.main()
