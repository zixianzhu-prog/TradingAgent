from sec_xbrl_validation_agent import select_fact, validate_company


def fact_payload():
    return {"facts": {"us-gaap": {"Revenues": {"units": {"USD": [
        {"val": 10_000_000, "start": "2026-01-01", "end": "2026-03-31", "filed": "2026-05-01", "form": "10-Q", "frame": "CY2026Q1"},
        {"val": 12_000_000, "start": "2026-07-01", "end": "2026-09-30", "filed": "2026-11-01", "form": "10-Q", "frame": "CY2026Q3"},
    ]}}}}}


def test_select_fact_uses_latest_true_quarter():
    fact = select_fact(fact_payload(), ("Revenues",), "USD", "quarter")
    assert fact["value"] == 12.0
    assert fact["frame"] == "CY2026Q3"


def test_material_difference_creates_review_without_overwrite():
    official = {"quarterly_revenue_m": {"value": 10.0, "unit": "USD_m", "tag": "us-gaap:Revenues", "filed": "2026-11-01", "periodEnd": "2026-09-30"}}
    result = validate_company("TEST", official, {"quarterly_revenue_m": 20.0})
    assert result["status"] == "review"
    assert result["reviewMetrics"] == ["quarterly_revenue_m"]
    assert result["checks"][0]["local"] == 20.0
