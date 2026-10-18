"""Only a live, evidenced human safety review can verify an ingredient."""

import unittest
from pathlib import Path

from tests.small_kitchen import SmallKitchen, cover, review, reviewer
from tools import check, reading, review_hash

BUTTER = 'graph/ingredient/butter.json'
RECORD = 'graph/review/owner-butter-safety.json'


class SafetyReviewTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)
        self.kitchen.add(reviewer())

    def change(self, path, alter):
        data = reading.read_json(Path(self.kitchen.root, path))
        alter(data)
        self.kitchen.files[path] = data
        self.kitchen.write(path, data)

    def record(self, **changes):
        data = review('owner-butter-safety', 'owner', 'verified',
                      [cover('ingredient/butter', review_hash.seen(self.kitchen.files[BUTTER], 'safety'), field='safety')],
                      cuisine=None, against=[{'how': 'source', 'source': 'source/kitchen-law', 'note': 'Checked the ingredient facts against the source.'}])
        data.update(changes)
        self.kitchen.add(data)
        self.change(BUTTER, lambda row: row['safety'].update(state='verified'))

    def rules(self):
        return {(issue.path, issue.rule) for issue in check.check_repository(self.kitchen.root)}

    def test_human_source_review_verifies_only_safety(self):
        self.record()
        self.assertEqual(set(), self.rules())

    def test_safety_can_be_reviewed_without_claiming_cuisine_knowledge(self):
        self.change('graph/reviewer/owner.json', lambda row: row.update(knows=[]))
        self.record()
        self.assertEqual(set(), self.rules())

    def test_model_cannot_verify_safety(self):
        self.kitchen.add(reviewer('judge', kind='model', knows=(), model_id='test-model'))
        self.record(reviewer='reviewer/judge')
        self.assertIn((BUTTER, 'safety-not-earned'), self.rules())

    def test_own_knowledge_without_owner_granted_authority_is_not_enough(self):
        self.record(against=[{'how': 'own-knowledge', 'source': None, 'note': 'I think so.'}])
        self.assertIn((BUTTER, 'safety-not-earned'), self.rules())

    def test_explicit_safety_authority_can_back_a_personal_review(self):
        self.change('graph/reviewer/owner.json', lambda row: row.update(safety_authority='Owner accepted this safety expertise.'))
        self.record(against=[{'how': 'own-knowledge', 'source': None, 'note': 'Checked under my safety expertise.'}])
        self.assertEqual(set(), self.rules())

    def test_source_without_an_evidence_note_is_not_enough(self):
        self.record(against=[{'how': 'source', 'source': 'source/kitchen-law', 'note': None}])
        self.assertIn((BUTTER, 'safety-not-earned'), self.rules())

    def test_editing_safety_after_verification_invalidates_it(self):
        self.record()
        self.change(BUTTER, lambda row: row['safety'].update(note='Changed after approval.'))
        self.assertIn((BUTTER, 'safety-not-earned'), self.rules())

    def test_editing_culinary_content_does_not_invalidate_safety(self):
        self.record()
        self.change(BUTTER, lambda row: row.update(behaviour='A changed culinary description.'))
        self.assertEqual(set(), self.rules())

    def test_verification_keeps_strict_answers_strict(self):
        self.change(BUTTER, lambda row: row['safety']['contains'][0].update(certain=False))
        self.record()
        self.assertEqual(set(), self.rules())

    def test_whole_ingredient_review_cannot_verify_safety(self):
        self.record(grants='reviewed', cuisine='cuisine/french', covers=[cover('ingredient/butter', review_hash.seen(self.kitchen.files[BUTTER]))])
        self.assertIn((BUTTER, 'safety-not-earned'), self.rules())

    def test_rejected_safety_review_cannot_verify_safety(self):
        self.record(covers=[cover('ingredient/butter', review_hash.seen(self.kitchen.files[BUTTER], 'safety'), field='safety', verdict='rejected', note='Needs changes.')])
        self.assertIn((BUTTER, 'safety-not-earned'), self.rules())

    def test_verified_safety_grant_cannot_promote_culinary_content(self):
        self.record()
        self.change(BUTTER, lambda row: row.update(tier='verified'))
        self.assertIn((BUTTER, 'tier-not-earned'), self.rules())
