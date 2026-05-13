from pathlib import Path


REPO = Path(__file__).parent.parent
SESSIONS_JS = (REPO / "static" / "sessions.js").read_text(encoding="utf-8")


def test_load_session_switches_active_profile_to_session_profile():
    start = SESSIONS_JS.find("async function loadSession(sid){")
    assert start != -1, "loadSession not found"
    end = SESSIONS_JS.find("  // Reset scroll-direction tracker", start)
    assert end != -1, "loadSession metadata block not found"
    block = SESSIONS_JS[start:end]

    assert "const _sessionProfile = (S.session && S.session.profile) ? S.session.profile : 'default';" in block
    assert "if (_sessionProfile && _sessionProfile !== (S.activeProfile || 'default')) {" in block
    assert "await api('/api/profile/switch'" in block
    assert "S.activeProfile = switched.active || _sessionProfile;" in block


def test_load_session_clears_skill_and_workspace_caches_after_profile_rebind():
    start = SESSIONS_JS.find("const _sessionProfile = (S.session && S.session.profile)")
    assert start != -1
    block = SESSIONS_JS[start:start + 1800]

    assert "_skillsData = null;" in block
    assert "_cronSkillsCache = null;" in block
    assert "_workspaceList = null;" in block
    assert "await Promise.all([populateModelDropdown(), loadWorkspaceList()]);" in block
    assert "await loadSkills();" in block
