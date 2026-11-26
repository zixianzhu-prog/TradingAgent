import claude_counter_review as ccr


def test_rubric_needs_all_dimensions_falsifiers_and_sourced_counter():
    allx = {d: True for d in (*ccr.DIMENSIONS, "valuation")}
    assert ccr.serenity_status(allx, 1, 1)[0] == "pass"
    assert ccr.serenity_status({**allx, "geopolitics": False}, 1, 1)[0] == "partial"
    assert ccr.serenity_status(allx, 0, 1)[0] == "partial"
    assert ccr.serenity_status(allx, 1, 0)[0] == "partial"


def test_dimension_counts_only_with_verified_quote(monkeypatch):
    text = ("We rely on Illumina as a sole supplier of sequencers. Payers may deny reimbursement for our tests. "
            "Competitors offer similar genomic tests. Substantially all of our revenue is generated in the United States.")
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    passages = [{"id": "ct_1", "url": "https://www.sec.gov/10k.htm", "title": "10-K", "text": text}]
    q = lambda s: {"examined": True, "summary": "x", "evidence": [{"id": "ct_1", "quote": s}]}
    answer = {"supply": q("We rely on Illumina as a sole supplier of sequencers"),
              "demand": q("Payers may deny reimbursement for our tests"),
              "substitution": q("Competitors offer similar genomic tests"),
              "geopolitics": q("invented sentence about tariffs"),
              "falsifiers": ["Illumina 供应中断"], "reason": "r"}
    val = {"examined": True, "summary": "现价 $57；限价 $62"}
    gate, dropped = ccr.to_gate(answer, passages, val)
    assert dropped == 1 and gate["status"] == "partial" and "geopolitics" in gate["reason"]
    answer["geopolitics"] = q("Substantially all of our revenue is generated in the United States")
    gate, _ = ccr.to_gate(answer, passages, val)
    assert gate["status"] == "pass" and len(gate["counter"]) == 4 and gate["falsifiers"]


def test_valuation_needs_a_range_or_flip_points():
    assert not ccr.valuation_check(None)["examined"]
    assert ccr.valuation_check({"price": 57.4, "limitPrice": 62.9, "flipPoints": ["growth can fall 2 points"]})["examined"]


def test_scenario_model_counts_as_valuation_when_there_is_no_ticket():
    row = {"price": 18.09, "scenario_model": {"probability_weighted_case_annualized_return": 0.08,
           "cases": {"bear": {"annualized_return": -0.12}, "base": {"annualized_return": 0.10, "price_for_policy_return": 16.5}}}}
    v = ccr.valuation_check(None, row)
    assert v["examined"] and "16.5" in v["summary"] and "-12.0%" in v["summary"]
    assert not ccr.valuation_check(None, {"price": 1, "scenario_model": {}})["examined"]


def test_rnpv_counts_as_valuation_for_drug_developers():
    r = {"price": 9.34, "phase": 2, "valuePerShare": {"bear": 2.38, "base": 2.79, "bull": 3.95}, "impliedPeakSalesM": 6121.0,
         "notes": ["discovery platform"]}
    v = ccr.valuation_check(None, None, r)
    assert v["examined"] and "6,121" in v["summary"] and v["source"].endswith("rnpv-valuations.json")
