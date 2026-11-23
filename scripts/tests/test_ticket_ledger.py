from ticket_ledger import freeze, score, spells, summarize


def test_freeze_once_per_day():
    tickets = [{"ticker": "TEM", "action": "starter", "price": 50.0}, {"ticker": "X", "action": "wait", "price": None}]
    rows = freeze(tickets, "2026-11-23", [])
    assert [r["ticker"] for r in rows] == ["TEM"]
    assert freeze(tickets, "2026-11-23", rows) == []


def test_spell_counts_once_until_action_changes():
    ledger = [{"date": "2026-11-23", "ticker": "TEM", "action": "starter", "price": 50.0},
              {"date": "2026-11-24", "ticker": "TEM", "action": "starter", "price": 52.0},
              {"date": "2026-11-25", "ticker": "TEM", "action": "wait", "price": 55.0}]
    s = spells(ledger)
    assert [(x["action"], x["start"], x["end"], x["endPrice"]) for x in s] == [
        ("starter", "2026-11-23", "2026-11-25", 55.0), ("wait", "2026-11-25", None, None)]


def test_score_against_benchmark_uses_prior_close():
    s = [{"ticker": "TEM", "action": "starter", "start": "2026-11-22", "startPrice": 50.0, "end": None, "endPrice": None}]
    closes = {"TEM": {"2026-11-28": 55.0}, "XBI": {"2026-11-21": 100.0, "2026-11-28": 102.0}}
    out = score(s, closes, "2026-11-29")
    assert out[0]["return"] == 0.1 and out[0]["xbi"] == 0.02 and out[0]["excess"] == 0.08
    assert summarize(out)["live (buy/starter)"]["beatXbi"] == 1


def test_same_day_call_is_not_scored():
    s = [{"ticker": "TEM", "action": "starter", "start": "2026-11-23", "startPrice": 50.0, "end": None, "endPrice": None}]
    assert score(s, {"TEM": {"2026-11-23": 49.0}, "XBI": {"2026-11-23": 100.0}}, "2026-11-23") == []
