"""MCP prompts: generic workflows that route through the discovery tools.
They contain no skill text and name no specific skills."""
from fastmcp import FastMCP

RULES = """
How to work:
1. Restate the objective and constraints in one or two lines.
2. Call `search_skills` (or `recommend_skills` for multi-part work) with {search_hint}.
3. Pick the best match(es) from the results and call `get_skill` for each one you use.
4. If a skill lists supporting resources you need, read them with `get_skill_resources`.
5. Apply the retrieved instructions to the inputs below, including any review gates they define.
6. List missing information and assumptions explicitly.
Never invent a skill, resource or result that the tools did not return. If no skill fits, say so and proceed with clearly labelled general guidance.
"""


def _p(goal: str, search_hint: str, inputs: dict[str, str | None]) -> str:
    lines = [f"Goal: {goal}", RULES.format(search_hint=search_hint).strip(), "", "Inputs:"]
    for k, v in inputs.items():
        lines.append(f"- {k}: {v if v else '(not provided - ask or state an assumption)'}")
    return "\n".join(lines)


def register_prompts(mcp: FastMCP) -> None:
    @mcp.prompt
    def find_skill_for_task(task: str) -> str:
        """Find and apply the most suitable skill for any task."""
        return _p("Find the right skill(s) for this task and apply them.",
                  "the task description", {"task": task})

    @mcp.prompt
    def generate_test_cases(requirement: str, scope: str | None = None) -> str:
        """Generate test cases from a requirement, story or ticket."""
        return _p("Produce executable test cases (positive, negative, boundary) for the requirement.",
                  "queries such as 'test case writer' and 'test scenario design'",
                  {"requirement": requirement, "scope": scope})

    @mcp.prompt
    def create_test_plan(feature_or_ticket: str, constraints: str | None = None) -> str:
        """Create a test plan for a feature, release or ticket."""
        return _p("Create a review-ready test plan.", "'test plan creator'",
                  {"feature_or_ticket": feature_or_ticket, "constraints": constraints})

    @mcp.prompt
    def create_test_strategy(product_context: str, constraints: str | None = None) -> str:
        """Create a product or organization test strategy."""
        return _p("Create a test strategy (levels, types, automation, environments, gates).",
                  "'test strategy' and, if relevant, 'risk based testing'",
                  {"product_context": product_context, "constraints": constraints})

    @mcp.prompt
    def design_playwright_tests(feature: str, existing_setup: str | None = None) -> str:
        """Design Playwright UI tests for a feature."""
        return _p("Design maintainable Playwright UI tests for the feature.",
                  "'Playwright' plus the specific need (e.g. page objects, fixtures, locators)",
                  {"feature": feature, "existing_setup": existing_setup})

    @mcp.prompt
    def design_playwright_api_tests(api_description: str, auth: str | None = None) -> str:
        """Design Playwright API tests for endpoints."""
        return _p("Design Playwright API tests covering success, error, auth and contract checks.",
                  "'Playwright API testing' and 'API contract testing'",
                  {"api_description": api_description, "auth": auth})

    @mcp.prompt
    def review_test_automation_framework(framework_summary: str, code_or_repo: str | None = None) -> str:
        """Review an automation framework or test code."""
        return _p("Review the automation framework and code; report findings by severity with fixes.",
                  "'test automation code review' and 'automation framework'",
                  {"framework_summary": framework_summary, "code_or_repo": code_or_repo})

    @mcp.prompt
    def analyze_defect(defect_description: str, evidence: str | None = None) -> str:
        """Analyze and triage a defect, then write it up."""
        return _p("Triage the defect (severity, priority, owner) and produce a clear bug report.",
                  "'bug triage' and 'bug report'",
                  {"defect_description": defect_description, "evidence": evidence})

    @mcp.prompt
    def perform_root_cause_analysis(incident: str, timeline_or_logs: str | None = None) -> str:
        """Root cause analysis of a production defect or incident."""
        return _p("Find the root cause, contributing factors and preventive actions.",
                  "'root cause analysis production defect'",
                  {"incident": incident, "timeline_or_logs": timeline_or_logs})

    @mcp.prompt
    def analyze_test_coverage(requirements: str, tests: str | None = None) -> str:
        """Analyze coverage of requirements by tests and list gaps."""
        return _p("Measure coverage and list uncovered requirements and orphan tests.",
                  "'test coverage' and 'traceability matrix'",
                  {"requirements": requirements, "tests": tests})

    @mcp.prompt
    def evaluate_llm_application(application: str, quality_goals: str | None = None) -> str:
        """Plan an evaluation of an LLM, RAG or agent application."""
        return _p("Design an evaluation (datasets, metrics, safety checks) for the AI application.",
                  "'LLM evaluation', 'RAG testing' or 'AI agent testing' as fits",
                  {"application": application, "quality_goals": quality_goals})

    @mcp.prompt
    def review_test_results(results: str, release_context: str | None = None) -> str:
        """Review execution results and summarize readiness."""
        return _p("Summarize results, failures, risks and a readiness recommendation.",
                  "'test execution report' and 'release readiness'",
                  {"results": results, "release_context": release_context})
