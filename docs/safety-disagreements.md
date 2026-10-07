# Where the safety probes and the graph disagree

Written by `./safety disagreements`. Nothing here is settled: each disagreement is for a person to rule on.
The graph's side is worked out from the ingredients of the dish's recipe, and every safety record behind it is unverified.

| Set | Probes | Answerable | Agreeing | Disagreeing | Of which on strict answers alone |
|---|---|---|---|---|---|
| growing | 32 | 20 | 8 | 12 | 11 |
| held-back | 8 | 2 | 1 | 1 | 1 |

A probe is not answerable when its dish is not in the graph or has no recipe. What a held-back probe disagrees with is counted and never shown.

A disagreement rests on strict answers alone when the probe says the dish does not hold a fact and the graph holds it only through answers that are recorded strictly and not for certain. `docs/strict-answers.md` lists those answers.

## Coq au vin

- **Probe:** `safety-probe/coq-au-vin`, written by claude-sonnet-5-5.
- **The probe says it holds:** gluten, wheat, milk, sulphites.
- **The probe says it does not hold:** egg, fish.
- **The probe's reason:** The red wine carries sulphites. Flour dusted over the chicken or kneaded with butter thickens the sauce, so wheat, gluten and milk are in it.
- **The graph's dish:** `dish/coq-au-vin`. From the ingredients of its recipe it holds:
  - `fact/alcohol`: `ingredient/red-wine` (certain: It is wine.)
  - `fact/celery`: `ingredient/chicken-stock` (strict: Stock is usually made with celery, and stock cubes often hold it.)
  - `fact/egg`: `ingredient/red-wine` (strict: Wine may be cleared with egg white.)
  - `fact/fish`: `ingredient/red-wine` (strict: Wine may be cleared with isinglass, which comes from fish.)
  - `fact/gluten`: `ingredient/flour` (certain: It is wheat flour.), `ingredient/chicken-stock` (strict: Bought stock and stock cubes often hold wheat.)
  - `fact/meat`: `ingredient/chicken` (certain: It is chicken.), `ingredient/bacon` (certain: It is cured pork.), `ingredient/chicken-stock` (certain: Made from chicken and its bones.)
  - `fact/milk`: `ingredient/bacon` (strict: Cured pork is often made with lactose or milk protein.), `ingredient/red-wine` (strict: Wine may be cleared with milk protein.), `ingredient/butter` (certain: It is made from cream.)
  - `fact/pork`: `ingredient/bacon` (certain: It is cured pork.)
  - `fact/slaughter-product`: `ingredient/red-wine` (strict: Wine may be cleared with gelatine or isinglass.)
  - `fact/sulphites`: `ingredient/red-wine` (strict: Nearly all wine holds sulphites.)
  - `fact/wheat`: `ingredient/flour` (certain: It is wheat flour.), `ingredient/chicken-stock` (strict: Bought stock and stock cubes often hold wheat.)
- **Where they disagree:**
  - the probe says it does not hold egg (`fact/egg`), and the graph says it does, on strict answers alone.
  - the probe says it does not hold fish (`fact/fish`), and the graph says it does, on strict answers alone.

## Entrecôte béarnaise

- **Probe:** `safety-probe/entrecote-bearnaise`, written by claude-sonnet-5-5.
- **The probe says it holds:** egg, milk, sulphites.
- **The probe says it does not hold:** gluten, fish.
- **The probe's reason:** Béarnaise is egg yolks whisked with butter. The vinegar and wine in the reduction carry sulphites.
- **The graph's dish:** `dish/entrecote-sauce-bearnaise`. From the ingredients of its recipe it holds:
  - `fact/alcohol`: `ingredient/white-wine` (certain: It is wine.), `ingredient/white-wine-vinegar` (strict: Vinegar keeps a trace of the alcohol it is made from.)
  - `fact/egg`: `ingredient/egg-yolk` (certain: It is the yolk of an egg.), `ingredient/white-wine` (strict: Wine may be cleared with egg white.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with egg white.)
  - `fact/fish`: `ingredient/white-wine` (strict: Wine may be cleared with isinglass, which comes from fish.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with isinglass from fish.)
  - `fact/meat`: `ingredient/rib-steak` (certain: It is beef.)
  - `fact/milk`: `ingredient/butter` (certain: It is made from cream.), `ingredient/white-wine` (strict: Wine may be cleared with milk protein.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with milk protein.)
  - `fact/slaughter-product`: `ingredient/white-wine` (strict: Wine may be cleared with gelatine or isinglass.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with gelatine or isinglass.)
  - `fact/sulphites`: `ingredient/white-wine` (strict: Nearly all wine holds sulphites.), `ingredient/white-wine-vinegar` (strict: Made from wine, which nearly always holds sulphites.)
- **Where they disagree:**
  - the probe says it does not hold fish (`fact/fish`), and the graph says it does, on strict answers alone.

## French onion soup

- **Probe:** `safety-probe/french-onion-soup`, written by claude-sonnet-5-5.
- **The probe says it holds:** gluten, wheat, milk, celery, sulphites.
- **The probe says it does not hold:** egg, fish.
- **The probe's reason:** Flour and a baguette crouton bring wheat and gluten, and the Gruyère and butter bring milk. The white wine carries sulphites and the beef stock often has celery in it.
- **The graph's dish:** `dish/french-onion-soup`. From the ingredients of its recipe it holds:
  - `fact/alcohol`: `ingredient/white-wine` (certain: It is wine.)
  - `fact/celery`: `ingredient/beef-stock` (strict: Stock is usually made with celery, and stock cubes often hold it.)
  - `fact/egg`: `ingredient/white-wine` (strict: Wine may be cleared with egg white.)
  - `fact/fish`: `ingredient/white-wine` (strict: Wine may be cleared with isinglass, which comes from fish.)
  - `fact/gluten`: `ingredient/flour` (certain: It is wheat flour.), `ingredient/beef-stock` (strict: Bought stock and stock cubes often hold wheat.), `ingredient/baguette` (certain: Made of wheat flour.)
  - `fact/meat`: `ingredient/beef-stock` (certain: Made from beef and its bones.)
  - `fact/milk`: `ingredient/butter` (certain: It is made from cream.), `ingredient/white-wine` (strict: Wine may be cleared with milk protein.), `ingredient/gruyere` (certain: It is a cheese made from milk.)
  - `fact/slaughter-product`: `ingredient/white-wine` (strict: Wine may be cleared with gelatine or isinglass.), `ingredient/gruyere` (strict: By tradition it is made with animal rennet.)
  - `fact/sulphites`: `ingredient/white-wine` (strict: Nearly all wine holds sulphites.)
  - `fact/wheat`: `ingredient/flour` (certain: It is wheat flour.), `ingredient/beef-stock` (strict: Bought stock and stock cubes often hold wheat.), `ingredient/baguette` (certain: Made of wheat flour.)
- **Where they disagree:**
  - the probe says it does not hold egg (`fact/egg`), and the graph says it does, on strict answers alone.
  - the probe says it does not hold fish (`fact/fish`), and the graph says it does, on strict answers alone.

## Œufs mayonnaise

- **Probe:** `safety-probe/oeufs-mayonnaise`, written by claude-sonnet-5-5.
- **The probe says it holds:** egg, mustard, sulphites.
- **The probe says it does not hold:** gluten, milk.
- **The probe's reason:** Mayonnaise is egg yolk and oil, and the classic one is seasoned with Dijon mustard and vinegar. Mustard and vinegar often carry sulphites.
- **The graph's dish:** `dish/oeufs-mayonnaise`. From the ingredients of its recipe it holds:
  - `fact/alcohol`: `ingredient/dijon-mustard` (strict: Often made with white wine or wine vinegar.), `ingredient/white-wine-vinegar` (strict: Vinegar keeps a trace of the alcohol it is made from.)
  - `fact/egg`: `ingredient/egg` (certain: It is an egg.), `ingredient/egg-yolk` (certain: It is the yolk of an egg.), `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with egg white.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with egg white.)
  - `fact/fish`: `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with isinglass from fish.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with isinglass from fish.)
  - `fact/milk`: `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with milk protein.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with milk protein.)
  - `fact/mustard`: `ingredient/dijon-mustard` (certain: It is made of mustard seed.)
  - `fact/slaughter-product`: `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with gelatine or isinglass.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with gelatine or isinglass.)
  - `fact/sulphites`: `ingredient/dijon-mustard` (strict: Often kept with sulphites.), `ingredient/white-wine-vinegar` (strict: Made from wine, which nearly always holds sulphites.)
- **Where they disagree:**
  - the probe says it does not hold milk (`fact/milk`), and the graph says it does, on strict answers alone.

## Poires au vin rouge

- **Probe:** `safety-probe/poires-au-vin-rouge`, written by claude-sonnet-5-5.
- **The probe says it holds:** sulphites.
- **The probe says it does not hold:** egg, milk.
- **The probe's reason:** It is fruit, sugar and spice, but red wine carries sulphites.
- **The graph's dish:** `dish/poires-au-vin-rouge`. From the ingredients of its recipe it holds:
  - `fact/alcohol`: `ingredient/red-wine` (certain: It is wine.)
  - `fact/egg`: `ingredient/red-wine` (strict: Wine may be cleared with egg white.)
  - `fact/fish`: `ingredient/red-wine` (strict: Wine may be cleared with isinglass, which comes from fish.)
  - `fact/milk`: `ingredient/red-wine` (strict: Wine may be cleared with milk protein.)
  - `fact/slaughter-product`: `ingredient/red-wine` (strict: Wine may be cleared with gelatine or isinglass.), `ingredient/sugar` (strict: Some cane sugar is whitened with bone char.)
  - `fact/sulphites`: `ingredient/red-wine` (strict: Nearly all wine holds sulphites.)
- **Where they disagree:**
  - the probe says it does not hold egg (`fact/egg`), and the graph says it does, on strict answers alone.
  - the probe says it does not hold milk (`fact/milk`), and the graph says it does, on strict answers alone.

## Salade de chèvre chaud

- **Probe:** `safety-probe/salade-de-chevre-chaud`, written by claude-sonnet-5-5.
- **The probe says it holds:** gluten, wheat, milk, tree nuts, mustard, sulphites.
- **The probe says it does not hold:** egg, peanuts.
- **The probe's reason:** Goat cheese is milk and the toasts are bread. The vinaigrette brings mustard and sulphites from the vinegar, and most versions add walnuts.
- **The graph's dish:** `dish/salade-de-chevre-chaud`. From the ingredients of its recipe it holds:
  - `fact/alcohol`: `ingredient/dijon-mustard` (strict: Often made with white wine or wine vinegar.), `ingredient/red-wine-vinegar` (strict: Vinegar keeps a trace of the alcohol it is made from.)
  - `fact/egg`: `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with egg white.), `ingredient/red-wine-vinegar` (strict: Made from wine, which may be cleared with egg white.)
  - `fact/fish`: `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with isinglass from fish.), `ingredient/red-wine-vinegar` (strict: Made from wine, which may be cleared with isinglass from fish.)
  - `fact/gluten`: `ingredient/baguette` (certain: Made of wheat flour.)
  - `fact/milk`: `ingredient/goat-cheese` (certain: It is a cheese made from the milk of a goat.), `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with milk protein.), `ingredient/red-wine-vinegar` (strict: Made from wine, which may be cleared with milk protein.)
  - `fact/mustard`: `ingredient/dijon-mustard` (certain: It is made of mustard seed.)
  - `fact/slaughter-product`: `ingredient/goat-cheese` (strict: Many goat cheeses are made with animal rennet.), `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with gelatine or isinglass.), `ingredient/red-wine-vinegar` (strict: Made from wine, which may be cleared with gelatine or isinglass.)
  - `fact/sulphites`: `ingredient/dijon-mustard` (strict: Often kept with sulphites.), `ingredient/red-wine-vinegar` (strict: Made from wine, which nearly always holds sulphites.)
  - `fact/tree-nuts`: `ingredient/walnut` (certain: It is a tree nut.)
  - `fact/wheat`: `ingredient/baguette` (certain: Made of wheat flour.)
- **Where they disagree:**
  - the probe says it does not hold egg (`fact/egg`), and the graph says it does, on strict answers alone.

## Salade lyonnaise

- **Probe:** `safety-probe/salade-lyonnaise`, written by claude-sonnet-5-5.
- **The probe says it holds:** gluten, wheat, egg, mustard, sulphites.
- **The probe says it does not hold:** fish.
- **The probe's reason:** A poached egg tops it, croutons add wheat and gluten, and the warm dressing is Dijon mustard and red wine vinegar. Vinegar and mustard often carry sulphites.
- **The graph's dish:** `dish/salade-lyonnaise`. From the ingredients of its recipe it holds:
  - `fact/alcohol`: `ingredient/red-wine-vinegar` (strict: Vinegar keeps a trace of the alcohol it is made from.), `ingredient/dijon-mustard` (strict: Often made with white wine or wine vinegar.), `ingredient/white-wine-vinegar` (strict: Vinegar keeps a trace of the alcohol it is made from.)
  - `fact/egg`: `ingredient/egg` (certain: It is an egg.), `ingredient/red-wine-vinegar` (strict: Made from wine, which may be cleared with egg white.), `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with egg white.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with egg white.)
  - `fact/fish`: `ingredient/red-wine-vinegar` (strict: Made from wine, which may be cleared with isinglass from fish.), `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with isinglass from fish.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with isinglass from fish.)
  - `fact/gluten`: `ingredient/baguette` (certain: Made of wheat flour.)
  - `fact/meat`: `ingredient/bacon` (certain: It is cured pork.)
  - `fact/milk`: `ingredient/bacon` (strict: Cured pork is often made with lactose or milk protein.), `ingredient/red-wine-vinegar` (strict: Made from wine, which may be cleared with milk protein.), `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with milk protein.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with milk protein.)
  - `fact/mustard`: `ingredient/dijon-mustard` (certain: It is made of mustard seed.)
  - `fact/pork`: `ingredient/bacon` (certain: It is cured pork.)
  - `fact/slaughter-product`: `ingredient/red-wine-vinegar` (strict: Made from wine, which may be cleared with gelatine or isinglass.), `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with gelatine or isinglass.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with gelatine or isinglass.)
  - `fact/sulphites`: `ingredient/red-wine-vinegar` (strict: Made from wine, which nearly always holds sulphites.), `ingredient/dijon-mustard` (strict: Often kept with sulphites.), `ingredient/white-wine-vinegar` (strict: Made from wine, which nearly always holds sulphites.)
  - `fact/wheat`: `ingredient/baguette` (certain: Made of wheat flour.)
- **Where they disagree:**
  - the probe says it does not hold fish (`fact/fish`), and the graph says it does, on strict answers alone.

## Salade piémontaise

- **Probe:** `safety-probe/salade-piemontaise`, written by claude-sonnet-5-5.
- **The probe says it holds:** egg, mustard, sulphites.
- **The probe says it does not hold:** gluten, milk.
- **The probe's reason:** Egg is in both the mayonnaise and the chopped hard-boiled egg. The mayonnaise has mustard, and its vinegar and the cornichons often carry sulphites.
- **The graph's dish:** `dish/salade-piemontaise`. From the ingredients of its recipe it holds:
  - `fact/alcohol`: `ingredient/cornichons` (strict: Vinegar keeps a trace of the alcohol it is made from.), `ingredient/dijon-mustard` (strict: Often made with white wine or wine vinegar.), `ingredient/white-wine-vinegar` (strict: Vinegar keeps a trace of the alcohol it is made from.)
  - `fact/celery`: `ingredient/ham` (strict: Cooked ham is often made with a stock or an extract that holds celery.)
  - `fact/egg`: `ingredient/egg` (certain: It is an egg.), `ingredient/egg-yolk` (certain: It is the yolk of an egg.), `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with egg white.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with egg white.)
  - `fact/fish`: `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with isinglass from fish.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with isinglass from fish.)
  - `fact/meat`: `ingredient/ham` (certain: It is cured pork.)
  - `fact/milk`: `ingredient/ham` (strict: Cured pork is often made with lactose or milk protein.), `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with milk protein.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with milk protein.)
  - `fact/mustard`: `ingredient/cornichons` (strict: Often pickled with mustard seed.), `ingredient/dijon-mustard` (certain: It is made of mustard seed.)
  - `fact/pork`: `ingredient/ham` (certain: It is cured pork.)
  - `fact/slaughter-product`: `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with gelatine or isinglass.), `ingredient/white-wine-vinegar` (strict: Made from wine, which may be cleared with gelatine or isinglass.)
  - `fact/sulphites`: `ingredient/cornichons` (strict: Pickles are sometimes kept with sulphites.), `ingredient/dijon-mustard` (strict: Often kept with sulphites.), `ingredient/white-wine-vinegar` (strict: Made from wine, which nearly always holds sulphites.)
- **Where they disagree:**
  - the probe says it does not hold milk (`fact/milk`), and the graph says it does, on strict answers alone.

## Soupe de poisson

- **Probe:** `safety-probe/soupe-de-poisson`, written by claude-sonnet-5-5.
- **The probe says it holds:** gluten, wheat, crustaceans, egg, fish, milk.
- **The probe says it does not hold:** nothing.
- **The probe's reason:** Rockfish and small crabs go in the pot, so crustaceans are included. It is served with wheat croutons, grated cheese and a rouille that is often made with egg yolk.
- **The graph's dish:** `dish/soupe-de-poisson`. From the ingredients of its recipe it holds:
  - `fact/egg`: `ingredient/bread` (strict: Enriched loaves may hold egg.), `ingredient/egg-yolk` (certain: It is the yolk of an egg.)
  - `fact/fish`: `ingredient/rockfish` (certain: It is a fish.)
  - `fact/gluten`: `ingredient/baguette` (certain: Made of wheat flour.), `ingredient/bread` (certain: Bread is made of a cereal that holds gluten.)
  - `fact/lupin`: `ingredient/bread` (strict: Some bread is made with lupin flour.)
  - `fact/milk`: `ingredient/bread` (strict: Enriched loaves hold milk or butter.), `ingredient/gruyere` (certain: It is a cheese made from milk.)
  - `fact/sesame`: `ingredient/bread` (strict: Many loaves carry sesame seeds.)
  - `fact/slaughter-product`: `ingredient/gruyere` (strict: By tradition it is made with animal rennet.)
  - `fact/soy`: `ingredient/bread` (strict: Many bought loaves hold soy flour.)
  - `fact/tree-nuts`: `ingredient/bread` (strict: Some loaves hold walnuts or other nuts.)
  - `fact/wheat`: `ingredient/baguette` (certain: Made of wheat flour.), `ingredient/bread` (strict: Nearly all bread is made with wheat flour.)
- **Where they disagree:**
  - the probe says it holds crustaceans (`fact/crustaceans`), and the graph says it does not.

## Steak tartare

- **Probe:** `safety-probe/steak-tartare`, written by claude-sonnet-5-5.
- **The probe says it holds:** egg, fish, mustard.
- **The probe says it does not hold:** milk.
- **The probe's reason:** Raw egg yolk and Dijon mustard are classic, and the seasoning very often includes Worcestershire sauce, which is made with anchovy.
- **The graph's dish:** `dish/steak-tartare`. From the ingredients of its recipe it holds:
  - `fact/alcohol`: `ingredient/capers` (strict: Vinegar keeps a trace of the alcohol it is made from.), `ingredient/cornichons` (strict: Vinegar keeps a trace of the alcohol it is made from.), `ingredient/dijon-mustard` (strict: Often made with white wine or wine vinegar.)
  - `fact/egg`: `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with egg white.), `ingredient/egg-yolk` (certain: It is the yolk of an egg.)
  - `fact/fish`: `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with isinglass from fish.)
  - `fact/meat`: `ingredient/beef-fillet` (certain: It is beef.)
  - `fact/milk`: `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with milk protein.)
  - `fact/mustard`: `ingredient/cornichons` (strict: Often pickled with mustard seed.), `ingredient/dijon-mustard` (certain: It is made of mustard seed.)
  - `fact/slaughter-product`: `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with gelatine or isinglass.)
  - `fact/sulphites`: `ingredient/capers` (strict: Pickles are sometimes kept with sulphites.), `ingredient/cornichons` (strict: Pickles are sometimes kept with sulphites.), `ingredient/dijon-mustard` (strict: Often kept with sulphites.)
- **Where they disagree:**
  - the probe says it does not hold milk (`fact/milk`), and the graph says it does, on strict answers alone.

## Tartiflette

- **Probe:** `safety-probe/tartiflette`, written by claude-sonnet-5-5.
- **The probe says it holds:** milk, sulphites.
- **The probe says it does not hold:** gluten, egg.
- **The probe's reason:** Reblochon and crème fraîche both bring milk, and the white wine carries sulphites. There is no flour or egg in the classic.
- **The graph's dish:** `dish/tartiflette`. From the ingredients of its recipe it holds:
  - `fact/alcohol`: `ingredient/white-wine` (certain: It is wine.)
  - `fact/egg`: `ingredient/white-wine` (strict: Wine may be cleared with egg white.)
  - `fact/fish`: `ingredient/white-wine` (strict: Wine may be cleared with isinglass, which comes from fish.)
  - `fact/meat`: `ingredient/bacon` (certain: It is cured pork.)
  - `fact/milk`: `ingredient/reblochon` (certain: It is a cheese made from milk.), `ingredient/bacon` (strict: Cured pork is often made with lactose or milk protein.), `ingredient/white-wine` (strict: Wine may be cleared with milk protein.), `ingredient/creme-fraiche` (certain: It is soured cream.)
  - `fact/pork`: `ingredient/bacon` (certain: It is cured pork.)
  - `fact/slaughter-product`: `ingredient/reblochon` (strict: By tradition it is made with animal rennet.), `ingredient/white-wine` (strict: Wine may be cleared with gelatine or isinglass.)
  - `fact/sulphites`: `ingredient/white-wine` (strict: Nearly all wine holds sulphites.)
- **Where they disagree:**
  - the probe says it does not hold egg (`fact/egg`), and the graph says it does, on strict answers alone.

## Tourteau mayonnaise

- **Probe:** `safety-probe/tourteau-mayonnaise`, written by claude-sonnet-5-5.
- **The probe says it holds:** crustaceans, egg, mustard, sulphites.
- **The probe says it does not hold:** molluscs, fish.
- **The probe's reason:** Crab is a crustacean, and the mayonnaise is egg yolk with mustard. The vinegar in it often carries sulphites.
- **The graph's dish:** `dish/tourteau-mayonnaise`. From the ingredients of its recipe it holds:
  - `fact/alcohol`: `ingredient/white-wine` (certain: It is wine.), `ingredient/dijon-mustard` (strict: Often made with white wine or wine vinegar.)
  - `fact/crustaceans`: `ingredient/brown-crab` (certain: It is a crustacean.)
  - `fact/egg`: `ingredient/white-wine` (strict: Wine may be cleared with egg white.), `ingredient/egg-yolk` (certain: It is the yolk of an egg.), `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with egg white.)
  - `fact/fish`: `ingredient/white-wine` (strict: Wine may be cleared with isinglass, which comes from fish.), `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with isinglass from fish.)
  - `fact/milk`: `ingredient/white-wine` (strict: Wine may be cleared with milk protein.), `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with milk protein.)
  - `fact/mustard`: `ingredient/dijon-mustard` (certain: It is made of mustard seed.)
  - `fact/slaughter-product`: `ingredient/white-wine` (strict: Wine may be cleared with gelatine or isinglass.), `ingredient/dijon-mustard` (strict: Often made with wine, which may be cleared with gelatine or isinglass.)
  - `fact/sulphites`: `ingredient/white-wine` (strict: Nearly all wine holds sulphites.), `ingredient/dijon-mustard` (strict: Often kept with sulphites.)
- **Where they disagree:**
  - the probe says it does not hold fish (`fact/fish`), and the graph says it does, on strict answers alone.
