from pathlib import Path


REPO = Path(__file__).parent.parent
PANELS_JS = (REPO / "static" / "panels.js").read_text(encoding="utf-8")
ROUTES_PY = (REPO / "api" / "routes.py").read_text(encoding="utf-8")
STYLE_CSS = (REPO / "static" / "style.css").read_text(encoding="utf-8")


def test_ontosynth_skills_panel_uses_overview_endpoint_when_scoped():
    compact = PANELS_JS.replace(" ", "")
    assert "function_ontosynthSkillsScopedModeEnabled()" in compact
    assert "constendpoint=_ontosynthSkillsScopedModeEnabled()?'/api/ontosynth/skills/overview':'/api/skills';" in compact
    assert "renderOntoSynthSkillsOverview(data);" in compact


def test_ontosynth_skills_overview_route_exists():
    assert 'if parsed.path == "/api/ontosynth/skills/overview":' in ROUTES_PY


def test_ontosynth_skills_panel_uses_i18n_keys_not_hardcoded_titles():
    assert "skills_ontosynth_platform_catalog" in PANELS_JS
    assert "skills_ontosynth_project_contract" in PANELS_JS
    assert "skills_ontosynth_runtime_materialized" in PANELS_JS
    assert "'Platform Catalog'" not in PANELS_JS
    assert "'Project Contract'" not in PANELS_JS
    assert "'Runtime Materialized'" not in PANELS_JS


def test_ontosynth_skills_panel_supports_detail_open_for_operator_items():
    assert "openOntoSynthSkillDetail(" in PANELS_JS
    assert "data-ontosynth-skill-detail=" in PANELS_JS
    assert "ontosynth-skill-item" in PANELS_JS
    assert "_renderOntoSynthSkillDetail(" in PANELS_JS
    assert "_renderSkillDetail(detail.name" in PANELS_JS


def test_ontosynth_role_detail_supports_nested_managed_skill_drilldown():
    assert "openOntoSynthManagedSkillDetail(" in PANELS_JS
    assert "data-ontosynth-managed-skill-detail=" in PANELS_JS
    assert "ontosynth-managed-skill-item" in PANELS_JS
    assert "skills_ontosynth_skill_references" in PANELS_JS


def test_ontosynth_runtime_detail_supports_materialized_skill_drilldown_and_contract_backlink():
    assert "openOntoSynthRuntimeSkillDetail(" in PANELS_JS
    assert "data-ontosynth-runtime-skill-detail=" in PANELS_JS
    assert "ontosynth-runtime-skill-item" in PANELS_JS
    assert "skills_ontosynth_runtime_status" in PANELS_JS
    assert "skills_ontosynth_contract_backlink" in PANELS_JS
    assert "skills_ontosynth_preloaded_runtime_reference" in PANELS_JS
    assert "skills_ontosynth_materialized_runtime_reference" in PANELS_JS
    assert "skills_ontosynth_reference_content" in PANELS_JS
    assert "ontosynth-detail-section-title" in PANELS_JS


def test_ontosynth_runtime_reference_content_is_rendered_in_collapsible_section():
    assert "_renderOntoSynthCollapsibleDetailSection(" in PANELS_JS
    assert "ontosynth-detail-section-toggle" in PANELS_JS
    assert "skills_ontosynth_reference_expand" in PANELS_JS
    assert "skills_ontosynth_reference_collapse" in PANELS_JS
    assert ".ontosynth-detail-section[open] .ontosynth-detail-expand-label{display:none;}" in STYLE_CSS
    assert ".ontosynth-detail-section[open] .ontosynth-detail-collapse-label{display:inline;}" in STYLE_CSS
