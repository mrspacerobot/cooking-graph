# Substitution round one: two blind drafters per batch

Issue [5](https://github.com/mrspacerobot/cooking-graph/issues/5). Everything here is tier `drafted`. No cook has tried a swap, and no ratio has been tested.

## What was done

- `./candidates` listed open swap pairs from shared groups and from dish part options, in seven batches: liquids and sauces, dairy and starch, herbs and spices,
  vegetables, meat, fish, and the options inside dish parts.
- Each batch was drafted twice, by two agents who worked in separate worktrees and were told not to look at each other's work. Together they wrote 966 rows
  (520 and 446).
- `./stand-in-merge` kept a pair when both wrote it with one verdict. It kept the contexts they share. When they named different contexts and neither excluded
  the other's, it kept both and the report says so. It kept the exclusions of both, and a ratio only when the two were close.
- 288 rows were applied after the batches were combined. 3 more were dropped when two batches disagreed about the same pair. 282 pairs that only one drafter wrote
  were not applied and are listed in `docs/rounds/substitution-round-1-one-drafter.md`.
- Stand-in statements went from 29 (25 allowing and 4 exclusions) to 317 (286 allowing and 31 exclusions). 27 of the new rows are exclusions: swaps a cook might try that fail.

## Pairs the drafters wrote against each other

Nine pairs are not in the graph because the two disagreed. They are for a person to rule on:

- white wine for red wine: one says it fails in boeuf bourguignon and poires au vin rouge, the other says it works in coq au vin and a braise.
- parmesan for gruyere: one says it fails in croque-monsieur, the other says it works in a thermidor and a fish soup gratin.
- strained yogurt for creme fraiche: one says it fails when reduced or simmered, the other says it works as a cold garnish. They agree that heat splits it.
- red chilli powder for a dried red chilli: one says it works in dal tadka, the other says it scorches in hot fat and fails.
- butter for sunflower oil: one says it works in menemen, bulgur pilaf and msemen, the other says it fails for deep frying.
- plain rice for short-grain rice: one says it works in dolmades, the other says it fails in onigiri and takikomi gohan.
- lettuce for frisee, red wine for white wine, and spring onion for onion: two batches wrote opposite verdicts for the same pair.

## The blind questions

Forty swap questions (batch `stand-ins-2`) were written by another model that was told not to read `graph/`. The hash rule held eight back. They are counted, never listed.
After this round the growing set answers 1 of 32 and the held-back set 1 of 8. This is low for a plain reason: most questions name an ingredient or a recipe the graph does not have
(arborio rice, pistachios, coconut milk, skimmed milk, white vinegar, bouillabaisse, gazpacho, naan). So the next growth is ingredients and recipes, not more swap rows.
One growing question disagrees with the graph: the probe says ghee for butter in a dal tadka works, and a row says it does not in that context. That is left for a person.

## Doubts

- Agreement between two models is not truth. They share training, and they agree on swaps that are common knowledge.
- A kept row with `contexts differ` holds the contexts of both drafters, and each context was supported by one of them only.
- Several rows name a technique as context that does not list the food among the things it works on. The checker allows this, and a reviewer should look.
- Most ratios are 1:1 by weight and are rough, especially for pulses and bone-in against boneless meat.
- Allowing rows move allergens (milk, egg, gluten, fish, pork). The safety facts are computed from ingredients and are unchanged. The caveats say nothing about safety.
- Some swaps lean on regional or religious practice (pork for lamb in kefta). The caveats speak of taste only.
