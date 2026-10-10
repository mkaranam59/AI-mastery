"""Parse a SKILL.md into metadata + body without altering its content."""
import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .discovery import list_resources
from .errors import SkillError
from .safety import read_text_file

FRONTMATTER_RE = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.S)
REF_RE = re.compile(r"[`(]((?:\./)?[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]*[A-Za-z0-9_-]\.[A-Za-z0-9]+)[`)]")
MIN_BODY_CHARS = 80
STOP_TAG = {"and", "the", "for", "pack", "skill", "skills", "of", "a", "to"}


def normalize_id(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")


def humanize_folder(name: str) -> str:
    """'03-test-design' -> 'Test Design'; 'playwright-pack' -> 'Playwright Pack'."""
    name = re.sub(r"^\d+[-_ ]*", "", name)
    words = [w.upper() if len(w) <= 2 else w.capitalize() for w in re.split(r"[-_ ]+", name) if w]
    return " ".join(words) or "Uncategorized"  # short words are acronyms: ai -> AI


def phase_order(rel_dir: str) -> int:
    """Numeric folder prefix (e.g. '05-') used to order recommendations; 99 if none."""
    m = re.match(r"(\d+)[-_]", rel_dir)
    return int(m.group(1)) if m else 99


@dataclass
class Skill:
    id: str
    name: str
    description: str
    category: str
    category_source: str            # "declared" | "inferred"
    tags: list[str]
    tags_source: str                # "declared" | "inferred"
    rel_dir: str                    # skill directory relative to root (posix)
    skill_md: str                   # SKILL.md path relative to root
    metadata: dict                  # all frontmatter keys except name/description
    body: str                       # markdown after frontmatter (original text)
    resources: list[dict]
    warnings: list[dict] = field(default_factory=list)
    order: int = 99
    sha1: str = ""
    size: int = 0

    def summary(self) -> dict:
        return {"id": self.id, "name": self.name, "description": self.description,
                "category": self.category, "tags": self.tags, "path": self.rel_dir}


def parse_skill(skill_md: Path, root: Path, max_bytes: int) -> Skill:
    """Raise SkillError for fatal problems; collect recoverable ones as warnings."""
    rel_dir = skill_md.parent.relative_to(root).as_posix()
    text = read_text_file(skill_md, max_bytes)
    warnings: list[dict] = []

    meta: dict = {}
    body = text
    m = FRONTMATTER_RE.match(text)
    if m:
        try:
            loaded = yaml.safe_load(m.group(1))
        except yaml.YAMLError as e:
            raise SkillError("invalid_frontmatter", f"YAML frontmatter could not be parsed: {e}".splitlines()[0])
        if loaded is None:
            loaded = {}
        if not isinstance(loaded, dict):
            raise SkillError("invalid_frontmatter", "Frontmatter must be a YAML mapping.")
        meta = loaded
        body = text[m.end():]
    else:
        warnings.append(_w("missing_frontmatter", "No YAML frontmatter; name derived from folder."))

    folder = skill_md.parent.name if rel_dir != "." else root.name
    raw_name = meta.get("name")
    if not raw_name or not isinstance(raw_name, str):
        warnings.append(_w("missing_name", "Frontmatter 'name' missing; using folder name."))
        raw_name = folder
    elif normalize_id(raw_name) != normalize_id(folder):
        warnings.append(_w("name_folder_mismatch", f"name '{raw_name}' differs from folder '{folder}'."))
    sid = normalize_id(raw_name)
    if not sid:
        raise SkillError("invalid_name", "Skill name normalizes to an empty identifier.")

    desc = meta.get("description")
    if not isinstance(desc, str) or not desc.strip():
        warnings.append(_w("missing_description", "Frontmatter 'description' missing or empty."))
        desc = ""
    desc = " ".join(desc.split())

    if len(body.strip()) < MIN_BODY_CHARS:
        raise SkillError("empty_instructions", f"Instructions are empty or shorter than {MIN_BODY_CHARS} characters.")

    parent = Path(rel_dir).parent.name if "/" in rel_dir else ""
    if isinstance(meta.get("category"), str) and meta["category"].strip():
        category, category_source = meta["category"].strip(), "declared"
    else:
        category, category_source = (humanize_folder(parent) if parent else "Uncategorized"), "inferred"

    tags_raw = meta.get("tags")
    if isinstance(tags_raw, str):
        tags_raw = [t for t in re.split(r"[,\s]+", tags_raw) if t]
    if isinstance(tags_raw, list) and tags_raw:
        tags = sorted({str(t).strip().lower() for t in tags_raw if str(t).strip()})
        tags_source = "declared"
    else:
        words = re.split(r"[-_ ]+", sid) + re.split(r"[-_ ]+", normalize_id(category))
        tags = sorted({w for w in words if len(w) > 1 and w not in STOP_TAG})
        tags_source = "inferred"

    skill_dir = skill_md.parent
    resources, res_issues = list_resources(skill_dir)
    warnings += res_issues
    existing = {r["path"] for r in resources}
    for ref in sorted(set(REF_RE.findall(body))):
        ref_clean = ref[2:] if ref.startswith("./") else ref
        if ref_clean.startswith((".", "~")) or "//" in ref_clean:
            continue
        top = ref_clean.split("/", 1)[0]
        # Only judge references that point into this skill's own sub-folders.
        if (skill_dir / top).is_dir() and ref_clean not in existing:
            warnings.append(_w("broken_reference", f"Referenced file '{ref_clean}' does not exist."))

    metadata = {k: v for k, v in meta.items() if k not in ("name", "description")}
    return Skill(
        id=sid, name=raw_name.strip(), description=desc,
        category=category, category_source=category_source,
        tags=tags, tags_source=tags_source,
        rel_dir=rel_dir, skill_md=skill_md.relative_to(root).as_posix(),
        metadata=_jsonable(metadata), body=body, resources=resources, warnings=warnings,
        order=phase_order(rel_dir), sha1=hashlib.sha1(text.encode("utf-8")).hexdigest(),
        size=len(text.encode("utf-8")),
    )


def _w(code: str, message: str) -> dict:
    return {"severity": "warning", "code": code, "message": message}


def _jsonable(v):
    if isinstance(v, dict):
        return {str(k): _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    return str(v)  # dates etc.
