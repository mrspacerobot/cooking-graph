"""Lists the answers that are strict and not certain.

An ingredient holds a fact for certain, as butter holds milk, or the fact is
recorded strictly because a common form of the ingredient may hold it, as wine
may have been cleared with egg white. How strict to be is for the owner to
rule. This list puts every strict answer in front of him, reason by reason.
"""


def strict_rows(things):
    """Each strict answer as (fact, basis) with the ingredients that share it."""
    rows = {}
    for thing_id, thing in sorted(things.items()):
        if thing.kind != "ingredient":
            continue
        for row in thing.data["safety"]["contains"]:
            if not row["certain"]:
                rows.setdefault((row["fact"], row["basis"]), []).append(thing_id.split("/")[1])
    return rows


def counts(things):
    held = [row for thing in things.values() if thing.kind == "ingredient" for row in thing.data["safety"]["contains"]]
    return len([row for row in held if not row["certain"]]), len(held)


def document(things):
    strict, held = counts(things)
    lines = [
        "# The answers that are strict and not certain",
        "",
        "Written by `./safety strict`. An ingredient holds a fact for certain, or the fact is recorded strictly because a common form of the ingredient may hold it.",
        "The rows below are the strict ones. How strict to be is for the owner to rule, reason by reason. Every safety record is unverified either way.",
        "",
        "%d of the %d facts that ingredients hold are strict." % (strict, held),
        "",
        "| Fact | Basis | Ingredients |",
        "|---|---|---|",
    ]
    for (fact, basis), ingredients in sorted(strict_rows(things).items()):
        lines.append("| `%s` | %s | %s |" % (fact, basis, ", ".join(ingredients)))
    return "\n".join(lines) + "\n"
