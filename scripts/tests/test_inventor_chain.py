import inventor_chain as ic


def test_search_name_uses_first_and_last():
    assert ic.search_name("Carl L. G. Hansen") == "Carl Hansen"
    assert ic.search_name("Eric P Lefkofsky") == "Eric Lefkofsky"
    assert ic.search_name("Sara Kenkare-Mitra") == "Sara Kenkare-Mitra"


def test_classify_company_licensor_other():
    lic = ["University of Pennsylvania", "University of Florida Research Foundation"]
    assert ic.classify("Tempus AI, Inc.", "Tempus AI, Inc.", []) == ("company", None)
    assert ic.classify("THE TRUSTEES OF THE UNIVERSITY OF PENNSYLVANIA", "Opus Genetics, Inc.", lic) == ("licensor", "University of Pennsylvania")
    assert ic.classify("Stanford University", "Opus Genetics, Inc.", lic) == ("other", None)


def test_build_counts_only_confirmed_links():
    apps = {"Jane Roe": [{"number": "1", "applicant": "Acme Bio Inc", "title": "t1", "filed": "2024", "patent": None},
                         {"number": "2", "applicant": "Regents of the University of California", "title": "t2", "filed": "2019", "patent": "X"},
                         {"number": "3", "applicant": "Other Corp", "title": "t3", "filed": "2020", "patent": None}]}
    out = ic.build({"ACME": {"Jane Roe": {"founder"}}}, {"ACME": "Acme Bio, Inc."}, {"ACME": ["University of California"]},
                   lambda person: apps[person])
    row = out["companies"]["ACME"]["people"][0]
    assert (row["companyPatents"], row["licensorPatents"], row["otherNameMatches"]) == (1, 1, 1)
    assert out["summary"]["labToCompanyLinks"] == 1 and row["licensors"] == ["University of California"]


def test_same_person_two_spellings_merged():
    kp = {"companies": {"TEM": {"people": [{"name": "Eric P Lefkofsky", "founder": True}]}}}
    fo = {"links": [{"ticker": "TEM", "relation": "founder", "person": "Eric Lefkofsky"}]}
    out = ic.people_by_company(kp, fo, {})
    assert list(out["TEM"]) == ["Eric P Lefkofsky"] and out["TEM"]["Eric P Lefkofsky"] == {"founder", "founder (10-K)"}
