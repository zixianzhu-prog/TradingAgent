from __future__ import annotations

from collections import Counter

from .config import ThemeConfig
from .models import Article, ThemeResult


HIGH_MATERIALITY_TERMS = (
    "ceo", "resign", "resignation", "transition", "board", "investigation",
    "affair", "scandal", "espionage", "intelligence", "earnings", "sec filing",
    "export control", "license", "inventory charge", "customer", "partnership",
    "监管", "辞职", "董事会", "调查", "婚外情", "丑闻", "财报", "出口管制",
)


def _evidence_priority(article: Article) -> tuple[int, str]:
    text = f"{article.title} {article.content}".lower()
    priority = sum(4 for term in HIGH_MATERIALITY_TERMS if term in text)
    source = article.source.lower()
    if any(marker in source for marker in ("sec", "investor", "nvidia news", "company ir", "regulator")):
        priority += 10
    return priority, article.published_at


def score_theme(theme: ThemeConfig, articles: list[Article]) -> ThemeResult:
    matched_articles: list[tuple[Article, list[str], list[str]]] = []
    term_counts: Counter[str] = Counter()
    counter_counts: Counter[str] = Counter()

    for article in articles:
        source_name = article.source.lower()
        if any(excluded in source_name for excluded in theme.excluded_sources):
            continue
        text = f"{article.title} {article.content}".lower()
        matched = [term for term in theme.keywords if term in text]
        counters = [term for term in theme.counter_keywords if term in text]
        if matched:
            matched_articles.append((article, matched, counters))
            term_counts.update(matched)
            counter_counts.update(counters)

    sources = {article.source.lower() for article, _, _ in matched_articles}
    trusted_hits = sum(1 for source in sources if any(name in source for name in theme.trusted_sources))
    evidence_points = min(40, len(matched_articles) * 8)
    diversity_points = min(25, len(sources) * 7)
    coverage_points = min(20, len(term_counts) * 4)
    trust_points = min(15, trusted_hits * 5)
    counter_penalty = min(25, sum(counter_counts.values()) * 5)
    score = max(0, min(100, evidence_points + diversity_points + coverage_points + trust_points - counter_penalty))

    if score >= 75:
        status = "accelerating"
    elif score >= 55:
        status = "emerging"
    elif score >= 30:
        status = "watch"
    else:
        status = "weak"

    ranked_evidence = sorted(matched_articles, key=lambda row: _evidence_priority(row[0]), reverse=True)
    evidence = tuple(
        {
            "title": article.title,
            "url": article.url,
            "source": article.source,
            "published_at": article.published_at,
            "content_excerpt": article.content[:1200],
            "matched_terms": matched,
            "counter_terms": counters,
        }
        for article, matched, counters in ranked_evidence[:10]
    )
    return ThemeResult(
        name=theme.name,
        label=theme.label,
        score=score,
        status=status,
        article_count=len(matched_articles),
        source_count=len(sources),
        matched_terms=tuple(term for term, _ in term_counts.most_common()),
        counter_terms=tuple(term for term, _ in counter_counts.most_common()),
        evidence=evidence,
    )
