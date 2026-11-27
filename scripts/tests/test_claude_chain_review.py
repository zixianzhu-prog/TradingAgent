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


def test_gate_passages_keeps_dated_results(monkeypatch):
    supply = "supplier vendor manufacture license customers pharma hospitals users cloud sequencing " * 20
    results = ("For the three months ended September 30, 2026, total revenue was $10.2 million compared to $3.1 million; "
               "net loss was $12.0 million. ") * 12
    text = (supply[:2200] * 12) + results[:2200] + (supply[:2200] * 6)
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    out = ccr.gate_passages([("10-Q", "2026-11-05", "u")], limit=6, results_per_filing=2)
    assert any("three months ended" in p["text"] for p in out)


def test_unrelated_actuals_are_not_reported_as_missing():
    status, rule = ccr.earnings_status(0, 0, 0, 3)
    assert status == "unknown" and "无直接关系" in rule


def test_gate_passages_keeps_named_counterparties(monkeypatch):
    filler = "supplier vendor manufacture license customers pharma hospitals users cloud sequencing revenue " * 20
    exhibit = ("10.26 Corporate Supply Agreement, dated January 10, 2022, by and between CeriBell, Inc. and Shenzhen Everwin "
               "Precision Technology Co., Ltd. 10.27 Supply Agreement, dated February 1, 2024, by and between CeriBell, Inc. and Ease Care. ") * 6
    text = (filler[:2200] * 14) + exhibit[:2200] + (filler[:2200] * 4)
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    out = ccr.gate_passages([("10-K", "2026-02-24", "u")], limit=8, results_per_filing=1, parties_per_filing=2)
    assert any("Shenzhen Everwin" in p["text"] for p in out)


def test_a_single_named_agreement_is_kept(monkeypatch):
    filler = "supplier vendor manufacture license customers pharma hospitals users cloud sequencing revenue " * 20
    one = ("Exhibit 10.9 Manufacturing Agreement, dated May 2, 2023, by and between Acme Robotics, Inc. and Delta Contract "
           "Manufacturing LLC. Exhibit 19.1 Insider Trading Policy. ") + "z " * 1000
    text = (filler[:2200] * 10) + one[:2200] + (filler[:2200] * 3)
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    out = ccr.gate_passages([("10-K", "2026-02-24", "u")], limit=6, results_per_filing=1, parties_per_filing=1)
    assert any("Delta Contract" in p["text"] for p in out)


def test_active_named_relationship_outranks_terminated_agreement(monkeypatch):
    terminated = ("The Supply Agreement by and between Acme and OldCo was terminated and is no longer in effect. "
                  + "old " * 520)
    active = ("We depend exclusively on Illumina for all sequencing instruments used in our laboratory. "
              + "active " * 360)
    text = terminated[:2200] + active[:2200]
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    out = ccr.gate_passages([("10-K", "2026-02-24", "u")], limit=3, results_per_filing=0, parties_per_filing=1)
    assert any("Illumina" in p["text"] for p in out)
