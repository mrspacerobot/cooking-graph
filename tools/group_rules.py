"""The rules about groups: what a technique works on, and what a step may work on.

A group holds ingredients and preparations that behave alike in cooking. A
technique names groups, so that its card speaks of a kind of food and not of
a list. A step may work only on what its technique's card works on.
"""

from tools.reading import Issue
from tools.rules import linked, of_kind

MOST_SINGLE_THINGS = 3  # a technique may name this many single things beside its groups


def groups_above(things):
    """The wider groups each group sits within, the nearest first."""
    within = {}
    for group_id, group in of_kind(things, "group"):
        if group.data["within"] is not None:
            within[group_id] = group.data["within"]["thing"]
    above = {}
    for group_id, group in of_kind(things, "group"):
        chain = []
        wider = within.get(group_id)
        while wider is not None and wider not in chain and wider != group_id:
            chain.append(wider)
            wider = within.get(wider)
        above[group_id] = chain
    return above


def members_of_groups(things):
    """The ingredients and preparations each group holds, counting those of the narrower groups within it."""
    above = groups_above(things)
    members = {group_id: set() for group_id in above}
    for kind in ("ingredient", "preparation"):
        for thing_id, thing in of_kind(things, kind):
            for group_id in linked(thing.data["groups"]):
                for holder in [group_id] + above.get(group_id, []):
                    members.setdefault(holder, set()).add(thing_id)
    return members


def groups_have_members(things):
    """A group has at least two members, or says why it stands alone for now."""
    members = members_of_groups(things)
    issues = []
    for group_id, group in of_kind(things, "group"):
        if len(members.get(group_id, ())) < 2 and group.data["stands_alone"] is None:
            message = "has fewer than two members and does not say why it stands alone"
            issues.append(Issue(group.path, "stands_alone", "group-too-small", message))
    return issues


def worked_on(technique, members):
    """Everything a technique's card works on: its single things, and every member of its groups."""
    covered = set()
    for target in linked(technique.data["works_on"]):
        if target.startswith("group/"):
            covered.update(members.get(target, ()))
        else:
            covered.add(target)
    return covered


def techniques_name_groups(things):
    """A technique works on groups. It names at most a few single things, and none a group of its own already holds."""
    members = members_of_groups(things)
    issues = []
    for technique_id, technique in of_kind(things, "technique"):
        targets = linked(technique.data["works_on"])
        singles = [target for target in targets if not target.startswith("group/")]
        if len(singles) > MOST_SINGLE_THINGS:
            message = "names %d single things. Name a group, or at most %d things nothing else behaves like" % (len(singles), MOST_SINGLE_THINGS)
            issues.append(Issue(technique.path, "works_on", "too-many-single-things", message))
        through_groups = set()
        for target in targets:
            if target.startswith("group/"):
                through_groups.update(members.get(target, ()))
        for single in singles:
            if single in through_groups:
                message = "'%s' is already in a group this technique works on" % single
                issues.append(Issue(technique.path, "works_on", "already-in-a-group", message))
    return issues


def steps_work_on_what_the_card_says(things):
    """What a step's technique works on is something its card works on, directly or through a group."""
    members = members_of_groups(things)
    covered = {technique_id: worked_on(technique, members) for technique_id, technique in of_kind(things, "technique")}
    issues = []
    for recipe_id, recipe in of_kind(things, "recipe"):
        for index, step in enumerate(recipe.data["steps"]):
            if step["technique"] not in covered:
                continue  # the card itself has an issue, which is reported first
            for target in step["works_on"]:
                if target not in covered[step["technique"]]:
                    where = "steps[%d].works_on" % index
                    message = "the card of '%s' does not work on '%s', directly or through a group" % (step["technique"], target)
                    issues.append(Issue(recipe.path, where, "not-what-the-technique-works-on", message))
    return issues


RULES = [groups_have_members, techniques_name_groups, steps_work_on_what_the_card_says]
