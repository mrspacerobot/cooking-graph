# New cuisines and fresh-4: the first run

Written on 7 October 2026, before anything was drafted for them. Everything here is about probes. No graph content was written for Japanese, Indian or Moroccan cooking, and no reviewer exists for any of the three.

## What was made

| Batch | Cuisine | Probes | Held back by the rule | Written by |
|---|---|---|---|---|
| fresh-4 | French | 42 | 8 | claude-fable-5-1 |
| japanese-1 | Japanese | 30 | 6 | claude-fable-5-1 |
| indian-1 | Indian | 30 | 6 | claude-fable-5-1 |
| moroccan-1 | Moroccan | 30 | 6 | claude-fable-5-1 |
| italian-1 | Italian | 30 | 6 | claude-fable-5-1 |
| greek-1 | Greek | 30 | 6 | claude-fable-5-1 |
| spanish-1 | Spanish | 30 | 6 | claude-fable-5-1 |
| lebanese-1 | Lebanese | 30 | 6 | claude-fable-5-1 |
| turkish-1 | Turkish | 30 | 6 | claude-fable-5-1 |

The model that drafts this graph in this cycle is `claude-sonnet-5-5`, and the three earlier fresh batches were also written by it. These four come from another model, as the rules ask.

The writers were told not to read `graph/` or anything else in the repository, and they wrote their files outside it. That is a rule given in words. Nothing stops an agent from opening a file, so the isolation is by instruction and cannot be shown.

Each of the Mediterranean batches was written for 30 dishes. Ten were first left out, because a name matched a probe of another cuisine: Shish taouk, Pollo alla cacciatora, Fakes, Arroz con leche, Piperrada, Sütlaç, İrmik helvası, Kuru fasulye, Lahana sarması and Zeytinyağlı yaprak sarma. Some are the same dish in two cuisines (rice pudding, stuffed leaves), and a cuisine's own version deserves its own probe, since one batch may ask a dish once but another batch may ask it again. They were put back before any drafting, because adding probes to a batch can change which of its probes are held back. Every Mediterranean batch is now 30, with 6 held back, and the numbers in the tables below are those at the time of the first run, before the ten went back in.

The cuisines became possible with change 29 in `docs/model.md`: a dish probe now names its cuisine, and a cuisine with no program yet takes any topic for `written_for`. The three cuisines are in the graph as bare drafted names.

## What the fresh-4 writer found

The first writer, who could not see what was taken, wrote 36 French dishes and **30 were already asked** by one of the 215 earlier probes. The well-known French dishes are used up. A second pass, given a plain list of the names already asked, wrote 36 more and none matched. The batch holds 6 of the first pass and 36 of the second.

The second pass was told to favour regional and less common dishes, so fresh-4 is a harder test than its predecessors. Its numbers do not compare directly with fresh-1 to fresh-3.

## The numbers

| Batch | Probes | Growing answered | Held back answered | New technique words | per 50 probes | New ingredient words | per 50 probes |
|---|---|---|---|---|---|---|---|
| fresh-4 | 42 | 7 of 34 | 0 of 8 | 25 | 29.8 | 45 | 53.6 |
| japanese-1 | 30 | 0 of 24 | 0 of 6 | 73 | 121.7 | 63 | 105.0 |
| indian-1 | 30 | 0 of 24 | 0 of 6 | 12 | 20.0 | 52 | 86.7 |
| moroccan-1 | 30 | 0 of 24 | 0 of 6 | 15 | 25.0 | 33 | 55.0 |

| Cuisine | Growing probes answered | Held back answered | Technique words known (growing) | Ingredient words known (growing) |
|---|---|---|---|---|
| French | 180 of 207 (87%) | 29 of 50 (58%) | 682 of 703 (97%) | 1205 of 1249 (96%) |
| Japanese | 0 of 24 | 0 of 6 | 47 of 134 (35%) | 83 of 192 (43%) |
| Indian | 0 of 24 | 0 of 6 | 58 of 89 (65%) | 63 of 187 (34%) |
| Moroccan | 0 of 24 | 0 of 6 | 60 of 80 (75%) | 96 of 172 (56%) |

**French.** The held-back share fell from 29 of 42 (69%) to 29 of 50 (58%), because eight new held-back probes are unanswered. This is the harder test, not a loss. The 27 unanswered growing probes of fresh-4 lack 18 technique words and 35 ingredient words, such as scale, gut, core, wrap, make a duxelles, vinegar, caper, hake and conger eel. Most are plain kitchen words.

**Japanese.** The graph knows about a third of the technique words. The most asked for are make dashi (ten dishes), stir fry, cover with a drop lid, cook rice and wash rice.

**Indian and Moroccan.** The most asked for are temper spices in hot fat (eight dishes), pressure cook, knead, roll and grind for Indian, and knead, grind, proof and steam couscous for Moroccan.

## The Mediterranean cuisines

`cuisine/mediterranean` is a parent. Italian, Greek, Spanish, Lebanese, Turkish and Moroccan sit within it, each with its own probes. No probe belongs to the parent, so the numbers below are for each cuisine and are never pooled.

| Cuisine | Probes | Growing answered | Held back answered | Technique words known (growing) | Ingredient words known (growing) | New technique words per 50 probes | New ingredient words per 50 probes |
|---|---|---|---|---|---|---|---|
| Italian | 29 | 1 of 24 | 0 of 5 | 57 of 106 (54%) | 120 of 175 (69%) | 58.6 | 84.5 |
| Greek | 29 | 1 of 24 | 0 of 5 | 64 of 89 (72%) | 125 of 175 (71%) | 27.6 | 46.6 |
| Spanish | 28 | 0 of 23 | 0 of 5 | 65 of 85 (76%) | 115 of 161 (71%) | 26.8 | 57.1 |
| Lebanese | 29 | 0 of 24 | 0 of 5 | 80 of 100 (80%) | 96 of 172 (56%) | 27.6 | 67.2 |
| Turkish | 25 | 0 of 20 | 0 of 5 | 50 of 61 (82%) | 95 of 139 (68%) | 14.0 | 56.0 |
| Moroccan | 30 | 0 of 24 | 0 of 6 | 60 of 80 (75%) | 96 of 172 (56%) | 25.0 | 55.0 |

The French graph already knew many of the ingredient words, such as olive oil, tomato, garlic and lemon. The technique words it lacks are mostly cuisine-specific moves.

**Moves missing across several cuisines.** Across the growing probes of all eight non-French cuisines, 134 distinct technique words are missing. Only three are asked for in four or more cuisines: **roll** and **knead** (five cuisines each) and **stir** (four). Most of the rest are asked for by one cuisine. Whether the same card will serve two cuisines is the test the epic describes, and this count shows only how often the same word appears.

## What this says, and what it does not

- A new cuisine begins at 0% on its own probes. That is expected, and it is the number the loop is meant to move.
- Much of what is missing is shared. Knead, roll, grind and make dashi are not Japanese or Indian words only. Whether the same card serves two cuisines, or each cuisine needs its own, is the test of the model that the epic's last story describes.
- Many words in these probes are phrases and not moves ("cover with a drop lid", "make tartar sauce", "pour boiling water over"). Some are one move under two names. How many separate technique cards a cuisine really has cannot be read from the count of words.
- The word counts are not comparable across cuisines. A writer chose each list, and the three writers did not choose in the same way.
- A probe checks that the graph has a name for each word. It does not check that a card is right, that a recipe works or that a safety fact is true.

## What was not done

- Nothing was drafted for any new cuisine, and nothing for the Mediterranean parent. That waits for the owner, for a reviewer who knows each cuisine, and for French to be reviewed, as the epic says and as [issue 8](https://github.com/mrspacerobot/cooking-graph/issues/8) records for Moroccan.
- There are no step probes. The model has no such kind.
- The probes have not been read by a person who knows the cuisine. Spellings and the idea that a dish is a typical home dish are the writers' own.
