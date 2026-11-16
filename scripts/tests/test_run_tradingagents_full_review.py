from datetime import date, timedelta
from pathlib import Path

import run_tradingagents_full_review as module


def test_priority_universe_puts_core_ai_medicine_names_first(tmp_path: Path):
    universe = tmp_path / "universe.json"
    universe.write_text(
        '{"companies":[{"ticker":"NVDA"},{"ticker":"TEM"},{"ticker":"RDNT"},{"ticker":"ILMN"}]}',
        encoding="utf-8",
    )
    assert module.load_universe(universe) == ["RDNT", "TEM", "NVDA", "ILMN"]


def test_select_due_respects_cadence(monkeypatch, tmp_path: Path):
    old = tmp_path / "TEM_20261101_120000"
    recent = tmp_path / "RDNT_20261113_120000"
    monkeypatch.setattr(module, "newest_review", lambda ticker: {"TEM": old, "RDNT": recent}.get(ticker))
    rows = module.select_due(["TEM", "RDNT", "SOPH"], date(2026, 11, 14), 7, False)
    assert [row["ticker"] for row in rows if row["due"]] == ["TEM", "SOPH"]


def test_review_age_uses_run_id_date(tmp_path: Path):
    path = tmp_path / "TEM_20261101_120000"
    path.mkdir()
    assert module.review_age(path, date(2026, 11, 14)) == 13
