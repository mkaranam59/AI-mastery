"""Validation, filtering, ranking and formatting. No MCP imports."""
from .repository import PRIORITY_RANK, PRIORITIES_DESC, Repository

DEFAULT_LIMIT = 10
MAX_LIMIT = 100
COMPACT_FIELDS = ("Issue Key", "Summary", "Priority", "Component", "Test Type",
                  "Status", "Browser", "Device")


class QueryError(ValueError):
    """User-facing validation error."""


def match_enum(value: str, options: list[str], label: str) -> str:
    for o in options:
        if o.lower() == value.strip().lower():
            return o
    raise QueryError(f"Unknown {label} '{value}'. Valid values: {', '.join(options)}")


def clamp_limit(limit: int) -> int:
    return max(1, min(int(limit), MAX_LIMIT))


def compact(r: dict) -> dict:
    return {k: r[k] for k in COMPACT_FIELDS}


def full(r: dict) -> dict:
    out = {k: v for k, v in r.items() if not k.startswith("_")}
    out["Steps"] = [s.strip() for s in r["Steps"].split(" | ")]
    return out


def find(repo: Repository, *, module=None, min_priority=None, max_priority=None,
         test_type=None, status=None, label=None, browser=None, device=None,
         query=None, keys=None, exclude_key=None, feature=None,
         include_deprecated=False, limit=DEFAULT_LIMIT) -> dict:
    """Filter -> rank (priority desc, key asc) -> cut to limit."""
    if module:
        module = match_enum(module, repo.values("Component"), "module")
    lo = PRIORITY_RANK[match_enum(min_priority, PRIORITIES_DESC, "priority")] if min_priority else 1
    hi = PRIORITY_RANK[match_enum(max_priority, PRIORITIES_DESC, "priority")] if max_priority else 4
    if lo > hi:
        raise QueryError("min_priority must not be higher than max_priority.")
    if test_type:
        test_type = match_enum(test_type, repo.values("Test Type"), "test_type")
    if status:
        status = match_enum(status, repo.values("Status"), "status")
    label = label and label.strip().lower()
    browser = browser and browser.strip().lower()
    device = device and device.strip().lower()
    query = query and query.strip().lower()
    keyset = {k.strip().upper() for k in keys} if keys is not None else None

    rows = []
    for r in repo.rows:
        if keyset is not None and r["Issue Key"] not in keyset:
            continue
        if exclude_key and r["Issue Key"] == exclude_key:
            continue
        if module and r["Component"] != module:
            continue
        if not lo <= r["_rank"] <= hi:
            continue
        if test_type and r["Test Type"] != test_type:
            continue
        if status:
            if r["Status"] != status:
                continue
        elif r["Status"] == "Deprecated" and not include_deprecated:
            continue
        if label and label not in r["Labels"].lower().split():
            continue
        if browser and browser not in r["Browser"].lower():
            continue
        if device and device not in r["Device"].lower():
            continue
        if feature is not None and r["_feature"] != feature:
            continue
        if query and query not in f'{r["Summary"]} {r["Description"]} {r["Labels"]}'.lower():
            continue
        rows.append(r)

    rows.sort(key=lambda r: (-r["_rank"], r["Issue Key"]))
    n = clamp_limit(limit)
    return {"total_matches": len(rows), "returned": min(n, len(rows)),
            "test_cases": [compact(r) for r in rows[:n]]}


def named_counts(repo: Repository, field: str, key: str) -> list[dict]:
    c = repo.counts(field)
    return [{key: v, "count": c[v]} for v in sorted(c)]


def priority_counts(repo: Repository) -> list[dict]:
    c = repo.counts("Priority")
    return [{"priority": p, "rank": PRIORITY_RANK[p], "count": c[p]} for p in PRIORITIES_DESC]


def summary_stats(repo: Repository, module: str | None) -> dict:
    if module:
        module = match_enum(module, repo.values("Component"), "module")
    rows = [r for r in repo.rows if not module or r["Component"] == module]
    from collections import Counter
    return {
        "module": module or "ALL",
        "total": len(rows),
        "by_priority": {p: n for p, n in ((p, Counter(r["Priority"] for r in rows)[p]) for p in PRIORITIES_DESC)},
        "by_test_type": dict(Counter(r["Test Type"] for r in rows)),
        "by_status": dict(Counter(r["Status"] for r in rows)),
    }
