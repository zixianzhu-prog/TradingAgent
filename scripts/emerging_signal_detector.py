"""Emerging-signal detector: find topics that are suddenly being talked about.

The theme scorer only scores themes someone already configured. A new event such
as an unknown pneumonia cluster would be ignored until a person wrote keywords for
it. This module needs no preset themes. For every word and two-word phrase in
article titles it compares how many articles mention it in the recent window with
how many mentioned it in a baseline window, and keeps the ones that jump, appear
in several independent sources, and ideally reach authoritative sources (WHO,
FDA, preprint servers).

It is purely statistical and uses no language model, so the same code can be
replayed on historical news with ``--as-of`` without leaking later knowledge.

Guardrails against false bursts:
- A feed that this system first ingested inside the recent window (a feed added
  yesterday dumps its whole backlog at once) does not count towards a burst;
  otherwise every word in a new feed would "spike". Publishers that simply appear
  rarely through an aggregator are not treated as new feeds.
- A topic must appear in at least ``min_sources`` distinct sources.
- Topics dominated by one source are flagged and down-weighted.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field, replace
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STOPWORDS = set("""
a about above after again against all also am an and any are as at be because been before being below between both but by
can could did do does doing down during each few for from further had has have having he her here hers him his how i if in
into is it its itself just me more most my no nor not now of off on once only or other our out over own same she should so
some such than that the their them then there these they this those through to too under until up very was we were what
when where which while who whom why will with would you your yours via vs amid among new says said say after over per
first one two three four five six seven eight nine ten amp us u.s inc corp ltd plc co llc
""".split())
# Words that recur in finance and news wire titles regardless of the topic.
NOISE = set("""
stock stocks share shares nasdaq nyse price prices target targets analyst analysts rating ratings buy sell hold upgrade
downgrade quarter quarterly q1 q2 q3 q4 fy results result reports report reported announces announced announcement
company companies news update updates market markets billion million percent year years week weeks today month months
day days investors investor earnings revenue guidance outlook deal deals ceo cfo time big top best worst latest could
study studies paper analysis using based use data effect effects role novel approach toward towards evidence review
provide provides provided propose proposed multiple related majority various different several large small high low
higher lower increased increase decreased reduced reduce associated association identify identified identification
improve improved improving understanding insights insight reveals revealed reveal shows show showing suggests suggest
potential possible within across between general specific important impact impacts factors factor level levels
method methods model models framework system systems network networks function functional mechanism mechanisms
""".split())
AUTHORITY_MARKERS = ("who", "world health", "cdc", "fda", "sec", "nih", "medrxiv", "biorxiv", "clinicaltrials", "nejm", "lancet", "nature", "ema")
TOKEN = re.compile(r"[a-z][a-z0-9\-]+")


@dataclass
class Doc:
    doc_id: str
    source: str
    title: str
    url: str
    at: datetime
    terms: set[str] = field(default_factory=set)
    ingested: datetime | None = None  # when this system first stored it


def parse_time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        try:
            parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def event_time(published: str | None, discovered: str | None) -> datetime | None:
    """When the item became public. Published time unless it is later than discovery."""
    pub, disc = parse_time(published), parse_time(discovered)
    if pub and disc:
        return min(pub, disc)
    return pub or disc


def extract_terms(text: str) -> set[str]:
    """Unigrams and bigrams after dropping stopwords and finance/news boilerplate."""
    words = [w.strip("-") for w in TOKEN.findall(text.lower())]
    words = [w for w in words if len(w) > 2 and not w.isdigit()]
    terms = {w for w in words if w not in STOPWORDS and w not in NOISE}
    for a, b in zip(words, words[1:]):
        if a in STOPWORDS or b in STOPWORDS or (a in NOISE and b in NOISE):
            continue
        terms.add(f"{a} {b}")
    return terms


def load_docs(databases: list[str], as_of: datetime, horizon_days: int) -> list[Doc]:
    start = as_of - timedelta(days=horizon_days)
    docs: list[Doc] = []
    for database in databases:
        path = Path(database)
        if not path.exists():
            continue
        connection = sqlite3.connect(path)
        rows = connection.execute("SELECT id, source, title, url, content, published_at, discovered_at FROM articles").fetchall()
        connection.close()
        for row_id, source, title, url, content, published, discovered in rows:
            at = event_time(published, discovered)
            if at is None or not (start <= at <= as_of):
                continue
            # Titles carry the topic. Abstracts and article bodies add generic wording that
            # drowns real bursts, so only the title is tokenised.
            text = title or (content or "")[:160]
            docs.append(Doc(f"{path.stem}:{row_id}", source or "unknown", title or "", url or "", at, extract_terms(text), parse_time(discovered) or at))
    return docs


def is_authority(source: str) -> bool:
    lowered = source.lower()
    return any(re.search(rf"\b{re.escape(marker)}\b", lowered) for marker in AUTHORITY_MARKERS)


def detect(
    docs: list[Doc],
    as_of: datetime,
    recent_days: int = 3,
    baseline_days: int = 21,
    min_docs: int = 4,
    min_sources: int = 2,
    min_ratio: float = 3.0,
    min_z: float = 3.0,
    new_feed_min_items: int = 10,
    common_share: float = 0.004,
    common_min_ratio: float = 8.0,
) -> dict:
    recent_start = as_of - timedelta(days=recent_days)
    baseline_start = recent_start - timedelta(days=baseline_days)
    first_ingested: dict[str, datetime] = {}
    volume: Counter[str] = Counter()
    for doc in docs:
        volume[doc.source] += 1
        ingested = doc.ingested or doc.at
        if doc.source not in first_ingested or ingested < first_ingested[doc.source]:
            first_ingested[doc.source] = ingested
    warming_up = sorted(
        source for source, first in first_ingested.items()
        if first >= recent_start and volume[source] >= new_feed_min_items
    )
    established = set(first_ingested) - set(warming_up)

    baseline_docs = [d for d in docs if baseline_start <= d.at < recent_start]
    recent_docs = [d for d in docs if recent_start <= d.at <= as_of and d.source in established]
    baseline_span = max(1.0, min(baseline_days, (recent_start - min((d.at for d in baseline_docs), default=recent_start)).total_seconds() / 86400))
    # Expected mentions scale with how many articles arrived, not with calendar days:
    # weekends and holidays are quiet, and a busy Monday must not look like a burst.
    volume_scale = len(recent_docs) / max(1, len(baseline_docs))

    base_df: Counter[str] = Counter()
    for doc in baseline_docs:
        base_df.update(doc.terms)
    # "Is this word normally common?" is judged on all loaded history before the recent
    # window (up to ``history_days``), which is far more stable than the 21-day baseline.
    history_docs = [d for d in docs if d.at < recent_start]
    history_df: Counter[str] = Counter()
    for doc in history_docs:
        history_df.update(doc.terms)
    recent_index: dict[str, list[Doc]] = defaultdict(list)
    for doc in recent_docs:
        for term in doc.terms:
            recent_index[term].append(doc)

    candidates = []
    for term, hits in recent_index.items():
        sources = {d.source for d in hits}
        if len(hits) < min_docs or len(sources) < min_sources:
            continue
        expected = (base_df[term] + 0.5) * volume_scale
        ratio = (len(hits) + 1) / (expected + 1)
        z = (len(hits) - expected) / math.sqrt(expected + 1)
        if ratio < min_ratio or z < min_z:
            continue
        # A genuinely new topic is rare in the baseline ("ncov" appeared 0-2 times before
        # January 2020). Words already common there, such as "research", only count if
        # they jump far more, otherwise small-count noise gets "confirmed" every week.
        history_share = history_df[term] / max(1, len(history_docs))
        if history_share > common_share and ratio < common_min_ratio:
            continue
        top_share = Counter(d.source for d in hits).most_common(1)[0][1] / len(hits)
        authority = any(is_authority(s) for s in sources)
        score = z * (1 + 0.15 * min(len(sources), 6)) * (1.3 if authority else 1.0) * (0.5 if top_share >= 0.8 else 1.0)
        candidates.append({
            "term": term, "score": score, "recent": len(hits), "baseline": base_df[term], "expected": expected,
            "ratio": ratio, "z": z, "sources": sources, "authority": authority, "topSourceShare": top_share,
            "docs": hits, "novel": base_df[term] == 0,
        })
    candidates.sort(key=lambda c: (-c["score"], -len(c["term"])))

    clusters: list[dict] = []
    for cand in candidates:
        ids = {d.doc_id for d in cand["docs"]}
        for cluster in clusters:
            overlap = len(ids & cluster["ids"]) / max(1, min(len(ids), len(cluster["ids"])))
            if overlap >= 0.6:
                cluster["terms"].append(cand)
                cluster["ids"] |= ids
                break
        else:
            clusters.append({"terms": [cand], "ids": set(ids)})

    all_by_id = {d.doc_id: d for d in docs}
    results = []
    for cluster in clusters:
        terms = cluster["terms"]
        lead = max(terms, key=lambda c: (c["score"] * (1.15 if " " in c["term"] else 1.0)))
        cluster_docs = sorted((all_by_id[i] for i in cluster["ids"]), key=lambda d: d.at)
        sources = sorted({d.source for d in cluster_docs})
        daily = Counter(d.at.date().isoformat() for d in docs if lead["term"] in d.terms)
        results.append({
            "label": lead["term"],
            "score": round(max(c["score"] for c in terms), 2),
            "relatedTerms": [c["term"] for c in terms if c["term"] != lead["term"]][:8],
            "recentArticles": lead["recent"],
            "baselineArticles": lead["baseline"],
            "expectedRecent": round(lead["expected"], 2),
            "burstRatio": round(lead["ratio"], 1),
            "zScore": round(lead["z"], 1),
            "novel": lead["novel"],
            "sources": sources,
            "sourceCount": len(sources),
            "authoritySource": any(is_authority(s) for s in sources),
            "singleSourceDominated": lead["topSourceShare"] >= 0.8,
            "firstSeen": cluster_docs[0].at.isoformat() if cluster_docs else None,
            "articleIds": sorted(cluster["ids"]),
            "dailyCounts": dict(sorted(daily.items())),
            "headlines": [
                {"title": d.title, "source": d.source, "url": d.url, "at": d.at.isoformat()}
                for d in sorted(cluster_docs, key=lambda d: (not is_authority(d.source), -d.at.timestamp()))[:6]
            ],
        })
    results.sort(key=lambda r: -r["score"])
    return {
        "asOf": as_of.isoformat(),
        "window": {"recentDays": recent_days, "baselineDays": baseline_days, "baselineSpanDays": round(baseline_span, 1)},
        "thresholds": {"minArticles": min_docs, "minSources": min_sources, "minBurstRatio": min_ratio, "minZ": min_z},
        "articles": {"recent": len(recent_docs), "baseline": len(baseline_docs)},
        "warmingUpSources": warming_up,
        "baselineWarning": baseline_span < 7,
        "signals": results,
    }


def _tokens(signal: dict) -> set[str]:
    return {token for term in [signal["label"], *signal.get("related", [])] for token in term.split()}


def confirm_topics(days: list[dict], window: int = 7) -> list[dict]:
    """Group signals that share words and keep groups that fire on two or more days within ``window``."""
    groups: list[dict] = []
    for row in days:
        for signal in row["signals"]:
            tokens = _tokens(signal)
            group = next((g for g in groups if g["tokens"] & tokens), None)
            if group is None:
                group = {"tokens": set(), "dates": [], "labels": {}, "headlines": [], "seen": set()}
                groups.append(group)
            group["tokens"] |= tokens
            ids = set(signal.get("ids", []))
            # Overlapping 3-day windows re-count the same articles. A day only counts as a
            # new firing when it brings at least two articles the topic had not shown before
            # (signals without ids, e.g. from tests, always count).
            fresh = not ids or len(ids - group["seen"]) >= 2
            group["seen"] |= ids
            if fresh and row["date"] not in group["dates"]:
                group["dates"].append(row["date"])
            group["labels"][signal["label"]] = group["labels"].get(signal["label"], 0) + signal["recent"]
            if signal.get("headline") and len(group["headlines"]) < 3:
                group["headlines"].append({"date": row["date"], "title": signal["headline"]})
    # Merge groups that ended up sharing words (signals can bridge two earlier groups).
    merged: list[dict] = []
    for group in groups:
        target = next((m for m in merged if m["tokens"] & group["tokens"]), None)
        if target is None:
            merged.append(group)
            continue
        target["tokens"] |= group["tokens"]
        target["seen"] = target.get("seen", set()) | group.get("seen", set())
        target["dates"] = sorted(set(target["dates"]) | set(group["dates"]))
        for label, count in group["labels"].items():
            target["labels"][label] = target["labels"].get(label, 0) + count
        target["headlines"] = (target["headlines"] + group["headlines"])[:3]
    if len(merged) < len(groups):
        return confirm_topics_from_groups(merged, window)
    return confirm_topics_from_groups(groups, window)


def confirm_topics_from_groups(groups: list[dict], window: int) -> list[dict]:
    confirmed = []
    for group in groups:
        dates = sorted(date.fromisoformat(d) for d in group["dates"])
        for first, second in zip(dates, dates[1:]):
            if (second - first).days <= window:
                # Prefer the single word that carries the most mentions: it searches filings best.
                label = max(group["labels"], key=lambda k: (group["labels"][k], " " not in k))
                search_terms = sorted(group["labels"], key=lambda k: -group["labels"][k])[:3]
                confirmed.append({"topic": label, "searchTerms": search_terms, "firstFired": dates[0].isoformat(), "confirmed": second.isoformat(),
                                  "daysFired": len(dates), "labels": group["labels"], "headlines": group["headlines"]})
                break
    return sorted(confirmed, key=lambda c: c["confirmed"])


def update_history(history_path: Path, payload: dict, keep_days: int = 30) -> list[dict]:
    """Append today's signals to the run history so confirmation works across daily runs."""
    try:
        history = json.loads(history_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        history = []
    today = payload["asOf"][:10]
    history = [row for row in history if row["date"] != today]
    history.append({"date": today, "signals": [
        {"label": s["label"], "related": s["relatedTerms"], "recent": s["recentArticles"], "baseline": s["baselineArticles"],
         "ids": s.get("articleIds", []), "headline": (s["headlines"] or [{}])[0].get("title")}
        for s in payload["signals"][:10]
    ]})
    history = sorted(history, key=lambda row: row["date"])[-keep_days:]
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(history, ensure_ascii=False), encoding="utf-8")
    return history


def mark_confirmed(payload: dict, history: list[dict], recent_days: int = 7) -> None:
    """A signal is confirmed when its topic fired on two days within a week with fresh articles."""
    today = date.fromisoformat(payload["asOf"][:10])
    confirmed = [c for c in confirm_topics(history[-14:]) if (today - date.fromisoformat(c["confirmed"])).days <= recent_days]
    payload["confirmedTopics"] = confirmed
    for signal in payload["signals"]:
        tokens = _tokens({"label": signal["label"], "related": signal["relatedTerms"]})
        signal["confirmed"] = any(tokens & {t for term in c["labels"] for t in term.split()} for c in confirmed)


def tag_known_themes(payload: dict, config_paths: list[str]) -> None:
    """Mark signals that an existing configured theme already tracks."""
    keywords: list[tuple[str, str]] = []
    for config_path in config_paths:
        path = Path(config_path)
        if not path.exists():
            continue
        for theme in json.loads(path.read_text(encoding="utf-8")).get("themes", []):
            keywords += [(str(k).lower(), theme.get("name", "")) for k in theme.get("keywords", [])]
    for signal in payload["signals"]:
        terms = [signal["label"], *signal["relatedTerms"]]
        hits = sorted({name for term in terms for keyword, name in keywords if keyword in term or term in keyword})
        signal["trackedBy"] = hits
        signal["status"] = "tracked-theme" if hits else "new-topic"


def collect(sources_path: str, database: str) -> list[dict]:
    """Fetch the radar feeds into their own database (needs trend-agent on sys.path)."""
    sys.path.insert(0, str(ROOT / "trend-agent/src"))
    from trend_agent.database import connect, insert_articles  # noqa: E402
    from trend_agent.feeds import fetch_feed  # noqa: E402

    config = json.loads(Path(sources_path).read_text(encoding="utf-8"))
    connection = connect(database)
    results = []
    for source in config.get("sources", []):
        if not source.get("enabled", True):
            continue
        try:
            articles = fetch_feed(source["url"], source["name"], int(source.get("timeout", 20)))[: int(source.get("max_items", 100))]
            # Keep the configured feed name so preprint servers and WHO stay recognisable as authority sources.
            articles = [replace(article, source=source["name"]) for article in articles]
            inserted, duplicates = insert_articles(connection, articles)
            results.append({"name": source["name"], "status": "ok", "fetched": len(articles), "inserted": inserted})
        except Exception as exc:  # one failing feed must not stop the radar
            results.append({"name": source["name"], "status": "error", "error": str(exc)[:200]})
    connection.close()
    return results


def write_markdown(payload: dict, path: str, limit: int = 15) -> None:
    lines = [
        "# 新兴信号雷达", "",
        f"截至：{payload['asOf']}　近 {payload['window']['recentDays']} 天 vs 前 {payload['window']['baselineDays']} 天基线"
        f"（实际基线 {payload['window']['baselineSpanDays']} 天）", "",
        "> 不预设主题：统计每个词和短语的提及量，找出突然暴增、出现在多个独立来源的话题。纯统计方法，不使用语言模型，可按历史日期回放。"
        "信号只代表“有人开始大量讨论”，不代表利好或利空。", "",
    ]
    if payload["baselineWarning"]:
        lines += ["> ⚠️ 基线不足 7 天，结果噪声较大，仅供参考。", ""]
    if payload["warmingUpSources"]:
        lines += [f"> 新接入、尚在预热期的来源（不计入暴增判断）：{', '.join(payload['warmingUpSources'])}", ""]
    lines += ["> 只有“已确认”的话题（一周内两天报警、第二次带来新文章）才会送去映射公司；单日报警多为噪音。", "",
              "| # | 话题 | 状态 | 确认 | 近期/基线文章 | 暴增倍数 | z 值 | 来源数 | 权威来源 | 首次出现 |",
              "| ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |"]
    for index, s in enumerate(payload["signals"][:limit], 1):
        status = {"new-topic": "新话题", "tracked-theme": "已跟踪主题"}.get(s.get("status"), "")
        flag = "（单一来源主导）" if s["singleSourceDominated"] else ""
        lines.append(
            f"| {index} | {s['label']}{flag} | {status} | {'已确认' if s.get('confirmed') else '单日'} | {s['recentArticles']}/{s['baselineArticles']} | {s['burstRatio']}× | {s['zScore']} | "
            f"{s['sourceCount']} | {'是' if s['authoritySource'] else '否'} | {(s['firstSeen'] or '')[:10]} |"
        )
    for index, s in enumerate(payload["signals"][:min(limit, 8)], 1):
        lines += ["", f"## {index}. {s['label']}", ""]
        if s["relatedTerms"]:
            lines.append(f"相关词：{', '.join(s['relatedTerms'])}")
            lines.append("")
        lines += [f"- [{h['title']}]({h['url']}) — {h['source']}, {h['at'][:10]}" for h in s["headlines"]]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect suddenly emerging topics without preset themes")
    parser.add_argument("--database", action="append", default=[], help="Article database (repeatable)")
    parser.add_argument("--collect", help="Radar sources JSON to fetch before detecting")
    parser.add_argument("--radar-db", default=str(ROOT / "state/radar-news.db"))
    parser.add_argument("--theme-config", action="append", default=[], help="Configured themes, used only to tag known topics")
    parser.add_argument("--as-of", help="ISO date/time for historical replay; default now")
    parser.add_argument("--recent-days", type=int, default=3)
    parser.add_argument("--baseline-days", type=int, default=21)
    parser.add_argument("--history-days", type=int, default=90, help="History used to decide whether a word is normally common")
    parser.add_argument("--history", default=str(ROOT / "state/emerging-signals-history.json"), help="Daily run history for confirmation")
    parser.add_argument("--json-output", default=str(ROOT / "state/emerging-signals.json"))
    parser.add_argument("--markdown-output", default=str(ROOT / "outputs/emerging-signals.md"))
    args = parser.parse_args()

    collected = collect(args.collect, args.radar_db) if args.collect else []
    as_of = parse_time(args.as_of) if args.as_of else datetime.now(timezone.utc)
    if args.as_of and len(args.as_of) == 10:
        as_of = as_of.replace(hour=23, minute=59, second=59)
    databases = args.database + [args.radar_db]
    docs = load_docs(databases, as_of, max(args.history_days, args.recent_days + args.baseline_days))
    payload = detect(docs, as_of, args.recent_days, args.baseline_days)
    tag_known_themes(payload, args.theme_config)
    mark_confirmed(payload, update_history(Path(args.history), payload))
    payload["generatedAt"] = datetime.now(timezone.utc).isoformat()
    payload["databases"] = databases
    payload["collection"] = collected
    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_output).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload, args.markdown_output)
    print(json.dumps({"signals": len(payload["signals"]), "top": [s["label"] for s in payload["signals"][:5]],
                      "collected": [(c["name"], c["status"], c.get("inserted")) for c in collected]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
