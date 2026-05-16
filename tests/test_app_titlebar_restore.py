from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
STYLE_CSS = (ROOT / "static" / "style.css").read_text(encoding="utf-8")
PANELS_JS = (ROOT / "static" / "panels.js").read_text(encoding="utf-8")
UI_JS = (ROOT / "static" / "ui.js").read_text(encoding="utf-8")


def test_app_titlebar_no_longer_contains_tps_chip():
    assert 'id="tpsStat"' not in INDEX_HTML


def test_app_titlebar_returns_to_centered_desktop_layout():
    assert ".app-titlebar{display:flex;align-items:center;justify-content:center;" in STYLE_CSS
    assert ".app-titlebar-inner{display:flex;align-items:center;gap:8px;min-width:0;max-width:100%;justify-content:center;}" in STYLE_CSS


def test_app_titlebar_subtitle_shows_message_count_again():
    assert "visible_message_count" in PANELS_JS
    assert "subText = t('n_messages', displayCount);" in PANELS_JS


def test_queue_updates_do_not_hijack_app_titlebar_subtitle():
    assert "_syncQueueTitlebar" not in UI_JS


def test_switch_panel_updates_titlebar_before_async_panel_loads():
    match = re.search(
        r"async function switchPanel\(name, opts = \{\}\) \{(.*?)syncAppTitlebar\(\);(.*?)if \(nextPanel === 'tasks'\)",
        PANELS_JS,
        re.DOTALL,
    )
    assert match, (
        "switchPanel() must sync the app titlebar before async panel loaders run, "
        "so slow tabs do not leave the previous panel title visible."
    )
