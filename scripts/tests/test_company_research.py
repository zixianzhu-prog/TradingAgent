from datetime import date

from company_research import build, matches


def test_name_matching_is_strict():
    assert matches("Tempus AI", "Tempus Labs (United States)")
    assert matches("Recursion Pharmaceuticals", "Recursion (United States)")
    assert not matches("Prime Medicine, Inc.", "Prime Healthcare Services (United States)")
    assert not matches("Alector, Inc.", "Alexion Pharmaceuticals (United States)")


def test_build_requires_unique_match_and_counts_company_authors():
    def fetch(url):
        if "/institutions?" in url:
            if "tempus" in url:
                return {"results": [{"display_name": "Tempus Labs (United States)", "id": "https://openalex.org/I1", "country_code": "US"}]}
            return {"results": [{"display_name": "Foo (United States)", "id": "https://openalex.org/I2"},
                                {"display_name": "Foo Labs (Germany)", "id": "https://openalex.org/I3"}]}
        return {"meta": {"count": 12}, "results": [{"display_name": "A paper", "doi": "https://doi.org/10.1/x", "cited_by_count": 40,
                                                   "publication_date": "2025-01-02", "authorships": [
            {"author": {"display_name": "Jane Roe"}, "institutions": [{"id": "https://openalex.org/I1"}]},
            {"author": {"display_name": "Outside Person"}, "institutions": [{"id": "https://openalex.org/I9"}]}]}]}
    p = build({"TEM": "Tempus AI", "FOO": "Foo Therapeutics"}, fetch, date(2026, 11, 23))
    assert list(p["companies"]) == ["TEM"]  # two Foo candidates: ambiguous, skipped
    c = p["companies"]["TEM"]
    assert c["verified"] and c["recentWorks"] == 12 and c["topWorks"][0]["companyAuthors"] == ["Jane Roe"]


def test_extra_institution_word_rejects():
    assert not matches("Opus Genetics, Inc.", "Opus Technologies (United States)")


def test_budget_exhausted_keeps_previous_and_cached_ids_skip_search():
    from company_research import BudgetExhausted
    prev = {"companies": {"TEM": {"company": "Tempus AI", "openalexId": "https://openalex.org/I1", "institution": "Tempus Labs",
                                  "recentWorks": 300, "verified": True, "topWorks": []},
                          "RXRX": {"company": "Recursion", "openalexId": "https://openalex.org/I2", "institution": "Recursion",
                                   "recentWorks": 70, "verified": True, "topWorks": []}}}
    calls = []
    def fetch(url):
        calls.append(url)
        if "I2" in url:
            raise BudgetExhausted()
        return {"meta": {"count": 310}, "results": []}
    p = build({"TEM": "Tempus AI", "RXRX": "Recursion"}, fetch, date(2026, 11, 23), prev)
    assert not any("/institutions?" in u for u in calls)  # cached ids: no search
    assert p["companies"]["RXRX"]["recentWorks"] == 70  # kept from last run
    assert "budget" in p["summary"]["errors"][0]
