"""Swaps worth drafting: pairs of foods that share a group or a dish part, and have no stand-in row yet.

This only lists. It writes nothing and it says nothing about whether a swap
works: a drafter decides that, in a context, and writes the row.
"""

from collections import namedtuple

from tools.rules import linked, of_kind

FOODS = ("ingredient", "preparation")
Candidate = namedtuple("Candidate", ["first", "second", "reasons"])


def settled_pairs(things):
    """Pairs that already have a stand-in row, whichever way round, whether it allows the swap or not."""
    settled = set()
    for kind in FOODS:
        for thing_id, thing in of_kind(things, kind):
            for row in thing.data["stands_in_for"]:
                settled.add(tuple(sorted((thing_id, row["thing"]))))
    return settled


def add_pair(found, first, second, reason):
    if first == second:
        return
    pair = tuple(sorted((first, second)))
    reasons = found.setdefault(pair, [])
    if reason not in reasons:
        reasons.append(reason)


def by_group(things, found):
    """Foods of one group, counted by the groups they name themselves, not by the wider groups above."""
    holders = {}
    for kind in FOODS:
        for thing_id, thing in of_kind(things, kind):
            for group_id in linked(thing.data["groups"]):
                holders.setdefault(group_id, []).append(thing_id)
    for group_id, members in sorted(holders.items()):
        for first in members:
            for second in members:
                if first < second:
                    add_pair(found, first, second, group_id)


def by_part_options(things, found):
    for kind in ("dish", "preparation"):
        for whole_id, whole in of_kind(things, kind):
            for part in whole.data["parts"]:
                reason = "%s part %s" % (whole_id, part["id"])
                for first in part["options"]:
                    for second in part["options"]:
                        if first < second:
                            add_pair(found, first, second, reason)


def find(things):
    found = {}
    by_group(things, found)
    by_part_options(things, found)
    settled = settled_pairs(things)
    return [Candidate(first, second, tuple(reasons)) for (first, second), reasons in sorted(found.items())
            if (first, second) not in settled]


def summary(pairs):
    """How many open pairs each group and each kind of part option holds."""
    counts = {}
    for pair in pairs:
        for reason in pair.reasons:
            label = reason if reason.startswith("group/") else "dish and preparation parts"
            counts[label] = counts.get(label, 0) + 1
    lines = ["%s: %d open pairs" % (label, count) for label, count in sorted(counts.items())]
    return lines + ["%d open pairs in all" % len(pairs)]


def listing(pairs, group=None, part_options=False):
    """One line per open pair, cut to one group or to the dish and preparation parts."""
    lines = []
    for pair in pairs:
        if group is not None and group not in pair.reasons:
            continue
        if part_options and not any(not reason.startswith("group/") for reason in pair.reasons):
            continue
        lines.append("%s and %s: %s" % (pair.first, pair.second, ", ".join(pair.reasons)))
    return lines
