# Review the cooking notebook

The notebook is an editorial review site for someone who knows cooking. It has
foundation classes, technique cards, preparations, recipes and substitution claims, drawn from the current graph.
It is separate from the force graph at `./view` and the gated production export.
Everything keeps its earned tier. The page prominently warns that drafts and
unverified safety information are not cooking guidance. No ingredient safety
assertions are exported to this site, and no probes appear. Substitution claims
retain their direction, tier, positive context, exclusions, ratio and caveat.

## Try it before publication

Run `./review-site` from the root. Open `out/site/index.html` in a browser.
The page is self-contained and needs no packages, CDN libraries or server.
Pull requests also build a `review-notebook-preview` artifact in Actions;
download and unzip it, then open `index.html` to review that branch.

The visual design is a separate, light notebook for reading and giving feedback.
It is written for a home cook who may read on a phone or tablet: large, high-contrast
text, big tap targets, short plain wording and a light or dark look that follows
the device. Each tier is shown with a plain sentence saying what it means. A
three-step guide at the top says what to do: pick an entry, read it, then score
it or write a note and send it.
Source assets live in `reviewer/`. Never edit generated files in `out/site/`.

## Put it on GitHub Pages

Only the owner merges the pull request into `main`.

1. In the repository's Settings > Pages, choose **GitHub Actions** as the source.
   A private repository needs a GitHub plan that supports Pages for private repositories.
2. Check who will be able to read the Pages site. A private repository does not
   by itself make its Pages site private. The `noindex` tag asks search engines
   not to list it; it is not access control. Choose an available private Pages
   configuration if the review drafts should only be read by invited people.
3. Merge the pull request. The **Review notebook** workflow checks and builds
   the site, then publishes it from `main`. Later changes to graph or site files
   rebuild it. If Pages is configured after merging, run the workflow manually.
4. Copy the live URL from Settings > Pages or the deployment's environment link.
   With the default domain it will be `https://mrspacerobot.github.io/cooking-graph/`.
5. Invite your mom to the private repository so she can submit feedback as issues.
   She will need her own GitHub account. Do not give anyone a token to put in the page.

The workflow never deploys a pull request or a manually selected non-main branch.
It follows GitHub's [custom Pages workflow](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Give feedback

Choose **Foundation classes**, **Techniques**, **Preparations**, **Recipes** or **Substitutions**. Search by names,
aliases or class topic, or filter by cuisine. Classes follow the program's order,
with prerequisites, linked techniques and recipes for practice. Techniques link
to recipes using the technique or its variants, using the existing `./recipes`
engine's order: exact use first, then teaching recipes. Each result identifies
direct use or the variants it uses. Technique pages also link to their variants
with the recorded differences, and to any parent technique.
Recipes show their quantities, equipment, method, time, temperature and any
open safety points. Each class level can be reviewed separately.

Preparation names in ingredient lists and other cards are clickable. Their pages
show definitions, required and optional components with their tiers, techniques,
recipes to make them, recipes that use or produce them, and related substitution
claims. A preparation with no separate recipe says so. Each preparation can be
rated or corrected through its own feedback form.

Each recipe also has **Substitutions to review**, grouped by ingredient. It uses
the existing `./stand-ins` engine, with the same recipe context, technique
compatibility and exclusion rules. Explicit exclusions win over listed dish
options. Candidates without an applicable claim stay separate from explicit
exclusions: a gap in the graph is not a statement that a swap cannot work.
Each listed option preserves its ratio and caveat; absent ratios are not invented
or treated as equal amounts. Safety and allergens remain unverified.

The **Substitutions** view makes each recorded directional claim independently
reviewable. Search for a food, open a claim and check its positive and negative
contexts before giving feedback. Recipe alternatives link to their recorded claims,
and technique cards link to claims that name that technique. These links do not
make a claim applicable to every recipe that uses the technique. Dish part options
without a stand-in claim can be discussed through feedback on their recipe.

Choose a score from 1 (needs a lot of work) to 5 (clear and useful), write a suggestion, or do both. A rating describes
how clear and useful the entry is, not a food safety judgement. Choose a topic
such as wording, method or a safety concern to help triage it.

**Continue to GitHub** opens a prepared issue. Sign in and select **Create issue**
to submit it. The notebook cannot confirm submission and does not mark feedback
as sent. GitHub provides the durable shared record and the submitter's identity.
This uses GitHub's supported [issue URL parameters](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue).

**Save to a file** saves a plain text file to share with the owner without
GitHub sign-in. Downloading does not send anything. Notes that exceed GitHub's
URL limit can also be shared this way.

Drafts stay in this browser's local storage, separately for each entry and content
hash. They are not sent to a server, shared with the owner, or moved between devices.
After an entry changes, its previous draft is not applied to the new wording.
Browser storage restrictions do not prevent submitting or downloading feedback.

Each issue or downloaded note identifies the class or card, immutable source
commit and entry SHA-256. The class source is its program record; the class ID
also identifies its course, skill and level. The owner can see what was read even
after the graph changes. Ratings are not aggregated or displayed on the site.
Substitution feedback points to the candidate food's source record; its content
identifier distinguishes the exact claim. Recipe review hashes include the computed
substitution answers, so changed swaps do not reuse drafts about the older answers.

## Keep your place

Under **Done with this one?**, mark an entry **Looked over**, **Revisit later**, or **To look at**.
The **Show** filter finds each group, or entries with a note not sent yet. A bar shows
how many in the current list are looked over, such as "12 of 40 recipes looked over". Counts follow the
selected category, cuisine and search. Draft feedback is listed as a draft;
opening GitHub or downloading it never marks it as sent or complete.

Progress is stored in this browser for the exact entry version, with the time
you marked it. A changed entry starts again as **To look at**. Progress is not
shared across devices, does not change graph tiers, and is separate from formal
culinary approval. If storage is blocked, progress lasts only for the current
visit and the site says so.

**Find feedback on GitHub** opens the repository's issues filtered by the entry ID.
Submitted suggestions, discussion and resolution remain in GitHub, which requires
sign-in and access to the private repository. The static site does not fetch or
publish private issue text.

## Exploration tools still outside the website

Pantry matching (`./kitchen`) and adaptation for several techniques, pantry and
servings (`./compose`) are available on the command line. They do not yet have
website controls. Allergen and dietary filters remain gated by safety verification.

## Act on suggestions

Find feedback in the repository's Issues, under titles beginning `[Notebook review]`.
Discuss and make corrections in pull requests. A suggestion, rating or resolved
issue never raises a tier. Formal culinary approval still needs the review record
in `docs/review-record.md`; safety verification remains a separate human process.
No graph content or safety state is changed by the website.
