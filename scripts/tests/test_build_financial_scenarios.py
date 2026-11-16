import unittest

from build_financial_scenarios import analyze


def base_row():
    return {
        "ticker": "TEST", "price": 100.0, "price_date": "2026-11-13", "shares": 100_000_000,
        "quarterly_revenue_m": 250.0, "full_year_revenue_guide_m": None, "revenue_growth_pct": 20.0,
        "cash_and_securities_m": 100.0, "quarterly_net_income_m": 10.0,
        "quarterly_operating_cash_flow_m": 20.0, "adjusted_ebitda_m": 25.0,
        "net_debt_m": 200.0, "dilution_flag": "low", "data_freshness": "current_test",
        "financial_period": "Q3 2026", "financial_date": "2026-09-30",
        "next_validation_event": "next filing", "bull_case": "bull", "base_case": "base",
        "bear_case": "bear", "sources": [],
    }


class FinancialScenarioTests(unittest.TestCase):
    def test_valuation_denominators_are_explicit_and_consistent(self):
        result = analyze(base_row())
        self.assertEqual(result["market_cap_m"], 10_000.0)
        self.assertEqual(result["annualized_revenue_basis_m"], 1_000.0)
        self.assertEqual(result["price_to_sales_approx"], 10.0)
        self.assertEqual(result["enterprise_value_m"], 10_200.0)
        self.assertEqual(result["ev_to_ebitda_approx"], 102.0)
        self.assertEqual(result["ocf_yield_approx"], 0.008)
        self.assertEqual(result["revenue_basis_type"], "latest quarter annualized (not TTM)")
        self.assertIn("latest quarter annualized (not TTM)", result["calculation_note"])


    def test_scenario_probabilities_produce_auditable_sensitivity(self):
        row = base_row()
        row["scenario_inputs"] = {
            "horizon_years": 5, "metric": "sales", "net_debt_assumption_m": 200,
            "net_debt_assumption_note": "test assumption",
            "cases": {
                "bear": {"probability": 0.25, "revenue_cagr": 0.0, "annual_share_dilution": 0.04, "terminal_margin": None, "terminal_multiple": 5.0},
                "base": {"probability": 0.50, "revenue_cagr": 0.1, "annual_share_dilution": 0.02, "terminal_margin": None, "terminal_multiple": 10.0},
                "bull": {"probability": 0.25, "revenue_cagr": 0.2, "annual_share_dilution": 0.0, "terminal_margin": None, "terminal_multiple": 15.0},
            },
        }
        model = analyze(row)["scenario_model"]
        self.assertEqual(model["metric"], "sales")
        self.assertEqual(model["net_debt_assumption_note"], "test assumption")
        self.assertEqual(sum(case["probability"] for case in model["cases"].values()), 1.0)
        self.assertGreater(model["cases"]["bull"]["future_revenue_m"], model["cases"]["base"]["future_revenue_m"])
        self.assertEqual(model["cases"]["base"]["annual_share_dilution"], 0.02)
        self.assertIn("probability_weighted_case_annualized_return", model)
        self.assertIn("expected_wealth_annualized_return", model)
        self.assertIn("price_for_policy_return", model["cases"]["base"])
        self.assertFalse(model["exclusion_test_pass"])


if __name__ == "__main__":
    unittest.main()
