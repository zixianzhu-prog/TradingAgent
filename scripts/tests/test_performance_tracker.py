import sqlite3
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmark_evaluator import create_table
from performance_tracker import backfill_prediction_tasks, build_report, connect, record_cohort_history, record_predictions


class PerformanceTrackerTests(unittest.TestCase):
    def test_report_uses_trading_day_outcomes_not_agent_run_gaps(self):
        """A skipped agent run must not stretch a 1-day outcome across several days."""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            connection = connect(str(root / "history.db"))
            # Agent ran on 11-04 and next on 11-09 (two trading days skipped).
            for day, price in (("2026-11-04", 100.0), ("2026-11-09", 130.0)):
                connection.execute(
                    "INSERT INTO predictions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    ("TEST", day, price, 70, 80, 60, 0.1, 75, 65, 0.03, 72, "high", "watch", "now"),
                )
            connection.commit()
            build_report(connection, str(root / "empty.md"))
            self.assertIn("| 1 | 0 |", (root / "empty.md").read_text(encoding="utf-8"))
            create_table(connection)
            connection.execute(
                """INSERT INTO benchmark_outcomes (ticker, prediction_as_of, horizon, target_as_of, target_price,
                realized_return, spy_return, xlv_return, xbi_return, excess_spy, excess_xlv, excess_xbi,
                direction_correct, evaluated_at) VALUES ('TEST', '2026-11-04', 1, '2026-11-05', 101, 0.01,
                0, 0, 0.005, 0.01, 0.01, 0.005, 1, 'now')"""
            )
            connection.commit()
            build_report(connection, str(root / "report.md"))
            text = (root / "report.md").read_text(encoding="utf-8")
            self.assertIn("| 1 | 1 | +1.00% | +0.50% |", text)
            self.assertNotIn("+30.00%", text)
            connection.close()

    def test_cohort_history_uses_saved_market_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            connection = connect(str(root / "history.db"))
            connection.execute(
                "INSERT INTO predictions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("TEST", "2026-01-02", 100, 70, 80, 60, 0.1, 75, 65, 0.03, 72, "high", "watch", "now"),
            )
            connection.commit()
            report_dir = root / "market"
            report_dir.mkdir()
            (report_dir / "run-1.json").write_text(
                __import__("json").dumps({"results": [{"signal": {"ticker": "TEST", "as_of": "2026-01-02"}}]}),
                encoding="utf-8",
            )
            self.assertEqual(record_cohort_history(connection, str(report_dir), "ai-medicine"), 1)
            self.assertEqual(record_cohort_history(connection, str(report_dir), "ai-medicine"), 0)
            connection.close()

    def test_legacy_task_backfill_uses_only_frozen_columns(self):
        with tempfile.TemporaryDirectory() as directory:
            connection = connect(str(Path(directory) / "history.db"))
            connection.execute(
                "INSERT INTO predictions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ("TEST", "2026-01-02", 100, 70, 80, 60, -0.2, 75, 65, -0.03, 72, "high", "research-ready", "then"),
            )
            connection.commit()
            self.assertEqual(backfill_prediction_tasks(connection), 3)
            self.assertEqual(backfill_prediction_tasks(connection), 0)
            rows = connection.execute(
                "SELECT task_type, claim FROM prediction_tasks ORDER BY task_type"
            ).fetchall()
            self.assertEqual([(row[0], row[1]) for row in rows], [
                ("event_impact", "negative"),
                ("long_term_quality", "durable-candidate"),
                ("price_direction", "down"),
            ])
            connection.close()

    def test_prediction_is_frozen_on_first_insert(self):
        with tempfile.TemporaryDirectory() as directory:
            connection = connect(str(Path(directory) / "history.db"))
            signal = {"ticker": "TEST", "as_of": "2026-01-02", "price": 100.0, "score": 0.8}
            market = {"results": [{"signal": signal}], "kronos": {"TEST": {"forecast_return": 0.02}}}
            news = {"companies": [{"ticker": "TEST", "news_score": 70, "confidence": "high"}]}
            serenity = {"companies": [{"ticker": "TEST", "serenity_decision": "watch"}]}
            self.assertEqual(record_predictions(connection, market, news, serenity), 1)
            news["companies"][0]["news_score"] = 5
            self.assertEqual(record_predictions(connection, market, news, serenity), 0)
            frozen = connection.execute("SELECT news_score FROM predictions").fetchone()[0]
            self.assertEqual(frozen, 70)
            tasks = connection.execute(
                "SELECT task_type, claim FROM prediction_tasks ORDER BY task_type"
            ).fetchall()
            self.assertEqual(
                [(row[0], row[1]) for row in tasks],
                [
                    ("event_impact", "neutral"),
                    ("long_term_quality", "needs-validation"),
                    ("price_direction", "up"),
                ],
            )
            cohort = connection.execute("SELECT cohort FROM prediction_cohorts").fetchone()[0]
            self.assertEqual(cohort, "general")
            connection.close()


if __name__ == "__main__":
    unittest.main()
