import pharma_deals_ind as pdi


def test_pharma_filers_are_dropped_so_the_row_is_the_smaller_partner():
    assert pdi.is_pharma_filer("ELI LILLY & Co")
    assert pdi.is_pharma_filer("Genentech, Inc.")
    assert not pdi.is_pharma_filer("Monte Rosa Therapeutics, Inc.")


def test_report_lists_only_confirmed_items_with_verified_values():
    payload = {"window": ["2026-08-19", "2026-11-17"],
               "summary": {"indFilings": 2, "dealFilings": 1, "indConfirmed": 1, "dealsConfirmed": 1, "aiPlatformDeals": 1},
               "filings": [
                   {"kind": "deal", "filed": "2026-11-01", "company": "Small Bio", "ticker": "SMB", "url": "u1", "inUniverse": False,
                    "smallCap": {"marketCapM": 300, "stage": "preparation", "stageDetail": "phase 1"},
                    "facts": {"isNewDeal": True, "partner": {"value": "Novartis"}, "upfrontUsdM": {"value": "150"},
                              "milestonesUsdM": {"value": "2,000"}, "scope": {"value": "three targets"}, "aiPlatformDeal": {"value": "yes"}}},
                   {"kind": "ind", "filed": "2026-10-01", "company": "Old News", "ticker": "OLD", "url": "u2", "inUniverse": False,
                    "smallCap": None, "facts": {"isIndClearance": False}},
                   {"kind": "ind", "filed": "2026-10-02", "company": "New Drug Co", "ticker": "NDC", "url": "u3", "inUniverse": True,
                    "smallCap": None, "facts": {"isIndClearance": True, "drug": {"value": "NDC-101"}, "indication": {"value": None},
                                                "nextTrial": {"value": "Phase 1"}, "modality": {"value": "antibody"}}}]}
    text = pdi.report(payload)
    assert "Novartis" in text and "$300M · preparation" in text
    assert "NDC-101" in text and "Old News" not in text


def test_dedupe_keeps_earliest_mention():
    import pharma_deals_ind as m
    fact = lambda v: {"value": v}
    rows = [
        {"kind": "deal", "ticker": "ZYME", "filed": "2026-11-09", "url": "b", "facts": {"isNewDeal": True, "partner": fact("Roche")}},
        {"kind": "deal", "ticker": "ZYME", "filed": "2026-10-23", "url": "a", "facts": {"isNewDeal": True, "partner": fact("Roche")}},
        {"kind": "deal", "ticker": "ALEC", "filed": "2026-11-05", "url": "d", "facts": {"isNewDeal": True, "partner": fact("Genentech (Roche Group)")}},
        {"kind": "deal", "ticker": "ALEC", "filed": "2026-10-05", "url": "c", "facts": {"isNewDeal": True, "partner": fact("Genentech (Roche)")}},
        {"kind": "ind", "ticker": "ACET", "filed": "2026-09-08", "url": "e", "facts": {"isIndClearance": True, "drug": fact("ADI-212")}},
        {"kind": "ind", "ticker": "ACET", "filed": "2026-11-05", "url": "f", "facts": {"isIndClearance": True, "drug": None}},
        {"kind": "ind", "ticker": "ACET", "filed": "2026-11-06", "url": "g", "facts": {"isIndClearance": True, "drug": fact("ADI-999")}},
    ]
    m.dedupe(rows)
    dup = {r["url"]: r.get("duplicateOf") for r in rows}
    assert dup == {"a": None, "b": "a", "c": None, "d": "c", "e": None, "f": "e", "g": None}


def test_history_keeps_confirmed_events_that_left_the_window():
    from datetime import date
    from pharma_deals_ind import carry_history
    prev = {"filings": [
        {"url": "a", "kind": "deal", "filed": "2026-08-01", "facts": {"isNewDeal": True}},
        {"url": "b", "kind": "deal", "filed": "2026-08-02", "facts": {"isNewDeal": False}},
        {"url": "c", "kind": "ind", "filed": "2026-08-03", "facts": {"isIndClearance": {"value": True}}, "duplicateOf": "x"},
        {"url": "d", "kind": "ind", "filed": "2026-10-01", "facts": {"isIndClearance": True}}],
        "history": [{"url": "e", "kind": "ind", "filed": "2022-01-01", "facts": {"isIndClearance": True}}]}
    out = carry_history(prev, [{"url": "d"}], "2026-08-25", date(2026, 11, 23))
    assert [r["url"] for r in out] == ["a"]  # b unconfirmed, c duplicate, d still in window, e older than 3 years
