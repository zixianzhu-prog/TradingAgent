import science_founders as sf

TEXT = ("Dr. Jane Roe is our co-founder and Chief Scientific Officer. We entered into an exclusive license agreement "
        "with the Massachusetts Institute of Technology in 2019. We also license software from Acme Corp under a license agreement.")


def test_sentences_pick_founder_and_license_lines():
    out = sf.sentences(TEXT)
    assert any("co-founder" in s for s in out) and any("Massachusetts Institute" in s for s in out)


def test_verified_drops_invented_quotes_and_company_licenses():
    links = [{"name": "Jane Roe", "kind": "person", "relation": "founder", "quote": "Dr. Jane Roe is our co-founder and Chief Scientific Officer."},
             {"name": "Massachusetts Institute of Technology", "kind": "institution", "relation": "license",
              "quote": "We entered into an exclusive license agreement with the Massachusetts Institute of Technology in 2019."},
             {"name": "Acme Corp", "kind": "institution", "relation": "license", "quote": "We also license software from Acme Corp under a license agreement."},
             {"name": "John Doe", "kind": "person", "relation": "founder", "quote": "John Doe founded the company."}]
    out = sf.verified(links, TEXT)
    assert [l["name"] for l in out] == ["Jane Roe", "Massachusetts Institute of Technology"]
    rows = sf.to_links("X", "u", out)
    assert rows[0]["relation"] == "founder" and rows[1]["relation"] == "license" and rows[1]["institution"].startswith("Massachusetts")


def test_openalex_requires_a_single_plausible_author():
    def fetch(url):
        return {"results": [
            {"id": "A1", "display_name": "Jane Roe", "works_count": 40, "last_known_institutions": [{"display_name": "Massachusetts Institute of Technology"}]},
            {"id": "A2", "display_name": "Jane Roe", "works_count": 30, "last_known_institutions": [{"display_name": "Some Other College"}]}]}
    assert sf.openalex_author("Jane Roe", None, fetch) is None  # two namesakes
    hit = sf.openalex_author("Jane Roe", "Massachusetts Institute of Technology", fetch)
    assert hit["openalexId"] == "A1" and hit["status"] == "candidate"


def test_partial_or_role_names_are_dropped():
    text = "Harpreet is our co-founder. Our Founder and Chief Scientist leads research."
    links = [{"name": "Harpreet", "kind": "person", "relation": "founder", "quote": "Harpreet is our co-founder."},
             {"name": "Founder and Chief Scientist (unnamed)", "kind": "person", "relation": "founder",
              "quote": "Our Founder and Chief Scientist leads research."}]
    assert sf.verified(links, text) == []
