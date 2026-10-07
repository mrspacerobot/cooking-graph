# New cuisines, round 2: up to eight more dishes each

Issue [8](https://github.com/mrspacerobot/cooking-graph/issues/8) is the roadmap this belongs to. Everything here is tier
`drafted`, written by agents that drafted from their own knowledge. Every safety record is `unverified`. No person has reviewed any of it.

## What was done

Nine agents, one per cuisine, each in its own worktree made from the same commit: French, Japanese, Indian, Italian, Greek, Spanish,
Lebanese, Turkish and Moroccan. The round-one limit of two dishes per cuisine was lifted to eight. The limit was a drafting guard in
the brief, not a rule of this repository. Each agent chose dishes by what they teach, read `./probe --cuisine <name>` for the words
growing probes still lack (it was empty for every cuisine, because round one had already drafted the words), and never opened `probes/`.

The work was merged with `./merge`, which refused nothing. Their small change requests were applied with a script (eleven changes:
six aliases, two group memberships and three links on technique cards). `./check` passes on all 1,900 files and `./twins` still lists only
the same two old pairs.

## What came in

| Kind | New | Now |
|---|---|---|
| dish | 64 | 156 |
| recipe | 67 | 174 |
| technique | 65 | 274 |
| preparation | 18 | 74 |
| equipment | 6 | 64 |
| ingredient | 2 | 429 |

Eleven existing files were changed by the requested edits. Every regional move keeps its own name as a technique with a `variant_of`
row that says what differs. No new group, no new cuisine node, no program.

## What the numbers say

- Growing dish probes whose dish is now written: 136 of 399, up from 81.
- Held-back dish probes expressed: 61 of 98 (62%), unchanged. The dishes drafted here do not move this number, because the words they
  needed were already there. The 95% bar is far off and these dishes were not aimed at it.
- Growing probes answered: 399 of 399. This only means every word has a name, not that the graph is right.

## What went wrong, plainly

- **The checker named held-back probes.** Four agents (Italian, Turkish, Moroccan and Indian) saw output that named held-back probe
  files or told them a dish they had drafted was asked by a held-back probe. Each deleted those dishes and what only they needed, and
  none of them is restored. Their names are not written here on purpose. Afterwards the checker was changed so that a wrong set is a
  count per batch and never a probe, and `./probe reset-sets` puts sets right and prints a count. One gap stays: `drafted-towards-held-back`
  still tells a drafter that a dish it wrote is asked by a held-back probe. That is one bit for each dish a drafter tries. The merge
  step may be a better home for it.
- **Two agents were stopped by an interruption** (Greek and Lebanese) with files half written and never checked. They were restarted as
  new agents, told to treat the earlier files as unvalidated, and removed several things that were too wide: aliases such as a bare
  "grilled sea bream", a tzatziki mention with no tzatziki in the graph, and a card that said "lean" about a fatty cut.
- **I told the owner those two were still running when they had stopped.** I had judged by files in their folders and not by whether they
  were alive.

## Doubts for a reviewer

- Several aliases were kept that may be wider than the dish (baba ghanoush as the tahini version, zenzai, onigiri, a few lemon-and-oil dressings).
- Turkish gozleme uses a yeast dough where many real gozleme doughs are unleavened.
- The Moroccan frying and tadouira cards work on wide groups (all stocks, all minced meats) and may not be true for every member.
- Indian `cook-on-dum` and `cook-in-masala-gravy` work on whole groups (poultry, braising cuts) and need a reviewer's eye.
- A new safety disagreement was found for the French béarnaise dish (the probe
  says no fish; the graph says fish on strict answers about wine and wine vinegar). It is in `docs/safety-disagreements.md` and awaits a ruling.
- All amounts, times and temperatures are model guesses. None has been cooked.
- Names that two cuisines may now hold twice (a garlic or tahini sauce, a rough aubergine mash, fried onions) were not flagged by `./twins`
  but have not been read side by side by a person.
