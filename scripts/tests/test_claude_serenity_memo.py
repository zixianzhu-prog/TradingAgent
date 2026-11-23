import claude_serenity_memo as m


def test_to_citations_maps_quote_ids_back_to_filing_urls_and_drops_unknown_ids():
    evidence = [{"id": "ev_a", "url": "https://sec.gov/10k.htm"}, {"id": "ev_b", "url": "https://sec.gov/10q.htm"}]
    gates = {"customer_dependency": {"status": "partial", "reason": "r", "missing": ["x"], "falsifiers": [],
                                     "support": [{"id": "ev_a", "quote": "one customer accounted for 30%"}, {"id": "ev_zz", "quote": "made up"}],
                                     "counter": [{"id": "ev_b", "quote": "revenue decreased"}]}}
    out = m.to_citations(gates, evidence)["customer_dependency"]
    assert out["support"] == [{"url": "https://sec.gov/10k.htm", "quote": "one customer accounted for 30%"}]
    assert out["counter"] == [{"url": "https://sec.gov/10q.htm", "quote": "revenue decreased"}]
    assert out["status"] == "partial" and out["missing"] == ["x"]
