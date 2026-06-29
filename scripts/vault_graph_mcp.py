#!/usr/bin/env python3
"""
Vault Graph MCP Server — Graph traversal for the Obsidian knowledge vault.

Provides agents with graph query tools:
  vault_graph_query     — Find notes by tag, group, or content
  vault_graph_path      — Find shortest path between two notes
  vault_graph_related   — Find notes related to a given note (1-2 hops)
  vault_graph_cluster   — Show all notes in the same cluster as a given note
  vault_graph_god_notes — Return top-N most connected notes
  vault_graph_orphans   — Find notes with no inbound links
  vault_graph_stats     — Overall vault health metrics

Run as MCP stdio server:
    python3 vault_graph_mcp.py --vault /root/projects/obsidian-vault
"""

import os
import sys
import json
import re
import argparse
from collections import defaultdict

# ── Configuration ────────────────────────────────────────────────────────────

VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH", "/root/projects/obsidian-vault")
WIKILINK_RE = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

# ── Data Model ──────────────────────────────────────────────────────────────

class Note:
    def __init__(self, path, relpath, title, tags, status, group):
        self.path = path
        self.relpath = relpath
        self.title = title
        self.tags = tags
        self.status = status
        self.group = group
        self.id = relpath.replace('.md', '')
        self.outbound: list[str] = []
        self.inbound: list[str] = []
        self.word_count = 0

    @property
    def degree(self):
        return len(self.outbound) + len(self.inbound)


def parse_frontmatter(content: str) -> dict:
    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split('\n'):
        if ':' in line and not line.strip().startswith('-'):
            key, _, val = line.partition(':')
            fm[key.strip()] = val.strip()
    return fm


def parse_tags(fm: dict) -> list[str]:
    raw = fm.get('tags', '')
    if raw.startswith('['):
        return [t.strip().strip('"').strip("'") for t in raw.strip('[]').split(',') if t.strip()]
    elif raw:
        return [t.strip().strip('"').strip("'") for t in raw.split(',') if t.strip()]
    return []


def get_group(relpath: str) -> str:
    parts = relpath.split(os.sep)
    if len(parts) <= 1:
        return 'root'
    top = parts[0]
    if top == '00-META': return 'meta'
    elif top == '10-PROPERTIES': return parts[1] if len(parts) > 2 else 'properties'
    elif top == '20-AGENTS': return 'agents'
    elif top == '30-PATTERNS': return 'patterns'
    elif top == '40-LOGS': return 'logs'
    elif top == '50-ARCHIVE': return 'archive'
    return 'other'


# ── Graph Builder ────────────────────────────────────────────────────────────

def build_graph(vault_path: str):
    """Build the full vault graph. Returns (notes_dict, unique_notes_dict)."""
    notes: dict[str, Note] = {}

    for root, dirs, files in os.walk(vault_path):
        dirs[:] = [d for d in dirs if d not in ('.git', '.obsidian', '.trash')]
        for fname in files:
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(root, fname)
            relpath = os.path.relpath(fpath, vault_path)
            group = get_group(relpath)

            try:
                content = open(fpath, 'r', encoding='utf-8', errors='replace').read()
            except Exception:
                continue

            fm = parse_frontmatter(content)
            title = fm.get('title', fname.replace('.md', ''))
            tags = parse_tags(fm)
            status = fm.get('status', 'unknown')

            note = Note(fpath, relpath, title, tags, status, group)
            note.word_count = len(content.split())

            notes[note.id] = note
            if title != note.id:
                notes[title] = note

    # Build links
    unique_notes = {n.id: n for n in notes.values()}
    for note in unique_notes.values():
        try:
            content = open(note.path, 'r', encoding='utf-8', errors='replace').read()
        except Exception:
            continue
        fm_match = FRONTMATTER_RE.match(content)
        if fm_match:
            content = content[fm_match.end():]
        for match in WIKILINK_RE.finditer(content):
            target_raw = match.group(1).strip()
            target_clean = target_raw.split('#')[0].strip()
            if target_clean:
                note.outbound.append(target_clean)

    # Resolve inbound links
    for note in unique_notes.values():
        for target in note.outbound:
            if target in notes:
                target_note = notes[target]
                if target_note.id != note.id:
                    target_note.inbound.append(note.id)

    return notes, unique_notes


# ── Query Functions ──────────────────────────────────────────────────────────

def query_notes(notes, unique_notes, tag=None, group=None, search=None, status=None, limit=10):
    """Filter notes by tag, group, content search, or status."""
    results = []
    for note in unique_notes.values():
        if tag and tag not in note.tags:
            continue
        if group and note.group != group:
            continue
        if status and note.status != status:
            continue
        if search:
            try:
                content = open(note.path, 'r', encoding='utf-8', errors='replace').read()
                if search.lower() not in content.lower() and search.lower() not in note.title.lower():
                    continue
            except Exception:
                continue
        results.append({
            "title": note.title,
            "id": note.id,
            "group": note.group,
            "tags": note.tags,
            "status": note.status,
            "inbound": len(note.inbound),
            "outbound": len(note.outbound),
        })
    return results[:limit]


def find_path(notes, unique_notes, source_title, target_title):
    """BFS shortest path between two notes."""
    # Resolve source and target
    source = None
    target = None
    for note in unique_notes.values():
        if note.title == source_title or note.id == source_title:
            source = note
        if note.title == target_title or note.id == target_title:
            target = note

    if not source or not target:
        return {"error": f"Note not found: {'source' if not source else 'target'}", "path": []}

    if source.id == target.id:
        return {"path": [source.title], "hops": 0}

    # BFS
    from collections import deque
    queue = deque([(source.id, [source.id])])
    visited = {source.id}

    while queue:
        current_id, path = queue.popleft()
        current_note = unique_notes.get(current_id)
        if not current_note:
            continue

        # Check outbound links
        for target_link in current_note.outbound:
            resolved = notes.get(target_link)
            if resolved:
                next_id = resolved.id
                if next_id not in visited:
                    if next_id == target.id:
                        full_path = path + [next_id]
                        return {
                            "path": [unique_notes[nid].title for nid in full_path],
                            "hops": len(full_path) - 1,
                        }
                    visited.add(next_id)
                    queue.append((next_id, path + [next_id]))

        # Check inbound links (undirected traversal)
        for other_id, other_note in unique_notes.items():
            if current_id in other_note.outbound and other_id not in visited:
                if other_id == target.id:
                    full_path = path + [other_id]
                    return {
                        "path": [unique_notes[nid].title for nid in full_path],
                        "hops": len(full_path) - 1,
                    }
                visited.add(other_id)
                queue.append((other_id, path + [other_id]))

    return {"path": [], "hops": -1, "message": "No path found — notes are in different clusters"}


def find_related(notes, unique_notes, title, hops=2, limit=10):
    """Find notes related to a given note within N hops."""
    target = None
    for note in unique_notes.values():
        if note.title == title or note.id == title:
            target = note
            break

    if not target:
        return {"error": f"Note not found: {title}"}

    from collections import deque
    queue = deque([(target.id, 0)])
    visited = {target.id: 0}
    related = []

    while queue:
        current_id, depth = queue.popleft()
        if depth >= hops:
            continue

        current_note = unique_notes.get(current_id)
        if not current_note:
            continue

        # Outbound
        for target_link in current_note.outbound:
            resolved = notes.get(target_link)
            if resolved and resolved.id not in visited:
                visited[resolved.id] = depth + 1
                queue.append((resolved.id, depth + 1))
                if resolved.id != target.id:
                    related.append({
                        "title": resolved.title,
                        "id": resolved.id,
                        "group": resolved.group,
                        "hops": depth + 1,
                        "direction": "outbound",
                    })

        # Inbound
        for other_id, other_note in unique_notes.items():
            if current_id in other_note.outbound and other_id not in visited:
                visited[other_id] = depth + 1
                queue.append((other_id, depth + 1))
                if other_id != target.id:
                    related.append({
                        "title": other_note.title,
                        "id": other_id,
                        "group": other_note.group,
                        "hops": depth + 1,
                        "direction": "inbound",
                    })

    related.sort(key=lambda x: x["hops"])
    return {"source": target.title, "related": related[:limit]}


def get_cluster(notes, unique_notes, title):
    """Get all notes in the same connected component as the given note."""
    target = None
    for note in unique_notes.values():
        if note.title == title or note.id == title:
            target = note
            break

    if not target:
        return {"error": f"Note not found: {title}"}

    # BFS to find all connected notes
    from collections import deque
    queue = deque([target.id])
    visited = {target.id}

    while queue:
        current_id = queue.popleft()
        current_note = unique_notes.get(current_id)
        if not current_note:
            continue

        for target_link in current_note.outbound:
            resolved = notes.get(target_link)
            if resolved and resolved.id not in visited:
                visited.add(resolved.id)
                queue.append(resolved.id)

        for other_id, other_note in unique_notes.items():
            if current_id in other_note.outbound and other_id not in visited:
                visited.add(other_id)
                queue.append(other_id)

    cluster_notes = [unique_notes[nid] for nid in visited if nid in unique_notes]
    return {
        "source": target.title,
        "cluster_size": len(cluster_notes),
        "notes": [{"title": n.title, "id": n.id, "group": n.group} for n in cluster_notes],
    }


def get_god_notes(unique_notes, top_n=5):
    """Return top-N most connected notes."""
    scored = sorted(unique_notes.values(), key=lambda n: n.degree, reverse=True)
    return [
        {
            "title": n.title,
            "id": n.id,
            "inbound": len(n.inbound),
            "outbound": len(n.outbound),
            "degree": n.degree,
            "group": n.group,
        }
        for n in scored[:top_n]
    ]


def get_orphans(unique_notes):
    """Find notes with no inbound links."""
    orphans = [n for n in unique_notes.values() if not n.inbound and n.group != 'logs']
    return [
        {"title": n.title, "id": n.id, "group": n.group, "word_count": n.word_count}
        for n in sorted(orphans, key=lambda x: x.group)
    ]


def get_stats(unique_notes):
    """Overall vault health metrics."""
    total = len(unique_notes)
    if total == 0:
        return {"total_notes": 0}

    link_count = sum(len(n.outbound) for n in unique_notes.values())
    orphans = len([n for n in unique_notes.values() if not n.inbound and n.group != 'logs'])
    dead_ends = len([n for n in unique_notes.values() if not n.outbound and n.group != 'logs'])
    untagged = len([n for n in unique_notes.values() if not n.tags and n.group != 'logs'])

    return {
        "total_notes": total,
        "total_links": link_count,
        "orphan_count": orphans,
        "dead_end_count": dead_ends,
        "untagged_count": untagged,
        "avg_links_per_note": round(link_count / total, 1),
        "groups": list(set(n.group for n in unique_notes.values())),
    }


# ── MCP Server ──────────────────────────────────────────────────────────────

def mcp_server(vault_path: str):
    """Run as MCP stdio server."""
    notes, unique_notes = build_graph(vault_path)

    # Define tools
    tools = [
        {
            "name": "vault_graph_query",
            "description": "Search vault notes by tag, group, content keyword, or status. Returns matching notes with metadata.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "tag": {"type": "string", "description": "Filter by tag (e.g. 'pattern', 'lesson')"},
                    "group": {"type": "string", "description": "Filter by group (e.g. 'patterns', 'agents', 'meta')"},
                    "search": {"type": "string", "description": "Search in note content and title"},
                    "status": {"type": "string", "description": "Filter by status (e.g. 'active', 'draft')"},
                    "limit": {"type": "integer", "description": "Max results (default 10)"},
                },
            },
        },
        {
            "name": "vault_graph_path",
            "description": "Find the shortest path between two notes through wikilinks. Returns the chain of notes connecting them.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "source": {"type": "string", "description": "Source note title or ID"},
                    "target": {"type": "string", "description": "Target note title or ID"},
                },
                "required": ["source", "target"],
            },
        },
        {
            "name": "vault_graph_related",
            "description": "Find notes related to a given note within N hops of wikilinks.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title or ID to find relations for"},
                    "hops": {"type": "integer", "description": "Max hops (default 2)"},
                    "limit": {"type": "integer", "description": "Max results (default 10)"},
                },
                "required": ["title"],
            },
        },
        {
            "name": "vault_graph_cluster",
            "description": "Show all notes in the same connected component as a given note.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Note title or ID"},
                },
                "required": ["title"],
            },
        },
        {
            "name": "vault_graph_god_notes",
            "description": "Return the top-N most connected notes (highest degree centrality).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "top_n": {"type": "integer", "description": "Number of top notes (default 5)"},
                },
            },
        },
        {
            "name": "vault_graph_orphans",
            "description": "Find notes with no inbound links (orphans).",
            "inputSchema": {"type": "object", "properties": {}},
        },
        {
            "name": "vault_graph_stats",
            "description": "Return overall vault health metrics and statistics.",
            "inputSchema": {"type": "object", "properties": {}},
        },
    ]

    # MCP protocol loop
    import sys

    def send(obj):
        sys.stdout.write(json.dumps(obj) + "\n")
        sys.stdout.flush()

    # Send initialization
    send({
        "jsonrpc": "2.0",
        "id": 0,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "vault-graph", "version": "1.0.0"},
        },
    })

    # Send tools list
    send({
        "jsonrpc": "2.0",
        "id": 1,
        "result": {"tools": tools},
    })

    # Rebuild graph periodically (every 60 seconds)
    last_rebuild = os.time() if hasattr(os, 'time') else 0

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue

        if msg.get("method") == "tools/call":
            tool_name = msg.get("params", {}).get("name", "")
            args = msg.get("params", {}).get("arguments", {})

            # Rebuild graph if stale (simple check: always rebuild for now)
            notes, unique_notes = build_graph(vault_path)

            result = {"error": f"Unknown tool: {tool_name}"}

            if tool_name == "vault_graph_query":
                result = query_notes(
                    notes, unique_notes,
                    tag=args.get("tag"),
                    group=args.get("group"),
                    search=args.get("search"),
                    status=args.get("status"),
                    limit=args.get("limit", 10),
                )
            elif tool_name == "vault_graph_path":
                result = find_path(
                    notes, unique_notes,
                    args.get("source", ""),
                    args.get("target", ""),
                )
            elif tool_name == "vault_graph_related":
                result = find_related(
                    notes, unique_notes,
                    args.get("title", ""),
                    hops=args.get("hops", 2),
                    limit=args.get("limit", 10),
                )
            elif tool_name == "vault_graph_cluster":
                result = get_cluster(
                    notes, unique_notes,
                    args.get("title", ""),
                )
            elif tool_name == "vault_graph_god_notes":
                result = get_god_notes(unique_notes, top_n=args.get("top_n", 5))
            elif tool_name == "vault_graph_orphans":
                result = get_orphans(unique_notes)
            elif tool_name == "vault_graph_stats":
                result = get_stats(unique_notes)

            send({
                "jsonrpc": "2.0",
                "id": msg.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(result, indent=2, default=str),
                        }
                    ],
                },
            })


# ── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Vault Graph MCP Server")
    parser.add_argument("--vault", default=VAULT_PATH, help="Path to vault")
    parser.add_argument("--test", action="store_true", help="Run a quick test query")
    args = parser.parse_args()

    if args.test:
        notes, unique_notes = build_graph(args.vault)
        print("=== STATS ===")
        print(json.dumps(get_stats(unique_notes), indent=2))
        print("\n=== GOD NOTES ===")
        print(json.dumps(get_god_notes(unique_notes), indent=2))
        print("\n=== ORPHANS ===")
        print(json.dumps(get_orphans(unique_notes), indent=2))
        print("\n=== PATH: Home → Coherence Scoring ===")
        print(json.dumps(find_path(notes, unique_notes, "Home", "Coherence Scoring"), indent=2))
        print("\n=== RELATED TO: Home ===")
        print(json.dumps(find_related(notes, unique_notes, "Home", hops=2, limit=5), indent=2))
    else:
        mcp_server(args.vault)
