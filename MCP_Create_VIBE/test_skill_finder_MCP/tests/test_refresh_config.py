"""G. Index refresh, plus configuration validation."""
import shutil
import threading

import pytest

from skillfinder_mcp.config import load_config
from skillfinder_mcp.core.errors import ConfigError, SkillError
from skillfinder_mcp.core.service import SkillService
from tests.conftest import cfg_for, make_skill


def test_refresh_add_modify_remove(tmp_root):
    svc = SkillService(cfg_for(tmp_root))
    assert svc.search_skills("quantum")["total_matches"] == 0
    make_skill(tmp_root, "02-design/quantum-tester", desc="Test quantum widgets.")
    (tmp_root / "01-planning/plan-maker/SKILL.md").write_text(
        "---\nname: plan-maker\ndescription: Changed description about release calendars.\n---\n"
        + "\n## Workflow\n1. Do the planning work in clear, ordered steps with review.\n2. Then review it.\n",
        encoding="utf-8")
    shutil.rmtree(tmp_root / "02-design/api-checker")
    r = svc.refresh()
    assert (r["added"], r["removed"], r["changed"]) == (["quantum-tester"], ["api-checker"], ["plan-maker"])
    assert svc.search_skills("quantum")["results"][0]["id"] == "quantum-tester"
    assert "calendars" in svc.get_skill_details("plan-maker")["description"]
    with pytest.raises(SkillError):
        svc.get_skill("api-checker")


def test_refresh_with_partially_invalid_inventory(tmp_root):
    svc = SkillService(cfg_for(tmp_root))
    make_skill(tmp_root, "02-design/bad", frontmatter="---\nname: [x\n---\n")
    r = svc.refresh()
    assert r["status"] == "ok_with_errors" and len(svc.snapshot.skills) == 3


def test_refresh_failure_keeps_last_index(tmp_path):
    root = tmp_path / "skills"
    make_skill(root, "01-a/one")
    svc = SkillService(cfg_for(root))
    shutil.rmtree(root)
    r = svc.refresh()
    assert r["status"] == "failed" and r["kept_previous_index"]
    assert "one" in svc.snapshot.skills


def test_refresh_disabled(tmp_root):
    svc = SkillService(cfg_for(tmp_root, SKILLFINDER_REFRESH_ENABLED="false"))
    with pytest.raises(SkillError) as e:
        svc.refresh()
    assert e.value.code == "refresh_disabled"


def test_concurrent_refresh_is_rejected(tmp_root):
    svc = SkillService(cfg_for(tmp_root))
    svc._lock.acquire()
    try:
        with pytest.raises(SkillError) as e:
            svc.refresh()
        assert e.value.code == "refresh_in_progress"
    finally:
        svc._lock.release()


def test_readers_see_complete_snapshots_during_refresh(tmp_root):
    svc = SkillService(cfg_for(tmp_root))
    errors = []

    def reader():
        for _ in range(200):
            n = svc.list_skills()["total"]
            if n not in (3, 4):
                errors.append(n)
    t = threading.Thread(target=reader)
    t.start()
    make_skill(tmp_root, "02-design/new-one")
    for _ in range(5):
        svc.refresh()
    t.join()
    assert not errors


@pytest.mark.parametrize("env,msg", [
    ({"SKILLFINDER_TRANSPORT": "carrier-pigeon"}, "SKILLFINDER_TRANSPORT"),
    ({"SKILLFINDER_PORT": "70000"}, "SKILLFINDER_PORT"),
    ({"SKILLFINDER_SEARCH_MODE": "magic"}, "SKILLFINDER_SEARCH_MODE"),
    ({"SKILLFINDER_TRANSPORT": "http"}, "requires SKILLFINDER_AUTH_TOKEN"),
    ({"SKILLFINDER_TRANSPORT": "http", "SKILLFINDER_AUTH_TOKEN": "short"}, "at least 16"),
    ({"SKILLFINDER_TRANSPORT": "http", "SKILLFINDER_AUTH_TOKEN": "x" * 20, "SKILLFINDER_HOST": "0.0.0.0"}, "non-loopback"),
    ({"SKILLFINDER_REFRESH_ENABLED": "maybe"}, "true or false"),
    ({"SKILLFINDER_HTTP_PATH": "mcp"}, "start with"),
])
def test_config_validation(env, msg):
    with pytest.raises(ConfigError, match=msg):
        load_config(env)


def test_config_defaults_do_not_depend_on_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = load_config({})
    assert cfg.skills_root.name == "skillmasterclass" and cfg.skills_root.is_dir()
    assert cfg.host == "127.0.0.1" and cfg.transport == "stdio"
