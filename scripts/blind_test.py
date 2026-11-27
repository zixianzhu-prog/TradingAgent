"""Forward blind test: this agent against a plain web-search model and mechanical baselines, frozen weekly.

A backtest cannot be blind for a language model (it has read the outcome), so the test only runs forward.
Every week, before the Monday open, three groups give calls on the same universe (the deep-review queue):

* A  this agent: the order tickets (action, potential score as confidence, Serenity counter quotes as risks,
     the first invalidation condition as the falsifier).
* B  Claude Sonnet with web search and a standard prompt, no access to this project's data or rules. Same output
     format; may add up to five companies outside the universe.
* C  mechanical: the three cheapest names by price/sales are "buy"; XBI and random baskets are computed at scoring.

Calls are appended to outputs/blind-test-ledger.jsonl (committed, so git history proves they came first) and
B's raw answer is kept under outputs/blind-test/raw/. Scoring, as time passes:
* citation accuracy: each risk quote is fetched from its URL and searched for word for word;
* crash avoidance: names that fell 30%+ within 20 trading days, and whether each group was holding them;
* basket excess vs XBI at 5/20/60/120/250 trading days (buy + starter, equal weight), and A's percentile among
  1,000 random baskets of the same size from the same universe;
* rank IC: Spearman correlation of confidence with 20- and 60-day excess, averaged over weeks.

Criteria written down before the first week (docs/blind-research-benchmark.md): at 26 weeks A must beat B on
citation accuracy and crash avoidance; at 52 weeks A's 60-day IC must exceed 0.05 with t > 2. Otherwise the page
says the agent has not been shown to beat asking a model directly.

    python3 scripts/blind_test.py --freeze                                  # weekly, deep run
    PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/blind_test.py --score
    python3 scripts/blind_test.py --export-blind 2026-11-23                 # shuffled copy for human graders
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import random
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, pstdev
import claude_cli

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "outputs/blind-test-ledger.jsonl"
RAW = ROOT / "outputs/blind-test/raw"
GRADING = ROOT / "outputs/blind-test/grading"
KEYS = ROOT / "state/blind-test-keys.json"
RESULT = ROOT / "state/blind-test.json"
REPORT = ROOT / "outputs/blind-test.md"
CITE_CACHE = ROOT / "state/blind-test-citations.json"
TICKETS = ROOT / "state/order-tickets.json"
FILTER = ROOT / "state/candidate-filter.json"
CITATIONS = ROOT / "state/serenity-claude-citations.json"
BENCH = "XBI"
HORIZONS = (5, 20, 60, 120, 250)
CRASH, CRASH_DAYS = -0.30, 20
HOLD = {"buy", "starter"}
ACTIONS = ["buy", "starter", "wait", "avoid"]

_RISK = {"type": "object", "required": ["text", "url", "quote"], "properties": {
    "text": {"type": "string"}, "url": {"type": "string"},
    "quote": {"type": "string", "description": "exact words copied from the page at url"}}}
_CALL = {"type": "object", "required": ["ticker", "action", "confidence", "excess12m", "risks", "falsifier"], "properties": {
    "ticker": {"type": "string"}, "action": {"type": "string", "enum": ACTIONS},
    "confidence": {"type": "number", "description": "0-100, how strongly you hold this view"},
    "excess12m": {"type": "number", "description": "expected 12-month return minus XBI, as a fraction (0.10 = +10 points)"},
    "risks": {"type": "array", "maxItems": 3, "items": _RISK},
    "falsifier": {"type": "string", "description": "what would show this call is wrong"}}}
SCHEMA = {"type": "object", "required": ["calls", "extras"], "properties": {
    "calls": {"type": "array", "items": _CALL},
    "extras": {"type": "array", "maxItems": 5, "items": _CALL, "description": "optional companies outside the list"}}}


def week_of(day: date) -> date:
    return day - timedelta(days=day.weekday())


def read_ledger(path: Path = LEDGER) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- freezing
def group_a(universe: list[str], tickets: dict, citations: dict) -> list[dict]:
    out = []
    for t in universe:
        k = tickets.get(t)
        if not k:  # no order ticket yet: the agent would not buy it, and it has no score to rank by
            out.append({"ticker": t, "action": "wait", "confidence": None, "excess12m": None, "risks": [], "falsifier": "", "noTicket": True})
            continue
        gates = (citations.get(t) or {}).get("gates", {})
        risks = []
        for gate in ("counter_thesis", "customer_dependency", "earnings_validation", "management_governance", "supply_chain_map"):
            for q in (gates.get(gate) or {}).get("counter", []):
                if len(risks) < 3 and q.get("url") and q.get("quote"):
                    risks.append({"text": gate.replace("_", " "), "url": q["url"], "quote": q["quote"]})
        inv = k.get("invalidation")
        if isinstance(inv, str) and inv.startswith("["):
            m = re.match(r"\[\s*['\"](.+?)['\"]\s*[,\]]", inv)
            inv = m.group(1) if m else inv
        elif isinstance(inv, list):
            inv = inv[0] if inv else ""
        out.append({"ticker": t, "action": k["action"], "confidence": round(k["potential"]["total"], 1) if (k.get("potential") or {}).get("total") else None,
                    "excess12m": None, "risks": risks, "falsifier": inv or "", "price": k.get("price")})
    return out


def group_c(universe: list[str], companies: dict) -> list[dict]:
    rows = [(c["marketCapM"] / c["revenueM"], t) for t in universe for c in [companies.get(t) or {}]
            if c.get("marketCapM") and c.get("revenueM")]
    rows.sort()
    n = len(rows)
    return [{"ticker": t, "action": "buy" if i < 3 else "wait", "confidence": round(100 * (n - i) / n, 1), "excess12m": None,
             "risks": [], "falsifier": "", "priceToSales": round(ps, 2)} for i, (ps, t) in enumerate(rows)]


def b_prompt(universe: list[str], cutoff: str) -> str:
    return ("You are an equity research analyst. For each of these AI-medicine companies listed in the US, give a 5-10 year "
            "research call as of " + cutoff + ": " + ", ".join(universe) + ". Use only information published before " + cutoff +
            ". For each company give: action (buy = open a position now, starter = small first position, wait = good company "
            "but not at this price or not yet proven, avoid), confidence 0-100, expected 12-month return minus the XBI biotech "
            "ETF as a fraction, up to three main risks each with the URL of a source and an exact quote copied from that page, "
            "and what would show the call is wrong. You may add up to five listed companies outside the list that you rate "
            "higher. Search the web as needed. This is a paper-trading research exercise, not advice to anyone.")


def ask_b(prompt: str, model: str, timeout: int = 2400) -> dict | None:
    cmd = ["claude", "-p", "--tools", "WebSearch,WebFetch", "--allowedTools", "WebSearch,WebFetch", "--no-session-persistence",
           "--output-format", "json", "--json-schema", json.dumps(SCHEMA), "--model", model]
    try:
        proc = claude_cli.require_success(claude_cli.run(cmd, prompt, timeout))
        return json.loads(proc.stdout).get("structured_output")
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return None


def clean_b(answer: dict, universe: list[str]) -> list[dict]:
    out, seen = [], set()
    for c in answer.get("calls", []):
        t = str(c.get("ticker", "")).upper().strip()
        if t in universe and t not in seen and c.get("action") in ACTIONS:
            seen.add(t)
            out.append({**{k: c.get(k) for k in ("action", "confidence", "excess12m", "falsifier")}, "ticker": t, "risks": c.get("risks", [])[:3]})
    for c in answer.get("extras", [])[:5]:
        t = str(c.get("ticker", "")).upper().strip()
        if t and t not in universe and t not in seen and c.get("action") in ACTIONS:
            seen.add(t)
            out.append({**{k: c.get(k) for k in ("action", "confidence", "excess12m", "falsifier")}, "ticker": t,
                        "risks": c.get("risks", [])[:3], "extra": True})
    return out


def freeze(today: date, model: str, ask=ask_b, ledger_path: Path = LEDGER, raw_dir: Path = RAW) -> dict:
    week = week_of(today).isoformat()
    done = {(r["week"], r["group"]) for r in read_ledger(ledger_path)}
    universe = load(FILTER, {}).get("deepReview", [])
    if not universe:
        return {"week": week, "frozen": [], "note": "no deep-review queue"}
    rows = load(FILTER, {}).get("companies", [])
    companies = rows if isinstance(rows, dict) else {c["ticker"]: c for c in rows}
    tickets = {t["ticker"]: t for t in load(TICKETS, {}).get("tickets", [])}
    citations = load(CITATIONS, {}).get("companies", {})
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines, frozen = [], []
    base = {"week": week, "frozenAt": now, "universe": universe}
    if (week, "A") not in done:
        lines.append({**base, "group": "A", "system": "serenity-agent", "calls": group_a(universe, tickets, citations),
                      "pricesAsOf": load(TICKETS, {}).get("pricesAsOf")})
    if (week, "C") not in done:
        lines.append({**base, "group": "C", "system": "cheapest-price-to-sales", "calls": group_c(universe, companies)})
    if (week, "B") not in done:
        prompt = b_prompt(universe, today.isoformat())  # the day the calls are frozen, same information date as group A
        answer = ask(prompt, model)
        if answer:
            raw_dir.mkdir(parents=True, exist_ok=True)
            (raw_dir / f"{week}-B.json").write_text(json.dumps({"prompt": prompt, "model": model, "answer": answer}, ensure_ascii=False, indent=2), encoding="utf-8")
            lines.append({**base, "group": "B", "system": f"claude-{model}+web-search", "promptSha256": sha(prompt), "calls": clean_b(answer, universe)})
        else:
            print("group B gave no answer; it will be retried on the next run this week", file=sys.stderr)
    if lines:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with ledger_path.open("a", encoding="utf-8") as fh:
            for line in lines:
                fh.write(json.dumps(line, ensure_ascii=False) + "\n")
                frozen.append(line["group"])
    return {"week": week, "frozen": frozen, "universe": len(universe)}


# ---------------------------------------------------------------- scoring
def norm(text: str) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", text))
    text = text.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def fetch_page(url: str) -> str | None:
    """Text of the cited page: the project's source cache first, SEC filings with the SEC contact header, other pages
    via curl; PDFs are converted to text the same way the FDA re-check does."""
    import prepare_claude_review as pcr

    cached = pcr.filing_text(url, allow_fetch=False)
    if cached:
        return cached
    if "sec.gov" in url:
        return pcr.filing_text(url, allow_fetch=True) if os.getenv("SEC_USER_AGENT") else None
    try:
        proc = subprocess.run(["curl", "-sL", "--max-time", "30", "--max-filesize", "8000000", "-A",
                               "Mozilla/5.0 (Macintosh) research citation check", url], capture_output=True, timeout=40)
    except subprocess.TimeoutExpired:
        return None
    if proc.returncode != 0 or not proc.stdout:
        return None
    if proc.stdout[:4] == b"%PDF":
        import tempfile
        import event_gate_recheck as egr

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "page.pdf"
            path.write_bytes(proc.stdout)
            return egr.pdf_text(path) or None
    return proc.stdout.decode("utf-8", "replace")


def check_citation(url: str, quote: str, cache: dict, fetch=fetch_page) -> str:
    key = sha(url + "\n" + quote)
    if cache.get(key) in ("verified", "numbers_only", "not_found"):
        return cache[key]
    page = fetch(url) if url.startswith("http") else None
    if page is None:
        status = "fetch_failed"
    elif norm(quote) and norm(quote) in norm(page):
        status = "verified"
    else:
        # Not word for word; are the figures at least on the page? (reworded but faithful vs. not supported)
        numbers = re.findall(r"\d[\d,]*\.?\d*", quote)
        text = norm(page).replace(",", "")
        status = "numbers_only" if numbers and all(n.replace(",", "").rstrip(".") in text for n in numbers) else "not_found"
    cache[key] = status
    return status


def close_on_or_before(series: dict[str, float], day: str) -> tuple[str, float] | None:
    days = [d for d in series if d <= day]
    return (max(days), series[max(days)]) if days else None


def forward(series: dict[str, float], bench: dict[str, float], start: str, horizon: int) -> float | None:
    """Excess return vs XBI from the last close before start, over `horizon` XBI trading days."""
    cal = sorted(bench)
    base = close_on_or_before(bench, start)
    if not base:
        return None
    i = cal.index(base[0])
    if i + horizon >= len(cal):
        return None
    end = cal[i + horizon]
    a, b = close_on_or_before(series, base[0]), close_on_or_before(series, end)
    if not a or not b or a[0] != base[0]:
        return None
    return (b[1] / a[1] - 1) - (bench[end] / base[1] - 1)


def spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 5:
        return None

    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r

    rx, ry = ranks(xs), ranks(ys)
    mx, my = mean(rx), mean(ry)
    sx, sy = pstdev(rx), pstdev(ry)
    if not sx or not sy:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / (len(rx) * sx * sy)


def score(ledger: list[dict], closes: dict[str, dict[str, float]], cache: dict, fetch=fetch_page, seed: int = 7) -> dict:
    bench = closes.get(BENCH, {})
    groups: dict[str, dict] = {}
    weeks = sorted({r["week"] for r in ledger})
    rng = random.Random(seed)
    for row in ledger:
        g = groups.setdefault(row["group"], {"system": row["system"], "weeks": 0, "calls": 0, "citations": {"verified": 0, "numbers_only": 0, "not_found": 0, "fetch_failed": 0},
                                             "baskets": {h: [] for h in HORIZONS}, "ic": {20: [], 60: []}, "crashes": 0, "crashesHeld": 0,
                                             "randomPercentile": []})
        g["weeks"] += 1
        g["calls"] += len(row["calls"])
        for c in row["calls"]:
            for r in c.get("risks", []):
                if r.get("url") and r.get("quote"):
                    g["citations"][check_citation(r["url"], r["quote"], cache, fetch)] += 1
        start = row["week"]
        inside = [c for c in row["calls"] if not c.get("extra")]
        for h in HORIZONS:
            held = [forward(closes.get(c["ticker"], {}), bench, start, h) for c in row["calls"] if c["action"] in HOLD]
            held = [x for x in held if x is not None]
            if held:
                g["baskets"][h].append(mean(held))
                pool = [forward(closes.get(t, {}), bench, start, h) for t in row["universe"]]
                pool = [x for x in pool if x is not None]
                if row["group"] == "A" and h == 20 and len(pool) > len(held):
                    draws = [mean(rng.sample(pool, len(held))) for _ in range(1000)]
                    g["randomPercentile"].append(round(100 * sum(d < mean(held) for d in draws) / len(draws), 1))
        for h in (20, 60):
            pairs = [(c["confidence"], forward(closes.get(c["ticker"], {}), bench, start, h)) for c in inside if c.get("confidence") is not None]
            pairs = [(a, b) for a, b in pairs if b is not None]
            ic = spearman([a for a, _ in pairs], [b for _, b in pairs])
            if ic is not None:
                g["ic"][h].append(ic)
        actions = {c["ticker"]: c["action"] for c in row["calls"]}
        for t in row["universe"]:  # the whole list, so a name a group left out still counts as seen
            if forward(closes.get(t, {}), bench, start, CRASH_DAYS) is None:
                continue
            cal = sorted(bench)
            end = cal[cal.index(close_on_or_before(bench, start)[0]) + CRASH_DAYS]
            raw = close_on_or_before(closes[t], end)[1] / close_on_or_before(closes[t], start)[1] - 1
            if raw <= CRASH:
                g["crashes"] += 1
                g["crashesHeld"] += actions.get(t) in HOLD
    out = {}
    for name, g in sorted(groups.items()):
        checked = g["citations"]["verified"] + g["citations"]["numbers_only"] + g["citations"]["not_found"]
        ic = {h: ({"mean": round(mean(v), 3), "weeks": len(v), "t": round(mean(v) / (pstdev(v) / len(v) ** 0.5), 2) if len(v) > 2 and pstdev(v) else None}
                  if v else None) for h, v in g["ic"].items()}
        out[name] = {"system": g["system"], "weeks": g["weeks"], "calls": g["calls"], "citations": g["citations"],
                     "citationAccuracy": round(g["citations"]["verified"] / checked, 3) if checked else None,
                     "figuresOnPage": round((g["citations"]["verified"] + g["citations"]["numbers_only"]) / checked, 3) if checked else None,
                     "basketExcess": {str(h): ({"mean": round(mean(v), 4), "weeks": len(v)} if v else None) for h, v in g["baskets"].items()},
                     "ic": {str(h): v for h, v in ic.items()}, "crashes": g["crashes"], "crashesHeld": g["crashesHeld"],
                     "randomPercentile20d": round(mean(g["randomPercentile"]), 1) if g["randomPercentile"] else None}
    return {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "weeks": weeks, "groups": out,
            "verdict": verdict(len(weeks), out)}


def verdict(weeks: int, groups: dict) -> str:
    a, b = groups.get("A"), groups.get("B")
    if weeks < 26 or not a or not b:
        return f"{weeks} of 26 weeks frozen: too early to compare. Citation accuracy is the only early read."
    cites = (a["citationAccuracy"] or 0) > (b["citationAccuracy"] or 0) and a["crashesHeld"] <= b["crashesHeld"]
    if weeks < 52:
        return "26-week check: A " + ("beats" if cites else "does not beat") + " B on citation accuracy and crash avoidance."
    ic = (a["ic"].get("60") or {})
    skill = (ic.get("mean") or 0) > 0.05 and (ic.get("t") or 0) > 2
    return "52-week check: " + ("A shows ranking skill (60-day IC > 0.05, t > 2)." if skill and cites else
                                "the agent has not been shown to beat asking a model directly.")


def render(result: dict) -> str:
    lines = ["# Blind test scoreboard", "", f"Generated {result['generatedAt']}. Weeks frozen: {len(result['weeks'])}.", "",
             f"**Verdict:** {result['verdict']}", "",
             "| Group | System | Weeks | Calls | Citation accuracy | Figures on page | Verified / figures only / not found / fetch failed | 20-day basket excess | 60-day IC | Crashes held / seen |",
             "|---|---|---:|---:|---:|---:|---|---:|---:|---:|"]
    for name, g in result["groups"].items():
        acc = f"{g['citationAccuracy']:.0%}" if g["citationAccuracy"] is not None else "—"
        c = g["citations"]
        b20 = g["basketExcess"].get("20")
        ic = g["ic"].get("60")
        lines.append(f"| {name} | {g['system']} | {g['weeks']} | {g['calls']} | {acc} | {'—' if g['figuresOnPage'] is None else format(g['figuresOnPage'], '.0%')} | {c['verified']} / {c['numbers_only']} / {c['not_found']} / {c['fetch_failed']} | "
                     f"{'—' if not b20 else format(b20['mean'], '+.1%')} | {'—' if not ic else ic['mean']} | {g['crashesHeld']} / {g['crashes']} |")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- blinding
def export_blind(week: str, ledger: list[dict], seed: int | None = None) -> Path:
    rows = [r for r in ledger if r["week"] == week and r["group"] in ("A", "B")]
    labels = ["X", "Y"]
    random.Random(seed).shuffle(labels)
    keys = load(KEYS, {})
    keys[week] = {lab: r["group"] for lab, r in zip(labels, rows)}
    KEYS.write_text(json.dumps(keys, indent=2), encoding="utf-8")
    GRADING.mkdir(parents=True, exist_ok=True)
    out = [f"# Blind grading, week of {week}", "", "Grade each system on the rubric in docs/blind-research-benchmark.md without knowing which is which.", ""]
    for lab, r in sorted(zip(labels, rows)):
        out += [f"## System {lab}", ""]
        for c in sorted(r["calls"], key=lambda c: c["ticker"]):
            out.append(f"### {c['ticker']}: {c['action']} (confidence {c.get('confidence')})")
            for risk in c.get("risks", []):
                out.append(f"- {risk.get('text', '')}: \"{risk.get('quote', '')}\" ({risk.get('url', '')})")
            if c.get("falsifier"):
                out.append(f"- Wrong if: {c['falsifier']}")
            out.append("")
    path = GRADING / f"{week}.md"
    path.write_text("\n".join(out), encoding="utf-8")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--score", action="store_true")
    parser.add_argument("--export-blind", metavar="WEEK")
    parser.add_argument("--model", default="sonnet")
    args = parser.parse_args()
    if args.freeze:
        print(json.dumps(freeze(datetime.now(timezone.utc).date(), args.model)))
    if args.score:
        ledger = read_ledger()
        if not ledger:
            print(json.dumps({"note": "nothing frozen yet"}))
            return
        import ticket_ledger as tl

        tickers = sorted({c["ticker"] for r in ledger for c in r["calls"]} | {t for r in ledger for t in r["universe"]})
        start = (date.fromisoformat(min(r["week"] for r in ledger)) - timedelta(days=10)).isoformat()
        cache = load(CITE_CACHE, {})
        result = score(ledger, tl.fetch_closes(tickers, start), cache)
        CITE_CACHE.write_text(json.dumps(cache, indent=2), encoding="utf-8")
        RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        REPORT.write_text(render(result), encoding="utf-8")
        print(json.dumps({g: {"citationAccuracy": v["citationAccuracy"], "calls": v["calls"]} for g, v in result["groups"].items()}))
    if args.export_blind:
        print(export_blind(args.export_blind, read_ledger()))


if __name__ == "__main__":
    main()
