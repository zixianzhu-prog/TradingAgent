import sqlite3
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from performance_tracker import backfill_outcomes, connect, record_predictions


class PerformanceTrackerTests(unittest.TestCase):
    def test_backfills_only_when_future_observation_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            connection = connect(str(Path(directory) / "history.db"))
            start = date(2026, 1, 1)
            for offset in range(6):
                connection.execute(
                    "INSERT INTO predictions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    ("TEST", str(start + timedelta(days=offset)), 100 + offset, 70, 80, 60, 0.1,
                     75, 65, 0.03, 72, "high", "watch", "now"),
                )
            connection.commit()
            self.assertEqual(backfill_outcomes(connection), 6)
            horizons = connection.execute(
                "SELECT horizon, COUNT(*) FROM outcomes GROUP BY horizon ORDER BY horizon"
            ).fetchall()
            self.assertEqual([(row[0], row[1]) for row in horizons], [(1, 5), (5, 1)])
            self.assertEqual(backfill_outcomes(connection), 0)
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
            connection.close()


if __name__ == "__main__":
    unittest.main()
