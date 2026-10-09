# Owner decision sheet

Written on 8 October 2026 for the owner. Everything below is waiting for a person. Answer by number ("D3 yes, D7 no") in a comment on [issue 6](https://github.com/mrspacerobot/cooking-graph/issues/6) or in the conversation. An item you do not answer keeps its default, and nothing is promoted above `drafted` either way.

The state behind it: all 453 ingredient safety records are unverified, no reviewer exists, every amount in every recipe is a model's guess, and nothing may be exported. The branch `claude/modest-clarke-n2wbsf` is 17 commits ahead of `main` with no pull request.

## A. Safety and strictness (the biggest block)

| # | Question | Default | If you answer |
|---|---|---|---|
| D1 | Keep strict answers for the 353 of 638 facts that ingredients hold only because a common form may hold them? (`docs/strict-answers.md`) | Yes, keep all strict | Loosening a reason (for example "wine may be cleared with egg white") removes that fact from every dish that uses the ingredient. Say which reason, not which fact. |
| D2 | Rule on the 12 growing and 2 held-back safety disagreements (`docs/safety-disagreements.md`). Eleven of the twelve rest on strict answers alone, so D1 decides most of them. | None settled | A probe and the graph are never edited to agree; you rule, or a fetched page does. |
| D3 | Dry vermouth holds animal-product strictly (finings). The older wines (white wine, red wine, sherry, marsala, madeira) hold milk, egg, fish and slaughter-product strictly but not animal-product. Make them consistent? | Leave as is, flagged | Consistency means adding animal-product strictly to the older wines, which then show it in every dish that uses wine. |
| D4 | May the names of entries on the Health Canada, CFIA, Codex and EU allergen lists be used in a product that is sold? | No: leave those rows out of any export | A lawyer's or the publisher's word is needed. The facts themselves are `sourced` for names only. |
| D5 | Chestnut as tree nut, Roquefort holding gluten and wheat, gelatin: keep as drafted and strict? | Yes | These are from memory, not from a fetched page. |

## B. Cards and dishes (judgement calls that stretched the model)

| # | Question | Default | If you answer |
|---|---|---|---|
| D6 | Widen `technique/grill` to poultry? Today a grilled chicken skewer cannot use it. | No | Yes adds `group/poultry` to the card; a reviewer should check the card still reads true for chicken. |
| D7 | Widen `technique/cook-on-dum` from meat to spiced vegetables, and `technique/cook-pilaf` to short-grain rice and olive oil? | No | Arroz con pollo and vegetable biryani use them today without stretching the card. |
| D8 | `simmer`, `puree`, `deglaze` and `sear` were used a little beyond their cards (salmorejo, rice in broth). Widen, add variants, or leave? | Leave | Leaving means some probes asking for `deglaze` (risotto) or `sear` (mince) stay unanswered, by design. |
| D9 | Keep Hyderabadi dum biryani as its own dish although `chicken-biryani` already carries the alias "dum biryani"? | Keep | No deletes two files. |
| D10 | Risotto bianco and risotto alla parmigiana as one dish with an alias? | Yes, one dish | A cheese-free "in bianco" would then be its own dish. |
| D11 | Keep `fold-a-paratha` and `cook-a-paratha` as new variant cards, or fold them into `laminate` and `griddle`? | Keep | Folding means widening those two cards to chapati dough. |
| D12 | Three frying cards now overlap (`deep-fry`, `fry-croquetas`, `fry-rice-balls`). Merge at the next review? | Leave | A reviewer decides which stays. |

## C. Swap rows waiting for a ruling

| # | Question | Default | If you answer |
|---|---|---|---|
| D13 | Apply any of the one-drafter swap rows? 282 pairs from round one (`docs/rounds/substitution-round-1-one-drafter.md`) and 47 since. The one that matters most is smoked paprika for plain paprika in Spanish sauces. | None applied | Name the ones to apply, or ask for a third drafter on a batch. |
| D14 | Eight pairs the two drafters wrote against each other: butter and olive oil (both ways), and chicken stock, stock, white chicken stock, red wine, milk for water, plus water for milk. | Kept out of the graph | Rule yes or no per pair, in a context. |
| D15 | Six exclusions were held back because they contradict the `deglaze` card (cognac and red wine vinegar for wine or water). Apply them anyway, or change the card's option list? | Neither | The card says both are options; the exclusions say a straight swap is wrong. A splash is fine, a replacement is not. |

## D. Scope

| # | Question | Default | If you answer |
|---|---|---|---|
| D16 | Add a Thai (and Vietnamese) cuisine node? Fish sauce, green curry paste and two Thai dishes wait for it. | No | Yes means a cuisine file, pantry links and a Thai dish round. |
| D17 | Add sub-cuisines Catalan, Sicilian, Roman? Crema catalana, arancini and suppli sit under Spanish and Italian. | No | Local names keep their own place in the graph. |
| D18 | Add kokum? The Kerala fish curry uses tamarind only. | No | A new ingredient with its swaps. |

## E. Measuring the graph

| # | Question | Default | If you answer |
|---|---|---|---|
| D19 | The compose probes use free-text technique labels from a writer who has not seen the graph, and they ask for moves real recipes do not contain, so the score stays at 1 of 64 growing. Allow a writer to see `./vocabulary` (ids and names only, no recipes) and write questions with ids? | No | This changes the AGENTS.md rule that probe writers cannot see `graph/`; the change would be made in the same pull request. |
| D20 | Four of the eight compose-1 held-back probes were read by the drafter before a rule change. Retire the batch's held-back set and rely on compose-2? | Keep, flagged as weakened | Retiring costs eight probes and nothing else. |

## F. Process

| # | Question | Default | If you answer |
|---|---|---|---|
| D21 | Open a pull request for the branch (17 commits since `main`)? | Wait | When you say so, the description will say how much and of what, and list the doubts. |
| D22 | Post the final cycle numbers as a comment on [issue 5](https://github.com/mrspacerobot/cooking-graph/issues/5)? | Wait | Outward-facing, so only on your word. |
| D23 | Decide the stack for the repository ([issue 4](https://github.com/mrspacerobot/cooking-graph/issues/4)), now that the app backend is planned in Rust. `docs/stack-options.md` keeps the graph tools standard-library Python behind a SQLite build. | Undecided | The export contract for the Rust backend can be written once this is settled. |
| D24 | Who is the first reviewer, and for which cuisine? A packet is ready for the cuisine with the most recipes (`docs/review-packets/`). | The owner, until found | Nothing rises above `drafted` without a person who knows that cuisine. |

## G. Older questions from issue 6, still open

| # | Question | Default |
|---|---|---|
| D25 | Is milk alone a same-method stand-in for cream in a gratin dauphinois? | Keep the disagreement visible |
| D26 | Should courgette-only ratatouille be its own dish? | Keep the variant explicit, await the reviewer |

## What I would answer first

D1 and D24. D1 decides most of the safety disagreements in one stroke, and D24 is the only thing that moves a recipe from a guess to something a person stands behind. D19 comes next if you want the probe scores to mean something again.
