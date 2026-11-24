import json
from datetime import date

import data_freshness as df


def write(root, rel, data):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def test_stale_critical_source_raises_alert(tmp_path):
    write(tmp_path, "state/order-tickets.json", {"generatedAt": "2026-11-24T10:00:00+00:00", "pricesAsOf": "2026-11-17"})
    out = df.check(date(2026, 11, 24), tmp_path)
    rows = {r["label"]: r for r in out["sources"]}
    assert rows["Market prices"]["status"] == "stale" and rows["Market prices"]["ageDays"] == 7
    assert rows["Order tickets"]["status"] == "fresh"
    assert rows["Serenity gates"]["status"] == "missing"
    assert out["alert"]


def test_dated_rows_use_latest_day():
    assert df.read_date({"articleDates": [{"day": "2026-11-20"}, {"day": "2026-11-23"}]}, "articleDates") == date(2026, 11, 23)
    assert df.read_date({"generatedAt": "2026-11-23"}, "generatedAt") == date(2026, 11, 23)
    assert df.read_date({"generatedAt": "garbage"}, "generatedAt") is None


def test_weekend_gap_within_price_limit(tmp_path):
    write(tmp_path, "state/order-tickets.json", {"generatedAt": "2026-11-23T10:00:00+00:00", "pricesAsOf": "2026-11-20"})
    rows = {r["label"]: r for r in df.check(date(2026, 11, 23), tmp_path)["sources"]}
    assert rows["Market prices"]["status"] == "fresh"
