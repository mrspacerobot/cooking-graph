# Compose probes, first run

Issue [5](https://github.com/mrspacerobot/cooking-graph/issues/5). Batch `compose-1`: 40 questions, 32 growing and 8 held back by the hash rule, written by `claude-opus-5-5` from its own knowledge and told not to read the repository. The graph was drafted by `claude-sonnet-5-5`. (A first attempt with `claude-fable-5-1` stopped on a usage limit before writing anything.) A question names two or three techniques, a pantry and the dishes a good cook would make. It is answered when every expected dish has a recipe that practises all the techniques with no required part missing.

## Baseline, before any growth

0 of 32 growing and 0 of 8 held back.

## Why the growing ones fail

Counted over the growing set only, after reading a plural pantry word ("lemons") as the one thing it names (change in `queries.resolve`; an exact name always wins and a guess must be unique):

| Reason | Probes |
|---|---|
| A word the graph does not know (a food such as ground cumin, canned chickpeas, coriander leaves; a technique such as fry masala base, temper spices, make a vinaigrette) | 15 |
| The dish is not in the graph | 9 |
| The recipe leaves one of the techniques out | 5 |
| The dish is in the graph but no recipe uses any of the techniques | 3 |
| The pantry is short of one or two required parts | 2 |

Before the plural reading, 25 probes failed on a word. Of 241 growing pantry words, 214 matched exactly, 27 matched once read as singular and 14 are unknown. Of 83 technique words, 5 are unknown.

## What it says

- The main limits of `./compose` are vocabulary and the number of recipes, not swaps. Only 2 of 32 growing questions are held up by a missing ingredient. Swap rows still matter, but they are not the next lever.
- The technique words the writer used are the ones a cook says ("fry masala base"), and the graph's names are fuller ("Fry a masala base"). An alias for each is the usual growth, one at a time against growing gaps.
- Nothing was drafted for the held-back questions, and nothing in this note names one.

## Doubts

- One writer, one model, 40 questions. The count is small and the writer may favour well-known dishes.
- A dish named as a cook would name it may sit in the graph under another name; a missing alias reads as a missing dish here.
- Matching is exact names and plurals only. An app that takes free text would resolve words before calling `./compose`.
