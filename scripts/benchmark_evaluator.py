from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, stdev

HORIZONS = (1, 5, 20, 60)
DECISION_TIERS = ("research-ready", "watch", "revalidate", "reject", "unreviewed")
# Signals checked for cross-sectional rank IC. ``past_momentum`` is the
# no-skill baseline: the combined score must beat it to claim added value.
IC_SIGNALS = (
    ("combined_score", "综合分"),
    ("news_score", "新闻分"),
    ("technical_score", "技术分"),
    ("kronos_score", "Kronos分"),
    ("past_momentum", "20日动量基线"),
)
MIN_NAMES_PER_DATE = 5
MIN_DATES_FOR_T = 10  # matches the 10-independent-date rule below
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
          past_momentum REAL,
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
    if "past_momentum" not in columns:
        connection.execute("ALTER TABLE benchmark_outcomes ADD COLUMN past_momentum REAL")
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
        # Trailing 20-session return of the predicted stock itself, known at as_of.
        "past_momentum": past_momentum(prices.get(ticker, {}), as_of),
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
                 random_ticker, random_return, momentum_ticker, momentum_return, past_momentum, evaluated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    result["ticker"], result["prediction_as_of"], result["horizon"], result["target_as_of"],
                    result["target_price"], result["realized_return"], result["spy_return"], result["xlv_return"],
                    result["xbi_return"], result["excess_spy"], result["excess_xlv"], result["excess_xbi"],
                    result["direction_correct"], result["random_ticker"], result["random_return"],
                    result["momentum_ticker"], result["momentum_return"], result["past_momentum"], evaluated_at,
                ),
            )
            inserted += int(connection.total_changes > before)
    connection.commit()
    return inserted


def outcome_rows(connection: sqlite3.Connection, horizon: int, cohort: str | None = None) -> list[sqlite3.Row]:
    has_cohorts = connection.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='prediction_cohorts'"
    ).fetchone()[0]
    cohort_join = "JOIN prediction_cohorts c ON c.ticker=p.ticker AND c.as_of=p.as_of" if cohort and has_cohorts else ""
    cohort_where = "AND c.cohort=?" if cohort and has_cohorts else ""
    params = (horizon, cohort) if cohort and has_cohorts else (horizon,)
    rows = connection.execute(
        f"""SELECT b.*, p.combined_score, p.news_score, p.technical_score, p.kronos_score, p.serenity_decision
           FROM benchmark_outcomes b JOIN predictions p
           ON p.ticker=b.ticker AND p.as_of=b.prediction_as_of
           {cohort_join}
           WHERE b.horizon=? {cohort_where}""", params
    ).fetchall()
    return rows


def _average_ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda index: values[index])
    ranks = [0.0] * len(values)
    position = 0
    while position < len(order):
        end = position
        while end + 1 < len(order) and values[order[end + 1]] == values[order[position]]:
            end += 1
        for index in order[position:end + 1]:
            ranks[index] = (position + end) / 2 + 1
        position = end + 1
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float | None:
    """Spearman rank correlation with tie-averaged ranks; None when undefined."""
    if len(xs) != len(ys) or len(xs) < 3:
        return None
    rx, ry = _average_ranks(xs), _average_ranks(ys)
    mx, my = mean(rx), mean(ry)
    cov = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    vx = sum((a - mx) ** 2 for a in rx)
    vy = sum((b - my) ** 2 for b in ry)
    if vx == 0 or vy == 0:
        return None
    return cov / math.sqrt(vx * vy)


def _by_date(rows) -> dict[str, list]:
    grouped: dict[str, list] = {}
    for row in rows:
        grouped.setdefault(row["prediction_as_of"], []).append(row)
    return grouped


def information_coefficient(rows, field: str, min_names: int = MIN_NAMES_PER_DATE) -> dict:
    """Mean cross-sectional rank IC between a frozen score and the realized return.

    One IC per prediction date (all names share the same benchmark return on a
    date, so ranking raw returns equals ranking excess returns). The t-stat treats
    dates as independent; for horizons > 1 the windows overlap and it is overstated.
    """
    daily = []
    for day_rows in _by_date(rows).values():
        pairs = [(float(row[field]), float(row["realized_return"])) for row in day_rows if row[field] is not None]
        if len(pairs) < min_names:
            continue
        value = spearman([a for a, _ in pairs], [b for _, b in pairs])
        if value is not None:
            daily.append(value)
    if not daily:
        return {"dates": 0, "meanIc": None, "icStd": None, "tStat": None, "positiveShare": None}
    spread = stdev(daily) if len(daily) > 1 else None
    t_stat = mean(daily) / (spread / math.sqrt(len(daily))) if spread else None
    return {
        "dates": len(daily),
        "meanIc": mean(daily),
        "icStd": spread,
        "tStat": t_stat,
        "positiveShare": sum(value > 0 for value in daily) / len(daily),
    }


def top_bottom_spread(rows, field: str = "combined_score", min_names: int = 6) -> dict:
    """Per date: mean return of the top third by score minus the bottom third."""
    spreads = []
    for day_rows in _by_date(rows).values():
        ranked = sorted((row for row in day_rows if row[field] is not None), key=lambda row: float(row[field]))
        bucket = len(ranked) // 3
        if len(ranked) < min_names or bucket == 0:
            continue
        top = mean(float(row["realized_return"]) for row in ranked[-bucket:])
        bottom = mean(float(row["realized_return"]) for row in ranked[:bucket])
        spreads.append(top - bottom)
    if not spreads:
        return {"dates": 0, "meanSpread": None, "positiveShare": None}
    return {"dates": len(spreads), "meanSpread": mean(spreads), "positiveShare": sum(v > 0 for v in spreads) / len(spreads)}


def cluster_bootstrap_ci(rows, field: str, iterations: int = 2000, seed: int = 7, level: float = 0.90) -> tuple[float, float] | None:
    """Percentile CI for the mean of ``field``, resampling whole prediction dates.

    Names on the same date move together, so resampling individual rows would
    understate uncertainty. A fixed seed keeps the report reproducible.
    """
    grouped = {day: [float(row[field]) for row in day_rows if row[field] is not None] for day, day_rows in _by_date(rows).items()}
    grouped = {day: values for day, values in grouped.items() if values}
    if len(grouped) < 2:
        return None
    days = sorted(grouped)
    rng = random.Random(seed)
    estimates = []
    for _ in range(iterations):
        sample = [value for day in (rng.choice(days) for _ in days) for value in grouped[day]]
        estimates.append(mean(sample))
    estimates.sort()
    tail = (1 - level) / 2
    return estimates[int(tail * (iterations - 1))], estimates[int((1 - tail) * (iterations - 1))]


def decision_tiers(rows) -> list[dict]:
    tiers = []
    for decision in DECISION_TIERS:
        subset = [row for row in rows if row["serenity_decision"] == decision and row["excess_xbi"] is not None]
        if not subset:
            continue
        tiers.append({
            "decision": decision,
            "samples": len(subset),
            "dates": len({row["prediction_as_of"] for row in subset}),
            "excessXbi": mean(float(row["excess_xbi"]) for row in subset),
            "ci90": cluster_bootstrap_ci(subset, "excess_xbi"),
        })
    return tiers


def diagnostics(connection: sqlite3.Connection, horizon: int, cohort: str | None = None) -> dict:
    rows = outcome_rows(connection, horizon, cohort)
    return {
        "ic": {field: information_coefficient(rows, field) for field, _ in IC_SIGNALS},
        "topBottom": top_bottom_spread(rows),
        "tiers": decision_tiers(rows),
    }


def metrics(connection: sqlite3.Connection, horizon: int, cohort: str | None = None) -> dict:
    rows = outcome_rows(connection, horizon, cohort)
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
    diagnostic = {str(h): diagnostics(connection, h, cohort) for h in HORIZONS}
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
    num = lambda value, spec="+.3f": format(value, spec) if value is not None else "—"
    pct = lambda value: f"{value:.0%}" if value is not None else "—"
    lines += [
        "",
        "## 评分有效性：横截面 Rank IC",
        "",
        f"> 每个预测日计算冻结分数与之后收益的 Spearman 相关（当天至少 {MIN_NAMES_PER_DATE} 只股票），再对日期取平均。"
        "综合分只有在 IC 显著大于 0 **且** 高于“20日动量基线”时，才说明新闻、Serenity 和 Kronos 带来了增量信息。",
        "",
        "| 后续交易日 | 信号 | 有效预测日 | 平均IC | IC标准差 | t值 | IC>0占比 |",
        "| ---: | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for horizon in HORIZONS:
        ics = diagnostic[str(horizon)]["ic"]
        if not any(ics[field]["dates"] for field, _ in IC_SIGNALS):
            lines.append(f"| {horizon} | 全部信号 | 0 | 等待数据 | — | — | — |")
            continue
        for field, label in IC_SIGNALS:
            ic = ics[field]
            t_value = num(ic["tStat"], "+.2f") if ic["dates"] >= MIN_DATES_FOR_T else f"—（<{MIN_DATES_FOR_T}日）"
            lines.append(f"| {horizon} | {label} | {ic['dates']} | {num(ic['meanIc'])} | {num(ic['icStd'], '.3f')} | {t_value} | {pct(ic['positiveShare'])} |")
    lines += [
        "",
        f"> 有效预测日少于 {MIN_DATES_FOR_T} 个时不显示 t 值。后续交易日大于 1 时观察窗口互相重叠，t 值会被高估，只能作方向参考。",
        "",
        "## 综合分高低三分位价差",
        "",
        "| 后续交易日 | 有效预测日 | 高分1/3减低分1/3平均收益 | 价差>0占比 |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for horizon in HORIZONS:
        spread = diagnostic[str(horizon)]["topBottom"]
        lines.append(f"| {horizon} | {spread['dates']} | {fmt(spread['meanSpread'])} | {pct(spread['positiveShare'])} |")
    lines += [
        "",
        "## Serenity 决策分层（相对 XBI 超额收益）",
        "",
        "> 90% 区间按预测日整体重抽样（固定种子 2000 次），同日股票的共同波动不会被当作独立样本。区间跨过 0 表示尚无法区分。",
        "",
        "| 后续交易日 | 决策 | 观察 | 预测日 | 平均超额XBI | 90%区间 |",
        "| ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for horizon in HORIZONS:
        tiers = diagnostic[str(horizon)]["tiers"]
        if not tiers:
            lines.append(f"| {horizon} | 等待数据 | 0 | 0 | 等待数据 | — |")
        for tier in tiers:
            ci = tier["ci90"]
            interval = f"[{ci[0]:+.2%}, {ci[1]:+.2%}]" if ci else "预测日不足"
            lines.append(f"| {horizon} | {tier['decision']} | {tier['samples']} | {tier['dates']} | {fmt(tier['excessXbi'])} | {interval} |")
    lines += [
        "",
        "## 判定规则",
        "",
        "- 少于30个股票-日期观察，或少于10个独立预测日：只展示，不作有效性结论。",
        "- AI Medicine 至少30个观察、10个预测日且同时跑赢SPY、XLV、XBI与随机基线：初步有效，仍需跨市场阶段验证。",
        "- 至少100个观察、30个预测日并覆盖上涨、下跌和震荡阶段：才允许讨论稳定预测能力。",
        "- 所有基准按同一预测日与交易日周期计算，禁止事后挑选起点。",
        "- 综合分要宣称“有增量价值”，必须在同一周期上 IC t 值>2、高于20日动量基线 IC，且 research-ready 组超额 XBI 的90%区间下限>0。",
        "",
    ]
    Path(output).write_text("\n".join(lines), encoding="utf-8")
    return {"metrics": result, "diagnostics": diagnostic}


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare frozen agent predictions against market baselines")
    parser.add_argument("--database", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--cohort", default="ai-medicine")
    args = parser.parse_args()
    connection = sqlite3.connect(args.database)
    connection.row_factory = sqlite3.Row
    has_predictions = connection.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='predictions'"
    ).fetchone()[0]
    predictions = connection.execute("SELECT * FROM predictions").fetchall() if has_predictions else []
    if not predictions:
        # First run: the tracker records predictions after this step. Nothing to evaluate yet.
        create_table(connection)
        report = build_report(connection, args.output, args.cohort) if has_predictions else None
        connection.close()
        print(json.dumps({"evaluated": 0, "metrics": report, "output": args.output, "note": "no frozen predictions yet"}))
        return
    universe = sorted({row["ticker"] for row in predictions} | set(BENCHMARKS))
    earliest = min(date.fromisoformat(row["as_of"]) for row in predictions) - timedelta(days=45)
    prices = download_prices(universe, earliest.isoformat(), (date.today() + timedelta(days=1)).isoformat())
    inserted = backfill(connection, prices)
    report = build_report(connection, args.output, args.cohort)
    connection.close()
    print(json.dumps({"evaluated": inserted, **report, "output": args.output}))


if __name__ == "__main__":
    main()
