import sqlite3

from benchmark_evaluator import (
    build_report,
    cluster_bootstrap_ci,
    create_table,
    decision_tiers,
    deterministic_choice,
    evaluate_prediction,
    future_return,
    information_coefficient,
    spearman,
    top_bottom_spread,
)


def test_future_return_counts_trading_observations_not_agent_runs():
    series = {
        "2026-11-02": 100.0,
        "2026-11-03": 101.0,
        "2026-11-04": 103.0,
    }
    target = future_return(series, "2026-11-02", 1)
    assert target[0] == "2026-11-03"
    assert round(target[2], 4) == 0.01


def test_evaluation_uses_same_horizon_for_agent_and_benchmarks():
    prediction = {"ticker": "AAA", "as_of": "2026-01-02", "price": 100.0, "forecast_return": 0.1}
    prices = {
        "AAA": {"2026-01-02": 100, "2026-01-05": 110},
        "BBB": {"2026-01-02": 100, "2026-01-05": 105},
        "SPY": {"2026-01-02": 100, "2026-01-05": 102},
        "XLV": {"2026-01-02": 100, "2026-01-05": 101},
        "XBI": {"2026-01-02": 100, "2026-01-05": 104},
    }
    result = evaluate_prediction(prediction, prices, ["AAA", "BBB"], 1)
    assert round(result["realized_return"], 3) == 0.1
    assert round(result["excess_spy"], 3) == 0.08
    assert round(result["excess_xbi"], 3) == 0.06
    assert result["target_as_of"] == "2026-01-05"


def test_random_baseline_is_reproducible():
    options = ["A", "B", "C"]
    assert deterministic_choice(options, "same-key") == deterministic_choice(options, "same-key")


def test_benchmark_table_is_idempotent():
    connection = sqlite3.connect(":memory:")
    create_table(connection)
    create_table(connection)
    count = connection.execute("SELECT COUNT(*) FROM sqlite_master WHERE name='benchmark_outcomes'").fetchone()[0]
    assert count == 1


def test_existing_benchmark_table_is_migrated_for_xbi():
    connection = sqlite3.connect(":memory:")
    connection.execute(
        """CREATE TABLE benchmark_outcomes (
        ticker TEXT, prediction_as_of TEXT, horizon INTEGER, target_as_of TEXT,
        target_price REAL, realized_return REAL, spy_return REAL, xlv_return REAL,
        excess_spy REAL, excess_xlv REAL, direction_correct INTEGER,
        random_ticker TEXT, random_return REAL, momentum_ticker TEXT,
        momentum_return REAL, evaluated_at TEXT)"""
    )
    create_table(connection)
    columns = {row[1] for row in connection.execute("PRAGMA table_info(benchmark_outcomes)")}
    assert {"xbi_return", "excess_xbi"} <= columns


def _row(day, ticker, score, realized, decision="watch", momentum=0.0):
    return {
        "prediction_as_of": day, "ticker": ticker, "combined_score": score, "realized_return": realized,
        "excess_xbi": realized - 0.01, "serenity_decision": decision, "past_momentum": momentum,
    }


def test_spearman_handles_ties_and_constant_input():
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == 1.0
    assert spearman([1, 2, 3, 4], [4, 3, 2, 1]) == -1.0
    assert spearman([1, 1, 1], [1, 2, 3]) is None
    assert abs(spearman([1, 2, 2, 3], [1, 2, 3, 4]) - 0.9487) < 1e-3


def test_information_coefficient_is_cross_sectional_per_date():
    rows = []
    for day in ("2026-01-02", "2026-01-05", "2026-01-06"):
        for index in range(6):
            rows.append(_row(day, f"T{index}", score=index, realized=index * 0.01, momentum=-index))
    perfect = information_coefficient(rows, "combined_score")
    assert perfect["dates"] == 3 and round(perfect["meanIc"], 6) == 1.0 and perfect["positiveShare"] == 1.0
    assert round(information_coefficient(rows, "past_momentum")["meanIc"], 6) == -1.0
    # Dates with too few names are skipped rather than producing noisy ICs.
    assert information_coefficient(rows[:4], "combined_score")["dates"] == 0


def test_top_bottom_spread_uses_score_terciles():
    rows = [_row("2026-01-02", f"T{i}", score=i, realized=i * 0.01) for i in range(6)]
    spread = top_bottom_spread(rows)
    assert spread["dates"] == 1
    assert round(spread["meanSpread"], 6) == 0.04  # mean(4,5)% - mean(0,1)%


def test_bootstrap_ci_is_reproducible_and_needs_two_dates():
    rows = [_row(day, "A", 1, value) for day, value in (("d1", 0.02), ("d2", -0.01), ("d3", 0.03))]
    first = cluster_bootstrap_ci(rows, "excess_xbi")
    assert first == cluster_bootstrap_ci(rows, "excess_xbi")
    assert first[0] <= first[1]
    assert cluster_bootstrap_ci(rows[:1], "excess_xbi") is None


def test_decision_tiers_group_by_serenity_decision():
    rows = [_row("d1", "A", 80, 0.05, "research-ready"), _row("d2", "A", 80, 0.03, "research-ready"), _row("d1", "B", 40, -0.02, "watch")]
    tiers = {tier["decision"]: tier for tier in decision_tiers(rows)}
    assert tiers["research-ready"]["samples"] == 2 and round(tiers["research-ready"]["excessXbi"], 6) == 0.03
    assert tiers["watch"]["ci90"] is None


def test_evaluation_records_point_in_time_momentum():
    prices = {"AAA": {f"2026-01-{day:02d}": 100.0 + day for day in range(1, 31)}}
    for name in ("SPY", "XLV", "XBI"):
        prices[name] = {day: 100.0 for day in prices["AAA"]}
    prediction = {"ticker": "AAA", "as_of": "2026-01-25", "price": 125.0, "forecast_return": 0.0}
    result = evaluate_prediction(prediction, prices, ["AAA"], 1)
    assert round(result["past_momentum"], 6) == round(125 / 105 - 1, 6)


def test_report_includes_ic_and_tier_sections(tmp_path):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.execute("""CREATE TABLE predictions (ticker TEXT, as_of TEXT, price REAL, news_score INTEGER,
        technical_score INTEGER, kronos_score INTEGER, combined_score INTEGER, serenity_decision TEXT)""")
    create_table(connection)
    for index in range(6):
        connection.execute("INSERT INTO predictions VALUES (?, '2026-01-02', 100, ?, ?, ?, ?, 'watch')",
                           (f"T{index}", index, index, index, index))
        connection.execute(
            """INSERT INTO benchmark_outcomes (ticker, prediction_as_of, horizon, target_as_of, target_price,
            realized_return, spy_return, xlv_return, xbi_return, excess_spy, excess_xlv, excess_xbi,
            direction_correct, past_momentum, evaluated_at)
            VALUES (?, '2026-01-02', 1, '2026-01-05', 100, ?, 0, 0, 0, ?, ?, ?, 1, 0.0, 'now')""",
            (f"T{index}", index / 100, index / 100, index / 100, index / 100),
        )
    output = tmp_path / "bench.md"
    result = build_report(connection, str(output), cohort=None)
    text = output.read_text(encoding="utf-8")
    assert "横截面 Rank IC" in text and "Serenity 决策分层" in text and "20日动量基线" in text
    assert round(result["diagnostics"]["1"]["ic"]["combined_score"]["meanIc"], 6) == 1.0
