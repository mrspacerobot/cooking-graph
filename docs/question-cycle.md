# The three questions: first cycle

Written on 7 October 2026 for the owner. The four next steps in
`docs/handover.md` were done in order, before the unfinished cycle-two round.
The work stays on `1-first-slice`, in draft pull request 1. Nothing is merged.

## What to open first

- `./stand-ins recipe/sole-meuniere --avoid fact/milk`: other options, contextual
  statements and exclusions, preserving recorded ratios, caveats and tiers.
- `./recipes technique/sear`: recipes whose steps use the move, teaching dishes
  first, with ids breaking ties.
- `./kitchen technique/sear ingredient/scallop ingredient/olive-oil ingredient/butter ingredient/lemon ingredient/salt`:
  recipes ranked by missing required parts, with an available original, option,
  stand-in or missing result for each line and part.
- `docs/rounds/question-cycle-first-run.md`, then `question-cycle-round-1.md`:
  baseline, growing gaps, the draft, reread and independent check.

The commands use the Python standard library only. They call no model, install
nothing and always return the same JSON for the same files and input. They
refuse a broken repository, unknown input and ambiguous names. Every answer
states that safety records are unverified. Avoidance rejects strict `contains`
answers and unanswered facts, following all preparation options conservatively.

## What changed

Three question commands were tested first. A separate blind model, `gpt-6-luna`,
wrote 25 stand-in and 30 kitchen questions, with the existing hash rule holding
back one in five within each kind and batch. No held-back question or gap was
opened by the graph drafter. The broad first kitchen batch remains in the test;
a focused second batch asks for one concrete move at a time.

One growth round added six ingredients, one dish, three recipes and seventeen
contextual statements. Parts gained explicit alternatives, including melting
cheeses, herbs, aromatics, acids and cooking fats. `allows: false` expresses
negative knowledge without implying a substitute works elsewhere. These model
changes and their forcing examples are in `docs/model.md`.

The graph is now 596 things, with 1,964 statements. All new things and statements
are drafted. The sixteen sourced allergen facts and their source records are
inherited unchanged. No page was re-fetched or newly sourced this cycle, and no
open dataset was imported. Reuse permissions are the recorded source metadata,
not a fresh licence audit. All 177 safety records remain unverified, with 113
certain answers and 119 strict answers. The generated strict-answer document was
regenerated through its command; no safety disagreement was settled.

## Measured results

| Measure | Before | After |
|---|---|---|
| Dish parts with multiple options | 46 / 479 (9.6%) | 56 / 485 (11.5%) |
| All dish and preparation parts with multiple options | 58 / 579 (10.0%) | 69 / 585 (11.8%) |
| Growing stand-in questions answered | 0 / 20 | 11 / 20 (55%) |
| Held-back stand-in questions answered | 0 / 5 | 0 / 5 |
| Growing kitchen questions answered | 1 / 24 | 8 / 24 (33.3%) |
| Held-back kitchen questions answered | 1 / 6 | 1 / 6 (16.7%) |

The growing stand-in set has one disagreement and eight other unanswered
questions. The kitchen set has sixteen unanswered growing questions. The
focused kitchen batch is 8 / 12 growing and 1 / 3 held-back; the broad batch
is 0 / 12 growing and 0 / 3 held-back. No held-back share improved, so this
round provides no evidence yet that the new knowledge generalizes.

## Each stopping rule

| Rule from mrspacerobot/tomi#106 | Measured value | State |
|---|---|---|
| At least 95% of held-back dish and step probes expressed | Dish probes 26 / 42 (61.9%); no independent step probes yet | Not met |
| Fewer than one new technique word per fifty probes, three fresh batches running | fresh-1: 0.0; fresh-2: 0.0; fresh-3: 8.3 | Not met |
| Reviewers reject under 5% of sampled rows | No cuisine reviewer or human sample | Unmeasured |
| Every safety probe passes, every exported safety record verified | 8 / 32 growing and 1 / 8 held-back agree; 0 / 177 records verified | Not met |
| Everything in an export at the customer's floor | No reviewed content and no export | Not met |
| Pause after three rounds with no held-back gain | One question growth round, with no gain | Threshold not reached |
| Pause when cost per newly answered probe exceeds budget | No budget specified | Unmeasured |

The older handover's technique-word and ingredient-word bars remain 126 / 128
(98.4%, above 95%) and 223 / 241 (92.5%, above 85%). They measure words, not
working recipes or contextual substitutions. They do not replace the epic's
full-probe rule. This requested cycle is complete; the slice is not.

## What was checked and what is doubtful

`./check` passes: 253 tests, 906 files read strictly, no issue. Command-line
checks compare repeated JSON and exercise real graph recipes. Logic tests
cover context precedence, exclusion-only rows, strict avoidance, unresolved
facts, preparation cycles, recipe ranking, optional and expanded parts, names,
probe schemas, hash assignment and held-back output secrecy.

Ten new content files were reread. Independent model `gpt-6-sol` reviewed the
tools and changed graph content without opening probes. Its concrete findings
were corrected with tests: oil was wrongly offered for a cold-butter mounted
sauce, explicit probe ids could select another variation, and unsuitable pepper
and parsley forms were accepted as interchangeable names. The mayonnaise
variation's copied vinegar text was also corrected. This is a model check,
not a cook's approval.

The culinary doubts still need the owner or a cuisine reviewer:

- Milk for cream in gratin dauphinois: the probe says it works with a caveat,
  while the new statement says this method needs a different reduction or
  thickening. Neither side is treated as authoritative.
- The aubergine-free, courgette-heavy ratatouille option changes the classic
  mixture and its creamy texture. The difference is now stated; whether to
  retain the familiar dish name needs review.
- Cheese age, oil flavour, acid strength and small-shallot size affect the
  proposed stand-ins. Recorded ratios have not been tested in a kitchen.
- Many original kitchen probes ask about families rather than one move, or
  omit ingredients from their expected recipe. These are independent draft
  expectations, not verified reference answers.
- Bakery recipes, several recipe variations, missing names and form-specific
  pantry items are still gaps. No alias was manufactured to erase a difference.

Kitchen matching means ingredient presence. It does not check quantities,
equipment or all starting forms. It does not skip a recorded make-a-roux step
because the pantry holds a prepared roux; that path needs its own variation.
Preparations are checked through every option, so avoidance can reject a
particular preparation more strictly than a fully specified batch would need.
These commands are internal exploration only and are not an export to cooks.

## Open questions, each with a default

| Question | Default |
|---|---|
| Which proposed sensory changes still count as the same result? | Keep claims drafted; require a cuisine review before product use |
| Is milk alone a same-method stand-in in this gratin? | Keep the disagreement visible; do not promote either answer |
| Should courgette-only ratatouille be another named dish? | Keep the variation explicit and await the cuisine reviewer |
| How should a kitchen describe prepared components and starting forms? | Separate recipe variations; no automatic step rewriting or form conversion |
| Should family-level kitchen queries return several moves? | Design that separately; do not alias a family to one technique |
| How strict should the ingredient answers be? | Keep strict avoidance until the owner rules from the existing ledger |
| What held-back question share should finish this track? | Set a bar after broader independent probes; current results do not justify shipping |

The remaining cycle-two work is unchanged: `fresh-3`, its report and the
associated issue update still wait. The new priority was completed first.

## Full counts from ./numbers

| Kind | All | drafted | sourced | reviewed | verified | cook-tested |
| --- | --- | --- | --- | --- | --- | --- |
| source | 12 | 12 | 0 | 0 | 0 | 0 |
| fact | 21 | 5 | 16 | 0 | 0 | 0 |
| cuisine | 6 | 6 | 0 | 0 | 0 | 0 |
| equipment | 42 | 42 | 0 | 0 | 0 | 0 |
| form | 39 | 39 | 0 | 0 | 0 | 0 |
| group | 42 | 42 | 0 | 0 | 0 | 0 |
| ingredient | 177 | 177 | 0 | 0 | 0 | 0 |
| technique | 80 | 80 | 0 | 0 | 0 | 0 |
| preparation | 30 | 30 | 0 | 0 | 0 | 0 |
| dish | 66 | 66 | 0 | 0 | 0 | 0 |
| recipe | 80 | 80 | 0 | 0 | 0 | 0 |
| program | 1 | 1 | 0 | 0 | 0 | 0 |
| dish-probe | 215 | 215 | 0 | 0 | 0 | 0 |
| safety-probe | 40 | 40 | 0 | 0 | 0 | 0 |
| stand-in-probe | 25 | 25 | 0 | 0 | 0 | 0 |
| kitchen-probe | 30 | 30 | 0 | 0 | 0 | 0 |
| all things of the graph | 596 | 580 | 16 | 0 | 0 | 0 |
| statements | 1964 | 1888 | 76 | 0 | 0 | 0 |

| Safety records | All | unverified | verified |
| --- | --- | --- | --- |
| ingredients | 177 | 177 | 0 |

Facts ingredients hold: 113 certain, 119 recorded strictly for want of knowing

| Dish probes | Answered | Share | Technique words | Ingredient words |
| --- | --- | --- | --- | --- |
| growing | 156 of 173 | 90% | 552 of 555 | 992 of 1011 |
| held-back | 26 of 42 | 62% | 126 of 128 | 223 of 241 |

| Batch | Probes | Growing answered | Held back answered | New technique words | per 50 probes | New ingredient words | per 50 probes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| braise-1 | 10 | 8 of 8 | 1 of 2 | 0 | 0.0 | 1 | 5.0 |
| eggs-1 | 10 | 8 of 8 | 2 of 2 | 0 | 0.0 | 0 | 0.0 |
| emulsions-1 | 10 | 8 of 8 | 2 of 2 | 0 | 0.0 | 0 | 0.0 |
| fresh-1 | 33 | 27 of 27 | 2 of 6 | 0 | 0.0 | 4 | 6.1 |
| fresh-2 | 32 | 26 of 26 | 4 of 6 | 0 | 0.0 | 2 | 3.1 |
| fresh-3 | 30 | 7 of 24 | 2 of 6 | 5 | 8.3 | 22 | 36.7 |
| gratin-1 | 10 | 8 of 8 | 2 of 2 | 0 | 0.0 | 0 | 0.0 |
| knife-cuts-1 | 10 | 8 of 8 | 1 of 2 | 0 | 0.0 | 1 | 5.0 |
| pan-sauce-1 | 10 | 8 of 8 | 0 of 2 | 0 | 0.0 | 2 | 10.0 |
| poach-1 | 10 | 8 of 8 | 0 of 2 | 0 | 0.0 | 3 | 15.0 |
| roast-1 | 10 | 8 of 8 | 2 of 2 | 0 | 0.0 | 0 | 0.0 |
| roux-1 | 10 | 8 of 8 | 2 of 2 | 0 | 0.0 | 0 | 0.0 |
| saute-1 | 10 | 8 of 8 | 2 of 2 | 0 | 0.0 | 0 | 0.0 |
| sear-1 | 10 | 8 of 8 | 2 of 2 | 0 | 0.0 | 0 | 0.0 |
| stocks-1 | 10 | 8 of 8 | 2 of 2 | 0 | 0.0 | 0 | 0.0 |

Levels of the programs that name a technique: 37 of 37
Recipe steps: 410
Safety points in recipe steps that wait for a verified fact: 72
Parts with more than one option: 69 of 585 (12%)
Dish parts with more than one option: 56 of 485 (12%)
Preparation parts with more than one option: 13 of 100 (13%)
Stand-in statements: 24 positive, 4 exclusion-only

| Question probes | Set | Answered |
|---|---|---|
| stand-in-probe | growing | 11 of 20 (55%) |
| stand-in-probe | held-back | 0 of 5 (0%) |
| kitchen-probe | growing | 8 of 24 (33%) |
| kitchen-probe | held-back | 1 of 6 (17%) |

| Safety probes | Agreeing | Answerable | Disagreeing |
|---|---|---|---|
| growing | 8 of 32 (25%) | 19 | 11 |
| held-back | 1 of 8 (12%) | 2 | 1 |
