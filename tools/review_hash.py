"""What a reviewer saw, as a short hash, so that an edit made afterwards is noticed.

A tier is a field of the file. The record of the review carries the hash of the
part it covers. If the file changes, the hash no longer matches and the tier falls.
The tier itself is never part of what was seen, so setting it does not undo it.
"""

import hashlib
import json


def without_tiers(value):
    if isinstance(value, dict):
        return {name: without_tiers(inner) for name, inner in value.items() if name != "tier"}
    if isinstance(value, list):
        return [without_tiers(inner) for inner in value]
    return value


def unit(data, field=None, target=None):
    """The part of a thing that a record covers, or None when the thing has no such part.

    No field: the whole thing, without its safety record. The field safety: the safety
    record without its state. A field and a target: the one statement or part of that name.
    """
    if field is None:
        return {name: value for name, value in data.items() if name != "safety"}
    if field not in data:
        return None
    inside = data[field]
    if field == "safety":
        return {name: value for name, value in inside.items() if name != "state"}
    if target is None:
        return inside
    if isinstance(inside, list):
        for row in inside:
            if isinstance(row, dict) and target in (row.get("thing"), row.get("id")):
                return row
    return None


def seen(data, field=None, target=None):
    """Twelve hex digits of the sha256 of the covered part, with no tier in it. None when there is no such part."""
    part = unit(data, field, target)
    if part is None:
        return None
    text = json.dumps(without_tiers(part), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]
