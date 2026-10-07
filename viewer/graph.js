let graph = null;
let graphSignature = '';
let hoverNode = null;
let neighbours = new Set();
let visibleAdjacency = new Map();
let graphTheme = {};
const positionedNodes = new Map();
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');

function endpointId(endpoint) { return typeof endpoint === 'string' ? endpoint : endpoint.id; }
function themeValue(name, fallback) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
}
function updateGraphTheme() {
  graphTheme = {
    text: getComputedStyle(document.body).color,
    background: themeValue('--color-base-200', '#242424'),
    technique: themeValue('--color-info', '#58a6ff'),
    ingredient: themeValue('--color-success', '#5cbe95'),
    dish: themeValue('--color-warning', '#e9b44c'),
    recipe: themeValue('--graph-recipe', themeValue('--color-secondary', '#bf8be6')),
    preparation: themeValue('--graph-preparation', themeValue('--color-accent', '#e886a8')),
    group: themeValue('--graph-group', themeValue('--color-primary', '#b0a090')),
    blocked: themeValue('--color-error', '#e77777')
  };
  $('legend').innerHTML = ['technique', 'ingredient', 'dish', 'recipe', 'preparation', 'group'].map(type =>
    `<span class="inline-flex items-center gap-2"><span class="legend-dot" style="background:${esc(graphTheme[type])}"></span>${esc(kindLabel[type])}</span>`
  ).join('') + '<span class="soft">Dashed red: explicit exclusion in a stated context</span>';
  if (graph) graph.backgroundColor(graphTheme.background);
  repaintGraph();
}
function connectionState(edge) {
  if (edge.state || edge.relation !== 'stands_in_for') return {...edge};
  const claims = nodes.get(edge.source)?.raw.stands_in_for?.filter(row => row.thing === edge.target) || [];
  const blocked = claims.length && claims.every(row => !row.allows);
  return {...edge, state: blocked ? 'blocked' : 'conditional', label: blocked ? 'exclusion (context)' : 'stand-in (context)'};
}
function filteredGraphEdges() {
  const unique = new Map();
  for (const edge of DATA.edges.filter(allowedEdge)) {
    const key = `${edge.source}|${edge.target}|${edge.relation}`;
    unique.set(key, connectionState(edge));
  }
  if ($('scope').value === 'local' && $('mode').value === 'substitutions') {
    for (const edge of neighborhood()) {
      if (edge.source === selected) unique.set(`${edge.source}|${edge.target}|${edge.label}`, {...edge});
    }
  }
  return [...unique.values()];
}
function adjacencyFor(edges) {
  const adjacency = new Map();
  for (const edge of edges) {
    for (const [source, target] of [[edge.source, edge.target], [edge.target, edge.source]]) {
      if (!adjacency.has(source)) adjacency.set(source, new Set());
      adjacency.get(source).add(target);
    }
  }
  return adjacency;
}
function visibleNodeIds(edges) {
  if ($('scope').value === 'global') {
    if ($('mode').value !== 'cooking' && $('mode').value !== 'all') {
      return new Set(edges.flatMap(edge => [edge.source, edge.target]));
    }
    return new Set(DATA.nodes.filter(node => $('mode').value === 'all' || !['fact', 'source'].includes(kind(node.id))).map(node => node.id));
  }
  const adjacency = adjacencyFor(edges), visible = new Set([selected]);
  let frontier = [selected];
  for (let step = 0; step < Number($('depth').value); step++) {
    const next = [];
    for (const id of frontier) {
      for (const neighbour of adjacency.get(id) || []) {
        if (!visible.has(neighbour)) { visible.add(neighbour); next.push(neighbour); }
      }
    }
    frontier = next;
  }
  return visible;
}
function nodeRadius(node) { return node.id === selected ? 8 : 3.5 + Math.min(3, Math.log1p(node.degree)); }
function paintRadius(node, scale) { return Math.max((node.id === selected ? 5 : 2.3) / scale, nodeRadius(node)); }
function isHighlighted(node) { return !hoverNode || node.id === hoverNode.id || neighbours.has(node.id); }
function paintNode(node, context, scale) {
  const focus = node.id === selected, hover = node.id === hoverNode?.id;
  const radius = paintRadius(node, scale), colour = graphTheme[kind(node.id)] || graphTheme.text;
  context.globalAlpha = isHighlighted(node) ? 1 : .18;
  context.beginPath(); context.arc(node.x, node.y, radius, 0, 2 * Math.PI);
  context.fillStyle = colour; context.fill();
  if (focus || hover) { context.strokeStyle = graphTheme.text; context.lineWidth = 2 / scale; context.stroke(); }
  const local = $('scope').value === 'local';
  const showLabel = focus || hover || (local && scale > .7) || (hoverNode && neighbours.has(node.id)) || scale > 2;
  if (showLabel) {
    const size = 12 / scale, label = node.name.length > 30 ? node.name.slice(0, 28) + '…' : node.name;
    context.font = `${size}px system-ui`; context.textBaseline = 'middle';
    const width = context.measureText(label).width;
    const screen = graph.graph2ScreenCoords(node.x, node.y);
    const left = screen.x + (radius + width) * scale + 3 > graph.width();
    const x = node.x + (left ? -1 : 1) * (radius + 3 / scale);
    context.textAlign = left ? 'right' : 'left';
    context.fillStyle = graphTheme.background; context.fillRect(x - (left ? width : 0) - 2 / scale, node.y - size * .7, width + 4 / scale, size * 1.4);
    context.fillStyle = graphTheme.text; context.fillText(label, x, node.y);
  }
  context.globalAlpha = 1;
}
function edgeHighlighted(edge) { return !hoverNode || endpointId(edge.source) === hoverNode.id || endpointId(edge.target) === hoverNode.id; }
function edgeColour(edge) {
  if (!edgeHighlighted(edge)) return 'rgba(130,140,150,.06)';
  if (edge.state === 'blocked') return graphTheme.blocked;
  if (edge.state === 'allowed' || edge.state === 'conditional') return graphTheme.dish;
  return hoverNode ? graphTheme.text : 'rgba(135,145,155,.28)';
}
function repaintGraph() {
  if (!graph) return;
  graph.nodeCanvasObject((...args) => paintNode(...args));
  graph.linkColor(edge => edgeColour(edge));
  graph.linkWidth(edge => hoverNode && edgeHighlighted(edge) ? 1.7 : .7);
}
function inspectGraphLink(edge) {
  const source = endpointId(edge.source), target = endpointId(edge.target);
  $('link-detail').innerHTML = `${jumpButton(source)} <span class="soft">${esc(edge.label)}</span> ${jumpButton(target)}`;
  const claims = nodes.get(source)?.raw.stands_in_for?.filter(row => row.thing === target) || [];
  showInspector();
  if (claims.length) $('inspector').insertAdjacentHTML('afterbegin', `<div class="mb-4"><h4 class="font-semibold">Selected connection</h4>${claims.map(row => claimCard(target, {...row, thing: source}, false)).join('')}</div>`);
}
function ensureGraph() {
  if (graph) return true;
  if (typeof ForceGraph === 'undefined') {
    $('graph').innerHTML = '<p class="p-6">The graph library could not load. You can still search and inspect connections using the list below.</p>';
    return false;
  }
  graph = new ForceGraph($('graph'))
    .nodeId('id').nodeLabel(node => esc(`${node.name} (${kindLabel[kind(node.id)]})`))
    .linkLabel(edge => esc(`${title(endpointId(edge.source))} · ${edge.label} · ${title(endpointId(edge.target))}`))
    .nodeCanvasObject(paintNode).nodeCanvasObjectMode(() => 'replace')
    .nodePointerAreaPaint((node, colour, context, scale) => {
      context.fillStyle = colour; context.beginPath(); context.arc(node.x, node.y, paintRadius(node, scale) + 4 / scale, 0, 2 * Math.PI); context.fill();
    })
    .linkColor(edgeColour).linkLineDash(edge => edge.state === 'blocked' ? [4, 3] : null)
    .linkDirectionalArrowLength(edge => $('scope').value === 'local' || edge.state ? 4 : 0)
    .linkDirectionalArrowRelPos(.75)
    .onNodeHover(node => { hoverNode = node; neighbours = visibleAdjacency.get(node?.id) || new Set(); repaintGraph(); })
    .onNodeClick(node => select(node.id))
    .onNodeDragEnd(node => { node.fx = node.x; node.fy = node.y; })
    .onLinkClick(inspectGraphLink)
    .warmupTicks(100).cooldownTicks(reducedMotion.matches ? 0 : 70);
  graph.d3Force('charge').strength(-110);
  graph.d3Force('link').distance($('scope').value === 'local' ? 95 : 45);
  updateGraphTheme();
  return true;
}
function sizeGraph() {
  if (!graph) return;
  const width = $('graph').clientWidth, height = $('graph').clientHeight;
  if (graph.width() === width && graph.height() === height) return;
  graph.width(width).height(height);
  if (graph.graphData().nodes.length) fitGraph();
}
function fitGraph() { if (graph) graph.zoomToFit(reducedMotion.matches ? 0 : 350, 40); }
function drawGraph(connections) {
  $('connections').innerHTML = connections.map(edge => `<div class="connection py-3"><span class="soft text-sm">${edge.incoming ? 'Linked from' : 'Links to'} · ${esc(edge.label)}</span> ${jumpButton(edge.other)}</div>`).join('') || '<p class="soft">No recorded connections under this filter.</p>';
  $('depth-control').hidden = $('scope').value !== 'local';
  if (!ensureGraph()) return;
  sizeGraph();
  const signature = `${$('scope').value}|${$('mode').value}|${$('depth').value}|${$('scope').value === 'local' ? selected : ''}`;
  if (signature === graphSignature) { repaintGraph(); return; }
  graphSignature = signature;
  const edges = filteredGraphEdges(), ids = visibleNodeIds(edges);
  const visibleEdges = edges.filter(edge => ids.has(edge.source) && ids.has(edge.target));
  visibleAdjacency = adjacencyFor(visibleEdges);
  const graphNodes = [...ids].map((id, index) => {
    if (!positionedNodes.has(id)) {
      const angle = index * 2.399963, radius = 12 * Math.sqrt(index + 1);
      positionedNodes.set(id, {id, name: title(id), x: Math.cos(angle) * radius, y: Math.sin(angle) * radius});
    }
    const node = positionedNodes.get(id); node.degree = visibleAdjacency.get(id)?.size || 0; return node;
  });
  hoverNode = null; neighbours = new Set();
  graph.d3Force('link').distance($('scope').value === 'local' ? 95 : 45);
  graph.onEngineStop(() => { fitGraph(); graph.onEngineStop(() => {}); });
  graph.graphData({nodes: graphNodes, links: visibleEdges.map(edge => ({...edge}))});
  repaintGraph();
  $('graph-count').textContent = `${graphNodes.length} entries · ${visibleEdges.length} connections · ${$('scope').value === 'global' ? 'whole graph under this filter' : 'around ' + title(selected)}`;
}
