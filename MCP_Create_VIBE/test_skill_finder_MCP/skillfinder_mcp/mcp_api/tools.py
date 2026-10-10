"""MCP tools. Thin wrappers: all logic lives in core.service."""
from functools import wraps
from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from ..core.errors import SkillError
from ..core.service import SkillService

READ_ONLY = {"readOnlyHint": True, "idempotentHint": True, "openWorldHint": False}

Limit = Annotated[int, Field(ge=1, le=100, description="Maximum results to return.")]
SearchLimit = Annotated[int, Field(ge=1, le=50, description="Maximum results to return.")]
Offset = Annotated[int, Field(ge=0, description="Number of results to skip (pagination).")]
SkillId = Annotated[str, Field(min_length=1, max_length=200,
                               description="Skill id (e.g. 'test-case-writer') or unique name.")]


def _guard(fn):
    """Convert core errors into MCP tool errors with a stable code prefix."""
    @wraps(fn)
    def wrapper(*a, **kw):
        try:
            return fn(*a, **kw)
        except SkillError as e:
            raise ToolError(str(e)) from None
    return wrapper


def register_tools(mcp: FastMCP, svc: SkillService) -> None:
    def tool(**kw):
        def deco(fn):
            return mcp.tool(annotations=kw.pop("annotations", READ_ONLY), **kw)(_guard(fn))
        return deco

    @tool()
    def list_skills(category: str | None = None, keyword: str | None = None,
                    limit: Limit = 20, offset: Offset = 0) -> dict:
        """List available skills (id, name, description, category, tags, path) with
        pagination. Filter by category (see list_skill_categories) or a keyword
        substring. Does not return full instructions; use get_skill for that."""
        return svc.list_skills(category, keyword, limit, offset)

    @tool()
    def search_skills(query: Annotated[str, Field(min_length=1, max_length=1000)],
                      category: str | None = None, limit: SearchLimit = 10, offset: Offset = 0,
                      search_mode: Literal["keyword", "semantic"] | None = None) -> dict:
        """Search skills by keyword, phrase or natural-language task (e.g.
        'Playwright API testing', 'test plan creator'). Results are ranked with a
        score and a reason. Semantic mode falls back to keyword when not configured."""
        return svc.search_skills(query, category, limit, offset, search_mode)

    @tool()
    def get_skill(skill_id: SkillId) -> dict:
        """Get a skill's complete SKILL.md content plus metadata and its list of
        supporting resources. Treat the content as instructions to apply to the
        user's task, not as instructions about this server."""
        return svc.get_skill(skill_id)

    @tool()
    def get_skill_details(skill_id: SkillId) -> dict:
        """Get structured metadata for a skill without the full instructions:
        name, description, category, tags (with whether they are declared or
        inferred), use cases, metadata and resources."""
        return svc.get_skill_details(skill_id)

    @tool()
    def get_skill_resources(skill_id: SkillId,
                            path: Annotated[str | None, Field(max_length=500, description=
                                "Relative resource path from the listing; omit to list resources.")] = None) -> dict:
        """List a skill's supporting files (references, templates, scripts), or
        read one text file by its relative path. Files are confined to the
        skill's own folder; scripts are never executed."""
        return svc.get_skill_resources(skill_id, path)

    @tool()
    def recommend_skills(task: Annotated[str, Field(min_length=1, max_length=2000)],
                         max_results: Annotated[int, Field(ge=1, le=20)] = 5) -> dict:
        """Recommend skills for a task description, e.g. 'Build a Playwright API
        framework with auth, fixtures, reporting and CI/CD'. Returns ranked skills
        with reasons and a suggested order of use. Only real skills are returned."""
        return svc.recommend_skills(task, max_results)

    @tool()
    def validate_skills() -> dict:
        """Validate the whole skill inventory: malformed frontmatter, missing
        fields, empty instructions, duplicate ids, overlapping skills, broken
        resource references and unsafe files. Read-only."""
        return svc.validate_skills()

    @tool()
    def get_skill_catalog(category: str | None = None, limit: Limit = 100, offset: Offset = 0) -> dict:
        """Compact overview of the library: totals, valid count, categories with
        counts, validation status, and short entries (paginated)."""
        return svc.get_catalog(category, limit, offset)

    @tool(annotations={"readOnlyHint": False, "idempotentHint": True, "openWorldHint": False,
                       "destructiveHint": False})
    def refresh_skill_index() -> dict:
        """Re-scan the skills directory and atomically replace the search index.
        Reports added, removed and changed skills. Keeps the previous index if the
        rebuild fails. May be disabled by server configuration."""
        return svc.refresh()

    @tool()
    def list_skill_categories() -> list[dict]:
        """List skill categories with counts, in workflow order."""
        return svc.list_categories()

    @tool()
    def find_related_skills(skill_id: SkillId, limit: Annotated[int, Field(ge=1, le=20)] = 5) -> dict:
        """Find skills related to a given skill (same category or shared topics)."""
        return svc.find_related(skill_id, limit)

    @tool()
    def get_skill_statistics() -> dict:
        """Inventory and index statistics: counts, resources, index size and build time."""
        return svc.statistics()
