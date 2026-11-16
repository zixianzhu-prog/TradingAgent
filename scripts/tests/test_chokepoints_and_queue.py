from datetime import date

import ai_medicine_chokepoints as choke
import prepare_serenity_queue as queue


def hit(name, sic, adsh):
    return {"_id": f"{adsh}:d.htm", "_source": {"display_names": [name], "sics": [sic], "form": "10-K", "items": [],
                                                 "file_type": "10-K", "file_date": "2026-02-01", "adsh": adsh}}


def test_dependents_exclude_supplier_itself_and_non_health():
    def fetch(url, agent):
        if "sole" in url or "single" in url:
            hits = [hit("GRAIL, Inc.  (GRAL)  (CIK 0001699031)", "8071", "x1"),
                    hit("ILLUMINA, INC.  (ILMN)  (CIK 0001110803)", "3826", "x2"),
                    hit("Burger Co  (BRGR)  (CIK 0000000004)", "5810", "x3")]
        else:
            hits = []
        return {"hits": {"hits": hits, "total": {"value": len(hits) if hits else 10}}}
    payload = choke.build(date(2026, 11, 15), {"companies": [{"ticker": "GRAL"}]}, {"devices": [{"panel": "Radiology"}]}, fetch=fetch)
    node = next(n for n in payload["nodes"] if n["supplier"] == "Illumina")
    assert node["healthDependents"] == 1 and node["aiMedicineDependents"] == 1
    assert node["examples"][0]["ticker"] == "GRAL"
    # Numerator and denominator both count every filer, as the denominator (all filings naming the
    # supplier) cannot be split by industry: 3 distinct filings with dependence wording / 10 mentions.
    assert node["dependenceShare"] == 0.3


def test_xbrl_passage_reports_quarter_and_year_ago_growth():
    facts = {"entityName": "Heartflow, Inc.", "facts": {"us-gaap": {
        "RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": [
            {"val": 46276000, "start": "2025-07-01", "end": "2025-09-30", "form": "10-Q", "filed": "2025-11-10", "accn": "a"},
            {"val": 72857000, "start": "2026-07-01", "end": "2026-09-30", "form": "10-Q", "filed": "2026-11-12", "accn": "b"},
            {"val": 200000000, "start": "2025-10-01", "end": "2026-09-30", "form": "10-K", "filed": "2026-11-12", "accn": "c"},
        ]}},
        "CashAndCashEquivalentsAtCarryingValue": {"units": {"USD": [{"val": 31649000, "end": "2026-09-30", "form": "10-Q", "filed": "2026-11-12", "accn": "b"}]}},
    }}}
    doc = queue.xbrl_passage("HTFL", "1464521", fetch=lambda url, agent: facts)
    assert "72,857,000 for 2026-07-01 to 2026-09-30" in doc["text"]
    assert "+57.4%" in doc["text"]
    assert "Cash and equivalents" in doc["text"] and doc["primary"] is True
    assert doc["url"].endswith("CIK0001464521.json")


def test_cik_is_read_from_filing_url():
    assert queue.cik_from({"filings": [{"url": "https://www.sec.gov/Archives/edgar/data/1464521/0001/x.htm"}]}) == "1464521"
    assert queue.cik_from({"filings": []}) is None


def test_xbrl_figures_share_one_period_and_label_year_to_date():
    usd = lambda rows: {"units": {"USD": rows}}
    facts = {"entityName": "Wave", "facts": {"us-gaap": {
        "RevenueFromContractWithCustomerExcludingAssessedTax": usd([
            {"val": 13158000, "start": "2026-07-01", "end": "2026-09-30", "form": "10-Q", "filed": "2026-10-27", "accn": "q3"}]),
        "NetCashProvidedByUsedInOperatingActivities": usd([
            {"val": -59553000, "start": "2026-01-01", "end": "2026-03-31", "form": "10-Q", "filed": "2026-04-28", "accn": "q1"},
            {"val": -170000000, "start": "2026-01-01", "end": "2026-09-30", "form": "10-Q", "filed": "2026-10-27", "accn": "q3"}]),
        "NetIncomeLoss": usd([{"val": -5, "start": "2026-01-01", "end": "2026-03-31", "form": "10-Q", "filed": "2026-04-28", "accn": "q1"}]),
    }}}
    text = queue.xbrl_passage("WVE", "1631574", fetch=lambda url, agent: facts)["text"]
    assert "quarter ended 2026-09-30" in text
    assert "-170,000,000 for 2026-01-01 to 2026-09-30 (year-to-date total as reported)" in text
    assert "-59,553,000" not in text  # the Q1 figure is not borrowed
    assert "Not reported for the quarter ended 2026-09-30: Net income (loss)" in text
