"""F. Real MCP protocol interactions (in-memory client)."""
import json

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from skillfinder_mcp.server import create_server
from tests.conftest import cfg_for, make_skill


TOOLS = {"list_skills", "search_skills", "get_skill", "get_skill_details", "get_skill_resources",
         "recommend_skills", "validate_skills", "get_skill_catalog", "refresh_skill_index",
         "list_skill_categories", "find_related_skills", "get_skill_statistics"}
PROMPTS = {"find_skill_for_task", "generate_test_cases", "create_test_plan", "create_test_strategy",
           "design_playwright_tests", "design_playwright_api_tests", "review_test_automation_framework",
           "analyze_defect", "perform_root_cause_analysis", "analyze_test_coverage",
           "evaluate_llm_application", "review_test_results"}


async def test_lists_tools_prompts_resources(real_mcp):
    async with Client(real_mcp) as c:
        assert {t.name for t in await c.list_tools()} == TOOLS
        assert {p.name for p in await c.list_prompts()} == PROMPTS
        uris = {str(r.uri) for r in await c.list_resources()}
        n = len(real_mcp.skill_service.snapshot.skills)
        assert "skillmasterclass://catalog" in uris and len(uris) == 1 + 2 * n
        assert "skillmasterclass://skills/test-case-writer" in uris
        tmpl = {t.uri_template for t in await c.list_resource_templates()}
        assert "skillmasterclass://skills/{skill_id}/files/{path*}" in tmpl


async def test_tool_calls(real_mcp):
    async with Client(real_mcp) as c:
        r = await c.call_tool("search_skills", {"query": "test plan creator", "limit": 3})
        assert r.data["results"][0]["id"] == "test-plan-generator"
        r = await c.call_tool("get_skill", {"skill_id": "test-plan-generator"})
        assert r.data["content"].replace("\r\n", "\n").startswith("---\nname: test-plan-generator")
        r = await c.call_tool("get_skill_catalog", {"category": "Test Closure"})
        assert r.data["total"] == 4 and r.data["valid_skills"] >= 50
        r = await c.call_tool("validate_skills", {})
        assert r.data["status"] in ("ok", "warnings")
        r = await c.call_tool("recommend_skills", {"task": "analyze a production defect", "max_results": 3})
        assert "rca-analyzer" in [x["id"] for x in r.data["recommendations"]]
        r = await c.call_tool("get_skill_statistics", {})
        assert r.data["script_files"] == 1


async def test_tool_input_validation_and_errors(real_mcp):
    async with Client(real_mcp) as c:
        with pytest.raises(ToolError):
            await c.call_tool("search_skills", {"query": ""})
        with pytest.raises(ToolError):
            await c.call_tool("list_skills", {"limit": 0})
        with pytest.raises(ToolError):
            await c.call_tool("search_skills", {"query": "x", "search_mode": "telepathy"})
        with pytest.raises(ToolError, match="not_found"):
            await c.call_tool("get_skill", {"skill_id": "nope-nope"})
        with pytest.raises(ToolError, match="invalid_path"):
            await c.call_tool("get_skill_resources", {"skill_id": "test-plan-generator", "path": "../../README.md"})
        with pytest.raises(ToolError):
            await c.call_tool("no_such_tool", {})


async def test_prompts(real_mcp):
    async with Client(real_mcp) as c:
        p = await c.get_prompt("design_playwright_api_tests", {"api_description": "GET /users/{id}"})
        text = p.messages[0].content.text
        assert "search_skills" in text and "get_skill" in text and "GET /users/{id}" in text
        p = await c.get_prompt("create_test_plan", {"feature_or_ticket": "KAN-7"})
        assert "(not provided" in p.messages[0].content.text


async def test_resources(real_mcp):
    async with Client(real_mcp) as c:
        cat = json.loads((await c.read_resource("skillmasterclass://catalog"))[0].text)
        assert cat["valid_skills"] >= 50
        md = (await c.read_resource("skillmasterclass://skills/rca-analyzer"))[0].text
        assert "name: rca-analyzer" in md
        meta = json.loads((await c.read_resource("skillmasterclass://skills/rca-analyzer/meta"))[0].text)
        assert meta["id"] == "rca-analyzer"
        f = (await c.read_resource(
            "skillmasterclass://skills/test-plan-generator/files/references/test-plan-template.md"))[0].text
        assert "Test Plan" in f
        with pytest.raises(Exception):
            await c.read_resource("skillmasterclass://skills/not-a-skill")


async def test_resources_follow_refresh(tmp_root):
    mcp = create_server(cfg_for(tmp_root))
    async with Client(mcp) as c:
        before = {str(r.uri) for r in await c.list_resources()}
        make_skill(tmp_root, "02-design/late-arrival")
        r = await c.call_tool("refresh_skill_index", {})
        assert r.data["added"] == ["late-arrival"]
        after = {str(r.uri) for r in await c.list_resources()}
        assert after - before == {"skillmasterclass://skills/late-arrival",
                                  "skillmasterclass://skills/late-arrival/meta"}
