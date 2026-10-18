"""The rules about reviews: which tier a record backs, who may grant it, and when it no longer holds.

A tier above drafted is backed when a live record of a reviewer approved it and
the thing is as the reviewer saw it. Only stage one is built: a person who knows
the cuisine may grant reviewed. A person may verify ingredient safety against
evidence. Verified culinary content, samples and rulings remain later stages.
"""

import json
import re
from collections import namedtuple

from tools import review_hash
from tools.reading import Issue, join, nested
from tools.rules import LOWEST_TIER, names_a_source, of_kind

TIERS = ("drafted", "sourced", "reviewed", "verified", "cook-tested")
NOT_BUILT = ("verified", "cook-tested")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
STATEMENT = re.compile(r"^([a-z_]+)\[[0-9]+\]$")
Backing = namedtuple("Backing", ["review_id", "grants", "seen"])


def rank(tier):
    return TIERS.index(tier)


def live_records(things):
    """The records no later record replaces."""
    records = dict(of_kind(things, "review"))
    replaced = set()
    for record in records.values():
        replaced.update(record.data["supersedes"])
    return {record_id: record for record_id, record in records.items() if record_id not in replaced}


def backing(things):
    """What live records approve: {(thing, field, target): [Backing, ...]}."""
    found = {}
    for record_id, record in live_records(things).items():
        for cover in record.data["covers"]:
            if cover["verdict"] == "approved":
                unit = (cover["thing"], cover["field"], cover["target"])
                found.setdefault(unit, []).append(Backing(record_id, record.data["grants"], cover["seen"]))
    return found


def statement_of(where, node):
    """The field and target of an object that is one statement or part of a file, or None."""
    matched = STATEMENT.match(where)
    if matched is None:
        return None
    return matched.group(1), node.get("thing") or node.get("id")


def tier_not_earned(things):
    """Nothing is above drafted unless a live record backs it, or the fact names the source it was taken from.

    Verified and cook-tested wait for a second reviewer and for cooks, and are refused.
    """
    approved = backing(things)
    issues = []
    for thing_id, thing in sorted(things.items()):
        for where, node in nested(thing.data):
            tier = node.get("tier", LOWEST_TIER)
            if tier == LOWEST_TIER:
                continue
            if tier == "sourced" and names_a_source(thing, where):
                continue
            place = join(where, "tier")
            if tier in NOT_BUILT:
                issues.append(Issue(thing.path, place, "tier-not-earned", "'%s' waits for a second reviewer or for cooks, and is not built yet" % tier))
                continue
            units = [(thing_id, None, None)]
            statement = statement_of(where, node) if where != "" else None
            if statement is not None:
                units.append((thing_id,) + statement)
            candidates = [(unit, one) for unit in units for one in approved.get(unit, []) if rank(one.grants) >= rank(tier)]
            if not candidates:
                message = "'%s' was not earned: no live record by a reviewer backs it" % tier
                issues.append(Issue(thing.path, place, "tier-not-earned", message))
            elif not any(one.seen == review_hash.seen(thing.data, unit[1], unit[2]) for unit, one in candidates):
                message = "'%s' was reviewed as it stood, and it has changed since" % tier
                issues.append(Issue(thing.path, place, "review-stale", message))
    return issues


def reviewer_of(things, record):
    """The reviewer a record names, or None when that file has a problem of its own, which is reported there."""
    return things.get(record.data["reviewer"])


def is_safety_record(record):
    covers = record.data['covers']
    return bool(covers) and all(row['field'] == 'safety' and row['target'] is None for row in covers)


def safety_evidence(things, record):
    reviewer = reviewer_of(things, record)
    if reviewer is None or reviewer.data['kind'] != 'person':
        return False
    against = record.data['against']
    if reviewer.data['safety_authority'] and any(row['note'] for row in against):
        return True
    return any(row['how'] == 'source' and row['note'] and row['source'] in things
               and things[row['source']].kind == 'source'
               and things[row['source']].data['url'] and things[row['source']].data['read_on']
               for row in against)


def safety_not_earned(things):
    approved = backing(things)
    issues = []
    for thing_id, thing in of_kind(things, 'ingredient'):
        if thing.data['safety']['state'] != 'verified':
            continue
        candidates = approved.get((thing_id, 'safety', None), [])
        earned = any(one.grants == 'verified' and one.seen == review_hash.seen(thing.data, 'safety')
                     and is_safety_record(things[one.review_id]) and safety_evidence(things, things[one.review_id])
                     for one in candidates)
        if not earned:
            issues.append(Issue(thing.path, 'safety.state', 'safety-not-earned',
                                'verified safety needs a live human approval of this exact safety record, with source evidence or owner-granted authority'))
    return issues


def model_grants_too_much(things):
    """A model may rank and flag. It grants nothing above sourced, and sourced only against a source."""
    issues = []
    for record_id, record in of_kind(things, "review"):
        reviewer = reviewer_of(things, record)
        if reviewer is None or reviewer.data["kind"] != "model":
            continue
        grants = record.data["grants"]
        names_source = any(row["how"] == "source" and row["source"] for row in record.data["against"])
        if rank(grants) > rank("sourced") or (grants == "sourced" and not names_source):
            message = "a model may not grant '%s'" % grants + ("" if grants != "sourced" else " without a source")
            issues.append(Issue(record.path, "grants", "model-grants-too-much", message))
    return issues


def wider_cuisines(things):
    """The cuisines each cuisine sits within, the nearest first."""
    above = {}
    for cuisine_id, cuisine in of_kind(things, "cuisine"):
        chain = []
        wider = cuisine.data["within"]
        while wider is not None and wider["thing"] not in chain and wider["thing"] != cuisine_id and wider["thing"] in things:
            chain.append(wider["thing"])
            wider = things[wider["thing"]].data["within"]
        above[cuisine_id] = chain
    return above


def cuisines_of(data):
    found = set()
    for field in ("belongs_to", "in_pantry_of"):
        found.update(row["thing"] for row in data.get(field, []))
    return found


def reviewer_does_not_know_cuisine(things):
    """A person who grants reviewed or verified answers for a cuisine, knows it, and the thing belongs to it.

    A reviewer of a wider cuisine covers a narrower one within it. The narrower does not cover the wider.
    """
    above = wider_cuisines(things)
    issues = []
    for record_id, record in of_kind(things, "review"):
        reviewer = reviewer_of(things, record)
        if reviewer is None or reviewer.data["kind"] != "person" or rank(record.data["grants"]) < rank("reviewed"):
            continue
        if is_safety_record(record):
            continue
        reviewer = reviewer.data
        cuisine = record.data["cuisine"]
        if cuisine is None:
            issues.append(Issue(record.path, "cuisine", "reviewer-does-not-know-cuisine", "a person names the cuisine answered for"))
            continue
        known = {row["cuisine"] for row in reviewer["knows"]}
        if not known & ({cuisine} | set(above.get(cuisine, []))):
            issues.append(Issue(record.path, "cuisine", "reviewer-does-not-know-cuisine", "'%s' is not a cuisine this reviewer knows" % cuisine))
            continue
        for cover in record.data["covers"]:
            if cover["verdict"] != "approved" or cover["thing"] not in things:
                continue
            belongs = cuisines_of(things[cover["thing"]].data)
            related = {cuisine} | set(above.get(cuisine, []))
            if belongs and not any(one in related or cuisine in above.get(one, []) for one in belongs):
                message = "'%s' does not belong to '%s'" % (cover["thing"], cuisine)
                issues.append(Issue(record.path, "covers", "reviewer-does-not-know-cuisine", message))
                break
    return issues


def review_unlinked(things):
    """Records that replace one another keep their order, and a rejection names the approval it withdraws."""
    issues = []
    records = dict(of_kind(things, "review"))
    for record_id, record in sorted(records.items()):
        for earlier in record.data["supersedes"]:
            if earlier in records and records[earlier].data["on"] > record.data["on"]:
                message = "replaces '%s', which is dated later" % earlier
                issues.append(Issue(record.path, "supersedes", "review-unlinked", message))
    live = live_records(things)
    granted = {}
    for record_id, record in live.items():
        for cover in record.data["covers"]:
            if cover["verdict"] == "approved":
                unit = (cover["thing"], cover["field"], cover["target"])
                granted.setdefault((unit, record.data["grants"]), set()).add(record_id)
    order = lambda item: (item[0][0][0], item[0][0][1] or '', item[0][0][2] or '', item[0][1])
    for (unit, grants), holders in sorted(granted.items(), key=order):
        if len(holders) > 1:
            for record_id in sorted(holders):
                message = "another live record already grants '%s' to the same unit" % grants
                issues.append(Issue(records[record_id].path, "covers", "review-unlinked", message))
    approved = backing(things)
    for record_id, record in sorted(live.items()):
        for cover in record.data["covers"]:
            if cover["verdict"] != "rejected":
                continue
            unit = (cover["thing"], cover["field"], cover["target"])
            standing = [one for one in approved.get(unit, []) if one.review_id != record_id
                        and records[one.review_id].data["on"] <= record.data["on"]]
            if standing:
                message = "rejects a unit that '%s' still approves: name it in supersedes" % standing[0].review_id
                issues.append(Issue(record.path, "covers", "review-unlinked", message))
                break
    return issues


def review_not_built(things):
    """Safety verification is distinct from the later verified culinary tier."""
    issues = []
    for record_id, record in of_kind(things, "review"):
        data = record.data
        if data["mode"] != "rows":
            issues.append(Issue(record.path, "mode", "review-not-built", "samples are not built yet"))
        if data["rulings"]:
            issues.append(Issue(record.path, "rulings", "review-not-built", "rulings on safety disagreements are not built yet"))
        safety = is_safety_record(record)
        if any(cover['field'] == 'safety' for cover in data['covers']):
            if not safety or data['grants'] != 'verified':
                issues.append(Issue(record.path, 'covers', 'review-not-built', 'a safety review covers only safety units and grants verified'))
            reviewer = reviewer_of(things, record)
            if reviewer is None or reviewer.data['kind'] != 'person' or (any(cover['verdict'] == 'approved' for cover in data['covers']) and not safety_evidence(things, record)):
                issues.append(Issue(record.path, 'against', 'safety-not-earned', 'a safety review needs a person and recorded evidence'))
            if any(cover['thing'] in things and things[cover['thing']].kind != 'ingredient' for cover in data['covers']):
                issues.append(Issue(record.path, 'covers', 'safety-not-earned', 'only an ingredient has a safety record'))
        if data["grants"] in NOT_BUILT and not (safety and data['grants'] == 'verified'):
            issues.append(Issue(record.path, "grants", "review-not-built", "'%s' is not built yet" % data["grants"]))
    return issues


def email_in_repo(things):
    """No email address anywhere in the graph. A reviewer is a slug, and the roster is kept outside the repository."""
    issues = []
    for thing_id, thing in sorted(things.items()):
        if EMAIL.search(json.dumps(thing.data, ensure_ascii=False)):
            issues.append(Issue(thing.path, "", "email-in-repo", "holds an email address"))
    return issues


RULES = [email_in_repo, tier_not_earned, model_grants_too_much, reviewer_does_not_know_cuisine, review_unlinked, review_not_built]
