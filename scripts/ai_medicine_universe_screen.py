"""Rule-based screen of the whole US-listed market for AI-medicine companies.

Replaces "we picked 17 names" with a funnel anyone can rerun:

1. Find:    SEC full-text search over the last 15 months of 10-K/10-Q/20-F/S-1
            filings for AI-medicine phrase pairs ("artificial intelligence" +
            "510(k)", "machine learning" + "drug discovery", ...). Each pair is
            tied to a segment (imaging & devices, diagnostics, drug discovery,
            clinical data & software).
2. Health:  keep operating companies in health industry codes; healthcare
            software filers (SIC 7370-7374) stay only with two or more AI-medicine
            phrase pairs. Blank-check companies and funds are dropped.
3. Evidence: count distinct phrase pairs and add FDA AI-enabled device clearances
            matched to the company (manufacturer name or a known subsidiary).
            Keep companies with at least two pairs or one FDA AI device.
4. Investable: market cap >= $300M and 60-day average dollar volume >= $2M.
5. Serenity pre-screen (from the aleabit-stock-selection skill): market-cap band
            ($400M-$5B is the skill's sweet spot; $50B+ "institutions already
            there"), and a bucket hint, "asymmetric upside" for sweet-spot names
            and "durable compounder" for large established ones. The full Serenity
            gates (supply-chain map, chokepoint, customer dependency, multi-node
            control) still need the evidence review; this screen only queues names.

Mentioning AI in a filing is not the same as making money from it. The screen
finds who to research, it does not rank potential.
"""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import beneficiary_mapper as mapper

ROOT = Path(__file__).resolve().parents[1]
FORMS = "10-K,10-Q,20-F,S-1,424B4"
QUERIES = [
    # Phrases are chosen to be unambiguous: plain "De Novo" also matches "de novo design" in
    # drug filings, and "AI-enabled" + "FDA" matches any drug company, so both are qualified.
    ('"artificial intelligence" "510(k)"', "Imaging & devices"),
    ('"artificial intelligence" "De Novo classification"', "Imaging & devices"),
    ('"deep learning" "medical imaging"', "Imaging & devices"),
    ('"AI-enabled" "medical device"', "Imaging & devices"),
    ('"artificial intelligence" "radiology"', "Imaging & devices"),
    ('"machine learning" "diagnostic test"', "Diagnostics"),
    ('"artificial intelligence" "pathology"', "Diagnostics"),
    ('"machine learning" "sequencing data"', "Diagnostics"),
    ('"artificial intelligence" "drug discovery"', "Drug discovery"),
    ('"machine learning" "drug discovery"', "Drug discovery"),
    ('"artificial intelligence" "clinical decision support"', "Clinical data & software"),
    ('"artificial intelligence" "real-world data"', "Clinical data & software"),
    ('"artificial intelligence" "electronic health record"', "Clinical data & software"),
]
# First-person language: "our machine learning platform" means AI is the company's own
# product, while "competitors use artificial intelligence" in a risk factor does not.
OWNERSHIP_QUERIES = ['"our artificial intelligence"', '"our machine learning"', '"our deep learning"', '"our AI platform"', '"our AI-powered"']
SOFTWARE_SIC = set(range(7370, 7375))
# Subsidiaries whose FDA manufacturer names do not match the listed parent's name.
FDA_ALIASES = {
    "GEHC": ["GE Medical Systems", "GE Healthcare", "GE Precision Healthcare", "Ge Medical Systems"],
    "RDNT": ["DeepHealth", "Aidence"],
    "PHG": ["Philips"],
    "MDT": ["Medtronic", "Covidien"],
    "BSX": ["Boston Scientific"],
    "ABT": ["Abbott"],
    "SYK": ["Stryker"],
    "BDX": ["Becton Dickinson", "BD "],
    "HOLX": ["Hologic"],
    "ISRG": ["Intuitive Surgical"],
}
CAP_BANDS = [(400, "Micro (<$400M)"), (5_000, "Sweet spot ($400M–$5B)"), (50_000, "Large ($5B–$50B)"), (float("inf"), "Mega ($50B+)")]
NAME_DROP = {"inc", "corp", "corporation", "co", "ltd", "llc", "plc", "sa", "ag", "nv", "bv", "gmbh", "the", "company", "holdings",
             "group", "limited", "technologies", "technology", "medical", "systems", "health", "healthcare", "international", "usa"}


def search_all(query: str, start: date, end: date, max_hits: int = 1500, fetch=mapper.http_json) -> list[dict]:
    hits, offset = [], 0
    while offset < max_hits:
        params = urllib.parse.urlencode({"q": query, "dateRange": "custom", "startdt": start.isoformat(),
                                         "enddt": end.isoformat(), "forms": FORMS, "from": offset})
        payload = fetch(f"{mapper.EFTS}?{params}", mapper.DEFAULT_AGENT)
        page = payload.get("hits", {}).get("hits", [])
        hits.extend(page)
        offset += len(page)
        if not page or offset >= payload.get("hits", {}).get("total", {}).get("value", 0):
            break
        time.sleep(0.15)
    return hits


def is_operating(row: dict) -> bool:
    for code in row.get("sics") or []:
        try:
            if 6700 <= int(code) <= 6799:  # blank checks, trusts and funds
                return False
        except (TypeError, ValueError):
            pass
    return bool(row.get("ticker"))


def software(row: dict) -> bool:
    return any(str(code).isdigit() and int(code) in SOFTWARE_SIC for code in row.get("sics") or [])


def core_tokens(name: str) -> list[str]:
    words = re.sub(r"[^a-z0-9 ]", " ", name.lower()).split()
    return [w for w in words if w not in NAME_DROP]


def same_entity(company_tokens: list[str], maker_tokens: list[str]) -> bool:
    """Whether an FDA manufacturer name refers to the listed company.

    Matching the first word alone paired Wave Life Sciences with Wave Neuroscience and
    Rhythm Pharmaceuticals with Rhythm AI. Now the first two core words must agree; a
    one-word company name ("Bruker", "iRhythm") still matches its subsidiaries
    ("Bruker Daltonics", "iRhythm Technologies").
    """
    if not company_tokens or not maker_tokens or company_tokens[0] != maker_tokens[0] or len(company_tokens[0]) < 4:
        return False
    return len(company_tokens) == 1 or maker_tokens[:2] == company_tokens[:2]


def fda_counts(devices: list[dict], companies: dict[str, dict]) -> dict[str, list[dict]]:
    """Match FDA manufacturer names to screened companies, plus known subsidiaries."""
    names = [(core_tokens(row["name"]), ticker) for ticker, row in companies.items()]
    matched: dict[str, list[dict]] = defaultdict(list)
    for device in devices:
        maker = device.get("manufacturer", "")
        ticker = next((t for t, aliases in FDA_ALIASES.items() if t in companies and any(maker.lower().startswith(n.lower()) for n in aliases)), None)
        if ticker is None:
            maker_tokens = core_tokens(maker)
            ticker = next((t for tokens, t in names if same_entity(tokens, maker_tokens)), None)
        if ticker:
            matched[ticker].append({"device": device.get("device"), "manufacturer": maker, "decisionDate": device.get("decisionDate"), "url": device.get("fdaUrl")})
    return matched


def market_data(tickers: list[str]) -> dict[str, dict]:
    """Market cap and 60-day average dollar volume (yfinance)."""
    import yfinance as yf

    out: dict[str, dict] = {}
    if not tickers:
        return out
    frame = yf.download(tickers, period="4mo", auto_adjust=True, progress=False, group_by="ticker", threads=True)
    for ticker in tickers:
        try:
            sub = frame[ticker] if len(tickers) > 1 else frame
            sub = sub.dropna(subset=["Close"]).tail(60)
            if sub.empty:
                continue
            adv = float((sub["Close"] * sub["Volume"]).mean())
            out[ticker] = {"price": float(sub["Close"].iloc[-1]), "advUsd": adv}
        except Exception:
            continue
    for ticker in [t for t, v in out.items() if v["advUsd"] >= 2_000_000]:
        try:
            cap = yf.Ticker(ticker).fast_info["market_cap"]  # .get() silently returns None on FastInfo
            out[ticker]["marketCapM"] = float(cap) / 1e6 if cap else None
        except Exception:
            out[ticker]["marketCapM"] = None
    return out


def cap_band(cap_m: float | None) -> str:
    if cap_m is None:
        return "Unknown"
    return next(label for limit, label in CAP_BANDS if cap_m < limit)


def bucket_hint(cap_m: float | None, segments: set[str]) -> str:
    if cap_m is None:
        return "—"
    if 400 <= cap_m < 5_000:
        return "Asymmetric upside candidate"
    if cap_m >= 5_000 and len(segments) >= 2:
        return "Durable compounder candidate"
    return "—"


def screen(as_of: date, devices: list[dict], known: set[str], fetch=mapper.http_json, prices=market_data,
           min_cap_m: float = 300, min_adv: float = 2_000_000, shortlist_size: int = 30) -> dict:
    start = as_of - timedelta(days=455)
    companies: dict[str, dict] = {}
    query_status = []
    for query, segment in QUERIES:
        try:
            hits = search_all(query, start, as_of, fetch=fetch)
            query_status.append({"query": query, "hits": len(hits), "status": "ok"})
        except Exception as exc:
            query_status.append({"query": query, "hits": 0, "status": f"error: {str(exc)[:120]}"})
            continue
        for key, row in mapper.aggregate(hits).items():
            entry = companies.setdefault(key, {"name": row["name"], "ticker": row["ticker"], "cik": row["cik"], "sics": row["sics"],
                                               "sicGroup": row["sicGroup"], "queries": set(), "segments": set(), "segmentHits": defaultdict(int), "filings": {}})
            entry["queries"].add(query)
            entry["segments"].add(segment)
            entry["segmentHits"][segment] += 1
            entry["filings"].update(row["filings"])
    owned: dict[str, int] = defaultdict(int)
    for query in OWNERSHIP_QUERIES:
        try:
            hits = search_all(query, start, as_of, fetch=fetch)
            query_status.append({"query": query, "hits": len(hits), "status": "ok"})
        except Exception as exc:
            query_status.append({"query": query, "hits": 0, "status": f"error: {str(exc)[:120]}"})
            continue
        for key in mapper.aggregate(hits):
            owned[key] += 1
    for key, row in companies.items():
        row["ownership"] = owned.get(key, 0)
    found = len(companies)
    health = {}
    for key, row in companies.items():
        if not is_operating(row):
            continue
        if row["sicGroup"] != "Other sector" or (software(row) and len(row["queries"]) >= 2):
            health[row["ticker"]] = row
    fda = fda_counts(devices, health)
    evidence = {t: r for t, r in health.items() if len(r["queries"]) >= 2 or fda.get(t)}
    own_product = {t: r for t, r in evidence.items() if r["ownership"] or fda.get(t)}
    market = prices(sorted(own_product))
    rows = []
    for ticker, row in own_product.items():
        m = market.get(ticker, {})
        cap = m.get("marketCapM")
        investable = bool(m) and m.get("advUsd", 0) >= min_adv and (cap or 0) >= min_cap_m
        devices_for = fda.get(ticker, [])
        score = 2 * min(len(row["queries"]), 6) + 4 * min(row["ownership"], 2) + min(len(devices_for), 10) * 0.6 + len(row["segments"])
        segment_size = defaultdict(int)
        for _, seg in QUERIES:
            segment_size[seg] += 1
        # Share of each segment's phrases matched, so the segment with more phrases does not win by default.
        primary = max(row["segmentHits"], key=lambda k: (row["segmentHits"][k] / segment_size[k], k == "Imaging & devices" and bool(devices_for)))
        sample = sorted(row["filings"].values(), key=lambda f: f["filed"] or "", reverse=True)[:2]
        rows.append({
            "ticker": ticker, "company": row["name"], "sicGroup": row["sicGroup"] if not software(row) else "Healthcare software",
            "segment": primary, "ownershipPhrases": row["ownership"],
            "segments": sorted(row["segments"]), "phrasePairs": len(row["queries"]), "fdaAiDevices": len(devices_for),
            "fdaExamples": devices_for[:2], "evidenceScore": round(score, 1),
            "marketCapM": round(cap) if cap else None, "advUsdM": round(m.get("advUsd", 0) / 1e6, 1) if m else None,
            "investable": investable, "capBand": cap_band(cap), "bucketHint": bucket_hint(cap, row["segments"]),
            "deepReviewed": ticker in known, "filings": [{"form": f["form"], "filed": f["filed"], "url": f["url"]} for f in sample],
        })
    rows.sort(key=lambda r: (-r["evidenceScore"], r["ticker"]))
    investable = [r for r in rows if r["investable"]]
    shortlist = investable[:shortlist_size]
    for r in shortlist:
        r["shortlisted"] = True
    missing_known = sorted(known - {r["ticker"] for r in rows})
    return {
        "asOf": as_of.isoformat(), "window": {"start": start.isoformat(), "end": as_of.isoformat()},
        "queries": query_status,
        "funnel": {"filersFound": found, "healthOperating": len(health), "aiEvidence": len(evidence),
                   "ownProduct": len(own_product), "investable": len(investable), "shortlist": len(shortlist),
                   "shortlistNotYetReviewed": sum(1 for r in shortlist if not r["deepReviewed"])},
        "thresholds": {"minMarketCapM": min_cap_m, "minAdvUsd": min_adv, "minPhrasePairsOrFda": "2 pairs or 1 FDA AI device"},
        "companies": rows,
        "knownNotFound": missing_known,
    }


def write_markdown(payload: dict, path: Path) -> None:
    f = payload["funnel"]
    lines = ["# AI 医疗全市场筛选", "",
             f"截至 {payload['asOf']}，检索 {payload['window']['start']} 至 {payload['window']['end']} 的 SEC 年报、季报和招股书。", "",
             "> 规则化筛选：提到 AI 医疗短语组合的公司 → 医疗行业的运营公司 → AI 证据充分（≥2 组短语或有 FDA AI 设备）→ AI 是公司自己的产品（文件中用“our machine learning”等第一人称描述，或有 FDA AI 设备）→ 可投资（市值 ≥3 亿美元、日均成交额 ≥200 万美元）→ 进入 Serenity 深审队列。"
             "在文件里提到 AI 不等于靠 AI 赚钱；这里决定研究谁，不决定潜力排名。", "",
             "| 阶段 | 公司数 |", "| --- | ---: |",
             f"| SEC 文件中提到 AI 医疗短语组合 | {f['filersFound']} |", f"| 医疗行业运营公司 | {f['healthOperating']} |",
             f"| AI 证据充分 | {f['aiEvidence']} |",
             f"| AI 是公司自己的产品（第一人称描述或有 FDA AI 设备） | {f['ownProduct']} |", f"| 可投资 | {f['investable']} |",
             f"| 进入深审队列 | {f['shortlist']}（其中 {f['shortlistNotYetReviewed']} 家尚未做 Serenity 深审） |", "",
             "## 深审队列", "",
             "| 股票 | 公司 | 主要细分 | 短语组合 | FDA AI 设备 | 市值 | Serenity 市值区间 | 类型提示 | 已深审 |",
             "| --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |"]
    for r in [r for r in payload["companies"] if r.get("shortlisted")]:
        cap = f"${r['marketCapM'] / 1000:.1f}B" if r["marketCapM"] and r["marketCapM"] >= 1000 else (f"${r['marketCapM']}M" if r["marketCapM"] else "—")
        lines.append(f"| {r['ticker']} | {r['company']} | {r['segment']} | {r['phrasePairs']} | {r['fdaAiDevices']} | {cap} | {r['capBand']} | {r['bucketHint']} | {'是' if r['deepReviewed'] else '否'} |")
    if payload["knownNotFound"]:
        lines += ["", f"现有深审公司中未被本筛选找到的：{', '.join(payload['knownNotFound'])}（可能是文件用词不同、外国发行人或非医疗行业代码，需要检查）。"]
    lines += ["", "## 检索词与命中数", "", "| 短语组合 | 命中文件 | 状态 |", "| --- | ---: | --- |"]
    lines += [f"| {q['query']} | {q['hits']} | {q['status']} |" for q in payload["queries"]]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Rule-based screen of US-listed AI-medicine companies")
    parser.add_argument("--as-of", help="YYYY-MM-DD; default today")
    parser.add_argument("--fda", default=str(ROOT / "state/fda-ai-devices.json"))
    parser.add_argument("--universe", default=str(ROOT / "trend-agent/ai-medicine-universe.json"))
    parser.add_argument("--theses", default=str(ROOT / "trend-agent/ai-medicine-theses.json"))
    parser.add_argument("--json-output", default=str(ROOT / "state/ai-medicine-universe-screen.json"))
    parser.add_argument("--markdown-output", default=str(ROOT / "outputs/ai-medicine-universe-screen.md"))
    args = parser.parse_args()
    as_of = date.fromisoformat(args.as_of) if args.as_of else datetime.now(timezone.utc).date()
    devices = json.loads(Path(args.fda).read_text(encoding="utf-8")).get("devices", []) if Path(args.fda).exists() else []
    known: set[str] = set()
    if Path(args.theses).exists():
        theses = json.loads(Path(args.theses).read_text(encoding="utf-8"))
        known = {r["ticker"] for r in theses.get("candidates", []) + theses.get("expanded_deep_dives", [])}
    payload = screen(as_of, devices, known)
    payload["generatedAt"] = datetime.now(timezone.utc).isoformat()
    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_output).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload, Path(args.markdown_output))
    print(json.dumps(payload["funnel"]))


if __name__ == "__main__":
    main()
