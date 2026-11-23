from insider_buy_study import events, forward, stats


def test_events_fold_purchases_within_30_days_and_need_minimum():
    ps = [{"cik": "1", "filed": "2024-01-02", "symbol": "A", "value": 20_000, "owners": ["o1"], "role": "officer/director"},
          {"cik": "1", "filed": "2024-01-20", "symbol": "A", "value": 30_000, "owners": ["o2"], "role": "10% holder"},
          {"cik": "1", "filed": "2024-03-01", "symbol": "A", "value": 10_000, "owners": ["o1"], "role": "officer/director"}]
    e = events(ps)
    assert len(e) == 1 and e[0]["valueUsd"] == 50_000 and e[0]["buyers"] == 2 and e[0]["role"] == "officer/director"


def test_forward_enters_after_filing_day_and_subtracts_benchmark():
    closes = [("2024-01-02", 10.0), ("2024-01-03", 10.0), ("2024-01-04", 12.0)]
    bench = {"2024-01-03": 100.0, "2024-01-04": 105.0}
    assert round(forward(closes, bench, "2024-01-02", 1), 4) == 0.15  # +20% minus +5%
    assert forward(closes, bench, "2024-01-04", 1) is None


def test_stats():
    s = stats([0.1, -0.6, 0.3])
    assert s["n"] == 3 and s["median"] == 0.1 and s["severeLoss"] == round(1 / 3, 3)
