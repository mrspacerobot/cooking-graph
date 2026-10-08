"""Keep only the stand-in rows that two drafters, working apart, both wrote.

A model that drafts a swap alone shares its own blind spots. Two drafters who have not seen
each other agree more often when the swap is real. What both write is kept, with the
stricter reading: the contexts they share, the exclusions of both, and a ratio only when
the two ratios are close. What only one writes, or what they write against each other,
is listed for the owner and never applied.
"""

from collections import namedtuple

CLOSE = 0.25  # two ratios are close when they differ by less than this share of the larger

Result = namedtuple("Result", ["agreed", "disputed", "single"])
Dispute = namedtuple("Dispute", ["file", "thing", "why", "first", "second"])


def key(change):
    return (change["file"], change["add"]["thing"])


def by_key(changes):
    return {key(change): change for change in changes}


def per_original(ratio):
    return ratio["stand_in"] / ratio["original"]


def merged_ratio(first, second):
    """The mean of two ratios of one measure that are close, else none."""
    if first is None or second is None or first["by"] != second["by"]:
        return None
    one, two = per_original(first), per_original(second)
    if abs(one - two) / max(one, two) >= CLOSE:
        return None
    return {"stand_in": round((one + two) / 2, 2), "original": 1, "by": first["by"]}


def merged_row(first, second):
    """The kept row, or a reason it cannot be kept."""
    a, b = first["add"], second["add"]
    if a["allows"] != b["allows"]:
        return None, "verdicts-differ"
    if not a["allows"]:
        if a["when"] or b["when"]:
            return None, "exclusion-with-a-context"
        return dict(a, when=[], not_when=sorted(set(a["not_when"]) | set(b["not_when"]), key=str), ratio=None), None
    if a["when"] and b["when"]:
        shared = [one for one in a["when"] if one in b["when"]]
        if not shared:
            return None, "contexts-do-not-overlap"
    else:
        shared = a["when"] or b["when"]
    return dict(a, when=shared, not_when=sorted(set(a["not_when"]) | set(b["not_when"])),
                ratio=merged_ratio(a["ratio"], b["ratio"]), tier="drafted"), None


def merge(first, second):
    """Compare the changes two drafters wrote. Each is a list of {file, field, add, why}."""
    one, two = by_key(first), by_key(second)
    agreed, disputed, single = [], [], []
    for pair in sorted(set(one) | set(two)):
        if pair not in one or pair not in two:
            single.append(one.get(pair) or two[pair])
            continue
        row, why = merged_row(one[pair], two[pair])
        if row is None:
            disputed.append(Dispute(pair[0], pair[1], why, one[pair]["add"], two[pair]["add"]))
        else:
            agreed.append({"file": pair[0], "field": "stands_in_for", "add": dict(row, tier="drafted"),
                           "why": "both drafters wrote this pair"})
    return Result(agreed, disputed, single)


def describe(row):
    kind = "works" if row["allows"] else "fails"
    return "%s when %s, not when %s: %s" % (kind, ", ".join(row["when"]) or "-", ", ".join(row["not_when"]) or "-", row["caveat"])


def report(result):
    lines = ["agreed: %d rows kept" % len(result.agreed),
             "disputed: %d pairs for the owner" % len(result.disputed),
             "single: %d pairs only one drafter wrote, not kept" % len(result.single)]
    for dispute in result.disputed:
        lines.append("  %s stands in for %s, %s" % (dispute.file, dispute.thing, dispute.why))
        lines.append("    first: " + describe(dispute.first))
        lines.append("    second: " + describe(dispute.second))
    for one in result.single:
        lines.append("  only one drafter: %s stands in for %s (%s)" % (one["file"], one["add"]["thing"], describe(one["add"])))
    return lines
