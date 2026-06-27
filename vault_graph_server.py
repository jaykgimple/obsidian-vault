#!/usr/bin/env python3
"""
Obsidian Vault Graph Server — Live dynamic graph visualization.
Watches vault filesystem, regenerates graph JSON on any change.
Serves interactive D3.js force-directed graph at http://localhost:8420.

Usage:
    python3 vault_graph_server.py [--vault PATH] [--port PORT]
"""

import os, sys, json, re, time, argparse, threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH", "/root/projects/obsidian-vault")
WIKILINK_RE = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
TAG_RE = re.compile(r'tags:\s*\[(.*?)\]', re.DOTALL)

graph_data = {"nodes": [], "links": [], "meta": {}}
graph_lock = threading.Lock()

def parse_frontmatter(content):
    """Extract YAML frontmatter from markdown content."""
    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip()
    return fm

def build_graph(vault_path):
    """Walk vault, parse all .md files, build nodes + links."""
    nodes = []
    links = []
    node_map = {}  # relative path -> node id
    link_set = set()

    for root, dirs, files in os.walk(vault_path):
        # Skip .git and .obsidian
        dirs[:] = [d for d in dirs if d not in ('.git', '.obsidian')]
        for fname in files:
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            relpath = os.path.relpath(fpath, vault_path)
            try:
                content = open(fpath, 'r').read()
            except:
                continue

            fm = parse_frontmatter(content)
            title = fm.get('title', fname.replace('.md', ''))
            tags_str = fm.get('tags', '')
            tags = [t.strip().strip('"').strip("'") for t in tags_str.strip('[]').split(',') if t.strip()]
            status = fm.get('status', 'unknown')

            # Determine group from path
            parts = relpath.split(os.sep)
            group = parts[0] if len(parts) > 1 else 'root'
            if group == '00-META':
                group = 'meta'
            elif group == '10-PROPERTIES':
                group = parts[1] if len(parts) > 2 else 'properties'
            elif group == '20-AGENTS':
                group = 'agents'
            elif group == '30-PATTERNS':
                group = 'patterns'
            elif group == '40-LOGS':
                group = 'logs'
            elif group == '50-ARCHIVE':
                group = 'archive'

            node_id = relpath.replace('.md', '')
            node_map[node_id] = len(nodes)
            node_map[title] = len(nodes)  # also map by title for wikilink resolution

            nodes.append({
                "id": node_id,
                "title": title,
                "group": group,
                "tags": tags,
                "status": status,
                "path": relpath,
                "links_count": 0
            })

            # Find wikilinks in content
            for match in WIKILINK_RE.finditer(content):
                target = match.group(1).strip()
                link_key = (node_id, target)
                if link_key not in link_set:
                    link_set.add(link_key)
                    links.append({"source": node_id, "target": target})

    # Resolve link targets and count
    resolved_links = []
    for link in links:
        src = link["source"]
        tgt = link["target"]
        # Try exact match, then title match
        if tgt in node_map or any(n["id"] == tgt or n["title"] == tgt for n in nodes):
            resolved_links.append(link)
            # Increment link count on source
            for n in nodes:
                if n["id"] == src:
                    n["links_count"] += 1
                    break

    # Count inbound links
    inbound = {}
    for link in resolved_links:
        t = link["target"]
        inbound[t] = inbound.get(t, 0) + 1
    for n in nodes:
        n["inbound_count"] = inbound.get(n["id"], 0) + inbound.get(n["title"], 0)

    meta = {
        "total_nodes": len(nodes),
        "total_links": len(resolved_links),
        "groups": list(set(n["group"] for n in nodes)),
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "vault_path": vault_path
    }

    return {"nodes": nodes, "links": resolved_links, "meta": meta}

def regenerate_graph():
    global graph_data
    with graph_lock:
        graph_data = build_graph(VAULT_PATH)
    print(f"[graph] Regenerated: {graph_data['meta']['total_nodes']} nodes, {graph_data['meta']['total_links']} links")

class VaultEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.src_path.endswith('.md'):
            regenerate_graph()

class GraphHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        elif self.path == '/graph.json':
            with graph_lock:
                data = json.dumps(graph_data)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(data.encode())
        elif self.path == '/note':
            # Return note content by path param
            import urllib.parse
            params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            # Actually the path is /note?path=...
            # Fix: parse from self.path
            q = self.path.split('?', 1)
            params = urllib.parse.parse_qs(q[1]) if len(q) > 1 else {}
            note_path = params.get('path', [''])[0]
            full_path = os.path.join(VAULT_PATH, note_path)
            if os.path.exists(full_path) and full_path.startswith(VAULT_PATH):
                content = open(full_path).read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(content.encode())
            else:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress request logging

HTML_PAGE = """<!DOCTYPE html>
<html>
<head>
<title>Obsidian Vault — Knowledge Graph</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { background: #1a1b2e; color: #e0e0e0; font-family: 'Inter', system-ui, sans-serif; overflow: hidden; }
#sidebar { position: fixed; right: 0; top: 0; width: 380px; height: 100vh; background: #22233a; border-left: 1px solid #333; overflow-y: auto; padding: 20px; z-index: 10; }
#sidebar h2 { color: #8be9fd; font-size: 16px; margin-bottom: 8px; }
#sidebar .meta { font-size: 12px; color: #888; margin-bottom: 16px; }
#sidebar .stat { display: inline-block; background: #2a2b3d; padding: 4px 10px; border-radius: 4px; margin: 2px; font-size: 11px; }
#sidebar .note-info { background: #2a2b3d; border-radius: 8px; padding: 12px; margin-top: 12px; }
#sidebar .note-info h3 { color: #bd93f9; font-size: 14px; }
#sidebar .note-info .tag { display: inline-block; background: #44475a; color: #8be9fd; padding: 2px 8px; border-radius: 3px; margin: 2px; font-size: 10px; }
#sidebar .note-info pre { background: #1a1b2e; padding: 8px; border-radius: 4px; font-size: 11px; max-height: 400px; overflow-y: auto; margin-top: 8px; white-space: pre-wrap; }
#graph-container { width: calc(100vw - 380px); height: 100vh; }
#controls { position: fixed; left: 16px; top: 16px; z-index: 10; background: #22233a; border-radius: 8px; padding: 12px; }
#controls h1 { font-size: 18px; color: #f1fa8c; margin-bottom: 4px; }
#controls .sub { font-size: 11px; color: #888; }
#controls select, #controls input { background: #2a2b3d; color: #e0e0e0; border: 1px solid #444; padding: 4px 8px; border-radius: 4px; margin-top: 6px; font-size: 12px; }
#controls .legend { margin-top: 12px; }
#controls .legend-item { display: flex; align-items: center; gap: 6px; font-size: 11px; margin-top: 3px; }
#controls .legend-dot { width: 10px; height: 10px; border-radius: 50%; }
svg { width: 100%; height: 100%; }
.node { cursor: pointer; }
.node circle { stroke: #444; stroke-width: 1.5; }
.node text { fill: #ccc; font-size: 10px; pointer-events: none; }
.link { stroke: #44475a; stroke-opacity: 0.4; }
.node:hover circle { stroke: #f1fa8c; stroke-width: 2; }
.node.selected circle { stroke: #ff79c6; stroke-width: 3; }
#refresh-indicator { position: fixed; left: 16px; bottom: 16px; background: #22233a; border-radius: 4px; padding: 4px 10px; font-size: 10px; color: #6272a4; z-index: 10; }
</style>
</head>
<body>
<div id="controls">
  <h1>🕸️ Knowledge Graph</h1>
  <div class="sub">Obsidian Vault — Live</div>
  <select id="groupFilter" onchange="filterGraph()"><option value="all">All Groups</option></select>
  <input id="searchBox" placeholder="Search notes..." oninput="filterGraph()" style="width:140px;margin-left:6px"/>
  <div class="legend" id="legend"></div>
</div>
<div id="graph-container"><svg id="graph"></svg></div>
<div id="sidebar">
  <h2>📊 Vault Stats</h2>
  <div class="meta" id="metaInfo">Loading...</div>
  <h2>📝 Note Detail</h2>
  <div class="note-info" id="noteInfo"><p style="color:#6272a4">Click a node to view</p></div>
</div>
<div id="refresh-indicator">Live — auto-refreshes on vault changes</div>
<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
const GROUP_COLORS = {
  meta: '#8be9fd', story engine: '#ff79c6', octogentic: '#f1fa8c',
  bookbrary: '#50fa7b', rolefresh: '#bd93f9', agents: '#ffb86c',
  patterns: '#ff5555', logs: '#6272a4', archive: '#44475a',
  'Story-Engine': '#ff79c6', 'OctoGentic': '#f1fa8c', properties: '#50fa7b'
};
function getColor(g) { return GROUP_COLORS[g] || GROUP_COLORS[g.toLowerCase()] || '#8be9fd'; }

let simulation, allNodes, allLinks, selectedNode = null;
const svg = d3.select('#graph');
const container = document.getElementById('graph-container');

function init(data) {
  allNodes = data.nodes;
  allLinks = data.links;

  // Meta
  document.getElementById('metaInfo').innerHTML =
    `<span class="stat">📝 ${data.meta.total_nodes} nodes</span>` +
    `<span class="stat">🔗 ${data.meta.total_links} links</span>` +
    `<span class="stat">⏰ ${data.meta.last_updated}</span>`;

  // Group filter
  const sel = document.getElementById('groupFilter');
  const current = sel.value;
  sel.innerHTML = '<option value="all">All Groups</option>';
  data.meta.groups.forEach(g => {
    sel.innerHTML += `<option value="${g}">${g}</option>`;
  });
  sel.value = current;

  // Legend
  const leg = document.getElementById('legend');
  leg.innerHTML = '';
  data.meta.groups.forEach(g => {
    leg.innerHTML += `<div class="legend-item"><div class="legend-dot" style="background:${getColor(g)}"></div>${g}</div>`;
  });

  filterGraph();
}

function filterGraph() {
  const group = document.getElementById('groupFilter').value;
  const search = document.getElementById('searchBox').value.toLowerCase();

  let filteredNodes = allNodes;
  let filteredLinks = allLinks;

  if (group !== 'all') {
    filteredNodes = filteredNodes.filter(n => n.group === group);
    const nodeIds = new Set(filteredNodes.map(n => n.id));
    filteredLinks = filteredLinks.filter(l => nodeIds.has(l.source) || nodeIds.has(l.target));
  }
  if (search) {
    filteredNodes = filteredNodes.filter(n =>
      n.title.toLowerCase().includes(search) ||
      n.tags.some(t => t.toLowerCase().includes(search))
    );
    const nodeIds = new Set(filteredNodes.map(n => n.id));
    filteredLinks = filteredLinks.filter(l => nodeIds.has(l.source) || nodeIds.has(l.target));
  }

  renderGraph(filteredNodes, filteredLinks);
}

function renderGraph(nodes, links) {
  svg.selectAll('*').remove();
  const width = container.clientWidth;
  const height = container.clientHeight;

  if (simulation) simulation.stop();

  // Resolve links to node objects
  const nodeMap = {};
  nodes.forEach(n => { nodeMap[n.id] = n; nodeMap[n.title] = n; });
  const resolvedLinks = links
    .map(l => {
      const s = typeof l.source === 'object' ? l.source : (nodeMap[l.source] || null);
      const t = typeof l.target === 'object' ? l.target : (nodeMap[l.target] || null);
      return (s && t) ? {source: s, target: t} : null;
    })
    .filter(Boolean);

  // Deduplicate nodes
  const uniqueNodes = [...new Map(nodes.map(n => [n.id, n])).values()];

  simulation = d3.forceSimulation(uniqueNodes)
    .force('link', d3.forceLink(resolvedLinks).id(d => d.id).distance(80))
    .force('charge', d3.forceManyBody().strength(-200))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(d => Math.sqrt((d.inbound_count || 0) + 1) * 6 + 4));

  const linkEls = svg.append('g').selectAll('line')
    .data(resolvedLinks).join('line').attr('class', 'link');

  const nodeEls = svg.append('g').selectAll('g')
    .data(uniqueNodes).join('g').attr('class', 'node')
    .call(d3.drag()
      .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
      .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
      .on('end', (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }))
    .on('click', (e, d) => selectNode(d));

  nodeEls.append('circle')
    .attr('r', d => Math.sqrt((d.inbound_count || 0) + 1) * 4 + 3)
    .attr('fill', d => getColor(d.group))
    .attr('fill-opacity', 0.8);

  nodeEls.append('text')
    .text(d => d.title.length > 25 ? d.title.slice(0, 22) + '...' : d.title)
    .attr('dx', d => Math.sqrt((d.inbound_count || 0) + 1) * 4 + 8)
    .attr('dy', 4);

  simulation.on('tick', () => {
    linkEls.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
           .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
    nodeEls.attr('transform', d => `translate(${d.x},${d.y})`);
  });
}

function selectNode(d) {
  selectedNode = d;
  d3.selectAll('.node').classed('selected', false);
  d3.select(this.parentNode).classed('selected', true);  // approx

  const info = document.getElementById('noteInfo');
  info.innerHTML = `<h3>${d.title}</h3>` +
    `<div style="margin:4px 0;font-size:11px;color:#6272a4">${d.path}</div>` +
    `<div style="margin:4px 0"><span class="stat">${d.group}</span> <span class="stat">${d.status}</span></div>` +
    `<div style="margin:4px 0">${d.tags.map(t => `<span class="tag">#${t}</span>`).join('')}</div>` +
    `<div style="margin:4px 0;font-size:11px">↗ Outbound: ${d.links_count} | ↙ Inbound: ${d.inbound_count}</div>` +
    `<pre id="noteContent">Loading...</pre>`;

  fetch('/note?path=' + encodeURIComponent(d.path))
    .then(r => r.text()).then(t => {
      document.getElementById('noteContent').textContent = t;
    });
}

// Auto-refresh every 5s
function refresh() {
  fetch('/graph.json').then(r => r.json()).then(data => init(data)).catch(() => {});
}
refresh();
setInterval(refresh, 5000);
</script>
</body>
</html>
"""

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Obsidian Vault Graph Server')
    parser.add_argument('--vault', default=VAULT_PATH, help='Vault path')
    parser.add_argument('--port', type=int, default=8420, help='Port')
    args = parser.parse_args()

    VAULT_PATH = args.vault
    print(f"[vault] Watching: {VAULT_PATH}")
    regenerate_graph()

    # File watcher
    observer = Observer()
    observer.schedule(VaultEventHandler(), VAULT_PATH, recursive=True)
    observer.start()
    print(f"[watch] File watcher started")

    # HTTP server
    server = HTTPServer(('0.0.0.0', args.port), GraphHandler)
    print(f"[server] Live graph at http://0.0.0.0:{args.port}")
    print(f"[server] Auto-refreshes on vault changes")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        observer.stop()
        server.server_close()
    observer.join()
