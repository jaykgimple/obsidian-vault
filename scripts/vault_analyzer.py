#!/usr/bin/env python3
"""
Obsidian Vault Graph Analyzer — God Nodes, Gaps, Clusters, Broken Links.

Walks the vault, parses wikilinks/frontmatter, computes:
  - God notes (highest connectivity / centrality)
  - Orphan notes (no inbound links — knowledge gaps)
  - Structural gaps (no outbound links — dead ends)
  - Broken links (targets that don't exist as notes)
  - Community clusters (connected components via Union-Find)
  - Hub notes (bridge between clusters)
  - Tag coverage (notes without tags, orphaned tags)
  - Stale notes (not updated in N days)
  - Graph density & health score

Usage:
    python3 vault_analyzer.py [--vault PATH] [--output PATH] [--format text|json|md] [--top N] [--stale-days N]

Outputs to stdout (default: text report). Use --output to write to file.
"""

import os
import sys
import json
import re
import time
import argparse
from collections import defaultdict
from datetime import datetime, timedelta

# ── Configuration ────────────────────────────────────────────────────────────

VAULT_PATH = os.environ.get("OBSIDIAN_VAULT_PATH", "/root/projects/obsidian-vault")
WIKILINK_RE = re.compile(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]')
FRONTMATTER_RE = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)
TAG_INLINE_RE = re.compile(r'#([a-zA-Z][a-zA-Z0-9_-]*)')

# ── Data Structures ─────────────────────────────────────────────────────────

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
        self.last_modified: float = 0

    @property
    def degree(self):
        return len(self.outbound) + len(self.inbound)


# ── Parsing ─────────────────────────────────────────────────────────────────

def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter as simple dict."""
    m = FRONTMATTER_RE.match(content)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).split('\n'):
        if ':' in line and not line.strip().startswith('-'):
            key, _, val = line.partition(':')
            fm[key.strip()] = val.strip()
        elif line.strip().startswith('-'):
            # Array item
            item = line.strip().strip('- ').strip('"').strip("'")
            last_key = list(fm.keys())[-1] if fm else None
            if last_key:
                existing = fm[last_key]
                if existing.startswith('['):
                    existing = existing.strip('[]')
                items = [x.strip().strip('"').strip("'") for x in existing.split(',') if x.strip()]
                items.append(item)
                if len(items) > 1:
                    fm[last_key] = f"[{', '.join(items)}]"
                else:
                    fm[last_key] = items[0] if items else ''
    return fm


def parse_tags(fm: dict) -> list[str]:
    """Extract tags from frontmatter."""
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
    if top == '00-META':
        return 'meta'
    elif top == '10-PROPERTIES':
        return parts[1] if len(parts) > 2 else 'properties'
    elif top == '20-AGENTS':
        return 'agents'
    elif top == '30-PATTERNS':
        return 'patterns'
    elif top == '40-LOGS':
        return 'logs'
    elif top == '50-ARCHIVE':
        return 'archive'
    return 'other'


def build_vault_index(vault_path: str) -> dict[str, Note]:
    """Walk vault and build note index."""
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
                stat = os.stat(fpath)
                content = open(fpath, 'r', encoding='utf-8', errors='replace').read()
            except Exception:
                continue

            fm = parse_frontmatter(content)
            title = fm.get('title', fname.replace('.md', ''))
            tags = parse_tags(fm)
            status = fm.get('status', 'unknown')

            note = Note(fpath, relpath, title, tags, status, group)
            note.word_count = len(content.split())
            note.last_modified = stat.st_mtime

            notes[note.id] = note
            # Also index by title for wikilink resolution
            if title != note.id:
                notes[title] = note

    return notes


# ── Graph Building ──────────────────────────────────────────────────────────

def build_links(notes: dict[str, Note]):
    """Parse all wikilinks and build connections."""
    seen_links = set()

    for key, note in list(notes.items()):
        if key != note.id:
            continue  # skip title-aliased entries

        content = ""
        try:
            content = open(note.path, 'r', encoding='utf-8', errors='replace').read()
        except Exception:
            continue

        # Strip frontmatter for link analysis
        fm_match = FRONTMATTER_RE.match(content)
        if fm_match:
            content = content[fm_match.end():]

        for match in WIKILINK_RE.finditer(content):
            target_raw = match.group(1).strip()
            # Normalize: strip section anchors (e.g. "Note#Section" -> "Note")
            target_clean = target_raw.split('#')[0].strip()
            if not target_clean:
                continue

            link_key = (note.id, target_clean)
            if link_key in seen_links:
                continue
            seen_links.add(link_key)
            note.outbound.append(target_clean)


# ── Analysis ────────────────────────────────────────────────────────────────

def find_god_notes(notes: dict[str, Note], top_n: int = 5) -> list[dict]:
    """Notes with highest degree centrality (inbound + outbound)."""
    unique_notes = {n.id: n for n in notes.values()}
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


def find_orphan_notes(notes: dict[str, Note]) -> list[dict]:
    """Notes with zero inbound links — no other note references them."""
    unique_notes = {n.id: n for n in notes.values()}
    orphans = [n for n in unique_notes.values() if not n.inbound and n.group != 'logs']
    return [
        {"title": n.title, "id": n.id, "group": n.group, "word_count": n.word_count}
        for n in sorted(orphans, key=lambda x: x.group)
    ]


def find_dead_ends(notes: dict[str, Note]) -> list[dict]:
    """Notes with zero outbound links — they don't connect to anything."""
    unique_notes = {n.id: n for n in notes.values()}
    dead = [n for n in unique_notes.values() if not n.outbound and n.group != 'logs']
    return [
        {"title": n.title, "id": n.id, "group": n.group, "word_count": n.word_count}
        for n in sorted(dead, key=lambda x: x.group)
    ]


def find_broken_links(notes: dict[str, Note]) -> list[dict]:
    """Wikilinks that point to non-existent notes (true broken links only)."""
    unique_notes = {n.id: n for n in notes.values()}
    broken = []
    seen = set()

    # Folder-level references (navigation shorthand, not broken)
    folder_whitelist = {
        '00-META', '10-PROPERTIES', '20-AGENTS', '30-PATTERNS', '40-LOGS', '50-ARCHIVE',
        'Story-Engine', 'OctoGentic', 'Bookbrary', 'RoleFresh',
    }

    # Build a set of all valid targets (by ID suffix, title, and known aliases)
    valid_targets = set(folder_whitelist)
    title_aliases: dict[str, str] = {}
    for key, note in notes.items():
        valid_targets.add(key)
        valid_targets.add(note.title)
        valid_targets.add(note.id)
        if '/' in key:
            valid_targets.add(key.split('/')[-1])
        # "Story Engine — Architecture Overview" -> "Architecture Overview"
        if '—' in note.title:
            short = note.title.split('—')[-1].strip()
            title_aliases[short] = note.id
        if ': ' in note.title:
            short = note.title.split(': ', 1)[1].strip()
            title_aliases[short] = note.id
    valid_targets.update(title_aliases.keys())

    # Patterns that indicate placeholder/template links (not truly broken)
    import re as _re
    PLACEHOLDER_PATTERNS = [
        _re.compile(r'^\.\.\.$'),                           # [[...]]
        _re.compile(r'^(Note Name|Parent Note|Related Note|Child Note|Example Note)$', _re.I),
        _re.compile(r'^(KEY:|TODO:|FIXME:)', _re.I),
        _re.compile(r'^Pattern:'),                           # [[Pattern: X]] — inline refs
        _re.compile(r'^Agent:'),                             # [[Agent: X]] — inline refs
        _re.compile(r'^[a-zA-Z]+-PATTERN'),                  # [[30-PATTERNS/]] — folder refs
    ]

    def _is_placeholder(target: str) -> bool:
        for pat in PLACEHOLDER_PATTERNS:
            if pat.match(target):
                return True
        return False

    for note in unique_notes.values():
        for target in note.outbound:
            target_clean = target.split('#')[0].strip()

            # Skip placeholder/template links
            if _is_placeholder(target_clean):
                continue

            target_name = target_clean.split('/')[-1] if '/' in target_clean else target_clean

            # Check if target resolves
            is_valid = (
                target_clean in notes
                or target_clean in valid_targets
                or target_name in valid_targets
                or target_clean in title_aliases
                or any(n.title == target_clean for n in notes.values())
                or any(n.id.split('/')[-1] == target_name for n in unique_notes.values())
            )

            if not is_valid:
                key = (note.id, target)
                if key not in seen:
                    seen.add(key)
                    broken.append({
                        "from": note.title,
                        "from_id": note.id,
                        "missing_target": target,
                    })
    return broken


def find_clusters(notes: dict[str, Note]) -> list[list[str]]:
    """Find connected components via Union-Find (undirected)."""
    parent = {}

    def find(x):
        if x not in parent:
            parent[x] = x
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    # Build undirected connections
    connected = set()
    unique_notes = {}
    for key, note in notes.items():
        if key == note.id:
            unique_notes[note.id] = note

    for note in unique_notes.values():
        for target in note.outbound:
            target_id = target
            if target in notes:
                n = notes[target_id]
                target_id = n.id
                if target_id in unique_notes:
                    pair = tuple(sorted([note.id, target_id]))
                    if pair not in connected:
                        connected.add(pair)
                        union(note.id, target_id)

    components = defaultdict(list)
    for nid in unique_notes:
        components[find(nid)].append(nid)

    # Sort by size descending
    clusters = sorted(components.values(), key=len, reverse=True)
    return clusters


def find_hub_notes(notes: dict[str, Note], clusters: list[list[str]]) -> list[dict]:
    """Notes that bridge between multiple clusters."""
    # Map note -> cluster index
    note_cluster = {}
    for i, cluster in enumerate(clusters):
        for nid in cluster:
            note_cluster[nid] = i

    unique_notes = {n.id: n for n in notes.values()}
    hubs = []

    for nid, note in unique_notes.items():
        connected_clusters = set()
        # Check outbound
        for target in note.outbound:
            if target in notes:
                target_n = notes[target]
                if target_n.id in note_cluster:
                    connected_clusters.add(note_cluster[target_n.id])
        # Also check inbound
        for other_nid, other in unique_notes.items():
            if other_nid != nid and nid in other.outbound:
                if other_nid in note_cluster:
                    connected_clusters.add(note_cluster[other_nid])

        if len(connected_clusters) > 1:
            hubs.append({
                "title": note.title,
                "id": nid,
                "bridges": len(connected_clusters),
                "group": note.group,
            })

    return sorted(hubs, key=lambda x: x["bridges"], reverse=True)[:5]


def find_tag_gaps(notes: dict[str, Note]) -> dict:
    """Notes without tags, and unused tags."""
    unique_notes = {n.id: n for n in notes.values()}
    untagged = [n for n in unique_notes.values() if not n.tags and n.group != 'logs']
    all_tags = set()
    for n in unique_notes.values():
        all_tags.update(n.tags)
    return {
        "untagged_notes": [{"title": n.title, "id": n.id, "group": n.group} for n in untagged],
        "total_tags": len(all_tags),
        "all_tags": sorted(all_tags),
    }


def find_stale_notes(notes: dict[str, Note], days: int = 14) -> list[dict]:
    """Notes not modified in N days."""
    cutoff = time.time() - (days * 86400)
    unique_notes = {n.id: n for n in notes.values()}
    stale = [n for n in unique_notes.values() if n.last_modified < cutoff and n.group != 'logs']
    cutoff_dt = datetime.fromtimestamp(cutoff).strftime('%Y-%m-%d')
    return [
        {
            "title": n.title,
            "id": n.id,
            "last_updated": datetime.fromtimestamp(n.last_modified).strftime('%Y-%m-%d'),
            "group": n.group,
        }
        for n in sorted(stale, key=lambda x: x.last_modified)
    ]


def compute_health_score(notes: dict[str, Note]) -> dict:
    """Overall vault health metrics."""
    unique_notes = {n.id: n for n in notes.values()}
    total = len(unique_notes)
    if total == 0:
        return {"score": 0}

    orphans = len([n for n in unique_notes.values() if not n.inbound and n.group != 'logs'])
    dead_ends = len([n for n in unique_notes.values() if not n.outbound and n.group != 'logs'])
    untagged = len([n for n in unique_notes.values() if not n.tags and n.group != 'logs'])

    link_count = sum(len(n.outbound) for n in unique_notes.values())
    max_links = total * (total - 1) if total > 1 else 1
    density = link_count / max_links if max_links > 0 else 0

    # Score components (0-100)
    orphan_ratio = orphans / total if total > 0 else 0
    dead_ratio = dead_ends / total if total > 0 else 0
    tag_ratio = untagged / total if total > 0 else 0

    connectivity_score = max(0, 100 - (orphan_ratio * 100))
    richness_score = max(0, 100 - (dead_ratio * 100))
    tagging_score = max(0, 100 - (tag_ratio * 100))
    density_score = min(100, density * 500)  # 20% density = 100 score

    overall = int(
        connectivity_score * 0.3
        + richness_score * 0.25
        + tagging_score * 0.2
        + density_score * 0.25
    )

    return {
        "score": overall,
        "grade": "A" if overall >= 90 else "B" if overall >= 75 else "C" if overall >= 60 else "D" if overall >= 40 else "F",
        "connectivity": int(connectivity_score),
        "richness": int(richness_score),
        "tagging": int(tagging_score),
        "density": round(density, 4),
        "total_notes": total,
        "total_links": link_count,
        "orphan_count": orphans,
        "dead_end_count": dead_ends,
        "untagged_count": untagged,
    }


# ── Report Generation ───────────────────────────────────────────────────────

def generate_text_report(analysis: dict) -> str:
    lines = []
    lines.append("=" * 60)
    lines.append("  VAULT GRAPH ANALYSIS")
    lines.append(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 60)

    # Health
    h = analysis["health"]
    lines.append(f"\n📊 HEALTH: {h['score']}/100 (Grade: {h['grade']})")
    lines.append(f"   Notes: {h['total_notes']} · Links: {h['total_links']} · Density: {h['density']:.2%}")
    lines.append(f"   Connectivity: {h['connectivity']}/100 · Richness: {h['richness']}/100 · Tagging: {h['tagging']}/100")

    # God Notes
    lines.append(f"\n{'─' * 60}")
    lines.append("👑 GOD NOTES (highest connectivity)")
    for i, gn in enumerate(analysis["god_notes"], 1):
        lines.append(f"  {i}. {gn['title']} [{gn['group']}] — in:{gn['inbound']} out:{gn['outbound']} (degree {gn['degree']})")

    # Hubs
    if analysis["hubs"]:
        lines.append(f"\n{'─' * 60}")
        lines.append("🌉 HUB NOTES (bridge clusters)")
        for h in analysis["hubs"]:
            lines.append(f"  · {h['title']} — bridges {h['bridges']} clusters [{h['group']}]")

    # Clusters
    lines.append(f"\n{'─' * 60}")
    lines.append(f"🧩 CLUSTERS ({len(analysis['clusters'])} connected components)")
    for i, cluster in enumerate(analysis["clusters"], 1):
        names = [notes_display(analysis, nid) for nid in cluster[:6]]
        suffix = f" ...+{len(cluster)-6} more" if len(cluster) > 6 else ""
        lines.append(f"  Cluster {i} ({len(cluster)} notes): {', '.join(names)}{suffix}")

    # Orphans
    if analysis["orphans"]:
        lines.append(f"\n{'─' * 60}")
        lines.append(f"🚨 ORPHAN NOTES ({len(analysis['orphans'])} — no inbound links)")
        for o in analysis["orphans"]:
            lines.append(f"  · {o['title']} [{o['group']}] ({o['word_count']}w)")

    # Dead Ends
    if analysis["dead_ends"]:
        lines.append(f"\n{'─' * 60}")
        lines.append(f"🏁 DEAD END NOTES ({len(analysis['dead_ends'])} — no outbound links)")
        for d in analysis["dead_ends"]:
            lines.append(f"  · {d['title']} [{d['group']}] ({d['word_count']}w)")

    # Broken Links
    if analysis["broken_links"]:
        lines.append(f"\n{'─' * 60}")
        lines.append(f"💔 BROKEN LINKS ({len(analysis['broken_links'])} → missing target)")
        for b in analysis["broken_links"][:10]:
            lines.append(f"  · {b['from']} → «{b['missing_target']}» (doesn't exist)")
        if len(analysis["broken_links"]) > 10:
            lines.append(f"     ... +{len(analysis['broken_links']) - 10} more")

    # Tag Gaps
    tg = analysis["tag_gaps"]
    lines.append(f"\n{'─' * 60}")
    lines.append(f"🏷️  TAGS: {tg['total_tags']} unique tags total")
    if tg["untagged_notes"]:
        lines.append(f"  Untagged ({len(tg['untagged_notes'])}):")
        for u in tg["untagged_notes"]:
            lines.append(f"    · {u['title']} [{u['group']}]")

    # Stale Notes
    if analysis["stale_notes"]:
        lines.append(f"\n{'─' * 60}")
        lines.append(f"⏰ STALE NOTES ({len(analysis['stale_notes'])} — not updated in {analysis['stale_threshold']} days)")
        for s in analysis["stale_notes"]:
            lines.append(f"  · {s['title']} [{s['group']}] — last: {s['last_updated']}")

    # Recommendations
    lines.append(f"\n{'─' * 60}")
    lines.append("💡 RECOMMENDATIONS")
    recs = []
    if analysis["orphans"]:
        recs.append(f"Link {len(analysis['orphans'])} orphan notes into the graph")
    if analysis["dead_ends"]:
        recs.append(f"Add outbound links to {len(analysis['dead_ends'])} dead-end notes")
    if analysis["broken_links"]:
        recs.append(f"Fix {len(analysis['broken_links'])} broken wikilinks (create target note or update ref)")
    if analysis["tag_gaps"]["untagged_notes"]:
        recs.append(f"Tag {len(analysis['tag_gaps']['untagged_notes'])} untagged notes")
    if analysis["stale_notes"]:
        recs.append(f"Review {len(analysis['stale_notes'])} stale notes for accuracy")
    if h["score"] >= 90 and not recs:
        recs.append("Graph is healthy — keep up the good linking discipline!")
    for r in recs:
        lines.append(f"  → {r}")

    lines.append(f"\n{'=' * 60}")
    return "\n".join(lines)


def notes_display(analysis, nid):
    """Get display name for a note ID."""
    key = f"_name_{nid}"
    return analysis.get(key, nid.split('/')[-1] if '/' in nid else nid)


def main():
    parser = argparse.ArgumentParser(description="Obsidian Vault Graph Analyzer")
    parser.add_argument("--vault", default=VAULT_PATH, help="Path to vault")
    parser.add_argument("--output", default=None, help="Output file (default: stdout)")
    parser.add_argument("--format", default="text", choices=["text", "json", "md"], help="Output format")
    parser.add_argument("--top", type=int, default=5, help="Top N god notes")
    parser.add_argument("--stale-days", type=int, default=14, help="Days before a note is stale")
    parser.add_argument("--graph-json", default=None, help="Also update vault-graph.json")
    args = parser.parse_args()

    vault_path = args.vault
    if not os.path.isdir(vault_path):
        print(f"ERROR: Vault not found: {vault_path}", file=sys.stderr)
        sys.exit(1)

    # Build index
    notes = build_vault_index(vault_path)
    build_links(notes)

    # Resolve inbound links
    unique_notes = {n.id: n for n in notes.values()}
    source_to_ids = defaultdict(list)
    for key, note in notes.items():
        if key == note.id:
            source_to_ids[note.id].append(key)

    for nid, note in unique_notes.items():
        for target in note.outbound:
            if target in notes:
                target_note = notes[target]
                if target_note.id != target:
                    target_note = unique_notes.get(target_note.id, target_note)
                if target_note.id != note.id:
                    target_note.inbound.append(note.id)

    # Compute all analyses
    clusters = find_clusters(notes)

    # Build ID→title map for display
    id_to_title = {}
    for nid, note in unique_notes.items():
        id_to_title[nid] = note.title

    analysis = {
        "timestamp": datetime.now().isoformat(),
        "vault_path": vault_path,
        "health": compute_health_score(notes),
        "god_notes": find_god_notes(notes, args.top),
        "clusters": clusters,
        "hubs": find_hub_notes(notes, clusters),
        "orphans": find_orphan_notes(notes),
        "dead_ends": find_dead_ends(notes),
        "broken_links": find_broken_links(notes),
        "tag_gaps": find_tag_gaps(notes),
        "stale_notes": find_stale_notes(notes, args.stale_days),
        "stale_threshold": args.stale_days,
    }

    # Embed display names
    for nid, title in id_to_title.items():
        analysis[f"_name_{nid}"] = title

    # Output
    if args.format == "json":
        output = json.dumps(analysis, indent=2, default=str)
    elif args.format == "md":
        output = generate_markdown_report(analysis)
    else:
        output = generate_text_report(analysis)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Wrote to {args.output}")
    else:
        print(output)

    # Optionally update vault-graph.json
    if args.graph_json:
        graph_data = {
            "nodes": [
                {
                    "id": nid,
                    "title": note.title,
                    "group": note.group,
                    "tags": note.tags,
                    "status": note.status,
                    "inbound": len(note.inbound),
                    "outbound": len(note.outbound),
                    "path": note.relpath,
                    "word_count": note.word_count,
                }
                for nid, note in unique_notes.items()
            ],
            "links": [
                {"source": nid, "target": notes[t].id if t in notes else t}
                for nid, note in unique_notes.items()
                for t in note.outbound
            ],
            "analysis": {
                k: v for k, v in analysis.items()
                if not k.startswith('_')
            },
            "meta": {
                "total_nodes": len(unique_notes),
                "total_links": sum(len(n.outbound) for n in unique_notes.values()),
                "last_updated": datetime.now().isoformat(),
                "vault_path": vault_path,
            }
        }
        os.makedirs(os.path.dirname(args.graph_json) or '.', exist_ok=True)
        with open(args.graph_json, 'w') as f:
            json.dump(graph_data, f, indent=2, default=str)
        print(f"Graph JSON updated: {args.graph_json}")


def generate_markdown_report(analysis: dict) -> str:
    h = analysis["health"]
    lines = [
        f"# Vault Graph Analysis",
        "",
        f"> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"## Health: {h['score']}/100 ({h['grade']})",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Notes | {h['total_notes']} |",
        f"| Links | {h['total_links']} |",
        f"| Density | {h['density']:.2%} |",
        f"| Orphans | {h['orphan_count']} |",
        f"| Dead Ends | {h['dead_end_count']} |",
        f"| Untagged | {h['untagged_count']} |",
        "",
        "## God Notes",
        "",
        "# | Note | In | Out | Group",
        "--|------|----|-----|------",
    ]
    for i, gn in enumerate(analysis["god_notes"], 1):
        lines.append(f"{i} | {gn['title']} | {gn['inbound']} | {gn['outbound']} | {gn['group']}")

    if analysis["orphans"]:
        lines.extend(["", "## Orphans", ""])
        for o in analysis["orphans"]:
            lines.append(f"- [[{o['id'].split('/')[-1]}]] — [{o['group']}]")

    if analysis["broken_links"]:
        lines.extend(["", "## Broken Links", ""])
        for b in analysis["broken_links"][:10]:
            lines.append(f"  **{b['from']}** links to missing «{b['missing_target']}»")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
