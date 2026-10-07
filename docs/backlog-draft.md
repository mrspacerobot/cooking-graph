# Backlog draft: stories 3 to 13 of the epic, and what is missing

For the owner, for [issue 4](https://github.com/mrspacerobot/cooking-graph/issues/4). Each story is written to paste as an issue. Nothing was created on GitHub.

Two cautions:

- The story numbers below are the epic's. The real issue numbers will differ. Issues 3 to 6 and 8 already exist here with other jobs (first slice, setup, cycle two, content review, new cuisines). Number the new ones when they are made, and link them to the epic.
- Status is read from the code and documents in this repository on 7 October 2026. "Done" means built and tested as a draft. It never means reviewed. Every thing is tier drafted except 16 sourced allergen facts, and all 195 safety records are unverified.

## Where each story stands

| Story | State |
|---|---|
| 3 Schemas, ids and the validator | Mostly done. Needs the model's own tests listed and one decision on the schema language |
| 4 Trust tiers and the evidence record | Half done. Tiers exist. The evidence record does not |
| 5 The build, the checks and the numbers | Half done. Checks and numbers exist. The database build and CI do not |
| 6 The skeleton from open data | Not done. Four sources looked at, none imported |
| 7 The probe set | Mostly done. Four of five kinds exist. Step probes do not |
| 8 The loop | Half done. Each step has a command. No one-command round, stopping rules are not checks |
| 9 Slice one: French foundations | Drafted, not reviewed. Held-back bar not met |
| 10 The export for the app | Not started, and blocked |
| 11 Slice two: Japanese basics | Probes only. No content, no reviewer |
| 12 Slice three: Indian basics | Probes only. No content, no reviewer |
| 13 The same move across cuisines | Not started. The model has `variant_of`, nothing more |

## Stories 3 to 13

### Story 3: Schemas, ids and the validator

**Why.** Every later step trusts the files, so the files must be read strictly and the same way each time.

**Done when.** (Largely met.) The model is `schema/model.json` with closed lists in `schema/words.json`. Unknown field, missing field, bad id, dangling reference and a file not written the one way are all errors. `docs/model.md` names every kind and field, and `./check` fails when it does not. Ids are kind plus English slug. 30 changes to the model are logged with their examples.

**Tested by.** 287 tests, each rule with a file that breaks it. `./check` reads 1,224 files in about 1 second.

**Still open.** Say in the issue that it is closed once the stack is decided, since a typed schema library would change how the model is written. Name the Python floor.

**Waits for.** The stack decision (issue 4).

**Size.** Small, to close it. Medium if the owner picks a typed schema library.

### Story 4: Trust tiers and the evidence record

**Why.** A tier is a promise. Without a record of who, when and against what, nothing can honestly rise above drafted.

**Done when.** (Half met.) The five tiers exist and the check refuses any tier above drafted, except sourced on a row that names a fetched `source`. Still to build: a review record kind (who, role, cuisine, date, what was seen, the thing and its version), and a check that a tier above drafted has one. The refusal rules `tier-not-earned` and `safety-not-earned` then relax to "needs a record". A safety record may become verified only with a record of a person and an authoritative source.

**Tested by.** A file with reviewed but no record fails. A record that names a missing thing fails. A record for a thing that changed after the review marks the tier stale.

**Waits for.** The owner's decision on how a review is put on record (open question in `docs/cycle-two.md`), and the stack. It must come before any review starts.

**Size.** Medium.

### Story 5: The build, the checks and the numbers

**Why.** Checks, queries and exports should read one loaded copy, not walk files each time.

**Done when.** (Half met.) `./check` and `./numbers` exist. `./numbers` counts by kind and tier and shares of probes answered, growing and held back apart. Still to build: a `./build` that loads the checked files into SQLite, a generated file that git ignores; the three question commands and `./numbers` read from it or agree with it; CI on GitHub running the checks in `docs/stack-options.md`.

**Tested by.** Build twice and get the same file. Every reference in the file resolves. Counts from SQL equal counts from `./numbers`. A broken repository builds nothing.

**Waits for.** The stack decision.

**Size.** Medium for the build, small for CI.

### Story 6: The skeleton from open data (licences checked)

**Why.** Names of ingredients and techniques should come from open data where the licence allows, so the drafter does not invent the spine.

**Done when.** (Not met.) Twelve `source` files record pages read on 7 October 2026, with reuse terms. FoodOn (CC BY 4.0), USDA FoodData Central (CC0) and Wikidata (CC0) were looked at and nothing was imported. Open Food Facts was refused as share-alike product data. What is left: pick what to import, check each licence again at its source, import names and ids only, mark them sourced, keep the import as a repeatable script with its tests.

**Tested by.** A fixture with a share-alike or unclear licence is refused. An import keeps the dataset id on each thing. Run twice, nothing changes.

**Waits for.** A model for dataset ids (the model does not hold them yet, see "what the model cannot express yet" in `docs/model.md`). The owner's ruling on name-only reuse.

**Size.** Medium to large, depending on how much is imported.

### Story 7: The probe set (five kinds of probe as strict files, the held-back share)

**Why.** The graph grows against questions it did not write. One in five is held back by a rule, not by a person.

**Done when.** (Mostly met.) Four kinds exist as strict files in `probes/`: dish (497), safety (40), stand-in (25), kitchen (30). The held-back rule is a hash in `tools/probes.py`, and `./probe` counts held-back probes without showing them. Still to build: the fifth kind, a step probe (see the separate story below), and a stored record that the writer did not see `graph/` (today this is by instruction only).

**Tested by.** Existing tests for the hash rule, the held-back guard and the counts. New: a step probe with a bad field fails.

**Waits for.** Nothing for the kinds. Step probes need a writer who cannot see `graph/`.

**Size.** Small to finish, if step probes are split out.

### Story 8: The loop (one command per step of a round, the stopping rules as checks)

**Why.** A round should be the same every time, and when to stop should not be a feeling.

**Done when.** (Half met.) Each step has a command: `./probe`, `./probe questions`, `./safety`, `./numbers`, `./check`, `./tidy`. Still to build: one `./round` that runs them in order and writes the round note; each stopping rule from the epic as a named check with a bar, a value and a state; the pause rules (three rounds with no held-back gain, cost over budget) computed from the round notes.

**Tested by.** A fixture repository where each rule is met, and one where it is not. The pause rule fires after three flat rounds.

**Waits for.** The numbers of story 5, the review record of story 4 (the reviewer rule), a budget from the owner.

**Size.** Medium.

### Story 9: Slice one, French foundations

**Why.** The first slice shows the method end to end on one cuisine.

**Done when.** (Drafted, not met.) 1 program, 83 techniques, 195 ingredients, 68 dishes, 82 recipes, all drafted, merged as a baseline in PR 1. Against the stopping rules: held-back dish probes 29 of 42 (69%, bar 95%), no step probes, no reviewer, 0 of 195 safety records verified, nothing at the customer's floor. The slice closes when a French reviewer has sampled rows, rejects stay under 5%, and the owner rules on issue 6.

**Tested by.** `./probe`, `./safety`, `./numbers`, and the reviewer's sample.

**Waits for.** Stories 4, 7 (step probes) and the content review (issue 6), a French reviewer (the owner, until found).

**Size.** Large, mostly in waiting for people.

### Story 10: The export for the app

**Why.** The app takes a slice of the graph. The graph knows no customer.

**Done when.** (Not started.) A slice is chosen by cuisine and tier floor and written out as one file with a version. Nothing unverified is exported. No level, XP or drawing appears in it.

**Tested by.** A fixture with an unverified safety record exports nothing for that ingredient and fails loudly. A source whose terms do not allow commercial use is left out. Export is the same for the same input.

**Waits for.** Stories 4 and 5, verified safety records, a ruling on the four pages with unclear or no commercial terms (Health Canada, CFIA, Codex, EU text), the export format (SQLite or JSON), and a reviewed slice to export.

**Size.** Medium once unblocked. Blocked now.

### Story 11: Slice two, Japanese basics

**Why.** A second cuisine tests whether the model holds local knowledge without flattening it.

**Done when.** (Probes only.) 30 Japanese dish probes exist (6 held back), written by another model. The cuisine node is a bare name. Nothing is drafted. The first run answered 0 of 24 growing, with 73 new technique words per 30 probes. To do: a reviewer, names in Japanese script with romanization (the language list is closed beyond `en` and `fr`), a program, drafting rounds against the growing probes, the review.

**Tested by.** `./probe --cuisine japanese`, the held-back share, the reviewer's sample.

**Waits for.** A Japanese reviewer. A change to the language list. Story 4.

**Size.** Large.

### Story 12: Slice three, Indian basics

**Why.** As story 11, for a cuisine whose regional differences are wide.

**Done when.** (Probes only.) 30 Indian dish probes (6 held back). Nothing drafted. The first run answered 0 of 24 growing, with fewer new technique words than Japanese (12) but 52 new ingredient words. To do: a reviewer, names in the original scripts, spice groups that are narrow enough to be true for every member, drafting rounds, the review.

**Tested by.** `./probe --cuisine indian`, the held-back share, the sample.

**Waits for.** An Indian reviewer. A change to the language list. Story 4.

**Size.** Large.

### Story 13: The same move across cuisines

**Why.** The graph's promise is that one move shows up in many kitchens, each keeping its own name and its difference.

**Done when.** (Not started.) A query: for one technique, its variants in each cuisine, with what differs, and its local names. The model has `variant_of` with `differs`, and `belongs_to` to a cuisine. It does not yet say how local names group under one move. Decide that with a real example from slices one and two.

**Tested by.** A fixture with a French and a Japanese variant of one move returns both, each with its difference and its name, and no flattening.

**Waits for.** Stories 9 and 11 (real content), and a model change forced by a real example.

**Size.** Medium.

## Stories I think are missing

### A. The review record

Same as story 4's record, if the owner wants it split out. Put it first. Nothing may be reviewed before it exists. **Size:** medium.

### B. Step probes

**Why.** The epic's stopping rule asks for step probes, and none exist. The question cycle's open questions say yes, by a writer who cannot see `graph/`.
**Done when.** A strict `step-probe` kind: a technique, a step in plain words, what the cook sees and hears, the common mistake. A runner reports growing gaps and counts held back. Written in a new batch by a model other than the drafter.
**Tested by.** A probe with a missing field fails. The hash rule holds some back.
**Waits for.** The model change (logged in `docs/model.md`), and a writer. **Size:** medium.

### C. Repository setup and CI (issue 4)

**Why.** There is no `.github/` folder.
**Done when.** A workflow with the checks in `docs/stack-options.md`, a pull request template that asks for "how much and of what" and the doubts, and branch protection set by the owner.
**Waits for.** The stack decision. **Size:** small.

### D. Batch log for model runs

**Why.** Today a batch of drafting leaves the commit message and a round note, and nothing a tool can read.
**Done when.** Each round writes a small record: model id, date, round, the probes it grew against (growing only), counts added. `./numbers` can show cost per newly answered probe.
**Tested by.** A round without a record fails the loop check.
**Waits for.** Story 8, and a budget. **Size:** small.

### E. Duplicate guards, second part

**Why.** The name rule, `./twins` and `./merge` catch the same name twice and likely twins. They cannot catch two things that are one but share no word and no listed synonym (change 30).
**Done when.** A way to find such pairs from structure (same group, same parts, same technique) and a list of pairs for a person to read. It never blocks.
**Tested by.** A fixture with two names, no shared word, same card.
**Waits for.** Nothing. **Size:** small to medium.

### F. The Mediterranean slice

**Why.** `cuisine/mediterranean` is a parent of Italian, Greek, Spanish, Lebanese, Turkish and Moroccan. Each has 30 dish probes (6 held back) and no content.
**Done when.** A choice of order, then one slice per cuisine or a shared base first (olive oil, legumes, grilling). One story each, with a reviewer each.
**Waits for.** Reviewers. Moroccan has [issue 8](https://github.com/mrspacerobot/cooking-graph/issues/8). **Size:** large, as several stories.

### G. Safety verification

**Why.** All 195 records are unverified, and 11 growing probes disagree with the graph, 10 of them on strict answers alone.
**Done when.** The owner rules on strict answers. A person checks each fact against an authoritative source, with the record of story 4. The disagreements are settled by people or by a fetched page, never by editing either side.
**Waits for.** Story 4, the owner. **Size:** large, mostly human time.

### H. Reuse terms

**Why.** Four pages (Health Canada, CFIA, Codex, EU text) do not allow commercial use or leave it unclear. Their rows are in the graph.
**Done when.** The terms are confirmed or permission is asked, or the rows are marked as not for export. Story 10 then respects it.
**Waits for.** The owner, perhaps a lawyer. **Size:** small.

### I. More languages for names

**Why.** Names must travel in every language they are known in, in their own script with a romanization. The list is closed beyond `en` and `fr`, and Japanese, Indian and Moroccan names need more.
**Done when.** Tags added with a model change and an example. The check accepts `<tag>-Latn` for each.
**Waits for.** A real example from story 11. **Size:** small.

### J. Growth of the question track

**Why.** Stand-in questions answer 0 of 5 held back, and kitchen questions 1 of 6. Part options sit on 11.8% of parts. Words are not the limit now. Knowledge about use is.
**Done when.** Rounds on stand-ins with context, ratio and caveat. A bar for the held-back share set after broader independent probes.
**Waits for.** More independent question probes, and story 8. **Size:** large, ongoing.

### K. The model's known gaps

**Why.** `docs/model.md` lists what the model cannot express: numbers that define a technique, doneness, leftovers, serve-with, a fact inside a fact, levels of sulphites.
**Done when.** One small story for each, only when a real example forces it.
**Waits for.** Examples. **Size:** small each.

### L. The question service (placeholder)

**Why.** The epic says a separate service will answer questions from the graph. It is not part of this repository yet.
**Done when.** Not drafted. Open it once the build (story 5) and the export contract (story 10) are fixed.
**Waits for.** Stories 5 and 10. **Size:** unknown.
