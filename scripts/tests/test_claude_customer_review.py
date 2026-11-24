import claude_customer_review as ccr


def test_rubric_applied_mechanically():
    assert ccr.serenity_status(1, 0)[0] == "pass"
    assert ccr.serenity_status(0, 2)[0] == "partial"   # partnership alone
    assert ccr.serenity_status(0, 0)[0] == "unknown"


def test_to_gate_verifies_quotes_and_keeps_risks_out_of_grade(monkeypatch):
    text = "Ceribell is used in over 500 hospitals. Our top three customers accounted for 30% of revenue. We partner with X."
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    passages = [{"id": "cu_1", "url": "https://www.sec.gov/10k.htm", "title": "10-K", "text": text}]
    answer = {"adoption": [{"id": "cu_1", "quote": "Ceribell is used in over 500 hospitals", "kind": "site_count"},
                           {"id": "cu_1", "quote": "invented 900 hospitals", "kind": "site_count"}],
              "partnership": [{"id": "cu_1", "quote": "We partner with X"}],
              "otherRisks": [{"id": "cu_1", "quote": "Our top three customers accounted for 30% of revenue", "note": "客户集中"}],
              "reason": "r"}
    gate, dropped = ccr.to_gate(answer, passages)
    assert gate["status"] == "pass" and dropped == 1 and gate["counter"] == [] and gate["missing"] == []
    assert gate["otherRisks"][0]["note"] == "客户集中"
    only_partner = {**answer, "adoption": []}
    assert ccr.to_gate(only_partner, passages)[0]["status"] == "partial"
