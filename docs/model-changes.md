# Changes to the starting model

The starting model is the one in mrspacerobot/tomi#106: nine kinds, ten statements, the id rule and five tiers. This log holds every place where real content did not fit it, with the example that forced the change. It becomes part of `docs/model.md`.

What counts as a change: a change to `schema/model.json`, which is the model as the checker reads it. That is a kind, a field, a statement, what a statement may point at, or the file a statement is kept in. A new word in a closed list (`schema/words.json`: a unit, a role) is a change to the vocabulary, not to the model. Vocabulary changes are listed in each round's notes.

## Changes

### 1. A tenth kind: fact (round 0)

- **Example:** butter contains dairy (Tomi's ingredient table).
- **What did not fit:** "contains" needs something to point at. Dairy is not an ingredient, a form, or any other of the nine kinds, yet it needs an id that never changes, names, and a sentence that says what it covers.
- **Now:** `graph/fact/` holds one file per safety fact, with `means`. The thirteen facts are Tomi's.

### 2. "Contains" is a safety record, not a statement with a tier (round 0)

- **Example:** olive oil, written `"contains": []` in Tomi's table. And white wine, which holds a slaughter product.
- **What did not fit:** a statement per fact leaves no row for "holds nothing", and "nothing" is a claim that needs verifying as much as "dairy" does. A safety fact has two states of its own, not five tiers. And white wine holding a slaughter product cannot be reviewed without its reason.
- **Now:** every ingredient has one `safety` record: a `state` (unverified or verified), the facts it `contains`, the facts it is `free_of`, and a `note`. Every fact of the graph must be in one of the two lists. A fact added later is unanswered in every older record, and the check fails until each is answered. Nothing is read as "free of" by default.

### 3. "Contains" starts only from an ingredient (round 0)

- **Example:** the spinach and cheese omelette of Tomi's lesson.
- **What did not fit:** writing "contains egg and dairy" on the dish repeats what egg and butter already say, and the two can come to disagree. The epic's own example, "most dashi contains fish", is a fact about what dashi is made of.
- **Now:** only ingredients carry safety facts. What a preparation, a dish or a recipe holds follows from its ingredients, through every option of every part. Two rules keep that sound: a recipe may use nothing its dish does not name as a part, and an ingredient that stands for a class (stock) holds every fact its members hold (chicken stock, vegetable stock).

### 4. "Is part of" is not stored for a part of a dish (round 0)

- **Example:** butter in the omelette.
- **What did not fit:** "butter is part of the omelette" is the same fact as "the omelette uses butter", read from the other end. Kept in the file of the thing it starts from, butter's file would list every dish that uses butter, and each of those would say it again.
- **Now:** the fact is kept once, in the whole: a dish or a preparation lists its `parts`. The other direction is a query.

### 5. "Comes before" is kept in the later thing, as comes after (round 0)

- **Example:** in Tomi's catalog, stocks names knife cuts as what comes first.
- **What did not fit:** what a thing builds on is known when it is written. Kept in the earlier thing, the earlier file must be opened again every time something new builds on it.
- **Now:** a technique and a skill of a program say what they `comes_after`, each with a `why`. The other direction is a query.

### 6. A level says what it is practised through (round 0)

- **Example:** the three levels of braise: braised leeks, chicken in wine, beef in red wine.
- **What did not fit:** all three teach braising. With `teaches` alone they are the same level three times.
- **Now:** a level has `teaches` (techniques) and `through` (the dishes or preparations it is practised on).

### 7. A technique needs more than equipment (round 1)

- **Example:** poaching an egg needs water held just under a simmer, and a little vinegar. Scrambling needs butter.
- **What did not fit:** the starting model's "needs" names a tool or a vessel: "stir-frying needs a wok or a wide pan". Many moves cannot be done without a liquid, a fat or an acid, and that is neither what the move works on nor a tool.
- **Now:** a need has a `role` from a closed list (vessel, tool, heat, liquid, fat, acid, seasoning) and `options` that may be equipment, ingredients or preparations.

### 8. A technique can make a preparation, not only a form (round 1)

- **Example:** making a roux makes a roux.
- **What did not fit:** "makes" pointed at a form, a state food is left in. A roux is not a state of flour. It is a building block with parts of its own.
- **Now:** `makes` points at a form or a preparation.

### 9. A form can have a size (round 1)

- **Example:** brunoise.
- **What did not fit:** a classic cut is defined by its size, and no number may stand in a sentence. `looks_like` alone cannot say how small.
- **Now:** a form has `size`: a list of a `measure` (side, width, length, thickness) and a `length` with a unit. It is empty for a form that has no fixed size.

### 10. An ingredient can be part of another (round 1)

- **Example:** egg yolk, in steak tartare.
- **What did not fit:** a yolk is not a kind of egg, so `is_a` would be false. Without any link, a kitchen that holds eggs could not be told it holds yolks.
- **Now:** an ingredient has `part_of`. This is the starting model's "is part of", back with a narrower meaning than in change 4: a part or a cut of one ingredient. The whole holds every safety fact its parts hold, and the check enforces it.

### 11. A preparation teaches too (round 1)

- **Example:** white chicken stock teaches skimming. Mirepoix teaches dicing.
- **What did not fit:** "teaches" started from a dish. Three of Tomi's twelve skills are taught on preparations: the stocks, the roux and the emulsions.
- **Now:** a preparation has `teaches`, like a dish.

### 12. A recipe can make a preparation (round 1)

- **Example:** white chicken stock.
- **What did not fit:** a recipe was "one way to make a dish". A stock is not served, yet it is the thing a cook most needs a recipe for.
- **Now:** a recipe `makes` a dish or a preparation. A recipe may also list a preparation among its ingredients, made ahead by its own recipe. A step may work on the thing its recipe is making, so that a stock can be strained and cooled.

### 13. An ingredient line says what form the ingredient is in (round 1)

- **Example:** the cheese of the omelette is grated. The celeriac of céleri rémoulade is peeled and cut in julienne.
- **What did not fit:** a line had a thing and an amount. A cook reads "one onion, diced", and the starting model had forms but no place where a recipe uses one.
- **Now:** a line has `forms`: the states the ingredient is in before the first step, in the order they are done. A step is still used for a cut when the cut is what the dish teaches.

### 14. A step can mark where a safety fact is needed (round 1)

- **Example:** steak tartare serves beef and egg yolk raw. Soft scrambled eggs stay runny. A stock must be cooled fast before it is kept. And Tomi's chicken lesson says "cooked through", which the graph may not say.
- **What did not fit:** no text may claim food is cooked through or safe to eat, and no safe temperature or time may be given. But a recipe that says nothing at the point where it matters is worse. The model had no way to say "a verified fact belongs here".
- **Now:** a step has `safety_points`, from a closed list: `doneness`, `raw-meat-or-fish`, `raw-or-lightly-cooked-egg`, `cooling-and-keeping`. A point claims nothing. It marks the place where an export must put a fact a person has verified, and a recipe with an open point cannot be exported.

### 15. A step says what it leaves behind (round 2)

- **Example:** steak au poivre. Searing leaves a fond on the pan, and the next step deglazes it. Round 1 had met the same thing twice already: the broth of the pot-au-feu and the bacon fat of the salade lyonnaise.
- **What did not fit:** a step could work only on what the recipe lists. A fond is not bought and has no amount. Yet it is the thing a pan sauce is made of, and "deglazing works on the fond" is the centre of that skill.
- **Now:** a step has `makes`: the preparations it leaves behind. A later step may work on them. Such a by-product (fond, pan sauce, broth, rendered fat) is a preparation with no parts of its own. Because it has no ingredients to answer for it, the check refuses it as an ingredient of a recipe and as a part of a dish or of another preparation: what a dish holds must always be found by following parts down to ingredients.

## Decisions where the starting model was silent

These are not changes. The starting model names kinds and statements, not files, so the first files had to settle them.

- **A statement is a field of the thing it starts from,** named after the statement and holding one row per thing it points at: `{"thing": ..., "tier": ...}`, with whatever the statement adds (`why`, `differs`, `when`).
- **Every field is always written.** An empty list is `[]`. `null` is allowed only where the model says so.
- **Names are one name per language tag,** English required. A name in another script brings its romanization under `<tag>-Latn`. Other names are `aliases`, by language.
- **"Is the same move as" is not a statement.** The same move under another name is one technique with two names. What differs makes it a variant: `variant_of` with `differs`.
- **Nothing is above drafted, and no safety record is verified, until a review can be put on record.** The epic asks for who, when and against what on every tier. No such record exists yet, so the check refuses any tier above drafted. That rule goes when the record comes.
- **A number is `{"value", "unit"}` or `{"from", "to", "unit"}`,** with the unit from the closed list the field names.
- **A stand-in names its context** as `when` and `not_when`: techniques, preparations or dishes. An empty `when` means no context is known to matter.
- **Ids of public datasets are not built.** Nothing in this slice came from one.
- **Probes are files too,** outside the graph, in `probes/`. A probe has a batch and a set. Which probes of a batch are held back follows from their ids by a rule in `tools/probes.py`. Nobody picks.
