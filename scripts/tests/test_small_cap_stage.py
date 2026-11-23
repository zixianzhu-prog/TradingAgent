import small_cap_stage as scs


def _q(start, end, val, filed="2026-11-01", form="10-Q"):
    return {"start": start, "end": end, "val": val, "filed": filed, "form": form, "accn": "a"}


def test_stage_rule_preparation_growth_slowing():
    none = {"highestPhase": None}
    rev = lambda fy, q, yoy: {"fiscalYearM": fy, "quarterM": q, "quarterYoY": yoy, "fiscalYoY": None}
    assert scs.stage(rev(2, 0.5, None), {"highestPhase": 2}, "Drug discovery") == ("preparation", "phase 2")
    assert scs.stage(rev(0, None, None), none, "Drug discovery") == ("preparation", "preclinical")
    assert scs.stage(rev(0, None, None), none, "Imaging & devices") == ("preparation", "pre-commercial")
    assert scs.stage(rev(50, 15, 0.4), none, "Diagnostics")[0] == "growth"
    assert scs.stage(rev(50, 13, 0.05), none, "Diagnostics")[0] == "slowing"
    # partner money does not make a phase 2 drug developer a growth company
    phase, detail = scs.stage(rev(124, 30, 3.0), {"highestPhase": 2}, "Drug discovery")
    assert phase == "preparation" and "partner revenue" in detail


def test_revenue_profile_pools_tags_and_compares_same_quarter():
    facts = {"facts": {"us-gaap": {
        "Revenues": {"units": {"USD": [_q("2024-07-01", "2024-09-30", 10e6)]}},
        "RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": [
            _q("2025-07-01", "2025-09-30", 15e6), _q("2025-01-01", "2025-12-31", 55e6, form="10-K"),
            _q("2024-01-01", "2024-12-31", 40e6, form="10-K")]}}}}}
    rev = scs.revenue_profile(facts)
    assert rev["quarterYoY"] == 0.5 and rev["fiscalYearM"] == 55.0 and rev["fiscalYoY"] == 0.375


def test_shares_fall_back_to_weighted_basic_and_runway_counts_marketable_securities():
    facts = {"facts": {"us-gaap": {
        "WeightedAverageNumberOfSharesOutstandingBasic": {"units": {"shares": [_q("2026-07-01", "2026-09-30", 80e6)]}},
        "CashAndCashEquivalentsAtCarryingValue": {"units": {"USD": [{"end": "2026-09-30", "val": 50e6, "filed": "2026-11-01"}]}},
        "MarketableSecurities": {"units": {"USD": [{"end": "2026-09-30", "val": 70e6, "filed": "2026-11-01"}]}},
        "NetCashProvidedByUsedInOperatingActivities": {"units": {"USD": [_q("2026-01-01", "2026-09-30", -90e6)]}}}}}
    assert scs.shares_outstanding(facts) == (80e6, "2026-09-30")
    r = scs.runway(facts)
    assert r["cashM"] == 120.0 and r["burnPerMonthM"] == 10.0 and r["runwayMonths"] == 12.0


def test_signal_candidates_add_ind_and_deal_filers_once():
    fact = lambda v: {"value": v}
    signals = {"filings": [
        {"kind": "ind", "ticker": "MGX", "company": "Metagenomi", "filed": "2026-11-10", "url": "u1", "sicGroup": "Therapeutics & vaccines",
         "facts": {"isIndClearance": True, "drug": fact("MGX-001"), "indication": fact("Hemophilia A"), "nextTrial": fact("Phase 1/2")}},
        {"kind": "ind", "ticker": "MGX", "company": "Metagenomi", "filed": "2026-11-16", "url": "u2", "duplicateOf": "u1",
         "facts": {"isIndClearance": True}},
        {"kind": "deal", "ticker": "ZYME", "company": "Zymeworks", "filed": "2026-10-23", "url": "u3", "sicGroup": "Medical devices & supplies",
         "facts": {"isNewDeal": True, "partner": fact("Roche"), "upfrontUsdM": fact("55")}},
        {"kind": "deal", "ticker": "NOPE", "company": "x", "filed": "2026-10-23", "url": "u4", "facts": {"isNewDeal": False}},
        {"kind": "deal", "ticker": "SDGR", "company": "Schrodinger", "filed": "2026-10-23", "url": "u5", "facts": {"isNewDeal": True}},
    ]}
    rows = {r["ticker"]: r for r in scs.signal_candidates(signals, known={"SDGR"})}
    assert set(rows) == {"MGX", "ZYME"}
    assert rows["MGX"]["segment"] == "Drug developer" and len(rows["MGX"]["signals"]) == 1
    assert rows["MGX"]["signals"][0]["text"] == "IND cleared: MGX-001 · Hemophilia A · Phase 1/2"
    assert rows["ZYME"]["signals"][0]["text"] == "Deal with Roche, $55M upfront"
    assert rows["ZYME"]["segment"] == "Medical devices & supplies"   # only therapeutics filers get the drug-developer stage rule
    assert scs.stage({"fiscalYearM": 0, "quarterM": None, "quarterYoY": None, "fiscalYoY": None}, {"highestPhase": None}, "Drug developer") == ("preparation", "preclinical")
