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

function progressLabel(record) {
  const marker = reviewProgress.get(record.id);
  if (marker?.state === "looked") return "Looked over";
  if (marker?.state === "revisit") return "Revisit";
  return feedbackDrafts.has(record.id) ? "Feedback draft" : "To look at";
}

function progressMatches(record, filter) {
  if (filter === "all") return true;
  if (filter === "draft") return feedbackDrafts.has(record.id);
  return (reviewProgress.get(record.id)?.state || "todo") === filter;
}

function updateProgressSummary(records) {
  const looked = records.filter(record => reviewProgress.get(record.id)?.state === "looked").length;
  const revisit = records.filter(record => reviewProgress.get(record.id)?.state === "revisit").length;
  const drafts = records.filter(record => feedbackDrafts.has(record.id)).length;
  document.getElementById("progress-summary").textContent = `${looked} of ${records.length} looked over · ${revisit} to revisit · ${drafts} feedback drafts`;
}

function progressPanel(record) {
  const query = new URLSearchParams({q: `is:issue in:body "${record.id}"`});
  return `<section class="progress-panel" aria-labelledby="progress-title">
    <h3 id="progress-title">Your place in the notebook</h3>
    <p id="entry-progress" class="fine" role="status"></p>
    <div class="actions" role="group" aria-label="Mark your progress">${[["todo", "To look at"], ["looked", "Looked over"], ["revisit", "Revisit"]].map(([state, title]) =>
      `<button type="button" data-progress-state="${state}" aria-pressed="false">${title}</button>`).join("")}</div>
    <p id="progress-storage-note" class="fine"></p>
    <p class="fine">These markers do not confirm feedback was submitted or formally approve an entry.
      <a href="https://github.com/${notebook.repository}/issues?${escapeText(query.toString())}" target="_blank" rel="noopener">Find feedback on GitHub ↗</a></p>
  </section>`;
}

function updateProgressPanel(record) {
  const marker = reviewProgress.get(record.id);
  const date = marker?.at && !Number.isNaN(Date.parse(marker.at)) ? new Date(marker.at).toLocaleString() : "";
  document.getElementById("entry-progress").textContent = progressLabel(record) + (date ? ` · Marked ${date}` : "");
  document.querySelectorAll("[data-progress-state]").forEach(button =>
    button.setAttribute("aria-pressed", button.dataset.progressState === (marker?.state || "todo")));
  document.getElementById("progress-storage-note").textContent = progressPersistent ?
    "Progress is saved in this browser for this version of the entry. It is not shared across devices." :
    "Browser storage is unavailable. Progress is kept for this visit only.";
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
