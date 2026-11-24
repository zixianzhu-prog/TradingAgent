import claude_management_review as cmr


def test_to_gate_keeps_only_quotes_found_in_the_filing(monkeypatch):
    text = "On October 22, 2026, Jane Doe notified the Company that she will resign as President."
    monkeypatch.setattr(cmr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    passages = [{"id": "ev_1", "url": "https://www.sec.gov/x.htm", "text": text}]
    answer = {"continuity": {"confirmed": False, "evidence": []}, "investigation": {"open": False, "evidence": []},
              "succession": {"unresolved": True, "evidence": [{"id": "ev_1", "quote": "she will resign as President"},
                                                               {"id": "ev_1", "quote": "invented words"}, {"id": "ev_9", "quote": "x"}]},
              "otherRisks": [], "reason": "r"}
    gate, dropped = cmr.to_gate(answer, passages)
    assert gate["counter"] == [{"url": "https://www.sec.gov/x.htm", "quote": "she will resign as President"}]
    assert dropped == 2 and gate["status"] == "partial" and "继任未定" in gate["reason"]


def test_serenity_rubric_applied_mechanically():
    assert cmr.serenity_status(True, False, False)[0] == "pass"
    assert cmr.serenity_status(True, True, False)[0] == "partial"   # open investigation
    assert cmr.serenity_status(True, False, True)[0] == "partial"   # unresolved succession
    assert cmr.serenity_status(False, False, False)[0] == "partial"  # continuity not shown


def test_other_risks_are_recorded_but_do_not_block_pass(monkeypatch):
    text = "John Roe serves as our Chief Executive Officer. We have Class B shares with ten votes per share."
    monkeypatch.setattr(cmr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    passages = [{"id": "px_1", "url": "https://www.sec.gov/def14a.htm", "text": text}]
    answer = {"continuity": {"confirmed": True, "evidence": [{"id": "px_1", "quote": "John Roe serves as our Chief Executive Officer"}]},
              "investigation": {"open": False, "evidence": []}, "succession": {"unresolved": False, "evidence": []},
              "otherRisks": [{"id": "px_1", "quote": "Class B shares with ten votes per share", "note": "双重股权"}], "reason": "r"}
    gate, _ = cmr.to_gate(answer, passages)
    assert gate["status"] == "pass" and gate["otherRisks"][0]["note"] == "双重股权"
    assert gate["counter"] == [] and gate["missing"] == []  # recorded, not counter-evidence to the rubric


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


def test_proxy_passages_include_resolution_text(monkeypatch):
    import claude_management_review as m
    filler = "The board met five times. " * 120
    text = ("Ms. A is an independent director. Related person transactions are reviewed. " * 3 + filler
            + "The notes were automatically converted upon the completion of our initial public offering. " + filler)
    monkeypatch.setattr(m.pcr, "filing_text", lambda url, allow=True: text)
    ps = m.proxy_passages("https://www.sec.gov/x", limit=1)
    assert any("automatically converted" in p["text"] for p in ps)
