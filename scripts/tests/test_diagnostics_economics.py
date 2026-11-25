import diagnostics_economics as de


def test_period_key_and_per_test():
    assert de.period_key("three months ended September 30, 2026") == "three-2026"
    assert de.period_key("Year ended December 31, 2025") == "year-2025"
    facts = {"volume": [{"period": "three months ended September 30, 2026", "value": 200000}],
             "testingRevenue": [{"period": "Three months ended September 30, 2026", "value": 250.0, "unit": "USD millions"}],
             "grossMargin": [], "payer": []}
    assert de.per_test(facts) == [{"period": "three months ended September 30, 2026", "scope": "total", "tests": 200000, "revenueM": 250.0, "revenuePerTest": 1250}]


def test_per_test_skips_mismatched_scope_and_ambiguity():
    q = "three months ended September 30, 2026"
    facts = {"volume": [{"period": q, "value": 244500, "scope": "total"}, {"period": q, "value": 101500, "scope": "oncology"}],
             "testingRevenue": [{"period": q, "value": 303.5, "unit": "USD millions", "scope": "total"},
                                {"period": q, "value": 102.6, "unit": "USD millions", "scope": "data and services"}],
             "grossMargin": [], "payer": []}
    out = de.per_test(facts)
    assert out == [{"period": q, "scope": "total", "tests": 244500, "revenueM": 303.5, "revenuePerTest": 1241}]


def test_verify_drops_short_and_missing_quotes(monkeypatch):
    text = "We delivered approximately 205,000 clinical tests in the quarter, up 20% from last year."
    monkeypatch.setattr(de.pcr, "filing_text", lambda url, allow=False: text)
    items = [{"id": "dx_1", "url": "https://www.sec.gov/q.htm", "title": "10-Q", "text": text}]
    facts, dropped = de.verify({"volume": [{"id": "dx_1", "quote": "We delivered approximately 205,000 clinical tests", "period": "q", "value": 205000, "unit": "tests"},
                                           {"id": "dx_1", "quote": "205,000 tests", "period": "q", "value": 1, "unit": "tests"}],
                                "testingRevenue": [], "grossMargin": [], "payer": []}, items)
    assert len(facts["volume"]) == 1 and dropped == 1
