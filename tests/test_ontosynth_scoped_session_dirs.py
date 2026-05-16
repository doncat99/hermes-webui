import api.models as models
from api.models import Session


def _set_session_store(monkeypatch, session_dir):
    monkeypatch.setattr(models, "SESSION_DIR", session_dir)
    monkeypatch.setattr(models, "SESSION_INDEX_FILE", session_dir / "_index.json")


def _write_session(session_dir, session_id, profile, title, content):
    session_dir.mkdir(parents=True, exist_ok=True)
    original_dir = models.SESSION_DIR
    original_index = models.SESSION_INDEX_FILE
    try:
        models.SESSION_DIR = session_dir
        models.SESSION_INDEX_FILE = session_dir / "_index.json"
        session = Session(
            session_id=session_id,
            title=title,
            profile=profile,
            messages=[{"role": "user", "content": content, "timestamp": 1.0}],
        )
        session.save()
        return session
    finally:
        models.SESSION_DIR = original_dir
        models.SESSION_INDEX_FILE = original_index


def test_all_sessions_merges_ontosynth_scoped_session_dirs(tmp_path, monkeypatch):
    current_dir = tmp_path / "current" / "sessions"
    shared_dir = tmp_path / "shared" / "sessions"
    current_dir.mkdir(parents=True)
    shared_dir.mkdir(parents=True)

    _set_session_store(monkeypatch, current_dir)
    models.SESSIONS.clear()
    monkeypatch.setattr(
        models,
        "_ontosynth_webui_session_dir_targets",
        lambda: [current_dir, shared_dir],
    )

    _write_session(
        shared_dir,
        "knowledge_sid",
        "os-knowledge-steward",
        "Knowledge Steward Session knowledge_sid",
        "shared knowledge",
    )
    _write_session(
        current_dir,
        "developer_sid",
        "os-developer",
        "Developer Session developer_sid",
        "developer work",
    )

    rows = models.all_sessions()
    ids = {row["session_id"] for row in rows}

    assert "developer_sid" in ids
    assert "knowledge_sid" in ids


def test_get_session_falls_back_to_ontosynth_scoped_session_dirs(tmp_path, monkeypatch):
    current_dir = tmp_path / "current" / "sessions"
    shared_dir = tmp_path / "shared" / "sessions"
    current_dir.mkdir(parents=True)
    shared_dir.mkdir(parents=True)

    _set_session_store(monkeypatch, current_dir)
    models.SESSIONS.clear()
    monkeypatch.setattr(
        models,
        "_ontosynth_webui_session_dir_targets",
        lambda: [current_dir, shared_dir],
    )

    _write_session(
        shared_dir,
        "knowledge_sid",
        "os-knowledge-steward",
        "Knowledge Steward Session knowledge_sid",
        "shared knowledge",
    )

    metadata_only = models.get_session("knowledge_sid", metadata_only=True)
    full = models.get_session("knowledge_sid", metadata_only=False)

    assert metadata_only.session_id == "knowledge_sid"
    assert metadata_only._metadata_message_count == 1
    assert full.messages[0]["content"] == "shared knowledge"
