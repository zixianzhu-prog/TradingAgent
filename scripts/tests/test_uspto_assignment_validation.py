from uspto_assignment_validation import build


OWNERSHIP = {"companies": [{"ticker": "TEST", "evidence": [
    {"relation": "patent_portfolio", "quote": "We own one patent family.", "url": "https://www.sec.gov/test"}
]}]}


def test_sec_claim_creates_queue_but_not_verification():
    result = build(OWNERSHIP, {"TEST": "Test Bio"}, {"records": []}, False)
    assert result["summary"]["queued"] == 1
    assert result["summary"]["verifiedCompanies"] == 0
    assert result["companies"][0]["status"] == "pending-official-search"


def test_official_assignment_record_verifies_company():
    imported = {"records": [{"ticker": "TEST", "assignee": "Test Bio", "assignor": "Example University",
                              "recordedAt": "2025-01-01", "reelFrame": "123/456",
                              "url": "https://assignmentcenter.uspto.gov/search/intellectualProperty/search"}]}
    result = build(OWNERSHIP, {"TEST": "Test Bio"}, imported, True)
    assert result["summary"]["verifiedCompanies"] == 1
    assert result["companies"][0]["officialAssignments"][0]["independentAssignmentVerified"] is True


def test_non_official_url_is_rejected():
    imported = {"records": [{"ticker": "TEST", "assignee": "Test Bio", "recordedAt": "2025-01-01",
                              "url": "https://company.test/patent"}]}
    result = build(OWNERSHIP, {"TEST": "Test Bio"}, imported, False)
    assert result["summary"]["verifiedCompanies"] == 0
    assert result["summary"]["rejectedImports"] == 1
