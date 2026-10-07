"""The rules about the parts of a dish or a preparation, and the recipe lines that fill them."""

from tools.reading import Issue
from tools.rules import everything_inside, of_kind


def part_ids_once(things):
    """The parts of one dish or preparation each have an id of their own, so that a line can point at one."""
    issues = []
    for kind in ("dish", "preparation"):
        for thing_id, thing in of_kind(things, kind):
            ids = [part["id"] for part in thing.data["parts"]]
            for part_id in sorted(set(ids)):
                if ids.count(part_id) > 1:
                    message = "the part id '%s' is used %d times" % (part_id, ids.count(part_id))
                    issues.append(Issue(thing.path, "parts", "part-id-twice", message))
    return issues


def may_fill(part, things):
    """What may fill a part: its options, and whatever a preparation among them is made of."""
    allowed = set(part["options"])
    for option in part["options"]:
        if option.startswith("preparation/"):
            allowed.update(everything_inside(option, things))
    return allowed


def lines_fill_parts(things):
    """A line says which part of its dish it fills, and uses one of that part's options. Every part that is not optional is filled."""
    issues = []
    for recipe_id, recipe in of_kind(things, "recipe"):
        whole = things.get(recipe.data["makes"])
        if whole is None:
            continue
        parts = {part["id"]: part for part in whole.data["parts"]}
        filled = set()
        for index, line in enumerate(recipe.data["ingredients"]):
            where = "ingredients[%d].part" % index
            part = parts.get(line["part"])
            if part is None:
                message = "'%s' has no part '%s'" % (recipe.data["makes"], line["part"])
                issues.append(Issue(recipe.path, where, "part-unknown", message))
            elif line["thing"] not in may_fill(part, things):
                message = "'%s' is no option of the part '%s'" % (line["thing"], line["part"])
                issues.append(Issue(recipe.path, where, "not-an-option-of-its-part", message))
            else:
                filled.add(line["part"])
        for part_id, part in sorted(parts.items()):
            if not part["optional"] and part_id not in filled:
                message = "no line fills the part '%s', and it is not optional" % part_id
                issues.append(Issue(recipe.path, "ingredients", "part-not-filled", message))
    return issues


RULES = [part_ids_once, lines_fill_parts]
