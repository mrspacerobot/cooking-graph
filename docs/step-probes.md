# Step probes: a design

Status: a design only. No code, no graph file, no probe and no model change comes with it. Written for the owner to rule on, and for the person who builds it.

## Why

The epic asks that at least 95% of a slice's held-back dish and step probes can be expressed. Only dish probes exist. A dish probe asks whether the graph has a name for the techniques and the ingredients of a dish. It never asks whether a step of a real method meets a technique card that works on that food. A step probe asks that, with no model and no recipe in the graph.

I tried the idea on the real graph with a throwaway script outside the repository. "Deglaze the fond with white wine" and "sweat the onion in butter" are expressed. "Sear chicken thigh in oil" fails on the word oil. "Temper mustard seed in ghee" fails on the technique. So the probe finds real gaps, and some are only naming gaps.

## 1. What a step probe says

A new kind `step-probe`, kept in `probes/step-probe/<slug>.json`. The id is `step-probe/<dish-slug>-<position>`. One probe is one move of one method.

| Field | Type | What it holds |
|---|---|---|
| `id`, `tier`, `batch`, `set`, `written_by`, `cuisine`, `written_for` | as on a dish probe | `tier` is drafted. `set` is from `probe_sets`. `cuisine` is a slug of a cuisine of the graph. `written_for` is a skill of a program of that cuisine, or any topic slug while the cuisine has no program (change 29) |
| `dish` | label | The dish the method is for, in plain words. It need not be in the graph |
| `also_called` | list of labels | Other names of the dish, as on a dish probe |
| `position` | integer, at least 1 | Where the move stands in the writer's method of the dish |
| `step` | note | The step in the writer's own words. Never matched by code. It is for the human who reads a gap, and may hold numbers. It is never text copied from a book |
| `technique` | label | One cook word for the one move, such as sear or fold. Not a list |
| `works_on` | list of labels, at least 1 | The foods the move acts on, by their common names. No group word, no cut word: onion, not diced onion |
| `with` | list of labels | The fat, the salt or the liquid it is done with. May be empty |
| `cue` | object or null | `sense` from the closed list `senses`, and `text` as a note: how the writer says a cook can tell the move is right |

Closed: `tier`, `set`, `sense`, and `cuisine` (it must exist). Free labels: `dish`, `technique`, every object and every `with`. They are the writer's words and the whole point is that the graph meets them as they come. Fields are written in this order, all always, `[]` and `null` where nothing is said.

## 2. How code answers it, with no model

The code is the same plain lookup the dish probe uses: `names.plain` on the label, against every name and alias of a thing, in every language.

1. **Technique.** Find the techniques whose plain names include the label. No match is the gap `no-technique`. Names are unique inside a kind, so there is at most one.
2. **Food.** For each object, find the ingredients and preparations that go by the label. No match is the gap `no-food`. A buy-or-make pair (stock, broth) gives two; either may answer. By-products such as fond are preparations, so a method that works on the fond finds it.
3. **Card.** `group_rules.members_of_groups` and `group_rules.worked_on` already give everything a card works on, directly or through a group and the wider groups. An object whose food is not in that set is the gap `not-worked-on`. This is the check `not-what-the-technique-works-on` already makes on a recipe step. The probe makes it on a step the graph has never seen.
4. **With.** Each `with` label must go by an ingredient or a preparation. A missing one is `no-food`. It is not tested against the card: `needs` lists some options, not all, and a miss would be noise.
5. **Cue.** If `cue` is not null, the card must have a cue of that sense. A miss is the gap `no-cue`.

**Expressed** means: the technique exists, and every object exists, and the card works on every object, and every `with` exists. The cue is counted apart and never decides it. A step with two objects needs both. This is one yes or no per probe, as for a dish probe.

Absence never proves anything. A step is only expressed or not expressed. "Expressed" does not mean "right" (section 5).

The runner, `tools/step_probes.py`, mirrors `tools/probes.py`:

- `run(things, batch, cuisine)` gives growing and held-back answers apart.
- Counts per set: probes expressed, technique words found, food words found, and technique-and-food pairs the card covers. Counts name no word, so they may be shown for held back.
- Growing gaps are listed, most wanted first, each with the dish and position: `no-technique: temper (Tarka dal 2)`, `not-worked-on: sweat on spinach, card works on alliums, root vegetables`. The card's groups are graph content, not a probe, so they may be named.
- **Held back: counted, never listed.** No word, no dish, no position, no gap kind is printed for a held-back probe. The gap kind is a count only when it is a total over all held-back probes (`3 held back not expressed`), never split by kind, because a split of a small set points at one probe.

## 3. The checker rules, and the test for each

Held back by the hash of the id, one in five of a batch, with `probes.held_back_ids`, like the others. `step-probe` joins `PROBE_KINDS`. For a step probe, `never` is the probes whose dish is already written as a dish, a recipe or a preparation: such a method meets the graph's own steps and says nothing about steps unseen. The written dish is passed over, as for a dish probe.

| Rule | What it refuses | Test: break this file, expect this rule |
|---|---|---|
| held-back-rule (existing, extended) | A `set` the hash does not give | Move a held-back step probe to growing, and a growing one to held back |
| cuisine-unknown, skill-unknown (existing, extended) | A cuisine not in the graph. A topic that is no skill of a program of that cuisine | Set `cuisine` to `narnian`. Set `written_for` to `frying` for a French probe. A cuisine with no program names any topic |
| same-step-twice (new) | Two probes with one plain dish name (or alias) and one `position` in a batch | Copy a probe under a new slug in the same batch. The same step in another batch, by another writer, passes |
| method-has-a-gap (new) | A dish whose positions in a batch do not run 1, 2, 3 and so on with no hole. Stops a writer from keeping only the easy steps | Delete position 2 of a three-step method |
| two-moves-in-one-step (new) | A `technique` label with `and`, a comma or a slash, which is two moves | Set `technique` to `sear and deglaze` |
| drafter-wrote-probe (new) | A `written_by` listed in `drafters`, a new list in `schema/words.json` that names the models that drafted the graph. A vocabulary change, not a model change | Set `written_by` to the drafter |
| drafted-towards-held-back (existing, extended) | A dish, recipe or preparation that carries the dish name of a held-back step probe | Give a dish the name of a held-back step probe |
| not-in-the-model-document (existing) | `docs/model.md` not naming `step-probe` and each of its fields | Remove the section |

The shape rules of `schema/model.json` already refuse an unknown or missing field, a bad `sense`, an empty label and a `position` below 1. Each gets one test in `tests/test_check.py` through `SmallKitchen.break_file`. The small kitchen gets a `step_probe_files()` beside `safety_probe_files()`, with a method of three steps in a batch of five, so that exactly one is held back.

Tests for the runner go in a new `tests/test_step_probes.py`, in the style of `tests/test_probes.py`: expressed; `no-technique`; `no-food`; `not-worked-on` through a group, through a wider group, and for a single thing the card names; a buy-or-make pair; a by-product as object; the cue counted apart; and that the report of a run with a held-back probe holds none of its words, its dish or its gap.

## 4. How a writer who cannot see `graph/` produces them

The writer is a model or a person that is not in `drafters`, with no access to `graph/` or to growing gaps. It is given: the cuisine, a list of topics (the skill slugs of the program, or plain topics such as rice and grilling), and this brief.

- Pick well-known dishes of the cuisine for each topic. Write the method in your own words, 5 to 9 steps, **one move per step**. Do not copy a book or a site.
- Per step: the cook word for the move, the foods it acts on by their common names, what it is done with, and, if you can, one cue.
- Name the usual food: olive oil, not oil, if you know which is used. Write the whole food, never a cut or a state.
- If the move has a local name, put it in `step`. Keep the label for the nearest plain cook word.
- Do not guess what the graph holds. Never list a technique to fit a list.

**How many.** Held back is a fifth. The bar is 95%, so with 20 held back one miss passes and two fail, and with 60 held back and no miss the true rate is still only shown to be above about 95% by the rule of three. A bar read on 5 probes means nothing.

- A first read: 150 probes per cuisine, so 30 held back.
- A claim against the bar: 300 per cuisine, so 60 held back. Below 20 held back, `./numbers` prints the share and says it is not read against the bar.
- Per topic or skill: at least 12 probes from at least 4 dishes, so a topic share is not one dish.
- Every technique that the cuisine's program teaches is asked by at least 2 probes with different objects. No dish has more than 10 probes. `./probe steps` prints the dishes, the topics and the distinct technique words per batch, counts only, so a thin batch is seen at once.
- Dish and step probes are reported apart and never pooled, as cuisines already are.

## 5. What it cannot test

A step probe measures **vocabulary and scope**: a name for the move, a name for the food, and a card whose `works_on` reaches that food. It does not test:

- Doneness, or any time or temperature. Those are safety facts and wait for a person.
- The right amount, or a ratio.
- Whether the move gives the result the cook wants, or whether the card's `how` is good.
- Whether the card is true for this food. `works_on` says the card is meant for the group, not that it was tried.
- The order of steps, `comes_after`, the equipment, or the fit of `with` to the move.
- A regional move. A writer's nearest plain word may match the French cousin, and the probe is then expressed while a local difference is flattened. A match is not a proof of the local name.
- Anything about a cook. No step probe is evidence for a tier above drafted.

So a share of 95% reads as "the graph meets 95% of unseen steps in words". It does not read as "95% of cooks get it right". The held-back share can also be optimistic: a step of a held-back probe may belong to a dish whose other steps are growing. `./probe steps` therefore prints the held-back count apart for dishes with no growing sibling, counts only.

## 6. One worked example, and the build plan

```json
{
  "id": "step-probe/chicken-piccata-4",
  "tier": "drafted",
  "batch": "steps-italian-1",
  "set": "growing",
  "written_by": "another-writer",
  "cuisine": "italian",
  "written_for": "pan-sauces",
  "dish": "Chicken piccata",
  "also_called": ["piccata di pollo"],
  "position": 4,
  "step": "Pour the wine into the hot pan and scrape up the browned bits.",
  "technique": "deglaze",
  "works_on": ["fond"],
  "with": ["white wine"],
  "cue": {"sense": "hear", "text": "A sharp hiss when the wine hits the pan."}
}
```

On today's graph this is expressed: `technique/deglaze` works on `preparation/fond`, `ingredient/white-wine` exists, and the card has a hear cue. The `set` is shown as growing for the example only. In a real batch the hash decides, and `chicken-piccata` is not written.

**Build, in order. Each stage ends with `./check` passing.**

1. **Model.** Change 31 in `docs/model.md`: the kind `step-probe`, a section in "The kinds", the forcing example (a dish probe cannot see a step), the rules in the table of rules, and "Not yet" for what section 5 lists. `schema/model.json` gets the kind and `schema/words.json` the list `drafters`. Shape tests first.
2. **Rules.** `tools/probe_rules.py`: add `step-probe` to `PROBE_KINDS`, to the cuisine and skill rules, and to the drafted-towards rule. Add `same-step-twice`, `method-has-a-gap`, `two-moves-in-one-step`, `drafter-wrote-probe`. A failing test for each before the rule.
3. **Runner.** `tools/step_probes.py` with the lookups of section 2, reusing `probes.name_index`, `group_rules.members_of_groups` and `worked_on`. Tests first.
4. **Command.** `./probe steps [batch] [--cuisine c]`, in the style of `./probe questions`. Report as in section 2.
5. **Numbers.** `./numbers` gains a table: step probes by cuisine and set, expressed of total, the word counts, and the line that says whether the held-back count is large enough to read.
6. **Fixture and docs.** Small-kitchen step probes. `docs/question-cycle.md` and the epic's stopping-rule table report dish and step apart.
7. **First batch.** 150 probes per cuisine by a writer outside `drafters`, French first because it has a program. Commit the batch, close it, run `./probe steps`, and only then draft against the growing gaps.

## Open questions for the owner, each with a default

| Question | Default |
|---|---|
| Hold back by probe or by dish? By dish is more honest (a whole unseen method), by probe is the rule everywhere else | By probe, with the sibling count in section 5. Change if the sibling count shows a gap |
| A generic word such as oil, wine or flour | A gap. The graph adds a generic ingredient or an alias only if a person agrees it is one thing. No alias is made to please a held-back probe |
| A writer's label for a local move | The nearest plain cook word in `technique`, the local name in `step`. Matching a French cousin is accepted and named as a limit |
| Is a step probe for a dish already written passed over? | Yes, like a dish probe |
| Who is in `drafters`? | Every model that drafted graph content, which I cannot list from the files: the 120 old probes name `claude-opus-5-5`, but the files do not say which models drafted the graph. The owner names them |
| Should `with` be checked against `needs` of the card? | No, for noise. Revisit once `needs` lists every option |
| A move that leaves something behind (the fond of a sear)? | Not asked in this version. A `makes` field can be added later |
| Which bar for steps if the first read is far under 95%? | Report it, do not move the bar. Same as dish probes |

What I could not decide: whether the 95% in the epic means dish and step probes pooled or each alone (I report each alone); whether 300 probes per cuisine is affordable; and how to compare a vocabulary share across cuisines with and without a program.
