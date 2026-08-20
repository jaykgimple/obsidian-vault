import os
import re
import json
from pathlib import Path

vault_path = Path("/root/projects/obsidian-vault")

# Get all markdown files
md_files = sorted([f for f in vault_path.rglob("*.md") if ".git" not in str(f)])
print(f"Total markdown files: {len(md_files)}")

# Build set of all note IDs
all_notes = set()
for f in md_files:
    rel = f.relative_to(vault_path)
    note_id = str(rel.with_suffix(""))
    all_notes.add(note_id)
    all_notes.add(rel.stem)

print(f"Total unique note identifiers: {len(all_notes)}")

# Sort notes by length (longest first) for greedy matching
sorted_notes = sorted(all_notes, key=len, reverse=True)

def normalize_note_id(name):
    """Normalize a wikilink target to check against known notes."""
    return name.strip()

def target_exists(target, all_notes_set):
    """Check if a wikilink target resolves to an existing note."""
    target = target.strip()
    if not target:
        return False
    # Direct match
    if target in all_notes_set:
        return True
    # Match by path ending
    for nid in all_notes_set:
        if nid == target or nid.endswith("/" + target):
            return True
    return False

# Remove code blocks and inline code before scanning
# This avoids false positives from documentation of past fixes
code_block_pattern = re.compile(r'```[\s\S]*?```', re.MULTILINE)
inline_code_pattern = re.compile(r'`([^`]+)`')

wikilink_pattern = re.compile(r'\[\[([^\]\|#]+)(?:#[^\]\|]*)?(?:\|[^\]]*)?\]\]')

broken_links = []
all_links = []

for f in md_files:
    rel = f.relative_to(vault_path)
    note_id = str(rel.with_suffix(""))
    content = f.read_text(encoding="utf-8")
    
    # Strip code blocks and inline code
    cleaned = code_block_pattern.sub('', content)
    cleaned = inline_code_pattern.sub('', cleaned)
    
    matches = wikilink_pattern.findall(cleaned)
    for match in matches:
        target = match.strip()
        if not target:
            continue
        all_links.append((note_id, target))
        
        if not target_exists(target, all_notes):
            broken_links.append((note_id, target))

print(f"\nTotal wikilinks found (excl. code): {len(all_links)}")
print(f"Broken wikilinks found: {len(broken_links)}")

if broken_links:
    print("\n--- BROKEN LINKS (REAL NAVIGATIONAL ISSUES) ---")
    for src, tgt in broken_links:
        print(f"  {src} -> [[{tgt}]]")
else:
    print("\nNo broken navigational links found!")

# Also check for orphan notes (no inbound links)
print("\n--- ORPHAN CHECK ---")
inbound_counts = {str(f.relative_to(vault_path).with_suffix("")): 0 for f in md_files}
for src, tgt in all_links:
    for nid in inbound_counts:
        if nid == tgt or nid.endswith("/" + tgt):
            inbound_counts[nid] += 1
            break

orphans = [nid for nid, count in inbound_counts.items() if count == 0]
if orphans:
    print(f"Orphan notes ({len(orphans)}):")
    for o in sorted(orphans):
        print(f"  {o}")
else:
    print("No orphan notes — all notes have at least one inbound link.")
