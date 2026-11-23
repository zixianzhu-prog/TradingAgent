from science_commercialization_graph import build


def base_company():
    return [{"ticker": "TEST", "company": "Test Bio", "exposure": "protein design"}]


def test_technology_overlap_does_not_validate_ownership_or_commercialization():
    frontier = {"works": [{"id": "w1", "title": "Protein design", "companyLinks": [
        {"ticker": "TEST", "relation": "technology_overlap_candidate", "evidence": ["protein design"]}
    ], "authors": []}]}
    result = build(frontier, base_company(), {}, {}, {}, {}, {}, {"links": []})
    row = result["companies"][0]
    assert row["verifiedStages"]["discovery"] == 0
    assert row["verifiedStages"]["researcherCompanyRelation"] == 0
    assert row["verifiedStages"]["technologyOwnership"] == 0
    assert row["chainStatus"] == "evidence-fragment"


def test_paid_partnership_is_commercial_signal_but_not_revenue():
    pharma = {"filings": [{"ticker": "TEST", "kind": "deal", "url": "https://sec.test/8k",
                            "facts": {"isNewDeal": True,
                                      "partner": {"value": "Big Pharma", "quote": "entered a multi-year paid collaboration with Big Pharma", "verified": True},
                                      "upfrontUsdM": {"value": 20, "quote": "received a non-refundable upfront payment of $20 million", "verified": True}}}]}
    result = build({}, base_company(), pharma, {}, {}, {}, {}, {"links": []})
    row = result["companies"][0]
    assert row["verifiedStages"]["pharmaValidation"] == 1
    assert row["verifiedStages"]["revenueValidation"] == 0
    assert row["chainStatus"] == "commercial-signal-with-ownership-gap"
    assert row["pharmaValidation"][0]["revenueProof"] is False


def test_primary_ownership_and_xbrl_create_auditable_chain():
    manual = {"links": [{"ticker": "TEST", "relation": "license", "sourceType": "university tech transfer",
                          "url": "https://university.test/license", "quote": "The university exclusively licensed the platform to Test Bio.",
                          "status": "verified"}]}
    financials = {"companies": [{"ticker": "TEST"}]}
    xbrl = {"companies": [{"ticker": "TEST", "source": "https://sec.test/xbrl", "checks": [
        {"metric": "quarterly_revenue_m", "status": "pass", "official": 12.3,
         "periodEnd": "2026-09-30", "tag": "us-gaap:Revenue"}]}]}
    result = build({}, base_company(), {}, {}, {}, financials, xbrl, manual)
    row = result["companies"][0]
    assert row["verifiedStages"]["technologyOwnership"] == 1
    assert row["verifiedStages"]["revenueValidation"] == 1
    assert row["chainStatus"] == "ownership-and-company-revenue-verified"
    assert "尚不能证明收入来自相关 AI/科研技术" in row["gaps"][-1]
