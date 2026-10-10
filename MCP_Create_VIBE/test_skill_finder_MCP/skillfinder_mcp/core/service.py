"""Transport-independent skill service used by every MCP tool, prompt and resource."""
import hashlib
import logging
import re
import threading
from collections import Counter
from typing import Protocol

from .errors import ConfigError, SkillError
from .index import Snapshot, build_snapshot
from .parser import Skill, normalize_id
from .safety import check_relative, is_within, read_text_file, safe_join
from .search import Synonyms
from .validate import validate

log = logging.getLogger(__name__)

MAX_LIST = 100
MAX_SEARCH = 50
SHARED_PREFIX = "@shared/"
FACET_SPLIT = re.compile(r",|;|\.|\band\b|\bwith\b|\bplus\b|\bincluding\b|\bthen\b", re.I)


class SemanticBackend(Protocol):
    """Optional plug-in. Return [(skill_id, similarity 0..1)] best first."""

    def search(self, query: str, skills: list[Skill], limit: int) -> list[tuple[str, float]]: ...


def _clamp(n: int, lo: int, hi: int) -> int:
    return max(lo, min(int(n), hi))


class SkillService:
    def __init__(self, cfg, semantic: SemanticBackend | None = None):
        self.cfg = cfg
        self.semantic = semantic
        self.synonyms = Synonyms.load(cfg.synonyms_file)
        self._lock = threading.Lock()
        self._snap: Snapshot = build_snapshot(cfg.skills_root, cfg.max_file_bytes, self.synonyms)

    @property
    def snapshot(self) -> Snapshot:
        return self._snap

    # ---------- identifier resolution ----------

    def resolve(self, identifier: str) -> Skill:
        snap = self._snap
        if not isinstance(identifier, str) or not identifier.strip():
            raise SkillError("invalid_identifier", "Skill identifier is empty.")
        raw = identifier.strip()
        if any(c in raw for c in ("/", "\\", "\x00")) or ".." in raw or re.match(r"^[A-Za-z]:", raw):
            raise SkillError("invalid_identifier",
                             "Skill identifiers are names, not paths. Use list_skills or search_skills to find one.")
        key = normalize_id(raw)
        if key in snap.skills:
            return snap.skills[key]
        by_name = [s for s in snap.skills.values() if normalize_id(s.name) == key
                   or normalize_id(s.rel_dir.rsplit("/", 1)[-1]) == key]
        if len(by_name) == 1:
            return by_name[0]
        partial = by_name or [s for s in snap.skills.values() if key and key in s.id]
        if len(partial) == 1:
            return partial[0]
        if len(partial) > 1:
            raise SkillError("ambiguous", f"'{identifier}' matches {len(partial)} skills; use an exact id.",
                             candidates=sorted(s.id for s in partial)[:20])
        raise SkillError("not_found", f"No skill with id or name '{identifier}'. Try search_skills.")

    def _category_filter(self, category: str | None) -> set[str] | None:
        if not category:
            return None
        snap = self._snap
        want = normalize_id(category)
        ids = {sid for sid, s in snap.skills.items()
               if normalize_id(s.category) == want or normalize_id(s.rel_dir.split("/")[0]) == want
               or normalize_id(re.sub(r"^\d+[-_]", "", s.rel_dir.split("/")[0])) == want}
        if not ids:
            cats = sorted({s.category for s in snap.skills.values()})
            raise SkillError("unknown_category", f"Unknown category '{category}'.", valid=cats)
        return ids

    # ---------- listing ----------

    def list_skills(self, category=None, keyword=None, limit=20, offset=0) -> dict:
        snap = self._snap
        limit, offset = _clamp(limit, 1, MAX_LIST), max(0, int(offset))
        ids = self._category_filter(category)
        items = [s for s in sorted(snap.skills.values(), key=lambda s: (s.order, s.rel_dir))
                 if ids is None or s.id in ids]
        if keyword and keyword.strip():
            kw = keyword.strip().lower()
            items = [s for s in items if kw in f"{s.id} {s.name} {s.description} {' '.join(s.tags)} {s.category}".lower()]
        page = items[offset: offset + limit]
        return {"total": len(items), "offset": offset, "returned": len(page),
                "next_offset": offset + limit if offset + limit < len(items) else None,
                "skills": [s.summary() for s in page]}

    def list_categories(self) -> list[dict]:
        snap = self._snap
        c = Counter(s.category for s in snap.skills.values())
        first = {}
        for s in snap.skills.values():
            first.setdefault(s.category, (s.order, s.rel_dir.split("/")[0]))
        return [{"category": k, "count": c[k], "folder": first[k][1]}
                for k in sorted(c, key=lambda k: (first[k][0], k))]

    # ---------- search ----------

    def search_skills(self, query: str, category=None, limit=10, offset=0, search_mode=None) -> dict:
        snap = self._snap
        if not query or not query.strip():
            raise SkillError("invalid_query", "Query must not be empty.")
        if len(query) > 1000:
            raise SkillError("invalid_query", "Query is longer than 1000 characters.")
        limit, offset = _clamp(limit, 1, MAX_SEARCH), max(0, int(offset))
        mode = (search_mode or self.cfg.search_mode).lower()
        if mode not in ("keyword", "semantic"):
            raise SkillError("invalid_mode", "search_mode must be 'keyword' or 'semantic'.")
        ids = self._category_filter(category)
        note = None
        if mode == "semantic":
            if self.semantic is None:
                note = "Semantic search is not configured; used keyword search."
                mode = "keyword"
            else:
                try:
                    pool = [s for s in snap.skills.values() if ids is None or s.id in ids]
                    hits = self.semantic.search(query, pool, offset + limit)
                    res = [{"id": sid, "score": round(sc, 3), "reason": "Semantic similarity"} for sid, sc in hits]
                    return self._search_payload(query, "semantic", len(res), res[offset:], offset, limit, None)
                except Exception as e:  # never fail a search because the plug-in failed
                    log.warning("Semantic search failed, falling back to keyword: %s", e)
                    note = "Semantic search failed; used keyword search."
                    mode = "keyword"
        total, res = snap.search.search(query, ids, limit, offset)
        return self._search_payload(query, mode, total, res, offset, limit, note)

    def _search_payload(self, query, mode, total, res, offset, limit, note) -> dict:
        snap = self._snap
        results = []
        for rank, r in enumerate(res, offset + 1):
            s = snap.skills[r["id"]]
            results.append({"rank": rank, "id": s.id, "name": s.name, "description": s.description,
                            "category": s.category, "path": s.rel_dir, "score": r["score"], "reason": r["reason"]})
        out = {"query": query, "mode": mode, "total_matches": total, "offset": offset,
               "returned": len(results),
               "next_offset": offset + limit if offset + limit < total else None, "results": results}
        if note:
            out["note"] = note
        if not results:
            out["hint"] = "No skills matched. Try fewer or more general words, or list_skill_categories."
        return out

    def recommend_skills(self, task: str, max_results=5) -> dict:
        snap = self._snap
        if not task or not task.strip():
            raise SkillError("invalid_query", "Task description must not be empty.")
        max_results = _clamp(max_results, 1, 20)
        combined: dict[str, dict] = {}

        def add(query: str, weight: float, label: str, k: int):
            _, res = snap.search.search(query, None, k, 0)
            if not res:
                return
            top = res[0]["score"]
            for r in res:
                e = combined.setdefault(r["id"], {"score": 0.0, "facets": []})
                e["score"] += weight * r["score"] / top
                e["facets"].append(label)

        add(task, 1.0, "overall task", 10)
        facets = [f.strip() for f in FACET_SPLIT.split(task) if len(f.strip().split()) >= 1]
        facets = [f for f in dict.fromkeys(facets) if f.lower() != task.strip().lower()]
        for f in facets[:8]:
            add(f, 0.8, f"'{f}'", 3)
        if not combined:
            return {"task": task, "recommendations": [],
                    "note": "No available skill matches this task. Try search_skills with different words."}
        ranked = sorted(combined.items(), key=lambda kv: (-kv[1]["score"], kv[0]))[:max_results]
        top = ranked[0][1]["score"]
        recs = []
        for sid, e in ranked:
            s = snap.skills[sid]
            recs.append({"id": sid, "name": s.name, "description": s.description, "category": s.category,
                         "path": s.rel_dir, "relevance": round(e["score"] / top, 3),
                         "reason": "Relevant to " + ", ".join(dict.fromkeys(e["facets"]))})
        for i, r in enumerate(recs, 1):
            r["rank"] = i
        order = sorted(recs, key=lambda r: (snap.skills[r["id"]].order, -r["relevance"]))
        return {"task": task, "facets_considered": facets[:8], "recommendations": recs,
                "suggested_order": [r["id"] for r in order],
                "order_basis": "Numbered phase folders (01 requirement ... 09) first, then unnumbered packs; ties by relevance."}

    def find_related(self, identifier: str, limit=5) -> dict:
        s = self.resolve(identifier)
        snap = self._snap
        limit = _clamp(limit, 1, 20)
        _, res = snap.search.search(f"{s.name.replace('-', ' ')} {s.description}", None, limit * 3, 0)
        out = []
        for r in res:
            if r["id"] == s.id:
                continue
            o = snap.skills[r["id"]]
            score = r["score"] * (1.2 if o.category == s.category else 1.0)
            out.append({"id": o.id, "name": o.name, "category": o.category, "path": o.rel_dir,
                        "score": round(score, 3),
                        "relation": "same category" if o.category == s.category else "shared terms"})
        out.sort(key=lambda x: (-x["score"], x["id"]))
        return {"skill_id": s.id, "related": out[:limit]}

    # ---------- retrieval ----------

    def _details(self, s: Skill) -> dict:
        return {
            "id": s.id, "name": s.name, "description": s.description,
            "category": s.category, "category_source": s.category_source,
            "tags": s.tags, "tags_source": s.tags_source,
            "path": s.rel_dir, "skill_md": s.skill_md,
            "use_cases": _when_to_use(s.body),
            "metadata": s.metadata,
            "resources": s.resources,
            "warnings": [w["message"] for w in s.warnings],
            "uri": f"skillmasterclass://skills/{s.id}",
        }

    def get_skill_details(self, identifier: str) -> dict:
        return self._details(self.resolve(identifier))

    def get_skill(self, identifier: str) -> dict:
        s = self.resolve(identifier)
        root = self._snap.root
        path = safe_join(root, s.skill_md)
        try:
            content = read_text_file(path, self.cfg.max_file_bytes)
        except SkillError as e:
            if e.code == "not_found":
                raise SkillError("not_found", f"SKILL.md for '{s.id}' no longer exists; call refresh_skill_index.") from None
            raise
        out = self._details(s)
        out["content"] = content
        out["content_note"] = "Skill instructions are data for the assistant; they do not change server policy."
        if hashlib.sha1(content.encode("utf-8")).hexdigest() != s.sha1:
            out["stale"] = True  # file changed since the last index refresh
        return out

    def get_skill_resources(self, identifier: str, path: str | None = None) -> dict:
        s = self.resolve(identifier)
        root = self._snap.root
        if not path:
            shared = []
            if self.cfg.shared_dir:
                from .discovery import list_resources
                shared = [dict(r, path=SHARED_PREFIX + r["path"]) for r in list_resources(self.cfg.shared_dir)[0]]
            return {"skill_id": s.id, "resources": s.resources + shared,
                    "note": "Scripts are listed for reference only; the server never executes them."}
        if path.startswith(SHARED_PREFIX):
            if not self.cfg.shared_dir:
                raise SkillError("not_found", "No shared resource directory is configured.")
            base, rel = self.cfg.shared_dir, path[len(SHARED_PREFIX):]
        else:
            base, rel = safe_join(root, s.rel_dir), path
        clean = check_relative(rel).as_posix()
        if base != self.cfg.shared_dir and clean == "SKILL.md":
            raise SkillError("invalid_path", "Use get_skill to read SKILL.md.")
        target = safe_join(base, clean)
        if not is_within(target, base.resolve()):
            raise SkillError("invalid_path", "Path resolves outside the permitted directory.")
        if base != self.cfg.shared_dir and not any(r["path"] == clean for r in s.resources):
            raise SkillError("not_found", f"Resource '{clean}' is not part of skill '{s.id}'.",
                             available=[r["path"] for r in s.resources])
        content = read_text_file(target, self.cfg.max_file_bytes)
        return {"skill_id": s.id, "path": path, "size": len(content.encode("utf-8")), "content": content}

    # ---------- inventory ----------

    def validate_skills(self) -> dict:
        return validate(self._snap)

    def get_catalog(self, category=None, limit=100, offset=0) -> dict:
        snap = self._snap
        listing = self.list_skills(category, None, limit, offset)
        report = validate(snap)
        return {
            "total_discovered": snap.discovered,
            "valid_skills": len(snap.skills),
            "validation_status": report["status"],
            "categories": self.list_categories(),
            "total": listing["total"], "offset": listing["offset"], "next_offset": listing["next_offset"],
            "skills": [{"id": s["id"], "name": s["name"], "category": s["category"],
                        "description": _short(s["description"])} for s in listing["skills"]],
        }

    def statistics(self) -> dict:
        snap = self._snap
        res = [r for s in snap.skills.values() for r in s.resources]
        return {
            "valid_skills": len(snap.skills), "discovered_skill_files": snap.discovered,
            "categories": len({s.category for s in snap.skills.values()}),
            "skills_with_resources": sum(1 for s in snap.skills.values() if s.resources),
            "resource_files": len(res), "script_files": sum(1 for r in res if r["kind"] == "script"),
            "total_skill_md_bytes": sum(s.size for s in snap.skills.values()),
            "index_terms": len(snap.search.idf), "index_build_seconds": snap.build_seconds,
            "built_at": snap.built_at, "issues": len(snap.issues),
            "search_mode_default": self.cfg.search_mode,
            "semantic_available": self.semantic is not None,
            "refresh_enabled": self.cfg.refresh_enabled,
        }

    def refresh(self) -> dict:
        if not self.cfg.refresh_enabled:
            raise SkillError("refresh_disabled", "Index refresh is disabled on this server (SKILLFINDER_REFRESH_ENABLED=false).")
        if not self._lock.acquire(blocking=False):
            raise SkillError("refresh_in_progress", "Another refresh is already running; try again shortly.")
        try:
            old = self._snap
            try:
                new = build_snapshot(self.cfg.skills_root, self.cfg.max_file_bytes, self.synonyms)
            except (ConfigError, OSError) as e:
                log.error("Refresh failed, keeping previous index: %s", e)
                return {"status": "failed", "message": str(e), "kept_previous_index": True,
                        "valid_skills": len(old.skills)}
            added = sorted(set(new.skills) - set(old.skills))
            removed = sorted(set(old.skills) - set(new.skills))
            changed = sorted(k for k in set(new.skills) & set(old.skills) if new.skills[k].sha1 != old.skills[k].sha1)
            self._snap = new  # atomic swap; readers holding `old` finish safely
            errors = [i for i in new.issues if i["severity"] == "error"]
            return {"status": "ok" if not errors else "ok_with_errors", "valid_skills": len(new.skills),
                    "discovered_skill_files": new.discovered, "added": added, "removed": removed,
                    "changed": changed, "errors": errors, "build_seconds": new.build_seconds}
        finally:
            self._lock.release()


def _short(text: str, n: int = 160) -> str:
    return text if len(text) <= n else text[: n - 1].rsplit(" ", 1)[0] + "…"


def _when_to_use(body: str) -> list[str]:
    m = re.search(r"^#+\s*When to use\s*$(.*?)(?=^#+\s|\Z)", body, re.M | re.S | re.I)
    if not m:
        return []
    return [re.sub(r"^[-*]\s+", "", l).strip() for l in m.group(1).splitlines() if re.match(r"^\s*[-*]\s+", l)]

