import sys
import time
import subprocess

import claude_cli


def test_logged_out_cli_fails_fast_with_actionable_reason(monkeypatch):
    monkeypatch.setattr(claude_cli, "auth_status", lambda: (False, "not logged in; run `claude /login` in a terminal"))
    result = claude_cli.run(["claude", "-p"], "hello", timeout=60)
    assert result.returncode == 78
    assert "claude /login" in result.stderr


def test_require_success_surfaces_cli_error():
    result = subprocess.CompletedProcess(["claude"], 1, "", "subscription unavailable")
    try:
        claude_cli.require_success(result)
        assert False, "expected ClaudeCLIError"
    except claude_cli.ClaudeCLIError as exc:
        assert "subscription unavailable" in str(exc)


def test_timeout_returns_without_waiting_for_helper_pipe():
    code = (
        "import subprocess,sys,time; "
        "subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); "
        "time.sleep(60)"
    )
    started = time.monotonic()
    result = claude_cli.run([sys.executable, "-c", code], "", timeout=0.1)
    assert result.returncode == -9
    assert result.stdout == ""
    assert time.monotonic() - started < 3
