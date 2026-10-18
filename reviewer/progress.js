"use strict";

const reviewProgress = new Map();
const feedbackDrafts = new Set();
let progressPersistent = true;

function progressKey(record) { return `cooking-notebook-progress:${record.id}:${record.hash}`; }

function storedValue(key) {
  let value;
  try { value = localStorage.getItem(key); }
  catch { progressPersistent = false; return null; }
  try { return JSON.parse(value); }
  catch { return null; }
}

function hasFeedback(value) {
  return /^[1-5]$/.test(value?.rating || "") || (typeof value?.notes === "string" && value.notes.trim().length > 0);
}

function loadProgress() {
  reviewProgress.clear();
  feedbackDrafts.clear();
  for (const record of entries) {
    const marker = storedValue(progressKey(record));
    if (marker && ["looked", "revisit"].includes(marker.state)) reviewProgress.set(record.id, marker);
    const draft = storedValue(`cooking-notebook:${record.id}:${record.hash}`);
    if (hasFeedback(draft)) feedbackDrafts.add(record.id);
  }
}

function progressState(record) {
  const state = reviewProgress.get(record.id)?.state;
  if (state === "looked" || state === "revisit") return state;
  return feedbackDrafts.has(record.id) ? "draft" : "todo";
}

function progressLabel(record) {
  return {looked: "Looked over", revisit: "Revisit", draft: "Note not sent yet", todo: "To look at"}[progressState(record)];
}

function progressMatches(record, filter) {
  if (filter === "all") return true;
  if (filter === "draft") return feedbackDrafts.has(record.id);
  return (reviewProgress.get(record.id)?.state || "todo") === filter;
}

function updateProgressSummary(records, title) {
  const looked = records.filter(record => reviewProgress.get(record.id)?.state === "looked").length;
  const revisit = records.filter(record => reviewProgress.get(record.id)?.state === "revisit").length;
  const drafts = records.filter(record => feedbackDrafts.has(record.id)).length;
  document.getElementById("progress-headline").textContent = `${looked} of ${records.length} ${title} looked over`;
  const meter = document.getElementById("progress-meter");
  meter.max = Math.max(records.length, 1);
  meter.value = looked;
  document.getElementById("progress-summary").textContent = `${revisit} marked to revisit · ${drafts} with a note not sent yet`;
}

function progressPanel(record) {
  const query = new URLSearchParams({q: `is:issue in:body "${record.id}"`});
  return `<section class="progress-panel" aria-labelledby="progress-title">
    <h3 id="progress-title">Done with this one?</h3>
    <p>Mark it so you can find your place next time.</p>
    <div class="choice-row" role="group" aria-label="Mark your progress">${[["looked", "Looked over"], ["revisit", "Revisit later"], ["todo", "To look at"]].map(([state, title]) =>
      `<button type="button" data-progress-state="${state}" aria-pressed="false">${title}</button>`).join("")}</div>
    <p id="entry-progress" class="fine" role="status"></p>
    <p id="progress-storage-note" class="fine"></p>
    <p class="fine">Marking an entry does not send your note or approve the entry.
      <a href="https://github.com/${notebook.repository}/issues?${escapeText(query.toString())}" target="_blank" rel="noopener">See notes already sent on GitHub ↗</a></p>
  </section>`;
}

function updateProgressPanel(record) {
  const marker = reviewProgress.get(record.id);
  const date = marker?.at && !Number.isNaN(Date.parse(marker.at)) ? new Date(marker.at).toLocaleString() : "";
  document.getElementById("entry-progress").textContent = "Right now: " + progressLabel(record) + (date ? ` · marked ${date}` : "");
  document.querySelectorAll("[data-progress-state]").forEach(button =>
    button.setAttribute("aria-pressed", button.dataset.progressState === (marker?.state || "todo")));
  document.getElementById("progress-storage-note").textContent = progressPersistent ?
    "Your marks are kept in this browser only, for this version of the entry. They do not move to other devices." :
    "This browser cannot save your marks. They last only until you close the page.";
}

function connectProgress(record) {
  updateProgressPanel(record);
  document.querySelector(".progress-panel").addEventListener("click", event => {
    const button = event.target.closest("[data-progress-state]");
    if (!button) return;
    const state = button.dataset.progressState;
    if (state === "todo") reviewProgress.delete(record.id);
    else reviewProgress.set(record.id, {state, at: new Date().toISOString()});
    try {
      if (state === "todo") localStorage.removeItem(progressKey(record));
      else localStorage.setItem(progressKey(record), JSON.stringify(reviewProgress.get(record.id)));
    } catch { progressPersistent = false; }
    updateProgressPanel(record);
    updateLibrary();
  });
}

function trackFeedbackDraft(record, value) {
  const before = feedbackDrafts.has(record.id);
  if (hasFeedback(value)) feedbackDrafts.add(record.id);
  else feedbackDrafts.delete(record.id);
  updateProgressPanel(record);
  if (before !== feedbackDrafts.has(record.id)) updateLibrary();
}
