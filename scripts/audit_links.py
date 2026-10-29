#!/usr/bin/env python3
"""Vault wikilink auditor. Scans all .md files for [[links]] and checks they resolve."""
import os, re, json
from collections import defaultdict

VAULT = '/root/projects/obsidian-vault'
ALL_NOTES = set()

# Build set of all note paths (without .md)
for root, dirs, files in os.walk(VAULT):
    if '.git' in root:
        continue
    for f in files:
        if f.endswith('.md'):
            relpath = os.path.relpath(os.path.join(root, f), VAULT).replace('.md', '')
            ALL_NOTES.add(relpath)
            # Also add just the filename
            ALL_NOTES.add(f.replace('.md', ''))

# Extract all wikilinks from all files
all_links = []
for root, dirs, files in os.walk(VAULT):
    if '.git' in root:
        continue
    for f in files:
        if f.endswith('.md'):
            filepath = os.path.join(root, f)
            relpath = os.path.relpath(filepath, VAULT)
            with open(filepath, 'r') as fh:
                content = fh.read()
            # Find all wikilinks: [[target]] or [[target|alias]]
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            for link in links:
                all_links.append({
                    'file': relpath,
                    'raw_link': link,
                    'target': link.split('|')[0].strip(),
                    'alias': link.split('|')[1].strip() if '|' in link else None
                })

# Check each link
broken = []
resolved = 0
unresolved_targets = defaultdict(list)

for link in all_links:
    target = link['target']
    # Check if target exists
    if target in ALL_NOTES:
        resolved += 1
        link['status'] = 'resolved'
    else:
        # Try adding path prefixes for short links
        found = False
        # Check if it's a short name that exists
        for note in ALL_NOTES:
            if note.endswith('/' + target) or note == target:
                found = True
                break
        if found:
            resolved += 1
            link['status'] = 'resolved'
        else:
            link['status'] = 'broken'
            broken.append(link)
            unresolved_targets[target].append(link['file'])

print(f"Total links: {len(all_links)}")
print(f"Resolved: {resolved}")
print(f"Broken: {len(broken)}")
print(f"\n=== BROKEN LINKS ===")
for target, files in sorted(unresolved_targets.items()):
    print(f"\n  [[{target}]]")
    for f in files:
        print(f"    in: {f}")

print(f"\n=== ALL NOTE PATHS (for reference) ===")
for n in sorted(ALL_NOTES):
    print(f"  {n}")
