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
    `Registered human reviewer. Cuisine coverage: ${scope}. ${person.safety_authority ? 'Safety authority is recorded.' : 'Safety decisions require recorded source evidence.'}` :
    'No reviewer is assigned to this file. The owner must identify and register its human author before applying it.';
  byId('session-status').textContent = `${decisions.size} decisions staged; none applied to the graph. ${approvalStorage ? 'Saved in this browser for this reviewer and version.' : 'Storage is unavailable; download before leaving this page.'} ${message}`;
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
  byId('approval-count').textContent = `${found.length} entries · ${decisions.size} staged decisions`;
  byId('approval-list').innerHTML = found.length ? found.map(unit => `<a class="entry" href="#${encodeURIComponent(unit.id)}" aria-current="${currentUnit?.id === unit.id}"><strong>${escapeApproval(unit.name)}</strong><small>${escapeApproval(words(unit.kind))} · ${escapeApproval(unit.status)}</small><small>${decisions.has(unit.id) ? decisions.get(unit.id).verdict === 'approved' ? 'Approval staged' : 'Correction needed' : alreadyApproved(unit) ? 'Approved in the graph' : 'Awaiting a decision'}</small></a>`).join('') : '<p class="muted">No entries match these filters.</p>';
  return found;
}

function readable(value) {
  if (value === null) return '<span class="muted">Not recorded</span>';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  if (Array.isArray(value)) return value.length ? `<ul>${value.map(row => `<li>${readable(row)}</li>`).join('')}</ul>` : '<span class="muted">None recorded</span>';
  if (typeof value === 'object') {
    const labels = {does:'What it does', is:'What it is', how:'Method', stands_in_for:'Substitution claims', when:'Applies in', not_when:'Excluded in'};
    return `<dl class="record-fields">${Object.entries(value).map(([key, inner]) => `<dt>${escapeApproval(labels[key] || words(key))}</dt><dd>${readable(inner)}</dd>`).join('')}</dl>`;
  }
  if (typeof value === 'string' && /^https?:\/\//.test(value)) return `<a href="${escapeApproval(value)}" target="_blank" rel="noopener">${escapeApproval(value)}</a>`;
  return escapeApproval(approval.names[value] || value);
}

function safetyFacts(unit) {
  const held = new Map(unit.raw.contains.map(row => [row.fact,row]));
  return `<p class="notice">Check every allergen and dietary answer for this ingredient. Regulatory lists define categories; they do not establish what a particular ingredient contains. Cite evidence for this ingredient.</p>
    <div class="fact-grid">${Object.entries(approval.facts).map(([id,fact]) => {
      const row = held.get(id);
      const free = unit.raw.free_of.includes(id);
      return `<section class="fact-card"><h3>${escapeApproval(fact.names.en)}</h3><p class="fine">${escapeApproval(words(fact.concern))}</p>
        <p><strong>Current assertion: ${row ? 'Contains' : free ? 'Free of' : 'No answer recorded'}</strong></p>
        ${row ? `<p>${escapeApproval(row.basis)}</p><p class="fine">${row.certain ? 'Marked certain in the record.' : 'Recorded strictly because uncertain. Approval does not remove this uncertainty flag.'}</p>` : '<p class="fine">No individual basis is recorded for this answer. Check it against your evidence.</p>'}
        <details><summary>Definition and references</summary><p>${escapeApproval(fact.means)}</p>${fact.regulated.map(reg => {
          const source = approval.sources[reg.source];
          return `<p class="fine">${escapeApproval(words(reg.where))}: ${escapeApproval(reg.name)} · ${escapeApproval(reg.tier)}${source ? ` · <a href="${escapeApproval(source.url)}" target="_blank" rel="noopener">Open reference</a>` : ''}${reg.exemptions ? `<br>Exemptions: ${escapeApproval(reg.exemptions)}` : ''}${reg.note ? `<br>${escapeApproval(reg.note)}` : ''}</p>`;
        }).join('')}</details></section>`;
    }).join('')}</div>${unit.raw.note ? `<p><strong>Ingredient safety note:</strong> ${escapeApproval(unit.raw.note)}</p>` : ''}`;
}

function showApproval(unit, focus = false) {
  currentUnit = unit;
  const saved = decisions.get(unit.id);
  const safety = unit.field === 'safety';
  const cuisines = Object.entries(approval.cuisines);
  byId('approval-content').innerHTML = `<div class="badges"><span class="badge">${safety ? 'Ingredient safety' : escapeApproval(words(unit.kind))}</span><span class="badge tier">${escapeApproval(unit.status)}</span></div>
    <h2>${escapeApproval(unit.name)}</h2><p class="fine">You are checking ${safety ? 'the safety facts only' : 'the complete culinary record, including its statements'}. <a href="https://github.com/${approval.repository}/blob/${approval.commit}/graph/${unit.thing}.json" target="_blank" rel="noopener">Read this exact source version ↗</a></p>
    ${safety ? safetyFacts(unit) : readable(unit.raw)}
    ${!safety && unit.raw.steps?.some(step => step.safety_points?.length) ? '<p class="notice">This recipe has open safety points. Approving the writing does not resolve those points or supply verified cooking guidance.</p>' : ''}
    <section class="feedback"><h3>Your human decision</h3>
      ${alreadyApproved(unit) ? '<p>This unit already has approval in the graph. Replacing or withdrawing it requires an explicit superseding review from the owner.</p>' : ''}
      ${safety ? '' : `<label for="decision-cuisine">Cuisine you are answering for</label><select id="decision-cuisine">${cuisines.map(([id,name]) => `<option value="${id}">${escapeApproval(name)}</option>`).join('')}</select>`}
      <label for="decision-sources">Sources you personally checked${safety ? ' (required unless safety authority is recorded)' : ' (or explain your own knowledge below)'}</label>
      <select id="decision-sources" multiple size="5">${Object.entries(approval.sources).map(([id,source]) => `<option value="${id}">${escapeApproval(source.title)}</option>`).join('')}</select>
      <details><summary>Open the recorded sources</summary><ul>${Object.values(approval.sources).map(source => `<li><a href="${escapeApproval(source.url)}" target="_blank" rel="noopener">${escapeApproval(source.title)}</a><p class="fine">Read on ${escapeApproval(source.read_on)}. ${escapeApproval(source.taken || 'No extraction note recorded.')}</p></li>`).join('')}</ul></details>
      <label for="decision-note">What did you check? Or what needs correcting?</label><textarea id="decision-note" maxlength="4000" placeholder="Explain how the evidence supports these exact facts, or describe the correction needed."></textarea>
      <label class="attestation"><input id="decision-attest" type="checkbox"> I am a human reviewer and personally checked this exact version${safety ? ', including every allergen and dietary answer above' : ''}.</label>
      <div class="actions"><button type="button" id="approve-unit" class="primary" ${alreadyApproved(unit) ? 'disabled' : ''}>${safety ? 'Approve safety verification' : 'Approve this content'}</button><button type="button" id="reject-unit" ${alreadyApproved(unit) ? 'disabled' : ''}>Needs a correction</button>${saved ? '<button type="button" id="clear-decision">Remove staged decision</button>' : ''}</div>
      <p id="decision-status" role="status" class="fine">${saved ? 'This decision is staged and has not changed the graph.' : 'Your decision will be staged for owner review, not applied immediately.'}</p>
    </section>`;
  if (!safety) byId('decision-cuisine').value = saved?.cuisine || unit.cuisines[0] || approval.reviewers[reviewerId()]?.knows[0]?.cuisine || cuisines[0]?.[0] || '';
  byId('decision-note').value = saved?.note || '';
  for (const option of byId('decision-sources').options) option.selected = saved?.sources.includes(option.value) || false;
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
  const sources = [...byId('decision-sources').selectedOptions].map(option => option.value);
  const note = byId('decision-note').value.trim();
  const fail = message => { byId('decision-status').textContent = message; };
  if (Object.keys(approval.reviewers).length && !reviewerId()) return fail('Choose your registered reviewer alias before recording a decision.');
  if (!byId('decision-attest').checked) return fail('Please confirm that you personally checked this exact version.');
  if (!note) return fail('Please explain your evidence or the correction needed.');
  if (/[\u2014]|[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/.test(note)) return fail('Use a plain hyphen, and leave email addresses out of the review note.');
  if (verdict === 'approved' && unit.field === 'safety' && !sources.length && !approval.reviewers[reviewerId()]?.safety_authority) return fail('Safety verification needs a recorded source you checked, or an owner-granted safety authority.');
  const decision = {thing:unit.thing,field:unit.field,seen:unit.seen,verdict,cuisine:unit.field === 'safety' ? null : byId('decision-cuisine').value,sources,note,attested:true};
  decisions.set(unit.id,decision);
  try { localStorage.setItem(decisionKey(unit),JSON.stringify(decision)); } catch { approvalStorage = false; }
  updateSession(`${unit.name}: ${verdict === 'approved' ? 'approval staged' : 'correction requested'}.`);
  const next = renderQueue().find(other => other.id !== unit.id);
  if (next && byId('approval-filter').value === 'pending') {
    history.replaceState(null,'','#' + encodeURIComponent(next.id)); showApproval(next,true);
  } else showApproval(unit);
}

function packet() {
  return {version:1,commit:approval.commit,reviewer:reviewerId() || null,on:new Date().toISOString().slice(0,10),decisions:[...decisions.values()]};
}

function downloadPacket() {
  if (!decisions.size) return updateSession('Choose at least one decision first.');
  const url = URL.createObjectURL(new Blob([JSON.stringify(packet(),null,2) + '\n'],{type:'text/plain;charset=utf-8'}));
  const anchor = document.createElement('a');anchor.href=url;anchor.download='cooking-approvals.txt';anchor.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  updateSession('Approval file downloaded. It still needs owner application and merge.');
}

byId('approval-reviewer').innerHTML = '<option value="">Owner assigns reviewer when applying</option>' + Object.keys(approval.reviewers).map(id => `<option value="${id}">${escapeApproval(id)}</option>`).join('');
byId('approval-kind').innerHTML += [...new Set(approvalUnits.map(unit=>unit.kind))].sort().map(kind=>`<option value="${kind}">${escapeApproval(words(kind))}</option>`).join('');
byId('approval-reviewer').addEventListener('change',()=>{loadDecisions();if(currentUnit)showApproval(currentUnit);});
for(const id of ['approval-mode','approval-kind','approval-filter','approval-search']) byId(id).addEventListener(id === 'approval-search' ? 'input' : 'change',()=>{const found=renderQueue();if(found.length)showApproval(found[0]);});
byId('download-approvals').addEventListener('click',downloadPacket);
byId('submit-approvals').href = `https://github.com/${approval.repository}/issues/new`;
byId('submit-approvals').addEventListener('click',event=>{
  if(!decisions.size){event.preventDefault();return updateSession('Choose at least one decision first.');}
  const title='[Human approvals] ' + new Date().toISOString().slice(0,10);
  let body='I personally reviewed these exact units. Please confirm my reviewer registration and prepare a pull request.\n\n```json\n' + JSON.stringify(packet(),null,2) + '\n```';
  const url=new URL(`https://github.com/${approval.repository}/issues/new`);url.searchParams.set('title',title);url.searchParams.set('body',body);
  if(url.href.length>8000){url.searchParams.set('body',`I personally reviewed ${decisions.size} units from commit ${approval.commit}. I will attach the downloaded cooking-approvals.txt file. Please confirm my reviewer registration and prepare a pull request.`);updateSession('Download the approval file and attach it to this issue before submitting.');}
  else updateSession('Select Create issue on GitHub to submit. No graph approval has been applied yet.');
  event.currentTarget.href=url.href;
});
window.addEventListener('hashchange',()=>{try{const unit=approval.units[decodeURIComponent(location.hash.slice(1))];if(unit){byId('approval-mode').value=unit.field==='safety'?'safety':'content';showApproval(unit,true);}}catch{}});
loadDecisions();
let initial;try{initial=approval.units[decodeURIComponent(location.hash.slice(1))];}catch{}
if(initial)byId('approval-mode').value=initial.field==='safety'?'safety':'content';
initial ||= matchingUnits()[0];
if(initial)showApproval(initial);else byId('approval-content').textContent='No entries are awaiting review.';
