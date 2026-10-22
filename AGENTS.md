# cooking-graph: rules for anyone writing here

This repository holds a knowledge graph of how the world cooks. This file is the steering document for people and coding agents. Read it before changing anything. If a rule here is wrong, change the rule in the same pull request, do not quietly ignore it.

The plan is [issue 2](https://github.com/mrspacerobot/cooking-graph/issues/2).
Progress and next work are in `docs/handover.md`; the active first slice is
[issue 3](https://github.com/mrspacerobot/cooking-graph/issues/3), and repository
setup is [issue 4](https://github.com/mrspacerobot/cooking-graph/issues/4).
Follow-up work is [cycle two, issue 5](https://github.com/mrspacerobot/cooking-graph/issues/5)
and [content review, issue 6](https://github.com/mrspacerobot/cooking-graph/issues/6).
Keep work tracking in this repository so a colleague needs access to no other one.

## What the graph is

- **The graph knows no customer.** No level, no XP, no drawing and no screen belongs in it. An app takes a slice of it through an export.
- **Know-how is at the centre.** Techniques first. Dishes and recipes hang off them.
- **A statement holds in a context.** Ghee stands in for butter when frying, not when mounting a sauce. Say the context.
- **Local knowledge keeps its name and its difference.** A regional technique is never flattened into its nearest French cousin. A variant says what differs.

## Content is data

- **One JSON file per thing,** in a folder for its kind: `graph/<kind>/<slug>.json`. Probes live apart, in `probes/`.
- **The model is `schema/model.json`,** with its closed word lists in `schema/words.json`. The checker reads them and nothing else decides what a file may hold. A change to `schema/model.json` is a change to the model: log it in `docs/model.md` with the example that forced it, in the same commit. `./check` fails when `docs/model.md` does not name a kind or a field of the model.
- **Files are read strictly.** An unknown field is an error. A missing field is an error. A reference to something that does not exist is an error.
- **Files are written one way.** `./tidy` rewrites them, and `./check` fails on a file written another way.
- **Ids are permanent.** An id is its kind and an English slug, lowercase, such as `technique/deglaze`. Never rename or reuse one.
- **Names travel with the thing,** in every language they are known in, English required. A local name is kept in its own script with a romanization.
- **Numbers are data.** An amount, a time or a temperature is a number with a unit from a closed list, never words in a sentence.

## The tier tells the truth

Every thing and every statement carries one tier:

| Tier | Meaning |
|---|---|
| drafted | A model wrote it |
| sourced | It is taken from a named reference that a person can open |
| reviewed | A reviewer who knows that cuisine approved it |
| verified | Confirmed a second time, by another reviewer or a test cook |
| cook-tested | Results from real cooks back it |

- Nothing is marked higher than it earned. A model alone never raises a tier above sourced.
- **Safety fails closed.** A safety fact (an allergen, an animal product, alcohol) is unverified until a person checked it against an authoritative source. Nothing unverified is ever exported.
- **Only an ingredient carries safety facts, and it answers every fact,** as `contains` or `free_of`. What a dish holds follows from its ingredients and is never typed. When unsure, the stricter answer is recorded.
- **Certain and strict are kept apart.** Each fact an ingredient holds says on what basis, and whether it is certain or recorded strictly because unsure. The owner rules on how strict to be. `docs/strict-answers.md` lists the strict ones.
- **A regulator's list is never written from memory.** Fetch the page, record it as a `source` with the day it was read and its reuse terms as stated there, and take the names it uses. A fact may be sourced only when its page was fetched and the entry is on it. A page that cannot be fetched is left out and reported.
- **A safety probe is never settled by editing either side.** `./safety` lists where a probe and the graph disagree. A person rules, unless a fetched page settles it.
- No text may claim that food is cooked through or safe to eat.

## Where knowledge may come from

- A model's own draft, marked drafted.
- Open data whose licence allows commercial use, with the licence checked at its source and recorded as a `source`. Nothing share-alike or unclear is imported, and no product data.
- A reviewer.
- **Never** scraped recipes, research-only datasets, or text copied from a book or a website. A reference is cited for its facts. The wording is our own.

## How we work

- **Only the owner merges into `main`.** An agent works on a branch, pushes it, opens a pull request and stops. Never push to `main`, never merge, never rewrite its history.
- **Tests first** for every tool. A rule of the checker has a test with a file that breaks it.
- **`./check` must pass** before anything is called done. Report honestly: if it fails or a step was skipped, say so.
- **The model that drafts the graph writes no probes.** A probe says who wrote it. Fresh probes come from another writer who cannot see `graph/`.
- **A technique works on groups,** not on a list of ingredients. A group is narrow enough that the card is true for every member.
- **The graph grows against probes.** `./probe` lists what the growing probes lack. One probe in five is held back by a rule, not by a person. Never write a dish, a name or an alias to please a held-back probe: `./probe` does not show what they lack, and it must stay that way.
- **A new food arrives with its swaps.** When you add an ingredient or a preparation and the graph holds no stand-in row for it, in either direction, do not leave it bare. Query a model for good stand-ins, and for the swaps a cook would wrongly assume, each with its context (a technique first; a preparation or a dish only where the swap does not hold across the technique), a ratio only where one is known, and a caveat. For a batch use two blind drafters and `./stand-in-merge`; for one or two foods a single query is enough. The rows are `drafted` and are listed among the doubts in the pull request. A model's rows never rise above `drafted`, and the model is never shown a held-back probe. This is drafting work done once and offline, never a model call when a cook asks. A recipe line whose part has one option and no swap is the same gap. `./swap-gaps --new` lists foods with no row at all; it reports and does not fail `./check`.
- **Recipe steps name foods only through placeholders.** The Tomi server swaps foods and leaves out optional parts in code, never with a model, so a step's `text` is written in the format of `docs/recipe-steps.md`: a food of a recipe line is `{part}` (or `{part.ingredient}` when the part holds several foods), never its name in plain words, and `{part:plural}` where the sentence is about several; text that applies only to an optional part sits in a clause `[part: ...]`. Every ingredient and preparation is `uncountable` or has a `plurals` entry per language of its names, so a new food comes with its plural. `./check` rejects a plain-word mention of a line's food, a placeholder for a part the recipe lacks, optional-part text that is not marked, a food with neither a plural nor an uncountable mark, and a plural of an uncountable food. Anyone drafting a recipe, human or model, writes steps this way from the start.
- **`./numbers` gives the numbers** for a round's notes and a pull request: counts by kind and tier, and the share of probes answered, growing and held back apart.
- **A pull request that adds or changes content says how much and of what,** and lists what its author doubts.
- Commit subjects are in the imperative and name the issue. No co-author lines for agents.
- No secrets in the repository, ever.

## Style

- Words for people are warm, short and plain. Use a plain hyphen, never the em dash.
- Code is small and plain: one function, one job, names that say what, comments that say why. No clever one-liners.
- Until the stack is decided, tools use the Python standard library only. Nothing is installed.

## Showing the graph in a browser

- **Human approvals have their own page, `out/site/approvals.html`.** It may display unverified ingredient safety assertions explicitly as evidence awaiting human review. Keep them out of the reading notebook and production exports. Only a human decision with evidence and the native review hash may back an approval. `./review apply <file>` validates an approval file and prepares graph changes on a branch; the owner confirms the human author and merges. Ratings, reading progress and an agent's tests never earn a factual tier or safety verification. Reviewer scopes explicitly authorized by the owner may use `owner-authorized`; do not invent experience or safety authority.

- **Keep website discovery consistent with the tools.** Technique recipe lists use `./recipes` rules, including variants and teaching order. Preparations must remain navigable. Browser progress markers are personal reading progress for an exact content hash; they never imply submission, shared progress, culinary approval or safety verification.

- **For editorial feedback, `./review-site` builds `out/site/index.html`.** This separate notebook lets an invited reviewer read foundation classes, techniques, recipes and substitution claims and prepare GitHub issues with ratings and suggestions. Recipe swaps use the existing `./stand-ins` engine; preserve context, exclusions, ratio and caveat, and keep missing knowledge separate from an explicit exclusion. It is a draft review surface, never a production export or cooking guide. Keep the draft and safety warning visible, omit ingredient safety assertions and probes, and preserve tiers. Feedback never promotes a tier or verifies safety. See `docs/review-website.md` for Pages setup and access requirements.

- **For a visual walkthrough, run `./view` from the repository root** after reading this file and `docs/handover.md`. It rebuilds `out/graph.html` from the current working files and opens the default browser. The owner asked for this direct clone-and-open path; use it when a colleague asks to see or explore the graph.
- **The page works independently of the agent.** It has no review session to keep alive or end. The colleague can keep exploring after your turn finishes and give feedback in the conversation.
- **No Lavish, package installation or application server is needed.** The generator uses Python's standard library. The owner's interactive viewer uses pinned browser-only CDN libraries: force-graph 1.52.0, DaisyUI 5.5.19 and Tailwind's browser runtime 4.2.4. This does not change the stack of the graph tools.
- **If automatic opening is unavailable, run `./view --no-open`** and open the printed HTML path with the available browser. Report the actual outcome; creating a file is not proof that a browser opened.
- **Never hand-edit `out/graph.html`.** Change `viewer/` or the generator in `tools/viewer.py`, then rebuild. Keep generated pages and local captures out of commits.
- **Show graph records only, never probes.** Preserve the tier, safety warning and context of every claim. Positions in a force layout are not evidence that ingredients are interchangeable. Keep the readable connection list alongside the canvas.
