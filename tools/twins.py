"""Things that are probably one thing under two names.

The checker refuses the same name twice. It cannot see aubergine and eggplant,
or a plural, or two words in another order. This lists such pairs for a person
to read. It never blocks anything: a pair may be two different things.
"""

from collections import namedtuple

from tools import names
from tools.rules import of_kind

KINDS_COMPARED = ("ingredient", "preparation", "technique", "group", "form", "equipment", "dish", "recipe")
Pair = namedtuple("Pair", ["first", "second", "why"])


def singular(word):
    if len(word) > 3 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("es") and word[-3] in "sxz":
        return word[:-2]
    if len(word) > 2 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def key(name):
    """The words of a name, each in the singular, in a fixed order."""
    return " ".join(sorted(singular(word) for word in names.plain(name).split()))


def family(kind):
    """An ingredient and a preparation are looked up together."""
    return "food" if kind in ("ingredient", "preparation") else kind


def synonym_keys(synonyms):
    return [{key(word) for word in group} for group in synonyms]


def find(things, synonyms=()):
    """Pairs of things of one family whose names agree after plural and word order, or that a synonym list joins."""
    groups = synonym_keys(synonyms)
    keyed = {}
    for kind in KINDS_COMPARED:
        for thing_id, thing in of_kind(things, kind):
            for name in names.all_names(thing.data):
                keyed.setdefault((family(kind), key(name)), set()).add(thing_id)
    found = {}
    for (kind_family, word_key), ids in keyed.items():
        for first in ids:
            for second in ids:
                if first < second and not same_name(things, first, second):
                    found[(first, second)] = "the same words, in the singular and in a fixed order"
    for kind_family in {family(kind) for kind in KINDS_COMPARED}:
        for group in groups:
            holders = sorted(set().union(*[keyed.get((kind_family, word), set()) for word in group]))
            for first in holders:
                for second in holders:
                    if first < second and (first, second) not in found and joined(keyed, kind_family, group, first, second):
                        found[(first, second)] = "a list of synonyms joins them"
    return [Pair(first, second, why) for (first, second), why in sorted(found.items())]


def same_name(things, first, second):
    """Two things with one plain name are the checker's business, not this list's."""
    return bool(names.plain_names(things[first].data) & names.plain_names(things[second].data))


def joined(keyed, kind_family, group, first, second):
    have_first = {word for word in group if first in keyed.get((kind_family, word), set())}
    have_second = {word for word in group if second in keyed.get((kind_family, word), set())}
    return bool(have_first) and bool(have_second) and have_first != have_second


def report(pairs):
    return ["%s and %s: %s" % (pair.first, pair.second, pair.why) for pair in pairs]
