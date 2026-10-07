"""The rules about probes: who they are written for, which are held back, and what may not be written for them."""

from tools import names, probes
from tools.reading import Issue
from tools.rules import linked, of_kind, skills_of

PROBE_KINDS = ("dish-probe", "safety-probe")


def every_skill(things):
    slugs = set()
    for thing_id, thing in of_kind(things, "program"):
        slugs.update(skill["slug"] for skill in skills_of(thing.data))
    return slugs


def probes_name_a_skill(things):
    """A dish probe is written for a skill of a program."""
    skills = every_skill(things)
    issues = []
    for thing_id, thing in of_kind(things, "dish-probe"):
        if thing.data["written_for"] not in skills:
            message = "'%s' is no skill of any program" % thing.data["written_for"]
            issues.append(Issue(thing.path, "written_for", "skill-unknown", message))
    return issues


def names_of_level_dishes(things):
    """The plain names of every dish a level of a program is practised through."""
    found = set()
    for thing_id, thing in of_kind(things, "program"):
        for skill in skills_of(thing.data):
            for level in skill["levels"]:
                for dish_id in linked(level["through"]):
                    if dish_id.startswith("dish/") and dish_id in things:
                        found.update(names.plain_names(things[dish_id].data))
    return found


def names_of_written_dishes(things):
    found = set()
    for thing_id, thing in of_kind(things, "dish"):
        found.update(names.plain_names(thing.data))
    return found


def may_not_be_held_back(things, probe_ids):
    """The dish probes that are never held back: a level is practised through their dish, or their dish is written.

    Nothing that is already written becomes held back, and no level is left
    without its dish because a hash fell badly.
    """
    taken = names_of_level_dishes(things) | names_of_written_dishes(things)
    return {probe_id for probe_id in probe_ids if probes.dish_names(things[probe_id].data) & taken}


def held_back_by_the_rule(things):
    """Which probes are held back is decided by the rule in tools/probes.py, never by hand."""
    issues = []
    for kind in PROBE_KINDS:
        batches = {}
        for thing_id, thing in of_kind(things, kind):
            batches.setdefault(thing.data["batch"], []).append(thing_id)
        for batch, probe_ids in sorted(batches.items()):
            never = set()
            if kind == "dish-probe":
                never = may_not_be_held_back(things, probe_ids)
            held_back = probes.held_back_ids(probe_ids, never)
            for probe_id in probe_ids:
                expected = "held-back" if probe_id in held_back else "growing"
                if things[probe_id].data["set"] != expected:
                    message = "the rule puts this probe of batch '%s' in the set '%s'" % (batch, expected)
                    issues.append(Issue(things[probe_id].path, "set", "held-back-rule", message))
    return issues


def level_dishes_are_never_held_back(things):
    """A dish that a level of a program is practised through is never held back."""
    level_dishes = names_of_level_dishes(things)
    issues = []
    for thing_id, thing in of_kind(things, "dish-probe"):
        if thing.data["set"] == "held-back" and probes.dish_names(thing.data) & level_dishes:
            message = "a level of a program is practised through this dish, so its probe must be in the growing set"
            issues.append(Issue(thing.path, "set", "level-dish-held-back", message))
    return issues


def one_probe_per_dish_in_a_batch(things):
    """One batch asks about a dish once. Another batch, by another writer, may ask again."""
    issues = []
    for kind in PROBE_KINDS:
        owners = {}
        for thing_id, thing in of_kind(things, kind):
            for name in probes.dish_names(thing.data):
                owners.setdefault((thing.data["batch"], name), []).append(thing_id)
        for (batch, name), sharing in sorted(owners.items()):
            if len(sharing) < 2:
                continue
            for probe_id in sharing:
                message = "another probe of batch '%s' already asks about '%s'" % (batch, name)
                issues.append(Issue(things[probe_id].path, "dish", "same-dish-twice", message))
    return issues


def nothing_drafted_towards_held_back(things):
    """Nothing is written for a held-back dish probe. Held-back probes test the graph, they never grow it."""
    held_back_names = set()
    for thing_id, thing in of_kind(things, "dish-probe"):
        if thing.data["set"] == "held-back":
            held_back_names.update(probes.dish_names(thing.data))
    issues = []
    for kind in ("dish", "recipe", "preparation"):
        for thing_id, thing in of_kind(things, kind):
            if names.plain_names(thing.data) & held_back_names:
                message = "a held-back probe asks about this dish, so it may not be written"
                issues.append(Issue(thing.path, "names", "drafted-towards-held-back", message))
    return issues


RULES = [
    probes_name_a_skill,
    held_back_by_the_rule,
    level_dishes_are_never_held_back,
    one_probe_per_dish_in_a_batch,
    nothing_drafted_towards_held_back,
]
