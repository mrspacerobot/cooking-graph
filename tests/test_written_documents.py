"""Documents that a command writes from the files must not fall behind the files."""

import unittest

from tests.small_kitchen import SmallKitchen
from tools import check, safety_probes, strictness, written_documents

STRICT = "docs/strict-answers.md"
DISAGREEMENTS = "docs/safety-disagreements.md"
BUTTER = "graph/ingredient/butter.json"


class WrittenDocuments(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def found(self):
        return {(issue.path, issue.rule) for issue in check.check_repository(self.kitchen.root)}

    def write_both(self):
        things, issues = check.read_repository(self.kitchen.root)
        self.kitchen.write_text(STRICT, strictness.document(things))
        self.kitchen.write_text(DISAGREEMENTS, safety_probes.disagreements_document(safety_probes.run(things)))

    def test_a_repository_without_the_documents_is_not_refused(self):
        self.assertEqual(set(), self.found())

    def test_documents_written_from_the_files_pass(self):
        self.write_both()
        self.assertEqual(set(), self.found())

    def test_the_list_of_strict_answers_falls_behind_an_ingredient(self):
        self.write_both()
        self.kitchen.change(BUTTER, lambda thing: thing["safety"]["contains"][0].update(certain=False))
        self.assertEqual({(STRICT, "not-current")}, self.found())

    def test_the_disagreements_fall_behind_a_probe(self):
        self.write_both()
        probe = "probes/safety-probe/buttered-onions.json"
        self.kitchen.change(probe, lambda thing: thing.update(holds=[], does_not_hold=["milk"]))
        self.assertEqual({(DISAGREEMENTS, "not-current")}, self.found())

    def test_each_document_names_the_command_that_writes_it(self):
        self.assertEqual(["docs/safety-disagreements.md", "docs/strict-answers.md"], sorted(written_documents.DOCUMENTS))


if __name__ == "__main__":
    unittest.main()
