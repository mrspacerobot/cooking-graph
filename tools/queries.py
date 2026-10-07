"""Deterministic graph questions. Only explicit, direct knowledge is used."""

from tools import group_rules, names, query_safety

SAFETY = "Safety records are unverified. Internal graph exploration only; nothing may be exported or shown to a cook."
FOODS = ("ingredient", "preparation")


def resolve(things, word, kinds):
    if word in things and things[word].kind in kinds:
        return word
    matches = sorted(thing_id for thing_id, thing in things.items()
                     if thing.kind in kinds and names.plain(word) in names.plain_names(thing.data))
    if len(matches) != 1:
        raise ValueError("unknown or ambiguous %s: %s" % ("/".join(kinds), word))
    return matches[0]


def resolve_many(things, words, kinds):
    return sorted({resolve(things, word, kinds) for word in words})


def context(recipe, line):
    found = {recipe["makes"]}
    for step in recipe["steps"]:
        if line["thing"] in step["works_on"] + step["with"]:
            found.add(step["technique"])
    return sorted(found)


def choice(thing_id, basis, row=None):
    detail = {"thing": thing_id, "basis": basis, "allows": True, "when": [], "not_when": [],
              "ratio": None, "caveat": None, "tier": "drafted"}
    if row is not None:
        for field in ("allows", "when", "not_when", "ratio", "caveat", "tier"):
            detail[field] = row[field]
    return detail


def changes_method(things, recipe, line, candidate):
    members = group_rules.members_of_groups(things)
    for step in recipe["steps"]:
        if line["thing"] in step["works_on"]:
            technique = things[step["technique"]]
            if candidate not in group_rules.worked_on(technique, members):
                return True
    return False


def candidate_answer(things, recipe, line, part, candidate, avoided):
    rows = [row for row in things[candidate].data.get("stands_in_for", []) if row["thing"] == line["thing"]]
    contexts = set(context(recipe, line))
    blocked = [row for row in rows if contexts.intersection(row["not_when"])]
    if blocked:
        return None, dict(choice(candidate, "stand-in", blocked[0]), reason="not-in-this-context")
    if not query_safety.free_of(things, candidate, avoided):
        return None, {"thing": candidate, "reason": "avoided-or-unknown-fact"}
    applicable = [row for row in rows if row["allows"] and (not row["when"] or contexts.intersection(row["when"]))]
    if changes_method(things, recipe, line, candidate):
        return None, {"thing": candidate, "reason": "method-not-supported"}
    if applicable:
        return choice(candidate, "stand-in", applicable[0]), None
    if line["thing"] in part["options"] and candidate in part["options"]:
        answer = choice(candidate, "part-option")
        answer["tier"] = part["tier"]
        return answer, None
    return None, {"thing": candidate, "reason": "no-matching-context"}


def line_answer(things, recipe, line, part, avoided):
    candidates = set()
    if line["thing"] in part["options"]:
        candidates.update(part["options"])
    for thing_id, thing in things.items():
        if thing.kind in FOODS and any(row["thing"] == line["thing"] for row in thing.data["stands_in_for"]):
            candidates.add(thing_id)
    answer = {"part": line["part"], "original": line["thing"], "amount": line["amount"],
              "forms": line["forms"], "context": context(recipe, line), "options": [], "excluded": []}
    for candidate in sorted(candidates - {line["thing"]}):
        allowed, excluded = candidate_answer(things, recipe, line, part, candidate, avoided)
        if allowed is not None:
            answer["options"].append(allowed)
        if excluded is not None:
            answer["excluded"].append(excluded)
    return answer


def stand_ins(things, recipe_word, avoid=()):
    recipe_id = resolve(things, recipe_word, ("recipe",))
    avoided = resolve_many(things, avoid, ("fact",))
    recipe = things[recipe_id].data
    parts = {part["id"]: part for part in things[recipe["makes"]].data["parts"]}
    lines = [line_answer(things, recipe, line, parts[line["part"]], avoided) for line in recipe["ingredients"]]
    return {"recipe": recipe_id, "safety": SAFETY, "avoid": avoided, "lines": lines}


def recipes(things, technique_word):
    technique_id = resolve(things, technique_word, ("technique",))
    found = []
    for recipe_id, thing in sorted(things.items()):
        if thing.kind != "recipe" or not any(step["technique"] == technique_id for step in thing.data["steps"]):
            continue
        whole = things[thing.data["makes"]].data
        teaches = any(row["thing"] == technique_id for row in whole["teaches"])
        found.append({"recipe": recipe_id, "makes": whole["id"], "teaches": teaches, "tier": thing.data["tier"]})
    found.sort(key=lambda row: (not row["teaches"], row["recipe"]))
    return {"technique": technique_id, "safety": SAFETY, "recipes": found}


def home_line(things, line, home, avoided):
    if line["original"] in home and query_safety.free_of(things, line["original"], avoided):
        return {"original": line["original"], "status": "at-home", "choice": choice(line["original"], "original")}
    options = [one for one in line["options"] if one["thing"] in home]
    if options:
        return {"original": line["original"], "status": options[0]["basis"], "choice": options[0]}
    return {"original": line["original"], "status": "missing", "choice": None}


def home_recipe(things, row, home, avoided):
    answer = dict(row, parts=[], missing_count=0)
    lines = stand_ins(things, row["recipe"], avoided)["lines"]
    for part in things[row["makes"]].data["parts"]:
        selected = [home_line(things, line, home, avoided) for line in lines if line["part"] == part["id"]]
        status = "omitted"
        if selected:
            status = "filled"
            if any(line["status"] == "missing" for line in selected):
                status = "missing"
        if status == "missing" and not part["optional"]:
            answer["missing_count"] += 1
        answer["parts"].append({"part": part["id"], "optional": part["optional"], "status": status, "lines": selected})
    return answer


def kitchen(things, technique_word, at_home, avoid=()):
    answer = recipes(things, technique_word)
    home = resolve_many(things, at_home, FOODS)
    avoided = resolve_many(things, avoid, ("fact",))
    answer["at_home"] = home
    answer["avoid"] = avoided
    answer["recipes"] = [home_recipe(things, row, home, avoided) for row in answer["recipes"]]
    answer["recipes"].sort(key=lambda row: (row["missing_count"], not row["teaches"], row["recipe"]))
    return answer
