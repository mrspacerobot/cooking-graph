# The review record

Stage one is built (the kinds, the hash, `./review`, and six rules, see changes 31 and 32 in `docs/model.md`). Stages two to four are still designs. It answers the open question in `docs/cycle-two.md`: how a review is put on record. Today `tiers_earned` refuses every tier above drafted and `safety_earned` refuses every verified safety record, so no reviewer can approve anything. This document says what replaces them.

**What stage one built, and what it refuses.** Built: the kinds `reviewer` and `review`; `tools/review_hash.py`; `./review show` and `./review seal`; the rules `email-in-repo`, `tier-not-earned`, `review-stale`, `model-grants-too-much`, `reviewer-does-not-know-cuisine`, `review-unlinked`; and the review counts in `./numbers`. Refused by `review-not-built` until their stages: a sample record, rulings, a review of a safety record, `verified` and `cook-tested`. Nobody has written a real record. The first one is for a person to write.

## 1. What a record is

Two new kinds, both in `graph/`, neither with a `tier` or `names` (a record is history, not a claim that can rise).

**`reviewer`** - `graph/reviewer/<slug>.json`. Says who may review what.

| Field | What it holds |
|---|---|
| `id` | `reviewer/<slug>` |
| `kind` | `person`, `model` or `test-cook` (closed list `reviewer_kinds`) |
| `model_id` | For a model, its id, such as `claude-sonnet-5-5`. `null` otherwise |
| `knows` | The cuisines this reviewer can answer for. Rows of `cuisine` and `how` (closed list `know_ways`: cooks-it-at-home, cooks-it-for-work, trained-in-it, lives-or-lived-there, studies-it). Self-declared. Empty for a model |
| `safety_authority` | A note on what makes this person an authority on safety, or `null`. Only the owner sets it |
| `added_on` | The day the owner accepted this reviewer |

**How a reviewer is named.** The slug is chosen by the owner, never taken from a real name, a handle or an email: `reviewer/owner`, `reviewer/french-1`, `reviewer/judge-opus`. The roster that says which human is `french-1` is kept by the owner outside the repository. The repository holds no name, no email, no address and no link to a profile. A rule refuses an email address anywhere in the repository (`email-in-repo`). A reviewer file is added only in a pull request the owner merges, so adding a reviewer is the owner's act of trust.

**`review`** - `graph/review/<reviewer-slug>-<topic>-<date>.json`. One record is one review session.

| Field | What it holds |
|---|---|
| `id` | `review/<same slug>` |
| `reviewer` | A `reviewer` id |
| `on` | The day of the session |
| `grants` | The tier this session grants to every row it approves. One tier per record |
| `cuisine` | The cuisine the reviewer answered for, or `null` for a test cook or a model |
| `mode` | `rows` (the reviewer chose the rows) or `sample` (the rows were drawn by a rule) |
| `sample` | For `sample`: `seed`, `per_hundred`, `kinds`, `cuisine`. `null` for `rows` |
| `against` | Against what. Rows of `how` (`source`, `own-knowledge`, `test-cook`), `source` (a `source` id when `how` is source, else `null`) and a `note` |
| `covers` | What was looked at. Rows of `thing`, `field`, `target`, `seen`, `verdict` (`approved` or `rejected`) and `note` (`null` unless rejected) |
| `rulings` | Rulings on safety disagreements (section 3). Empty otherwise |
| `supersedes` | Earlier `review` ids this record replaces. Usually empty |
| `note` | Free words from the reviewer, or `null` |

**A unit** is what a row of `covers` points at, because tiers sit on things and on statements:
- the whole thing: `field: null`, `target: null`. It grants the tier to the thing and to every statement and part inside it, except `safety`;
- one statement: `field: "works_on"`, `target: "preparation/fond"`. A part of a dish: `field: "parts"`, `target: "<part id>"`;
- the safety record of an ingredient: `field: "safety"`. This is the only way `safety.state` can become verified.

**`seen`** is a short hash (12 hex digits of sha256) of the unit as the reviewer saw it: the canonical JSON of the unit without any `tier` key, without `safety.state`, and for a whole thing without `safety`. If the file changes later, the hash no longer matches and the tier falls (rule `review-stale`). The tier stays a field of the file, as now. The record is what backs it.

All fields are written from the first record, including `mode`, `sample` and `rulings`. A record is never edited, so a field added later would mean editing every old record.

## 2. The rules, and the test that breaks each

`tiers_earned` and `safety_earned` are replaced. A unit is *backed* when a live record backs it. A record is *live* when no later record names it in `supersedes`. New test files: `tests/test_review_shape.py`, `tests/test_review_tiers.py`, `tests/test_review_safety.py`, `tests/test_review_sample.py`, `tests/test_review_history.py`. Each uses the small kitchen and breaks one file.

| Rule | What it refuses | Test that breaks it |
|---|---|---|
| `tier-not-earned` | A tier above drafted that no live, approved record backs, or that is higher than the records grant. The old exception stays: a regulated row and its fact may be sourced | `test_review_tiers.py`: `test_reviewed_with_no_record`, `test_tier_higher_than_the_record_grants` |
| `model-grants-too-much` | A record by a `model` reviewer that grants above sourced, or grants sourced with no `source` row in `against` | `test_review_tiers.py`: `test_model_grants_reviewed`, `test_model_grants_sourced_without_a_source` |
| `reviewer-does-not-know-cuisine` | `reviewed` or `verified` by a person whose `knows` lacks the record's `cuisine`, or a `cuisine` the thing does not belong to (`belongs_to`, `in_pantry_of`) | `test_review_tiers.py`: `test_reviewer_without_that_cuisine`, `test_cuisine_the_thing_is_not_in` |
| `verified-needs-another` | `verified` where the live `reviewed` record is by the same reviewer, or where there is none. The second record may be a person who knows the cuisine, or a test cook whose `against` is `test-cook` | `test_review_tiers.py`: `test_verified_by_the_same_reviewer`, `test_verified_with_nothing_before` |
| `review-stale` | A unit whose hash is no longer the `seen` of the record that backs it | `test_review_tiers.py`: `test_a_reviewed_thing_edited_afterwards` |
| `review-unlinked` | Two live records with the same `grants` for one unit, a `supersedes` that names no record or a later one, and a rejection that does not name the approval it withdraws | `test_review_tiers.py`: `test_two_live_records_for_one_unit`, `test_supersedes_unknown` |
| `safety-not-earned` | `safety.state: verified` without a live approved `safety` row by a *person*, whose `against` holds a `source` row (a source has a `read_on` and a `url`) or whose reviewer has a `safety_authority`; and a `seen` that no longer matches | `test_review_safety.py`: `test_verified_by_a_model`, `test_verified_with_no_source_and_no_authority`, `test_verified_then_edited` |
| `ruling-by-model` | A ruling by a reviewer who is not a person | `test_review_safety.py`: `test_ruling_by_a_model` |
| `cook-tested-not-built` | `cook-tested`, until stage 4 | `test_review_tiers.py`: `test_cook_tested_still_refused` |
| `email-in-repo` | An email address in any file | `test_review_shape.py`: `test_an_email_in_a_reviewer_note` |
| `sample-not-drawn` | A `sample` record that covers a unit the draw does not pick (section 3) | `test_review_sample.py`: `test_a_row_the_draw_did_not_pick` |
| `review-edited` | A record file changed or deleted after it was added | `test_review_history.py`: `test_an_old_record_edited` (a temporary git repository) |

Shape rules (unknown reviewer, unknown `thing`, a bad `how`, a `source` missing when `how` is source) come from the model, as for every kind. A kind without a `tier` needs a small change in the reader, covered by `test_review_shape.py`.

What these rules cannot see: whether a reviewer who is a `person` is a person, whether two slugs are one human, and whether what a reviewer wrote under `knows` is true. The owner's merge is the guard for all three.

## 3. How a reviewer works

**Row by row.** The reviewer runs `./review show technique/deglaze`. It prints the card, its tier, and the `seen` hash. The reviewer reads, answers approved or rejected for each unit, and the record is written with those answers. An approval edits the file's `tier` in the same pull request. A rejection leaves the tier at drafted and says why in `note`. The graph is then corrected by a drafter and offered again.

**By sample.** A reviewer who cannot read everything asks for a draw: `./review sample --cuisine french --kind ingredient --per-hundred 10 --seed lyon-oct`. A unit is in the sample when the first 8 hex digits of sha256(seed + unit id), taken modulo 100, are under `per_hundred`. The rule needs no list of the population, so it still holds after the graph grows. Nobody picks the rows, as with held-back probes. `sample-not-drawn` refuses any covered unit the rule would not pick.
- A sample grants only to the rows it covers and approves. **Unsampled rows stay drafted.** A sample measures the graph. It does not approve it.
- The **reject rate** is rejected rows over covered rows of `sample` records, by cuisine and kind. `./numbers` shows it. A rejected row counts for good, even if fixed afterwards.
- The **5% stopping rule** is met for a cuisine when at least 40 rows were sampled and under 5% were rejected.
- The half that offline checking cannot do: a reviewer leaving out a drawn row that is hard. `./review sample --check` lists drawn units that are neither covered nor approved, and runs in the pull request.

**Safety.** To verify an ingredient, the reviewer covers `field: "safety"` with `grants: verified`. The pull request sets `state` to verified and the record carries the `seen` hash of `contains`, `free_of` and `note`. A person who verifies a row that is strict (`certain: false`) is saying the strict answer is the right one. It stays strict. To change it, the file is edited (flip `certain`, or move the fact to `free_of`) and the new unit is verified. This is the owner's ruling "reason by reason" in `docs/strict-answers.md`, so strict answers need no ruling of their own.

**A disagreement.** `./safety disagreements` lists where a probe and the graph differ. A person rules in the `rulings` of a record: `probe`, `fact`, `stands` (`graph` or `probe`) and `why`. The record's `against` may be a fetched source: a fetched page settles it, as `AGENTS.md` says. Then:
- `docs/safety-disagreements.md` keeps the disagreement and adds a line under it: ruled by `reviewer/x` on a day, graph stands or probe stands, with the record id. A ruled disagreement moves to a section "Ruled". It never leaves the file by an edit to the graph or the probe;
- `graph stands`: the line says whether the ingredients under it are verified. A ruling over unverified ingredients reads "ruled, still unverified";
- `probe stands`: the graph is wrong. The line reads "ruled for the probe, graph not changed" until an ingredient is edited and its safety unit verified again;
- `docs/strict-answers.md` gains a column: verified or not, by which record.
The counts in the table of the file gain a column, "Ruled". A held-back probe is counted and never shown, as now.

## 4. Layout

- One record per session, never per row, so a French session of 40 rows is one file of about 40 lines. Each `covers` row is one line, as `./tidy` writes statements. A whole-ingredient safety pass over all 195 ingredients is about 200 lines, one file.
- Records are append-only. A fix is a new record with `supersedes`. A withdrawal is a new record with `rejected` rows that supersede the approval.
- `graph/review/` holds no content of the graph, only history. `./check` builds one index from (thing, field, target) to the live records, so no rule reads the folder twice.
- The thing's file stays small: it holds a `tier` and nothing about the reviewer. Who, when and against what is found by id in one place.
- `./numbers` adds: units by tier backed by a record, records by reviewer kind, the reject rate by cuisine.

## 5. Stages

**Stage 1 - the owner approves one ingredient and one technique (tier `reviewed`).** Smallest slice. Safety stays refused.

Model: kinds `reviewer` and `review` with the fields above; words `reviewer_kinds`, `know_ways`, `verdicts`, `against_ways`, `review_modes`, `stands`. Logged in `docs/model.md` as changes 31 and 32 with the example that forced them (deglaze cannot be reviewed). The decision "Nothing is above drafted..." changes in the same commit.

Tool: `tools/review_hash.py` (the hash, one function) and `./review show` and `./review seal` that print it.

Rules to build first, tests first, in this order: `email-in-repo`, `tier-not-earned` (new), `model-grants-too-much`, `reviewer-does-not-know-cuisine`, `review-stale`, `review-unlinked`, `verified-needs-another`. The old tests in `tests/test_check.py` `Trust` move into `test_review_tiers.py`.

Worked example. The reviewer file:

```json
{
  "id": "reviewer/owner",
  "kind": "person",
  "model_id": null,
  "knows": [{"cuisine": "cuisine/french", "how": "cooks-it-at-home"}],
  "safety_authority": null,
  "added_on": "2026-10-14"
}
```

The record (`graph/review/owner-deglaze-butter-2026-10-14.json`, a slug starts with a letter, so the day comes last; the hashes are made up, `./review seal` would print the real ones):

```json
{
  "id": "review/owner-deglaze-butter-2026-10-14",
  "reviewer": "reviewer/owner",
  "on": "2026-10-14",
  "grants": "reviewed",
  "cuisine": "cuisine/french",
  "mode": "rows",
  "sample": null,
  "against": [
    {"how": "own-knowledge", "source": null, "note": "Cooked and taught in a French home kitchen."}
  ],
  "covers": [
    {"thing": "technique/deglaze", "field": null, "target": null, "seen": "3f9a1c07d2b4", "verdict": "approved", "note": null},
    {"thing": "ingredient/butter", "field": null, "target": null, "seen": "a81e5b60c9d2", "verdict": "approved", "note": null}
  ],
  "rulings": [],
  "supersedes": [],
  "note": null
}
```

The pull request also sets `"tier": "reviewed"` on both files and on their statements. The checker then finds a live approved record by a person who knows French, with the right `seen`. Butter's `safety.state` stays `unverified`: the record has no `safety` row.

**Stage 2 - safety.** `safety-not-earned` (new), `ruling-by-model`, `rulings` in `./safety`, the "Ruled" section and the new columns. Verify butter's `safety` against a fetched source, then one strict ingredient (white wine) to prove the strict path. Tests: `test_review_safety.py`.

**Stage 3 - samples.** `./review sample`, `sample-not-drawn`, the reject-rate table in `./numbers`, `review-edited` (with `./check --base origin/main` in CI). Tests: `test_review_sample.py`, `test_review_history.py`.

**Stage 4 - the second reviewer and cook-tested.** `verified-needs-another` with a real second person; a test cook kind; the design of `cook-tested` (what counts as a result). Not designed here.

## 6. Open questions for the owner, each with a default

| Question | Default |
|---|---|
| Is the owner the first reviewer and may the owner review and verify one unit? | Owner is `reviewer/owner`. Verified needs a second reviewer, never the owner twice |
| Does any edit of a reviewed unit drop its tier? | Yes. Wording fixes included. Safety is a unit of its own so that a new fact does not stale every ingredient |
| How are reviewers named? | A slug the owner picks. Roster outside the repository. Owner-only merge |
| Does a reviewer who knows French cover Lyonnaise? Does Lyonnaise cover French? | The wider covers the narrower (`within`). The narrower does not cover the wider |
| A technique with no cuisine (deglaze): is one cuisine enough for `reviewed`? | Yes. The record says which. A later reviewer from another cuisine adds a record |
| Can a person verify safety with no source? | Only a reviewer with a `safety_authority` the owner set. Otherwise a fetched source is needed |
| May a model judge write records at all? | Yes, to rank the queue and to flag, at drafted or sourced, never alone for a tier above sourced. It never rules |
| Does a sample approve the rows it did not draw? | No |
| Sample size and the 5% bar | At least 40 rows, under 5% rejected, per cuisine |
| Is a git check in CI acceptable for `review-edited`? | Yes. The check also refuses a deleted record |

## What I could not decide

- **Immutability offline.** `./check` sees files, not history. `review-edited` needs git, so it runs only with a base branch. Without CI, the owner's reading of the pull request is the guard.
- **Who is a person.** Nothing in the repository tells a person from a model that wrote `kind: person`. The owner merges reviewer files. That is a rule of people, not of the checker.
- **One human, two slugs.** `verified-needs-another` compares slugs. It cannot compare humans.
- **The sample's omission half** (a hard drawn row left out) is checked by a command in the pull request, not by `./check`.
- **Whether 40 rows and 5% mean anything.** It is the epic's number. A real reviewer's first batch will show whether it is a useful bar.
- **Cook-tested.** What a cook's result is as data (a date, a count, a verdict) is not designed.
- **A model judge's worth.** It may only add noise. Stage 1 does not need it.
