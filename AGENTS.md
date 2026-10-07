# cooking-graph: rules for anyone writing here

This repository holds a knowledge graph of how the world cooks. This file is the steering document for people and coding agents. Read it before changing anything. If a rule here is wrong, change the rule in the same pull request, do not quietly ignore it.

The plan is in mrspacerobot/tomi#106.

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
- **`./numbers` gives the numbers** for a round's notes and a pull request: counts by kind and tier, and the share of probes answered, growing and held back apart.
- **A pull request that adds or changes content says how much and of what,** and lists what its author doubts.
- Commit subjects are in the imperative and name the issue. No co-author lines for agents.
- No secrets in the repository, ever.

## Style

- Words for people are warm, short and plain. Use a plain hyphen, never the em dash.
- Code is small and plain: one function, one job, names that say what, comments that say why. No clever one-liners.
- Until the stack is decided, tools use the Python standard library only. Nothing is installed.
