# Cycle two: the report

Written on 7 October 2026 for the owner, for [issue 5](https://github.com/mrspacerobot/cooking-graph/issues/5). Everything in the graph is a model's work, except the sixteen allergen facts taken from regulators' pages that were fetched. No person has reviewed any of it and no cook has tried a recipe. Every safety record is unverified. Nothing here may be shown to a cook or exported.

## What the owner asked, and where it is done

| Ask | Where |
|---|---|
| Four fixes to the model | `docs/rounds/cycle-two-part-1.md` |
| A better allergen list, from real sources | `docs/rounds/cycle-two-part-2.md` |
| Fresh probes by another model, run before anything was drafted | `docs/rounds/cycle-two-first-run.md` |
| Growth rounds on the three fresh batches | `docs/rounds/cycle-two-round-1.md`, `-round-2.md`, `-round-3.md` |

The question cycle (stand-ins, recipes for a technique, what to cook with what is at home) was done between rounds 2 and 3 at the owner's request. Its report is `docs/question-cycle.md`. Round 3 did not touch it.

## What changed in the model

Ten changes, numbered 17 to 26 in `docs/model.md`, each with the example that forced it. The question cycle added 27 and 28. Round 3 added none.

| Change | In a line |
|---|---|
| 17 A kind for a group of ingredients that behave alike | A technique names groups, not a list of ingredients |
| 18 `works_on` means one thing | A step says what it works on and what it is done with, and the check holds each step against its card |
| 19 Parts of a dish have ids | A recipe line names the part it fills |
| 20 A dish a level is practised through is never held back | No level is left without its dish by a hash |
| 21 A probe says who wrote it | The model that drafts writes no probes |
| 22 A kind for the page a fact was read in | `source`, with the day it was read and its reuse terms |
| 23 A fact says what it concerns and where it is regulated | Seven places, mandatory or recommended |
| 24 What an ingredient holds says on what basis, and whether it is certain | Strict answers are kept apart from certain ones |
| 25 Sourced can be earned, by a fact | A model alone never raises a tier above sourced |
| 26 Words about a source or a probe are notes, not sentences | The sentence rules apply to what a cook reads |

## The sources, and what each allows

Twelve `source` files. Each gives the page, the day it was read (all 7 October 2026) and the reuse terms as stated there.

| Source | Reuse for commercial use | What was taken |
|---|---|---|
| Food Standards Agency, United Kingdom | Allowed, with the source named | The names of the allergens |
| U.S. Food and Drug Administration | Allowed | The names of the allergens |
| Food Standards Australia New Zealand | Allowed | The names of the allergens |
| Consumer Affairs Agency, Japan | Allowed | The mandatory and recommended items, from the Japanese leaflet of April 2026 |
| Publications Office of the European Union, for Regulation 1169/2011 | Unclear | The 14 entries and their exemptions |
| Health Canada | Not allowed without written permission | The eleven priority allergens |
| Canadian Food Inspection Agency | Not allowed without written permission | Which cereals count as a gluten source |
| Codex Alimentarius, text of 2010 | Not allowed without written permission | Nine rows, at tier drafted, because only the old text could be read |
| FoodOn | Allowed (CC BY 4.0) | Nothing. Looked at, not imported |
| USDA FoodData Central | Allowed (CC0) | Nothing. It holds no allergen data |
| Wikidata | Allowed (CC0) | Nothing. No allergen property was found |
| Open Food Facts | Share-alike | Nothing. It is product data and share-alike |

Only the names of entries were taken, as facts, and no sentence was copied. **Four pages do not allow commercial use or leave it unclear** (Canada twice, Codex, the European Union). Their rows are in the graph. They have to be settled before anything is exported (see the open questions).

## The numbers

| | Earlier | Now |
|---|---|---|
| Things in the graph | 449 at night one | 623 |
| Statements | 1,543 at night one | 2,021 |
| Ingredients, every one answering all 21 facts | 138 | 195 |
| Facts held, certain and strict | 87 and 86 after part 2 | 130 and 140 |
| Safety records verified | 0 | 0 of 195 |

| Dish probes | At first run | Now |
|---|---|---|
| Fresh probes, all 95 | 26 answered (27%) | 87 answered (92%) |
| Fresh growing probes | 21 of 77 | 77 of 77 |
| Fresh held-back probes | 5 of 18 | 10 of 18 |
| All held-back probes, 42 | 20 | 29 (69%) |
| Held-back technique words known | 122 of 128 (95.3%) | 126 of 128 (98.4%) |
| Held-back ingredient words known | 214 of 241 (88.8%) | 226 of 241 (93.8%) |

| Batch | Probes | New technique words, per 50 probes | New ingredient words, per 50 probes |
|---|---|---|---|
| fresh-1 | 33 | 0.0 (was 15.2) | 3.0 (was 33.3) |
| fresh-2 | 32 | 0.0 (was 17.2) | 3.1 (was 40.6) |
| fresh-3 | 30 | 3.3 (was 13.3) | 6.7 (was 46.7) |

Safety probes: 19 of 32 growing probes are answerable, 8 agree and 11 disagree, 10 of them on strict answers alone. Held back: 2 answerable, 1 agreeing, 1 disagreeing. Round 3 added no answerable probe.

Held-back probes rose in every round: 20, 24, 26 and then 29 of 42. Some of that is ordinary overlap of kitchen words between batches. Nothing was drafted for a held-back probe, and what they lack was never listed.

## Each stopping rule, with its measured value

| Rule from the epic | Measured | State |
|---|---|---|
| At least 95% of held-back dish and step probes expressed | Dish probes 29 of 42 (69%). No step probes exist | Not met |
| Fewer than one new technique word per 50 probes, three batches running | fresh-1 0.0, fresh-2 0.0, fresh-3 3.3 | Not met. The two words left are asked only by held-back probes, which may not be drafted for |
| Reviewers reject under 5% of the rows they sample | No cuisine reviewer and no sample | Not measured |
| Every safety probe passes and every exported safety fact is verified | 8 of 32 growing agree. 0 of 195 records verified | Not met |
| Everything exported is at the customer's floor | Nothing is reviewed. There is no export | Not met |
| Pause after three rounds with no held-back gain | Held-back answers rose in each of the three rounds | Not reached |
| Pause when the cost of a newly answered probe passes the budget | No budget was set | Not measured |

The two older bars still hold: held-back technique words known 98.4% against a bar of 95%, and ingredient words 93.8% against 85%. They measure words, not working recipes or stand-ins, and do not replace the epic's rules above.

**What this says.** In cycle one the graph answered every growing probe and the held-back share looked high, because one model had written both sides. Against another writer it answered 27%. After three rounds it answers every growing probe of that writer, and the held-back probes it was never grown against moved from 20 to 29 of 42. The graph now knows nearly every word. What it does not yet do is answer the questions: stand-ins answer 11 of 20 growing and 0 of 5 held back, and kitchen questions 8 of 24 and 1 of 6. Words are not the limit any more. Knowledge about use is.

## What is doubtful

- **Every amount, time and temperature in a recipe is from memory.** No recipe was cooked.
- **Strict answers.** 140 of the 270 facts ingredients hold are recorded strictly because a common form may hold them. The rule of thumb is the drafter's own: a fact is strict when a common form, as sold, holds it, and a rare form is not chased. `docs/strict-answers.md` lists them.
- **Safety disagreements.** 11 growing and 1 held-back probes disagree with the graph. All but one growing disagreement rest on strict answers alone. None was settled.
- **Reuse terms.** The four pages above are used for names only. Whether names of entries on a regulator's list may be used commercially was not decided by a lawyer.
- **Groups.** A technique card is true for its group only if the card is true for every member. Three rounds each found a card that reached for the nearest group and was wider than it. The check cannot see this.
- **Chestnut and Roquefort.** The chestnut is recorded as a tree nut, strictly, though no page that was fetched names it. Roquefort holds gluten and wheat strictly, for the bread its mould is grown on, from memory.
- **Probes are drafts too.** The fresh probes come from another model. Their expected answers are not reference answers.
- **Strict reading of preparations.** The safety runner takes every option of every part, so a dish may be said to hold a fact that only one option of one part holds.

## Open questions, each with a default

| Question | Default |
|---|---|
| How strict should ingredient answers be? | Keep strict answers. The owner rules from `docs/strict-answers.md` |
| Which of the 12 safety disagreements stand? | None is settled. A person rules, or a fetched page does (issue 6) |
| May names from Health Canada, CFIA, Codex and the EU text be used commercially? | No. Leave those rows out of any export until the terms are confirmed or permission is given |
| Who is the French reviewer? | The owner, until a reviewer is found |
| How is a review put on record? | The check refuses any tier above drafted until a record of who, when and against what exists. Build it before any review starts |
| Are chestnut, Roquefort and gelatin right? | Keep them as they are, drafted and strict, until a person rules |
| Should courgette-only ratatouille be its own dish? | Keep the variant explicit and await the reviewer (issue 6) |
| Is milk a same-method stand-in for cream in a gratin? | Keep the disagreement visible (issue 6) |
| Should Jambon persillé, and the other dishes the probes name, be written? | No. Probes need only their words. Write a dish only for a skill with fewer than two |
| Should independent step probes be written? | Yes, by a writer who cannot see `graph/`, before the next cycle |
| What held-back share finishes the question track? | Set a bar after broader independent probes |
| Should a cooked-first food have a way to say it arrives cooked? | Design it separately. Do not add aliases |
| What next after this cycle? | Owner review (issue 6), then the repository stack (issue 4), then the review record, before a second cuisine |
