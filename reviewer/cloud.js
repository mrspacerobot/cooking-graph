// Shared saving for the notebook. Mirrors the notebook's own browser keys to one
// Firestore document each, so independent items never overwrite one another.
// For one item, the latest save wins. Nothing here changes a tier or a safety fact.
import {initializeApp} from "https://www.gstatic.com/firebasejs/13.0.0/firebase-app.js";
import {getAuth, signInWithEmailAndPassword, onAuthStateChanged, signOut}
  from "https://www.gstatic.com/firebasejs/13.0.0/firebase-auth.js";
import {initializeFirestore, persistentLocalCache, doc, setDoc, onSnapshot, collection, serverTimestamp}
  from "https://www.gstatic.com/firebasejs/13.0.0/firebase-firestore.js";

const config = window.notebookCloudConfig;
const PREFIX = "cooking-notebook";
const app = initializeApp(config.firebase);
const auth = getAuth(app);
const db = initializeFirestore(app, {localCache: persistentLocalCache()});

const bar = document.createElement("div");
bar.id = "cloud-bar";
bar.setAttribute("role", "status");
bar.style.cssText = "position:fixed;bottom:0;left:0;right:0;padding:.5rem 1rem;background:#fff8e8;border-top:1px solid #d9c9a3;font:14px system-ui;z-index:9;display:flex;gap:1rem;align-items:center;flex-wrap:wrap";
document.body.append(bar);
document.body.style.paddingBottom = "4rem";

let unsubscribe = null;
let pending = 0;
const remote = new Map();

function say(text, extra) {
  bar.textContent = text + " ";
  if (extra) bar.append(extra);
}

function button(label, click) {
  const b = document.createElement("button");
  b.type = "button";
  b.textContent = label;
  b.addEventListener("click", click);
  return b;
}

async function docId(key) {
  const bytes = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(key));
  return [...new Uint8Array(bytes)].map(byte => byte.toString(16).padStart(2, "0")).join("");
}

const timers = new Map();
function schedule(key, value) {
  clearTimeout(timers.get(key));
  timers.set(key, setTimeout(() => push(key, value), 600));
  say("Saving…");
}

async function push(key, value) {
  timers.delete(key);
  pending++;
  try {
    await setDoc(doc(db, "notebook", await docId(key)),
      {key, value: JSON.stringify(value), updatedAt: serverTimestamp()});
    pending--;
    if (!pending) say("Saved to the shared notebook.", button("Sign out", () => signOut(auth)));
  } catch (error) {
    pending--;
    say("Not saved yet. Your change is kept on this device and will go up when the connection returns.");
  }
}

window.addEventListener("notebook-save", event => {
  const {key, value} = event.detail;
  if (key.startsWith(PREFIX) && auth.currentUser) schedule(key, value);
});

function editing() {
  const active = document.activeElement;
  return Boolean(active && active.closest && active.closest("#content form"));
}

function applyRemote(snapshot) {
  const changed = [];
  for (const change of snapshot.docChanges()) {
    const data = change.doc.data({serverTimestamps: "estimate"});
    if (!data.key || !data.key.startsWith(PREFIX) || change.doc.metadata.hasPendingWrites) continue;
    remote.set(data.key, data.value);
    let current = null;
    try { current = localStorage.getItem(data.key); } catch { /* keep going */ }
    const next = data.value === "null" ? null : data.value;
    if (current === next) continue;
    try {
      if (next === null) localStorage.removeItem(data.key);
      else localStorage.setItem(data.key, next);
      changed.push(data.key);
    } catch { /* storage full or blocked: the page still shows the saved copy next load */ }
  }
  if (changed.length) window.dispatchEvent(new CustomEvent("notebook-remote", {detail: {keys: changed, editing: editing()}}));
}

// Push what this device holds that the cloud has not seen yet, such as notes
// written offline. The first snapshot tells us what the cloud already has.
function pushLocalOnly() {
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (!key.startsWith(PREFIX) || key === `${PREFIX}-cloud`) continue;
    if (!remote.has(key)) schedule(key, JSON.parse(localStorage.getItem(key)));
  }
}

function quizKey(input) { return `${PREFIX}-quiz:${input.dataset.quizCard}:${input.dataset.quizQuestion}`; }

function connectQuiz() {
  for (const input of document.querySelectorAll("#content input[data-quiz-card]")) {
    let saved = null;
    try { saved = JSON.parse(localStorage.getItem(quizKey(input)) || "null"); } catch { /* none */ }
    input.checked = saved !== null && String(saved.choice) === input.value;
    if (input.dataset.bound) continue;
    input.dataset.bound = "yes";
    input.addEventListener("change", () =>
      window.saveNotebookValue(quizKey(input), {choice: Number(input.value), at: new Date().toISOString()}));
  }
}
window.addEventListener("notebook-entry", connectQuiz);
window.addEventListener("notebook-remote", connectQuiz);
// The first entry is drawn before this module runs.
connectQuiz();

function showLogin(message) {
  if (unsubscribe) { unsubscribe(); unsubscribe = null; }
  const form = document.createElement("form");
  const password = document.createElement("input");
  password.type = "password";
  password.autocomplete = "current-password";
  password.placeholder = "Notebook password";
  password.setAttribute("aria-label", "Notebook password");
  const go = document.createElement("button");
  go.textContent = "Open the shared notebook";
  form.append(password, go);
  form.addEventListener("submit", async event => {
    event.preventDefault();
    try { await signInWithEmailAndPassword(auth, config.email, password.value); }
    catch (error) {
      const wrong = ["auth/invalid-credential", "auth/wrong-password", "auth/invalid-login-credentials"].includes(error.code);
      showLogin(wrong ? "That password did not work. Please try again."
        : `Could not sign in just now (${error.code || "network problem"}). Check the connection and try again.`);
    }
  });
  say(message || "Sign in to save and share your answers.", form);
}

onAuthStateChanged(auth, user => {
  if (!user) { showLogin(); return; }
  say("Connecting…");
  let first = true;
  unsubscribe = onSnapshot(collection(db, "notebook"), snapshot => {
    applyRemote(snapshot);
    if (first) { first = false; pushLocalOnly(); }
    if (!pending && !timers.size) say(snapshot.metadata.fromCache ? "Offline. Changes will be saved when you reconnect." : "Saved to the shared notebook.", button("Sign out", () => signOut(auth)));
  }, () => say("Could not reach the shared notebook. Your changes are kept on this device."));
});
