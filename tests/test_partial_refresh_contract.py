from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PANELS = (ROOT / "static" / "panels.js").read_text(encoding="utf-8")


def test_shared_panel_refresh_state_registry_exists():
    assert "function _panelRefreshState(" in PANELS
    assert "mounted: false" in PANELS
    assert "refreshInFlight: false" in PANELS
    assert "refreshQueued: false" in PANELS


def test_background_refresh_helper_never_uses_loading_shell():
    assert "async function _runPanelRefresh(" in PANELS
    assert "function _panelRememberSelection(" in PANELS
    assert "background refresh must not paint Loading" not in PANELS


def test_in_scope_panels_use_mount_load_patch_shape():
    for panel_name in ("Kanban", "KnowledgeStructure", "Skills", "Memory", "Tasks"):
        assert f"mount{panel_name}Panel" in PANELS
        assert f"load{panel_name}Data" in PANELS
        assert f"patch{panel_name}View" in PANELS
