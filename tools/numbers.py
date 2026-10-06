"""The numbers: what the graph holds, how far it can be trusted, and how many probes it answers."""

from tools import probes
from tools.reading import nested

SAFETY_STATES = ("unverified", "verified")


def add_one(counts, key):
    counts[key] = counts.get(key, 0) + 1


def count_things(things):
    """How many things of each kind sit at each tier."""
    counts = {}
    for thing in things.values():
        add_one(counts.setdefault(thing.kind, {}), thing.data["tier"])
    return counts


def count_statements(things):
    """How many statements sit at each tier. A statement is an object inside a file that carries a tier."""
    counts = {}
    for thing in things.values():
        for where, node in nested(thing.data):
            if where != "" and "tier" in node:
                add_one(counts, node["tier"])
    return counts


def count_safety(things):
    counts = {}
    for thing in things.values():
        if thing.kind == "ingredient":
            add_one(counts, thing.data["safety"]["state"])
    return counts


def count_levels(things):
    """How many levels of the programs name a technique they teach, and out of how many."""
    with_a_technique = 0
    total = 0
    for thing in things.values():
        if thing.kind != "program":
            continue
        for course in thing.data["courses"]:
            for skill in course["skills"]:
                for level in skill["levels"]:
                    total += 1
                    if level["teaches"]:
                        with_a_technique += 1
    return (with_a_technique, total)


def count_steps(things):
    return sum(len(thing.data["steps"]) for thing in things.values() if thing.kind == "recipe")


def count_safety_points(things):
    """How many places in recipe steps wait for a safety fact a person has verified."""
    recipes = [thing for thing in things.values() if thing.kind == "recipe"]
    return sum(len(step["safety_points"]) for recipe in recipes for step in recipe.data["steps"])


def count(things):
    return {
        "things": count_things(things),
        "statements": count_statements(things),
        "safety": count_safety(things),
        "probes": probes.shares(probes.run(things)),
        "levels_with_a_technique": count_levels(things),
        "recipe_steps": count_steps(things),
        "safety_points": count_safety_points(things),
    }


def row(cells):
    return "| " + " | ".join(str(cell) for cell in cells) + " |"


def tier_row(name, by_tier, tiers):
    return row([name, sum(by_tier.values())] + [by_tier.get(tier, 0) for tier in tiers])


def tier_table(counts, model, words):
    tiers = words["tiers"]
    lines = [row(["Kind", "All"] + tiers), row(["---"] * (len(tiers) + 2))]
    everything = {}
    for kind in model["kinds"]:
        by_tier = counts["things"].get(kind, {})
        lines.append(tier_row(kind, by_tier, tiers))
        if model["kinds"][kind]["home"] == "graph":
            for tier, number in by_tier.items():
                everything[tier] = everything.get(tier, 0) + number
    lines.append(tier_row("all things of the graph", everything, tiers))
    lines.append(tier_row("statements", counts["statements"], tiers))
    return lines


def safety_table(counts):
    lines = [row(["Safety records", "All"] + list(SAFETY_STATES)), row(["---"] * 4)]
    by_state = counts["safety"]
    cells = ["ingredients", sum(by_state.values())] + [by_state.get(state, 0) for state in SAFETY_STATES]
    lines.append(row(cells))
    return lines


def probe_table(counts):
    lines = [row(["Dish probes", "Answered", "Share"]), row(["---"] * 3)]
    for name in ("growing", "held-back"):
        answered, total = counts["probes"][name]
        percent = "none yet"
        if total > 0:
            percent = "%d%%" % round(100 * answered / total)
        lines.append(row([name, "%d of %d" % (answered, total), percent]))
    return lines


def render(counts, model, words):
    """The numbers as Markdown tables, ready for a round's notes or a pull request."""
    with_a_technique, levels = counts["levels_with_a_technique"]
    lines = tier_table(counts, model, words)
    lines.append("")
    lines.extend(safety_table(counts))
    lines.append("")
    lines.extend(probe_table(counts))
    lines.append("")
    lines.append("Levels of the programs that name a technique: %d of %d" % (with_a_technique, levels))
    lines.append("Recipe steps: %d" % counts["recipe_steps"])
    lines.append("Safety points in recipe steps that wait for a verified fact: %d" % counts["safety_points"])
    return "\n".join(lines)
