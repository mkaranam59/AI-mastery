"""Recursive discovery of SKILL.md files and their supporting resources."""
import os
from dataclasses import dataclass, field
from pathlib import Path

SKILL_FILE = "SKILL.md"


@dataclass
class DiscoveryResult:
    skill_files: list[Path] = field(default_factory=list)
    issues: list[dict] = field(default_factory=list)  # problems found while walking


def discover_skill_files(root: Path) -> DiscoveryResult:
    """Walk root (no symlink following) and return every SKILL.md, sorted."""
    res = DiscoveryResult()
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        d = Path(dirpath)
        kept = []
        for name in sorted(dirnames):
            sub = d / name
            if name.startswith(".") or name == "__pycache__":
                continue
            if sub.is_symlink():
                res.issues.append({"severity": "warning", "code": "symlink_skipped",
                                   "path": _rel(sub, root),
                                   "message": "Symlinked directory skipped by policy."})
                continue
            kept.append(name)
        dirnames[:] = kept
        if SKILL_FILE in filenames:
            f = d / SKILL_FILE
            if f.is_symlink():
                res.issues.append({"severity": "error", "code": "symlink_skipped",
                                   "path": _rel(f, root),
                                   "message": "SKILL.md is a symbolic link; skipped by policy."})
            else:
                res.skill_files.append(f)
        elif d != root and not dirnames and not filenames:
            res.issues.append({"severity": "warning", "code": "empty_directory",
                               "path": _rel(d, root), "message": "Empty directory."})
    res.skill_files.sort(key=lambda p: _rel(p, root))
    return res


def list_resources(skill_dir: Path) -> tuple[list[dict], list[dict]]:
    """Files belonging to one skill, excluding SKILL.md and nested skills."""
    resources, issues = [], []
    for dirpath, dirnames, filenames in os.walk(skill_dir, followlinks=False):
        d = Path(dirpath)
        keep = []
        for name in sorted(dirnames):
            sub = d / name
            if name.startswith(".") or name == "__pycache__":
                continue
            if sub.is_symlink():
                issues.append({"severity": "warning", "code": "symlink_skipped",
                               "path": _rel(sub, skill_dir), "message": "Symlinked directory not exposed."})
                continue
            if (sub / SKILL_FILE).exists():
                continue  # a nested skill owns its own files
            keep.append(name)
        dirnames[:] = keep
        for name in sorted(filenames):
            f = d / name
            if d == skill_dir and name == SKILL_FILE:
                continue
            rel = _rel(f, skill_dir)
            if f.is_symlink():
                issues.append({"severity": "warning", "code": "symlink_skipped",
                               "path": rel, "message": "Symlinked file not exposed."})
                continue
            try:
                size = f.stat().st_size
            except OSError:
                issues.append({"severity": "warning", "code": "unreadable", "path": rel,
                               "message": "Resource could not be stat'ed."})
                continue
            resources.append({"path": rel, "size": size, "kind": _kind(name)})
    return resources, issues


def _kind(name: str) -> str:
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext in ("sh", "bash", "ps1", "py", "js", "ts", "bat", "cmd"):
        return "script"  # listed only; never executed by the server
    if ext in ("md", "txt", "rst"):
        return "document"
    if ext in ("json", "yaml", "yml", "toml", "ini", "cfg"):
        return "config"
    if ext in ("png", "jpg", "jpeg", "gif", "svg", "pdf", "zip"):
        return "binary"
    return "other"


def _rel(p: Path, base: Path) -> str:
    return p.relative_to(base).as_posix()
