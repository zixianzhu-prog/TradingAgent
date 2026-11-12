import sqlite3

from benchmark_evaluator import create_table, deterministic_choice, evaluate_prediction, future_return


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
