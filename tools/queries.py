"""Deterministic graph questions. Only explicit, direct knowledge is used."""

from tools import group_rules, names, query_safety

SAFETY = "Safety records are unverified. Internal graph exploration only; nothing may be exported or shown to a cook."
FOODS = ("ingredient", "preparation")


def singular_forms(word):
    """What a plural may be the plural of, for a word of four letters or more. A guess, so resolve wants it unique."""
    plain = names.plain(word)
    forms = []
    for ending, instead in (("ies", "y"), ("oes", "o"), ("es", ""), ("s", "")):
        if plain.endswith(ending) and len(plain) - len(ending) >= 3:
            forms.append(plain[:-len(ending)] + instead)
    return forms


def named(things, plain_word, kinds):
    return sorted(thing_id for thing_id, thing in things.items()
                  if thing.kind in kinds and plain_word in names.plain_names(thing.data))


def resolve(things, word, kinds):
    """An id, else an exact name, else the one thing a plural reads as. Ambiguity is an error, never a pick."""
    if word in things and things[word].kind in kinds:
        return word
    matches = named(things, names.plain(word), kinds)
    if not matches:
        matches = sorted({found for form in singular_forms(word) for found in named(things, form, kinds)})
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
            found.update(thing_id for thing_id in step["works_on"] + step["with"] + step["makes"]
                         if thing_id.startswith("preparation/"))
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


def family(things, technique_id):
    """The technique and every technique that is a variant of it, at any depth. A kind of boil is a boil, not the reverse."""
    children = {}
    for thing_id, thing in things.items():
        if thing.kind == "technique":
            for row in thing.data["variant_of"]:
                children.setdefault(row["thing"], []).append(thing_id)
    found, waiting = {technique_id}, [technique_id]
    while waiting:
        for child in children.get(waiting.pop(), []):
            if child not in found:
                found.add(child)
                waiting.append(child)
    return found


def recipes(things, technique_word):
    technique_id = resolve(things, technique_word, ("technique",))
    kin = family(things, technique_id)
    found = []
    for recipe_id, thing in sorted(things.items()):
        if thing.kind != "recipe":
            continue
        used = {step["technique"] for step in thing.data["steps"]}
        if not used & kin:
            continue
        whole = things[thing.data["makes"]].data
        teaches = any(row["thing"] in kin for row in whole["teaches"])
        found.append({"recipe": recipe_id, "makes": whole["id"], "teaches": teaches, "tier": thing.data["tier"],
                      "exact": technique_id in used, "variants_used": sorted(used & kin - {technique_id})})
    found.sort(key=lambda row: (not row["exact"], not row["teaches"], row["recipe"]))
    return {"technique": technique_id, "safety": SAFETY, "recipes": found}


def home_line(things, line, home, avoided):
    """What the cook can do about one recipe line: use the original, use an allowed alternative they have, buy one,
    or nothing at all. `refused` is that last case: the original is not safe for what is avoided and no alternative
    is allowed, so buying anything cannot help. It is never `missing`, which means "go and buy it"."""
    original_is_safe = query_safety.free_of(things, line["original"], avoided)
    if line["original"] in home and original_is_safe:
        return {"original": line["original"], "status": "at-home", "choice": choice(line["original"], "original")}
    options = [one for one in line["options"] if one["thing"] in home]
    if options:
        return {"original": line["original"], "status": options[0]["basis"], "choice": options[0]}
    if not original_is_safe and not line["options"]:
        return {"original": line["original"], "status": "refused", "choice": None}
    return {"original": line["original"], "status": "missing", "choice": None}


def part_status(selected):
    """`refused` beats `missing`: a part that cannot be made safely is not one that is merely not at home."""
    if not selected:
        return "omitted"
    statuses = {line["status"] for line in selected}
    if "refused" in statuses:
        return "refused"
    return "missing" if "missing" in statuses else "filled"


def home_recipe(things, row, home, avoided):
    answer = dict(row, parts=[], missing_count=0, status="ok")
    lines = stand_ins(things, row["recipe"], avoided)["lines"]
    for part in things[row["makes"]].data["parts"]:
        selected = [home_line(things, line, home, avoided) for line in lines if line["part"] == part["id"]]
        status = part_status(selected)
        if status == "refused" and part["optional"]:
            status = "omitted"
        if status == "refused":
            answer["status"] = "refused"
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
    answer["recipes"].sort(key=lambda row: (row["status"] == "refused", row["missing_count"], not row["exact"],
                                            not row["teaches"], row["recipe"]))
    return answer


# A ratio is by weight, volume or count. A unit outside this table (a pinch) has no measure, so no ratio applies.
MEASURE_OF_UNIT = {"gram": "weight", "kilogram": "weight", "millilitre": "volume", "litre": "volume",
                   "teaspoon": "volume", "tablespoon": "volume", "piece": "count", "clove": "count",
                   "sprig": "count", "leaf": "count", "slice": "count"}


def number(value):
    value = round(value, 2)
    return int(value) if value == int(value) else value


def amount_of(amount, factor):
    return {"value": number(amount["value"] * factor), "unit": amount["unit"]}


def scaling(recipe, servings):
    """The factor to multiply every amount by, the servings asked for, and a note when they cannot be applied."""
    if servings is None:
        return 1, None, None
    if servings <= 0:
        raise ValueError("servings must be more than zero")
    yields = recipe["yields"]
    if yields["unit"] != "serving":
        return 1, None, "The recipe yields in %s, not servings; amounts are as written." % yields["unit"]
    return servings / yields["value"], {"from": number(yields["value"]), "to": number(servings)}, None


def line_amount(amount, status, choice, factor):
    needed = amount_of(amount, factor)
    answer = {"original": needed, "for_home": None, "note": None}
    if status == "at-home":
        answer["for_home"] = needed
    elif status not in ("missing", "refused"):
        ratio = choice["ratio"]
        if ratio is None:
            answer["note"] = "No ratio is recorded for this swap, so the amount is not converted."
        elif MEASURE_OF_UNIT.get(amount["unit"]) != ratio["by"]:
            answer["note"] = "The recorded ratio is by %s and does not fit this amount, so it is not converted." % ratio["by"]
        else:
            answer["for_home"] = amount_of(amount, factor * ratio["stand_in"] / ratio["original"])
    return answer


def steps_as_read(recipe, parts):
    """Each step as written, and which ingredient to read in place of which, from the parts already answered."""
    replaced = {line["original"]: line["choice"]["thing"] for part in parts for line in part["lines"]
                if line["status"] not in ("at-home", "missing", "refused")}
    return [{"technique": step["technique"], "text": step["text"], "time": step["time"],
             "temperature": step["temperature"], "safety_points": step["safety_points"],
             "read_as": [{"original": thing_id, "instead": replaced[thing_id]}
                         for thing_id in step["works_on"] + step["with"] if thing_id in replaced]}
            for step in recipe["steps"]]


def compose_recipe(things, row, home, avoided, factor):
    answer = home_recipe(things, row, home, avoided)
    recipe = things[row["recipe"]].data
    amounts = {(line["part"], line["thing"]): line["amount"] for line in recipe["ingredients"]}
    answer["missing"] = []
    for part in answer["parts"]:
        for line in part["lines"]:
            line["amount"] = line_amount(amounts[(part["part"], line["original"])], line["status"], line["choice"], factor)
            if line["status"] == "missing" and not part["optional"]:
                answer["missing"].append({"part": part["part"], "original": line["original"]})
    answer["steps"] = steps_as_read(recipe, answer["parts"])
    return answer


def own_techniques(recipe):
    return {step["technique"] for step in recipe["steps"]}


def preparation_techniques(things, recipe_id, made_by, seen):
    """Techniques of the recipes that make the preparations this recipe names, at any depth. A loop ends."""
    found = set()
    for line in things[recipe_id].data["ingredients"]:
        for made in made_by.get(line["thing"], []):
            if made not in seen:
                seen.add(made)
                found |= own_techniques(things[made].data)
                found |= preparation_techniques(things, made, made_by, seen)
    return found


def compose(things, technique_words, at_home, avoid=(), servings=None, top=5):
    """Recipes that practise the techniques, adapted to what is at home: the stand-ins, amounts and steps as read.

    A technique counts when a step uses it, when a step uses a variant of it, or when the recipe of a preparation
    the dish names does. Exact use ranks first.
    """
    if not technique_words:
        raise ValueError("name at least one technique")
    if top < 1:
        raise ValueError("top must be at least one")
    techniques = resolve_many(things, technique_words, ("technique",))
    home = resolve_many(things, at_home, FOODS)
    avoided = resolve_many(things, avoid, ("fact",))
    kin = {one: family(things, one) for one in techniques}
    made_by = {}
    for recipe_id, thing in things.items():
        if thing.kind == "recipe":
            made_by.setdefault(thing.data["makes"], []).append(recipe_id)
    answers, refused = [], []
    for recipe_id, thing in sorted(things.items()):
        if thing.kind != "recipe":
            continue
        own = own_techniques(thing.data)
        through = preparation_techniques(things, recipe_id, made_by, {recipe_id}) - own
        covered = [one for one in techniques if kin[one] & (own | through)]
        if not covered:
            continue
        whole = things[thing.data["makes"]].data
        by_variant = {one: sorted(kin[one] & own - {one}) for one in covered if one not in own and kin[one] & own}
        by_preparation = {one: sorted(kin[one] & through) for one in covered if not kin[one] & own}
        row = {"recipe": recipe_id, "makes": whole["id"], "tier": thing.data["tier"],
               "teaches": any(one["thing"] in kin[t] for one in whole.get("teaches", []) for t in techniques),
               "covered": covered, "uncovered": [one for one in techniques if one not in covered],
               "covered_by_variant": by_variant, "covered_by_preparation": by_preparation,
               "exact_count": sum(one in own for one in techniques)}
        factor, asked, note = scaling(thing.data, servings)
        answer = compose_recipe(things, row, home, avoided, factor)
        if answer["status"] == "refused":
            refused.append(recipe_id)
            continue
        answers.append(dict(answer, servings=asked, scaling_note=note))
    answers.sort(key=lambda row: (len(row["uncovered"]), row["missing_count"], len(row["covered_by_preparation"]),
                                  -row["exact_count"], not row["teaches"], row["recipe"]))
    return {"techniques": techniques, "at_home": home, "avoid": avoided, "safety": SAFETY, "recipes": answers[:top],
            "refused": refused}


def required_lines(things, recipe):
    """The lines of the parts a dish cannot leave out, and the lines of the optional parts by part."""
    optional = {part["id"] for part in things[recipe["makes"]].data["parts"] if part["optional"]}
    required = [line for line in recipe["ingredients"] if line["part"] not in optional]
    left_out = {}
    for line in recipe["ingredients"]:
        if line["part"] in optional:
            left_out.setdefault(line["part"], []).append(line)
    return required, left_out


def can_make(things, recipe_word, avoid=()):
    """Can the recipe be made for a cook who avoids these facts, with the swaps the graph allows?

    A line is fine when its food is free of what is avoided, or when one of its allowed swaps is. `ok` when every
    required line is fine, with the swaps used; otherwise `refused`, with the foods that have no way. Optional parts
    that have no way are named in `leave_out`.
    """
    recipe_id = resolve(things, recipe_word, ("recipe",))
    avoided = resolve_many(things, avoid, ("fact",))
    optional = {part["id"] for part in things[things[recipe_id].data["makes"]].data["parts"] if part["optional"]}
    blocking, leave_out, swaps = set(), set(), []
    for line in stand_ins(things, recipe_id, avoided)["lines"]:
        if query_safety.free_of(things, line["original"], avoided):
            continue
        if line["options"]:
            swaps.append({"original": line["original"], "instead": line["options"][0]["thing"]})
        elif line["part"] in optional:
            leave_out.add(line["part"])
        else:
            blocking.add(line["original"])
    status = "refused" if blocking else "ok"
    if blocking:
        swaps = []
    return {"recipe": recipe_id, "avoid": avoided, "status": status, "because": sorted(blocking),
            "leave_out": sorted(leave_out), "swaps": swaps}
