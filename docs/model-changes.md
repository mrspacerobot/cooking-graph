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
