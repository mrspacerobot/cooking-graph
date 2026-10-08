"""The two kinds that put a review on record: the shape of a reviewer and of a review, and what may never be in them."""

import unittest

from tests.small_kitchen import SmallKitchen, cover, review, reviewer
from tools import check, numbers, review_hash

SWEAT = "graph/technique/sweat.json"
REVIEWER = "graph/reviewer/owner.json"
REVIEW = "graph/review/owner-sweat-2026-10-14.json"


class ReviewShapeTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)
        self.kitchen.add(reviewer())
        seen = review_hash.seen(self.kitchen.files[SWEAT])
        self.kitchen.add(review("owner-sweat-2026-10-14", "owner", "reviewed", [cover("technique/sweat", seen)]))

    def issues(self):
        return check.check_repository(self.kitchen.root)

    def rules(self):
        return {(issue.path, issue.rule) for issue in self.issues()}

    def test_a_reviewer_and_a_review_that_back_nothing_are_valid(self):
        self.assertEqual([], self.issues())

    def test_a_review_names_a_reviewer_that_exists(self):
        self.kitchen.change(REVIEW, lambda record: record.update(reviewer="reviewer/nobody"))
        self.assertIn((REVIEW, "missing-reference"), self.rules())

    def test_a_review_covers_a_thing_that_exists(self):
        self.kitchen.change(REVIEW, lambda record: record["covers"][0].update(thing="technique/nothing"))
        self.assertIn((REVIEW, "missing-reference"), self.rules())

    def test_a_review_has_no_tier_of_its_own(self):
        self.kitchen.change(REVIEW, lambda record: record.update(tier="reviewed"))
        self.assertIn((REVIEW, "unknown-field"), self.rules())

    def test_a_grant_is_one_of_the_tiers(self):
        self.kitchen.change(REVIEW, lambda record: record.update(grants="approved"))
        self.assertIn((REVIEW, "not-in-tiers"), self.rules())

    def test_a_verdict_is_a_word_of_the_list(self):
        self.kitchen.change(REVIEW, lambda record: record["covers"][0].update(verdict="fine"))
        self.assertIn((REVIEW, "not-in-verdicts"), self.rules())

    def test_a_reviewer_kind_is_a_word_of_the_list(self):
        self.kitchen.change(REVIEWER, lambda person: person.update(kind="robot"))
        self.assertIn((REVIEWER, "not-in-reviewer_kinds"), self.rules())

    def test_an_email_address_in_a_reviewer_note_is_refused(self):
        self.kitchen.change(REVIEWER, lambda person: person.update(safety_authority="Ask me at someone@example.org"))
        self.assertIn((REVIEWER, "email-in-repo"), self.rules())

    def test_an_email_address_in_a_review_note_is_refused(self):
        self.kitchen.change(REVIEW, lambda record: record.update(note="Mail me at someone@example.org"))
        self.assertIn((REVIEW, "email-in-repo"), self.rules())

    def test_the_numbers_still_count_a_graph_that_holds_records(self):
        things, issues = check.read_repository(self.kitchen.root)
        self.assertEqual([], issues)
        counts = numbers.count_things(things)
        self.assertNotIn("review", counts)
        self.assertNotIn("reviewer", counts)


if __name__ == "__main__":
    unittest.main()
