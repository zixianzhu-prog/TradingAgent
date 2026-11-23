from technology_ownership_agent import extract_passage


def evidence(text: str, url: str = "https://www.sec.gov/Archives/test.htm") -> dict:
    return {"id": "ev_test", "url": url, "text": text}


def test_explicit_exclusive_license_is_captured():
    rows = extract_passage("TEST", evidence("We have an exclusive worldwide license to the core platform from Example University."))
    assert rows and rows[0]["relation"] == "exclusive_license"


def test_generic_patent_risk_is_not_ownership_evidence():
    rows = extract_passage("TEST", evidence("We may be unable to protect our patents and competitors may challenge them."))
    assert rows == []


def test_we_have_policy_is_not_patent_ownership():
    rows = extract_passage("TEST", evidence("We have a policy of seeking patent protection for patentable aspects of our technology."))
    assert rows == []


def test_hypothetical_valid_patent_is_not_ownership():
    rows = extract_passage("TEST", evidence("We may not prevent competitors from launching a product even if we hold a valid patent."))
    assert rows == []


def test_non_sec_material_is_ignored():
    rows = extract_passage("TEST", evidence("We have an exclusive license to this platform.", "https://company.test/news"))
    assert rows == []


def test_founder_relation_is_separate_from_patent_ownership():
    rows = extract_passage("TEST", evidence("We believe Dr. Example is qualified because of the experience he brings as a co-founder and our Chief Executive Officer."))
    assert rows[0]["relation"] == "founder_company"
    assert "not proof" in rows[0]["scopeNote"]
