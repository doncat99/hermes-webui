"""Regression tests for /api/models local-auth short-circuit.

When WebUI already has enough local provider evidence from auth.json /
credential_pool / config, `get_available_models()` should not trigger the
expensive Hermes-wide provider auth scan. That scan can fan out into Copilot
token exchange and AWS metadata probing, which makes the first `/api/models`
request take seconds.
"""

from __future__ import annotations

import json
import sys
import types

import api.config as config
import api.profiles as profiles


def test_local_auth_store_short_circuits_global_provider_probe(monkeypatch, tmp_path):
    fake_pkg = types.ModuleType("hermes_cli")
    fake_pkg.__path__ = []

    fake_models = types.ModuleType("hermes_cli.models")
    calls: list[str] = []

    def _should_not_run():
        calls.append("list_available_providers")
        return []

    fake_models.list_available_providers = _should_not_run
    fake_models.provider_model_ids = lambda pid: []

    fake_auth = types.ModuleType("hermes_cli.auth")
    fake_auth.get_auth_status = lambda _pid: {}

    monkeypatch.setitem(sys.modules, "hermes_cli", fake_pkg)
    monkeypatch.setitem(sys.modules, "hermes_cli.models", fake_models)
    monkeypatch.setitem(sys.modules, "hermes_cli.auth", fake_auth)
    monkeypatch.delitem(sys.modules, "agent.credential_pool", raising=False)
    monkeypatch.delitem(sys.modules, "agent", raising=False)

    auth_payload = {
        "version": 1,
        "active_provider": "custom:apiopencc.com",
        "providers": {
            "openai-codex": {
                "tokens": {"access_token": "token"},
            }
        },
        "credential_pool": {
            "custom:apiopencc.com": [
                {
                    "id": "cp_custom",
                    "label": "custom-pool",
                    "source": "manual",
                }
            ],
            "google-gemini-cli": [
                {
                    "id": "cp_gemini",
                    "label": "gemini-oauth",
                    "source": "oauth",
                }
            ],
        },
    }
    (tmp_path / "auth.json").write_text(json.dumps(auth_payload), encoding="utf-8")
    monkeypatch.setattr(profiles, "get_active_hermes_home", lambda: tmp_path)

    old_cfg = dict(config.cfg)
    old_mtime = config._cfg_mtime
    config.cfg.clear()
    config.cfg.update(
        {
            "model": {
                "provider": "custom:apiopencc.com",
                "default": "gpt-5.5",
                "base_url": "https://apiopencc.com/v1",
            },
            "providers": {},
            "fallback_providers": [],
        }
    )
    try:
        try:
            config._cfg_mtime = config.Path(config._get_config_path()).stat().st_mtime
        except Exception:
            config._cfg_mtime = 0.0
        config.invalidate_models_cache()
        result = config.get_available_models()
    finally:
        config.cfg.clear()
        config.cfg.update(old_cfg)
        config._cfg_mtime = old_mtime
        config.invalidate_models_cache()

    assert calls == [], (
        "get_available_models() should not call hermes_cli.models."
        "list_available_providers() when local auth store already proves"
        " the visible providers"
    )
    assert result.get("active_provider") == "custom:apiopencc.com"
