# Night one: the first slice

For the owner. Written at the end of one unattended night on mrspacerobot/tomi#119.

**Read this first:** a model wrote everything here and read it back to itself. No person, no second model and no kitchen has seen any of it. Every thing and every statement is tier drafted. Every safety record is unverified. Nothing may be shown to a cook or exported.

`./check` passes: 140 tests of the tools, then 569 files read strictly with no issue.

## What to open first

| Open | To judge |
|---|---|
| `graph/technique/sear.json` | A technique card: what it does, how in a few beats, what you see, hear and feel, the mistakes |
| `graph/technique/mount-with-butter.json` | A French move that keeps its name, and is a variant of emulsifying |
| `graph/dish/coq-au-vin.json`, then `graph/recipe/coq-au-vin.json` | A dish as parts and roles with options, and a recipe whose every step names one technique. Follow the fond: the sear leaves it, the deglaze works on it |
| `graph/recipe/seared-chicken-thighs-with-lemon-butter-pan-sauce.json` | Tomi's own lesson as the graph writes it. Compare with the lesson file. Note what the graph may not say: "cooked through" |
| `graph/ingredient/red-wine.json` beside `graph/ingredient/white-wine.json` | A safety record, and the first doubt below |
| `graph/preparation/clarified-butter.json` | The plan's own example: it stands in for butter when searing, not when mounting |
| `graph/program/french-foundations.json` | Tomi's 37 levels. Each names the techniques it teaches. Two have no dish, on purpose |
| `docs/model.md` | The model, and the 16 changes to the starting model with the example that forced each |
| `docs/rounds/round-1.md` to `round-4.md` | The numbers of each round, and what the model could not express |

Then run `./check`, `./probe` and `./numbers`.

## What was built

- **The home:** the model as a file (`schema/model.json`), a strict checker, a probe runner, the numbers, a tidier and drafting helpers. Python standard library only, tests written first.
- **The seed from Tomi:** the program with its 12 skills and 37 levels, the 13 safety facts, the 23 ingredients with exactly Tomi's facts, the 6 pieces of equipment, the dishes of the two lessons.
- **Four growth rounds,** three skills each, in the order of Tomi's catalog.

| Kind | All | drafted | above drafted |
|---|---|---|---|
| fact | 13 | 13 | 0 |
| cuisine | 6 | 6 | 0 |
| equipment | 40 | 40 | 0 |
| form | 37 | 37 | 0 |
| ingredient | 138 | 138 | 0 |
| technique | 64 | 64 | 0 |
| preparation | 28 | 28 | 0 |
| dish | 55 | 55 | 0 |
| recipe | 67 | 67 | 0 |
| program | 1 | 1 | 0 |
| all things of the graph | 449 | 449 | 0 |
| statements | 1543 | 1543 | 0 |
| dish-probe | 120 | 120 | 0 |

| Safety | Number |
|---|---|
| Safety records, one per ingredient | 138, all unverified |
| Facts recorded as held | 121 |
| Ingredients recorded as holding none of the 13 facts | 59. That is a claim too, and it is unverified |
| Safety points in recipe steps that wait for a verified fact | 55, in 44 of the 67 recipes: doneness 27, raw or lightly cooked egg 15, cooling and keeping 10, raw meat or fish 3 |

| Dish probes | Answered | Share | Technique words | Ingredient words |
|---|---|---|---|---|
| growing | 96 of 96 | 100% | 297 of 297 | 581 of 581 |
| held-back | 15 of 24 | 62% | 65 of 66 | 120 of 131 |

## The rounds

| Round | Skills | New growing probes answered at first run | New technique words | Per 50 probes | New ingredient words | Changes to the model | Held-back share after |
|---|---|---|---|---|---|---|---|
| 0 | the seed | | | | | 6 | |
| 1 | knife cuts, eggs, stocks | 0 of 24 | 27 | 56 | 54 | 8 | 1 of 6 (17%) |
| 2 | sauté, sear, poach | 3 of 24 | 11 | 23 | 26 | 1 | 6 of 12 (50%) |
| 3 | roux, pan sauces, emulsions | 9 of 24 | 4 | 8 | 19 | 1 | 9 of 18 (50%) |
| 4 | braise, roast, gratin | 3 of 24 | 6 | 12.5 | 14 | 0 | 15 of 24 (62%) |

Techniques drafted per round: 39, 12, 6, 7. Things drafted for each growing probe newly answered: 7.8, 4.0, 4.5, 3.0.

## The stopping rules, each with its measured value

**The rule of this story:** stop when all 12 skills are covered and a full round needed no change to the model, or after six rounds. All 12 are covered. Round 4 changed neither `schema/model.json` nor `schema/words.json`. The growth stopped after four rounds.

**The rules of mrspacerobot/tomi#106 for a slice.** None is met. That is the honest state after one night.

| Rule | Measured | Met |
|---|---|---|
| At least 95% of the held-back dish and step probes can be expressed | 62% of held-back dish probes: 15 of 24. No step probe was written | No |
| Fewer than one new technique per 50 fresh probes, three batches running | 56, 23, 8, then 12.5 per 50 | No |
| Reviewers reject fewer than 5% of the rows they sample | No reviewer. The writer's own reread found 6 files wrong in 42 | Not measured |
| Every safety probe passes, and every safety fact in the export is verified | No safety probe was written. 0 of 138 safety records are verified | No |
| Everything in the export is at the customer's floor | Tomi's floor is reviewed. 0 of 449 things and 0 of 1543 statements are there. There is no export | No |
| Pause when three rounds bring no gain on the held-back probes | 17%, 50%, 50%, 62%. One round without gain, not three | Not triggered |
| Pause when the cost of a newly answered probe passes the budget | No budget was set. 3 to 8 things drafted for each newly answered probe | Not measured |

Two things about these numbers matter more than the numbers.

- **The held-back probes fail on ingredients, not on techniques.** 65 of their 66 technique words have a name in the graph. 11 of their 131 ingredient words do not, and one missing word fails a whole probe. This is what the plan predicted: techniques run out, dishes never do. The 95% rule, as written, counts probes, so it mostly measures ingredients.
- **The second rule has not had a fair test.** Every batch here was the first batch of three new skills, so each was bound to find new moves. The rule needs fresh probes on skills already covered. No such batch was written.

## How it was checked

- **By code, on every file:** shape, ids, references, tiers, closed word lists, the safety rules, the recipe rules, names, the held-back rule, and every sentence for numbers, units and claims. `docs/model.md` lists the rules.
- **By code, once, with scratch scripts that are not kept:** techniques no recipe uses, forms no technique makes, ingredients nothing points at, recipes that hold meat without a doneness point. This found two missing recipes, three missing safety points and a handful of missing links. They were fixed. One more audit looked for anything that is in the graph only because a held-back probe names it: a technique, an ingredient or a preparation that no growing probe asks for and nothing else points at. It found none.
- **By the writer rereading:** 42 files in the four rounds, 6 fixed. Then all 138 safety records in one pass, 5 made stricter. Then the steps of the 40 recipes not yet read back: one was wrong (the pot-au-feu poached four marrow bones in a ladleful of broth), three poaching times did not say when they start, and two yields did not add up. All were fixed. Every recipe but three has now been read back once, by the one who wrote it.
- **Not checked at all:** whether any recipe works. Whether a French name is the one a French cook would use. Whether a cue is what you really see. Whether a dish belongs where it is said to belong.

## What I doubt most

1. **One model wrote the probes and the graph, minutes apart.** The held-back rule stops a dish being written towards a probe, and the check enforces it. It cannot stop the two from sharing one vocabulary and one set of blind spots. The held-back share is honest about ingredients and flattering about wording.
2. **The safety records.** The meaning of each fact is my reading of Tomi's table. Where strictness stops is a judgment I made alone: red wine holds egg and dairy from fining, wine vinegar does not. Vinegar, capers, cornichons and mustard hold alcohol. Sugar holds a slaughter product because of bone char. Cured pork holds dairy. A reviewer may undo half of these and add others.
3. **The fact list is too short for France.** Mustard, celery and sulphites must be declared in the European Union and are in these recipes every day. The graph has no fact for them. Three ingredients say so in their note. No fact was added: a person should.
4. **Two seed rows I kept and do not trust.** White wine records no egg, dairy or fish, though fining can leave them. Soy sauce records no alcohol, though brewing leaves some. Tomi's facts were kept as told.
5. **The recipes are untested.** Amounts and times are from memory. Doneness is left to "a trusted guide" in 27 steps, because the graph may not give it.
6. **`works_on` means two things.** On a technique it is what the move is for. On a step it is everything the step handles, the fat and the salt included. A query that joins the two will mislead.
7. **Where a technique ends.** 64 techniques. Some are thin: plate, season, layer, toss. Some are nearly small recipes: make a roux, roll an omelette, boil an egg. And the French sauter of meat has no card at all: poulet sauté chasseur is written as sear, deglaze and simmer.
8. **The French names.** 365 of 449 things have one, from memory. Some are guesses a French cook would wince at: "mélanger" for toss, "fondant" for fork-tender, "quadriller" for score.
9. **The choice of dishes.** The probes are my list of well-known dishes. Several are plain cooking rather than named dishes: green beans with garlic, roast potatoes, roasted root vegetables. The two seed dishes are Tomi's lessons, not classics.
10. **By-products.** Fond, pan sauce, broth, rendered fat, poaching liquid, braising liquid and jus are preparations with no parts. It works and the check keeps them out of dishes. It may want a kind of its own.

## Open questions, each with a default

| Question | Default |
|---|---|
| Who adds mustard, celery, sulphites and the other missing facts | A person, before any export. The check then demands an answer from every ingredient |
| Does vinegar hold alcohol | Yes, as recorded, until a person rules |
| Do the doubted seed rows change (white wine, soy sauce) | They stay. A person decides. Red wine is recorded stricter meanwhile |
| Is sugar a slaughter product | Yes, as recorded. Add beet sugar as its own ingredient once verified, as Tomi does with vegetarian hard cheese |
| Where do doneness temperatures live | In a safety table of their own, verified by a person, which a safety point refers to. Nothing until then |
| Where do the numbers that define a technique live (how long a soft egg boils) | A list of named numbers on the technique. Never one that is a safety fact |
| How does a preparation hold its proportions (a roux is equal weights) | A ratio on a part |
| Can a part be left out | Add `optional` to a part |
| Can a need hold only for some food (vinegar for poaching an egg) | Add a list to a need: for what |
| Is bought chicken stock the same thing as the stock a cook makes | No. Two things, and the bought one stands in for the made one. Look again when open data arrives |
| Does an ingredient keep `forms` | Remove it. It is empty on all 138. Forms found their place on recipe lines |
| Do by-products get a kind of their own | Not yet. Add where one comes from if an export needs the facts of a single step |
| Does a step split what it works on from what it works with | Yes, in the schema story. It would end doubt 6 |
| When may a tier rise | When the evidence record exists: who, when, against what. Until then the check refuses it |
| May a held-back probe ever be written | Not silently. Gratin dauphinois and the butter-basted pork chop are held back, so two of Tomi's levels have no dish. Default: move one to the growing set only by a logged decision, and hold a fresh one back in its place |
| Is 95% of held-back probes the right bar | Split it: 95% of technique words (98% today), and a lower bar for ingredient words, which never run out |
| Who writes the probes of the next slice | Not the model that drafts the graph. A reviewer, or another model, and before the drafting starts |
| How does the French sauter enter | As a technique of its own, a variant of searing, once a reviewer who knows it says what differs |
| Amounts in cups | The export does it, from a density per ingredient that the graph does not hold yet |
| Diets and avoid items | A kind of their own, with the first safety probes |
| The stack (mrspacerobot/tomi#120) | Nothing here forces one. What worked: the model as one data file that the checker reads, so a change to the model is one diff. One file per thing. A check that runs in about a second |

## What happened that should be known

- **Nothing was merged.** The work is on the branch `1-first-slice`, in a draft pull request.
- **Limits kept:** no network but git and gh, nothing installed, no other agents, no change in the Tomi repository.
- **One slip:** early in the night one scratch file, the output of `./numbers`, was written to the system's temporary folder, outside the clone. It was deleted at once.
- **How the content was typed:** through `tools/drafting.py`, from scratch scripts in the ignored `out/` folder. The scripts are not kept. The JSON files are the only source.
- **Tools added that the story did not ask for:** `./tidy` and the rule that a file is written one way, the drafting helpers, the rule that `docs/model.md` names every kind and field, and the count of words answered. Each has tests.
- **One commit message is wrong by one:** "Draft what the probes of round 1 lack" says 59 ingredients. It was 58.
