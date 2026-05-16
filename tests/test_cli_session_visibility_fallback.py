import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from api.agent_sessions import is_cli_session_row_visible  # noqa: E402


def test_cli_session_visibility_uses_messages_length_when_message_count_missing():
    row = {
        "session_id": "knowledge_session_1",
        "title": "Knowledge Steward Session 20260511_121007_7cfb4d",
        "profile": "os-knowledge-steward",
        "is_cli_session": True,
        "session_source": "cli",
        "source_tag": "cli",
        "raw_source": "cli",
        "source_label": "CLI",
        "messages": [
            {"role": "user", "content": "seed"},
            {"role": "assistant", "content": "result"},
        ],
    }

    assert is_cli_session_row_visible(row) is True


def test_cli_session_visibility_still_hides_zero_message_rows():
    row = {
        "session_id": "empty_cli_1",
        "title": "CLI Session",
        "is_cli_session": True,
        "session_source": "cli",
        "source_tag": "cli",
        "raw_source": "cli",
        "source_label": "CLI",
        "messages": [],
    }

    assert is_cli_session_row_visible(row) is False
