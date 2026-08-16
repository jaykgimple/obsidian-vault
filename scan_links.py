import re
import os
import json
from pathlib import Path
from collections import defaultdict

vault_path = Path("/root/projects/obsidian-vault")

# Get all markdown files
all_md_files = list(vault_path.rglob("*.md"))
print(f"Total markdown files: {len(all_md_files)}")

# Build set of existing note names (without extension, and relative paths)
existing_notes = set()
existing_paths = set()
for f in all_md_files:
    rel = f.relative_to(vault_path)
    existing_paths.add(str(rel))
    # Various forms Obsidian might resolve
    existing_notes.add(f.name)  # e.g. "Home.md"
    existing_notes.add(f.stem)  # e.g. "Home"
    existing_notes.add(str(rel))  # e.g. "00-META/Home.md"
    existing_notes.add(str(rel).replace('.md', ''))  # e.g. "00-META/Home"
    # Also with forward slashes normalized
    existing_notes.add(str(rel).replace('.md', '').replace('\\', '/'))

print(f"\nExisting paths:")
for p in sorted(existing_paths):
    print(f"  {p}")

# Extract all wikilinks from all files
wikilink_pattern = re.compile(r'\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]')

all_broken = []
all_links = []

for f in all_md_files:
    content = f.read_text()
    rel = str(f.relative_to(vault_path))
    for match in wikilink_pattern.finditer(content):
        link_target = match.group(1).strip()
        all_links.append((rel, link_target))
        
        # Check if target exists
        found = False
        
        # 1. As-is with .md
        if link_target + '.md' in existing_notes:
            found = True
        # 2. As-is without .md (stem only)
        elif link_target in existing_notes:
            found = True
        # 3. As relative path in vault
        elif (vault_path / link_target).exists():
            found = True
        elif (vault_path / (link_target + '.md')).exists():
            found = True
            
        if not found:
            all_broken.append((rel, link_target, match.group(0)))

print(f"\nTotal wikilinks found: {len(all_links)}")
print(f"Broken wikilinks: {len(all_broken)}")

if all_broken:
    print("\nBroken links by file:")
    by_file = defaultdict(list)
    for file, target, full in all_broken:
        by_file[file].append((target, full))
    for file, links in sorted(by_file.items()):
        print(f"\n  {file}:")
        for target, full in links:
            print(f"    → {full}")
else:
    print("\nNo broken links found!")
