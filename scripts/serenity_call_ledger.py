"""Freeze Serenity research tiers and score them on real trading days.

Serenity tiers (standard / starter) are a research view of company quality, not
a price forecast. They still have to be tested, so each call is frozen with the
price known when it was made and scored later against XBI, in the same SQLite
ledger as the daily scores (state/investment-score-history.db):

  serenity_calls     one row per ticker per call: tier, base close, base date
  serenity_outcomes  realized return and XBI return 1 / 5 / 20 / 60 sessions later

A ticker gets a new call when its tier changes or its last call is at least
CALL_INTERVAL_DAYS old, so a daily run does not stack near-identical rows.

The script also writes state/track-record.json, which the demo page reads:
the short-term score backfill and the benchmark table (both from
benchmark_outcomes, AI-medicine cohort) plus the Serenity tier comparison.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean

import benchmark_evaluator as bench
from news_signal_engine import serenity_tier

ROOT = Path(__file__).resolve().parents[1]
CALL_INTERVAL_DAYS = 7
TIERS = ("standard", "starter")
MIN_OBS, MIN_DATES = 30, 10  # same rule as benchmark_evaluator


def create_tables(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS serenity_calls (
          ticker TEXT NOT NULL,
          called_on TEXT NOT NULL,
          tier TEXT NOT NULL,
          tier_text TEXT NOT NULL,
          base_date TEXT NOT NULL,
          base_price REAL NOT NULL,
          reviewer TEXT,
          source TEXT,
          recorded_at TEXT NOT NULL,
          PRIMARY KEY (ticker, called_on)
        );
        CREATE TABLE IF NOT EXISTS serenity_outcomes (
          ticker TEXT NOT NULL,
          called_on TEXT NOT NULL,
          horizon INTEGER NOT NULL,
          target_date TEXT NOT NULL,
          realized_return REAL NOT NULL,
          xbi_return REAL NOT NULL,
          excess_xbi REAL NOT NULL,
          evaluated_at TEXT NOT NULL,
          PRIMARY KEY (ticker, called_on, horizon)
        );
        """
    )
    connection.commit()


def current_calls(verdicts: dict) -> list[dict]:
    calls = []
    for company in verdicts.get("companies", []):
        tier = serenity_tier(company.get("tier", "")).removeprefix("serenity-")
        calls.append({"ticker": company["ticker"], "tier": tier, "tierText": company.get("tier", ""),
                      "source": company.get("memo", "")})
    return calls


def last_close(series: dict[str, float], on_or_before: str) -> tuple[str, float] | None:
    days = [d for d in series if d <= on_or_before]
    if not days:
        return None
    day = max(days)
    return day, series[day]


def freeze(connection: sqlite3.Connection, calls: list[dict], prices: dict[str, dict[str, float]],
           today: date, reviewer: str = "") -> list[str]:
    """Record today's calls; skip a ticker whose tier is unchanged and whose last call is recent."""
    create_tables(connection)
    frozen = []
    for call in calls:
        if call["tier"] not in TIERS:
            continue
        previous = connection.execute(
            "SELECT called_on, tier FROM serenity_calls WHERE ticker=? ORDER BY called_on DESC LIMIT 1", (call["ticker"],)
        ).fetchone()
        if previous and previous[1] == call["tier"] and (today - date.fromisoformat(previous[0])).days < CALL_INTERVAL_DAYS:
            continue
        base = last_close(prices.get(call["ticker"], {}), today.isoformat())
        if not base:
            continue
        connection.execute(
            "INSERT OR IGNORE INTO serenity_calls VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (call["ticker"], today.isoformat(), call["tier"], call["tierText"], base[0], base[1], reviewer,
             call["source"], datetime.now(timezone.utc).isoformat()),
        )
        frozen.append(call["ticker"])
    connection.commit()
    return frozen


def backfill(connection: sqlite3.Connection, prices: dict[str, dict[str, float]]) -> int:
    create_tables(connection)
    evaluated_at = datetime.now(timezone.utc).isoformat()
    count = 0
    for ticker, called_on, base_date, base_price in connection.execute(
            "SELECT ticker, called_on, base_date, base_price FROM serenity_calls").fetchall():
        for horizon in bench.HORIZONS:
            stock = bench.future_return(prices.get(ticker, {}), base_date, horizon, base_price)
            xbi = bench.future_return(prices.get("XBI", {}), base_date, horizon)
            if not stock or not xbi or stock[0] != xbi[0]:
                continue
            connection.execute(
                "INSERT OR REPLACE INTO serenity_outcomes VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (ticker, called_on, horizon, stock[0], stock[2], xbi[2], stock[2] - xbi[2], evaluated_at),
            )
            count += 1
    connection.commit()
    return count


def avg(values: list[float]) -> float | None:
    return mean(values) if values else None


def tier_table(connection: sqlite3.Connection) -> list[dict]:
    create_tables(connection)
    rows = []
    for horizon in bench.HORIZONS:
        data = connection.execute(
            """SELECT c.tier, c.called_on, o.realized_return, o.xbi_return, o.excess_xbi
               FROM serenity_outcomes o JOIN serenity_calls c ON c.ticker=o.ticker AND c.called_on=o.called_on
               WHERE o.horizon=?""", (horizon,)).fetchall()
        row = {"horizon": horizon, "xbi": avg([r[3] for r in data])}
        for tier in TIERS:
            subset = [r for r in data if r[0] == tier]
            row[tier] = {"samples": len(subset), "dates": len({r[1] for r in subset}),
                         "return": avg([r[2] for r in subset]), "excessXbi": avg([r[4] for r in subset])}
        s, t = row["standard"]["return"], row["starter"]["return"]
        row["standardMinusStarter"] = s - t if s is not None and t is not None else None
        rows.append(row)
    return rows


def score_tables(connection: sqlite3.Connection, cohort: str) -> tuple[list[dict], list[dict]]:
    """Short-term score backfill (all tracked stocks) and benchmark comparison (cohort), both from benchmark_outcomes."""
    has = connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='benchmark_outcomes'").fetchone()[0]
    scores, benchmarks = [], []
    for horizon in bench.HORIZONS:
        rows = bench.outcome_rows(connection, horizon, None) if has else []  # every tracked stock, as in the tracker report
        returns = [float(r["realized_return"]) for r in rows]
        scores.append({
            "horizon": horizon, "samples": len(rows), "dates": len({r["prediction_as_of"] for r in rows}),
            "return": avg(returns),
            "hitRate": avg([r["direction_correct"] for r in rows]),
            "highScore": avg([float(r["realized_return"]) for r in rows if r["combined_score"] >= 70]),
            "lowScore": avg([float(r["realized_return"]) for r in rows if r["combined_score"] < 70]),
        })
        m = bench.metrics(connection, horizon, cohort) if has else {}
        benchmarks.append({"horizon": horizon, "samples": m.get("samples", 0), "dates": m.get("distinctDates", 0),
                           **{k: m.get(k) for k in ("agentReturn", "spyReturn", "xlvReturn", "xbiReturn", "excessXbi",
                                                    "randomReturn", "momentumReturn")}})
    return scores, benchmarks


def build_track_record(connection: sqlite3.Connection, cohort: str) -> dict:
    create_tables(connection)
    scores, benchmarks = score_tables(connection, cohort)
    calls = connection.execute(
        "SELECT ticker, tier, called_on, base_date, base_price FROM serenity_calls ORDER BY called_on DESC, tier, ticker").fetchall()
    first = connection.execute("SELECT MIN(as_of) FROM predictions").fetchone()[0] if connection.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='predictions'").fetchone()[0] else None
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "cohort": cohort,
        "rule": {"minObservations": MIN_OBS, "minDates": MIN_DATES},
        "scoresSince": first,
        "scoreTickers": connection.execute("SELECT COUNT(DISTINCT ticker) FROM predictions").fetchone()[0] if first else 0,
        "scoreBackfill": scores,
        "benchmarks": benchmarks,
        "serenityCalls": [{"ticker": r[0], "tier": r[1], "calledOn": r[2], "baseDate": r[3], "basePrice": r[4]} for r in calls],
        "serenityTiers": tier_table(connection),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze Serenity tiers and score them against XBI")
    parser.add_argument("--database", default=str(ROOT / "state/investment-score-history.db"))
    parser.add_argument("--verdicts", default=str(ROOT / "state/serenity-claude-verdicts.json"))
    parser.add_argument("--output", default=str(ROOT / "state/track-record.json"))
    parser.add_argument("--cohort", default="ai-medicine")
    parser.add_argument("--no-freeze", action="store_true", help="only backfill and report")
    args = parser.parse_args()
    verdicts = json.loads(Path(args.verdicts).read_text(encoding="utf-8"))
    connection = sqlite3.connect(args.database)
    connection.row_factory = sqlite3.Row
    create_tables(connection)
    calls = current_calls(verdicts)
    tickers = sorted({c["ticker"] for c in calls} | {r[0] for r in connection.execute("SELECT ticker FROM serenity_calls")} | {"XBI"})
    earliest = connection.execute("SELECT MIN(base_date) FROM serenity_calls").fetchone()[0] or date.today().isoformat()
    start = (date.fromisoformat(earliest) - timedelta(days=10)).isoformat()
    prices = bench.download_prices(tickers, start, (date.today() + timedelta(days=1)).isoformat())
    frozen = [] if args.no_freeze else freeze(connection, calls, prices, date.today(), verdicts.get("reviewer", ""))
    scored = backfill(connection, prices)
    record = build_track_record(connection, args.cohort)
    connection.close()
    Path(args.output).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"frozen": frozen, "outcomes": scored, "output": args.output}))


if __name__ == "__main__":
    main()
