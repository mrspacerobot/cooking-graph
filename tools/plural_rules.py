"""The plural of a food's name, so that a placeholder can print "the eggs" as well as "the egg".

Every ingredient and preparation answers once: it is `uncountable` (butter, salt, rice) and has no plural, or it has a
plural for every language it has a name in. A food with neither is an error, never an assumed plural.
"""

from tools.reading import Issue
from tools.rules import of_kind

FOODS = ("ingredient", "preparation")


def uncountable_has_no_plural(thing):
    if thing.data["uncountable"] and thing.data["plurals"]:
        return [Issue(thing.path, "plurals", "uncountable-with-plural", "an uncountable food has no plural: leave plurals empty")]
    return []


def countable_has_every_plural(thing):
    if thing.data["uncountable"]:
        return []
    issues = []
    for language in thing.data["names"]:
        if language not in thing.data["plurals"]:
            message = "a countable food needs a plural for each language it is named in: '%s' is missing" % language
            issues.append(Issue(thing.path, "plurals", "plural-missing", message))
    for language in thing.data["plurals"]:
        if language not in thing.data["names"]:
            message = "there is a plural in '%s' but no name in that language" % language
            issues.append(Issue(thing.path, join_where("plurals", language), "plural-without-name", message))
    return issues


def join_where(where, language):
    return "%s.%s" % (where, language)


def foods_have_a_plural_or_are_uncountable(things):
    issues = []
    for kind in FOODS:
        for _, thing in of_kind(things, kind):
            issues.extend(uncountable_has_no_plural(thing))
            issues.extend(countable_has_every_plural(thing))
    return issues


RULES = [foods_have_a_plural_or_are_uncountable]
