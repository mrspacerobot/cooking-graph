"""The numbers: what the graph holds, how far it can be trusted, and how many probes it answers."""

from tools import probes, question_probes, safety_probes
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


def count_facts_held(things):
    """How many facts ingredients are said to hold: those that are certain, and those recorded strictly for want of knowing."""
    counts = {"certain": 0, "strict": 0}
    for thing in things.values():
        if thing.kind == "ingredient":
            for row in thing.data["safety"]["contains"]:
                counts["certain" if row["certain"] else "strict"] += 1
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


def count_parts(things, kinds=("dish", "preparation")):
    parts = [part for thing in things.values() if thing.kind in kinds for part in thing.data["parts"]]
    return (sum(len(part["options"]) > 1 for part in parts), len(parts))


def count_stand_ins(things):
    rows = [row for thing in things.values() for row in thing.data.get("stands_in_for", [])]
    positive = sum(row["allows"] for row in rows)
    return {"positive": positive, "exclusion_only": len(rows) - positive}


def count(things):
    return {
        "things": count_things(things),
        "statements": count_statements(things),
        "safety": count_safety(things),
        "facts_held": count_facts_held(things),
        "probes": probes.shares(probes.run(things)),
        "probe_words": probes.word_shares(probes.run(things)),
        "batches": probes.by_batch(probes.run(things)),
        "batch_lines": probes.batch_lines(probes.run(things)),
        "levels_with_a_technique": count_levels(things),
        "recipe_steps": count_steps(things),
        "safety_points": count_safety_points(things),
        "parts_with_options": count_parts(things),
        "question_probes": question_probes.counts(question_probes.run(things)),
        "parts_by_kind": {kind: count_parts(things, (kind,)) for kind in ("dish", "preparation")},
        "stand_in_statements": count_stand_ins(things),
        "safety_probes": safety_probes.counts(safety_probes.run(things)),
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
    lines.append("")
    lines.append("Facts ingredients hold: %d certain, %d recorded strictly for want of knowing" % (counts["facts_held"]["certain"], counts["facts_held"]["strict"]))
    return lines


def probe_table(counts):
    """The probes answered, and the words answered. A probe fails on a single word, so both are shown."""
    lines = [row(["Dish probes", "Answered", "Share", "Technique words", "Ingredient words"]), row(["---"] * 5)]
    for name in ("growing", "held-back"):
        answered, total = counts["probes"][name]
        percent = "none yet"
        if total > 0:
            percent = "%d%%" % round(100 * answered / total)
        words = counts["probe_words"][name]
        cells = [name, "%d of %d" % (answered, total), percent, "%d of %d" % words["techniques"], "%d of %d" % words["ingredients"]]
        lines.append(row(cells))
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
    lines.extend(counts["batch_lines"])
    lines.append("")
    lines.append("Levels of the programs that name a technique: %d of %d" % (with_a_technique, levels))
    lines.append("Recipe steps: %d" % counts["recipe_steps"])
    lines.append("Safety points in recipe steps that wait for a verified fact: %d" % counts["safety_points"])
    lines.append("Parts with more than one option: %s" % probes.as_share(counts["parts_with_options"]))
    for kind, pair in counts["parts_by_kind"].items():
        lines.append("%s parts with more than one option: %s" % (kind.capitalize(), probes.as_share(pair)))
    stand_ins = counts["stand_in_statements"]
    lines.append("Stand-in statements: %d positive, %d exclusion-only" % (stand_ins["positive"], stand_ins["exclusion_only"]))
    lines.append("")
    lines.extend(["| Question probes | Set | Answered |", "|---|---|---|"])
    for kind, sets in counts["question_probes"].items():
        for set_name, pair in sets.items():
            lines.append("| %s | %s | %s |" % (kind, set_name, probes.as_share(pair)))
    lines.extend(["", "| Safety probes | Agreeing | Answerable | Disagreeing |", "|---|---|---|---|"])
    for set_name, values in counts["safety_probes"].items():
        share = probes.as_share((values["agreeing"], values["probes"]))
        lines.append("| %s | %s | %d | %d |" % (set_name, share, values["answerable"], values["disagreeing"]))
    return "\n".join(lines)
