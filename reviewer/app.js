"use strict";

const notebook = JSON.parse(document.getElementById("review-data").textContent);
const entries = Object.values(notebook.entries);
const kinds = {class: "Foundation classes", technique: "Techniques", recipe: "Recipes", substitution: "Substitutions", preparation: "Preparations"};
let category = "class";
let selected = null;
let filtered = [];

function escapeText(value) {
  return String(value ?? "").replace(/[&<>"']/g, char => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[char]);
}

function nameOf(id) {
  return notebook.entries[id]?.names.en || notebook.names[id]?.name || id.split("/").pop().replaceAll("-", " ");
}

function titleOf(record) { return record.names.en; }
function href(id) { return "#" + encodeURIComponent(id); }
function label(value) { return value.replaceAll("_", " ").replaceAll("-", " "); }
function section(title, body) { return body ? `<section><h3>${escapeText(title)}</h3>${body}</section>` : ""; }

function link(id) {
  if (notebook.entries[id]) return `<a href="${href(id)}">${escapeText(nameOf(id))}</a>`;
  return `<span>${escapeText(nameOf(id))}</span>`;
}

function links(rows) {
  if (!rows.length) return "";
  return `<div class="links">${rows.map(row => {
    const id = typeof row === "string" ? row : row.thing;
    const tier = typeof row === "string" ? "" : ` <small>(${escapeText(row.tier)})</small>`;
    return `<span>${link(id)}${tier}</span>`;
  }).join("")}</div>`;
}

function list(rows) { return `<ul>${rows.map(row => `<li>${escapeText(row)}</li>`).join("")}</ul>`; }

function measure(value) {
  if (!value) return "";
  const amount = value.value ?? `${value.from} to ${value.to}`;
  const symbols = {gram: "g", kilogram: "kg", millilitre: "ml", litre: "l", celsius: "°C", millimetre: "mm", centimetre: "cm"};
  const plurals = {leaf: "leaves", pinch: "pinches"};
  const unit = symbols[value.unit] || (value.value === 1 ? label(value.unit) : plurals[value.unit] || label(value.unit) + "s");
  return `${amount} ${unit}`;
}

function recipesFor(ids) {
  return entries.filter(record => record.kind === "recipe" && ids.includes(record.makes));
}

function recipeLinks(records) { return links(records.map(record => record.id)); }

function ratioText(ratio) {
  return ratio ? `${ratio.stand_in} substitute : ${ratio.original} original, by ${ratio.by}.` : "No ratio recorded. Equal amounts are not established.";
}

function claimContext(record) {
  const unrestricted = record.allows ? "No positive context restriction recorded; exclusions still apply." : "This exclusion-only claim does not permit use in other contexts.";
  return `<p><strong>Applies in:</strong> ${record.when.length ? record.when.map(link).join(", ") : unrestricted}</p>` +
    `<p><strong>Excluded in:</strong> ${record.not_when.length ? record.not_when.map(link).join(", ") : "No exclusions recorded."}</p>`;
}

function substitutionBody(record) {
  const recipes = entries.filter(other => other.kind === "recipe" && other.substitutions.some(line =>
    [...line.options, ...line.excluded].some(row => row.claims.includes(record.id))));
  return `<p class="lead">${link(record.candidate)} in place of ${link(record.original)}</p>
    <p class="notice">This is a directional claim for review. Its tier and context matter; safety and allergens remain unverified.</p>
    <p><span class="badge ${record.allows ? "" : "blocked-badge"}">${record.allows ? "Conditional substitution" : "Explicit exclusion"}</span></p>` +
    section("When this claim applies", claimContext(record)) +
    section("Ratio", `<p>${escapeText(ratioText(record.ratio))}</p>`) +
    section("Caveat", `<p>${escapeText(record.caveat || "No caveat recorded.")}</p>`) +
    section("Recipes where this candidate is checked", recipes.length ? `<p class="fine">Open a recipe to see whether its complete context offers or excludes this candidate.</p>${recipeLinks(recipes)}` : "<p>No recipe currently checks this candidate.</p>");
}

function substitutionCandidate(row) {
  const reasons = {
    "not-in-this-context": "Explicitly excluded in this recipe's context.",
    "no-matching-context": "No matching context is recorded. This does not establish that the swap cannot work.",
    "method-not-supported": "The recorded technique does not support this candidate. A method change may be needed.",
    "avoided-or-unknown-fact": "The query cannot offer this candidate. Safety remains unverified."
  };
  return `<div class="swap-candidate ${row.reason === "not-in-this-context" ? "blocked" : row.reason ? "unknown" : ""}">
    <p><strong>${link(row.thing)}</strong>${row.tier ? ` <span class="badge tier">${escapeText(row.tier)}</span>` : ""}</p>
    ${row.reason ? `<p>${escapeText(reasons[row.reason] || label(row.reason))}</p>` : ""}
    ${row.basis === "part-option" ? "<p>Listed as another option for this dish part.</p>" : ""}
    ${row.caveat ? `<p>${escapeText(row.caveat)}</p>` : ""}
    ${row.basis ? `<p class="fine">${escapeText(ratioText(row.ratio))}</p>` : ""}
    ${row.basis === "stand-in" ? `<div class="fine">${claimContext(row)}</div>` : ""}
    <div class="links">${row.claims.map((id, index) => `<a href="${href(id)}">Review recorded claim${row.claims.length > 1 ? ` ${index + 1}` : ""}</a>`).join("")}</div>
  </div>`;
}

function recipeSubstitutions(record) {
  const first = record.substitutions.findIndex(line => line.options.length || line.excluded.some(row => row.reason === "not-in-this-context"));
  return `<p>These recorded options need review in this recipe's context. Safety and allergens remain unverified.</p>` + record.substitutions.map((line, index) => {
    const blocked = line.excluded.filter(row => row.reason === "not-in-this-context");
    const unknown = line.excluded.filter(row => row.reason !== "not-in-this-context");
    return `<details class="swap-line" ${index === first ? "open" : ""}><summary><strong>${escapeText(nameOf(line.original))}</strong><span>${line.options.length} listed ${line.options.length === 1 ? "option" : "options"} · ${blocked.length} explicit ${blocked.length === 1 ? "exclusion" : "exclusions"}</span></summary>
      <p class="fine">Original amount: ${escapeText(measure(line.amount))}. Context checked: ${line.context.map(link).join(", ")}.</p>
      ${line.options.length ? `<h4>Listed alternatives</h4>${line.options.map(substitutionCandidate).join("")}` : "<p>No applicable alternative is recorded. That is a gap in the graph, not a claim that none exists.</p>"}
      ${blocked.length ? `<h4>Explicit exclusions</h4>${blocked.map(substitutionCandidate).join("")}` : ""}
      ${unknown.length ? `<details><summary>${unknown.length} ${unknown.length === 1 ? "candidate" : "candidates"} without an applicable claim</summary>${unknown.map(substitutionCandidate).join("")}</details>` : ""}
    </details>`;
  }).join("");
}

function introduction(card) {
  if (!card.intro) return '<p class="content-gap">Introduction and why it matters have not been drafted yet.</p>';
  return `<div class="technique-intro"><p>${escapeText(card.intro.what)}</p><p><strong>Why it matters:</strong> ${escapeText(card.intro.why)}</p>
    ${card.intro.idea ? `<p class="key-idea">The idea to remember: <strong>${escapeText(card.intro.idea)}</strong></p>` : ""}
    <p class="fine">Introduction: ${escapeText(card.intro.tier)} · ${escapeText(plainTier(card.intro.tier))}</p></div>`;
}

function questionCatalog(card) {
  const questions = card.quiz || [];
  if (!questions.length) return '<p class="content-gap">No questions have been drafted for this technique yet.</p>';
  return `<p class="fine">${questions.length} questions for review. Open an answer to check the reasoning. These are the technique’s reusable questions, not a scored exam.</p>
    <ol class="question-catalog">${questions.map(question => `<li><p><strong>${escapeText(question.question)}</strong></p>
      <ol type="A" class="question-choices">${question.choices.map(choice => `<li>${window.notebookCloudEnabled ? `<label><input type="radio" name="quiz-${escapeText(card.id)}-${escapeText(question.id)}" data-quiz-card="${escapeText(card.id)}" data-quiz-question="${escapeText(question.id)}" value="${question.choices.indexOf(choice)}"> ${escapeText(choice)}</label>` : escapeText(choice)}</li>`).join("")}</ol>
      <details class="answer-review"><summary>Check the answer and explanation</summary><p><strong>Recorded answer: ${escapeText(question.choices[question.answer])}</strong></p>
      <p>${escapeText(question.because)}</p><p class="fine">${escapeText(question.tier)} · ${escapeText(plainTier(question.tier))}</p></details></li>`).join("")}</ol>`;
}

function lessonFlow() {
  return `<div class="lesson-flow"><p class="eyebrow">The planned Tomi lesson</p><ol class="steps"><li><strong>Understand</strong><br>Tomi introduces the technique and why it matters.</li><li><strong>Cook and notice</strong><br>Practise it in a dish and notice what changes.</li><li><strong>Think it through</strong><br>After cooking, answer a short quiz and learn why.</li></ol>
    <p class="fine">You are reviewing this learning sequence. This notebook is not cooking guidance and ${window.notebookCloudEnabled ? "saves your answers for shared review. Answering does not approve a claim." : "does not record cooking or quiz completion."}</p></div>`;
}

function prerequisiteLinks(record) {
  return record.comes_after.map(row => {
    const first = entries.find(other => other.kind === "class" && other.source === record.source && other.skill_slug === row.skill);
    return first ? `<a href="${href(first.id)}">${escapeText(first.skill)}</a> <small>(${escapeText(row.tier)})</small>` : escapeText(label(row.skill));
  });
}

function classBody(record) {
  const practice = record.through.map(row => row.thing);
  const prerequisites = prerequisiteLinks(record);
  const cards = record.teaching_cards || [];
  return `<p class="lead">${escapeText(record.program)} · ${escapeText(record.skill)} · Lesson ${record.number}</p>
    <a class="curriculum-back" href="#curriculum">↑ See the whole learning path</a>` +
    lessonFlow() +
    section("Learn first", prerequisites.length ? `<p>${prerequisites.join(", ")}</p>` : "<p>You can start this skill without an earlier skill in this program.</p>") +
    section("1. Before cooking: the introduction", cards.length ? cards.map(card => `<div class="teaching-card"><h4>${link(card.id)}</h4><p class="fine">Technique: ${escapeText(card.tier)} · Lesson link: ${escapeText(card.link_tier)}</p>${introduction(card)}<p><a href="${href(card.id)}">Read the full technique card →</a></p></div>`).join("") : '<p class="content-gap">No teaching technique is recorded yet.</p>') +
    section("2. Practice to review", `<p>These dishes or preparations are the lesson’s practice examples.</p>${links(record.through)}${recipeLinks(recipesFor(practice)) || '<p class="content-gap">No practice recipe is listed yet.</p>'}`) +
    section("3. After cooking: questions to review", '<p>Questions belong to each technique and can be reused in other lessons. Please check whether the answers explain the cooking clearly.</p>' + (cards.length ? cards.map(card => `<details class="technique-questions"><summary>${escapeText(card.names.en)} · ${(card.quiz || []).length} questions</summary>${questionCatalog(card)}</details>`).join("") : '<p class="content-gap">No question catalog is linked yet.</p>'));
}

function curriculumOverview() {
  const host = document.getElementById("curriculum");
  const previousSkills = new Map([...host.querySelectorAll("[data-curriculum-skill]")].map(detail => [detail.dataset.curriculumSkill, detail.open]));
  const lessons = entries.filter(record => record.kind === "class");
  if (!lessons.length) { host.hidden = true; return; }
  const programs = [...new Set(lessons.map(record => record.source))];
  host.innerHTML = `<p class="eyebrow">Find your way through the foundations</p><h2 id="curriculum-title">A clear path, one skill at a time</h2>
    <p>Each numbered lesson introduces techniques, gives a practice example, then reviews the ideas with questions. Start with a skill below. The links marked “Learn first” show what it builds on.</p>` + programs.map(id => {
      const program = lessons.filter(record => record.source === id);
      const courses = [...new Set(program.map(record => record.course_slug))];
      return `<div class="curriculum-program"><h3>${escapeText(program[0].program)}</h3><p class="fine">${courses.length} sections · ${new Set(program.map(record => record.skill_slug)).size} skills · ${program.length} lessons. These lessons follow one cooking tradition. Other cuisines may teach these skills differently.</p>
        <div class="curriculum-grid">${courses.map((slug, index) => {
          const course = program.filter(record => record.course_slug === slug);
          const skills = [...new Set(course.map(record => record.skill_slug))];
          return `<section class="curriculum-course"><h4><span class="step-number">${index + 1}</span>${escapeText(course[0].course)}</h4>${skills.map(skill => {
            const rows = course.filter(record => record.skill_slug === skill);
            const prerequisites = prerequisiteLinks(rows[0]);
            const key = `${id}/${slug}/${skill}`;
            const open = previousSkills.has(key) ? previousSkills.get(key) : selected?.skill_slug === skill && selected?.source === id;
            return `<details class="curriculum-skill" data-curriculum-skill="${escapeText(key)}" ${open ? "open" : ""}><summary>${escapeText(rows[0].skill)} <span>${rows.length} lessons</span></summary>
              <p class="fine">${prerequisites.length ? `Learn first: ${prerequisites.join(", ")}` : 'A starting skill in this program.'}</p><ol>${rows.map(row => `<li><a href="${href(row.id)}" aria-current="${selected?.id === row.id}"><strong>${escapeText(row.names.en)}</strong><span>${escapeText(row.teaching_cards?.[0]?.intro?.what || row.teaching_cards?.[0]?.does || "No technique introduction is recorded yet.")}</span><span class="progress-label" data-state="${progressState(row)}">${progressLabel(row)}</span></a></li>`).join("")}</ol></details>`;
          }).join("")}</section>`;
        }).join("")}</div></div>`;
    }).join("") + '<p class="fine">“Looked over” means personal reading progress in this browser. It does not mean a lesson was cooked, a quiz was passed, or a claim was approved.</p>';
}

function techniqueBody(record) {
  const claims = entries.filter(other => other.kind === "substitution" && [...other.when, ...other.not_when].includes(record.id));
  return `<p class="lead">${escapeText(record.does)}</p>` +
    section("Before cooking: what and why", introduction(record)) +
    section("How it works", `<ol>${record.how.map(text => `<li>${escapeText(text)}</li>`).join("")}</ol>`) +
    section("What to look for", list(record.cues.map(cue => `${label(cue.sense)}: ${cue.text}`))) +
    section("Common mistakes", `<ul class="plain-list">${record.mistakes.map(row => `<li><strong>${escapeText(row.mistake)}</strong><p>${escapeText(row.fix)}</p></li>`).join("")}</ul>`) +
    section("After cooking: question catalog", questionCatalog(record)) +
    section("Works on", links(record.works_on)) + section("Makes", links(record.makes)) +
    section("What you need", `<ul class="plain-list">${record.needs.map(row => `<li><strong>${escapeText(label(row.role))}</strong> <small>(${escapeText(row.tier)})</small>${links(row.options)}</li>`).join("")}</ul>`) +
    section("Learn first", record.comes_after.length ? `<ul>${record.comes_after.map(row => `<li>${link(row.thing)} (${escapeText(row.tier)})<p>${escapeText(row.why)}</p></li>`).join("")}</ul>` : "") +
    section("Variant of", record.variant_of.length ? `<ul>${record.variant_of.map(row => `<li>${link(row.thing)} (${escapeText(row.tier)})<p>${escapeText(row.differs)}</p></li>`).join("")}</ul>` : "") +
    section("Variants to explore", record.variants.length ? `<ul>${record.variants.map(row => `<li>${link(row.thing)} (${escapeText(row.tier)})<p>${escapeText(row.differs)}</p></li>`).join("")}</ul>` : "") +
    section("Recipes that use this technique", record.recipes.length ? `<p class="fine">Includes variants. Exact use comes first, then recipes that teach the technique.</p><ul class="plain-list">${record.recipes.map(row => `<li>${link(row.recipe)}<p class="fine">${row.exact ? "Uses this technique directly" : `Uses a variant: ${row.variants_used.map(link).join(", ")}`}${row.teaches ? " · Teaching recipe" : ""} · ${escapeText(row.tier)}</p></li>`).join("")}</ul>` : "<p>No recipe is listed yet.</p>") +
    section("Substitution claims naming this technique", claims.length ? `<p class="fine">Includes conditional substitutions and exclusions. Open each claim to review its direction and full context.</p>${recipeLinks(claims)}` : "<p>No substitution claim names this technique yet.</p>");
}

function recipeBody(record) {
  return `<p class="lead">Makes ${link(record.makes)} · ${escapeText(measure(record.yields))}</p>` +
    section("Ingredients", `<ul class="plain-list">${record.ingredients.map(row => `<li>${escapeText(measure(row.amount))} <strong>${link(row.thing)}</strong>${row.forms.length ? `, ${escapeText(row.forms.map(nameOf).join(", "))}` : ""}</li>`).join("")}</ul>`) +
    section("Substitutions to review", recipeSubstitutions(record)) +
    section("Equipment", links(record.equipment)) +
    section("Method to review", `<ol>${record.steps.map(step => `<li><strong>${link(step.technique)}</strong><p>${escapeText(step.text_as_read)}</p><p class="step-meta">${[
      measure(step.time), measure(step.temperature),
      step.works_on.length ? "Works on: " + step.works_on.map(nameOf).join(", ") : "",
      step.with.length ? "With: " + step.with.map(nameOf).join(", ") : "",
      step.safety_points.length ? "Open safety points: " + step.safety_points.map(label).join(", ") : ""
    ].filter(Boolean).map(escapeText).join(" · ")}</p></li>`).join("")}</ol>`);
}

function preparationBody(record) {
  const madeBy = recipesFor([record.id]);
  const usedBy = entries.filter(other => other.kind === "recipe" && other.makes !== record.id &&
    (other.ingredients.some(row => row.thing === record.id) || other.steps.some(step => step.makes.includes(record.id))));
  const claims = entries.filter(other => other.kind === "substitution" && [other.candidate, other.original].includes(record.id));
  return `<p class="lead">${escapeText(record.is)}</p>` +
    section("Components", record.parts.length ? `<ul class="plain-list">${record.parts.map(part => `<li><strong>${escapeText(label(part.id))}</strong> · ${escapeText(label(part.role))}${part.optional ? " · Optional" : " · Required"} <span class="badge tier">${escapeText(part.tier)}</span>${links(part.options)}</li>`).join("")}</ul>` : "<p>No separate components are recorded. This preparation may be made within a recipe step.</p>") +
    section("Recipes to make this preparation", madeBy.length ? recipeLinks(madeBy) : "<p>No separate recipe is recorded. Check the recipes that use or make it below.</p>") +
    section("Techniques to look over", record.teaches.length ? links(record.teaches) : "<p>No teaching technique is recorded.</p>") +
    section("Recipes that use or make it", usedBy.length ? recipeLinks(usedBy) : "<p>No other recipe is listed yet.</p>") +
    section("Substitution claims to review", claims.length ? recipeLinks(claims) : "<p>No substitution claim is recorded yet.</p>");
}

function cuisineIds(record) {
  if (record.kind === "substitution") return [...new Set([record.candidate, record.original, ...record.when, ...record.not_when].flatMap(id => notebook.names[id]?.cuisines || []))];
  const source = record.kind === "recipe" ? record.makes : record.source;
  return notebook.names[source]?.cuisines || [];
}

function subtitle(record) {
  if (record.kind === "class") return `${record.course} / ${record.skill} / Lesson ${record.number}`;
  if (record.kind === "substitution") return `${record.allows ? "Conditional substitution" : "Explicit exclusion"} · ${[...record.when, ...record.not_when].map(nameOf).join(", ") || "See full context"}`;
  return cuisineIds(record).map(nameOf).join(", ") || label(record.kind);
}

function searchText(record) {
  const words = [titleOf(record), subtitle(record), record.id, ...Object.values(record.names),
    ...Object.values(record.aliases || {}).flat()];
  if (record.kind === "class") words.push(record.program, ...record.teaches.map(row => nameOf(row.thing)));
  if (record.kind === "technique") words.push(record.intro?.what || "", record.intro?.why || "", ...(record.quiz || []).map(row => row.question));
  return words.join(" ").toLocaleLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function updateLibrary() {
  curriculumOverview();
  document.querySelectorAll("[data-kind]").forEach(button => button.setAttribute("aria-pressed", button.dataset.kind === category));
  const query = document.getElementById("search").value.toLocaleLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
  const cuisine = document.getElementById("cuisine").value;
  const matches = entries.filter(record => record.kind === category && searchText(record).includes(query) && (!cuisine || cuisineIds(record).includes(cuisine)));
  updateProgressSummary(matches, kinds[category].toLowerCase());
  filtered = matches.filter(record => progressMatches(record, document.getElementById("progress-filter").value));
  if (category !== "class") filtered.sort((a, b) => titleOf(a).localeCompare(titleOf(b)));
  document.getElementById("result-count").textContent = `Showing ${filtered.length} ${kinds[category].toLowerCase()}`;
  document.getElementById("entry-list").innerHTML = filtered.length ? filtered.map(record =>
    `<a class="entry" href="${href(record.id)}" aria-current="${selected?.id === record.id}"><strong>${escapeText(titleOf(record))}</strong><small>${escapeText(subtitle(record))}</small><small class="progress-label" data-state="${progressState(record)}">${progressLabel(record)}</small></a>`).join("") :
    '<p class="muted">Nothing matches. Try another word, or set Cuisine and Show back to everything.</p>';
  updateNext();
}

function updateNext() {
  const nav = document.getElementById("entry-navigation");
  if (!nav || !selected) return;
  const index = filtered.findIndex(record => record.id === selected.id);
  nav.innerHTML = index < 0 ? "" : [
    index > 0 ? `<a class="previous" href="${href(filtered[index - 1].id)}"><small>Previous</small>← ${escapeText(titleOf(filtered[index - 1]))}</a>` : "",
    index < filtered.length - 1 ? `<a class="next" href="${href(filtered[index + 1].id)}"><small>Next</small>${escapeText(titleOf(filtered[index + 1]))} →</a>` : ""
  ].join("");
}

const ratingWords = {1: "Needs a lot of work", 2: "Needs work", 3: "All right", 4: "Good", 5: "Clear and useful"};

function feedbackForm() {
  return `<section class="feedback" aria-labelledby="feedback-title">
    <h3 id="feedback-title">What do you think?</h3>
    <p>A score, a note, or both. Every bit helps.</p>
    <form id="feedback-form">
      <fieldset><legend>1. How clear and useful is it? (optional)</legend><div class="ratings">${[1, 2, 3, 4, 5].map(number =>
        `<label class="rating"><input type="radio" name="rating" value="${number}"><b>${number}</b><span>${ratingWords[number]}</span></label>`).join("")}</div>
        <p class="fine">This scores the writing, not whether the food is safe.</p></fieldset>
      <div class="field"><label for="feedback-notes">2. What would you change? (optional)</label>
      <textarea id="feedback-notes" name="notes" maxlength="1200" placeholder="For example: I would add the salt earlier, or this step needs more time."></textarea>
      <p id="draft-status" class="fine" role="status"></p></div>
      <div class="field"><label for="feedback-kind">Is your note mostly about one thing? (optional)</label>
      <select id="feedback-kind" name="kind"><option>General feedback</option><option>Wording or clarity</option><option>Technique or method</option><option>Substitution or ingredient option</option><option>Amounts or timing</option><option>Class order or practice</option><option>Safety concern</option></select></div>
      <fieldset><legend>${window.notebookCloudEnabled ? "3. Saved together" : "3. Send it"}</legend>
      <div class="actions"><a class="primary button" id="send-feedback" ${window.notebookCloudEnabled ? "hidden" : ""} href="https://github.com/${notebook.repository}/issues/new" target="_blank" rel="noopener">Continue to GitHub ↗</a><button type="button" id="download-feedback">Save to a file</button></div>
      ${window.notebookCloudEnabled ? '<p class="fine">Your score and note save automatically. Both of you can come back and continue here.</p>' : `<p class="fine"><strong>Continue to GitHub</strong> opens a ready-made message. Sign in, then press the green <strong>Create issue</strong> button to send it. <strong>Save to a file</strong> keeps a copy you can email or hand to the owner yourself.</p>`}
      <p class="feedback-status" id="feedback-status" role="status" aria-live="polite"></p></fieldset>
    </form>
    <p class="fine">Your note is a suggestion. It does not approve the entry or confirm that anything is safe.</p>
  </section>`;
}

function feedbackMessage(text, problem) {
  const status = document.getElementById("feedback-status");
  status.textContent = text;
  status.classList.toggle("problem", Boolean(problem));
}

function feedbackValue() {
  const form = document.getElementById("feedback-form");
  return {rating: new FormData(form).get("rating") || "", kind: form.elements.kind.value, notes: form.elements.notes.value};
}

function feedbackText(record, value) {
  const source = `https://github.com/${notebook.repository}/blob/${notebook.commit}/graph/${record.source}.json`;
  return [`Entry: ${titleOf(record)}`, `Entry ID: ${record.id}`, `Source: ${source}`,
    `Edition: ${notebook.commit}`, `Entry SHA-256: ${record.hash}`, "",
    `Rating: ${value.rating ? value.rating + '/5' : 'Not rated'}`, `Topic: ${value.kind}`, "",
    "Suggested changes / notes:", value.notes.trim() || "No notes.", "",
    "This is editorial feedback, not a formal review or safety verification."].join("\n");
}

function feedbackValid(value) {
  if (value.rating || value.notes.trim()) return true;
  feedbackMessage("Please choose a score or write a note first.", true);
  return false;
}

function connectFeedback(record) {
  const key = `cooking-notebook:${record.id}:${record.hash}`;
  const form = document.getElementById("feedback-form");
  const status = document.getElementById("draft-status");
  try {
    const saved = JSON.parse(localStorage.getItem(key) || "null");
    if (saved) {
      if (/^[1-5]$/.test(saved.rating)) form.querySelector(`input[value="${saved.rating}"]`).checked = true;
      form.elements.kind.value = saved.kind;
      if (!form.elements.kind.value) form.elements.kind.selectedIndex = 0;
      form.elements.notes.value = saved.notes || "";
      status.textContent = "Welcome back. Your unsent note is here, just as you left it.";
    }
  } catch { status.textContent = "This browser cannot keep unsent notes. You can still send it or save it to a file."; }
  const save = () => {
    saveNotebookValue(key, feedbackValue());
    status.textContent = window.notebookCloudEnabled ? "Your note is being saved to the shared notebook." :
      (progressPersistent ? "Kept in this browser as you type. Not sent yet." : "This browser cannot keep unsent notes. Save a copy to a file.");
    trackFeedbackDraft(record, feedbackValue());
    feedbackMessage("");
  };
  form.addEventListener("input", save);
  form.addEventListener("change", save);
  form.addEventListener("submit", event => event.preventDefault());
  document.getElementById("send-feedback").addEventListener("click", event => {
    const value = feedbackValue();
    if (!feedbackValid(value)) { event.preventDefault(); return; }
    const url = new URL(`https://github.com/${notebook.repository}/issues/new`);
    url.searchParams.set("title", `[Notebook review] ${titleOf(record)}`);
    url.searchParams.set("body", feedbackText(record, value));
    if (url.href.length > 8000) {
      event.preventDefault();
      feedbackMessage("This note is too long to open on GitHub. Make it a little shorter, or save it to a file and share that.", true);
      return;
    }
    event.currentTarget.href = url.href;
    feedbackMessage("Thank you! GitHub opened in a new tab. Press “Create issue” there to send it. This page cannot tell whether it was sent.");
  });
  document.getElementById("download-feedback").addEventListener("click", () => {
    const value = feedbackValue();
    if (!feedbackValid(value)) return;
    const url = URL.createObjectURL(new Blob([feedbackText(record, value)], {type: "text/plain;charset=utf-8"}));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = record.id.replaceAll("/", "-") + "-feedback.txt";
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    feedbackMessage("Thank you! The file is saved. Send it to the owner to share your note. Saving alone does not send it.");
  });
}

function showEntry(record, focus) {
  selected = record;
  category = record.kind;
  const renderers = {class: classBody, technique: techniqueBody, recipe: recipeBody, substitution: substitutionBody, preparation: preparationBody};
  const body = renderers[record.kind](record);
  const content = document.getElementById("content");
  content.innerHTML = `<button type="button" class="to-list">↑ Back to the list</button>
    <div class="badges"><span class="badge">${escapeText(kinds[record.kind])}</span><span class="badge tier">${escapeText(record.tier)}</span></div>
    <p class="eyebrow">${escapeText(subtitle(record))}</p><h2>${escapeText(titleOf(record))}</h2>
    <p class="tier-note"><strong>What “${escapeText(record.tier)}” means:</strong> ${escapeText(plainTier(record.tier))}</p>${body}${feedbackForm()}${progressPanel(record)}
    <nav id="entry-navigation" class="bottom-nav" aria-label="More entries"></nav>
    <p class="fine"><a href="https://github.com/${notebook.repository}/blob/${notebook.commit}/graph/${record.source}.json" target="_blank" rel="noopener">Read the source entry on GitHub ↗</a></p>`;
  document.title = `${titleOf(record)} - The cooking notebook`;
  connectFeedback(record);
  connectProgress(record);
  window.dispatchEvent(new Event("notebook-entry"));
  content.querySelector(".to-list").addEventListener("click", () => {
    const library = document.getElementById("library");
    library.focus({preventScroll: true});
    library.scrollIntoView({block: "start"});
  });
  updateLibrary();
  if (focus) {
    content.focus({preventScroll: true});
    content.scrollIntoView({block: "start"});
  }
}

function navigate(focus) {
  if (location.hash === "#curriculum") {
    if (!selected) {
      const first = entries.find(record => record.kind === "class") || entries[0];
      if (first) showEntry(first, false);
    }
    document.getElementById("curriculum").focus({preventScroll: true});
    document.getElementById("curriculum").scrollIntoView({block: "start"});
    return;
  }
  let id;
  try { id = decodeURIComponent(location.hash.slice(1)); } catch { id = ""; }
  const record = notebook.entries[id] || entries.find(item => item.kind === "class") || entries[0];
  if (record) showEntry(record, focus);
  else document.getElementById("content").textContent = "No entries are available to review yet.";
}

const cuisines = [...new Set(entries.flatMap(cuisineIds))].sort((a, b) => nameOf(a).localeCompare(nameOf(b)));
document.getElementById("categories").innerHTML = Object.entries(kinds).map(([kind, title]) =>
  `<button type="button" data-kind="${kind}" aria-pressed="${category === kind}">${title}</button>`).join("");
document.getElementById("cuisine").innerHTML += cuisines.map(id => `<option value="${escapeText(id)}">${escapeText(nameOf(id))}</option>`).join("");
document.getElementById("categories").addEventListener("click", event => {
  const button = event.target.closest("[data-kind]");
  if (!button) return;
  category = button.dataset.kind;
  updateLibrary();
  if (filtered.length) {
    history.replaceState(null, "", href(filtered[0].id));
    showEntry(filtered[0], false);
  }
});
document.getElementById("search").addEventListener("input", updateLibrary);
document.getElementById("cuisine").addEventListener("change", updateLibrary);
document.getElementById("progress-filter").addEventListener("change", updateLibrary);
document.getElementById("source-link").href = `https://github.com/${notebook.repository}/tree/${notebook.commit}`;
window.addEventListener("hashchange", () => navigate(true));
loadProgress();
function refreshFromStorage(rerender) {
  loadProgress();
  updateLibrary();
  if (!selected) return;
  if (rerender) showEntry(selected, false);
  else updateProgressPanel(selected);
}
window.addEventListener("storage", event => {
  if (!event.key || event.key.startsWith("cooking-notebook")) refreshFromStorage(false);
});
// A change from another device. Never redraw the page under someone who is typing.
window.addEventListener("notebook-remote", event => {
  const touched = event.detail.keys.some(key => selected && key.includes(selected.id));
  refreshFromStorage(touched && !event.detail.editing);
});
navigate(false);
