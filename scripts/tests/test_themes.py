import json
from datetime import datetime, timedelta, timezone

import news_signal_engine as engine
import topic_exposure
from ai_medicine_topics import classify_topics

NOW = datetime(2026, 11, 15, 12, tzinfo=timezone.utc)
COMPANIES = [{"ticker": "RDNT", "name": "RadNet", "aliases": ["RadNet"]}, {"ticker": "SDGR", "name": "Schrodinger", "aliases": ["Schrodinger"]}]
EXPOSURE = {"topics": {"imaging": {"companies": {"RDNT": {"company": "RadNet", "strength": 1.0}, "BFLY": {"company": "Butterfly", "strength": 0.8}}},
                       "drug_discovery": {"companies": {"SDGR": {"company": "Schrodinger", "strength": 1.0}}}},
            "investable": {"BFLY"}}


def art(title, days_ago, source="STAT"):
    return {"source": source, "title": f"{title} - {source}", "url": f"https://e.example/{abs(hash((title, days_ago)))}", "content": "", "at": NOW - timedelta(days=days_ago)}


def test_topic_rules():
    assert "imaging" in classify_topics("Deep learning reads chest X-ray images as well as radiologists")
    assert "imaging" not in classify_topics("Hospital opens new MRI suite")  # imaging news without AI
    assert "ai_regulation" not in classify_topics("Big pharma tempers AI drug hype as investments surge without FDA wins")
    assert "ai_regulation" in classify_topics("FDA issues draft guidance on AI-enabled device software functions")
    assert "liquid_biopsy" in classify_topics("Blood test for multi-cancer early detection meets endpoint")


def test_heat_needs_rise_over_baseline():
    steady = [art(f"Deep learning for chest X-ray study {i}", d, src) for i, (d, src) in enumerate([(2, "medRxiv"), (3, "STAT"), (9, "medRxiv"), (10, "STAT"), (16, "medRxiv"), (17, "STAT"), (23, "medRxiv"), (24, "STAT")])]
    themes = engine.extract_themes(COMPANIES, steady, NOW, EXPOSURE)
    assert themes["imaging"]["heat"] <= 0.6 and not themes["imaging"]["material"]
    rising = [art(f"AI model for chest X-ray triage {i}", 1 + i % 5, ["medRxiv", "STAT", "Reuters"][i % 3]) for i in range(6)]
    themes = engine.extract_themes(COMPANIES, rising, NOW, EXPOSURE)
    assert themes["imaging"]["material"] and themes["imaging"]["heat"] > 1
    assert themes["imaging"]["uncovered"][0]["ticker"] == "BFLY"


def test_company_named_articles_are_not_theme_articles():
    themes = engine.extract_themes(COMPANIES, [art("RadNet deploys AI for chest X-ray reading", 1)], NOW, EXPOSURE)
    assert themes["imaging"]["articles"] == 0


def test_theme_alone_can_make_a_pick(tmp_path):
    (tmp_path / "state").mkdir()
    (tmp_path / "state/serenity-gate-results.json").write_text(json.dumps({"companies": [{"ticker": "SDGR", "substantiatedScore": 52, "decision": "watch"}]}))
    articles = [art(f"New AI drug discovery model designs proteins {i}", 1 + i % 4, ["STAT", "Nature", "Reuters", "medRxiv"][i % 4]) for i in range(10)]
    themes = engine.extract_themes(COMPANIES, articles, NOW, EXPOSURE)
    calls = {c["ticker"]: c for c in engine.recommend(COMPANIES, {"RDNT": [], "SDGR": []}, root=tmp_path, themes=themes)}
    assert calls["SDGR"]["tier"] == "pick" and calls["SDGR"]["driver"] == "theme"
    assert "chokepoint_evidence" in calls["SDGR"]["gatesToRecheck"]


def test_device_topics_exclude_drug_developers():
    def fetch(url, agent):
        hits = [{"_id": "a1:d.htm", "_source": {"display_names": ["HeartFlow, Inc.  (HTFL)  (CIK 0001464521)"], "sics": ["3841"], "form": "10-K", "file_date": "2026-03-01", "adsh": "a1", "items": [], "file_type": "10-K"}},
                {"_id": "a2:d.htm", "_source": {"display_names": ["Wave Life Sciences Ltd.  (WVE)  (CIK 0001631574)"], "sics": ["2834"], "form": "10-K", "file_date": "2026-03-01", "adsh": "a2", "items": [], "file_type": "10-K"}}]
        return {"hits": {"hits": hits, "total": {"value": 2}}}
    from datetime import date
    device = topic_exposure.filing_exposure(['"ECG" "artificial intelligence"'], date(2025, 8, 1), date(2026, 11, 15), fetch=fetch, device=True)
    assert set(device) == {"HTFL"} and device["HTFL"]["strength"] == 0.25
