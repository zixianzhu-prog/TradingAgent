from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean

HORIZONS = (1, 5, 20, 60)
BENCHMARKS = ("SPY", "XLV", "XBI")


def create_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS benchmark_outcomes (
          ticker TEXT NOT NULL,
          prediction_as_of TEXT NOT NULL,
          horizon INTEGER NOT NULL,
          target_as_of TEXT NOT NULL,
          target_price REAL NOT NULL,
          realized_return REAL NOT NULL,
          spy_return REAL NOT NULL,
          xlv_return REAL NOT NULL,
          xbi_return REAL,
          excess_spy REAL NOT NULL,
          excess_xlv REAL NOT NULL,
          excess_xbi REAL,
          direction_correct INTEGER NOT NULL,
          random_ticker TEXT,
          random_return REAL,
          momentum_ticker TEXT,
          momentum_return REAL,
          evaluated_at TEXT NOT NULL,
          PRIMARY KEY (ticker, prediction_as_of, horizon)
        )
        """
    )
    columns = {row[1] for row in connection.execute("PRAGMA table_info(benchmark_outcomes)")}
    if "xbi_return" not in columns:
        connection.execute("ALTER TABLE benchmark_outcomes ADD COLUMN xbi_return REAL")
    if "excess_xbi" not in columns:
        connection.execute("ALTER TABLE benchmark_outcomes ADD COLUMN excess_xbi REAL")
    connection.commit()


def future_return(series: dict[str, float], as_of: str, horizon: int, base_price: float | None = None) -> tuple[str, float, float] | None:
    dates = sorted(day for day in series if day <= as_of)
    if not dates:
        return None
    base_date = dates[-1]
    all_dates = sorted(series)
    base_index = all_dates.index(base_date)
    target_index = base_index + horizon
    if target_index >= len(all_dates):
        return None
    target_date = all_dates[target_index]
    base = float(base_price if base_price is not None else series[base_date])
    target = float(series[target_date])
    return target_date, target, target / base - 1.0


def past_momentum(series: dict[str, float], as_of: str, sessions: int = 20) -> float | None:
    dates = sorted(day for day in series if day <= as_of)
    if len(dates) <= sessions:
        return None
    return series[dates[-1]] / series[dates[-1 - sessions]] - 1.0


def deterministic_choice(options: list[str], key: str) -> str | None:
    if not options:
        return None
    index = int(hashlib.sha256(key.encode()).hexdigest()[:8], 16) % len(options)
    return sorted(options)[index]


def evaluate_prediction(prediction: sqlite3.Row | dict, prices: dict[str, dict[str, float]], universe: list[str], horizon: int) -> dict | None:
    ticker = prediction["ticker"]
    as_of = prediction["as_of"]
    stock = future_return(prices.get(ticker, {}), as_of, horizon, float(prediction["price"]))
    spy = future_return(prices.get("SPY", {}), as_of, horizon)
    xlv = future_return(prices.get("XLV", {}), as_of, horizon)
    xbi = future_return(prices.get("XBI", {}), as_of, horizon)
    if not stock or not spy or not xlv or not xbi:
        return None
    random_options = [item for item in universe if item != ticker and future_return(prices.get(item, {}), as_of, horizon)]
    random_ticker = deterministic_choice(random_options, f"{ticker}|{as_of}|{horizon}")
    random_result = future_return(prices[random_ticker], as_of, horizon) if random_ticker else None
    momentum_candidates = [(item, past_momentum(prices.get(item, {}), as_of)) for item in universe]
    momentum_candidates = [(item, value) for item, value in momentum_candidates if value is not None and future_return(prices.get(item, {}), as_of, horizon)]
    momentum_ticker = max(momentum_candidates, key=lambda item: item[1])[0] if momentum_candidates else None
    momentum_result = future_return(prices[momentum_ticker], as_of, horizon) if momentum_ticker else None
    realized = stock[2]
    forecast = float(prediction["forecast_return"])
    return {
        "ticker": ticker,
        "prediction_as_of": as_of,
        "horizon": horizon,
        "target_as_of": stock[0],
        "target_price": stock[1],
        "realized_return": realized,
        "spy_return": spy[2],
        "xlv_return": xlv[2],
        "xbi_return": xbi[2],
        "excess_spy": realized - spy[2],
        "excess_xlv": realized - xlv[2],
        "excess_xbi": realized - xbi[2],
        "direction_correct": int((forecast >= 0 and realized >= 0) or (forecast < 0 and realized < 0)),
        "random_ticker": random_ticker,
        "random_return": random_result[2] if random_result else None,
        "momentum_ticker": momentum_ticker,
        "momentum_return": momentum_result[2] if momentum_result else None,
    }


def download_prices(tickers: list[str], start: str, end: str) -> dict[str, dict[str, float]]:
    import yfinance as yf

    prices: dict[str, dict[str, float]] = {}
    for ticker in tickers:
        frame = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
        if frame.empty:
            prices[ticker] = {}
            continue
        close = frame["Close"]
        if getattr(close, "ndim", 1) > 1:
            close = close.iloc[:, 0]
        prices[ticker] = {index.date().isoformat(): float(value) for index, value in close.dropna().items()}
    return prices


def backfill(connection: sqlite3.Connection, prices: dict[str, dict[str, float]]) -> int:
    create_table(connection)
    predictions = connection.execute("SELECT * FROM predictions ORDER BY as_of, ticker").fetchall()
    universe = sorted({row["ticker"] for row in predictions})
    evaluated_at = datetime.now(timezone.utc).isoformat()
    inserted = 0
    for prediction in predictions:
        for horizon in HORIZONS:
            result = evaluate_prediction(prediction, prices, universe, horizon)
            if not result:
                continue
            before = connection.total_changes
            connection.execute(
                """INSERT OR REPLACE INTO benchmark_outcomes
                (ticker, prediction_as_of, horizon, target_as_of, target_price,
                 realized_return, spy_return, xlv_return, xbi_return,
                 excess_spy, excess_xlv, excess_xbi, direction_correct,
                 random_ticker, random_return, momentum_ticker, momentum_return, evaluated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    result["ticker"], result["prediction_as_of"], result["horizon"], result["target_as_of"],
                    result["target_price"], result["realized_return"], result["spy_return"], result["xlv_return"],
                    result["xbi_return"], result["excess_spy"], result["excess_xlv"], result["excess_xbi"],
                    result["direction_correct"], result["random_ticker"], result["random_return"],
                    result["momentum_ticker"], result["momentum_return"], evaluated_at,
                ),
            )
            inserted += int(connection.total_changes > before)
    connection.commit()
    return inserted


def metrics(connection: sqlite3.Connection, horizon: int, cohort: str | None = None) -> dict:
    has_cohorts = connection.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='prediction_cohorts'"
    ).fetchone()[0]
    cohort_join = "JOIN prediction_cohorts c ON c.ticker=p.ticker AND c.as_of=p.as_of" if cohort and has_cohorts else ""
    cohort_where = "AND c.cohort=?" if cohort and has_cohorts else ""
    params = (horizon, cohort) if cohort and has_cohorts else (horizon,)
    rows = connection.execute(
        f"""SELECT b.*, p.combined_score, p.serenity_decision
           FROM benchmark_outcomes b JOIN predictions p
           ON p.ticker=b.ticker AND p.as_of=b.prediction_as_of
           {cohort_join}
           WHERE b.horizon=? {cohort_where}""", params
    ).fetchall()
    def avg(field: str, subset=None):
        values = [float(row[field]) for row in rows if row[field] is not None and (subset is None or subset(row))]
        return mean(values) if values else None
    return {
        "samples": len(rows),
        "distinctDates": len({row["prediction_as_of"] for row in rows}),
        "agentReturn": avg("realized_return"),
        "spyReturn": avg("spy_return"),
        "xlvReturn": avg("xlv_return"),
        "xbiReturn": avg("xbi_return"),
        "excessSpy": avg("excess_spy"),
        "excessXlv": avg("excess_xlv"),
        "excessXbi": avg("excess_xbi"),
        "randomReturn": avg("random_return"),
        "momentumReturn": avg("momentum_return"),
        "hitRate": avg("direction_correct"),
        "highScoreReturn": avg("realized_return", lambda row: row["combined_score"] >= 70),
        "serenityReturn": avg("realized_return", lambda row: row["serenity_decision"] == "research-ready"),
    }


def build_report(connection: sqlite3.Connection, output: str, cohort: str | None = None) -> dict:
    result = {str(h): metrics(connection, h, cohort) for h in HORIZONS}
    lines = [
        "# Agent 样本外基准验证",
        "",
        f"> 评测队列：`{cohort or 'all'}`。",
        "",
        "> 使用真实交易日日线回填。SPY、XLV、XBI、固定种子的随机股票和20日动量作为独立基准；样本不足时不宣称有效。",
        "",
        "| 后续交易日 | 股票-日期观察 | 独立预测日 | Agent股票 | SPY | XLV | XBI | 超额SPY | 超额XBI | 随机基线 | 动量基线 | 方向命中 |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    fmt = lambda value: f"{value:+.2%}" if value is not None else "等待数据"
    for horizon in HORIZONS:
        row = result[str(horizon)]
        lines.append(f"| {horizon} | {row['samples']} | {row['distinctDates']} | {fmt(row['agentReturn'])} | {fmt(row['spyReturn'])} | {fmt(row['xlvReturn'])} | {fmt(row['xbiReturn'])} | {fmt(row['excessSpy'])} | {fmt(row['excessXbi'])} | {fmt(row['randomReturn'])} | {fmt(row['momentumReturn'])} | {fmt(row['hitRate'])} |")
    lines += [
        "",
        "## 判定规则",
        "",
        "- 少于30个股票-日期观察，或少于10个独立预测日：只展示，不作有效性结论。",
        "- AI Medicine 至少30个观察、10个预测日且同时跑赢SPY、XLV、XBI与随机基线：初步有效，仍需跨市场阶段验证。",
        "- 至少100个观察、30个预测日并覆盖上涨、下跌和震荡阶段：才允许讨论稳定预测能力。",
        "- 所有基准按同一预测日与交易日周期计算，禁止事后挑选起点。",
        "",
    ]
    Path(output).write_text("\n".join(lines), encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare frozen agent predictions against market baselines")
    parser.add_argument("--database", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--cohort", default="ai-medicine")
    args = parser.parse_args()
    connection = sqlite3.connect(args.database)
    connection.row_factory = sqlite3.Row
    predictions = connection.execute("SELECT * FROM predictions").fetchall()
    if not predictions:
        raise SystemExit("No frozen predictions found")
    universe = sorted({row["ticker"] for row in predictions} | set(BENCHMARKS))
    earliest = min(date.fromisoformat(row["as_of"]) for row in predictions) - timedelta(days=45)
    prices = download_prices(universe, earliest.isoformat(), (date.today() + timedelta(days=1)).isoformat())
    inserted = backfill(connection, prices)
    report = build_report(connection, args.output, args.cohort)
    connection.close()
    print(json.dumps({"evaluated": inserted, "metrics": report, "output": args.output}))


if __name__ == "__main__":
    main()
