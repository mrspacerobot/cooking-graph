# The model

How the cooking graph is laid out. This document was written last, from what was built in the first slice (mrspacerobot/tomi#119), not before it.

`schema/model.json` is the model as the checker reads it, and `schema/words.json` holds the closed word lists. This document says the same in words. `./check` fails when it names fewer kinds or fields than the model has, so it cannot fall behind.

Everything built with this model so far is a model's draft that nobody has reviewed. `docs/night-one.md` says how far it can be trusted.

## Files and ids

- **One thing, one file.** A thing of the graph lives at `graph/<kind>/<slug>.json`. A probe lives at `probes/<probe-kind>/<slug>.json`.
- **The id is the kind and the slug:** `technique/deglaze`. The slug is lowercase English words joined by hyphens. An id is permanent: never renamed, never reused. A file's `id` must be the one its place gives it.
- **Every field is always written,** in the order of the model. An empty list is `[]`. `null` is allowed only where the model says so. An unknown field, a missing field and a field out of order are all issues.
- **A reference is an id.** It must exist, and be of a kind the field allows.
- **A file is written one way.** `./tidy` writes it: two spaces, a statement or an amount on one line, sentences on a line each.

## Trust

Every thing and every statement carries a `tier`:

| Tier | Meaning |
|---|---|
| drafted | A model wrote it |
| sourced | It is taken from a named reference that a person can open |
| reviewed | A reviewer who knows that cuisine approved it |
| verified | Confirmed a second time, by another reviewer or a test cook |
| cook-tested | Results from real cooks back it |

The plan asks for who, when and against what on every tier. No such record exists yet. Until it does, the check refuses every tier above drafted, so nothing can claim more than it earned, with one exception. A row that says where a fact is regulated names its `source`: a page that was fetched, with the day it was read. Such a row may be sourced, and so may the fact that carries one. Nothing else may be sourced, and nothing is above sourced.

A safety record has a `state` of its own, with two values: unverified and verified. The check refuses verified for the same reason.

## What every thing has

| Field | What it holds |
|---|---|
| `id` | The kind and the slug |
| `tier` | One of the five tiers |
| `names` | One name per language tag. `en` is required. A name in another script brings its romanization under `<tag>-Latn`. A French term keeps its own name beside the English one |
| `aliases` | Other names it goes by, as a list per language tag |

Two things of one kind may not share a name or an alias, in any language. That would be two nodes for one thing.

A source and a probe have an `id` and a `tier` and no names: a source has a `title`,
a probe names the dish, recipe or technique its question concerns.

## The kinds

A statement is a field of the thing it starts from. It holds one row for each thing it points at. A row is the `thing`, what the statement adds, and its `tier`.

### `source`

A page that something in the graph was read in, or a dataset that was looked at: a regulator's list, a standard, an open database.

| Field | What it holds |
|---|---|
| `title` | The title of the page or the document, as it stands there |
| `publisher` | Who publishes it |
| `url` | The web address that was fetched |
| `read_on` | The day it was read |
| `reuse` | Its reuse terms as the source states them, or what could not be read |
| `commercial_use` | One of allowed, share-alike, not-allowed and unclear: may it be used in a product that is sold, without having to share our own data alike |
| `taken` | What was taken from it. For a dataset that was only looked at: that nothing was imported, and what it could give |

A source is cited for its facts. The wording of the graph is our own. Only the names a list uses are kept as they stand there.

### `fact`

A safety fact: something a cook may need to avoid. There are 21. Five are matters of diet and are Tomi's: meat, pork, animal product, slaughter product and alcohol. Sixteen are allergens, rebuilt in cycle two from the lists of seven places, at the grain those lists use.

| Field | What it holds |
|---|---|
| `means` | A sentence that says what the fact covers |
| `concern` | allergen or diet |
| `regulated` | Where a list names it, one row for each place and standing. A row has `where` (european-union, united-kingdom, united-states, canada, australia-and-new-zealand, japan or codex), the `source` it was read in, the `name` used there, its `standing` (mandatory or recommended), the `exemptions` the source states or `null`, a `note` or `null` on how the entry there differs from the fact, and the row's `tier` |

A row is sourced when its page was fetched and the entry is on it. The rows read in the Codex standard are drafted: the only text that could be fetched is the one amended up to 2010.

### `cuisine`

A cooking tradition, nested by region.

| Field | What it holds |
|---|---|
| `within` | The cuisine it lies within, as one statement. `null` for a tradition that lies within no other |

### `equipment`

A tool or a vessel.

| Field | What it holds |
|---|---|
| `use` | A sentence that says what it is for |

### `form`

A state food is in: a cut, a result of cooking, or a condition such as cold.

| Field | What it holds |
|---|---|
| `looks_like` | A sentence that says how to tell it is right |
| `size` | For a cut that is defined by its size: rows of a `measure` (side, width, length, thickness) and a `length` with a unit. Empty for every other form |

### `group`

Ingredients and preparations that behave alike in cooking. A technique works on groups, so that its card speaks of a kind of food and not of a list.

| Field | What it holds |
|---|---|
| `shares` | A sentence that says what the members share in the pan, and why a technique cares |
| `within` | The wider group it sits within, as one statement, or `null` |
| `stands_alone` | Why it has fewer than two members for now, or `null`. The check asks for it when a group is that small |

A group must be narrow enough that a technique's card is true for every member. If the card would need an exception for one member, the group is too wide and is split. A wide group, such as vegetables or meat, is what a move that suits everything works on: seasoning, plating.

### `ingredient`

Something a cook starts from. It may stand for a class: stock, bread, white fish.

| Field | What it holds |
|---|---|
| `is_a` | The classes it is a kind of. Statement |
| `part_of` | The ingredient it is a part or a cut of: a yolk of an egg, a thigh of a chicken. Statement |
| `groups` | The groups it is in. Statement |
| `forms` | The forms it comes in. Statement. Empty on every ingredient so far, see the gaps below |
| `behaviour` | A sentence or two on how it behaves in the pan |
| `safety` | Its safety record: a `state`, the facts it `contains`, the facts it is `free_of`, and a `note` or `null`. Each row of `contains` names the `fact`, the `basis` in a few plain words, and whether it is `certain`: true when the ingredient holds the fact by what it is, false when the answer is recorded strictly because a common form of the ingredient may hold it |
| `stands_in_for` | Contextual replacements and exclusions. Each statement adds `allows`, `when` and `not_when` (techniques, preparations or dishes), a `ratio` or `null`, and a `caveat`. A ratio is the `stand_in` amount for the `original` amount, measured `by` weight, volume or count |
| `in_pantry_of` | The cuisines that keep it as a staple. Statement |

### `technique`

One kitchen move, defined by what it does to food.

| Field | What it holds |
|---|---|
| `does` | A sentence that says what the move does to food |
| `how` | The move in a few short beats, at least two |
| `cues` | What tells the cook it is right, at least one. Each has a `sense` (see, hear, smell, feel, taste) and a `text` |
| `mistakes` | The mistakes people really make, at least one. Each has the `mistake` and its `fix` |
| `works_on` | What the move is done to. Statement. It points at groups. It may name a single ingredient or preparation only where nothing else in the graph behaves like it, and never more than three |
| `makes` | What it leaves: forms or preparations. Statement |
| `needs` | What it cannot be done without. Statement. Each row has a `role` and `options`: equipment, ingredients or preparations, any one of which will do |
| `comes_after` | The techniques to learn first. Statement. Each row adds `why` |
| `variant_of` | The technique it is a variant of. Statement. Each row adds what `differs` |
| `belongs_to` | The cuisines it belongs to. Statement. Empty for a move that belongs to no one tradition |

### `preparation`

A building block made on the way to a dish: a stock, a roux, a vinaigrette. A preparation with no parts is a by-product, something a step leaves behind: fond, pan sauce, broth, rendered fat, poaching liquid, braising liquid, jus.

| Field | What it holds |
|---|---|
| `is` | A sentence that says what it is |
| `parts` | What it is made of. Statement. Each row has an `id` that is its own within this preparation or dish, a `role`, its `options` (the ingredients or preparations a cook may choose), and whether it is `optional`. Empty for a by-product |
| `groups` | The groups it is in, where it behaves like one. Statement |
| `teaches` | The techniques it is a good way to learn. Statement |
| `stands_in_for` | What it can replace, as on an ingredient |
| `belongs_to` | The cuisines it belongs to. Statement |

### `dish`

A named thing people serve, written as parts and roles.

| Field | What it holds |
|---|---|
| `is` | A sentence that says what it is |
| `parts` | What it is made of, as on a preparation, at least one. A dish names every ingredient any of its recipes uses |
| `teaches` | The techniques it is a good way to learn. Statement |
| `belongs_to` | The cuisines it belongs to. Statement |

### `recipe`

One way to make a dish or a preparation, with amounts and steps. No recipe here has been cooked.

| Field | What it holds |
|---|---|
| `makes` | The dish or preparation it makes |
| `yields` | How much: a number of servings, or an amount for a preparation |
| `ingredients` | The lines, at least one. Each has the `thing` (an ingredient, or a preparation made ahead), its `amount`, the `forms` it is in before the first step, and the `part` of the dish it fills, by that part's id |
| `equipment` | The equipment it needs |
| `steps` | The steps in order, at least one. Each has one `technique`, what the technique `works_on`, what it is done `with` (the fat, the salt, the liquid poured in), its `text`, a `time` or `null`, a `temperature` or `null`, its `safety_points`, and what it `makes` |

`works_on` means one thing everywhere. On a step it is what the technique acts on, and it must be something the technique's card works on, directly or through a group. Deglazing works on the fond, with the wine.

A step handles only what is at hand: a line of the recipe, the thing the recipe is making, or something this step or an earlier one `makes`. Every line is used by some step. Every line fills a part of the dish with one of that part's options, and every part that is not optional is filled.

`safety_points` mark where a fact that a person has verified must be supplied before a cook may see the step. A point claims nothing.

| Safety point | Where it is put |
|---|---|
| doneness | The step that decides when meat, poultry or fish has cooked enough |
| raw-meat-or-fish | A step that serves meat or fish raw |
| raw-or-lightly-cooked-egg | A step that serves egg raw or soft |
| cooling-and-keeping | A step that cools or keeps food that spoils fast |

### `program`

A teaching path. Only a program knows levels. No level is written on a technique or a dish.

| Field | What it holds |
|---|---|
| `belongs_to` | The cuisines it belongs to. Statement |
| `courses` | The courses, at least one. Each has a `slug`, `names` and its `skills` |
| `skills` | The skills of a course. Each has a `slug`, `names`, what it `comes_after` and its `levels` |
| `comes_after` | On a skill: the skills to learn first. Each row names a `skill` by its slug and carries a `tier` |
| `levels` | The levels of a skill, numbered from 1. Each has its `number`, `names`, the techniques it `teaches` and the dishes or preparations it is practised `through` |

### `dish-probe`

A question the graph must be able to answer: can this well-known dish be written with what the graph holds? A probe is no part of the graph. It lives in `probes/`.

| Field | What it holds |
|---|---|
| `batch` | The batch it was written in. A batch is closed once it is committed |
| `set` | growing or held-back. The rule in `tools/probes.py` decides: one in five of a batch, taken in the order their ids hash. A probe is passed over, and the next takes its place, when its dish is already written, as a dish, a recipe or a preparation, or a level of a program is practised through it |
| `written_by` | Who wrote the probe. The model that drafts the graph writes no probes |
| `written_for` | The skill of a program it was written for |
| `dish` | The dish, in plain words |
| `also_called` | Other names of the dish |
| `techniques` | The techniques it needs, in plain words, at least one |
| `ingredients` | Its main ingredients, in plain words, at least one |

A probe is answered when every one of its technique words is a name of a technique, and every one of its ingredient words is a name of an ingredient or a preparation. One missing word fails the probe, so `./probe` also counts the words answered, for each set. It lists what the growing probes lack. Of the held-back probes it gives counts only and never a word. No dish, recipe or preparation may carry the name of a held-back probe.

### `safety-probe`

A second question: what does this well-known dish hold? It lives in `probes/` too, and one in five of a batch is held back by the plain hash rule. A held-back safety probe may ask about a dish that is written. It is counted, and what it disagrees with is never shown.

| Field | What it holds |
|---|---|
| `batch`, `set`, `written_by`, `dish`, `also_called` | As on a dish probe |
| `holds` | What the classic dish holds, in plain words |
| `does_not_hold` | What it does not hold, in plain words |
| `why` | The reason, in the writer's own words. It is a note and may hold numbers |

`./safety` answers a safety probe whose dish is in the graph and has a recipe. What the dish holds is what the ingredients of its recipe hold. A preparation on a line brings what the ingredients of its own recipe hold, or every option of its parts when it has no recipe. A word of the probe is read as a fact through the fact's names and aliases, and a word that names no fact is set apart. A dish that is not in the graph is not answerable, which is not a disagreement. `./safety disagreements` writes every disagreement of a growing probe, with both sides, and the check keeps `docs/safety-disagreements.md` equal to it. Nothing settles a disagreement but a person.

## The statements of the plan, and where they went

| Statement in the plan | Kept in | Field | Rows after night one |
|---|---|---|---|
| is a kind of | the ingredient | `is_a` | 23 |
| is the same move as, or a variant of | the technique | `variant_of`, with `differs`. The same move under another name is one technique with two names | 12 |
| works on | the technique | `works_on`, pointing at groups | 342 |
| makes | the technique | `makes` | 51 |
| needs | the technique | `needs`, with `role` and `options` | 167 |
| comes before | the later technique, and the later skill of a program | `comes_after`, with `why` on a technique | 32 and 12 |
| stands in for | the ingredient or the preparation | `stands_in_for` | 11 |
| belongs to | the technique, preparation, dish or program | `belongs_to` | 91 |
| is in the pantry of | the ingredient | `in_pantry_of` | 39 |
| is part of | the ingredient, for a part or a cut of another ingredient | `part_of` | 5 |
| uses, in a role, with options | the dish or the preparation | `parts` | 498 |
| teaches | the dish, the preparation, or a level of a program | `teaches` | 202 |
| contains | the ingredient | `safety`. Not a statement with a tier: one record with a state | 138 records |

Four statements are not in the plan: a cuisine lies `within` another, a level is practised `through` a dish or a preparation, an ingredient or a preparation is in `groups`, and a group sits `within` a wider one.

What a preparation, a dish or a recipe holds is never written. It follows from its ingredients, through every option of every part. Three rules keep that sound: an ingredient answers every fact, a class or a whole holds every fact its members or parts hold, and a recipe uses nothing its dish does not name.

## Numbers

A number never stands in a sentence. It is `{"value", "unit"}` or `{"from", "to", "unit"}`, with the unit from the list its field names.

| Field | Units |
|---|---|
| `amount` | gram, kilogram, millilitre, litre, piece, teaspoon, tablespoon, pinch, clove, sprig, leaf, slice |
| `yields` | serving, litre, millilitre, gram |
| `time` | second, minute, hour |
| `temperature` | celsius |
| `length` | millimetre, centimetre |

In every sentence the check looks for digits, for number words from two to twelve and beyond, for unit words, and for words that claim food is cooked through or safe to eat. The lists are in `schema/words.json`. One, half, a third and a quarter are allowed: they scale with the recipe.

## The roles

| List | Words |
|---|---|
| The role of a part | main, fat, filling, seasoning, aromatic, liquid, enrichment, acid, side, thickener, garnish, sauce, base, topping, sweetener, emulsifier, coating |
| The role of a need | vessel, tool, heat, liquid, fat, acid, seasoning, coating |

## The rules beyond the shape of a file

| Rule | What it refuses |
|---|---|
| tier-not-earned, safety-not-earned | A tier above drafted, or a verified safety record, while no review can be put on record. Sourced is allowed on a row that says where a fact is regulated, and on a fact with such a row |
| regulated-twice | A fact said twice to have one standing in one place |
| bad-date, bad-url | A source read on a day that does not exist, or with no web address |
| not-current | A document that a command writes from the files, `docs/strict-answers.md` or `docs/safety-disagreements.md`, that has fallen behind them |
| fact-not-answered, fact-answered-twice | An ingredient that does not answer every fact exactly once |
| class-less-strict, whole-less-strict | An ingredient that holds a fact its class or its whole does not |
| step-works-on-unlisted, ingredient-never-used | A step that works on something not at hand, or a line no step uses |
| part-unknown, not-an-option-of-its-part, part-not-filled, part-id-twice | A recipe line that names no part of its dish or is no option of it, a part no line fills unless it is optional, and two parts of a dish with one id |
| not-what-the-technique-works-on | A step whose technique works on something its card does not work on, directly or through a group |
| too-many-single-things, already-in-a-group, group-too-small | A technique that names more than three single things or one its group already holds, and a group with fewer than two members that does not say why |
| by-product-as-part, by-product-as-ingredient | A by-product named as a part or bought as an ingredient |
| same-name-twice | Two things of one kind with one name |
| cycle | A thing that is a kind of, part of, within, after or a variant of itself |
| slug-twice, skill-unknown, level-numbers | A program that does not hold together |
| held-back-rule, level-dish-held-back, same-dish-twice, drafted-towards-held-back | A probe set by hand, a held-back probe for a dish a level is practised through, a dish asked twice in one batch, and a dish written towards a held-back probe |
| number-in-sentence, unit-in-sentence, claim-in-sentence | A sentence that holds data or a safety claim |
| em-dash | The em dash, in any file of the repository |
| not-tidy, field-order | A file not written the one way |
| not-in-the-model-document | A kind or a field this document does not name |

## Changes to the starting model

The starting model is the one in mrspacerobot/tomi#106: nine kinds, ten statements, the id rule and five tiers. This is the log of every place where real content did not fit it, in the order it happened, each with the example that forced it. A new change is added here in the commit that makes it.

What counts as a change: a change to `schema/model.json`. That is a kind, a field, a statement, what a statement may point at, or the file a statement is kept in. A new word in a closed list of `schema/words.json`, such as a unit or a role, is a change to the vocabulary and not to the model. Vocabulary changes are listed in each round's notes.

| Round | Changes to the model | Changes to the vocabulary |
|---|---|---|
| 0, the seed | 6 | the first lists |
| 1, knife cuts, eggs, stocks | 8 | yes |
| 2, sauté, sear, poach | 1 | yes |
| 3, roux, pan sauces, emulsions | 1 | none |
| 4, braise, roast, gratin | 0 | none |
| cycle two, part 1: groups, parts, probes | 5 | none |
| cycle two, part 2: sources and allergens | 5 | yes |

### 1. A tenth kind: fact (round 0)

- **Example:** butter contains dairy (Tomi's ingredient table).
- **What did not fit:** "contains" needs something to point at. Dairy is not an ingredient, a form, or any other of the nine kinds, yet it needs an id that never changes, names, and a sentence that says what it covers.
- **Now:** `graph/fact/` holds one file per safety fact, with `means`. The thirteen facts are Tomi's.

### 2. "Contains" is a safety record, not a statement with a tier (round 0)

- **Example:** olive oil, written `"contains": []` in Tomi's table. And white wine, which holds a slaughter product.
- **What did not fit:** a statement per fact leaves no row for "holds nothing", and "nothing" is a claim that needs verifying as much as "dairy" does. A safety fact has two states of its own, not five tiers. And white wine holding a slaughter product cannot be reviewed without its reason.
- **Now:** every ingredient has one `safety` record: a `state` (unverified or verified), the facts it `contains`, the facts it is `free_of`, and a `note`. Every fact of the graph must be in one of the two lists. A fact added later is unanswered in every older record, and the check fails until each is answered. Nothing is read as "free of" by default.

### 3. "Contains" starts only from an ingredient (round 0)

- **Example:** the spinach and cheese omelette of Tomi's lesson.
- **What did not fit:** writing "contains egg and dairy" on the dish repeats what egg and butter already say, and the two can come to disagree. The epic's own example, "most dashi contains fish", is a fact about what dashi is made of.
- **Now:** only ingredients carry safety facts. What a preparation, a dish or a recipe holds follows from its ingredients, through every option of every part. Two rules keep that sound: a recipe may use nothing its dish does not name as a part, and an ingredient that stands for a class (stock) holds every fact its members hold (chicken stock, vegetable stock).

### 4. "Is part of" is not stored for a part of a dish (round 0)

- **Example:** butter in the omelette.
- **What did not fit:** "butter is part of the omelette" is the same fact as "the omelette uses butter", read from the other end. Kept in the file of the thing it starts from, butter's file would list every dish that uses butter, and each of those would say it again.
- **Now:** the fact is kept once, in the whole: a dish or a preparation lists its `parts`. The other direction is a query.

### 5. "Comes before" is kept in the later thing, as comes after (round 0)

- **Example:** in Tomi's catalog, stocks names knife cuts as what comes first.
- **What did not fit:** what a thing builds on is known when it is written. Kept in the earlier thing, the earlier file must be opened again every time something new builds on it.
- **Now:** a technique and a skill of a program say what they `comes_after`, each with a `why`. The other direction is a query.

### 6. A level says what it is practised through (round 0)

- **Example:** the three levels of braise: braised leeks, chicken in wine, beef in red wine.
- **What did not fit:** all three teach braising. With `teaches` alone they are the same level three times.
- **Now:** a level has `teaches` (techniques) and `through` (the dishes or preparations it is practised on).

### 7. A technique needs more than equipment (round 1)

- **Example:** poaching an egg needs water held just under a simmer, and a little vinegar. Scrambling needs butter.
- **What did not fit:** the starting model's "needs" names a tool or a vessel: "stir-frying needs a wok or a wide pan". Many moves cannot be done without a liquid, a fat or an acid, and that is neither what the move works on nor a tool.
- **Now:** a need has a `role` from a closed list (vessel, tool, heat, liquid, fat, acid, seasoning) and `options` that may be equipment, ingredients or preparations.

### 8. A technique can make a preparation, not only a form (round 1)

- **Example:** making a roux makes a roux.
- **What did not fit:** "makes" pointed at a form, a state food is left in. A roux is not a state of flour. It is a building block with parts of its own.
- **Now:** `makes` points at a form or a preparation.

### 9. A form can have a size (round 1)

- **Example:** brunoise.
- **What did not fit:** a classic cut is defined by its size, and no number may stand in a sentence. `looks_like` alone cannot say how small.
- **Now:** a form has `size`: a list of a `measure` (side, width, length, thickness) and a `length` with a unit. It is empty for a form that has no fixed size.

### 10. An ingredient can be part of another (round 1)

- **Example:** egg yolk, in steak tartare.
- **What did not fit:** a yolk is not a kind of egg, so `is_a` would be false. Without any link, a kitchen that holds eggs could not be told it holds yolks.
- **Now:** an ingredient has `part_of`. This is the starting model's "is part of", back with a narrower meaning than in change 4: a part or a cut of one ingredient. The whole holds every safety fact its parts hold, and the check enforces it.

### 11. A preparation teaches too (round 1)

- **Example:** white chicken stock teaches skimming. Mirepoix teaches dicing.
- **What did not fit:** "teaches" started from a dish. Three of Tomi's twelve skills are taught on preparations: the stocks, the roux and the emulsions.
- **Now:** a preparation has `teaches`, like a dish.

### 12. A recipe can make a preparation (round 1)

- **Example:** white chicken stock.
- **What did not fit:** a recipe was "one way to make a dish". A stock is not served, yet it is the thing a cook most needs a recipe for.
- **Now:** a recipe `makes` a dish or a preparation. A recipe may also list a preparation among its ingredients, made ahead by its own recipe. A step may work on the thing its recipe is making, so that a stock can be strained and cooled.

### 13. An ingredient line says what form the ingredient is in (round 1)

- **Example:** the cheese of the omelette is grated. The celeriac of céleri rémoulade is peeled and cut in julienne.
- **What did not fit:** a line had a thing and an amount. A cook reads "one onion, diced", and the starting model had forms but no place where a recipe uses one.
- **Now:** a line has `forms`: the states the ingredient is in before the first step, in the order they are done. A step is still used for a cut when the cut is what the dish teaches.

### 14. A step can mark where a safety fact is needed (round 1)

- **Example:** steak tartare serves beef and egg yolk raw. Soft scrambled eggs stay runny. A stock must be cooled fast before it is kept. And Tomi's chicken lesson says "cooked through", which the graph may not say.
- **What did not fit:** no text may claim food is cooked through or safe to eat, and no safe temperature or time may be given. But a recipe that says nothing at the point where it matters is worse. The model had no way to say "a verified fact belongs here".
- **Now:** a step has `safety_points`, from a closed list: `doneness`, `raw-meat-or-fish`, `raw-or-lightly-cooked-egg`, `cooling-and-keeping`. A point claims nothing. It marks the place where an export must put a fact a person has verified, and a recipe with an open point cannot be exported.

### 15. A step says what it leaves behind (round 2)

- **Example:** steak au poivre. Searing leaves a fond on the pan, and the next step deglazes it. Round 1 had met the same thing twice already: the broth of the pot-au-feu and the bacon fat of the salade lyonnaise.
- **What did not fit:** a step could work only on what the recipe lists. A fond is not bought and has no amount. Yet it is the thing a pan sauce is made of, and "deglazing works on the fond" is the centre of that skill.
- **Now:** a step has `makes`: the preparations it leaves behind. A later step may work on them. Such a by-product (fond, pan sauce, broth, rendered fat) is a preparation with no parts of its own. Because it has no ingredients to answer for it, the check refuses it as an ingredient of a recipe and as a part of a dish or of another preparation: what a dish holds must always be found by following parts down to ingredients.

### 16. A preparation can stand in for something too (round 3)

- **Example:** clarified butter stands in for butter when searing, and not when mounting a sauce. This is the epic's own example, ghee for butter, and in this graph clarified butter is a preparation.
- **What did not fit:** only an ingredient could stand in for something.
- **Now:** a preparation has `stands_in_for`, with the same shape as an ingredient's.

### 17. A kind for a group of ingredients that behave alike (cycle two)

- **Example:** searing listed 21 single ingredients, and poaching 13.
- **What did not fit:** a list of ingredients is no knowledge. It is out of date with every new ingredient, and it does not say what the listed things have in common.
- **Now:** `graph/group/` holds groups, each with a sentence on what its members share and the wider group it sits within. An ingredient or a preparation says which `groups` it is in. A technique's `works_on` points at groups, and at no more than three single things. Searing works on steaks and chops, braising cuts, poultry, roasting joints and offal, and on salmon and the scallop. `ingredient/allium`, which no cook ever bought, became `group/alliums`.

### 18. `works_on` means one thing, and a step says what it is done with (cycle two)

- **Example:** the deglazing step of steak au poivre listed the fond and the cognac. Deglazing works on the fond, with the cognac.
- **What did not fit:** on a technique `works_on` was what the move is for. On a step it was everything the step handled, the fat and the salt included.
- **Now:** a step has `works_on` and `with`. What a step's technique works on must be something its card works on, directly or through a group. The rule found 14 steps on its first run. Ten were wrong steps and four were missing memberships: `docs/cycle-two.md` lists them.

### 19. The parts of a dish have ids, and a recipe line names its part (cycle two)

- **Example:** coq au vin had four parts called aromatic and two called liquid, so nothing could point at "the liquid".
- **What did not fit:** a part had a role and no name. A recipe could not say which part a line fills, and a part could not be left out.
- **Now:** a part has an `id` of its own within its dish (wine, stock) beside its `role`, and may be `optional`: the cheese of a gratin dauphinois is. A recipe line names the `part` it fills and must be one of its options. This replaces the older rule that a recipe uses nothing its dish does not name.

### 20. A dish a level is practised through is never held back (cycle two)

- **Example:** gratin dauphinois and the butter-basted pork chop fell into the held-back set, so two of Tomi's levels had no dish.
- **Decision, logged here as asked:** on 7 October 2026 the probes `dish-probe/gratin-dauphinois` and `dish-probe/butter-basted-pork-chop` moved to the growing set. In each of their batches the next probe in hash order that may be held back took the place: `dish-probe/gratin-de-courgettes` in `gratin-1` and `dish-probe/carre-d-agneau` in `roast-1`. In both batches the probes ranked just before them were passed over because their dishes were already written. Both replacements had been growing probes in cycle one, so their words were already answered when they became held back.
- **Now:** the held-back rule passes over a probe whose dish is already written or that a level is practised through, and the check refuses a held-back probe for a level's dish. Both dishes are written and their levels point at them.

### 21. A probe says who wrote it, and there is a second kind of probe (cycle two)

- **Example:** in cycle one a single model wrote the 120 probes and the graph, minutes apart.
- **Now:** a probe has `written_by`. The 120 old probes are stamped `claude-opus-5-5`, and the model that drafts the graph writes no more. One batch asks about a dish once, and another batch by another writer may ask again. `safety-probe` is a new kind: what a classic dish `holds` and what it `does_not_hold`, and `why`.

### 22. A kind for the page a fact was read in: source (cycle two)

- **Example:** the thirteen facts of the first slice were typed from Tomi's table. Mustard, celery, sulphites, lupin and molluscs were missing, and no file said where any list came from.
- **Now:** `source` is a kind: a page that was fetched, with its `title`, `publisher` and `url`, the day it was read (`read_on`), its `reuse` terms as stated there, a verdict on `commercial_use`, and what was `taken`. Twelve exist: eight pages of regulators and four open databases that were looked at and not imported.

### 23. A fact says what it concerns and where it is regulated (cycle two)

- **Example:** the United States lists wheat and Europe lists cereals containing gluten. Japan lists shrimp and crab, Canada lists crustaceans and molluscs as one entry. One fact called shellfish and one called nuts could say none of that.
- **Now:** a fact has a `concern`, allergen or diet, and `regulated` rows: `where`, the `source`, the `name` used there, its `standing`, the `exemptions` stated there and a `note`.
- **The ids that changed.** The branch is not merged, so an id could still change. Every old id is logged here with what replaces it:

| Old id | What replaces it |
|---|---|
| `fact/nuts` | `fact/peanuts` and `fact/tree-nuts` |
| `fact/shellfish` | `fact/crustaceans` and `fact/molluscs` |
| `fact/dairy` | `fact/milk`, the name every list uses |
| `fact/gluten` | Kept. It now means the cereals that hold gluten, and `fact/wheat` stands beside it for the places that list wheat alone |

New ids: `fact/wheat`, `fact/celery`, `fact/mustard`, `fact/sulphites`, `fact/lupin` and `fact/buckwheat`. Unchanged: `fact/egg`, `fact/fish`, `fact/soy`, `fact/sesame`, and the five diet facts `fact/meat`, `fact/pork`, `fact/animal-product`, `fact/slaughter-product` and `fact/alcohol`.

### 24. What an ingredient holds says on what basis, and whether it is certain (cycle two)

- **Example:** butter holds milk because it is made from cream. Wine holds egg only because egg white may have been used to clear it. Both were one word in a list, and the reason sat in a note for the whole record.
- **Now:** each row of `contains` has the `fact`, a `basis` and `certain`. The owner rules on how strict to be and can do it reason by reason: `docs/strict-answers.md` lists every answer that is not certain, and the check keeps it equal to the files.

### 25. Sourced can be earned, by a fact (cycle two)

- **Example:** celery is entry 9 of Annex II of Regulation 1169/2011, read on 7 October 2026. That is more than a model's draft.
- **Now:** a `regulated` row may be sourced, because it names its source, and a fact with a sourced row may be sourced. The check still refuses sourced everywhere else, and every tier above it.

### 26. Words about a source or a probe are notes, not sentences (cycle two)

- **Example:** the European list counts sulphites from 10 mg/kg, a licence is called CC BY 4.0, and the reason of a safety probe is written by another model. The sentence rules, which keep numbers out of what a cook reads, refused all three.
- **Now:** the model has a note beside the sentence: `reuse`, `taken`, `exemptions`, the `note` of a regulated row and the `why` of a safety probe. A note may hold numbers. Nothing a cook reads is a note. A source also has a date and a web address, each with a shape of its own.

### 27. Probes for stand-ins and kitchens (the question cycle)

- **Example:** clarified butter can replace butter when frying, but cannot mount a sauce.
  A dish probe only tests whether words exist. It cannot test either contextual answer,
  or whether a kitchen can fill every required part of a recipe.
- **Now:** `stand-in-probe` and `kitchen-probe` live apart from the graph. Both have
  `id`, `tier`, `batch`, `set` and `written_by`. The existing hash rule holds back
  one in five within each kind and batch, with no exception for written recipes.
- **A stand-in-probe** has `recipe`, `ingredient`, `candidate`, `verdict` and `why`.
  These are independent names, not references that would force the graph to contain
  the answer. `verdict` takes `works`, `works-with-caveat` or `does-not-work` from
  `stand_in_verdicts`. `why` is the independent writer's note.
- **A kitchen-probe** has `technique`, `at_home`, `dishes` and `why`. Names again,
  with every pantry item explicit and at least one expected dish or preparation.
- **What counts:** the commands answer a stand-in probe only through an applicable
  part option or direct statement, with a caveat when required, or an explicit
  `not_when` for a negative. Absence never proves a negative. `works` accepts a
  recorded caveat; `works-with-caveat` requires one. If an ingredient occurs more
  than once, a positive must work for every line. A kitchen probe is answered when
  every expected dish has a recipe using the named technique with no missing
  required part. It measures recall of the expected dishes, not whether every
  returned recipe deserves a cook's approval. Optional parts do not score.
- **Recipe variations:** a named recipe is tried first. If it does not use the
  probe's original, one uniquely matching recipe for the same dish or preparation
  may answer. For example, the existing hollandaise uses whole butter; a separate
  clarified-butter recipe answers a question that names clarified butter. Several
  matching variants are ambiguous and do not answer. The query command itself
  continues to take one explicit recipe. An explicit recipe id in a probe is
  binding too and never selects another variation.
- **Independence:** the question-cycle writer is `gpt-6-luna`, with no access to
  `graph/` or previous probes. The graph drafter is a different model. Held-back
  questions and gaps are counted by code and never shown to the drafter.

### 28. A negative statement does not imply a positive elsewhere (the question cycle)

- **Example:** yogurt is not a substitute for cream in the hot egg-yolk liaison of
  blanquette. The model could only record `when: []` and a `not_when`. But an empty
  `when` meant a universal positive everywhere outside that prohibition.
- **Now:** a stand-in statement has `allows`. Existing positives are `true`.
  An exclusion-only statement is `false`, has an empty `when` and a nonempty
  `not_when`. It supplies no positive answer in any other context. The checker
  tests both constraints. Matching prohibitions always take precedence.
- **Query context:** the recipe's dish or preparation, and the technique and
  preparations a relevant step works on, uses or makes. An unrelated step
  cannot enable a stand-in. A test proves intermediate preparations count too.
- **No promotion:** changing the shape or adding a prohibition earns no tier.
  All these statements remain drafted, awaiting a cook's judgment.

### 29. A dish probe says which cuisine it asks about (new cuisines)

- **Example:** a weeknight chicken with couscous. The only program is French, and `written_for` had to name one of its skills, so no probe could be written for a Moroccan, Japanese or Indian dish. A slice is also judged on its own probes, and a share pooled over every cuisine would hide a new one behind French.
- **Now:** `dish-probe` has a `cuisine`, the slug of a `cuisine` of the graph, written after `written_by`. A probe for a cuisine that is not in the graph is refused. `written_for` names a skill of a program of that cuisine. A cuisine with no program yet has no skills to name, so its probes name any topic, such as rice or grilling, and they name a skill once the cuisine has a program. The 215 existing probes are `french`. `./probe` reports the probes answered for each cuisine and `./probe --cuisine japanese` runs one alone. The cuisines `japanese`, `indian` and `moroccan` are in the graph as bare names, drafted, so that probes can point at them.
- **Not yet:** a step probe is still not a kind of the model. Cuisine names in their own script need languages beyond `en` and `fr`, and that list is closed.
- **No promotion:** nothing is above drafted. A cuisine node carries no knowledge and no reviewer is named.

## Decisions where the starting model was silent

These are not changes. The starting model names kinds and statements, not files, so the first files had to settle them.

- **A statement is a field of the thing it starts from,** named after the statement and holding one row per thing it points at: `{"thing": ..., "tier": ...}`, with whatever the statement adds (`why`, `differs`, `when`).
- **Every field is always written.** An empty list is `[]`. `null` is allowed only where the model says so.
- **Names are one name per language tag,** English required. A name in another script brings its romanization under `<tag>-Latn`. Other names are `aliases`, by language.
- **"Is the same move as" is not a statement.** The same move under another name is one technique with two names. What differs makes it a variant: `variant_of` with `differs`.
- **Nothing is above drafted, and no safety record is verified, until a review can be put on record.** The epic asks for who, when and against what on every tier. No such record exists yet, so the check refuses any tier above drafted. That rule goes when the record comes.
- **A number is `{"value", "unit"}` or `{"from", "to", "unit"}`,** with the unit from the closed list the field names.
- **A stand-in names its context** as `when` and `not_when`: techniques, preparations or dishes. With `allows: true`, an empty `when` means no context is known to matter. With `allows: false`, only the listed exclusions are asserted.
- **Ids of public datasets are not built.** Nothing in this slice came from one.
- **Probes are files too,** outside the graph, in `probes/`. A probe has a batch and a set. Which probes of a batch are held back follows from their ids by a rule in `tools/probes.py`. Nobody picks.

## What the model cannot express yet

Each of these came up while writing real content. They are listed with the example in `docs/rounds/`. `docs/night-one.md` gives a default for each.

- A number that defines a technique, such as how long a soft egg boils.
- A proportion that defines a preparation, such as the equal weights of a roux.
- Doneness. The temperatures are safety facts and wait for a person.
- A need that holds only for some food, such as vinegar when poaching an egg.
- A cooking aid that stays in the pot, such as the vinegar of poaching water.
- A helper that is not what the move works on, such as the egg white that clears a consommé.
- One thing a cook either buys or makes, such as chicken stock.
- A leftover: a dish that starts from what another dish leaves.
- What a dish is served with.
- Time that is waiting, time per side, two heats in one step, a step that runs while another runs, and a choice between the stove and the oven.
- Keeping a sauce warm, which is neither cooling nor keeping.
- The French sauter of meat, which has no technique of its own.
- Diets and avoid items, which the safety probe will need.
- A fact inside a fact. Japan names walnut and cashew, Australia each tree nut by name, the United States the species of a fish. The fact is the class, and the finer entry sits in the `name` of a row.
- What a list recommends for a food that has no fact: orange, kiwi fruit, beef, chicken, banana, peach, yam, apple and gelatin in Japan.
- A level. Every list counts sulphites from a set level, and an ingredient can only hold the fact or not.
- An exemption that fits one ingredient. Europe exempts the isinglass that clears wine, and the wine cannot point at that row.
- A word of a probe that covers several facts, such as shellfish.
- Ids of public datasets. Nothing here came from one.
