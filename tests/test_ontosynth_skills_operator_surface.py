import json
import pathlib
import urllib.request

from tests._pytest_port import BASE
from tests.conftest import requires_agent_modules

pytestmark = requires_agent_modules


def _get(path: str):
    req = urllib.request.Request(BASE + path)
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read()), resp.status


def test_ontosynth_skills_overview_endpoint_exposes_three_layers():
    payload, status = _get("/api/ontosynth/skills/overview")

    assert status == 200
    assert payload["project_key"] == "knowledge_governance_console"
    assert payload["scope_active"] is True
    assert "platform_catalog" in payload
    assert "project_contract" in payload
    assert "runtime_materialized" in payload

    contract = payload["project_contract"]
    assert contract["role_count"] >= 1
    developer = next(
        role for role in contract["roles"] if role["runtime_identity"] == "developer"
    )
    assert "developer-role-entrypoint" in developer["session_preloaded_skill_keys"]
    assert "developer-governed-materialization" in developer["managed_skill_keys"]
    assert developer["managed_skill_count"] >= 3

    runtime = payload["runtime_materialized"]
    assert runtime["profile_count"] >= 1
    developer_runtime = next(
        role for role in runtime["profiles"] if role["runtime_identity"] == "developer"
    )
    assert developer_runtime["profile_key"].startswith("os-")
    assert "developer-role-entrypoint" in developer_runtime["materialized_skill_names"]
    assert developer_runtime["materialized_skill_count"] >= 1
    assert developer_runtime["contract_managed_only_skill_count"] >= 1

    platform = payload["platform_catalog"]
    assert "skill_count" in platform
    assert "source_roots" in platform


def test_ontosynth_skills_overview_separates_contract_from_materialized_counts():
    payload, _status = _get("/api/ontosynth/skills/overview")

    developer_contract = next(
        role
        for role in payload["project_contract"]["roles"]
        if role["runtime_identity"] == "developer"
    )
    developer_runtime = next(
        role
        for role in payload["runtime_materialized"]["profiles"]
        if role["runtime_identity"] == "developer"
    )

    assert developer_contract["managed_skill_count"] > 1
    assert (
        developer_contract["managed_skill_count"]
        > developer_runtime["materialized_skill_count"]
    )


def test_ontosynth_skills_overview_includes_managed_skill_details_and_reference_content():
    payload, status = _get("/api/ontosynth/skills/overview")

    assert status == 200
    developer_contract = next(
        role
        for role in payload["project_contract"]["roles"]
        if role["runtime_identity"] == "developer"
    )
    managed_skills = developer_contract["managed_skills"]
    grounding = next(
        skill for skill in managed_skills if skill["skill_key"] == "developer-codebase-grounding"
    )
    assert grounding["title"] == "Codebase Grounding"
    assert grounding["references"]
    reference = grounding["references"][0]
    assert reference["path"] == "references/developer-grounding-and-implementation.md"
    assert "Keep developer work file-grounded" in reference["content"]


def test_ontosynth_skills_overview_includes_preloaded_runtime_skill_detail_and_linked_files():
    payload, status = _get("/api/ontosynth/skills/overview")

    assert status == 200
    developer_runtime = next(
        role
        for role in payload["runtime_materialized"]["profiles"]
        if role["runtime_identity"] == "developer"
    )
    preloaded_details = developer_runtime["preloaded_skill_details"]
    entrypoint = next(
        skill
        for skill in preloaded_details
        if skill["skill_key"] == "developer-role-entrypoint"
    )
    assert entrypoint["name"] == "developer-role-entrypoint"
    assert "Load this skill first." in entrypoint["content"]
    assert "Procedure References" in entrypoint["content"]
    assert "references" in entrypoint["linked_files"]
    assert "references/developer-codebase-grounding.md" in entrypoint["linked_files"]["references"]


def test_ontosynth_skills_overview_includes_materialized_runtime_skill_detail_for_builtin_skill():
    payload, status = _get("/api/ontosynth/skills/overview")

    assert status == 200
    developer_runtime = next(
        role
        for role in payload["runtime_materialized"]["profiles"]
        if role["runtime_identity"] == "developer"
    )
    materialized_details = developer_runtime["materialized_skill_details"]
    worker = next(
        skill
        for skill in materialized_details
        if skill["skill_key"] == "kanban-worker"
    )
    assert worker["name"] == "kanban-worker"
    assert "Kanban Worker" in worker["content"]
    assert "Workspace handling" in worker["content"]
