import unittest
from datetime import datetime, timezone

from trend_agent.company_news import _recent, score_company
from trend_agent.models import Article


class CompanyNewsTests(unittest.TestCase):
    def setUp(self):
        self.company = {
            "ticker": "MRNA",
            "name": "Moderna",
            "company_terms": ["Moderna"],
            "product_terms": ["mRNA", "vaccine"],
            "trusted_sources": ["moderna", "fda.gov"],
        }
        self.lexicon = {"positive": ["approval", "growth"], "negative": ["failed", "delay"]}

    def test_requires_company_and_product_match(self):
        result = score_company(self.company, [Article("source", "mRNA advances", "u", "approval")], self.lexicon)
        self.assertEqual(result["article_count"], 0)
        self.assertEqual(result["news_score"], 0)

    def test_scores_relevance_reliability_and_sentiment(self):
        articles = [
            Article("Moderna IR", "Moderna mRNA vaccine approval", "https://moderna.com/a", "growth"),
            Article("Independent News", "Moderna vaccine expansion", "https://news.example/b", "growth"),
        ]
        result = score_company(self.company, articles, self.lexicon)
        self.assertEqual(result["article_count"], 2)
        self.assertEqual(result["source_count"], 2)
        self.assertGreater(result["relevance_score"], 0)
        self.assertGreater(result["reliability_score"], 0)
        self.assertGreater(result["sentiment"], 0)

    def test_recent_filter_prefers_publisher_date_over_discovery_date(self):
        article = Article(
            "source", "old story", "https://example.com/old", "",
            published_at="Tue, 14 Jul 2020 07:00:00 GMT",
            discovered_at="2026-11-03T05:00:00+00:00",
        )
        self.assertFalse(_recent(article, datetime(2026, 10, 27, tzinfo=timezone.utc)))


if __name__ == "__main__":
    unittest.main()
