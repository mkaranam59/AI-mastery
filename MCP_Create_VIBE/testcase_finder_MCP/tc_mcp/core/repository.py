"""Read-only, in-memory access to the test-case CSV."""
import csv
import os
import re
from collections import Counter
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_CSV_CANDIDATES = (
    PROJECT_DIR / "data" / "vwo_5000_test_cases.csv",
    PROJECT_DIR.parent / "data" / "vwo_5000_test_cases.csv",
)

PRIORITY_RANK = {"Highest": 4, "High": 3, "Medium": 2, "Low": 1}
PRIORITIES_DESC = sorted(PRIORITY_RANK, key=PRIORITY_RANK.get, reverse=True)

_FEATURE_RE = re.compile(r"Navigate to the (.+?) screen", re.I)


def resolve_csv_path() -> Path:
    env = os.environ.get("TC_MCP_CSV")
    if env:
        return Path(env)
    for p in DEFAULT_CSV_CANDIDATES:
        if p.exists():
            return p
    raise FileNotFoundError(
        "CSV not found. Set TC_MCP_CSV or put vwo_5000_test_cases.csv in "
        f"{DEFAULT_CSV_CANDIDATES[0].parent}"
    )


class Repository:
    def __init__(self, path: Path | None = None):
        self.path = Path(path) if path else resolve_csv_path()
        with open(self.path, encoding="utf-8-sig", newline="") as f:
            self.rows: list[dict] = list(csv.DictReader(f))
        for r in self.rows:
            m = _FEATURE_RE.search(r["Steps"])
            r["_feature"] = m.group(1).lower() if m else ""
            r["_rank"] = PRIORITY_RANK[r["Priority"]]
        self.by_key = {r["Issue Key"]: r for r in self.rows}

    def values(self, field: str) -> list[str]:
        return sorted({r[field] for r in self.rows})

    def counts(self, field: str) -> Counter:
        return Counter(r[field] for r in self.rows)
