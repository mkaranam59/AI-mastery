"""Immutable index snapshot built from the skills root."""
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path

from .discovery import discover_skill_files
from .errors import ConfigError, SkillError
from .parser import Skill, parse_skill
from .search import SearchIndex, Synonyms

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Snapshot:
    root: Path
    skills: dict[str, Skill]                      # valid, indexed skills by id
    issues: list[dict] = field(default_factory=list)  # inventory-level errors/warnings
    discovered: int = 0
    duplicates: dict[str, list[str]] = field(default_factory=dict)
    search: SearchIndex | None = None
    built_at: float = 0.0
    build_seconds: float = 0.0

    @property
    def invalid_count(self) -> int:
        return len({i["path"] for i in self.issues if i["severity"] == "error" and i.get("path")})


def build_snapshot(root: Path, max_file_bytes: int, synonyms: Synonyms) -> Snapshot:
    """Build a full snapshot. Raises ConfigError only if the root itself is unusable."""
    t0 = time.perf_counter()
    if not root.is_dir():
        raise ConfigError(f"Skills root is missing or not a directory: {root}")
    disc = discover_skill_files(root)
    issues = list(disc.issues)
    skills: dict[str, Skill] = {}
    seen_paths: dict[str, list[str]] = {}

    for f in disc.skill_files:
        rel = f.parent.relative_to(root).as_posix()
        try:
            s = parse_skill(f, root, max_file_bytes)
        except SkillError as e:
            issues.append({"severity": "error", "code": e.code, "path": rel, "message": e.message})
            continue
        except Exception as e:  # unexpected parse failure must not stop the server
            log.exception("Unexpected error parsing %s", f)
            issues.append({"severity": "error", "code": "parse_failed", "path": rel, "message": str(e)})
            continue
        seen_paths.setdefault(s.id, []).append(rel)
        for w in s.warnings:
            issues.append({**w, "skill_id": s.id, "path": rel + ("/" + w["path"] if w.get("path") else "")})
        if s.id in skills:
            issues.append({"severity": "error", "code": "duplicate_id", "skill_id": s.id, "path": rel,
                           "message": f"Duplicate id '{s.id}'; already defined at {skills[s.id].rel_dir}. Excluded."})
            continue
        skills[s.id] = s

    duplicates = {k: v for k, v in seen_paths.items() if len(v) > 1}
    search = SearchIndex(list(skills.values()), synonyms)
    snap = Snapshot(root=root, skills=skills, issues=issues, discovered=len(disc.skill_files),
                    duplicates=duplicates, search=search, built_at=time.time(),
                    build_seconds=round(time.perf_counter() - t0, 4))
    log.info("Indexed %d skills (%d discovered, %d issues) in %.3fs",
             len(skills), snap.discovered, len(issues), snap.build_seconds)
    return snap
