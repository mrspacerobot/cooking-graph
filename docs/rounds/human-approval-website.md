# Human approval website

The owner asked for a separate page where humans can approve the culinary graph
and verify ingredient safety, including allergens. The owner explicitly assigned
all current cuisines to two people: their mother and the owner.

Two anonymous reviewer registrations, `reviewer/culinary-1` and
`reviewer/culinary-2`, record that scope. Their real-world identity mapping stays
with the owner, outside the repository. Neither reviewer is granted a safety
authority. Safety approval needs evidence from recorded sources.

The closed vocabulary gains `owner-authorized` in `know_ways`. This records the
owner's explicit endorsement of the reviewer's cuisine scope. It does not invent
training, residence, professional work or cooking experience. Existing knowledge
bases keep their meanings. New cuisines still need an explicit roster update.

The approval page is separate from the reading notebook. It shows unverified
safety assertions as claims for review, including every fact, strict answers,
bases, definitions and recorded source links. Whole culinary content excludes
ingredient safety. A safety approval covers the entire safety unit separately.

Human decisions carry the review engine's native hash, source commit, reviewer
alias, cuisine, evidence and attestation. They can be submitted through GitHub or
downloaded. `./review apply` validates the complete proposed graph with the
existing checker before writing anything, rolls back failed writes, and never
merges or pushes. The owner confirms the human author before applying a file.
Only the owner's merge makes the new record authoritative in the graph.

Ingredient safety verification is now built. Verified culinary content,
cook-tested tiers, sampling and safety-probe rulings remain separate, unbuilt
stages. No factual graph claim was approved or safety unit verified by this work.

An unrelated command test compared the whole working tree's git status while
agents were editing. It failed even though the command wrote nothing. The test
now runs the real command against an isolated small repository and compares its
files byte for byte, excluding only Python's import cache.
