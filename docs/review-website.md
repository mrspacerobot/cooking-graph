# Review the cooking notebook

The notebook is an editorial review site for someone who knows cooking. It has
foundation classes, technique cards and recipes, drawn from the current graph.
It is separate from the force graph at `./view` and the gated production export.
Everything keeps its earned tier. The page prominently warns that drafts and
unverified safety information are not cooking guidance. No ingredient safety
assertions or substitution claims are exported to this site, and no probes appear.

## Try it before publication

Run `./review-site` from the root. Open `out/site/index.html` in a browser.
The page is self-contained and needs no packages, CDN libraries or server.
Pull requests also build a `review-notebook-preview` artifact in Actions;
download and unzip it, then open `index.html` to review that branch.

The visual design is a separate, light notebook for reading and giving feedback.
It uses system fonts, large text, keyboard navigation and a layout for phones.
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

Choose **Foundation classes**, **Techniques** or **Recipes**. Search by names,
aliases or class topic, or filter by cuisine. Classes follow the program's order,
with prerequisites, linked techniques and recipes for practice. Techniques link
to recipes that use that exact technique; variants are linked separately.
Recipes show their quantities, equipment, method, time, temperature and any
open safety points. Each class level can be reviewed separately.

Choose a rating from 1 to 5, write a suggestion, or do both. A rating describes
how clear and useful the entry is, not a food safety judgement. Choose a topic
such as wording, method or a safety concern to help triage it.

**Continue to GitHub** opens a prepared issue. Sign in and select **Create issue**
to submit it. The notebook cannot confirm submission and does not mark feedback
as sent. GitHub provides the durable shared record and the submitter's identity.
This uses GitHub's supported [issue URL parameters](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue).

**Download feedback** saves a plain text file to share with the owner without
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

## Act on suggestions

Find feedback in the repository's Issues, under titles beginning `[Notebook review]`.
Discuss and make corrections in pull requests. A suggestion, rating or resolved
issue never raises a tier. Formal culinary approval still needs the review record
in `docs/review-record.md`; safety verification remains a separate human process.
No graph content or safety state is changed by the website.
