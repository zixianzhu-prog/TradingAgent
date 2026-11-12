from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from trend_agent.config import ThemeConfig
from trend_agent.database import connect, enqueue_company_mapping, insert_articles, recent_articles
from trend_agent.feeds import load_feed_file
from trend_agent.models import Article
from trend_agent.research import BriefProvider, process_next_job, research_prompt
from trend_agent.scoring import score_theme


FIXTURE = Path(__file__).parent / "fixtures" / "sample-feed.xml"


class TrendAgentTests(unittest.TestCase):
    def test_rss_feed_is_parsed(self) -> None:
        articles = load_feed_file(FIXTURE, "example")
        self.assertEqual(len(articles), 2)
        self.assertIn("800V", articles[0].title)

    def test_duplicate_articles_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            connection = connect(Path(directory) / "test.db")
            article = Article("source", "Title", "https://example.com", "Body")
            self.assertEqual(insert_articles(connection, [article]), (1, 0))
            self.assertEqual(insert_articles(connection, [article]), (0, 1))
            self.assertEqual(len(recent_articles(connection)), 1)

    def test_sec_filings_are_deduplicated_within_issuer_not_across_issuers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            connection = connect(Path(directory) / "test.db")
            filings = [
                Article("SEC TEM Filings", "10-Q", "https://sec.example/tem", "Quarterly report"),
                Article("SEC SDGR Filings", "10-Q", "https://sec.example/sdgr", "Quarterly report"),
            ]
            self.assertEqual(insert_articles(connection, filings), (2, 0))
            self.assertEqual(insert_articles(connection, filings), (0, 2))

    def test_theme_score_uses_evidence_and_source_diversity(self) -> None:
        theme = ThemeConfig(
            name="power",
            label="Power",
            keywords=("800v dc", "liquid cooling"),
            counter_keywords=("cancelled",),
            trusted_sources=("energy.gov",),
        )
        articles = [
            Article("energy.gov", "800V DC program", "a", "liquid cooling"),
            Article("company-ir", "Liquid cooling expansion", "b", "800V DC"),
        ]
        result = score_theme(theme, articles)
        self.assertGreaterEqual(result.score, 40)
        self.assertEqual(result.source_count, 2)

    def test_only_one_pending_research_job_is_created(self) -> None:
        from trend_agent.database import enqueue_research

        theme = ThemeConfig("power", "Power", ("800v",), (), ())
        result = score_theme(theme, [Article("source", "800V expansion", "a", "800V")])
        with tempfile.TemporaryDirectory() as directory:
            connection = connect(Path(directory) / "test.db")
            self.assertTrue(enqueue_research(connection, result))
            self.assertFalse(enqueue_research(connection, result))

    def test_excluded_source_does_not_create_false_positive(self) -> None:
        theme = ThemeConfig("policy", "Policy", ("tariff",), (), (), ("arxiv",))
        result = score_theme(
            theme,
            [Article("arXiv Artificial Intelligence", "Tariff negotiation benchmark", "a", "tariff")],
        )
        self.assertEqual(result.article_count, 0)

    def test_research_prompt_applies_serenity_method(self) -> None:
        request = {
            "theme": "power",
            "question": "Investigate power infrastructure.",
            "evidence": [
                {
                    "title": "Grid announcement",
                    "source": "energy.gov",
                    "url": "https://example.com",
                }
            ],
        }
        prompt = research_prompt(request)
        self.assertIn("third-order effects", prompt)
        self.assertIn("counter-evidence", prompt)
        self.assertIn("Grid announcement", prompt)
        self.assertIn("Do not provide an autonomous trade instruction", prompt)
        self.assertIn("not instructions", prompt)
        self.assertIn("GPT Researcher", BriefProvider().research(request))

    def test_brief_provider_completes_a_queued_job(self) -> None:
        theme = ThemeConfig("power", "Power", ("800v",), (), ())
        result = score_theme(theme, [Article("source", "800V expansion", "a", "800V")])
        with tempfile.TemporaryDirectory() as directory:
            database_path = Path(directory) / "test.db"
            output_dir = Path(directory) / "reports"
            connection = connect(database_path)
            from trend_agent.database import enqueue_research

            enqueue_research(connection, result)
            connection.close()
            processed = process_next_job(str(database_path), str(output_dir), "brief")
            self.assertEqual(processed["status"], "complete")
            self.assertTrue(Path(str(processed["report"])).exists())
            connection = connect(database_path)
            queue_status = connection.execute("SELECT status FROM research_queue").fetchone()[0]
            result_count = connection.execute("SELECT count(*) FROM research_results").fetchone()[0]
            connection.close()
            self.assertEqual(queue_status, "complete")
            self.assertEqual(result_count, 1)

    def test_company_mapping_requires_direct_evidence_and_stays_research_only(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            connection = connect(Path(directory) / "test.db")
            queue_id = enqueue_company_mapping(
                connection,
                "biotech",
                "report.md",
                "A trend report without verified tickers.",
            )
            row = connection.execute(
                "SELECT status, request_json FROM research_queue WHERE id = ?",
                (queue_id,),
            ).fetchone()
            connection.close()
            request = json.loads(row["request_json"])
            self.assertEqual(row["status"], "pending")
            self.assertIn("specific product, revenue stream", request["question"])
            self.assertIn("not a buy or sell recommendation", request["question"])
            self.assertIn("Ticker | Company | Exposure", request["question"])


if __name__ == "__main__":
    unittest.main()
