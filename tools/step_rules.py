"""The rules about the text of a recipe step: foods only through placeholders, optional parts only in clauses.

The format is in `docs/recipe-steps.md`; `tools/step_text.py` reads it. The reason for the rules: the server adapts a
recipe in code, never with a model. It puts the name of a swapped-in food where a placeholder stands and drops the
clause of a part left out, so a step that names a food in plain words, or leaves optional text unmarked, would still
say the original food after the swap.
"""

import re
from collections import namedtuple

from tools import plain_mentions, step_text
from tools.reading import Issue
from tools.rules import of_kind

ARTICLE_BEFORE = re.compile(r"(^|[^A-Za-z])[Aa]n?\s+$")
SINGULAR_VERB = re.compile(r"^\s+(is|has|was|does)\b")

# `lines` maps a part to the foods of the recipe's lines that fill it; `foods` is all of them.
Context = namedtuple("Context", ["lines", "optional", "foods", "vocabulary", "uncountable"])
Problem = namedtuple("Problem", ["rule", "message"])


def slug_of(thing_id):
    return thing_id.split("/")[1]


def context_of(things, recipe, vocabulary):
    lines = {}
    for line in recipe["ingredients"]:
        lines.setdefault(line["part"], []).append(line["thing"])
    optional = {part["id"] for part in things[recipe["makes"]].data["parts"] if part["optional"]}
    foods = {line["thing"] for line in recipe["ingredients"]}
    uncountable = {food for food in foods if food in things and things[food].data["uncountable"]}
    return Context(lines, optional, foods, vocabulary, uncountable)


def foods_named(context, mention):
    """The foods a mention stands for, or a problem when it names none or more than one."""
    foods = context.lines.get(mention.part)
    if foods is None:
        return None, Problem("step-part-unknown", "'%s' is a part this recipe has no line for" % mention.part)
    if mention.slug is not None:
        foods = [food for food in foods if slug_of(food) == mention.slug]
        if not foods:
            message = "no line of the part '%s' is the ingredient '%s'" % (mention.part, mention.slug)
            return None, Problem("step-ingredient-unknown", message)
    if len(set(foods)) > 1:
        message = "the part '%s' holds several foods: name one, as {%s.%s}" % (mention.part, mention.part, slug_of(sorted(foods)[0]))
        return None, Problem("step-ingredient-ambiguous", message)
    return set(foods), None


def placeholder_problems(context, pieces):
    problems = []
    for mention, _ in step_text.mentions_of(pieces):
        _, problem = foods_named(context, mention)
        if problem is not None:
            problems.append(problem)
    return problems


def plural_problems(context, pieces):
    """A plural of a food that has none, `a` before a plural, and a singular verb straight after a plural."""
    problems = []
    for mention, _ in step_text.mentions_of(pieces):
        if not mention.plural:
            continue
        foods, problem = foods_named(context, mention)
        if problem is None and foods & context.uncountable:
            message = "{%s:plural} asks for the plural of an uncountable food: write {%s}" % (mention.part, mention.part)
            problems.append(Problem("step-plural-of-uncountable", message))
    return problems + article_and_verb_problems(pieces)


def article_and_verb_problems(pieces):
    problems = []
    for index, piece in enumerate(pieces[:-1]):
        following = pieces[index + 1]
        if isinstance(piece, str) and isinstance(following, step_text.Mention) and following.plural:
            if ARTICLE_BEFORE.search(piece):
                problems.append(Problem("step-article-before-plural", "'a' or 'an' stands before a plural: write 'the' or leave it out"))
        if isinstance(piece, step_text.Mention) and piece.plural and isinstance(following, str) and SINGULAR_VERB.match(following):
            problems.append(Problem("step-number-disagrees", "a singular verb follows {%s:plural}" % piece.part))
    for clause in step_text.clauses_of(pieces):
        problems.extend(article_and_verb_problems(clause.pieces))
    return problems


def clause_problems(context, pieces):
    problems = []
    for clause in step_text.clauses_of(pieces):
        if clause.part not in context.lines:
            problems.append(Problem("step-part-unknown", "'%s' is a part this recipe has no line for" % clause.part))
        elif clause.part not in context.optional:
            message = "the clause marks '%s', which is not an optional part: it is never left out" % clause.part
            problems.append(Problem("step-clause-on-required-part", message))
    return problems


def unmarked_problems(context, pieces):
    """A mention of an optional part must stand in a clause of that part, or leaving the part out would leave it in."""
    problems = []
    for mention, marked_with in step_text.mentions_of(pieces):
        if mention.part in context.optional and marked_with != mention.part:
            message = "{%s} names an optional part outside a clause: write [%s: ... {%s} ...]" % (mention.part, mention.part, mention.part)
            problems.append(Problem("step-optional-unmarked", message))
    return problems


def plain_problems(context, pieces):
    problems = []
    for stretch in step_text.plain_pieces(pieces):
        for words, owners in context.vocabulary.foods_named_in(stretch):
            if owners & context.foods:
                message = "names '%s' in plain words: use the placeholder of its part" % words
                problems.append(Problem("step-plain-ingredient", message))
    return problems


def problems_in(text, context):
    pieces, malformed = step_text.parse(text)
    problems = [Problem("step-text-malformed", message) for message in malformed]
    if malformed:
        return problems
    problems.extend(placeholder_problems(context, pieces))
    problems.extend(clause_problems(context, pieces))
    problems.extend(unmarked_problems(context, pieces))
    problems.extend(plain_problems(context, pieces))
    problems.extend(plural_problems(context, pieces))
    return problems


def steps_name_foods_by_placeholder(things):
    """Every step names the foods of its recipe's lines through placeholders and marks the text of optional parts."""
    vocabulary = plain_mentions.Vocabulary(things)
    issues = []
    for recipe_id, recipe in of_kind(things, "recipe"):
        if recipe.data["makes"] not in things:
            continue
        context = context_of(things, recipe.data, vocabulary)
        for index, step in enumerate(recipe.data["steps"]):
            for problem in problems_in(step["text"], context):
                issues.append(Issue(recipe.path, "steps[%d].text" % index, problem.rule, problem.message))
    return issues


RULES = [steps_name_foods_by_placeholder]
