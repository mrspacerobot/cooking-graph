"""Short ways to write the rows a drafter writes most.

Everything written through here is tier drafted and every safety record is
unverified: a drafter is a model, and a model earns no more than that.
"""

import os

from tools import reading, writing

DRAFTED = "drafted"
UNVERIFIED = "unverified"


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


def part(role, *options):
    """One part of a dish or a preparation: a role, and the things a cook may choose for it."""
    return {"role": role, "options": list(options), "tier": DRAFTED}


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

    The drafter names what the ingredient holds. The rest is written out as
    free_of at that moment, so a fact added to the graph later is never read
    as answered by a record that was written before it.
    """
    facts = every_fact(root)
    unknown = [fact for fact in contains if fact not in facts]
    if unknown:
        raise ValueError("no such fact: " + ", ".join(unknown))
    free_of = [fact for fact in facts if fact not in contains]
    return {"state": UNVERIFIED, "contains": list(contains), "free_of": free_of, "note": note}


def put(root, data):
    """Write a drafted thing to its file."""
    return writing.write_thing(root, data)
