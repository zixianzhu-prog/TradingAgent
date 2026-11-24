import claude_chain_review as ccr


def test_map_rubric():
    assert ccr.map_status(1, 1, 1)[0] == "pass"
    assert ccr.map_status(0, 1, 1)[0] == "partial"
    assert ccr.map_status(0, 0, 0)[0] == "unknown"


def test_earnings_rubric():
    assert ccr.earnings_status(2, 0, 0)[0] == "pass"
    assert ccr.earnings_status(1, 1, 0)[0] == "partial"
    assert ccr.earnings_status(0, 1, 0)[0] == "partial"
    assert ccr.earnings_status(0, 0, 3)[0] == "partial"   # guidance alone
    assert ccr.earnings_status(0, 0, 0)[0] == "unknown"


def test_to_gates_needs_named_parties_and_dated_actuals(monkeypatch):
    text = ("We purchase sequencers from Illumina. Our software platform predicts molecular properties. "
            "Our customers include all of the top 20 pharmaceutical companies. "
            "Software revenue increased 15% to $180 million for the year ended December 31, 2025. "
            "We expect revenue growth of 10% in 2026.")
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    p = [{"id": "sc_1", "url": "https://www.sec.gov/10k.htm", "title": "10-K", "text": text}]
    ans = {"upstream": [{"id": "sc_1", "quote": "We purchase sequencers from Illumina", "party": "Illumina"}],
           "product": [{"id": "sc_1", "quote": "Our software platform predicts molecular properties"}],
           "downstream": [{"id": "sc_1", "quote": "Our customers include all of the top 20 pharmaceutical companies", "party": ""}],
           "results": [{"id": "sc_1", "quote": "Software revenue increased 15% to $180 million for the year ended December 31, 2025",
                        "period": "FY2025", "kind": "actual", "relation": "consistent"},
                       {"id": "sc_1", "quote": "We expect revenue growth of 10% in 2026", "period": "2026", "kind": "guidance", "relation": "consistent"}],
           "otherRisks": [], "reason": "r"}
    s, e, _ = ccr.to_gates(ans, p)
    assert s["status"] == "partial"  # downstream names no party
    assert e["status"] == "pass" and len(e["support"]) == 1  # guidance is not counted as support
    ans["downstream"][0]["party"] = "top 20 pharmaceutical companies"
    assert ccr.to_gates(ans, p)[0]["status"] == "pass"
