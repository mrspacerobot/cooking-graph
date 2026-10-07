"""An exclusion is not an assertion that a substitute works anywhere else."""

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


RULES = [exclusions_are_explicit]
