"""The closed list a photo step chooses from: the foods and techniques of the graph, by id. Never a probe."""

from tools import names
from tools.rules import linked

FOODS = ("ingredient", "preparation")
NOTE = ("A closed list for matching what a photo or a voice shows to ids. A label that matches nothing here is none: "
        "never invent an id. The cook confirms every id.")


def row(thing_id, thing):
    english = thing.data["names"]["en"]
    others = [alias for aliases in thing.data["aliases"].values() for alias in aliases]
    found = {"id": thing_id, "name": english, "aliases": others}
    if "groups" in thing.data:
        found["groups"] = linked(thing.data["groups"])
    return found


def closed_list(things):
    foods = [row(thing_id, thing) for thing_id, thing in sorted(things.items()) if thing.kind in FOODS]
    techniques = [row(thing_id, thing) for thing_id, thing in sorted(things.items()) if thing.kind == "technique"]
    for found in techniques:
        found.pop("groups", None)
    return {"note": NOTE, "foods": foods, "techniques": techniques}


def as_names(listed):
    """One line per id and its English name, for a prompt that must stay short."""
    return ["%s\t%s" % (found["id"], found["name"]) for section in ("foods", "techniques") for found in listed[section]]
