"""Dynamic beneficiary mapper: which listed companies have real exposure to a new topic?

The hand-written theme-company map only covers themes someone anticipated. This
module starts from a topic phrase (usually an emerging signal) and asks primary,
time-stamped sources who is actually involved:

1. SEC EDGAR full-text search: companies whose filings mention the phrase inside
   a date window ending at ``as_of``. The 8-K item code separates two very
   different situations: an event announcement (items 7.01/8.01/1.01) usually
   means the company is announcing work on the topic, while a mention inside an
   earnings release (item 2.02) usually describes the topic as a business impact.
   In the January 2020 coronavirus replay, announcements came from Moderna, Vir,
   Meridian and OpGen; earnings mentions came from Starbucks, Las Vegas Sands and
   device makers describing China disruption.
2. ClinicalTrials.gov: industry sponsors that registered trials on the topic
   before ``as_of``, matched to the EDGAR companies by name.
3. Optional filing text (needs ``SEC_USER_AGENT`` with your own contact, per
   SEC's fair-access policy): the sentence that mentions the phrase is checked
   for capability language (vaccine, assay, collaboration, award) versus impact
   language (disruption, closure, adversely affected).

Companies are then split by industry (SIC code) into capability candidates
(therapeutics, diagnostics, devices, care delivery, health research) and
companies that are more likely exposed to the topic as a cost or disruption.

No language model is used, so a historical replay (``--as-of 2020-01-31``) only
sees what was filed by then. Candidates are handed to Serenity for screening;
nothing here is a buy list.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import ssl
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_AGENT = "FocusKPI-Research-Agent/0.1"
EFTS = "https://efts.sec.gov/LATEST/search-index"
CTGOV = "https://clinicaltrials.gov/api/v2/studies"
FORMS = "8-K,6-K,10-Q,10-K,20-F,S-1,F-1,424B4"

# SIC code -> capability group. Anything else is "other sector".
SIC_GROUPS = [
    ("Therapeutics & vaccines", {2833, 2834, 2836}),
    ("Diagnostics & labs", {2835, 8071, 8734, 3826}),
    ("Health research services", {8731, 8733}),
    ("Medical devices & supplies", {3841, 3842, 3843, 3844, 3845, 3851, 5047, 5122}),
    ("Care delivery", set(range(8000, 8100)) - {8071}),
]
GROUP_WEIGHT = {
    "Therapeutics & vaccines": 3, "Diagnostics & labs": 3, "Health research services": 2,
    "Medical devices & supplies": 2, "Care delivery": 1, "Other sector": 0,
}
CAPABILITY_WORDS = (
    "vaccine", "candidate", "develop", "program", "collaborat", "partner", "assay", "test kit", "diagnostic",
    "antibod", "antiviral", "therapeut", "clinical trial", "phase 1", "phase i", "award", "contract", "grant",
    "funding", "launch", "manufactur", "supply agreement", "emergency use", "cepi", "barda", "nih",
)
IMPACT_WORDS = (
    "adversely", "impact on our", "disruption", "closure", "closed", "suspend", "cancel", "decline in",
    "reduced demand", "travel restriction", "uncertainty", "headwind", "lower traffic", "outbreak could",
)


def http_json(url: str, agent: str, timeout: int = 30, retries: int = 2) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": agent, "Accept": "application/json"})
    system_ca = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(system_ca) if system_ca.exists() else None)
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception:
            if attempt == retries:
                raise
            time.sleep(1.5 * (attempt + 1))
    return {}


def http_text(url: str, agent: str, timeout: int = 30) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": agent})
    system_ca = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(system_ca) if system_ca.exists() else None)
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        return response.read().decode("utf-8", errors="replace")


def sic_group(sics: list) -> str:
    for code in sics or []:
        try:
            value = int(code)
        except (TypeError, ValueError):
            continue
        for name, codes in SIC_GROUPS:
            if value in codes:
                return name
    return "Other sector"


DISPLAY = re.compile(r"^(?P<name>.*?)\s+(?:\((?P<ticker>[A-Z0-9.\-, ]+)\)\s+)?\(CIK (?P<cik>\d+)\)\s*$")


def parse_display_name(value: str) -> dict:
    match = DISPLAY.match(value.strip())
    if not match:
        return {"name": value.strip(), "ticker": None, "cik": None}
    tickers = [t.strip() for t in (match.group("ticker") or "").split(",") if t.strip()]
    return {"name": match.group("name").strip(), "ticker": tickers[0] if tickers else None, "cik": match.group("cik").lstrip("0")}


def search_edgar(phrase: str, start: date, end: date, agent: str, max_hits: int = 300, fetch=http_json) -> list[dict]:
    hits: list[dict] = []
    offset = 0
    while offset < max_hits:
        query = urllib.parse.urlencode({
            "q": f'"{phrase}"', "dateRange": "custom", "startdt": start.isoformat(), "enddt": end.isoformat(),
            "forms": FORMS, "from": offset,
        })
        payload = fetch(f"{EFTS}?{query}", agent)
        page = payload.get("hits", {}).get("hits", [])
        hits.extend(page)
        total = payload.get("hits", {}).get("total", {}).get("value", 0)
        offset += len(page)
        if not page or offset >= total:
            break
        time.sleep(0.2)  # stay well under SEC's request-rate limit
    return hits


def filing_url(cik: str, hit_id: str) -> str:
    adsh, _, filename = hit_id.partition(":")
    folder = adsh.replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{folder}/{filename}" if filename else f"https://www.sec.gov/Archives/edgar/data/{cik}/{folder}/"


def aggregate(hits: list[dict]) -> dict[str, dict]:
    companies: dict[str, dict] = {}
    for hit in hits:
        source = hit.get("_source", {})
        names = source.get("display_names") or []
        if not names:
            continue
        who = parse_display_name(names[0])
        key = who["cik"] or who["name"]
        row = companies.setdefault(key, {
            **who, "sicGroup": sic_group(source.get("sics", [])), "sics": source.get("sics", []),
            "filings": {}, "announcements": 0, "earningsMentions": 0, "firstFiled": None,
        })
        adsh = source.get("adsh") or hit.get("_id", "").split(":")[0]
        form = source.get("form") or (source.get("root_forms") or [""])[0]
        filed = source.get("file_date")
        items = set(source.get("items") or [])
        is_press = form in {"8-K", "6-K"} and str(source.get("file_type", "")).upper().startswith("EX-99")
        new_filing = adsh not in row["filings"]
        record = row["filings"].setdefault(adsh, {"form": form, "filed": filed, "url": filing_url(row["cik"] or "", hit.get("_id", "")), "pressRelease": False, "kind": filing_kind(form, items)})
        if is_press and not record["pressRelease"]:
            record["pressRelease"] = True
            record["url"] = filing_url(row["cik"] or "", hit.get("_id", ""))
        if new_filing:
            if record["kind"] == "announcement":
                row["announcements"] += 1
            elif record["kind"] == "earnings":
                row["earningsMentions"] += 1
        if filed and (row["firstFiled"] is None or filed < row["firstFiled"]):
            row["firstFiled"] = filed
    return companies


def filing_kind(form: str, items: set[str]) -> str:
    """announcement / earnings / periodic, from the form type and 8-K item codes."""
    if form in {"8-K", "6-K"}:
        if "2.02" in items:
            return "earnings"
        if items & {"7.01", "8.01", "1.01"} or form == "6-K":
            return "announcement"
        return "other-current"
    return "periodic"


def normalize_name(value: str) -> str:
    value = re.sub(r"[^a-z0-9 ]", " ", value.lower())
    drop = {"inc", "corp", "corporation", "co", "ltd", "plc", "llc", "sa", "ag", "nv", "the", "company", "holdings", "group"}
    return " ".join(w for w in value.split() if w not in drop)


def trial_sponsors(phrase: str, as_of: date, lookback_days: int, fetch=http_json) -> list[dict]:
    start = as_of - timedelta(days=lookback_days)
    query = urllib.parse.urlencode({
        "query.term": phrase,
        "filter.advanced": f"AREA[StudyFirstPostDate]RANGE[{start.isoformat()},{as_of.isoformat()}]",
        "fields": "NCTId,LeadSponsorName,LeadSponsorClass,StudyFirstPostDate,BriefTitle",
        "pageSize": 200,
    })
    payload = fetch(f"{CTGOV}?{query}", DEFAULT_AGENT)
    sponsors = []
    for study in payload.get("studies", []):
        section = study.get("protocolSection", {})
        sponsor = section.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {})
        if sponsor.get("class") != "INDUSTRY":
            continue
        sponsors.append({
            "sponsor": sponsor.get("name", ""),
            "nctId": section.get("identificationModule", {}).get("nctId"),
            "title": section.get("identificationModule", {}).get("briefTitle"),
            "firstPosted": section.get("statusModule", {}).get("studyFirstPostDateStruct", {}).get("date"),
        })
    return sponsors


def attach_trials(companies: dict[str, dict], sponsors: list[dict]) -> list[dict]:
    by_name = {normalize_name(row["name"]): row for row in companies.values()}
    unmatched = []
    for trial in sponsors:
        key = normalize_name(trial["sponsor"])
        row = by_name.get(key) or next((r for n, r in by_name.items() if key and (n.startswith(key) or key.startswith(n))), None)
        if row is None:
            unmatched.append(trial)
            continue
        row.setdefault("trials", []).append(trial)
    return unmatched


def sentence_context(text: str, phrase: str, width: int = 260) -> str:
    plain = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text)))
    match = re.search(re.escape(phrase), plain, re.IGNORECASE)
    if not match:
        return ""
    return plain[max(0, match.start() - width): match.end() + width].strip()


def classify_context(snippet: str) -> str:
    lowered = snippet.lower()
    capability = sum(word in lowered for word in CAPABILITY_WORDS)
    impact = sum(word in lowered for word in IMPACT_WORDS)
    if capability > impact:
        return "capability"
    if impact > capability:
        return "impact"
    return "unclear"


def score_company(row: dict) -> float:
    filings = list(row["filings"].values())
    periodic = sum(1 for f in filings if f["kind"] == "periodic")
    score = GROUP_WEIGHT.get(row["sicGroup"], 0) * 2.0
    score += 4.0 * min(row["announcements"], 2) + 0.5 * min(row["earningsMentions"], 2) + 0.5 * min(periodic, 2)
    score += 3.0 * min(len(row.get("trials", [])), 2)
    score += {"capability": 4.0, "impact": -4.0}.get(row.get("context", {}).get("label"), 0.0)
    return round(score, 1)


def relation(row: dict) -> str:
    label = (row.get("context") or {}).get("label")
    health = row["sicGroup"] != "Other sector"
    if label == "impact":
        return "exposed (likely impacted)"
    if label == "capability" or row.get("trials") or (health and row["announcements"]):
        return "capability candidate"
    if health:
        return "health company, mention only"
    return "exposed (likely impacted)" if row["earningsMentions"] or row["announcements"] else "mention"


def map_topic(phrase: str, as_of: date, lookback_days: int = 60, agent: str = DEFAULT_AGENT, context_agent: str | None = None,
              context_top: int = 8, fetch=http_json, fetch_text=http_text, include_trials: bool = True) -> dict:
    start = as_of - timedelta(days=lookback_days)
    status = {"edgar": "ok", "trials": "skipped", "context": "skipped (set SEC_USER_AGENT with your own contact to enable)"}
    try:
        hits = search_edgar(phrase, start, as_of, agent, fetch=fetch)
    except Exception as exc:
        hits, status["edgar"] = [], f"error: {str(exc)[:160]}"
    companies = aggregate(hits)
    unmatched: list[dict] = []
    if include_trials:
        try:
            unmatched = attach_trials(companies, trial_sponsors(phrase, as_of, lookback_days, fetch=fetch))
            status["trials"] = "ok"
        except Exception as exc:
            status["trials"] = f"error: {str(exc)[:160]}"
    rows = sorted(companies.values(), key=lambda r: -score_company(r))
    if context_agent:
        status["context"] = "ok"
        for row in rows[:context_top]:
            press = next((f for f in row["filings"].values() if f["kind"] == "announcement"), None) or next(iter(row["filings"].values()))
            try:
                snippet = sentence_context(fetch_text(press["url"], context_agent), phrase)
                row["context"] = {"label": classify_context(snippet) if snippet else "unclear", "snippet": snippet, "url": press["url"]}
            except Exception as exc:
                row["context"] = {"label": "unclear", "snippet": "", "url": press["url"], "error": str(exc)[:120]}
            time.sleep(0.2)
    output = []
    for row in rows:
        filings = list(row["filings"].values())
        output.append({
            "ticker": row["ticker"], "company": row["name"], "cik": row["cik"], "sicGroup": row["sicGroup"],
            "relation": relation(row), "score": score_company(row), "firstFiled": row["firstFiled"],
            "announcements": row["announcements"], "earningsMentions": row["earningsMentions"], "filingCount": len(filings),
            "trials": row.get("trials", [])[:3], "context": row.get("context"),
            "evidence": [{"form": f["form"], "kind": f["kind"], "filed": f["filed"], "url": f["url"]}
                         for f in sorted(filings, key=lambda f: (f["kind"] != "announcement", f["filed"] or ""))[:3]],
        })
    output.sort(key=lambda r: (r["relation"] != "capability candidate", -r["score"], r["firstFiled"] or ""))
    return {
        "topic": phrase, "asOf": as_of.isoformat(), "window": {"start": start.isoformat(), "end": as_of.isoformat()},
        "status": status, "filingHits": len(hits),
        "candidates": [r for r in output if r["relation"] == "capability candidate"],
        "mentionOnly": [r for r in output if r["relation"] == "health company, mention only"],
        "exposed": [r for r in output if r["relation"] in {"exposed (likely impacted)", "mention"}],
        "unmatchedTrialSponsors": unmatched[:10],
    }


def write_markdown(results: list[dict], path: str, known: set[str]) -> None:
    lines = [
        "# 动态受益者映射", "",
        "> 从话题出发，在 SEC 文件和临床试验注册中查找真正参与其中的上市公司。只使用截至当日已公开的一手资料，不使用语言模型。"
        "候选公司需要再经过 Serenity 筛选，这里不是买入清单。", "",
    ]
    for result in results:
        lines += [f"## {result['topic']}", "",
                  f"截至 {result['asOf']}，检索窗口 {result['window']['start']} 至 {result['window']['end']}；命中 {result['filingHits']} 份文件。"
                  f" 数据状态：EDGAR {result['status']['edgar']}，临床试验 {result['status']['trials']}，原文判断 {result['status']['context']}。", ""]
        if result["candidates"]:
            lines += ["**有能力受益的候选公司**（医疗行业公司以事件公告形式提及，或注册了相关临床试验）", "",
                      "| 股票 | 公司 | 行业 | 得分 | 首次提及 | 事件公告 | 临床试验 | 原文判断 | 证据 | 已在研究池 |",
                      "| --- | --- | --- | ---: | --- | ---: | ---: | --- | --- | --- |"]
            for r in result["candidates"][:15]:
                ev = r["evidence"][0] if r["evidence"] else None
                ctx = (r.get("context") or {}).get("label", "—")
                link = f"[{ev['form']}]({ev['url']})" if ev else ""
                lines.append(
                    f"| {r['ticker'] or '无代码（可能已退市）'} | {r['company']} | {r['sicGroup']} | {r['score']} | {r['firstFiled']} | {r['announcements']} | "
                    f"{len(r['trials'])} | {ctx} | {link} | {'是' if r['ticker'] in known else '否'} |"
                )
            lines.append("")
        if result["mentionOnly"]:
            names = ", ".join(f"{r['ticker'] or r['company']}" for r in result["mentionOnly"][:12])
            lines += [f"**医疗公司但仅在财报或定期报告中提及（多为业务影响，需看原文）：** {names}", ""]
        if result["exposed"]:
            names = ", ".join(f"{r['ticker'] or r['company']}（{r['sicGroup']}）" for r in result["exposed"][:12])
            lines += [f"**可能受冲击或只是提及：** {names}", ""]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Map a topic to listed companies using time-stamped primary sources")
    parser.add_argument("--topic", action="append", default=[], help="Topic phrase (repeatable)")
    parser.add_argument("--signals", help="emerging-signals.json; maps its top new topics")
    parser.add_argument("--top-signals", type=int, default=3)
    parser.add_argument("--include-tracked", action="store_true", help="Also map signals an existing theme already tracks")
    parser.add_argument("--include-unconfirmed", action="store_true", help="Also map one-day signals (default: confirmed topics only)")
    parser.add_argument("--as-of", help="YYYY-MM-DD for historical replay; default today")
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--universe", default=str(ROOT / "trend-agent/ai-medicine-universe.json"))
    parser.add_argument("--json-output", default=str(ROOT / "state/beneficiary-map.json"))
    parser.add_argument("--markdown-output", default=str(ROOT / "outputs/beneficiary-map.md"))
    args = parser.parse_args()

    as_of = date.fromisoformat(args.as_of) if args.as_of else datetime.now(timezone.utc).date()
    topics = list(args.topic)
    if args.signals and Path(args.signals).exists():
        signals = json.loads(Path(args.signals).read_text(encoding="utf-8")).get("signals", [])
        picked = [s for s in signals
                  if (args.include_tracked or s.get("status") != "tracked-theme")
                  and (args.include_unconfirmed or s.get("confirmed"))]
        topics += [s["label"] for s in picked[: args.top_signals]]
    topics = list(dict.fromkeys(t.strip() for t in topics if t.strip()))
    context_agent = os.getenv("SEC_USER_AGENT")
    results = [map_topic(topic, as_of, args.lookback_days, context_agent=context_agent) for topic in topics]
    known: set[str] = set()
    if Path(args.universe).exists():
        known = {row["ticker"] for row in json.loads(Path(args.universe).read_text(encoding="utf-8")).get("companies", [])}
    for result in results:
        for row in result["candidates"]:
            row["inResearchUniverse"] = row["ticker"] in known
            row["nextStep"] = "already tracked" if row["ticker"] in known else "send to Serenity screen"
    payload = {"generatedAt": datetime.now(timezone.utc).isoformat(), "asOf": as_of.isoformat(), "topics": results,
               "method": "SEC EDGAR full-text search + ClinicalTrials.gov industry sponsors, both limited to filings/registrations dated on or before asOf; SIC-based capability grouping; optional filing-text context. No language model."}
    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_output).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(results, args.markdown_output, known)
    print(json.dumps({t["topic"]: [c["ticker"] for c in t["candidates"][:8]] for t in results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
