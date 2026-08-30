#!/usr/bin/env python3
import os
import re
from pathlib import Path

vault_path = Path("/root/projects/obsidian-vault")

# Collect all markdown files
all_md_files = set()
md_file_paths = []

for root, dirs, files in os.walk(vault_path):
    dirs[:] = [d for d in dirs if d != '.git']
    for f in files:
        if f.endswith('.md'):
            full = Path(root) / f
            rel = full.relative_to(vault_path)
            md_file_paths.append(rel)
            stem = rel.stem
            all_md_files.add(stem)
            all_md_files.add(str(rel.with_suffix('')))

print(f"Total markdown files: {len(md_file_paths)}")
print(f"Unique link targets available: {len(all_md_files)}")

# Scan each file for wikilinks
wikilink_pattern = re.compile(r'\[\[([^\]\|#]+)(?:\|[^\]]+)?(?:#[^\]]+)?\]\]')

broken_links = []

for rel_path in sorted(md_file_paths):
    full_path = vault_path / rel_path
    content = full_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    for i, line in enumerate(lines, 1):
        for match in wikilink_pattern.finditer(line):
            target = match.group(1).strip()
            target_lower = target.lower()
            found = any(t.lower() == target_lower for t in all_md_files)
            if not found:
                broken_links.append((str(rel_path), target, i, line.strip()))

print(f"\nBroken wikilinks found: {len(broken_links)}")
for file, target, line_num, line_content in broken_links:
    print(f"  {file}:{line_num} -> [[{target}]]")
    print(f"    Line: {line_content[:120]}")
