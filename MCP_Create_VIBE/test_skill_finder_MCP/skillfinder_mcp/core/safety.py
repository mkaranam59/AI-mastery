"""Filesystem boundary: every user-influenced path goes through here."""
import os
from pathlib import Path, PurePosixPath, PureWindowsPath

from .errors import SkillError


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def check_relative(rel: str) -> PurePosixPath:
    """Validate a client-supplied relative path without touching the disk."""
    if not rel or not rel.strip():
        raise SkillError("invalid_path", "Path is empty.")
    if "\x00" in rel:
        raise SkillError("invalid_path", "Path contains a null byte.")
    norm = rel.replace("\\", "/")
    if norm.startswith("/") or PureWindowsPath(rel).drive or PureWindowsPath(rel).is_absolute():
        raise SkillError("invalid_path", "Absolute paths are not allowed.")
    parts = PurePosixPath(norm).parts
    if any(p == ".." for p in parts):
        raise SkillError("invalid_path", "Parent-directory segments ('..') are not allowed.")
    return PurePosixPath(*[p for p in parts if p not in ("", ".")])


def safe_join(base: Path, rel: str) -> Path:
    """Resolve rel under base, rejecting traversal and any symlink on the way."""
    clean = check_relative(rel)
    current = base
    for part in clean.parts:
        current = current / part
        if current.is_symlink():
            raise SkillError("invalid_path", "Symbolic links are not allowed.", path=str(clean))
    resolved = Path(os.path.realpath(current))
    if not is_within(resolved, Path(os.path.realpath(base))):
        raise SkillError("invalid_path", "Path resolves outside the permitted directory.")
    return resolved


def read_text_file(path: Path, max_bytes: int) -> str:
    """Read a UTF-8 text file with a size cap. Never executes anything."""
    if not path.exists():
        raise SkillError("not_found", "File does not exist.")
    if not path.is_file():
        raise SkillError("invalid_path", "Not a regular file.")
    size = path.stat().st_size
    if size > max_bytes:
        raise SkillError("too_large", f"File is {size} bytes; limit is {max_bytes}.")
    try:
        data = path.read_bytes()
    except OSError as e:
        raise SkillError("unreadable", f"File could not be read: {e.strerror}.") from None
    if b"\x00" in data[:8192]:
        raise SkillError("binary_file", "File appears to be binary and is not returned.")
    try:
        return data.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise SkillError("binary_file", "File is not valid UTF-8 text and is not returned.") from None
