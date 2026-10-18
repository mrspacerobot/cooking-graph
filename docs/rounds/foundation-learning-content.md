# Foundation introductions and question catalog

The French foundation program teaches 28 distinct techniques across 37 levels.
This round adds an introduction and four questions to each of those techniques:
28 introductions and 112 questions, all `drafted`. It adds no techniques,
recipes, foods, safety assertions or factual approvals.

Each introduction explains the move and why understanding it helps a cook.
Each question has a permanent local id, choices, a correct answer and an
explanation. The four ids are `purpose`, `method`, `observation` and
`correction`. They identify different learning targets within a technique;
they are not a global set of questions or a record of a learner's progress.
The correct answers vary in position across the catalog.

The source material is the existing technique card: its `does`, `how`, `cues`
and `mistakes`. Explanations paraphrase that material. This is model-authored
learning content derived from drafted knowledge, with no newly fetched
references. These questions are teaching content, not evaluation probes.
No probe files were opened by the content writer.

## Context and ownership

The catalog belongs to a technique so that repeated program levels can reuse
it. The program still chooses the teaching sequence and practice dishes.
An app can choose the wording of its welcome, present visual curriculum
steps, select and order questions, and remember a person's answers. Those
app choices and quiz results do not belong in the graph and never promote a
factual tier.

Several cards have a narrower scope than their English verb might suggest.
The introductions and questions preserve it: `caramelize` is the existing
onion method, `roll-an-omelette` is the smooth pale French-style omelette,
`scramble` is the gentle creamy scramble, and `make-a-sabayon` is the yolk
foam prepared before butter in this card. The `emulsify` questions describe
the existing gradual whisked addition of fat rather than every way of
making an emulsion.

Four questions are an editorial target for this foundation catalog, not a
universal requirement for every technique. The 255 other technique cards
have no authored learning content in this round.

## Culinary doubts for human review

- All source cards and new learning text remain drafted. A question can
  repeat an unverified culinary claim correctly without establishing that
  the claim itself is correct. A human should check the card and its new
  questions together through the existing hash-backed culinary review.
- `rest` repeats the card's account of juice retention. Its accuracy and
  usefulness depend on the food and cooking method. The questions avoid
  prescribing the card's broad resting-time rule.
- `sear` uses natural release from the pan as a turning cue. Food and pan
  surfaces differ, so the scope and reliability of that cue need review.
- `mount-with-butter` repeats cold butter additions and the card's suggested
  cold-water-or-cream correction for splitting. These are method-specific
  draft claims, not a guarantee that every sauce can be rescued.
- `emulsify` repeats a fresh yolk or mustard restart from the source card.
  A reviewer should check its scope across the sauces linked to the card.
- `braise` asks about partial submersion of the meat. Covered pot shape,
  food and recipe can change the needed liquid; the question is explicitly
  about this method rather than a universal liquid proportion.
- `make-a-roux` questions avoid the card's categorical claim that no later
  simmering can remove a raw flour taste, and avoid presenting opposite
  roux/liquid temperatures as the only valid approach.
- `saute` questions avoid the card's broad rule about salting watery
  vegetables near the end. `brunoise` questions avoid its claim that a blunt
  knife makes shallot bitter. Both source claims still need culinary review.
- Egg-method questions ask about pan control, appearance and texture. They
  give no assurance of doneness or food safety. The existing ingredient
  safety and recipe safety gates still apply independently.
- Distractors describe plausible confusions with nearby methods or mistakes
  already discussed by the cards. A home cook should still try the questions
  after practice to check that there is a single clear answer and that the
  explanations are useful rather than merely recognisable.

The content writer reread the answer and explanation for every question,
checked that each matched its source card, and revised distractors to avoid
irrelevant alternatives. Structural validation and the full repository
check are reported with the enclosing implementation work.

## Repository numbers

The round's `./numbers` snapshot keeps 1,387 graph things: 1,371 drafted
and 16 sourced, with nothing reviewed or above. It counts 6,642 statements:
6,167 drafted and 475 sourced. The 283 techniques, 178 dishes, 197 recipes
and 75 preparations all remain drafted. All 453 ingredient safety records
remain unverified. The new learning content adds no graph things and consists
of 140 drafted units: 28 introductions and 112 questions.

| Probe family | Growing answered | Held back answered |
| --- | --- | --- |
| Dish | 399 of 399 | 63 of 98 |
| Stand-in | 12 of 52 | 2 of 13 |
| Kitchen | 8 of 24 | 1 of 6 |
| Compose | 1 of 64 | 0 of 16 |

These measures test the existing graph tools, not the quality or learning
value of the new teaching questions. This round did not author or inspect
probe content, or change names, cooking methods or practice recipes.

## Validation

`./check` passed all 645 tests and read 2,101 records strictly with no issues.
`./numbers` produced the counts above. The review site builds 987 entries.
Browser checks covered curriculum and lesson navigation, question and answer
expansion, reading progress persistence, plain technique explanations and
expanded-section preservation. Layouts have no horizontal overflow at 320,
390, 768 and 1440 pixels, and dark mode keeps the existing readable theme.
The browser console reported no errors. JavaScript syntax and whitespace
checks passed. Generated pages and local screenshots are not committed.
