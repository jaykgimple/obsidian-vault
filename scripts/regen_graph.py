import re
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict

vault_path = Path("/root/projects/obsidian-vault")

all_md_files = []
for root, dirs, files in os.walk(vault_path):
    if ".git" in root:
        continue
    for f in files:
        if f.endswith(".md"):
            all_md_files.append(os.path.join(root, f))
all_md_files.sort()

existing_notes = {}
for f in all_md_files:
    rel = os.path.relpath(f, vault_path).replace("\\", "/")
    note_path = rel[:-3]
    existing_notes[note_path] = rel

short_to_paths = defaultdict(list)
for note_path in existing_notes:
    short = note_path.split("/")[-1]
    short_to_paths[short].append(note_path)

wikilink_pattern = re.compile(r"\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|([^\]]*))?\]\]")

nodes = {}
all_link_pairs = []

for f in all_md_files:
    rel = os.path.relpath(f, vault_path).replace("\\", "/")
    note_path = rel[:-3]
    with open(f, "r") as fh:
        content = fh.read()
    title = note_path.split("/")[-1]
    tags = []
    status = "active"
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        fm = fm_match.group(1)
        title_m = re.search(r"^title:\s*(.+)", fm, re.MULTILINE)
        if title_m:
            title = title_m.group(1).strip()
        tags_m = re.search(r"^tags:\s*\[(.+?)\]", fm, re.MULTILINE)
        if tags_m:
            tags = [t.strip() for t in tags_m.group(1).split(",")]
        status_m = re.search(r"^status:\s*(.+)", fm, re.MULTILINE)
        if status_m:
            status = status_m.group(1).strip()
    group = note_path.split("/")[0]
    out_links = set()
    for match in wikilink_pattern.finditer(content):
        target = match.group(1).strip()
        resolved = None
        if target in existing_notes:
            resolved = target
        elif target in short_to_paths:
            resolved = short_to_paths[target][0]
        else:
            file_dir = os.path.dirname(note_path)
            candidate = os.path.normpath(os.path.join(file_dir, target)).replace("\\", "/")
            if candidate in existing_notes:
                resolved = candidate
        if resolved and resolved != note_path:
            out_links.add(resolved)
            all_link_pairs.append((note_path, resolved))
    nodes[note_path] = {
        "id": note_path,
        "title": title,
        "group": group,
        "tags": tags,
        "status": status,
        "path": rel,
        "links_count": len(out_links),
        "inbound_count": 0
    }

inbound_count = defaultdict(int)
for src, dst in all_link_pairs:
    inbound_count[dst] += 1
for note_path in nodes:
    nodes[note_path]["inbound_count"] = inbound_count.get(note_path, 0)

links = [{"source": s, "target": d} for s, d in all_link_pairs]
groups = sorted(set(n["group"] for n in nodes.values()))

graph = {
    "meta": {
        "total_nodes": len(nodes),
        "total_links": len(links),
        "groups": groups,
        "last_updated": datetime.now(timezone.utc).isoformat()
    },
    "nodes": [nodes[k] for k in sorted(nodes.keys())],
    "links": links
}

with open(vault_path / "vault-graph.json", "w") as fh:
    json.dump(graph, fh, indent=2)

print(f"Nodes: {len(nodes)}")
print(f"Links: {len(links)}")
print(f"Groups: {groups}")
orphans = sum(1 for n in nodes.values() if n["inbound_count"] == 0)
dead_ends = sum(1 for n in nodes.values() if n["links_count"] == 0)
untagged = sum(1 for n in nodes.values() if not n["tags"])
print(f"Orphans: {orphans}")
print(f"Dead Ends: {dead_ends}")
print(f"Untagged: {untagged}")
