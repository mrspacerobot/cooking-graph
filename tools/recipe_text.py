"""The text of a recipe's steps as a cook reads it, once swaps are made and parts are left out.

This is the reference for what the Tomi server does in code: put the name of the food in use where a placeholder
stands, drop the clause of a part that is left out, and drop a step whose text is then empty.
"""

from tools import step_text


def slug_of(thing_id):
    return thing_id.split("/")[1]


def foods_named(recipe, mention):
    """The foods of the recipe lines a mention stands for. Check keeps a mention to one food."""
    foods = []
    for line in recipe["ingredients"]:
        if line["part"] != mention.part:
            continue
        if mention.slug is None or slug_of(line["thing"]) == mention.slug:
            foods.append(line["thing"])
    return foods


def name_in_use(things, recipe, swaps):
    """A function from a mention to the English name of the food in use. `swaps` maps (part, food) to its stand-in."""

    def name_of(mention):
        food = foods_named(recipe, mention)[0]
        instead = swaps.get((mention.part, food), food)
        return things[instead].data["names"]["en"]

    return name_of


def rendered_steps(things, recipe, swaps=None, left_out=()):
    """(step number, text) for each step that stays. Numbers start at one, as a cook counts."""
    name_of = name_in_use(things, recipe, swaps or {})
    kept = []
    for number, step in enumerate(recipe["steps"], start=1):
        pieces, _ = step_text.parse(step["text"])
        text = step_text.render(pieces, name_of, left_out, step_text.PROPER_NAME_WORDS)
        if text:
            kept.append((number, text))
    return kept
