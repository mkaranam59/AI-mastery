"""TC MCP: read-only FastMCP server over the VWO test-case CSV (phase 1).

Run:  python -m tc_mcp.server      (stdio)
"""
import json
import time
from functools import wraps

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from .core import query as q
from .core.repository import PRIORITIES_DESC, Repository

_t0 = time.perf_counter()
repo = Repository()
LOAD_SECONDS = round(time.perf_counter() - _t0, 3)

L = q.DEFAULT_LIMIT

mcp = FastMCP(
    "testcase-finder",
    instructions=(
        "Read-only access to the VWO test-case library (CSV). A 'module' is the "
        "Component column (see list_modules). Priority order: Highest > High > "
        "Medium > Low. Results are always ranked by priority, then Issue Key. "
        "Deprecated cases are hidden unless include_deprecated=true or "
        "status='Deprecated'. limit defaults to 10 (max 100). Use "
        "get_top_test_cases_for_module to find what to execute first."
    ),
)


def tool(fn):
    """Register as an MCP tool, turning validation errors into ToolErrors."""
    @wraps(fn)
    def wrapper(*a, **kw):
        try:
            return fn(*a, **kw)
        except q.QueryError as e:
            raise ToolError(str(e)) from None
    return mcp.tool(wrapper)


# ---------------- A. Discovery ----------------

@tool
def list_modules() -> list[dict]:
    """List all modules (Component values) with test-case counts."""
    return q.named_counts(repo, "Component", "module")


@tool
def list_priorities() -> list[dict]:
    """List priorities from most to least important, with rank and counts."""
    return q.priority_counts(repo)


@tool
def list_test_types() -> list[dict]:
    """List test types (Functional, Security, Boundary...) with counts."""
    return q.named_counts(repo, "Test Type", "test_type")


@tool
def list_statuses() -> list[dict]:
    """List statuses (Ready, Automated, Draft, Deprecated) with counts."""
    return q.named_counts(repo, "Status", "status")


@tool
def list_browsers_devices() -> dict:
    """List browsers and devices with counts."""
    return {"browsers": q.named_counts(repo, "Browser", "browser"),
            "devices": q.named_counts(repo, "Device", "device")}


@tool
def get_data_info() -> dict:
    """Diagnostics: CSV path, row count, load time and columns."""
    return {"csv_path": str(repo.path), "rows": len(repo.rows),
            "load_seconds": LOAD_SECONDS,
            "columns": [c for c in repo.rows[0] if not c.startswith("_")],
            "read_only": True}


@tool
def get_summary_stats(module: str | None = None) -> dict:
    """Counts by priority, test type and status for one module (or all)."""
    return q.summary_stats(repo, module)


# ---------------- B. Retrieval ----------------

@tool
def get_test_case(issue_key: str) -> dict:
    """Get one test case in full (e.g. 'VWO-1001'), with steps as a list."""
    r = repo.by_key.get(issue_key.strip().upper())
    if not r:
        raise ToolError(f"No test case with key '{issue_key}'.")
    return q.full(r)


@tool
def get_test_cases_by_keys(keys: list[str]) -> dict:
    """Bulk fetch compact records for a list of issue keys (max 100).
    Includes Deprecated cases; unknown keys are reported in `not_found`."""
    keys = [k.strip().upper() for k in keys][: q.MAX_LIMIT]
    res = q.find(repo, keys=keys, include_deprecated=True, limit=q.MAX_LIMIT)
    found = {t["Issue Key"] for t in res["test_cases"]}
    res["not_found"] = [k for k in keys if k not in found]
    return res


@tool
def get_test_cases_by_priority(priority: str, limit: int = L, status: str | None = None,
                               include_deprecated: bool = False) -> dict:
    """Test cases with exactly this priority (Highest/High/Medium/Low)."""
    return q.find(repo, min_priority=priority, max_priority=priority, status=status,
                  include_deprecated=include_deprecated, limit=limit)


@tool
def get_test_cases_by_priority_range(min_priority: str, max_priority: str = "Highest",
                                     module: str | None = None, limit: int = L,
                                     status: str | None = None,
                                     include_deprecated: bool = False) -> dict:
    """Test cases whose priority is between min_priority and max_priority
    (inclusive), e.g. Medium..Highest, optionally within a module."""
    return q.find(repo, module=module, min_priority=min_priority,
                  max_priority=max_priority, status=status,
                  include_deprecated=include_deprecated, limit=limit)


@tool
def get_test_cases_by_module(module: str, limit: int = L, priority: str | None = None,
                             test_type: str | None = None, status: str | None = None,
                             include_deprecated: bool = False) -> dict:
    """Test cases in a module, highest priority first. Optionally narrow by
    exact priority, test_type or status."""
    return q.find(repo, module=module, min_priority=priority, max_priority=priority,
                  test_type=test_type, status=status,
                  include_deprecated=include_deprecated, limit=limit)


@tool
def get_test_cases_by_test_type(test_type: str, module: str | None = None, limit: int = L,
                                min_priority: str | None = None,
                                status: str | None = None) -> dict:
    """Test cases of one test type (e.g. Security), optionally in a module."""
    return q.find(repo, test_type=test_type, module=module, min_priority=min_priority,
                  status=status, limit=limit)


@tool
def get_test_cases_by_status(status: str, module: str | None = None,
                             limit: int = L, min_priority: str | None = None) -> dict:
    """Test cases with a given status (Ready/Automated/Draft/Deprecated)."""
    return q.find(repo, status=status, module=module, min_priority=min_priority, limit=limit)


@tool
def get_test_cases_by_label(label: str, module: str | None = None, limit: int = L,
                            min_priority: str | None = None) -> dict:
    """Test cases carrying a label, e.g. 'regression'."""
    return q.find(repo, label=label, module=module, min_priority=min_priority, limit=limit)


@tool
def get_test_cases_by_environment(browser: str | None = None, device: str | None = None,
                                  module: str | None = None, limit: int = L,
                                  min_priority: str | None = None) -> dict:
    """Test cases for a browser and/or device (substring match, e.g. 'safari',
    'iOS')."""
    return q.find(repo, browser=browser, device=device, module=module,
                  min_priority=min_priority, limit=limit)


@tool
def search_test_cases(query: str, module: str | None = None, limit: int = L,
                      min_priority: str | None = None) -> dict:
    """Keyword search over summary, description and labels."""
    return q.find(repo, query=query, module=module, min_priority=min_priority, limit=limit)


@tool
def get_related_test_cases(issue_key: str, limit: int = L) -> dict:
    """Other cases for the same module and feature as the given case (its
    siblings across test types, browsers and devices)."""
    r = repo.by_key.get(issue_key.strip().upper())
    if not r:
        raise ToolError(f"No test case with key '{issue_key}'.")
    if not r["_feature"]:
        return {"total_matches": 0, "returned": 0, "test_cases": []}
    res = q.find(repo, module=r["Component"], feature=r["_feature"],
                 exclude_key=r["Issue Key"], limit=limit)
    res["feature"] = r["_feature"]
    return res


# ---------------- C. Headline ----------------

@tool
def get_top_test_cases_for_module(module: str, limit: int = L, min_priority: str = "Low",
                                  status: str | None = None, test_type: str | None = None,
                                  browser: str | None = None,
                                  device: str | None = None) -> dict:
    """Top-N test cases to execute for a module, in pure priority order
    (Highest, High, Medium, Low, then Issue Key). Deprecated are excluded.
    Use status='Ready' for cases ready for manual execution. browser/device
    are substring filters."""
    return q.find(repo, module=module, min_priority=min_priority, status=status,
                  test_type=test_type, browser=browser, device=device, limit=limit)


# ---------------- Resources ----------------

@mcp.resource("vwo://modules", mime_type="application/json")
def modules_resource() -> str:
    """All modules with counts."""
    return json.dumps(q.named_counts(repo, "Component", "module"))


@mcp.resource("vwo://priorities", mime_type="application/json")
def priorities_resource() -> str:
    """Priorities in rank order with counts."""
    return json.dumps(q.priority_counts(repo))


@mcp.resource("vwo://case/{issue_key}", mime_type="application/json")
def case_resource(issue_key: str) -> str:
    """One full test case."""
    r = repo.by_key.get(issue_key.strip().upper())
    if not r:
        raise ValueError(f"No test case with key '{issue_key}'.")
    return json.dumps(q.full(r))


# ---------------- Prompt ----------------

@mcp.prompt
def top_cases_for_module(module: str, limit: int = L) -> str:
    """Ask for the top test cases to execute for a module."""
    return (
        f"Call get_top_test_cases_for_module with module='{module}' and "
        f"limit={limit}. Present the results as a table (key, priority, test "
        "type, status, summary) in the order returned, which is pure priority "
        "order. State total_matches so I know how many more exist. Do not "
        "re-rank or rebalance the list."
    )


def main():
    mcp.run()


if __name__ == "__main__":
    main()
