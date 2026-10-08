"""What ./review prints: a card as it stands, with its tier and the hash a record must carry. It writes nothing."""

from tools import review_hash, writing


def find(things, thing_id):
    if thing_id not in things:
        raise ValueError("no such thing: " + thing_id)
    return things[thing_id].data


def show(things, thing_id):
    data = find(things, thing_id)
    lines = [thing_id, "tier: " + data.get("tier", "none"), "seen: " + review_hash.seen(data), ""]
    return lines + writing.as_text(data).rstrip("\n").split("\n")


def seal(things, thing_id, field=None, target=None):
    data = find(things, thing_id)
    found = review_hash.seen(data, field, target)
    if found is None:
        raise ValueError("%s has no %s %s" % (thing_id, field, target))
    return found
