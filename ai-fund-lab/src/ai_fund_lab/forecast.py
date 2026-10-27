from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

from .config import Settings
from .models import Bar


def run_kronos_forecast(
    bars_by_ticker: dict[str, list[Bar]], settings: Settings
) -> dict[str, dict[str, float]]:
    """Run Kronos out-of-process so its pinned dependencies stay isolated."""
    if not settings.kronos_enabled:
        return {}
    # Do not resolve the interpreter symlink: a venv's ``python`` commonly
    # points at its base interpreter, and resolving it would bypass the venv.
    python = Path(settings.kronos_python).expanduser().absolute()
    repo = Path(settings.kronos_repo).expanduser().resolve()
    if not python.is_file():
        raise RuntimeError(f"Kronos Python not found: {python}")
    if not (repo / "model" / "kronos.py").is_file():
        raise RuntimeError(f"Kronos repository is invalid: {repo}")

    runner = Path(__file__).resolve().parents[2] / "integrations" / "kronos_runner.py"
    payload = {
        "model": settings.kronos_model,
        "tokenizer": settings.kronos_tokenizer,
        "forecast_days": settings.kronos_forecast_days,
        "sample_count": settings.kronos_sample_count,
        "series": {
            ticker: [
                {
                    "date": bar.day.isoformat(),
                    "open": bar.open,
                    "high": bar.high,
                    "low": bar.low,
                    "close": bar.close,
                    "volume": bar.volume,
                }
                for bar in bars
            ]
            for ticker, bars in bars_by_ticker.items()
        },
    }
    with tempfile.TemporaryDirectory(prefix="ai-fund-kronos-") as tmp:
        input_path = Path(tmp) / "input.json"
        output_path = Path(tmp) / "output.json"
        input_path.write_text(json.dumps(payload), encoding="utf-8")
        env = os.environ.copy()
        env["PYTHONPATH"] = str(repo)
        env["HF_HOME"] = str(repo / "hf-cache")
        env["HF_HUB_DISABLE_TELEMETRY"] = "1"
        completed = subprocess.run(
            [str(python), str(runner), str(input_path), str(output_path)],
            env=env,
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout)[-2000:]
            raise RuntimeError(f"Kronos forecast failed: {detail}")
        return json.loads(output_path.read_text(encoding="utf-8"))
