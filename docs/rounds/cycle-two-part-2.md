# Cycle two, part 2: the allergen list, from real sources

Written on 7 October 2026. Everything here is a model's work and nobody has reviewed it. Every safety record is unverified.

## What was fetched, and what was not

No list was written from memory. Each place below has a `source` file with the address, the day it was read and its reuse terms as stated there.

| Place | Page that was read | How |
|---|---|---|
| European Union | Regulation 1169/2011, Annex II, consolidated text of 1 January 2018 | From the Publications Office, which serves the same text as EUR-Lex. EUR-Lex itself answered every request with a robot check |
| United Kingdom | Food Standards Agency, food allergy and intolerance advice for consumers | Direct download. The agency's own site now forwards to this page on gov.uk |
| United States | FDA, Food Allergies | Direct download |
| Canada | Health Canada, Common food allergens | Through the fetch tool only. The site refused a direct download, so the eleven names were read twice the same way and never from the raw page |
| Canada | Food Inspection Agency, on gluten-free statements | Direct download. Only for which cereals count as a gluten source |
| Australia and New Zealand | FSANZ, Allergen labelling for consumers | Direct download |
| Japan | Consumer Affairs Agency, the leaflet "What allergen labelling is", as of April 2026 | Direct download of a PDF in Japanese. See below |
| Codex | General Standard for the Labelling of Prepackaged Foods, as amended up to 2010 | Direct download of an older PDF. The current standard answered 403 |

**Not fetched, and so not recorded:**

- **What Codex says today.** Only the text amended up to 2010 could be read. Its rows are in the graph at tier drafted, each with a note that says so. The standard has a newer text that was refused.
- **EUR-Lex's reuse terms.** Its copyright notice sits behind the same robot check. The source says "unclear" for commercial use. Only the names of the 14 entries and their exemptions were taken.
- **The exemptions of Canada, Australia and New Zealand, and Japan.** The pages read state none. FSANZ keeps its product exemptions on another page, which was not read.

**The Japanese leaflet.** The agency's page shows the lists as a picture, and its PDFs are protected: a reader opens them with an empty password, and their own settings allow text to be taken out. No tool may be installed here, so a scratch script of standard-library Python opened the file the way a reader does and read the text. The English leaflet on the same site still shows the older list, eight mandatory and 20 recommended. The Japanese leaflet of April 2026 has nine mandatory, with the cashew nut moved up, and 20 recommended, with the pistachio added. The graph follows the Japanese one. The English names beside the Japanese ones are ours.

**Reuse.** Four of the eight pages allow commercial use with the source named: the United Kingdom, the United States, Australia and New Zealand, and Japan. Canada's two pages and the FAO site allow non-commercial use only without written permission. EUR-Lex is unclear. Nothing but the names of the entries was taken from any of them, as facts, and no sentence was copied.

## The facts

There are 21 facts: 16 allergens, all at tier sourced, and the five diet facts, kept as they were and still drafted.

| Old id | What replaces it |
|---|---|
| `fact/nuts` | `fact/peanuts` and `fact/tree-nuts` |
| `fact/shellfish` | `fact/crustaceans` and `fact/molluscs` |
| `fact/dairy` | `fact/milk` |
| `fact/gluten` | Kept. `fact/wheat` is new beside it |

New: `fact/wheat`, `fact/celery`, `fact/mustard`, `fact/sulphites`, `fact/lupin`, `fact/buckwheat`.

The facts carry 85 rows that say where they are regulated: 76 sourced and 9 drafted, the nine being those of the Codex text.

| Place | Rows |
|---|---|
| European Union | 14 |
| United Kingdom | 14 |
| Canada | 13 |
| Australia and New Zealand | 13 |
| Japan | 7 mandatory, 5 recommended |
| United States | 10 |
| Codex, the text of 2010 | 9 |

Decisions taken while building them, each for the owner to overrule:

- **Wheat stands beside gluten.** The United States, Canada, Australia and New Zealand and Japan list wheat. Europe, the United Kingdom and Codex list the cereals that contain gluten. One fact could not say both truthfully, and a cook who avoids wheat is not the cook who avoids gluten.
- **Buckwheat is a fact,** because Japan makes it mandatory. No ingredient holds it yet.
- **An item that only Japan recommends gets no fact:** orange, kiwi fruit, beef, chicken, banana, pork, peach, yam, apple and gelatin. They are named in the Japanese source. Pork is a diet fact already.
- **Where a place names single foods, the fact is the class** and the row says so: Japan's shrimp and crab under crustaceans, its walnut and cashew under tree nuts, its salmon, mackerel and salmon roe under fish.
- **Sulphites have a row for the United States,** though they are not one of its nine major allergens: the page says they must be declared from 10 parts per million.
- **`fact/milk` and not `fact/dairy`,** because every list says milk. Dairy is an alias.
- **The diet facts were not touched,** as asked. `fact/animal-product` still says "shellfish" and "dairy" in its sentence.

## The ingredients

All 137 ingredients answer all 21 facts again. 81 hold at least one fact. Each fact held now says on what basis, and whether it is certain.

| | Count |
|---|---|
| Facts that ingredients hold | 173 |
| Certain | 87 |
| Strict: recorded because a common form of the ingredient may hold it | 86 |
| Ingredients with at least one strict answer | 28 |

`docs/strict-answers.md` lists the 86 by fact and reason. The check keeps it equal to the files. The largest groups, in the words of the reasons:

- **What clears wine and beer:** egg white, milk protein, isinglass from fish, gelatine. It reaches the three wines, the two wine vinegars, Dijon mustard and beer. Europe exempts isinglass and fish gelatine used this way from fish labelling. The stricter answer is recorded all the same, and the exemption is on the fish fact.
- **Sulphites:** the wines, the vinegars, mustard, beer, pickles and fresh sausage. All ten answers are strict.
- **Bought stock:** wheat, gluten and celery in all five stocks.
- **Bread of unknown kind:** wheat, milk, egg, sesame, soy, tree nuts and lupin.
- **Cured and minced pork:** milk in bacon, ham and sausage, celery in ham, and wheat, soy and sulphites in sausage.

**The rule of thumb that was used.** A fact is recorded strictly when a common form of the ingredient, as sold, holds it. A rare form is not chased: pasta is not given lupin, bread is not given peanuts, bacon is not given celery. This rule is the drafter's own and is the first thing to rule on.

Answers that changed beyond the split of the old facts:

- White wine now holds egg and milk strictly, as red wine did. Tomi's row had neither. All wines and beer now hold fish strictly, through isinglass.
- Celery and celeriac hold celery, and Dijon mustard holds mustard. Their notes used to say that the graph had no fact for it.
- Cornichons hold mustard strictly, for the seed they are often pickled with.
- Gruyère and reblochon hold a slaughter product strictly and no longer for certain: a cheese sold under the name may be made with another rennet. Parmesan stays certain.

## The open databases

A short look, as asked. Nothing was imported. Each has a `source` file.

| Database | Licence as stated there | Commercial use without sharing alike | What it would give |
|---|---|---|---|
| FoodOn | CC BY 4.0 | Allowed, with attribution | Names of foods and what they come from. A search found 24 allergen terms, among them labelling classes named after the European entries. Whether it ties a generic ingredient to an allergen was not checked |
| USDA FoodData Central | Public domain, CC0 1.0 | Allowed | Nothing for this purpose. Neither its API guide nor its download page mentions allergens |
| Wikidata | CC0 for structured data | Allowed | Nothing ready. A search of its properties for the word allergen returned none |
| Open Food Facts | Open Database License, share-alike | Not without sharing alike | Nothing we may use, and it is product data |

**Recommendation, not done:** none of them gives allergen facts for a generic ingredient that could be imported as they stand. FoodOn is the one worth a second look, as a check on the reasons ("a milk product", "a fish") and not as a source of answers.

## The safety probes

The runner is built and tested: `./safety`. For a probe whose dish is in the graph and has a recipe, it works out what the dish holds from the ingredients of the recipe and compares that with what the probe says. A dish that is not in the graph is not answerable and is not counted as wrong. `./safety disagreements` writes `docs/safety-disagreements.md`, with both sides of every disagreement of a growing probe.

There is no safety probe in the repository yet. The first batch arrives with the fresh probes, so the document holds an empty table for now.

## The model

Five changes, logged in `docs/model.md` as 22 to 26: the kind `source`, what a fact concerns and where it is regulated, the basis and certainty of what an ingredient holds, the tier sourced for a fact, and the note beside the sentence.

Vocabulary: four new lists in `schema/words.json`. `concerns` (allergen, diet), `places` (the seven), `standings` (mandatory, recommended) and `commercial_uses` (allowed, share-alike, not-allowed, unclear).

New rules of the check: regulated-twice, bad-date, bad-url and not-current. The tests of the tools went from 161 to 200.

## What does not fit yet

- A fact inside a fact: walnut within tree nuts, shrimp within crustaceans.
- A level: every list counts sulphites from a set level, and an ingredient can only hold the fact or not.
- An exemption that fits one ingredient: the wine cannot point at the row that exempts its isinglass.
- A word of a probe that covers more than one fact, such as shellfish. The runner sets such a word apart as naming no fact.
