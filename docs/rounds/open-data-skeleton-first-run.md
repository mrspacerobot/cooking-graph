# The open-data skeleton: Wikidata ids and names (first run)

Story 6 of `docs/backlog-draft.md`, and change 33 in `docs/model.md`. Tier of the things stays `drafted`. The new `same_as` rows are `sourced`.

## What was done

- The licence page of Wikidata was read again before the import: all structured data, which includes item labels, is released under CC0. `source/wikidata` says so and was updated to say what was taken.
- `./wikidata` asked the query service for items whose English label equals the primary English name of an ingredient, a preparation or a dish, and that are a food, a food ingredient, a type of food or dish, or a type of ingredient. The labels of those four classes were fetched and read, not remembered.
- A first run matched through aliases as well and took the wrong item for salt (sea salt), skate (ray), egg (whole egg) and mushroom (button mushroom). Matching now uses the primary English name only.
- 320 of 659 things matched an item and each got a sourced `same_as` row (396 sourced statements in all, with the 76 regulated rows before). 26 labels had more than one item and were skipped, as were 5 more for a shared id or a held name.
- Names were taken in Spanish, Italian, Turkish and French when they were a plain name: no brackets, no digit, no full stop, at most forty letters, in the Latin script, and not already held by another thing.

## What a person read and refused

A person (here, the agent running the import) read all 320 matches and the names they brought, and refused twelve names that were clearly wrong for their thing. They are in `schema/wikidata-refused.json` with a reason each, were removed from the files, and will not return. Examples: a Turkish word for scallop on the clam, a scientific name on wakame, an appellation on sherry vinegar, the tissue of the body on bone marrow. This is a reading by a model that knows Spanish and Italian better than Turkish, so more wrong names probably remain.

## Doubts

- Labels in Wikidata are written by volunteers, and nobody reviewed them. The names are drafted words on drafted things.
- A match is on a label, and the item may be a nearby sense (bone marrow as tissue and as food are one item). The id says "this is the Wikidata item with that name", not "this is the same in every sense".
- Casing follows Wikidata and is not uniform.
- Names in Japanese, Hindi, Arabic and Greek were not taken, because a name in another script must bring a romanization and Wikidata does not give one.
- 339 things had no match or were skipped. They are only counted here. The skip list is printed by `./wikidata --dry-run`.
- FoodOn was not used.

## Second pass: propose, read, choose

- 339 things had no id. `./wikidata --propose` asked for items of any class for their names and aliases and printed those whose description sounds like a food: 149 proposals for 107 things. It writes nothing.
- All 149 were read. 79 ids were chosen and are listed in `schema/wikidata-chosen.json`. The rest were refused for a reason that shows in the description: a colour, a stew with the same name, a work, a ship, the general
  kind when ours is a variety (crab for brown crab), a plant species when ours is the food, a British dish for a French one (cauliflower cheese), or two items that were equally good.
- 399 of 659 things now carry a sourced `same_as` row (475 sourced statements in all). Things stay drafted.
- Eight more names the reading found wrong were added to `schema/wikidata-refused.json` and removed: for example a species name on courgette, "el frijol ancho" for butter bean, and a Turkish word for cod on whiting.
  A species name written the same in two languages is now skipped by the tool.
- Doubts: a choice is a reading by a model, not a cook. Some ids point at the nearest sense (oil as vegetable oil, egg as whole egg). 260 things still have no id.
