import claude_management_review as cmr


def test_to_gate_keeps_only_quotes_found_in_the_filing(monkeypatch):
    text = "On October 22, 2026, Jane Doe notified the Company that she will resign as President."
    monkeypatch.setattr(cmr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    passages = [{"id": "ev_1", "url": "https://www.sec.gov/x.htm", "text": text}]
    answer = {"status": "partial", "reason": "r", "support": [],
              "counter": [{"id": "ev_1", "quote": "she will resign as President"}, {"id": "ev_1", "quote": "invented words"},
                          {"id": "ev_9", "quote": "unknown id"}]}
    gate, dropped = cmr.to_gate(answer, passages)
    assert gate["counter"] == [{"url": "https://www.sec.gov/x.htm", "quote": "she will resign as President"}]
    assert dropped == 2


def test_event_passages_skip_non_sec_links(monkeypatch):
    monkeypatch.setattr(cmr.pcr, "filing_text", lambda url, allow_fetch=True: "The officer will resign. " * 10)
    out = cmr.event_passages([{"url": "https://example.com/a"}, {"url": "https://www.sec.gov/b.htm", "date": "d", "title": "t"}])
    assert out and all(p["url"].startswith("https://www.sec.gov/") for p in out)


def test_form4_only_pass_is_capped_at_partial():
    gate = {"status": "pass", "reason": "r", "missing": [],
            "support": [{"url": "https://www.sec.gov/a/xslF345X06/f.xml", "quote": "10b5-1"}]}
    assert cmr.cap_pass(gate)["status"] == "partial"
    gate = {"status": "pass", "reason": "r", "missing": [],
            "support": [{"url": "https://www.sec.gov/a/x-10k.htm", "quote": "CEO since 2012"}]}
    assert cmr.cap_pass(gate)["status"] == "pass"
