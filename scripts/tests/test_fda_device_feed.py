import fda_device_feed as feed
from ai_medicine_universe_screen import core_tokens


def company(ticker, name, covered=True):
    return {"ticker": ticker, "name": name, "tokens": core_tokens(name), "covered": covered}


def decision(number, device, applicant, decided="2026-09-16", code="XYZ"):
    return {"id": number, "kind": "510k", "label": "510(k) clearance", "device": device, "applicant": applicant,
            "decisionDate": decided, "productCode": code, "panel": "", "url": f"https://fda.example/{number}"}


def test_normalise_drops_pma_supplements_and_spots_de_novo():
    assert feed.normalise({"pma_number": "P1", "supplement_number": "S001", "decision_date": "20261030"}, "pma") is None
    original = feed.normalise({"pma_number": "P2", "supplement_number": "", "trade_name": "X", "decision_date": "20261030"}, "pma")
    assert original["kind"] == "pma" and original["decisionDate"] == "2026-10-30"
    denovo = feed.normalise({"k_number": "DEN250044", "device_name": "Queen of Hearts", "decision_date": "2026-09-03"}, "510k")
    assert denovo["kind"] == "denovo" and "denovo.cfm" in denovo["url"]


def test_confidence_separates_named_ai_from_product_code_only():
    events = feed.build([decision("K1", "EEG Analysis Software", "Ceribell, Inc."),
                         decision("K2", "Voluson Expert 22", "GE Medical Systems Ultrasound", code="IYN"),
                         decision("K3", "Bone screw", "Acme Ortho", code="HWC")],
                        [company("CBLL", "Ceribell"), company("GEHC", "GE HealthCare Technologies")], {"IYN"}, set())
    by_id = {e["id"]: e for e in events}
    assert by_id["K1"]["aiConfidence"] == "high" and by_id["K1"]["ticker"] == "CBLL"
    assert by_id["K2"]["aiConfidence"] == "possible" and by_id["K2"]["ticker"] == "GEHC"  # subsidiary alias
    assert "K3" not in by_id
    rows = feed.article_rows(events)
    assert [r["key"] for r in rows] == ["openfda|K1"]  # possible-AI devices are not pushed as events
    assert "Ceribell receives FDA 510(k) clearance" in rows[0]["title"]


def test_market_wide_fallback_needs_every_core_word():
    listed = [company("BETA", "BETA Technologies, Inc.", False), company("BBNX", "Beta Bionics, Inc.", False)]
    events = feed.build([decision("K4", "iLet Dosing Decision Software", "Beta Bionics, Inc.")], [], set(), set(), listed)
    assert events[0]["ticker"] == "BBNX" and events[0]["newCandidate"] is True
    assert feed.article_rows(events) == []  # new candidates go to the screen, not the news engine


def test_public_time_uses_first_sighting_only_for_fresh_postings():
    fresh = {"decisionDate": "2026-11-01"}
    old = {"decisionDate": "2026-09-16"}
    assert feed.public_at(fresh, "2026-11-15T12:00:00+00:00") == "2026-11-15T12:00:00+00:00"
    assert feed.public_at(old, "2026-11-15T12:00:00+00:00").startswith("2026-09-16")
