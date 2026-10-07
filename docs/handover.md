# Handover: where the cooking graph stands

Written on 7 October 2026 for an agent or a person picking this up cold. Read `AGENTS.md` first. Its rules apply to you.

## What the owner wants next

Added later on 7 October 2026. The owner's concern is the graph itself, not the app. The graph must answer three questions:

1. **For this recipe, what can stand in for this ingredient,** and what must not?
2. **For this technique, which recipes practise it?**
3. **For this technique and what I have at home, which recipes can I make,** with which stand-ins, and what is missing?

Where the graph stands on them today, counted from the files:

| | Count |
|---|---|
| Parts of dishes | 479 |
| Parts that offer more than one option | 46 |
| Statements that one thing stands in for another | 11 |
| Recipe lines, and those that name the part they fill | 564, 564 |
| Recipe steps, and distinct techniques they use | 401, 57 |
| Dishes that say which techniques they teach | 65 of 65 |

So question 2 can already be worked out from the files. Questions 1 and 3 have their shape (parts with options, lines that name their part) but little knowledge behind them, and no command answers any of the three.

**What to do, in this order. It comes before the leftovers of cycle two below.**

1. **Three commands,** tests first, standard library only, no model involved, the same input always giving the same output:
   - the stand-ins for a recipe: for each line, the other options of its part and whatever stands in for the ingredient, with the context, the ratio and the caveat where the graph has them. Asked to avoid a fact, it leaves out what holds it, and always says the safety records are unverified;
   - the recipes for a technique: those whose steps use it, the ones whose dish teaches it first;
   - what to cook for a technique with what is at home: the recipes ranked by how little is missing, and for each part the option the cook has, the stand-in, or "missing".
2. **Probes for these questions, written by another model** than the one that drafts, with one in five held back as always:
   - stand-in probes: a recipe, an ingredient, a candidate, and whether it works, works with a caveat, or does not, and why;
   - kitchen probes: a technique, what is at home, and the dishes a good cook would make of it.
3. **A cycle on stand-ins.** Run the probes, list the gaps, and draft what is missing: more options on the parts of dishes, statements that one thing stands in for another with its context, ratio and caveat, and statements that something does not stand in where a cook would wrongly assume it does. A stand-in gives the same result by the same technique in about the same time. If the method changes, it is another recipe, not a stand-in.
4. **Numbers for it:** the share of parts with more than one option, and the share of each kind of probe answered, the held-back ones apart.

## Where things are

- Branch `1-first-slice`, draft pull request 1 into `main`. Everything is pushed and nothing is merged.
- `./check` passes: 841 files read strictly, no issue.
- The plan is the epic mrspacerobot/tomi#106. This work is its first story, mrspacerobot/tomi#119. The next story is mrspacerobot/tomi#120: the stack, the checks, agents and the backlog.
- What to read: `docs/night-one.md` (the first cycle), `docs/rounds/` (one note per round), `docs/model.md` (the model and every change to it, each with the example that forced it).

## What exists

| Kind | Count |
|---|---|
| Techniques | 80 |
| Ingredients | 171 |
| Groups of ingredients that behave alike | 42 |
| Preparations | 30 |
| Dishes | 65 |
| Recipes | 77 |
| Facts (allergens and diet facts) | 21, of which 16 are sourced |
| Sources | 12 |
| Forms, equipment, cuisines, program | 39, 42, 6, 1 |
| Dish probes | 215: 120 by the drafting model, 95 by another model |
| Safety probes | 40, by the other model |

Everything is tier `drafted`, except the 16 allergen facts taken from a regulator's page that was fetched. All 171 safety records are `unverified`. Nothing here may be shown to a cook or exported.

## Cycle two: what was asked, and how far it got

The owner asked for four fixes to the model, a better allergen list from real sources, and one more cycle on fresh probes written by another model. The work stopped part way because the usage limit of the agent ran out, not because of a problem.

| Item | State | Where |
|---|---|---|
| A technique works on groups, a recipe step splits what it works on from what it is done with, and the check holds each step against its technique's card | Done | `docs/rounds/cycle-two-part-1.md` |
| Parts of a dish have ids, and a recipe line names its part | Done | same |
| A dish that a program level is practised through is never held back. The two missing dishes are written | Done | same |
| Probes written by another model, which could not see `graph/` | Done | batches `fresh-1`, `fresh-2`, `fresh-3`, `safety-1`, all `written_by` `claude-sonnet-5-5` |
| The allergen facts rebuilt from regulators' pages, every ingredient answered again, each answer marked certain or strict | Done | `docs/rounds/cycle-two-part-2.md`, `graph/source/`, `graph/fact/`, `docs/strict-answers.md` |
| The safety probe runner, and the list of disagreements | Done | `./safety`, `docs/safety-disagreements.md` |
| The first run of the fresh probes, before anything was drafted | Done | `docs/rounds/cycle-two-first-run.md` |
| Growth round on `fresh-1` | Done | `docs/rounds/cycle-two-round-1.md` |
| Growth round on `fresh-2` | Done | `docs/rounds/cycle-two-round-2.md` |
| Growth round on `fresh-3` | **Not done.** 7 of its 24 growing probes are answered | |
| The report `docs/cycle-two.md` | **Not written** | |
| The pull request's description | **Still describes the first cycle only** | |

## What is left, in order

1. **The round on `fresh-3`.** `./probe` lists what its growing probes lack: about five technique words and 22 ingredient words. Draft what is missing: techniques, ingredients, groups, preparations. Keep the volume down. A probe only needs its techniques and ingredients to exist. A full dish file with a recipe is written for at most two fresh dishes per skill in the whole cycle, so read the notes of rounds 1 and 2 for what each skill already got. Then `./check` clean, read ten of the new files again with fresh eyes and fix what is wrong, write `docs/rounds/cycle-two-round-3.md` like the earlier notes, commit and push.
2. **The report `docs/cycle-two.md`:** what changed in the model, the sources and what each allows, the numbers, each stopping rule with its measured value, what is doubtful, and the open questions, each with a default.
3. **The pull request's description,** brought up to date. It stays a draft.
4. **A comment on mrspacerobot/tomi#119** with the final numbers of the cycle.

## Rules that are easy to break

- **Never open a held-back probe file, and never draft towards one.** `./probe` and `./numbers` count them without showing them.
- **Whoever drafts the graph writes no probes.** The next probes come from someone else, and say who in `written_by`.
- **Tiers stay honest.** Drafted, unless it is an allergen fact taken from a regulator's page that you fetched yourself. Every safety record stays `unverified`: a person verifies.
- **A safety disagreement is never settled by editing either side.** They are for the owner.
- **No amount, time or temperature in a sentence,** and no claim that food is safe to eat.
- **Python standard library only.** Install nothing. No em dash anywhere.
- **Never push to `main`, never merge.** Commit subjects are in the imperative and end with `(mrspacerobot/tomi#119)`.

## The commands

| Command | What it does |
|---|---|
| `./check` | Runs the tests of the tools, then reads every file strictly and lists every issue |
| `./probe` | Runs the dish probes and lists what the graph lacks for the growing ones |
| `./safety` | Runs the safety probes against what the graph works out for each dish |
| `./numbers` | Counts by kind and tier, and the values the stopping rules ask for |
| `./tidy` | Rewrites files into the one written form the check expects |

`tools/drafting.py` holds helpers for writing many things from a short script.

## The stopping rules today

| Rule | Value | Bar | Met |
|---|---|---|---|
| Held-back technique words the graph knows | 126 of 128 (98%) | 95% | Yes |
| Held-back ingredient words the graph knows | 223 of 241 (93%) | 85% | Yes |
| Held-back dish probes answered in full | 26 of 42 (62%) | none set | |
| Safety probes that can be answered and agree | 8 of 19 growing | all, after a person rules | No |
| Reviewer rejects under 5%, everything at the customer's floor | no reviewer yet | | No |

Of the 11 safety disagreements among the growing probes, 10 rest on strict answers alone.

## Waiting for the owner

- A review of pull request 1.
- A ruling on how strict to be: 109 of the facts ingredients hold are certain and 116 are recorded strictly for want of knowing (`docs/strict-answers.md`).
- A ruling on each safety disagreement (`docs/safety-disagreements.md`).
- The stack (mrspacerobot/tomi#120).
- The app's own allergen list (mrspacerobot/tomi#123).
- A reviewer for Japanese and for Indian cooking, before those slices start.
