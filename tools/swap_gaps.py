"""Where a swap is plausible and the graph offers none: a work list for drafting. It writes nothing.

A swap is plausible when a technique card names it for the ingredient (the card lists what the move can use, which is
a hint and not a licence), or when a stand-in row exists but its context never matches the recipe. A pair a row has
excluded on purpose is settled, and is not a gap.
"""

from tools import queries

FOODS = ("ingredient", "preparation")
# Excluded on purpose: the graph has already answered "no" for this pair here.
SETTLED = ("not-in-this-context", "method-not-supported")


def is_food(thing_id):
    return thing_id.split("/")[0] in FOODS


def steps_handling(recipe, line):
    return [step for step in recipe["steps"] if line["thing"] in step["works_on"] + step["with"]]


def named_by_cards(things, recipe, line):
    """Foods the technique cards of the steps that handle this line list beside it for the same role."""
    found = set()
    for step in steps_handling(recipe, line):
        for need in things[step["technique"]].data["needs"]:
            if line["thing"] in need["options"]:
                found.update(one for one in need["options"] if is_food(one))
    return found - {line["thing"]}


def line_gaps(things, recipe, answer):
    """The candidates that are plausible for one line and not offered, each with why it is listed."""
    offered = {one["thing"] for one in answer["options"]}
    settled = {one["thing"] for one in answer["excluded"] if one["reason"] in SETTLED}
    row_context = {one["thing"] for one in answer["excluded"] if one["reason"] == "no-matching-context"}
    named = named_by_cards(things, recipe, {"thing": answer["original"]})
    gaps = {}
    for candidate in (named | row_context) - offered - settled:
        gaps[candidate] = [why for why, found in (("card", named), ("row-context", row_context)) if candidate in found]
    return offered, gaps


def analyse(things):
    totals = {"lines": 0, "with_swap": 0, "with_gap": 0, "with_broader": 0}
    pairs = {}
    for recipe_id, thing in sorted(things.items()):
        if thing.kind != "recipe":
            continue
        recipe = thing.data
        answers = queries.stand_ins(things, recipe_id)["lines"]
        for line, answer in zip(recipe["ingredients"], answers):
            offered, gaps = line_gaps(things, recipe, answer)
            totals["lines"] += 1
            totals["with_swap"] += bool(offered)
            card = any("card" in why for why in gaps.values())
            totals["with_gap"] += card
            totals["with_broader"] += bool(gaps) and not card
            techniques = {step["technique"] for step in steps_handling(recipe, line)}
            for candidate, why in gaps.items():
                row = pairs.setdefault((line["thing"], candidate), {"recipes": set(), "techniques": set(), "why": set()})
                row["recipes"].add(recipe_id)
                row["techniques"].update(techniques)
                row["why"].update(why)
    rows = [{"original": original, "candidate": candidate, "count": len(row["recipes"]),
             "recipes": sorted(row["recipes"]), "techniques": sorted(row["techniques"]), "why": sorted(row["why"])}
            for (original, candidate), row in pairs.items()]
    rows.sort(key=lambda row: ("card" not in row["why"], -row["count"], row["original"], row["candidate"]))
    return dict(totals, gaps=rows)


def new_foods(things):
    """Foods that appear in no stand-in row, neither as the one that stands in nor as the one stood in for."""
    named = set()
    for thing_id, thing in things.items():
        for row in thing.data.get("stands_in_for", []):
            named.update((thing_id, row["thing"]))
    return sorted(thing_id for thing_id, thing in things.items() if thing.kind in FOODS and thing_id not in named)


def counts(things):
    found = analyse(things)
    return {"lines": found["lines"], "with_swap": found["with_swap"], "with_gap": found["with_gap"],
            "gap_pairs": sum("card" in row["why"] for row in found["gaps"]), "new_foods": len(new_foods(things))}


def summary(found, foods):
    return ["%d recipe lines" % found["lines"],
            "%d with a swap offered" % found["with_swap"],
            "%d with a swap a technique card names and the graph does not offer, in %d pairs" % (
                found["with_gap"], sum("card" in row["why"] for row in found["gaps"])),
            "%d more where a swap row exists but its context never matches (could be broadened)" % found["with_broader"],
            "%d foods in no stand-in row" % len(foods)]


def shown(techniques, limit=3):
    if not techniques:
        return "no technique"
    if len(techniques) <= limit:
        return ", ".join(techniques)
    return "%s and %d more" % (", ".join(techniques[:limit]), len(techniques) - limit)


def listing(found, top):
    return ["%d recipes: %s for %s (%s) in %s" % (row["count"], row["candidate"], row["original"], ", ".join(row["why"]),
                                               shown(row["techniques"]))
            for row in found["gaps"][:top]]
