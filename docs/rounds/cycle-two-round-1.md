# Cycle two, round 1: the batch fresh-1

Written on 7 October 2026. Everything drafted here is a model's work and nobody has reviewed it. Every safety record is unverified.

## The gaps

`./probe fresh-1` listed what the 27 growing probes of the batch lacked. The six held-back probes of the batch were counted and never shown.

**Technique words, 10:** tie, bake in a salt crust, cut into batons, deep fry, fillet, flambe, melt, shape, stuff, trim.

**Ingredient words, 18:** apple, artichoke, beaufort, black pudding, calf's foot, calvados, chervil, cider, crayfish, dark chocolate, frogs' legs, lobster, rouille, sausage meat, sea bass, sherry vinegar, veal roasting joint, zander.

## What was drafted

| Kind | New | Changed |
|---|---|---|
| technique | 9 | 12 |
| ingredient | 17 | 4 |
| group | 3 | 0 |
| preparation | 1 | 0 |
| form | 1 | 1 |
| equipment | 1 | 0 |
| dish | 4 | 0 |
| recipe | 4 | 0 |

- **Nine new technique cards:** bake in a salt crust, cut into batons, deep-fry, fillet, flambé, melt, shape, stuff and trim.
- **One word was a name the graph already had a card for.** "Tie" is the truss card, which already covers a joint. It gained the names tie and ficeler. No other alias was added for a probe.
- **Three new groups.** Firm fruits (apple, pear), crustaceans (crayfish, lobster) and round fish (sea bass, zander, pike, rockfish, salmon). The pear had been a single thing on four cards. Those cards now name the group.
- **Cards that widened, each because a recipe of this round needed it and the card is true for the new members:** peel now covers the shell of a cooked lobster or crab, with a line that says how. Boil covers crustaceans. Simmer and toss cover fish and shellfish. Purée covers lean fish. Sauté covers firm fruits and frogs' legs. Dredge covers frogs' legs. Reduce covers cider.
- **Seventeen ingredients,** each answering all 21 facts with a basis and whether it is certain. Strict answers: animal rennet in beaufort, milk and cereal in black pudding, what may clear cider and its sulphites, milk fat and soy lecithin in dark chocolate, what bought sausage meat may hold, and everything a wine vinegar holds in sherry vinegar.
- **Rouille is a preparation** with parts and no recipe.
- **One name moved.** The form lardons had "batons" as an alias. The new form batons owns that name now.

## The four dishes

A fresh probe only needs its words to exist. A full dish with a recipe was written for four, each the one that teaches its skill best among those a growing safety probe also asks about:

| Dish | Skill | Why this one |
|---|---|---|
| Poulet vallée d'Auge | pan-sauce | Sear, flame, deglaze, simmer and reduce with cream, in one pan |
| Homard Thermidor | roux | A roux, a white sauce, a reduction, a yolk and a gratin in one dish |
| Cuisses de grenouilles à la provençale | saute | Flour, hot butter and a quick toss: the sauté at its plainest |
| Soupe de poisson | stocks | A soup built like a stock: sweat, simmer, crush and strain |

That is one fresh dish each for four skills, out of the two per skill that were allowed for the whole cycle.

## The reread

Thirteen new files were read again: the cards deep-fry, shape, flambé, fillet, trim and bake in a salt crust, the ingredients cider and black pudding, the preparation rouille, the dish soupe de poisson, and the recipes of Homard Thermidor, soupe de poisson and poulet vallée d'Auge.

**Four of the thirteen were wrong:**

- **Fillet** pointed at lean fish. That group holds skate, sole and salt cod, and the card describes none of them: a flat fish gives four fillets, a skate has wings, salt cod is sold filleted. It now points at the new group of round fish.
- **Bake in a salt crust** pointed at lean fish for the same reason. It now points at round fish.
- **Trim** pointed at green vegetables, which holds peas and spinach. The card is about beans, asparagus and artichokes, and now names those three.
- **The recipe of Homard Thermidor** never salted its sauce. It does now.

All three card faults are one mistake: reaching for the nearest group, which is too wide for the card. The step rule cannot catch it, because it checks that a step is covered by its card and not that the card is true for every member of its group.

## The numbers after the round

| Batch | Probes | Growing answered | Held back answered | New technique words | per 50 probes | New ingredient words | per 50 probes |
|---|---|---|---|---|---|---|---|
| fresh-1 | 33 | 27 of 27 | 2 of 6 | 0 | 0.0 | 4 | 6.1 |
| fresh-2, before its round | 32 | 11 of 26 | 3 of 6 | 7 | 10.9 | 20 | 31.2 |
| fresh-3, before its round | 30 | 7 of 24 | 2 of 6 | 5 | 8.3 | 23 | 38.3 |

At first run, before anything was drafted, fresh-2 had 11 new technique words and fresh-3 had 8. Round 1 answered four of the eleven and three of the eight without having seen either batch.

| Held-back probes | Answered | Technique words known | Ingredient words known |
|---|---|---|---|
| The 24 of cycle one | 17 of 24 | 66 of 66 (100.0%) | 124 of 133 (93.2%) |
| The 18 fresh ones | 7 of 18 | 59 of 62 (95.2%) | 97 of 108 (89.8%) |
| All 42 | 24 of 42 | 125 of 128 (97.7%) | 221 of 241 (91.7%) |

## The safety probes

The four dishes made four more growing safety probes answerable: 16 of 32 now.

- **Three agree:** poulet vallée d'Auge, Homard Thermidor and cuisses de grenouilles.
- **One disagrees, and not on a strict answer.** The probe says soupe de poisson holds crustaceans, because small crabs go into the pot. The recipe here was written from the dish probe, which names rockfish and no crab. Neither side was changed. It is for a person to say what the classic is.

Growing: 16 answerable, 7 agreeing, 9 disagreeing, of which 8 on strict answers alone. Held back: 2 answerable, 1 agreeing, 1 disagreeing.

## The model

No change to `schema/model.json` in this round, and no new word in a closed list. `./probe` can now run one batch alone.

## What did not fit

- Rouille has no recipe, so the safety runner takes every option of every part, the optional egg yolk included. The soup is said to hold egg for certain, when it holds egg only if the rouille is made with a yolk.
- The shell of a lobster comes off under the peel card. A cook would say shell it. Whether that is one move or its own card is open.
- A card cannot say that a need holds only for some food. The lemon that keeps a cut artichoke pale is in a sentence of the trim card and not in its needs.
