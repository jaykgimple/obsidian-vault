#!/usr/bin/env python3
"""Fix broken wikilinks in the Obsidian vault.

Strategy:
1. In documentation sections (health reports, fix logs), convert broken wikilinks to backtick-wrapped text.
2. Fix truly broken navigational links.
3. Leave valid links and section links alone.
"""

import re
from pathlib import Path

VAULT = Path("/root/projects/obsidian-vault")

# Files that contain documentation sections with broken wikilinks
# These need their doc-section wikilinks converted to backtick text
DOC_FILES = {
    "40-LOGS/2026-08-15.md",
    "40-LOGS/2026-08-16.md",
    "40-LOGS/2026-08-17.md",
    "40-LOGS/2026-08-18.md",
    "40-LOGS/2026-08-19.md",
    "40-LOGS/2026-08-26.md",
    "40-LOGS/2026-09-02.md",
}

def fix_file(rel_path):
    """Fix broken wikilinks in a file."""
    filepath = VAULT / rel_path
    content = filepath.read_text(encoding="utf-8")
    original = content
    
    # Pattern: wikilinks that are broken (target doesn't exist as a file)
    # We'll convert them to backtick-wrapped text
    
    # Specific fixes for known broken links in documentation
    
    # 40-LOGS/2026-09-02.md: old slug in maintenance log
    if rel_path == "40-LOGS/2026-09-02.md":
        content = content.replace(
            "[[10-PROPERTIES/OctoGentic/Blog/2026-09-02-agentic-grounding-how-autonomous-systems-verify-what-they-think-they-know|...]]",
            "`10-PROPERTIES/OctoGentic/Blog/2026-09-02-agentic-grounding-how-autonomous-systems-verify-what-they-think-they-know`"
        )
    
    # 40-LOGS/2026-08-26.md: non-existent blog post reference
    if rel_path == "40-LOGS/2026-08-26.md":
        content = content.replace("[[2026-08-24-Agentic-Coherence]]", "`2026-08-24-Agentic-Coherence`")
    
    # 40-LOGS/2026-08-16.md: Lessons folder link in doc
    if rel_path == "40-LOGS/2026-08-16.md":
        content = content.replace(
            "[[10-PROPERTIES/Story-Engine/Lessons|Lesson]]",
            "`10-PROPERTIES/Story-Engine/Lessons`"
        )
    
    # 40-LOGS/2026-08-15.md: documentation section wikilinks
    if rel_path == "40-LOGS/2026-08-15.md":
        # Convert all the broken wikilinks in the health report section
        replacements = {
            "[[00-META]]": "`00-META`",
            "[[10-PROPERTIES]]": "`10-PROPERTIES`",
            "[[20-AGENTS]]": "`20-AGENTS`",
            "[[30-PATTERNS]]": "`30-PATTERNS`",
            "[[40-LOGS]]": "`40-LOGS`",
            "[[50-ARCHIVE]]": "`50-ARCHIVE`",
            "[[30-PATTERNS/]]": "`30-PATTERNS/`",
            "[[Agent: Architect]]": "`Agent: Architect`",
            "[[Agent: Novelist]]": "`Agent: Novelist`",
            "[[Agent: Dev Editor]]": "`Agent: Dev Editor`",
            "[[Agent: Copy Editor]]": "`Agent: Copy Editor`",
            "[[Agent: Pipeline Orchestrator]]": "`Agent: Pipeline Orchestrator`",
            "[[Agent: Audit]]": "`Agent: Audit`",
            "[[Agent: Biographer]]": "`Agent: Biographer`",
            "[[Lesson: Coherence Threshold Must Be 9]]": "`Lesson: Coherence Threshold Must Be 9`",
            "[[Pattern: Queue Dual-Write]]": "`Pattern: Queue Dual-Write`",
            "[[Bookbrary — Submission Form]]": "`Bookbrary — Submission Form`",
            "[[Story-Engine — Queue Worker]]": "`Story-Engine — Queue Worker`",
            "[[2026-06-26-the-Agentic-Compound-Effect]]": "`2026-06-26-the-Agentic-Compound-Effect`",
            "[[2026-06-26-The-Agentic-Compound-Effect]]": "`2026-06-26-The-Agentic-Compound-Effect`",
            "[[Takeaway 7.5]]": "`Takeaway 7.5`",
            "[[Agent: Cover Artist]]": "`Agent: Cover Artist`",
            "[[Takeaway T-A2]]": "`Takeaway T-A2`",
            "[[Takeaway T-C3]]": "`Takeaway T-C3`",
            "[[Parent Note]]": "`Parent Note`",
        }
        for old, new in replacements.items():
            content = content.replace(old, new)
    
    # 40-LOGS/2026-08-17.md: documentation section wikilinks
    if rel_path == "40-LOGS/2026-08-17.md":
        replacements = {
            "[[2026-06-26-The-Agentic-Compound-Effect]]": "`2026-06-26-The-Agentic-Compound-Effect`",
            "[[2026-06-25-The-Agentic-Feedback-Loop]]": "`2026-06-25-The-Agentic-Feedback-Loop`",
            "[[Story Engine — Overview]]": "`Story Engine — Overview`",
            "[[OctoGentic Blog Index]]": "`OctoGentic Blog Index`",
            "[[OctoGentic — Portfolio]]": "`OctoGentic — Portfolio`",
            "[[Story Engine — Agent Deep-Dives]]": "`Story Engine — Agent Deep-Dives`",
            "[[Daily Log Template]]": "`Daily Log Template`",
            "[[Story-Engine — Watchdog]]": "`Story-Engine — Watchdog`",
            "[[Story-Engine — Review System]]": "`Story-Engine — Review System`",
        }
        for old, new in replacements.items():
            content = content.replace(old, new)
    
    # 40-LOGS/2026-08-18.md: documentation section wikilinks
    if rel_path == "40-LOGS/2026-08-18.md":
        replacements = {
            "[[Story Engine — Overview]]": "`Story Engine — Overview`",
            "[[Story-Engine — Watchdog]]": "`Story-Engine — Watchdog`",
            "[[Story-Engine — Review System]]": "`Story-Engine — Review System`",
            "[[Agent: Architect]]": "`Agent: Architect`",
        }
        for old, new in replacements.items():
            content = content.replace(old, new)
    
    if content != original:
        filepath.write_text(content, encoding="utf-8")
        return True
    return False

def main():
    fixed_files = []
    for rel_path in DOC_FILES:
        if fix_file(rel_path):
            fixed_files.append(rel_path)
    
    if fixed_files:
        print(f"Fixed {len(fixed_files)} files:")
        for f in fixed_files:
            print(f"  - {f}")
    else:
        print("No fixes applied.")

if __name__ == "__main__":
    main()
