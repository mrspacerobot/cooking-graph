"""The serving section of the release: what a server needs about each recipe, worked out here so it only compares sets.

For a recipe, each line lists the facts its food is not free of (a fact a food does not answer counts against it, as
everywhere) and every swap the graph allows in this dish, each with the facts it is not free of. A line is fine for a
cook when its food or one of its swaps is safe for what they avoid; a recipe is offered when every required line is.
`unsafe_for` on the recipe is the same question without swaps. Optional parts are left out for a cook they are
unsafe for, and never make the recipe unsafe.
"""

from tools import queries, query_safety


def facts_in(things):
    return sorted(thing_id for thing_id, thing in things.items() if thing.kind == "fact")


def unsafe_facts(things, thing_ids, facts):
    return [fact for fact in facts if any(not query_safety.free_of(things, one, [fact]) for one in thing_ids)]


def swap_entry(things, option, facts):
    return {"thing": option["thing"], "unsafe_for": unsafe_facts(things, [option["thing"]], facts),
            "basis": option["basis"], "ratio": option["ratio"], "caveat": option["caveat"], "tier": option["tier"]}


def line_entry(things, line, optional_parts, facts):
    """One recipe line: what it is unsafe for, and every swap the graph allows in this dish, each with the same.

    The swaps do not depend on what a cook avoids except for whether the swap itself is safe, so they are listed
    in full and a server keeps the safe ones."""
    return {"thing": line["original"], "part": line["part"], "optional": line["part"] in optional_parts,
            "unsafe_for": unsafe_facts(things, [line["original"]], facts),
            "swaps": [swap_entry(things, option, facts) for option in line["options"]]}


def recipe_entry(things, recipe_id, facts):
    recipe = things[recipe_id].data
    optional_parts = {part["id"] for part in things[recipe["makes"]].data["parts"] if part["optional"]}
    required, optional = queries.required_lines(things, recipe)
    lines = [line_entry(things, line, optional_parts, facts) for line in queries.stand_ins(things, recipe_id)["lines"]]
    return {
        "makes": recipe["makes"],
        "tier": recipe["tier"],
        "techniques": sorted({step["technique"] for step in recipe["steps"]}),
        "ingredients": sorted({line["thing"] for line in recipe["ingredients"]}),
        "equipment": sorted(recipe["equipment"]),
        "unsafe_for": unsafe_facts(things, sorted({line["thing"] for line in required}), facts),
        "optional_parts": [{"part": part, "unsafe_for": unsafe_facts(things, sorted({line["thing"] for line in lines}), facts)}
                           for part, lines in sorted(optional.items())],
        "lines": lines,
    }


def line_is_fine(line, avoided):
    """The one rule a server applies: the food is safe, or one of its allowed swaps is."""
    if not avoided & set(line["unsafe_for"]):
        return True
    return any(not avoided & set(swap["unsafe_for"]) for swap in line["swaps"])


def offered(entry, avoided):
    """Is the recipe offered to a cook avoiding these facts, with swaps? An optional part with no way is left out."""
    return all(line_is_fine(line, avoided) for line in entry["lines"] if not line["optional"])


def serving_of(things):
    facts = facts_in(things)
    recipes = sorted(thing_id for thing_id, thing in things.items() if thing.kind == "recipe")
    return {"facts": facts, "recipes": {recipe_id: recipe_entry(things, recipe_id, facts) for recipe_id in recipes}}


def avoid_sets(facts):
    """Nothing, each fact alone, each fact with the next, and everything: enough to catch a wrong intersection."""
    sets = [[]]
    sets += [[fact] for fact in facts]
    sets += [[first, second] for first, second in zip(facts, facts[1:])]
    sets.append(list(facts))
    return sets


def vectors_of(things):
    """Cases written by the reference (`queries.can_make`), not by the section above, so a server that checks the
    section against them is checked against the rules and not against a copy of itself."""
    recipes = sorted(thing_id for thing_id, thing in things.items() if thing.kind == "recipe")
    cases = []
    for avoid in avoid_sets(facts_in(things)):
        offered = [recipe for recipe in recipes if queries.can_make(things, recipe, avoid)["status"] == "ok"]
        cases.append({"avoid": avoid, "offered": offered})
    return {"cases": cases}
