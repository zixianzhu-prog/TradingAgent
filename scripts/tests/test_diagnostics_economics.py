import diagnostics_economics as de


def test_period_key_and_per_test():
    assert de.period_key("three months ended September 30, 2026") == "three-2026"
    assert de.period_key("Year ended December 31, 2025") == "year-2025"
    facts = {"volume": [{"period": "three months ended September 30, 2026", "value": 200000, "unit": "tests"}],
             "testingRevenue": [{"period": "Three months ended September 30, 2026", "value": 250.0, "unit": "USD millions"}],
             "grossMargin": [], "payer": []}
    assert de.per_test(facts) == [{"period": "three months ended September 30, 2026", "scope": "total", "tests": 200000, "revenueM": 250.0, "revenuePerTest": 1250}]


def test_per_test_skips_mismatched_scope_and_ambiguity():
    q = "three months ended September 30, 2026"
    facts = {"volume": [{"period": q, "value": 244500, "unit": "tests", "scope": "total"}, {"period": q, "value": 101500, "unit": "tests", "scope": "oncology"}],
             "testingRevenue": [{"period": q, "value": 303.5, "unit": "USD millions", "scope": "total"},
                                {"period": q, "value": 102.6, "unit": "USD millions", "scope": "data and services"}],
             "grossMargin": [], "payer": []}
    out = de.per_test(facts)
    assert out == [{"period": q, "scope": "total", "tests": 244500, "revenueM": 303.5, "revenuePerTest": 1241}]


def test_verify_drops_short_and_missing_quotes(monkeypatch):
    text = "In the third quarter of 2026 we delivered approximately 205,000 clinical tests, up 20% from last year."
    monkeypatch.setattr(de.pcr, "filing_text", lambda url, allow=False: text)
    items = [{"id": "dx_1", "url": "https://www.sec.gov/q.htm", "title": "10-Q", "text": text}]
    facts, dropped = de.verify({"volume": [{"id": "dx_1", "quote": "In the third quarter of 2026 we delivered approximately 205,000 clinical tests", "period": "third quarter of 2026", "value": 205000, "unit": "tests"},
                                           {"id": "dx_1", "quote": "205,000 tests", "period": "q", "value": 1, "unit": "tests"}],
                                "testingRevenue": [], "grossMargin": [], "payer": []}, items)
    assert len(facts["volume"]) == 1 and dropped == 1


def test_value_and_year_must_be_in_quote():
    good = {"quote": "For the three months ended September 30, 2026, revenue was $303.5 million", "value": 303.5, "period": "three months ended September 30, 2026"}
    assert de.figure_in_quote(good)
    assert not de.figure_in_quote({**good, "value": 330.5})
    assert not de.figure_in_quote({**good, "period": "three months ended September 30, 2025"})


def test_units_are_explicit_never_guessed():
    q = "three months ended September 30, 2026"
    base = {"grossMargin": [], "payer": []}
    thousands = {**base, "volume": [{"period": q, "value": 61.5, "unit": "thousand tests"}],
                 "testingRevenue": [{"period": q, "value": 262700, "unit": "USD thousands"}]}
    assert de.per_test(thousands)[0]["revenuePerTest"] == 4272
    vague = {**base, "volume": [{"period": q, "value": 61500, "unit": "samples"}],
             "testingRevenue": [{"period": q, "value": 262.7, "unit": "USD millions"}]}
    assert de.per_test(vague) == []


def test_table_row_year_can_come_from_header():
    row = {"quote": "Net revenue Diagnostics $ 303,470 $ 252,878 $ 853,901", "value": 303470, "period": "three months ended September 30, 2026"}
    assert not de.figure_in_quote(row)
    assert de.figure_in_quote(row, "Three Months Ended September 30, 2026 2025 Nine Months Ended")


def test_mislabeled_id_falls_back_to_the_passage_holding_the_quote(monkeypatch):
    text = "In the third quarter of 2026 we delivered approximately 205,000 clinical tests, up 20% from last year."
    monkeypatch.setattr(de.pcr, "filing_text", lambda url, allow=False: text)
    items = [{"id": "dx_1", "url": "https://www.sec.gov/q.htm", "title": "10-Q", "text": text}]
    facts, dropped = de.verify({"volume": [{"id": "v1", "quote": "In the third quarter of 2026 we delivered approximately 205,000 clinical tests",
                                            "period": "third quarter of 2026", "value": 205000, "unit": "tests"}],
                                "testingRevenue": [], "grossMargin": [], "payer": []}, items)
    assert len(facts["volume"]) == 1 and dropped == 0
