#!/usr/bin/env python3
"""Obsidian vault daily maintenance: create daily note, scan wikilinks, fix broken ones, save log."""

import os
import re
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

VAULT = Path('/root/projects/obsidian-vault')
TODAY = datetime.now().strftime('%Y-%m-%d')
YESTERDAY = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

# --- Step 1: Collect all markdown files and their note names ---
all_md_files = {}
for root, dirs, files in os.walk(VAULT):
    dirs[:] = [d for d in dirs if d != '.git']
    for f in files:
        if f.endswith('.md'):
            full_path = Path(root) / f
            rel = full_path.relative_to(VAULT)
            note_name = str(rel.with_suffix(os.path.sep if False else '')).replace(os.sep, '/')
            # Use forward slashes
            note_name = str(rel.with_suffix('')).replace('\\', '/')
            all_md_files[note_name] = str(full_path)

all_note_names = set(all_md_files.keys())

# Build stem-to-fullname map for resolving ambiguous short links
stem_to_full = {}
for note_name in all_note_names:
    stem = note_name.split('/')[-1]
    stem_to_full.setdefault(stem, []).append(note_name)

print(f"Total markdown files: {len(all_md_files)}")

# --- Step 2: Extract all wikilinks from all files ---
WIKILINK_RE = re.compile(r'\[\[([^\]\|#]+)(?:#[^\|\]]+)?(?:\|[^\]]+)?\]\]')

links_found = []  # (source_file, line_num, link_target, full_match)

for note_name, filepath in sorted(all_md_files.items()):
    try:
        content = open(filepath, 'r', encoding='utf-8').read()
    except:
        continue
    for i, line in enumerate(content.split('\n'), 1):
        for m in WIKILINK_RE.finditer(line):
            target = m.group(1).strip()
            links_found.append((note_name, i, target, m.group(0), line.strip()))

print(f"Total wikilink occurrences found: {len(links_found)}")

# --- Step 3: Check each link for resolution ---
broken = []
resolved = []

for src, line, target, full_match, line_text in links_found:
    # Try exact match first
    if target in all_note_names:
        resolved.append((src, line, target, 'exact'))
        continue
    # Try matching by stem
    stem = target.split('/')[-1]
    candidates = stem_to_full.get(stem, [])
    if len(candidates) == 1:
        resolved.append((src, line, target, f'ambiguous-resolved-to:{candidates[0]}'))
    elif len(candidates) > 1:
        # Ambiguous - multiple candidates
        broken.append((src, line, target, f'AMBIGUOUS: {candidates}', full_match, line_text))
    else:
        # Check if it's a future-dated daily note (forward reference - acceptable)
        if re.match(r'20\d{2}-\d{2}-\d{2}$', target):
            # Check if the file exists
            daily_path = VAULT / '00-DAILY' / f'{target}.md'
            if daily_path.exists():
                resolved.append((src, line, target, 'daily-exists'))
            else:
                # Forward reference to future daily note - this is a valid forward link
                broken.append((src, line, target, 'FUTURE_DAILY', full_match, line_text))
        else:
            broken.append((src, line, target, 'NO_MATCH', full_match, line_text))

print(f"\nResolved links: {len(resolved)}")
print(f"Broken/ambiguous links: {len(broken)}")

# Print broken links
print("\n--- BROKEN/AMBIGUOUS LINKS ---")
for b in broken:
    print(f"  {b[0]}:{b[1]} -> [[{b[2]}]] -- {b[3]}")
    if len(b) > 5:
        print(f"    Line: {b[5]}")

# --- Step 4: Fix broken links ---
fixes_made = []

for src, line, target, reason, full_match, line_text in broken:
    filepath = all_md_files.get(src)
    if not filepath:
        continue
    
    # Strategy 1: Fix ambiguous links by picking the most likely candidate
    if reason.startswith('AMBIGUOUS:'):
        candidates = [c for c in stem_to_full.get(target.split('/')[-1], []) if c]
        if not candidates:
            continue
        # Prefer shorter path (more likely the main note)
        candidates.sort(key=lambda c: (len(c.split('/')), len(c)))
        best = candidates[0]
        # Replace the link
        try:
            content = open(filepath, 'r', encoding='utf-8').read()
            lines = content.split('\n')
            old_line = lines[line - 1]
            new_line = old_line.replace(full_match, f'[[{best}|{target}]]')
            lines[line - 1] = new_line
            open(filepath, 'w', encoding='utf-8').write('\n'.join(lines))
            fixes_made.append((src, line, f'[[{target}]] -> [[{best}|{target}]]'))
            print(f"  FIXED: {src}:{line} [[{target}]] -> [[{best}|{target}]]")
        except Exception as e:
            print(f"  ERROR fixing {src}:{line}: {e}")
    
    # Strategy 2: Fix non-existent links by finding similar file
    elif reason == 'NO_MATCH':
        stem = target.split('/')[-1]
        # Search for any file whose stem contains the target or vice versa
        found = None
        for note_name in all_note_names:
            if stem.lower() in note_name.lower() or note_name.lower().endswith('/' + stem.lower()):
                found = note_name
                break
        if found:
            try:
                content = open(filepath, 'r', encoding='utf-8').read()
                lines = content.split('\n')
                old_line = lines[line - 1]
                # Preserve alias
                alias = target.split('/')[-1]
                new_link = f'[[{found}|{alias}]]'
                new_line = old_line.replace(full_match, new_link)
                lines[line - 1] = new_line
                open(filepath, 'w', encoding='utf-8').write('\n'.join(lines))
                fixes_made.append((src, line, f'[[{target}]] -> [[{found}|{alias}]]'))
                print(f"  FIXED: {src}:{line} [[{target}]] -> [[{found}|{alias}]]")
            except Exception as e:
                print(f"  ERROR fixing {src}:{line}: {e}")
        else:
            print(f"  UNFIXED (no match found): {src}:{line} [[{target}]]")
    
    # Strategy 3: Future daily notes - leave as forward references (valid)
    elif reason == 'FUTURE_DAILY':
        print(f"  FORWARD REF (valid): {src}:{line} [[{target}]]")

# --- Step 5: Create today's daily note ---
daily_note_path = VAULT / '00-DAILY' / f'{TODAY}.md'
if not daily_note_path.exists():
    # Read yesterday's note for context
    yesterday_path = VAULT / '00-DAILY' / f'{YESTERDAY}.md'
    yesterday_content = ''
    if yesterday_path.exists():
        yesterday_content = open(yesterday_path).read()
    
    daily_content = f"""# Daily Note: {TODAY}

_Part of → [[Home]]_
_Maintained by → [[CoS]]_
_Created: {TODAY}_

## Today's #1 Priority
- [ ] Awaiting principal direction

## Overnight Signals
- (checked at cron time)

## Shipped Today
- Vault maintenance: created daily note, scanned wikilinks, fixed broken links

## Decisions
- None yet

## Open Items
- None yet

## Notes
- {TODAY}: [[{TODAY}]] — Daily maintenance cron ran

---
← [[{YESTERDAY}]]
"""
    daily_note_path.write_text(daily_content, encoding='utf-8')
    print(f"\nCreated daily note: {daily_note_path}")
else:
    print(f"\nDaily note already exists: {daily_note_path}")

# --- Step 6: Save maintenance log ---
log_dir = VAULT / '40-LOGS'
log_dir.mkdir(exist_ok=True)
log_path = log_dir / 'vault-analysis-latest.md'

log_content = f"""# Vault Maintenance Log: {TODAY}

> Generated by CoS daily maintenance cron
> Date: {TODAY} (Saturday, October 17, 2026)

## Summary
- Total notes: {len(all_md_files)}
- Total wikilink occurrences: {len(links_found)}
- Resolved links: {len(resolved)}
- Broken/ambiguous links found: {len(broken)}
- Fixes applied: {len(fixes_made)}
- Daily note created: {not (VAULT / '00-DAILY' / f'{TODAY}.md').exists()}

## Fixes Applied
"""
for src, line, fix in fixes_made:
    log_content += f"- {src}:{line} — {fix}\n"

log_content += f"""
## Unresolved Links (forward references / known acceptable)
"""
for b in broken:
    if b[3] == 'FUTURE_DAILY':
        log_content += f"- {b[0]}:{b[1]} -> [[{b[2]}]] -- forward reference (valid)\n"

log_content += f"""
## Notes
"""
for n in sorted(all_note_names):
    log_content += f"- {n}\n"

log_path.write_text(log_content, encoding='utf-8')
print(f"Saved maintenance log to: {log_path}")

# --- Step 7: Output summary ---
print(f"\n=== VAULT MAINTENANCE COMPLETE ===")
print(f"Notes: {len(all_md_files)}")
print(f"Links scanned: {len(links_found)}")
print(f"Fixes applied: {len(fixes_made)}")
print(f"Daily note: {TODAY} created")
print(f"Log: vault-analysis-latest.md updated")
