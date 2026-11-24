import build_top5_brief as b


def test_repriced_moves_cap_and_ps_to_latest_close():
    fin = {"market_cap_m": 1000.0, "price_to_sales_approx": 8.0, "price": 50.0, "price_date": "2026-11-13"}
    out = b.repriced(fin, {"last": 55.0, "asOf": "2026-11-24"})
    assert out == {"marketCapM": 1100.0, "priceToSales": 8.8, "priceDate": "2026-11-24"}
    assert b.repriced(fin, {})["priceDate"] == "2026-11-13"
