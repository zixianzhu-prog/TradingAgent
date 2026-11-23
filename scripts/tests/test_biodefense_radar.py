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
    p = br.build(date(2026, 11, 23), sec, fetch=fake, get=lambda url: None)
    by = {c["recipient"]: c for c in p["contracts"]}
    assert len(p["contracts"]) == 2  # under $5M dropped
    assert by["SCYNEXIS INC"]["ticker"] == "SCYX"
    assert by["GLAXOSMITHKLINE, LLC"]["ticker"] == "GSK"
    assert p["outbreaks"][0]["fundedResponders"] == ["GSK"] and len(p["outbreaks"]) == 1


def test_han_probe_stops_after_two_missing_and_reads_dates():
    pages = {
        531: "<title>Domestically Acquired Cyclosporiasis Cases | HAN | CDC</title>Distributed via the CDC Health Alert Network <br> July 14, 2026",
        533: '<title>Ebola Disease Outbreak Update | HAN | CDC</title><meta name="cdc:first_published" content="September 10, 2026">',
    }
    asked = []
    def get(url):
        n = int(url[-10:-5])
        asked.append(n)
        return pages.get(n)
    rows, latest = br.han_alerts(date(2026, 1, 1), 531, get, lookback=2)
    assert latest == 533 and max(asked) == 535  # 534 and 535 missing -> stop
    assert [(r["number"], r["date"]) for r in rows] == [(533, "2026-09-10"), (531, "2026-07-14")]
    assert rows[0]["pathogens"] == ["ebola"] and rows[0]["title"] == "Ebola Disease Outbreak Update"
