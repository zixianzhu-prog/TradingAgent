from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


RISK_TERMS = {
    "financing": ["s-3", "424b", "public offering", "registered offering", "common shares", "dilution"],
    "earnings": ["net loss", "revenue declined", "revenue decreased", "impairment", "going concern", "cash used"],
    "clinical": ["clinical hold", "terminated", "did not meet", "failed endpoint", "serious adverse"],
    "partnership": ["opted out", "terminated collaboration", "returned rights", "discontinued program"],
}
OPTIMISM_TERMS = [
    "breakthrough", "promising", "surge", "strong growth", "expands", "milestone",
    "approval", "beats", "record", "transformative", "leading platform", "bullish",
]
GATE_MAP = {
    "financing": ["cash_runway", "dilution", "valuation"],
    "earnings": ["earnings_validation", "cash_runway", "valuation"],
    "clinical": ["clinical_validation", "falsifiers"],
    "partnership": ["customer_dependency", "partner_economics"],
}


def is_official(article: dict) -> bool:
    source = article.get("source", "").lower()
    url = article.get("url", "").lower()
    return source.startswith("sec ") or any(
        marker in source or marker in url
        for marker in ("company-ir", "investor", "sec.gov", "fda.gov", "clinicaltrials.gov")
    )


def matches_company(article: dict, company: dict) -> bool:
    source = article.get("source", "").lower()
    if source.startswith(f"sec {company['ticker'].lower()} "):
        return True
    text = f"{article.get('title', '')} {article.get('content', '')}".lower()
    return any(alias.lower() in text for alias in company.get("aliases", []))


def risk_categories(article: dict) -> list[str]:
    text = f"{article.get('title', '')} {article.get('content', '')}".lower()
    return [category for category, terms in RISK_TERMS.items() if any(term in text for term in terms)]


def optimism_hits(article: dict) -> list[str]:
    text = f"{article.get('title', '')} {article.get('content', '')}".lower()
    return [term for term in OPTIMISM_TERMS if term in text]


def analyze_company(company: dict, articles: list[dict], threshold: int = 60) -> dict:
    matched = [article for article in articles if matches_company(article, company)]
    official_risks = []
    optimistic_news = []
    categories: set[str] = set()
    for article in matched:
        if is_official(article):
            risks = risk_categories(article)
            if risks:
                categories.update(risks)
                official_risks.append({**article, "riskCategories": risks})
        else:
            hits = optimism_hits(article)
            if hits:
                optimistic_news.append({**article, "optimismTerms": hits})

    score = 0
    if official_risks and optimistic_news:
        score = min(100, 35 + 10 * len(categories) + 5 * min(5, len(optimistic_news)) + 15)
    affected = sorted({gate for category in categories for gate in GATE_MAP.get(category, [])})
    status = "revalidate" if score >= threshold else "official-risk-only" if official_risks else "no-material-divergence"
    return {
        "ticker": company["ticker"],
        "status": status,
        "divergenceScore": score,
        "officialRiskCategories": sorted(categories),
        "affectedGates": affected,
        "officialEvidence": [
            {key: row.get(key) for key in ("title", "url", "source", "published_at", "riskCategories")}
            for row in official_risks[:5]
        ],
        "optimisticNarrative": [
            {key: row.get(key) for key in ("title", "url", "source", "published_at", "optimismTerms")}
            for row in optimistic_news[:5]
        ],
        "interpretation": (
            "Public narrative appears more optimistic while official evidence contains risk markers; human review required."
            if score >= threshold else
            "Official risk markers were found, but there is not enough opposing news narrative to call it a divergence."
            if official_risks else
            "No material narrative-versus-disclosure divergence detected under the deterministic rules."
        ),
        "limitation": "Keyword divergence flag, not proof that a news claim is false and not a return forecast.",
    }


def build(config: dict, articles: list[dict]) -> dict:
    threshold = int(config.get("disclosure_divergence_threshold", 60))
    companies = [analyze_company(company, articles, threshold) for company in config["companies"]]
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "method": "Deterministic comparison of optimistic non-official narrative with risk markers in official disclosures.",
        "companies": companies,
        "summary": {
            "companies": len(companies),
            "revalidate": sum(row["status"] == "revalidate" for row in companies),
            "officialRiskOnly": sum(row["status"] == "official-risk-only" for row in companies),
            "noMaterialDivergence": sum(row["status"] == "no-material-divergence" for row in companies),
        },
    }


def load_articles(database: str, lookback_days: int, today: date) -> list[dict]:
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    cutoff = (today - timedelta(days=lookback_days)).isoformat()
    rows = connection.execute(
        "SELECT source,title,url,content,published_at,discovered_at FROM articles "
        "WHERE (published_at<>'' AND substr(published_at,1,10)>=?) "
        "OR (published_at='' AND substr(discovered_at,1,10)>=?) ORDER BY discovered_at DESC",
        (cutoff, cutoff),
    ).fetchall()
    connection.close()
    return [dict(row) for row in rows]


def write_report(payload: dict, output: Path) -> None:
    lines = [
        "# 新闻叙事与官方披露差异检查", "",
        "> 这是研究提醒，不是事实判决、收益预测或交易信号。关键词命中必须回到原始文件人工核对。", "",
        "| 股票 | 状态 | 差异分 | 官方风险类别 | 受影响 Serenity 门槛 |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in payload["companies"]:
        lines.append(
            f"| {row['ticker']} | {row['status']} | {row['divergenceScore']}/100 | "
            f"{', '.join(row['officialRiskCategories']) or '无'} | {', '.join(row['affectedGates']) or '无'} |"
        )
        if row["status"] == "revalidate":
            lines += ["", f"### {row['ticker']} 需要重新验证", "", "官方风险证据："]
            for item in row["officialEvidence"]:
                lines.append(f"- [{item['title']}]({item['url']}) — {', '.join(item['riskCategories'])}")
            lines.append("\n乐观新闻叙事：")
            for item in row["optimisticNarrative"]:
                lines.append(f"- [{item['title']}]({item['url']}) — {', '.join(item['optimismTerms'])}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Flag narrative divergence between news and official disclosures")
    parser.add_argument("--config", required=True)
    parser.add_argument("--database", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    parser.add_argument("--as-of")
    args = parser.parse_args()
    today = date.fromisoformat(args.as_of) if args.as_of else date.today()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    payload = build(config, load_articles(args.database, int(config.get("lookback_days", 7)), today))
    target = Path(args.json_output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(payload, Path(args.markdown_output))
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
