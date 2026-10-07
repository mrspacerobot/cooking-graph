# cooking-graph

A knowledge graph of how the world cooks: the techniques, what they work on, the cues, the mistakes, what to learn first, and how one move shows up in different cuisines.

It is private. `cooking-graph` is a working name.

## Status

Night one is done: the first slice, the 12 French skills the Tomi app teaches today. Read `docs/night-one.md` first.

Everything in this repository was drafted by a model and reviewed by nobody. Safety facts are unverified. Nothing here may be shown to a cook or exported to an app.

## What is where

| Place | What it holds |
|---|---|
| `graph/<kind>/<slug>.json` | The graph: one file per thing |
| `graph/source/` | The pages a fact was read in, each with the day it was read and its reuse terms |
| `probes/dish-probe/` | The dish probes: well-known dishes the graph must be able to express |
| `probes/safety-probe/` | The safety probes: what a well-known dish holds and does not hold |
| `probes/stand-in-probe/`, `probes/kitchen-probe/` | Independent question probes, with one in five held back by the hash rule |
| `schema/model.json` | The model: every kind, its fields and what each may hold |
| `schema/words.json` | The closed word lists: tiers, units, roles |
| `tools/`, `tests/` | The commands and their tests. Python standard library only |
| `docs/model.md` | The model in words, and every change to the starting model with the example that forced it |
| `docs/night-one.md` | The report of the first night: what to open first, the numbers, the doubts, the open questions |
| `docs/strict-answers.md` | Every answer that an ingredient holds a fact strictly and not for certain. Written by `./safety strict` |
| `docs/safety-disagreements.md` | Where a safety probe and the graph disagree, with both sides. Written by `./safety disagreements` |
| `docs/rounds/` | The numbers and notes of each round |

## Commands

| Command | What it does |
|---|---|
| `./check` | Runs the tests of the tools, then reads every file strictly and lists every issue |
| `./probe` | Runs the dish probes and lists what the graph lacks. Held-back probes are counted, never shown |
| `./probe questions [batch]` | Runs the stand-in and kitchen questions; shows only growing gaps and aggregate held-back counts |
| `./numbers` | Counts by kind and tier, and the share of probes answered, growing and held back apart |
| `./safety` | Runs the safety probes: what each dish holds, worked out from its recipe, against what the probe says |
| `./tidy` | Rewrites every file in the one way a file is written |
| `./stand-ins <recipe> [--avoid <fact>]` | Other part options, contextual stand-ins and recorded exclusions, for every recipe line |
| `./recipes <technique>` | Recipes whose steps use the technique, teaching dishes first |
| `./kitchen <technique> [food ...] [--avoid <fact>]` | Recipes ranked by missing required parts, with each line's available option, stand-in or missing ingredient |

They need Python 3.9 or later and nothing else.

The three questions accept exact ids or unambiguous names and aliases. Quote names with spaces.
Repeat `--avoid` for several facts. Output is deterministic JSON. A broken repository or an unknown
or ambiguous input is an error, never a partial answer.

For example:

```sh
./stand-ins recipe/sole-meuniere --avoid fact/milk
./recipes technique/sear
./kitchen technique/sear ingredient/salmon ingredient/sunflower-oil ingredient/salt
```

These are internal exploration commands. Every answer says safety records are unverified.
Avoidance excludes strict `contains` answers too. Preparations are checked through every option
of every part; a missing answer or a cycle fails closed. This is deliberately conservative.

Only direct statements are used. No reverse or chained stand-in is inferred. A line's context
is what the recipe makes and the techniques of steps that handle that line. An explicit
`not_when` overrides a positive statement or a part option. A replacement must fit each
technique that works on the original. A part option supplies no ratio or caveat unless a
stand-in statement records them. Recipe amounts and starting forms are returned unchanged;
the commands do not adapt steps, calculate converted amounts or test a recipe in a kitchen.
An exclusion-only statement has `allows: false`: it asserts only its `not_when`,
and never enables the replacement in other contexts.

Kitchen inputs mean presence, not quantity. Required missing parts count once even when
several lines fill one part. Optional omissions are shown and do not affect the score.
An expanded preparation's ingredient lines are assessed individually: owning the whole
preparation does not silently replace those steps. Ties put teaching dishes first, then
recipe ids. Equipment is not part of the kitchen input yet.

## Where the plan is

- The epic: mrspacerobot/tomi#106. It holds the starting model, the loop that grows the graph, and the rules for when a round and a slice stop.
- The first story: mrspacerobot/tomi#119, which builds the first slice (the 12 French techniques the Tomi app teaches today) and settles the model from it.

## Rules

Read `AGENTS.md` before changing anything.
