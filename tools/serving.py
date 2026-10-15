"""The serving section of the release: what a server needs about each recipe, worked out here so it only compares sets.

For a recipe, `unsafe_for` lists every fact that some required line is not free of, as written (a fact a food does
not answer counts against it, as everywhere). A cook avoiding any of them is refused the recipe. Optional parts are
listed apart: they are left out for a cook they are unsafe for, and never make the recipe unsafe.
"""

from tools import queries, query_safety


def facts_in(things):
    return sorted(thing_id for thing_id, thing in things.items() if thing.kind == "fact")


def unsafe_facts(things, thing_ids, facts):
    return [fact for fact in facts if any(not query_safety.free_of(things, one, [fact]) for one in thing_ids)]


def recipe_entry(things, recipe_id, facts):
    recipe = things[recipe_id].data
    required, optional = queries.required_lines(things, recipe)
    return {
        "makes": recipe["makes"],
        "tier": recipe["tier"],
        "techniques": sorted({step["technique"] for step in recipe["steps"]}),
        "ingredients": sorted({line["thing"] for line in recipe["ingredients"]}),
        "equipment": sorted(recipe["equipment"]),
        "unsafe_for": unsafe_facts(things, sorted({line["thing"] for line in required}), facts),
        "optional_parts": [{"part": part, "unsafe_for": unsafe_facts(things, sorted({line["thing"] for line in lines}), facts)}
                           for part, lines in sorted(optional.items())],
    }


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
    """Cases written by the reference (`queries.as_written`), not by the section above, so a server that checks the
    section against them is checked against the rules and not against a copy of itself."""
    recipes = sorted(thing_id for thing_id, thing in things.items() if thing.kind == "recipe")
    cases = []
    for avoid in avoid_sets(facts_in(things)):
        offered = [recipe for recipe in recipes if queries.as_written(things, recipe, avoid)["status"] == "ok"]
        cases.append({"avoid": avoid, "offered": offered})
    return {"cases": cases}
