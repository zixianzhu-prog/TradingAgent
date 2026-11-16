from datetime import date

import ai_medicine_universe_screen as screen_mod


def hit(name, sic, adsh, form="10-K"):
    return {"_id": f"{adsh}:d.htm", "_source": {"display_names": [name], "sics": [sic], "form": form, "items": [],
                                                 "file_type": form, "file_date": "2026-03-01", "adsh": adsh}}


AI_NATIVE = hit("HeartFlow, Inc.  (HTFL)  (CIK 0000000001)", "3841", "a1")
DRUG_MENTION = hit("Generic Pharma Inc  (GPX)  (CIK 0000000002)", "2834", "a2")
SPAC = hit("AI Health Acquisition Corp  (AIHC)  (CIK 0000000003)", "6770", "a3")
RESTAURANT = hit("Burger Co  (BRGR)  (CIK 0000000004)", "5810", "a4")
SOFTWARE_ONE = hit("Health Cloud Inc  (HCLD)  (CIK 0000000005)", "7372", "a5")
TINY = hit("Tiny Dx Inc  (TINY)  (CIK 0000000006)", "2835", "a6")


def fake_fetch(url, agent):
    q = url.split("q=")[1].split("&")[0]
    if "our" in q.lower():
        hits = [AI_NATIVE, TINY]  # only these describe AI as their own product
    elif "510" in q:
        hits = [AI_NATIVE, DRUG_MENTION, SPAC, RESTAURANT, SOFTWARE_ONE, TINY]  # software matches this pair only
    elif "radiology" in q:
        hits = [AI_NATIVE, DRUG_MENTION, SPAC, RESTAURANT, TINY]
    elif "drug" in q or "pathology" in q:
        hits = [AI_NATIVE, DRUG_MENTION, SPAC, TINY]
    else:
        hits = []
    return {"hits": {"hits": hits, "total": {"value": len(hits)}}}


def fake_prices(tickers):
    data = {"HTFL": {"advUsd": 50e6, "marketCapM": 4300}, "GPX": {"advUsd": 80e6, "marketCapM": 20000},
            "TINY": {"advUsd": 0.5e6, "marketCapM": 120}}
    return {t: data[t] for t in tickers if t in data}


def test_funnel_filters_each_stage():
    devices = [{"manufacturer": "Heartflow, Inc.", "device": "FFRct", "decisionDate": "01/01/2026", "fdaUrl": "u"}]
    result = screen_mod.screen(date(2026, 11, 15), devices, known={"HTFL", "NTRA"}, fetch=fake_fetch, prices=fake_prices)
    f = result["funnel"]
    assert f["filersFound"] == 6
    assert f["healthOperating"] == 3          # SPAC, restaurant and single-phrase software dropped
    assert f["ownProduct"] == 2                # pharma that only mentions AI is dropped
    assert f["investable"] == 1                # TINY fails cap and liquidity
    row = next(r for r in result["companies"] if r["ticker"] == "HTFL")
    assert row["fdaAiDevices"] == 1 and row["capBand"].startswith("Sweet spot") and row["bucketHint"].startswith("Asymmetric")
    assert row["shortlisted"] and row["deepReviewed"]
    assert result["knownNotFound"] == ["NTRA"]


def test_fda_aliases_map_subsidiaries():
    companies = {"GEHC": {"name": "GE HealthCare Technologies Inc."}, "IRTC": {"name": "iRhythm Holdings, Inc."}}
    devices = [{"manufacturer": "GE Medical Systems, LLC"}, {"manufacturer": "iRhythm Technologies, Inc."}, {"manufacturer": "Aidoc Medical, Ltd."}]
    matched = screen_mod.fda_counts(devices, companies)
    assert len(matched["GEHC"]) == 1 and len(matched["IRTC"]) == 1 and "Aidoc" not in str(dict(matched))


def test_cap_bands_follow_stock_selection_skill():
    assert screen_mod.cap_band(300).startswith("Micro")
    assert screen_mod.cap_band(2000).startswith("Sweet spot")
    assert screen_mod.cap_band(60000).startswith("Mega")
    assert screen_mod.bucket_hint(30000, {"Diagnostics", "Imaging & devices"}).startswith("Durable")


def test_fda_name_collisions_are_rejected_but_subsidiaries_match():
    companies = {
        "WVE": {"name": "Wave Life Sciences Ltd."}, "RYTM": {"name": "RHYTHM PHARMACEUTICALS, INC."},
        "CDIO": {"name": "Cardio Diagnostics Holdings, Inc."}, "DRTS": {"name": "Alpha Tau Medical Ltd."},
        "IMDX": {"name": "Insight Molecular Diagnostics Inc."}, "INBS": {"name": "INTELLIGENT BIO SOLUTIONS INC."},
        "SGHT": {"name": "Sight Sciences, Inc."},
        "IRTC": {"name": "iRhythm Holdings, Inc."}, "ATEC": {"name": "Alphatec Holdings, Inc."},
        "BRKR": {"name": "BRUKER CORP"}, "NNOX": {"name": "Nano-X Imaging Ltd."}, "PRCT": {"name": "PROCEPT BioRobotics Corp"},
    }
    makers = ["Wave Neuroscience", "Rhythm Al, Ltd", "Cardio-Phoenix Inc.", "Alpha Intelligence Manifolds, Inc.",
              "Insight Medical Systems, Inc.", "Intelligent Ultrasound Limited", "Sight Diagnostics Ltd.",
              "iRhythm Technologies, Inc.", "Alphatec Spine, Inc.", "BRUKER DALTONICS, INC", "Nano-X AI Ltd.", "Procept BioRobotics"]
    matched = screen_mod.fda_counts([{"manufacturer": m} for m in makers], companies)
    assert set(matched) == {"IRTC", "ATEC", "BRKR", "NNOX", "PRCT"}
