from datetime import date

import management_radar as mr


WATCH = {"companies": [
    {"ticker": "BIO", "aliases": ["Bio Systems"], "events": []},
    {"ticker": "SAFE", "aliases": ["Safe Health"], "events": [
        {"type": "governance", "date": "2026-11-10", "label": "Board investigation",
         "gates": ["management_governance", "counter_thesis"]}
    ]},
]}


def test_ceo_departure_reopens_governance_and_earnings():
    event = mr.departure_event({"date": "2026-11-01", "sentence": "The Chief Executive Officer resigned immediately.", "url": "u"}, "BIO")
    assert event["severity"] == "critical"
    assert {"management_governance", "counter_thesis", "earnings_validation"} <= set(event["affectedGates"])


def test_form4_sale_needs_context_and_purchase_is_supportive():
    base = {"date": "2026-11-01", "ticker": "BIO", "owner": "A", "roles": ["CEO"], "shares": 10, "value": 100, "url": "u"}
    assert mr.transaction_event({**base, "code": "S"})["interpretation"] == "context-needed"
    assert mr.transaction_event({**base, "code": "P"})["interpretation"] == "supportive"


def test_build_prioritizes_material_events_without_calling_sales_bearish():
    early = {"people": {"keyDepartures": [
        {"company": "Bio Systems Inc.", "date": "2026-11-01", "sentence": "The Chief Scientific Officer resigned.", "url": "8k"}
    ]}}
    form4 = {"filings": [{"ticker": "BIO", "issuer": "Bio Systems, Inc.", "owner": "Alex", "roles": ["CEO"]}],
             "marketTransactions": [{"ticker": "BIO", "date": "2026-11-02", "owner": "Alex", "roles": ["CEO"],
                                     "code": "S", "shares": 100, "value": 1000, "url": "f4"}]}
    payload = mr.build(early, form4, WATCH, today=date(2026, 11, 20))
    bio = next(row for row in payload["companies"] if row["ticker"] == "BIO")
    assert bio["attention"] == "urgent-revalidate"
    assert bio["summary"]["salesNeedingContext"] == 1
    assert bio["summary"]["pendingForm4Reads"] == 0
    assert next(e for e in bio["timeline"] if e["type"] == "insider_transaction")["severity"] == "informational"
    safe = next(row for row in payload["companies"] if row["ticker"] == "SAFE")
    assert safe["attention"] == "urgent-revalidate"
