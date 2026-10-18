"""The separate approval page shows evidence without leaking it into the notebook."""

import json
import unittest
from pathlib import Path

from tests.small_kitchen import REPOSITORY, reviewer
from tests.test_queries import kitchen
from tools import approval_site, review_hash, review_site
from tools.reading import Thing


class ApprovalSiteTest(unittest.TestCase):
    def setUp(self):
        self.things = kitchen()

    def test_safety_and_content_are_separate_units_with_native_review_hashes(self):
        data = approval_site.payload(self.things, 'a' * 40)
        safety = data['units']['ingredient/butter#safety']
        content = data['units']['ingredient/butter#content']
        self.assertEqual('unverified', safety['status'])
        self.assertEqual('drafted', content['status'])
        self.assertEqual(review_hash.seen(self.things['ingredient/butter'].data, 'safety'), safety['seen'])
        self.assertNotIn('safety', content['raw'])
        self.assertIn('contains', safety['raw'])

    def test_facts_and_their_sources_are_available_for_a_human_to_check(self):
        data = approval_site.payload(self.things, 'a' * 40)
        self.assertIn('fact/dairy', data['facts'])
        self.assertIn('source/kitchen-law', data['sources'])
        self.assertIn('url', data['sources']['source/kitchen-law'])

    def test_models_cannot_appear_in_the_human_reviewer_picker(self):
        for person in (reviewer(), reviewer('judge', kind='model', knows=(), model_id='test-model')):
            self.things[person['id']] = Thing('graph/' + person['id'] + '.json', 'reviewer', person)
        data = approval_site.payload(self.things, 'a' * 40)
        self.assertEqual(['reviewer/owner'], list(data['reviewers']))

    def test_probe_content_never_reaches_the_approval_page(self):
        self.things['dish-probe/hidden'] = Thing('probes/dish-probe/hidden.json', 'dish-probe', {'id': 'dish-probe/hidden', 'secret': 'do not show this'})
        self.assertNotIn('do not show this', json.dumps(approval_site.payload(self.things, 'a' * 40)))

    def test_safety_is_confined_to_the_approval_page_and_script_text_is_escaped(self):
        self.things['ingredient/butter'].data['safety']['note'] = '</script><script>alert(1)</script>'
        data = approval_site.payload(self.things, 'a' * 40)
        text = approval_site.page(REPOSITORY, data)
        self.assertNotIn('</script><script>alert(1)', text)
        self.assertIn('\\u003c/script>', text)
        self.assertNotIn('__APPROVAL_', text)
        self.assertNotIn('"contains"', json.dumps(review_site.payload(self.things, 'a' * 40)))

    def test_page_explains_tiers_and_safety_states_and_keeps_its_warning(self):
        text = approval_site.page(REPOSITORY, approval_site.payload(self.things, 'a' * 40))
        words = json.loads((Path(REPOSITORY) / 'schema/words.json').read_text())
        for word in words['tiers'] + words['safety_states']:
            self.assertIn("'%s':" % word, text)
        self.assertIn('not a verified food recommendation', text)
        self.assertNotIn('__REVIEW_', text)
        self.assertNotIn('\u2014', text)
