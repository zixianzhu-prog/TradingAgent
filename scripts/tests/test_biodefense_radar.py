from datetime import date

import biodefense_radar as br


def fake(url, body=None, agent=""):
    if "usaspending" in url:
        return {"results": [
            {"Action Date": "2026-09-25", "Recipient Name": "SCYNEXIS INC", "Transaction Amount": 18_500_000,
             "Transaction Description": "ADVANCE SCY-247, A NOVEL ANTIFUNGAL", "Award ID": "A1", "generated_internal_id": "G1"},
            {"Action Date": "2026-09-25", "Recipient Name": "GLAXOSMITHKLINE, LLC", "Transaction Amount": 18_200_000,
             "Transaction Description": "RELENZA (ZANAMIVIR) INFLUENZA", "Award ID": "A2", "generated_internal_id": "G2"},
            {"Action Date": "2026-09-25", "Recipient Name": "SMALL LLC", "Transaction Amount": 1_000_000,
             "Transaction Description": "tiny", "Award ID": "A3", "generated_internal_id": "G3"}]}
    return {"value": [{"PublicationDate": "2026-11-20T00:00:00Z", "Title": "Avian influenza A(H5N1) - X", "ItemDefaultUrl": "/2026-DON1"},
                      {"PublicationDate": "2025-01-01T00:00:00Z", "Title": "Old", "ItemDefaultUrl": "/old"}]}


def test_contracts_match_tickers_parents_and_outbreaks():
    sec = {"0": {"ticker": "SCYX", "title": "SCYNEXIS INC", "cik_str": 1}}
    p = br.build(date(2026, 11, 23), sec, fetch=fake)
    by = {c["recipient"]: c for c in p["contracts"]}
    assert len(p["contracts"]) == 2  # under $5M dropped
    assert by["SCYNEXIS INC"]["ticker"] == "SCYX"
    assert by["GLAXOSMITHKLINE, LLC"]["ticker"] == "GSK"
    assert p["outbreaks"][0]["fundedResponders"] == ["GSK"] and len(p["outbreaks"]) == 1
