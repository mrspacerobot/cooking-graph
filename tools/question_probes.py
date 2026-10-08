"""Probe the real question commands. Missing knowledge never proves a negative."""

from tools import names, probes, queries

KINDS = ("stand-in-probe", "kitchen-probe", "compose-probe")
SETS = ("growing", "held-back")


def result(probe, status, gaps):
    return {"id": probe["id"], "batch": probe["batch"], "status": status, "gaps": gaps}


def recipe_for_original(probe, things, original):
    recipe_id = queries.resolve(things, probe["recipe"], ("recipe",))
    recipe = things[recipe_id].data
    if probe["recipe"] == recipe_id:
        return recipe_id
    if any(line["thing"] == original for line in recipe["ingredients"]):
        return recipe_id
    variants = [thing_id for thing_id, thing in sorted(things.items())
                if thing.kind == "recipe" and thing.data["makes"] == recipe["makes"]
                and any(line["thing"] == original for line in thing.data["ingredients"])]
    if len(variants) == 1:
        return variants[0]
    if len(variants) > 1:
        raise ValueError("the original occurs in several recipe variants; name one explicitly")
    return recipe_id


def answer_stand_in(probe, things):
    try:
        original = queries.resolve(things, probe["ingredient"], queries.FOODS)
        candidate = queries.resolve(things, probe["candidate"], queries.FOODS)
        recipe_id = recipe_for_original(probe, things, original)
        answer = queries.stand_ins(things, recipe_id)
    except ValueError as error:
        return result(probe, "not-answerable", [str(error)])
    lines = [line for line in answer["lines"] if line["original"] == original]
    if not lines:
        return result(probe, "not-answerable", ["the recipe has no line for " + original])
    offered = [[one for one in line["options"] if one["thing"] == candidate] for line in lines]
    forbidden = any(one["thing"] == candidate and one["reason"] == "not-in-this-context"
                    for line in lines for one in line["excluded"])
    if forbidden:
        if probe["verdict"] == "does-not-work":
            return result(probe, "answered", [])
        return result(probe, "disagrees", ["an explicit not_when rejects the candidate"])
    if all(offered):
        if probe["verdict"] == "does-not-work":
            return result(probe, "disagrees", ["the graph offers the candidate"])
        if probe["verdict"] == "works-with-caveat" and not all(one[0]["caveat"] for one in offered):
            return result(probe, "not-answerable", ["a caveat is not recorded for every line"])
        return result(probe, "answered", [])
    return result(probe, "not-answerable", ["no applicable choice or explicit exclusion for every line"])


def answer_kitchen(probe, things):
    try:
        answer = queries.kitchen(things, probe["technique"], probe["at_home"])
    except ValueError as error:
        return result(probe, "not-answerable", [str(error)])
    ready = {row["makes"] for row in answer["recipes"] if row["missing_count"] == 0}
    ready_names = set()
    for whole in ready:
        ready_names.update(names.plain_names(things[whole].data))
    missing = [dish for dish in probe["dishes"] if names.plain(dish) not in ready_names]
    if missing:
        return result(probe, "not-answerable", ["no recipe with all required parts for " + dish for dish in missing])
    return result(probe, "answered", [])


def answer_compose(probe, things):
    """Answered when every expected dish has a recipe that uses every named technique with no required part missing."""
    try:
        answer = queries.compose(things, probe["techniques"], probe["at_home"], top=len(things))
    except ValueError as error:
        return result(probe, "not-answerable", [str(error)])
    ready = {row["makes"] for row in answer["recipes"] if row["missing_count"] == 0 and not row["uncovered"]}
    ready_names = set()
    for whole in ready:
        ready_names.update(names.plain_names(things[whole].data))
    missing = [dish for dish in probe["dishes"] if names.plain(dish) not in ready_names]
    if missing:
        return result(probe, "not-answerable", ["no recipe with every technique and all required parts for " + dish for dish in missing])
    return result(probe, "answered", [])


def run(things, batch=None):
    found = {kind: {set_name: [] for set_name in SETS} for kind in KINDS}
    answerers = {"stand-in-probe": answer_stand_in, "kitchen-probe": answer_kitchen, "compose-probe": answer_compose}
    for thing_id, thing in sorted(things.items()):
        if thing.kind not in KINDS or (batch is not None and thing.data["batch"] != batch):
            continue
        answer = answerers[thing.kind](thing.data, things)
        found[thing.kind][thing.data["set"]].append(answer)
    return found


def counts(found):
    return {kind: {set_name: (sum(one["status"] == "answered" for one in answers), len(answers))
                   for set_name, answers in sets.items()} for kind, sets in found.items()}


def count_lines(found):
    lines = ["| Question probes | Set | Answered |", "|---|---|---|"]
    for kind, sets in counts(found).items():
        for set_name, pair in sets.items():
            lines.append("| %s | %s | %s |" % (kind, set_name, probes.as_share(pair)))
    return lines


def report(found):
    lines = count_lines(found)
    lines += ["", "Only growing gaps are shown. Held-back questions, answers and gaps are never listed."]
    for kind, sets in found.items():
        for answer in sets["growing"]:
            if answer["status"] != "answered":
                lines.append("%s: %s: %s" % (answer["id"], answer["status"], "; ".join(answer["gaps"])))
    return "\n".join(lines)
