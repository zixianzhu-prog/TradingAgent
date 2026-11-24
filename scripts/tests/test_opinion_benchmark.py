from datetime import date, datetime, timedelta, timezone

import opinion_benchmark as ob


CONFIG = {
    "publicOpinion": [{"id": "critic", "name": "Critic", "organization": "X", "role": "skeptic", "use": "counter"}],
    "capitalBehavior": [{"id": "ra", "name": "RA Capital", "aliases": ["RA Capital"]}]
}


def call(**changes):
    row = {"leaderId": "critic", "publishedAt": "2026-11-23T12:00:00+00:00",
           "discoveredAt": "2026-11-24T10:00:00+00:00", "ticker": "TEM", "stance": "negative",
           "confidence": 70, "sourceUrl": "https://example.com/view",
           "quote": "This is an exact source passage longer than twenty characters.",
           "thesis": "The claim is overstated.", "falsifiers": ["Revenue accelerates"]}
    row.update(changes)
    return row


def series(start_price, daily, days=300, start=date(2026, 11, 24)):
    out, price, day = {}, start_price, start
    while len(out) < days:
        if day.weekday() < 5:
            out[day.isoformat()] = price
            price *= 1 + daily
        day += timedelta(days=1)
    return out


def test_freeze_uses_discovery_or_freeze_not_old_publication():
    now = datetime(2026, 11, 24, 13, tzinfo=timezone.utc)
    rows, rejected = ob.freeze_calls([call()], CONFIG, [], now)
    assert not rejected and rows[0]["evaluationStart"] == "2026-11-24"
    assert rows[0]["citationStatus"] == "pending-verification"
    again, _ = ob.freeze_calls([call()], CONFIG, rows, now)
    assert again == []


def test_validation_rejects_missing_quote_and_future_discovery():
    now = datetime(2026, 11, 24, 13, tzinfo=timezone.utc)
    rows, rejected = ob.freeze_calls(
        [call(quote="short", discoveredAt="2026-11-25T10:00:00+00:00")], CONFIG, [], now
    )
    assert not rows
    assert any("quote" in error for error in rejected[0]["errors"])
    assert any("future" in error for error in rejected[0]["errors"])


def test_negative_call_scores_falling_stock_as_correct():
    now = datetime(2026, 11, 24, 13, tzinfo=timezone.utc)
    calls, _ = ob.freeze_calls([call()], CONFIG, [], now)
    scored = ob.score_calls(calls, {"XBI": series(100, 0), "TEM": series(10, -0.01)})
    row = next(item for item in scored if item["horizon"] == 20)
    assert row["directionCorrect"] is True and row["signedExcess"] > 0


def test_selected_funds_are_context_not_generic_owners():
    ownership = {"filings": [
        {"reportingPerson": "RA Capital Management", "ticker": "IRD", "filed": "2026-11-16", "form": "SC 13G",
         "percent": 6.6, "initial": True, "intentClass": "passive", "url": "https://sec.gov/a"},
        {"reportingPerson": "Vanguard", "ticker": "TEM", "filed": "2026-11-16", "form": "SC 13G",
         "percent": 5.1, "initial": True, "intentClass": "passive", "url": "https://sec.gov/b"}
    ]}
    rows = ob.specialist_signals(ownership, CONFIG)
    assert len(rows) == 1 and rows[0]["fund"] == "RA Capital"
