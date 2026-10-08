# Loop hour one: ticks

Issue [5](https://github.com/mrspacerobot/cooking-graph/issues/5). An autonomous hour on the branch, started at 20:51 UTC. Everything is tier `drafted`. No pull request, nothing on `main`.

## Baseline (start of the hour)

463 of 1648 recipe lines with a swap offered; 103 lines where a technique card names a swap not offered; 672 narrow rows; 291 foods in no stand-in row. Compose probes 1 of 32 growing, 0 of 8 held back. Stand-in probes 12 of 52 growing, 2 of 13 held back.

## Tick 1: a clean held-back set

A second compose batch, `compose-2`, 40 questions written by `claude-opus-5-5` from its own knowledge, told not to read the repository. The hash rule held back 8. Installing it and running `./probe reset-sets` moved 6 probes whose dishes already exist (by rule, a written dish is never held back). Only counts were printed; no compose-2 content has been read by the drafter. Compose probes now: 1 of 64 growing, 0 of 16 held back.

## Tick 2: swap round two

45 of the widest card-named pairs went to two blind drafters, who wrote 44 and 33 rows. `./stand-in-merge` kept 25, disputed 8 and left 5 single-drafter pairs. Six agreed rows were not applied: the exclusions of cognac and red wine vinegar as replacements for wine or water in `deglaze`. They contradict the `deglaze` card, which lists both as options, and both drafters' caveats say a splash works. 19 rows were applied.

| | Before | After |
|---|---|---|
| Recipe lines with a swap offered | 463 | 475 |
| Lines with a card-named swap not offered | 103 | 91 |
| Foods in no stand-in row | 291 | 290 |

## Doubts so far

- Plain yogurt for lemon juice in a spice paste, and the stock-for-water rows in braise and grain cooking, are moderate-confidence calls that two drafters of one model agreed on.
- Eight pairs the drafters wrote against each other (for example butter for olive oil) wait for a person.
- Every ratio is from memory.

## Tick 3: content for the growing compose-2 gaps

Three worktree agents wrote 9 dishes with recipes (arancini, suppli, arroz con pollo, crema catalana, fish molee, Kerala fish curry, masoor dal, plain paratha, vegetable biryani), 5 technique cards (shape a stuffed rice ball, fry rice balls, burn a sugar crust, fold a paratha, cook a paratha; each a variant with a "differs" sentence) and 2 foods (fish sauce, green curry paste). `./merge` copied 25 files and refused none; `./twins` shows only the two old pairs. Shish taouk was drafted and deleted because the checker reported a held-back probe asks for it (4 files, not restored). Gazpacho, imam bayildi and oyakodon were left out for the same reason, and the Thai dishes wait for a decision on a new cuisine.

Small data fixes from the agents' change requests: chicken breast joins the poultry group, red lentil joins the pulses group (so the redundant single entry on `simmer` was dropped), and pork chop gains the alias pork loin chop. Not done on purpose: widening `grill` to poultry, `cook-on-dum` to vegetables, and `cook-pilaf`, which are card decisions for a reviewer.

| | Before the hour | After tick 3 |
|---|---|---|
| Dishes / recipes / techniques | 169 / 188 / 278 | 178 / 197 / 283 |
| Recipe lines with a swap offered | 463 of 1648 | 522 of 1782 |
| Foods in no stand-in row | 291 | 292 |
| Compose probes, growing / held back | 1 of 32 / 0 of 8 | 1 of 64 / 0 of 16 |

Compose did not move again. On the growing compose-2 questions, with pantry words that do not match exactly dropped, the first blocker is a generic technique the best recipe does not name in 17 of 32 (saute, simmer, pan-fry, toast, soak, boil, whisk, puree and similar), a dish absent in 5, a pantry shortfall in 8 and no recipe using the techniques in 2. The dishes are there; their steps use more specific technique names that are not linked to the general ones.
