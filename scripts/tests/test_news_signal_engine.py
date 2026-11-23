import json
from datetime import datetime, timedelta, timezone

import news_signal_engine as engine

NOW = datetime(2026, 11, 15, 12, tzinfo=timezone.utc)
TEM = {"ticker": "TEM", "name": "Tempus AI", "query": '"Tempus AI"', "aliases": ["Tempus AI", "Tempus"]}


def art(title, days_ago=1, source="Google News · TEM"):
    return {"source": source, "title": title, "url": f"https://e.example/{abs(hash(title))}", "content": "", "at": NOW - timedelta(days=days_ago)}


def test_classify_common_headlines():
    assert engine.classify("Natera and Incyte partner on Phase II colorectal cancer trial")["type"] == "partnership"
    assert engine.classify("Leerink Partners Maintains Certara With Buy Rating")["type"] == "analyst"
    assert engine.classify("RXRX Stock Soars On Q4 Beat, CEO Says Company Has Reached An Inflection")["type"] == "earnings"
    assert engine.classify("Intuitive Surgical Adds Aaron Martin To Its Board")["type"] == "leadership"
    assert engine.classify("Moderna moves UK office to London's knowledge quarter")["type"] != "earnings"
    assert engine.classify("RadNet Could Be 18% Undervalued After Its Acquisition Focus")["type"] == "commentary"
    legal = engine.classify("Wisconsin joins federal lawsuit against Hims & Hers")
    assert legal["type"] == "legal" and legal["direction"] == -1


def test_quote_pages_dropped_and_outlets_merged_with_vote():
    articles = [
        art("Tempus AI, Inc. (TEM) Stock Price, News, Quote & History - Yahoo Finance"),
        art("Tempus AI Revenue Up 23% In Third Quarter - Barron's"),
        art("Tempus AI beats estimates and raises outlook - Reuters"),
        art("Tempus AI quarterly earnings snapshot - AP"),
    ]
    events = engine.extract_events([TEM], articles, NOW)["TEM"]
    assert len(events) == 1  # one earnings story from three outlets, quote page dropped
    event = events[0]
    assert len(event["sources"]) == 3 and event["direction"] == 1 and event["material"]


def test_single_low_credibility_source_is_not_material():
    events = engine.extract_events([TEM], [art("Tempus AI partners with Novo Nordisk - SomeBlog")], NOW)["TEM"]
    assert events[0]["type"] == "partnership" and not events[0]["material"]


def test_old_news_decays():
    fresh = engine.extract_events([TEM], [art("Tempus AI wins FDA clearance - Reuters", 1)], NOW)["TEM"][0]
    old = engine.extract_events([TEM], [art("Tempus AI wins FDA clearance - Reuters", 13)], NOW)["TEM"][0]
    assert fresh["weight"] > 2 * old["weight"]


def test_serenity_gates_the_recommendation(tmp_path):
    (tmp_path / "state").mkdir()
    (tmp_path / "state/serenity-gate-results.json").write_text(json.dumps({"companies": [
        {"ticker": "TEM", "substantiatedScore": 55, "decision": "watch"},
        {"ticker": "NEW", "substantiatedScore": 30, "decision": "watch"},
        {"ticker": "BAD", "substantiatedScore": 60, "decision": "watch"}]}))
    (tmp_path / "state/ai-medicine-top5.json").write_text(json.dumps({"ranking": [{"ticker": "TEM", "potential": {"total": 88}, "bucket": "durable"}]}))
    companies = [TEM, {"ticker": "NEW", "name": "Newco", "aliases": ["Newco"]}, {"ticker": "BAD", "name": "Badco", "aliases": ["Badco"]}]
    articles = [art("Tempus AI wins FDA clearance - Reuters"), art("Tempus AI wins FDA clearance for new assay - STAT"),
                art("Newco wins FDA clearance - Reuters"), art("Newco wins FDA clearance for device - STAT"),
                art("Badco faces federal lawsuit - Reuters"), art("Badco hit with class action lawsuit - Bloomberg")]
    calls = {c["ticker"]: c for c in engine.recommend(companies, engine.extract_events(companies, articles, NOW), root=tmp_path)}
    assert calls["TEM"]["tier"] == "pick" and "chokepoint_evidence" in calls["TEM"]["gatesToRecheck"]
    assert calls["NEW"]["tier"] == "unproven" and "below 50" in calls["NEW"]["whyNotPick"][0]
    assert calls["BAD"]["tier"] == "warning"


def test_serenity_verdict_decides_and_unanalysed_news_is_queued(tmp_path):
    (tmp_path / "state").mkdir()
    (tmp_path / "state/serenity-gate-results.json").write_text(json.dumps({"companies": [
        {"ticker": "TEM", "substantiatedScore": 55, "decision": "watch"}, {"ticker": "NEW", "substantiatedScore": 30, "decision": "watch"}]}))
    (tmp_path / "state/serenity-claude-verdicts.json").write_text(json.dumps({"companies": [
        {"ticker": "TEM", "tier": "starter until governance clarified", "chokepoint": "no", "countersHolding": ["related party"], "verdict": "v"}]}))
    companies = [TEM, {"ticker": "NEW", "name": "Newco", "aliases": ["Newco"]}]
    articles = [art("Tempus AI wins FDA clearance - Reuters"), art("Tempus AI wins FDA clearance for new assay - STAT"),
                art("Newco wins FDA clearance - Reuters"), art("Newco wins FDA clearance for device - STAT")]
    calls = {c["ticker"]: c for c in engine.recommend(companies, engine.extract_events(companies, articles, NOW), root=tmp_path)}
    assert calls["TEM"]["decision"] == "serenity-starter" and calls["TEM"]["serenity"]["chokepoint"] == "no"
    assert calls["NEW"]["decision"] == "awaiting-serenity" and calls["NEW"]["trigger"] == "positive"


def test_insider_trades_are_not_read_as_mergers():
    from news_signal_engine import classify
    assert classify("An accounting chief acquired 795 Heartflow (HTFL) shares at $19.70 under an employee purchase plan.")["type"] == "insider"
    assert classify("Director sells 10,000 shares of RadNet")["type"] == "insider"
    assert classify("Tempus to acquire Paige in $81 million deal")["type"] == "m&a"


def test_evidence_date_and_news_recheck():
    from datetime import date, datetime, timezone
    from news_signal_engine import evidence_through, news_recheck
    packet = {"evidence": [{"url": "https://www.sec.gov/x/rdnt-20251231.htm"}, {"url": "https://www.sec.gov/x/rdnt-20260930.htm"},
                           {"url": "https://www.sec.gov/x/htfl-20261112xex99_1.htm"}]}
    assert evidence_through(packet) == date(2026, 11, 12)  # exhibit date beats 2026-09-30 + 40 days
    through = date(2026, 11, 9)
    at = lambda d: datetime.fromisoformat(d).replace(tzinfo=timezone.utc)
    bucket = [
        {"type": "earnings", "title": "Earnings call highlights", "at": at("2026-11-16"), "materiality": 2.0, "gates": ["earnings_validation"]},
        {"type": "analyst", "title": "Price target raised", "at": at("2026-11-16"), "materiality": 1.0, "gates": []},
        {"type": "m&a", "title": "Acquires ONRAD", "at": at("2026-10-27"), "materiality": 2.5, "gates": ["multi_node_control"]},
        {"type": "partnership", "title": "New alliance", "at": at("2026-11-13"), "materiality": 2.5, "gates": ["customer_dependency"]},
    ]
    r = news_recheck(bucket, through)
    assert r["status"] == "queued" and [e["title"] for e in r["events"]] == ["New alliance"] and r["gates"] == ["customer_dependency"]
    stale = news_recheck([{"type": "earnings", "title": "Q3 results", "at": at("2026-11-04"), "materiality": 2.0, "gates": ["earnings_validation"]}], date(2026, 2, 9))
    assert stale["status"] == "queued"  # review read only the annual report; a newer quarter must be re-checked
