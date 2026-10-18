"use strict";

const notebook = JSON.parse(document.getElementById("review-data").textContent);
const entries = Object.values(notebook.entries);
const kinds = {class: "Foundation classes", technique: "Techniques", recipe: "Recipes"};
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
  return `${amount} ${label(value.unit)}`;
}

function recipesFor(ids) {
  return entries.filter(record => record.kind === "recipe" && ids.includes(record.makes));
}

function recipeLinks(records) { return links(records.map(record => record.id)); }

function classBody(record) {
  const practice = record.through.map(row => row.thing);
  const prerequisites = record.comes_after.map(row => {
    const first = entries.find(other => other.kind === "class" && other.source === record.source && other.skill_slug === row.skill);
    return first ? `<a href="${href(first.id)}">${escapeText(first.skill)}</a> (${escapeText(row.tier)})` : escapeText(label(row.skill));
  });
  return `<p class="lead">${escapeText(record.program)} · ${escapeText(record.skill)} · Lesson ${record.number}</p>` +
    section("Before this class", prerequisites.length ? `<p>${prerequisites.join(", ")}</p>` : "<p>No earlier class is listed.</p>") +
    section("Techniques to look over", links(record.teaches)) +
    section("Practise through", links(record.through)) +
    section("Recipes for this class", recipeLinks(recipesFor(practice)) || "<p>No recipe is listed yet.</p>");
}

function techniqueBody(record) {
  const recipes = entries.filter(other => other.kind === "recipe" && other.steps.some(step => step.technique === record.id));
  return `<p class="lead">${escapeText(record.does)}</p>` +
    section("How it works", `<ol>${record.how.map(text => `<li>${escapeText(text)}</li>`).join("")}</ol>`) +
    section("What to look for", list(record.cues.map(cue => `${label(cue.sense)}: ${cue.text}`))) +
    section("Common mistakes", `<ul class="plain-list">${record.mistakes.map(row => `<li><strong>${escapeText(row.mistake)}</strong><p>${escapeText(row.fix)}</p></li>`).join("")}</ul>`) +
    section("Works on", links(record.works_on)) + section("Makes", links(record.makes)) +
    section("What you need", `<ul class="plain-list">${record.needs.map(row => `<li><strong>${escapeText(label(row.role))}</strong> <small>(${escapeText(row.tier)})</small>${links(row.options)}</li>`).join("")}</ul>`) +
    section("Learn first", record.comes_after.length ? `<ul>${record.comes_after.map(row => `<li>${link(row.thing)} (${escapeText(row.tier)})<p>${escapeText(row.why)}</p></li>`).join("")}</ul>` : "") +
    section("Variant of", record.variant_of.length ? `<ul>${record.variant_of.map(row => `<li>${link(row.thing)} (${escapeText(row.tier)})<p>${escapeText(row.differs)}</p></li>`).join("")}</ul>` : "") +
    section("Recipes that use this technique", recipes.length ? recipeLinks(recipes) : "<p>No recipe is listed yet.</p>");
}

function recipeBody(record) {
  return `<p class="lead">Makes ${escapeText(nameOf(record.makes))} · ${escapeText(measure(record.yields))}</p>` +
    section("Ingredients", `<ul class="plain-list">${record.ingredients.map(row => `<li>${escapeText(measure(row.amount))} <strong>${escapeText(nameOf(row.thing))}</strong>${row.forms.length ? `, ${escapeText(row.forms.map(nameOf).join(", "))}` : ""}</li>`).join("")}</ul>`) +
    section("Equipment", links(record.equipment)) +
    section("Method to review", `<ol>${record.steps.map(step => `<li><strong>${link(step.technique)}</strong><p>${escapeText(step.text)}</p><p class="step-meta">${[
      measure(step.time), measure(step.temperature),
      step.works_on.length ? "Works on: " + step.works_on.map(nameOf).join(", ") : "",
      step.with.length ? "With: " + step.with.map(nameOf).join(", ") : "",
      step.safety_points.length ? "Open safety points: " + step.safety_points.map(label).join(", ") : ""
    ].filter(Boolean).map(escapeText).join(" · ")}</p></li>`).join("")}</ol>`);
}

function cuisineIds(record) {
  const source = record.kind === "recipe" ? record.makes : record.source;
  return notebook.names[source]?.cuisines || [];
}

function subtitle(record) {
  if (record.kind === "class") return `${record.course} / ${record.skill} / Lesson ${record.number}`;
  return cuisineIds(record).map(nameOf).join(", ") || label(record.kind);
}

function searchText(record) {
  const words = [titleOf(record), subtitle(record), record.id, ...Object.values(record.names),
    ...Object.values(record.aliases || {}).flat()];
  if (record.kind === "class") words.push(record.program, ...record.teaches.map(row => nameOf(row.thing)));
  return words.join(" ").toLocaleLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function updateLibrary() {
  document.querySelectorAll("[data-kind]").forEach(button => button.setAttribute("aria-pressed", button.dataset.kind === category));
  const query = document.getElementById("search").value.toLocaleLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").trim();
  const cuisine = document.getElementById("cuisine").value;
  filtered = entries.filter(record => record.kind === category && searchText(record).includes(query) && (!cuisine || cuisineIds(record).includes(cuisine)));
  if (category !== "class") filtered.sort((a, b) => titleOf(a).localeCompare(titleOf(b)));
  document.getElementById("result-count").textContent = `${filtered.length} ${category === "class" ? "classes" : kinds[category].toLowerCase()}`;
  document.getElementById("entry-list").innerHTML = filtered.length ? filtered.map(record =>
    `<a class="entry" href="${href(record.id)}" aria-current="${selected?.id === record.id}"><strong>${escapeText(titleOf(record))}</strong><small>${escapeText(subtitle(record))}</small></a>`).join("") :
    '<p class="muted">No matches. Try another word or cuisine.</p>';
  updateNext();
}

function updateNext() {
  const nav = document.getElementById("entry-navigation");
  if (!nav || !selected) return;
  const index = filtered.findIndex(record => record.id === selected.id);
  nav.innerHTML = index < 0 ? "" : [
    index > 0 ? `<a href="${href(filtered[index - 1].id)}">← ${escapeText(titleOf(filtered[index - 1]))}</a>` : "",
    index < filtered.length - 1 ? `<a href="${href(filtered[index + 1].id)}">${escapeText(titleOf(filtered[index + 1]))} →</a>` : ""
  ].join("");
}

function feedbackForm() {
  return `<section class="feedback" aria-labelledby="feedback-title">
    <h3 id="feedback-title">What do you think?</h3>
    <p>Rate how clear and useful this entry is, or suggest a change. Your experience helps us improve it.</p>
    <form id="feedback-form">
      <fieldset><legend>Your rating (optional)</legend><div class="ratings">${[1, 2, 3, 4, 5].map(number =>
        `<label class="rating"><input type="radio" name="rating" value="${number}">${number}</label>`).join("")}</div>
        <p class="fine">1 = needs a lot of work · 5 = clear and useful</p></fieldset>
      <label for="feedback-kind">What would you like us to look at?</label>
      <select id="feedback-kind" name="kind"><option>General feedback</option><option>Wording or clarity</option><option>Technique or method</option><option>Amounts or timing</option><option>Class order or practice</option><option>Safety concern</option></select>
      <label for="feedback-notes">Your notes or suggested changes (optional)</label>
      <textarea id="feedback-notes" name="notes" maxlength="1200" placeholder="For example: I’d explain this step a little differently…"></textarea>
      <p id="draft-status" class="fine" role="status"></p>
      <div class="actions"><a class="primary button" id="send-feedback" href="https://github.com/${notebook.repository}/issues/new" target="_blank" rel="noopener">Continue to GitHub ↗</a><button type="button" id="download-feedback">Download feedback</button></div>
      <p class="fine">GitHub sign-in and repository access are required. On the next page, select “Create issue” to send. Downloading saves a text file you can share yourself.</p>
      <p class="feedback-status" id="feedback-status" role="status" aria-live="polite"></p>
    </form>
    <p class="fine">Feedback is a suggestion. It does not automatically approve an entry or verify its safety.</p>
  </section>`;
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
  document.getElementById("feedback-status").textContent = "Please choose a rating or add a note first.";
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
      status.textContent = "Your draft was restored from this browser. It has not been sent.";
    }
  } catch { status.textContent = "Draft saving is unavailable in this browser. You can still send or download feedback."; }
  const save = () => {
    try {
      localStorage.setItem(key, JSON.stringify(feedbackValue()));
      status.textContent = "Draft saved in this browser. It has not been sent.";
    } catch { status.textContent = "Draft saving is unavailable. You can still send or download feedback."; }
    document.getElementById("feedback-status").textContent = "";
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
      document.getElementById("feedback-status").textContent = "These notes are too long for a GitHub link. Shorten them or download the feedback to share.";
      return;
    }
    event.currentTarget.href = url.href;
    document.getElementById("feedback-status").textContent = "Finish by selecting “Create issue” on GitHub. This site cannot confirm whether it was sent.";
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
    document.getElementById("feedback-status").textContent = "Feedback downloaded. Share the file with the notebook owner to send it.";
  });
}

function showEntry(record, focus) {
  selected = record;
  category = record.kind;
  const body = record.kind === "class" ? classBody(record) : record.kind === "technique" ? techniqueBody(record) : recipeBody(record);
  const content = document.getElementById("content");
  content.innerHTML = `<div class="badges"><span class="badge">${escapeText(kinds[record.kind])}</span><span class="badge tier">${escapeText(record.tier)}</span></div>
    <p class="eyebrow">${escapeText(subtitle(record))}</p><h2>${escapeText(titleOf(record))}</h2>${body}${feedbackForm()}
    <nav id="entry-navigation" class="bottom-nav" aria-label="More entries"></nav>
    <p class="fine"><a href="https://github.com/${notebook.repository}/blob/${notebook.commit}/graph/${record.source}.json" target="_blank" rel="noopener">Read the source entry on GitHub ↗</a></p>`;
  document.title = `${titleOf(record)} - The cooking notebook`;
  connectFeedback(record);
  updateLibrary();
  if (focus) {
    content.focus({preventScroll: true});
    content.scrollIntoView({block: "start"});
  }
}

function navigate(focus) {
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
document.getElementById("source-link").href = `https://github.com/${notebook.repository}/tree/${notebook.commit}`;
window.addEventListener("hashchange", () => navigate(true));
navigate(false);
