from unittest.mock import MagicMock, patch
from urllib.parse import urlparse


class TestSessionVisibleMessageCount:
    def _stub_session(self):
        session = MagicMock()
        session.context_length = 1
        session.threshold_tokens = 0
        session.last_prompt_tokens = 0
        session.input_tokens = 0
        session.output_tokens = 0
        session.model = "test-model"
        session.title = "Visible Count Session"
        session.session_id = "visible-count-001"
        session.active_stream_id = None
        session.pending_user_message = None
        session.pending_attachments = []
        session.pending_started_at = None
        session.tool_calls = []
        session.messages = [
            {"role": "user", "content": "u1"},
            {"role": "assistant", "content": "a1"},
            {"role": "tool", "content": "t1"},
            {"role": "assistant", "content": "a2"},
            {"role": "tool", "content": "t2"},
            {"role": "assistant", "content": "a3"},
        ]
        session.compact.return_value = {
            "session_id": "visible-count-001",
            "title": "Visible Count Session",
            "model": "test-model",
            "message_count": 6,
            "context_length": 1,
            "created_at": 1000,
            "updated_at": 2000,
            "last_message_at": 2000,
            "pinned": False,
            "archived": False,
            "project_id": None,
            "profile": None,
            "input_tokens": 0,
            "output_tokens": 0,
            "estimated_cost": None,
            "personality": None,
            "compression_anchor_visible_idx": None,
            "compression_anchor_message_key": None,
            "active_stream_id": None,
            "is_streaming": False,
        }
        return session

    def test_get_session_exposes_visible_message_count_even_when_tail_window_is_truncated(self):
        import api.routes as routes

        session = self._stub_session()
        captured = {}

        def fake_j(_handler, payload, status=200, extra_headers=None):
            captured["payload"] = payload
            captured["status"] = status
            return payload

        handler = MagicMock()
        parsed = urlparse("/api/session?session_id=visible-count-001&messages=1&resolve_model=0&msg_limit=2")

        with patch("api.routes.get_session", return_value=session), \
             patch("api.routes.j", side_effect=fake_j):
            routes.handle_get(handler, parsed)

        body = captured["payload"]["session"]
        assert body["message_count"] == 6
        assert body["visible_message_count"] == 4, (
            "visible_message_count must represent the full non-tool transcript, "
            "not just the paginated tail window"
        )
        assert len(body["messages"]) == 2
        assert [msg["role"] for msg in body["messages"]] == ["tool", "assistant"]

    def test_get_session_metadata_only_still_reports_visible_message_count_for_cli_sessions(self):
        import api.routes as routes

        session = self._stub_session()
        captured = {}

        def fake_j(_handler, payload, status=200, extra_headers=None):
            captured["payload"] = payload
            captured["status"] = status
            return payload

        handler = MagicMock()
        parsed = urlparse("/api/session?session_id=visible-count-001&messages=0&resolve_model=0")

        with patch("api.routes.get_session", return_value=session), \
             patch("api.routes.j", side_effect=fake_j), \
             patch("api.routes._lookup_cli_session_metadata", return_value={"source_tag": "cli", "message_count": 6}), \
             patch("api.routes.get_cli_session_messages", return_value=session.messages):
            routes.handle_get(handler, parsed)

        body = captured["payload"]["session"]
        assert body["visible_message_count"] == 4
        assert body["message_count"] == 6

    def test_get_session_metadata_only_falls_back_to_full_sidecar_for_visible_count(self):
        import api.routes as routes

        full_session = self._stub_session()
        metadata_only_session = MagicMock()
        metadata_only_session.context_length = 1
        metadata_only_session.threshold_tokens = 0
        metadata_only_session.last_prompt_tokens = 0
        metadata_only_session.input_tokens = 0
        metadata_only_session.output_tokens = 0
        metadata_only_session.model = "test-model"
        metadata_only_session.title = "Visible Count Session"
        metadata_only_session.session_id = "visible-count-001"
        metadata_only_session.active_stream_id = None
        metadata_only_session.pending_user_message = None
        metadata_only_session.pending_attachments = []
        metadata_only_session.pending_started_at = None
        metadata_only_session.tool_calls = []
        metadata_only_session.messages = []
        metadata_only_session.compact.return_value = dict(full_session.compact.return_value)

        captured = {}

        def fake_j(_handler, payload, status=200, extra_headers=None):
            captured["payload"] = payload
            captured["status"] = status
            return payload

        calls = []

        def fake_get_session(_sid, metadata_only=False):
            calls.append(metadata_only)
            return metadata_only_session if metadata_only else full_session

        handler = MagicMock()
        parsed = urlparse("/api/session?session_id=visible-count-001&messages=0&resolve_model=0")

        with patch("api.routes.get_session", side_effect=fake_get_session), \
             patch("api.routes.j", side_effect=fake_j), \
             patch("api.routes._lookup_cli_session_metadata", return_value={}):
            routes.handle_get(handler, parsed)

        body = captured["payload"]["session"]
        assert calls == [True, False]
        assert body["visible_message_count"] == 4
