from hidden_gems_agent import build, score_company


def inputs():
    link = {"ticker": "TEST", "company": "Test", "theme": "ai", "theme_label": "AI", "serenity_role": "chokepoint", "pure_play": True}
    serenity = {"chokepoint_evidence": "pass", "customer_dependency": "pass", "multi_node_control": "pass", "earnings_validation": "pass"}
    financial = {"market_cap_m": 1200, "funding_risk": "low", "sources": ["https://example.com"]}
    news = {"article_count": 2}
    market = {"liquidityStatus": "pass", "averageDollarVolume60d": 5_000_000}
    return link, serenity, financial, news, market


def test_high_quality_liquid_small_cap_enters_deep_research():
    row = score_company(*inputs())
    assert row["status"] == "deep-research"
    assert row["score"] == 100
    assert "point-in-time dollar-volume liquidity" not in row["missingEvidence"]


def test_large_cap_does_not_pass_hidden_gem_size_gate():
    link, serenity, financial, news, _ = inputs()
    financial["market_cap_m"] = 20_000
    row = score_company(link, serenity, financial, news, {"liquidityStatus": "pass"})
    assert row["status"] == "outside-size-range"


def test_missing_financial_data_is_audited_not_promoted():
    link, serenity, _, news, _ = inputs()
    payload = build({"companies": [link]}, {"companies": [{"ticker": "TEST", **serenity}]}, {"companies": []}, {"companies": [{"ticker": "TEST", **news}]}, {"companies": []})
    assert payload["summary"]["withMarketCap"] == 0
    assert payload["candidates"] == []
    assert payload["allCompanies"][0]["status"] == "incomplete"
