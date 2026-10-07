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
| `./numbers` | Counts by kind and tier, and the share of probes answered, growing and held back apart |
| `./safety` | Runs the safety probes: what each dish holds, worked out from its recipe, against what the probe says |
| `./tidy` | Rewrites every file in the one way a file is written |

They need Python 3.9 or later and nothing else.

## Where the plan is

- The epic: mrspacerobot/tomi#106. It holds the starting model, the loop that grows the graph, and the rules for when a round and a slice stop.
- The first story: mrspacerobot/tomi#119, which builds the first slice (the 12 French techniques the Tomi app teaches today) and settles the model from it.

## Rules

Read `AGENTS.md` before changing anything.
