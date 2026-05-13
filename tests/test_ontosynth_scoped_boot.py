from pathlib import Path


REPO = Path(__file__).parent.parent
BOOT_JS = (REPO / "static" / "boot.js").read_text(encoding="utf-8")
ROUTES_PY = (REPO / "api" / "routes.py").read_text(encoding="utf-8")


def _boot_saved_session_block() -> str:
    marker = "const urlSession="
    start = BOOT_JS.find(marker)
    assert start > 0, "boot saved-session restore block not found"
    end_marker = "// no saved session"
    end = BOOT_JS.find(end_marker, start)
    assert end > start, "no-saved-session marker not found after restore block"
    return BOOT_JS[start:end]


def test_scoped_boot_helpers_exist():
    assert "function _ontosynthScopedBootEnabled()" in BOOT_JS
    assert "function _ontosynthScopedBootDefaultPanel()" in BOOT_JS
    assert "function _ontosynthScopedBootDefaultBoard()" in BOOT_JS
    assert "_ontosynthApplyScopedBootDefaults();" in BOOT_JS


def test_boot_reads_scoped_flags_from_api_settings():
    assert "window.ONTOSYNTH_WEBUI_SCOPE_ACTIVE=!!s.ontosynth_scope_active;" in BOOT_JS
    assert "window.ONTOSYNTH_WEBUI_PROFILE_SCOPE_PATH=s.ontosynth_scope_path||'';" in BOOT_JS
    assert "window.ONTOSYNTH_WEBUI_DEFAULT_PANEL=s.ontosynth_default_panel||'';" in BOOT_JS
    assert "window.ONTOSYNTH_WEBUI_DEFAULT_KANBAN_BOARD=s.ontosynth_default_kanban_board||'';" in BOOT_JS


def test_scoped_root_boot_skips_saved_chat_projection():
    block = _boot_saved_session_block().replace(" ", "")
    assert "constscopedBoot=_ontosynthScopedBootEnabled();" in block
    assert "if(saved&&!(scopedBoot&&!urlSession)){" in block


def test_scoped_boot_defaults_to_kanban_panel():
    compact = BOOT_JS.replace(" ", "")
    assert "if(scopedBoot&&_ontosynthScopedBootDefaultPanel()==='kanban'&&typeofswitchPanel==='function'){" in compact
    assert "awaitswitchPanel('kanban');" in compact


def test_api_settings_expose_ontosynth_scoped_boot_contract():
    assert 'settings["ontosynth_webui_patch"] = "profile-scope-v8"' in ROUTES_PY
    assert 'settings["ontosynth_scope_active"] = bool(_ontosynth_webui_profile_scope())' in ROUTES_PY
    assert 'settings["ontosynth_scope_path"] = os.getenv("ONTOSYNTH_WEBUI_PROFILE_SCOPE_PATH", "")' in ROUTES_PY
    assert 'settings["ontosynth_default_panel"] = "kanban" if bool(_ontosynth_webui_profile_scope()) else ""' in ROUTES_PY
    assert '"knowledge-governance"' in ROUTES_PY
