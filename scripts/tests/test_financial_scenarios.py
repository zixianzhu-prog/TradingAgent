from build_financial_scenarios import analyze


def test_positive_ebitda_company_is_not_given_fake_runway():
    row = {
        "ticker": "TEM",
        "price": 10,
        "shares": 100_000_000,
        "quarterly_revenue_m": 100,
        "revenue_growth_pct": 25,
        "cash_and_securities_m": 500,
        "quarterly_net_income_m": -10,
        "adjusted_ebitda_m": 5,
        "full_year_revenue_guide_m": 400,
        "dilution_flag": "medium",
        "data_freshness": "current",
    }
    result = analyze(row)
    assert result["funding_risk"] == "low"
    assert result["runway_years_proxy"] is None
    assert result["market_cap_m"] == 1000
    assert result["price_to_sales_approx"] == 2.5


def test_milestone_biotech_revenue_multiple_is_flagged_not_used_as_decision():
    row = {
        "ticker": "RXRX",
        "price": 4,
        "shares": 500_000_000,
        "quarterly_revenue_m": 10,
        "revenue_growth_pct": 100,
        "cash_and_securities_m": 800,
        "quarterly_net_income_m": -100,
        "quarterly_operating_cash_flow_m": -80,
        "adjusted_ebitda_m": None,
        "full_year_revenue_guide_m": None,
        "dilution_flag": "high",
        "data_freshness": "current",
    }
    result = analyze(row)
    assert "not decision-useful" in result["valuation_label"]
    assert result["runway_years_proxy"] == 2.5


def test_stale_financials_force_wait_for_earnings():
    row = {
        "ticker": "ABCL",
        "price": 10,
        "shares": 300_000_000,
        "quarterly_revenue_m": 5,
        "revenue_growth_pct": -50,
        "cash_and_securities_m": 700,
        "quarterly_net_income_m": -50,
        "adjusted_ebitda_m": None,
        "full_year_revenue_guide_m": None,
        "dilution_flag": "high",
        "data_freshness": "stale_pending_earnings",
    }
    assert analyze(row)["research_action"] == "wait-for-earnings"


def test_period_specific_current_financials_are_not_treated_as_stale():
    row = {
        "ticker": "ABCL",
        "price": 12,
        "shares": 324_000_000,
        "quarterly_revenue_m": 10.6,
        "revenue_growth_pct": 17.8,
        "cash_and_securities_m": 790,
        "quarterly_net_income_m": -40.8,
        "adjusted_ebitda_m": None,
        "full_year_revenue_guide_m": None,
        "dilution_flag": "high",
        "data_freshness": "current_q3_2026",
    }
    assert analyze(row)["research_action"] == "valuation-watch"
