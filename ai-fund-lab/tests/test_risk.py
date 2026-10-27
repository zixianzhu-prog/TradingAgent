import unittest
from datetime import date

from ai_fund_lab.config import Settings
from ai_fund_lab.models import Portfolio, Signal
from ai_fund_lab.risk import build_order


class RiskTests(unittest.TestCase):
    def test_position_is_bounded_by_position_cap(self):
        settings = Settings()
        portfolio = Portfolio(cash=100_000)
        signal = Signal("TEST", 0.9, "buy", 100, 99, ("test",), date.today())
        order = build_order(signal, portfolio, {"TEST": 100}, settings)
        self.assertIsNotNone(order)
        self.assertEqual(order.quantity, 200)

    def test_low_score_does_not_create_order(self):
        settings = Settings()
        portfolio = Portfolio(cash=100_000)
        signal = Signal("TEST", 0.5, "buy", 100, 95, ("test",), date.today())
        self.assertIsNone(build_order(signal, portfolio, {"TEST": 100}, settings))

    def test_live_trading_is_rejected(self):
        settings = Settings(allow_live_trading=True)
        with self.assertRaisesRegex(ValueError, "disabled"):
            settings.validate()


if __name__ == "__main__":
    unittest.main()
