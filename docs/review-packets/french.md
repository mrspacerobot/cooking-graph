# Reviewer packet: French cooking

Generated from the graph on 8 October 2026 by a script, so it reads exactly what the files say. Everything in it is tier `drafted`: a model wrote it, nobody has cooked it and no person has approved it. **Every amount, time and temperature below is a guess.** Your job is to say where a guess is wrong.

French has the most recipes of any cuisine (82 of 197). This packet holds the 10 technique cards the French recipes use most, and 10 French recipes that between them exercise those cards.

## What you are asked to do

Read each card and each recipe and answer in plain words, one line per item, in any format you like. Suggested shorthand:

- **OK** - I would stand behind it as written.
- **FIX** - wrong, and here is what it should say.
- **UNSURE** - I cannot judge this one.

For a recipe, answer the amounts line by line (too much, too little, right) and say whether the order and the cues are true to how the dish is made. Say what you would cook differently and why. You do not need to know the repository to do this.

You are not asked to judge safety (allergens, doneness, raw egg). Those stay unverified until a person with safety authority checks them against a source.

## Putting your answers on record (for the owner, not the reviewer)

Nothing here changes the graph by itself. When the reviewer has answered, the owner turns each OK into a review record:

1. Add a reviewer file by hand in a pull request you merge: `graph/reviewer/french-1.json` (a slug, never a real name or an email) with `kind` person and `knows` French and how (`cooks-it-at-home`, `cooks-it-for-work`, `trained-in-it`, `lives-or-lived-there` or `studies-it`).
2. For each approved card or recipe run `./review show <id>` to read it as the reviewer saw it, and `./review seal <id>` to print its hash. A hash is only valid for the file as it stands, so seal it on the day.
3. Write one `review` file for the session (`graph/review/french-1-<topic>-<day>.json`) using the template in `docs/review-record.md` section 5, with `grants` set to `reviewed`, the hashes in `seen`, and a `note` for every rejection.
4. Set `"tier": "reviewed"` on the approved files in the same pull request. `./check` then finds a live record by a reviewer who knows French with the right hash. If the file is edited later, the tier falls back.

A FIX is not written into the graph by the reviewer. It goes back to a drafter, who corrects the file, and the corrected version is offered again.

## Part 1: the technique cards

### T1. Simmer (`technique/simmer`)

Used in 27 of the 82 French recipes.

**What it does:** Cooks food in liquid that is kept just below a boil, so that it turns tender without being knocked about.

**How:**

1. Bring the liquid up to a boil, then turn the heat down at once.
2. Find the setting where a few bubbles break the surface now and then.
3. Leave the lid off or ajar, so that the heat does not build back up to a boil.
4. Look in from time to time, and top the pot up if food shows above the liquid.

**Cues:** (see) A bubble or a small cluster of them rising every moment or so, and a surface that shivers. (hear) Near silence. A pot that rolls and rattles is boiling.

**Common mistakes:** Letting it boil, which toughens meat and turns a stock cloudy. Fix: Turn the heat down, or move the pot half off the burner. Covering the pot tightly, so that it climbs to a boil unseen. Fix: Leave the lid ajar.

**Works on:** vegetables, pulses, pasta, meat, stocks, sauces, butter, fish-and-shellfish

Your answer: OK / FIX / UNSURE - ________

### T2. Sweat (`technique/sweat`)

Used in 18 of the 82 French recipes.

**What it does:** Softens cut vegetables in a little fat over low heat, so that they give up their water and turn sweet without browning.

**How:**

1. Warm the fat in a wide pan over low heat.
2. Add the vegetables with a little salt and stir to coat them.
3. Keep the heat low and stir now and then, so that nothing sits long enough to colour.
4. Cover the pan to go faster: the trapped steam softens them.
5. Stop when the pieces are soft and glassy.

**Cues:** (hear) A quiet, steady hiss. A loud sizzle means the heat is too high. (see) The onion turns glassy and limp, with no brown at the edges. (smell) Sweet, with the raw sharpness gone.

**Common mistakes:** The heat is too high, so the edges brown before the middle softens. Fix: Turn the heat down and add a spoonful of water to stop the colour. Too many vegetables in a small pan, so they stew in their own water. Fix: Use a wider pan, or let the water cook off before going on.

**Works on:** aromatic-vegetables, alliums, watery-vegetables, mushrooms

Your answer: OK / FIX / UNSURE - ________

### T3. Deglaze (`technique/deglaze`)

Used in 17 of the 82 French recipes.

**What it does:** Dissolves the browned layer stuck to a hot pan with a splash of liquid, turning it into the base of a sauce.

**How:**

1. Pour off the fat, and keep everything brown that sticks to the pan.
2. Soften a little shallot or garlic in the pan first, if the sauce calls for it.
3. Take the pan off the flame to add wine or spirits, then put it back.
4. Scrape the bottom with a wooden spoon as the liquid boils, until the pan is clean and the liquid has turned brown.

**Cues:** (hear) A sharp hiss and a burst of steam when the liquid hits the pan. (see) The bottom of the pan comes clean under the spoon and the liquid darkens. (smell) The raw smell of the wine goes as it boils.

**Common mistakes:** Deglazing a pan whose fond has burnt black, which makes a bitter sauce. Fix: Taste a scrap of the fond first. If it is bitter, wipe the pan out and build the sauce without it. Leaving all the fat in, so that the sauce is greasy and will not come together. Fix: Pour the fat off first. The flavour is in the brown bits, not in the fat.

**Works on:** fond

Your answer: OK / FIX / UNSURE - ________

### T4. Sear (`technique/sear`)

Used in 14 of the 82 French recipes.

**What it does:** Browns the surface of meat or fish fast in a very hot pan, building a crust full of flavour while the inside stays underdone.

**How:**

1. Dry the surface well. Wet food steams before it browns.
2. Salt it just before it goes in.
3. Heat a heavy pan until a thin film of oil shimmers and gives off its first wisp of smoke.
4. Lay the food in away from you and press it flat. Then leave it alone.
5. Turn it when it lifts off the pan by itself and the underside is deep brown.
6. Take it out to rest. The crust left on the pan is the fond for a sauce.

**Cues:** (hear) A loud, steady sizzle that does not fade. A weak hiss means the pan was not hot enough. (see) A deep brown crust, and a brown line climbing the side of the piece. (feel) The piece lets go of the pan when it is ready to turn. If it sticks, it is not ready.

**Common mistakes:** Moving the food before it has browned, which tears the crust and leaves it on the pan. Fix: Leave it until it releases by itself. Crowding the pan, so that the pieces stew in their own juice and turn grey. Fix: Sear in batches with space between the pieces, and let the pan heat up again. Putting food in the pan while its surface is wet. Fix: Pat it dry with paper on every side first.

**Works on:** steaks-and-chops, braising-cuts, poultry, roasting-joints, offal, salmon, scallop

Your answer: OK / FIX / UNSURE - ________

### T5. Whisk (`technique/whisk`)

Used in 14 of the 82 French recipes.

**What it does:** Beats a liquid with a whisk until it is blended and smooth.

**How:**

1. Use a bowl large enough that nothing slops over.
2. Tilt the bowl and beat in quick strokes that cross the middle.
3. Keep going until the mixture is one colour and one texture.

**Cues:** (see) No streaks. Beaten eggs are an even yellow that runs off the whisk in a thin stream.

**Common mistakes:** Whisking eggs for an omelette until they foam, which makes it spongy. Fix: Stop as soon as the streaks of white are gone.

**Works on:** emulsified-sauces, roux-sauces, creams, egg, egg-yolk, roux

Your answer: OK / FIX / UNSURE - ________

### T6. Reduce (`technique/reduce`)

Used in 15 of the 82 French recipes.

**What it does:** Boils a liquid down, so that its water leaves as steam and what remains is thicker and stronger.

**How:**

1. Use a wide pan. The wider the surface, the faster the water leaves.
2. Boil steadily, uncovered.
3. Watch the level against the side of the pan, and the size of the bubbles.
4. Stop when it coats the back of a spoon, and season only then.

**Cues:** (see) The bubbles grow larger and slower, and a finger drawn across the back of a coated spoon leaves a clear path. (hear) The boil deepens from a rattle to a slow, thick plop.

**Common mistakes:** Salting before reducing, so that the salt is concentrated with everything else. Fix: Season at the end. Walking away near the end, when a sauce goes from syrup to scorched in moments. Fix: Stay with it once it starts to thicken, and pull it off the heat early.

**Works on:** cooking-liquors, stocks, wines, creams, cider

Your answer: OK / FIX / UNSURE - ________

### T7. Boil (`technique/boil`)

Used in 13 of the 82 French recipes.

**What it does:** Cooks food in plenty of fast-bubbling salted water, so that it is done quickly and evenly.

**How:**

1. Fill a large pot with far more water than the food needs.
2. Bring it to a rolling boil and salt it until it tastes pleasantly salty.
3. Add the food and bring the water back to the boil as fast as you can.
4. Test a piece often, and lift the food out the moment it is tender.

**Cues:** (see) Big bubbles that keep rolling even when you stir. (feel) The tip of a knife slides into a vegetable with only slight resistance.

**Common mistakes:** Too little water, so it stops boiling when the food goes in and green vegetables turn dull. Fix: Use a bigger pot and more water, and cook in batches. Salting the water too lightly. Fix: Salt it well. Food boiled in plain water tastes flat, however it is seasoned later.

**Works on:** green-vegetables, root-vegetables, pasta, alliums, cauliflower, crustaceans

Your answer: OK / FIX / UNSURE - ________

### T8. Chill (`technique/chill`)

Used in 12 of the 82 French recipes.

**What it does:** Brings hot food down to the cold of the fridge quickly, so that it keeps well and so that a cold dish is truly cold.

**How:**

1. Move the hot food out of its pot into a wide, shallow container.
2. Stand the container in iced water and stir now and then.
3. Put it in the fridge, uncovered, once it has stopped steaming.
4. Cover it when it is cold. Taste a cold dish again before serving, because cold dulls salt.

**Cues:** (feel) The container is cold to the hand all over, with no warm core.

**Common mistakes:** Leaving a large pot of stock to cool by itself on the stove, where its middle stays warm for a long time. Fix: Divide it into shallow containers and cool them in iced water. Seasoning a soup while it is hot and serving it cold. Fix: Taste it again when it is cold.

**Works on:** stocks, sauces, vegetables, fish-and-shellfish, firm-fruits

Your answer: OK / FIX / UNSURE - ________

### T9. Toss (`technique/toss`)

Used in 10 of the 82 French recipes.

**What it does:** Coats every piece evenly with a dressing or a sauce by lifting and turning.

**How:**

1. Put the food in a bowl far larger than it needs.
2. Add the dressing a little at a time, around the edge and not on top.
3. Lift from the bottom and let the pieces fall, with clean hands or a pair of spoons.
4. Taste a piece and adjust before serving.

**Cues:** (see) Every piece glistens, and nothing pools in the bottom of the bowl.

**Common mistakes:** Dressing leaves long before serving, so that the acid and salt make them limp. Fix: Toss at the last moment. Pouring on all the dressing at once, which drowns the food. Fix: Add it in stages and stop when everything is lightly coated.

**Works on:** vegetables, starches, meat, egg, fish-and-shellfish

Your answer: OK / FIX / UNSURE - ________

### T10. Peel (`technique/peel`)

Used in 10 of the 82 French recipes.

**What it does:** Takes off the skin or the shell, and as little as possible of what lies under it.

**How:**

1. Wash the vegetable first, so that dirt does not travel from the skin to the flesh.
2. Draw a peeler along its length in long strokes, turning it as you go.
3. Use a knife for a thick or knobbly skin: cut a flat base, then follow the curve from top to bottom.
4. For a boiled egg, crack the shell all over and peel from the wide end under a thin stream of water.
5. For a cooked lobster or crab, crack the shell and ease the flesh out in whole pieces.

**Cues:** (see) Smooth flesh, with no skin left and no deep gouges.

**Common mistakes:** Peeling long before cooking, so that potato and celeriac turn brown. Fix: Peel just before use, or hold the pieces under water with a little lemon juice.

**Works on:** root-vegetables, alliums, egg, asparagus, firm-fruits, crustaceans

Your answer: OK / FIX / UNSURE - ________

## Part 2: the recipes

### R1. Homard Thermidor (`recipe/homard-thermidor`)

Lobster boiled, split and taken from its shell, bound in a white sauce sharpened with mustard, put back into the shells and browned under the grill.

Serves / makes: 2 serving

| Amount | Ingredient | Your answer (right / too much / too little) |
|---|---|---|
| 1 piece | lobster | |
| 100 millilitre | white wine | |
| 1 piece | shallot (minced) | |
| 30 gram | butter | |
| 20 gram | flour | |
| 200 millilitre | milk | |
| 1 teaspoon | dijon mustard | |
| 1 piece | egg yolk | |
| 40 gram | gruyere (grated) | |
| 2 tablespoon | salt | |

**Steps:**

1. *boil* - Bring a large pot of water to a rolling boil and salt it well. Plunge the lobster in head first, cover the pot, and count the time from the moment the water boils again. Check the thickest part against a trusted guide to doneness. [8-10 minute]
2. *chill* - Lift the lobster out and let it cool until it can be handled.
3. *peel* - Split the lobster in half along its length. Lift out the tail meat and cut it in thick slices, crack the claws and ease out their meat. Rinse the half shells and keep them.
4. *reduce* - Boil the wine with the shallot in a small pan until only a spoonful of syrupy liquid is left. [4-5 minute]
5. *make a roux* - Melt the butter in a saucepan, stir in the flour and cook it gently for a moment without colour. [2 minute]
6. *whisk* - Whisk in the milk a little at a time, bring it to the boil and simmer until the sauce is thick and smooth. [5 minute]
7. *thicken with egg yolk* - Off the heat, stir in the reduced wine, the mustard and the egg yolk. Taste the sauce and salt it lightly. Do not let it boil again.
8. *toss* - Fold the lobster meat into most of the sauce and spoon it into the half shells. Cover it with the rest of the sauce and scatter the cheese over.
9. *gratinate* - Set the filled shells on a tray under a hot grill until the top is golden and bubbling. [3-5 minute]
10. *plate* - Serve at once, in the shells.

Your answer on the order, cues and method: OK / FIX / UNSURE - ________

### R2. Poulet à l'estragon (`recipe/poulet-a-l-estragon`)

Chicken pieces browned and then simmered with white wine, stock and tarragon, in a sauce finished with cream and fresh tarragon leaves.

Serves / makes: 4 serving

| Amount | Ingredient | Your answer (right / too much / too little) |
|---|---|---|
| 1.4 kilogram | chicken (jointed) | |
| 1 tablespoon | sunflower oil | |
| 20 gram | butter | |
| 2 piece | shallot (peeled, minced) | |
| 150 millilitre | white wine | |
| 200 millilitre | chicken stock | |
| 4 sprig | tarragon | |
| 150 millilitre | cream | |
| 1 teaspoon | salt | |
| 0.25 teaspoon | black pepper | |

**Steps:**

1. *sear* - Dry the chicken pieces and salt them. Brown them in the oil and the butter in a wide sauté pan, skin side down first, without moving them, then turn them. Lift them out. [10-12 minute]
2. *sweat* - Pour off all but a film of fat. Soften the shallots in it over low heat. [1-2 minute]
3. *deglaze* - Pour in the wine and scrape the pan clean. Boil until about half is left. [2-3 minute]
4. *simmer* - Add the stock and the stalks of the tarragon, and keep the leaves. Put the chicken back, skin side up, cover and simmer gently, taking the breast pieces out before the legs. Check the thickest part against a trusted guide to doneness. [20-25 minute]
5. *reduce* - Lift the chicken onto a warm dish and take out the stalks. Add the cream and boil the sauce down until it coats a spoon. [4-6 minute]
6. *season* - Chop the tarragon leaves and stir them in off the heat. Taste, season, and spoon the sauce over the chicken.

Your answer on the order, cues and method: OK / FIX / UNSURE - ________

### R3. Poulet vallée d'Auge (`recipe/poulet-vallee-d-auge`)

Chicken browned in butter, flamed with calvados and simmered in cider, finished with cream and served with apples fried in butter.

Serves / makes: 4 serving

| Amount | Ingredient | Your answer (right / too much / too little) |
|---|---|---|
| 1.4 kilogram | chicken (jointed) | |
| 60 gram | butter | |
| 2 piece | shallot (minced) | |
| 4 tablespoon | calvados | |
| 300 millilitre | cider | |
| 200 millilitre | cream | |
| 2 piece | apple (peeled, sliced) | |
| 1 teaspoon | salt | |

**Steps:**

1. *season* - Dry the chicken pieces well and salt them.
2. *sear* - Brown the pieces in half the butter in a wide, heavy pan, skin side first, until they are deep gold all over. Do it in batches if the pan is crowded. [8-10 minute]
3. *sweat* - Lower the heat, add the shallots and soften them in the fat without colour. [2 minute]
4. *flambe* - Take the pan off the heat and pour in the calvados from a ladle. Put the pan back, stand clear and set the calvados alight. Shake the pan until the flames die.
5. *deglaze* - Pour in the cider and scrape up everything stuck to the pan as it comes to the boil.
6. *simmer* - Cover the pan and simmer gently until the chicken is tender. Check the thickest part against a trusted guide to doneness. [25-30 minute]
7. *saute* - Meanwhile fry the apple slices in the rest of the butter in another pan, until they are golden on both sides and just tender. [5-6 minute]
8. *reduce* - Lift the chicken out and keep it warm. Add the cream to the pan and boil until the sauce coats the back of a spoon. [4-6 minute]
9. *season* - Taste the sauce and salt it.
10. *plate* - Coat the chicken with the sauce and arrange the apples around it.

Your answer on the order, cues and method: OK / FIX / UNSURE - ________

### R4. Filet mignon de porc à la moutarde (`recipe/filet-mignon-a-la-moutarde`)

Pork tenderloin browned in a pan, with a sauce of shallot, white wine and cream made on its fond and finished with mustard.

Serves / makes: 3 serving

| Amount | Ingredient | Your answer (right / too much / too little) |
|---|---|---|
| 500 gram | pork tenderloin (sliced) | |
| 1 tablespoon | sunflower oil | |
| 15 gram | butter | |
| 2 piece | shallot (peeled, minced) | |
| 100 millilitre | white wine | |
| 200 millilitre | cream | |
| 1.5 tablespoon | dijon mustard | |
| 0.75 teaspoon | salt | |
| 0.25 teaspoon | black pepper | |

**Steps:**

1. *sear* - Dry the thick slices of pork and salt them. Sear them in the oil and the butter in a hot pan until golden on both sides. Lift them out. [4-6 minute]
2. *sweat* - Soften the shallots in the fat left in the pan over low heat. [1-2 minute]
3. *deglaze* - Pour in the wine, scrape the pan clean and boil until about half is left. [2 minute]
4. *reduce* - Add the cream and boil until the sauce coats a spoon. [3-4 minute]
5. *simmer* - Put the pork and its juices back into the sauce and simmer very gently until it is done. Check the thickest part against a trusted guide to doneness. [3-5 minute]
6. *season* - Off the heat, stir in the mustard and the pepper. Taste. Do not let the sauce boil again, or the mustard loses its bite.

Your answer on the order, cues and method: OK / FIX / UNSURE - ________

### R5. Poulet sauté chasseur (`recipe/poulet-saute-chasseur`)

Chicken pieces browned in a sauté pan, then finished in a sauce made in the same pan from mushrooms, shallots, white wine, tomato and stock, with tarragon.

Serves / makes: 4 serving

| Amount | Ingredient | Your answer (right / too much / too little) |
|---|---|---|
| 1.4 kilogram | chicken (jointed) | |
| 1 tablespoon | sunflower oil | |
| 30 gram | butter | |
| 250 gram | mushroom (sliced) | |
| 2 piece | shallot (peeled, minced) | |
| 150 millilitre | white wine | |
| 2 piece | tomato (diced) | |
| 200 millilitre | chicken stock | |
| 2 sprig | tarragon (chopped) | |
| 1 teaspoon | salt | |
| 0.25 teaspoon | black pepper | |

**Steps:**

1. *sear* - Dry the chicken pieces and salt them. Heat the oil and the butter in a wide sauté pan. Brown the pieces skin side down first, without moving them, then turn them. Lift them out. [10-12 minute]
2. *saute* - Brown the mushrooms in the fat left in the pan over high heat, then lift them out too. [4-5 minute]
3. *sweat* - Pour off all but a film of fat. Soften the shallots in it over low heat. [1-2 minute]
4. *deglaze* - Pour in the wine and scrape the pan clean. Boil until about half of the wine is left. [2-3 minute]
5. *simmer* - Add the tomatoes and the stock, then put the chicken back, skin side up. Cover and simmer gently, taking the breast pieces out before the legs. Check the thickest part against a trusted guide to doneness. [20-25 minute]
6. *reduce* - Lift the chicken onto a warm dish. Put the mushrooms back and boil the sauce down until it coats a spoon. [3-5 minute]
7. *season* - Off the heat, stir in the tarragon. Taste, season, and spoon the sauce over the chicken.

Your answer on the order, cues and method: OK / FIX / UNSURE - ________

### R6. Côte de porc charcutière (`recipe/cote-de-porc-charcutiere`)

A pork chop seared and rested, with a sauce made in its pan from onion, white wine and stock, finished off the heat with mustard and strips of cornichon.

Serves / makes: 2 serving

| Amount | Ingredient | Your answer (right / too much / too little) |
|---|---|---|
| 2 piece | pork chop | |
| 1 tablespoon | sunflower oil | |
| 15 gram | butter | |
| 1 piece | onion (peeled, minced) | |
| 100 millilitre | white wine | |
| 150 millilitre | beef stock | |
| 1 tablespoon | dijon mustard | |
| 4 piece | cornichons (julienne) | |
| 0.5 teaspoon | salt | |
| 0.25 teaspoon | black pepper | |

**Steps:**

1. *sear* - Dry the chops and salt them. Sear them in the oil in a hot, heavy pan until deep golden on both sides, then lower the heat and cook them more gently. Check the thickest part against a trusted guide to doneness. [10-12 minute]
2. *rest* - Rest the chops on a warm plate, loosely covered. [5 minute]
3. *sweat* - Pour off the fat. Soften the onion in the butter in the same pan over low heat. [3-4 minute]
4. *deglaze* - Pour in the wine and scrape the pan clean. Boil until almost all of it has gone. [2 minute]
5. *reduce* - Add the stock and boil it down until the sauce coats a spoon. [4-5 minute]
6. *season* - Take the pan off the heat. Stir in the mustard, which must not boil, then the cornichons, the pepper and the juices from the resting chops. Taste.
7. *plate* - Serve the chops on warm plates with the sauce spooned beside them.

Your answer on the order, cues and method: OK / FIX / UNSURE - ________

### R7. Seared chicken thighs with lemon butter pan sauce (`recipe/seared-chicken-thighs-with-lemon-butter-pan-sauce`)

Chicken thighs seared skin side down until crisp, with a sauce made in the same pan from the browned bits, white wine, butter and lemon, and wilted spinach on the side.

Serves / makes: 2 serving

| Amount | Ingredient | Your answer (right / too much / too little) |
|---|---|---|
| 4 piece | chicken thigh | |
| 1 teaspoon | salt | |
| 1 tablespoon | sunflower oil | |
| 2 clove | garlic (minced) | |
| 120 millilitre | white wine | |
| 30 gram | butter (cold, diced) | |
| 0.5 piece | lemon | |
| 150 gram | spinach | |

**Steps:**

1. *sear* - Pat the thighs dry and salt both sides. Lay them skin side down in the hot oil and leave them alone until the skin is deep golden and lifts off the pan by itself. [7-8 minute]
2. *sear* - Turn the thighs, lower the heat and cook the other side. Check the thickest thigh against a trusted guide to doneness, then move them to a warm plate. [5-6 minute]
3. *sweat* - Pour off most of the fat and keep every brown bit. Stir the garlic in the pan just until it smells sweet. [30 second]
4. *deglaze* - Pour in the wine and scrape the pan with a wooden spoon until the brown bits have dissolved.
5. *reduce* - Let it boil until about half is left. [3 minute]
6. *mount with butter* - Take the pan off the heat. Whisk in the cold butter a few cubes at a time, then the juice of the lemon. The sauce turns glossy.
7. *season* - Taste, and add salt if it needs it. Pour the sauce into a warm jug.
8. *wilt* - Wilt the spinach in the same pan. [1 minute]
9. *plate* - Plate the spinach with the chicken, skin side up, and spoon the sauce around it.

Your answer on the order, cues and method: OK / FIX / UNSURE - ________

### R8. Bisque de homard (`recipe/bisque-de-homard`)

A smooth, coral-coloured soup made from lobster shells fried with vegetables, flamed with cognac, simmered in stock with rice to thicken it, then crushed, strained and finished with cream.

Serves / makes: 4 serving

| Amount | Ingredient | Your answer (right / too much / too little) |
|---|---|---|
| 1 piece | lobster | |
| 40 gram | butter | |
| 1 piece | onion (diced) | |
| 1 piece | carrot (diced) | |
| 1 tablespoon | tomato paste | |
| 3 tablespoon | cognac | |
| 150 millilitre | white wine | |
| 1 litre | fish stock | |
| 40 gram | rice | |
| 150 millilitre | cream | |
| 2 teaspoon | salt | |

**Steps:**

1. *boil* - Boil the lobster in plenty of well-salted water. Check the thickest part against a trusted guide to doneness. [8-10 minute]
2. *peel* - When it is cool enough to handle, take the meat out of the tail and the claws and keep it cold for the garnish. Break the shells and the head into small pieces.
3. *saute* - Fry the pieces of shell in the butter over a lively heat until they smell toasted. Add the onion and the carrot and cook until they start to colour. [6-8 minute]
4. *flambe* - Take the pot off the heat and pour in the cognac from a ladle. Put the pot back, stand clear and set the cognac alight.
5. *deglaze* - Pour in the wine and scrape the bottom of the pot as the wine boils down by half. [2-3 minute]
6. *simmer* - Add the stock, the tomato paste and the rice. Simmer until the rice is very soft. [25-30 minute]
7. *puree* - Blend the soup in short bursts, shells and all, until the shells are crushed and the rice has thickened it.
8. *strain* - Press it hard through a fine sieve with the back of a ladle. Strain it once more for a smooth soup.
9. *simmer* - Bring the soup back to a simmer, stir in the cream and let it thicken a little. [3-5 minute]
10. *season* - Taste it and salt it.
11. *plate* - Ladle the bisque into warm bowls and set the pieces of lobster meat in the middle.

Your answer on the order, cues and method: OK / FIX / UNSURE - ________

### R9. Œufs à la tripe (`recipe/oeufs-a-la-tripe`)

Hard-boiled eggs, sliced and warmed in a béchamel full of onions that have been sweated soft without colour.

Serves / makes: 4 serving

| Amount | Ingredient | Your answer (right / too much / too little) |
|---|---|---|
| 6 piece | egg | |
| 300 gram | onion (peeled, sliced) | |
| 40 gram | butter | |
| 30 gram | flour | |
| 500 millilitre | milk | |
| 1 pinch | nutmeg | |
| 0.75 teaspoon | salt | |

**Steps:**

1. *boil an egg* - Boil the eggs gently until the yolks are firm, then cool them under cold water. [9-10 minute]
2. *peel* - Peel the eggs and cut them into thick slices.
3. *sweat* - Sweat the onions in the butter with a little of the salt over low heat, covered, until completely soft. They must not colour. [15-20 minute]
4. *sprinkle with flour* - Scatter the flour over the onions and stir for a moment over the heat, without colour. [1-2 minute]
5. *simmer* - Stir in the milk a little at a time, and make each addition smooth. Simmer gently, stirring, until the sauce coats a spoon. Season with the rest of the salt and a little nutmeg. [8-10 minute]
6. *toss* - Fold the sliced eggs gently into the sauce, warm them for a moment and serve.

Your answer on the order, cues and method: OK / FIX / UNSURE - ________

### R10. Poires au vin rouge (`recipe/poires-au-vin-rouge`)

Whole peeled pears poached in sweetened, spiced red wine until tender and stained deep red, served cold in their syrup.

Serves / makes: 4 serving

| Amount | Ingredient | Your answer (right / too much / too little) |
|---|---|---|
| 4 piece | pear | |
| 750 millilitre | red wine | |
| 150 gram | sugar | |
| 1 piece | cinnamon | |

**Steps:**

1. *simmer* - Bring the wine, the sugar and the cinnamon to a simmer in a pan that will hold the pears snugly, and stir until the sugar has dissolved.
2. *peel* - Peel the pears and leave the stalks on. Cut a thin slice off each base so that they stand.
3. *poach* - Lower the pears into the wine and cover them with a round of paper. Poach at a bare tremble, turning them now and then, until the tip of a knife slides in with no resistance. [20-30 minute]
4. *reduce* - Lift the pears out. Boil the wine down until it is syrupy and coats a spoon. [10-15 minute]
5. *chill* - Pour the syrup over the pears and chill them, turning them once or twice so that they colour evenly. [4 hour]
6. *plate* - Serve each pear standing in a pool of its syrup.

Your answer on the order, cues and method: OK / FIX / UNSURE - ________

## Part 3: general questions

1. Which of these would a French home cook never do this way?
2. Which French dish or technique is missing from the list that you would expect in a first set?
3. Where did you feel the card was written for the nearest famous version and not for the whole family it names?

