from datetime import date

from event_revalidation_agent import build, event_status, information_timing


def sample_config():
    return {
        "materiality_threshold": 60,
        "event_keywords": {
            "earnings": ["financial results", "revenue", "10-q"],
            "clinical": ["phase 2", "clinical data"],
        },
        "companies": [{
            "ticker": "TEST",
            "aliases": ["Test Bio"],
            "events": [{"type": "earnings", "date": "2026-11-09", "label": "Q3 earnings", "gates": ["earnings_validation"]}],
        }],
    }


def test_due_soon_event_is_visible_without_news():
    payload = build(sample_config(), [], date(2026, 11, 8))
    assert payload["scheduledEvents"][0]["status"] == "due-soon"
    assert payload["summary"]["dueSoon"] == 1


def test_material_news_creates_revalidation_not_trade():
    article = {
        "source": "company-ir",
        "title": "Test Bio reports financial results and revenue",
        "url": "https://investor.example.com/results",
        "content": "Q3 earnings update",
        "published_at": "2026-11-08T12:00:00Z",
        "discovered_at": "2026-11-08T12:05:00Z",
    }
    payload = build(sample_config(), [article], date(2026, 11, 8))
    task = payload["revalidationTasks"][0]
    assert task["status"] == "pending-revalidation"
    assert "earnings_validation" in task["affectedGates"]
    assert "order" not in task
    assert task["knowledgeAt"] == "2026-11-08T12:05:00+00:00"
    assert task["firstEligibleResearchDate"] == "2026-11-09"
    assert payload["scheduledEvents"][0]["status"] == "evidence-received"


def test_late_discovery_controls_eligibility_and_skips_weekend():
    timing = information_timing({
        "published_at": "2026-11-05T12:00:00Z",
        "discovered_at": "2026-11-06T23:00:00Z",
    })
    assert timing["knowledgeAt"] == "2026-11-06T23:00:00+00:00"
    assert timing["firstEligibleResearchDate"] == "2026-11-09"


def test_old_scheduled_event_waits_for_evidence():
    status, days = event_status("2026-11-01", date(2026, 11, 8))
    assert status == "overdue-awaiting-evidence"
    assert days == -7


def test_issuer_scoped_sec_source_matches_without_company_name_in_title():
    article = {
        "source": "SEC TEST Filings",
        "title": "10-Q - Quarterly report",
        "url": "https://sec.example/filing",
        "content": "Quarterly report",
        "published_at": "2026-11-08T12:00:00Z",
        "discovered_at": "2026-11-08T12:05:00Z",
    }
    payload = build(sample_config(), [article], date(2026, 11, 8))
    assert payload["revalidationTasks"][0]["ticker"] == "TEST"
    assert "earnings_validation" in payload["revalidationTasks"][0]["affectedGates"]
