"use strict";

const approval = JSON.parse(document.getElementById('approval-data').textContent);
const approvalUnits = Object.values(approval.units);
const decisions = new Map();
let currentUnit = null;
let approvalStorage = true;
const byId = id => document.getElementById(id);
const escapeApproval = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[char]);
const words = value => value.replaceAll('_', ' ').replaceAll('-', ' ');

function reviewerId() { return byId('approval-reviewer').value; }
function decisionKey(unit) { return `cooking-approval:${reviewerId() || 'unassigned'}:${unit.id}:${unit.seen}`; }
function shortName(id) { return id.replace(/^reviewer\//, ''); }
function statusNote(unit) {
  if (unit.field !== 'safety') return plainTier(unit.status);
  return unit.status === 'verified' ? 'A person checked these safety answers against a trusted source.' : plainTier('unverified');
}
function queueState(unit) {
  if (decisions.has(unit.id)) return decisions.get(unit.id).verdict === 'approved' ? ['looked', 'Approval ready to send'] : ['draft', 'Correction ready to send'];
  return alreadyApproved(unit) ? ['looked', 'Already approved in the graph'] : ['todo', 'Waiting for a decision'];
}
function alreadyApproved(unit) { return unit.field === 'safety' ? unit.status === 'verified' : ['reviewed','verified','cook-tested'].includes(unit.status); }

function loadDecisions() {
  decisions.clear();
  for (const unit of approvalUnits) {
    try {
      const saved = JSON.parse(localStorage.getItem(decisionKey(unit)) || 'null');
      if (saved && saved.thing === unit.thing && saved.field === unit.field && saved.seen === unit.seen &&
          saved.attested === true && ['approved','rejected'].includes(saved.verdict) &&
          typeof saved.note === 'string' && saved.note.trim() && Array.isArray(saved.sources) &&
          saved.sources.every(id => Object.keys(approval.sources).includes(id))) decisions.set(unit.id, saved);
    } catch (error) { if (!(error instanceof SyntaxError)) approvalStorage = false; }
  }
  updateSession();
}

function updateSession(message = '') {
  const person = approval.reviewers[reviewerId()];
  const scope = person?.knows.length === Object.keys(approval.cuisines).length ? 'all current cuisines' :
    person?.knows.map(row => approval.cuisines[row.cuisine]).join(', ') || 'none recorded';
  byId('reviewer-scope').textContent = person ?
    `Registered human reviewer for ${scope}. ${person.safety_authority ? 'Safety authority is recorded.' : 'For a safety approval, tick a source you checked yourself.'}` :
    'No name chosen. The owner will need to confirm who you are before using your decisions.';
  byId('staged-count').textContent = decisions.size ? `${decisions.size} ${decisions.size === 1 ? 'decision' : 'decisions'} ready to send` : 'No decisions yet';
  byId('session-status').textContent = `${message ? message + ' ' : ''}Nothing changes in the notebook until the owner applies your decisions. ${approvalStorage ? 'Your decisions are kept in this browser for this reviewer name.' : 'This browser cannot keep your decisions: save them to a file before leaving.'}`;
}

function matchingUnits() {
  const mode = byId('approval-mode').value;
  const query = byId('approval-search').value.trim().toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'');
  const kind = byId('approval-kind').value;
  const filter = byId('approval-filter').value;
  return approvalUnits.filter(unit => (mode === 'safety') === (unit.field === 'safety') && (!kind || kind === unit.kind) &&
    `${unit.name} ${unit.thing}`.toLocaleLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').includes(query) &&
    (filter === 'all' || (filter === 'decided' ? decisions.has(unit.id) : !decisions.has(unit.id) && !alreadyApproved(unit))))
    .sort((a,b) => a.name.localeCompare(b.name));
}

function renderQueue() {
  const found = matchingUnits();
  byId('approval-count').textContent = `Showing ${found.length} ${found.length === 1 ? 'entry' : 'entries'}`;
  byId('approval-list').innerHTML = found.length ? found.map(unit => `<a class="entry" href="#${encodeURIComponent(unit.id)}" aria-current="${currentUnit?.id === unit.id}"><strong>${escapeApproval(unit.name)}</strong><small>${escapeApproval(words(unit.kind))} · ${escapeApproval(unit.status)}</small><small class="progress-label" data-state="${queueState(unit)[0]}">${queueState(unit)[1]}</small></a>`).join('') : '<p class="muted">Nothing matches. Try another word, or set Kind and Show back to everything.</p>';
  return found;
}

function readable(value) {
  if (value === null) return '<span class="muted">Not recorded</span>';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (Array.isArray(value)) return value.length ? `<ul>${value.map(row => `<li>${readable(row)}</li>`).join('')}</ul>` : '<span class="muted">None recorded</span>';
  if (typeof value === 'object') {
    // An amount reads as one phrase, such as "200 gram", with the recorded unit kept exactly.
    const keys = Object.keys(value).sort().join(',');
    if (!keys) return '<span class="muted">None recorded</span>';
    if (keys === 'unit,value') return `${escapeApproval(value.value)} ${escapeApproval(words(value.unit))}`;
    if (keys === 'from,to,unit') return `${escapeApproval(value.from)} to ${escapeApproval(value.to)} ${escapeApproval(words(value.unit))}`;
    const labels = {does:'What it does', is:'What it is', how:'Method', stands_in_for:'Substitution claims', when:'Applies in', not_when:'Excluded in'};
    return `<dl class="record-fields">${Object.entries(value).map(([key, inner]) => `<dt>${escapeApproval(labels[key] || words(key))}</dt><dd>${readable(inner)}</dd>`).join('')}</dl>`;
  }
  if (typeof value === 'string' && /^https?:\/\//.test(value)) return `<a href="${escapeApproval(value)}" target="_blank" rel="noopener">${escapeApproval(value)}</a>`;
  return escapeApproval(approval.names[value] || value);
}

function safetyFacts(unit) {
  const held = new Map(unit.raw.contains.map(row => [row.fact,row]));
  return `<p class="notice"><strong>Check every answer below for this ingredient.</strong> A regulator's list says what counts as an allergen. It does not say whether this particular ingredient contains it, so look for evidence about this ingredient itself.</p>
    <div class="fact-grid">${Object.entries(approval.facts).map(([id,fact]) => {
      const row = held.get(id);
      const free = unit.raw.free_of.includes(id);
      return `<section class="fact-card"><h3>${escapeApproval(fact.names.en)}</h3><p class="fine">${escapeApproval(words(fact.concern))}</p>
        <p>Recorded answer: <span class="answer ${row ? 'contains' : free ? 'free' : 'none'}">${row ? 'Contains' : free ? 'Free of' : 'No answer recorded'}</span></p>
        ${row ? `<p>${escapeApproval(row.basis)}</p><p class="fine">${row.certain ? 'Marked certain in the record.' : 'Recorded strictly because uncertain. Approval does not remove this uncertainty flag.'}</p>` : '<p class="fine">No individual basis is recorded for this answer. Check it against your evidence.</p>'}
        <details><summary>What this means, and references</summary><p>${escapeApproval(fact.means)}</p>${fact.regulated.map(reg => {
          const source = approval.sources[reg.source];
          return `<p class="fine">${escapeApproval(words(reg.where))}: ${escapeApproval(reg.name)} · ${escapeApproval(reg.tier)}${source ? ` · <a href="${escapeApproval(source.url)}" target="_blank" rel="noopener">Open reference</a>` : ''}${reg.exemptions ? `<br>Exemptions: ${escapeApproval(reg.exemptions)}` : ''}${reg.note ? `<br>${escapeApproval(reg.note)}` : ''}</p>`;
        }).join('')}</details></section>`;
    }).join('')}</div>${unit.raw.note ? `<p><strong>Ingredient safety note:</strong> ${escapeApproval(unit.raw.note)}</p>` : ''}`;
}

function showApproval(unit, focus = false, notice = '') {
  currentUnit = unit;
  const saved = decisions.get(unit.id);
  const safety = unit.field === 'safety';
  const cuisines = Object.entries(approval.cuisines);
  byId('approval-content').innerHTML = `<p class="saved-banner" role="status">${escapeApproval(notice)}</p><button type="button" class="to-list">↑ Back to the list</button>
    <div class="badges"><span class="badge">${safety ? 'Ingredient safety' : escapeApproval(words(unit.kind))}</span><span class="badge tier">${escapeApproval(unit.status)}</span></div>
    <h2>${escapeApproval(unit.name)}</h2>
    <p class="tier-note"><strong>What “${escapeApproval(unit.status)}” means:</strong> ${escapeApproval(statusNote(unit))}</p>
    <p class="fine">You are checking ${safety ? 'the allergen and diet answers only' : 'the whole cooking record, including its statements. Safety answers are checked separately'}. <a href="https://github.com/${approval.repository}/blob/${approval.commit}/graph/${unit.thing}.json" target="_blank" rel="noopener">Read this exact source version ↗</a></p>
    ${safety ? safetyFacts(unit) : readable(unit.raw)}
    ${!safety && unit.raw.steps?.some(step => step.safety_points?.length) ? '<p class="notice">This recipe has open safety points. Approving the writing does not resolve those points or supply verified cooking guidance.</p>' : ''}
    <section class="feedback"><h3><span class="step-number" aria-hidden="true">3</span>Your decision</h3>
      ${alreadyApproved(unit) ? '<p>This entry is already approved in the graph. Replacing or withdrawing an approval needs a separate review by the owner.</p>' : ''}
      ${safety ? '' : `<div class="field"><label for="decision-cuisine">Which cuisine are you answering for?</label><select id="decision-cuisine">${cuisines.map(([id,name]) => `<option value="${id}">${escapeApproval(name)}</option>`).join('')}</select></div>`}
      <fieldset id="decision-sources"><legend>Which sources did you check yourself?</legend>
        <p class="fine">${safety ? 'A safety approval needs at least one source you checked, unless the owner gave you safety authority.' : 'Tick any you used. If you answer from your own knowledge, say so in your note.'}</p>
        <div class="source-list">${Object.entries(approval.sources).map(([id,source]) => `<div class="source-card"><label class="check"><input type="checkbox" value="${escapeApproval(id)}"><strong>${escapeApproval(source.title)}</strong></label>
          <p class="fine"><a href="${escapeApproval(source.url)}" target="_blank" rel="noopener">Open the source ↗</a> · read on ${escapeApproval(source.read_on)}</p>
          <details><summary>What was taken from it</summary><p class="fine">${escapeApproval(source.taken || 'No extraction note recorded.')}</p></details></div>`).join('')}</div>
      </fieldset>
      <div class="field"><label for="decision-note">What did you check, or what needs correcting?</label><textarea id="decision-note" maxlength="4000" placeholder="For example: I checked the label rules and this ingredient's own description; the answers match."></textarea></div>
      <label class="check attestation"><input id="decision-attest" type="checkbox"><span>I am a human reviewer and personally checked this exact version${safety ? ', including every allergen and dietary answer above' : ''}.</span></label>
      <div class="actions"><button type="button" id="approve-unit" class="primary" ${alreadyApproved(unit) ? 'disabled' : ''}>${safety ? 'Approve safety verification' : 'Approve this content'}</button><button type="button" id="reject-unit" ${alreadyApproved(unit) ? 'disabled' : ''}>Needs a correction</button>${saved ? '<button type="button" id="clear-decision">Undo my decision</button>' : ''}</div>
      <p id="decision-status" role="status" class="feedback-status">${saved ? `Your decision (${saved.verdict === 'approved' ? 'approve' : 'needs a correction'}) is ready to send. It has not changed the notebook.` : ''}</p>
      <p class="fine">Your decision is kept for the owner to review. Nothing is applied straight away.</p>
    </section>`;
  byId('approval-content').querySelector('.to-list').addEventListener('click', () => {
    byId('library').focus({preventScroll:true}); byId('library').scrollIntoView({block:'start'});
  });
  if (!safety) byId('decision-cuisine').value = saved?.cuisine || unit.cuisines[0] || approval.reviewers[reviewerId()]?.knows[0]?.cuisine || cuisines[0]?.[0] || '';
  byId('decision-note').value = saved?.note || '';
  for (const box of byId('decision-sources').querySelectorAll('input')) box.checked = saved?.sources.includes(box.value) || false;
  byId('approve-unit').addEventListener('click', () => stageDecision('approved'));
  byId('reject-unit').addEventListener('click', () => stageDecision('rejected'));
  byId('clear-decision')?.addEventListener('click', () => {
    decisions.delete(unit.id);
    try { localStorage.removeItem(decisionKey(unit)); } catch { approvalStorage = false; }
    updateSession(); showApproval(unit); renderQueue();
  });
  renderQueue();
  if (focus) { byId('approval-content').focus({preventScroll:true}); byId('approval-content').scrollIntoView({block:'start'}); }
}

function stageDecision(verdict) {
  const unit = currentUnit;
  const sources = [...byId('decision-sources').querySelectorAll('input:checked')].map(box => box.value);
  const note = byId('decision-note').value.trim();
  const fail = message => { byId('decision-status').textContent = message; byId('decision-status').classList.add('problem'); };
  if (Object.keys(approval.reviewers).length && !reviewerId()) return fail('Please choose your reviewer name in step 1 first.');
  if (!byId('decision-attest').checked) return fail('Please confirm that you personally checked this exact version.');
  if (!note) return fail('Please write a short note: what you checked, or what needs correcting.');
  if (/[\u2014]|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/.test(note)) return fail('Use a plain hyphen, and leave email addresses out of the review note.');
  if (verdict === 'approved' && unit.field === 'safety' && !sources.length && !approval.reviewers[reviewerId()]?.safety_authority) return fail('To approve safety, tick at least one source you checked yourself.');
  const decision = {thing:unit.thing,field:unit.field,seen:unit.seen,verdict,cuisine:unit.field === 'safety' ? null : byId('decision-cuisine').value,sources,note,attested:true};
  decisions.set(unit.id,decision);
  try { localStorage.setItem(decisionKey(unit),JSON.stringify(decision)); } catch { approvalStorage = false; }
  const done = `Saved: ${unit.name} - ${verdict === 'approved' ? 'approval' : 'correction'} ready to send.`;
  updateSession(done);
  const next = renderQueue().find(other => other.id !== unit.id);
  if (next && byId('approval-filter').value === 'pending') {
    history.replaceState(null,'','#' + encodeURIComponent(next.id)); showApproval(next,true,`${done} Here is the next one.`);
  } else showApproval(unit,false,done);
}

function packet() {
  return {version:1,commit:approval.commit,reviewer:reviewerId() || null,on:new Date().toISOString().slice(0,10),decisions:[...decisions.values()]};
}

function downloadPacket() {
  if (!decisions.size) return updateSession('There is nothing to save yet: make a decision on an entry first.');
  const url = URL.createObjectURL(new Blob([JSON.stringify(packet(),null,2) + '\n'],{type:'text/plain;charset=utf-8'}));
  const anchor = document.createElement('a');anchor.href=url;anchor.download='cooking-approvals.txt';anchor.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  updateSession('Thank you! The file is saved. Attach it to a GitHub message or send it to the owner.');
}

byId('approval-reviewer').innerHTML = '<option value="">Choose your name</option>' + Object.keys(approval.reviewers).map(id => `<option value="${id}">${escapeApproval(shortName(id))}</option>`).join('');
byId('approval-kind').innerHTML += [...new Set(approvalUnits.map(unit=>unit.kind))].sort().map(kind=>`<option value="${kind}">${escapeApproval(words(kind))}</option>`).join('');
byId('approval-reviewer').addEventListener('change',()=>{loadDecisions();if(currentUnit)showApproval(currentUnit);});
for(const id of ['approval-mode','approval-kind','approval-filter','approval-search']) byId(id).addEventListener(id === 'approval-search' ? 'input' : 'change',()=>{const found=renderQueue();if(found.length)showApproval(found[0]);});
byId('download-approvals').addEventListener('click',downloadPacket);
byId('submit-approvals').href = `https://github.com/${approval.repository}/issues/new`;
byId('submit-approvals').addEventListener('click',event=>{
  if(!decisions.size){event.preventDefault();return updateSession('There is nothing to send yet: make a decision on an entry first.');}
  const title='[Human approvals] ' + new Date().toISOString().slice(0,10);
  let body='I personally reviewed these exact units. Please confirm my reviewer registration and prepare a pull request.\n\n```json\n' + JSON.stringify(packet(),null,2) + '\n```';
  const url=new URL(`https://github.com/${approval.repository}/issues/new`);url.searchParams.set('title',title);url.searchParams.set('body',body);
  if(url.href.length>8000){url.searchParams.set('body',`I personally reviewed ${decisions.size} units from commit ${approval.commit}. I will attach the downloaded cooking-approvals.txt file. Please confirm my reviewer registration and prepare a pull request.`);updateSession('You have many decisions: save them to a file and attach it to the GitHub message before pressing Create issue.');}
  else updateSession('Thank you! GitHub opened in a new tab. Press Create issue there to send. This page cannot tell whether it was sent.');
  event.currentTarget.href=url.href;
});
window.addEventListener('hashchange',()=>{try{const unit=approval.units[decodeURIComponent(location.hash.slice(1))];if(unit){byId('approval-mode').value=unit.field==='safety'?'safety':'content';showApproval(unit,true);}}catch{}});
loadDecisions();
let initial;try{initial=approval.units[decodeURIComponent(location.hash.slice(1))];}catch{}
if(initial)byId('approval-mode').value=initial.field==='safety'?'safety':'content';
initial ||= matchingUnits()[0];
if(initial)showApproval(initial);else byId('approval-content').textContent='No entries are awaiting review.';
