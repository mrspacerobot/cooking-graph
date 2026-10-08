"""Match our things to Wikidata items by exact English label, and write only an id and new names.

Wikidata's structured data is CC0, and `source/wikidata` says so. This module
never guesses: a label with two items, an item for two things, a name another
thing holds, or a name in another script is skipped and listed. It only adds.
Nothing is overwritten, and a second run changes nothing.
"""

import copy
import re
from collections import namedtuple

from tools import names, writing
from tools.rules import SAME_AS_KINDS, of_kind

Change = namedtuple("Change", ["thing", "same_as", "names", "aliases"])
Skip = namedtuple("Skip", ["thing", "why", "detail"])
Plan = namedtuple("Plan", ["changes", "skipped", "matched"])
Proposal = namedtuple("Proposal", ["thing", "qid", "label", "description", "via", "labels"])

FOOD_WORDS = ("edible", "culinary", "spice", "herb", "vegetable", "fruit", "dish", "food", "sauce", "cheese", "fish", "meat", "cut of",
              "bread", "pasta", "dessert", "soup", "salad", "cereal", "grain", "legume", "nut", "seed", "oil", "beverage", "drink", "wine",
              "sausage", "cake", "pastry", "noodle", "rice", "bean", "mushroom", "seaweed", "condiment", "dairy", "egg", "pepper", "sugar",
              "flour", "powder", "paste", "stew", "cooking", "kitchen", "shellfish", "mollus", "crustacean", "tuber", "berry", "citrus")
NOT_FOOD_WORDS = ("disambiguation", "family name", "given name", "film", "painting", "television", "song", "album", "single", "village", "town",
                  "city", "river", "restaurant", "company", "enterprise", "building", "character", "human", "footballer", "singer", "software",
                  "python", "magazine", "novel", "play", "band", "ship", "crater", "municipality", "district", "township", "community",
                  "settlement", "episode", "video game", "organization", "publishing", "station", "hill", "library", "deity", "kingdom",
                  "country", "poet", "wrestler", "tug", "shipwreck", "house", "print", "textile", "business", "motorcycle")


def words_in(text, words):
    return re.search(r"\b(?:%s)" % "|".join(re.escape(word) for word in words), text.lower()) is not None


def sounds_like_food(description):
    """A description from Wikidata that names a food and not a place, a person, a work or a company. A person still reads each one."""
    return bool(description) and words_in(description, FOOD_WORDS) and not words_in(description, NOT_FOOD_WORDS)


def all_english_names(data):
    return [data["names"]["en"]] + data.get("aliases", {}).get("en", [])


def propose(things, entities):
    """Items that might be a thing but were not taken: any class, a description that sounds like a food. For a person to read."""
    by_label = {}
    for one in entities:
        by_label.setdefault(names.plain(one["label"]), []).append(one)
    found = []
    for kind in SAME_AS_KINDS:
        for thing_id, thing in of_kind(things, kind):
            if thing.data["same_as"]:
                continue
            for name in all_english_names(thing.data):
                for one in by_label.get(names.plain(name), []):
                    if sounds_like_food(one.get("description", "")):
                        via = None if name == thing.data["names"]["en"] else name
                        found.append(Proposal(thing_id, one["qid"], one["label"], one["description"], via, one["labels"]))
    return sorted(found, key=lambda one: (one.thing, one.qid))


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


LONGEST_NAME = 40


def is_plain_name(label):
    """No note in brackets, no digit, no full stop, and not a long appellation: those are not what a cook calls a thing."""
    return not any(sign in label for sign in "()[]") and not any(letter.isdigit() for letter in label) \
        and "." not in label and len(label) <= LONGEST_NAME


def is_scientific(label, item, languages):
    """Two words, a capital then lower case, written the same in at least two languages: a species, not what a cook says."""
    words = label.split()
    if len(words) != 2 or not words[0][:1].isupper() or not words[1].islower():
        return False
    same = [language for language in languages if names.plain(item["labels"].get(language, "")) == names.plain(label)]
    return len(same) >= 2


def new_names(thing, item, languages, held, claimed, refused=frozenset()):
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
        elif (thing.data["id"], language, plain) in refused:
            skipped.append(Skip(thing.data["id"], "read-and-refused", "%s: %s" % (language, label)))
        elif is_scientific(label, item, languages):
            skipped.append(Skip(thing.data["id"], "scientific-name", "%s: %s" % (language, label)))
        elif not is_plain_name(label):
            skipped.append(Skip(thing.data["id"], "not-a-plain-name", "%s: %s" % (language, label)))
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


def plan(things, entities, source_id, languages, refused=(), chosen=()):
    """What would change. Raises ValueError when the source may not be used in a product that is sold.

    `refused` lists names a person read and found wrong for the thing, as rows of thing, language and label.
    They are never written, so a later run does not bring them back.

    `chosen` lists items a person read and chose for a thing, as rows of thing, id and why. They are taken
    whatever their class, and they settle an ambiguous label.
    """
    chosen = {row["thing"]: row["id"] for row in chosen}
    refused = {(row["thing"], row["language"], names.plain(row["label"])) for row in refused}
    source = things.get(source_id)
    if source is None or source.data["commercial_use"] != "allowed":
        raise ValueError("%s is not a source that allows use in a product that is sold" % source_id)
    held = holders(things)
    claimed = {}
    changes, skipped = [], []
    found = candidates_for(things, entities)
    single = {}
    for thing_id, items in sorted(found.items()):
        if thing_id in chosen:
            continue
        if len(items) > 1:
            skipped.append(Skip(thing_id, "ambiguous", ", ".join(sorted(items))))
        else:
            single[thing_id] = next(iter(items.values()))
    for thing_id, qid in sorted(chosen.items()):
        item = next((one for one in entities if one["qid"] == qid), None)
        if thing_id not in things or item is None:
            skipped.append(Skip(thing_id, "chosen-not-fetched", qid))
        else:
            single[thing_id] = item
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
        added, aliases, left_out = new_names(thing, item, languages, held, claimed, refused)
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


def proposal_lines(proposals):
    """One line per proposal, for a person to read and choose from."""
    lines = []
    for one in proposals:
        via = "" if one.via is None else " (through the alias '%s')" % one.via
        names_in = ", ".join("%s:%s" % pair for pair in sorted(one.labels.items()))
        lines.append("%s %s '%s'%s: %s [%s]" % (one.thing, one.qid, one.label, via, one.description, names_in))
    return lines


def report(the_plan, total):
    """Counts first, then every skip, so a person reads each one."""
    lines = ["matched: %d of %d considered" % (the_plan.matched, total),
             "to change: %d things" % len(the_plan.changes),
             "skipped: %d" % len(the_plan.skipped)]
    for skip in sorted(the_plan.skipped):
        lines.append("  %s %s: %s" % (skip.thing, skip.why, skip.detail))
    return lines
