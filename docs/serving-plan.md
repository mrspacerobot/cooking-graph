# Serving the private cooking graph to the Tomi iOS app

A plan, not a build. Nothing here is implemented. It says how the graph could reach the Tomi iOS app through a read-only
API, and what stands in the way. It is for the owner to decide from.

## What was and was not checked

- Only this repository was visible while writing. Tomi's `docs/implementation-plan.md` and the fridge-photo proof of concept
  (`fridge-photos/owner-fridge-01-poc.json`, Git-ignored) are on the owner's Mac. Everything below about them comes from the
  owner's description and is **unverified**. Someone who can read them should check the section on the older plan.
- The privacy points are from general knowledge of good practice, not legal advice. A privacy adviser must check them before any
  photo leaves a phone.
- No benchmark has been run. Rust or Go is undecided.

## Where the graph stands

- The three first endpoints already exist as local commands, and they are the reference behaviour: `tools/queries.py`
  (`recipes`, `stand_ins`, `kitchen`), used by `./recipes`, `./stand-ins` and `./kitchen`. They fail closed: a safety fact that is
  unknown excludes the candidate.
- Everything is tier `drafted`. Every safety record is `unverified`. The review record that lets a tier rise is designed in
  `docs/review-record.md` and not built. AGENTS says nothing unverified is exported, and a recipe with an open safety point cannot be
  exported (`docs/model.md`, on safety points).
- So no graph-derived cooking advice can reach a cook yet. Only an internal draft channel can exist.
- `docs/stack-options.md` lists the export format (SQLite, JSON or both) and the service stack as open owner decisions.

## Decisions to record

These are recommended defaults. The owner can overrule any of them.

1. **Privacy shape.** Good practice is to collect little, ask for consent each time, use data for one purpose, keep it briefly and never
   train on it. Because on-device recognition on iOS 17 is likely weaker than a server model, the default is:
   - Photos and voice go to a separate vision and speech service, only after an explicit opt-in for each scan.
   - They are processed transiently, deleted when the answer returns, never logged and never used for training.
   - The graph API never receives photos, audio or chat text. It receives only ids that the cook confirmed, and restrictions.
   - Check before launch: App Review rules on sending personal data to a third-party AI service, how GDPR treats photos and voice,
     and the vision provider's retention terms. Measure an on-device mode against the two proof-of-concept photos before ruling it out.
2. **Four layers never merge.** The proof of concept showed why. Each is its own object and its own step:
   an observed label (from a photo, with a confidence), a cook-confirmed item, an exact graph id, and a cook-facing result.
   A label is never treated as an id. `POST /v1/resolve` returns candidate ids with the basis (exact, alias, ambiguous, none) and never
   picks one for the cook. A cook-facing result exists only for content at tier reviewed or higher with safety verified by a person.
3. **A local recheck stays, and it is not a model.** The app still checks diet, allergens and swaps on the ids it gets back and on
   their `contains` and `free_of` facts. It is a plain rules lookup that works on any iOS, and a second guard for allergens. The API
   returns tier, certain-or-strict basis and channel so that the check has what it needs.
4. **An offline lesson path.** The app bundles reviewed lessons and works without the API. The API only adds candidates. Until review
   exists, the bundle holds only Tomi's own reviewed lessons, none from this graph.
5. **The language is provisional.** At this size (a few thousand files, tens of megabytes) indexing once at startup matters far more
   than Rust against Go. Decide by the measured spike below. If the numbers are close, pick what the team will maintain and what lets
   the ratings code live beside it.

## The release artifact (graph side)

- A new tool in this repository, `./release`, written tests first and standard library only. It runs `./check`, then writes one
  immutable, versioned artifact and a manifest: schema version, git commit, content hash, counts by kind and tier, build time, and a
  `channel`.
- Two channels:
  - `draft` is for internal development only. It carries every record and marks every response `channel: draft`. The app refuses it
    in a release build.
  - `production` can be built only when every gate passes: each included record is at the tier the gate names, each included
    ingredient's safety record is verified by a person, no recipe has an open safety point, and the review record exists.
    Today the build refuses `production` and says which gates fail.
- Contents come from `graph/` only. Never `probes/`, never held-back words, never `out/` or a generated page. A test fails the build if
  a probe file is included.
- Format: a versioned JSON bundle with a checksum. It is language neutral and suits "replicas index at startup". SQLite can be a second
  output if the owner picks it. The server builds its indexes in memory when it starts and refuses to start on a checksum or schema
  version mismatch. Replicas pin an artifact version, so rolling forward or back means changing the pin.
- Conformance vectors: golden request and response pairs generated from `tools/queries.py` over the artifact. Any server must
  reproduce them exactly. They are the contract between this Python authoring side and a Rust or Go server.

## API version one: read-only and stateless

| Endpoint | What it does | Reference |
|---|---|---|
| `GET /v1/meta` | artifact version, channel, schema version, counts | the manifest |
| `POST /v1/resolve` | labels to candidate ids with the basis; never picks one | new; graph names and aliases, Wikidata ids later |
| `GET /v1/techniques/{id}/recipes` | recipes that use a technique, those that teach it first | `queries.recipes` |
| `POST /v1/recipes/{id}/stand-ins` | contextual options and exclusions per line, given fact ids to avoid | `queries.stand_ins` |
| `POST /v1/kitchen/match` | recipes for a technique that the cook can make from confirmed ids, and what is missing | `queries.kitchen` |

- Every response carries the artifact version, the channel and the tier of each item. An unknown safety fact excludes the candidate.
  No text claims that food is safe or cooked through.
- Request bodies are never logged and never echoed in an error. The client sends an opt-in header.
- Auth, rate limits and the record of consent belong to the Tomi gateway, not to the graph service.

## The older Tomi plan (unverified, from the owner's description)

The older plan describes a small Go service for ratings and a hosted lesson library. The owner says the app is only a front end. A
split that fits both, to be checked against the real document:

- **Tomi gateway** (client-facing): auth, consent, ratings, the hosted lesson library, and mapping candidates to reviewed lessons.
  This is where the older Go service lives or is replaced.
- **Graph service** (internal, read-only): the five endpoints above, served from the artifact, called by the gateway and not by the phone.
- **Vision and speech adapters**: photo or voice in, observed labels out, nothing kept.

The phone talks to the gateway only. Open: whether the gateway and the graph service ship as one program or two.

## Phases

0. In this repository: decide the export format, write `./release` and its gates with tests, generate the golden vectors.
   Status: `./release`, its four production gates, the manifest and the release workflow exist ([issue 14](https://github.com/mrspacerobot/cooking-graph/issues/14)).
   The format is a JSON bundle with a checksum. Not built yet: the precomputed indexes and the golden vectors.
1. Spike: the same artifact, endpoints and vectors in Rust and in Go. Measure startup index time, p50 and p99 latency and memory on the
   current graph and on a copy ten times larger. Write the numbers and the decision here.
2. `resolve`, with a contract test built from a cleaned copy of the proof of concept's structure. The file itself stays Git-ignored.
3. Privacy review of the photo and voice path before any photo leaves a device.
4. Map candidates to reviewed Tomi lessons, and keep the offline bundle working from the first day.

## What blocks shipping

The review record is not built. No reviewer exists for any cuisine. No safety record is verified. The rulings on
[issue 6](https://github.com/mrspacerobot/cooking-graph/issues/6) are open. Until these clear, only the `draft` channel exists and
nothing from the graph reaches a cook.

## How it will be checked once built

- `./check` includes the release tests.
- The artifact checksum round-trips.
- Rust and Go both reproduce every golden vector.
- A test proves the production build refuses today's graph.
- A test fails the build if a probe file is included.
- `resolve` returns "ambiguous" for a label with two ids, and never an id for an unknown label.

## Questions for the owner

1. Approve the photo opt-in default above, or choose on-device only, or everything to the backend.
2. Export format: JSON bundle, SQLite or both.
3. Share `docs/implementation-plan.md` and the proof of concept's structure, or let the agent that can read them write the reconciliation.
4. Name the vision and speech provider and its retention terms.
