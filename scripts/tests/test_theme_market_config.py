import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_theme_market_config import build_config


class ThemeMarketConfigTests(unittest.TestCase):
    def test_selects_ranked_theme_candidates(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "theme.json"
            base = root / "base.json"
            output = root / "output.json"
            report.write_text(json.dumps({"companies": [
                {"ticker": "LOW", "theme": "robotics", "decision": "watch", "transmission_score": 40},
                {"ticker": "HIGH", "theme": "robotics", "decision": "watch", "transmission_score": 70},
                {"ticker": "OTHER", "theme": "biotech", "decision": "deep-research", "transmission_score": 90},
            ]}), encoding="utf-8")
            base.write_text(json.dumps({"watchlist": ["OLD"], "max_positions": 5}), encoding="utf-8")
            selected = build_config(str(report), str(base), str(output), 2, "robotics")
            self.assertEqual(selected, ["HIGH", "LOW"])
            self.assertEqual(json.loads(output.read_text())["watchlist"], ["HIGH", "LOW"])

    def test_explicit_coverage_ticker_is_kept_when_news_link_is_weak(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report, base, output = root / "theme.json", root / "base.json", root / "output.json"
            report.write_text(json.dumps({"companies": [
                {"ticker": "TEM", "theme": "ai_medicine", "decision": "deep-research", "transmission_score": 80},
                {"ticker": "GEHC", "theme": "ai_medicine", "decision": "weak-link", "transmission_score": 20},
            ]}), encoding="utf-8")
            base.write_text(json.dumps({"watchlist": [], "max_positions": 5}), encoding="utf-8")
            selected = build_config(str(report), str(base), str(output), 2, "ai_medicine", include_tickers=["GEHC"])
            self.assertEqual(selected, ["TEM", "GEHC"])


if __name__ == "__main__":
    unittest.main()
