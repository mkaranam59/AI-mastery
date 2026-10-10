"""A. Discovery and parsing (temporary skill trees)."""
import pytest

from skillfinder_mcp.core.errors import ConfigError
from skillfinder_mcp.core.service import SkillService
from tests.conftest import cfg_for, make_skill


def test_discovers_nested_skills_and_categories(tmp_svc):
    snap = tmp_svc.snapshot
    assert set(snap.skills) == {"plan-maker", "api-checker", "pw-thing"}
    assert snap.skills["plan-maker"].category == "Planning"
    assert snap.skills["pw-thing"].category == "Sample Pack"
    assert snap.skills["plan-maker"].category_source == "inferred"


def test_resources_discovered_relative_to_skill(tmp_svc):
    res = {r["path"]: r["kind"] for r in tmp_svc.snapshot.skills["pw-thing"].resources}
    assert res == {"references/guide.md": "document", "scripts/run.sh": "script"}


def test_empty_directory_reported(tmp_root):
    (tmp_root / "03-empty").mkdir()
    svc = SkillService(cfg_for(tmp_root))
    assert any(i["code"] == "empty_directory" for i in svc.snapshot.issues)


def test_empty_root_is_handled(tmp_path):
    root = tmp_path / "empty"
    root.mkdir()
    svc = SkillService(cfg_for(root))
    assert svc.list_skills()["total"] == 0
    assert svc.search_skills("anything")["total_matches"] == 0


def test_missing_root_is_config_error(tmp_path):
    with pytest.raises(ConfigError, match="does not exist"):
        cfg_for(tmp_path / "nope")


def test_malformed_frontmatter_does_not_crash(tmp_root):
    make_skill(tmp_root, "02-design/broken", frontmatter="---\nname: [unclosed\n---\n")
    svc = SkillService(cfg_for(tmp_root))
    assert "broken" not in svc.snapshot.skills
    errs = [i for i in svc.validate_skills()["errors"] if i["code"] == "invalid_frontmatter"]
    assert errs and errs[0]["path"] == "02-design/broken"
    assert len(svc.snapshot.skills) == 3  # others still indexed


def test_missing_frontmatter_falls_back_to_folder(tmp_root):
    make_skill(tmp_root, "02-design/no-front", frontmatter="")
    svc = SkillService(cfg_for(tmp_root))
    s = svc.snapshot.skills["no-front"]
    assert any(w["code"] == "missing_frontmatter" for w in s.warnings)


def test_empty_instructions_rejected(tmp_root):
    make_skill(tmp_root, "02-design/empty-body", body="\n# Title\n")
    svc = SkillService(cfg_for(tmp_root))
    assert "empty-body" not in svc.snapshot.skills
    assert any(i["code"] == "empty_instructions" for i in svc.validate_skills()["errors"])


def test_duplicate_ids_detected(tmp_root):
    make_skill(tmp_root, "02-design/plan-maker-copy", name="plan-maker")
    svc = SkillService(cfg_for(tmp_root))
    report = svc.validate_skills()
    assert "plan-maker" in report["duplicate_ids"]
    assert any(i["code"] == "duplicate_id" for i in report["errors"])
    assert svc.snapshot.skills["plan-maker"].rel_dir == "01-planning/plan-maker"  # first wins


def test_unreadable_file_reported(tmp_root, monkeypatch):
    from pathlib import Path
    target = tmp_root / "02-design" / "api-checker" / "SKILL.md"
    real = Path.read_bytes

    def fake(self):
        if self == target:
            raise PermissionError(13, "Permission denied")
        return real(self)
    monkeypatch.setattr(Path, "read_bytes", fake)
    svc = SkillService(cfg_for(tmp_root))
    assert "api-checker" not in svc.snapshot.skills
    assert any(i["code"] == "unreadable" for i in svc.validate_skills()["errors"])


def test_broken_reference_warning(tmp_root):
    body = "\n# X\n\n## Workflow\n1. Read `references/missing.md` and `references/guide.md` before you begin the work here.\n"
    d = make_skill(tmp_root, "02-design/refs", body=body)
    (d / "references").mkdir()
    (d / "references" / "guide.md").write_text("ok", encoding="utf-8")
    svc = SkillService(cfg_for(tmp_root))
    msgs = [w["message"] for w in svc.snapshot.skills["refs"].warnings if w["code"] == "broken_reference"]
    assert msgs == ["Referenced file 'references/missing.md' does not exist."]


def test_declared_tags_and_category_are_used(tmp_root):
    fm = "---\nname: tagged\ndescription: d\ncategory: Special\ntags: [alpha, Beta]\n---\n"
    make_skill(tmp_root, "02-design/tagged", frontmatter=fm)
    s = SkillService(cfg_for(tmp_root)).snapshot.skills["tagged"]
    assert (s.category, s.category_source, s.tags, s.tags_source) == ("Special", "declared", ["alpha", "beta"], "declared")
