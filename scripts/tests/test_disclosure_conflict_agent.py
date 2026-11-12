from disclosure_conflict_agent import analyze_company, build


COMPANY = {"ticker": "TEST", "aliases": ["Test Bio"]}


def test_official_financing_vs_optimistic_news_triggers_review():
    articles = [
        {"source": "SEC TEST Filings", "title": "424B5 - Prospectus", "content": "common shares", "url": "sec", "published_at": "2026-01-02"},
        {"source": "news", "title": "Test Bio breakthrough platform sees strong growth", "content": "promising", "url": "news", "published_at": "2026-01-02"},
    ]
    result = analyze_company(COMPANY, articles)
    assert result["status"] == "revalidate"
    assert "dilution" in result["affectedGates"]
    assert "financing" in result["officialRiskCategories"]


def test_official_risk_without_optimistic_narrative_is_not_called_divergence():
    articles = [
        {"source": "SEC TEST Filings", "title": "S-3 registration", "content": "common shares", "url": "sec", "published_at": "2026-01-02"},
    ]
    result = analyze_company(COMPANY, articles)
    assert result["status"] == "official-risk-only"
    assert result["divergenceScore"] == 0


def test_summary_counts_revalidation_flags():
    articles = [
        {"source": "SEC TEST Filings", "title": "424B5", "content": "public offering", "url": "sec", "published_at": "2026-01-02"},
        {"source": "news", "title": "Test Bio record breakthrough", "content": "bullish", "url": "news", "published_at": "2026-01-02"},
    ]
    payload = build({"companies": [COMPANY]}, articles)
    assert payload["summary"]["revalidate"] == 1
