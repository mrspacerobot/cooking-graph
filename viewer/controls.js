const DATA=JSON.parse(document.getElementById('graph-data').textContent);
const nodes=new Map(DATA.nodes.map(n=>[n.id,n]));
const $=id=>document.getElementById(id);
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const title=id=>nodes.get(id)?.name??id;
const requested=location.hash.slice(1);
const initial=DATA.nodes.find(node=>node.kind==='technique')??DATA.nodes[0];
let selected=nodes.has(requested)?requested:initial?.id;
const kindLabel={technique:'Technique',recipe:'Recipe',dish:'Dish',ingredient:'Ingredient',preparation:'Preparation',group:'Ingredient group',fact:'Safety fact',form:'Form',equipment:'Equipment',source:'Source',cuisine:'Cuisine',program:'Program'};
function kind(id){return id.split('/')[0];}
function jumpButton(id,label){return `<button type="button" class="link text-left" data-jump="${esc(id)}">${esc(label??title(id))}</button>`;}
function badge(text,style='outline'){return `<span class="badge badge-sm badge-${style}">${esc(text)}</span>`;}
function filterPicks(){
 const needle=$('search').value.toLocaleLowerCase().trim();
 const matches=DATA.nodes.filter(n=>n.search.includes(needle));
 $('pick').innerHTML=matches.map(n=>`<option value="${esc(n.id)}">${esc(n.name)} · ${esc(kindLabel[kind(n.id)])}</option>`).join('');
 if(matches.some(n=>n.id===selected))$('pick').value=selected;
 if(!matches.length)$('pick').innerHTML='<option value="">No matching entry</option>';
}
function allowedEdge(edge){
 const mode=$('mode').value;
 if(mode==='all')return true;
 if(mode==='substitutions')return edge.relation==='stands_in_for';
 if(mode==='techniques')return ['technique','teaches'].includes(edge.relation);
 if(mode==='recipes')return ['makes','ingredients','options'].includes(edge.relation);
 return !['fact','source'].includes(kind(edge.target))&&!['fact','source'].includes(kind(edge.source))&&edge.relation!=='free_of';
}
function neighborhood(){
 const unique=new Map();
 for(const edge of DATA.edges){
  if((edge.source!==selected&&edge.target!==selected)||!allowedEdge(edge))continue;
  const incoming=edge.target===selected, other=incoming?edge.source:edge.target;
  const key=`${incoming}|${other}|${edge.label}`;
  unique.set(key,{...edge,incoming,other});
 }
 if($('mode').value==='substitutions'&&DATA.answers[selected]){
  for(const line of DATA.answers[selected].lines){
   for(const row of [...line.options,...line.excluded]){
    const status=row.reason==='not-in-this-context'?'excludes':row.reason?'no claim':'offers';
    const edge={source:selected,target:row.thing,relation:'stands_in_for',label:`${status} for ${title(line.original)}`,state:row.reason==='not-in-this-context'?'blocked':row.reason?'unknown':'allowed',incoming:false,other:row.thing};
    unique.set(`${row.thing}|${line.original}`,edge);
   }
  }
 }
 const priority={technique:0,teaches:0,stands_in_for:1,makes:2,ingredients:3,options:3,works_on:4,with:5,groups:6};
 return [...unique.values()].sort((a,b)=>(priority[a.relation]??9)-(priority[b.relation]??9)||a.label.localeCompare(b.label)||title(a.other).localeCompare(title(b.other)));
}
function ratioText(ratio){if(!ratio)return 'No ratio recorded';return `${ratio.stand_in}:${ratio.original} by ${ratio.by}`;}
function contextText(label, identifiers){
 if(!identifiers?.length)return '';
 return `<p class="text-xs soft mt-2">${label}: ${identifiers.map(title).map(esc).join(', ')}</p>`;
}
function claimStatus(row,contextMatched){
 if(!contextMatched)return row.allows?'Conditional stand-in':'Explicit exclusion';
 if(row.reason==='not-in-this-context')return 'Explicit exclusion';
 if(row.reason)return 'No applicable claim';
 return 'Applicable option';
}
function claimCard(original,row,contextMatched){
 const rejected=contextMatched?row.reason==='not-in-this-context':!row.allows;
 const unknown=contextMatched&&Boolean(row.reason)&&!rejected;
 let border='',colour='warning';
 if(rejected){border='blocked';colour='error';}
 else if(unknown){border='unknown';colour='outline';}
 const tier=row.tier?badge(row.tier):'';
 const reason=row.reason?`<p class="text-xs soft mt-2">Query reason: ${esc(row.reason.replaceAll('-',' '))}</p>`:'';
 return `<article class="claim ${border} bg-base-100 rounded-lg p-3 my-3">
  <div class="flex flex-wrap gap-2 mb-2">${badge(claimStatus(row,contextMatched),colour)}${tier}</div>
  <p class="font-semibold">${jumpButton(row.thing)} <span class="soft font-normal">for</span> ${jumpButton(original)}</p>
  <p class="text-sm soft mt-2">${esc(row.caveat??'No explanatory caveat recorded.')}</p>
  <p class="text-sm mt-2">${esc(ratioText(row.ratio))}</p>
  ${contextText('Applies in',row.when)}${contextText('Excluded in',row.not_when)}${reason}
 </article>`;
}
function showInspector(){
 const n=nodes.get(selected);
 if(!n){$('inspector').textContent='No graph entries in this checkout.';return;}
 const raw=n.raw;
 let html=`<p class="eyebrow">${esc(kindLabel[kind(selected)])}</p><h3 class="text-2xl font-semibold">${esc(n.name)}</h3><p class="text-xs soft">${esc(selected)}</p><div class="flex flex-wrap gap-2">${badge(raw.tier)}${raw.safety?badge('Safety '+raw.safety.state,raw.safety.state==='verified'?'outline':'warning'):''}</div>`;
 const description=raw.is??raw.behaviour??raw.what??raw.summary??raw.description;
 if(typeof description==='string')html+=`<p class="text-sm mt-2">${esc(description)}</p>`;
 if(kind(selected)==='recipe'){
  html+=`<p class="text-sm">Makes ${jumpButton(raw.makes)}</p><h4 class="font-semibold mt-4">Substitution answers for this recipe</h4><p class="soft text-sm">Context is checked by the existing command. Missing knowledge is separate from an explicit prohibition.</p>`;
  let count=0,unknown='';
  for(const line of DATA.answers[selected].lines){for(const row of [...line.options,...line.excluded]){const card=claimCard(line.original,row,true);if(row.reason&&row.reason!=='not-in-this-context')unknown+=card;else html+=card;count++;}}
  if(unknown)html+=`<details class="mt-3"><summary class="cursor-pointer text-sm">Candidates without an applicable claim</summary>${unknown}</details>`;
  if(!count)html+='<p class="soft text-sm">No alternative candidates recorded for these ingredient lines.</p>';
 }
 if(raw.stands_in_for?.length){html+='<h4 class="font-semibold mt-3">Recorded stand-in claims</h4><p class="soft text-sm">These apply only in their stated contexts. A link is not universal interchangeability.</p>';for(const row of raw.stands_in_for)html+=claimCard(row.thing,{...row,thing:selected},false);}
 if(raw.parts){html+='<h4 class="font-semibold mt-3">Parts and options</h4>';for(const part of raw.parts)html+=`<div class="text-sm mb-2"><strong>${esc(part.id)}</strong>${part.optional?' · optional':''}<p>${part.options.map(id=>jumpButton(id)).join(', ')}</p></div>`;}
 html+=`<details class="mt-4"><summary class="cursor-pointer text-sm font-semibold">Inspect the original record</summary><pre id="raw" class="mt-3">${esc(JSON.stringify(raw,null,2))}</pre></details>`;
 if(DATA.metadata.commit)html+=`<a class="link text-sm mt-4" href="https://github.com/mrspacerobot/cooking-graph/blob/${esc(DATA.metadata.commit)}/${esc(n.path)}" target="_blank" rel="noopener">View the record at the checked-out commit</a>`;
 $('inspector').innerHTML=html;
}
function render(){drawGraph(neighborhood());showInspector();}
function select(id){if(!nodes.has(id))return;selected=id;history.replaceState(null,'','#'+id);filterPicks();render();}
$('search').addEventListener('input',filterPicks);
$('pick').addEventListener('change',event=>select(event.target.value));
$('mode').addEventListener('change',render);
$('scope').addEventListener('change',render);
$('depth').addEventListener('change',render);
new ResizeObserver(sizeGraph).observe($('graph'));
$('fit').addEventListener('click',fitGraph);
$('focus').addEventListener('click',()=>{const node=positionedNodes.get(selected);if(graph&&node){graph.centerAt(node.x,node.y,reducedMotion.matches?0:350);graph.zoom(Math.max(graph.zoom(),1.8),reducedMotion.matches?0:350);}});
$('zoom-in').addEventListener('click',()=>{if(graph)graph.zoom(graph.zoom()*1.4,0);});
$('zoom-out').addEventListener('click',()=>{if(graph)graph.zoom(graph.zoom()/1.4,0);});
$('reset-layout').addEventListener('click',()=>{for(const node of positionedNodes.values()){delete node.fx;delete node.fy;}graphSignature='';render();});
document.addEventListener('click',event=>{const jump=event.target.closest('[data-jump]');if(jump)select(jump.dataset.jump);});
$('theme').addEventListener('click',()=>{const isDark=document.documentElement.dataset.theme==='luxury';document.documentElement.dataset.theme=isDark?'light':'luxury';$('theme').textContent=isDark?'Switch to dark':'Switch to light';updateGraphTheme();});
$('stats').innerHTML=[[String(DATA.nodes.length),'Graph entries'],[String(DATA.counts.technique??0),'Techniques'],[`${DATA.claims.positive} + ${DATA.claims.exclusions}`,'Stand-in / exclusion claims'],[`${DATA.unverified} / ${DATA.counts.ingredient??0}`,'Unverified safety records']].map(([number,label])=>`<div class="card card-border bg-base-200 p-4"><p class="text-2xl font-semibold">${number}</p><p class="text-sm soft mt-1">${label}</p></div>`).join('');
$('checkout').textContent=`Working files${DATA.metadata.branch?' on '+DATA.metadata.branch:''}. Source links point to the checked-out commit${DATA.metadata.commit?' '+DATA.metadata.commit.slice(0,7):''}.`;
filterPicks();render();
