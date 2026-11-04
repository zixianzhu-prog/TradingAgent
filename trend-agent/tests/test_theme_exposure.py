import json
import tempfile
import unittest
from pathlib import Path

from trend_agent.theme_exposure import build_theme_stock_report


class ThemeExposureTests(unittest.TestCase):
    def test_theme_maps_to_verified_company_without_company_name_in_news(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            trends = root / "trends.json"
            mapping = root / "mapping.json"
            trends.write_text(json.dumps({"themes": [{
                "name": "robotics", "label": "Robotics", "score": 80,
            }]}), encoding="utf-8")
            mapping.write_text(json.dumps({"themes": {"robotics": [{
                "ticker": "BOT", "company": "Robot Co", "exposure": "actuators",
                "exposure_strength": 0.9, "evidence_status": "confirmed",
                "serenity_role": "chokepoint supplier", "pure_play": True,
            }]}}), encoding="utf-8")
            result = build_theme_stock_report(str(trends), str(mapping), str(root / "out"))
            payload = json.loads(Path(result["json_report"]).read_text(encoding="utf-8"))
            self.assertEqual(payload["companies"][0]["ticker"], "BOT")
            self.assertEqual(payload["companies"][0]["transmission_score"], 72)
            self.assertEqual(payload["companies"][0]["decision"], "deep-research")


if __name__ == "__main__":
    unittest.main()
