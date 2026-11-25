"""Build the AI Medicine 5-10 year leaders brief (HTML page, Markdown, JSON).

Answers one question: which AI-medicine companies have the highest potential over
the next 5-10 years, and why. It reuses the pipeline's existing outputs only:

- trend-agent/ai-medicine-universe.json   analyst 1-5 scores per dimension, each with a source
- trend-agent/ai-medicine-theses.json     thesis, why now, chokepoint angle, bear case, falsifiers
- state/ai-medicine-financial-scenarios.json  reported revenue, growth, market cap, P/S
- state/serenity-gate-results.json        Serenity gate completeness and evidence quality
- state/event-revalidation.json           unresolved material events
- state/fda-ai-devices.json               FDA AI-enabled device counts per company

Two numbers are kept apart on purpose. Potential ranks the companies. Evidence
confidence says how much of that view is backed by verified primary sources. A
high-potential company with thin evidence is flagged, not hidden or promoted.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Potential score weights (sum 100). Kept short so it can be explained in one breath.
WEIGHTS = {"moat": 35, "exposure": 20, "growth": 30, "durability": 15}
DIMENSION_LABELS = {
    "moat": "Moat",
    "exposure": "AI-medicine exposure",
    "growth": "Proven growth",
    "durability": "Financial durability",
}
# Compute enablers are shown for context but not ranked as AI-medicine companies.
BENCHMARK_ONLY = {"NVDA": "Compute supplier to the whole sector; healthcare is a small share of revenue, so it is a benchmark rather than an AI-medicine pick."}
TOP_N = 5  # kept for compatibility; picks are now chosen per bucket
PICKS_PER_BUCKET = 3
# Buckets from the aleabit-stock-selection skill: "safest compounders" (durability) versus
# "asymmetric upside" in its $400M-$5B market-cap sweet spot.
BUCKETS = [
    ("durable", "Durable compounders", "Market cap $5B+. Established platforms where AI strengthens an existing moat; lower risk, the market already knows them."),
    ("asymmetric", "Asymmetric upside", "Market cap $400M–$5B, the Serenity stock-selection sweet spot. Smaller, more AI-central, less followed; higher risk and higher torque."),
]
LOW_EVIDENCE = 50
# A citation-checked Serenity review replaces the analyst's 1-5 judgement on five
# dimensions with the matching gate result, so the ranking rests on quoted filings.
# Financial resilience stays a judgement on reported cash, debt and losses.
GATE_POINTS = {"pass": 5, "partial": 3, "unknown": 2, "pending": 2, "fail": 1}
GATE_FOR_DIMENSION = {
    "ai_medicine_relevance": "pure_play",
    "proprietary_data_or_models": "chokepoint_evidence",
    "workflow_or_customer_lock_in": "customer_dependency",
    "multi_node_control": "multi_node_control",
    "commercial_validation": "earnings_validation",
}
SCORE_NOISE = 3  # rank gaps smaller than this are within scoring noise


def load(path: Path, default=None):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        if default is not None:
            return default
        raise


def implied_growth(financial: dict, price: float, target: float = 0.12) -> float | None:
    """Reverse scenario: yearly revenue growth needed to earn `target` a year from `price`,
    holding the base case's exit multiple, margin and dilution. Fewer assumptions than the range."""
    model = financial.get("scenario_model") or {}
    base = (model.get("cases") or {}).get("base") or {}
    years, revenue0, shares = model.get("horizon_years") or 5, model.get("revenue_basis_m"), financial.get("shares")
    multiple = base.get("terminal_multiple")
    if not (price and revenue0 and shares and multiple):
        return None
    per_revenue = multiple * (base.get("terminal_margin") or 1 if model.get("metric") == "ebitda" else 1)
    equity_needed = price * shares / 1e6 * (1 + target) ** years * (1 + base.get("annual_share_dilution", 0)) ** years
    revenue_needed = (equity_needed + model.get("net_debt_assumption_m", 0)) / per_revenue
    return (revenue_needed / revenue0) ** (1 / years) - 1 if revenue_needed > 0 else -1.0


def rnpv_range(r: dict | None) -> dict | None:
    """rNPV order range (scripts/rnpv_valuation.py) for a drug developer with no revenue to model; platforms excluded."""
    return dict(r["orderRange"]) if r and r.get("rangeUsable") else None


def rnpv_summary(r: dict | None) -> dict | None:
    if not r:
        return None
    return {"phase": r["phase"], "impliedPeakSalesM": r["impliedPeakSalesM"], "rangeUsable": r.get("rangeUsable"),
            "platform": r.get("platform"), "upper": r["orderRange"]["upper"], "floor": r["orderRange"]["floor"]}


def order_range(financial: dict, latest_price: float | None = None) -> dict | None:
    """Price levels implied by the 5-year scenarios: where buying meets the return policy, and a safety floor.

    upper: base case >= 12% a year and bear case no worse than -10% a year.
    floor: the bear case does not lose money. Inputs are analyst-set assumptions, not verified forecasts.
    """
    model = financial.get("scenario_model") or {}
    cases = model.get("cases") or {}
    base, bear = cases.get("base", {}), cases.get("bear", {})
    if base.get("price_for_policy_return") is None or bear.get("price_for_policy_return") is None:
        return None
    # The two levels depend only on the scenarios and share count; today's price only moves the status.
    snapshot_price = financial.get("price")
    price = latest_price or snapshot_price
    scale = (snapshot_price / price) ** (1 / (model.get("horizon_years") or 5)) if price and snapshot_price else 1.0
    upper = min(base["price_for_policy_return"], bear["price_for_policy_return"])
    floor = min(bear.get("price_for_zero_return", upper), upper)
    status = ("below-floor" if price <= floor else "in-range" if price <= upper
              else "at-top" if price / upper - 1 < 0.01 else "above")
    return {"price": round(price, 2), "upper": upper, "floor": floor, "status": status,
            "gapToUpper": round(price / upper - 1, 3) if upper else None,
            "baseReturn": (1 + base["annualized_return"]) * scale - 1 if base.get("annualized_return") is not None else None,
            "bearReturn": (1 + bear["annualized_return"]) * scale - 1 if bear.get("annualized_return") is not None else None,
            "impliedGrowth": implied_growth(financial, price),
            "baseGrowth": base.get("revenue_cagr"), "baseMultiple": base.get("terminal_multiple"),
            "baseMultipleBasis": base.get("terminal_multiple_basis"), "bearMultiple": bear.get("terminal_multiple"),
            "bearMultipleBasis": bear.get("terminal_multiple_basis"), "growthSource": model.get("growth_source"),
            "multipleMetric": "EBITDA" if model.get("metric") == "ebitda" else "sales",
            "reportedGrowth": (financial.get("revenue_growth_pct") or 0) / 100 if financial.get("revenue_growth_pct") is not None else None,
            "priceSource": "latest close" if latest_price else "financial snapshot",
            "verified": bool((financial.get("scenario_inputs") or {}).get("inputs_verified"))}


def serenity_scores(scores: dict, assessment: dict) -> dict:
    """Dimension scores derived from a citation-checked Serenity review's gate results."""
    derived = dict(scores)
    for dimension, gate in GATE_FOR_DIMENSION.items():
        derived[dimension] = GATE_POINTS.get(assessment.get(gate, "unknown"), 2)
    return derived


def growth_points(financial: dict) -> tuple[float, str]:
    """Points (0-15) from reported year-over-year revenue growth."""
    growth = financial.get("revenue_growth_pct")
    if growth is None:
        return 4.0, "growth not reported"
    if financial.get("price_to_sales_approx") is None:
        # Collaboration/milestone revenue swings (e.g. +258%) say little about durable growth.
        return 4.0, f"{growth:+.0f}% YoY, milestone-driven, not counted as durable"
    points = 15.0 if growth >= 30 else 12.0 if growth >= 20 else 8.0 if growth >= 10 else 4.0
    return points, f"{growth:+.0f}% YoY reported revenue"


def potential(scores: dict, financial: dict) -> dict:
    moat = (scores["proprietary_data_or_models"] + scores["workflow_or_customer_lock_in"] + scores["multi_node_control"]) / 15 * WEIGHTS["moat"]
    exposure = scores["ai_medicine_relevance"] / 5 * WEIGHTS["exposure"]
    reported, growth_note = growth_points(financial)
    growth = scores["commercial_validation"] / 5 * 15 + reported
    durability = scores["financial_resilience"] / 5 * WEIGHTS["durability"]
    parts = {"moat": moat, "exposure": exposure, "growth": growth, "durability": durability}
    return {
        "total": round(sum(parts.values()), 1),
        "parts": {key: round(value, 1) for key, value in parts.items()},
        "growthNote": growth_note,
    }


def fda_counts(fda: dict) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in fda.get("companyCoverage", []) or []:
        if isinstance(row, dict) and row.get("ticker"):
            value = row.get("matchedDevices", row.get("deviceCount", row.get("count")))
            if isinstance(value, int):
                counts[row["ticker"]] = value
            elif isinstance(value, list):
                counts[row["ticker"]] = len(value)
    return counts


def repriced(financial: dict, market: dict) -> dict:
    """Market value and price/sales moved from the scenario snapshot to the latest close, so every price-based number on a
    card shares one date. Shares and revenue do not move with the price."""
    cap, ps, snap, day = financial.get("market_cap_m"), financial.get("price_to_sales_approx"), financial.get("price"), financial.get("price_date")
    last, asof = market.get("last"), market.get("asOf")
    if last and snap and asof and (not day or asof > day):
        k = last / snap
        return {"marketCapM": round(cap * k, 1) if cap else cap, "priceToSales": round(ps * k, 1) if ps else ps, "priceDate": asof}
    return {"marketCapM": cap, "priceToSales": ps, "priceDate": day}


def build(root: Path = ROOT) -> dict:
    universe = {row["ticker"]: row for row in load(root / "trend-agent/ai-medicine-universe.json")["companies"]}
    thesis_file = load(root / "trend-agent/ai-medicine-theses.json")
    theses = {row["ticker"]: row for row in thesis_file["candidates"] + thesis_file.get("expanded_deep_dives", [])}
    financials = {row["ticker"]: row for row in load(root / "state/ai-medicine-financial-scenarios.json")["companies"]}
    gates = {row["ticker"]: row for row in load(root / "state/serenity-gate-results.json")["companies"]}
    rnpv = {row["ticker"]: row for row in load(root / "state/rnpv-valuations.json", {"companies": []})["companies"]}
    events = load(root / "state/event-revalidation.json", {"revalidationTasks": []})
    fda = load(root / "state/fda-ai-devices.json", {})
    devices = fda_counts(fda)

    open_events: dict[str, list[dict]] = {}
    for task in events.get("revalidationTasks", []):
        bucket = open_events.setdefault(task["ticker"], [])
        if all(existing["title"] != task["title"] for existing in bucket):
            bucket.append({"title": task["title"], "url": task.get("url"), "source": task.get("source")})

    assessments = {r["ticker"]: r for r in load(root / "state/serenity-auto-assessments.json", {}).get("companies", [])}
    review_status = load(root / "state/serenity-review-status.json", {}).get("companies", {})

    def serenity_reviewed(ticker: str) -> bool:
        return (review_status.get(ticker, {}).get("claudeMemo") == "citation-checked"
                and "-claude-" in str(assessments.get(ticker, {}).get("review_path", "")))

    latest_prices = load(root / "state/market-validation.json", {}).get("companies", {})
    companies, benchmarks = [], []
    for ticker, thesis in theses.items():
        if ticker not in universe or ticker not in financials:
            continue
        financial = financials[ticker]
        gate = gates.get(ticker, {})
        reviewed = serenity_reviewed(ticker)
        scores = serenity_scores(universe[ticker]["scores"], assessments[ticker]) if reviewed else universe[ticker]["scores"]
        row = {
            "ticker": ticker,
            "company": thesis["company"],
            "segment": universe[ticker].get("segment", ""),
            "potential": potential(scores, financial),
            "serenityReviewed": reviewed,
            "orderRange": order_range(financial, (latest_prices.get(ticker) or {}).get("last")) or rnpv_range(rnpv.get(ticker)),
            "rnpv": rnpv_summary(rnpv.get(ticker)),
            "scoreBasis": "Serenity gates (citation-checked)" if reviewed else "analyst judgement, not yet Serenity-reviewed",
            "evidence": gate.get("substantiatedScore", 0),
            "gateDecision": gate.get("decision", "unreviewed"),
            "missingGates": gate.get("hardGateFailures", []),
            "openEvents": open_events.get(ticker, [])[:3],
            "fdaAiDevices": devices.get(ticker),
            "thesis": thesis.get("thesis", ""),
            "whyNow": thesis.get("why_now", ""),
            "chokepoint": thesis.get("serenity_angle", ""),
            "bearCase": thesis.get("bear_case", ""),
            "falsifiers": thesis.get("falsifiers", [])[:3],
            "longTerm": thesis.get("long_term_case"),
            "sources": list(dict.fromkeys(thesis.get("sources", []) + financial.get("sources", [])))[:4],
            "numbers": {
                "period": financial.get("financial_period"),
                "quarterlyRevenueM": financial.get("quarterly_revenue_m"),
                "revenueGrowthPct": financial.get("revenue_growth_pct"),
                **repriced(financial, latest_prices.get(ticker) or {}),
                "valuation": financial.get("valuation_label", ""),
            },
        }
        if ticker in BENCHMARK_ONLY:
            row["benchmarkReason"] = BENCHMARK_ONLY[ticker]
            benchmarks.append(row)
        else:
            companies.append(row)

    screen = load(root / "state/ai-medicine-universe-screen.json", {})
    not_found = set(screen.get("knownNotFound", []))
    companies.sort(key=lambda row: (-row["potential"]["total"], -row["evidence"]))
    for rank, row in enumerate(companies, 1):
        row["rank"] = rank
        row["lowEvidence"] = row["evidence"] < LOW_EVIDENCE
        # The market-wide screen requires filings to describe AI as the company's own product.
        # A citation-checked Serenity review that quotes the filing's AI description settles it.
        review = assessments.get(row["ticker"], {})
        quoted_ai = "-claude-" in str(review.get("review_path", "")) and bool(review.get("gate_reviews", {}).get("pure_play", {}).get("support"))
        row["aiConfirmedInFilings"] = quoted_ai and review.get("pure_play") != "pass"
        row["aiUnverified"] = bool(screen) and row["ticker"] in not_found and not quoted_ai
        cap = row["numbers"]["marketCapM"]
        row["bucket"] = "durable" if cap and cap >= 5_000 else "asymmetric" if cap and cap >= 400 else "micro"
    picks = {}
    for key, _, _ in BUCKETS:
        # Only companies with a current, citation-checked Serenity review can be picked.
        members = [row for row in companies if row["bucket"] == key and row["serenityReviewed"]]
        for position, row in enumerate(members, 1):
            row["bucketRank"] = position
        picks[key] = members[:PICKS_PER_BUCKET]
        for row in picks[key]:
            row["pick"] = True
    news_calls = {c["ticker"]: c for c in load(root / "state/news-recommendations.json", {}).get("calls", [])}
    verdicts = {r["ticker"]: r for r in load(root / "state/serenity-claude-verdicts.json", {}).get("companies", [])}
    for row in companies:
        call = news_calls.get(row["ticker"], {})
        row["newsEvents"] = [e for e in call.get("events", []) if e.get("type") != "commentary"][:3]
        row["newsTier"] = call.get("tier")
        row["serenityVerdict"] = verdicts.get(row["ticker"])
    queue_manifest = load(root / "state/serenity-codex-queue.json", {})
    chokepoints = load(root / "state/ai-medicine-chokepoints.json", {})
    screened_out = [
        {"ticker": row["ticker"], "company": row["company"], "reason": row.get("screen_reason", "")}
        for row in universe.values() if row["ticker"] not in theses
    ]
    price_dates = sorted({row["numbers"]["priceDate"] for row in companies if row["numbers"]["priceDate"]})
    scenario_dates = sorted({f.get("price_date") for f in financials.values() if f.get("price_date")})
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "question": "Which AI-medicine companies have the highest potential over the next 5-10 years, and why?",
        "weights": WEIGHTS,
        "scoreNoise": SCORE_NOISE,
        "lowEvidenceThreshold": LOW_EVIDENCE,
        "priceDate": price_dates[-1] if price_dates else None,
        "scenarioDate": scenario_dates[-1] if scenario_dates else None,
        "funnel": {
            "screened": len(universe),
            "deepReviewed": len(companies) + len(benchmarks),
            "ranked": len(companies),
            "top": sum(len(v) for v in picks.values()),
        },
        "screen": {
            "funnel": screen.get("funnel"),
            "asOf": screen.get("asOf"),
            "queue": [r for r in screen.get("companies", []) if r.get("shortlisted") and not r.get("deepReviewed")][:12],
            "notFound": sorted(not_found & {row["ticker"] for row in companies}),
        } if screen else None,
        "picks": picks,
        "serenityQueue": {"queued": len(queue_manifest.get("companies", [])), "generatedAt": queue_manifest.get("generatedAt")} if queue_manifest else None,
        "chokepoints": chokepoints or None,
        "news": load(root / "state/news-recommendations.json", {}) or None,
        "top": [row for key, _, _ in BUCKETS for row in picks[key]],
        "ranking": companies,
        "benchmarks": benchmarks,
        "screenedOut": screened_out,
        "fdaTotalDevices": (fda.get("summary") or {}).get("totalDevices"),
    }


# ---------- rendering ----------

def esc(value) -> str:
    return html.escape(str(value or ""), quote=True)


def money(value_m) -> str:
    if value_m is None:
        return "n/a"
    return f"${value_m / 1000:,.1f}B" if value_m >= 1000 else f"${value_m:,.0f}M"


def scatter_svg(rows: list[dict]) -> str:
    """Potential (y) vs evidence confidence (x), drawn on one linear scale."""
    width, height = 640, 420
    left, right, top, bottom = 56, 24, 20, 52
    x_min, x_max, y_min, y_max = 20, 80, 55, 95
    px = lambda v: left + (v - x_min) / (x_max - x_min) * (width - left - right)
    py = lambda v: top + (y_max - v) / (y_max - y_min) * (height - top - bottom)
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-labelledby="map-title map-desc" class="map">',
             '<title id="map-title">Potential versus evidence confidence</title>',
             '<desc id="map-desc">Each dot is one company. Higher means more 5-10 year potential; further right means more of the view is backed by verified primary evidence.</desc>']
    # quadrant shading for the lead-candidate corner
    parts.append(f'<rect x="{px(LOW_EVIDENCE):.1f}" y="{py(y_max):.1f}" width="{px(x_max) - px(LOW_EVIDENCE):.1f}" height="{py(80) - py(y_max):.1f}" class="lead-zone"/>')
    for tick in range(x_min, x_max + 1, 10):
        parts.append(f'<line x1="{px(tick):.1f}" x2="{px(tick):.1f}" y1="{top}" y2="{height - bottom}" class="grid"/>')
        parts.append(f'<text x="{px(tick):.1f}" y="{height - bottom + 18}" class="tick" text-anchor="middle">{tick}</text>')
    for tick in range(y_min, y_max + 1, 10):
        parts.append(f'<line x1="{left}" x2="{width - right}" y1="{py(tick):.1f}" y2="{py(tick):.1f}" class="grid"/>')
        parts.append(f'<text x="{left - 10}" y="{py(tick) + 4:.1f}" class="tick" text-anchor="end">{tick}</text>')
    parts.append(f'<line x1="{px(LOW_EVIDENCE):.1f}" x2="{px(LOW_EVIDENCE):.1f}" y1="{top}" y2="{height - bottom}" class="divider"/>')
    parts.append(f'<line x1="{left}" x2="{width - right}" y1="{py(80):.1f}" y2="{py(80):.1f}" class="divider"/>')
    parts.append(f'<text x="{width - right - 8}" y="{py(y_max) + 18:.1f}" class="zone-label" text-anchor="end">Lead candidates</text>')
    parts.append(f'<text x="{left + 8}" y="{py(y_max) + 18:.1f}" class="zone-label">High potential, verify first</text>')
    parts.append(f'<text x="{(left + width - right) / 2:.1f}" y="{height - 8}" class="axis" text-anchor="middle">Evidence confidence (verified primary sources, 0-100)</text>')
    parts.append(f'<text transform="translate(16 {(top + height - bottom) / 2:.1f}) rotate(-90)" class="axis" text-anchor="middle">5-10 year potential</text>')

    placed: list[tuple[float, float, float, float]] = []
    dots = [(px(min(max(r["evidence"], x_min), x_max)), py(min(max(r["potential"]["total"], y_min), y_max)), r) for r in rows]

    def collides(box):
        x1, y1, x2, y2 = box
        if x1 < left or x2 > width - right or y1 < top or y2 > height - bottom:
            return True
        if any(not (x2 < a or x1 > c or y2 < b or y1 > d) for a, b, c, d in placed):
            return True
        return any(x1 - 4 < dx < x2 + 4 and y1 - 4 < dy < y2 + 4 for dx, dy, _ in dots)

    for x, y, row in sorted(dots, key=lambda item: item[1]):
        top_pick = bool(row.get("pick"))
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{6 if top_pick else 4.5}" class="{"dot top" if top_pick else "dot"}"/>')
        label_w = 8.2 * len(row["ticker"]) + 4
        for dx, dy, anchor in ((10, 4, "start"), (-10, 4, "end"), (0, -11, "middle"), (0, 19, "middle"), (10, -9, "start"), (10, 17, "start"), (-10, -9, "end"), (-10, 17, "end")):
            x1 = x + dx if anchor == "start" else x + dx - label_w if anchor == "end" else x - label_w / 2
            box = (x1, y + dy - 11, x1 + label_w, y + dy + 2)
            if not collides(box):
                break
        placed.append(box)
        parts.append(f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}" class="{"label top" if top_pick else "label"}">{esc(row["ticker"])}</text>')
    parts.append("</svg>")
    return "".join(parts)


def bars(parts: dict) -> str:
    rows = []
    for key, maximum in WEIGHTS.items():
        value = parts[key]
        rows.append(
            f'<div class="dim"><span>{DIMENSION_LABELS[key]}</span>'
            f'<span class="track" aria-hidden="true"><span style="width:{value / maximum * 100:.0f}%"></span></span>'
            f'<span class="num">{value:.0f}/{maximum}</span></div>'
        )
    return "".join(rows)


EVENT_LABEL = {"regulatory": "Regulatory", "reimbursement": "Reimbursement", "partnership": "Partnership", "m&a": "M&A",
               "clinical": "Clinical", "earnings": "Earnings", "financing": "Financing", "leadership": "Leadership",
               "legal": "Legal", "product": "Product", "analyst": "Analyst", "commentary": "Commentary",
               "disclosure": "SEC disclosure", "filing": "SEC filing", "insider": "Insider trade"}


def event_item(event: dict) -> str:
    tone = "ok" if event.get("direction", 0) > 0 else "alert" if event.get("direction", 0) < 0 else "plain"
    arrow = "▲" if event.get("direction", 0) > 0 else "▼" if event.get("direction", 0) < 0 else "•"
    outlets = len(event.get("sources", []))
    return (f'<li class="news-item"><span class="chip {tone}">{arrow} {esc(EVENT_LABEL.get(event.get("type"), event.get("type")))}</span> '
            f'<a href="{esc(event.get("url"))}" target="_blank" rel="noopener">{esc(event.get("title"))}</a> '
            f'<span class="news-meta">{esc((event.get("at") or "")[:10])} · {outlets} outlet{"s" if outlets != 1 else ""}</span></li>')


def implied_line(o: dict) -> str:
    """What today's price already assumes: growth needed for 12% a year, against reported and base-case growth."""
    g = o.get("impliedGrowth")
    if g is None:
        return ""
    reported = f'Last reported growth {o["reportedGrowth"]:+.0%} year over year; ' if o.get("reportedGrowth") is not None else ""
    basis = ""
    if o.get("baseMultipleBasis") and o.get("bearMultipleBasis"):
        basis = (f' <span class="muted-note">Exit multiples have a source, the same rule for every company: base case {o["baseMultiple"]:g}x = '
                 f'{esc(o["baseMultipleBasis"].split(" (")[0])}; bear case {o["bearMultiple"]:g}x = {esc(o["bearMultipleBasis"].split(", Damodaran")[0])}, '
                 f'<a href="https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/psdata.html" rel="noopener" target="_blank">Damodaran, January 2026</a>.</span>')
    gs = o.get("growthSource")
    if gs:
        assumed = (f'our base case assumes {o["baseGrowth"]:.0%}: growth fades from {gs["start"]:.0%} ({esc(gs["start_basis"])}) '
                   f'to the industry\'s fundamental growth {gs["industry_fundamental_growth"]:.1%} over 5 years '
                   f'(<a href="https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/fundgr.html" rel="noopener" target="_blank">Damodaran</a>; '
                   'the fade follows the mean-reversion finding in Mauboussin, The Base Rate Book).')
    else:
        assumed = f'our base case assumes {o["baseGrowth"]:.0%}.'
    return (f'<p class="implied">Priced in: to earn 12% a year from ${o["price"]:,.2f}, revenue must grow '
            f'<strong>{g:.0%} a year for 5 years</strong> (exit at {o["baseMultiple"]:g}x {o["multipleMetric"]}). '
            f'{reported}{assumed}{basis}</p>')


def order_block(o: dict | None) -> str:
    """Order range from the scenarios, with today's price against it."""
    if not o:
        return ""
    chip = {"above": ("warn", f"Above range by {o['gapToUpper']:.0%}"), "in-range": ("ok", "Inside range"), "at-top": ("plain", "At the top of the range"),
            "below-floor": ("ok", "Below safety floor")}[o["status"]]
    return (f'<div class="order"><h4>Order range (from 5-year scenarios)</h4>'
            f'<p><span class="chip {chip[0]}">{esc(chip[1])}</span> Price now <strong>${o["price"]:,.2f}</strong> · '
            f'consider at or below <strong>${o["upper"]:,.2f}</strong> · safety floor <strong>${o["floor"]:,.2f}</strong></p>'
            f'{implied_line(o)}'
            f'<p class="muted-note">At today\'s price the base case returns {o["baseReturn"]:+.1%} a year and the bear case {o["bearReturn"]:+.1%}. '
            'Upper: base case ≥12% a year and bear case no worse than −10%. Floor: bear case does not lose money. '
            'Growth and exit multiples follow one sourced rule for every company (see below), not verified forecasts; this is a research range, not advice.</p></div>')


CARD_ACTION = {"buy": ("Buy", "ok"), "starter": ("Starter", "warn"), "wait": ("Wait", "plain"), "avoid": ("Avoid", "alert")}
CARD_DECISION = {"research-ready": ("Research-ready", "ok"), "watch": ("Watch", "warn"), "revalidate": ("Re-check", "alert"),
                 "reject": ("Reject", "alert")}


def card(row: dict, ticket: dict | None = None, gates: dict | None = None) -> str:
    """Four layers, one line of conclusion each: why it was found, what the Serenity evidence says, what the price says,
    and what happens next. The full memo sits underneath, collapsed."""
    n = row["numbers"]
    stats = [
        (f"{n['period']} revenue" if n["period"] else "Quarterly revenue", money(n["quarterlyRevenueM"])),
        ("Revenue growth", f"{n['revenueGrowthPct']:+.0f}% YoY" if n["revenueGrowthPct"] is not None else "n/a"),
        ("Market cap", money(n["marketCapM"])),
        ("Price / sales", f"{n['priceToSales']:.1f}x" if n["priceToSales"] else "n/a"),
    ]
    if row.get("fdaAiDevices"):
        stats.append(("FDA AI devices", str(row["fdaAiDevices"])))
    lt = row.get("longTerm") or {}
    # 1. Why it was found
    news = "".join(event_item(e) for e in row.get("newsEvents", [])[:2])
    found = (f'<p>{esc(row["chokepoint"])}</p><p class="via-theme">{esc(row["whyNow"])}</p>'
             + (f'<ul class="news-list">{news}</ul>' if news else ""))
    # 2. Serenity evidence
    states = gates or (row.get("serenityVerdict") or {}).get("gates") or {}
    passed = [GATE_NAMES.get(g, g) for g, v in states.items() if v == "pass"]
    open_ = [f'<span>{esc(GATE_NAMES.get(g, g))}</span> <span>{esc(v)}</span>' for g, v in states.items() if v != "pass"]
    label, tone = CARD_DECISION.get(row.get("gateDecision") or "", ("Not reviewed", "plain"))
    evidence = (f'<p><span class="chip {tone}">{label}</span> {len(passed)} of {len(states)} evidence gates pass'
                + (". Open: " + " · ".join(open_) if open_ else ".") + "</p>" if states else
                f'<p><span class="chip {tone}">{label}</span> No gate review yet.</p>')
    if lt.get("counter"):
        evidence += f'<p class="via-theme">Biggest counter-point: <span>{esc(lt["counter"])}</span></p>'
    # 3. Price
    if ticket:
        a_label, a_tone = CARD_ACTION.get(ticket["action"], (ticket["action"], "plain"))
        size = f' {ticket["positionPct"]:.1%}' if ticket.get("positionPct") else ""
        price = (f'<p><span class="chip {a_tone}">{a_label}{size}</span> {esc((ticket.get("reasons") or [""])[0])}</p>')
    else:
        price = '<p><span class="chip plain">No ticket</span> No order ticket for this company yet.</p>'
    price += f'<dl class="stats">{"".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in stats)}</dl>' + order_block(row.get("orderRange"))
    # 4. Next trigger
    triggers = [esc(lt["next_check"])] if lt.get("next_check") else []
    triggers += [f"Open re-check: {esc(e['title'])}" for e in row["openEvents"][:2]]
    nxt = (f'<ul class="plain-list">{"".join(f"<li>{t}</li>" for t in triggers)}</ul>' if triggers else '<p class="via-theme">No dated trigger on file.</p>')
    if row["falsifiers"]:
        nxt += f'<p class="via-theme">Wrong if: <span>{esc(row["falsifiers"][0])}</span></p>'
    falsifiers = "".join(f"<li>{esc(item)}</li>" for item in row["falsifiers"])
    sources = "".join(
        f'<li><a href="{esc(url)}" rel="noopener" target="_blank">{esc(url.split("/")[2] if "//" in url else url)}</a></li>'
        for url in row["sources"]
    )
    v = row.get("serenityVerdict")
    memo = (f'<h4>Serenity memo</h4><p>{esc(v.get("verdict", ""))} Counters that hold: {esc("; ".join(v.get("countersHolding", [])))}.</p>' if v else "")
    return f"""
<article class="pick" id="{esc(row['ticker'])}">
  <header class="pick-head">
    <div class="rank" aria-label="Rank {row.get('bucketRank', row['rank'])} in bucket">{row.get('bucketRank', row['rank'])}</div>
    <div class="who">
      <h3><span class="ticker">{esc(row['ticker'])}</span> {esc(row['company'])}</h3>
      <p class="segment">{esc(row['segment'])}</p>
    </div>
    <div class="scores">
      <div><span class="big">{row['potential']['total']:.0f}</span><span class="cap">Potential</span></div>
      <div><span class="big muted">{row['evidence']}</span><span class="cap">Evidence</span></div>
    </div>
  </header>
  <ol class="layers">
    <li><h4>Why it was found</h4>{found}</li>
    <li><h4>Serenity evidence</h4>{evidence}</li>
    <li><h4>Price today</h4>{price}</li>
    <li><h4>Next trigger</h4>{nxt}</li>
  </ol>
  <details class="memo">
    <summary>Full memo: thesis, case against, score parts, sources</summary>
    <div class="pick-body">
      <section>
        <h4>Why it can win</h4>
        <p>{esc(row['thesis'])}</p>
        {memo}
        <div class="dims">{bars(row['potential']['parts'])}</div>
      </section>
      <section class="against">
        <h4>Strongest case against</h4>
        <p>{esc(row['bearCase'])}</p>
        <h4>We are wrong if</h4>
        <ul>{falsifiers}</ul>
        <h4>Sources</h4>
        <ul class="sources">{sources}</ul>
      </section>
    </div>
  </details>
</article>"""


STYLE = """
/* Layout: one reading column; answer first, then the map, then each pick as a memo, then method. */
:root{
  --ink:#15221d; --muted:#5f6c66; --paper:#f3f0e8; --card:#fbfaf5; --line:#d8d7cd;
  --green:#0d6b4e; --green-soft:#e3eee6; --amber:#9a5f17; --amber-soft:#f4e7d2; --red:#a2443a; --red-soft:#f5e1dd;
  --serif:Georgia,"Times New Roman",serif; --sans:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  color-scheme:dark; --ink:#e6ece8; --muted:#9aa8a1; --paper:#111814; --card:#18211c; --line:#2c3832;
  --green:#6fcf9f; --green-soft:#1d3329; --amber:#e3ad5f; --amber-soft:#382b17; --red:#ec8f84; --red-soft:#3a2120;}}
:root[data-theme="dark"]{
  color-scheme:dark; --ink:#e6ece8; --muted:#9aa8a1; --paper:#111814; --card:#18211c; --line:#2c3832;
  --green:#6fcf9f; --green-soft:#1d3329; --amber:#e3ad5f; --amber-soft:#382b17; --red:#ec8f84; --red-soft:#3a2120;}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:15px;line-height:1.6}
.page{max-width:1040px;margin:0 auto;padding-block:40px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:56px}
h1,h2,h3{font-family:var(--serif);font-weight:500;text-wrap:balance;margin:0}
h1{font-size:clamp(32px,5vw,52px);line-height:1.05;letter-spacing:-.02em}
h2{font-size:clamp(24px,3vw,30px)}
h4{margin:0;font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:700}
p{margin:0}
a{color:var(--green)} a:focus-visible{outline:2px solid var(--green);outline-offset:2px}
.eyebrow{font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:var(--green);font-weight:700}
.intro{display:grid;gap:18px}
.lede{max-width:65ch;color:var(--muted);font-size:17px}
.answers{display:grid;gap:14px}
.answer-group{display:grid;gap:6px}
.answer-label{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:700}
.answer{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1px;background:var(--line);border:1px solid var(--line)}
.bucket-h{font-size:22px;margin-top:8px}
.calls{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px}
.call{background:var(--card);border:1px solid var(--line);padding:20px;display:grid;gap:12px;align-content:start}
.call-head{display:flex;justify-content:space-between;gap:12px;align-items:flex-start;flex-wrap:wrap}
.call-head h3{font-size:20px}
.call-foot{font-size:13px;color:var(--muted)}
.news-list{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.news-item{font-size:13px;line-height:1.45}
.news-item a{color:var(--ink)}
.news-meta{color:var(--muted);font-size:12px;white-space:nowrap}
.news-block{display:grid;gap:8px}
.news-answer a{background:var(--green-soft)}
.via-theme{font-size:13px;color:var(--muted);margin:0}
.call-step{display:grid;gap:8px;padding-top:10px;border-top:1px solid var(--line)}
.status-banner{max-width:75ch;font-size:14px;padding:12px 14px;background:var(--amber-soft);color:var(--ink);margin:0}
.fresh-alert{max-width:75ch;font-size:14px;padding:12px 14px;background:var(--red-soft);color:var(--ink);margin:0;border-left:4px solid var(--red)}
.fresh-alert strong{color:var(--red)}
.fresh{font-size:12px;color:var(--muted);max-width:75ch}
.fresh summary{cursor:pointer}
.fresh table{font-size:12px;margin-top:8px}
.call-verdict{font-family:var(--serif);font-size:16px;line-height:1.45}
.mini{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin:0}
.mini dt{font-size:11px;color:var(--muted)} .mini dd{margin:2px 0 0;font-size:13px;font-weight:600}
.via-theme a{color:var(--ink)}
.bucket-blurb{color:var(--muted);max-width:70ch;font-size:14px}
.note{font-size:13px;color:var(--muted);max-width:75ch}
.plain-list{margin:0;padding-left:18px;display:grid;gap:6px;font-size:14px;color:var(--muted)}
.answer a{display:grid;gap:4px;padding:16px;background:var(--card);text-decoration:none;color:var(--ink)}
.answer a:hover{background:var(--green-soft)}
.answer .r{font-family:var(--mono);font-size:12px;color:var(--muted)}
.answer .t{font-family:var(--mono);font-weight:700;font-size:20px}
.answer .c{font-size:12px;color:var(--muted);line-height:1.35}
.answer .s{font-variant-numeric:tabular-nums;font-size:12px}
.meta{display:flex;flex-wrap:wrap;gap:8px 24px;font-size:12px;color:var(--muted)}
.section{display:grid;gap:20px}
.section > p{max-width:65ch;color:var(--muted)}
.map-wrap{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:28px;align-items:start}
.map-box{overflow-x:auto;background:var(--card);border:1px solid var(--line);padding:12px}
.map{width:100%;min-width:520px;height:auto;display:block}
.map .grid{stroke:var(--line);stroke-width:1}
.map .divider{stroke:var(--muted);stroke-dasharray:4 4;stroke-width:1}
.map .lead-zone{fill:var(--green-soft)}
.map .tick{fill:var(--muted);font:11px var(--sans);font-variant-numeric:tabular-nums}
.map .axis{fill:var(--muted);font:12px var(--sans)}
.map .zone-label{fill:var(--green);font:600 11px var(--sans);letter-spacing:.04em}
.map .dot{fill:var(--muted)} .map .dot.top{fill:var(--green)}
.map .label{fill:var(--muted);font:600 12px var(--mono)} .map .label.top{fill:var(--ink);font-weight:700}
.reading{display:grid;gap:14px;font-size:14px}
.reading p{color:var(--muted)}
.reading strong{color:var(--ink)}
.picks{display:grid;gap:28px}
.pick{background:var(--card);border:1px solid var(--line);padding:28px;display:grid;gap:18px}
.pick-head{display:grid;grid-template-columns:auto 1fr auto;gap:18px;align-items:center}
.rank{width:44px;height:44px;display:grid;place-items:center;background:var(--ink);color:var(--paper);font:500 22px var(--serif)}
.who h3{font-size:24px}
.ticker{font-family:var(--mono);font-weight:700;font-size:20px;margin-right:6px}
.segment{color:var(--muted);font-size:13px}
.scores{display:flex;gap:22px;text-align:right}
.scores div{display:grid}
.big{font:500 34px/1 var(--serif);font-variant-numeric:tabular-nums}
.big.muted{color:var(--muted)}
.cap{font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin-top:4px}
.angle{font-family:var(--serif);font-size:19px;line-height:1.5;max-width:70ch}
.chips{display:flex;flex-wrap:wrap;gap:8px}
.chip{font-size:11px;font-weight:700;padding:4px 9px;letter-spacing:.03em}
.chip.ok{background:var(--green-soft);color:var(--green)}
.chip.warn{background:var(--amber-soft);color:var(--amber)}
.chip.alert{background:var(--red-soft);color:var(--red)}
.ticket{border-top:1px solid var(--line);padding-top:10px;margin-top:14px}
.ticket ul{margin:6px 0 0;padding-left:18px;display:grid;gap:4px;max-width:90ch}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin:0}
.stats div{background:var(--card);padding:10px 12px}
.stats dt{font-size:11px;color:var(--muted)}
.stats dd{margin:2px 0 0;font-weight:700;font-variant-numeric:tabular-nums}
.pick-body{display:grid;grid-template-columns:1fr 1fr;gap:28px}
.layers{list-style:none;margin:0;padding:0;display:grid;gap:0;border-top:1px solid var(--line)}
.layers>li{display:grid;grid-template-columns:150px 1fr;gap:6px 18px;padding:14px 0;border-bottom:1px solid var(--line)}
.layers>li>h4{grid-row:span 4;padding-top:3px}
.layers>li>*:not(h4){grid-column:2}
.memo summary{cursor:pointer;font-size:13px;color:var(--green);font-weight:600}
.memo[open] summary{margin-bottom:16px}
@media (max-width:640px){.layers>li{grid-template-columns:1fr}.layers>li>*:not(h4){grid-column:1}.layers>li>h4{grid-row:auto}}
.pick-body section{display:grid;gap:10px;align-content:start}
.pick-body p,.pick-body li{font-size:14px}
.pick-body ul{margin:0;padding-left:18px;display:grid;gap:4px}
.against p,.against li{color:var(--muted)}
.events{display:grid;gap:6px;padding:10px 12px;background:var(--red-soft)}
.events h4{color:var(--red)} .events li{color:var(--ink)}
.sources{font-size:12px} .sources li{font-size:12px}
.dims{display:grid;gap:6px;margin-top:6px}
.dim{display:grid;grid-template-columns:150px 1fr 48px;gap:10px;align-items:center;font-size:12px;color:var(--muted)}
.track{height:6px;background:var(--line)} .track span{display:block;height:100%;background:var(--green)}
.num{text-align:right;font-variant-numeric:tabular-nums;color:var(--ink)}
.table-wrap{overflow-x:auto;border:1px solid var(--line);background:var(--card)}
table{width:100%;border-collapse:collapse;font-size:13px;font-variant-numeric:tabular-nums}
th,td{padding:10px 12px;text-align:left;border-top:1px solid var(--line);white-space:nowrap}
thead th{border-top:0;font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
td.n,th.n{text-align:right}
tr.is-top td{background:var(--green-soft)}
td.tk{font-family:var(--mono);font-weight:700}
.order{border:1px solid var(--line);padding:10px 12px;margin:10px 0;background:var(--card)}.order p{margin:4px 0}.order-cell{font-weight:600;font-size:12px}
.recheck{border-left:3px solid var(--amber);padding-left:10px;margin:6px 0}.recheck li{font-size:13px}
.tailwind-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px;align-items:start}
.tailwind-fig{margin:0}.tailwind-fig figcaption{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:700;margin-bottom:8px}
.tailwind-chart{width:100%;height:auto;display:block}.tailwind-chart .fill{fill:var(--green)}.tailwind-chart .partial .fill{fill:var(--green);opacity:.45}
.tailwind-chart .hit{fill:transparent}.tailwind-chart .bar:hover .fill{opacity:.8}.tailwind-chart .val{fill:var(--ink);font:600 12px var(--sans)}
.tailwind-chart .tick{fill:var(--muted);font:11px var(--sans)}.tailwind-chart .axis-line{stroke:var(--line);stroke-width:1}
.pays li{margin-bottom:6px}
.quote{font-family:var(--serif);font-size:13px;color:var(--muted);font-style:italic}
.muted-note{color:var(--muted);font-size:12px;font-family:var(--sans);font-weight:400}
.pipeline{list-style:none;padding:0;margin:16px 0;display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}
.pipeline li{display:flex;gap:10px;align-items:flex-start;border-top:2px solid var(--green);padding-top:10px}
.pipeline .pnum{font:500 22px var(--serif);color:var(--green);line-height:1}
.pipeline p{margin:4px 0 0;font-size:13px;line-height:1.45;color:var(--muted)}
.long-term{margin-top:18px} .long-term td{white-space:normal;vertical-align:top;font-size:13px;line-height:1.45} .long-term caption{text-align:left;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:700;padding-bottom:8px}
.funnel{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:1px;background:var(--line);border:1px solid var(--line)}
.funnel div{background:var(--card);padding:16px;display:grid;gap:4px}
.funnel strong{font:500 30px/1 var(--serif);font-variant-numeric:tabular-nums}
.funnel span{font-size:12px;color:var(--muted)}
.method{display:grid;grid-template-columns:1fr 1fr;gap:28px}
.method section{display:grid;gap:10px;align-content:start}
.method ul{margin:0;padding-left:18px;display:grid;gap:6px;font-size:14px;color:var(--muted)}
.method li strong{color:var(--ink)}
footer{font-size:12px;color:var(--muted);border-top:1px solid var(--line);padding-top:18px;max-width:80ch}
@media (max-width:860px){
  .answer{grid-template-columns:1fr}
  .map-wrap,.pick-body,.method{grid-template-columns:1fr}
  .funnel{grid-template-columns:repeat(auto-fit,minmax(110px,1fr))}
}
@media (max-width:520px){
  .pick{padding:18px} .pick-head{grid-template-columns:auto 1fr} .scores{grid-column:1/-1;justify-content:flex-start;text-align:left}
  .dim{grid-template-columns:110px 1fr 44px}
}
"""


def radar_week(root: Path, signals: dict, days: int = 7) -> str:
    """Every topic that jumped in the last `days` days of daily radar runs, with its dates and status."""
    from datetime import date as _date, timedelta as _td

    history = load(root / "state/emerging-signals-history.json", [])
    if not history:
        return ""
    end = _date.fromisoformat((signals.get("asOf") or max(r["date"] for r in history))[:10])
    start = end - _td(days=days - 1)
    runs = [r for r in history if start.isoformat() <= r["date"] <= end.isoformat()]
    confirmed = {c["topic"]: c for c in signals.get("confirmedTopics", [])}
    topics: dict[str, dict] = {}
    for run in sorted(runs, key=lambda r: r["date"]):
        for sig in run.get("signals", []):
            t = topics.setdefault(sig["label"], {"dates": [], "peak": 0, "headline": ""})
            t["dates"].append(run["date"])
            t["peak"] = max(t["peak"], sig.get("recent") or 0)
            head = sig.get("headline")
            head = head.get("title") if isinstance(head, dict) else head
            t["headline"] = head or t["headline"]
    if not topics:
        return f'<p class="empty">No topic jumped between {esc(start.isoformat())} and {esc(end.isoformat())}.</p>'
    rows = ""
    for label, t in sorted(topics.items(), key=lambda kv: (-len(kv[1]["dates"]), kv[1]["dates"][0])):
        if label in confirmed:
            state = f'<span class="chip ok">Confirmed {esc(confirmed[label].get("confirmed", "")[5:])}</span>'
        elif len(t["dates"]) > 1:
            state = '<span class="chip warn">Several days</span>'
        else:
            state = '<span class="chip plain">One day</span>'
        rows += (f'<tr><td><strong>{esc(label)}</strong></td><td>{state}</td><td class="n">{len(t["dates"])}</td>'
                 f'<td>{esc(", ".join(d[5:] for d in t["dates"]))}</td><td class="n">{t["peak"]}</td>'
                 f'<td style="white-space:normal">{esc((t["headline"] or "")[:110])}</td></tr>')
    covered = len(runs)
    n_conf = sum(1 for label in topics if label in confirmed)
    note = (f" The radar history starts on {esc(history[0]['date'])}, so this covers {covered} daily run{'s' if covered != 1 else ''} so far."
            if covered < days else "")
    return (f'<h3 style="font-size:20px">Last {days} days</h3>'
            f'<p>{len(topics)} topic{"s" if len(topics) != 1 else ""} jumped between {esc(start.isoformat())} and {esc(end.isoformat())}, '
            f'{n_conf} confirmed.{note}</p>'
            '<div class="table-wrap"><table><thead><tr><th>Topic</th><th>Status</th><th class="n">Days jumped</th><th>Dates</th>'
            f'<th class="n">Peak articles (3 days)</th><th>Example headline</th></tr></thead><tbody>{rows}</tbody></table></div>')


def radar_section(root: Path = ROOT) -> tuple[str, str]:
    """The "next theme" block: replays first (the evidence), then today's radar. Returns (html, extra css)."""
    try:
        import build_radar_page as radar  # imported here: build_radar_page imports this module
    except ImportError:
        return "", ""
    signals = radar.load(root / "state/emerging-signals.json", {"signals": []})
    mapping = radar.load(root / "state/beneficiary-map.json", {"topics": []})
    pricing = radar.load(root / "state/pricing-check.json", {"results": []})
    cases = [radar.load(path, None) for path in sorted((root / "state/replay").glob("*.json"))]
    cases = sorted([c for c in cases if c and "case" in c], key=lambda c: (c.get("detection") is None, c["case"]))
    if not cases and not signals.get("signals"):
        return "", ""
    confirmed = sum(1 for s in signals.get("signals", []) if s.get("confirmed"))
    jumping = len(signals.get("signals", []))
    today = (
        radar.signals_table(signals["signals"][:5]) if signals.get("signals") else '<p class="empty">No topic is jumping today.</p>'
    )
    html = f"""
  <section class="section" id="radar" aria-labelledby="radar-h">
    <h2 id="radar-h">Spotting the next theme early</h2>
    <p>The six picks answer who leads today. The agent also watches health news, WHO and preprint servers for topics that suddenly gain attention, with no preset themes, then finds the listed companies involved through SEC filings and trial registrations and checks whether their stocks have already reacted. It uses no language model, so it can be replayed on past dates without knowing what happened next.</p>
    <h3 style="font-size:20px">Time-machine test</h3>
    {''.join(radar.replay_card(c) for c in cases) or '<p class="empty">No replay has been run yet.</p>'}
    <h3 style="font-size:20px">Today</h3>
    <p>{jumping} topic{'s' if jumping != 1 else ''} jumping, {confirmed} confirmed. A topic is confirmed when it jumps on two days within a week with new articles; only confirmed topics are mapped to companies. The radar covers every field, so non-medical news can appear here.</p>
    {today}
    {radar_week(root, signals)}
    {radar.candidates_block(mapping, pricing)}
  </section>
"""
    return html, radar.EXTRA_STYLE


def fda_block(root: Path) -> str:
    """Latest FDA AI/software device decisions from openFDA, mapped to listed companies where possible."""
    feed = load(root / "state/fda-device-events.json", {})
    events = [e for e in feed.get("events", []) if e.get("aiConfidence") == "high"][:12]
    if not events:
        return ""
    possible = sum(1 for e in feed.get("events", []) if e.get("aiConfidence") == "possible")

    def who(e):
        if not e.get("ticker"):
            return '<span class="muted-note">private or unlisted</span>'
        if e.get("newCandidate"):
            return f'<strong>{esc(e["ticker"])}</strong> <span class="chip warn">listed, not covered yet</span>'
        return f'<strong>{esc(e["ticker"])}</strong> <span class="chip ok">covered</span>'
    rows = "".join(
        f'<tr><td class="n">{esc(e["decisionDate"])}</td><td>{esc(e["label"])}</td>'
        f'<td style="white-space:normal"><a href="{esc(e["url"])}" target="_blank" rel="noopener">{esc(e["device"])}</a></td>'
        f'<td style="white-space:normal">{esc(e["applicant"])}</td><td>{who(e)}</td></tr>' for e in events)
    window = feed.get("window", {})
    return (f'<h3 class="bucket-h">Primary source: FDA AI device decisions</h3>'
            f'<p class="bucket-blurb">openFDA records of 510(k) clearances, De Novo grants and PMA approvals, {esc(window.get("start", ""))} to {esc(window.get("end", ""))}: '
            f'{feed.get("decisionsScanned", 0)} decisions scanned, {len([e for e in feed.get("events", []) if e.get("aiConfidence") == "high"])} clearly AI or software '
            f'(on FDA\'s AI-enabled list or named as such), {possible} more possible from product code only. Latest decision in the feed: {esc(feed.get("latestDecisionInFeed") or "—")}; '
            'openFDA trails FDA by one to two weeks. A decision by a covered company becomes an official regulatory event for Serenity; a listed company we do not cover yet is flagged for the screen.</p>'
            f'<div class="table-wrap"><table><thead><tr><th class="n">Decided</th><th>Decision</th><th>Device</th><th>Applicant</th><th>Listed company</th></tr></thead><tbody>{rows}</tbody></table></div>')


PAYMENT_QUOTES = [  # (ticker, gate, quote fragment) from citation-checked reviews
    ("HTFL", "chokepoint_evidence", "Category I CPT code"),
    ("HTFL", "chokepoint_evidence", "99% of covered lives"),
    ("CBLL", "customer_dependency", "New Technology Add-on Payment"),
    ("NTRA", "chokepoint_evidence", "Advanced Diagnostic Laboratory Test"),
]
SPECIALTY_PICKS = {"Radiology": "RDNT, GEHC", "Cardiovascular": "HTFL (pick)", "Neurology": "CBLL (pick)"}


def fda_by_year(fda: dict) -> tuple[list[tuple[str, int]], str]:
    from collections import Counter
    years = Counter(d["decisionDate"][-4:] for d in fda.get("devices", []) if d.get("decisionDate"))
    latest = (fda.get("summary") or {}).get("latestDecisionDate", "")
    rows = [(y, years[y]) for y in sorted(years) if y >= "2015"]
    return rows, latest


def tailwind_section(root: Path) -> str:
    """Sector case for 5-10 years from primary data: FDA AI authorisations by year and specialty, and who pays."""
    fda = load(root / "state/fda-ai-devices.json", {})
    rows, latest = fda_by_year(fda)
    if not rows:
        return ""
    partial_year = latest[-4:] if latest else ""
    w, h, left, bottom, top = 640, 260, 36, 28, 18
    peak = max(n for _, n in rows)
    step = (w - left - 8) / len(rows)
    bars = []
    for i, (year, n) in enumerate(rows):
        x = left + i * step + step * 0.18
        bw = step * 0.64
        bh = (h - top - bottom) * n / peak
        y = h - bottom - bh
        partial = year == partial_year
        label = f"{year}: {n} AI-enabled devices authorised" + (f" (to {latest}, list updated periodically)" if partial else "")
        bars.append(f'<g class="bar{" partial" if partial else ""}"><title>{esc(label)}</title>'
                    f'<rect x="{left + i * step:.1f}" y="{top}" width="{step:.1f}" height="{h - top - bottom}" class="hit"/>'
                    f'<path d="M{x:.1f},{h - bottom} V{y + 4:.1f} Q{x:.1f},{y:.1f} {x + 4:.1f},{y:.1f} H{x + bw - 4:.1f} Q{x + bw:.1f},{y:.1f} {x + bw:.1f},{y + 4:.1f} V{h - bottom}Z" class="fill"/>')
        if year in {rows[0][0], "2020", "2025", partial_year}:
            bars.append(f'<text x="{x + bw / 2:.1f}" y="{y - 6:.1f}" text-anchor="middle" class="val">{n}{"*" if partial else ""}</text>')
        bars.append(f'<text x="{x + bw / 2:.1f}" y="{h - 10}" text-anchor="middle" class="tick">{"’" + year[2:]}</text>')
        bars.append("</g>")
    svg = (f'<svg viewBox="0 0 {w} {h}" class="tailwind-chart" role="img" aria-label="FDA AI-enabled device authorisations per year, {rows[0][0]} to {rows[-1][0]}">'
           f'<line x1="{left}" x2="{w - 8}" y1="{h - bottom}" y2="{h - bottom}" class="axis-line"/>{"".join(bars)}</svg>')
    devices = fda.get("devices", [])
    def count(panel, recent):
        return sum(1 for d in devices if d.get("panel") == panel and (d.get("decisionDate", "")[-4:] >= "2023") == recent)
    spec_rows = "".join(
        f'<tr><td>{esc(panel)}</td><td class="n">{count(panel, False)}</td><td class="n"><strong>{count(panel, True)}</strong></td><td class="tk">{esc(picks)}</td></tr>'
        for panel, picks in SPECIALTY_PICKS.items())
    assessments = {a["ticker"]: a for a in load(root / "state/serenity-auto-assessments.json", {}).get("companies", [])}
    pays = []
    for ticker, gate, fragment in PAYMENT_QUOTES:
        refs = [q for side in ("support", "counter") for q in assessments.get(ticker, {}).get("gate_reviews", {}).get(gate, {}).get(side, [])]
        hit = next((q for q in refs if fragment in q["quote"]), None)
        if hit:
            pays.append(f'<li><strong>{esc(ticker)}</strong> <span class="quote">“{esc(hit["quote"])}”</span> '
                        f'<a href="{esc(hit["url"])}" target="_blank" rel="noopener" class="muted-note">filing</a></li>')
    first, last_full = rows[0], next((r for r in reversed(rows) if r[0] != partial_year), rows[-1])
    return f"""
  <section class="section" id="tailwind" aria-labelledby="tailwind-h">
    <h2 id="tailwind-h">Why AI medicine grows by 2035</h2>
    <p>The track itself has to grow for any company in it to matter in ten years. Two primary-source facts say it is growing, and say where. FDA authorised {first[1]} AI-enabled devices in {first[0]} and {last_full[1]} in {last_full[0]}. And Medicare and insurers have started paying for specific AI-based tests, which is what turns a clearance into revenue.</p>
    <div class="tailwind-grid">
      <figure class="tailwind-fig"><figcaption>FDA AI-enabled device authorisations per year</figcaption>{svg}
        <p class="note">Source: FDA list of AI-enabled medical devices ({fda.get("summary", {}).get("totalDevices", 0):,} devices). *{esc(partial_year)} runs to {esc(latest)}; FDA updates the list periodically and says it is not comprehensive.</p></figure>
      <div>
        <h3 class="bucket-h">Where the growth is</h3>
        <div class="table-wrap"><table><thead><tr><th>Specialty</th><th class="n">Before 2023</th><th class="n">2023 onward</th><th>Reviewed companies exposed</th></tr></thead><tbody>{spec_rows}</tbody></table></div>
        <p class="note">Neurology authorisations since 2023 already exceed every earlier year combined; radiology remains the largest market. The durable picks (Caris, Intuitive, Tempus) sit in molecular testing and robotics, which this device list covers only in part.</p>
      </div>
    </div>
    <h3 class="bucket-h">Who pays: payment pathways quoted from the picks' filings</h3>
    <ul class="plain-list pays">{"".join(pays)}</ul>
    <p class="note">A clearance lets a product be sold; a billing code or add-on payment lets it be paid for. HeartFlow and Ceribell, which lead the asymmetric-upside group, both already hold one; that is a large part of why they rank first and second.</p>
  </section>"""


RELATION_WORD = {"own-product": "own", "supplier": "supplier", "customer": "customer", "mention": "mention"}
GATE_NAMES = {"chokepoint_evidence": "Chokepoint", "pure_play": "AI purity", "counter_thesis": "Counter-thesis",
              "supply_chain_map": "Supply chain", "customer_dependency": "Customers", "multi_node_control": "Multi-node control",
              "earnings_validation": "Earnings", "management_governance": "Governance"}


def recheck_block(root: Path) -> str:
    """Event -> gates reopened -> before/after, with the primary-document quotes that decided it."""
    trace = [r for r in load(root / "state/event-rechecks.json", {}).get("rechecks", []) if r.get("status") == "re-checked"]
    if not trace:
        return ""
    chip = lambda st: f'<span class="chip {"ok" if st == "pass" else "warn" if st == "partial" else "plain"}">{esc(st)}</span>'
    items = []
    for r in sorted(trace, key=lambda x: x.get("recheckedAt", ""), reverse=True):
        e = r["event"]
        gates = "".join(
            f'<li><strong>{esc(GATE_NAMES.get(g, g))}</strong>: {chip(r["before"][g])} → {chip(r["after"][g])}'
            + (' <span class="muted-note">changed</span>' if g in r.get("changed", {}) else ' <span class="muted-note">unchanged</span>')
            + "".join(f'<br><span class="quote">“{esc(q)}”</span>' for q in r.get("quotes", {}).get(g, [])[:2]) + "</li>"
            for g in r["gatesReopened"])
        tier = r.get("tierAfter") or r.get("tierBefore") or "—"
        items.append(
            f'<article class="call"><header class="call-head"><h3><span class="ticker">{esc(r["ticker"])}</span> FDA {esc(e.get("label") or "")} '
            f'<a href="{esc(e.get("url") or "")}" target="_blank" rel="noopener">{esc(r["eventId"])}</a></h3>'
            f'<span class="chip plain">{esc(e.get("decisionDate") or "")}</span></header>'
            f'<p class="call-foot">{esc(e.get("device") or "")}</p>'
            f'<div class="call-step"><h4>1 · Gates the event reopened, before → after (quotes from the FDA record and summary, matched word for word)</h4><ul class="plain-list">{gates}</ul></div>'
            f'<div class="call-step"><h4>2 · What it means</h4><p class="call-verdict">{esc(r.get("reviewerNote", ""))}</p>'
            f'<p class="call-foot">Serenity tier after the re-check: <strong>{esc(tier)}</strong></p></div></article>')
    return ('<h3 class="bucket-h">From event to Serenity re-check</h3>'
            '<p class="bucket-blurb">An FDA decision never changes a rating by itself. It reopens the gates it bears on; the re-check reads the FDA record and '
            'summary, and every quote is matched word for word before the gate can move. Both examples below looked like good news in a headline. '
            'Other news about a reviewed company works the same way: it queues a re-check of the gates it bears on, shown on each card further down.</p>'
            f'<div class="calls">{"".join(items)}</div>')


def early_signals_section(root: Path) -> str:
    """Money and people: Form D private raises in health/biotech, insider open-market buys and key departures."""
    data = load(root / "state/early-signals.json", {})
    radar, people = data.get("fundingRadar") or {}, data.get("people") or {}
    if not radar.get("companies") and not people:
        return ""
    money = lambda v: (f"${v / 1e6:,.1f}M" if v and v >= 1e6 else f"${v / 1e3:,.0f}K" if v else "—")
    private = [c for c in radar.get("companies", []) if not c.get("listedTicker")]
    rows = ""
    for c in private[:10]:
        flags = []
        if c.get("aiName"):
            flags.append('<span class="chip ok">AI in name</span>')
        if c.get("newsMentions"):
            flags.append(f'<span class="chip warn">in frontier news ×{c["newsMentions"]}</span>')
        if c.get("young"):
            flags.append('<span class="chip plain">founded ≤5 yrs</span>')
        execs = ", ".join(p["name"] for p in c.get("people", [])[:2]) or "—"
        rows += (f'<tr><td><a href="{esc(c["url"])}" target="_blank" rel="noopener"><strong>{esc(c["name"])}</strong></a><br><span class="muted-note">{esc(c.get("location") or "")}</span></td>'
                 f'<td>{esc(c.get("industry") or "")}</td><td class="n">{money(c.get("sold"))}</td><td class="n">{esc(c.get("firstSale") or "—")}</td>'
                 f'<td style="white-space:normal">{esc(execs)}</td><td>{" ".join(flags) or "—"}</td></tr>')
    window = radar.get("window", {})
    in_news = sum(1 for c in private if c.get("newsMentions"))
    funding = (f'<h3 class="bucket-h">Who is raising money: SEC Form D</h3>'
               f'<p class="bucket-blurb">A private company selling shares under Reg D must file Form D within 15 days of the first sale, naming its industry, the amount raised and its executives. '
               f'{radar.get("filings", 0)} new filings from biotech, pharmaceutical and health-care companies between {esc(window.get("start", ""))} and {esc(window.get("end", ""))}, '
               f'{money(radar.get("raisedTotal"))} sold in total. '
               + ("None of these private companies appears by full name in the frontier-news stores, so they are found here before any news covers them. " if not in_news
                  else f"{in_news} of these private companies appear by full name in the frontier-news stores; the rest are found here before any news covers them. ")
               + 'Private companies cannot be bought today; they are a watch list for future listings, deals and partners of covered companies.</p>'
               '<div class="table-wrap"><table><thead><tr><th>Company</th><th>Industry</th><th class="n">Raised</th><th class="n">First sale</th><th>Executives named</th><th>Flags</th></tr></thead>'
               f'<tbody>{rows}</tbody></table></div>') if rows else ""
    trades = people.get("insiderTrades", {})
    buy_rows = "".join(
        f'<tr><td class="tk">{esc(t)}</td><td>{esc(b.get("owner") or "")}</td><td>{esc(", ".join(r for r in b.get("roles", []) if r != "Officer") or "Officer")}</td>'
        f'<td class="n">{esc(b.get("date") or "")}</td><td class="n">{money(b.get("value"))}</td></tr>'
        for t, v in trades.items() for b in v.get("buys", []))
    sells = ", ".join(f'{esc(t)} {v["sellCount"]} ({money(v["sellValue"])})' for t, v in sorted(trades.items(), key=lambda kv: -kv[1].get("sellValue", 0)) if v.get("sellCount"))
    dep_rows = "".join(f'<tr><td>{esc(d["company"])}</td><td class="n">{esc(d["date"])}</td><td style="white-space:normal"><a href="{esc(d["url"])}" target="_blank" rel="noopener">“{esc(d["sentence"][:220])}”</a></td></tr>'
                       for d in people.get("keyDepartures", []))
    people_html = ('<h3 class="bucket-h">What insiders are doing</h3>'
                   f'<p class="bucket-blurb">Covered companies since {esc(people.get("since", ""))}. Open-market buying (Form 4, code P) is shown as context, not as a buy signal: in 1,561 purchases at 445 health-care companies (2018 to mid-2025), stocks did no better than the same companies bought at a random month start (12-month median excess vs XBI -21.6% against -21.4%); only buying by 10% holders, usually funds, did somewhat better (170 cases, borderline significance). See outputs/insider-buy-study.md. '
                   'sales are common (tax, diversification, pre-set plans) and are listed only as counts. A CEO, CFO, CSO, president or founder leaving (8-K Item 5.02) is a negative signal. '
                   'Both are written to the news store as official SEC events; a key departure at a reviewed company also queues a re-check of its governance gate.</p>'
                   + ('<div class="table-wrap"><table><thead><tr><th>Ticker</th><th>Buyer</th><th>Role</th><th class="n">Date</th><th class="n">Bought</th></tr></thead>'
                      f'<tbody>{buy_rows}</tbody></table></div>' if buy_rows else '<p class="empty">No open-market insider buying in the window.</p>')
                   + (f'<p class="note"><span>Open-market sales in the window:</span> {sells}.</p>' if sells else "")
                   + ('<div class="table-wrap"><table><thead><tr><th>Company</th><th class="n">Filed</th><th>Key departure (8-K Item 5.02, quoted)</th></tr></thead>'
                      f'<tbody>{dep_rows}</tbody></table></div>' if dep_rows else ""))
    return f"""
  <section class="section" id="early" aria-labelledby="early-h">
    <h2 id="early-h">Earlier signals: money and people</h2>
    <p>Before a company makes the news, money moves and people move. New companies raise private rounds; insiders buy or leave. Both are on the public record at the SEC.</p>
    {funding}
    {people_html}
  </section>"""


def management_radar_section(root: Path) -> str:
    """A compact people/governance view from SEC 8-K and Form 4 evidence."""
    data = load(root / "state/management-radar.json", {})
    companies = [row for row in data.get("companies", []) if row.get("timeline")]
    if not companies:
        return ""
    labels = {"urgent-revalidate": "Urgent re-check", "revalidate": "Re-check", "monitor": "Monitor"}
    chips = {"urgent-revalidate": "alert", "revalidate": "warn", "monitor": "plain"}
    rows = ""
    for company in companies[:12]:
        latest = company["timeline"][0]
        summary = company["summary"]
        rows += (
            f'<tr><td><span class="chip {chips[company["attention"]]}">{labels[company["attention"]]}</span></td>'
            f'<td class="tk">{esc(company["ticker"])}</td><td class="n">{summary["people"]}</td>'
            f'<td class="n">{summary["purchases"]}</td><td class="n">{summary["salesNeedingContext"]}</td>'
            f'<td style="white-space:normal">{esc(latest.get("date") or "—")} · {esc(latest.get("title") or "")}</td>'
            f'<td>{esc(", ".join(company.get("affectedGates", [])) or "—")}</td></tr>'
        )
    summary = data.get("summary", {})
    return f"""
  <section class="section" id="management" aria-labelledby="management-h">
    <h2 id="management-h">Management and key-person radar</h2>
    <p>The agent joins SEC 8-K officer changes with Form 4 transactions into a named timeline. A CEO, CSO, CMO or founder departure, repeated departures, or a board investigation reopens Serenity governance and counter-thesis gates. An insider purchase is supporting evidence only; a sale stays context-needed until its 10b5-1 plan, tax purpose, ownership percentage and concentration are checked.</p>
    <p class="note">{summary.get("people", 0)} named filers; {summary.get("events", 0)} events; {summary.get("urgent", 0)} companies need an urgent re-check. These are research alerts, not price predictions.</p>
    <div class="table-wrap"><table><thead><tr><th>Status</th><th>Ticker</th><th class="n">People</th><th class="n">Buys</th><th class="n">Sales needing context</th><th>Latest event</th><th>Gates reopened</th></tr></thead><tbody>{rows}</tbody></table></div>
  </section>"""


ACTION_WORD = {"buy": "Buy", "starter": "Starter", "wait": "Wait", "avoid": "Avoid"}
ACTION_CHIP = {"buy": "ok", "starter": "warn", "wait": "plain", "avoid": "alert"}


def tickets_section(root: Path) -> str:
    """Order tickets from scripts/order_tickets.py: action, limit, size, scale plan, invalidation."""
    data = load(root / "state/order-tickets.json", {})
    tickets = data.get("tickets") or []
    if not tickets:
        return ""
    money = lambda v: f"${v:,.2f}" if v else "—"
    rows = ""
    for x in tickets:
        size = f"{x['positionPct']:.1%}" + (f" (now {x['buyNowPct']:.1%})" if x["buyNowPct"] != x["positionPct"] else "") if x["positionPct"] else "—"
        rows += (f'<tr><td><span class="chip {ACTION_CHIP[x["action"]]}">{ACTION_WORD[x["action"]]}</span></td><td class="tk">{esc(x["ticker"])}</td>'
                 f'<td class="n">{money(x["price"])}</td><td class="n">{money(x["limitPrice"])}</td><td class="n">{money(x["safetyFloor"])}</td>'
                 f'<td class="n">{size}</td><td style="white-space:normal">{esc("; ".join(x["reasons"]))}</td></tr>')
    details = ""
    for x in tickets:
        if x["action"] not in ("buy", "starter"):
            continue
        items = [f"<li><strong>Size:</strong> {x['positionPct']:.1%} of the portfolio (Serenity tier: {esc(x['serenityTier'])})"
                 + (f"; {esc('; '.join(x['sizeAdjustments']))}" if x["sizeAdjustments"] else "") + "</li>",
                 f"<li><strong>Add:</strong> {esc(x['scalePlan'])}</li>"]
        if x.get("trimRule"):
            items.append(f"<li><strong>Trim:</strong> {esc(x['trimRule'])}</li>")
        if x.get("adversarial") and x["adversarial"].get("overall"):
            dg = x["adversarial"].get("downgrades") or []
            head = (f"no gate fails; {len(dg)} pass grade(s) overstated ({', '.join(dg)})" if dg else "no gate fails")
            items.append(f"<li><strong>Second review ({esc(x['adversarial'].get('model') or 'opus')}, arguing against):</strong> "
                         f"{esc(head)}. {esc(x['adversarial']['overall'])}</li>")
        if x.get("flipPoints"):
            items.append("<li><strong>Flips if:</strong> " + esc("; ".join(x["flipPoints"])) + "</li>")
        if x.get("invalidation"):
            items.append("<li><strong>Wrong if:</strong> " + esc("; ".join(x["invalidation"][:4])) + "</li>")
        details += f'<div class="ticket"><h3 class="bucket-h">{esc(x["ticker"])} · {ACTION_WORD[x["action"]]}</h3><ul>{"".join(items)}</ul></div>'
    t = data.get("totals", {})
    return f"""
  <section class="section" id="tickets" aria-labelledby="tickets-h">
    <h2 id="tickets-h">Order tickets</h2>
    <p>Each company gets the same rules. The action comes from the Serenity verdict and where the price sits against the order range. Size starts from the Serenity tier (starter 1%, standard 5%, at most 10% per name) and is cut for a recent -20% day, thin trading, under 12 months of cash, or a market value under $1B. Positions are added only after earnings, a customer or a deal confirms the thesis, never because the price rose; there are no tight stops, a broken thesis is the exit. A ticket also waits after an FDA rejection letter in the last 12 months that asks for a new trial: in 114 letters to listed companies (2012-2026), those stocks lagged XBI by a median 20 points over the next year, while letters asking for label or manufacturing fixes barely moved them.</p>
    <p class="note"><span>Today:</span> target {t.get('positionPct', 0):.1%} of a ${data.get('portfolioUsd', 0):,.0f} portfolio. Research suggestions for paper trading only; a person approves every ticket, and none of these sizing rules has been backtested yet.</p>
    <div class="table-wrap"><table><thead><tr><th>Action</th><th>Ticker</th><th class="n">Price</th><th class="n">Limit</th><th class="n">Safety floor</th><th class="n">Size</th><th>Why</th></tr></thead>
    <tbody>{rows}</tbody></table></div>
    {details}
  </section>"""


STAGE_WORD = {"growth": "Growth", "preparation": "Preparation", "slowing": "Slowing"}


def rnpv_cell(r: dict | None, money) -> str:
    if not r:
        return "—"
    o = r["orderRange"]
    implied = f'<span class="muted-note">price implies {money(r["impliedPeakSalesM"])} peak sales (phase {r["phase"]})</span>'
    import rnpv_valuation as rv
    line = rv.implied_share_text(r)
    if line:
        implied += f'<br><span class="muted-note">{esc(line)} (patients quoted from its 10-K)</span>'
    if r.get("platform"):
        return f"platform: not used<br>{implied}"
    if not r.get("rangeUsable"):
        return f"cash nearly gone: not used until it raises money<br>{implied}"
    if not o["upper"]:
        return f"base case worth $0 a share: burn exceeds the risk-adjusted value<br>{implied}"
    state = {"in-range": "inside range", "below-floor": "below floor", "at-top": "at the top"}.get(o["status"], f"{o['gapToUpper']:+.0%} vs range")
    return f'≤ ${o["upper"]:.2f} · floor ${o["floor"]:.2f}<br><span class="muted-note">{state}</span><br>{implied}'


def small_caps_section(root: Path) -> str:
    """AI-medicine companies under $1B by stage (scripts/small_cap_stage.py), with their Serenity verdict."""
    data = load(root / "state/small-cap-stage.json", {})
    rows_data = data.get("companies") or []
    if not rows_data:
        return ""
    gates = {r["ticker"]: r for r in load(root / "state/serenity-gate-results.json", {}).get("companies", [])}
    rnpv = {r["ticker"]: r for r in load(root / "state/rnpv-valuations.json", {}).get("companies", [])}
    raises = load(root / "state/equity-raises.json", {}).get("companies", {})
    money = lambda v: "—" if v is None else (f"${v / 1000:.1f}B" if v >= 1000 else f"${v:,.0f}M" if v >= 10 else f"${v:.1f}M")
    rows = ""
    for r in rows_data:
        growth = r["quarterYoY"] if r.get("quarterYoY") is not None else r.get("fiscalYoY")
        runway = "cash positive" if r.get("burnPerMonthM") == 0 else (f"{r['runwayMonths']:.0f} mo" if r.get("runwayMonths") is not None else "—")
        if r.get("financingRisk"):
            runway = f'<span class="chip alert">{runway}</span>'
        got = (raises.get(r["ticker"]) or {}).get("totalUsdM") or 0
        if got >= 5 and r.get("marketCapM"):
            share = got / r["marketCapM"]
            note = f"raised {money(got)} in 24 mo ({share:.0%} of value)"
            runway += f'<br><span class="{"chip alert" if share >= 0.3 else "muted-note"}">{note}</span>'
        g = gates.get(r["ticker"], {})
        verdict = g.get("decision", "not reviewed")
        why = "; ".join(f'<a href="{esc(s["url"])}">{esc(s["text"])}</a>' for s in r.get("signals", [])) or "own AI product (market-wide screen)"
        rows += (f'<tr><td><span class="chip plain">{STAGE_WORD[r["stage"]]}</span><br><span class="muted-note">{esc(r["stageDetail"])}</span></td>'
                 f'<td class="tk">{esc(r["ticker"])}</td><td>{esc(r["company"])}<br><span class="muted-note">{why}</span></td><td class="n">{money(r["marketCapM"])}</td>'
                 f'<td class="n">{money(r.get("revenueRunRateM")) if r.get("revenueTagged") else "not tagged"}</td>'
                 f'<td class="n">{"—" if growth is None else f"{growth:+.0%}"}</td><td class="n">{runway}</td>'
                 f'<td>{esc(verdict)}<br><span class="muted-note">completeness {g.get("completenessScore", "—")}</span></td>'
                 f'<td>{rnpv_cell(rnpv.get(r["ticker"]), money)}</td></tr>')
    stages = data.get("byStage", {})
    return f"""
  <section class="section" id="smallcaps" aria-labelledby="smallcaps-h">
    <h2 id="smallcaps-h">Under $1B: preparation and growth</h2>
    <p>Earlier and smaller: companies worth $50M to $1B from two sources. The first is AI-medicine companies whose own filings describe their own AI product. The second is drug developers whose 8-K press releases in the last 90 days report an IND clearance or a new big-pharma deal; they are listed for that signal, not for AI. Every company is tagged by one rule. Preparation means under $10M of yearly revenue (a drug developer still in trials counts as preparation whatever its partner payments); growth means $10M+ growing at least 20% a year; the rest are slowing. Market value is SEC-reported shares times the latest close; runway is cash and short-term investments over operating cash burn, flagged under 12 months because a share sale is then likely. Below it: cash raised from selling shares in the last 24 months (SEC XBRL cash-flow statement), flagged when it reaches 30% of today's market value, because existing holders were diluted and more sales usually follow.</p>
    <p class="note"><span>Now:</span> {len(rows_data)} companies; {stages.get('growth', 0)} growth, {stages.get('preparation', 0)} preparation, {stages.get('slowing', 0)} slowing. Each was graded with the Serenity gates; none has enough primary evidence to be research-ready yet, so these are a research queue, not picks.</p>
    <div class="table-wrap"><table><thead><tr><th>Stage</th><th>Ticker</th><th>Company</th><th class="n">Market value</th><th class="n">Revenue (yearly)</th><th class="n">Growth</th><th class="n">Cash runway</th><th>Serenity</th><th>rNPV range</th></tr></thead>
    <tbody>{rows}</tbody></table></div>
    <p class="note"><span>rNPV range:</span> for drug developers with no sales to model. Approval odds and phase lengths come from the BIO/Informa/QLS 2011-2020 success-rate study; cash burn is charged only while the lead program is alive; discounted at the 12% policy return. Peak sales are unverified priors ($150M bear, $500M base, $1.5B bull), so the useful number is what today's price implies. Discovery platforms run many programs, so their one-asset value is shown but never used for an order.</p>
  </section>"""


def freshness_section(root: Path) -> str:
    """Red alert when a source the calls depend on is past its schedule; otherwise a one-line all-clear with the table."""
    data = load(root / "state/data-freshness.json", {})
    rows = data.get("sources") or []
    if not rows:
        return ""
    bad = [r for r in rows if r["status"] != "fresh"]

    def when(r):
        if r["status"] == "degraded":
            return f'updated {esc(r["asOf"])} but {r["errors"]} fetch errors'
        return f'last {esc(r["asOf"])}, {r["ageDays"]} days ago' if r["asOf"] else "no date found"

    table = "".join(
        f'<tr><td>{esc(r["label"])}</td><td>{esc(r["asOf"] or "—")}</td><td class="n">{"" if r["ageDays"] is None else r["ageDays"]}</td>'
        f'<td>{esc(r["cadence"])}</td><td>{CHIP[r["status"]]}</td><td>{esc(r["feeds"])}</td></tr>' for r in rows)
    details = ('<details class="fresh"><summary>Data freshness: ' + f'{data.get("fresh", 0)} of {len(rows)} sources on schedule (checked {esc(data.get("today", ""))})</summary>'
               '<div class="table-wrap"><table><thead><tr><th>Source</th><th>Last data</th><th class="n">Days old</th><th>Schedule</th><th>Status</th><th>Feeds</th></tr></thead>'
               f'<tbody>{table}</tbody></table></div></details>')
    run = data.get("run") or {}
    fails = run.get("softFailures") or []
    run_note = ""
    if str(run.get("state", "")).startswith("aborted"):
        run_note = (f'<p class="fresh-alert"><strong>The last daily run stopped early</strong> ({esc(run["state"])}, {esc(run.get("at", "")[:16])} UTC). '
                    "Sections it did not reach still show the previous run.</p>")
    elif fails:
        run_note = ('<p class="fresh">Steps that failed in the last run and kept their previous result: ' + "; ".join(esc(f) for f in fails) + ".</p>")
    critical = [r for r in bad if r["critical"]]
    if not critical:
        details = run_note + details
        note = ("" if not bad else '<p class="fresh">Behind schedule, not affecting the calls: '
                + "; ".join(f'{esc(r["label"])} ({when(r)})' for r in bad) + ".</p>")
        return note + details
    items = "; ".join(f'<strong>{esc(r["label"])}</strong> ({when(r)}; feeds {esc(r["feeds"])})' for r in critical)
    return run_note + (f'<p class="fresh-alert"><strong>Stale data.</strong> {items}. Treat the affected calls as out of date until the next run refreshes them.</p>'
            + details)


CHIP = {"fresh": '<span class="chip ok">on schedule</span>', "stale": '<span class="chip alert">stale</span>',
        "missing": '<span class="chip alert">missing</span>', "degraded": '<span class="chip warn">fetch errors</span>'}


def blind_test_section(root: Path) -> str:
    """Weekly blind test: this agent vs a plain web-search model vs a mechanical rule, frozen in advance."""
    path = root / "outputs/blind-test-ledger.jsonl"
    if not path.exists():
        return ""
    ledger = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not ledger:
        return ""
    result = load(root / "state/blind-test.json", {})
    week = max(r["week"] for r in ledger)
    latest = {r["group"]: {c["ticker"]: c for c in r["calls"]} for r in ledger if r["week"] == week}
    names = {"A": "This agent", "B": "Claude + web search", "C": "Cheapest price/sales"}
    universe = next(r["universe"] for r in ledger if r["week"] == week)
    extras = sorted({t for c in latest.get("B", {}).values() if c.get("extra") for t in [c["ticker"]]})

    def cell(group, t):
        c = latest.get(group, {}).get(t)
        if not c:
            return "—"
        label = esc(c["action"]) + (" (no ticket)" if c.get("noTicket") else "")
        return f'{label} <span class="r">{c["confidence"]:.0f}</span>' if c.get("confidence") is not None else label

    rows = "".join(f'<tr><td class="tk">{esc(t)}</td>' + "".join(f"<td>{cell(g, t)}</td>" for g in "ABC") + "</tr>" for t in universe)
    groups = result.get("groups", {})
    score_rows = ""
    for g in "ABC":
        r = groups.get(g)
        if not r:
            continue
        c = r["citations"]
        acc = f'{r["citationAccuracy"]:.0%}' if r["citationAccuracy"] is not None else "—"
        b20 = (r["basketExcess"] or {}).get("20")
        figs = f'{r["figuresOnPage"]:.0%}' if r.get("figuresOnPage") is not None else "—"
        score_rows += (f'<tr><td>{names[g]}</td><td class="n">{r["weeks"]}</td><td class="n">{acc}</td><td class="n">{figs}</td>'
                       f'<td class="n">{c["verified"]} / {c.get("numbers_only", 0)} / {c["not_found"]} / {c["fetch_failed"]}</td>'
                       f'<td class="n">{"—" if not b20 else format(b20["mean"], "+.1%")}</td><td class="n">{r["crashesHeld"]} / {r["crashes"]}</td></tr>')
    board = ('<div class="table-wrap"><table><thead><tr><th>Group</th><th class="n">Weeks</th><th class="n">Citations found word for word</th>'
             '<th class="n">Figures on the page</th><th class="n">Word for word / figures only / not found / page unreachable</th><th class="n">20-day excess vs XBI</th><th class="n">Crashes held / seen</th></tr></thead>'
             f'<tbody>{score_rows}</tbody></table></div>') if score_rows else ""
    return f"""<section class="bucket" id="blind">
  <h2>Blind test: this agent against asking a model directly</h2>
  <p class="bucket-blurb">A backtest cannot be blind for a language model, which has read what happened next, so this test only runs forward. Every week three groups give calls on the same deep-review list, frozen in an append-only file before prices move: this agent's order tickets; Claude Sonnet with web search and one standard prompt, without this project's data or rules; and a mechanical rule that buys the three cheapest names by price/sales. Each risk quote is opened at its source and searched for word for word; a quote that is reworded but whose figures all appear on the page counts as "figures only".</p>
  <p class="status-banner"><strong>{esc(result.get("verdict") or "Scoring starts after the first week.")}</strong> Criteria set before the first week: at 26 weeks this agent must beat the plain model on citation accuracy and on not holding names that fall 30% or more; at 52 weeks its confidence must rank 60-day returns (correlation above 0.05, t above 2). If not, this page will say it has not been shown to beat asking a model directly.</p>
  {board}
  <h3 class="bucket-h">Calls frozen for the week of {esc(week)} (action and confidence 0–100)</h3>
  <div class="table-wrap"><table><thead><tr><th>Ticker</th><th>{names["A"]}</th><th>{names["B"]}</th><th>{names["C"]}</th></tr></thead><tbody>{rows}</tbody></table></div>
  {f'<p class="note">The plain model also suggested, outside the list: <strong>{esc(", ".join(extras))}</strong></p>' if extras else ""}
</section>"""


def opinion_benchmark_section(root: Path) -> str:
    """Forward-only public commentator and specialist-fund comparison."""
    data = load(root / "state/opinion-benchmark.json", {})
    if not data:
        return ""
    profiles = {r["id"]: r for r in load(root / "trend-agent/opinion-leaders.json", {}).get("publicOpinion", [])}
    calls = data.get("calls", [])
    call_rows = "".join(
        f'<tr><td>{esc(c["evaluationStart"])}</td><td>{esc(profiles.get(c["leaderId"], {}).get("name", c["leaderId"]))}</td>'
        f'<td class="tk">{esc(c["ticker"])}</td><td>{esc(c["stance"])}</td><td class="n">{c["confidence"]:.0f}</td>'
        f'<td><a href="{esc(c["sourceUrl"])}">source</a></td></tr>' for c in calls[-30:])
    if not call_rows:
        call_rows = '<tr><td colspan="6">No ticker-specific view has been frozen yet. The test starts now and does not backfill old calls.</td></tr>'
    funds = data.get("fundSignals", [])
    fund_rows = "".join(
        f'<tr><td>{esc(r.get("filed") or "")}</td><td>{esc(r["fund"])}</td><td class="tk">{esc(r.get("ticker") or "")}</td>'
        f'<td>{esc(r.get("form") or "")}</td><td class="n">{"—" if r.get("percent") is None else format(r["percent"] / 100, ".1%")}</td>'
        f'<td>{"initial" if r.get("initial") else "amendment"}</td></tr>' for r in funds[:20])
    return f"""<section class="section" id="opinion-benchmark" aria-labelledby="opinion-h">
  <h2 id="opinion-h">Public biotech views vs Serenity</h2>
  <p>Brad Loncar is the industry radar, Adam Feuerstein the clinical skeptic, and Peter Kolchinsky/RA Capital the science, economics and policy view. A view enters the test only with a ticker, direction, original timestamp, exact quote and falsifier. Its return starts when this project first freezes it—not from an old article date. Baker Bros, RA Capital, Perceptive, RTW and Cormorant filings are shown separately as capital context, never as automatic recommendations.</p>
  <div class="table-wrap"><table><thead><tr><th>Freeze date</th><th>Source</th><th>Ticker</th><th>View</th><th class="n">Confidence</th><th>Original</th></tr></thead><tbody>{call_rows}</tbody></table></div>
  <h3 class="bucket-h">Selected specialist-fund ownership (Schedule 13D/13G)</h3>
  <div class="table-wrap"><table><thead><tr><th>Date</th><th>Fund</th><th>Ticker</th><th>Filing</th><th class="n">Stake</th><th>Type</th></tr></thead><tbody>{fund_rows or '<tr><td colspan="6">No matching filings.</td></tr>'}</tbody></table></div>
  <p class="note">Current sample: {len(calls)} frozen public calls and {len(funds)} matching fund filings. Performance appears only after 20/60/120/250 trading sessions; until then no source is described as more accurate.</p>
</section>"""


def early_candidates(root: Path, limit: int = 5) -> str:
    """Peter's under-$1B list: companies worth less than $1B that pass every hard check of the candidate filter and are not
    rejected, ranked by how much of the Serenity evidence is in. A separate list from the 5-10 year ranking above."""
    companies = load(root / "state/candidate-filter.json", {}).get("companies", {})
    rows = companies.values() if isinstance(companies, dict) else companies
    picks = sorted((c for c in rows if c.get("track") == "ai" and (c.get("marketCapM") or 1e9) < 1000 and c.get("serenity") != "reject"
                    and c.get("checks") and all(k["pass"] for k in c["checks"])), key=lambda c: -(c.get("completeness") or 0))[:limit]
    if not picks:
        return ""
    links = "".join(
        f'<a href="#smallcaps"><span class="r">#{i}</span><span class="t">{esc(c["ticker"])}</span><span class="c">{esc(c["company"])}</span>'
        f'<span class="s">{money(c["marketCapM"])} · AI product · evidence {c.get("completeness") or 0}%</span></a>'
        for i, c in enumerate(picks, 1))
    return (f'<div class="answer-group"><p class="answer-label">Under $1B · early AI candidates (passed the hard filter, ranked by evidence so far)</p>'
            f'<nav class="answer" aria-label="Under $1B early candidates">{links}</nav></div>')


def candidate_filter_section(root: Path) -> str:
    """Hard filter before deep review (scripts/candidate_filter.py): which watch-list names deserve research time."""
    data = load(root / "state/candidate-filter.json", {})
    cs = data.get("companies") or {}
    if not cs:
        return ""
    money = lambda v: "—" if not v else (f"${v / 1000:.1f}B" if v >= 1000 else f"${v:,.0f}M")
    q_rows = "".join(
        f'<tr><td class="tk">{esc(t)}</td><td>{esc(cs[t]["company"])}<br><span class="muted-note">{esc(cs[t]["segment"] or "")}</span></td>'
        f'<td class="n">{money(cs[t].get("marketCapM"))}</td><td style="white-space:normal">{esc(cs[t]["checks"][0]["detail"])}</td>'
        f'<td style="white-space:normal">{esc(cs[t]["checks"][1]["detail"])}</td><td class="n">{cs[t].get("completeness")}</td></tr>'
        for t in data.get("deepReview", []))
    out_rows = "".join(f'<tr><td class="tk">{esc(t)}</td><td style="white-space:normal">{esc(c["firstFailure"])}</td></tr>'
                       for t, c in sorted(cs.items()) if not c["pass"])
    s = data.get("summary", {})
    others = [t for t in data.get("eligible", []) if t not in data.get("deepReview", [])]
    return f"""
  <section class="section" id="filter" aria-labelledby="filter-h">
    <h2 id="filter-h">Deep-review queue</h2>
    <p>Every company with a Serenity gate review must pass five checks before more research time goes into it. AI must be the company's own product used for medical decisions, life-science research or clinical work: Claude reads the AI sentences of the latest annual report and its supporting quote must appear in the filing; a feature counts only with an FDA-cleared AI device. There must be hard evidence (an FDA-cleared AI device, $10M+ revenue, a pharma deal or IND, or a registered trial). The stock must be tradable ($50M+ market value, $0.5M+ a day) and survivable (6+ months of cash, price of $1+, shares sold in 24 months under 100% of market value). Drug developers listed for an IND or pharma deal skip the AI check. Of those that pass, companies up to $20B are ranked by Serenity evidence completeness and the top {len(data.get("deepReview", []))} form the queue; larger ones stay as benchmarks.</p>
    <p class="note"><span>Now:</span> {s.get("companies", 0)} reviewed, {s.get("passed", 0)} pass, {len(data.get("deepReview", []))} in the queue. Passed but outside the queue:</p>
    <p class="muted-note">{esc(", ".join(others)) or "—"}</p>
    <div class="table-wrap"><table><thead><tr><th>Ticker</th><th>Company</th><th class="n">Market value</th><th>AI check</th><th>Hard evidence</th><th class="n">Completeness</th></tr></thead><tbody>{q_rows}</tbody></table></div>
    <h3 class="bucket-h">Filtered out, with the first failed check</h3>
    <div class="table-wrap"><table><thead><tr><th>Ticker</th><th>Reason</th></tr></thead><tbody>{out_rows}</tbody></table></div>
  </section>"""


def inventor_block(root: Path) -> str:
    """Founders, scientists and paper authors who are named inventors on USPTO applications (scripts/inventor_chain.py)."""
    data = load(root / "state/inventor-chain.json", {})
    rows = [(t, r) for t, c in (data.get("companies") or {}).items() for r in c["people"] if r["companyPatents"] or r["licensorPatents"]]
    if not rows:
        return ""
    rows.sort(key=lambda x: (-x[1]["licensorPatents"], -x[1]["companyPatents"]))
    s = data.get("summary", {})
    body = "".join(
        f'<tr><td class="tk">{esc(t)}</td><td>{esc(r["person"])}</td><td>{esc(", ".join(r["roles"]))}</td>'
        f'<td class="n">{r["companyPatents"]}</td><td class="n">{r["licensorPatents"]}</td>'
        f'<td style="white-space:normal">{esc(", ".join(r["licensors"])) or "—"}</td>'
        f'<td style="white-space:normal">{esc((r["examples"][0]["title"] or "")[:70].capitalize()) if r["examples"] else "—"}</td></tr>'
        for t, r in rows)
    return (f'<h3 class="bucket-h">Inventors: from paper to patent to company</h3>'
            f'<p class="bucket-blurb">{s.get("peopleSearched", 0)} founders, scientists and frequent paper authors searched as inventors in the USPTO Open Data Portal. '
            "A person counts only when the application is filed by the company itself or by a university the company's 10-K names as its licensor; "
            "other applications under the same name may be someone else and are not counted. A licensor patent with a company founder as inventor is direct evidence "
            "that the technology came from that lab.</p>"
            '<div class="table-wrap"><table><thead><tr><th>Ticker</th><th>Person</th><th>Role</th><th class="n">Company applications</th>'
            f'<th class="n">Licensor applications</th><th>Licensor</th><th>Example</th></tr></thead><tbody>{body}</tbody></table></div>')


def patent_life_block(root: Path) -> str:
    """Patent life from USPTO file wrappers (scripts/patent_status.py)."""
    data = load(root / "state/patent-status.json", {})
    rows = data.get("companies") or {}
    if not rows:
        return ""
    order = sorted(rows, key=lambda t: (-(rows[t]["grantedTotal"] or 0)))
    def cnt(c, k):
        return ("" if c.get("complete", True) else "≥") + str(c[k])
    body = "".join(
        f'<tr><td class="tk">{esc(t)}</td><td class="n">{"" if c.get("complete", True) else "≈"}{c["grantedTotal"]:,}</td><td class="n">{cnt(c, "expireBy2031")}</td>'
        f'<td class="n">{cnt(c, "expireBy2036")}</td><td class="n">{esc(c["earliestLiveExpiry"] or "—")}</td><td class="n">{esc(c["medianExpiry"] or "—")}</td>'
        f'<td class="n">{"—" if c["terminalDisclaimerShare"] is None else format(c["terminalDisclaimerShare"], ".0%")}</td></tr>'
        for t in order for c in [rows[t]])
    return ('<h3 class="bucket-h">Patent life</h3>'
            '<p class="bucket-blurb">Granted US patents filed by each company (or its patent-holding subsidiary), from USPTO file wrappers. '
            "Expiry is estimated as 20 years from the effective filing date plus the term adjustment; a terminal disclaimer can make it earlier. "
            "Companies with more than 100 patents are sampled from both ends (50 oldest, 50 newest): their totals (≈) are estimated from the share of records that match the company, their expiry counts are minimums and no median is shown. Expiry is an estimate: term extensions and the exact priority chain are not resolved. "
            "This says how long protection lasts, not whether it covers the core product or would survive a challenge.</p>"
            '<div class="table-wrap"><table><thead><tr><th>Ticker</th><th class="n">Granted</th><th class="n">Expire by 2030</th><th class="n">Expire by 2035</th>'
            f'<th class="n">Earliest live expiry</th><th class="n">Median expiry</th><th class="n">Terminal disclaimers</th></tr></thead><tbody>{body}</tbody></table></div>')


def diagnostics_section(root: Path) -> str:
    """Unit economics of diagnostics companies (scripts/diagnostics_economics.py)."""
    data = load(root / "state/diagnostics-economics.json", {})
    rows = data.get("companies") or {}
    if not rows:
        return ""
    body = ""
    for t, c in rows.items():
        f = c.get("facts", {})
        pt = (c.get("perTest") or [None])[0]
        vol = f.get("volume", [])
        gm = f.get("grossMargin", [])
        payer = f.get("payer", [])
        vol_txt = f'{vol[0]["value"]:,.0f} · {esc(vol[0]["period"])}' if vol else "—"
        body += (f'<tr><td class="tk">{esc(t)}</td>'
                 f'<td style="white-space:normal">{vol_txt}</td>'
                 f'<td class="n">{"$" + format(pt["revenuePerTest"], ",") if pt else "—"}</td>'
                 f'<td style="white-space:normal">{(esc(str(gm[0]["value"])) + "% · " + esc(gm[0]["period"])) if gm else "—"}</td>'
                 f'<td style="white-space:normal">{esc(payer[0]["note"]) if payer else "—"}</td></tr>')
    return f"""
  <section class="section" id="diagnostics" aria-labelledby="diagnostics-h">
    <h2 id="diagnostics-h">Diagnostics: tests, price per test, margin, payers</h2>
    <p>A diagnostics company is worth what it earns per test times how many tests it runs, after what payers actually pay. These figures are quoted from each company's latest 10-K and 10-Q; every number kept was found word for word in the filing. Revenue per test is computed only when the test count and the testing revenue cover the same period and the same scope (the whole company or one named test line). Nothing here is graded; it is the input a diagnostics valuation needs.</p>
    <div class="table-wrap"><table><thead><tr><th>Ticker</th><th>Tests (period)</th><th class="n">Revenue per test</th><th>Gross margin</th><th>Payer fact</th></tr></thead><tbody>{body}</tbody></table></div>
  </section>"""


def people_activity_block(root: Path) -> str:
    """Conference talks and other public appearances (scripts/people_activity.py)."""
    data = load(root / "state/people-activity.json", {})
    rows = data.get("companies") or {}
    items = []
    for t, r in rows.items():
        items += [(x["date"] or "", t, x.get("person"), x["headline"], x["url"]) for x in r.get("peopleTalks", [])]
        items += [(x["date"] or "", t, None, x["headline"], x["url"]) for x in r.get("companyTalks", [])]
    if not items:
        return ""
    items.sort(reverse=True)
    lis = "".join(f'<li><span class="r">{esc(d)}</span> <strong>{esc(t)}</strong>{(" · " + esc(p)) if p else ""}: '
                  f'<a href="{esc(u)}" rel="noopener" target="_blank">{esc(h)}</a></li>' for d, t, p, h, u in items[:20])
    s = data.get("summary", {})
    return ('<h3 class="bucket-h">Company conference radar</h3>'
            f'<p class="bucket-blurb">Conference presentations, fireside chats, keynotes and academic talks in the last {data.get("lookbackDays", 60)} days, '
            "found by news search for each queued company and its founders and scientists. "
            f'So far it finds company events ({s.get("companyTalks", 0)}) far more than named people ({s.get("peopleTalks", 0)}), because headlines rarely name scientists; '
            "it is not yet full people tracking. Visibility, not evidence: it says what to read or listen to next.</p>"
            f'<ul class="plain-list">{lis}</ul>')


def lab_to_company_section(root: Path) -> str:
    """Peter's chain in one table: research origin -> founders -> specialist money -> pharma/clinic, all from primary filings."""
    founders = load(root / "state/science-founders.json", {}).get("links", [])
    if not founders:
        return ""
    own = load(root / "state/institutional-ownership.json", {}).get("filings", [])
    pharma = [f for f in load(root / "state/pharma-deals-ind.json", {}).get("filings", []) if not f.get("duplicateOf")]
    uspto = {c["ticker"]: c for c in load(root / "state/uspto-assignment-validation.json", {}).get("companies", [])}
    def patents(t):
        c = uspto.get(t)
        if not c:
            return "—"
        own = f'{len(c["officialAssignments"])} owner records' if c["officialAssignments"] else "no owner record"
        lien = sorted({r["assignee"] for r in c.get("securityInterests", [])})
        return own + (f'; pledged to {", ".join(lien)}' if lien else "")
    research = {t: c for t, c in load(root / "state/company-research.json", {}).get("companies", {}).items() if c.get("verified")}
    raises = load(root / "state/equity-raises.json", {}).get("companies", {})
    def papers(t):
        c = research.get(t)
        if not c:
            return "—"
        w = (c.get("topWorks") or [{}])[0]
        link = w.get("doi") or w.get("id")
        top = f'; top: <a href="{esc(link)}">{esc((w.get("title") or "")[:60])}</a> ({w.get("citedBy")} cites)' if link else ""
        return f'{c["recentWorks"]}{top}'
    def raised(t):
        r = raises.get(t) or {}
        return f'${r["totalUsdM"]:,.0f}M' if r.get("totalUsdM", 0) >= 5 else "—"
    elite = ("Massachusetts Institute", "MIT", "Broad Institute", "Harvard", "Stanford", "Whitehead", "Dana-Farber", "Scripps")
    rows_by = {}
    for l in founders:
        r = rows_by.setdefault(l["ticker"], {"inst": {}, "people": set()})
        if l.get("institution"):
            r["inst"].setdefault(l["institution"], l["url"])
        elif l.get("person"):
            r["people"].add(l["person"])
    for t in research:
        rows_by.setdefault(t, {"inst": {}, "people": set()})
    def funds(t):
        names = sorted({f["specialistFund"] for f in own if f["ticker"] == t and f.get("specialistFund")})
        return ", ".join(names) or "—"
    def deals(t):
        out = []
        for f in pharma:
            if f.get("ticker") != t:
                continue
            fx = f.get("facts", {})
            v = lambda k: (fx.get(k) or {}).get("value") if (fx.get(k) or {}).get("verified") else None
            if f["kind"] == "deal" and v("partner"):
                out.append(f"deal: {v('partner')}")
            elif f["kind"] == "ind" and v("drug"):
                out.append(f"IND: {v('drug')}")
        return "; ".join(dict.fromkeys(out)) or "—"
    order = sorted(rows_by, key=lambda t: (-any(e in i for i in rows_by[t]["inst"] for e in elite), -len(rows_by[t]["inst"]),
                                            -(research.get(t, {}).get("recentWorks") or 0), t))
    body = ""
    for t in order:
        r = rows_by[t]
        inst = ", ".join(f'<a href="{esc(u)}">{esc(i)}</a>' for i, u in sorted(r["inst"].items())) or "—"
        body += (f'<tr><td class="tk">{esc(t)}</td><td style="white-space:normal">{inst}</td><td>{esc(", ".join(sorted(r["people"])) or "—")}</td>'
                 f'<td style="white-space:normal">{papers(t)}</td>'
                 f'<td style="white-space:normal">{esc(patents(t))}</td>'
                 f'<td style="white-space:normal">{esc(funds(t))}</td><td class="n">{raised(t)}</td><td style="white-space:normal">{esc(deals(t))}</td></tr>')
    n_elite = sum(any(e in i for i in rows_by[t]["inst"] for e in elite) for t in rows_by)
    return f"""
  <section class="section" id="lab" aria-labelledby="lab-h">
    <h2 id="lab-h">From lab to company</h2>
    <p>The chain Peter asked for: which university or institute the technology came from, who founded the company, whether specialist biotech funds own it, and whether pharma or the FDA has engaged. Origins and founders are quoted from each company's own 10-K (every quote checked against the filing); funds come from Schedule 13D/13G; deals and IND clearances from 8-K press releases.</p>
    <p class="note"><span>Now:</span> {len(rows_by)} companies with a quoted research origin, a named founder or their own published papers; {n_elite} license from MIT, Broad, Harvard, Stanford, Whitehead, Dana-Farber or Scripps. A license proves where the patents came from, not that a given paper became the product. Company papers are OpenAlex works whose authors list the company as their institution (unique name match only). Equity raised is cash received from selling shares, from the cash-flow statement in SEC XBRL; offerings and PIPEs by listed companies do not file a Form D. USPTO records come from the Open Data Portal: an owner record shows the company holds the patent application; "pledged to" means a lender holds a security interest in it.</p>
    <div class="table-wrap"><table><thead><tr><th>Ticker</th><th>Research origin (licensed from)</th><th>Founders named in the 10-K</th><th>Company papers, last 3 years</th><th>USPTO assignment records</th><th>Specialist funds holding 5%+</th><th class="n">Equity raised, 24 months</th><th>Pharma deal / IND (90 days)</th></tr></thead><tbody>{body}</tbody></table></div>
  {inventor_block(root)}
  {patent_life_block(root)}
  </section>"""


REASON_WORD = {"efficacy": "efficacy", "safety": "safety", "manufacturing": "manufacturing", "pharmacology": "pharmacology",
               "usability": "usability"}
SEVERITY_CHIP = {"heavy": "alert", "medium": "warn", "light": "ok"}


def clean_drug(name) -> str:
    """openFDA metadata sometimes puts a sentence fragment where the drug name belongs."""
    name = (name or "").strip()
    if not name or name == "?" or len(name) > 50 or re.match(r"(the|each|a|an|for|treatment|prescribing)\b", name, re.I):
        return "—"
    return name


def fda_crl_section(root: Path) -> str:
    """FDA complete response letters to listed companies: why, how severe, and what the company left out (scripts/fda_crl_reasons.py)."""
    data = load(root / "state/fda-crl-reasons.json", {})
    rows_data = data.get("rows") or []
    if not rows_data:
        return ""
    since = (date.today() - timedelta(days=548)).isoformat()
    listed = sorted((r for r in rows_data if r.get("listed") and (r.get("issued") or "") >= since), key=lambda r: r["issued"], reverse=True)
    tickets = {t["ticker"]: t["action"] for t in load(root / "state/order-tickets.json", {}).get("tickets", [])}
    rows = ""
    for r in listed:
        t = r["listed"]["ticker"]
        sev = r.get("severity") or "unknown"
        reasons = r.get("reasons") or {}
        main = next((k for k in ("efficacy", "safety", "pharmacology", "manufacturing", "usability") if k in reasons), None)
        quote = (r.get("newTrialQuote") if r.get("newTrialRequired") else None) or (reasons.get(main) or {}).get("quote") or ""
        cited = ", ".join(REASON_WORD[k] for k in reasons if k in REASON_WORD) or "—"
        d = r.get("disclosure") or {}
        if d.get("url"):
            notes = []
            if d.get("omitted"):
                notes.append("omits " + ", ".join(d["omitted"]))
            if d.get("companyMentionsNewTrial") is False:
                notes.append("does not mention the new trial")
            said = f'<a href="{esc(d["url"])}">8-K</a>: ' + (esc("; ".join(notes)) if notes else "covers the cited reasons")
        else:
            said = "—"
        held = f'<br><span class="chip warn">ticket: {esc(tickets[t])}</span>' if t in tickets else ""
        rows += (f'<tr><td class="n">{esc(r["issued"])}</td><td class="tk">{esc(t)}<br><span class="muted-note">{esc((r.get("company") or "")[:40])}</span>{held}</td><td>{esc(clean_drug(r.get("drug")))}</td>'
                 f'<td><span class="chip {SEVERITY_CHIP.get(sev, "plain")}">{esc(sev)}</span>{"<br>new trial" if r.get("newTrialRequired") else ""}</td>'
                 f'<td style="white-space:normal">{esc(cited)}' + (f'<br><span class="muted-note">&ldquo;{esc(quote[:220])}&rdquo;</span>' if quote else "") + '</td>'
                 f'<td style="white-space:normal">{said}</td></tr>')
    sev = data.get("bySeverity", {})
    later = data.get("laterApprovedBySeverity", {})
    pct = lambda k: f'{later[k]["approved"] / later[k]["total"]:.0%}' if later.get(k, {}).get("total") else "—"
    drift = load(root / "state/crl-drift-study.json", {}).get("groups", {})
    heavy12 = (drift.get("severity: heavy", {}).get("12m") or {}).get("median")
    light12 = (drift.get("severity: light", {}).get("12m") or {}).get("median")
    drift_txt = (f" After a heavy letter the stock lagged XBI by a median {abs(heavy12):.0%} over the next year; after a light one by {abs(light12):.0%}."
                 if heavy12 is not None and light12 is not None else "")
    c = data.get("disclosureComparison", {})
    return f"""
  <section class="section" id="fda" aria-labelledby="fda-h">
    <h2 id="fda-h">FDA rejections, read in FDA's words</h2>
    <p>Why the FDA did not approve, from the complete response letters it publishes, not from the company's press release. Heavy means FDA found the efficacy evidence insufficient or asked for a new trial; medium means a safety issue or missing pharmacology studies; light means manufacturing, device usability or paperwork. Each row quotes the letter; quotes are read from FDA's scanned PDFs, so a redacted factory name can show up as stray characters. Tickers are matched to the letter's company by name, so check the company name under each ticker. Where the company filed an 8-K about it, the agent checks whether the company named the same problems.</p>
    <p class="note"><span>All {data.get("letters", 0)} letters:</span> {sev.get("heavy", 0)} heavy (later approved {pct("heavy")}), {sev.get("medium", 0)} medium ({pct("medium")}), {sev.get("light", 0)} light ({pct("light")}), {sev.get("unknown", 0) + sev.get("redacted", 0)} unclassified or redacted.{drift_txt} Of {c.get("compared", 0)} letters with a company 8-K, {c.get("withOmissions", 0)} left out at least one problem FDA cited, and {c.get("newTrialOmitted", 0)} did not mention the new trial FDA asked for. A ticket waits after a heavy letter in the last 12 months.</p>
    <div class="table-wrap"><table><thead><tr><th class="n">Date</th><th>Ticker</th><th>Drug</th><th>Severity</th><th>FDA's reasons (quote)</th><th>What the company said</th></tr></thead><tbody>{rows}</tbody></table></div>
  </section>"""


def key_people_section(root: Path) -> str:
    """Peter's "track the core people": roster from SEC Forms 3/4/5, founders from 10-Ks, papers from PubMed (scripts/key_people.py)."""
    data = load(root / "state/key-people.json", {})
    companies = data.get("companies") or {}
    if not companies:
        return ""
    def person(p):
        pp = p.get("papers") or {}
        paper = ""
        if pp.get("count"):
            r = (pp.get("recent") or [{}])[0]
            paper = f' · <a href="{esc(r.get("url") or "")}">{pp["count"]} paper{"s" if pp["count"] > 1 else ""}</a>'
        founder = " · founder" if p.get("founder") and "Founder" not in (p.get("title") or "") else ""
        return (f'<a href="{esc(p["linkedin"])}">{esc(p["name"])}</a> <span class="muted-note">{esc((p.get("title") or "officer")[:40])}'
                f'{founder}{paper}</span>')
    rows = ""
    for t, c in sorted(companies.items(), key=lambda kv: (-sum((p.get("papers") or {}).get("count", 0) > 0 for p in kv[1]["people"]), kv[0])):
        people = c["people"][:5]
        left = "; ".join(f'<a href="{esc(d.get("url") or "")}">{esc(d.get("date") or "")} {esc(d.get("title") or "")}</a>' for d in c.get("departures", []))
        rows += (f'<tr><td class="tk">{esc(t)}</td><td style="white-space:normal">{"<br>".join(person(p) for p in people)}</td>'
                 f'<td style="white-space:normal">{left or "—"}</td></tr>')
    s = data.get("summary", {})
    return f"""
  <section class="section" id="people" aria-labelledby="people-h">
    <h2 id="people-h">Key people</h2>
    <p>Who runs each company and what they publish. The roster comes from SEC Forms 3, 4 and 5 filed in the last four quarters (each filing carries the officer's title), plus founders quoted from the 10-K. Papers are PubMed articles from the last three years where both the author's name and the company as affiliation match. Each name links to a LinkedIn search for following by hand; LinkedIn does not allow automated collection, so nothing is fetched from it.</p>
    <p class="note"><span>Now:</span> {s.get("keyPeople", 0)} people at {s.get("companies", 0)} companies; {s.get("withPapers", 0)} published under the company's name in the last three years; {s.get("departures", 0)} key departure in the management radar.</p>
    <div class="table-wrap"><table><thead><tr><th>Ticker</th><th>Key people (LinkedIn search · title · papers)</th><th>Recent departure</th></tr></thead><tbody>{rows}</tbody></table></div>
  {people_activity_block(root)}
  </section>"""


def biodefense_section(root: Path) -> str:
    """Government countermeasure contracts (ASPR/BARDA via USAspending) and WHO outbreak reports."""
    data = load(root / "state/biodefense-radar.json", {})
    if not data.get("contracts") and not data.get("outbreaks"):
        return ""
    s = data["summary"]
    listed = [c for c in data.get("contracts", []) if c.get("ticker")]
    c_rows = "".join(
        f'<tr><td class="n">{esc(c["date"])}</td><td>{esc(c["recipient"])}</td><td class="tk">{esc(c["ticker"])}</td>'
        f'<td class="n">${c["amountM"]:,.1f}M</td><td style="white-space:normal"><a href="{esc(c["url"])}">{esc(c["description"][:90])}</a></td></tr>'
        for c in listed)
    seen, o_rows = set(), ""
    for o in data.get("outbreaks", []):
        key = o["title"].split(" - ")[0].split("-")[0].strip().lower()
        if key in seen:
            continue
        seen.add(key)
        o_rows += (f'<tr><td class="n">{esc(o["date"])}</td><td style="white-space:normal"><a href="{esc(o["url"])}">{esc(o["title"])}</a></td>'
                   f'<td>{esc(", ".join(o["fundedResponders"]) or "—")}</td></tr>')
    h_rows = "".join(
        f'<tr><td class="n">{esc(o["date"])}</td><td style="white-space:normal"><a href="{esc(o["url"])}">{esc(o["title"])}</a></td>'
        f'<td>{esc(", ".join(o["fundedResponders"]) or "—")}</td></tr>' for o in data.get("cdcAlerts", []))
    han = (f"""
    <h3 class="bucket-h">CDC health alerts (HAN), last 12 months</h3>
    <div class="table-wrap"><table><thead><tr><th class="n">Date</th><th>Alert</th><th>Funded responders</th></tr></thead><tbody>{h_rows}</tbody></table></div>"""
           if h_rows else "")
    return f"""
  <section class="section" id="biodefense" aria-labelledby="bio-h">
    <h2 id="bio-h">Biodefense and outbreaks</h2>
    <p>Where U.S. countermeasure money is going (contract actions by HHS's preparedness office, which runs BARDA and the Strategic National Stockpile, from USAspending.gov) and which outbreaks WHO and the CDC are warning about. A contract is revenue for the company; an outbreak is context, not sales.</p>
    <p class="note"><span>Last 90 days:</span> {s["contracts"]} contract actions of $5M or more, ${s["contractUsdM"]:,.0f}M in total, {s["listedRecipients"]} to listed companies or their parents. Outbreaks are linked to contracts by pathogen name only: Regeneron's Inmazeb, for example, treats Zaire ebolavirus and is not approved for the Bundibugyo strain now spreading.</p>
    <div class="table-wrap"><table><thead><tr><th class="n">Date</th><th>Recipient</th><th>Ticker</th><th class="n">Amount</th><th>Purpose</th></tr></thead><tbody>{c_rows}</tbody></table></div>
    <h3 class="bucket-h">WHO outbreak reports, last 60 days (latest per outbreak)</h3>
    <div class="table-wrap"><table><thead><tr><th class="n">Date</th><th>Report</th><th>Funded responders</th></tr></thead><tbody>{o_rows}</tbody></table></div>{han}
  </section>"""


FUND_SUFFIX = {"Capital", "Management", "Advisors", "Investments", "Group", "Partners", "Global", "Asset", "Funds", "Fund", "Investors", "LLC", "LP"}


def thirteen_f_block(root: Path) -> str:
    """Quarter-on-quarter 13F changes by specialist funds (scripts/fund_13f.py)."""
    data = load(root / "state/fund-13f.json", {})
    companies = data.get("companies") or {}
    if not companies:
        return ""
    word = {"new": "new", "added": "added", "trimmed": "trimmed", "exited": "exited", "held": "held"}
    tone = {"new": "ok", "added": "ok", "trimmed": "warn", "exited": "alert", "held": "plain"}

    def cell(rows, kind):
        names = [" ".join(w for w in r["fund"].replace(".", "").split() if w not in FUND_SUFFIX) for r in rows if r["change"] == kind]
        return f'<span class="chip {tone[kind]}">{len(names)}</span> {esc(", ".join(names))}' if names else "—"

    order = sorted(companies, key=lambda t: (-sum(r["change"] in ("new", "added") for r in companies[t]), t))
    body = "".join(f'<tr><td class="tk">{esc(t)}</td>' + "".join(f'<td style="white-space:normal">{cell(companies[t], k)}</td>' for k in ("new", "added", "trimmed", "exited"))
                   + f'<td class="n">{sum(r["change"] == "held" for r in companies[t])}</td></tr>' for t in order)
    s = data.get("summary", {})
    period = max((f["period"] for f in data.get("funds", [])), default="")
    return (f'<h3 class="bucket-h">Quarterly 13F: adds and trims below 5%</h3>'
            f'<p class="bucket-blurb">{s.get("funds", 0)} specialist funds, quarter ended {esc(period)} against the quarter before. '
            "13F covers every position of a fund managing over $100M, so it shows buying and selling that never reaches the 5% filing line. "
            "It is filed up to 45 days after quarter end, so it shows what a fund held then, not now. Issuers are matched to companies by name. "
            "Context only, like the 13D/13G list above.</p>"
            '<div class="table-wrap"><table><thead><tr><th>Ticker</th><th>New</th><th>Added 10%+</th><th>Trimmed 10%+</th><th>Exited</th><th class="n">Held</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


def funds_section(root: Path) -> str:
    """Specialist life-science funds crossing 5% (Schedule 13D/13G, scripts/institutional_ownership_agent.py)."""
    data = load(root / "state/institutional-ownership.json", {})
    rows_data = [f for f in data.get("filings", []) if f.get("specialistFund")]
    if not rows_data:
        return ""
    new = [f for f in rows_data if f.get("initial")]
    stake = lambda v: "—" if v is None else f"{v:.1f}%"
    by_company = {}
    for f in rows_data:
        by_company.setdefault(f["ticker"], set()).add(f["specialistFund"])
    crowded = sorted(((t, sorted(v)) for t, v in by_company.items() if len(v) >= 2), key=lambda x: -len(x[1]))
    rows = "".join(
        f'<tr><td class="n">{esc(f["filed"])}</td><td class="tk">{esc(f["ticker"])}</td><td>{esc(f["reportingPerson"])}</td>'
        f'<td class="n">{stake(f.get("percent"))}</td><td>{esc(f["form"])}</td>'
        f'<td><a href="{esc(f["url"])}">SEC</a></td></tr>' for f in new)
    crowd = "; ".join(f'{esc(t)} ({", ".join(esc(x) for x in v)})' for t, v in crowded[:8])
    return f"""
  <section class="section" id="funds" aria-labelledby="funds-h">
    <h2 id="funds-h">Specialist biotech funds building positions</h2>
    <p>Schedule 13G/13D filings by dedicated life-science investors (RA Capital, Baker Bros, Perceptive, RTW, Commodore, BVF and others) in the companies this page follows, last 12 months. A first filing means the fund just crossed 5% of the shares. This is ownership bought in the market or in an offering; it is not proof the company raised new money, and 13G filers are passive by definition. Treat it as context: in a 2018 to mid-2025 test on 445 health-care companies, stocks where a specialist fund newly crossed 5% did no better than the same stocks bought at a random month start (430 cases, 12-month median excess vs XBI -21.5% against -21.4%); a specialist 13D did worse (60 cases, -45.4%). See outputs/fund-stake-study.md.</p>
    <p class="note"><span>Now:</span> {len(new)} new positions and {len(rows_data) - len(new)} amendments from specialist funds across {len(by_company)} companies.</p>
    <p class="note"><span>Several specialists in the same company:</span> {crowd or "—"}</p>
    <div class="table-wrap"><table><thead><tr><th class="n">Filed</th><th>Ticker</th><th>Fund</th><th class="n">Stake</th><th>Form</th><th></th></tr></thead>
    <tbody>{rows}</tbody></table></div>
    {thirteen_f_block(root)}
  </section>"""


def deals_section(root: Path) -> str:
    """IND clearances and big-pharma deals from 8-K press releases (scripts/pharma_deals_ind.py)."""
    data = load(root / "state/pharma-deals-ind.json", {})
    filings = data.get("filings") or []
    v = lambda f, k: esc(((f or {}).get(k) or {}).get("value") or "—")
    deals = [r for r in filings if r["kind"] == "deal" and (r.get("facts") or {}).get("isNewDeal") is True and not r.get("duplicateOf")]
    inds = [r for r in filings if r["kind"] == "ind" and (r.get("facts") or {}).get("isIndClearance") is True and not r.get("duplicateOf")]
    if not deals and not inds:
        return ""
    link = lambda r: f'<a href="{esc(r["url"])}" target="_blank" rel="noopener">8-K</a>'
    deal_rows = "".join(f'<tr><td class="n">{esc(r["filed"])}</td><td>{esc(r["company"])} <span class="tk">{esc(r["ticker"] or "")}</span></td><td>{v(r["facts"], "partner")}</td>'
                        f'<td class="n">{v(r["facts"], "upfrontUsdM")}</td><td class="n">{v(r["facts"], "milestonesUsdM")}</td><td style="white-space:normal">{v(r["facts"], "scope")}</td><td>{link(r)}</td></tr>' for r in deals)
    ind_rows = "".join(f'<tr><td class="n">{esc(r["filed"])}</td><td>{esc(r["company"])} <span class="tk">{esc(r["ticker"] or "")}</span></td><td>{v(r["facts"], "drug")}</td>'
                       f'<td style="white-space:normal">{v(r["facts"], "indication")}</td><td>{v(r["facts"], "nextTrial")}</td><td>{link(r)}</td></tr>' for r in inds)
    w = data.get("window", ["", ""])
    return f"""
  <section class="section" id="deals" aria-labelledby="deals-h">
    <h2 id="deals-h">Cleared for human trials, big pharma paying</h2>
    <p>Two early, hard signals from companies' own 8-K press releases between {esc(w[0])} and {esc(w[1])}. An IND clearance means FDA did not stop the drug from starting human trials. It does not show the drug works, and it is years and several trial phases away from approval. A new deal with a large drug maker, with cash up front, means a buyer did its own diligence and paid. Facts were extracted by Claude and every value is kept only if its quote is found word for word in the filing.</p>
    {('<h3 class="bucket-h">New big-pharma deals</h3><div class="table-wrap"><table><thead><tr><th class="n">Filed</th><th>Company</th><th>Partner</th><th class="n">Upfront ($M)</th><th class="n">Milestones ($M)</th><th>Scope</th><th></th></tr></thead><tbody>' + deal_rows + '</tbody></table></div>') if deal_rows else ''}
    {('<h3 class="bucket-h">IND clearances</h3><div class="table-wrap"><table><thead><tr><th class="n">Filed</th><th>Company</th><th>Drug</th><th>Indication</th><th>Next trial</th><th></th></tr></thead><tbody>' + ind_rows + '</tbody></table></div>') if ind_rows else ''}
  </section>"""


def commercialization_chain_section(root: Path) -> str:
    """Show where a scientific idea has, and has not, become a commercial business."""
    data = load(root / "state/science-commercialization-graph.json", {})
    companies = data.get("companies") or []
    if not companies:
        return ""
    label = {"ownership-and-pharma-validated": "ownership + pharma payment",
             "ownership-and-company-revenue-verified": "ownership + company revenue; technology share unknown",
             "commercial-signal-with-ownership-gap": "commercial signal; ownership gap",
             "clinical-signal-with-ownership-gap": "clinical signal; ownership gap",
             "science-linked": "science linked; not commercial",
             "evidence-fragment": "separate evidence only"}
    rows = ""
    for r in companies[:24]:
        v = r.get("verifiedStages", {})
        mark = lambda key: "✓" if v.get(key) else "—"
        gaps = "; ".join(r.get("gaps", [])[:2]) or "none"
        rows += (f'<tr><td class="tk">{esc(r["ticker"])}</td><td>{esc(r.get("company") or "")}</td>'
                 f'<td class="n">{mark("discovery")}</td><td class="n">{mark("researcherCompanyRelation")}</td>'
                 f'<td class="n">{mark("technologyOwnership")}</td>'
                 f'<td class="n">{mark("funding")}</td><td class="n">{mark("institutionalOwnership")}</td><td class="n">{mark("pharmaValidation")}</td>'
                 f'<td class="n">{mark("clinicalValidation")}</td><td class="n">{mark("revenueValidation")}</td>'
                 f'<td style="white-space:normal"><strong>{esc(label.get(r.get("chainStatus"), r.get("chainStatus")))}</strong><br>'
                 f'<span class="muted-note">{esc(gaps)}</span></td></tr>')
    s = data.get("summary", {})
    uspto = load(root / "state/uspto-assignment-validation.json", {})
    institutional = load(root / "state/institutional-ownership.json", {})
    pending = []
    if uspto.get("status") == "pending-official-export":
        pending.append("USPTO assignment validation is waiting for an official Assignment Center/ODP export")
    if institutional.get("status") == "pending-config":
        pending.append("13D/13G collection is waiting for SEC_USER_AGENT")
    pending_note = f'<p class="note"><span>Configuration:</span> {esc("; ".join(pending))}.</p>' if pending else ""
    return f"""
  <section class="section" id="commercial-chain" aria-labelledby="commercial-chain-h">
    <h2 id="commercial-chain-h">From scientific idea to a business somebody pays for</h2>
    <p>This is the first-priority chain Peter asked for: paper and researcher → founder/company relation, patent or license → financing → a drug maker paying → IND or clinical trial → reported revenue. Every column requires its own primary evidence. A founder relationship is not patent ownership; a paper that sounds similar to a company's technology remains a discovery lead; a partnership announcement is not treated as customer revenue.</p>
    <p class="note"><span>Current state:</span> {s.get('companiesLinked', 0)} companies have at least one link, {s.get('commercialSignals', 0)} have a commercial signal, {s.get('researcherCompanyVerified', 0)} have a verified researcher/founder relationship, {s.get('technologyOwnershipDisclosed', 0)} disclose patent or license rights, {s.get('usptoAssignmentVerified', 0)} have independent USPTO assignment verification, {s.get('institutionalOwnersVerified', 0)} have a verified 13D/13G owner, and {s.get('completeChains', 0)} complete every stage. Zero is an honest research gap, not a zero company score.</p>
    {pending_note}
    <div class="table-wrap"><table><thead><tr><th>Ticker</th><th>Company</th><th class="n">Paper</th><th class="n">Researcher / company</th><th class="n">Patent / license</th><th class="n">Funding</th><th class="n">5% owner</th><th class="n">Pharma pays</th><th class="n">Clinical</th><th class="n">Revenue</th><th>Conclusion and missing proof</th></tr></thead><tbody>{rows}</tbody></table></div>
  </section>"""


def mapping_validation_block(root: Path) -> str:
    """Recall and precision of the SEC topic->company mapping, before and after the filing-reading upgrade."""
    after = load(root / "state/topic-mapping-validation.json", {})
    before = load(root / "state/topic-mapping-validation.before.json", {})
    if not after.get("topics"):
        return ""
    pct = lambda v: f"{v:.0%}" if v is not None else "—"
    arrow = lambda b, a: f'<span class="muted-note">{esc(b)} →</span> {esc(a)}' if b not in (None, "", "—") and b != a else esc(a)
    rows = ""
    for key, t in after["topics"].items():
        b = (before.get("topics") or {}).get(key, {})
        rb, ra = (b.get("recall") or {}).get("recall"), (t.get("recall") or {}).get("recall")
        missed = ", ".join((t.get("recall") or {}).get("missed", [])) or "—"
        rows += (f'<tr><td>{esc(t["label"])}</td><td class="n">{arrow(b.get("mapped"), t["mapped"])}</td>'
                 f'<td class="n">{arrow(pct(rb) if b else None, pct(ra))}</td><td class="tk" style="white-space:normal">{esc(missed)}</td>'
                 f'<td class="n">{arrow(pct(b.get("precisionProxy")) if b else None, pct(t["precisionProxy"]))}</td></tr>')
    return ('<h3 class="bucket-h">How good is the topic-to-company mapping?</h3>'
            '<p class="bucket-blurb">Recall: listed makers with two or more AI devices on the matching FDA review panel that the mapping found. '
            'Precision (rule-based proxy): mapped companies whose filing text shows an own-product, supplier or customer link, judged by the same rules the mapping uses, not by hand. '
            + ('Grey figures are before the agent started reading each candidate\'s filing. ' if before.get("topics") else '')
            + 'Misses that remain are companies whose filings do not describe the work (Apple) or that file outside EDGAR full-text search (Canon ADR).</p>'
            '<div class="table-wrap"><table><thead><tr><th>Topic</th><th class="n">Mapped</th><th class="n">Recall</th><th>Still missed</th><th class="n">Precision (proxy)</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


def tier_word(row: dict) -> str:
    tier = ((row.get("serenityVerdict") or {}).get("tier") or "").lower()
    return "standard tier" if "standard" in tier else "starter tier" if "starter" in tier else "not reviewed"


def order_cell(o: dict | None) -> str:
    if not o:
        return ""
    state = {"above": f"{o['gapToUpper']:+.0%} vs range", "in-range": "inside range", "at-top": "at the top of the range"}.get(o["status"], "below safety floor")
    return f'<br><span class="order-cell">Order ≤ ${o["upper"]:,.2f} · {esc(state)}</span>'


def market_cell(m: dict | None) -> str:
    """Compact market check: 3-month move vs XBI, distance from high, valuation, Kronos 5-day."""
    if not m or m.get("error"):
        return "—"
    pc = lambda v: f"{v:+.0%}" if v is not None else "n/a"
    xbi = m["threeMonths"] - m["threeMonthsVsXbi"] if m.get("threeMonths") is not None and m.get("threeMonthsVsXbi") is not None else None
    parts = [f'3 mo {pc(m.get("threeMonths"))}, XBI {pc(xbi)}']
    if m.get("fromHigh") is not None:
        parts.append(f'{abs(m["fromHigh"]):.0%} below 6-mo high')
    if m.get("priceToSales"):
        parts.append(f'{m["priceToSales"]:.1f}× sales')
    if m.get("kronos5d"):
        parts.append(f'Kronos 5-day {m["kronos5d"]["forecastReturn"]:+.1%}')
    return f'{esc(" · ".join(parts))}<br><span class="muted-note">{esc(m.get("reading", ""))}</span>'


def core_articles(root: Path) -> int:
    """Articles in the core frontier-news store (company, radar and policy stores can overlap with it)."""
    import sqlite3
    try:
        with sqlite3.connect(root / "trend-agent/state/daily-news.db") as connection:
            return connection.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    except sqlite3.Error:
        return 0


def oos_block(root: Path) -> str:
    """Out-of-sample replay on health-care companies the rule never saw, split by how deep the discount is."""
    ins, oos = load(root / "state/order-rule-backtest.json", {}), load(root / "state/order-rule-backtest-oos.json", {})
    if not oos.get("rows"):
        return ""
    def cell(rows, lo, hi, key, filt=False):
        v = sorted(r[key] for r in rows if r.get(key) is not None and lo < r["gap"] <= hi and (not filt or r.get("notSlowing")))
        if not v:
            return "—"
        return f'{v[len(v) // 2]:+.0%} · {sum(x < -0.6 for x in v) / len(v):.0%} · n={len(v)}'
    buckets = ((-9, -0.20, False, "Deep discount (implied growth 20+ points below base)"),
               (-0.20, 0, False, "Mild discount (0-20 points below)"),
               (-0.20, 0, True, "Mild discount, growth not slowing"),
               (0, 9, False, "Above range"))
    rows = "".join(f'<tr><td>{name}</td><td class="n">{cell(ins.get("rows", []), lo, hi, "excess1y", f)}</td>'
                   f'<td class="n">{cell(oos["rows"], lo, hi, "excess1y", f)}</td><td class="n">{cell(oos["rows"], lo, hi, "excess3y", f)}</td></tr>'
                   for lo, hi, f, name in buckets)
    return f"""
    <h3 class="bucket-h">5 · Out of sample: {oos["companies"]} health-care companies the rule never saw</h3>
    <p class="bucket-blurb">The same rules replayed on {oos["observations"]} filings from listed health-care companies (drugs, diagnostics, biologics, devices, labs) that were not in the sample above. Each cell: median excess return vs XBI · share that lost 60%+ vs XBI · filings.</p>
    <p class="status-banner"><strong>Bottom line: the valuation rule has not shown a stable, significant excess return.</strong> No bucket beat XBI on average, mean and median returns differ widely, the same company appears in many years, the sample holds only companies listed today, multiples are today&#39;s, and the rule was adjusted after part of these results were seen. Treat it as a risk filter, not as proof of an edge.</p>
    <p class="status-banner"><strong>What held up:</strong> a deep discount was the worst bucket in both samples, so the tickets now wait on it. A mild discount with growth not slowing was the steadiest bucket in both. The slowing-growth filter still cut severe losses out of sample, but by much less than in sample, and no bucket beat XBI on average.</p>
    <div class="table-wrap"><table><thead><tr><th>Price vs base case</th><th class="n">In sample, 1 year</th><th class="n">Out of sample, 1 year</th><th class="n">Out of sample, 3 years</th></tr></thead><tbody>{rows}</tbody></table></div>"""


def backtest_block(root: Path) -> str:
    """The order rule replayed on 2014-2026 10-K filings (scripts/backtest_order_rule.py)."""
    bt = load(root / "state/order-rule-backtest.json", {})
    if not bt.get("buckets"):
        return ""
    pc = lambda v: "—" if v is None else f"{v:+.1%}"
    names = (("inRange", "In range (old rule buys)"), ("aboveRange", "Above range (wait)"),
             ("inRangeNotSlowing", "In range, growth not slowing (new rule buys)"), ("inRangeSlowing", "In range, growth slowing (new rule waits)"))
    rows = ""
    for label in ("1y", "3y"):
        for key, name in names:
            st, sl = bt["buckets"][label].get(key, {}), bt["severeLoss"][label].get(key)
            if st.get("n"):
                rows += (f'<tr><td class="n">{label}</td><td>{name}</td><td class="n">{st["n"]}</td><td class="n">{pc(st["median"])}</td>'
                         f'<td class="n">{st["hit"]:.0%}</td><td class="n">{"—" if sl is None else f"{sl:.0%}"}</td></tr>')
    return f"""
    <h3 class="bucket-h">4 · The order rule on 2014-2026 history</h3>
    <p class="bucket-blurb">On the day after each 10-K, using only that filing: does a price inside the order range (the price implies no more growth than the base case) lead to better returns than XBI? {bt["observations"]} filings from {bt["companies"]} health-care companies.</p>
    <p class="status-banner"><strong>Result: the range alone did not pick winners.</strong> In-range stocks had a lower median and more severe losses, mostly fast growers whose growth then fell well short of the base case. Requiring that growth is not slowing roughly halved the severe-loss rate, so the order tickets now apply that test. It does not make the rule beat XBI on average, and the filter was found in this same sample.</p>
    <div class="table-wrap"><table><thead><tr><th class="n">Held</th><th>Group</th><th class="n">Filings</th><th class="n">Median excess vs XBI</th><th class="n">Beat XBI</th><th class="n">Lost 60%+ vs XBI</th></tr></thead><tbody>{rows}</tbody></table></div>
    {oos_block(root)}
    <p class="note">Survivorship bias: only companies listed today are in the sample. Multiples and industry growth are today's Damodaran tables. Details: <code>outputs/order-rule-backtest.md</code> and <code>outputs/order-rule-backtest-oos.md</code>.</p>"""


def track_section(root: Path) -> str:
    """Track record: frozen scores and Serenity tiers scored on real trading days."""
    tr = load(root / "state/track-record.json", {})
    if not tr:
        return ""
    pc = lambda v: f"{v:+.2%}" if v is not None else "waiting"
    hit = lambda v: f"{v:.0%}" if v is not None else "waiting"
    rule = tr.get("rule", {"minObservations": 30, "minDates": 10})
    enough = lambda n, d: n >= rule["minObservations"] and d >= rule["minDates"]
    flag = lambda n, d: "" if not n else ("" if enough(n, d) else ' <span class="chip warn">too few</span>')
    score_rows = "".join(
        f'<tr><td class="n">{r["horizon"]}</td><td class="n">{r["samples"]}</td><td class="n">{r["dates"]}{flag(r["samples"], r["dates"])}</td>'
        f'<td class="n">{pc(r["return"])}</td><td class="n">{hit(r["hitRate"])}</td><td class="n">{pc(r["highScore"])}</td><td class="n">{pc(r["lowScore"])}</td></tr>'
        for r in tr.get("scoreBackfill", []))
    bench_rows = "".join(
        f'<tr><td class="n">{r["horizon"]}</td><td class="n">{r["samples"]}</td><td class="n">{r["dates"]}{flag(r["samples"], r["dates"])}</td>'
        f'<td class="n"><strong>{pc(r["agentReturn"])}</strong></td><td class="n">{pc(r["spyReturn"])}</td><td class="n">{pc(r["xlvReturn"])}</td>'
        f'<td class="n">{pc(r["xbiReturn"])}</td><td class="n">{pc(r["excessXbi"])}</td><td class="n">{pc(r["randomReturn"])}</td><td class="n">{pc(r["momentumReturn"])}</td></tr>'
        for r in tr.get("benchmarks", []))
    tier_rows = "".join(
        f'<tr><td class="n">{r["horizon"]}</td>'
        f'<td class="n">{r["standard"]["samples"]}</td><td class="n">{pc(r["standard"]["return"])}</td>'
        f'<td class="n">{r["starter"]["samples"]}</td><td class="n">{pc(r["starter"]["return"])}</td>'
        f'<td class="n">{pc(r["xbi"])}</td><td class="n">{pc(r["standardMinusStarter"])}</td></tr>'
        for r in tr.get("serenityTiers", []))
    calls = tr.get("serenityCalls", [])
    first_call = min((c["calledOn"] for c in calls), default=None)
    base_date = min((c["baseDate"] for c in calls), default=None)
    by_tier = {t: ", ".join(f'{c["ticker"]} {c["basePrice"]:.2f}' for c in calls if c["tier"] == t and c["calledOn"] == first_call) for t in ("standard", "starter")}
    frozen_note = (f'<p>Frozen on <strong>{esc(first_call)}</strong> at the {esc(base_date)} close. Standard: {esc(by_tier["standard"])}. Starter: {esc(by_tier["starter"])}. '
                   f'A ticker gets a new row when its tier changes or a week has passed; earlier rows are never edited.</p>') if calls else ""
    return f"""
  <section class="section" id="track" aria-labelledby="track-h">
    <h2 id="track-h">Track record</h2>
    <p class="status-banner"><strong>Too few samples; no effectiveness claim.</strong> The system's own rule: no conclusion before {rule["minObservations"]} stock-day observations across {rule["minDates"]} separate prediction days. No row below meets it yet.</p>
    <p>Every prediction is frozen with the price known on the day it was made. Returns are filled in later from real trading-day closes, so a day the agent did not run never stretches a horizon. <strong>OpenBB</strong> supplies the price history. <strong>Kronos</strong>, a time-series model trained on market candlesticks, supplies the short-term forecast that enters the daily score alongside news and technicals.</p>
    <h3 class="bucket-h">1 · Short-term daily score</h3>
    <p class="bucket-blurb">News, technical and Kronos scores combined, frozen daily since {esc(tr.get("scoresSince") or "—")} for {tr.get("scoreTickers", 0)} tracked stocks (AI medicine plus a few test names from other themes). High score means 70 or more.</p>
    <div class="table-wrap"><table><thead><tr><th class="n">Sessions later</th><th class="n">Observations</th><th class="n">Prediction days</th><th class="n">Average return</th><th class="n">Kronos direction right</th><th class="n">High-score group</th><th class="n">Other scores</th></tr></thead><tbody>{score_rows}</tbody></table></div>
    <h3 class="bucket-h">2 · AI-medicine picks against benchmarks</h3>
    <p class="bucket-blurb">The same frozen predictions for AI-medicine names only, against the S&amp;P 500 (SPY), health care (XLV), biotech (XBI), a fixed-seed random stock and a 20-day momentum pick on the same days.</p>
    <div class="table-wrap"><table><thead><tr><th class="n">Sessions later</th><th class="n">Observations</th><th class="n">Prediction days</th><th class="n">Agent picks</th><th class="n">SPY</th><th class="n">XLV</th><th class="n">XBI</th><th class="n">Excess vs XBI</th><th class="n">Random</th><th class="n">Momentum</th></tr></thead><tbody>{bench_rows}</tbody></table></div>
    <h3 class="bucket-h">3 · Serenity tiers, tracked from today</h3>
    <p class="bucket-blurb">Serenity tiers judge company quality over 5–10 years, not next week's price. They are scored anyway, so that in a few months we can see whether standard-tier names beat starter-tier names and XBI.</p>
    {frozen_note}
    <div class="table-wrap"><table><thead><tr><th class="n">Sessions later</th><th class="n">Standard calls</th><th class="n">Standard return</th><th class="n">Starter calls</th><th class="n">Starter return</th><th class="n">XBI</th><th class="n">Standard minus starter</th></tr></thead><tbody>{tier_rows}</tbody></table></div>
    {backtest_block(root)}
    <p class="note">Horizons longer than one session overlap, so neighbouring observations are not independent. Full tables, rank IC and bootstrap intervals: <code>outputs/agent-benchmark-validation.md</code> and <code>outputs/investment-score-performance.md</code>.</p>
  </section>"""


def render_html(payload: dict, root: Path = ROOT) -> str:
    status = load(root / "state/serenity-review-status.json", {})
    st = status.get("summary", {})
    status_line = (
        '<p class="status-banner"><strong>Research tiers, not buy decisions.</strong> '
        "The eight evidence gates are this project's own checklist built on the Serenity method; no company passes all eight yet. "
        f'Every company with a Serenity tier on this page has a current review whose quotes were checked word for word against its filings '
        f'({st.get("claudeChecked", 0)} of {st.get("claudePending", 0) + st.get("claudeChecked", 0)}).</p>'
    ) if st else ""
    pending = st.get("claudePending", 0)
    checked = st.get("claudeChecked", 0)
    citation_label = (f"{checked} citation-checked, {pending} pending" if pending else "citation-checked") if checked else "citation check pending"
    citation_note = ("Every quote in these memos was matched word for word against the filing before import; quotes that do not match are rejected or downgraded."
                     if checked and not pending else
                     "Memo quotes are matched word for word against the filing before import; memos still pending are research drafts.")
    review_of = status.get("companies", {})
    mv = load(root / "state/market-validation.json", {}).get("companies", {})
    lt_rows = "".join(
        f'<tr><td class="tk"><a href="#{esc(r["ticker"])}">{esc(r["ticker"])}</a><br><span class="muted-note">{esc(label.split()[0])}</span></td><td>{esc(r["longTerm"]["edge"])}</td>'
        f'<td>{esc(r["longTerm"]["counter"])}</td><td>{market_cell(mv.get(r["ticker"]))}{order_cell(r.get("orderRange"))}</td><td>{esc(r["longTerm"]["next_check"])}</td></tr>'
        for key, label, _ in BUCKETS for r in payload["picks"].get(key, []) if r.get("longTerm"))
    long_term_html = (f'<div class="table-wrap long-term"><table><caption>Why these six could lead by 2035, what could stop them, what the market says today, and what we check next</caption>'
                      f'<thead><tr><th>Ticker</th><th>Why it could win (Serenity)</th><th>Biggest counter (Serenity)</th><th>Market check and order range (context only)</th><th>Next check</th></tr></thead><tbody>{lt_rows}</tbody></table></div>') if lt_rows else ""
    responses = load(root / "state/serenity-claude-response.json", {}).get("reviews", [])
    quotes = sum(len(g.get("support", [])) + len(g.get("counter", [])) for r in responses for g in r.get("gates", {}).values())
    tr_calls = load(root / "state/track-record.json", {}).get("serenityCalls", [])
    n_mapped = len((payload.get("news") or {}).get("calls", []))
    steps_pipe = [
        ("1", "Catch frontier news", f"More than {core_articles(root) // 100 * 100:,} core news articles so far, plus company SEC filings, FDA device decisions from openFDA and FDA, CMS and HHS policy records."),
        ("2", "Map it to companies", f"{n_mapped} companies touched by material news in the last two weeks, by name or because their own filings describe the work; a market-wide SEC screen adds companies the news has not named."),
        ("3", "Serenity reads the filings", f"{len(responses)} companies reviewed with three Serenity skills through eight evidence gates; {quotes} quotes matched word for word against SEC filings and FDA records."),
        ("4", "Check the market", f"OpenBB prices and valuation plus Kronos 5-day forecasts for {len(mv)} companies. Short-term market context only; it does not validate or change the long-term thesis."),
        ("5", "Rank, explain, freeze", f"Only Serenity-reviewed companies can be picked. {len({c['ticker'] for c in tr_calls})} tiers frozen at a known price and scored on real trading days."),
    ]
    pipeline_html = ('<section class="section" id="how" aria-labelledby="how-h"><h2 id="how-h">How this list is made</h2><ol class="pipeline">'
                     + "".join(f'<li><span class="pnum">{n}</span><div><strong>{esc(t)}</strong><p>{esc(d)}</p></div></li>' for n, t, d in steps_pipe)
                     + '</ol><p class="note">News finds the candidates. Serenity tests long-term potential against the filings. Scores are derived consistently from evidence-gate results and reported financial data, rather than free-form ranking. Market data and Kronos give short-term context only.</p></section>')
    radar_html, radar_css = radar_section(root)
    track_html = track_section(root)
    top = payload["top"]
    def answer_links(rows):
        return "".join(
            f'<a href="#{esc(r["ticker"])}"><span class="r">#{r["bucketRank"]}</span><span class="t">{esc(r["ticker"])}</span>'
            f'<span class="c">{esc(r["company"])}</span><span class="s">Potential {r["potential"]["total"]:.0f} · Serenity {esc(tier_word(r))}</span></a>'
            for r in rows
        )
    answer = "".join(
        f'<div class="answer-group"><p class="answer-label">5–10 year ranking · {esc(label)}</p><nav class="answer" aria-label="{esc(label)}">{answer_links(payload["picks"][key])}</nav></div>'
        for key, label, _ in BUCKETS if payload["picks"].get(key)
    )
    answer += early_candidates(root)
    TIER_LABEL = {"serenity-standard": ("Serenity: standard tier", "ok"), "serenity-starter": ("Serenity: starter tier", "warn"),
                  "serenity-watch": ("Serenity: watch", "plain")}
    news = payload.get("news") or {}
    calls = news.get("calls", [])
    analysed = [c for c in calls if c.get("decision", "").startswith("serenity-")]
    awaiting = [c for c in calls if c.get("decision") == "awaiting-serenity"]
    warnings_ = [c for c in calls if c.get("decision") == "warning"]
    bucket_label = {key: label for key, label, _ in BUCKETS}
    news_html = ""
    if calls:
        def trigger_line(c):
            evs = [e for e in c["events"] if e.get("type") != "commentary"][:2]
            themes = [t for t in c.get("themes", []) if t.get("material")][:1]
            out = "".join(event_item(e) for e in evs)
            out += "".join(f'<li class="news-item"><span class="chip ok">▲ Theme</span> {esc(t["label"])} heating up in the frontier news (exposure {t["strength"]:.0%} from its filings)</li>' for t in themes)
            return f'<ul class="news-list">{out}</ul>'

        def recheck_line(r):
            """Whether news after the review's evidence has reopened gates (news_signal_engine.news_recheck)."""
            if not r or not r.get("evidenceThrough"):
                return ""
            if r["status"] != "queued":
                return (f'<p class="call-foot"><span class="chip ok">Evidence covers the news</span> '
                        f'review reads primary documents through {esc(r["evidenceThrough"])}; no material news since then</p>')
            items = "".join(f'<li>{esc(e["date"])} · <strong>{esc(EVENT_LABEL.get(e["type"], e["type"]))}</strong> <span>{esc(e["title"][:90])}</span></li>' for e in r["events"][:3])
            gates = ", ".join(g.replace("_", " ") for g in r["gates"]) or "—"
            return (f'<div class="recheck"><p class="call-foot"><span class="chip warn">Re-check queued</span> '
                    f'news after the review\'s evidence ({esc(r["evidenceThrough"])}) reopens: <strong>{esc(gates)}</strong></p>'
                    f'<ul class="plain-list">{items}</ul></div>')

        def serenity_card(c):
            v = c["serenity"] or {}
            label, tone = TIER_LABEL.get(c["decision"], ("Serenity", "plain"))
            counters = "".join(f"<li>{esc(x)}</li>" for x in v.get("countersHolding", []))
            gates = ", ".join(g.replace("_", " ") for g in c["gatesToRecheck"]) or "none"
            return (f'<article class="call"><header class="call-head"><h3><span class="ticker">{esc(c["ticker"])}</span> {esc(c["company"])}</h3>'
                    f'<span class="chip {tone}">{esc(label)}</span></header>'
                    + (lambda r: f'<p class="call-foot">Claude memo: <strong>{esc(r.get("claudeMemo") or "none")}</strong> · first-round review: <strong>{esc(r.get("review", "none"))}</strong></p>')(review_of.get(c["ticker"], {}))
                    + recheck_line(c.get("recheck"))
                    + f'<div class="call-step"><h4>1 · What the news changed</h4>{trigger_line(c)}</div>'
                    f'<div class="call-step"><h4>2 · Serenity analysis</h4><p class="call-verdict">{esc(v.get("verdict", ""))}</p>'
                    f'<dl class="mini"><div><dt>Chokepoint</dt><dd>{esc(v.get("chokepoint", "—"))}</dd></div>'
                    f'<div><dt>Bucket</dt><dd>{esc(bucket_label.get(v.get("bucket"), v.get("bucket") or "—"))}</dd></div>'
                    f'<div><dt>Sizing tier the skills imply</dt><dd>{esc(v.get("tier", "—"))}</dd></div></dl>'
                    f'<h4>Counter-theses that hold</h4><ul class="plain-list">{counters}</ul></div>'
                    f'<p class="call-foot">Gates this news touches: <strong>{esc(gates)}</strong>. Full memo: <code>{esc(v.get("memo", ""))}</code></p></article>')

        def queue_rows(rows):
            out = ""
            for c in rows:
                top = next((e for e in c["events"] if e.get("type") != "commentary"), None)
                link = f'<a href="{esc(top["url"])}" target="_blank" rel="noopener">{esc(top["title"][:90])}</a>' if top else ""
                if c.get("driver") == "theme":
                    theme = next((t for t in c.get("themes", []) if t.get("material")), None)
                    link = f'Via theme: <strong>{esc(theme["label"])}</strong>' if theme else link
                gates = esc(", ".join(g.replace("_", " ") for g in c["gatesToRecheck"]))
                out += (f'<tr><td class="tk">{esc(c["ticker"])}</td><td class="n">{c["newsSignal"]:+.0f}</td>'
                        f'<td style="white-space:normal;min-width:240px">{link}</td><td style="white-space:normal">{gates}</td></tr>')
            return out
        hot = [t for t in news.get("themes", []) if t["articles"] and t["heat"] > 0][:6]
        theme_rows = ""
        for t in hot:
            heads = "".join(f'<li><a href="{esc(h["url"])}" target="_blank" rel="noopener">{esc(h["title"][:95])}</a> <span class="news-meta">{esc(h["source"][:24])}</span></li>' for h in t["headlines"][:2])
            rel = lambda x: f' <span class="muted-note">{esc(RELATION_WORD[x["relation"]])}</span>' if x.get("relation") in RELATION_WORD else ""
            covered = ", ".join(f'{esc(x["ticker"])} {x["strength"]:.0%}{rel(x)}' for x in t["covered"][:6]) or "—"
            new_names = ", ".join(f'{esc(x["ticker"])}{rel(x)}' for x in t["uncovered"]) or "—"
            state = '<span class="chip ok">Heating up</span>' if t["material"] else '<span class="chip plain">Early</span>'
            theme_rows += (f'<tr><td><strong>{esc(t["label"])}</strong><br>{state}</td><td class="n">{t["articles"]}</td><td class="n">{t["heat"]:+.1f}</td>'
                           f'<td style="white-space:normal;min-width:280px"><ul class="news-list">{heads}</ul></td><td style="white-space:normal">{covered}</td><td>{new_names}</td></tr>')
        themes_html = (
            '<h3 class="bucket-h">What the frontier news is about</h3>'
            '<p class="bucket-blurb">Articles that name no company (new models, papers, policy, funding rounds) are grouped into AI-medicine topics. '
            'Heat compares the last 7 days with the weekly average of the three weeks before, so a topic that is always discussed does not count; only one heating up does. '
            'Each topic then reaches the companies whose own SEC filings describe that work, weighted by how strongly. '
            'A phrase match is not enough: the agent opens each candidate\'s filing and keeps it only if the text shows the company makes the product (own), '
            'supplies the companies that do (supplier) or buys it (customer); competitors named in risk factors, glossary lines and AI shells are dropped.</p>'
            '<div class="table-wrap"><table><thead><tr><th>Topic</th><th class="n">Articles, 7 days</th><th class="n">Heat</th><th>Examples</th>'
            f'<th>Covered companies (exposure)</th><th>New names to look at</th></tr></thead><tbody>{theme_rows}</tbody></table></div>'
        ) if theme_rows else ""
        cards = "".join(serenity_card(c) for c in analysed) or '<p class="empty">No news-triggered company has a Serenity analysis yet.</p>'
        news_html = f"""
  <section class="section" id="news" aria-labelledby="news-h">
    <h2 id="news-h">This week: frontier news, then Serenity</h2>
    <p>The news does not decide anything. It shows what changed and for whom: news that names a company becomes an event (FDA, reimbursement, partnership, clinical data, earnings, lawsuits), and frontier news that names no company is mapped to the companies whose own filings describe that work. Each change is then handed to a Serenity analysis that applies three core Serenity skills to primary filings through eight evidence gates: map the supply chain, test for a chokepoint, check customer dependence, stress-test the counter-thesis and set validation gates. <strong>The Serenity tier is a research view, not a trade.</strong> A company with material news but no Serenity analysis yet waits in the queue below instead of being rated on news alone.</p>
    {themes_html}
    {mapping_validation_block(root)}
    {fda_block(root)}
    {recheck_block(root)}
    <h3 class="bucket-h">News-triggered companies with a Serenity verdict</h3>
    <p class="bucket-blurb">For a company that already has a review, the agent compares each news item with the date of the latest primary document the review read. Write-ups of a quarter already in the evidence are covered; material news after it (a deal, a partnership, a trial, a board change, a newer quarterly report) puts the company in the re-check queue for the gates that news bears on. The tier shown stays until that re-check is done.</p>
    <div class="calls">{cards}</div>
    <h3 class="bucket-h">Next for Serenity analysis</h3>
    <p class="bucket-blurb">Material news this week, no Serenity analysis yet. The gates column says what the analysis must re-check first.</p>
    <div class="table-wrap"><table><thead><tr><th>Ticker</th><th class="n">News signal</th><th>What changed</th><th>Gates to analyse</th></tr></thead><tbody>{queue_rows(awaiting)}</tbody></table></div>
    {f'<h3 class="bucket-h">Negative news, re-analysis needed</h3><div class="table-wrap"><table><thead><tr><th>Ticker</th><th class="n">News signal</th><th>What changed</th><th>Gates to re-check</th></tr></thead><tbody>{queue_rows(warnings_)}</tbody></table></div>' if warnings_ else ''}
    <p class="note">News events are classified by keyword rules, so some headlines are misread; each links to its source. Serenity verdicts come from memos that quote 10-K, 20-F and 10-Q text. {citation_note} Sizing tiers describe what the skills imply and are not advice.</p>
  </section>"""
    tickets = {t["ticker"]: t for t in load(root / "state/order-tickets.json", {}).get("tickets", [])}
    gate_states = {r["ticker"]: r.get("gateStates") for r in load(root / "state/serenity-gate-results.json", {}).get("companies", [])}
    picks_html = ""
    for key, label, blurb in BUCKETS:
        rows_in = payload["picks"].get(key, [])
        if not rows_in:
            continue
        extra = ""
        if key == "asymmetric" and payload.get("screen") and payload["screen"].get("queue"):
            names = ", ".join(q["ticker"] for q in payload["screen"]["queue"] if q.get("capBand", "").startswith("Sweet spot"))[:200]
            extra = f'<p class="note">Sweet-spot names found by the market-wide screen but not reviewed yet, such as {esc(names)}, can only join this bucket after a Serenity review.</p>'
        picks_html += f'<h3 class="bucket-h" id="bucket-{key}">{esc(label)}</h3><p class="bucket-blurb">{esc(blurb)}</p>{extra}<div class="picks">{"".join(card(r, tickets.get(r["ticker"]), gate_states.get(r["ticker"])) for r in rows_in)}</div>'
    choke_html = ""
    cp = payload.get("chokepoints")
    if cp and cp.get("nodes"):
        nodes = [n for n in cp["nodes"] if n["aiMedicineDependents"]][:8]
        node_rows = ""
        for n in nodes:
            share = f"{n['dependenceShare']:.0%}" if n.get("dependenceShare") is not None else "—"
            links = ", ".join(
                f'<a href="{esc(e["filing"]["url"])}" target="_blank" rel="noopener">{esc(e["ticker"])}</a>'
                for e in n["examples"] if e.get("inAiUniverse") and e.get("filing")
            )
            node_rows += (
                f'<tr><td>{esc(n["layer"])}</td><td><strong>{esc(n["supplier"])}</strong></td><td class="tk">{esc(n["ticker"] or "—")}</td>'
                f'<td class="n">{n["aiMedicineDependents"]}</td><td class="n">{n["healthDependents"]}</td><td class="n">{share}</td>'
                f'<td style="white-space:normal">{links}</td></tr>'
            )
        others = "".join(f"<li><strong>{esc(b['name'])}.</strong> {esc(b['evidence'])}</li>" for b in cp.get("nonCompanyBottlenecks", []))
        choke_html = f"""
  <section class="section" aria-labelledby="choke-h">
    <h2 id="choke-h">Where the bottlenecks are</h2>
    <p>The chokepoint skill says to look past the obvious beneficiary to what it cannot route around. Health companies disclose that dependence in their risk factors, so the agent searched filings for each upstream supplier named next to “sole supplier” or “single source”.</p>
    <div class="table-wrap"><table><thead><tr><th>Layer</th><th>Supplier</th><th>US ticker</th><th class="n">AI-medicine filers</th><th class="n">All health filers</th><th class="n">Dependence wording</th><th>AI-medicine examples</th></tr></thead><tbody>{node_rows}</tbody></table></div>
    <p class="note">Search has no proximity operator, so a supplier and “sole supplier” can sit in different paragraphs of one filing. Treat these as leads for the supply-chain gate and open the filing to check. Dependence wording is the share of all filings naming the supplier that also use sole/single-source language; around half is typical for health filings, so only clearly higher or lower values say much. Illumina stands out: it was left out of the original candidate list as not AI-native, yet AI diagnostics companies name it as a critical supplier, which makes it a chokepoint candidate for review.</p>
    <ul class="plain-list">{others}</ul>
  </section>"""
    rows = []
    for r in payload["ranking"]:
        p = r["potential"]["parts"]
        flag = "Serenity review pending; cannot be picked" if not r.get("serenityReviewed") else "Open event" if r["openEvents"] else ("Evidence incomplete" if r["lowEvidence"] else "")
        rows.append(
            f'<tr class="{"is-top" if r.get("pick") else ""}"><td class="n">{r["rank"]}</td><td class="tk">{esc(r["ticker"])}</td><td>{esc(r["company"])}</td><td>{esc(bucket_label.get(r["bucket"], "Micro cap"))}</td>'
            f'<td class="n"><strong>{r["potential"]["total"]:.1f}</strong></td><td class="n">{p["moat"]:.0f}</td><td class="n">{p["exposure"]:.0f}</td><td class="n">{p["growth"]:.0f}</td><td class="n">{p["durability"]:.0f}</td>'
            f'<td class="n">{r["evidence"]}</td><td>{esc(flag)}</td></tr>'
        )
    for r in payload["benchmarks"]:
        rows.append(f'<tr><td class="n">–</td><td class="tk">{esc(r["ticker"])}</td><td>{esc(r["company"])}</td><td>Benchmark</td><td colspan="7">{esc(r["benchmarkReason"])}</td></tr>')
    screened = ", ".join(f'{esc(s["ticker"])}' for s in payload["screenedOut"])
    f = payload["funnel"]
    gap_note = ""
    if len(top) >= 2:
        close = []
        for key, _, _ in BUCKETS:
            members = [r for r in payload["ranking"] if r["bucket"] == key][:PICKS_PER_BUCKET + 1]
            close += [f'{a["ticker"]}/{b["ticker"]}' for a, b in zip(members, members[1:]) if a["potential"]["total"] - b["potential"]["total"] < SCORE_NOISE]
        if close:
            gap_note = f"Pairs within {SCORE_NOISE} points ({', '.join(close)}) are effectively tied; read the order inside a pair as a coin flip."
    low = [r for r in top if r["lowEvidence"]]
    low_note = (
        f"<p><strong>{', '.join(r['ticker'] for r in low)}</strong> ranks high on potential but less than half of the required evidence is verified yet. "
        "It stays on the list with a flag rather than being promoted or dropped.</p>" if low else ""
    )
    generated = payload["generatedAt"][:10]
    sc = payload.get("screen")
    if sc and sc.get("funnel"):
        sf = sc["funnel"]
        steps = [(sf["filersFound"], "SEC filers using AI-medicine language"), (sf["healthOperating"], "Health operating companies"),
                 (sf["ownProduct"], "AI is their own product"), (sf["investable"], "Investable (cap ≥ $300M, liquid)"),
                 (sf["shortlist"], "Deep-review queue"), (f["deepReviewed"], "Reviewed in depth so far"), (f["top"], "Top picks")]
    else:
        steps = [(f["screened"], "Companies screened"), (f["deepReviewed"], "Reviewed in depth"), (f["ranked"], "Ranked as AI-medicine companies"), (f["top"], "Top picks")]
    funnel_html = "".join(f"<div><strong>{n:,}</strong><span>{esc(label)}</span></div>" for n, label in steps)
    queue_html = ""
    if sc:
        queue_rows = "".join(
            f'<tr><td class="tk">{esc(q["ticker"])}</td><td>{esc(q["company"])}</td><td>{esc(q["segment"])}</td><td class="n">{q["fdaAiDevices"]}</td>'
            f'<td class="n">{money(q["marketCapM"])}</td><td>{esc(q["capBand"])}</td><td>{esc(q["bucketHint"])}</td></tr>'
            for q in sc["queue"]
        )
        not_found = ", ".join(sc["notFound"])
        sq = payload.get("serenityQueue")
        queue_html = (
            f'<h3 style="font-size:20px">Next in line for Serenity review</h3>'
            f'<p>The market-wide screen (SEC filings to {esc(sc["asOf"])}) found these investable companies that describe AI as their own product but have not been reviewed in depth yet. '
            "The Serenity market-cap band and bucket follow the stock-selection skill: $400M–$5B is its sweet spot for asymmetric upside."
            + (f" Evidence packets for {sq['queued']} of them (SEC financial data, FDA records, news) are ready for the same eight-gate review; none is graded until that review is done." if sq and sq.get("queued") else "")
            + "</p>"
            '<div class="table-wrap"><table><thead><tr><th>Ticker</th><th>Company</th><th>Main segment</th><th class="n">FDA AI devices</th><th class="n">Market cap</th>'
            f'<th>Serenity cap band</th><th>Bucket hint</th></tr></thead><tbody>{queue_rows}</tbody></table></div>'
            + (f"<p>Reviewed companies the strict screen did not find: <strong>{esc(not_found)}</strong>. The screen's phrases missed them; where a Serenity review has quoted the 10-K's AI description, "
               "the card says so and notes whether AI is core or auxiliary.</p>" if not_found else "")
        )
    return f"""<meta charset="utf-8">
<title>Who Leads AI Medicine by 2035?</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>{STYLE}{radar_css}</style>
<main class="page">
  <header class="intro">
    <p class="eyebrow">AI Medicine · 5–10 year view · Serenity research agent</p>
    <h1>Who leads AI medicine by 2035?</h1>
    {freshness_section(root)}
    {status_line}
    <p class="lede">Which AI-medicine companies have the highest potential over the next 5 to 10 years, and why? The answer below comes from one pipeline: frontier news finds the companies, Serenity reads their SEC filings and tests whether each controls something the industry cannot route around, market data checks whether that is already in the price, and every call is frozen so it can be scored later. The two groups follow the Serenity stock-selection skill: durable compounders and asymmetric upside.</p>
    <div class="answers">{answer}</div>
    {long_term_html}
    {'<p class="meta"><a href="#radar">How the agent spots the next theme early, tested on COVID-19 and mpox →</a></p>' if radar_html else ''}
    {'<p class="meta"><a href="#track">Track record: frozen calls scored on real trading days →</a></p>' if track_html else ''}
    <div class="meta"><span>Prices as of {esc(payload['priceDate'] or generated)}</span>{f"<span>5-year scenarios set {esc(payload['scenarioDate'])}</span>" if payload.get('scenarioDate') else ''}<span>Financials: latest reported quarter</span><span>Updated daily by the research agent</span><span>Research only, not investment advice</span></div>
  </header>

{tailwind_section(root)}
{pipeline_html}
  <section class="section" aria-labelledby="map-h">
    <h2 id="map-h">Potential and proof, kept separate</h2>
    <div class="map-wrap">
      <div class="map-box">{scatter_svg(payload['ranking'])}</div>
      <div class="reading">
        <p><strong>Potential</strong> (up) ranks the companies: moat, how central AI is to the business, proven growth and financial durability.</p>
        <p><strong>Evidence confidence</strong> (right) measures how much of that view is backed by primary sources the agent has verified, such as filings, FDA records and quoted company disclosures.</p>
        {low_note}
        <p>{esc(gap_note)}</p>
      </div>
    </div>
  </section>

  <section class="section" aria-labelledby="picks-h">
    <h2 id="picks-h">The picks, in two buckets</h2>
    <p>The Serenity stock-selection skill sorts ideas into durable compounders and asymmetric upside, and prefers the $400M–$5B range where it sees the edge. One ranking across all sizes would favour large platforms, so each bucket is ranked on its own with the same potential score. Only companies with a current, citation-checked Serenity review can be picked, and for them moat, AI exposure and proven growth come from their gate results.</p>
    {picks_html}
  </section>

{tickets_section(root)}

  <section class="section" aria-labelledby="rank-h">
    <h2 id="rank-h">Full ranking</h2>
    <div class="funnel">{funnel_html}</div>
    <div class="table-wrap"><table>
      <thead><tr><th class="n">#</th><th>Ticker</th><th>Company</th><th>Bucket</th><th class="n">Potential</th><th class="n">Moat /35</th><th class="n">AI exposure /20</th><th class="n">Growth /30</th><th class="n">Durability /15</th><th class="n">Evidence</th><th>Flag</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table></div>
    <p>Screened out before deep review: {screened}. These are strong businesses, but AI medicine is not the core of their equity story.</p>
    {queue_html}
  </section>

{news_html}
{early_signals_section(root)}
{commercialization_chain_section(root)}
{management_radar_section(root)}
{candidate_filter_section(root)}
{blind_test_section(root)}
{opinion_benchmark_section(root)}
{small_caps_section(root)}
{deals_section(root)}
{lab_to_company_section(root)}
{diagnostics_section(root)}
{funds_section(root)}
{fda_crl_section(root)}
{key_people_section(root)}
{biodefense_section(root)}
{choke_html}
{radar_html}
{track_html}
  <section class="section" aria-labelledby="method-h">
    <h2 id="method-h">How this is built</h2>
    <div class="method">
      <section>
        <h4>Every day</h4>
        <ul>
          <li><strong>Read the news.</strong> One news search per covered company plus health, WHO and preprint feeds; each article becomes a classified event with direction, importance and the gates it bears on.</li>
          <li><strong>Collect.</strong> News, FDA AI-device records{f" ({payload['fdaTotalDevices']:,} tracked)" if payload.get('fdaTotalDevices') else ''}, ClinicalTrials.gov changes, SEC filings and insider trades, each stamped with when it was first known.</li>
          <li><strong>Map.</strong> Link each item to the companies it affects, even when the ticker is never named.</li>
          <li><strong>Test.</strong> Serenity gates check supply-chain position, customer dependence, earnings and the counter-thesis. A model's citation is accepted only if the quoted text is found word-for-word in the source.</li>
          <li><strong>Re-check.</strong> A material event reopens the affected gates. It can never upgrade a company on its own.</li>
        </ul>
      </section>
      <section>
        <h4>How we will know if we are wrong</h4>
        <ul>
          <li>Every daily view is frozen on the day it is made and scored later against XBI, XLV, SPY, a random pick and a plain momentum strategy.</li>
          <li>Each pick lists falsifiers. When one triggers, the company is re-reviewed.</li>
          <li><strong>Limits today:</strong> for Serenity-reviewed companies, five dimension scores come from evidence-gate results by a fixed rule, and financial durability is a judgement on reported cash, debt and losses; the rule is not yet calibrated. Tracking began in November 2026, so there is no long track record yet.</li>
        </ul>
      </section>
    </div>
  </section>

  <footer>Generated {esc(generated)} from the research agent's daily outputs. Potential = Moat 35 + AI-medicine exposure 20 + Proven growth 30 + Financial durability 15. Research and education only; not a recommendation to buy or sell any security.</footer>
</main>
"""


def render_markdown(payload: dict) -> str:
    lines = [
        "# AI Medicine: 5–10 Year Leaders", "",
        f"> {payload['question']} Research only, not investment advice. Data as of {payload['priceDate']}.", "",
        "| # | Ticker | Company | Potential | Evidence | Flag |", "| ---: | --- | --- | ---: | ---: | --- |",
    ]
    for r in payload["ranking"]:
        flag = "open event" if r["openEvents"] else ("evidence incomplete" if r["lowEvidence"] else "")
        lines.append(f"| {r['rank']} | {r['ticker']} | {r['company']} | {r['potential']['total']:.1f} | {r['evidence']} | {flag} |")
    for r in payload["top"]:
        lines += ["", f"## {r['rank']}. {r['ticker']} — {r['company']}", "", f"**Chokepoint:** {r['chokepoint']}", "",
                  f"**Why it can win:** {r['thesis']}", "", f"**Why now:** {r['whyNow']}", "",
                  f"**Strongest case against:** {r['bearCase']}", "", "**We are wrong if:**"]
        lines += [f"- {item}" for item in r["falsifiers"]]
        lines += ["", "Sources: " + ", ".join(r["sources"])]
    lines += ["", "Potential = Moat 35 + AI-medicine exposure 20 + Proven growth 30 + Financial durability 15. Evidence = Serenity gate completeness and evidence quality.", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the AI Medicine 5-10 year leaders brief")
    parser.add_argument("--json-output", default=str(ROOT / "state/ai-medicine-top5.json"))
    parser.add_argument("--markdown-output", default=str(ROOT / "outputs/ai-medicine-top5.md"))
    parser.add_argument("--html-output", default=str(ROOT / "dashboard/dist/top5.html"))
    args = parser.parse_args()
    payload = build()
    for path, text in (
        (args.json_output, json.dumps(payload, indent=2, ensure_ascii=False)),
        (args.markdown_output, render_markdown(payload)),
        (args.html_output, render_html(payload)),
    ):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text, encoding="utf-8")
    print(json.dumps({"top": [r["ticker"] for r in payload["top"]], "html": args.html_output}))


if __name__ == "__main__":
    main()
