# Cycle two, part 3: the fresh probes at first run

Written on 7 October 2026, before anything was drafted for them. These are the numbers of the graph as it stood at the end of part 2, against probes written by another model that could not see `graph/`.

## What arrived

The branch `2-fresh-probes` brought 135 probe files, all stamped `claude-sonnet-5-5`:

| Batch | Kind | Probes | Held back by the rule |
|---|---|---|---|
| fresh-1 | dish probes | 33 | 6 |
| fresh-2 | dish probes | 32 | 6 |
| fresh-3 | dish probes | 30 | 6 |
| safety-1 | safety probes | 40 | 8 |

Each batch of dish probes spans the twelve skills.

**How they were made to pass the check without being read.** The files had `written_for` before `written_by`. A script put the fields of the 95 dish probes in the order of the model and changed nothing else. The sets the other writer had given agree with the rule in all four batches, so no set was changed. No fresh probe asks about a dish, a recipe or a preparation that was already written, and none asks about a dish that a held-back probe of cycle one asks about. No held-back file was opened: every script printed counts only.

One rule was widened first, with its test: a probe is never held back when its dish is already written as a preparation or a recipe, and not only as a dish. Until then the rule and the check disagreed about what counts as written.

## The dish probes, as they are

| Batch | Probes | Answered | Share | New technique words | per 50 probes | New ingredient words | per 50 probes |
|---|---|---|---|---|---|---|---|
| fresh-1 | 33 | 10 | 30% | 10 | 15.2 | 22 | 33.3 |
| fresh-2 | 32 | 8 | 25% | 11 | 17.2 | 26 | 40.6 |
| fresh-3 | 30 | 8 | 27% | 8 | 13.3 | 28 | 46.7 |
| all three | 95 | 26 | 27% | 22 | 11.6 | 62 | 32.6 |

A new word is a technique or ingredient word that the graph has no name for. It is counted once in a batch, whoever asks for it, the held-back probes included. The last row counts a word once across the three batches.

By word:

| Batch | Technique words known | Ingredient words known |
|---|---|---|
| fresh-1 | 101 of 112 (90.2%) | 169 of 194 (87.1%) |
| fresh-2 | 99 of 111 (89.2%) | 153 of 181 (84.5%) |
| fresh-3 | 88 of 97 (90.7%) | 136 of 165 (82.4%) |

The held-back probes, which the graph was never grown against:

| Held-back probes | Answered | Technique words known | Ingredient words known |
|---|---|---|---|
| The 24 of cycle one | 15 of 24 | 65 of 66 (98.5%) | 122 of 133 (91.7%) |
| The 18 fresh ones | 5 of 18 | 57 of 62 (91.9%) | 92 of 108 (85.2%) |
| All 42 | 20 of 42 | 122 of 128 (95.3%) | 214 of 241 (88.8%) |

**What this says.** Cycle one ended with every growing probe answered and a held-back technique share of 98.5%. Against probes by another writer the graph answers a little over a quarter, knows about nine technique words in ten and about seventeen ingredient words in twenty, and meets a new technique word about every four probes. The numbers of cycle one were flattered by one model writing both sides, as the owner suspected.

## The safety probes, as they are

| Set | Probes | Answerable | Agreeing | Disagreeing | Of which on strict answers alone |
|---|---|---|---|---|---|
| growing | 32 | 12 | 4 | 8 | 8 |
| held-back | 8 | 2 | 1 | 1 | 1 |

A probe is answerable when its dish is in the graph with a recipe: 14 of the 40. Every word of the growing probes names a fact.

All eight growing disagreements are of one kind: the probe says the dish does not hold egg, fish or milk, and the graph holds it only because wine, wine vinegar or Dijon mustard may have been cleared with egg white, isinglass or milk protein. `docs/safety-disagreements.md` has both sides of each. None was settled: the page that was fetched exempts only isinglass and fish gelatine, in Europe, and how strict to be is for the owner to rule.
