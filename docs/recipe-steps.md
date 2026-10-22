# Writing recipe steps

The Tomi server adapts a recipe in code, never with a model. It swaps a food for a stand-in, scales amounts by the swap's
ratio, leaves out an optional part a cook cannot have, and checks the result again against the cook's diet and avoid list.
Free prose cannot be changed that way: "stir in the cold butter and the cream" still says cream after cream is left out.
So a step's `text` is written in a small format that code can read. `./check` enforces it.

## The format

| Write | Meaning |
|---|---|
| `{part}` | The food of the recipe line that fills `part`. The server writes the name of the food in use here |
| `{part.ingredient}` | The same, for a part that holds several different foods. `ingredient` is the slug of the food's id (`butter` for `ingredient/butter`) |
| `{part:plural}` | The plural of the food's name: `{part.ingredient:plural}` for a part with several foods. Use it where the original words are plural: `the {egg:plural} still look wet` |
| `[part: text]` | A clause: text that belongs only to the optional `part`. It stays when the part is kept and goes when it is left out |

Rules of the format:

- **Name a food of the recipe through its part, never in plain words.** `Melt the {butter}`, not `Melt the butter`. The check
  looks for every name and alias of every food on the recipe's lines (plural too: eggs is egg), in any language the graph
  knows, the longest name first, and rejects a plain mention.
- **The key is the `part` of the line, not the food.** `{enrichment}` stays right when cream is swapped for creme fraiche.
- **A part with several different foods needs `{part.ingredient}`.** A roux part that holds butter and flour is `{roux.butter}` and
  `{roux.flour}`. A part whose lines are all one food (two water lines) is just `{part}`. The same food in two parts
  (salt for the pasta water, salt for the sauce) is told apart by the part.
- **Only optional parts have clauses.** The dish says which parts are `optional`. A clause on a required part is rejected, since a
  required part is never left out.
- **A placeholder of an optional part stands only inside a clause of that part.** Anything else would stay in the text after
  the part is left out. A clause holds text and placeholders, never another clause.
- **The clause owns the space before it.** Write the space outside the brackets: `stir in the {butter} [enrichment: and the {enrichment}] to stop`.
  Kept, it reads "stir in the butter and the cream to stop". Left out, the clause and the space before it go: "stir in the butter to stop".
  A comma goes inside: `swell[garnish: , and scatter with the {garnish}].`
- **A step whose whole text is a clause** (`[sesame: Toast the {sesame} in a dry pan.]`) is dropped when the part is left out,
  with its time, temperature and safety points. The server drops any step whose rendered text is empty.
- **Sentence start:** a placeholder at the start of the text or after `. ` gets a capital letter. Anywhere else the first letter
  of the name is made small, except when the first word is a proper name (`Dijon`, `Parmesan`: the list is `PROPER_NAME_WORDS`
  in `tools/step_text.py`, also in the artifact).
- **`a` or `an` before a placeholder** is chosen again from the first letter of the name in use (`an {egg}`, `a {onion}` both come out right).
- **No other `{`, `}`, `[` or `]`** may appear in a text. The check rejects stray and unclosed brackets.
- Numbers, units and temperatures still never go in the text. Amounts are in the line, scaled by the server.

### Number

Every ingredient and preparation is either **uncountable** (butter, salt, rice, flour: `uncountable: true`, no plurals) or has a
**plural** of its name in each language it is named in (`plurals`: `{"en": "Eggs"}`). `./check` rejects a food that is neither.

- Write `{part}` where the sentence is about one or about a mass, `{part:plural}` where it is about several. "Crack the eggs" is
  `Crack the {egg:plural}`, "stir in the cold butter" is `stir in the cold {butter}`.
- With a swap the stand-in's own plural is printed. If the stand-in is uncountable, `{part:plural}` prints its name ("the eggs" becomes "the tofu").
  Write the sentence so that its verb reads for both: prefer "until the {egg:plural} set" over "until the {egg:plural} are firm".
- A plural placeholder of a line whose own food is uncountable is rejected (`step-plural-of-uncountable`): there is nothing to make plural.
- `a` or `an` before a plural placeholder is rejected (`step-article-before-plural`). Write `the` or nothing.
- A plural placeholder directly followed by `is`, `has`, `was` or `does` is rejected (`step-number-disagrees`). The reverse (a singular
  placeholder followed by `are`) is not checked, because "the {onion} and the {carrot} are tender" is right.
- Names that the graph writes in the plural (Peas, Capers, White beans) have the same plural. Use `{peas:plural}` there and `are` after it.

### Write so that it reads for any food

- Do not use a food as a verb: `Season them with the {salt}`, not `{salt} them`; `Rub the dish with the {butter}`, not `{butter} the dish`.
- Keep a modifier next to the placeholder when it matters: `cold {butter}`, `thin {thin-milk}`.
- Do not describe what the food is: `the {bay-leaf} leaves` renders "bay leaf leaves". Write `the {bay-leaf:plural}` or `the {bay-leaf}`.
- Reserved water ("the cooking water", "the soaking water") is a mention of the water line if the recipe has one: write `{water}`
  or the part that holds it, and do not call a mention of the tomato's own moisture "water".
- When a list holds an optional food, put the separator in the clause: `{onion}[carrot: , {carrot}] [celery: and {celery}]`.
  When two optional parts share a sentence and the sentence would not read with either left out, split it into one sentence per
  part: `[parsley: Scatter over the {parsley}.] Serve [lemon: with the {lemon} cut in wedges].`

## Example: soft scrambled eggs

Before (`recipe/soft-scrambled-eggs`, step 3):

```
While the eggs still look wet and loose, take the pan off the heat and stir in the cold butter and the cream to stop the cooking. Serve at once on warm plates.
```

After:

```
While the {egg:plural} still look wet and loose, take the pan off the heat and stir in the cold {butter} and the {enrichment} to stop the cooking. Serve at once on warm plates.
```

With cream swapped for creme fraiche the server renders "...stir in the cold butter and the creme fraiche to stop the cooking...".
In this dish `enrichment` is a required part, so it has no clause. For an optional part, here is salmorejo's boiled egg, where the whole
step goes when `egg` is left out, and the tail of the finishing step:

```
"[egg: Crack and peel the cooled {egg}.]"
"[egg: Scatter over the chopped {egg}.] [ham: Scatter over the {ham}.] Finish with a thread of {oil}."
```

## What the server does

1. Parse the text: `{...}` placeholders, `[part: ...]` clauses, everything else is literal.
2. For each clause whose part is left out, delete it and the whitespace right before it. For a kept clause, remove only the brackets and the header `part: `.
3. For each placeholder, find the recipe line(s) of the part (and the ingredient slug, if given). Take the food the cook uses for that line:
   the original, or its stand-in. Write its English name, or its English plural for `:plural` when the food is countable (an uncountable food prints its name), with the capital and article rules above.
4. If a step's text is now empty, drop the step.
5. Scale each line's amount by the swap ratio (the amounts are in the lines, never in the text) and check the whole recipe against the cook's
   diet and avoid list again before showing it.

`tools/step_text.py` (parser and renderer) and `tools/recipe_text.py` (a recipe's steps for chosen swaps and left-out parts) are the
reference. The release writes `step_text_cases` into `serving-vectors.json`: for every recipe, the text as written, with each optional
part left out, and with every swappable line swapped. A server that renders the same text for every case agrees with the reference.
`serving.step_text.proper_name_words` in the artifact is the capital list.

## What `./check` rejects

| Rule | Example |
|---|---|
| `step-text-malformed` | `Melt the {butter` , a stray `]`, a clause inside a clause |
| `step-part-unknown` | `{cheese}` in a recipe with no line for the part `cheese` |
| `step-ingredient-unknown` | `{roux.cream}` when no line of `roux` is cream |
| `step-ingredient-ambiguous` | `{roux}` when the part holds butter and flour: write `{roux.butter}` |
| `step-plain-ingredient` | `stir in the cream` when a line holds cream: write `{enrichment}` |
| `step-plural-of-uncountable` | `{butter:plural}` when butter is uncountable: write `{butter}` |
| `step-article-before-plural` | `a {egg:plural}` |
| `step-number-disagrees` | `the {egg:plural} is firm`: write `are` |
| `step-optional-unmarked` | `scatter the {parsley}` when `parsley` is optional: write `[parsley: scatter the {parsley}]` |
| `step-clause-on-required-part` | `[enrichment: and the {enrichment}]` when `enrichment` is required |

Known limits: only names and aliases of a food are looked for, so a short form ("the oil" for olive oil, "the pepper" for black
pepper, "the paste") is not caught. Write it as a placeholder anyway. The plurals in French, Spanish, Italian and Turkish were drafted by rule and are not reviewed by a native speaker.
