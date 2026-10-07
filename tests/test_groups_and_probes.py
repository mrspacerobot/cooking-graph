"""Groups, what a technique may work on, and the rules about which probes are held back."""

import unittest

from tests.small_kitchen import SmallKitchen, link
from tools import check, probes

SWEAT = "graph/technique/sweat.json"
ALLIUMS = "graph/group/alliums.json"
VEGETABLES = "graph/group/vegetables.json"
ONION = "graph/ingredient/onion.json"
ALLIUM = "graph/ingredient/allium.json"
PROGRAM = "graph/program/small-program.json"
SAFETY = "probes/safety-probe/onion-soup.json"


def hidden(path):
    """Where the checker reports which set a probe is in: the folder of its kind, never the probe."""
    return "/".join(path.split("/")[:2])


class KitchenTest(unittest.TestCase):
    def setUp(self):
        self.kitchen = SmallKitchen()
        self.addCleanup(self.kitchen.close)

    def found(self):
        return {(issue.path, issue.rule) for issue in check.check_repository(self.kitchen.root)}


class Groups(KitchenTest):
    def test_a_technique_that_names_too_many_single_things(self):
        singles = ["ingredient/onion-skin", "ingredient/butter", "ingredient/flour", "preparation/roux"]
        self.kitchen.change(SWEAT, lambda thing: thing.update(works_on=[link(one) for one in singles]))
        self.assertIn((SWEAT, "too-many-single-things"), self.found())

    def test_a_technique_that_names_a_thing_its_group_already_holds(self):
        self.kitchen.change(SWEAT, lambda thing: thing["works_on"].append(link("ingredient/onion")))
        self.assertEqual({(SWEAT, "already-in-a-group")}, self.found())

    def test_a_group_with_one_member_and_no_reason(self):
        self.kitchen.change(ALLIUM, lambda thing: thing.update(groups=[]))
        self.kitchen.change(ONION, lambda thing: thing.update(groups=[]))
        self.assertIn((ALLIUMS, "group-too-small"), self.found())

    def test_a_group_with_one_member_that_says_why(self):
        self.kitchen.change(ALLIUM, lambda thing: thing.update(groups=[]))
        self.kitchen.change(ALLIUMS, lambda thing: thing.update(stands_alone="Only the onion is in the kitchen yet."))
        self.assertNotIn((ALLIUMS, "group-too-small"), self.found())

    def test_a_wide_group_counts_the_members_of_the_groups_within_it(self):
        self.assertNotIn((VEGETABLES, "group-too-small"), self.found())

    def test_a_group_within_itself(self):
        self.kitchen.change(VEGETABLES, lambda thing: thing.update(within=link("group/alliums")))
        self.assertIn((VEGETABLES, "cycle"), self.found())


class HeldBack(KitchenTest):
    def test_a_probe_that_may_not_be_held_back_is_passed_over(self):
        ids = ["dish-probe/a", "dish-probe/b", "dish-probe/c", "dish-probe/d", "dish-probe/e"]
        first = probes.held_back_ids(ids)
        second = probes.held_back_ids(ids, never=first)
        self.assertEqual(1, len(second))
        self.assertNotEqual(first, second)

    def test_fewer_are_held_back_when_too_few_may_be(self):
        ids = ["dish-probe/a", "dish-probe/b", "dish-probe/c", "dish-probe/d", "dish-probe/e"]
        self.assertEqual(set(), probes.held_back_ids(ids, never=ids))

    def test_a_probe_whose_dish_a_level_is_practised_through_is_never_held_back(self):
        path = "probes/dish-probe/buttered-onions.json"
        self.kitchen.change(path, lambda probe: probe.update(set="held-back"))
        found = self.found()
        self.assertIn((hidden(path), "level-dish-held-back"), found)
        self.assertIn((hidden(path), "held-back-rule"), found)

    def test_a_probe_for_a_preparation_that_is_written_is_never_held_back(self):
        path = self.kitchen.held_back_path()
        self.assertTrue(path.startswith("probes/dish-probe/"))
        self.kitchen.change(path, lambda probe: probe.update(dish="Roux"))
        self.assertIn((hidden(path), "held-back-rule"), self.found())

    def test_one_batch_asks_about_a_dish_once(self):
        path = "probes/dish-probe/creamed-onions.json"
        self.kitchen.change(path, lambda probe: probe.update(dish="Glazed onions"))
        rules = {rule for _, rule in self.found()}
        self.assertEqual({"same-dish-twice"}, rules)

    def test_another_batch_may_ask_about_the_same_dish(self):
        fresh = dict(self.kitchen.files["probes/dish-probe/creamed-onions.json"])
        fresh["id"] = "dish-probe/creamed-onions-again"
        fresh["batch"] = "fresh-1"
        fresh["set"] = "growing"
        self.kitchen.write("probes/dish-probe/creamed-onions-again.json", fresh)
        self.assertEqual(set(), self.found())


class SafetyProbes(KitchenTest):
    def test_a_safety_probe_with_a_field_too_many(self):
        self.kitchen.change(SAFETY, lambda probe: probe.update(written_for="sweating"))
        self.assertIn((SAFETY, "unknown-field"), self.found())

    def test_a_safety_probe_without_its_writer(self):
        self.kitchen.change(SAFETY, lambda probe: probe.pop("written_by"))
        self.assertIn((SAFETY, "missing-field"), self.found())

    def test_a_safety_probe_set_by_hand(self):
        flip = {"growing": "held-back", "held-back": "growing"}
        self.kitchen.change(SAFETY, lambda probe: probe.update(set=flip[probe["set"]]))
        self.assertIn((hidden(SAFETY), "held-back-rule"), self.found())

    def test_a_held_back_safety_probe_may_ask_about_a_dish_that_is_written(self):
        held_back = [path for path, content in self.kitchen.files.items() if path.startswith("probes/safety-probe/") and content["set"] == "held-back"]
        self.kitchen.change(held_back[0], lambda probe: probe.update(dish="Buttered onions"))
        self.kitchen.change("probes/safety-probe/buttered-onions.json", lambda probe: probe.update(dish="Onions in butter"))
        self.assertEqual(set(), self.found())


if __name__ == "__main__":
    unittest.main()
