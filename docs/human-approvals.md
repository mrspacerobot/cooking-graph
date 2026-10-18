# Put human approvals on record

Open **Human approvals** from the notebook, or open `out/site/approvals.html`
after running `./review-site`. This is a separate review page. Unverified safety
assertions are displayed here for a human to check, never as food recommendations.

## Reviewers

The owner authorized two human reviewers for all 15 current cuisines. Their
anonymous registrations are `reviewer/culinary-1` and `reviewer/culinary-2`.
The owner keeps the real identity mapping outside the repository. Registration
is authoritative only once the owner merges the registration pull request.
`owner-authorized` records that explicit scope without claiming training,
residence, cooking experience or safety expertise. New cuisines need a roster update.

Neither registration grants safety authority. Both people can verify safety
against source evidence they personally checked. The roster does not turn a
reviewer's own knowledge into an authoritative allergen reference.

## Use the page

1. Choose your assigned reviewer alias. Different reviewers keep separate
   staged decisions in this browser.
2. Choose **Ingredient safety** or **Culinary content**. Search for an entry or
   filter its kind. The queue starts with units awaiting a decision.
3. Read the exact version. Culinary content includes its statements and parts,
   with ingredient safety excluded. Ingredient safety shows every allergen and
   dietary answer, the contains basis, certainty or strict uncertainty, the
   ingredient note, fact definitions and recorded references.
4. Open the sources and check the ingredient itself. A regulator's definition
   of an allergen does not establish whether a particular food contains it.
   Choose the source records you checked and explain what supports the answers.
   When a needed source is absent, flag the correction and have it recorded
   before trying to approve that safety unit.
5. Confirm you are a human who personally checked this version. Approve it or
   request a correction. A safety approval must cover every safety answer for
   that ingredient. It keeps strict answers strict. These are staged decisions,
   not changes to the graph.
6. Submit the decisions on GitHub. A small batch is included in the prepared
   issue. For a large batch, download `cooking-approvals.txt` and attach it to
   the issue before selecting Create issue. GitHub supports attaching text
   files in its [web interface](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files).

Decisions are kept for the chosen reviewer and native unit hash. Changed content
starts without a decision. If storage is unavailable, the page says so; download
before leaving. Opening GitHub or downloading does not confirm submission or
apply any approval. Already approved units cannot be overwritten through this
page: an explicit superseding review is needed.

## Apply a person's decisions

The owner first confirms who authored the file and checks its evidence. A
downloaded file can name any alias; it is not proof of identity. Do not apply
an agent's simulated browser-test decisions as a human review.

On a feature branch:

```sh
./review apply cooking-approvals.txt
./check
git diff
```

If the page left the reviewer unassigned, identify the registered author explicitly:

```sh
./review apply cooking-approvals.txt --reviewer reviewer/culinary-1
```

The importer checks the native hash against the current graph, requires a
registered person and personal attestation, validates cuisine scope and source
records, rejects duplicate units, and refuses to replace a live approval.
Each ingredient safety approval needs its own sources or an explicitly granted
safety authority. A source on one ingredient does not verify another.

It groups decisions into review sessions by grant and cuisine, preserving each
unit's evidence note. Content approvals grant reviewed and promote the covered
statements, while leaving safety unchanged. Safety approvals grant verified to
the safety unit only and set its state; they do not promote culinary content.
Corrections record rejected decisions and promote nothing.

The complete result is checked in a temporary copy before any file is written.
Failed writes are rolled back. Existing review records are never rewritten.
Read the resulting pull request and merge it as the owner. Only then does a
rebuilt site or released artifact reflect the new graph state. This work does
not itself verify any food or settle any safety-probe disagreement.

Verified culinary content, cook-tested tiers, sampling and safety-probe rulings
remain later stages. See `docs/review-record.md` for the review model.
Approving recipe text does not clear its open `safety_points`; production
export gates continue to apply.
