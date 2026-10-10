"""B/C. Inventory acceptance and search accuracy against the REAL library."""
import re

import pytest

from tests.conftest import REAL_ROOT


def test_at_least_50_valid_skills(real_svc):
    report = real_svc.validate_skills()
    assert report["valid_skills"] >= 50
    assert report["error_count"] == 0, report["errors"]
    assert report["duplicate_ids"] == {}


def test_each_skill_maps_to_its_own_skill_md(real_svc):
    files = sorted(p.parent.relative_to(REAL_ROOT).as_posix() for p in REAL_ROOT.rglob("SKILL.md"))
    assert sorted(s.rel_dir for s in real_svc.snapshot.skills.values()) == files
    for s in real_svc.snapshot.skills.values():
        assert s.skill_md == f"{s.rel_dir}/SKILL.md"
        assert s.id == s.rel_dir.rsplit("/", 1)[-1]


def test_no_placeholder_skills(real_svc):
    for s in real_svc.snapshot.skills.values():
        assert len(s.description) >= 60, s.id
        assert len(s.body) >= 800, s.id
        # Placeholder-only lines; skills may legitimately *mention* TODO markers.
        assert not re.search(r"lorem ipsum|^\s*[-*]?\s*(TODO|TBD|placeholder)\.?\s*$", s.body, re.I | re.M), s.id
        assert re.search(r"^#+ .*(workflow|steps|how|process|checklist|procedure)", s.body, re.I | re.M), s.id


def top(svc, q, n=5, **kw):
    return [r["id"] for r in svc.search_skills(q, limit=n, **kw)["results"]]


@pytest.mark.parametrize("query,expected,within", [
    ("Playwright API testing", "pw-api-tester", 1),
    ("test case creator", "test-case-writer", 1),
    ("test plan creator", "test-plan-generator", 1),
    ("test strategy", "test-strategy-creator", 1),
    ("generate login test cases", "test-case-writer", 5),
    ("analyze production defects", "rca-analyzer", 3),
    ("analyze production defects", "defect-trend-analyzer", 3),
    ("create an automation framework", "se-framework-scaffolder", 3),
    ("root cause analysis", "rca-analyzer", 1),
    ("flaky tests", "pw-flaky-debugger", 3),
    ("wcag", "accessibility-test-designer", 3),
    ("RAG", "rag-application-tester", 1),
])
def test_expected_skill_ranked(real_svc, query, expected, within):
    assert expected in top(real_svc, query, within), top(real_svc, query, 5)


def test_playwright_returns_playwright_skills(real_svc):
    res = top(real_svc, "Playwright", 10)
    assert len(res) == 10 and all(r.startswith("pw-") for r in res)


def test_exact_name_and_case_insensitive(real_svc):
    assert top(real_svc, "test-case-writer", 1) == ["test-case-writer"]
    assert top(real_svc, "PLAYWRIGHT API TESTING", 1) == top(real_svc, "playwright api testing", 1)


def test_partial_keyword(real_svc):
    assert "pw-accessibility-auditor" in top(real_svc, "accessib playwright", 3)


def test_description_and_content_matching(real_svc):
    # 'getByTestId' never appears in a skill name, only in descriptions/bodies
    expected = {p.parent.name for p in REAL_ROOT.rglob("SKILL.md")
                if "getbytestid" in p.read_text(encoding="utf-8").lower()}
    res = real_svc.search_skills("getByTestId", limit=50)["results"]
    assert expected and {r["id"] for r in res} == expected
    assert all("body" in r["reason"] or "description" in r["reason"] for r in res)


def test_category_filter(real_svc):
    res = real_svc.search_skills("test", category="Test Planning", limit=50)["results"]
    assert res and {r["category"] for r in res} == {"Test Planning"}
    with pytest.raises(Exception, match="unknown_category"):
        real_svc.search_skills("test", category="Nope")


def test_ranking_and_reasons(real_svc):
    res = real_svc.search_skills("Playwright API testing", limit=10)["results"]
    scores = [r["score"] for r in res]
    assert scores == sorted(scores, reverse=True)
    assert all(r["reason"] for r in res) and [r["rank"] for r in res] == list(range(1, 11))


def test_pagination(real_svc):
    p1 = real_svc.search_skills("test", limit=5)
    p2 = real_svc.search_skills("test", limit=5, offset=5)
    assert p1["next_offset"] == 5 and p2["results"][0]["rank"] == 6
    assert not set(r["id"] for r in p1["results"]) & set(r["id"] for r in p2["results"])
    lst = real_svc.list_skills(limit=10, offset=50)
    assert lst["returned"] == lst["total"] - 50 and lst["next_offset"] is None


def test_empty_results(real_svc):
    r = real_svc.search_skills("zzqxv nonexistentword")
    assert r["total_matches"] == 0 and "hint" in r


def test_semantic_mode_falls_back(real_svc):
    r = real_svc.search_skills("test strategy", search_mode="semantic")
    assert r["mode"] == "keyword" and "not configured" in r["note"]


def test_recommend_framework_task(real_svc):
    task = ("Build an end-to-end Playwright API automation framework with authentication, "
            "reusable fixtures, reporting, and CI/CD integration.")
    r = real_svc.recommend_skills(task, 8)
    ids = [x["id"] for x in r["recommendations"]]
    for expected in ("pw-fixture-designer", "ci-cd-test-integrator", "pw-api-tester"):
        assert expected in ids
    assert set(r["suggested_order"]) == set(ids)
    assert all(i in real_svc.snapshot.skills for i in ids)


def test_find_related(real_svc):
    r = real_svc.find_related("pw-flaky-debugger", 5)
    ids = [x["id"] for x in r["related"]]
    assert "pw-flaky-debugger" not in ids and "se-flaky-debugger" in ids
