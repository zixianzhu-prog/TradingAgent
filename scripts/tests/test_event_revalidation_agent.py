from datetime import date

from event_revalidation_agent import build, event_status, information_timing, validate_article_timing


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


def test_future_dated_event_is_quarantined_before_gate_revalidation():
    article = {
        "source": "company-ir",
        "title": "Test Bio reports financial results and revenue",
        "url": "https://investor.example.com/future-results",
        "content": "Q3 earnings update",
        "published_at": "2026-11-09T12:00:00Z",
        "discovered_at": "2026-11-08T12:05:00Z",
    }
    validation = validate_article_timing(article, date(2026, 11, 8))
    assert validation["status"] == "quarantined"
    payload = build(sample_config(), [article], date(2026, 11, 8))
    assert payload["revalidationTasks"] == []
    assert payload["summary"]["quarantinedDates"] == 1


def test_short_alias_does_not_match_inside_common_words():
    from event_revalidation_agent import mentions

    assert mentions("Intuitive launches new Ion software", "Ion")
    assert not mentions("FDA Issues Final Guidance on Prescription Drug regulation", "Ion")
    assert not mentions("ion channel modelling with transformers", "Ion")
    assert mentions("RadNet's DeepHealth unit", "DeepHealth")
    assert not mentions("the system test", "TEM")


def test_unrelated_fda_release_does_not_create_isrg_task():
    config = {
        "materiality_threshold": 60,
        "event_keywords": {"regulatory": ["fda", "approval", "guidance"]},
        "companies": [{"ticker": "ISRG", "aliases": ["Intuitive Surgical", "da Vinci", "Ion"], "events": []}],
    }
    article = {
        "source": "FDA Press Releases",
        "title": "FDA Provides Clarity to Support Cell and Gene Therapy Development and Administration",
        "content": "Final guidance on regulation and approval pathways.",
        "url": "https://www.fda.gov/news",
        "published_at": "2026-11-02T13:56:06+00:00",
        "discovered_at": "2026-11-02T15:00:00+00:00",
    }
    assert build(config, [article], date(2026, 11, 3))["revalidationTasks"] == []


def test_preprints_mentioning_a_company_are_not_company_events():
    config = {"materiality_threshold": 60, "event_keywords": {"regulatory": ["fda", "approval"], "leadership": ["ceo"]},
              "companies": [{"ticker": "NVDA", "aliases": ["NVIDIA"], "events": []}]}
    paper = {"source": "arXiv Artificial Intelligence", "title": "PlantVLM-Edge: quantized VLMs on NVIDIA Jetson, CEO-level summary",
             "content": "approval", "url": "https://arxiv.org/x", "published_at": "2026-11-12T00:00:00+00:00",
             "discovered_at": "2026-11-12T01:00:00+00:00"}
    assert build(config, [paper], date(2026, 11, 13))["revalidationTasks"] == []
