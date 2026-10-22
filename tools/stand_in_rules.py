"""An exclusion is not an assertion that a substitute works anywhere else."""

from tools import queries
from tools.reading import Issue


def exclusions_are_explicit(things):
    issues = []
    for thing in things.values():
        for index, row in enumerate(thing.data.get("stands_in_for", [])):
            if row["allows"]:
                continue
            where = "stands_in_for[%d]" % index
            if row["when"]:
                issues.append(Issue(thing.path, where, "exclusion-with-positive-context", "an exclusion has no when"))
            if not row["not_when"]:
                issues.append(Issue(thing.path, where, "exclusion-without-context", "an exclusion names its not_when"))
    return issues


def row_index(candidate, line, ratio):
    for index, row in enumerate(candidate.data["stands_in_for"]):
        if row["thing"] == line["thing"] and row["ratio"] == ratio:
            return index
    return 0


def ratios_fit_their_lines(things):
    """A ratio is by weight, volume or count, so it can only turn an amount measured the same way. Exactly one
    leaves the amount alone, so it is let through; any other would make a server refuse the recipe."""
    issues = []
    for recipe in things.values():
        if recipe.kind != "recipe":
            continue
        whole = things.get(recipe.data["makes"])
        parts = {part["id"]: part for part in whole.data["parts"]} if whole else {}
        for line in recipe.data["ingredients"]:
            if line["part"] not in parts:
                continue
            measure = queries.MEASURE_OF_UNIT.get(line["amount"]["unit"])
            for option in queries.line_answer(things, recipe.data, line, parts[line["part"]], [])["options"]:
                ratio = option.get("ratio")
                if not ratio or measure is None or ratio["by"] == measure or ratio["stand_in"] == ratio["original"]:
                    continue
                candidate = things[option["thing"]]
                issues.append(Issue(candidate.path, "stands_in_for[%d]" % row_index(candidate, line, ratio),
                                    "ratio-measure-mismatch",
                                    "its ratio is by %s but %s measures it in %s" % (ratio["by"], recipe.data["id"], line["amount"]["unit"])))
    return issues


RULES = [exclusions_are_explicit, ratios_fit_their_lines]
