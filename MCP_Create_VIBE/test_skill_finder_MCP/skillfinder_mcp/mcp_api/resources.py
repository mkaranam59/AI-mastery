"""MCP resources: catalog, per-skill content/metadata, supporting files.

Concrete per-skill resources come from a dynamic provider so resources/list
always reflects the current index (including after refresh). URI templates
cover clients that resolve URIs without listing first."""
import json
from collections.abc import Sequence

from fastmcp import FastMCP
from fastmcp.exceptions import ResourceError
from fastmcp.resources import FunctionResource
from fastmcp.server.providers import Provider

from ..core.errors import SkillError
from ..core.service import SkillService

SCHEME = "skillmasterclass"
CATALOG_URI = f"{SCHEME}://catalog"


def _call(fn, *a):
    try:
        return fn(*a)
    except SkillError as e:
        raise ResourceError(str(e)) from None


class SkillResourceProvider(Provider):
    """Lists one content and one metadata resource per indexed skill."""

    def __init__(self, svc: SkillService):
        super().__init__()
        self.svc = svc

    async def _list_resources(self) -> Sequence[FunctionResource]:
        out = []
        for sid, s in sorted(self.svc.snapshot.skills.items()):
            out.append(FunctionResource.from_function(
                (lambda sid=sid: _call(self.svc.get_skill, sid)["content"]),
                uri=f"{SCHEME}://skills/{sid}", name=f"skill-{sid}", title=s.name,
                description=s.description[:300], mime_type="text/markdown"))
            out.append(FunctionResource.from_function(
                (lambda sid=sid: json.dumps(_call(self.svc.get_skill_details, sid), indent=2)),
                uri=f"{SCHEME}://skills/{sid}/meta", name=f"skill-{sid}-meta",
                title=f"{s.name} (metadata)", mime_type="application/json"))
        return out


def register_resources(mcp: FastMCP, svc: SkillService) -> None:
    mcp.add_provider(SkillResourceProvider(svc))

    @mcp.resource(CATALOG_URI, name="skill-catalog", mime_type="application/json")
    def catalog() -> str:
        """Compact catalog of all skills with ids, categories and short descriptions."""
        return json.dumps(_call(svc.get_catalog, None, 100, 0), indent=2)

    @mcp.resource(f"{SCHEME}://skills/{{skill_id}}", name="skill-content", mime_type="text/markdown")
    def skill_content(skill_id: str) -> str:
        """Full SKILL.md content of one skill."""
        return _call(svc.get_skill, skill_id)["content"]

    @mcp.resource(f"{SCHEME}://skills/{{skill_id}}/meta", name="skill-metadata", mime_type="application/json")
    def skill_meta(skill_id: str) -> str:
        """Structured metadata of one skill."""
        return json.dumps(_call(svc.get_skill_details, skill_id), indent=2)

    @mcp.resource(f"{SCHEME}://skills/{{skill_id}}/files/{{path*}}", name="skill-file", mime_type="text/plain")
    def skill_file(skill_id: str, path: str) -> str:
        """A supporting text file of one skill, by relative path."""
        return _call(svc.get_skill_resources, skill_id, path)["content"]
