import math
import unittest
from datetime import date

from ai_fund_lab.data import validated_bar
from ai_fund_lab.models import Bar
from ai_fund_lab.signals import trend_signal


class DataValidationTests(unittest.TestCase):
    def test_rejects_nan_price(self):
        self.assertIsNone(validated_bar(date.today(), 10, 11, 9, math.nan, 100))

    def test_rejects_inconsistent_ohlc(self):
        self.assertIsNone(validated_bar(date.today(), 10, 9, 8, 11, 100))

    def test_accepts_valid_bar_and_cleans_nan_volume(self):
        bar = validated_bar(date.today(), 10, 11, 9, 10.5, math.nan)
        self.assertIsNotNone(bar)
        self.assertEqual(bar.volume, 0.0)

    def test_signal_rejects_invalid_history_defense_in_depth(self):
        bars = [Bar(date.today(), 10, 11, 9, 10, 100) for _ in range(51)]
        bars[-1] = Bar(date.today(), 10, 11, 9, math.nan, 100)
        with self.assertRaisesRegex(ValueError, "invalid OHLC"):
            trend_signal("TEST", bars, 20, 50, 2.0)


if __name__ == "__main__":
    unittest.main()
