"""The rules that need more than one field, or more than one file, to decide.

Each rule takes the sound things (the files whose shape is right), by id, and
returns the issues it finds. A rule never reads a file whose shape is wrong:
the shape issue is reported first and the rest follows once it is fixed.
"""

import os

from tools import names
from tools.reading import Issue, join, nested

LOWEST_TIER = "drafted"
EM_DASH = chr(0x2014)  # written as a number so that this file holds none
FOLDERS_NOT_READ = {".git", "__pycache__", ".venv", "out"}


def of_kind(things, kind):
    return [(thing_id, thing) for thing_id, thing in sorted(things.items()) if thing.kind == kind]


def linked(links):
    return [link["thing"] for link in links]


SAME_AS_KINDS = ("ingredient", "preparation", "dish")


def names_a_source(thing, where):
    """True for a row that names the page it was taken from: where a fact is regulated, or the id a public dataset gives a thing.

    A fact with a sourced regulated row may be sourced itself. A thing with an id from a dataset stays drafted:
    only the row is sourced.
    """
    if thing.kind in SAME_AS_KINDS:
        return where.startswith("same_as[")
    if thing.kind != "fact":
        return False
    if where.startswith("regulated["):
        return True
    return where == "" and any(row["tier"] == "sourced" for row in thing.data["regulated"])


def same_as_source_allowed(things):
    """An id taken from a public dataset may be sourced only when the source says it may be used in a product that is sold."""
    issues = []
    for kind in SAME_AS_KINDS:
        for thing_id, thing in of_kind(things, kind):
            for index, row in enumerate(thing.data["same_as"]):
                source = things.get(row["source"])
                if row["tier"] == "sourced" and source is not None and source.data["commercial_use"] != "allowed":
                    message = "'%s' may not be used in a product that is sold, so its id cannot be sourced" % row["source"]
                    issues.append(Issue(thing.path, "same_as[%d]" % index, "same-as-source-not-allowed", message))
    return issues


def same_as_once(things):
    """One id of one dataset names one thing. Two things with the same id are probably one thing."""
    owners = {}
    for kind in SAME_AS_KINDS:
        for thing_id, thing in of_kind(things, kind):
            for row in thing.data["same_as"]:
                owners.setdefault((kind in FOOD_KINDS and "food" or kind, row["source"], row["id"]), []).append(thing_id)
    issues = []
    for (family, source, identifier), sharing in sorted(owners.items()):
        if len(sharing) < 2:
            continue
        for thing_id in sharing:
            others = ", ".join(other for other in sharing if other != thing_id)
            message = "the id '%s' of '%s' is also the id of %s" % (identifier, source, others)
            issues.append(Issue(things[thing_id].path, "same_as", "same-id-twice", message))
    return issues


def regulated_once(things):
    """A fact says once what its standing is in a place. Mandatory and recommended may both stand, as in Japan."""
    issues = []
    for thing_id, thing in of_kind(things, "fact"):
        seen = set()
        for index, row in enumerate(thing.data["regulated"]):
            key = (row["where"], row["standing"])
            if key in seen:
                message = "'%s' is already said to be %s in %s" % (thing_id, row["standing"], row["where"])
                issues.append(Issue(thing.path, "regulated[%d]" % index, "regulated-twice", message))
            seen.add(key)
    return issues


def held(thing):
    """The ids of the facts an ingredient holds."""
    return [row["fact"] for row in thing.data["safety"]["contains"]]


def safety_earned(things):
    """Only a person's live, evidenced review can verify ingredient safety."""
    from tools.review_rules import safety_not_earned
    return safety_not_earned(things)


def facts_answered(things):
    """An ingredient answers every fact, yes or no. A fact nobody thought of is never read as 'free of'."""
    every_fact = {thing_id for thing_id, thing in of_kind(things, "fact")}
    issues = []
    for thing_id, thing in of_kind(things, "ingredient"):
        contains = set(held(thing))
        free_of = set(thing.data["safety"]["free_of"])
        for fact in sorted(contains & free_of):
            message = "'%s' is answered both ways" % fact
            issues.append(Issue(thing.path, "safety", "fact-answered-twice", message))
        for fact in sorted(every_fact - contains - free_of):
            message = "'%s' is not answered: list it under contains or free_of" % fact
            issues.append(Issue(thing.path, "safety", "fact-not-answered", message))
    return issues


def facts_missing_above(thing, things, field):
    """The facts a thing holds that something it points at through `field` does not hold, with that thing."""
    holds = set(held(thing))
    found = []
    for above_id in linked(thing.data[field]):
        above = things.get(above_id)
        if above is not None:
            for fact in sorted(holds - set(held(above))):
                found.append((fact, above_id))
    return found


def classes_as_strict_as_members(things):
    """What a member holds, its class holds too. Stock is at least as strict as chicken stock."""
    issues = []
    for thing_id, thing in of_kind(things, "ingredient"):
        for fact, class_id in facts_missing_above(thing, things, "is_a"):
            message = "holds '%s' but its class '%s' does not" % (fact, class_id)
            issues.append(Issue(thing.path, "safety.contains", "class-less-strict", message))
    return issues


def wholes_as_strict_as_parts(things):
    """What a part holds, its whole holds too. An egg is at least as strict as its yolk."""
    issues = []
    for thing_id, thing in of_kind(things, "ingredient"):
        for fact, whole_id in facts_missing_above(thing, things, "part_of"):
            message = "holds '%s' but the whole it is part of, '%s', does not" % (fact, whole_id)
            issues.append(Issue(thing.path, "safety.contains", "whole-less-strict", message))
    return issues


def steps_use_what_is_listed(things):
    """A step works only on what is at hand, and everything the recipe lists is used.

    At hand are the ingredients the recipe lists, the thing the recipe is
    making, and whatever this step or an earlier one leaves behind. A step
    uses a thing when it works on it or is done with it.
    """
    issues = []
    for thing_id, thing in of_kind(things, "recipe"):
        listed = [line["thing"] for line in thing.data["ingredients"]]
        at_hand = set(listed) | {thing.data["makes"]}
        used = set()
        for index, step in enumerate(thing.data["steps"]):
            at_hand.update(step["makes"])
            for field in ("works_on", "with"):
                for handled in step[field]:
                    used.add(handled)
                    if handled not in at_hand:
                        where = "steps[%d].%s" % (index, field)
                        message = "'%s' is neither an ingredient of this recipe nor left behind by a step so far" % handled
                        issues.append(Issue(thing.path, where, "step-works-on-unlisted", message))
        for index, listed_thing in enumerate(listed):
            if listed_thing not in used:
                where = "ingredients[%d]" % index
                message = "no step works on '%s'" % listed_thing
                issues.append(Issue(thing.path, where, "ingredient-never-used", message))
    return issues


def everything_inside(thing_id, things, found=None):
    """Every ingredient and preparation a dish or a preparation may hold, through all its options."""
    if found is None:
        found = set()
    whole = things.get(thing_id)
    if whole is None:
        return found
    for part in whole.data["parts"]:
        for option in part["options"]:
            if option not in found:
                found.add(option)
                if option.startswith("preparation/"):
                    everything_inside(option, things, found)
    return found


def by_products(things):
    """The preparations with no parts of their own: what a step leaves behind, such as the fond of a seared pan."""
    return {thing_id for thing_id, thing in of_kind(things, "preparation") if not thing.data["parts"]}


def by_products_stay_inside_recipes(things):
    """A by-product has no ingredients to answer for it, so it is never bought, listed or named as a part.

    What a dish holds follows from its parts. A part with nothing inside
    would be read as holding nothing, and safety never reads a gap that way.
    """
    left_behind = by_products(things)
    issues = []
    for kind in ("dish", "preparation"):
        for thing_id, thing in of_kind(things, kind):
            for index, part in enumerate(thing.data["parts"]):
                for option in part["options"]:
                    if option in left_behind:
                        message = "'%s' has no parts of its own, so it cannot be a part here" % option
                        issues.append(Issue(thing.path, "parts[%d]" % index, "by-product-as-part", message))
    for thing_id, thing in of_kind(things, "recipe"):
        for index, line in enumerate(thing.data["ingredients"]):
            if line["thing"] in left_behind:
                message = "'%s' is what a step leaves behind, not something a recipe starts from" % line["thing"]
                issues.append(Issue(thing.path, "ingredients[%d]" % index, "by-product-as-ingredient", message))
    return issues


def names_once_per_kind(things):
    """Two things of one kind never share a name. That would be two nodes for one thing."""
    owners = {}
    for thing_id, thing in sorted(things.items()):
        if thing.kind == "dish-probe":
            continue
        for name in names.plain_names(thing.data):
            owners.setdefault((thing.kind, name), []).append(thing_id)
    issues = []
    for (kind, name), sharing in sorted(owners.items()):
        if len(sharing) < 2:
            continue
        for thing_id in sharing:
            others = ", ".join(other for other in sharing if other != thing_id)
            message = "the name '%s' is also a name of %s" % (name, others)
            issues.append(Issue(things[thing_id].path, "names", "same-name-twice", message))
    return issues


FOOD_KINDS = ("ingredient", "preparation")  # the probes and the recipes look both up as one thing a cook buys or makes


def foods_share_no_name(things, known_pairs=()):
    """An ingredient and a preparation never share a name. A recipe line and a probe word would not know which is meant.

    The pairs in `known_pairs` are the things a cook either buys or makes,
    such as stock: the model cannot yet say it, and docs/model.md says so.
    """
    allowed = {frozenset(pair) for pair in known_pairs}
    owners = {}
    for thing_id, thing in sorted(things.items()):
        if thing.kind in FOOD_KINDS:
            for name in names.plain_names(thing.data):
                owners.setdefault(name, {}).setdefault(thing.kind, []).append(thing_id)
    issues = []
    for name, by_kind in sorted(owners.items()):
        if len(by_kind) < 2:
            continue
        everyone = [thing_id for ids in by_kind.values() for thing_id in ids]
        if len(everyone) == 2 and frozenset(everyone) in allowed:
            continue
        for thing_id in everyone:
            others = ", ".join(other for other in everyone if other != thing_id)
            message = "the name '%s' is an ingredient and a preparation at once: also %s" % (name, others)
            issues.append(Issue(things[thing_id].path, "names", "same-name-across-kinds", message))
    return issues


def can_reach_themselves(follows):
    """The things that come back to themselves by following the links."""

    def comes_back(start):
        seen = set()
        waiting = list(follows.get(start, []))
        while waiting:
            current = waiting.pop()
            if current == start:
                return True
            if current not in seen:
                seen.add(current)
                waiting.extend(follows.get(current, []))
        return False

    return [start for start in sorted(follows) if comes_back(start)]


def links_of(things, kind, field):
    """What each thing of a kind points at through one field."""
    follows = {}
    for thing_id, thing in of_kind(things, kind):
        value = thing.data[field]
        if value is None:
            follows[thing_id] = []
        elif isinstance(value, dict):
            follows[thing_id] = [value["thing"]]
        else:
            follows[thing_id] = linked(value)
    return follows


LOOPS_THAT_MAKE_NO_SENSE = [
    ("ingredient", "is_a"),
    ("ingredient", "part_of"),
    ("cuisine", "within"),
    ("group", "within"),
    ("technique", "comes_after"),
    ("technique", "variant_of"),
]


def no_loops(things):
    """Nothing is a kind of itself, lies within itself or comes after itself."""
    issues = []
    for kind, field in LOOPS_THAT_MAKE_NO_SENSE:
        for thing_id in can_reach_themselves(links_of(things, kind, field)):
            message = "following '%s' from here leads back here" % field
            issues.append(Issue(things[thing_id].path, field, "cycle", message))
    return issues


def skills_of(program):
    return [skill for course in program["courses"] for skill in course["skills"]]


def program_issues(thing):
    """A program holds together: one slug per skill, skills that exist, levels numbered from one."""
    found = []
    skills = skills_of(thing.data)
    slugs = [skill["slug"] for skill in skills]
    course_slugs = [course["slug"] for course in thing.data["courses"]]
    for slug in sorted(set(slugs)):
        if slugs.count(slug) > 1:
            found.append(("courses", "slug-twice", "the skill slug '%s' is used twice" % slug))
    for slug in sorted(set(course_slugs)):
        if course_slugs.count(slug) > 1:
            found.append(("courses", "slug-twice", "the course slug '%s' is used twice" % slug))
    follows = {}
    for skill in skills:
        follows[skill["slug"]] = [earlier["skill"] for earlier in skill["comes_after"]]
        for earlier in follows[skill["slug"]]:
            if earlier not in slugs:
                found.append((skill["slug"], "skill-unknown", "comes after '%s', which is no skill here" % earlier))
        numbers = [level["number"] for level in skill["levels"]]
        if numbers != list(range(1, len(numbers) + 1)):
            found.append((skill["slug"], "level-numbers", "levels must be numbered from 1, in order"))
    for slug in can_reach_themselves(follows):
        found.append((slug, "cycle", "this skill comes after itself"))
    return [Issue(thing.path, where, rule, message) for where, rule, message in found]


def programs_hold_together(things):
    issues = []
    for thing_id, thing in of_kind(things, "program"):
        issues.extend(program_issues(thing))
    return issues


def field_names(rule, found):
    """Every field name a rule of the model mentions, however deep."""
    for name, inner in list(rule.get("fields", {}).items()) + list(rule.get("with", {}).items()):
        found.add(name)
        field_names(inner, found)
    if "of" in rule:
        field_names(rule["of"], found)
    return found


def names_of_the_model(model):
    """Every kind and every field of the model, in a fixed order."""
    found = set(model["kinds"])
    for kind in model["kinds"].values():
        field_names(kind, found)
    for shape in model["shapes"].values():
        field_names(shape, found)
    return sorted(found)


def model_document(root, model):
    """docs/model.md names every kind and every field, so that the document cannot fall behind the model."""
    path = os.path.join(root, "docs", "model.md")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as handle:
        text = handle.read()
    issues = []
    for name in names_of_the_model(model):
        if "`%s`" % name not in text:
            message = "the model has '%s' and the document does not name it" % name
            issues.append(Issue("docs/model.md", "", "not-in-the-model-document", message))
    return issues


def em_dashes(root):
    """The em dash appears in no file of the repository. A plain hyphen does its work."""
    issues = []
    for folder, folders, files in os.walk(root):
        folders[:] = sorted(name for name in folders if name not in FOLDERS_NOT_READ)
        for name in sorted(files):
            path = os.path.join(folder, name)
            for number in lines_with_an_em_dash(path):
                shown = os.path.relpath(path, root).replace(os.sep, "/")
                issues.append(Issue(shown, "line %d" % number, "em-dash", "holds an em dash: use a plain hyphen"))
    return issues


def lines_with_an_em_dash(path):
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().split("\n")
    except UnicodeDecodeError:
        return []
    return [number for number, line in enumerate(lines, start=1) if EM_DASH in line]


BASE_RULES = [
    same_as_source_allowed,
    same_as_once,
    regulated_once,
    safety_earned,
    facts_answered,
    classes_as_strict_as_members,
    wholes_as_strict_as_parts,
    steps_use_what_is_listed,
    by_products_stay_inside_recipes,
    names_once_per_kind,
    no_loops,
    programs_hold_together,
]
