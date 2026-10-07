"""Runs the safety probes: what a dish holds, worked out from its recipe, against what a probe says.

A safety probe names a well-known dish, what it holds and what it does not,
in plain words. For a dish that is in the graph, the facts it holds are worked
out from the ingredients of its recipe and nothing else. A dish that is not in
the graph is not answerable. That is no disagreement.

A disagreement is never settled here. Both sides are written down for a person.
"""

from collections import namedtuple

from tools import names

Result = namedtuple("Result", ["growing", "held_back"])
Answer = namedtuple("Answer", ["probe_id", "probe", "dish_id", "verdict", "graph_holds", "disagreements", "unknown_words"])


def recipe_that_makes(thing_id, things):
    """The recipe that makes a thing, the first by id when there are several, or None."""
    for recipe_id, recipe in sorted(things.items()):
        if recipe.kind == "recipe" and recipe.data["makes"] == thing_id:
            return recipe
    return None


def add_facts(found, thing_id, things, seen):
    """Add what one ingredient or preparation holds: for each fact, where it comes from and whether that is certain."""
    if thing_id in seen or thing_id not in things:
        return
    seen.add(thing_id)
    thing = things[thing_id]
    if thing.kind == "ingredient":
        for row in thing.data["safety"]["contains"]:
            found.setdefault(row["fact"], []).append((thing_id, row["basis"], row["certain"]))
        return
    recipe = recipe_that_makes(thing_id, things)
    if recipe is not None:
        for line in recipe.data["ingredients"]:
            add_facts(found, line["thing"], things, seen)
        return
    for part in thing.data["parts"]:  # no recipe: every option of every part, the strict reading
        for option in part["options"]:
            add_facts(found, option, things, seen)


def facts_of_recipe(recipe, things):
    found = {}
    seen = set()
    for line in recipe.data["ingredients"]:
        add_facts(found, line["thing"], things, seen)
    return found


def fact_index(things):
    """Which fact each plain word names."""
    index = {}
    for thing_id, thing in things.items():
        if thing.kind == "fact":
            for name in names.plain_names(thing.data):
                index[name] = thing_id
    return index


def dish_for(probe, things):
    wanted = {names.plain(name) for name in [probe["dish"]] + probe["also_called"]}
    for thing_id, thing in sorted(things.items()):
        if thing.kind == "dish" and names.plain_names(thing.data) & wanted:
            return thing_id
    return None


def answer(probe, things, facts_by_word):
    dish_id = dish_for(probe, things)
    recipe = recipe_that_makes(dish_id, things) if dish_id else None
    if recipe is None:
        return Answer(probe["id"], probe, dish_id, "not answerable", {}, [], [])
    graph_holds = facts_of_recipe(recipe, things)
    disagreements = []
    unknown = []
    for word in probe["holds"]:
        fact = facts_by_word.get(names.plain(word))
        if fact is None:
            unknown.append(word)
        elif fact not in graph_holds:
            disagreements.append(("the probe says it holds", word, fact))
    for word in probe["does_not_hold"]:
        fact = facts_by_word.get(names.plain(word))
        if fact is None:
            unknown.append(word)
        elif fact in graph_holds:
            disagreements.append(("the probe says it does not hold", word, fact))
    verdict = "disagrees" if disagreements else "agrees"
    return Answer(probe["id"], probe, dish_id, verdict, graph_holds, disagreements, unknown)


def run(things):
    facts_by_word = fact_index(things)
    result = Result(growing=[], held_back=[])
    for thing_id, thing in sorted(things.items()):
        if thing.kind != "safety-probe":
            continue
        one = answer(thing.data, things, facts_by_word)
        if thing.data["set"] == "held-back":
            result.held_back.append(one)
        else:
            result.growing.append(one)
    return result


def count(answers):
    return {
        "probes": len(answers),
        "answerable": len([one for one in answers if one.verdict != "not answerable"]),
        "agreeing": len([one for one in answers if one.verdict == "agrees"]),
        "disagreeing": len([one for one in answers if one.verdict == "disagrees"]),
    }


def counts(result):
    return {"growing": count(result.growing), "held-back": count(result.held_back)}


def report(result):
    lines = []
    for name, numbers in counts(result).items():
        line = "Safety probes, %s: %d. Answerable %d, agreeing %d, disagreeing %d."
        lines.append(line % (name, numbers["probes"], numbers["answerable"], numbers["agreeing"], numbers["disagreeing"]))
    unknown = sorted({names.plain(word) for one in result.growing for word in one.unknown_words})
    lines.append("Words of the growing probes that name no fact: %s" % (", ".join(unknown) or "none"))
    lines.append("What a held-back probe disagrees with is never shown.")
    return "\n".join(lines)


def where_from(sources):
    parts = []
    for ingredient_id, basis, certain in sources:
        sure = "certain" if certain else "recorded strictly, not certain"
        parts.append("`%s` (%s %s)" % (ingredient_id, basis.rstrip("."), sure))
    return "; ".join(parts)


def disagreement_lines(one):
    probe = one.probe
    lines = ["## %s" % probe["dish"], ""]
    lines.append("- **Probe:** `%s`, written by %s." % (probe["id"], probe["written_by"]))
    lines.append("- **The probe says it holds:** %s." % (", ".join(probe["holds"]) or "nothing"))
    lines.append("- **The probe says it does not hold:** %s." % (", ".join(probe["does_not_hold"]) or "nothing"))
    lines.append("- **The probe's reason:** %s" % probe["why"])
    lines.append("- **The graph's dish:** `%s`. From the ingredients of its recipe it holds:" % one.dish_id)
    for fact, sources in sorted(one.graph_holds.items()):
        lines.append("  - `%s`, from %s" % (fact, where_from(sources)))
    lines.append("- **Where they disagree:**")
    for side, word, fact in one.disagreements:
        graph_side = "the graph says it does not" if side == "the probe says it holds" else "the graph says it does"
        lines.append("  - %s %s (`%s`), and %s." % (side, word, fact, graph_side))
    lines.append("")
    return lines


def disagreements_document(result):
    """Every disagreement of a growing probe, with both sides. Held-back probes add to the counts and to nothing else."""
    numbers = counts(result)
    lines = [
        "# Where the safety probes and the graph disagree",
        "",
        "Written by `./safety disagreements`. Nothing here is settled: each disagreement is for a person to rule on.",
        "The graph's side is worked out from the ingredients of the dish's recipe, and every safety record behind it is unverified.",
        "",
        "| Set | Probes | Answerable | Agreeing | Disagreeing |",
        "|---|---|---|---|---|",
    ]
    for name in ("growing", "held-back"):
        row = numbers[name]
        lines.append("| %s | %d | %d | %d | %d |" % (name, row["probes"], row["answerable"], row["agreeing"], row["disagreeing"]))
    lines.extend(["", "A probe is not answerable when its dish is not in the graph or has no recipe. What a held-back probe disagrees with is counted and never shown.", ""])
    for one in result.growing:
        if one.verdict == "disagrees":
            lines.extend(disagreement_lines(one))
    return "\n".join(lines).rstrip() + "\n"
