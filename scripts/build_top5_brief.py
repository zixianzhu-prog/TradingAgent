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
from datetime import datetime, timezone
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


def build(root: Path = ROOT) -> dict:
    universe = {row["ticker"]: row for row in load(root / "trend-agent/ai-medicine-universe.json")["companies"]}
    thesis_file = load(root / "trend-agent/ai-medicine-theses.json")
    theses = {row["ticker"]: row for row in thesis_file["candidates"] + thesis_file.get("expanded_deep_dives", [])}
    financials = {row["ticker"]: row for row in load(root / "state/ai-medicine-financial-scenarios.json")["companies"]}
    gates = {row["ticker"]: row for row in load(root / "state/serenity-gate-results.json")["companies"]}
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
                "marketCapM": financial.get("market_cap_m"),
                "priceToSales": financial.get("price_to_sales_approx"),
                "priceDate": financial.get("price_date"),
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
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "question": "Which AI-medicine companies have the highest potential over the next 5-10 years, and why?",
        "weights": WEIGHTS,
        "scoreNoise": SCORE_NOISE,
        "lowEvidenceThreshold": LOW_EVIDENCE,
        "priceDate": price_dates[-1] if price_dates else None,
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
               "disclosure": "SEC disclosure", "filing": "SEC filing"}


def event_item(event: dict) -> str:
    tone = "ok" if event.get("direction", 0) > 0 else "alert" if event.get("direction", 0) < 0 else "plain"
    arrow = "▲" if event.get("direction", 0) > 0 else "▼" if event.get("direction", 0) < 0 else "•"
    outlets = len(event.get("sources", []))
    return (f'<li class="news-item"><span class="chip {tone}">{arrow} {esc(EVENT_LABEL.get(event.get("type"), event.get("type")))}</span> '
            f'<a href="{esc(event.get("url"))}" target="_blank" rel="noopener">{esc(event.get("title"))}</a> '
            f'<span class="news-meta">{esc((event.get("at") or "")[:10])} · {outlets} outlet{"s" if outlets != 1 else ""}</span></li>')


def card(row: dict) -> str:
    n = row["numbers"]
    stats = [
        (f"{n['period']} revenue" if n["period"] else "Quarterly revenue", money(n["quarterlyRevenueM"])),
        ("Revenue growth", f"{n['revenueGrowthPct']:+.0f}% YoY" if n["revenueGrowthPct"] is not None else "n/a"),
        ("Market cap", money(n["marketCapM"])),
        ("Price / sales", f"{n['priceToSales']:.1f}x" if n["priceToSales"] else "n/a"),
    ]
    if row.get("fdaAiDevices"):
        stats.append(("FDA AI devices", str(row["fdaAiDevices"])))
    chips = []
    if row["lowEvidence"]:
        chips.append('<span class="chip warn">Evidence incomplete</span>')
    if row["openEvents"]:
        chips.append('<span class="chip alert">Open event</span>')
    if row.get("aiUnverified"):
        chips.append('<span class="chip warn">AI not confirmed by market screen</span>')
    elif row.get("aiConfirmedInFilings"):
        chips.append('<span class="chip plain">AI confirmed in filings, not core</span>')
    if not chips:
        chips.append('<span class="chip ok">Evidence on file</span>')
    falsifiers = "".join(f"<li>{esc(item)}</li>" for item in row["falsifiers"])
    sources = "".join(
        f'<li><a href="{esc(url)}" rel="noopener" target="_blank">{esc(url.split("/")[2] if "//" in url else url)}</a></li>'
        for url in row["sources"]
    )
    v = row.get("serenityVerdict")
    serenity_block = (f'<div class="news-block"><h4>Serenity analysis</h4><p class="via-theme"><strong>{esc(v.get("tier", ""))}</strong> · chokepoint: {esc(v.get("chokepoint", ""))}. '
                      f'{esc(v.get("verdict", ""))} Counters that hold: {esc("; ".join(v.get("countersHolding", [])))}.</p></div>' if v else
                      '<div class="news-block"><h4>Serenity analysis</h4><p class="via-theme">Not done yet for this company.</p></div>')
    news_block = (f'<div class="news-block"><h4>In the news, last two weeks</h4><ul class="news-list">{"".join(event_item(e) for e in row.get("newsEvents", []))}</ul></div>'
                  if row.get("newsEvents") else "")
    events = "".join(f"<li>{esc(event['title'])}</li>" for event in row["openEvents"])
    events_block = f'<div class="events"><h4>Unresolved before upgrading</h4><ul>{events}</ul></div>' if events else ""
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
  <p class="angle">{esc(row['chokepoint'])}</p>
  <div class="chips">{''.join(chips)}</div>
  {serenity_block}
  {news_block}
  <dl class="stats">{''.join(f'<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>' for k, v in stats)}</dl>
  <div class="pick-body">
    <section>
      <h4>Why it can win</h4>
      <p>{esc(row['thesis'])}</p>
      <h4>Why now</h4>
      <p>{esc(row['whyNow'])}</p>
      <div class="dims">{bars(row['potential']['parts'])}</div>
    </section>
    <section class="against">
      <h4>Strongest case against</h4>
      <p>{esc(row['bearCase'])}</p>
      <h4>We are wrong if</h4>
      <ul>{falsifiers}</ul>
      {events_block}
      <h4>Sources</h4>
      <ul class="sources">{sources}</ul>
    </section>
  </div>
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
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin:0}
.stats div{background:var(--card);padding:10px 12px}
.stats dt{font-size:11px;color:var(--muted)}
.stats dd{margin:2px 0 0;font-weight:700;font-variant-numeric:tabular-nums}
.pick-body{display:grid;grid-template-columns:1fr 1fr;gap:28px}
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
    <p>The five picks answer who leads today. The agent also watches health news, WHO and preprint servers for topics that suddenly gain attention, with no preset themes, then finds the listed companies involved through SEC filings and trial registrations and checks whether their stocks have already reacted. It uses no language model, so it can be replayed on past dates without knowing what happened next.</p>
    <h3 style="font-size:20px">Time-machine test</h3>
    {''.join(radar.replay_card(c) for c in cases) or '<p class="empty">No replay has been run yet.</p>'}
    <h3 style="font-size:20px">Today</h3>
    <p>{jumping} topic{'s' if jumping != 1 else ''} jumping, {confirmed} confirmed. A topic is confirmed when it jumps on two days within a week with new articles; only confirmed topics are mapped to companies. The radar covers every field, so non-medical news can appear here.</p>
    {today}
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
            'summary, and every quote is matched word for word before the gate can move. Both examples below looked like good news in a headline.</p>'
            f'<div class="calls">{"".join(items)}</div>')


def tier_word(row: dict) -> str:
    tier = ((row.get("serenityVerdict") or {}).get("tier") or "").lower()
    return "standard tier" if "standard" in tier else "starter tier" if "starter" in tier else "not reviewed"


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
    <p class="note">Horizons longer than one session overlap, so neighbouring observations are not independent. Full tables, rank IC and bootstrap intervals: <code>outputs/agent-benchmark-validation.md</code> and <code>outputs/investment-score-performance.md</code>.</p>
  </section>"""


def render_html(payload: dict, root: Path = ROOT) -> str:
    status = load(root / "state/serenity-review-status.json", {})
    st = status.get("summary", {})
    status_line = (
        f'<p class="status-banner"><strong>Status: no company has passed every Serenity gate.</strong> '
        f'Serenity reviews on today\'s evidence: {st.get("current", 0)}; evidence changed since review: {st.get("stale", 0)}; '
        f'not reviewed yet: {st.get("notReviewed", 0)}. Claude memos are research views until their quotes pass the citation check '
        f'({st.get("claudeChecked", 0)} of {st.get("claudePending", 0) + st.get("claudeChecked", 0)} checked). Tiers below are next research steps, not buy decisions.</p>'
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
        f'<td>{esc(r["longTerm"]["counter"])}</td><td>{market_cell(mv.get(r["ticker"]))}</td><td>{esc(r["longTerm"]["next_check"])}</td></tr>'
        for key, label, _ in BUCKETS for r in payload["picks"].get(key, []) if r.get("longTerm"))
    long_term_html = (f'<div class="table-wrap long-term"><table><caption>Why these six could lead by 2035, what could stop them, what the market says today, and what we check next</caption>'
                      f'<thead><tr><th>Ticker</th><th>Why it could win (Serenity)</th><th>Biggest counter (Serenity)</th><th>Market check (OpenBB, Kronos; context only)</th><th>Next check</th></tr></thead><tbody>{lt_rows}</tbody></table></div>') if lt_rows else ""
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

        def serenity_card(c):
            v = c["serenity"] or {}
            label, tone = TIER_LABEL.get(c["decision"], ("Serenity", "plain"))
            counters = "".join(f"<li>{esc(x)}</li>" for x in v.get("countersHolding", []))
            gates = ", ".join(g.replace("_", " ") for g in c["gatesToRecheck"]) or "none"
            return (f'<article class="call"><header class="call-head"><h3><span class="ticker">{esc(c["ticker"])}</span> {esc(c["company"])}</h3>'
                    f'<span class="chip {tone}">{esc(label)}</span></header>'
                    + (lambda r: f'<p class="call-foot">Claude memo: <strong>{esc(r.get("claudeMemo") or "none")}</strong> · first-round review: <strong>{esc(r.get("review", "none"))}</strong></p>')(review_of.get(c["ticker"], {}))
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
            covered = ", ".join(f'{esc(x["ticker"])} {x["strength"]:.0%}' for x in t["covered"][:6]) or "—"
            new_names = ", ".join(esc(x["ticker"]) for x in t["uncovered"]) or "—"
            state = '<span class="chip ok">Heating up</span>' if t["material"] else '<span class="chip plain">Early</span>'
            theme_rows += (f'<tr><td><strong>{esc(t["label"])}</strong><br>{state}</td><td class="n">{t["articles"]}</td><td class="n">{t["heat"]:+.1f}</td>'
                           f'<td style="white-space:normal;min-width:280px"><ul class="news-list">{heads}</ul></td><td style="white-space:normal">{covered}</td><td>{new_names}</td></tr>')
        themes_html = (
            '<h3 class="bucket-h">What the frontier news is about</h3>'
            '<p class="bucket-blurb">Articles that name no company (new models, papers, policy, funding rounds) are grouped into AI-medicine topics. '
            'Heat compares the last 7 days with the weekly average of the three weeks before, so a topic that is always discussed does not count; only one heating up does. '
            'Each topic then reaches the companies whose own SEC filings describe that work, weighted by how strongly.</p>'
            '<div class="table-wrap"><table><thead><tr><th>Topic</th><th class="n">Articles, 7 days</th><th class="n">Heat</th><th>Examples</th>'
            f'<th>Covered companies (exposure)</th><th>New names to look at</th></tr></thead><tbody>{theme_rows}</tbody></table></div>'
        ) if theme_rows else ""
        cards = "".join(serenity_card(c) for c in analysed) or '<p class="empty">No news-triggered company has a Serenity analysis yet.</p>'
        news_html = f"""
  <section class="section" id="news" aria-labelledby="news-h">
    <h2 id="news-h">This week: frontier news, then Serenity</h2>
    <p>The news does not decide anything. It shows what changed and for whom: news that names a company becomes an event (FDA, reimbursement, partnership, clinical data, earnings, lawsuits), and frontier news that names no company is mapped to the companies whose own filings describe that work. Each change is then handed to a Serenity analysis that applies three core Serenity skills to primary filings through eight evidence gates: map the supply chain, test for a chokepoint, check customer dependence, stress-test the counter-thesis and set validation gates. <strong>The Serenity tier is a research view, not a trade.</strong> A company with material news but no Serenity analysis yet waits in the queue below instead of being rated on news alone.</p>
    {themes_html}
    {fda_block(root)}
    {recheck_block(root)}
    <h3 class="bucket-h">News-triggered companies with a Serenity verdict</h3>
    <div class="calls">{cards}</div>
    <h3 class="bucket-h">Next for Serenity analysis</h3>
    <p class="bucket-blurb">Material news this week, no Serenity analysis yet. The gates column says what the analysis must re-check first.</p>
    <div class="table-wrap"><table><thead><tr><th>Ticker</th><th class="n">News signal</th><th>What changed</th><th>Gates to analyse</th></tr></thead><tbody>{queue_rows(awaiting)}</tbody></table></div>
    {f'<h3 class="bucket-h">Negative news, re-analysis needed</h3><div class="table-wrap"><table><thead><tr><th>Ticker</th><th class="n">News signal</th><th>What changed</th><th>Gates to re-check</th></tr></thead><tbody>{queue_rows(warnings_)}</tbody></table></div>' if warnings_ else ''}
    <p class="note">News events are classified by keyword rules, so some headlines are misread; each links to its source. Serenity verdicts come from memos that quote 10-K, 20-F and 10-Q text. {citation_note} Sizing tiers describe what the skills imply and are not advice.</p>
  </section>"""
    picks_html = ""
    for key, label, blurb in BUCKETS:
        rows_in = payload["picks"].get(key, [])
        if not rows_in:
            continue
        extra = ""
        if key == "asymmetric" and payload.get("screen") and payload["screen"].get("queue"):
            names = ", ".join(q["ticker"] for q in payload["screen"]["queue"] if q.get("capBand", "").startswith("Sweet spot"))[:200]
            extra = f'<p class="note">Sweet-spot names found by the market-wide screen but not reviewed yet, such as {esc(names)}, can only join this bucket after a Serenity review.</p>'
        picks_html += f'<h3 class="bucket-h" id="bucket-{key}">{esc(label)}</h3><p class="bucket-blurb">{esc(blurb)}</p>{extra}<div class="picks">{"".join(card(r) for r in rows_in)}</div>'
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
    {status_line}
    <p class="lede">Peter's question: which AI-medicine companies have the highest potential over the next 5 to 10 years, and why? The answer below comes from one pipeline: frontier news finds the companies, Serenity reads their SEC filings and tests whether each controls something the industry cannot route around, market data checks whether that is already in the price, and every call is frozen so it can be scored later. The two groups follow the Serenity stock-selection skill: durable compounders and asymmetric upside.</p>
    <div class="answers">{answer}</div>
    {long_term_html}
    {'<p class="meta"><a href="#radar">How the agent spots the next theme early, tested on COVID-19 and mpox →</a></p>' if radar_html else ''}
    {'<p class="meta"><a href="#track">Track record: frozen calls scored on real trading days →</a></p>' if track_html else ''}
    <div class="meta"><span>Data as of {esc(payload['priceDate'] or generated)}</span><span>Financials: latest reported quarter</span><span>Updated daily by the research agent</span><span>Research only, not investment advice</span></div>
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
          <li><strong>Limits today:</strong> dimension scores are analyst judgments (1–5) tied to cited sources; growth uses reported figures. Tracking began in November 2026, so there is no long track record yet.</li>
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
