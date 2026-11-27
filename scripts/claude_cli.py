"""Run `claude -p` with a timeout that really ends it.

subprocess.run(timeout=...) kills only the direct child. When `claude` leaves helper processes holding stdout open, the
caller then waits on the pipe forever (seen on 2026-11-26: three calls hung for over three hours). Here the call runs in its
own process group and the whole group is killed on timeout; the caller gets empty output and treats it as no answer.
"""
from __future__ import annotations

import os
import json
import signal
import subprocess
import sys
from functools import lru_cache


class ClaudeCLIError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def auth_status() -> tuple[bool, str]:
    try:
        result = subprocess.run(["claude", "auth", "status", "--json"], capture_output=True,
                                text=True, timeout=10)
        payload = json.loads(result.stdout or "{}")
        if payload.get("loggedIn"):
            return True, str(payload.get("authMethod") or "logged-in")
        return False, "not logged in; run `claude /login` in a terminal"
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        return False, f"Claude CLI health check failed: {exc}"


def run(cmd: list[str], prompt: str, timeout: int = 600, cwd=None) -> subprocess.CompletedProcess:
    if cmd and os.path.basename(cmd[0]) == "claude":
        ready, reason = auth_status()
        if not ready:
            return subprocess.CompletedProcess(cmd, 78, "", reason)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            cwd=cwd, start_new_session=True)
    try:
        out, err = proc.communicate(prompt, timeout=timeout)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        try:
            proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        return subprocess.CompletedProcess(cmd, -9, "", f"timed out after {timeout}s")
    return subprocess.CompletedProcess(cmd, proc.returncode, out, err)


def require_success(result: subprocess.CompletedProcess) -> subprocess.CompletedProcess:
    if result.returncode == 0:
        return result
    detail = (result.stderr or "").strip()
    if not detail and result.stdout:
        try:
            payload = json.loads(result.stdout)
            detail = str(payload.get("result") or payload.get("error") or "")
        except json.JSONDecodeError:
            detail = result.stdout[:500]
    raise ClaudeCLIError(detail or f"Claude CLI exited with code {result.returncode}")


if __name__ == "__main__":
    ready, reason = auth_status()
    print(json.dumps({"ready": ready, "reason": reason}, ensure_ascii=False))
    raise SystemExit(0 if ready else 1)
