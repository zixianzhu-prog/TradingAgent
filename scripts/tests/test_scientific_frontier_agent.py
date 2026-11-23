from datetime import date

import scientific_frontier_agent as sf


COMPANIES = [{"ticker": "SDGR", "company": "Schrodinger", "aliases": ["schrodinger"],
              "exposure": "computational chemistry drug discovery software", "tokens": {"computational", "chemistry", "drug", "discovery", "software"}}]
CONFIG = {"lookback_days": 30, "history_days": 180, "per_query": 5,
          "target_institutions": ["Massachusetts Institute of Technology"],
          "themes": [{"id": "drug", "label": "Drug discovery", "query": "drug discovery", "keywords": ["drug discovery"]}]}


def fake_fetch(url, data=None, timeout=40):
    if "openalex" in url:
        return {"results": [{
            "id": "https://openalex.org/W1", "doi": "https://doi.org/10.1/test", "display_name": "Schrodinger computational chemistry discovery",
            "publication_date": "2026-11-01", "type": "article", "cited_by_count": 8, "is_retracted": False,
            "abstract_inverted_index": {"drug": [0], "discovery": [1]}, "topics": [], "keywords": [],
            "awards": [{"funder_id": "F1", "funder_display_name": "NIH", "funder_award_id": "A1"}],
            "primary_location": {"source": {"display_name": "Journal"}},
            "authorships": [{"author": {"id": "A1", "display_name": "Ada", "orcid": "O1"},
                             "raw_affiliation_strings": ["Massachusetts Institute of Technology"],
                             "institutions": [{"id": "I1", "display_name": "Massachusetts Institute of Technology", "ror": "R1", "country_code": "US", "type": "education"}]}]
        }]}
    if "esearch" in url:
        return {"esearchresult": {"idlist": ["123"]}}
    return {"result": {"123": {"uid": "123", "title": "Drug paper", "pubdate": "2026 Nov", "authors": [{"name": "Ada A"}], "fulljournalname": "Journal"}}}


def test_build_creates_auditable_science_graph_and_direct_company_link():
    payload = sf.build(CONFIG, COMPANIES, fetch=fake_fetch, today=date(2026, 11, 20))
    assert payload["summary"] == {"works": 1, "pubmedRecords": 1, "directCompanyWorks": 1, "targetInstitutionWorks": 1, "errors": 0}
    work = payload["works"][0]
    assert work["authors"][0]["name"] == "Ada"
    assert work["institutions"][0]["name"] == "Massachusetts Institute of Technology"
    assert work["companyLinks"][0]["relation"] == "direct_mention"
    assert any(edge["relation"] == "AUTHORED_BY" for edge in payload["graph"]["edges"])
    assert any(edge["source"] == "A1" and edge["target"] == "I1" and edge["relation"] == "AFFILIATED_WITH"
               for edge in payload["graph"]["edges"])
    assert any(edge["relation"] == "FUNDED_BY" for edge in payload["graph"]["edges"])
    assert any(edge["relation"] == "DIRECTLY_MENTIONS" for edge in payload["graph"]["edges"])


def test_technology_overlap_is_candidate_not_direct_evidence():
    links = sf.candidate_company_links("computational chemistry software improves drug discovery", COMPANIES, set())
    assert links[0]["relation"] == "technology_overlap_candidate"
    graph = sf.relationship_graph([{"id": "W", "theme": "drug", "themeLabel": "Drug", "title": "T",
                                    "authors": [], "institutions": [], "funders": [], "companyLinks": links}])
    edge = next(edge for edge in graph["edges"] if edge["relation"] == "TECHNOLOGY_OVERLAP_CANDIDATE")
    assert edge["commercialEvidence"] is False


def test_ticker_substrings_do_not_create_false_direct_links():
    ntra = [{"ticker": "NTRA", "company": "Natera", "aliases": ["ntra", "natera"],
             "exposure": "genomics", "tokens": {"genomics"}}]
    assert sf.direct_company_links("central nervous system", [], ntra) == []


def test_network_errors_are_explicit_and_do_not_crash():
    def broken(*_args, **_kwargs):
        raise OSError("offline")
    payload = sf.build(CONFIG, COMPANIES, fetch=broken, today=date(2026, 11, 20))
    assert payload["summary"]["errors"] == 2 and payload["works"] == []


def test_generic_words_alone_do_not_link_a_company():
    nvda = [{"ticker": "NVDA", "company": "NVIDIA", "aliases": ["nvidia"],
             "exposure": "accelerated computing, software libraries and model infrastructure used across medical imaging and drug discovery",
             "tokens": sf.tokens("accelerated computing software libraries model infrastructure used medical imaging drug discovery")}]
    text = "Natural bioactive compounds accelerated drug discovery for envenomation; the model was used in imaging"
    assert sf.candidate_company_links(text, nvda, set()) == []
