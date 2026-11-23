"""Forward record of the order tickets: freeze each day's calls, then score them against XBI as time passes.

The backtests say what the rule would have done; this says what the agent actually said, in advance.
Each run appends today's tickets (action, price, limit, size) to outputs/order-ticket-ledger.jsonl, once per
day, never rewriting earlier lines. The file is committed, so git history proves when each call was made.

Scoring counts a call once per spell: from the first day a ticker gets an action until the action changes.
Return runs from the frozen price to the latest close (or to the day the action changed); XBI over the same
dates is the benchmark. "wait" and "avoid" are the control group: if starters do no better than waits, the
tickets add nothing.

    PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/ticket_ledger.py
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TICKETS = ROOT / "state/order-tickets.json"
LEDGER = ROOT / "outputs/order-ticket-ledger.jsonl"
REPORT = ROOT / "outputs/order-ticket-ledger.md"
BENCH = "XBI"
FIELDS = ("ticker", "action", "price", "limitPrice", "safetyFloor", "positionPct", "serenityDecision")


def read_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def freeze(tickets: list[dict], day: str, ledger: list[dict]) -> list[dict]:
    """Rows to append for `day`; nothing if that day is already frozen (calls are never rewritten)."""
    if any(r["date"] == day for r in ledger):
        return []
    return [{"date": day, **{k: t.get(k) for k in FIELDS}} for t in tickets if t.get("price")]


def spells(ledger: list[dict]) -> list[dict]:
    """One entry per (ticker, uninterrupted action): start date and price, end date (None = still open)."""
    out, open_by_ticker = [], {}
    for day in sorted({r["date"] for r in ledger}):
        today = {r["ticker"]: r for r in ledger if r["date"] == day}
        for t, cur in list(open_by_ticker.items()):
            if t not in today or today[t]["action"] != cur["action"]:
                cur["end"], cur["endPrice"] = day, (today.get(t) or {}).get("price")
                del open_by_ticker[t]
        for t, r in today.items():
            if t not in open_by_ticker:
                open_by_ticker[t] = {"ticker": t, "action": r["action"], "start": day, "startPrice": r["price"],
                                     "end": None, "endPrice": None}
                out.append(open_by_ticker[t])
    return out


def close_on(series: dict[str, float], day: str) -> float | None:
    """Close on `day`, or the last close before it (weekends, holidays)."""
    prior = [d for d in series if d <= day]
    return series[max(prior)] if prior else None


def score(spell_rows: list[dict], closes: dict[str, dict[str, float]], today: str) -> list[dict]:
    bench = closes.get(BENCH, {})
    out = []
    for s in spell_rows:
        end = s["end"] or today
        if end <= s["start"]:
            continue  # same day: no market move to score yet
        series = closes.get(s["ticker"], {})
        last = s["endPrice"] if s["end"] and s["endPrice"] else close_on(series, end)
        b0, b1 = close_on(bench, s["start"]), close_on(bench, end)
        if not (s["startPrice"] and last and b0 and b1):
            continue
        ret, bret = last / s["startPrice"] - 1, b1 / b0 - 1
        out.append({**s, "days": (date.fromisoformat(end) - date.fromisoformat(s["start"])).days,
                    "return": round(ret, 4), "xbi": round(bret, 4), "excess": round(ret - bret, 4)})
    return out


def summarize(scored: list[dict]) -> dict[str, dict]:
    groups: dict[str, list[dict]] = {}
    for s in scored:
        groups.setdefault("live (buy/starter)" if s["action"] in ("buy", "starter") else s["action"], []).append(s)
    return {g: {"calls": len(rows), "meanReturn": round(sum(r["return"] for r in rows) / len(rows), 4),
                "meanExcess": round(sum(r["excess"] for r in rows) / len(rows), 4),
                "beatXbi": sum(r["excess"] > 0 for r in rows)} for g, rows in groups.items()}


def fetch_closes(tickers: list[str], start: str) -> dict[str, dict[str, float]]:
    import yfinance as yf

    frame = yf.download(sorted(set(tickers) | {BENCH}), start=start, auto_adjust=False, progress=False, group_by="ticker", threads=True)
    out = {}
    for t in set(tickers) | {BENCH}:
        try:
            col = frame[t]["Close"].dropna()
            out[t] = {d.date().isoformat(): float(v) for d, v in col.items()}
        except Exception:
            continue
    return out


def render(summary: dict, scored: list[dict], first: str | None, days: int) -> str:
    lines = ["# 下单单前瞻记录", "",
             f"> 从 {first or '—'} 起每天冻结一次下单单（{days} 个交易日已记录），只追加、不改写；文件随仓库提交，git 时间戳证明是事前判断。",
             "> 收益从冻结价算到最新收盘（或动作改变那天），同期 XBI 为基准。“等待/回避”是对照组：如果试探仓不比等待好，单据就没有价值。", "",
             "| 组别 | 判断次数 | 平均收益 | 平均超额（对 XBI） | 跑赢 XBI |", "|---|---:|---:|---:|---:|"]
    for g, s in sorted(summary.items()):
        lines.append(f"| {g} | {s['calls']} | {s['meanReturn']:+.1%} | {s['meanExcess']:+.1%} | {s['beatXbi']}/{s['calls']} |")
    if not scored:
        lines += ["| 尚无可计分的判断（第一天冻结，下一个交易日开始计分） | | | | |"]
    lines += ["", "## 每次判断", "", "| 股票 | 动作 | 起始 | 结束 | 天数 | 收益 | XBI | 超额 |", "|---|---|---|---|---:|---:|---:|---:|"]
    for s in sorted(scored, key=lambda x: (x["action"], -x["excess"])):
        lines.append(f"| {s['ticker']} | {s['action']} | {s['start']} | {s['end'] or '持有中'} | {s['days']} | "
                     f"{s['return']:+.1%} | {s['xbi']:+.1%} | {s['excess']:+.1%} |")
    lines += ["", "样本还小时（几十天、十几次判断）结果主要是噪声；至少积累半年、几十次判断再下结论。"]
    return "\n".join(lines) + "\n"


def main() -> None:
    tickets = json.loads(TICKETS.read_text(encoding="utf-8"))["tickets"]
    ledger = read_ledger(LEDGER)
    today = date.today().isoformat()
    new = freeze(tickets, today, ledger)
    if new:
        with LEDGER.open("a", encoding="utf-8") as fh:
            fh.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in new)
        ledger += new
    rows = spells(ledger)
    first = min((r["date"] for r in ledger), default=None)
    scored = score(rows, fetch_closes([r["ticker"] for r in rows], first), today) if first else []
    summary = summarize(scored)
    REPORT.write_text(render(summary, scored, first, len({r["date"] for r in ledger})), encoding="utf-8")
    print(json.dumps({"frozenToday": len(new), "days": len({r["date"] for r in ledger}), "calls": len(scored), "summary": summary}))


if __name__ == "__main__":
    main()
