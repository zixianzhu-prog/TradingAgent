from datetime import date

import news_signal_engine as engine
import official_feeds


def test_filing_rows_skip_exhibits_and_describe_items():
    hits = [
        {"_id": "a1:tem-8k.htm", "_source": {"adsh": "a1", "form": "8-K", "items": ["2.02", "7.01", "9.01"], "file_date": "2026-11-02", "file_type": "8-K"}},
        {"_id": "a1:ex99.htm", "_source": {"adsh": "a1", "form": "8-K", "items": ["2.02"], "file_date": "2026-11-02", "file_type": "EX-99.1"}},
        {"_id": "a2:tem-10q.htm", "_source": {"adsh": "a2", "form": "10-Q", "items": [], "file_date": "2026-11-02", "file_type": "10-Q"}},
    ]
    rows = official_feeds.filing_rows("TEM", "Tempus AI", "1717115", date(2026, 10, 1), date(2026, 11, 15),
                                      fetch=lambda url, agent: {"hits": {"hits": hits}})
    assert len(rows) == 2
    assert rows[0]["title"] == "Tempus AI files 8-K: Item 2.02 Results of Operations and Financial Condition; Item 7.01 Regulation FD Disclosure"
    assert rows[0]["url"].startswith("https://www.sec.gov/Archives/edgar/data/1717115/a1/")
    assert "items=2.02,7.01" in rows[0]["content"] and rows[1]["title"].endswith("Quarterly report")


def test_item_codes_decide_event_type():
    assert engine.classify_filing("form=8-K items=4.02")["direction"] == -1  # restatement is a material negative
    assert engine.classify_filing("form=8-K items=2.02,7.01")["type"] == "earnings"
    assert engine.classify_filing("form=8-K items=5.02")["type"] == "leadership"
    assert engine.classify_filing("form=8-K items=8.01")["type"] == "disclosure"
    assert engine.classify_filing("form=10-Q items=")["type"] == "filing"


def test_federal_register_rows_put_match_note_first():
    doc = {"document_number": "2026-1", "type": "Rule", "title": "CY 2027 Physician Fee Schedule", "abstract": "x" * 900,
           "publication_date": "2026-11-09", "html_url": "https://www.federalregister.gov/d/2026-1",
           "agencies": [{"slug": "centers-for-medicare-medicaid-services"}]}
    rows = official_feeds.federal_register_rows(date(2026, 9, 1), fetch=lambda url, agent: {"results": [doc]})
    assert len(rows) == 1  # same document from several search terms is kept once
    assert rows[0]["title"].startswith("CMS Rule:") and rows[0]["content"].startswith("(Federal Register search match: artificial intelligence)")


def test_official_rule_alone_is_a_material_theme():
    from datetime import datetime, timedelta, timezone
    now = datetime(2026, 11, 15, tzinfo=timezone.utc)
    article = {"source": "Federal Register · CMS", "title": "CMS Rule: Medicare CY 2027 Physician Fee Schedule payment policies",
               "url": "u", "content": "(Federal Register search match: artificial intelligence) payment", "at": now - timedelta(days=2)}
    themes = engine.extract_themes([], [article], now, {"topics": {}})
    assert themes["ai_reimbursement"]["material"] is True
