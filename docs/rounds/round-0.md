# Round 0: the home and the seed

No growth yet. This round built the place the graph lives in and moved Tomi's library into it.

## What was built

- **The model as a file.** `schema/model.json` is the starting model of mrspacerobot/tomi#106 written as fields, and `schema/words.json` holds the closed word lists.
- **`./check`,** tests first: 114 tests, one failing file per rule, against a small valid repository built in `tests/small_kitchen.py`.
- **`./probe`,** tests first: a probe the graph answers, one it does not, and the held-back rule.
- **`./numbers`** and **`./tidy`,** tests first.
- **The seed from Tomi.**

## The numbers

| Kind | All | drafted | sourced | reviewed | verified | cook-tested |
| --- | --- | --- | --- | --- | --- | --- |
| fact | 13 | 13 | 0 | 0 | 0 | 0 |
| cuisine | 1 | 1 | 0 | 0 | 0 | 0 |
| equipment | 6 | 6 | 0 | 0 | 0 | 0 |
| form | 0 | 0 | 0 | 0 | 0 | 0 |
| ingredient | 23 | 23 | 0 | 0 | 0 | 0 |
| technique | 0 | 0 | 0 | 0 | 0 | 0 |
| preparation | 0 | 0 | 0 | 0 | 0 | 0 |
| dish | 2 | 2 | 0 | 0 | 0 | 0 |
| recipe | 0 | 0 | 0 | 0 | 0 | 0 |
| program | 1 | 1 | 0 | 0 | 0 | 0 |
| dish-probe | 0 | 0 | 0 | 0 | 0 | 0 |
| all things of the graph | 46 | 46 | 0 | 0 | 0 | 0 |
| statements | 50 | 50 | 0 | 0 | 0 | 0 |

| Safety records | All | unverified | verified |
| --- | --- | --- | --- |
| ingredients | 23 | 23 | 0 |

No probes yet. Levels of the program that name a technique: 0 of 37.

## What came from Tomi, and what it became

| In Tomi | In the graph |
|---|---|
| `catalog.json`: 4 courses, 12 skills, 37 levels, prerequisites | `program/french-foundations`, with the same slugs, names and numbers. A prerequisite is `comes_after` |
| `ingredients.json`: 13 facts | `graph/fact/`, same ids as slugs: `animalProduct` is `fact/animal-product`, `slaughterProduct` is `fact/slaughter-product` |
| `ingredients.json`: 23 ingredients | `graph/ingredient/`, same ids. Each keeps exactly the facts Tomi gives it, all unverified |
| `equipment.json`: 6 pieces | `graph/equipment/`, same ids |
| The two lessons | `dish/spinach-and-cheese-omelette` and `dish/seared-chicken-thighs-with-lemon-butter-pan-sauce`, as parts and roles. The lessons' swaps became `stands_in_for` on olive oil and chicken stock |

## What the seed held that the graph did not take

- **Diets and avoid items.** Tomi's table also says which facts a diet rules out and which trigger an avoid item. The graph has no kind for them yet. The safety probe will need them. Default: a `diet` kind when safety probes are written.
- **The screen words of a skill** ("Even pieces cook evenly") and whether a kitchen is assumed to have a piece of equipment. Those belong to the app.
- **The lessons' steps, amounts, quiz and drawings.** A recipe needs its techniques first, and none exists yet. The two recipes are written in the rounds that draft their techniques, in the graph's own words: Tomi's chicken lesson says "cooked through, with no pink", and the graph may not say that.
- **Amounts in cups.** The graph keeps one amount per ingredient, in metric. Turning it into cups needs a density per ingredient, which the graph does not hold. Default: the export does it.

## What was added to the seed, all drafted

- A sentence for what each fact means. Tomi's table has only the ids, so each meaning is this draft's reading of how the table uses the fact.
- For each ingredient: a French name where one is sure, aliases, a sentence on how it behaves in the pan, a note that gives the reason for a strict safety answer, and whether it is in the French pantry.
- Chicken stock and vegetable stock are each a kind of stock.

## What the model could not express

- **"Holds nothing" as a safety answer.** See change 2 in `docs/model.md`.
- **What a level is practised on.** See change 6.
- Nothing else yet: no technique, form, preparation or recipe has been written, so those kinds are still the starting model, untested.

## Doubts about the seed

- **White wine.** Tomi records alcohol and a slaughter product. Isinglass is a fish product, and wine is also cleared with egg white or milk protein. None of those three is recorded. The seed row was kept as it is. A person should decide.
- **What the facts cover.** This draft reads `shellfish` as crustaceans and molluscs, `nuts` as tree nuts and peanuts, and `gluten` as including oats. Those are the stricter readings, and they are guesses about Tomi's intent.
- **Facts the list lacks.** Mustard, celery and sulphites are allergens that must be declared in the European Union, and French cooking uses all three every day. No fact was added: the list is safety vocabulary and a person should extend it.
- **The two seed dishes** are plain home dishes from Tomi's lessons, not named classics.
