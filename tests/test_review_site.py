"""The review site carries drafts and provenance, never probes or safety claims."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.small_kitchen import REPOSITORY
from tests.test_queries import kitchen
from tools import review_site
from tools.reading import Thing


class ReviewSiteTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()

    def test_only_graph_records_are_included_and_safety_is_not_exported(self):
        self.things['dish-probe/hidden'] = Thing('probes/dish-probe/hidden.json', 'dish-probe',
                                                {'id': 'dish-probe/hidden', 'secret': 'hidden words'})
        data = review_site.payload(self.things, 'abc123')
        encoded = json.dumps(data)
        self.assertNotIn('hidden words', encoded)
        self.assertNotIn('"safety"', encoded)
        self.assertNotIn('"contains"', encoded)
        self.assertEqual('abc123', data['commit'])
        self.assertEqual('drafted', data['entries']['technique/sweat']['tier'])
        self.assertIn('ingredient/onion', data['names'])
        self.assertNotIn('ingredient/onion', data['entries'])

    def test_class_keeps_program_order_prerequisites_and_level_context(self):
        program = json.loads(Path(REPOSITORY, 'graph/program/french-foundations.json').read_text())
        self.things[program['id']] = Thing('graph/program/french-foundations.json', 'program', program)
        data = review_site.payload(self.things, 'abc123')
        classes = [entry for entry in data['entries'].values() if entry['kind'] == 'class']
        first = classes[0]
        self.assertEqual('Mirepoix', first['names']['en'])
        self.assertEqual('Foundations', first['course'])
        self.assertEqual('Knife cuts', first['skill'])
        self.assertEqual('program/french-foundations', first['source'])
        self.assertEqual(program['courses'][0]['skills'][0]['levels'][0]['teaches'], first['teaches'])
        self.assertEqual([], first['comes_after'])
        self.assertEqual(1, first['number'])

    def test_entry_hash_changes_only_when_its_content_changes(self):
        before = review_site.payload(self.things, 'old')['entries']['technique/sweat']['hash']
        self.assertEqual(before, review_site.payload(self.things, 'new')['entries']['technique/sweat']['hash'])
        self.things['technique/sweat'].data['does'] = 'Changed wording.'
        after = review_site.payload(self.things, 'new')['entries']['technique/sweat']['hash']
        self.assertNotEqual(before, after)

    def test_page_cannot_be_broken_out_of_by_graph_text(self):
        self.things['technique/sweat'].data['does'] = '</script><script>alert(1)</script>'
        page = review_site.page(REPOSITORY, review_site.payload(self.things, 'abc123'))
        self.assertNotIn('</script><script>alert(1)', page)
        self.assertIn('\\u003c/script>', page)
        self.assertNotIn('__REVIEW_', page)

    def test_build_refuses_invalid_graph_and_does_not_write(self):
        with tempfile.TemporaryDirectory() as root:
            with patch.object(review_site.check, 'read_repository', return_value=({}, ['broken'])):
                with contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(1, review_site.main(root, assets=REPOSITORY))
            self.assertFalse(Path(root, 'out/site/index.html').exists())

    def test_build_writes_only_site_and_nojekyll(self):
        with tempfile.TemporaryDirectory() as root:
            with patch.object(review_site.check, 'read_repository', return_value=(self.things, [])):
                with patch.object(review_site, 'metadata', return_value={'commit': 'abc123'}):
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(0, review_site.main(root, assets=REPOSITORY))
            self.assertEqual(['.nojekyll', 'index.html'], sorted(p.name for p in Path(root, 'out/site').iterdir()))
