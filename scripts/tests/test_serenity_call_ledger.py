import sqlite3

import pytest
from datetime import date

import serenity_call_ledger as ledger


def series(start_price, days, step):
    return {f"2026-11-{d:02d}": start_price + i * step for i, d in enumerate(days)}


DAYS = [13, 16, 17, 18, 19, 20, 23]
PRICES = {"AAA": series(10.0, DAYS, 1.0), "BBB": series(20.0, DAYS, -1.0), "XBI": series(100.0, DAYS, 0.0)}
CALLS = [{"ticker": "AAA", "tier": "standard", "tierText": "standard", "source": ""},
         {"ticker": "BBB", "tier": "starter", "tierText": "starter", "source": ""},
         {"ticker": "CCC", "tier": "watch", "tierText": "", "source": ""}]


def db():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    return connection


def test_current_calls_maps_free_text_tiers():
    calls = ledger.current_calls({"companies": [{"ticker": "X", "tier": "standard-thematic candidate"},
                                                {"ticker": "Y", "tier": "starter until governance clarified"}]})
    assert [(c["ticker"], c["tier"]) for c in calls] == [("X", "standard"), ("Y", "starter")]


def test_freeze_uses_last_close_known_on_call_day_and_skips_watch():
    connection = db()
    frozen = ledger.freeze(connection, CALLS, PRICES, date(2026, 11, 15))
    assert frozen == ["AAA", "BBB"]
    row = connection.execute("SELECT base_date, base_price FROM serenity_calls WHERE ticker='AAA'").fetchone()
    assert tuple(row) == ("2026-11-13", 10.0)


def test_freeze_is_weekly_unless_tier_changes():
    connection = db()
    ledger.freeze(connection, CALLS, PRICES, date(2026, 11, 15))
    assert ledger.freeze(connection, CALLS, PRICES, date(2026, 11, 16)) == []
    changed = [dict(CALLS[0], tier="starter")]
    assert ledger.freeze(connection, changed, PRICES, date(2026, 11, 17)) == ["AAA"]
    assert ledger.freeze(connection, CALLS[1:2], PRICES, date(2026, 11, 22)) == ["BBB"]


def test_backfill_counts_trading_sessions_and_compares_tiers():
    connection = db()
    ledger.freeze(connection, CALLS, PRICES, date(2026, 11, 15))
    ledger.backfill(connection, PRICES)
    table = {row["horizon"]: row for row in ledger.tier_table(connection)}
    assert table[1]["standard"]["return"] == pytest.approx(0.1)     # 10 -> 11 on the next session
    assert table[5]["starter"]["return"] == pytest.approx(-0.25)      # 20 -> 15 five sessions later
    assert table[5]["standardMinusStarter"] == pytest.approx(0.75)
    assert table[20]["standard"]["samples"] == 0


def test_track_record_handles_empty_score_ledger():
    connection = db()
    record = ledger.build_track_record(connection, "ai-medicine")
    assert record["scoreBackfill"][0]["samples"] == 0
    assert record["serenityCalls"] == []
