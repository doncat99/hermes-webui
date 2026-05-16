from __future__ import annotations

import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import api.config as config
import api.startup as startup


def test_ensure_server_runtime_python_reexecs_when_current_python_cannot_import_agent(
    monkeypatch,
    tmp_path: Path,
) -> None:
    calls: list[tuple[str, list[str]]] = []

    def fake_probe(python_exe: str, agent_dir: Path | None = None) -> bool:
        return python_exe == "/good/python"

    def fake_execv(path: str, argv: list[str]) -> None:
        calls.append((path, argv))
        raise SystemExit(0)

    monkeypatch.setattr(startup, "_python_can_import_agent_runtime", fake_probe)
    monkeypatch.setattr(os, "execv", fake_execv)

    try:
        startup.ensure_server_runtime_python(
            current_python="/bad/python",
            target_python="/good/python",
            agent_dir=tmp_path / "agent",
            server_script=tmp_path / "server.py",
            argv=["server.py", "--demo"],
        )
    except SystemExit:
        pass

    assert calls == [
        ("/good/python", ["/good/python", str(tmp_path / "server.py"), "--demo"])
    ]


def test_ensure_server_runtime_python_does_not_reexec_when_current_python_is_already_healthy(
    monkeypatch,
    tmp_path: Path,
) -> None:
    calls: list[tuple[str, list[str]]] = []

    monkeypatch.setattr(
        startup,
        "_python_can_import_agent_runtime",
        lambda python_exe, agent_dir=None: True,
    )
    monkeypatch.setattr(os, "execv", lambda path, argv: calls.append((path, argv)))

    changed = startup.ensure_server_runtime_python(
        current_python="/good/python",
        target_python="/other/python",
        agent_dir=tmp_path / "agent",
        server_script=tmp_path / "server.py",
        argv=["server.py"],
    )

    assert changed is False
    assert calls == []


def test_ensure_server_runtime_python_does_not_reexec_when_target_python_is_not_better(
    monkeypatch,
    tmp_path: Path,
) -> None:
    calls: list[tuple[str, list[str]]] = []

    def fake_probe(python_exe: str, agent_dir: Path | None = None) -> bool:
        return False

    monkeypatch.setattr(startup, "_python_can_import_agent_runtime", fake_probe)
    monkeypatch.setattr(os, "execv", lambda path, argv: calls.append((path, argv)))

    changed = startup.ensure_server_runtime_python(
        current_python="/bad/python",
        target_python="/also-bad/python",
        agent_dir=tmp_path / "agent",
        server_script=tmp_path / "server.py",
        argv=["server.py"],
    )

    assert changed is False
    assert calls == []


def test_verify_hermes_imports_probes_with_runtime_python(monkeypatch, tmp_path: Path) -> None:
    calls: list[dict] = []
    real_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "run_agent":
            raise ModuleNotFoundError("sentinel current interpreter import failure")
        return real_import(name, *args, **kwargs)

    def fake_run(cmd, capture_output, text, timeout, env):
        calls.append(
            {
                "cmd": cmd,
                "capture_output": capture_output,
                "text": text,
                "timeout": timeout,
                "env": env,
            }
        )
        return SimpleNamespace(returncode=0, stderr="", stdout="")

    monkeypatch.setattr("builtins.__import__", fake_import)
    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(config, "PYTHON_EXE", "/runtime/python")
    monkeypatch.setattr(config, "_AGENT_DIR", tmp_path / "agent")

    ok, missing, errors = config.verify_hermes_imports()

    assert ok is True
    assert missing == []
    assert errors == {}
    assert calls, "verify_hermes_imports() must probe with the Hermes runtime interpreter"
    assert calls[0]["cmd"][0] == "/runtime/python"
    assert calls[0]["cmd"][1:3] == ["-c", calls[0]["cmd"][2]]
    assert "run_agent" in calls[0]["cmd"][2]
    assert str(tmp_path / "agent") in calls[0]["env"].get("PYTHONPATH", "")
