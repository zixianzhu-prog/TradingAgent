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


def test_odp_records_map_assignments_and_require_applicant_match():
    from uspto_assignment_validation import odp_records, base_name
    assert base_name("TuHURA Biosciences, Inc./NV") == "TuHURA Biosciences"
    def fetch(url, key):
        assert key == "k"
        if url.endswith("/assignment"):
            return {"patentFileWrapperDataBag": [{"assignmentBag": [{
                "assigneeBag": [{"assigneeNameText": "OCUPHIRE PHARMA, INC."}], "assignorBag": [{"assignorName": "DOE, JANE"}],
                "assignmentRecordedDate": "2026-07-29", "reelAndFrameNumber": "075447/0730", "conveyanceText": "ASSIGNMENT",
                "assignmentDocumentLocationURI": "https://assignmentcenter.uspto.gov/ipas/search/api/v3/public/download/patent/75447/730"}]}]}
        return {"count": 2, "patentFileWrapperDataBag": [
            {"applicationNumberText": "19566464", "applicationMetaData": {"firstApplicantName": "Opus Genetics, Inc.", "inventionTitle": "T"}},
            {"applicationNumberText": "1", "applicationMetaData": {"firstApplicantName": "Other Co", "inventionTitle": "X"}}]}
    recs, n = odp_records("IRD", "Opus Genetics, Inc.", "k", fetch)
    assert n == 2 and len(recs) == 1
    r = recs[0]
    assert r["reelFrame"] == "075447/0730" and r["assignee"] == "OCUPHIRE PHARMA, INC." and r["url"].startswith("https://assignmentcenter.uspto.gov")
    result = build(OWNERSHIP | {"companies": [{"ticker": "IRD", "evidence": [{"relation": "license", "quote": "q", "url": "u"}]}]},
                   {"IRD": "Opus Genetics, Inc."}, {"records": recs}, True)
    assert result["summary"]["verifiedCompanies"] == 1


def test_security_interest_is_a_lien_not_ownership():
    lien = {"ticker": "TEST", "assignee": "Lender LP", "recordedAt": "2026-01-01", "conveyance": "SECURITY INTEREST",
            "url": "https://assignmentcenter.uspto.gov/x"}
    result = build(OWNERSHIP, {"TEST": "Test Bio"}, {"records": [lien]}, True)
    c = result["companies"][0]
    assert c["status"] == "pending-official-search" and len(c["securityInterests"]) == 1
    assert result["summary"]["companiesWithPatentLiens"] == 1


def test_run_without_key_keeps_last_live_records():
    rec = {"ticker": "IRD", "assignee": "Opus Genetics", "recordedAt": "2024-01-02", "url": "https://assignmentcenter.uspto.gov/x",
           "source": "USPTO Open Data Portal", "independentAssignmentVerified": True}
    manual = {**rec, "source": "manual export"}
    prev = {"companies": [{"officialAssignments": [rec, manual], "securityInterests": []}],
            "api": {"applicationsFound": {"IRD": 36}, "lastLiveLookup": "2026-11-23"}}
    from uspto_assignment_validation import cached_api_records
    recs, counts, last = cached_api_records(prev)
    assert recs == [{k: v for k, v in rec.items() if k != "independentAssignmentVerified"}]
    assert counts == {"IRD": 36} and last == "2026-11-23"


def test_applicant_match_needs_every_company_word():
    import uspto_assignment_validation as u
    assert u.applicant_words("Tempus AI, Inc.") <= u.applicant_words("TEMPUS AI, INC.")
    assert not u.applicant_words("Tempus AI, Inc.") <= u.applicant_words("TEMPUS STEEL LTD")
