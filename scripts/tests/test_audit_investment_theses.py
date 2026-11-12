from audit_investment_theses import audit_candidate


def test_audit_score_is_completeness_not_return_score():
    candidate = {
        "ticker": "TEST",
        "thesis": "A traceable thesis",
        "why_now": "A forward signal",
        "classification": "watch",
        "bear_case": "The thesis can fail",
        "falsifiers": ["a", "b", "c"],
        "sources": ["https://example.com/a", "https://example.com/b"],
    }
    serenity = {"TEST": {"serenity_decision": "watch", "earnings_validation": "pass", "reason": "reviewed"}}
    market = {
        "results": [{"signal": {"ticker": "TEST", "price": 10}}],
        "kronos": {"TEST": {"forecast_return": -0.50}},
    }
    result = audit_candidate(candidate, serenity, market)
    assert result["auditScore"] == 100
    assert result["evidenceConfidence"] == "high"
    assert "expected return" not in result["provenance"]["audit_score"].lower()


def test_missing_earnings_validation_is_disclosed():
    candidate = {
        "ticker": "TEST",
        "thesis": "A thesis",
        "why_now": "A signal",
        "classification": "watch",
        "bear_case": "Can fail",
        "falsifiers": ["a", "b", "c"],
        "sources": ["https://example.com/a"],
    }
    result = audit_candidate(candidate, {"TEST": {"serenity_decision": "watch", "earnings_validation": "pending"}}, {})
    assert "财报验证尚未通过" in result["missingEvidence"]
    assert result["evidenceConfidence"] != "high"
