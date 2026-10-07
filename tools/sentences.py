"""What a sentence may not say.

A number, an amount, a time or a temperature is data and lives in a field, so
that code can scale and format it. And no sentence may claim that food is
cooked through or safe to eat: that is a safety fact, and safety facts are
verified by a person, never written by the way.
"""

import re

# Digits, the degree and percent signs, and the fraction signs such as one half.
NUMBER_SIGNS = re.compile("[0-9°%¼-¾⅐-⅞]")


def _holds(lowered, phrase):
    """True when the phrase stands in the text as whole words."""
    pattern = r"(?<![a-z])" + re.escape(phrase) + r"(?![a-z])"
    return re.search(pattern, lowered) is not None


def _found(lowered, phrases):
    return [phrase for phrase in phrases if _holds(lowered, phrase)]


def issues_in(text, words):
    """The rules a sentence breaks, each as a rule name and a message."""
    lowered = text.lower()
    issues = []
    if NUMBER_SIGNS.search(text):
        issues.append(("number-in-sentence", "a number belongs in a field with a unit, not in a sentence"))
    for word in _found(lowered, words["sentence_numbers"]):
        issues.append(("number-in-sentence", "'%s' is a number: it belongs in a field, not in a sentence" % word))
    for word in _found(lowered, words["sentence_units"]):
        issues.append(("unit-in-sentence", "'%s' is a unit: an amount, time or temperature belongs in a field" % word))
    for phrase in _found(lowered, words["sentence_claims"]):
        issues.append(("claim-in-sentence", "'%s' claims food is cooked through or safe to eat" % phrase))
    return issues
