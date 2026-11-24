from datetime import date

from key_people import build, display_name, merge_roster, pubmed_author


def test_names_and_pubmed_author():
    assert display_name("Gibson Christopher C") == "Christopher C Gibson"
    assert display_name("Smith John Jr.") == "John Smith"
    assert pubmed_author("Christopher C Gibson") == "Gibson CC"


def test_roster_keeps_latest_title_and_flags_roles():
    raw = [{"cik": "1", "filed": "2026-01-02", "ownerCik": "9", "name": "Roe Jane", "relationship": "Officer", "title": "SVP"},
           {"cik": "1", "filed": "2026-06-02", "ownerCik": "9", "name": "Roe Jane", "relationship": "Officer", "title": "Chief Scientific Officer"},
           {"cik": "1", "filed": "2026-03-02", "ownerCik": "8", "name": "Doe John", "relationship": "Director", "title": ""}]
    r = merge_roster(raw)["1"]
    jane = next(p for p in r if p["name"] == "Jane Roe")
    john = next(p for p in r if p["name"] == "John Doe")
    assert jane["title"] == "Chief Scientific Officer" and jane["key"] and jane["scientist"] and jane["firstSeen"] == "2026-01-02"
    assert not john["key"]  # a director with no key title is not tracked


def test_build_adds_founders_and_research_roles_get_pubmed():
    roster = {"1": [{"name": "Ann Lee", "title": "Chief Executive Officer", "key": True, "scientist": False},
                    {"name": "Jane Roe", "title": "Chief Scientific Officer", "key": True, "scientist": True}]}
    founders = [{"ticker": "TST", "person": "Bob Ray", "url": "https://www.sec.gov/x"}]
    asked = []
    def fetch(url):
        asked.append(url)
        if "esearch" in url:
            return {"esearchresult": {"count": "2", "idlist": ["11"]}}
        return {"result": {"11": {"title": "A paper", "source": "Nature", "pubdate": "2025"}}}
    p = build({"TST": ("1", "Test Bio Inc")}, roster, founders, {}, fetch, date(2026, 11, 24))
    people = p["companies"]["TST"]["people"]
    assert [x["name"] for x in people][0] == "Ann Lee"  # CEO first
    assert {x["name"] for x in people if "papers" in x} == {"Ann Lee", "Jane Roe", "Bob Ray"}  # CEO searched too
    assert people[1]["papers"]["count"] == 2 and "linkedin.com/search" in people[0]["linkedin"]
    from urllib.parse import unquote_plus
    assert all("\"Test Bio\"[Affiliation]" in unquote_plus(u) or "esummary" in u for u in asked)


def test_founder_merges_with_roster_entry_despite_middle_names_and_accents():
    from key_people import person_key
    assert person_key("Carl L. G. Hansen") == person_key("Carl Hansen")
    assert person_key("Véronique Lecault") == person_key("Veronique Lecault")
    roster = {"1": [{"name": "Carl L. G. Hansen", "title": "Chief Executive Officer", "key": True, "scientist": False}]}
    p = build({"T": ("1", "AbCellera Biologics")}, roster, [{"ticker": "T", "person": "Carl Hansen", "url": "u"}], {},
              lambda url: {"esearchresult": {"count": "0", "idlist": []}}, date(2026, 11, 24))
    people = p["companies"]["T"]["people"]
    assert len(people) == 1 and people[0]["founder"] and "papers" in people[0]  # a CEO is searched too
