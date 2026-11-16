"""Priced-in check: has the market already reacted to an emerging topic?

For each candidate company this compares, using only daily bars dated on or
before ``as_of``:

- Move since the signal: return from the last close before the topic first fired,
  minus the sector benchmark (XBI) over the same days.
- Move over the trailing 10 trading days, because the market often reacts to the
  underlying news before our detector fires (Moderna jumped on the CEPI funding
  news on 23 January 2020, two days before the first preprint signal).
- Size of the move in units of normal volatility: excess log return divided by the
  stock's pre-signal daily volatility times sqrt(days). A 15% move is huge for a
  large cap and ordinary for a micro-cap biotech; this puts them on one scale.
- Volume: average volume over the last 5 sessions versus the 60 sessions before
  the signal.

Verdict per company:
- early:            move under 1 sigma and volume under 1.5x normal
- heavily priced:   move of 3+ sigma, or excess return of 50%+, or 2+ sigma with 4x volume
- partly priced:    anything in between

This says whether a reaction has already happened. It is not a forecast of what
happens next: in January 2020 Moderna looked "partly priced" and still rose
several-fold, because the market underestimated the scale of the pandemic.
"""
from __future__ import annotations

import argparse
import json
import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, stdev

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = "XBI"
TRAILING_SESSIONS = 10
VOL_LOOKBACK = 60


def download_bars(ticker: str, start: date, end: date) -> list[dict]:
    """Daily bars with date, close and volume, oldest first (yfinance, adjusted)."""
    import yfinance as yf

    frame = yf.download(ticker, start=start.isoformat(), end=(end + timedelta(days=1)).isoformat(), auto_adjust=True, progress=False)
    if frame.empty:
        return []
    close, volume = frame["Close"], frame["Volume"]
    if getattr(close, "ndim", 1) > 1:
        close, volume = close.iloc[:, 0], volume.iloc[:, 0]
    return [
        {"date": index.date().isoformat(), "close": float(c), "volume": float(v)}
        for index, c, v in zip(close.index, close.values, volume.values)
        if not math.isnan(float(c))
    ]


def _close_before(bars: list[dict], day: str) -> dict | None:
    prior = [bar for bar in bars if bar["date"] < day]
    return prior[-1] if prior else None


def assess(bars: list[dict], bench: list[dict], signal_start: date, as_of: date) -> dict:
    bars = [b for b in bars if b["date"] <= as_of.isoformat()]
    bench = [b for b in bench if b["date"] <= as_of.isoformat()]
    if len(bars) < 30 or not bench:
        return {"verdict": "no data", "reason": "fewer than 30 trading days of history before as-of"}
    start = signal_start.isoformat()
    ref = _close_before(bars, start)
    bench_ref = _close_before(bench, start)
    if ref is None or bench_ref is None:
        return {"verdict": "no data", "reason": "no close before the signal date"}
    last, bench_last = bars[-1], bench[-1]
    since = last["close"] / ref["close"] - 1
    bench_since = bench_last["close"] / bench_ref["close"] - 1

    trailing_ref = bars[-TRAILING_SESSIONS - 1] if len(bars) > TRAILING_SESSIONS else bars[0]
    bench_trailing_ref = next((b for b in reversed(bench) if b["date"] <= trailing_ref["date"]), bench[0])
    trailing = last["close"] / trailing_ref["close"] - 1
    bench_trailing = bench_last["close"] / bench_trailing_ref["close"] - 1

    # Normal volatility and volume are measured before both windows, so a run-up that
    # started before the signal does not inflate the baseline it is compared against.
    baseline_end = min(start, trailing_ref["date"])
    pre = [b for b in bars if b["date"] < baseline_end][-(VOL_LOOKBACK + 1):]
    returns = [math.log(b["close"] / a["close"]) for a, b in zip(pre, pre[1:])]
    sigma = stdev(returns) if len(returns) >= 20 else None

    def sigmas(excess_return: float, sessions: int) -> float | None:
        if not sigma or sessions <= 0:
            return None
        return math.log1p(excess_return) / (sigma * math.sqrt(sessions))

    sessions_since = sum(1 for b in bars if b["date"] >= start)
    excess_since = (1 + since) / (1 + bench_since) - 1
    excess_trailing = (1 + trailing) / (1 + bench_trailing) - 1
    z_since = sigmas(excess_since, max(1, sessions_since))
    z_trailing = sigmas(excess_trailing, TRAILING_SESSIONS)
    # Judge on whichever window shows the larger reaction: the market may have moved before we noticed.
    window, excess, z = max(
        (("since signal", excess_since, z_since), ("last 10 sessions", excess_trailing, z_trailing)),
        key=lambda item: abs(item[2]) if item[2] is not None else abs(item[1]),
    )
    pre_volume = [b["volume"] for b in pre[-VOL_LOOKBACK:] if b["volume"] > 0]
    recent_volume = [b["volume"] for b in bars[-5:] if b["volume"] > 0]
    volume_ratio = mean(recent_volume) / mean(pre_volume) if pre_volume and recent_volume else None

    magnitude = abs(z) if z is not None else 0.0
    vol = volume_ratio or 1.0
    if magnitude >= 3 or abs(excess) >= 0.5 or (magnitude >= 2 and vol >= 4):
        verdict = "heavily priced"
    elif magnitude < 1 and vol < 1.5:
        verdict = "early"
    else:
        verdict = "partly priced"
    return {
        "verdict": verdict,
        "asOfClose": round(last["close"], 2),
        "asOfDate": last["date"],
        "referenceDate": ref["date"],
        "returnSinceSignal": round(since, 4),
        "excessSinceSignal": round(excess_since, 4),
        "return10d": round(trailing, 4),
        "excess10d": round(excess_trailing, 4),
        "sigmaMove": round(z, 2) if z is not None else None,
        "judgedOn": window,
        "volumeRatio": round(volume_ratio, 2) if volume_ratio else None,
        "dailyVolatility": round(sigma, 4) if sigma else None,
    }


def check(candidates: list[str], signal_start: date, as_of: date, benchmark: str = BENCHMARK, fetch=download_bars) -> dict:
    start = signal_start - timedelta(days=130)
    bench = fetch(benchmark, start, as_of)
    rows = {}
    for ticker in candidates:
        try:
            rows[ticker] = assess(fetch(ticker, start, as_of), bench, signal_start, as_of)
        except Exception as exc:  # one bad ticker must not stop the rest
            rows[ticker] = {"verdict": "no data", "reason": str(exc)[:160]}
    return {"signalStart": signal_start.isoformat(), "asOf": as_of.isoformat(), "benchmark": benchmark, "companies": rows}


VERDICT_ZH = {"early": "还早", "partly priced": "部分反映", "heavily priced": "已大幅定价", "no data": "无数据"}


def pct(value) -> str:
    return f"{value:+.1%}" if value is not None else "—"


def write_markdown(results: list[dict], path: str) -> None:
    lines = ["# 是否已被定价", "",
             "> 只用截至当日的行情：比较信号出现以来和最近 10 个交易日的超额涨幅（相对 XBI）、涨幅相当于几倍日常波动、成交量放大倍数。"
             "判断的是“市场是否已经反应”，不是对未来涨跌的预测。", ""]
    if not results:
        lines.append("今天没有已确认的新话题，因此没有需要检查的候选公司。")
    for result in results:
        lines += [f"## {result['topic']}", "", f"信号首次出现 {result['signalStart']}，检查日 {result['asOf']}，基准 {result['benchmark']}。", "",
                  "| 股票 | 判断 | 信号以来超额 | 近10日超额 | 波动倍数 | 成交量倍数 | 依据窗口 |",
                  "| --- | --- | ---: | ---: | ---: | ---: | --- |"]
        for ticker, row in result["companies"].items():
            if row["verdict"] == "no data":
                lines.append(f"| {ticker} | 无数据 | — | — | — | — | {row.get('reason', '')} |")
                continue
            sigma = f"{row['sigmaMove']:+.1f}σ" if row["sigmaMove"] is not None else "—"
            volume = f"{row['volumeRatio']:.1f}×" if row["volumeRatio"] else "—"
            lines.append(f"| {ticker} | {VERDICT_ZH[row['verdict']]} | {pct(row['excessSinceSignal'])} | {pct(row['excess10d'])} | {sigma} | {volume} | {row['judgedOn']} |")
        lines.append("")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Check whether mapped candidates have already moved")
    parser.add_argument("--map", default=str(ROOT / "state/beneficiary-map.json"))
    parser.add_argument("--signals", default=str(ROOT / "state/emerging-signals.json"))
    parser.add_argument("--json-output", default=str(ROOT / "state/pricing-check.json"))
    parser.add_argument("--markdown-output", default=str(ROOT / "outputs/pricing-check.md"))
    args = parser.parse_args()
    mapping = json.loads(Path(args.map).read_text(encoding="utf-8")) if Path(args.map).exists() else {"topics": []}
    signals = json.loads(Path(args.signals).read_text(encoding="utf-8")) if Path(args.signals).exists() else {}
    first_fired = {c["topic"]: c.get("firstFired") for c in signals.get("confirmedTopics", [])}
    for c in signals.get("confirmedTopics", []):
        for label in c.get("labels", {}):
            first_fired.setdefault(label, c.get("firstFired"))
    results = []
    for topic in mapping.get("topics", []):
        tickers = [c["ticker"] for c in topic.get("candidates", []) if c.get("ticker")][:15]
        if not tickers:
            continue
        as_of = date.fromisoformat(topic["asOf"])
        start = date.fromisoformat(first_fired.get(topic["topic"]) or topic["asOf"])
        results.append({"topic": topic["topic"], **check(tickers, start, as_of)})
    payload = {"generatedAt": datetime.now(timezone.utc).isoformat(), "results": results}
    Path(args.json_output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.json_output).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(results, args.markdown_output)
    print(json.dumps({r["topic"]: {t: v["verdict"] for t, v in r["companies"].items()} for r in results}, ensure_ascii=False))


if __name__ == "__main__":
    main()
