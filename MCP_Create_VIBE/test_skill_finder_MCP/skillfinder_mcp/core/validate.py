"""Inventory validation report. Read-only: never modifies skill files."""
from itertools import combinations

from .index import Snapshot
from .search import tokenize

OVERLAP_THRESHOLD = 0.6
SUGGESTIONS = {
    "invalid_frontmatter": "Fix the YAML between the leading '---' lines (check indentation and quoting).",
    "missing_frontmatter": "Add YAML frontmatter with at least 'name' and 'description'.",
    "missing_name": "Add a 'name' field matching the folder name.",
    "missing_description": "Add a 'description' that says what the skill does and when to use it.",
    "name_folder_mismatch": "Rename the folder or the 'name' so they match.",
    "empty_instructions": "Add actionable instructions below the frontmatter.",
    "duplicate_id": "Give each skill a unique 'name'.",
    "broken_reference": "Create the referenced file or fix the path in SKILL.md.",
    "symlink_skipped": "Replace the symbolic link with a real file or directory.",
    "unreadable": "Check file permissions.",
    "too_large": "Split the file or raise SKILLFINDER_MAX_FILE_BYTES.",
    "binary_file": "SKILL.md must be UTF-8 text.",
    "empty_directory": "Remove the empty directory or add a skill to it.",
    "high_overlap": "Merge the skills or sharpen their descriptions so they are distinct.",
    "parse_failed": "Check the file for unusual encoding or structure.",
}


def validate(snap: Snapshot) -> dict:
    issues = [dict(i, suggestion=SUGGESTIONS.get(i["code"], "")) for i in snap.issues]

    # Highly overlapping descriptions (Jaccard on description stems).
    sets = {sid: set(tokenize(s.description)) for sid, s in snap.skills.items() if s.description}
    for a, b in combinations(sorted(sets), 2):
        if not sets[a] or not sets[b]:
            continue
        j = len(sets[a] & sets[b]) / len(sets[a] | sets[b])
        if j >= OVERLAP_THRESHOLD:
            issues.append({"severity": "warning", "code": "high_overlap", "skill_id": a,
                           "path": snap.skills[a].rel_dir,
                           "message": f"Description overlaps {round(j * 100)}% with '{b}'.",
                           "suggestion": SUGGESTIONS["high_overlap"]})

    errors = [i for i in issues if i["severity"] == "error"]
    warnings = [i for i in issues if i["severity"] == "warning"]
    return {
        "status": "errors" if errors else ("warnings" if warnings else "ok"),
        "skills_root": str(snap.root),
        "discovered_skill_files": snap.discovered,
        "valid_skills": len(snap.skills),
        "invalid_skills": snap.invalid_count,
        "duplicate_ids": snap.duplicates,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
    }
