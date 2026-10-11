# cooking-graph

A knowledge graph of how the world cooks: the techniques, what they work on, the cues, the mistakes, what to learn first, and how one move shows up in different cuisines.

It is private. `cooking-graph` is a working name.

## Status

The three graph questions have commands, independent probes and a stand-in
growth cycle. Read `docs/handover.md` for the current status and next steps.
`docs/question-cycle.md` records the question cycle's results and limits;
`docs/night-one.md` records the first slice, and `docs/cycle-two.md` reports
the later cycle.

Cooking content has no human review or kitchen test. Sixteen inherited allergen
facts are sourced from regulator pages; the rest is drafted. Safety records are
unverified. Nothing here may be shown to a cook or exported to an app.

## What is where

| Place | What it holds |
|---|---|
| `graph/<kind>/<slug>.json` | The graph: one file per thing |
| `graph/source/` | The pages a fact was read in, each with the day it was read and its reuse terms |
| `probes/dish-probe/` | The dish probes: well-known dishes the graph must be able to express |
| `probes/safety-probe/` | The safety probes: what a well-known dish holds and does not hold |
| `probes/stand-in-probe/`, `probes/kitchen-probe/`, `probes/compose-probe/` | Independent question probes, with one in five held back by the hash rule. A compose probe names several techniques and a pantry |
| `schema/model.json` | The model: every kind, its fields and what each may hold |
| `schema/words.json` | The closed word lists: tiers, units, roles |
| `tools/`, `tests/` | The commands and their tests. Python standard library only |
| `viewer/` | The interactive browser page's template, styles and JavaScript |
| `docs/model.md` | The model in words, and every change to the starting model with the example that forced it |
| `docs/night-one.md` | The report of the first night: what to open first, the numbers, the doubts, the open questions |
| `docs/strict-answers.md` | Every answer that an ingredient holds a fact strictly and not for certain. Written by `./safety strict` |
| `docs/safety-disagreements.md` | Where a safety probe and the graph disagree, with both sides. Written by `./safety disagreements` |
| `docs/rounds/` | The numbers and notes of each round |

## Explore in your browser

Clone the repository:

```sh
git clone https://github.com/mrspacerobot/cooking-graph.git
cd cooking-graph
```

Open the graph from the default branch:

```sh
./view
```

`./view` checks the repository, builds `out/graph.html` from the current working
files, and opens it in your default browser. Run it again after changing the
graph. The generated page is ignored by git. No Lavish session, local server,
Node installation or package install is needed. Python 3.9 or later is enough
to build it; the browser needs internet access to load the pinned CDN libraries.

Drag nodes to rearrange them, drag the background to pan, and scroll or pinch
to zoom. Click an entry to inspect its record, hover to highlight its neighbours,
or click a connection to see its meaning. Switch between the whole graph and a
local view with one to three steps of connection depth. Filter relationships,
search names or aliases, and use the connection list for keyboard navigation.
Dashed red links represent explicit exclusions in their stated contexts;
ordinary stand-in links are conditional claims. The layout is a drawing of
links, not a measure of culinary similarity or confidence.

The viewer contains graph files only, never probes. It uses the existing
stand-in query rules and displays tiers and safety states. It is an internal
review tool; unverified content remains unavailable for export to cooks.

For an agent or a machine without a browser:

```sh
./view --no-open
```

Then open the printed file path. The command reports when automatic browser
opening fails. An agent giving a first visual walkthrough should follow
the browser instructions in `AGENTS.md`.

## The release artifact

`./release` turns `graph/` into one artifact for a server to load: `graph-artifact.json`, a `manifest.json` (schema
version, graph version, source commit, content hash, channel, the gate results, counts by kind and tier, the fact list)
and `SHA256SUMS`. The same commit always gives the same artifact bytes and the same hash; the time of the build is in
the manifest only. Probes are never included. The `draft` channel is for internal development. The `production` channel
is refused until every gate passes: all included things at tier reviewed or higher, every ingredient's safety verified
by a person, no open safety point in any recipe, and a live review record. Today it fails all four.

On GitHub, `Check` runs `./check` and a draft build on every pull request. The `Release artifact` workflow, started by
hand on `main` from the Actions tab, builds the artifact and attaches it to a release named `graph-v<graph version>`.
The Tomi backend pins one such version.

## Commands

| Command | What it does |
|---|---|
| `./check` | Runs the tests of the tools, then reads every file strictly and lists every issue |
| `./release [--channel draft\|production]` | Writes the graph's versioned, checksummed artifact to `out/release`. Production is refused until its gates pass |
| `./view [--no-open]` | Builds the current graph's interactive HTML page and opens it in the default browser |
| `./probe` | Runs the dish probes and lists what the graph lacks. Held-back probes are counted, never shown |
| `./probe questions [batch]` | Runs the stand-in and kitchen questions; shows only growing gaps and aggregate held-back counts |
| `./numbers` | Counts by kind and tier, part-option shares, positive and negative statements, and all probe kinds, growing and held back apart |
| `./safety` | Runs the safety probes: what each dish holds, worked out from its recipe, against what the probe says |
| `./tidy` | Rewrites every file in the one way a file is written |
| `./stand-ins <recipe> [--avoid <fact>]` | Other part options, contextual stand-ins and recorded exclusions, for every recipe line |
| `./recipes <technique>` | Recipes whose steps use the technique, teaching dishes first |
| `./kitchen <technique> [food ...] [--avoid <fact>]` | Recipes ranked by missing required parts, with each line's available option, stand-in or missing ingredient |
| `./swap-gaps [--list [--top N]] [--new]` | A work list for drafting swaps: counts of recipe lines with no swap where a technique card names one, the pairs most recipes share, and foods in no stand-in row. Writes nothing |
| `./vocabulary [--names]` | The closed list a photo or voice step chooses from: every ingredient, preparation and technique by id, with its English name, aliases and groups. Graph only, never a probe. A label that matches nothing is none |
| `./compose --technique <t> [--technique <t> ...] [food ...] [--avoid <fact>] [--servings <n>] [--top <n>]` | Recipes that practise the techniques, covering the most first, adapted to what is at home: stand-ins, amounts converted by a recorded ratio and scaled to servings, and each step with what to read in place of what |

They need Python 3.9 or later and nothing else.

The three questions accept exact ids or unambiguous names and aliases, and read a plural (lemons) as the one thing it names when no exact name matches. Quote names with spaces.
Repeat `--avoid` for several facts. Output is deterministic JSON. A broken repository or an unknown
or ambiguous input is an error, never a partial answer.

For example:

```sh
./stand-ins recipe/sole-meuniere --avoid fact/milk
./recipes technique/sear
./kitchen technique/sear ingredient/salmon ingredient/sunflower-oil ingredient/salt
./compose --technique technique/sear --technique technique/mount-with-butter --servings 4 \
  ingredient/chicken-thigh ingredient/butter ingredient/olive-oil ingredient/lemon ingredient/salt
```

These are internal exploration commands. Every answer says safety records are unverified.
Avoidance excludes strict `contains` answers too. Preparations are checked through every option
of every part; a missing answer or a cycle fails closed. This is deliberately conservative.

A request for a technique also finds its variants (`variant_of`, at any depth): `boil` finds `boil-pasta`, `emulsify` finds `beat-tahini-sauce`. Exact use ranks first, each recipe says `exact` and which `variants_used`, and `./compose` lists `covered_by_variant`. A variant does not stand in for its parent the other way round. `./compose` also counts a technique used by the recipe of a preparation the dish names, at any depth (croque madame makes a roux through its bechamel); it lists these as `covered_by_preparation`, and ranks a dish's own steps first. Only direct statements are used. No reverse or chained stand-in is inferred. A line's context
is what the recipe makes and the techniques and preparations of steps that handle that line. An explicit
`not_when` overrides a positive statement or a part option. A replacement must fit each
technique that works on the original. A part option supplies no ratio or caveat unless a
stand-in statement records them. `./stand-ins`, `./recipes` and `./kitchen` return recipe amounts and
starting forms unchanged. `./compose` converts an amount only where a stand-in statement records a ratio
of the same measure (weight, volume or count) as the amount's unit; otherwise it says why it did not.
It never edits a step's words: each step comes back as written, with a `read_as` list of what to read in
place of what. None of the commands tests a recipe in a kitchen, and `./compose` does not write a new
recipe: it adapts one the graph already holds, with no model involved.
An exclusion-only statement has `allows: false`: it asserts only its `not_when`,
and never enables the replacement in other contexts.

Kitchen inputs mean presence, not quantity. Required missing parts count once even when
several lines fill one part. Optional omissions are shown and do not affect the score.
An expanded preparation's ingredient lines are assessed individually: owning the whole
preparation does not silently replace those steps. Ties put teaching dishes first, then
recipe ids. Equipment is not part of the kitchen input yet.

## Where the plan is

- [Epic #2](https://github.com/mrspacerobot/cooking-graph/issues/2) holds the starting model, the growth loop, stopping rules and future stories.
- [First slice #3](https://github.com/mrspacerobot/cooking-graph/issues/3) established the internal draft baseline in the merged [PR #1](https://github.com/mrspacerobot/cooking-graph/pull/1).
- [Cycle two #5](https://github.com/mrspacerobot/cooking-graph/issues/5) covers the completed `fresh-3` round and report. [Content review #6](https://github.com/mrspacerobot/cooking-graph/issues/6) covers culinary claims, strict facts and safety disagreements.
- [Repository setup #4](https://github.com/mrspacerobot/cooking-graph/issues/4) covers the stack decision, CI, agent workflow and later backlog.
- [docs/handover.md](docs/handover.md) records the current state and next steps. Start there after `AGENTS.md`; measured results are in [docs/question-cycle.md](docs/question-cycle.md), with history in `docs/rounds/`.

These issues live here so a colleague only needs access to `cooking-graph`.
They were transferred from Tomi issues 106, 119 and 120 with their history.
References in older reports and commits are historical; use the links above for current work.

## Rules

Read `AGENTS.md` before changing anything.
