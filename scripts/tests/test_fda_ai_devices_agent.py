import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fda_ai_devices_agent import build_payload, map_companies, parse_csv


CSV_FIXTURE = """Date of Final Decision,Submission Number,Device,Company,Panel (Lead),Primary Product Code
06/24/2026,K253560,Enhanced Boundary for PCCT,"Ge Medical Systems, LLC",Radiology,JAK
06/15/2026,K253825,Saige-Dx,"DeepHealth, Inc.",Radiology,QDQ
12/16/2025,K251763,IRISeg,"Intuitive Surgical, Inc.",Radiology,QIH
"""


CONFIG = {
    "source_url": "https://www.fda.gov/example.csv",
    "list_url": "https://www.fda.gov/example",
    "companies": [
        {"ticker": "GEHC", "company": "GE HealthCare", "manufacturer_patterns": ["GE Medical Systems"]},
        {"ticker": "RDNT", "company": "RadNet", "manufacturer_patterns": ["DeepHealth"]},
        {"ticker": "IQV", "company": "IQVIA", "manufacturer_patterns": ["IQVIA"]},
    ],
}


class FDADevicesAgentTests(unittest.TestCase):
    def test_parses_and_maps_subsidiary_manufacturers(self):
        rows = parse_csv(CSV_FIXTURE)
        mapped, notes = map_companies(rows, CONFIG)
        self.assertEqual(len(rows), 3)
        self.assertEqual(mapped["GEHC"][0]["submissionNumber"], "K253560")
        self.assertEqual(mapped["RDNT"][0]["device"], "Saige-Dx")
        self.assertEqual(mapped["IQV"], [])
        self.assertEqual(notes[-1]["interpretation"], "no-direct-device-sponsor-match; retain as adjacent workflow/infrastructure exposure")

    def test_snapshot_diff_counts_new_submissions(self):
        rows = parse_csv(CSV_FIXTURE)
        payload = build_payload(rows, CONFIG, {"devices": rows[:1]})
        self.assertEqual(payload["summary"]["newSincePreviousSnapshot"], 2)
        self.assertEqual(payload["summary"]["removedSincePreviousSnapshot"], 0)

    def test_rejects_schema_drift(self):
        with self.assertRaises(ValueError):
            parse_csv("date,id\n2026-01-01,K1\n")


if __name__ == "__main__":
    unittest.main()
