"""Human decisions apply only to unchanged units through the existing checker."""

import unittest
from pathlib import Path
from unittest.mock import patch

from tests.small_kitchen import SmallKitchen, reviewer
from tools import approval_packets, check, reading, review_hash


class ApprovalPacketTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)
        self.kitchen.add(reviewer())

    def decision(self, thing='technique/sweat', field=None, **changes):
        data = self.kitchen.files['graph/' + thing + '.json']
        result = dict(thing=thing, field=field, seen=review_hash.seen(data, field), verdict='approved',
                      cuisine='cuisine/french' if field is None else None,
                      sources=['source/kitchen-law'] if field == 'safety' else [],
                      note='I personally checked this exact unit.', attested=True)
        result.update(changes)
        return result

    def packet(self, decisions=None, **changes):
        result = dict(version=1, commit='a' * 40, reviewer='reviewer/owner', on='2026-10-18',
                      decisions=decisions or [self.decision()])
        result.update(changes)
        return result

    def snapshot(self):
        return {str(path.relative_to(self.kitchen.root)): path.read_bytes()
                for path in Path(self.kitchen.root, 'graph').rglob('*.json')}

    def test_content_approval_creates_backing_record_and_preserves_safety(self):
        approval_packets.apply(self.kitchen.root, self.packet([self.decision('ingredient/butter')]))
        data = reading.read_json(Path(self.kitchen.root, 'graph/ingredient/butter.json'))
        self.assertEqual('reviewed', data['tier'])
        self.assertEqual('unverified', data['safety']['state'])
        self.assertEqual([], check.check_repository(self.kitchen.root))

    def test_evidenced_safety_approval_verifies_safety_without_promoting_content(self):
        approval_packets.apply(self.kitchen.root, self.packet([self.decision('ingredient/butter', 'safety')]))
        data = reading.read_json(Path(self.kitchen.root, 'graph/ingredient/butter.json'))
        self.assertEqual('drafted', data['tier'])
        self.assertEqual('verified', data['safety']['state'])
        records = list(Path(self.kitchen.root, 'graph/review').glob('*.json'))
        self.assertIn('source/kitchen-law', reading.read_json(records[0])['covers'][0]['note'])
        self.assertEqual([], check.check_repository(self.kitchen.root))

    def test_rejection_records_the_decision_without_promoting_content(self):
        approval_packets.apply(self.kitchen.root, self.packet([self.decision(verdict='rejected')]))
        data = reading.read_json(Path(self.kitchen.root, 'graph/technique/sweat.json'))
        self.assertEqual('drafted', data['tier'])

    def test_changed_content_is_refused_before_any_write(self):
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'changed'):
            approval_packets.apply(self.kitchen.root, self.packet([self.decision(seen='0' * 12)]))
        self.assertEqual(before, self.snapshot())

    def test_model_reviewer_is_refused(self):
        self.kitchen.add(reviewer('judge', kind='model', knows=(), model_id='test-model'))
        with self.assertRaisesRegex(ValueError, 'person'):
            approval_packets.apply(self.kitchen.root, self.packet(reviewer='reviewer/judge'))

    def test_no_person_is_invented_for_an_unknown_reviewer(self):
        with self.assertRaisesRegex(ValueError, 'registered'):
            approval_packets.apply(self.kitchen.root, self.packet(reviewer='reviewer/unknown'))

    def test_absent_human_attestation_is_refused(self):
        with self.assertRaisesRegex(ValueError, 'attest'):
            approval_packets.apply(self.kitchen.root, self.packet([self.decision(attested=False)]))

    def test_source_free_safety_without_authority_is_refused(self):
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, 'safety'):
            approval_packets.apply(self.kitchen.root, self.packet([self.decision('ingredient/butter', 'safety', sources=[])]))
        self.assertEqual(before, self.snapshot())

    def test_safety_rejection_can_request_a_correction_without_claiming_verification(self):
        approval_packets.apply(self.kitchen.root, self.packet([self.decision('ingredient/butter', 'safety', verdict='rejected', sources=[])]))
        data = reading.read_json(Path(self.kitchen.root, 'graph/ingredient/butter.json'))
        self.assertEqual('unverified', data['safety']['state'])
        self.assertEqual([], check.check_repository(self.kitchen.root))

    def test_evidence_for_one_ingredient_does_not_silently_verify_another(self):
        decisions = [self.decision('ingredient/butter', 'safety'), self.decision('ingredient/onion', 'safety', sources=[])]
        with self.assertRaisesRegex(ValueError, 'safety'):
            approval_packets.apply(self.kitchen.root, self.packet(decisions))

    def test_cuisine_outside_the_reviewers_scope_is_refused(self):
        self.kitchen.change('graph/reviewer/owner.json', lambda row: row.update(knows=[]))
        with self.assertRaisesRegex(ValueError, 'cuisine'):
            approval_packets.apply(self.kitchen.root, self.packet())

    def test_duplicate_units_and_unknown_fields_are_refused(self):
        decision = self.decision()
        for packet in (self.packet([decision, decision]), self.packet(surprise=True)):
            with self.assertRaises(ValueError):
                approval_packets.apply(self.kitchen.root, packet)

    def test_mixed_content_and_safety_make_separate_review_sessions(self):
        changed = approval_packets.apply(self.kitchen.root, self.packet([self.decision('ingredient/butter'), self.decision('ingredient/butter', 'safety')]))
        self.assertEqual(2, sum(path.startswith('graph/review/') for path in changed))
        self.assertEqual([], check.check_repository(self.kitchen.root))

    def test_reapplying_a_packet_does_not_rewrite_history(self):
        packet = self.packet()
        approval_packets.apply(self.kitchen.root, packet)
        before = self.snapshot()
        with self.assertRaises(ValueError):
            approval_packets.apply(self.kitchen.root, packet)
        self.assertEqual(before, self.snapshot())

    def test_write_failure_rolls_back_every_file(self):
        before = self.snapshot()
        original = approval_packets.write_file
        calls = []

        def fail_second(path, text):
            calls.append(path)
            if len(calls) == 2:
                raise OSError('test write failure')
            original(path, text)

        with patch.object(approval_packets, 'write_file', side_effect=fail_second):
            with self.assertRaises(OSError):
                approval_packets.apply(self.kitchen.root, self.packet())
        self.assertEqual(before, self.snapshot())
