"""AI-medicine companies under $1B, tagged by stage: preparation or growth.

Peter's direction is earlier and smaller: a company worth under $1 billion, still preparing
(no real revenue yet, proving the science) or starting to grow. The market-wide screen
(ai_medicine_universe_screen.py) finds companies whose own filings describe their own AI
product; this step measures each one from primary data:

    market cap  = SEC shares outstanding (dei cover page, latest filing) x latest close
                  (yfinance; the screen's cap field was only filled for liquid names)
    revenue     = SEC XBRL: latest fiscal year and latest quarter versus a year earlier
    runway      = (cash + short-term investments) / operating cash burn, in months
    clinical    = highest phase of the company's own trials on ClinicalTrials.gov (sponsor search)

Stage rule, the same for every company:

    preparation  annual revenue under $10M (sub-stage = clinical phase, or "pre-commercial")
    growth       revenue $10M+ and latest growth 20%+ a year
    slowing      revenue $10M+ and growth under 20%

A second source adds drug developers that our 8-K tracker (pharma_deals_ind.py) caught clearing an
IND or signing a big-pharma deal in the last 90 days: Peter's "animal studies passed" and "big pharma
uses their product" signals. They are not screened for AI; each row says why it is listed.

Runway under 12 months marks a financing risk: a new share sale (dilution) is likely soon.
Size band: $50M to $1B market cap and at least $250K average daily trading, so a position
can actually be bought. This queues names for Serenity research; it does not rank potential.

    python3 scripts/small_cap_stage.py            # needs SEC_USER_AGENT for new SEC files
    python3 scripts/small_cap_stage.py --offline  # cached SEC and trial data only (prices still fetched)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCREEN = ROOT / "state/ai-medicine-universe-screen.json"
SIGNALS = ROOT / "state/pharma-deals-ind.json"
DRUG_SEGMENTS = ("Drug discovery", "Drug developer")
XBRL_CACHE = ROOT / "state/serenity-source-cache/xbrl"
TRIALS_CACHE = ROOT / "state/serenity-source-cache/trials-sponsor"
OUTPUT = ROOT / "state/small-cap-stage.json"
REPORT = ROOT / "outputs/ai-medicine-small-caps.md"
CAP_MIN_M, CAP_MAX_M, MIN_ADV = 50, 1_000, 250_000
REVENUE_FLOOR_M, GROWTH_LINE, RUNWAY_RISK = 10, 0.20, 12

REVENUE = ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet",
           "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueGoodsNet",
           "Revenue", "RevenueFromContractsWithCustomers")                               # last two: IFRS
CASH = ("CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
        "CashAndCashEquivalents")
INVESTMENTS = ("ShortTermInvestments", "MarketableSecuritiesCurrent", "MarketableSecurities", "AvailableForSaleSecuritiesDebtSecuritiesCurrent",
               "CurrentFinancialAssetsAtFairValueThroughProfitOrLoss")
OPERATING_CF = ("NetCashProvidedByUsedInOperatingActivities", "CashFlowsFromUsedInOperatingActivities")
PHASES = {"EARLY_PHASE1": 0.5, "PHASE1": 1, "PHASE2": 2, "PHASE3": 3, "PHASE4": 4}
SUFFIX = re.compile(r",?\s*\b(inc|corp|corporation|ltd|limited|plc|n\.?v|s\.?a|ag|holdings?|co)\b\.?", re.I)


def _opener():
    import serenity_evidence_review as ser
    return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))


def companyfacts(ticker: str, cik: str, fetch: bool) -> dict | None:
    path = XBRL_CACHE / f"companyfacts-{ticker}.json"
    fresh = path.exists() and (time.time() - path.stat().st_mtime) < 7 * 86400
    if path.exists() and (fresh or not fetch):
        return json.loads(path.read_text(encoding="utf-8"))
    agent = os.getenv("SEC_USER_AGENT", "")
    if not fetch or "@" not in agent:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    req = urllib.request.Request(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json",
                                 headers={"User-Agent": agent, "Accept-Encoding": "identity"})
    try:
        with _opener().open(req, timeout=40) as resp:
            data = resp.read()
    except Exception as exc:
        print(f"{ticker}: companyfacts not fetched ({type(exc).__name__})")
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
    XBRL_CACHE.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    time.sleep(0.15)
    return json.loads(data)


def _facts(facts: dict, tags: tuple[str, ...], unit: str = "USD") -> list[dict]:
    """All values for the first tag that has any, across us-gaap and ifrs-full."""
    for taxonomy in ("us-gaap", "ifrs-full"):
        block = facts.get("facts", {}).get(taxonomy, {})
        for tag in tags:
            units = block.get(tag, {}).get("units", {})
            values = units.get(unit) or next((v for k, v in units.items() if k.startswith(unit[:3]) or unit == "USD"), [])
            if values:
                return values
    return []


def _days(x: dict) -> int | None:
    if not (x.get("start") and x.get("end")):
        return None
    return (date.fromisoformat(x["end"]) - date.fromisoformat(x["start"])).days


def _latest_by_end(values: list[dict], keep) -> dict[str, dict]:
    best: dict[str, dict] = {}
    for x in values:
        if keep(x) and (x["end"] not in best or x["filed"] > best[x["end"]]["filed"]):
            best[x["end"]] = x
    return best


def shares_outstanding(facts: dict) -> tuple[float | None, str | None]:
    dei = facts.get("facts", {}).get("dei", {}).get("EntityCommonStockSharesOutstanding", {}).get("units", {}).get("shares", [])
    if not dei:
        # Some filers leave the cover-page count untagged. The weighted-average basic count of the
        # latest quarter covers every share class (Tempus has two) at the cost of a short lag.
        basic = [x for x in facts.get("facts", {}).get("us-gaap", {}).get("WeightedAverageNumberOfSharesOutstandingBasic", {})
                 .get("units", {}).get("shares", []) if (d := _days(x)) and d <= 100]
        if not basic:
            return None, None
        latest = max(basic, key=lambda x: (x["end"], x["filed"]))
        return float(latest["val"]), latest["end"]
    latest = max(dei, key=lambda x: (x["end"], x["filed"]))
    # Companies with several share classes report one row per class on the same date.
    total = sum(x["val"] for x in dei if x["end"] == latest["end"] and x["accn"] == latest["accn"])
    return float(total), latest["end"]


def revenue_profile(facts: dict) -> dict:
    # Filers switch revenue tags over the years, so pool every revenue tag; the latest filing wins per period.
    values = [x for tag in REVENUE for x in _facts(facts, (tag,))]
    annual = _latest_by_end(values, lambda x: (d := _days(x)) is not None and 350 <= d <= 380)
    quarter = _latest_by_end(values, lambda x: (d := _days(x)) is not None and 80 <= d <= 100)
    out = {"revenueTagged": bool(values), "fiscalYearM": None, "fiscalYearEnd": None, "fiscalYoY": None, "quarterM": None, "quarterEnd": None, "quarterYoY": None}
    if annual:
        ends = sorted(annual)
        out["fiscalYearM"], out["fiscalYearEnd"] = round(annual[ends[-1]]["val"] / 1e6, 1), ends[-1]
        prior = next((annual[e] for e in reversed(ends[:-1]) if 350 <= (date.fromisoformat(ends[-1]) - date.fromisoformat(e)).days <= 380), None)
        if prior and prior["val"] > 0:
            out["fiscalYoY"] = round(annual[ends[-1]]["val"] / prior["val"] - 1, 3)
    if quarter:
        ends = sorted(quarter)
        q = quarter[ends[-1]]
        out["quarterM"], out["quarterEnd"] = round(q["val"] / 1e6, 1), ends[-1]
        prior = next((quarter[e] for e in ends[:-1] if 355 <= (date.fromisoformat(ends[-1]) - date.fromisoformat(e)).days <= 375), None)
        if prior and prior["val"] > 0:
            out["quarterYoY"] = round(q["val"] / prior["val"] - 1, 3)
    return out


def runway(facts: dict) -> dict:
    def latest_instant(tags):
        vals = [x for x in _facts(facts, tags) if not x.get("start")]
        return max(vals, key=lambda x: (x["end"], x["filed"])) if vals else None

    cash = latest_instant(CASH)
    if not cash:
        return {"cashM": None, "burnPerMonthM": None, "runwayMonths": None, "cashAsOf": None}
    investments = [x for x in _facts(facts, INVESTMENTS) if not x.get("start") and x["end"] == cash["end"]]
    total = cash["val"] + (max(investments, key=lambda x: x["filed"])["val"] if investments else 0)
    # Operating cash flow is reported year-to-date; take the latest period and turn it into a monthly rate.
    flows = [x for x in _facts(facts, OPERATING_CF) if _days(x)]
    burn = None
    if flows:
        f = max(flows, key=lambda x: (x["end"], _days(x), x["filed"]))
        months = max(1, round(_days(f) / 30.4))
        burn = -f["val"] / months / 1e6 if f["val"] < 0 else 0.0
    months_left = round(total / 1e6 / burn, 1) if burn else None
    return {"cashM": round(total / 1e6, 1), "cashAsOf": cash["end"], "burnPerMonthM": round(burn, 2) if burn is not None else None,
            "runwayMonths": months_left}


def sponsor_query(name: str) -> str:
    return SUFFIX.sub("", name).replace(",", " ").strip()


def clinical_stage(name: str, fetch: bool) -> dict:
    """Highest phase among the company's own industry-sponsored trials started in the last 6 years."""
    TRIALS_CACHE.mkdir(parents=True, exist_ok=True)
    query = sponsor_query(name)
    path = TRIALS_CACHE / (re.sub(r"[^A-Za-z0-9]+", "-", query).strip("-").lower() + ".json")
    if path.exists() and (not fetch or time.time() - path.stat().st_mtime < 7 * 86400):
        studies = json.loads(path.read_text(encoding="utf-8"))
    elif fetch:
        params = urllib.parse.urlencode({"query.spons": query, "pageSize": 100,
                                         "fields": "NCTId,BriefTitle,Phase,OverallStatus,StartDate,LeadSponsorName"})
        try:
            with _opener().open(urllib.request.Request(f"https://clinicaltrials.gov/api/v2/studies?{params}",
                                                       headers={"User-Agent": "serenity-research-agent"}), timeout=30) as resp:
                studies = json.loads(resp.read()).get("studies", [])
        except Exception as exc:
            print(f"{name}: trials not fetched ({type(exc).__name__})")
            studies = []
        path.write_text(json.dumps(studies), encoding="utf-8")
        time.sleep(0.2)
    else:
        return {"highestPhase": None, "trials": 0, "examples": []}
    key = sponsor_query(name).lower().split()[0]
    own = []
    for s in studies:
        p = s.get("protocolSection", {})
        sponsor = p.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", "")
        start = (p.get("statusModule", {}).get("startDateStruct") or {}).get("date", "")
        status = p.get("statusModule", {}).get("overallStatus", "")
        if key not in sponsor.lower() or status == "WITHDRAWN" or start[:4] < str(date.today().year - 6):
            continue
        phases = [PHASES[x] for x in p.get("designModule", {}).get("phases", []) if x in PHASES]
        if phases:
            own.append({"nct": p["identificationModule"]["nctId"], "title": p["identificationModule"].get("briefTitle", ""),
                        "phase": max(phases), "status": status, "start": start})
    own.sort(key=lambda s: (-s["phase"], s["start"]), reverse=False)
    return {"highestPhase": own[0]["phase"] if own else None, "trials": len(own), "examples": own[:2]}


def stage(rev: dict, clinical: dict, segment: str) -> tuple[str, str]:
    revenue = rev["fiscalYearM"] or 0
    if rev["quarterM"] is not None:
        revenue = max(revenue, rev["quarterM"] * 4)
    growth = rev["quarterYoY"] if rev["quarterYoY"] is not None else rev["fiscalYoY"]
    phase = clinical.get("highestPhase")
    labels = {0.5: "early phase 1", 1: "phase 1", 2: "phase 2", 3: "phase 3", 4: "approved, phase 4"}
    if segment in DRUG_SEGMENTS and phase is not None and phase < 4 and revenue >= REVENUE_FLOOR_M:
        # Partner payments are lumpy and say nothing about a drug's commercial stage.
        return "preparation", f"{labels[phase]}, partner revenue ${revenue:.0f}M"
    if revenue < REVENUE_FLOOR_M:
        if phase:
            return "preparation", labels[phase]
        return "preparation", "preclinical" if segment in DRUG_SEGMENTS else "pre-commercial"
    if growth is not None and growth >= GROWTH_LINE:
        return "growth", f"revenue +{growth:.0%} a year"
    return "slowing", f"revenue {growth:+.0%} a year" if growth is not None else "growth not reported"


def prices(tickers: list[str]) -> dict[str, dict]:
    import yfinance as yf

    out = {}
    frame = yf.download(tickers, period="4mo", auto_adjust=False, progress=False, group_by="ticker", threads=True)
    for t in tickers:
        try:
            sub = (frame[t] if len(tickers) > 1 else frame).dropna(subset=["Close"]).tail(60)
            if not sub.empty:
                out[t] = {"price": round(float(sub["Close"].iloc[-1]), 2), "priceDate": str(sub.index[-1].date()),
                          "advUsd": float((sub["Close"] * sub["Volume"]).mean())}
        except Exception:
            continue
    return out


def signal_text(filing: dict) -> str:
    v = lambda k: ((filing.get("facts") or {}).get(k) or {}).get("value")
    if filing["kind"] == "ind":
        return "IND cleared: " + " · ".join(x for x in (v("drug"), v("indication"), v("nextTrial")) if x)[:120]
    upfront = f", ${v('upfrontUsdM')}M upfront" if v("upfrontUsdM") else ""
    return f"Deal with {v('partner') or 'big pharma'}{upfront}"[:120]


def signal_candidates(signals: dict, known: set[str]) -> list[dict]:
    """Drug developers with a confirmed IND clearance or new big-pharma deal, shaped like screen rows."""
    flag = {"ind": "isIndClearance", "deal": "isNewDeal"}
    out: dict[str, dict] = {}
    for f in sorted(signals.get("filings", []), key=lambda f: f.get("filed") or ""):
        t = f.get("ticker")
        if not t or t in known or f.get("duplicateOf") or (f.get("facts") or {}).get(flag[f["kind"]]) is not True:
            continue
        segment = "Drug developer" if f.get("sicGroup") == "Therapeutics & vaccines" else (f.get("sicGroup") or "Other")
        row = out.setdefault(t, {"ticker": t, "company": f["company"], "segment": segment, "source": "deal-ind",
                                 "phrasePairs": 0, "fdaAiDevices": 0, "ownershipPhrases": 0, "filings": [], "signals": []})
        row["filings"].append({"form": "8-K", "filed": f["filed"], "url": f["url"]})
        row["signals"].append({"kind": f["kind"], "filed": f["filed"], "text": signal_text(f), "url": f["url"]})
    return list(out.values())


def build(screen: dict, fetch: bool, price_fn=prices, signals: dict | None = None) -> dict:
    candidates = {r["ticker"]: r for r in screen["companies"] if r.get("ticker")}
    extra = signal_candidates(signals or {}, set(candidates))
    candidates.update({r["ticker"]: r for r in extra})
    screen = {**screen, "companies": screen["companies"] + extra}
    ciks = {}
    for r in screen["companies"]:
        for f in r.get("filings", []):
            m = re.search(r"edgar/data/0*(\d+)/", f.get("url", ""))
            if m:
                ciks[r["ticker"]] = m.group(1)
                break
    market = price_fn(sorted(candidates))
    rows, skipped = [], []
    for ticker, r in sorted(candidates.items()):
        m = market.get(ticker)
        facts = companyfacts(ticker, ciks[ticker], fetch) if ticker in ciks else None
        shares, shares_date = shares_outstanding(facts) if facts else (None, None)
        if not m or not shares:
            skipped.append({"ticker": ticker, "reason": "no recent price" if not m else "no SEC share count"})
            continue
        cap = shares * m["price"] / 1e6
        if m["advUsd"] > cap * 1e6 * 0.5:
            # Some filers tag share counts in thousands (Tempus). No stock trades half its value every day.
            skipped.append({"ticker": ticker, "reason": f"SEC share count or price data inconsistent: daily trading ${m['advUsd'] / 1e6:.1f}M is more than half the computed market value ${cap:.1f}M"})
            continue
        if not (CAP_MIN_M <= cap < CAP_MAX_M) or m["advUsd"] < MIN_ADV:
            if cap < CAP_MAX_M:
                skipped.append({"ticker": ticker, "reason": f"market cap ${cap:.0f}M / daily trading ${m['advUsd'] / 1e6:.2f}M outside the band"})
            continue
        rev = revenue_profile(facts)
        cash = runway(facts)
        clinical = clinical_stage(r["company"], fetch) if r["segment"] in DRUG_SEGMENTS or (rev["fiscalYearM"] or 0) < REVENUE_FLOOR_M else \
            {"highestPhase": None, "trials": 0, "examples": []}
        phase, detail = stage(rev, clinical, r["segment"])
        run_rate = max(rev["fiscalYearM"] or 0, (rev["quarterM"] or 0) * 4) if rev["revenueTagged"] else None
        rows.append({
            "revenueRunRateM": round(run_rate, 1) if run_rate is not None else None,
            "ticker": ticker, "company": r["company"], "segment": r["segment"],
            "marketCapM": round(cap), "price": m["price"], "priceDate": m["priceDate"], "advUsdM": round(m["advUsd"] / 1e6, 2),
            "sharesM": round(shares / 1e6, 1), "sharesAsOf": shares_date,
            "stage": phase, "stageDetail": detail, **rev, **cash, "clinical": clinical,
            "financingRisk": bool(cash["runwayMonths"] is not None and cash["runwayMonths"] < RUNWAY_RISK),
            "aiEvidence": {"phrasePairs": r["phrasePairs"], "fdaAiDevices": r["fdaAiDevices"], "ownershipPhrases": r["ownershipPhrases"]},
            "deepReviewed": r.get("deepReviewed", False), "filings": r.get("filings", []),
            "source": r.get("source", "ai-screen"), "signals": r.get("signals", []),
        })
    order = {"growth": 0, "preparation": 1, "slowing": 2}
    rows.sort(key=lambda x: (order[x["stage"]], x["financingRisk"], -x["marketCapM"]))
    return {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "method": __doc__.split("\n\n")[1].strip(),
            "rules": {"capBandM": [CAP_MIN_M, CAP_MAX_M], "minAdvUsd": MIN_ADV, "revenueFloorM": REVENUE_FLOOR_M,
                      "growthLine": GROWTH_LINE, "runwayRiskMonths": RUNWAY_RISK},
            "screenAsOf": screen.get("asOf"), "screened": len(candidates), "signalCandidates": len(extra), "companies": rows, "skipped": skipped,
            "byStage": {s: sum(1 for x in rows if x["stage"] == s) for s in order}}


def _money(v):
    return "—" if v is None else (f"${v / 1000:.1f}B" if v >= 1000 else f"${v:,.0f}M" if v >= 10 else f"${v:.1f}M")


def report(payload: dict) -> str:
    labels = {"growth": "增长期", "preparation": "准备期", "slowing": "放缓期"}
    lines = ["# AI 医疗：市值 10 亿美元以内", "",
             f"生成：{payload['generatedAt'][:10]}；来源：全市场筛选（{payload['screenAsOf']}）里自己的文件描述自有 AI 产品的公司，"
             f"加上最近 90 天 8-K 里确认拿到 IND 或大药厂合作的 {payload.get('signalCandidates', 0)} 家新药公司（后者没有按 AI 筛选），共检查 {payload['screened']} 家。", "",
             "> 规则对每家公司相同：市值 = SEC 披露股数 × 最新收盘价；年收入不到 1000 万美元为**准备期**（再按自家临床试验最高阶段细分），"
             "收入 1000 万美元以上且增速 ≥20% 为**增长期**，否则为**放缓期**；仍在临床阶段的新药公司一律算准备期，合作方付款不算商业化收入。现金只够不到 12 个月标为融资风险（近期很可能增发稀释）。"
             "这是研究队列，不是排名，也不是买入建议。", "",
             f"共 {len(payload['companies'])} 家：" + "，".join(f"{labels[k]} {v}" for k, v in payload["byStage"].items()) + "。", "",
             "| 阶段 | 股票 | 公司 | 方向 | 市值 | 年收入（或季度×4） | 最新增速 | 现金跑道 | 临床最高阶段 | 入选原因 |",
             "|---|---|---|---|---:|---:|---:|---:|---|---|"]
    for r in payload["companies"]:
        growth = r["quarterYoY"] if r["quarterYoY"] is not None else r["fiscalYoY"]
        run = "盈利/无消耗" if r["burnPerMonthM"] == 0 else (f"{r['runwayMonths']:.0f} 个月" if r["runwayMonths"] is not None else "—")
        if r["financingRisk"]:
            run = f"**{run} ⚠**"
        phase = r["clinical"]["highestPhase"]
        lines.append(f"| {labels[r['stage']]}：{r['stageDetail']} | {r['ticker']} | {r['company']} | {r['segment']} | {_money(r['marketCapM'])} | "
                     f"{_money(r['revenueRunRateM']) if r['revenueTagged'] else '未标注'} | {'—' if growth is None else f'{growth:+.0%}'} | {run} | "
                     f"{'—' if phase is None else ('Phase ' + str(phase))} | {'；'.join(x['text'] for x in r.get('signals', [])).replace('|', '/') or 'AI 产品（全市场筛选）'} |")
    lines += ["", "## 未进入（10 亿美元以下但数据不足或流动性不够）", ""]
    lines += [f"- {s['ticker']}：{s['reason']}" for s in payload["skipped"]] or ["无"]
    lines += ["", "## 局限", "",
              "- AI 候选只来自全市场筛选：文件里没写自有 AI 产品的小公司不会出现。IND/合作来源的公司只因该信号入选，不代表它用 AI。",
              "- 临床阶段按申办方名称搜索 ClinicalTrials.gov，合作方主导的试验不算在内；名称相近的公司可能误配，表里每家都带试验编号可核对（JSON）。",
              "- 收入“未标注”指公司的 XBRL 里没有收入标签：多数是确实没有收入的研发公司，但部分外国公司（IFRS）只是没标，阶段需对照年报确认。",
              "- 现金跑道用最近一期经营现金流折算，不含已宣布但未到账的融资。"]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    signals = json.loads(SIGNALS.read_text(encoding="utf-8")) if SIGNALS.exists() else None
    payload = build(json.loads(SCREEN.read_text(encoding="utf-8")), fetch=not args.offline, signals=signals)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(report(payload), encoding="utf-8")
    print(f"{len(payload['companies'])} companies under $1B: {payload['byStage']}; skipped {len(payload['skipped'])}")


if __name__ == "__main__":
    main()
