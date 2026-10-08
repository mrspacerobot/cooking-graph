"""Two drafters write stand-in rows without seeing each other. Only what both write is kept."""

import unittest

from tools import stand_in_merge


def row(thing="ingredient/butter", allows=True, when=(), not_when=(), ratio=None, caveat="It tastes milder."):
    return {"thing": thing, "allows": allows, "when": list(when), "not_when": list(not_when), "ratio": ratio, "caveat": caveat, "tier": "drafted"}


def change(file="graph/ingredient/ghee.json", **more):
    return {"file": file, "field": "stands_in_for", "add": row(**more), "why": "same group"}


def ratio(stand_in, original, by="weight"):
    return {"stand_in": stand_in, "original": original, "by": by}


class StandInMergeTest(unittest.TestCase):
    def merge(self, first, second):
        return stand_in_merge.merge(first, second)

    def test_a_pair_both_write_with_the_same_verdict_is_kept(self):
        result = self.merge([change(when=["technique/saute"])], [change(when=["technique/saute"], caveat="It browns later.")])
        self.assertEqual(1, len(result.agreed))
        self.assertEqual([], result.disputed + result.single)
        self.assertEqual("It tastes milder.", result.agreed[0]["add"]["caveat"])

    def test_the_kept_row_is_always_drafted(self):
        result = self.merge([change()], [change()])
        self.assertEqual("drafted", result.agreed[0]["add"]["tier"])

    def test_when_the_contexts_differ_only_the_shared_ones_are_kept(self):
        result = self.merge([change(when=["technique/saute", "technique/sear"])], [change(when=["technique/sear", "technique/fry"])])
        self.assertEqual(["technique/sear"], result.agreed[0]["add"]["when"])

    def test_contexts_that_share_nothing_are_disputed(self):
        result = self.merge([change(when=["technique/saute"])], [change(when=["technique/poach"])])
        self.assertEqual([], result.agreed)
        self.assertEqual("contexts-do-not-overlap", result.disputed[0].why)

    def test_one_drafter_naming_no_context_takes_the_context_of_the_other(self):
        result = self.merge([change(when=[])], [change(when=["technique/saute"])])
        self.assertEqual(["technique/saute"], result.agreed[0]["add"]["when"])

    def test_the_exclusions_of_both_are_kept(self):
        result = self.merge([change(not_when=["technique/emulsify"])], [change(not_when=["preparation/hollandaise"])])
        self.assertEqual(["preparation/hollandaise", "technique/emulsify"], sorted(result.agreed[0]["add"]["not_when"]))

    def test_a_pair_one_says_works_and_the_other_says_fails_is_disputed(self):
        result = self.merge([change()], [change(allows=False, not_when=["technique/emulsify"])])
        self.assertEqual([], result.agreed)
        self.assertEqual("verdicts-differ", result.disputed[0].why)

    def test_two_exclusions_are_kept_with_all_their_contexts(self):
        result = self.merge([change(allows=False, not_when=["technique/emulsify"])], [change(allows=False, not_when=["technique/whisk"])])
        self.assertFalse(result.agreed[0]["add"]["allows"])
        self.assertEqual(["technique/emulsify", "technique/whisk"], sorted(result.agreed[0]["add"]["not_when"]))
        self.assertEqual([], result.agreed[0]["add"]["when"])

    def test_a_pair_only_one_wrote_is_listed_and_not_kept(self):
        result = self.merge([change()], [change(file="graph/ingredient/oil.json")])
        self.assertEqual([], result.agreed)
        self.assertEqual({"graph/ingredient/ghee.json", "graph/ingredient/oil.json"}, {one["file"] for one in result.single})

    def test_close_ratios_are_averaged(self):
        result = self.merge([change(ratio=ratio(1, 1))], [change(ratio=ratio(1, 1.1))])
        kept = result.agreed[0]["add"]["ratio"]
        self.assertEqual("weight", kept["by"])
        self.assertAlmostEqual(1.0, kept["stand_in"] / kept["original"], delta=0.1)

    def test_ratios_that_disagree_are_dropped_and_the_row_kept(self):
        result = self.merge([change(ratio=ratio(1, 1))], [change(ratio=ratio(1, 2))])
        self.assertIsNone(result.agreed[0]["add"]["ratio"])

    def test_a_ratio_only_one_gave_is_dropped(self):
        result = self.merge([change(ratio=ratio(1, 1))], [change()])
        self.assertIsNone(result.agreed[0]["add"]["ratio"])

    def test_an_exclusion_with_a_when_is_refused_as_invalid(self):
        result = self.merge([change(allows=False, when=["technique/saute"], not_when=["technique/sear"])], [change(allows=False, not_when=["technique/sear"])])
        self.assertEqual("exclusion-with-a-context", result.disputed[0].why)

    def test_the_result_is_the_same_in_either_order_of_the_drafters(self):
        first = [change(when=["technique/saute"]), change(file="graph/ingredient/oil.json", thing="ingredient/lard")]
        second = [change(file="graph/ingredient/oil.json", thing="ingredient/lard"), change(when=["technique/saute"])]
        one = self.merge(first, second)
        two = self.merge(second, first)
        self.assertEqual(sorted(x["file"] + x["add"]["thing"] for x in one.agreed), sorted(x["file"] + x["add"]["thing"] for x in two.agreed))

    def test_the_report_names_counts_and_every_dispute_and_single(self):
        result = self.merge([change(when=["technique/saute"]), change(file="graph/ingredient/oil.json")], [change(when=["technique/poach"])])
        lines = stand_in_merge.report(result)
        self.assertTrue(any(line.startswith("agreed: 0") for line in lines))
        self.assertTrue(any("contexts-do-not-overlap" in line and "ghee" in line for line in lines))
        self.assertTrue(any("only one drafter" in line and "oil" in line for line in lines))


if __name__ == "__main__":
    unittest.main()
