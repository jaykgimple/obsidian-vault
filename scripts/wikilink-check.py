#!/usr/bin/env python3
"""Scan vault for broken wikilinks, categorize, and generate maintenance log.

Skips:
- Wikilinks inside inline code spans (backticks)
- The generated report file itself (vault-analysis-latest.md)
- Known template placeholders in documentation
"""

import re
from pathlib import Path
from datetime import datetime

VAULT = Path("/root/projects/obsidian-vault")
REPORT_FILE = "40-LOGS/vault-analysis-latest.md"

# Known template placeholders to skip
PLACEHOLDERS = {"note name", "...", "note name|alias"}

def get_all_note_paths():
    notes = set()
    for md in VAULT.rglob("*.md"):
        if ".git" in str(md):
            continue
        rel = str(md.relative_to(VAULT).with_suffix(""))
        notes.add(rel)
    return notes

def extract_wikilinks_outside_code(text):
    """Extract wikilinks that are NOT inside inline code spans."""
    # First, remove fenced code blocks (triple backticks)
    cleaned = re.sub(r'```[\s\S]*?```', '', text)
    # Remove double-backtick spans first
    cleaned = re.sub(r'``[^`]*``', '', cleaned)
    # Then remove single-backtick spans
    cleaned = re.sub(r'`[^`]+`', '', cleaned)
    pattern = r'\[\[([^\]]+)\]\]'
    return re.findall(pattern, cleaned)

def check_link(link, all_notes):
    target = link.split("|")[0].strip()
    if target.lower() in PLACEHOLDERS:
        return "placeholder", target
    if "#" in target:
        file_part, section = target.split("#", 1)
    else:
        file_part = target
        section = None
    if file_part in all_notes:
        return "ok", target
    file_name = file_part.split("/")[-1] if "/" in file_part else file_part
    for note in all_notes:
        note_name = note.split("/")[-1] if "/" in note else note
        if note_name == file_name:
            return "ok", note + (f"#{section}" if section else "")
    return "broken_file", target

def main():
    all_notes = get_all_note_paths()
    broken_links = []
    placeholder_links = []
    files_checked = 0
    total_links = 0
    
    for md_file in sorted(VAULT.rglob("*.md")):
        if ".git" in str(md_file):
            continue
        rel_path = str(md_file.relative_to(VAULT))
        # Skip the generated report file
        if rel_path == REPORT_FILE:
            continue
        files_checked += 1
        content = md_file.read_text(encoding="utf-8")
        links = extract_wikilinks_outside_code(content)
        total_links += len(links)
        if not links:
            continue
        for link in links:
            status, resolved = check_link(link, all_notes)
            if status == "placeholder":
                placeholder_links.append({"file": rel_path, "link": link})
            elif status == "broken_file":
                broken_links.append({
                    "file": rel_path,
                    "link": link,
                    "target": link.split("|")[0].strip(),
                })
    
    # Generate report
    report_lines = [
        "---",
        f"title: Vault Analysis — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"tags: [vault, maintenance, analysis]",
        f"updated: {datetime.now().strftime('%Y-%m-%d')}",
        "---",
        "",
        "# Vault Analysis Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total notes scanned:** {files_checked}",
        f"**Total unique notes:** {len(all_notes)}",
        f"**Total wikilinks found (excl. code spans):** {total_links}",
        "",
        "## Summary",
        "",
        f"- Valid links: **{total_links - len(broken_links) - len(placeholder_links)}**",
        f"- Broken links (file not found): **{len(broken_links)}**",
        f"- Template placeholders: **{len(placeholder_links)}**",
        f"- Files with broken links: **{len(set(b['file'] for b in broken_links))}**",
        "",
    ]
    
    if broken_links:
        report_lines.append("## Broken Wikilinks (File Not Found)")
        report_lines.append("")
        by_file = {}
        for b in broken_links:
            by_file.setdefault(b["file"], []).append(b)
        for file, links in sorted(by_file.items()):
            report_lines.append(f"### `{file}`")
            for b in links:
                report_lines.append(f"- [[{b['link']}]] → `{b['target']}`")
            report_lines.append("")
    else:
        report_lines.append("## Broken Wikilinks")
        report_lines.append("")
        report_lines.append("No broken wikilinks found. Vault is clean.")
        report_lines.append("")
    
    if placeholder_links:
        report_lines.append("## Template Placeholders (not broken, needs authoring)")
        report_lines.append("")
        by_file = {}
        for p in placeholder_links:
            by_file.setdefault(p["file"], []).append(p)
        for file, links in sorted(by_file.items()):
            report_lines.append(f"### `{file}`")
            for p in links:
                report_lines.append(f"- [[{p['link']}]]")
            report_lines.append("")
    
    log_path = VAULT / REPORT_FILE
    log_path.write_text("\n".join(report_lines), encoding="utf-8")
    
    print(f"Files scanned: {files_checked}")
    print(f"Total notes: {len(all_notes)}")
    print(f"Total wikilinks: {total_links}")
    print(f"Broken links: {len(broken_links)}")
    print(f"Placeholders: {len(placeholder_links)}")
    if broken_links:
        print("\nBroken links by file:")
        by_file = {}
        for b in broken_links:
            by_file.setdefault(b["file"], []).append(b)
        for file, links in sorted(by_file.items()):
            print(f"  {file}: {len(links)} broken")

if __name__ == "__main__":
    main()
