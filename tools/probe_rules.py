"""The rules about probes: who they are written for, which are held back, and what may not be written for them."""

from tools import names, probes, writing
from tools.reading import Issue
from tools.rules import linked, of_kind, skills_of

PROBE_KINDS = ("dish-probe", "safety-probe", "stand-in-probe", "kitchen-probe")


def every_skill(things):
    slugs = set()
    for thing_id, thing in of_kind(things, "program"):
        slugs.update(skill["slug"] for skill in skills_of(thing.data))
    return slugs


def skills_by_cuisine(things):
    """The skills of the programs each cuisine has. A cuisine with no program yet has none."""
    found = {}
    for thing_id, thing in of_kind(things, "program"):
        slugs = {skill["slug"] for skill in skills_of(thing.data)}
        for cuisine_id in linked(thing.data["belongs_to"]):
            found.setdefault(cuisine_id, set()).update(slugs)
    return found


def probes_name_a_cuisine(things):
    """A dish probe says which cuisine it asks about, and that cuisine is in the graph."""
    issues = []
    for thing_id, thing in of_kind(things, "dish-probe"):
        if "cuisine/" + thing.data["cuisine"] not in things:
            message = "'%s' is no cuisine of the graph" % thing.data["cuisine"]
            issues.append(Issue(thing.path, "cuisine", "cuisine-unknown", message))
    return issues


def probes_name_a_skill(things):
    """A dish probe is written for a skill of a program of its cuisine.

    A cuisine with no program yet has no skills to name, so its probes name
    any topic. They name a skill once the cuisine has a program.
    """
    skills = skills_by_cuisine(things)
    issues = []
    for thing_id, thing in of_kind(things, "dish-probe"):
        known = skills.get("cuisine/" + thing.data["cuisine"])
        if known is not None and thing.data["written_for"] not in known:
            message = "'%s' is no skill of a program of the cuisine '%s'" % (thing.data["written_for"], thing.data["cuisine"])
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


WRITTEN_KINDS = ("dish", "recipe", "preparation")  # what a probe's dish may already be written as


def names_of_what_is_written(things):
    found = set()
    for kind in WRITTEN_KINDS:
        for thing_id, thing in of_kind(things, kind):
            found.update(names.plain_names(thing.data))
    return found


def may_not_be_held_back(things, probe_ids):
    """The dish probes that are never held back: a level is practised through their dish, or their dish is written.

    Nothing that is already written becomes held back, be it written as a
    dish, a recipe or a preparation, and no level is left without its dish
    because a hash fell badly.
    """
    taken = names_of_level_dishes(things) | names_of_what_is_written(things)
    return {probe_id for probe_id in probe_ids if probes.dish_names(things[probe_id].data) & taken}


def expected_sets(things):
    """The set each probe belongs in, by the rule and never by hand: {probe id: 'held-back' or 'growing'}."""
    expected = {}
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
                expected[probe_id] = "held-back" if probe_id in held_back else "growing"
    return expected


def about_sets(things, probe_ids, rule, message):
    """One issue for each kind and batch of probes, naming a count and never a probe.

    A drafter reads the checker's output. A path or a message that named a held-back
    probe would tell the drafter which dish it asks about.
    """
    counts = {}
    for probe_id in probe_ids:
        key = (things[probe_id].kind, things[probe_id].data["batch"])
        counts[key] = counts.get(key, 0) + 1
    return [Issue("probes/" + kind, "set", rule, message % (count, batch))
            for (kind, batch), count in sorted(counts.items())]


def held_back_by_the_rule(things):
    """Which probes are held back is decided by the rule in tools/probes.py, never by hand."""
    wrong = [probe_id for probe_id, expected in expected_sets(things).items() if things[probe_id].data["set"] != expected]
    message = "%d probes of batch '%s' are in another set than the rule gives: run ./probe reset-sets"
    return about_sets(things, wrong, "held-back-rule", message)


def reset_sets(root, things):
    """Put every probe in the set the rule gives. Return how many moved. Nothing about them is printed."""
    moved = 0
    for probe_id, expected in sorted(expected_sets(things).items()):
        data = things[probe_id].data
        if data["set"] != expected:
            writing.write_thing(root, dict(data, set=expected))
            moved += 1
    return moved


def level_dishes_are_never_held_back(things):
    """A dish that a level of a program is practised through is never held back."""
    level_dishes = names_of_level_dishes(things)
    wrong = [thing_id for thing_id, thing in of_kind(things, "dish-probe")
             if thing.data["set"] == "held-back" and probes.dish_names(thing.data) & level_dishes]
    message = "%d probes of batch '%s' ask about a dish a level is practised through, so they belong in the growing set: run ./probe reset-sets"
    return about_sets(things, wrong, "level-dish-held-back", message)


def one_probe_per_dish_in_a_batch(things):
    """One batch asks about a dish once. Another batch, by another writer, may ask again."""
    issues = []
    for kind in ("dish-probe", "safety-probe"):
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
    for kind in WRITTEN_KINDS:
        for thing_id, thing in of_kind(things, kind):
            if names.plain_names(thing.data) & held_back_names:
                message = "a held-back probe asks about this dish, so it may not be written"
                issues.append(Issue(thing.path, "names", "drafted-towards-held-back", message))
    return issues


def question_once_per_batch(things):
    issues = []
    for kind in ("stand-in-probe", "kitchen-probe"):
        owners = {}
        for probe_id, thing in of_kind(things, kind):
            data = thing.data
            if kind == "stand-in-probe":
                question = tuple(names.plain(data[field]) for field in ("recipe", "ingredient", "candidate"))
            else:
                question = (names.plain(data["technique"]), tuple(sorted({names.plain(word) for word in data["at_home"]})))
            key = (data["batch"], question)
            owners.setdefault(key, []).append(thing.path)
        for paths in owners.values():
            if len(paths) > 1:
                for path in paths:
                    issues.append(Issue(path, "batch", "same-question-twice", "this batch already asks this question"))
    return issues


RULES = [
    probes_name_a_cuisine,
    probes_name_a_skill,
    held_back_by_the_rule,
    level_dishes_are_never_held_back,
    one_probe_per_dish_in_a_batch,
    nothing_drafted_towards_held_back,
    question_once_per_batch,
]
