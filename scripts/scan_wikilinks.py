#!/usr/bin/env python3
"""Scan all markdown files for wikilinks, identify truly broken ones.
Handles path-based links and excludes code-span/template false positives."""
import os
import re
import json
from pathlib import Path

VAULT = Path("/root/projects/obsidian-vault")

# Build lookup: full relative path (lowercase, no .md) -> rel path
# Also build stem lookup
existing_by_path = {}  # e.g. "10-properties/octogentic/blog/2026-09-07-agentic-synthesis" -> rel
existing_by_stem = {}  # e.g. "2026-09-07-agentic-synthesis" -> rel

for root, dirs, files in os.walk(VAULT):
    if '.git' in root:
        continue
    for f in files:
        if f.endswith('.md'):
            rel = os.path.relpath(os.path.join(root, f), VAULT)
            path_key = rel.lower().replace('.md', '')
            existing_by_path[path_key] = rel
            stem = Path(f).stem.lower()
            existing_by_stem[stem] = rel

# Pattern for wikilinks: [[target#heading|alias]] -> capture target
wikilink_pattern = re.compile(r'\[\[([^\]\|#]+)')

def is_inside_backticks(content, pos):
    """Check if position is inside a code span (backticks)."""
    line_start = content.rfind('\n', 0, pos) + 1
    line_end = content.find('\n', pos)
    if line_end == -1:
        line_end = len(content)
    line = content[line_start:line_end]
    # Check if there's a backtick before pos on this line
    backtick_count = line[:pos - line_start].count('`')
    return backtick_count % 2 == 1

broken_links = []
all_links = []

for root, dirs, files in os.walk(VAULT):
    if '.git' in root:
        continue
    for f in files:
        if f.endswith('.md'):
            rel = os.path.relpath(os.path.join(root, f), VAULT)
            filepath = os.path.join(root, f)
            with open(filepath, 'r') as fh:
                content = fh.read()
            
            for match in wikilink_pattern.finditer(content):
                target = match.group(1).strip()
                target_lower = target.lower()
                pos = match.start()
                
                # Skip if inside backticks
                if is_inside_backticks(content, pos):
                    continue
                
                # Skip template examples
                if target in ('Note Name', '...', 'link', 'target'):
                    continue
                
                line_num = content[:pos].count('\n') + 1
                line_content = content.split('\n')[line_num - 1].strip()
                
                all_links.append({"from": rel, "to": target, "line": line_num})
                
                # Check if link resolves
                resolved = False
                if '/' in target:
                    # Path-based link
                    if target_lower in existing_by_path:
                        resolved = True
                else:
                    # Stem-based link
                    if target_lower in existing_by_stem:
                        resolved = True
                
                if not resolved:
                    broken_links.append({
                        "from": rel,
                        "to": target,
                        "line": line_num,
                        "context": line_content
                    })

print(json.dumps({
    "total_links": len(all_links),
    "broken_count": len(broken_links),
    "broken": broken_links,
    "total_notes": len(existing_by_path)
}, indent=2))
