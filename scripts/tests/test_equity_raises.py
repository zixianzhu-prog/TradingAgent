from datetime import date

from equity_raises import raised


def fact(start, end, val, form="10-K", filed="2026-02-01", accn="0001-26-000001"):
    return {"start": start, "end": end, "val": val, "form": form, "filed": filed, "accn": accn}


def test_annual_plus_ytd_largest_tag_per_period():
    facts = {"cik": 123, "facts": {"us-gaap": {
        "ProceedsFromIssuanceOfCommonStock": {"units": {"USD": [
            fact("2024-01-01", "2024-12-31", 50_000_000),
            fact("2025-01-01", "2025-12-31", 20_000_000),
            fact("2026-01-01", "2026-03-31", 5_000_000, "10-Q"),
            fact("2026-01-01", "2026-09-30", 30_000_000, "10-Q"),
            fact("2023-01-01", "2023-12-31", 99_000_000)]}},  # outside the window
        "ProceedsFromIssuanceOfPrivatePlacement": {"units": {"USD": [
            fact("2025-01-01", "2025-12-31", 25_000_000)]}}}}}  # same period: largest wins, not summed
    r = raised(facts, date(2026, 11, 23))
    assert [(p["end"], p["usdM"]) for p in r["periods"]] == [("2024-12-31", 50.0), ("2025-12-31", 25.0), ("2026-09-30", 30.0)]
    assert r["totalUsdM"] == 105.0
    assert r["periods"][0]["url"] == "https://www.sec.gov/Archives/edgar/data/123/000126000001/"


def test_option_exercises_and_instant_facts_ignored():
    facts = {"cik": 1, "facts": {"us-gaap": {
        "ProceedsFromStockOptionsExercised": {"units": {"USD": [fact("2025-01-01", "2025-12-31", 9_000_000)]}},
        "ProceedsFromIssuanceOfCommonStock": {"units": {"USD": [{"end": "2025-06-09", "val": 1, "form": "10-Q"}]}}}}}
    assert raised(facts, date(2026, 11, 23)) == {"totalUsdM": 0, "periods": []}


def test_specific_tag_beats_generic_shelf_capacity():
    g = "ProceedsFromIssuanceOrSaleOfEquity"
    facts = {"cik": 1, "facts": {"us-gaap": {
        g: {"units": {"USD": [fact("2025-01-01", "2025-12-31", 400_000_000), fact("2026-01-01", "2026-09-30", 400_000_000, "10-Q"),
                              fact("2026-01-01", "2026-06-30", 400_000_000, "10-Q")]}},
        "ProceedsFromIssuanceOfPrivatePlacement": {"units": {"USD": [
            fact("2025-01-01", "2025-12-31", 173_000_000), fact("2026-01-01", "2026-09-30", 0, "10-Q")]}},
        "ProceedsFromIssuanceInitialPublicOffering": {"units": {"USD": [fact("2026-01-01", "2026-06-30", 13_000_000, "10-Q")]}}}}}
    r = raised(facts, date(2026, 11, 23))
    assert [(p["end"], p["usdM"]) for p in r["periods"]] == [("2025-12-31", 173.0), ("2026-06-30", 13.0)]
