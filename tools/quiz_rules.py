"""The rules about a technique card's introduction and quiz that need more than one field to decide."""

from tools.reading import Issue
from tools.rules import of_kind

# A short set keeps distractors focused on plausible cooking mistakes.
MOST_CHOICES = 4


def answers_point_at_a_choice(things):
    """The answer is the place of the right choice, counted from zero, so it must be a choice that is there."""
    issues = []
    for thing_id, thing in of_kind(things, "technique"):
        for index, question in enumerate(thing.data["quiz"]):
            if question["answer"] >= len(question["choices"]):
                where = "quiz[%d].answer" % index
                message = "%d is past the last choice: the first choice is 0" % question["answer"]
                issues.append(Issue(thing.path, where, "quiz-answer-out-of-range", message))
    return issues


def few_choices(things):
    """A question keeps to a few choices, so each one is a real thought a cook might have."""
    issues = []
    for thing_id, thing in of_kind(things, "technique"):
        for index, question in enumerate(thing.data["quiz"]):
            if len(question["choices"]) > MOST_CHOICES:
                where = "quiz[%d].choices" % index
                message = "has %d choices: keep to %d at most" % (len(question["choices"]), MOST_CHOICES)
                issues.append(Issue(thing.path, where, "quiz-too-many-choices", message))
    return issues


def quiz_comes_with_an_intro(things):
    """A quiz tests the idea the introduction names. With no introduction there is nothing to test yet."""
    issues = []
    for thing_id, thing in of_kind(things, "technique"):
        if thing.data["quiz"] and thing.data["intro"] is None:
            issues.append(Issue(thing.path, "quiz", "quiz-without-intro", "a quiz needs the intro it tests"))
    return issues


def question_ids_are_unique(things):
    """A local question id identifies one claim even when questions move."""
    issues = []
    for thing_id, thing in of_kind(things, "technique"):
        found = set()
        for index, question in enumerate(thing.data["quiz"]):
            identifier = question["id"]
            if identifier in found:
                issues.append(Issue(thing.path, "quiz[%d].id" % index, "quiz-id-twice",
                                    "question id '%s' is used twice" % identifier))
            found.add(identifier)
    return issues


RULES = [answers_point_at_a_choice, few_choices, quiz_comes_with_an_intro, question_ids_are_unique]
