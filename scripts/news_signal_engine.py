"""Frontier news as the trigger, Serenity analysis as the decision.

News answers "what changed, for whom, and which Serenity gates does it touch".
The recommendation comes from the Serenity analysis of that company (chokepoint or
not, which counter-theses hold, the sizing tier the skills imply), stored in
state/serenity-claude-verdicts.json. A company with material news but no Serenity
analysis yet is queued for one (state/serenity-analysis-queue.json) instead of being
recommended on news alone. A company that already has one, but has material news dated after
its review's latest primary document, is queued for a gate re-check
(state/serenity-news-recheck-queue.json); the card says which.

Earlier design notes (still accurate for the news layer):

Pipeline, run daily:
1. Collect: one Google News search per covered company (last 14 days) into
   state/company-news.db, on top of the theme feeds and the radar feeds.
2. Extract events: match articles to companies (whole-word names), drop quote
   pages, merge the same story from several outlets, and classify each event:
   regulatory, reimbursement, partnership, M&A, clinical, earnings, financing,
   leadership, legal, product or commentary. Each gets a direction (+/-), a
   materiality weight, the outlets that reported it, and the Serenity gates it
   bears on (a partnership bears on customer dependency, an FDA clearance on the
   chokepoint and supply-chain gates, a lawsuit on governance...).
3. News signal per company: materiality x direction, decayed with a 7-day
   half-life, squashed to -100..100. Commentary counts very little.
4. Combine with Serenity:
   - News-driven pick: material positive news AND the company clears the Serenity
     bar (evidence score >= 50, not rejected, AI exposure confirmed).
   - Promising, unproven: material positive news but Serenity evidence too thin.
   - Warning: material negative news.
   Each call lists the gates the news bears on, so the next Serenity review
   re-checks exactly those. News never passes a gate by itself.

The same articles are added to the Serenity evidence packets (serenity_evidence_review
reads state/company-news.db), so the scheduled review re-grades with the news.
Keyword rules, not a language model: transparent and replayable, but they misread
some headlines; every event links to its source.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
import sys
import urllib.parse
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from emerging_signal_detector import event_time  # noqa: E402
from event_revalidation_agent import mentions  # noqa: E402
from ai_medicine_topics import TOPICS, classify_topics, theme_direction  # noqa: E402

LOOKBACK_DAYS = 14
THEME_RECENT_DAYS = 7
THEME_BASELINE_DAYS = 21
THEME_WEIGHT = 0.4  # a theme moves a company less than news that names it
THEME_GATES = ["supply_chain_map", "chokepoint_evidence"]
AUTHORITY = ("who", "fda", "nih", "medrxiv", "biorxiv", "stat", "nature", "nejm", "lancet", "jama", "cms")
TOPIC_LABEL = {t["key"]: t["label"] for t in TOPICS}
HALF_LIFE_DAYS = 7
SERENITY_BAR = 50
EXCLUDE = {"NVDA"}  # compute benchmark; its news volume would swamp the AI-medicine names
NAME_OVERRIDES = {
    "PHG": ("Philips", '"Philips" (healthcare OR medical OR FDA OR imaging)'),
    "GRAL": ("GRAIL", '"GRAIL" (Galleri OR cancer OR "GRAIL Inc")'),
    "RDNT": ("RadNet", None), "HIMS": ("Hims & Hers", None), "GSK": ("GSK", None), "IQV": ("IQVIA", None),
    "MDT": ("Medtronic", None), "RMD": ("ResMed", None), "RYTM": ("Rhythm Pharmaceuticals", None), "WGS": ("GeneDx", None),
    "HTFL": ("HeartFlow", None), "SOPH": ("SOPHiA GENETICS", None), "TLX": ("Telix Pharmaceuticals", None),
}
EXTRA_ALIASES = {"TEM": ["Tempus"], "SDGR": ["Schrödinger", "Schrodinger"], "RDNT": ["DeepHealth"], "HTFL": ["Heartflow"], "ISRG": ["da Vinci"]}
QUOTE_PAGE = re.compile(r"stock price,? news,? quote|stock quote|price, news|share price & news|quote & history|stock price today", re.I)
# Opinion and valuation pieces ("Could Be 18% Undervalued", "Might Change The Case") are commentary, not events.
COMMENTARY = re.compile(r"\b(should you|is it time|buy now|top \d+|best .* stocks|stocks to watch|etf|what is really moving|what changed for|here's why|reasons to|is .* a buy|could .* soar|millionaire|investors should watch|might change|undervalued|overvalued|narrative|still intact|valuation|stretched|bargain|bull case|bear case|investment case|what .* means for|justify)\b", re.I)
STOP = set("a an and the of for to in on at by with as is are its it from after amid over new stock stocks shares inc corp says said".split())
# (type, pattern, default direction, materiality, gates it bears on). First match wins, so order matters.
EVENT_RULES = [
    ("legal", r"lawsuit|sued|class action|investigation|subpoena|short seller|short report|recall|warning letter", -1, 2.5, ["management_governance", "counter_thesis"]),
    # Insider trades ("CFO acquired 795 shares under an employee purchase plan") read as M&A on "acquired".
    ("insider", r"employee (?:stock )?purchase plan|\bespp\b|(?:acquired|bought|sold|purchased) [\d,]+ (?:\w+ )?shares|\binsider (?:buy|sell|purchase|sale|trad)|form 4\b|(?:director|officer|ceo|cfo|chief \w+) (?:buys|sells|bought|sold)", 0, 0.5, ["management_governance"]),
    ("regulatory", r"\bfda\b|clearance|cleared|510\(k\)|de novo|breakthrough device|approv|ce mark", 1, 3.0, ["chokepoint_evidence", "supply_chain_map"]),
    # Analyst actions mention "Partners" (Leerink Partners) and must not read as partnerships.
    ("analyst", r"maintains|reiterates|price target|raises target|initiates coverage|\brating\b|upgrade|downgrade", 0, 1.0, []),
    # Leadership needs a change of person; a CEO quoted in an earnings story is not a leadership event.
    ("leadership", r"resign|steps down|appoint|names .*(chief|ceo|cfo|president)|ceo (transition|succession|departure)|to retire|to (its )?board|board of directors", 0, 1.5, ["management_governance"]),
    ("reimbursement", r"\bcms\b|medicare|\bcpt\b|reimburs|coverage decision|payer coverage|ntap", 1, 3.0, ["customer_dependency", "earnings_validation"]),
    ("m&a", r"acquir|acquisition|merger|to buy |buyout|takeover", 0, 2.5, ["multi_node_control", "pure_play"]),
    ("earnings", r"\bq[1-4]\b|(first|second|third|fourth) quarter|quarterly|earnings|revenue|guidance|outlook|full-year|beats|misses|profit", 0, 2.0, ["earnings_validation"]),
    ("partnership", r"partner|collaborat|agreement with|deal with|teams up|alliance|signs .* (deal|agreement)|selects", 1, 2.5, ["customer_dependency", "multi_node_control"]),
    ("financing", r"offering|private placement|convertible|raises \$|notes due|at-the-market", -1, 1.5, ["counter_thesis"]),
    ("clinical", r"\btrial\b|phase [123i]|study (shows|finds|results)|data (show|presented)|published in|topline", 1, 2.0, ["counter_thesis"]),
    ("product", r"launch|unveil|introduc|rolls out|debuts|expands (access|availability)", 1, 1.5, ["supply_chain_map"]),
]
POSITIVE = re.compile(r"surge|soar|jump|rall|rises?\b|gains?\b|beats?\b|raises? (its )?(guidance|outlook|forecast)|record|wins?\b|upgrade|tops|strong|accelerat|approv|cleared|expands?|\bup \d+%|grew \d+|first (adjusted )?profit|inflection", re.I)
NEGATIVE = re.compile(r"plunge|tumble|slump|falls?\b|drops?\b|sinks?|miss(es)?\b|cuts? (its )?(guidance|outlook|forecast)|lowers|downgrade|weak|delay|halt|reject|denied|loss widens|widens|layoff|stumble|\bdown \d+%|wind down", re.I)
OFFICIAL = ("business wire", "businesswire", "globenewswire", "pr newswire", "prnewswire", "sec.gov", "fda.gov", "investor", "sec edgar", "federal register")
# SEC 8-K item codes are SEC's own event taxonomy, so filings skip headline guessing.
# (item, type, direction, materiality, gates); the most material item in a filing wins.
FILING_ITEMS = [
    ("4.02", "legal", -1, 3.0, ["earnings_validation", "management_governance"]),   # restatement
    ("3.01", "legal", -1, 3.0, ["counter_thesis"]),                                  # delisting notice
    ("1.03", "legal", -1, 3.0, ["counter_thesis"]),                                  # bankruptcy
    ("2.01", "m&a", 0, 2.5, ["multi_node_control", "pure_play"]),
    ("1.01", "partnership", 0, 2.5, ["customer_dependency", "multi_node_control"]),  # could also be a credit agreement
    ("1.02", "partnership", -1, 2.5, ["customer_dependency"]),
    ("2.06", "earnings", -1, 2.0, ["earnings_validation"]),                          # impairment
    ("2.05", "earnings", -1, 2.0, ["earnings_validation"]),                          # restructuring
    ("2.02", "earnings", 0, 2.0, ["earnings_validation"]),
    ("2.03", "financing", -1, 1.5, ["counter_thesis"]),
    ("3.02", "financing", -1, 1.5, ["counter_thesis"]),
    ("5.02", "leadership", 0, 1.5, ["management_governance"]),
    ("4.01", "leadership", 0, 1.5, ["management_governance"]),                       # auditor change
]
MAJOR = ("reuters", "bloomberg", "wall street journal", "wsj", "barron", "cnbc", "stat", "fierce", "endpoints", "biopharma dive", "financial times", "the new york times")


def coverage(root: Path = ROOT) -> list[dict]:
    """Every company with a Serenity assessment, with a search query and matching aliases."""
    assessed = [r["ticker"] for r in json.loads((root / "state/serenity-auto-assessments.json").read_text(encoding="utf-8")).get("companies", [])]
    known = {c["ticker"]: c for c in json.loads((root / "trend-agent/companies.example.json").read_text(encoding="utf-8")).get("companies", [])}
    screen_path = root / "state/ai-medicine-universe-screen.json"
    screened = {r["ticker"]: r["company"] for r in json.loads(screen_path.read_text(encoding="utf-8")).get("companies", [])} if screen_path.exists() else {}
    out = []
    for ticker in assessed:
        if ticker in EXCLUDE:
            continue
        name, query = NAME_OVERRIDES.get(ticker, (None, None))
        if not name:
            raw = known.get(ticker, {}).get("name") or screened.get(ticker) or ticker
            name = re.sub(r",?\s+(inc|corp|corporation|ltd|plc|n\.v|nv|s\.a|sa|ag|holdings|holdings corp)\.?$", "", raw, flags=re.I).strip()
            name = name.title() if name.isupper() and len(name) > 5 else name
        aliases = list(dict.fromkeys([name, *known.get(ticker, {}).get("company_terms", []), *EXTRA_ALIASES.get(ticker, [])]))
        out.append({"ticker": ticker, "name": name, "query": query or f'"{name}"', "aliases": [a for a in aliases if a and a != ticker]})
    return out


def collect(companies: list[dict], database: Path) -> list[dict]:
    sys.path.insert(0, str(ROOT / "trend-agent/src"))
    from trend_agent.database import connect, insert_articles  # noqa: E402
    from trend_agent.feeds import fetch_feed  # noqa: E402

    connection = connect(database)
    results = []
    for company in companies:
        url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
            {"q": f"{company['query']} when:{LOOKBACK_DAYS}d", "hl": "en-US", "gl": "US", "ceid": "US:en"})
        try:
            articles = fetch_feed(url, f"Google News · {company['ticker']}", 20)[:60]
            inserted, _ = insert_articles(connection, articles)
            results.append({"ticker": company["ticker"], "status": "ok", "fetched": len(articles), "inserted": inserted})
        except Exception as exc:  # one failed search must not stop the rest
            results.append({"ticker": company["ticker"], "status": "error", "error": str(exc)[:120]})
    connection.close()
    return results


def load_articles(databases: list[Path], as_of: datetime, lookback_days: int = LOOKBACK_DAYS) -> list[dict]:
    start = as_of - timedelta(days=lookback_days)
    rows = []
    for database in databases:
        if not database.exists():
            continue
        connection = sqlite3.connect(database)
        for source, title, url, content, published, discovered in connection.execute(
                "SELECT source, title, url, content, published_at, discovered_at FROM articles"):
            at = event_time(published, discovered)
            if at and start <= at <= as_of:
                rows.append({"source": source or "", "title": title or "", "url": url or "", "content": (content or "")[:400], "at": at})
        connection.close()
    return rows


def headline(title: str) -> tuple[str, str]:
    """Split 'Headline - Publisher' as Google News formats it."""
    if " - " in title:
        head, _, publisher = title.rpartition(" - ")
        if len(publisher) <= 60:
            return head.strip(), publisher.strip()
    return title.strip(), ""


def classify(text: str) -> dict:
    lowered = text.lower()
    if COMMENTARY.search(lowered):
        kind, base_direction, weight, gates = "commentary", 0, 0.3, []
    else:
        kind, base_direction, weight, gates = "commentary", 0, 0.3, []
        for name, pattern, direction, materiality, affected in EVENT_RULES:
            if re.search(pattern, lowered):
                kind, base_direction, weight, gates = name, direction, materiality, affected
                break
    pos, neg = bool(POSITIVE.search(lowered)), bool(NEGATIVE.search(lowered))
    direction = 1 if pos and not neg else -1 if neg and not pos else base_direction
    return {"type": kind, "direction": direction, "materiality": weight, "gates": gates}


def classify_filing(content: str) -> dict:
    """Event from an SEC filing's form and 8-K items (content written by official_feeds.py)."""
    items = set(re.search(r"items=([\d.,]*)", content).group(1).split(",")) if "items=" in content else set()
    for item, kind, direction, materiality, gates in FILING_ITEMS:
        if item in items:
            return {"type": kind, "direction": direction, "materiality": materiality, "gates": gates}
    if items & {"7.01", "8.01"}:
        return {"type": "disclosure", "direction": 0, "materiality": 1.0, "gates": []}
    return {"type": "filing", "direction": 0, "materiality": 1.0, "gates": ["earnings_validation"]}


def credibility(publisher: str, source: str) -> float:
    text = f"{publisher} {source}".lower()
    if any(m in text for m in OFFICIAL):
        return 1.3
    if any(m in text for m in MAJOR):
        return 1.2
    return 1.0


def extract_events(companies: list[dict], articles: list[dict], as_of: datetime) -> dict[str, list[dict]]:
    events: dict[str, list[dict]] = {c["ticker"]: [] for c in companies}
    for article in articles:
        head, publisher = headline(article["title"])
        if QUOTE_PAGE.search(article["title"]):
            continue
        for company in companies:
            if not any(mentions(head, alias) for alias in company["aliases"]):
                continue
            info = classify_filing(article["content"]) if article["source"].startswith("SEC EDGAR") else classify(head)
            key = re.sub(r"[^a-z0-9 ]", "", head.lower())[:90]
            bucket = events[company["ticker"]]
            # The same story from several outlets is one event with several sources.
            words = {w for w in re.findall(r"[a-z0-9]+", head.lower()) if w not in STOP and not any(w in a.lower().split() for a in company["aliases"])}

            def same_story(e) -> bool:
                if e["key"] == key:
                    return True
                if abs((e["at"] - article["at"]).days) > 3:
                    return False
                overlap = len(words & e["words"]) / max(1, len(words | e["words"]))
                # An earnings release is one event however outlets phrase it; other types need similar wording.
                return overlap >= 0.35 or (info["type"] == e["type"] == "earnings" and abs((e["at"] - article["at"]).days) <= 2)

            twin = next((e for e in bucket if same_story(e)), None)
            outlet = publisher or article["source"]
            if twin:
                if outlet not in twin["sources"]:
                    twin["sources"].append(outlet)
                    twin["votes"].append(info["direction"])
                twin["credibility"] = max(twin["credibility"], credibility(publisher, article["source"]))
                continue
            bucket.append({**info, "key": key, "words": words, "title": head, "url": article["url"], "at": article["at"], "sources": [outlet],
                           "votes": [info["direction"]], "credibility": credibility(publisher, article["source"])})
    for ticker, bucket in events.items():
        for event in bucket:
            # One story, many outlets: direction is the sign of all headlines' votes, so one neutral
            # first headline ("Revenue Up 23%") cannot hide eleven positive ones.
            tally = sum(event.pop("votes"))
            event["direction"] = (tally > 0) - (tally < 0)
            age = max(0.0, (as_of - event["at"]).total_seconds() / 86400)
            corroboration = 1 + 0.15 * min(len(event["sources"]) - 1, 4)
            event["weight"] = round(event["materiality"] * event["credibility"] * corroboration * 0.5 ** (age / HALF_LIFE_DAYS), 3)
            event["material"] = event["type"] != "commentary" and event["materiality"] >= 2 and (len(event["sources"]) >= 2 or event["credibility"] >= 1.2)
        bucket.sort(key=lambda e: (-e["weight"] * (1 if e["direction"] else 0.3), -e["at"].timestamp()))
    return events


def theme_credibility(publisher: str, source: str) -> float:
    text = f"{publisher} {source}".lower()
    if "arxiv" in text:
        return 0.3  # high-volume academic feed: frontier, but each paper says little on its own
    if any(re.search(rf"\b{m}\b", text) for m in AUTHORITY):
        return 1.3
    return credibility(publisher, source)


def extract_themes(companies: list[dict], articles: list[dict], as_of: datetime, exposure: dict) -> dict:
    """Frontier articles that name no covered company, grouped into AI-medicine topics.

    Heat compares the last 7 days with the weekly average of the 21 days before, so a
    topic that is always discussed (imaging papers on arXiv) does not give a permanent
    tailwind; only a topic heating up, or clear regulatory/payment news, does.
    """
    recent_start = as_of - timedelta(days=THEME_RECENT_DAYS)
    seen: set[tuple[str, str]] = set()
    topics = {t["key"]: {"key": t["key"], "label": t["label"], "recent": [], "baselineWeight": 0.0} for t in TOPICS}
    for article in articles:
        head, publisher = headline(article["title"])
        if QUOTE_PAGE.search(article["title"]) or any(mentions(head, a) for c in companies for a in c["aliases"]):
            continue  # company-named news is handled as a direct event
        text = f"{head} {article['content'][:300]}"
        for key in classify_topics(text):
            dedup = (key, re.sub(r"[^a-z0-9 ]", "", head.lower())[:80])
            if dedup in seen:
                continue
            seen.add(dedup)
            direction = theme_direction(head)
            weight = theme_credibility(publisher, article["source"]) * (1.0 * direction if direction else 0.5)
            if article["at"] >= recent_start:
                topics[key]["recent"].append({"title": head, "url": article["url"], "at": article["at"].isoformat(),
                                              "source": publisher or article["source"], "direction": direction, "weight": round(weight, 2)})
            else:
                topics[key]["baselineWeight"] += weight
    out = {}
    for key, topic in topics.items():
        recent_weight = sum(a["weight"] for a in topic["recent"])
        expected = topic["baselineWeight"] / (THEME_BASELINE_DAYS / THEME_RECENT_DAYS)
        sources = {a["source"] for a in topic["recent"]}
        heat = round(recent_weight - 0.8 * expected, 2)
        topic["recent"].sort(key=lambda a: (-abs(a["weight"]), a["at"]), reverse=False)
        covered = {c["ticker"] for c in companies}
        exposed = exposure.get("topics", {}).get(key, {}).get("companies", {})
        investable = exposure.get("investable") or set()
        out[key] = {
            "key": key, "label": topic["label"], "articles": len(topic["recent"]), "sources": len(sources),
            "recentWeight": round(recent_weight, 2), "expectedWeight": round(expected, 2), "heat": heat,
            # A final or proposed FDA/CMS rule is material on its own; news needs corroboration.
            "material": (len(topic["recent"]) >= 3 and len(sources) >= 2 and heat > 0)
                        or any(a["source"].startswith("Federal Register") and " Rule:" in a["title"] for a in topic["recent"]),
            "headlines": topic["recent"][:4],
            "covered": [{"ticker": t, "strength": v["strength"], "relation": v.get("relation")} for t, v in exposed.items() if t in covered][:8],
            # Only names that passed the market-wide screen's size and liquidity test; micro caps are not shown.
            "uncovered": [{"ticker": t, "company": v["company"], "strength": v["strength"], "relation": v.get("relation")} for t, v in exposed.items() if t not in covered and t in investable][:5],
        }
    return out


def theme_contributions(ticker: str, themes: dict) -> list[dict]:
    rows = []
    for key, topic in themes.items():
        strength = next((c["strength"] for c in topic["covered"] if c["ticker"] == ticker), 0)
        if strength and topic["heat"] > 0:
            rows.append({"topic": key, "label": topic["label"], "strength": strength, "heat": topic["heat"],
                         "contribution": round(THEME_WEIGHT * strength * topic["heat"], 2), "material": topic["material"] and strength >= 0.5,
                         "headline": (topic["headlines"] or [{}])[0]})
    return sorted(rows, key=lambda r: -r["contribution"])


def news_signal(events: list[dict], themes: list[dict] | None = None) -> float:
    total = sum(e["weight"] * e["direction"] for e in events) + sum(t["contribution"] for t in themes or [])
    return round(math.tanh(total / 6) * 100, 1)


def serenity_tier(tier_text: str) -> str:
    """Map a free-text Serenity sizing tier to a page tier."""
    text = (tier_text or "").lower()
    if "standard" in text:
        return "serenity-standard"
    if "starter" in text:
        return "serenity-starter"
    return "serenity-watch"


# News types that can change a Serenity conclusion. Analyst notes, commentary and insider trades do not.
RECHECK_TYPES = {"earnings", "legal", "regulatory", "reimbursement", "m&a", "leadership", "financing",
                 "partnership", "clinical", "product", "filing", "disclosure"}
PERIOD_ENDS = {"0331", "0630", "0930", "1231"}
FILING_LAG_DAYS = 40  # a 10-Q/10-K usually reaches EDGAR 30-45 days after its period ends
SAME_QUARTER_DAYS = 45  # earnings news this soon after the evidence date is about the quarter already read


def evidence_through(packet: dict) -> date | None:
    """Latest date the review's primary documents speak for.

    SEC file names carry a date: a period end (rdnt-20260930.htm, filed ~40 days later) or the
    document date of an 8-K exhibit (htfl-20261112xex99_1.htm). FDA passages carry publishedAt.
    """
    latest = None
    for passage in packet.get("evidence", []):
        found = re.search(r"(20\d{2})(\d{2})(\d{2})", passage.get("url", "").rsplit("/", 1)[-1])
        day = None
        if found:
            try:
                day = date(int(found.group(1)), int(found.group(2)), int(found.group(3)))
            except ValueError:
                day = None
            if day and found.group(2) + found.group(3) in PERIOD_ENDS:
                day = day + timedelta(days=FILING_LAG_DAYS)
        elif passage.get("publishedAt"):
            try:
                day = date.fromisoformat(str(passage["publishedAt"])[:10])
            except ValueError:
                day = None
        if day and (latest is None or day > latest):
            latest = day
    return latest


def news_recheck(bucket: list[dict], through: date | None) -> dict:
    """Material news dated after the review's evidence reopens the gates it bears on."""
    if through is None:
        return {"status": "no-review-evidence", "evidenceThrough": None, "events": [], "gates": []}
    fresh = []
    for e in bucket:
        at = e.get("at")
        day = at.date() if isinstance(at, datetime) else (date.fromisoformat(str(at)[:10]) if at else None)
        periodic = e.get("type") == "earnings" or (e.get("type") == "filing" and re.search(r"10-[QK]|20-F|6-K", e.get("title", "")))
        # Earnings-call write-ups and analyses of a quarter whose report is already in the evidence add nothing new.
        if periodic and day and (day - through).days <= SAME_QUARTER_DAYS:
            continue
        if day and day > through and e.get("type") in RECHECK_TYPES and e.get("materiality", 0) >= 1.0:
            fresh.append({"title": e["title"], "type": e["type"], "date": day.isoformat(), "url": e.get("url"),
                          "gates": e.get("gates") or ["earnings_validation"]})
    gates = sorted({g for e in fresh for g in e["gates"]})
    return {"status": "queued" if fresh else "current", "evidenceThrough": through.isoformat(), "events": fresh[:5], "gates": gates}


def recommend(companies: list[dict], events: dict[str, list[dict]], root: Path = ROOT, themes: dict | None = None) -> list[dict]:
    gates = {r["ticker"]: r for r in json.loads((root / "state/serenity-gate-results.json").read_text(encoding="utf-8")).get("companies", [])}
    top5_path = root / "state/ai-medicine-top5.json"
    ranked = {r["ticker"]: r for r in json.loads(top5_path.read_text(encoding="utf-8")).get("ranking", [])} if top5_path.exists() else {}
    verdict_path = root / "state/serenity-claude-verdicts.json"
    verdicts = {r["ticker"]: r for r in json.loads(verdict_path.read_text(encoding="utf-8")).get("companies", [])} if verdict_path.exists() else {}
    manifest_path = root / "state/serenity-claude-queue.json"
    packets = {}
    if manifest_path.exists():
        for entry in json.loads(manifest_path.read_text(encoding="utf-8")).get("companies", []):
            path = root / entry.get("packetPath", "")
            if path.exists():
                packets[entry["ticker"]] = json.loads(path.read_text(encoding="utf-8"))
    calls = []
    for company in companies:
        ticker = company["ticker"]
        bucket = events.get(ticker, [])
        via = theme_contributions(ticker, themes or {})
        signal = news_signal(bucket, via)
        gate = gates.get(ticker, {})
        rank_row = ranked.get(ticker, {})
        evidence = gate.get("substantiatedScore", 0)
        material_pos = [e for e in bucket if e["material"] and e["direction"] > 0]
        material_themes = [t for t in via if t["material"]]
        material_neg = [e for e in bucket if e["material"] and e["direction"] < 0]
        serenity_ok = evidence >= SERENITY_BAR and gate.get("decision") != "reject" and not rank_row.get("aiUnverified")
        if material_neg and signal < 0:
            tier = "warning"
        elif (material_pos or material_themes) and signal >= 25 and serenity_ok:
            tier = "pick"
        elif (material_pos or material_themes) and signal >= 25:
            tier = "unproven"
        else:
            tier = "no catalyst"
        why_not = []
        if tier == "unproven":
            if evidence < SERENITY_BAR:
                why_not.append(f"Serenity evidence {evidence} is below {SERENITY_BAR}")
            if rank_row.get("aiUnverified"):
                why_not.append("AI exposure not confirmed by the market-wide screen")
            if gate.get("decision") == "reject":
                why_not.append("Serenity decision is reject")
        recheck = sorted({g for e in material_pos + material_neg for g in e["gates"]} | ({*THEME_GATES} if material_themes else set()))
        # News is the trigger; the Serenity analysis decides.
        trigger = "negative" if material_neg and signal < 0 else "positive" if (material_pos or material_themes) and signal >= 25 else "none"
        verdict = verdicts.get(ticker)
        if trigger == "negative":
            decision = "warning"
        elif verdict:
            decision = serenity_tier(verdict.get("tier", ""))
        elif trigger == "positive":
            decision = "awaiting-serenity"
        else:
            decision = "no catalyst"
        potential = rank_row.get("potential", {}).get("total")
        score = round(0.5 * max(signal, 0) + 0.3 * (potential if potential is not None else evidence) + 0.2 * evidence, 1)
        calls.append({
            "ticker": ticker, "company": company["name"], "tier": tier, "newsSignal": signal, "callScore": score,
            "serenityEvidence": evidence, "serenityDecision": gate.get("decision", "unreviewed"), "potential": potential,
            "bucket": rank_row.get("bucket"), "aiUnverified": bool(rank_row.get("aiUnverified")),
            "gatesToRecheck": recheck, "whyNotPick": why_not,
            "events": [{k: (v.isoformat() if isinstance(v, datetime) else v) for k, v in e.items() if k not in ("key", "words")} for e in bucket[:6]],
            "eventCount": len(bucket), "materialEvents": len(material_pos) + len(material_neg),
            "themes": via[:3], "driver": ("company news" if material_pos or material_neg else "theme" if material_themes else "none"),
            "trigger": trigger, "decision": decision,
            "serenity": ({k: verdict.get(k) for k in ("chokepoint", "countersHolding", "bucket", "tier", "verdict", "memo")} if verdict else None),
            # Reviewed companies: does news after the review's latest primary document reopen any gates?
            "recheck": news_recheck(bucket, evidence_through(packets[ticker])) if verdict and ticker in packets else None,
        })
    order = {"serenity-standard": 0, "serenity-starter": 1, "serenity-watch": 2, "awaiting-serenity": 3, "warning": 4, "no catalyst": 5}
    calls.sort(key=lambda c: (order[c["decision"]], -c["newsSignal"]))
    return calls


TIER_ZH = {"pick": "本周推荐", "unproven": "有利好但待验证", "warning": "负面警示", "no catalyst": "无重大新闻"}


def write_markdown(payload: dict, path: Path) -> None:
    lines = ["# 新闻驱动的推荐", "",
             f"截至 {payload['asOf'][:16]}，回看 {LOOKBACK_DAYS} 天。", "",
             "> 先看新闻：按公司抓取并识别事件（合作、FDA、医保、临床、财报、融资、诉讼等），按重要性、方向、来源可信度和时效打分；"
             f"再用 Serenity 把关：证据分 ≥{SERENITY_BAR}、未被否决、AI 属性已确认，才进入本周推荐。新闻本身不会让任何门槛通过，只会指出下一轮该复核哪些门槛。", "",
             "| 判断 | 股票 | 新闻信号 | 重大事件 | Serenity 证据 | 需复核的门槛 | 主要新闻 |", "| --- | --- | ---: | ---: | ---: | --- | --- |"]
    for c in payload["calls"]:
        if c["tier"] == "no catalyst":
            continue
        top = c["events"][0] if c["events"] else None
        link = f"[{top['title'][:70]}]({top['url']})（{top['type']}）" if top else ""
        lines.append(f"| {TIER_ZH[c['tier']]} | {c['ticker']} | {c['newsSignal']:+.0f} | {c['materialEvents']} | {c['serenityEvidence']} | {', '.join(c['gatesToRecheck']) or '—'} | {link} |")
    quiet = [c["ticker"] for c in payload["calls"] if c["tier"] == "no catalyst"]
    lines += ["", f"本期无重大新闻：{', '.join(quiet) or '无'}", ""]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Turn frontier news into Serenity-gated recommendations")
    parser.add_argument("--collect", action="store_true", help="Fetch one Google News search per covered company first")
    parser.add_argument("--as-of", help="ISO date/time; default now")
    parser.add_argument("--company-db", default=str(ROOT / "state/company-news.db"))
    parser.add_argument("--json-output", default=str(ROOT / "state/news-recommendations.json"))
    parser.add_argument("--markdown-output", default=str(ROOT / "outputs/news-recommendations.md"))
    args = parser.parse_args()
    as_of = datetime.fromisoformat(args.as_of).replace(tzinfo=timezone.utc) if args.as_of else datetime.now(timezone.utc)
    companies = coverage()
    collected = collect(companies, Path(args.company_db)) if args.collect else []
    databases = [Path(args.company_db), ROOT / "trend-agent/state/daily-news.db", ROOT / "state/radar-news.db", ROOT / "state/policy-news.db"]
    events = extract_events(companies, load_articles(databases, as_of), as_of)
    exposure_path = ROOT / "state/topic-exposure.json"
    exposure = json.loads(exposure_path.read_text(encoding="utf-8")) if exposure_path.exists() else {}
    screen_path = ROOT / "state/ai-medicine-universe-screen.json"
    if screen_path.exists():
        exposure["investable"] = {r["ticker"] for r in json.loads(screen_path.read_text(encoding="utf-8")).get("companies", []) if r.get("investable")}
    themes = extract_themes(companies, load_articles(databases, as_of, THEME_RECENT_DAYS + THEME_BASELINE_DAYS), as_of, exposure)
    calls = recommend(companies, events, themes=themes)
    payload = {"generatedAt": datetime.now(timezone.utc).isoformat(), "asOf": as_of.isoformat(), "lookbackDays": LOOKBACK_DAYS,
               "serenityBar": SERENITY_BAR, "collection": collected, "calls": calls,
               "themes": sorted(themes.values(), key=lambda t: -t["heat"]),
               "summary": {d: [c["ticker"] for c in calls if c["decision"] == d] for d in ("serenity-standard", "serenity-starter", "awaiting-serenity", "warning")}}
    # The next step after the news: which companies need a Serenity analysis, and on which gates.
    queue = [{"ticker": c["ticker"], "company": c["company"], "reason": c["trigger"] + " news", "newsSignal": c["newsSignal"],
              "gatesToRecheck": c["gatesToRecheck"], "events": c["events"][:3], "themes": c["themes"][:2],
              "hasSerenityMemo": bool(c["serenity"])}
             for c in calls if c["trigger"] != "none" and (not c["serenity"] or c["trigger"] == "negative")]
    (ROOT / "state/serenity-analysis-queue.json").write_text(json.dumps({"generatedAt": payload["generatedAt"], "queue": sorted(queue, key=lambda q: -abs(q["newsSignal"]))}, indent=2, ensure_ascii=False), encoding="utf-8")
    # Reviewed companies with material news dated after their review's evidence: re-check those gates.
    rechecks = [{"ticker": c["ticker"], "company": c["company"], "tier": (c.get("serenity") or {}).get("tier"), **c["recheck"]}
                for c in payload["calls"] if (c.get("recheck") or {}).get("status") == "queued"]
    (ROOT / "state/serenity-news-recheck-queue.json").write_text(json.dumps({"generatedAt": payload["generatedAt"], "queue": rechecks}, indent=2, ensure_ascii=False), encoding="utf-8")
    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_output).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload, Path(args.markdown_output))
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
