# Handover: where the cooking graph stands

Written on 7 October 2026 for an agent or a person picking this up cold. Read `AGENTS.md` first. Its rules apply to you.

## Current status and next steps

- [PR 1](https://github.com/mrspacerobot/cooking-graph/pull/1) (the first slice, `1-first-slice`) was merged by the owner on 7 October 2026 as an internal draft baseline, and [issue 3](https://github.com/mrspacerobot/cooking-graph/issues/3) is closed. The cycle-two follow-up is on the branch `claude/modest-clarke-n2wbsf`, with no pull request yet. The owner reviews and merges; an agent never merges. The merge did not promote any tier, verify safety records or permit an export.
- Completed: the first graph slice, strict checker and schema; the question commands, independent probes and one stand-in growth round; the standalone interactive browser viewer. `./view` builds the current working files and opens the browser. See `README.md` for a fresh clone.
- Current validation: `./check` passes 287 tests and reads 1651 files strictly. Content remains drafted except for the inherited sourced facts; all 427 ingredient safety records are unverified.
- Cycle two is finished on its branch ([issue 5](https://github.com/mrspacerobot/cooking-graph/issues/5)): the `fresh-3` round is done (`docs/rounds/cycle-two-round-3.md`) and the report is `docs/cycle-two.md`. All 173 growing dish probes are answered; the held-back dish probes are 29 of 42. The branch awaits the owner's decision on a pull request, and the final numbers await a comment on issue 5. No dish was written for the held-back probes, and Jambon persillé has its words but no dish.
- The new cuisines now have drafted words and two dishes each, and still no reviewer and no program. A dish probe names its cuisine (change 29). `cuisine/mediterranean` is a parent of Italian, Greek, Spanish, Lebanese, Turkish and Moroccan. Probes (30 each, 42 for French fresh-4) were written by `claude-fable-5-1`. Round 1 drafted 232 ingredients, 119 techniques and 16 dishes with recipes through agents and `./merge`: see `docs/rounds/new-cuisines-round-1.md`. All 399 growing dish probes are answered; held-back are 61 of 98. Everything is drafted and unverified, and the amounts are from memory. Moroccan has the weeknight chicken with instant couscous ([issue 8](https://github.com/mrspacerobot/cooking-graph/issues/8)).
- Round two of the new cuisines (`docs/rounds/new-cuisines-round-2.md`): the limit of two dishes per cuisine was lifted to eight; 64 more dishes and 67 recipes were drafted across nine cuisines (156 dishes, 174 recipes now). The held-back share did not move (61 of 98). Do not restore dishes that agents deleted after the checker told them a held-back probe asks for them.
- Guards against duplicates (change 30): `./check` refuses an ingredient and a preparation with one name, `./twins` lists likely duplicates (read every pair), and `./merge <checkout>` copies only new files from another checkout and refuses clashes. Use it when agents work in separate checkouts, and create the checkouts from the current commit. The checker no longer prints the name or path of a held-back probe: a wrong set is a count per batch, and `./probe reset-sets` puts the sets right and prints a count. `drafted-towards-held-back` still tells a drafter that a dish it wrote is asked by a held-back probe, which is one bit per dish it tries; the owner may want it moved to the merge step.
- Design notes, nothing built: `docs/review-record.md` (blocks every tier above drafted), `docs/step-probes.md`, `docs/stack-options.md`, `docs/backlog-draft.md`, and `docs/serving-plan.md` (how a read-only API could serve the Tomi iOS app; nothing built, the older Tomi plan is described from the owner's summary and unverified).
- Open-data skeleton, first run (`docs/rounds/open-data-skeleton-first-run.md`): 320 things carry a sourced Wikidata id in `same_as`, with plain names in Spanish, Italian, Turkish and French. `./wikidata --dry-run` repeats the match and prints every skip; a name read and found wrong goes in `schema/wikidata-refused.json`. The things stay drafted.
- **How to review (stage one of the review record is built).** A person who knows a cuisine reviews a card like this: add a `reviewer` file by hand in a pull request the owner merges (a slug such as `reviewer/french-1`, never a real name or an email); run `./review show technique/deglaze`; read the card; run `./review seal technique/deglaze` for the hash; write one `review` file for the session (`graph/review/<reviewer>-<topic>-<day>.json`, template in `docs/review-record.md`) with the hash in `seen`; then set `"tier": "reviewed"` on the card in the same pull request. `./check` then finds a live record by a reviewer who knows the cuisine with the right hash. Edit the card later and the tier falls (`review-stale`). No record exists yet. Verified, safety and samples are not built.
- Next is the owner's review, [issue 6](https://github.com/mrspacerobot/cooking-graph/issues/6): the disputed milk/cream exclusion, the courgette-heavy ratatouille option, strict ingredient answers and safety disagreements. The graph is not ready for export to cooks.
- Work tracking lives here: [epic 2](https://github.com/mrspacerobot/cooking-graph/issues/2), [first slice 3](https://github.com/mrspacerobot/cooking-graph/issues/3), and [repository setup 4](https://github.com/mrspacerobot/cooking-graph/issues/4). Issues 2 and 4 are open and issue 3 is closed. They were transferred from Tomi issues 106, 119 and 120 with their history, so a colleague needs access only to this repository. Issue 4 creates the later backlog and CI after the owner decides the stack.

`README.md` is the entry point and commands, `AGENTS.md` is the working rules,
this handover is the current progress and next work, `docs/question-cycle.md`
is the measured question report, and `docs/rounds/` keeps the history. Update
this current-status section when work finishes or priorities change.

The sections below retain the earlier cycle history. Old Tomi issue references
in past reports and commits are historical; current work uses issues 2, 3 and 4
here, with follow-ups 5 and 6. Reading the Tomi repository is not required to
continue this graph work. Issues 5 and 6 remain open when PR 1 closes issue 3.

## Update after the question cycle

The graph now has a standalone browser viewer. Run `./view` to build it from
the current checkout and open the default browser; no Lavish session or package
installation is needed. `README.md` has the clone-and-open instructions, and
`AGENTS.md` tells the next agent how to give a visual walkthrough. The viewer
is an internal review tool and includes no probe records.

The four steps in "What the owner wants next" have now been carried out, in
order, on `1-first-slice`. Read `docs/question-cycle.md` and
`docs/rounds/question-cycle-round-1.md` for current numbers, unresolved probes,
the independent review and the limits. Commands are `./stand-ins`, `./recipes`,
`./kitchen`, and `./probe questions`; `./numbers` now counts every probe kind.

The graph has 177 ingredients, 80 techniques, 66 dishes and 80 recipes, with
28 contextual statements (24 positive, 4 exclusion-only). Growing stand-in
questions answer 11 of 20; held-back 0 of 5. Growing kitchen questions answer
8 of 24; held-back 1 of 6. Dish parts with more than one option: 56 of 485.
`./check` passes 253 tests and reads 906 files strictly.

All 177 safety records remain unverified. No tier was promoted and no safety
disagreement was settled. No held-back file was opened by the graph drafter.
The pull request remains a draft and nothing was merged.

The original sections below describe the starting point and retained cycle-two
backlog. Its `fresh-3` round and `docs/cycle-two.md` remain outstanding under
issue 5; the new owner priority was completed first, as requested.

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

- Written before the merge: `1-first-slice` was then a draft pull request. It is merged now, and the current status is at the top.
- `./check` passed 841 files then; it reads 933 now.
- The plan is [epic 2](https://github.com/mrspacerobot/cooking-graph/issues/2). This work is [first slice 3](https://github.com/mrspacerobot/cooking-graph/issues/3). The next story is [repository setup 4](https://github.com/mrspacerobot/cooking-graph/issues/4): the stack, checks, agents and backlog.
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
| Growth round on `fresh-3` | Done. All 24 of its growing probes are answered | `docs/rounds/cycle-two-round-3.md` |
| The report `docs/cycle-two.md` | Done | `docs/cycle-two.md` |
| The pull request's description | Moot: PR 1 is merged. A new pull request waits for the owner | |

## What is left, in order

Issue 5 is finished on its branch. What remains of it:

1. **Post the final cycle numbers as a comment on [issue 5](https://github.com/mrspacerobot/cooking-graph/issues/5).** They are in `docs/cycle-two.md`. This is outward-facing, so the owner says when.
2. **A pull request for the branch,** only if the owner asks for one. Do not reuse PR 1: it is merged.
3. **Owner review,** [issue 6](https://github.com/mrspacerobot/cooking-graph/issues/6), then the stack and CI, [issue 4](https://github.com/mrspacerobot/cooking-graph/issues/4). The open questions, each with a default, are at the end of `docs/cycle-two.md`.

## Rules that are easy to break

- **Never open a held-back probe file, and never draft towards one.** `./probe` and `./numbers` count them without showing them.
- **Whoever drafts the graph writes no probes.** The next probes come from someone else, and say who in `written_by`.
- **Tiers stay honest.** Drafted, unless it is an allergen fact taken from a regulator's page that you fetched yourself. Every safety record stays `unverified`: a person verifies.
- **A safety disagreement is never settled by editing either side.** They are for the owner.
- **No amount, time or temperature in a sentence,** and no claim that food is safe to eat.
- **Python standard library only.** Install nothing. No em dash anywhere.
- **Never push to `main`, never merge.** Commit subjects are in the imperative and name the active issue: `(#3)` for the first slice, `(#5)` for the cycle-two follow-up. Earlier commits named the original Tomi issue; never rewrite them.

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
| Held-back ingredient words the graph knows | 226 of 241 (94%) | 85% | Yes |
| Held-back dish probes answered in full | 29 of 42 (69%) | 95% | No |
| Safety probes that can be answered and agree | 8 of 19 growing | all, after a person rules | No |
| Reviewer rejects under 5%, everything at the customer's floor | no reviewer yet | | No |

Of the 11 safety disagreements among the growing probes, 10 rest on strict answers alone.

## Waiting for the owner

- A decision on a pull request for the cycle-two branch, and a go-ahead to post the final numbers on issue 5.
- A ruling on how strict to be: 130 of the facts ingredients hold are certain and 140 are recorded strictly for want of knowing (`docs/strict-answers.md`).
- A ruling on each safety disagreement (`docs/safety-disagreements.md`).
- The stack ([issue 4](https://github.com/mrspacerobot/cooking-graph/issues/4)).
- The app's own allergen list remains the owner's separate app work; it does not block work on this repository.
- A reviewer for Japanese and for Indian cooking, before those slices start.
