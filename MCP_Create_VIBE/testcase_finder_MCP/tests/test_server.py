import json

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from tc_mcp.core.repository import PRIORITY_RANK
from tc_mcp.server import mcp

pytestmark = pytest.mark.asyncio


async def call(name, **args):
    async with Client(mcp) as c:
        return (await c.call_tool(name, args)).data


async def test_tool_surface():
    async with Client(mcp) as c:
        names = {t.name for t in await c.list_tools()}
    assert len(names) == 19 and "get_top_test_cases_for_module" in names


async def test_modules_sum_to_5000():
    mods = await call("list_modules")
    assert len(mods) == 17 and sum(m["count"] for m in mods) == 5000


async def test_top_sorted_no_deprecated():
    r = await call("get_top_test_cases_for_module", module="reports", limit=30)
    ranks = [PRIORITY_RANK[t["Priority"]] for t in r["test_cases"]]
    assert ranks == sorted(ranks, reverse=True)
    keys = [t["Issue Key"] for t in r["test_cases"] if t["Priority"] == r["test_cases"][0]["Priority"]]
    assert keys == sorted(keys)
    assert all(t["Component"] == "Reports" and t["Status"] != "Deprecated" for t in r["test_cases"])
    assert r["returned"] == 30 and r["total_matches"] > 30


async def test_status_ready_filter():
    r = await call("get_top_test_cases_for_module", module="Heatmaps", status="Ready", limit=50)
    assert {t["Status"] for t in r["test_cases"]} == {"Ready"}


async def test_min_priority_and_range():
    r = await call("get_top_test_cases_for_module", module="Heatmaps", min_priority="High", limit=100)
    assert {t["Priority"] for t in r["test_cases"]} <= {"High", "Highest"}
    r = await call("get_test_cases_by_priority_range", min_priority="Medium", max_priority="High", limit=100)
    assert {t["Priority"] for t in r["test_cases"]} <= {"Medium", "High"}


async def test_limit_clamped_to_100():
    r = await call("get_test_cases_by_priority", priority="Highest", limit=5000)
    assert r["returned"] == 100


async def test_get_case_and_bulk():
    r = await call("get_test_case", issue_key="vwo-1001")
    assert r["Issue Key"] == "VWO-1001" and len(r["Steps"]) == 4
    r = await call("get_test_cases_by_keys", keys=["VWO-1001", "vwo-1002", "NOPE-1"])
    assert r["returned"] == 2 and r["not_found"] == ["NOPE-1"]


async def test_filters_type_status_label_env_search():
    r = await call("get_test_cases_by_test_type", test_type="security", module="Reports", limit=100)
    assert {t["Test Type"] for t in r["test_cases"]} == {"Security"}
    r = await call("get_test_cases_by_status", status="Deprecated", limit=5)
    assert r["total_matches"] == 415
    r = await call("get_test_cases_by_label", label="regression", limit=5)
    assert r["total_matches"] > 0
    r = await call("get_test_cases_by_environment", browser="safari", device="ios", limit=20)
    assert all(t["Browser"].startswith("Safari") and "iOS" in t["Device"] for t in r["test_cases"])
    r = await call("search_test_cases", query="step drop-off", module="Funnels")
    assert r["total_matches"] > 0


async def test_related():
    r = await call("get_related_test_cases", issue_key="VWO-1002")
    assert r["feature"] == "step drop-off"
    assert all(t["Component"] == "Funnels" and t["Issue Key"] != "VWO-1002" for t in r["test_cases"])


async def test_discovery_and_stats():
    assert (await call("get_summary_stats", module="Surveys"))["total"] == 307
    assert (await call("get_data_info"))["rows"] == 5000
    assert [p["priority"] for p in await call("list_priorities")] == ["Highest", "High", "Medium", "Low"]
    assert (await call("list_browsers_devices"))["devices"]


async def test_errors():
    async with Client(mcp) as c:
        for name, args in [("get_test_case", {"issue_key": "NOPE"}),
                           ("get_top_test_cases_for_module", {"module": "Nope"}),
                           ("get_test_cases_by_priority", {"priority": "Urgent"}),
                           ("get_test_cases_by_priority_range",
                            {"min_priority": "Highest", "max_priority": "Low"})]:
            with pytest.raises(ToolError):
                await c.call_tool(name, args)


async def test_resources_and_prompt():
    async with Client(mcp) as c:
        mods = json.loads((await c.read_resource("vwo://modules"))[0].text)
        assert len(mods) == 17
        pr = json.loads((await c.read_resource("vwo://priorities"))[0].text)
        assert pr[0]["priority"] == "Highest"
        case = json.loads((await c.read_resource("vwo://case/VWO-1001"))[0].text)
        assert case["Issue Key"] == "VWO-1001"
        p = await c.get_prompt("top_cases_for_module", {"module": "Reports"})
        assert "get_top_test_cases_for_module" in p.messages[0].content.text
