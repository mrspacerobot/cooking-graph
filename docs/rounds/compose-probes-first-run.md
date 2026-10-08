# Compose probes, first run

Issue [5](https://github.com/mrspacerobot/cooking-graph/issues/5). Batch `compose-1`: 40 questions, 32 growing and 8 held back by the hash rule, written by `claude-opus-5-5` from its own knowledge and told not to read the repository. The graph was drafted by `claude-sonnet-5-5`. (A first attempt with `claude-fable-5-1` stopped on a usage limit before writing anything.) A question names two or three techniques, a pantry and the dishes a good cook would make. It is answered when every expected dish has a recipe that practises all the techniques with no required part missing.

## Baseline, before any growth

0 of 32 growing and 0 of 8 held back.

## Why the growing ones fail

Counted over the growing set only, after reading a plural pantry word ("lemons") as the one thing it names (a change in `queries.resolve`; an exact name always wins and a guess must be unique):

| Reason | Probes |
|---|---|
| A word the graph does not match exactly | 15 |
| The dish is not in the graph | 9 |
| The recipe leaves one of the techniques out | 5 |
| The dish is in the graph but no recipe uses any of the techniques | 3 |
| The pantry is short of one or two required parts | 2 |

Before the plural reading, 25 probes failed on a word. Of 241 growing pantry words, 214 matched exactly, 27 matched once read as singular and 14 are unknown. Of 83 technique words, 5 are unknown.

### Naming is not the same as a gap

The probes are free text because a blind writer cannot know ids. The product does not work that way: a photo model returns labels or ids from the graph's closed list and the cook confirms them (`docs/serving-plan.md`), and the graph receives only ids. Read that way, the 15 word failures split:

- **Naming or form only, about 10 of the 14 foods:** canned chickpeas (`chickpea`), ground cumin (`cumin`), coriander leaves (`coriander-leaf`), dried fenugreek leaves (`dried-fenugreek-leaf`), frisee lettuce (`frisee`), ripe tomatoes (`tomato`), dried wakame (`wakame`), sweet paprika (`paprika`). A classifier choosing from the list removes these.
- **Missing from the graph, about 4:** dry vermouth, plaice, smoked paprika (a different taste from paprika, so its own ingredient), silken tofu (the graph has tofu and firm tofu).
- **Technique phrases, all 5, are naming:** fry masala base (`Fry a masala base`), temper spices (`temper-spices-in-hot-fat`), enrich with egg yolk (`thicken-with-egg-yolk`), make a vinaigrette (a preparation `vinaigrette` exists). A cook picks a technique from a list or an app maps the words.

## What it says

- The limit of `./compose` is content: recipes and dishes (9 dishes absent, 8 questions where the best recipe leaves a technique out or uses none), then a few missing foods. Only 2 of 32 growing questions are held up by a missing ingredient, so more swap rows are not the next lever either.
- Aliases are a safety net for typed and spoken input and for other languages. They are not the first investment, and no alias round follows from this run.
- The plural reading matters for typed or spoken input. A photo path does not need it.
- Nothing was drafted for the held-back questions, and nothing in this note names one.

## Doubts

- One writer, one model, 40 questions. The count is small and the writer may favour well-known dishes.
- A dish named as a cook would name it may sit in the graph under another name; a missing alias reads as a missing dish here.
- Matching is exact names and plurals only. An app that takes free text would resolve words before calling `./compose`.
