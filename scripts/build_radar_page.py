"""Build the Emerging Signal Radar page (dashboard/dist/radar.html).

Shows, from the pipeline's own outputs:
- today's signals from the no-preset-theme detector, and which are confirmed;
- for confirmed topics, the companies found in SEC filings and trial registrations,
  with the priced-in check;
- time-machine replays, the miss as prominently as the hit.
"""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

from build_top5_brief import STYLE as BASE_STYLE, esc

ROOT = Path(__file__).resolve().parents[1]
CASE_NAMES = {"covid-2020": "COVID-19 · January 2020", "mpox-2022": "Mpox · May–June 2022"}
VERDICT = {"early": ("Early", "ok"), "partly priced": ("Partly priced", "warn"), "heavily priced": ("Heavily priced", "alert"), "no data": ("No data", "")}
HORIZONS = ("30", "90", "180", "365")

EXTRA_STYLE = """
:root{--bar:#0b7a55}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bar:#3fa877}}
:root[data-theme="dark"]{--bar:#3fa877}
.status-line{display:flex;flex-wrap:wrap;gap:8px 22px;font-size:12px;color:var(--muted)}
.empty{background:var(--card);border:1px dashed var(--line);padding:18px 20px;color:var(--muted);max-width:75ch}
.case{background:var(--card);border:1px solid var(--line);padding:26px;display:grid;gap:18px}
.case-head{display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px;align-items:baseline}
.case-head h3{font-size:24px}
.facts{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);margin:0}
.facts div{background:var(--card);padding:10px 12px}
.facts dt{font-size:11px;color:var(--muted)} .facts dd{margin:2px 0 0;font-weight:700;font-variant-numeric:tabular-nums}
.chart-box{overflow-x:auto}
.counts{width:100%;min-width:560px;height:auto;display:block}
.counts .bar{fill:var(--bar)} .counts .bar:hover{opacity:.8}
.counts .grid{stroke:var(--line)} .counts .tick{fill:var(--muted);font:11px var(--sans);font-variant-numeric:tabular-nums}
.counts .fire{fill:var(--ink)} .counts .fire-label{fill:var(--ink);font:600 11px var(--sans)}
.counts .axis-label{fill:var(--muted);font:12px var(--sans)}
.note{font-size:13px;color:var(--muted);max-width:75ch}
.chip.plain{background:var(--line);color:var(--ink)}
td.pos{color:var(--green)} td.neg{color:var(--red)}
"""


def load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def pct(value) -> str:
    return f"{value:+.0%}" if value is not None else "—"


def signed_cell(value) -> str:
    cls = "pos" if value is not None and value > 0 else "neg" if value is not None and value < 0 else ""
    return f'<td class="n {cls}">{pct(value)}</td>'


def verdict_chip(row: dict | None) -> str:
    label, cls = VERDICT.get((row or {}).get("verdict", "no data"), ("—", ""))
    return f'<span class="chip {cls or "plain"}">{label}</span>'


def counts_chart(truth: dict, start: str, end: str, confirmed: str | None) -> str:
    """Daily article count for the expected term, one bar per day, fired days marked above."""
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    days = [(first + timedelta(days=i)).isoformat() for i in range((last - first).days + 1)]
    counts = [truth["dailyCounts"].get(day, 0) for day in days]
    fired = set(truth.get("firedOn", []))
    top = max(4, max(counts, default=0))
    step = 2 if top <= 8 else 5
    top = ((top + step - 1) // step) * step
    width, height, left, right, top_pad, bottom = 720, 220, 40, 12, 34, 34
    plot_w, plot_h = width - left - right, height - top_pad - bottom
    slot = plot_w / len(days)
    bar_w = max(2.0, slot - 2)  # 2px surface gap between bars
    y = lambda v: top_pad + plot_h - v / top * plot_h
    parts = [f'<svg class="counts" viewBox="0 0 {width} {height}" role="img" aria-label="Daily articles mentioning {esc(truth["term"])}">']
    for tick in range(0, top + 1, step):
        parts.append(f'<line class="grid" x1="{left}" x2="{width - right}" y1="{y(tick):.1f}" y2="{y(tick):.1f}"/>')
        parts.append(f'<text class="tick" x="{left - 8}" y="{y(tick) + 4:.1f}" text-anchor="end">{tick}</text>')
    for i, (day, count) in enumerate(zip(days, counts)):
        x = left + i * slot + 1
        if count:
            h = plot_h * count / top
            radius = min(4, bar_w / 2, h)
            # Rounded data end at the top, square at the baseline.
            path = (f"M{x:.1f},{y(0):.1f} V{y(count) + radius:.1f} Q{x:.1f},{y(count):.1f} {x + radius:.1f},{y(count):.1f} "
                    f"H{x + bar_w - radius:.1f} Q{x + bar_w:.1f},{y(count):.1f} {x + bar_w:.1f},{y(count) + radius:.1f} V{y(0):.1f} Z")
            parts.append(f'<path class="bar" d="{path}"><title>{day}: {count} article{"s" if count != 1 else ""}{" · detector fired" if day in fired else ""}</title></path>')
        if day in fired:
            cx = x + bar_w / 2
            cy = y(count) - 9
            parts.append(f'<path class="fire" d="M{cx - 4:.1f},{cy - 4:.1f} L{cx + 4:.1f},{cy - 4:.1f} L{cx:.1f},{cy + 2:.1f} Z"><title>{day}: detector fired</title></path>')
            if day == confirmed:
                anchor = "end" if i > len(days) * 0.7 else "start"
                parts.append(f'<text class="fire-label" x="{cx + (-6 if anchor == "end" else 6):.1f}" y="{cy - 6:.1f}" text-anchor="{anchor}">confirmed {day[5:]}</text>')
    for i in range(0, len(days), 7):
        parts.append(f'<text class="tick" x="{left + i * slot + slot / 2:.1f}" y="{height - bottom + 16}" text-anchor="middle">{days[i][5:]}</text>')
    parts.append(f'<text class="axis-label" x="{left}" y="14">Preprints per day with “{esc(truth["term"])}” in the title · ▼ detector fired</text>')
    parts.append("</svg>")
    return "".join(parts)


def replay_card(case: dict) -> str:
    name = CASE_NAMES.get(case["case"], case["case"])
    det, truth, mapping = case.get("detection"), case.get("groundTruth") or {}, case.get("mapping") or {}
    pricing = (case.get("pricing") or {}).get("companies", {})
    outcomes, basket = case.get("outcomes") or {}, case.get("basket") or {}
    days = case.get("dailySignals", [])
    start, end = (days[0]["date"], days[-1]["date"]) if days else (None, None)
    chip = '<span class="chip ok">Caught</span>' if det else '<span class="chip warn">Missed · stayed silent</span>'
    facts = [
        ("First in the data", truth.get("firstInData") or "—"),
        ("Detector first fired", (det or {}).get("firstFired") or "never"),
        ("Confirmed", (det or {}).get("confirmed") or "—"),
        ("Candidates that day", str(len(mapping.get("candidates", []))) if det else "none"),
    ]
    html = [f'<article class="case"><div class="case-head"><h3>{esc(name)}</h3>{chip}</div>',
            f'<dl class="facts">{"".join(f"<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd></div>" for k, v in facts)}</dl>']
    if truth and start:
        html.append(f'<div class="chart-box">{counts_chart(truth, start, end, (det or {}).get("confirmed"))}</div>')
    if det:
        rows = []
        for c in mapping.get("candidates", []):
            ticker = c.get("ticker")
            outcome = outcomes.get(ticker) or {}
            rows.append(
                f'<tr><td class="tk">{esc(ticker or "—")}</td><td>{esc(c["company"])}</td><td>{esc(c["sicGroup"])}</td><td>{esc(c.get("firstFiled"))}</td>'
                f'<td>{verdict_chip(pricing.get(ticker))}</td>' + "".join(signed_cell(outcome.get(f"r{h}")) for h in HORIZONS) + "</tr>"
            )
        bench = case.get("benchmark", "XBI")
        bench_row = outcomes.get(bench) or {}
        rows.append(f'<tr><td class="tk">{esc(bench)}</td><td>Biotech benchmark</td><td></td><td></td><td></td>' + "".join(signed_cell(bench_row.get(f"r{h}")) for h in HORIZONS) + "</tr>")
        html.append(
            '<div class="table-wrap"><table><thead><tr><th>Ticker</th><th>Company</th><th>Sector</th><th>First in a filing</th>'
            '<th>Priced in that day?</th>' + "".join(f'<th class="n">+{h} days</th>' for h in HORIZONS) + f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
        )
        b365 = basket.get("365") or basket.get(365) or {}
        rated = [f"{t} {VERDICT.get(r.get('verdict'), ('—', ''))[0].lower()}" for t, r in pricing.items()]
        html.append(
            f'<p class="note">Bought the whole basket at the first close after confirmation. After a year it averaged {pct(b365.get("mean"))} '
            f'against {pct(b365.get("benchmark"))} for {esc(bench)}, with {b365.get("winners", 0)} of {b365.get("n", 0)} stocks ahead of the benchmark. '
            + (f"On the day, the priced-in check rated {esc(', '.join(rated))}. " if rated else "")
            + "A stock that has already moved can keep moving; the check describes the reaction so far, not the next one. One case does not prove a repeatable edge.</p>"
        )
    else:
        html.append(
            f'<p class="note">The first {esc(truth.get("term", "topic"))} preprint appeared on {esc(truth.get("firstInData") or "—")}, weeks after the news broke, '
            f'and never reached the confirmation bar ({truth.get("articlesInWindow", 0)} articles in the whole window). The detector stayed silent, so no basket was built. '
            "Preprints alone are too slow for outbreaks like this; news and WHO bulletins need to be added to the historical replay.</p>"
        )
    html.append("</article>")
    return "".join(html)


def signals_table(signals: list[dict]) -> str:
    rows = []
    for s in signals[:12]:
        state = '<span class="chip ok">Confirmed</span>' if s.get("confirmed") else '<span class="chip plain">One day</span>'
        kind = "New topic" if s.get("status") == "new-topic" else "Already tracked"
        headline = (s.get("headlines") or [{}])[0]
        link = f'<a href="{esc(headline.get("url"))}" target="_blank" rel="noopener">{esc(headline.get("title", "")[:90])}</a>' if headline.get("url") else esc(headline.get("title", ""))
        rows.append(
            f'<tr><td><strong>{esc(s["label"])}</strong></td><td>{state}</td><td>{kind}</td><td class="n">{s["recentArticles"]} / {s["baselineArticles"]}</td>'
            f'<td class="n">{s["burstRatio"]}×</td><td class="n">{s["sourceCount"]}</td><td style="white-space:normal;min-width:260px">{link}</td></tr>'
        )
    return ('<div class="table-wrap"><table><thead><tr><th>Topic</th><th>Status</th><th>Type</th><th class="n">Recent / baseline</th><th class="n">Jump</th>'
            f'<th class="n">Sources</th><th>Example headline</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def candidates_block(mapping: dict, pricing: dict) -> str:
    topics = [t for t in mapping.get("topics", []) if t.get("candidates")]
    if not topics:
        return ('<p class="empty">No confirmed topic needs company mapping today. When a topic is confirmed, the companies that mention it in SEC filings '
                "or trial registrations appear here with a priced-in check.</p>")
    by_topic = {r["topic"]: r["companies"] for r in pricing.get("results", [])}
    out = []
    for topic in topics:
        priced = by_topic.get(topic["topic"], {})
        rows = "".join(
            f'<tr><td class="tk">{esc(c.get("ticker") or "—")}</td><td>{esc(c["company"])}</td><td>{esc(c["sicGroup"])}</td><td>{esc(c.get("firstFiled"))}</td>'
            f'<td class="n">{c.get("announcements", 0)}</td><td>{verdict_chip(priced.get(c.get("ticker")))}</td></tr>'
            for c in topic["candidates"][:12]
        )
        out.append(f'<h3 style="font-size:20px">{esc(topic["topic"])}</h3><div class="table-wrap"><table><thead><tr><th>Ticker</th><th>Company</th><th>Sector</th>'
                   f'<th>First in a filing</th><th class="n">Announcements</th><th>Priced in?</th></tr></thead><tbody>{rows}</tbody></table></div>')
    return "".join(out)


def render(root: Path = ROOT) -> str:
    signals = load(root / "state/emerging-signals.json", {"signals": []})
    mapping = load(root / "state/beneficiary-map.json", {"topics": []})
    pricing = load(root / "state/pricing-check.json", {"results": []})
    cases = [load(path, None) for path in sorted((root / "state/replay").glob("*.json"))]
    cases = sorted([c for c in cases if c and "case" in c], key=lambda c: (c.get("detection") is None, c["case"]))
    confirmed = [s for s in signals.get("signals", []) if s.get("confirmed")]
    as_of = (signals.get("asOf") or "")[:10]
    articles = signals.get("articles", {})
    return f"""<meta charset="utf-8">
<title>Emerging Signal Radar</title>
<meta name="claude:viewport-fit-sides" content="cover">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>{BASE_STYLE}{EXTRA_STYLE}</style>
<main class="page">
  <header class="intro">
    <p class="eyebrow">Serenity research agent · no preset themes</p>
    <h1>Emerging signal radar</h1>
    <p class="lede">The agent watches health news, WHO and preprint servers for topics that suddenly gain attention across independent sources, then looks up which listed companies are actually involved and whether their stocks have already reacted. It uses no language model, so the same code can be replayed on any past date.</p>
    <div class="status-line"><span>As of {esc(as_of or '—')}</span><span>{articles.get('recent', 0)} articles in the last 3 days, {articles.get('baseline', 0)} in the 21-day baseline</span><span>{len(confirmed)} confirmed topic{'s' if len(confirmed) != 1 else ''} today</span></div>
  </header>

  <section class="section" aria-labelledby="today-h">
    <h2 id="today-h">Today</h2>
    <p>A topic is confirmed when it jumps on two days within a week and the second day brings new articles. One-day jumps are shown for context and are not mapped to companies.</p>
    {signals_table(signals.get('signals', [])) if signals.get('signals') else '<p class="empty">No topic is jumping today.</p>'}
    {candidates_block(mapping, pricing)}
  </section>

  <section class="section" aria-labelledby="replay-h">
    <h2 id="replay-h">Time-machine replays</h2>
    <p>Each replay puts the agent back on a past date. Every day it sees only preprints and filings published by then. The miss is shown next to the hit, because a detector that only gets judged on its famous wins proves nothing.</p>
    {''.join(replay_card(c) for c in cases) or '<p class="empty">No replay has been run yet.</p>'}
  </section>

  <section class="section" aria-labelledby="how-h">
    <h2 id="how-h">How it decides</h2>
    <div class="method">
      <section><h4>Finding companies</h4><ul>
        <li><strong>SEC filings</strong> dated on or before the day: a health company announcing something in an 8-K (items 7.01/8.01) is a candidate; a mention inside an earnings release (item 2.02) usually describes business disruption.</li>
        <li><strong>Trial registrations</strong> by industry sponsors on the topic add weight.</li>
        <li>Candidates still go through the Serenity screen. This is not a buy list.</li></ul></section>
      <section><h4>Priced in?</h4><ul>
        <li>Excess return against XBI since the signal and over the last 10 sessions, in units of the stock's normal daily volatility, plus volume against its 60-day norm.</li>
        <li><strong>Early</strong>: under 1σ and normal volume. <strong>Heavily priced</strong>: 3σ+, 50%+ excess, or 2σ with 4× volume.</li>
        <li>It says whether the market has reacted, not what happens next.</li></ul></section>
    </div>
  </section>

  <footer>Built from the agent's daily outputs: emerging signals, SEC full-text search, ClinicalTrials.gov and daily prices. Research only; not a recommendation to buy or sell any security.</footer>
</main>
"""


def main() -> None:
    out = ROOT / "dashboard/dist/radar.html"
    out.write_text(render(), encoding="utf-8")
    print(json.dumps({"html": str(out)}))


if __name__ == "__main__":
    main()
