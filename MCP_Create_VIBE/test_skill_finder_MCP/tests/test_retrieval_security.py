"""D/E. Retrieval and security."""
import os

import pytest

from skillfinder_mcp.core.errors import SkillError
from skillfinder_mcp.core.service import SkillService
from tests.conftest import REAL_ROOT, can_symlink, cfg_for, make_skill


def test_get_skill_returns_original_content(real_svc):
    r = real_svc.get_skill("test-plan-generator")
    raw = (REAL_ROOT / "02-test-planning/test-plan-generator/SKILL.md").read_bytes()
    assert r["content"] == raw.decode("utf-8-sig")  # byte-for-byte, line endings preserved
    assert r["path"] == "02-test-planning/test-plan-generator"
    assert {x["path"] for x in r["resources"]} >= {"references/test-plan-template.md", "scripts/fetch_jira.sh"}


def test_get_skill_by_name_variants(real_svc):
    assert real_svc.get_skill_details("Test Case Writer")["id"] == "test-case-writer"


def test_details_mark_inferred_fields(real_svc):
    d = real_svc.get_skill_details("rca-analyzer")
    assert d["category_source"] == "inferred" and d["tags_source"] == "inferred"
    assert "content" not in d and d["use_cases"]


def test_missing_and_ambiguous(real_svc):
    with pytest.raises(SkillError) as e:
        real_svc.get_skill("does-not-exist")
    assert e.value.code == "not_found"
    with pytest.raises(SkillError) as e:
        real_svc.get_skill("flaky")
    assert e.value.code == "ambiguous" and "pw-flaky-debugger" in e.value.details["candidates"]


def test_deleted_skill_after_index(tmp_root):
    svc = SkillService(cfg_for(tmp_root))
    (tmp_root / "02-design/api-checker/SKILL.md").unlink()
    with pytest.raises(SkillError, match="no longer exists"):
        svc.get_skill("api-checker")


def test_unicode_resource(tmp_svc):
    r = tmp_svc.get_skill_resources("pw-thing", "references/guide.md")
    assert "café ✓" in r["content"]


def test_scripts_are_listed_not_executed(tmp_svc, tmp_root):
    listing = tmp_svc.get_skill_resources("pw-thing")
    assert any(r["kind"] == "script" for r in listing["resources"])
    r = tmp_svc.get_skill_resources("pw-thing", "scripts/run.sh")
    assert r["content"].strip() == "echo should-never-run"  # returned as text only


@pytest.mark.parametrize("path", [
    "../../01-planning/plan-maker/SKILL.md", "..\\..\\x", "references/../../x",
    "/etc/passwd", "C:\\Windows\\win.ini", "\\\\server\\share\\x", "references/\x00.md",
])
def test_resource_path_traversal_rejected(tmp_svc, path):
    with pytest.raises(SkillError) as e:
        tmp_svc.get_skill_resources("pw-thing", path)
    assert e.value.code == "invalid_path"


@pytest.mark.parametrize("ident", ["../pw-thing", "pack/sample-pack/pw-thing", "C:\\x", "/abs", "a\\b", ".."])
def test_identifiers_cannot_be_paths(tmp_svc, ident):
    with pytest.raises(SkillError) as e:
        tmp_svc.get_skill(ident)
    assert e.value.code == "invalid_identifier"


def test_resource_must_belong_to_skill(tmp_svc):
    with pytest.raises(SkillError) as e:
        tmp_svc.get_skill_resources("pw-thing", "SKILL.md")
    assert e.value.code == "invalid_path"
    with pytest.raises(SkillError) as e:
        tmp_svc.get_skill_resources("plan-maker", "references/guide.md")
    assert e.value.code == "not_found"


def test_oversized_file_rejected(tmp_root):
    d = tmp_root / "pack/sample-pack/pw-thing/references"
    (d / "big.md").write_text("x" * 5000, encoding="utf-8")
    svc = SkillService(cfg_for(tmp_root, SKILLFINDER_MAX_FILE_BYTES="2048"))
    with pytest.raises(SkillError) as e:
        svc.get_skill_resources("pw-thing", "references/big.md")
    assert e.value.code == "too_large"


def test_oversized_skill_md_excluded(tmp_root):
    make_skill(tmp_root, "02-design/huge", body="\n## Workflow\n" + "y" * 5000)
    svc = SkillService(cfg_for(tmp_root, SKILLFINDER_MAX_FILE_BYTES="2048"))
    assert "huge" not in svc.snapshot.skills
    assert any(i["code"] == "too_large" for i in svc.validate_skills()["errors"])


def test_binary_resource_not_returned(tmp_root):
    (tmp_root / "pack/sample-pack/pw-thing/references/img.png").write_bytes(b"\x89PNG\x00\x00binary")
    svc = SkillService(cfg_for(tmp_root))
    with pytest.raises(SkillError) as e:
        svc.get_skill_resources("pw-thing", "references/img.png")
    assert e.value.code == "binary_file"


def test_symlinks_rejected(tmp_root, tmp_path):
    if not can_symlink(tmp_path):
        pytest.skip("OS does not allow creating symlinks for this user")
    outside = tmp_path / "secret.txt"
    outside.write_text("secret", encoding="utf-8")
    os.symlink(outside, tmp_root / "pack/sample-pack/pw-thing/references/link.md")
    os.symlink(tmp_path, tmp_root / "02-design/linkdir", target_is_directory=True)
    svc = SkillService(cfg_for(tmp_root))
    assert all(r["path"] != "references/link.md" for r in svc.snapshot.skills["pw-thing"].resources)
    with pytest.raises(SkillError) as e:
        svc.get_skill_resources("pw-thing", "references/link.md")
    assert e.value.code == "invalid_path"
    assert any(i["code"] == "symlink_skipped" for i in svc.snapshot.issues)


def test_shared_dir_is_opt_in_and_confined(tmp_root, tmp_path):
    shared = tmp_path / "shared"
    shared.mkdir()
    (shared / "common.md").write_text("shared text", encoding="utf-8")
    svc = SkillService(cfg_for(tmp_root))
    with pytest.raises(SkillError):
        svc.get_skill_resources("pw-thing", "@shared/common.md")
    svc2 = SkillService(cfg_for(tmp_root, SKILLFINDER_SHARED_DIR=str(shared)))
    assert svc2.get_skill_resources("pw-thing", "@shared/common.md")["content"] == "shared text"
    with pytest.raises(SkillError):
        svc2.get_skill_resources("pw-thing", "@shared/../skills/01-planning/plan-maker/SKILL.md")


def test_symlink_policy_simulated(tmp_root, monkeypatch):
    """Runs everywhere (incl. Windows without symlink privilege) by faking is_symlink."""
    from pathlib import Path
    link = tmp_root / "pack/sample-pack/pw-thing/references/guide.md"
    real = Path.is_symlink
    monkeypatch.setattr(Path, "is_symlink", lambda self: True if self == link else real(self))
    svc = SkillService(cfg_for(tmp_root))
    assert all(r["path"] != "references/guide.md" for r in svc.snapshot.skills["pw-thing"].resources)
    with pytest.raises(SkillError) as e:
        svc.get_skill_resources("pw-thing", "references/guide.md")
    assert e.value.code in ("invalid_path", "not_found")
    from skillfinder_mcp.core.safety import safe_join
    with pytest.raises(SkillError, match="Symbolic links"):
        safe_join(tmp_root, "pack/sample-pack/pw-thing/references/guide.md")
