from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


def parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def information_timing(article: dict) -> dict:
    """Return a conservative timestamp after which an event may enter research.

    We use the later of publisher time and local discovery time, then wait until
    the next weekday. The benchmark evaluator later resolves actual price sessions.
    """
    published = parse_timestamp(article.get("published_at"))
    discovered = parse_timestamp(article.get("discovered_at"))
    observed = max(value for value in (published, discovered) if value is not None) if published or discovered else datetime.now(timezone.utc)
    eligible = observed.date() + timedelta(days=1)
    while eligible.weekday() >= 5:
        eligible += timedelta(days=1)
    return {
        "publishedAt": published.isoformat() if published else article.get("published_at", ""),
        "discoveredAt": discovered.isoformat() if discovered else article.get("discovered_at", ""),
        "knowledgeAt": observed.isoformat(),
        "firstEligibleResearchDate": eligible.isoformat(),
        "timingPolicy": "later-of-published-or-discovered; next-weekday research eligibility; price evaluator resolves actual sessions",
    }


def event_status(event_date: str | None, today: date) -> tuple[str, int | None]:
    if not event_date:
        return "unscheduled", None
    delta = (date.fromisoformat(event_date) - today).days
    if delta < 0:
        return "overdue-awaiting-evidence", delta
    if delta <= 3:
        return "due-soon", delta
    if delta <= 30:
        return "upcoming", delta
    return "scheduled", delta


def classify(text: str, keyword_map: dict[str, list[str]]) -> list[str]:
    lowered = text.lower()
    return [kind for kind, words in keyword_map.items() if any(word.lower() in lowered for word in words)]


def materiality(article: dict, company: dict, kinds: list[str], today: date) -> tuple[int, list[str]]:
    text = f"{article['title']} {article.get('content', '')}".lower()
    direct_ticker = company["ticker"].lower() in text
    alias_match = any(alias.lower() in text for alias in company["aliases"])
    source_company_match = article.get("source", "").lower().startswith(f"sec {company['ticker'].lower()} ")
    reasons = []
    score = 0
    if alias_match or source_company_match:
        score += 35
        reasons.append("公司名称直接匹配" if alias_match else "SEC 公司专属披露源匹配")
    if direct_ticker:
        score += 10
        reasons.append("股票代码直接匹配")
    if kinds:
        score += min(30, 15 + 5 * len(kinds))
        reasons.append("重大事件关键词：" + ", ".join(kinds))
    source = article.get("source", "").lower()
    url = article.get("url", "").lower()
    if any(marker in source or marker in url for marker in ("sec", "fda", "investor", "company-ir")):
        score += 15
        reasons.append("官方或监管来源")
    for event in company.get("events", []):
        if event.get("type") in kinds and event.get("date"):
            distance = abs((date.fromisoformat(event["date"]) - today).days)
            if distance <= 3:
                score += 10
                reasons.append("接近预定事件窗口")
                break
    return min(score, 100), reasons


def affected_gates(company: dict, kinds: list[str]) -> list[str]:
    gates = set()
    for event in company.get("events", []):
        if event.get("type") in kinds:
            gates.update(event.get("gates", []))
    defaults = {
        "earnings": ["earnings_validation", "valuation", "cash_runway"],
        "clinical": ["clinical_validation", "falsifiers"],
        "regulatory": ["regulatory_path", "falsifiers"],
        "partnership": ["customer_dependency", "partner_economics"],
        "financing": ["cash_runway", "dilution", "valuation"],
        "integration": ["integration_execution", "valuation"],
    }
    for kind in kinds:
        gates.update(defaults.get(kind, []))
    return sorted(gates)


def build(config: dict, articles: list[dict], today: date) -> dict:
    threshold = int(config.get("materiality_threshold", 60))
    scheduled = []
    tasks = []
    seen_tasks: set[str] = set()
    for company in config["companies"]:
        for event in company.get("events", []):
            status, days = event_status(event.get("date"), today)
            if event.get("resolved"):
                status = "evidence-received"
            scheduled.append({"ticker": company["ticker"], **event, "status": status, "daysUntil": days})
        for article in articles:
            text = f"{article['title']} {article.get('content', '')}"
            source_company_match = article.get("source", "").lower().startswith(f"sec {company['ticker'].lower()} ")
            if not source_company_match and not any(alias.lower() in text.lower() for alias in company["aliases"]):
                continue
            kinds = classify(text, config["event_keywords"])
            if not kinds:
                continue
            score, reasons = materiality(article, company, kinds, today)
            if score < threshold:
                continue
            event_id = hashlib.sha256(f"{company['ticker']}|{article['url']}|{article['title']}".encode()).hexdigest()[:16]
            if event_id in seen_tasks:
                continue
            seen_tasks.add(event_id)
            tasks.append({
                "eventId": event_id,
                "ticker": company["ticker"],
                "materialityScore": score,
                "eventTypes": kinds,
                "title": article["title"],
                "url": article["url"],
                "source": article["source"],
                **information_timing(article),
                "affectedGates": affected_gates(company, kinds),
                "reasons": reasons,
                "status": "pending-revalidation",
            })
    for event in scheduled:
        if any(
            task["ticker"] == event["ticker"] and event.get("type") in task.get("eventTypes", [])
            for task in tasks
        ):
            event["status"] = "evidence-received"
    tasks.sort(key=lambda row: (row["materialityScore"], row["publishedAt"]), reverse=True)
    scheduled.sort(key=lambda row: (row["daysUntil"] is None, row["daysUntil"] if row["daysUntil"] is not None else 9999))
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "asOf": today.isoformat(),
        "method": "Deterministic event matching, conservative information timing and materiality scoring; tasks request research revalidation and never place orders.",
        "scheduledEvents": scheduled,
        "revalidationTasks": tasks,
        "summary": {
            "dueSoon": sum(row["status"] in {"due-soon", "overdue-awaiting-evidence"} for row in scheduled),
            "evidenceReceived": sum(row["status"] == "evidence-received" for row in scheduled),
            "pendingTasks": len(tasks),
            "companies": len(config["companies"]),
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


def write_report(payload: dict, output: str) -> None:
    lines = [
        "# 事件驱动重新验证队列", "",
        f"生成日期：{payload['asOf']}", "",
        "> 事件只触发重新研究，不会自动改变评级、仓位或创建交易。", "",
        "## 事件日历", "",
        "| 股票 | 事件 | 日期 | 状态 | 重新检查 |", "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["scheduledEvents"]:
        lines.append(f"| {row['ticker']} | {row['label']} | {row.get('date') or '待公布'} | {row['status']} | {', '.join(row.get('gates', []))} |")
    lines += ["", "## 待重新验证任务", ""]
    if not payload["revalidationTasks"]:
        lines.append("当前没有达到重大性门槛的新事件。")
    for row in payload["revalidationTasks"]:
        lines += [
            f"### {row['ticker']} · {row['materialityScore']}/100",
            f"- [{row['title']}]({row['url']})",
            f"- 事件类型：{', '.join(row['eventTypes']) or 'unclassified'}",
            f"- 信息可用：{row['knowledgeAt']}；最早进入研究：{row['firstEligibleResearchDate']}",
            f"- 重新检查：{', '.join(row['affectedGates'])}",
            f"- 触发原因：{'；'.join(row['reasons'])}", "",
        ]
    Path(output).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create auditable revalidation tasks from scheduled and detected company events")
    parser.add_argument("--config", required=True)
    parser.add_argument("--database", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    parser.add_argument("--as-of")
    args = parser.parse_args()
    today = date.fromisoformat(args.as_of) if args.as_of else date.today()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    articles = load_articles(args.database, int(config.get("lookback_days", 7)), today)
    payload = build(config, articles, today)
    target = Path(args.json_output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(payload, args.markdown_output)
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
