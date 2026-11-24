from datetime import date, timedelta

import blind_test as bt


def series(start_price, daily, days=80, start=date(2026, 11, 2)):
    out, p, d = {}, start_price, start
    while len(out) < days:
        if d.weekday() < 5:
            out[d.isoformat()] = p
            p *= 1 + daily
        d += timedelta(days=1)
    return out


def test_week_and_forward_excess():
    assert bt.week_of(date(2026, 11, 26)) == date(2026, 11, 23)
    bench = series(100, 0.0)
    up = series(10, 0.01)
    x = bt.forward(up, bench, "2026-11-09", 5)
    assert abs(x - (1.01 ** 5 - 1)) < 1e-9
    assert bt.forward(up, bench, "2026-11-09", 500) is None


def test_spearman():
    assert abs(bt.spearman([1, 2, 3, 4, 5], [10, 20, 30, 40, 50]) - 1) < 1e-9
    assert abs(bt.spearman([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]) + 1) < 1e-9
    assert bt.spearman([1, 2], [1, 2]) is None


def test_citation_check_matches_normalized_text():
    cache = {}
    page = "<p>Revenue&nbsp;fell   to <b>$106.3 million</b> ’s</p>"
    assert bt.check_citation("https://x.test/a", "revenue fell to $106.3 million", cache, lambda u: page) == "verified"
    assert bt.check_citation("https://x.test/a", "revenue rose", cache, lambda u: page) == "not_found"
    assert bt.check_citation("https://x.test/b", "anything", cache, lambda u: None) == "fetch_failed"


def test_clean_b_keeps_universe_and_five_extras():
    answer = {"calls": [{"ticker": "tem", "action": "buy", "confidence": 70, "excess12m": 0.1, "risks": [], "falsifier": "x"},
                        {"ticker": "TEM", "action": "wait", "confidence": 1, "excess12m": 0, "risks": [], "falsifier": ""},
                        {"ticker": "ZZZ", "action": "buy", "confidence": 1, "excess12m": 0, "risks": [], "falsifier": ""}],
              "extras": [{"ticker": f"E{i}", "action": "buy", "confidence": 50, "excess12m": 0, "risks": [], "falsifier": ""} for i in range(7)]}
    calls = bt.clean_b(answer, ["TEM", "CAI"])
    assert [c["ticker"] for c in calls if not c.get("extra")] == ["TEM"]
    assert calls[0]["action"] == "buy"
    assert sum(1 for c in calls if c.get("extra")) == 5


def test_score_counts_crash_held_and_basket():
    bench = series(100, 0.0)
    closes = {"XBI": bench, "UP": series(10, 0.005), "CRASH": series(10, -0.03), "FLAT": series(10, 0.0)}
    calls = [{"ticker": "UP", "action": "buy", "confidence": 90, "risks": []},
             {"ticker": "CRASH", "action": "starter", "confidence": 10, "risks": []},
             {"ticker": "FLAT", "action": "wait", "confidence": 50, "risks": []}]
    ledger = [{"week": "2026-11-09", "group": "A", "system": "a", "universe": ["UP", "CRASH", "FLAT"], "calls": calls}]
    out = bt.score(ledger, closes, {}, fetch=lambda u: None)
    a = out["groups"]["A"]
    assert a["crashes"] == 1 and a["crashesHeld"] == 1
    assert a["basketExcess"]["20"]["weeks"] == 1
    assert "too early" in out["verdict"]


def test_freeze_is_once_per_week(tmp_path, monkeypatch):
    monkeypatch.setattr(bt, "FILTER", tmp_path / "f.json")
    monkeypatch.setattr(bt, "TICKETS", tmp_path / "t.json")
    monkeypatch.setattr(bt, "CITATIONS", tmp_path / "c.json")
    (tmp_path / "f.json").write_text('{"deepReview": ["TEM"], "companies": [{"ticker": "TEM", "marketCapM": 9000, "revenueM": 1000}]}')
    (tmp_path / "t.json").write_text('{"tickets": [{"ticker": "TEM", "action": "buy", "potential": {"total": 78}, "invalidation": "[\'Volume stalls\', \'x\']"}]}')
    ledger = tmp_path / "l.jsonl"
    fake = lambda prompt, model: {"calls": [{"ticker": "TEM", "action": "wait", "confidence": 40, "excess12m": 0, "risks": [], "falsifier": ""}], "extras": []}
    first = bt.freeze(date(2026, 11, 24), "sonnet", ask=fake, ledger_path=ledger, raw_dir=tmp_path / "raw")
    again = bt.freeze(date(2026, 11, 26), "sonnet", ask=fake, ledger_path=ledger, raw_dir=tmp_path / "raw")
    assert sorted(first["frozen"]) == ["A", "B", "C"] and again["frozen"] == []
    rows = bt.read_ledger(ledger)
    a = next(r for r in rows if r["group"] == "A")["calls"][0]
    assert a["falsifier"] == "Volume stalls" and a["confidence"] == 78


def test_group_a_records_names_without_ticket():
    calls = bt.group_a(["TEM", "GENB"], {"TEM": {"action": "buy", "potential": {}}}, {})
    assert calls[0]["confidence"] is None
    assert calls[1] == {"ticker": "GENB", "action": "wait", "confidence": None, "excess12m": None, "risks": [], "falsifier": "", "noTicket": True}


def test_reworded_quote_with_right_figures():
    page = "<td>Net Income</td><td>-189.29M</td>"
    assert bt.check_citation("https://x.test/c", "Net Income: -$189.29M", {}, lambda u: page) == "numbers_only"
    assert bt.check_citation("https://x.test/c", "Net Income: -$200M", {}, lambda u: page) == "not_found"
