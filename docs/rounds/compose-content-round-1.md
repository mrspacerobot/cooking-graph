# Compose content round one: dishes, foods and technique gaps

Issue [5](https://github.com/mrspacerobot/cooking-graph/issues/5). Everything here is tier `drafted`. No cook has tried a recipe, and every amount, time and temperature is a model's guess.

## What was done

Four drafting agents, each in its own worktree, wrote what the growing compose probes named and the graph lacked. They never opened `probes/`. `./merge` copied 22 new files and refused none; `./twins` lists only the two old pairs; `./check` passes.

| Agent | Wrote |
|---|---|
| Greek and Spanish | avgolemono soup, salmorejo |
| Italian and French | risotto bianco (with risotto alla parmigiana as an alias), croque madame, a recipe for the existing ragu preparation |
| Indian, Moroccan, Turkish | chicken tikka masala, Hyderabadi dum biryani, chicken tagine with preserved lemon and olives, couscous royale; one new food, merguez |
| Japanese and foods | four foods: dry vermouth, plaice, smoked paprika, silken tofu |

Small changes to existing files: aliases and meat options on `preparation/ragu`, two aliases on `technique/emulsify`, and sole meunière gained a French name, the alias fish meunière and plaice as an option.

## Held-back flags

Four dishes the agents drafted were reported by the checker as asked by a held-back probe. Each was deleted with what only it needed and none is restored. Their names are not written here. Those dishes are not written in this round.

## Technique gaps: all five were already in the graph

The five technique phrases the id-mapping step could not match are aliases or variants that already exist: temper eggs (alias of `temper`), stew (alias of `braise`), dress (alias of `toss`), poach in oil (alias of `confit`), make a vinaigrette (now an alias of `emulsify`). The earlier note counted them as missing because the mapper was given names without aliases. That was a measurement mistake of mine, and it is corrected here.

## Numbers

| | Before | After |
|---|---|---|
| Compose probes, growing | 1 of 32 | 1 of 32 |
| Compose probes, held back | 0 of 8 | 0 of 8 |
| Stand-in probes, growing / held back | 12 of 52 / 2 of 13 | 12 of 52 / 2 of 13 |
| Recipe lines with a swap offered | 428 of 1522 | 463 of 1648 |
| Foods in no stand-in row | 294 | 299 |

The compose score did not move. Nine new dishes exist, and none answers its question yet. The reasons are specific:

- **Avgolemono:** the probe asks for tempering eggs, and the recipe's step is `make-avgolemono`, which is a variant of `thicken-with-egg-yolk`, not of `temper`.
- **Ragu and risotto:** the recipes are coarse. The ragu has two steps and no `sear` or `simmer`; the risotto has no `deglaze` step.
- **Croque madame:** the probe asks for `make a roux` and `grill`. The béchamel is an ingredient whose own recipe makes a roux, but a dish's techniques are read from its own steps only.
- **Free-text words** such as "ripe tomatoes" and "plaice fillets" still fail an exact match, which a closed-list photo step does not suffer.

## Swaps for the new foods

Two blind drafters wrote rows for 41 pairs involving the new foods (36 from `./candidates` and 5 added by hand: the tofus, and paprika with smoked paprika). They wrote 13 and 24 rows. `./stand-in-merge` kept the 12 both wrote (6 allowing, 6 exclusions), disputed 0, and left 13 that only one drafter wrote unapplied. Foods in no stand-in row went from 299 to 291. The swap most worth having, smoked paprika for plain paprika in Spanish sauces, was written by one drafter only and is not applied; a person can rule on it. The merguez and chorizo exclusions are also one-drafter and wait.

## Doubts

- Hyderabadi dum biryani overlaps `chicken-biryani`, which already carries the alias dum biryani. It was kept for its regional differences (raw marinated lamb, longer dum). Delete the two files if no overlap is wanted.
- Merguez in the couscous royale is warmed in broth because `pan-fry` works on one named sausage only. A group of sausages would fix that.
- Dry vermouth holds animal-product strictly (finings) while the older wines do not. A person should rule on consistency. Its botanical blend is unknown, so other allergens are recorded free of and must be checked on a bottle.
- Smoked paprika has no link to paprika on purpose. Silken tofu is a kind of tofu, like firm tofu.
- Salmorejo uses `puree` for the oil because `emulsify` works only on emulsified sauces. The `simmer` and `puree` cards are stretched by the way these recipes use them. A reviewer should look.
