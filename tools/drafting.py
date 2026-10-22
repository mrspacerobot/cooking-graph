"""Short ways to write the rows a drafter writes most.

Everything written through here is tier drafted and every safety record is
unverified: a drafter is a model, and a model earns no more than that.
"""

import os

from tools import reading, writing

DRAFTED = "drafted"
UNVERIFIED = "unverified"


# A drafter may write i/butter for ingredient/butter. Every helper below writes the id out in full.
SHORT_KINDS = {
    "i": "ingredient",
    "p": "preparation",
    "t": "technique",
    "e": "equipment",
    "f": "form",
    "c": "cuisine",
    "d": "dish",
    "r": "recipe",
    "x": "fact",
    "g": "group",
}


def full(thing_id):
    """The id written out: i/butter is ingredient/butter."""
    kind, slug = thing_id.split("/")
    return SHORT_KINDS.get(kind, kind) + "/" + slug


def all_full(thing_ids):
    return [full(thing_id) for thing_id in thing_ids]


def thing(thing_id, english, fr=None, also=None):
    """The head every thing starts with: its id, its tier, its names and its aliases."""
    names = {"en": english}
    if fr is not None:
        names["fr"] = fr
    return {"id": thing_id, "tier": DRAFTED, "names": names, "aliases": also or {}}


def link(thing_id, **more):
    """A statement that points at a thing, with whatever the model adds to it."""
    row = {"thing": thing_id}
    row.update(more)
    row["tier"] = DRAFTED
    return row


def links(*thing_ids):
    return [link(thing_id) for thing_id in thing_ids]


def part(part_id, role, *options, optional=False):
    """One part of a dish or a preparation: its id, its role, and the things a cook may choose for it."""
    return {"id": part_id, "role": role, "options": all_full(options), "optional": optional, "tier": DRAFTED}


def amount(value, unit):
    return {"value": value, "unit": unit}


def span(low, high, unit):
    return {"from": low, "to": high, "unit": unit}


def every_fact(root):
    """The id of every safety fact the graph holds."""
    folder = os.path.join(root, "graph", "fact")
    return sorted("fact/" + name[: -len(".json")] for name in os.listdir(folder) if name.endswith(".json"))


def safety(root, contains, note=None):
    """An unverified safety record that answers every fact: these it holds, all others it is free of.

    `contains` is a list of (fact, basis, certain): the fact, on what basis in
    a few plain words, and whether that is certain or recorded strictly for
    want of knowing. The rest is written out as free_of at that moment, so a
    fact added to the graph later is never read as answered by an older record.
    """
    facts = every_fact(root)
    rows = [{"fact": full(fact), "basis": basis, "certain": certain} for fact, basis, certain in contains]
    unknown = [row["fact"] for row in rows if row["fact"] not in facts]
    if unknown:
        raise ValueError("no such fact: " + ", ".join(unknown))
    holds = [row["fact"] for row in rows]
    free_of = [fact for fact in facts if fact not in holds]
    return {"state": UNVERIFIED, "contains": rows, "free_of": free_of, "note": note}


def put(root, data):
    """Write a drafted thing to its file."""
    return writing.write_thing(root, data)


def full_links(thing_ids):
    return links(*all_full(thing_ids))


def equipment(slug, english, use, fr=None, also=None):
    tool = thing("equipment/" + slug, english, fr=fr, also=also)
    tool["use"] = use
    return tool


def form(slug, english, looks_like, fr=None, also=None, size=()):
    """A form. `size` is a list of (measure, length) pairs, for a cut that is defined by its size."""
    state = thing("form/" + slug, english, fr=fr, also=also)
    state["looks_like"] = looks_like
    state["size"] = [{"measure": measure, "length": length} for measure, length in size]
    return state


def stand_in(original, caveat, when=(), not_when=(), ratio=None, allows=True):
    """A stands-in-for row. `ratio` is (stand_in, original, measured by), or None when it is not known."""
    row = {"allows": allows, "when": all_full(when), "not_when": all_full(not_when), "ratio": None, "caveat": caveat}
    if ratio is not None:
        row["ratio"] = {"stand_in": ratio[0], "original": ratio[1], "by": ratio[2]}
    return link(full(original), **row)


def group(slug, english, shares, fr=None, also=None, within=None, stands_alone=None):
    """A group of ingredients that behave alike in cooking, and the wider group it sits within."""
    kind = thing("group/" + slug, english, fr=fr, also=also)
    kind["shares"] = shares
    kind["within"] = link(full(within)) if within else None
    kind["stands_alone"] = stands_alone
    return kind


def counting(food, plurals):
    """The plural of a food's name in each language it is named in, or none when it is uncountable (butter, salt, rice).

    A countable food needs one plural per name. `./check` rejects a food that is neither. The plural stands where a
    step writes `{part:plural}`."""
    food["plurals"] = dict(plurals or {})
    food["uncountable"] = not plurals
    return food


def ingredient(root, slug, english, behaviour, fr=None, also=None, contains=(), note=None,
               is_a=(), part_of=(), groups=(), forms=(), stands=(), pantry=(), plurals=None):
    food = counting(thing("ingredient/" + slug, english, fr=fr, also=also), plurals)
    food["is_a"] = full_links(is_a)
    food["part_of"] = full_links(part_of)
    food["groups"] = full_links(groups)
    food["forms"] = full_links(forms)
    food["behaviour"] = behaviour
    food["safety"] = safety(root, contains, note=note)
    food["stands_in_for"] = list(stands)
    food["in_pantry_of"] = full_links(pantry)
    food["same_as"] = []
    return food


def technique(slug, english, does, how, cues, mistakes, fr=None, also=None, works_on=(), makes=(),
              needs=(), comes_after=(), variant_of=(), belongs_to=()):
    """A technique card. Cues are (sense, text), mistakes (mistake, fix), needs (role, options),
    comes_after (technique, why) and variant_of (technique, what differs)."""
    move = thing("technique/" + slug, english, fr=fr, also=also)
    move["does"] = does
    move["intro"] = None
    move["how"] = list(how)
    move["cues"] = [{"sense": sense, "text": text} for sense, text in cues]
    move["mistakes"] = [{"mistake": mistake, "fix": fix} for mistake, fix in mistakes]
    move["quiz"] = []
    move["works_on"] = full_links(works_on)
    move["makes"] = full_links(makes)
    move["needs"] = [{"role": role, "options": all_full(options), "tier": DRAFTED} for role, options in needs]
    move["comes_after"] = [link(full(earlier), why=why) for earlier, why in comes_after]
    move["variant_of"] = [link(full(other), differs=differs) for other, differs in variant_of]
    move["belongs_to"] = full_links(belongs_to)
    return move


def preparation(slug, english, what_it_is, parts, fr=None, also=None, groups=(), teaches=(), stands=(), belongs_to=(),
                plurals=None):
    block = counting(thing("preparation/" + slug, english, fr=fr, also=also), plurals)
    block["is"] = what_it_is
    block["parts"] = list(parts)
    block["groups"] = full_links(groups)
    block["teaches"] = full_links(teaches)
    block["stands_in_for"] = list(stands)
    block["belongs_to"] = full_links(belongs_to)
    block["same_as"] = []
    return block


def dish(slug, english, what_it_is, parts, fr=None, also=None, teaches=(), belongs_to=()):
    plate = thing("dish/" + slug, english, fr=fr, also=also)
    plate["is"] = what_it_is
    plate["parts"] = list(parts)
    plate["teaches"] = full_links(teaches)
    plate["belongs_to"] = full_links(belongs_to)
    plate["same_as"] = []
    return plate


def line(thing_id, value, unit, *forms, part=None):
    """One ingredient line of a recipe: the thing, how much, the forms it is in, and the part of the dish it fills.

    The part is the slug of the thing unless another is named.
    """
    filled = part or full(thing_id).split("/")[1]
    return {"thing": full(thing_id), "amount": amount(value, unit), "forms": all_full(forms), "part": filled}


def step(technique_id, works_on, text, using=(), time=None, temperature=None, safety=(), makes=()):
    """One step of a recipe: what the technique works on, what it is done with, and what it leaves behind.

    The text names the foods of the recipe's lines only through placeholders, `{part}` (or `{part.ingredient}` when the
    part holds several foods), and puts text that belongs to an optional part in a clause, `[part: ... {part} ...]`.
    The part of a line is the slug of its food unless `line(..., part=...)` names another. `./check` rejects a plain
    mention of such a food. See docs/recipe-steps.md.
    """
    return {
        "technique": full(technique_id),
        "works_on": all_full(works_on),
        "with": all_full(using),
        "text": text,
        "time": time,
        "temperature": temperature,
        "safety_points": list(safety),
        "makes": all_full(makes),
    }


def recipe(slug, english, makes, yields, ingredients, equipment, steps, fr=None, also=None):
    way = thing("recipe/" + slug, english, fr=fr, also=also)
    way["makes"] = full(makes)
    way["yields"] = yields
    way["ingredients"] = list(ingredients)
    way["equipment"] = all_full(equipment)
    way["steps"] = list(steps)
    return way


def intro(what, why, idea=None):
    """Explain a technique and its wider cooking purpose, as a draft."""
    return {"what": what, "why": why, "idea": idea, "tier": DRAFTED}


def question(identifier, prompt, choices, answer, because):
    """One reusable question with a permanent local id and a zero-based answer."""
    return {"id": identifier, "question": prompt, "choices": list(choices),
            "answer": answer, "because": because, "tier": DRAFTED}
