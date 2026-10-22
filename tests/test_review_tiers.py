"""A tier above drafted is backed by a live record of a reviewer who knows the cuisine, and falls when the thing is edited."""

import unittest

from tests.small_kitchen import SmallKitchen, cover, head, review, reviewer
from tools import check, review_hash
from tests.test_intro_quiz import sound_intro, sound_question

SWEAT = "graph/technique/sweat.json"
BUTTER = "graph/ingredient/butter.json"
SWEAT_REVIEW = "graph/review/owner-sweat-2026-10-14.json"
SOURCE = "source/kitchen-law"


class ReviewTierTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)
        self.kitchen.add(reviewer())

    def issues(self):
        return check.check_repository(self.kitchen.root)

    def rules(self):
        return {(issue.path, issue.rule) for issue in self.issues()}

    def seen(self, path, field=None, target=None):
        return review_hash.seen(self.kitchen.files[path], field=field, target=target)

    def record(self, slug="owner-sweat-2026-10-14", who="owner", grants="reviewed", covers=None, **more):
        covers = covers if covers is not None else [cover("technique/sweat", self.seen(SWEAT))]
        content = review(slug, who, grants, covers, **more)
        return self.kitchen.add(content)

    def raise_tier(self, path, tier="reviewed"):
        self.kitchen.change(path, lambda thing: thing.update(tier=tier))

    def test_a_tier_with_no_record_is_not_earned(self):
        self.raise_tier(SWEAT)
        self.assertIn((SWEAT, "tier-not-earned"), self.rules())

    def test_a_tier_backed_by_a_live_record_of_someone_who_knows_the_cuisine(self):
        self.record()
        self.raise_tier(SWEAT)
        self.assertEqual([], self.issues())

    def test_the_tier_a_record_grants_is_the_most_a_thing_may_hold(self):
        self.record(grants="sourced")
        self.raise_tier(SWEAT, "reviewed")
        self.assertIn((SWEAT, "tier-not-earned"), self.rules())

    def test_a_tier_below_the_grant_is_allowed(self):
        self.record(grants="reviewed")
        self.raise_tier(SWEAT, "sourced")
        self.assertEqual([], self.issues())

    def test_a_record_that_rejects_backs_nothing(self):
        self.record(covers=[cover("technique/sweat", self.seen(SWEAT), verdict="rejected", note="The cue is wrong.")])
        self.raise_tier(SWEAT)
        self.assertIn((SWEAT, "tier-not-earned"), self.rules())

    def test_a_thing_edited_after_the_review_falls(self):
        self.record()
        self.kitchen.change(SWEAT, lambda thing: thing.update(tier="reviewed", does="Softens cut vegetables in fat over gentle heat."))
        self.assertIn((SWEAT, "review-stale"), self.rules())

    def test_a_statement_backed_by_a_record_of_its_own(self):
        covers = [cover("technique/sweat", self.seen(SWEAT, "works_on", "group/vegetables"), field="works_on", target="group/vegetables")]
        self.record(covers=covers)
        self.kitchen.change(SWEAT, lambda thing: thing["works_on"][0].update(tier="reviewed"))
        self.assertEqual([], self.issues())

    def test_a_statement_record_does_not_back_the_whole_thing(self):
        covers = [cover("technique/sweat", self.seen(SWEAT, "works_on", "group/vegetables"), field="works_on", target="group/vegetables")]
        self.record(covers=covers)
        self.raise_tier(SWEAT)
        self.assertIn((SWEAT, "tier-not-earned"), self.rules())

    def test_a_whole_thing_record_backs_the_statements_inside_it(self):
        self.record()
        self.kitchen.change(SWEAT, lambda thing: thing["works_on"][0].update(tier="reviewed"))
        self.assertEqual([], self.issues())

    def learning_card(self):
        self.kitchen.files[SWEAT].update(intro=sound_intro(), quiz=[sound_question()])
        self.kitchen.write(SWEAT, self.kitchen.files[SWEAT])

    def test_an_intro_can_be_reviewed_separately(self):
        self.learning_card()
        self.record(covers=[cover("technique/sweat", self.seen(SWEAT, "intro"), field="intro")])
        self.kitchen.change(SWEAT, lambda card: card["intro"].update(tier="reviewed"))
        self.assertEqual([], self.issues())
        self.kitchen.change(SWEAT, lambda card: card["intro"].update(tier="reviewed", why="It builds a gentle base."))
        self.assertIn((SWEAT, "review-stale"), self.rules())

    def test_a_question_is_reviewed_by_its_id_and_edits_invalidate_it(self):
        self.learning_card()
        self.record(covers=[cover("technique/sweat", self.seen(SWEAT, "quiz", "gentle-heat"),
                                  field="quiz", target="gentle-heat")])
        self.kitchen.change(SWEAT, lambda card: card["quiz"][0].update(tier="reviewed"))
        self.assertEqual([], self.issues())
        self.kitchen.change(SWEAT, lambda card: card["quiz"][0].update(tier="reviewed", because="Gentle heat limits browning."))
        self.assertIn((SWEAT, "review-stale"), self.rules())

    def test_question_review_survives_reordering(self):
        self.learning_card()
        self.record(covers=[cover("technique/sweat", self.seen(SWEAT, "quiz", "gentle-heat"),
                                  field="quiz", target="gentle-heat")])
        def reorder(card):
            card["quiz"][0]["tier"] = "reviewed"
            other = sound_question()
            other.update(id="other-cue", question="What changes in the pan?")
            card["quiz"].insert(0, other)
        self.kitchen.change(SWEAT, reorder)
        self.assertEqual([], self.issues())

    def test_a_model_may_not_grant_reviewed(self):
        self.kitchen.add(reviewer("judge", kind="model", knows=(), model_id="claude-sonnet-5-5"))
        path = self.record("judge-sweat-2026-10-14", "judge", cuisine=None)
        self.raise_tier(SWEAT)
        self.assertEqual({(path, "model-grants-too-much")}, self.rules())

    def test_a_model_may_not_grant_sourced_without_a_source(self):
        self.kitchen.add(reviewer("judge", kind="model", knows=(), model_id="claude-sonnet-5-5"))
        path = self.record("judge-sweat-2026-10-14", "judge", grants="sourced", cuisine=None)
        self.assertEqual({(path, "model-grants-too-much")}, self.rules())

    def test_a_model_may_grant_sourced_when_it_names_a_source(self):
        self.kitchen.add(reviewer("judge", kind="model", knows=(), model_id="claude-sonnet-5-5"))
        against = [{"how": "source", "source": SOURCE, "note": "The page names this move."}]
        self.record("judge-sweat-2026-10-14", "judge", grants="sourced", cuisine=None, against=against)
        self.raise_tier(SWEAT, "sourced")
        self.assertEqual([], self.issues())

    def test_a_person_who_does_not_know_the_cuisine(self):
        self.kitchen.add(reviewer("stranger", knows=()))
        path = self.record("stranger-sweat-2026-10-14", "stranger")
        self.assertEqual({(path, "reviewer-does-not-know-cuisine")}, self.rules())

    def test_a_person_must_name_a_cuisine_to_grant_reviewed(self):
        path = self.record(cuisine=None)
        self.assertIn((path, "reviewer-does-not-know-cuisine"), self.rules())

    def test_a_cuisine_the_thing_does_not_belong_to(self):
        self.kitchen.add(dict(head("cuisine/italian", "Italian"), within=None))
        self.kitchen.add(reviewer("italian-1", knows=(("cuisine/italian", "lives-or-lived-there"),)))
        path = self.record("italian-1-sweat-2026-10-14", "italian-1", cuisine="cuisine/italian")
        self.assertEqual({(path, "reviewer-does-not-know-cuisine")}, self.rules())

    def test_the_wider_cuisine_covers_the_narrower(self):
        path = self.record(cuisine="cuisine/provencal")
        self.assertNotIn((path, "reviewer-does-not-know-cuisine"), self.rules())

    def test_the_narrower_cuisine_does_not_cover_the_wider(self):
        self.kitchen.add(reviewer("provencal-1", knows=(("cuisine/provencal", "lives-or-lived-there"),)))
        path = self.record("provencal-1-sweat-2026-10-14", "provencal-1", cuisine="cuisine/french")
        self.assertIn((path, "reviewer-does-not-know-cuisine"), self.rules())

    def test_two_live_records_grant_one_unit_twice(self):
        first = self.record()
        second = self.record("owner-sweat-2026-10-15", on="2026-10-15")
        self.assertEqual({(first, "review-unlinked"), (second, "review-unlinked")} & self.rules(),
                         {(first, "review-unlinked"), (second, "review-unlinked")})

    def test_a_record_that_replaces_another_leaves_one_live(self):
        self.record()
        self.record("owner-sweat-2026-10-15", on="2026-10-15", supersedes=["owner-sweat-2026-10-14"])
        self.raise_tier(SWEAT)
        self.assertEqual([], self.issues())

    def test_a_record_may_not_replace_a_later_one(self):
        self.record(on="2026-10-14", supersedes=["owner-sweat-2026-10-20"])
        later = self.record("owner-sweat-2026-10-20", on="2026-10-20", grants="sourced")
        self.assertIn((SWEAT_REVIEW, "review-unlinked"), self.rules())
        self.assertNotIn((later, "review-unlinked"), self.rules())

    def test_a_rejection_that_does_not_name_the_approval_it_withdraws(self):
        self.record()
        rejection = self.record("owner-sweat-2026-10-16", on="2026-10-16", covers=[
            cover("technique/sweat", self.seen(SWEAT), verdict="rejected", note="The cue is wrong.")])
        self.assertIn((rejection, "review-unlinked"), self.rules())

    def test_a_rejection_that_withdraws_the_approval_takes_the_tier_away(self):
        self.record()
        self.record("owner-sweat-2026-10-16", on="2026-10-16", supersedes=["owner-sweat-2026-10-14"], covers=[
            cover("technique/sweat", self.seen(SWEAT), verdict="rejected", note="The cue is wrong.")])
        self.assertEqual([], self.issues())
        self.raise_tier(SWEAT)
        self.assertIn((SWEAT, "tier-not-earned"), self.rules())

    def test_verified_stays_refused_until_a_second_reviewer_is_built(self):
        self.record(grants="verified")
        self.raise_tier(SWEAT, "verified")
        self.assertIn((SWEAT, "tier-not-earned"), self.rules())

    def test_cook_tested_stays_refused(self):
        self.record()
        self.raise_tier(SWEAT, "cook-tested")
        self.assertIn((SWEAT, "tier-not-earned"), self.rules())

    def test_a_sample_record_is_not_built_yet(self):
        sample = {"seed": "lyon", "per_hundred": 10, "kinds": ["technique"], "cuisine": "cuisine/french"}
        path = self.record(mode="sample", sample=sample)
        self.assertIn((path, "review-not-built"), self.rules())

    def test_a_ruling_on_a_safety_disagreement_is_not_built_yet(self):
        ruling = {"probe": "safety-probe/onion-soup", "fact": "fact/dairy", "stands": "graph", "why": "The butter holds milk."}
        path = self.record(rulings=[ruling])
        self.assertIn((path, "review-not-built"), self.rules())

    def test_a_safety_record_cannot_be_covered_yet(self):
        covers = [cover("ingredient/butter", self.seen(BUTTER, "safety"), field="safety")]
        path = self.record(who="owner", grants="reviewed", covers=covers)
        self.assertIn((path, "review-not-built"), self.rules())

    def test_safety_stays_unverified_whatever_a_record_says(self):
        self.kitchen.change(BUTTER, lambda thing: thing["safety"].update(state="verified"))
        self.assertIn((BUTTER, "safety-not-earned"), self.rules())

    def test_a_fact_taken_from_a_source_may_still_be_sourced_with_no_record(self):
        regulated = [{"where": "european-union", "source": SOURCE, "name": "Milk and products thereof",
                      "standing": "mandatory", "exemptions": None, "note": None, "tier": "sourced"}]
        self.kitchen.change("graph/fact/dairy.json", lambda thing: thing.update(tier="sourced", regulated=regulated))
        self.assertEqual([], self.issues())


if __name__ == "__main__":
    unittest.main()
