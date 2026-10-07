"""Conservative avoidance for internal queries, never a verification or an export."""


def free_of(things, thing_id, avoided, seen=()):
    if thing_id in seen or thing_id not in things:
        return False
    thing = things[thing_id]
    if thing.kind == "ingredient":
        safety = thing.data["safety"]
        contains = {row["fact"] for row in safety["contains"]}
        return not contains.intersection(avoided) and set(avoided).issubset(safety["free_of"])
    if thing.kind != "preparation" or not thing.data["parts"]:
        return False
    return all(free_of(things, option, avoided, seen + (thing_id,))
               for part in thing.data["parts"] for option in part["options"])
