"""The serving section of the release: what a server needs about each recipe, worked out here so it only compares sets.

For a recipe, each line lists the facts its food is not free of (a fact a food does not answer counts against it, as
everywhere) and every swap the graph allows in this dish, each with the facts it is not free of. A line is fine for a
cook when its food or one of its swaps is safe for what they avoid; a recipe is offered when every required line is.
`unsafe_for` on the recipe is the same question without swaps. Optional parts are left out for a cook they are
unsafe for, and never make the recipe unsafe.
"""

from tools import queries, query_safety, recipe_text, step_text


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
    return {"facts": facts, "step_text": {"proper_name_words": list(step_text.PROPER_NAME_WORDS)},
            "recipes": {recipe_id: recipe_entry(things, recipe_id, facts) for recipe_id in recipes}}


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
    return {"cases": cases, "step_text_cases": step_text_cases(things, recipes)}


def first_swaps(things, recipe_id, uncountable_only=False):
    """Every line that has a swap, replaced by its first swap: {(part, food): stand-in}. With `uncountable_only`, only
    swaps to an uncountable food count, and a line takes the first of those."""
    swaps = {}
    for line in queries.stand_ins(things, recipe_id)["lines"]:
        options = [one["thing"] for one in line["options"]]
        if uncountable_only:
            options = [thing_id for thing_id in options if things[thing_id].data["uncountable"]]
        if options:
            swaps[(line["part"], line["original"])] = options[0]
    return swaps


def step_text_case(things, recipe_id, swaps, left_out):
    recipe = things[recipe_id].data
    steps = recipe_text.rendered_steps(things, recipe, swaps, left_out)
    return {"recipe": recipe_id, "left_out": sorted(left_out),
            "swaps": [{"part": part, "thing": food, "instead": instead} for (part, food), instead in sorted(swaps.items())],
            "steps": [{"step": number, "text": text} for number, text in steps]}


def step_text_cases(things, recipes):
    """What a server must render for each recipe: as written, with each optional part left out, with every
    line that has a swap swapped, and with every line swapped to an uncountable stand-in (a plural placeholder then
    prints the name). Written by the reference (`recipe_text`), so a server that renders the same
    text is proven against it."""
    cases = []
    for recipe_id in recipes:
        recipe = things[recipe_id].data
        optional = sorted({part["id"] for part in things[recipe["makes"]].data["parts"] if part["optional"]})
        cases.append(step_text_case(things, recipe_id, {}, []))
        cases.extend(step_text_case(things, recipe_id, {}, [part]) for part in optional
                     if any(line["part"] == part for line in recipe["ingredients"]))
        swaps = first_swaps(things, recipe_id)
        if swaps:
            cases.append(step_text_case(things, recipe_id, swaps, []))
        uncountable = first_swaps(things, recipe_id, uncountable_only=True)
        if uncountable and uncountable != swaps:
            cases.append(step_text_case(things, recipe_id, uncountable, []))
    return cases
