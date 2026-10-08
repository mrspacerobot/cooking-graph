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
