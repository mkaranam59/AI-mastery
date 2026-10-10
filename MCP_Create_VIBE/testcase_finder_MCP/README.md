# TestCase Finder MCP (TC MCP) – phase 1

Read-only FastMCP server over `../data/vwo_5000_test_cases.csv`. "Module" = the `Component` column. Ranking is pure priority: Highest > High > Medium > Low, then Issue Key. Deprecated cases are hidden unless asked for. `limit` defaults to 10, max 100.

## Install
```
pip install -r requirements.txt
```

## Connect
Claude Code:
```
claude mcp add testcase-finder -- python -m tc_mcp.server
```
(run from this folder, or use `claude mcp add testcase-finder --scope user -e PYTHONPATH=<this folder> -- python -m tc_mcp.server`)

Claude Desktop / any `mcpServers` JSON:
```json
{
  "mcpServers": {
    "testcase-finder": {
      "command": "python",
      "args": ["-m", "tc_mcp.server"],
      "cwd": "C:\\Users\\ADMIN\\AIMastery\\MCP_Create_VIBE\\testcase_finder_MCP"
    }
  }
}
```
Inspector: `fastmcp dev tc_mcp/server.py`. Override the CSV with env var `TC_MCP_CSV`.

## Tools (19)
Discovery: `list_modules`, `list_priorities`, `list_test_types`, `list_statuses`, `list_browsers_devices`, `get_data_info`, `get_summary_stats`
Retrieval: `get_test_case`, `get_test_cases_by_keys`, `get_test_cases_by_priority`, `get_test_cases_by_priority_range`, `get_test_cases_by_module`, `get_test_cases_by_test_type`, `get_test_cases_by_status`, `get_test_cases_by_label`, `get_test_cases_by_environment`, `search_test_cases`, `get_related_test_cases`
Headline: `get_top_test_cases_for_module`

Resources: `vwo://modules`, `vwo://priorities`, `vwo://case/{issue_key}`. Prompt: `top_cases_for_module`.

## Test
```
pip install pytest pytest-asyncio
pytest
```
