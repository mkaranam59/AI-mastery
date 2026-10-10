import os
import socket
from pathlib import Path

import pytest

from skillfinder_mcp.config import DEFAULT_SKILLS_ROOT, load_config
from skillfinder_mcp.core.service import SkillService
from skillfinder_mcp.server import create_server

BODY = """
# {title}

## When to use
- Use it when you need {title}.

## Workflow
1. Read the input carefully and confirm scope.
2. Apply the method step by step and record assumptions.
3. Stop for human review.
"""


def make_skill(root: Path, rel: str, name: str | None = None, desc: str = "A test skill.",
               body: str | None = None, frontmatter: str | None = None) -> Path:
    d = root / rel
    d.mkdir(parents=True, exist_ok=True)
    name = name if name is not None else rel.rsplit("/", 1)[-1]
    if frontmatter is None:
        frontmatter = f"---\nname: {name}\ndescription: {desc}\n---\n"
    (d / "SKILL.md").write_text(frontmatter + (body or BODY.format(title=name)), encoding="utf-8")
    return d


@pytest.fixture
def tmp_root(tmp_path):
    root = tmp_path / "skills"
    root.mkdir()
    make_skill(root, "01-planning/plan-maker", desc="Create a test plan from a ticket.")
    make_skill(root, "02-design/api-checker", desc="Design REST API tests.")
    d = make_skill(root, "pack/sample-pack/pw-thing", desc="Playwright thing.")
    (d / "references").mkdir()
    (d / "references" / "guide.md").write_text("# Guide\nUnicode: café ✓", encoding="utf-8")
    (d / "scripts").mkdir()
    (d / "scripts" / "run.sh").write_text("echo should-never-run\n", encoding="utf-8")
    return root


def cfg_for(root: Path, **over):
    env = {"SKILLMASTERCLASS_ROOT": str(root)}
    env.update(over)
    return load_config(env)


@pytest.fixture
def tmp_svc(tmp_root):
    return SkillService(cfg_for(tmp_root))


@pytest.fixture(scope="session")
def real_cfg():
    return load_config({})


@pytest.fixture(scope="session")
def real_svc(real_cfg):
    return SkillService(real_cfg)


@pytest.fixture(scope="session")
def real_mcp(real_cfg, real_svc):
    return create_server(real_cfg, real_svc)


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def can_symlink(tmp_path: Path) -> bool:
    try:
        os.symlink(tmp_path, tmp_path / "_probe_link", target_is_directory=True)
        (tmp_path / "_probe_link").unlink()
        return True
    except (OSError, NotImplementedError):
        return False


REAL_ROOT = DEFAULT_SKILLS_ROOT
