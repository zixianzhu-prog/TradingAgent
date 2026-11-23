"""Point-in-time backtest of the order rule: does "price implies more growth than the base case" predict returns?

The order tickets buy only when today's price is inside the range set by the 5-year base case: the price
must imply no more revenue growth than the base case assumes (start at the company's own growth, fade in a
straight line to the industry's fundamental growth). This replays that rule on history:

* for every 10-K in the cached SEC companyfacts (state/serenity-source-cache/xbrl), on the day after it
  was filed, using only that filing: revenue, prior-year revenue, cover-page share count;
* price = split-adjusted close on that day (yfinance), shares adjusted for later splits;
* implied CAGR = growth needed for a 12% yearly return over 5 years at the industry P/S multiple;
* gap = implied CAGR - base-case CAGR; in-range = gap <= 0 (what a ticket would allow);
* forward 1-year and 3-year returns (dividends included) against XBI over the same window.

Known bias: the universe is companies cached today, so firms that were delisted are missing
(survivorship). Multiples and fundamental growth are today's Damodaran tables, not those of each year.

    ai-fund-lab/.venv/bin/python scripts/backtest_order_rule.py
"""
from __future__ import annotations

import json
import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
XBRL = ROOT / "state/serenity-source-cache/xbrl"
DAMODARAN = ROOT / "trend-agent/damodaran-industry-multiples.json"
OUT = ROOT / "state/order-rule-backtest.json"
REPORT = ROOT / "outputs/order-rule-backtest.md"
REVENUE = ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet",
           "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueGoodsNet")
IFRS_REVENUE = ("Revenue", "RevenueFromContractsWithCustomers")
INDUSTRY = "Healthcare Products"
POLICY, HORIZON, BENCH = 0.12, 5, "XBI"
MIN_REVENUE_M = 20.0


def base_cagr(start: float, fundamental: float) -> float:
    """Same base case as calibrate_growth.growth_paths: straight-line fade to fundamental growth over 5 years."""
    start = max(-0.5, min(start, 1.5))
    total = 1.0
    for y in range(1, HORIZON + 1):
        total *= 1 + start + (fundamental - start) * y / HORIZON
    return total ** (1 / HORIZON) - 1


def implied_cagr(market_cap: float, revenue: float, ps: float) -> float | None:
    """Revenue growth for which revenue x P/S in 5 years equals today's value compounded at the policy return."""
    if market_cap <= 0 or revenue <= 0:
        return None
    return (market_cap * (1 + POLICY) ** HORIZON / (revenue * ps)) ** (1 / HORIZON) - 1


def annual_filings(facts: dict) -> list[dict]:
    """One row per 10-K: fiscal-year revenue, prior-year revenue, filing date and cover shares, all from that filing."""
    dei = facts.get("facts", {}).get("dei", {}).get("EntityCommonStockSharesOutstanding", {}).get("units", {}).get("shares", [])
    rows = {}
    # US filers report 10-K in us-gaap; foreign private issuers (e.g. SOPHiA) report 20-F in ifrs-full.
    pairs = [("us-gaap", t) for t in REVENUE] + [("ifrs-full", t) for t in IFRS_REVENUE]
    for taxonomy, tag in pairs:
        for x in facts.get("facts", {}).get(taxonomy, {}).get(tag, {}).get("units", {}).get("USD", []):
            if x.get("form") not in ("10-K", "20-F") or not (x.get("start") and x.get("end")):
                continue
            if not 350 <= (date.fromisoformat(x["end"]) - date.fromisoformat(x["start"])).days <= 380:
                continue
            rows.setdefault(x["accn"], {"filed": x["filed"], "values": {}})["values"][x["end"]] = x["val"]
    out = []
    for accn, r in rows.items():
        ends = sorted(r["values"])
        if len(ends) < 2:
            continue
        cur, prev = r["values"][ends[-1]], r["values"][ends[-2]]
        shares = sum(s["val"] for s in dei if s.get("accn") == accn)
        if not shares or prev <= 0:
            continue
        # The same filing's third year gives last year's growth: the deceleration test stays point-in-time.
        older = r["values"][ends[-3]] if len(ends) >= 3 else None
        prev_growth = prev / older - 1 if older and older > 0 else None
        out.append({"accn": accn, "filed": r["filed"], "fiscalEnd": ends[-1], "revenue": cur, "priorRevenue": prev,
                    "shares": shares, "previousGrowth": prev_growth})
    return sorted(out, key=lambda r: r["filed"])


def fiscal_revenue(facts: dict) -> dict[str, float]:
    """Fiscal-year revenue by period end from all annual reports (latest filing wins). A single 10-K already
    carries three years, so recent IPOs get a trend too; no share count is needed."""
    best = {}
    pairs = [("us-gaap", t) for t in REVENUE] + [("ifrs-full", t) for t in IFRS_REVENUE]
    for taxonomy, tag in pairs:
        for x in facts.get("facts", {}).get(taxonomy, {}).get(tag, {}).get("units", {}).get("USD", []):
            if x.get("form") not in ("10-K", "20-F") or not (x.get("start") and x.get("end")):
                continue
            if not 350 <= (date.fromisoformat(x["end"]) - date.fromisoformat(x["start"])).days <= 380:
                continue
            if x["end"] not in best or x["filed"] > best[x["end"]]["filed"]:
                best[x["end"]] = x
    return {e: best[e]["val"] for e in sorted(best)}


def growth_trend(facts: dict) -> dict | None:
    """Latest and previous fiscal-year revenue growth (the backtest's deceleration test)."""
    rev = fiscal_revenue(facts)
    ends = sorted(rev)[-3:]
    if len(ends) < 3 or min(rev[e] for e in ends[:2]) <= 0:
        return None
    g_last, g_prev = rev[ends[2]] / rev[ends[1]] - 1, rev[ends[1]] / rev[ends[0]] - 1
    return {"fiscalEnd": ends[2], "growth": round(g_last, 3), "previousGrowth": round(g_prev, 3), "slowing": g_last < g_prev}


def load_prices(tickers: list[str]):
    import yfinance as yf
    frame = yf.download(tickers + [BENCH], start="2012-01-01", auto_adjust=False, actions=True, progress=False,
                        group_by="ticker", threads=True)
    return frame


def series(frame, ticker: str):
    try:
        sub = frame[ticker].dropna(subset=["Close"])
    except KeyError:
        return None
    return sub if len(sub) > 250 else None


def on_or_after(sub, day: str):
    idx = sub.index.searchsorted(datetime.fromisoformat(day))
    return None if idx >= len(sub) else idx


def forward(sub, i: int, days: int) -> float | None:
    j = i + days
    if j >= len(sub):
        return None
    return float(sub["Adj Close"].iloc[j] / sub["Adj Close"].iloc[i] - 1)


def split_factor_after(sub, i: int) -> float:
    """Shares on the cover page are pre-split; Close is split-adjusted, so scale shares by later splits."""
    splits = sub["Stock Splits"].iloc[i + 1:] if "Stock Splits" in sub else []
    factor = 1.0
    for s in splits:
        if s and s > 0:
            factor *= s
    return factor


def build(tickers: list[str], facts_by: dict, frame, ps: float, fundamental: float) -> dict:
    bench = series(frame, BENCH)
    obs = []
    for t in tickers:
        sub = series(frame, t)
        if sub is None:
            continue
        for f in annual_filings(facts_by[t]):
            if f["revenue"] / 1e6 < MIN_REVENUE_M or f["filed"] < "2014-01-01":
                continue
            i = on_or_after(sub, (date.fromisoformat(f["filed"]) + timedelta(days=1)).isoformat())
            if i is None:
                continue
            price = float(sub["Close"].iloc[i])
            cap = price * f["shares"] * split_factor_after(sub, i)
            # Sanity: tagged share counts are sometimes in thousands; skip implausible P/S.
            if not 0.05 <= cap / f["revenue"] <= 200:
                continue
            start = f["revenue"] / f["priorRevenue"] - 1
            implied = implied_cagr(cap, f["revenue"], ps)
            base = base_cagr(start, fundamental)
            b = on_or_after(bench, sub.index[i].isoformat())
            row = {"ticker": t, "filed": f["filed"], "date": str(sub.index[i].date()), "revenueM": round(f["revenue"] / 1e6, 1),
                   "trailingGrowth": round(start, 4), "ps": round(cap / f["revenue"], 2), "impliedCagr": round(implied, 4),
                   "baseCagr": round(base, 4), "gap": round(implied - base, 4), "inRange": implied <= base,
                   "previousGrowth": None if f["previousGrowth"] is None else round(f["previousGrowth"], 4)}
            row["notSlowing"] = row["previousGrowth"] is not None and start >= row["previousGrowth"]
            row["filtered"] = row["inRange"] and row["notSlowing"]
            for label, days in (("1y", 252), ("3y", 756)):
                r, rb = forward(sub, i, days), (forward(bench, b, days) if b is not None else None)
                row[f"ret{label}"] = None if r is None else round(r, 4)
                row[f"excess{label}"] = None if r is None or rb is None else round(r - rb, 4)
            obs.append(row)
    return summarize(obs)


def spearman(x: list[float], y: list[float]) -> float | None:
    n = len(x)
    if n < 10:
        return None
    rank = lambda v: {i: r for r, i in enumerate(sorted(range(n), key=lambda k: v[k]))}
    rx, ry = rank(x), rank(y)
    d = sum((rx[i] - ry[i]) ** 2 for i in range(n))
    return 1 - 6 * d / (n * (n * n - 1))


def stats(rows: list[dict], key: str) -> dict:
    vals = sorted(r[key] for r in rows if r.get(key) is not None)
    if not vals:
        return {"n": 0}
    n = len(vals)
    mean = sum(vals) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in vals) / (n - 1)) if n > 1 else 0.0
    return {"n": n, "mean": round(mean, 4), "median": round(vals[n // 2], 4), "hit": round(sum(v > 0 for v in vals) / n, 3),
            "t": round(mean / (sd / math.sqrt(n)), 2) if sd else None}


def summarize(obs: list[dict]) -> dict:
    out = {"observations": len(obs), "companies": len({o["ticker"] for o in obs}),
           "period": [min((o["date"] for o in obs), default=None), max((o["date"] for o in obs), default=None)], "buckets": {}, "quintiles": {}, "ic": {}}
    for label in ("1y", "3y"):
        key = f"excess{label}"
        done = [o for o in obs if o.get(key) is not None]
        out["buckets"][label] = {"inRange": stats([o for o in done if o["inRange"]], key),
                                 "aboveRange": stats([o for o in done if not o["inRange"]], key),
                                 "inRangeNotSlowing": stats([o for o in done if o["filtered"]], key),
                                 "inRangeSlowing": stats([o for o in done if o["inRange"] and not o["filtered"]], key)}
        out.setdefault("severeLoss", {})[label] = {
            name: round(sum(o[key] < -0.6 for o in g) / len(g), 3) if g else None
            for name, g in (("inRange", [o for o in done if o["inRange"]]), ("aboveRange", [o for o in done if not o["inRange"]]),
                            ("inRangeNotSlowing", [o for o in done if o["filtered"]]),
                            ("inRangeSlowing", [o for o in done if o["inRange"] and not o["filtered"]]))}
        ranked = sorted(done, key=lambda o: o["gap"])
        q = [ranked[k * len(ranked) // 5:(k + 1) * len(ranked) // 5] for k in range(5)]
        out["quintiles"][label] = [{"gapFrom": g[0]["gap"], "gapTo": g[-1]["gap"], **stats(g, key)} for g in q if g]
        # Negative IC is what the rule expects: a larger growth gap should mean lower excess return.
        out["ic"][label] = round(spearman([o["gap"] for o in done], [o[key] for o in done]) or 0, 3) if len(done) >= 10 else None
    out["rows"] = obs
    return out


def report(p: dict) -> str:
    pct = lambda v: "—" if v is None else f"{v:+.1%}"
    lines = ["# 下单规则历史回测（2014 年以来）", "",
             f"生成时间：{p['generatedAt']}。{p['observations']} 个“年报发布日”观察，{p['companies']} 家公司，{p['period'][0]} 至 {p['period'][1]}。", "",
             "规则：在每份 10-K 发布次日，只用该年报的收入、上年收入和封面股数，算出“现价隐含的 5 年收入增速”（按 12% 年回报和行业市销率），",
             "与基准情景增速（从公司自身增速直线回落到行业基本增速）比较。隐含 ≤ 基准 = 在下单区间内。收益为含分红的总回报，超额 = 减去同期 XBI。", "",
             "| 持有期 | 组别 | 样本 | 平均超额 | 中位超额 | 跑赢 XBI 比例 | t 值 |", "|---|---|---:|---:|---:|---:|---:|"]
    for label in ("1y", "3y"):
        for name, zh in (("inRange", "在区间内（旧规则会下单）"), ("aboveRange", "高于区间（等待）"),
                         ("inRangeNotSlowing", "在区间内 + 增速未放缓（新规则）"), ("inRangeSlowing", "在区间内但增速放缓（新规则等待）")):
            s = p["buckets"][label][name]
            if s.get("n"):
                lines.append(f"| {label} | {zh} | {s['n']} | {pct(s['mean'])} | {pct(s['median'])} | {s['hit']:.0%} | {s['t']} |")
    lines += ["", "严重亏损（超额收益低于 −60%）的比例：", "", "| 持有期 | 旧规则下单 | 等待 | 新规则下单 | 新规则挡掉的 |", "|---|---:|---:|---:|---:|"]
    for label in ("1y", "3y"):
        sl = p["severeLoss"][label]
        lines.append(f"| {label} | " + " | ".join("—" if sl[k] is None else f"{sl[k]:.0%}" for k in ("inRange", "aboveRange", "inRangeNotSlowing", "inRangeSlowing")) + " |")
    lines += ["", "按“增速缺口”（隐含 − 基准）分五组，缺口越大 = 价格要求越高：", "",
              "| 持有期 | 组 | 缺口范围 | 样本 | 平均超额 | 中位超额 | 跑赢比例 |", "|---|---|---|---:|---:|---:|---:|"]
    for label in ("1y", "3y"):
        for k, q in enumerate(p["quintiles"][label], start=1):
            lines.append(f"| {label} | Q{k} | {q['gapFrom']:+.0%} ~ {q['gapTo']:+.0%} | {q['n']} | {pct(q['mean'])} | {pct(q['median'])} | {q['hit']:.0%} |")
    lines += ["", f"秩相关（缺口 vs 超额收益，规则预期为负）：1 年 {p['ic']['1y']}，3 年 {p['ic']['3y']}。", "",
              "## 局限", "", "- 幸存者偏差：样本是今天缓存的公司，已退市公司缺失，会高估所有组的绝对收益；组间比较受影响较小但仍有偏。",
              f"- 市销率和行业基本增速用的是今天的 Damodaran 表（{INDUSTRY}），不是每年当时的数值。",
              "- 同一公司不同年份的观察相互不独立，t 值偏乐观。",
              "- “增速未放缓”过滤是在看到旧规则结果后提出的（同时预先只比较了两个变体：更快回落、增速放缓过滤），属于样本内发现；需要用之后的实盘数据继续验证。", "- 不含药物开发公司（收入低于 2000 万美元的年份被排除）；那一类用 rNPV，另需单独验证。"]
    return "\n".join(lines) + "\n"


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--xbrl-dir", default=str(XBRL), help="companyfacts files to replay (default: the original sample)")
    parser.add_argument("--state", default=str(OUT))
    parser.add_argument("--report", default=str(REPORT))
    parser.add_argument("--label", default="in-sample", help="in-sample or out-of-sample, recorded in the output")
    args = parser.parse_args()
    damo = json.loads(DAMODARAN.read_text(encoding="utf-8"))
    ps = damo["industries"][INDUSTRY]["ps"]
    fundamental = damo["growth"]["fundamental"]["industries"][INDUSTRY]
    facts_by = {p.stem.removeprefix("companyfacts-"): json.loads(p.read_text(encoding="utf-8"))
                for p in sorted(Path(args.xbrl_dir).glob("companyfacts-*.json"))}
    tickers = sorted(facts_by)
    frame = load_prices(tickers)
    payload = {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "sample": args.label,
               "industry": INDUSTRY, "ps": ps, "fundamentalGrowth": fundamental, "policyReturn": POLICY,
               **build(tickers, facts_by, frame, ps, fundamental)}
    Path(args.state).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    text = report(payload)
    if args.label != "in-sample":
        text = text.replace("# 下单规则历史回测（2014 年以来）", "# 下单规则样本外回测（2014 年以来，规则从未见过的公司）", 1)
    Path(args.report).write_text(text, encoding="utf-8")
    print(json.dumps({k: payload[k] for k in ("sample", "observations", "companies", "period", "ic")}))


if __name__ == "__main__":
    main()
