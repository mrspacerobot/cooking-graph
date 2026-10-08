# Swap gaps, round one: fats, stocks, wine and acids

Issue [5](https://github.com/mrspacerobot/cooking-graph/issues/5). Everything here is tier `drafted`. No cook has tried a swap, and no ratio has been tested.

## Why

Asked for butter chicken with no butter, `./compose` found no stand-in: the ghee row covered only hollandaise and oil had none. `./swap-gaps` (new) showed the gap is wide. Of 1522 recipe lines, 174 had a swap that a technique card names and the graph does not offer, and a further 545 had a swap row whose context never matched.

## What was done

- Butter chicken first, by hand: ghee and oil for butter at `technique/fry-masala-base`, with tests on the real graph (commit 7ab1296).
- `./swap-gaps` listed the pairs most recipes share. The 45 biggest card-named pairs became one batch (fats, water and stocks, wine, acids).
- Two blind drafters wrote rows for the batch, each in a separate worktree, told not to read `probes/`, `docs/rounds/` or each other's work. They wrote 32 and 33 rows and skipped 13 and 12 pairs.
- `./stand-in-merge` kept 32 rows: 0 disputed, 1 pair only one drafter wrote (white wine for chicken-stock), not applied. All 32 were applied by a script that appends rows and skips exact duplicates. All are allowing rows; 14 carry `not_when` contexts where the swap fails.
- Technique cards were treated as a hint and never as a licence: the pairs the drafters skipped include cognac, red wine vinegar and water for white wine.

## Numbers

| | Before | After |
|---|---|---|
| Recipe lines with a swap offered | 344 of 1522 | 428 of 1522 |
| Lines where a technique card names a swap not offered | 174 (116 pairs) | 95 (95 pairs) |
| Lines with a row whose context never matches | 545 | 620 (some moved here from the line above) |
| Foods in no stand-in row | 295 | 294 |
| Stand-in statements, positive | 286 | 320 |
| Stand-in probes, growing | 12 of 52 | 12 of 52 |
| Stand-in probes, held back | 1 of 13 | 2 of 13 |

The held-back movement is one probe. The drafters never saw a probe, but one probe is not evidence that the swaps generalise.

## Doubts

- Agreement between two drafters of one model is not truth. They agreed on 32 of 32 pairs they both wrote, which is more than chance would give; the common-knowledge pairs are likely right, the rest need a cook.
- Wine for water at deglaze (white and red) and water for court-bouillon at poach make the result richer or plainer and are judgment calls.
- Three stock-for-white-wine rows and one stock-for-chicken-stock row carry a 1:1 volume ratio from memory. Ghee for oil also carries 1:1 by volume, and ghee for butter 1:1 by weight.
- Several `when` lists are broad technique sweeps (stock for water, honey for sugar, the fat-for-fat rows). A reviewer who knows the cuisines should look.
- Rows allow swaps that move allergens and alcohol (milk, cream, wine). The safety facts follow the ingredients and are unchanged, and `--avoid` still applies.
- 95 card-named gaps and 295 foods with no row remain.
