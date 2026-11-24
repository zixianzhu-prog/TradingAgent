from datetime import date

from people_signal_tracker import build, changes, current_snapshot, person_key


def fixtures():
    people = {"companies": {"TST": {"company": "Test Bio", "people": [
        {"name": "Jane Q. Roe", "title": "Chief Scientific Officer", "lastSeen": "2026-11-01",
         "linkedin": "https://linkedin.test/jane", "papers": {"recent": [
             {"pmid": "1", "title": "First paper", "date": "2026", "url": "https://pubmed/1"}
         ]}}
    ], "departures": []}}}
    research = {"companies": {"TST": {"topWorks": [
        {"title": "Open paper", "doi": "https://doi.org/10/x", "published": "2026-10-01",
         "companyAuthors": ["Jane Roe"]}
    ]}}}
    return people, research


def test_person_identity_drops_middle_names_and_accents():
    assert person_key("Jane Q. Roe") == person_key("Jane Roe")
    assert person_key("Véronique Lecault") == person_key("Veronique Lecault")


def test_snapshot_joins_pubmed_and_openalex_by_person_and_company():
    people, research = fixtures()
    row = current_snapshot(people, research)["TST"]["people"]["jane roe"]
    assert {p["source"] for p in row["publications"]} == {"PubMed", "OpenAlex"}


def test_first_run_is_baseline_not_a_false_alert():
    people, research = fixtures()
    result = build(people, research, None, {"reviews": {}}, date(2026, 11, 24))
    assert result["events"] == []
    assert result["baselineInitialized"] is False
    assert result["summary"]["manualReviewsDue"] == 1
    assert result["summary"]["selectedThisWeek"] == 1
    assert result["manualLinkedinReview"][0]["priority"] == "high"


def test_later_run_detects_paper_role_and_departure_changes():
    people, research = fixtures()
    old_companies = current_snapshot(people, research)
    previous = {"companies": old_companies}
    person = people["companies"]["TST"]["people"][0]
    person["title"] = "Chief Executive Officer"
    person["papers"]["recent"].append({"pmid": "2", "title": "New paper", "date": "2026", "url": "https://pubmed/2"})
    people["companies"]["TST"]["departures"] = [{"url": "https://sec/8k", "date": "2026-11-24", "detail": "CSO departed"}]
    new_companies = current_snapshot(people, research)
    kinds = [row["type"] for row in changes(new_companies, previous)]
    assert kinds.count("role_change") == 1
    assert kinds.count("new_publication") == 1
    assert kinds.count("key_departure") == 1


def test_recent_manual_review_is_not_due():
    people, research = fixtures()
    manual = {"reviews": {"TST:jane roe": {"lastReviewedAt": "2026-11-22", "notes": "No change"}}}
    result = build(people, research, {"companies": current_snapshot(people, research)}, manual, date(2026, 11, 24))
    assert result["manualLinkedinReview"][0]["due"] is False
