"""Order tickets: turn the research into a concrete, reviewable suggestion per company.

Each ticket answers: what to do (buy / starter / wait / avoid), at what limit price, how big,
when to add, and what would prove the thesis wrong. Every rule is fixed and the same for each
company; nothing here places an order (paper trading only, a person approves every ticket).

Sources, all already produced by the pipeline:
  state/ai-medicine-top5.json         ranking, Serenity decision and tier, order range, open events, falsifiers
  state/ai-medicine-financial-scenarios.json   bull case (for the trim cue)
  state/small-cap-stage.json          cash runway (financing risk)
  state/event-revalidation.json       open re-check tasks, FDA rejection letters
  state/early-signals.json            key departures, insider buys
  state/pharma-deals-ind.json         IND clearances and big-pharma deals (scale-up cues)
  prices (yfinance)                   worst single day in 6 months, 60-day average dollar volume

Sizing follows the Serenity position-sizing and risk skill files (~/.codex/skills/aleabit-*):
  starter 1% (0.5-1% for small caps) / standard 5% / cap 10% per name, scale only on validation
  (earnings, customer or deal disclosure), never on price; halve if a -20% day happened in the
  last 6 months (the skill's drawdown budget); never more than 2% of a day's trading; cash runway
  under 12 months caps the position at a starter; no tight stops: the exit is a broken thesis.

    ai-fund-lab/.venv/bin/python scripts/order_tickets.py --portfolio 100000
"""
from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RANKING = ROOT / "state/ai-medicine-top5.json"
FINANCIALS = ROOT / "state/ai-medicine-financial-scenarios.json"
SMALL_CAPS = ROOT / "state/small-cap-stage.json"
EVENTS = ROOT / "state/event-revalidation.json"
EARLY = ROOT / "state/early-signals.json"
DEALS = ROOT / "state/pharma-deals-ind.json"
WATCHLIST = ROOT / "trend-agent/event-watchlist.json"
OUTPUT = ROOT / "state/order-tickets.json"
REPORT = ROOT / "outputs/order-tickets.md"

STARTER, SMALL_STARTER, STANDARD, CAP = 0.01, 0.005, 0.05, 0.10
DRAWDOWN_DAY, ADV_SHARE, RUNWAY_MONTHS, POLICY_RETURN = -0.20, 0.02, 12, 0.12


def read(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def tier_of(row: dict) -> str:
    """Serenity's own tier word from the memo verdict; 'starter' unless it says standard."""
    text = str((row.get("serenityVerdict") or {}).get("tier") or "").lower()
    return "standard" if text.startswith("standard") else "starter"


def bull_price(financial: dict) -> float | None:
    """Today's price at which even the bull case only earns the 12% policy return."""
    model = financial.get("scenario_model") or {}
    bull = (model.get("cases") or {}).get("bull") or {}
    shares, equity = financial.get("shares"), bull.get("terminal_equity_value_m")
    if not shares or not equity:
        return None
    years = model.get("horizon_years") or 5
    return round(equity * 1e6 / (bull.get("diluted_share_factor") or 1) / (1 + POLICY_RETURN) ** years / shares, 2)


def price_risk(tickers: list[str]) -> dict[str, dict]:
    import yfinance as yf

    out = {}
    frame = yf.download(tickers, period="7mo", auto_adjust=False, progress=False, group_by="ticker", threads=True)
    for t in tickers:
        try:
            sub = (frame[t] if len(tickers) > 1 else frame).dropna(subset=["Close"])
            daily = sub["Close"].pct_change().dropna().tail(126)
            out[t] = {"worstDay": round(float(daily.min()), 3), "advUsd": float((sub["Close"] * sub["Volume"]).tail(60).mean()),
                      "price": round(float(sub["Close"].iloc[-1]), 2)}
        except Exception:
            continue
    return out


def flip_points(o: dict, rnpv: dict | None) -> list[str]:
    """What would have to change for today's call to flip: the assumption a reader should argue with."""
    if not o or not o.get("price") or not o.get("upper"):
        return []
    out, price, upper = [], o["price"], o["upper"]
    if o.get("impliedGrowth") is not None and o.get("baseGrowth") is not None:
        room = o["baseGrowth"] - o["impliedGrowth"]
        if room >= 0:
            out.append(f"base-case growth can fall {room * 100:.1f} points a year (from {o['baseGrowth']:.1%} to {o['impliedGrowth']:.1%}) "
                       "before today's price leaves the range")
            # The policy price is proportional to the terminal multiple.
            out.append(f"the terminal sales multiple can shrink {1 - price / upper:.0%} before the price leaves the range")
        else:
            out.append(f"base-case growth would have to be {-room * 100:.1f} points a year higher ({o['impliedGrowth']:.1%}) to justify today's price")
    elif o.get("method") == "rNPV" and (rnpv or {}).get("impliedPeakSalesM"):
        out.append(f"the call flips if you believe peak sales of the lead asset below ${rnpv['impliedPeakSalesM']:,.0f}M "
                   "(what today's price implies)")
    return out


def small_cap_rows(covered: set[str]) -> list[dict]:
    """Small caps (Peter's under-$1B list) enter the tickets once they have a citation-checked Serenity memo and a
    usable rNPV range; the same rules apply (watch -> starter at most, small-cap and runway caps)."""
    rnpv = {r["ticker"]: r for r in read(ROOT / "state/rnpv-valuations.json", {}).get("companies", [])}
    small = {r["ticker"]: r for r in read(SMALL_CAPS, {}).get("companies", [])}
    status = read(ROOT / "state/serenity-review-status.json", {}).get("companies", {})
    assess = {r["ticker"]: r for r in read(ROOT / "state/serenity-auto-assessments.json", {}).get("companies", [])}
    gates = {r["ticker"]: r for r in read(ROOT / "state/serenity-gate-results.json", {}).get("companies", [])}
    verdicts = {r["ticker"]: r for r in read(ROOT / "state/serenity-claude-verdicts.json", {}).get("companies", [])}
    events: dict[str, list] = {}
    for task in read(EVENTS, {}).get("revalidationTasks", []):
        events.setdefault(task["ticker"], []).append({"title": task["title"]})
    rows = []
    for t, r in rnpv.items():
        reviewed = (status.get(t, {}).get("claudeMemo") == "citation-checked"
                    and "-claude-" in str(assess.get(t, {}).get("review_path", "")))
        if t in covered or t not in small or not r.get("rangeUsable") or not reviewed:
            continue
        g = gates.get(t, {})
        rows.append({"ticker": t, "company": small[t]["company"], "rank": None, "serenityReviewed": True,
                     "gateDecision": g.get("decision", "unreviewed"), "evidence": g.get("substantiatedScore", 0),
                     "openEvents": events.get(t, []), "lowEvidence": False, "orderRange": dict(r["orderRange"]),
                     "rnpv": {"phase": r["phase"], "impliedPeakSalesM": r["impliedPeakSalesM"], "platform": False},
                     "serenityVerdict": verdicts.get(t), "falsifiers": [], "source": "small-cap"})
    return rows


def growth_trends(tickers: list[str]) -> dict:
    """Fiscal-year revenue growth trend from cached SEC companyfacts (scripts/backtest_order_rule.py)."""
    import backtest_order_rule as bt
    out = {}
    for t in tickers:
        path = ROOT / f"state/serenity-source-cache/xbrl/companyfacts-{t}.json"
        if path.exists():
            out[t] = bt.growth_trend(json.loads(path.read_text(encoding="utf-8")))
    return out


def next_earnings(ticker: str, watch: dict, today: date) -> str | None:
    for company in watch.get("companies", []):
        if company["ticker"] == ticker:
            for e in company.get("events", []):
                if e.get("type") == "earnings" and e.get("date") and e["date"] >= today.isoformat():
                    return e["date"]
    return None


def patent_liens(uspto: dict) -> dict[str, list[tuple[str, str]]]:
    """Lender and latest recorded date per company, from USPTO security-interest assignments."""
    out: dict[str, list[tuple[str, str]]] = {}
    for c in uspto.get("companies", []):
        latest: dict[str, str] = {}
        for r in c.get("securityInterests", []):
            latest[r["assignee"]] = max(latest.get(r["assignee"], ""), (r.get("recordedAt") or "")[:10])
        if latest:
            out[c["ticker"]] = sorted(latest.items(), key=lambda x: x[1], reverse=True)
    return out


def ticket(row: dict, ctx: dict, portfolio: float, today: date) -> dict:
    t = row["ticker"]
    o = row.get("orderRange") or {}
    risk = ctx["risk"].get(t, {})
    small = ctx["small"].get(t)
    reasons, adjustments = [], []
    decision = row.get("gateDecision")
    open_events = row.get("openEvents") or []
    # 1. Action from research state, then from price against the order range.
    if decision == "reject":
        action, reasons = "avoid", ["Serenity verdict is reject: a gate is contradicted by a primary source"]
    elif open_events or row.get("lowEvidence") or decision == "revalidate" or not row.get("serenityReviewed"):
        action = "wait"
        if open_events:
            reasons.append("Open re-check: " + "; ".join(str(e.get("title", e))[:60] for e in open_events[:2]))
        elif decision == "revalidate":
            reasons.append("Serenity verdict is revalidate: a material event reopened gates")
        elif not row.get("serenityReviewed"):
            reasons.append("No citation-checked Serenity memo yet: gate reviews exist, the deep memo does not")
        else:
            reasons.append(f"Evidence incomplete: primary-source completeness {row.get('evidence', 0)} is below the bar")
    elif decision not in ("research-ready", "watch"):
        action = "wait"
        reasons.append(
            f"Serenity verdict is {decision or 'unknown'}: valuation cannot upgrade an unverified research thesis"
        )
    elif not o:
        rn = row.get("rnpv") or {}
        if rn.get("platform"):
            action, reasons = "wait", [f"No valuation range: discovery platform, a one-asset rNPV understates it; today's price implies ${rn['impliedPeakSalesM']:,.0f}M peak sales for the lead asset"]
        else:
            action, reasons = "wait", ["No valuation range (no 5-year scenario model), so no limit price"]
    elif o["status"] == "in-range":
        action = "buy"
        reasons.append(f"Price ${o['price']} is inside the order range (consider at or below ${o['upper']})")
    elif o["status"] == "at-top":
        action = "buy"
        reasons.append(f"Price ${o['price']} is less than 1% above ${o['upper']}: place a limit order at ${o['upper']}")
    elif o["status"] == "below-floor":
        action = "starter"
        reasons.append(f"Price ${o['price']} is below the safety floor ${o['floor']}: cheaper than the bear case, so a starter only until a fundamental problem is ruled out")
    else:
        action = "wait"
        if o.get("method") == "rNPV":
            implied = (row.get("rnpv") or {}).get("impliedPeakSalesM")
            reasons.append(f"Price ${o['price']} is {o['gapToUpper']:.0%} above the rNPV base value ${o['upper']}"
                           + (f"; it implies ${implied:,.0f}M peak sales for the lead asset" if implied else ""))
        else:
            reasons.append(f"Price ${o['price']} is {o['gapToUpper']:.0%} above ${o['upper']}; it implies {o['impliedGrowth']:.0%} growth a year against {o['baseGrowth']:.0%} in the base case")
    # A watch verdict has a citation-checked memo but open gates: price can justify a starter, never a full buy.
    if decision == "watch" and action == "buy":
        action = "starter"
        reasons.append("Serenity verdict is watch (gates still open): starter only until the upgrade condition in the memo is met")
    # Adversarial second review (scripts/claude_adversarial_review.py): a verified quote that would fail a hard gate
    # sends the ticket back to a human before any money moves.
    adv = ctx.get("adversarial", {}).get(t) or {}
    if action in ("buy", "starter") and adv.get("blocking"):
        b = adv["blocking"][0]
        action = "wait"
        reasons.append(f"Adversarial review ({adv.get('model', 'opus')}) would fail {b['gate']}: {b['argument'][:160]}")
    # Backtest, confirmed out of sample (outputs/order-rule-backtest-oos.md): when the price implies growth more than
    # 20 points below the base case, outcomes were the worst of any bucket; the market usually knows something.
    if action in ("buy", "starter") and o and o.get("impliedGrowth") is not None and o.get("baseGrowth") is not None \
            and o["impliedGrowth"] - o["baseGrowth"] < -0.20:
        action = "wait"
        reasons.append(f"Deep discount: the price implies {o['impliedGrowth']:.0%} growth against {o['baseGrowth']:.0%} in the base case. "
                       "In the 2014-2026 backtests (both samples) this bucket had the worst returns; find out what the market knows first")
    # Backtest (outputs/order-rule-backtest.md): stocks in range while revenue growth was slowing had about twice
    # the rate of severe losses; a cheap price there usually means the market already sees the slowdown.
    trend = ctx.get("trends", {}).get(t)
    if action in ("buy", "starter") and trend and trend.get("slowing"):
        action = "wait"
        reasons.append(f"Revenue growth slowed from {trend['previousGrowth']:.0%} to {trend['growth']:.0%} (fiscal {trend['fiscalEnd'][:4]}): "
                       "in the 2014-2026 backtest, in-range stocks with slowing growth had about twice the severe losses")
    # 2. Size: Serenity tier, then the risk caps.
    tier = tier_of(row)
    size = STANDARD if tier == "standard" else STARTER
    if small and small.get("marketCapM", 1e9) < 1000:
        size = min(size, SMALL_STARTER if tier == "starter" else STARTER * 3)
        adjustments.append(f"market value ${small['marketCapM']}M, under $1B: smaller cap")
    if action == "starter":
        size = min(size, STARTER)
    if risk.get("worstDay") is not None and risk["worstDay"] <= DRAWDOWN_DAY:
        size /= 2
        adjustments.append(f"worst day in 6 months {risk['worstDay']:.0%}: halved for the drawdown budget")
    if small and small.get("runwayMonths") is not None and small["runwayMonths"] < RUNWAY_MONTHS:
        size = min(size, STARTER)
        adjustments.append(f"cash for {small['runwayMonths']:.0f} months: a share sale is likely, starter only")
    if risk.get("advUsd"):
        liquidity_cap = ADV_SHARE * risk["advUsd"] / portfolio
        if liquidity_cap < size:
            size = liquidity_cap
            adjustments.append(f"daily trading ${risk['advUsd'] / 1e6:.1f}M: at most 2% of a day's volume")
    size = round(min(size, CAP), 4) if action in ("buy", "starter") else 0.0
    # 3. Timing: split around the next earnings print; scale only on validation.
    earnings = next_earnings(t, ctx["watch"], today)
    near = earnings and (date.fromisoformat(earnings) - today).days <= 60
    now_part = round(size / 2, 4) if near and size else size
    target = round(min(CAP, (STANDARD if tier == "starter" else CAP)), 4)
    deal_cues = [f"{r['filed']} {('IND clearance' if r['kind'] == 'ind' else 'big-pharma deal')}" for r in ctx["deals"].get(t, [])]
    scale = (f"add after earnings, a customer or a deal confirms the thesis, up to {target:.0%}; never because the price rose"
             + (f". Next earnings {earnings}: buy half now" if near else ""))
    # 4. What would prove it wrong, and when to trim.
    falsifiers = [str(f) for f in (row.get("falsifiers") or [])][:3]
    counters = [str(c) for c in ((row.get("serenityVerdict") or {}).get("countersHolding") or [])][:2]
    crl = [e["title"] for e in ctx["events"].get(t, []) if "complete_response" in e.get("eventTypes", [])]
    departures = ctx["departures"].get(t, [])
    trim = ctx["bull"].get(t)
    return {
        "ticker": t, "company": row.get("company"), "rank": row.get("rank"), "potential": row.get("potential"),
        "action": action, "reasons": reasons, "serenityDecision": decision, "serenityTier": tier,
        "price": o.get("price") or risk.get("price"), "limitPrice": o.get("upper") if action in ("buy", "starter", "wait") and o else None,
        "safetyFloor": o.get("floor"), "positionPct": size, "buyNowPct": now_part, "positionUsd": round(size * portfolio),
        "sizeAdjustments": adjustments, "scalePlan": scale, "scaleCues": deal_cues, "nextEarnings": earnings,
        "invalidation": falsifiers + [f"open counter-point: {c}" for c in counters] + [f"FDA rejection letter: {c}" for c in crl]
                        + [f"key departure: {d}" for d in departures]
                        + [f"patents pledged to {who} (USPTO, recorded {when}): a default hands the IP to the lender"
                           for who, when in ctx.get("liens", {}).get(t, [])],
        "flipPoints": flip_points(o, row.get("rnpv")),
        "adversarial": {k: adv.get(k) for k in ("verdict", "overall", "model", "downgrades")} if adv else None,
        "trimAbove": trim, "trimRule": f"consider trimming above ${trim}, where even the bull case earns less than 12% a year" if trim else None,
        "risk": risk,
    }


def build(portfolio: float, price_fn=price_risk) -> dict:
    today = date.today()
    ranking = read(RANKING, {}).get("ranking", [])
    financials = {r["ticker"]: r for r in read(FINANCIALS, {}).get("companies", [])}
    events: dict[str, list] = {}
    for task in read(EVENTS, {}).get("revalidationTasks", []):
        events.setdefault(task["ticker"], []).append(task)
    departures: dict[str, list] = {}
    for d in (read(EARLY, {}).get("people") or {}).get("keyDepartures", []):
        if d.get("ticker"):
            departures.setdefault(d["ticker"], []).append(f"{d.get('filed', '')} {d.get('role') or d.get('summary') or ''}".strip())
    deals: dict[str, list] = {}
    for r in read(DEALS, {}).get("filings", []):
        f = r.get("facts") or {}
        if r.get("ticker") and (f.get("isNewDeal") is True or f.get("isIndClearance") is True):
            deals.setdefault(r["ticker"], []).append(r)
    ctx = {"risk": price_fn([r["ticker"] for r in ranking]) if ranking else {},
           "small": {r["ticker"]: r for r in read(SMALL_CAPS, {}).get("companies", [])},
           "events": events, "departures": departures, "deals": deals, "watch": read(WATCHLIST, {}),
           "trends": growth_trends([r["ticker"] for r in ranking]),
           "adversarial": read(ROOT / "state/serenity-adversarial.json", {}).get("companies", {}),
           "bull": {t: bull_price(f) for t, f in financials.items()},
           "liens": patent_liens(read(ROOT / "state/uspto-assignment-validation.json", {}))}
    small_rows = small_cap_rows({r["ticker"] for r in ranking})
    if small_rows:
        ctx["risk"].update(price_fn([r["ticker"] for r in small_rows]))
        ctx["trends"].update(growth_trends([r["ticker"] for r in small_rows]))
    tickets = [ticket(r, ctx, portfolio, today) for r in ranking + small_rows]
    order = {"buy": 0, "starter": 1, "wait": 2, "avoid": 3}
    tickets.sort(key=lambda x: (order[x["action"]], x.get("rank") or 99))
    return {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "portfolioUsd": portfolio,
            "method": __doc__.split("\n\n")[2].strip(), "tickets": tickets,
            "totals": {"positionPct": round(sum(x["positionPct"] for x in tickets), 4),
                       "buyNowPct": round(sum(x["buyNowPct"] for x in tickets), 4),
                       "byAction": {a: sum(x["action"] == a for x in tickets) for a in order}}}


ACTION_ZH = {"buy": "模拟买入", "starter": "模拟试探仓", "wait": "等待", "avoid": "回避"}


def report(payload: dict) -> str:
    t = payload["totals"]
    lines = ["# 模拟订单条件（研究用，需人工确认）", "",
             f"生成：{payload['generatedAt'][:16]}；假设组合规模 ${payload['portfolioUsd']:,.0f}。只在模拟盘执行，真实交易关闭。", "",
             "> 规则对每家公司相同：动作由 Serenity 结论和价格相对下单区间决定；仓位按 Serenity 分档（试探 1%、标准 5%、单只上限 10%），"
             "再按单日回撤、日成交额和现金跑道下调；只在财报、客户或合作披露验证后加仓；不设紧止损，论点被证伪才退出。", "",
             f"合计目标仓位 {t['positionPct']:.1%}，现在可买 {t['buyNowPct']:.1%}；" + "，".join(f"{ACTION_ZH[k]} {v}" for k, v in t["byAction"].items()) + "。", "",
             "| 动作 | 股票 | 价格 | 限价 | 安全底线 | 仓位（现在） | 理由 |", "|---|---|---:|---:|---:|---:|---|"]
    for x in payload["tickets"]:
        money = lambda v: f"${v:,.2f}" if v else "—"
        size = f"{x['positionPct']:.1%}（{x['buyNowPct']:.1%}）" if x["positionPct"] else "—"
        lines.append(f"| **{ACTION_ZH[x['action']]}** | {x['ticker']} | {money(x['price'])} | {money(x['limitPrice'])} | "
                     f"{money(x['safetyFloor'])} | {size} | {'；'.join(x['reasons'])[:140]} |")
    for x in payload["tickets"]:
        if x["action"] not in ("buy", "starter"):
            continue
        lines += ["", f"## {x['ticker']} · {ACTION_ZH[x['action']]} {x['positionPct']:.1%}（${x['positionUsd']:,}）", ""]
        lines += [f"- 理由：{'；'.join(x['reasons'])}", f"- Serenity：{x['serenityDecision']}，分档 {x['serenityTier']}"]
        if x["sizeAdjustments"]:
            lines.append(f"- 仓位调整：{'；'.join(x['sizeAdjustments'])}")
        lines.append(f"- 加仓：{x['scalePlan']}" + (f"（近期信号：{'、'.join(x['scaleCues'])}）" if x["scaleCues"] else ""))
        if x["trimRule"]:
            lines.append(f"- 减仓：{x['trimRule']}")
        lines.append("- 认错条件：" + ("；".join(x["invalidation"]) or "（待补充）"))
    lines += ["", "## 局限", "",
              "- 仓位规则来自 Serenity 的公开方法，没有经过本项目自己的回测；下单区间规则也还没有回测。",
              "- 组合层面的相关性还没考虑：几只同方向的股票可能一起跌。下一步用 Riskfolio-Lib 控制。",
              "- 这是研究建议，不是投资建议；每张单都需要人看过再执行。"]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--portfolio", type=float, default=100_000)
    args = parser.parse_args()
    payload = build(args.portfolio)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(report(payload), encoding="utf-8")
    print(json.dumps(payload["totals"], ensure_ascii=False))


if __name__ == "__main__":
    main()
