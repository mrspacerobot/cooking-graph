"""Match our things to Wikidata items by exact English label, and write only an id and new names.

Wikidata's structured data is CC0, and `source/wikidata` says so. This module
never guesses: a label with two items, an item for two things, a name another
thing holds, or a name in another script is skipped and listed. It only adds.
Nothing is overwritten, and a second run changes nothing.
"""

import copy
from collections import namedtuple

from tools import names, writing
from tools.rules import SAME_AS_KINDS, of_kind

Change = namedtuple("Change", ["thing", "same_as", "names", "aliases"])
Skip = namedtuple("Skip", ["thing", "why", "detail"])
Plan = namedtuple("Plan", ["changes", "skipped", "matched"])


def english_names(data):
    """The one name a match is made on. An alias is often wider or narrower than the thing, so it never decides."""
    return [data["names"]["en"]]


def families(kind):
    return "food" if kind in ("ingredient", "preparation") else kind


def holders(things):
    """Who holds each plain name, by family: an ingredient and a preparation count as one."""
    held = {}
    for thing_id, thing in things.items():
        for name in names.plain_names(thing.data):
            held.setdefault((families(thing.kind), name), set()).add(thing_id)
    return held


def candidates_for(things, entities):
    """The food items each thing's English names point at: {thing id: {item id: item}}."""
    by_label = {}
    for one in entities:
        if one["food"]:
            by_label.setdefault(names.plain(one["label"]), []).append(one)
    found = {}
    for kind in SAME_AS_KINDS:
        for thing_id, thing in of_kind(things, kind):
            for name in english_names(thing.data):
                for one in by_label.get(names.plain(name), []):
                    found.setdefault(thing_id, {})[one["qid"]] = one
    return found


def new_names(thing, item, languages, held, claimed):
    """The names and aliases to add for one thing, and the labels left out and why."""
    added, aliases, skipped = {}, {}, []
    own = names.plain_names(thing.data)
    family = families(thing.kind)
    for language in languages:
        label = item["labels"].get(language)
        if not label or language == "en":
            continue
        plain = names.plain(label)
        if not names.is_latin(label):
            skipped.append(Skip(thing.data["id"], "not-latin", "%s: %s" % (language, label)))
        elif plain in own:
            continue
        elif held.get((family, plain), set()) - {thing.data["id"]} or claimed.get((family, plain), thing.data["id"]) != thing.data["id"]:
            who = sorted(held.get((family, plain), set()) | {claimed.get((family, plain), "")} - {thing.data["id"], ""})
            skipped.append(Skip(thing.data["id"], "name-held", "%s: %s is held by %s" % (language, label, ", ".join(who))))
        elif language not in thing.data["names"]:
            added[language] = label
            claimed[(family, plain)] = thing.data["id"]
        else:
            aliases.setdefault(language, []).append(label)
            claimed[(family, plain)] = thing.data["id"]
    return added, aliases, skipped


def plan(things, entities, source_id, languages):
    """What would change. Raises ValueError when the source may not be used in a product that is sold."""
    source = things.get(source_id)
    if source is None or source.data["commercial_use"] != "allowed":
        raise ValueError("%s is not a source that allows use in a product that is sold" % source_id)
    held = holders(things)
    claimed = {}
    changes, skipped = [], []
    found = candidates_for(things, entities)
    single = {}
    for thing_id, items in sorted(found.items()):
        if len(items) > 1:
            skipped.append(Skip(thing_id, "ambiguous", ", ".join(sorted(items))))
        else:
            single[thing_id] = next(iter(items.values()))
    owners = {}
    for thing_id, item in single.items():
        owners.setdefault((families(things[thing_id].kind), item["qid"]), []).append(thing_id)
    for (family, qid), sharing in sorted(owners.items()):
        if len(sharing) > 1:
            for thing_id in sharing:
                skipped.append(Skip(thing_id, "one-id-for-two-things", "%s is also the id of %s" % (qid, ", ".join(o for o in sharing if o != thing_id))))
                single.pop(thing_id)
    matched = 0
    for thing_id, item in sorted(single.items()):
        thing = things[thing_id]
        rows = [row for row in thing.data["same_as"] if row["source"] == source_id]
        if rows and rows[0]["id"] != item["qid"]:
            skipped.append(Skip(thing_id, "different-id-held", "%s already has %s" % (thing_id, rows[0]["id"])))
            continue
        matched += 1
        added, aliases, left_out = new_names(thing, item, languages, held, claimed)
        skipped.extend(left_out)
        row = None if rows else {"source": source_id, "id": item["qid"], "tier": "sourced"}
        if row or added or aliases:
            changes.append(Change(thing_id, row, added, aliases))
    return Plan(changes, skipped, matched)


def apply(root, things, the_plan, dry_run=False):
    """Write the planned changes. Return how many things change. A dry run writes nothing."""
    if not dry_run:
        for change in the_plan.changes:
            data = copy.deepcopy(things[change.thing].data)
            if change.same_as:
                data["same_as"].append(change.same_as)
            data["names"].update(change.names)
            for language, labels in change.aliases.items():
                data["aliases"].setdefault(language, []).extend(labels)
            writing.write_thing(root, data)
    return len(the_plan.changes)


def report(the_plan, total):
    """Counts first, then every skip, so a person reads each one."""
    lines = ["matched: %d of %d considered" % (the_plan.matched, total),
             "to change: %d things" % len(the_plan.changes),
             "skipped: %d" % len(the_plan.skipped)]
    for skip in sorted(the_plan.skipped):
        lines.append("  %s %s: %s" % (skip.thing, skip.why, skip.detail))
    return lines
