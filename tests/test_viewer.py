"""The browser page never leaks probes, invents links or opens invalid data."""

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.small_kitchen import REPOSITORY
from tests.test_queries import kitchen
from tools import reading, viewer
from tools.reading import Issue, Thing


class ViewerTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()
        self.model, _ = reading.read_schema(REPOSITORY)

    def payload(self):
        return viewer.payload(self.things, self.model, {"commit": "", "branch": "test"})

    def test_neither_growing_nor_held_back_probes_reach_the_page(self):
        for state in ("growing", "held-back"):
            identifier = "dish-probe/" + state
            record = {"id": identifier, "set": state, "dish": "probe-only-secret"}
            self.things[identifier] = Thing("probes/" + identifier + ".json", "dish-probe", record)
        encoded = json.dumps(self.payload())
        self.assertNotIn("probe-only-secret", encoded)
        self.assertNotIn("dish-probe/", encoded)

    def test_only_schema_references_become_links(self):
        self.things["technique/sweat"].data["does"] = "ingredient/onion"
        edges = self.payload()["edges"]
        self.assertFalse(any(edge["source"] == "technique/sweat" and
                             edge["target"] == "ingredient/onion" for edge in edges))
        self.assertTrue(any(edge["source"] == "recipe/buttered-onions" and
                            edge["target"] == "technique/sweat" for edge in edges))

    def test_answers_use_the_existing_context_and_exclusion_rules(self):
        row = self.things["ingredient/oil"].data["stands_in_for"][0]
        row.update(allows=False, when=[], not_when=["technique/sweat"])
        answer = self.payload()["answers"]["recipe/buttered-onions"]["lines"][1]
        self.assertEqual([], answer["options"])
        self.assertEqual("not-in-this-context", answer["excluded"][0]["reason"])
        self.assertEqual(["technique/sweat"], answer["excluded"][0]["not_when"])

    def test_new_content_and_counts_appear_without_a_stored_snapshot(self):
        before = self.payload()
        extra = copy.deepcopy(self.things["ingredient/onion"].data)
        extra.update(id="ingredient/red-onion", names={"en": "Red onion"})
        self.things[extra["id"]] = Thing("graph/ingredient/red-onion.json", "ingredient", extra)
        after = self.payload()
        self.assertEqual(len(before["nodes"]) + 1, len(after["nodes"]))
        self.assertEqual(before["counts"]["ingredient"] + 1, after["counts"]["ingredient"])

    def test_embedded_records_cannot_close_the_data_script(self):
        self.things["ingredient/onion"].data["behaviour"] = '</script><script>alert("onion")</script>'
        page = viewer.page(REPOSITORY, self.payload())
        self.assertNotIn('</script><script>alert("onion")', page)
        self.assertIn("\\u003c/script>", page)
        self.assertNotIn('__GRAPH_DATA__', page)
        self.assertNotIn('src="graph-view.js"', page)

    def run_command(self, root, arguments, issues=(), opened=True):
        with patch.object(viewer.check, "read_repository", return_value=(self.things, list(issues))):
            with patch.object(viewer, "metadata", return_value={"commit": "", "branch": "test"}):
                with patch.object(viewer.webbrowser, "open", return_value=opened) as browser:
                    with contextlib.redirect_stdout(io.StringIO()) as output:
                        with contextlib.redirect_stderr(io.StringIO()) as error:
                            result = viewer.main(root, arguments, assets=REPOSITORY)
        return result, output.getvalue(), error.getvalue(), browser

    def test_default_command_opens_the_generated_file_in_the_browser(self):
        with tempfile.TemporaryDirectory() as root:
            result, output, error, browser = self.run_command(root, [])
            destination = Path(root, "out", "graph.html")
            self.assertEqual(0, result)
            self.assertTrue(destination.exists())
            browser.assert_called_once_with(destination.resolve().as_uri(), new=2)
            self.assertIn("Opened", output)
            self.assertEqual("", error)

    def test_no_open_builds_a_page_without_opening_a_browser(self):
        with tempfile.TemporaryDirectory() as root:
            result, output, _, browser = self.run_command(root, ["--no-open"])
            self.assertEqual(0, result)
            self.assertIn("graph.html", output)
            browser.assert_not_called()

    def test_invalid_graph_never_replaces_a_page_or_opens_the_browser(self):
        with tempfile.TemporaryDirectory() as root:
            destination = Path(root, "out", "graph.html")
            destination.parent.mkdir()
            destination.write_text("earlier valid page")
            issue = Issue("graph/ingredient/onion.json", "", "missing-field", "broken")
            result, _, error, browser = self.run_command(root, [], [issue])
            self.assertEqual(1, result)
            self.assertEqual("earlier valid page", destination.read_text())
            self.assertIn("run ./check", error)
            browser.assert_not_called()

    def test_failed_browser_launch_reports_the_file_without_claiming_it_opened(self):
        with tempfile.TemporaryDirectory() as root:
            result, output, _, _ = self.run_command(root, [], opened=False)
            self.assertEqual(0, result)
            self.assertNotIn("Opened", output)
            self.assertIn("could not open", output)
            self.assertIn(Path(root, "out", "graph.html").resolve().as_uri(), output)


if __name__ == "__main__":
    unittest.main()
