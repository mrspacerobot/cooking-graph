# Round 1: knife cuts, eggs, stocks

## The probes

30 dish probes were written, ten for each skill, before anything was drafted. The rule in `tools/probes.py` then held six of them back from their ids. Those six were never looked at again.

## First run

| | Growing | Held back |
|---|---|---|
| Answered | 0 of 24 | 0 of 6 |

The 24 growing probes asked for 27 technique words and 54 ingredient words the graph did not hold. That is 56 new techniques per 50 probes.

## What was drafted

| Kind | New | Note |
|---|---|---|
| technique | 39 | 27 that the probes asked for by name, and 12 that the recipes needed for a step: boil an egg, roll an omelette, mince, peel, grate, wilt, season, plate, blanch, refresh, chill, render |
| ingredient | 58 | each with an unverified safety record that answers all 13 facts |
| form | 22 | 6 of them cuts with a size |
| equipment | 29 | |
| preparation | 10 | the three stocks, mirepoix, bouquet garni, roux, béchamel, clarified butter, mayonnaise, shortcrust pastry |
| cuisine | 2 | Provençal and Lyonnaise, each within French |
| dish | 12 | four or five per skill, the ones that teach it best |
| recipe | 15 | one per dish written, one for the seed omelette, and one each for vegetable stock and white chicken stock |

Brown stock has its parts but no recipe yet: it needs roasting and deglazing, which come with later skills.

## After the round

| Kind | All | drafted | sourced | reviewed | verified | cook-tested |
| --- | --- | --- | --- | --- | --- | --- |
| fact | 13 | 13 | 0 | 0 | 0 | 0 |
| cuisine | 3 | 3 | 0 | 0 | 0 | 0 |
| equipment | 35 | 35 | 0 | 0 | 0 | 0 |
| form | 22 | 22 | 0 | 0 | 0 | 0 |
| ingredient | 81 | 81 | 0 | 0 | 0 | 0 |
| technique | 39 | 39 | 0 | 0 | 0 | 0 |
| preparation | 10 | 10 | 0 | 0 | 0 | 0 |
| dish | 14 | 14 | 0 | 0 | 0 | 0 |
| recipe | 15 | 15 | 0 | 0 | 0 | 0 |
| program | 1 | 1 | 0 | 0 | 0 | 0 |
| dish-probe | 30 | 30 | 0 | 0 | 0 | 0 |
| all things of the graph | 233 | 233 | 0 | 0 | 0 | 0 |
| statements | 601 | 601 | 0 | 0 | 0 | 0 |

| Safety records | All | unverified | verified |
| --- | --- | --- | --- |
| ingredients | 81 | 81 | 0 |

| Dish probes | Answered | Share |
| --- | --- | --- |
| growing | 24 of 24 | 100% |
| held-back | 1 of 6 | 17% |

Levels of the program that name a technique: 9 of 37. Recipe steps: 72. Safety points in recipe steps that wait for a verified fact: 16.

## Changes to the model: 8

Changes 7 to 14 in `docs/model-changes.md`: what a technique needs and makes, the size of a form, a part of an ingredient, what a preparation teaches, recipes for preparations, forms on an ingredient line, and safety points on a step. One rule of the checker changed with change 12: a step may work on the thing its recipe is making, so that a stock can be strained.

## Changes to the vocabulary

- Roles of a part: thickener, garnish, sauce, base, topping, sweetener and emulsifier were added.
- New lists: the roles of a need, the measures of a size, the safety points, and units of length.
- Units of amount: kilogram, litre, pinch, clove, sprig, leaf and slice were added. A yield may be a litre, a millilitre or a gram, for a preparation.

## The reread

Twelve of the new files were read again after the check was clean. Three were wrong and were fixed:

- The vichyssoise recipe blended the soup "until smooth", which the puree card names as the mistake that turns potato to glue.
- The salade lyonnaise never washed, dried or tore the frisée.
- Mayonnaise called its egg yolk a thickener. It is the emulsifier.

No reviewer saw any of it. Three in twelve is this draft's own count of its own mistakes, not a reject rate.

## What the model could not express

- **What an earlier step left behind.** The pot-au-feu serves "the broth", and the salade lyonnaise whisks "the warm fat left in the pan". Neither is an ingredient of the recipe, so no step can name it. The step that uses the bacon fat lists the bacon. This will come back with the fond of a pan sauce.
- **A need that holds only for some food.** Poaching needs vinegar for an egg and not for a fish. A need cannot say for what.
- **The numbers that define a technique.** How long a soft egg boils and how hot poaching water is are numbers, so they may not stand in a card, and a card has no field for them. They live only in recipes.
- **A helper that is not what the move works on.** The egg white and the minced meat that clear a consommé are listed as what clarifying works on, for lack of a better place.
- **A cooking aid that stays in the pot.** The vinegar in poaching water is a part of the salade lyonnaise like any other, because a recipe may use nothing its dish does not name.
- **A part that may be left out.** The chives on œufs cocotte are a part like the eggs.
- **One thing a cook either buys or makes.** Chicken stock is two things: an ingredient with the strict facts of a bought stock, and a preparation with a recipe. The bought one stands in for the made one.
- **The forms an ingredient comes in.** The field is empty on all 81 ingredients. Forms found their use on the lines of a recipe instead.
