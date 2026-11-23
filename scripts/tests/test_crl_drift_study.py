from crl_drift_study import shock_and_drift, study


def series(n, start=10.0, step=0.0):
    from datetime import date, timedelta
    d0 = date(2024, 1, 1)
    return [((d0 + timedelta(days=i)).isoformat(), start + step * i) for i in range(n)]


def test_shock_measured_from_day_before_letter_and_drift_after():
    closes = series(200)
    closes = closes[:10] + [(d, 5.0) for d, _ in closes[10:]]  # halves on day 10
    bench = {d: 100.0 for d, _ in closes}
    r = shock_and_drift(closes, bench, closes[10][0])
    assert round(r["shock"], 4) == -0.5 and r["6m"] == 0.0 and r["12m"] is None  # 252 trading days not available in 200


def test_study_groups_by_severity_and_big_drop():
    closes = series(300)
    closes = closes[:10] + [(d, 6.0) for d, _ in closes[10:]]
    prices = {"AAA": closes, "XBI": [(d, 100.0) for d, _ in closes]}
    rows = [{"listed": {"ticker": "AAA"}, "issued": closes[10][0], "severity": "heavy", "set": "unapproved", "drug": "X"}]
    g = study(rows, prices)["groups"]
    assert g["severity: heavy"]["shock"]["n"] == 1 and "first-week drop of 30%+" in g
