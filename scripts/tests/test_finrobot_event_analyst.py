from finrobot_event_analyst import build, candidate_jobs, normalize_analysis, score_company


def test_rule_screening_only_queues_high_score_themes():
    trends = {"themes": [
        {"name": "ai_medicine", "label": "AI Medicine", "score": 75, "evidence": [{"title": "A", "url": "u1", "source": "FDA"}]},
        {"name": "optical", "label": "Optical", "score": 40, "evidence": [{"title": "B", "url": "u2", "source": "News"}]},
    ]}
    links = {"companies": [{"theme": "ai_medicine", "ticker": "CERT", "company": "Certara", "serenity_role": "infrastructure"}]}
    jobs = candidate_jobs(trends, links, 70, 10)
    assert len(jobs) == 1
    assert jobs[0]["candidateCompanies"][0]["ticker"] == "CERT"


def test_normalizer_rejects_unsupplied_ticker():
    raw = {"companies": [
        {"ticker": "CERT", "impact_direction": "positive", "materiality": "high", "direct_company_relationship": True},
        {"ticker": "FAKE", "impact_direction": "positive", "materiality": "high"},
    ]}
    result = normalize_analysis(raw, {"CERT"})
    assert [row["ticker"] for row in result["companies"]] == ["CERT"]


def test_deterministic_score_is_not_return_probability():
    row = {
        "ticker": "CERT", "impactDirection": "positive", "materiality": "high", "timeHorizon": "1-3y",
        "directCompanyRelationship": True, "revenuePath": "demand to software revenue",
        "supportingSourceUrls": ["https://www.sec.gov/a", "https://example.com/b"],
        "counterEvidenceSeverity": "medium", "pricedInRisk": "medium", "affectedSerenityGates": ["earnings_validation"],
    }
    result = score_company(row, "SEC filing", "research-ready")
    assert result["businessImpactScore"] == 77
    assert "not a probability" in result["interpretation"]


def test_pending_mode_generates_auditable_job_without_claims():
    trends = {"themes": [{"name": "ai_medicine", "label": "AI Medicine", "score": 75, "evidence": [{"title": "A", "url": "u1", "source": "FDA"}]}]}
    links = {"companies": [{"theme": "ai_medicine", "ticker": "CERT", "company": "Certara"}]}
    payload = build(trends, links, {"companies": []}, "pending", "finrobot", None, 70, 10, 1)
    assert payload["summary"]["pendingConfig"] == 1
    assert payload["events"][0]["status"] == "pending-config"
    assert "analysis" not in payload["events"][0]
