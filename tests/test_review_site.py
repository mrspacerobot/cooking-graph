"""The review site carries drafts and provenance, never probes or safety claims."""

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

    def test_substitution_claim_can_be_reviewed_with_its_context_and_source(self):
        data = review_site.payload(self.things, 'abc123')
        claims = [row for row in data['entries'].values() if row['kind'] == 'substitution']
        claim = next(row for row in claims if row['candidate'] == 'ingredient/oil' and row['original'] == 'ingredient/butter')
        self.assertEqual('ingredient/oil', claim['source'])
        self.assertEqual('drafted', claim['tier'])
        self.assertEqual(['technique/sweat'], claim['when'])
        self.assertEqual({'stand_in': 1, 'original': 1, 'by': 'weight'}, claim['ratio'])
        self.assertEqual('The flavour changes.', claim['caveat'])

    def test_recipe_uses_the_query_engine_and_links_to_reviewable_claims(self):
        data = review_site.payload(self.things, 'abc123')
        fat = data['entries']['recipe/buttered-onions']['substitutions'][1]
        option = next(row for row in fat['options'] if row['thing'] == 'ingredient/oil')
        self.assertEqual('stand-in', option['basis'])
        self.assertIn('technique/sweat', fat['context'])
        self.assertEqual('ingredient/oil', data['entries'][option['claims'][0]]['candidate'])

    def test_recipe_links_the_matching_claim_instead_of_another_context_for_the_same_pair(self):
        other = copy.deepcopy(self.things['ingredient/oil'].data['stands_in_for'][0])
        other.update(when=['technique/mince'], caveat='Another context.')
        self.things['ingredient/oil'].data['stands_in_for'].append(other)
        data = review_site.payload(self.things, 'abc123')
        oil = next(row for row in data['entries']['recipe/buttered-onions']['substitutions'][1]['options'] if row['thing'] == 'ingredient/oil')
        self.assertEqual(1, len(oil['claims']))
        self.assertEqual(['technique/sweat'], data['entries'][oil['claims'][0]]['when'])

    def test_exclusions_win_over_part_options_and_missing_context_is_not_a_ban(self):
        self.things['dish/buttered-onions'].data['parts'][1]['options'].append('ingredient/oil')
        raw = self.things['ingredient/oil'].data['stands_in_for'][0]
        raw['not_when'] = ['technique/sweat']
        fat = review_site.payload(self.things, 'abc123')['entries']['recipe/buttered-onions']['substitutions'][1]
        self.assertEqual([], fat['options'])
        excluded = next(row for row in fat['excluded'] if row['thing'] == 'ingredient/oil')
        self.assertEqual('not-in-this-context', excluded['reason'])
        self.things['dish/buttered-onions'].data['parts'][1]['options'].remove('ingredient/oil')
        raw.update(when=['technique/mince'], not_when=[])
        fat = review_site.payload(self.things, 'abc123')['entries']['recipe/buttered-onions']['substitutions'][1]
        self.assertEqual('no-matching-context', next(row for row in fat['excluded'] if row['thing'] == 'ingredient/oil')['reason'])

    def test_recipe_review_hash_changes_when_a_substitution_changes(self):
        before = review_site.payload(self.things, 'abc123')['entries']['recipe/buttered-onions']['hash']
        self.things['ingredient/oil'].data['stands_in_for'][0]['caveat'] = 'A different finish.'
        after = review_site.payload(self.things, 'abc123')['entries']['recipe/buttered-onions']['hash']
        self.assertNotEqual(before, after)

    def test_part_option_has_no_invented_claim_or_ratio(self):
        self.things['ingredient/oil'].data['stands_in_for'] = []
        self.things['dish/buttered-onions'].data['parts'][1]['options'].append('ingredient/oil')
        data = review_site.payload(self.things, 'abc123')
        option = data['entries']['recipe/buttered-onions']['substitutions'][1]['options'][0]
        self.assertEqual('part-option', option['basis'])
        self.assertIsNone(option['ratio'])
        self.assertEqual([], option['claims'])

    def test_entry_hash_changes_only_when_its_content_changes(self):
        before = review_site.payload(self.things, 'old')['entries']['technique/sweat']['hash']
        self.assertEqual(before, review_site.payload(self.things, 'new')['entries']['technique/sweat']['hash'])
        self.things['technique/sweat'].data['does'] = 'Changed wording.'
        after = review_site.payload(self.things, 'new')['entries']['technique/sweat']['hash']
        self.assertNotEqual(before, after)

    def test_technique_discovery_uses_variants_in_the_engine_order(self):
        child = copy.deepcopy(self.things['technique/sweat'].data)
        child.update(id='technique/gentle-sweat', names={'en': 'Gentle sweat'},
                     variant_of=[{'thing': 'technique/sweat', 'tier': 'drafted', 'differs': 'A gentler heat.'}])
        self.things[child['id']] = Thing('graph/technique/gentle-sweat.json', 'technique', child)
        recipe = copy.deepcopy(self.things['recipe/buttered-onions'].data)
        recipe['id'] = 'recipe/a-gentle-onions'
        recipe['steps'][0]['technique'] = child['id']
        self.things[recipe['id']] = Thing('graph/recipe/a-gentle-onions.json', 'recipe', recipe)
        data = review_site.payload(self.things, 'abc123')
        parent = data['entries']['technique/sweat']
        self.assertEqual(['recipe/buttered-onions', 'recipe/a-gentle-onions'], [row['recipe'] for row in parent['recipes']])
        self.assertTrue(parent['recipes'][0]['exact'])
        self.assertEqual([child['id']], parent['recipes'][1]['variants_used'])
        self.assertEqual([{'thing': child['id'], 'tier': 'drafted', 'differs': 'A gentler heat.'}], parent['variants'])
        self.assertEqual(['recipe/a-gentle-onions'], [row['recipe'] for row in data['entries'][child['id']]['recipes']])

    def test_preparations_are_readable_reviewable_records_with_their_parts(self):
        data = review_site.payload(self.things, 'abc123')
        preparation = data['entries']['preparation/roux']
        self.assertEqual('preparation', preparation['kind'])
        self.assertEqual('preparation/roux', preparation['source'])
        self.assertEqual(self.things['preparation/roux'].data['parts'], preparation['parts'])
        self.assertEqual(self.things['preparation/roux'].data['is'], preparation['is'])
        self.assertEqual('drafted', preparation['tier'])

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
            self.assertEqual(['.nojekyll', 'approvals.html', 'index.html'], sorted(p.name for p in Path(root, 'out/site').iterdir()))
