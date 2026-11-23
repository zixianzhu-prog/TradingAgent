import backtest_order_rule as bt


def test_implied_cagr_matches_policy_return_at_fair_ps():
    # Market cap = revenue x P/S and a 12% target: revenue must grow 12% a year.
    assert abs(bt.implied_cagr(400, 100, 4.0) - 0.12) < 1e-9


def test_base_cagr_fades_toward_fundamental():
    assert 0.05 < bt.base_cagr(0.30, 0.05) < 0.30
    assert abs(bt.base_cagr(0.05, 0.05) - 0.05) < 1e-9


def test_growth_trend_from_one_filing_with_three_years():
    def v(end, start, val):
        return {"form": "10-K", "start": start, "end": end, "val": val, "filed": "2026-03-01", "accn": "a"}
    facts = {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [
        v("2023-12-31", "2023-01-01", 100), v("2024-12-31", "2024-01-01", 150), v("2025-12-31", "2025-01-01", 180)]}}}}}
    tr = bt.growth_trend(facts)
    assert tr["growth"] == 0.2 and tr["previousGrowth"] == 0.5 and tr["slowing"] is True
