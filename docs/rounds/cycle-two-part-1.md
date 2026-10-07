# Cycle two, part 1: four problems in the model

No growth. The owner read the report of night one and asked for four fixes. They are changes 17 to 21 in `docs/model.md`.

## What changed

| Problem | What was done |
|---|---|
| A technique listed single ingredients | 39 groups were written. 132 of the 166 ingredients and preparations say which groups they are in. All 64 technique cards now work on groups, and on at most three single things |
| `works_on` meant two things | All 342 recipe steps were split into what the technique works on and what it is done with |
| Parts of a dish had no id | All 513 parts have an id of their own within their dish or preparation. All 495 recipe lines name the part they fill. 12 parts are optional |
| Probes written by the model that drafts | The 120 old probes are stamped `claude-opus-5-5`. A second kind, the safety probe, exists and has no files yet |

`ingredient/allium` is gone. It became `group/alliums`, and the seven ingredients that were "a kind of allium" are members of the group. One by-product was added, `preparation/reduction`, so that the butter of a beurre blanc is mounted on something that has a name.

## What the new step rule found

The rule: what a step's technique works on must be something its card works on, directly or through a group. The steps were split first, by one script that knew for each technique what it is usually done with. Then the rule ran. It found 14.

**Ten were wrong steps.**

| Recipe | What was wrong | Fix |
|---|---|---|
| beurre blanc | The reduction worked on the vinegar as well as the wine | The vinegar is what it is done with |
| beurre blanc | Mounting worked on the finished sauce | It works on the reduction, which the step before now leaves behind |
| bœuf bourguignon | Braising worked on the lardons | They are added to the pot, not braised |
| bœuf bourguignon, coq au vin, navarin (twice) | Braising worked on the pan sauce or the braising liquid | That is the liquid the meat braises in: done with, not worked on |
| endives braisées | The chicory was seared | Browning a head of chicory gently in butter is pan-frying |
| gratin de chou-fleur | Simmering worked on the cheese | The cheese is stirred into the sauce: done with |
| poule au pot | Poaching worked on the celery | The celery and the onion flavour the pot: done with |

**Four were missing memberships.**

| Thing | What was missing |
|---|---|
| potato purée (twice) | It was in no group. It is a starch, and layering works on starches |
| marrow bone | It was only a bone. It is served, so it is in the wide group of meat |
| cornichons | Dicing did not work on pickles |

Seven more steps were changed that the rule could not find, because they worked on nothing at all: skimming a pot-au-feu and a poule au pot now works on the broth those steps leave, the syrup of the pears and the dressing of the salade lyonnaise are named, and three steps name the food they season, chill or plate. Eleven steps still work on nothing: most of them season or garnish a finished dish, which is no ingredient and no preparation.

## The two probes that moved

Gratin dauphinois and the butter-basted pork chop moved to the growing set, by the decision logged as change 20. Both dishes are written, with a recipe each, and Tomi's levels "Potato gratin" and "Butter-basted pork chop" point at them. Gratin de courgettes and carré d'agneau took their places in the held-back set. Both had been growing probes in cycle one, so they entered the held-back set already answered. The two probes that left it were answered too, so the share did not move.

| Dish probes | Answered before | Answered after the move |
|---|---|---|
| growing | 96 of 96 | 96 of 96 |
| held-back | 15 of 24 | 15 of 24 |

Of the held-back words, 65 of 66 technique words and 122 of 133 ingredient words have a name in the graph.

## What the model still could not express

- **What a move is done with has no card.** A step now says what it is done with, and nothing checks that list against the technique's needs. Searing with olive oil would pass.
- **A step that seasons or plates the whole dish works on nothing,** because a step may work on an ingredient or a preparation and the dish is neither.
- **A group cannot say that a member behaves a little differently.** Duck breast is a steak that must first be rendered. It is in both groups, and the sear card is true only for its flesh side.
