"""Runs the dish probes against the graph and lists what the graph lacks.

A dish probe names a well-known dish, the techniques it needs and its main
ingredients, in plain words. The graph answers a probe when every one of those
words is the name of something it holds. No model is needed to find a gap.

One probe in five is held back. Held-back probes are counted and never shown:
what they lack is not listed, so nothing can be written to please them.
"""

import hashlib
from collections import namedtuple

from tools import names

HELD_BACK_SHARE = 5  # one probe in this many is held back
KINDS_THAT_ANSWER = {
    "techniques": ("technique",),
    "ingredients": ("ingredient", "preparation"),
    "dish": ("dish",),
}

Result = namedtuple("Result", ["growing", "held_back"])


ANSWER_FIELDS = ["probe_id", "batch", "skill", "dish", "techniques", "ingredients", "missing_techniques", "missing_ingredients", "dishes"]


class Answer(namedtuple("Answer", ANSWER_FIELDS)):
    """What the graph says to one probe: the words it has no thing for, and the dish files that match."""

    @property
    def answered(self):
        return not self.missing_techniques and not self.missing_ingredients


def _hash(probe_id):
    return hashlib.sha256(probe_id.encode("utf-8")).hexdigest()


def held_back_ids(batch_ids, never=()):
    """The probes of one batch that are held back: one in five, taken in the order their ids hash.

    Nobody picks. The order follows from the ids alone and is the same on
    every machine. A probe in `never` is passed over and the next in the
    order takes its place: a probe whose dish is already written, or that a
    level of a program is practised through. If too few are left, fewer are held back.
    """
    in_hash_order = sorted(batch_ids, key=_hash)
    may_be_held_back = [probe_id for probe_id in in_hash_order if probe_id not in never]
    return set(may_be_held_back[: len(in_hash_order) // HELD_BACK_SHARE])


def dish_names(probe):
    """The plain names a probe's dish goes by."""
    return {names.plain(name) for name in [probe["dish"]] + probe["also_called"]}


def name_index(things, kinds):
    """Which things of the given kinds go by each plain name."""
    index = {}
    for thing_id, thing in things.items():
        if thing.kind in kinds:
            for name in names.plain_names(thing.data):
                index.setdefault(name, []).append(thing_id)
    return index


def missing(words, index):
    return [word for word in words if names.plain(word) not in index]


def answer(probe, indexes):
    dishes = set()
    for name in dish_names(probe):
        dishes.update(indexes["dish"].get(name, []))
    return Answer(
        probe_id=probe["id"],
        batch=probe["batch"],
        skill=probe["written_for"],
        dish=probe["dish"],
        techniques=list(probe["techniques"]),
        ingredients=list(probe["ingredients"]),
        missing_techniques=missing(probe["techniques"], indexes["techniques"]),
        missing_ingredients=missing(probe["ingredients"], indexes["ingredients"]),
        dishes=sorted(dishes),
    )


def run(things, batch=None):
    """Answer every dish probe, or those of one batch, the growing ones and the held-back ones apart."""
    indexes = {word: name_index(things, kinds) for word, kinds in KINDS_THAT_ANSWER.items()}
    result = Result(growing=[], held_back=[])
    for thing_id, thing in sorted(things.items()):
        if thing.kind != "dish-probe":
            continue
        if batch is not None and thing.data["batch"] != batch:
            continue
        if thing.data["set"] == "held-back":
            result.held_back.append(answer(thing.data, indexes))
        else:
            result.growing.append(answer(thing.data, indexes))
    return result


def share(answers):
    """How many of the answers are full, and out of how many."""
    return (len([one for one in answers if one.answered]), len(answers))


def shares(result):
    return {"growing": share(result.growing), "held-back": share(result.held_back)}


def words_answered(answers):
    """How many technique words and ingredient words the graph has a name for, and out of how many."""
    techniques = sum(len(one.techniques) for one in answers)
    ingredients = sum(len(one.ingredients) for one in answers)
    return {
        "techniques": (techniques - sum(len(one.missing_techniques) for one in answers), techniques),
        "ingredients": (ingredients - sum(len(one.missing_ingredients) for one in answers), ingredients),
    }


def word_shares(result):
    """The words answered, for each set. A count names no word, so it may be shown for the held-back set too."""
    return {"growing": words_answered(result.growing), "held-back": words_answered(result.held_back)}


def new_words(answers, field):
    """The distinct words the graph has no name for. Only ever counted: a held-back word must not be named."""
    return {names.plain(word) for one in answers for word in getattr(one, field)}


def per_fifty(count, probes):
    """A count of new words, brought to a batch of fifty probes so that batches of any size compare."""
    return round(50 * count / probes, 1)


def batch_numbers(growing, held_back):
    everyone = growing + held_back
    techniques = len(new_words(everyone, "missing_techniques"))
    ingredients = len(new_words(everyone, "missing_ingredients"))
    return {
        "probes": len(everyone),
        "growing": share(growing),
        "held-back": share(held_back),
        "new_technique_words": techniques,
        "new_ingredient_words": ingredients,
        "technique_words_per_50": per_fifty(techniques, len(everyone)),
        "ingredient_words_per_50": per_fifty(ingredients, len(everyone)),
    }


def by_batch(result):
    """The numbers of each batch: its probes, those answered in each set, and its new words.

    A new word is a technique or ingredient word the graph has no name for.
    It is counted once in a batch, whoever asks for it, the held-back probes
    included. A count names no word.
    """
    batches = sorted({one.batch for one in result.growing + result.held_back})
    numbers = {}
    for batch in batches:
        growing = [one for one in result.growing if one.batch == batch]
        held_back = [one for one in result.held_back if one.batch == batch]
        numbers[batch] = batch_numbers(growing, held_back)
    return numbers


def batch_lines(result):
    """The numbers of each batch as a Markdown table."""
    header = ["Batch", "Probes", "Growing answered", "Held back answered", "New technique words", "per 50 probes", "New ingredient words", "per 50 probes"]
    lines = ["| " + " | ".join(header) + " |", "|" + " --- |" * len(header)]
    for batch, numbers in by_batch(result).items():
        cells = [
            batch,
            numbers["probes"],
            "%d of %d" % numbers["growing"],
            "%d of %d" % numbers["held-back"],
            numbers["new_technique_words"],
            numbers["technique_words_per_50"],
            numbers["new_ingredient_words"],
            numbers["ingredient_words_per_50"],
        ]
        lines.append("| " + " | ".join(str(cell) for cell in cells) + " |")
    return lines


def as_share(pair):
    answered, total = pair
    if total == 0:
        return "0 of 0"
    return "%d of %d (%d%%)" % (answered, total, round(100 * answered / total))


def gaps(answers, field):
    """Each missing word with the dishes that ask for it, the most wanted first."""
    wanted = {}
    for one in answers:
        for word in getattr(one, field):
            wanted.setdefault(names.plain(word), []).append(one.dish)
    return sorted(wanted.items(), key=lambda gap: (-len(gap[1]), gap[0]))


def skill_lines(result):
    skills = sorted({one.skill for one in result.growing + result.held_back})
    lines = []
    for skill in skills:
        growing = share([one for one in result.growing if one.skill == skill])
        held_back = share([one for one in result.held_back if one.skill == skill])
        lines.append("  %s: growing %s, held back %s" % (skill, as_share(growing), as_share(held_back)))
    return lines


def gap_lines(result, field, title):
    found = gaps(result.growing, field)
    lines = ["  %s (%d):" % (title, len(found))]
    for word, dishes in found:
        lines.append("    %s: %s" % (word, ", ".join(sorted(dishes))))
    return lines


def report(result):
    """The run as text. A held-back probe adds to a count and to nothing else."""
    written = [one for one in result.growing if one.dishes]
    lines = [
        "Dish probes that grow the graph: %s answered" % as_share(share(result.growing)),
        "Dish probes held back: %s answered. What they lack is never listed." % as_share(share(result.held_back)),
        "Growing probes whose dish is written: %d of %d" % (len(written), len(result.growing)),
        "",
        "Words the graph has a name for:",
    ]
    for name, words in word_shares(result).items():
        counted = (name, as_share(words["techniques"]), as_share(words["ingredients"]))
        lines.append("  %s: techniques %s, ingredients %s" % counted)
    lines += [
        "",
        "By skill:",
    ]
    lines.extend(skill_lines(result))
    lines.extend(["", "What the growing probes lack:"])
    lines.extend(gap_lines(result, "missing_techniques", "techniques"))
    lines.extend(gap_lines(result, "missing_ingredients", "ingredients and preparations"))
    return "\n".join(lines)
