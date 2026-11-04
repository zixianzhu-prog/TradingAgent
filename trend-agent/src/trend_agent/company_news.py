from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

from .database import connect, recent_articles
from .models import Article, utc_now


def _contains(text: str, term: str) -> bool:
    if term.isalnum() and len(term) <= 5:
        return re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE) is not None
    return term.lower() in text.lower()


def _recent(article: Article, cutoff: datetime) -> bool:
    if article.published_at:
        try:
            published = parsedate_to_datetime(article.published_at)
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            return published >= cutoff
        except (TypeError, ValueError, OverflowError):
            pass
    try:
        discovered = datetime.fromisoformat(article.discovered_at.replace("Z", "+00:00"))
        return discovered >= cutoff
    except ValueError:
        return True


def score_company(company: dict[str, Any], articles: list[Article], lexicon: dict[str, list[str]]) -> dict[str, Any]:
    matched: list[dict[str, Any]] = []
    product_hits: set[str] = set()
    sources: set[str] = set()
    trusted_sources: set[str] = set()
    sentiment_values: list[float] = []
    company_terms = [str(term) for term in company.get("company_terms", [])]
    product_terms = [str(term) for term in company.get("product_terms", [])]
    trusted = [str(term).lower() for term in company.get("trusted_sources", [])]

    for article in articles:
        text = f"{article.title} {article.content}"
        company_matches = [term for term in company_terms if _contains(text, term)]
        products = [term for term in product_terms if _contains(text, term)]
        if not company_matches or not products:
            continue
        positives = [term for term in lexicon.get("positive", []) if _contains(text, term)]
        negatives = [term for term in lexicon.get("negative", []) if _contains(text, term)]
        denominator = len(positives) + len(negatives)
        article_sentiment = (len(positives) - len(negatives)) / denominator if denominator else 0.0
        sentiment_values.append(article_sentiment)
        source = article.source.lower()
        sources.add(source)
        if any(term in source or term in article.url.lower() for term in trusted):
            trusted_sources.add(source)
        product_hits.update(term.lower() for term in products)
        matched.append({
            "title": article.title,
            "url": article.url,
            "source": article.source,
            "published_at": article.published_at,
            "company_terms": company_matches,
            "product_terms": products,
            "positive_terms": positives,
            "negative_terms": negatives,
            "sentiment": round(article_sentiment, 3),
        })

    article_count = len(matched)
    source_count = len(sources)
    relevance = min(100, article_count * 10 + source_count * 8 + len(product_hits) * 6)
    reliability = 0 if not matched else min(
        100,
        round((len(trusted_sources) / max(1, source_count)) * 60 + min(40, source_count * 10)),
    )
    sentiment = sum(sentiment_values) / len(sentiment_values) if sentiment_values else 0.0
    news_score = 0 if not matched else round(
        relevance * 0.5 + reliability * 0.3 + ((sentiment + 1.0) / 2.0 * 100) * 0.2
    )
    confidence = "high" if article_count >= 8 and source_count >= 4 else "medium" if article_count >= 4 and source_count >= 2 else "low"
    return {
        "ticker": str(company["ticker"]).upper(),
        "company": company["name"],
        "article_count": article_count,
        "source_count": source_count,
        "trusted_source_count": len(trusted_sources),
        "relevance_score": relevance,
        "reliability_score": reliability,
        "sentiment": round(sentiment, 3),
        "news_score": news_score,
        "confidence": confidence,
        "evidence": matched[:10],
    }


def build_company_news_report(database: str, config: str, output_dir: str, lookback_days: int) -> dict[str, Any]:
    settings = json.loads(Path(config).read_text(encoding="utf-8"))
    connection = connect(database)
    articles = recent_articles(connection, limit=int(settings.get("article_limit", 1000)))
    connection.close()
    cutoff = datetime.now(timezone.utc) - timedelta(days=lookback_days)
    recent = [article for article in articles if _recent(article, cutoff)]
    results = [score_company(company, recent, settings["sentiment_lexicon"]) for company in settings["companies"]]
    payload = {
        "generated_at": utc_now(),
        "lookback_days": lookback_days,
        "articles_considered": len(recent),
        "method": "deterministic heuristic; not a return probability",
        "companies": results,
    }
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / "company-news-scores.json"
    markdown_path = target / "company-news-scores.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# 每日公司新闻评分", "", f"生成时间：{payload['generated_at']}", "",
             "> 固定规则研究评分，不是上涨概率或买卖建议。", "",
             "| 股票 | 新闻数 | 来源数 | 关联度 | 可靠度 | 情绪 | 新闻评分 | 置信度 |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |"]
    for result in results:
        lines.append(
            f"| {result['ticker']} | {result['article_count']} | {result['source_count']} | "
            f"{result['relevance_score']} | {result['reliability_score']} | {result['sentiment']:+.2f} | "
            f"{result['news_score']} | {result['confidence']} |"
        )
        if result["evidence"]:
            lines.extend(["", f"### {result['ticker']} 证据", ""])
            for item in result["evidence"][:5]:
                lines.append(f"- [{item['title']}]({item['url']}) — {item['source']}")
    markdown_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return {"json_report": str(json_path), "markdown_report": str(markdown_path), "companies": len(results)}
