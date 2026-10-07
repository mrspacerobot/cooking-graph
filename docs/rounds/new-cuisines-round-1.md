# New cuisines, round 1: thirteen agents and a guard against duplicates

Written on 7 October 2026. Everything drafted here is a model's work and nobody has reviewed it. Every safety record is unverified. Nothing here may be shown to a cook or exported.

This is the first drafting round for the eight new cuisines, and a fourth round for French. The probes they were measured against are described in `docs/rounds/new-cuisines-first-run.md`.

## How it ran

Agents drafted in their own checkouts of the repository and could not collide. The files came back through `./merge`, which copies only new files and refuses any whose id or name another thing already holds. Small changes to existing things (an alias, a link) came back in a list and were applied by script.

| Wave | Agents | Task |
|---|---|---|
| 1 | 2 drafters | The words that two or more cuisines ask for, written once (72 words), and the French words fresh-4 still lacked (34 words) |
| 1 | 3 designers | Notes only: the review record, step probes, the stack and the backlog. No code, no issue created |
| 2 | 8 drafters | One cuisine each: Japanese, Indian, Italian, Greek, Spanish, Lebanese, Turkish, Moroccan |

Wave 1 came first so that eight agents never invent the same ingredient. The guard was built before any of them ran, with tests: an ingredient and a preparation may not share a name, `./twins` lists likely duplicates and never blocks, and `./merge` refuses clashes. It is change 30 in `docs/model.md`.

A mistake in the run: the first five agents were started in checkouts of the old `main` and did not have the cuisine field, `./probe --cuisine` or the new probes. They were stopped within minutes, their checkouts removed, and the five were started again from the right commit. Nothing from the first attempt was used.

## What was drafted

New graph files since the design notes, by kind:

| Kind | New |
|---|---|
| ingredient | 232 |
| technique | 119 |
| preparation | 22 |
| dish | 16 |
| recipe | 16 |
| equipment | 15 |
| group | 7 |

Thirty-seven existing files were changed, nearly all by an alias or a link. By agent: shared words 68 files, French 30, Japanese 102, Italian 57, Spanish 33, Indian 45, Moroccan 28, Lebanese 25, Greek 22, Turkish 15.

Each cuisine has two dishes with a recipe, 16 in all. Moroccan has the weeknight chicken with instant couscous and a tagine. No cuisine has a program.

## The numbers

Growing probes are the ones the graph is grown against. Held-back ones are never opened and are counted only.

| Cuisine | Growing answered, first run | Growing answered now | Held back answered now |
|---|---|---|---|
| French | 180 of 207 | 207 of 207 | 33 of 50 |
| Japanese | 0 of 24 | 24 of 24 | 0 of 6 |
| Indian | 0 of 24 | 24 of 24 | 3 of 6 |
| Italian | 1 of 24 | 24 of 24 | 2 of 6 |
| Greek | 1 of 24 | 24 of 24 | 4 of 6 |
| Spanish | 0 of 24 | 24 of 24 | 6 of 6 |
| Lebanese | 0 of 24 | 24 of 24 | 4 of 6 |
| Turkish | 0 of 24 | 24 of 24 | 5 of 6 |
| Moroccan | 0 of 24 | 24 of 24 | 4 of 6 |
| All | 182 of 399 | 399 of 399 | 61 of 98 (62%) |

Words known: growing 1462 of 1462 technique words and 2654 of 2654 ingredient words. Held-back probes: 329 of 355 technique words and 613 of 648 ingredient words.

The graph now holds 1,059 things and 427 ingredients, each answering all 21 safety facts, with 269 facts held for certain and 317 recorded strictly for want of knowing. None of the 427 safety records is verified. The safety probes did not move: 8 of 32 growing agree, 11 disagree, 10 of those on strict answers alone.

## What the numbers do not say

- **The growing score is 100% because the graph was grown against it.** It shows the work was done, not that the graph is right.
- **The held-back gains are not clean evidence.** The held-back probes ask for common kitchen words, and the shared and French rounds drafted many of them. Held-back answers rose in every round. The drafters were told not to open `probes/`, but that is an instruction and cannot be shown. One agent reported seeing a file name in the probe writers' folder, which holds every probe of its batch, and says it did not open it. The checker's rule against a dish drafted towards a held-back probe passes.
- **Japanese held-back is 0 of 6.** It is the cuisine furthest from French, and the one probe batch whose gaps were widest. A zero is a result and was left alone.
- **No stopping rule is met.** French held back is 33 of 50 against a bar of 95%, there are no step probes, no reviewer exists and nothing is verified.
- **Each cuisine has two written dishes.** Of 399 growing probes, 81 have their dish written. The rest are answered because their words exist.

## What the guard caught

Seven clashes between agents or with the graph, every one a real duplicate or near-duplicate:

| Files | What clashed | Settled |
|---|---|---|
| Shared `bread` and French `coat` | Both were crumb-coating | One card, `coat`, with the name bread |
| Shared `core` and French `gut a fish` | Both claimed the French verb vider | Kept on gut only |
| Greek `pita` and Lebanese `pita-bread` | One bread, two files | The Lebanese file stays |
| Moroccan `dried-fava-bean` and Turkish `dried-broad-bean` | Fava and broad bean are one bean | The Turkish file stays |
| Japanese `mix-batter` and shared `batter` | One move | Alias on `batter` |
| Japanese `squeeze-out-water` and Lebanese `squeeze` | One move | Alias on `squeeze` |
| Greek and Spanish `make-a-bechamel` | The same id | The Greek card stays, left alone by the merge |

`./twins` lists two pairs, both read and both kept: bone marrow and marrow bone (the tissue is part of the bone), and okra and savoiardi ("ladies' fingers" is British for okra and "ladyfingers" are sponge biscuits).

What the guard cannot find: two things that are one thing and share no word and no listed synonym.

## The reread

I read a sample of each merge with fresh eyes, as in earlier rounds.

- **Pork brawn** was named "Museau de porc". That is the snout; brawn is set head meat. Renamed.
- **Shake the pan** worked on all lean fish. It suits cod-like fish that give up gelatine. Narrowed.
- **An agent's link to pan-fry** would have been a fourth single thing. Dropped.
- **Set in aspic** claimed to work on dashi through the stocks group. Narrowed to the stocks that set.
- **Yam** was an alias of the Japanese yam and is wider than it. There is now a general yam and the Japanese yam is a kind of it.
- **The group `minced meat`** still said it stood alone after it gained two members. Corrected.

## What is doubtful

- **Every amount, time and temperature is from memory.** No recipe was cooked. The tangia is four to five hours in an earthenware jar in a home oven, which may need care.
- **Strict safety guesses.** Coconut as a tree nut, sulphites in jaggery, amchur and black salt, wheat in asafoetida, rennet in cheeses, soy in phyllo, and the sausages and cured meats of Spain and Italy are the drafters' own guesses. A person has to rule.
- **Salt and dried beans.** The pulses group says to salt early to keep the skins firm. The Turkish bean recipe salts late, and so does the lentil card. The graph disagrees with itself.
- **Broad cards.** Drain names seven groups, and keep warm, cover with a lid, garnish and dry name several. Each needs a person to confirm it is true for every member. Clarify works on the whole stocks group, which includes dashi.
- **Names from memory.** Regional names such as phodni, oggarane, thalippu, paximadi, rigani, kritharaki, risoni, seksu and baqleh need a reviewer who knows the cuisine.
- **Thin cards.** Reheat works only on pulses and stocks. Make a sauce was drafted for a single probe word.
- **Marsala sits in the wines group,** whose description does not fit its use in a zabaione.
- **French is not flattened, but nothing proves it.** Each regional move is a card of its own with a `variant_of` and a `differs` line. Whether the line is true is for a reviewer.

## The model

One change, number 30: the guards against one thing written twice. No other change to `schema/model.json`, and no new word in a closed list. Names stay in English and French only; local names are written in Latin letters as aliases. A vocabulary change would be needed for names in their own script.

## What this does not change

The cuisines have no reviewer, so nothing here moves them towards the app. The next steps are in `docs/review-record.md`, `docs/step-probes.md`, `docs/stack-options.md` and `docs/backlog-draft.md`: the review record, step probes, the stack decision and the backlog. Those four notes are designs and nothing in them is built.
