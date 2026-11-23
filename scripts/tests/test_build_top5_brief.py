import json
from pathlib import Path

from build_top5_brief import build, potential, render_html, scatter_svg


def write(root: Path, rel: str, payload) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def scores(**overrides):
    base = {"ai_medicine_relevance": 4, "proprietary_data_or_models": 4, "workflow_or_customer_lock_in": 4,
            "commercial_validation": 4, "multi_node_control": 4, "financial_resilience": 4, "primary_evidence_coverage": 4}
    return base | overrides


def fixture(root: Path, serenity: bool = True) -> None:
    universe = [
        {"ticker": "AAA", "company": "Alpha", "segment": "imaging", "scores": scores(ai_medicine_relevance=5)},
        {"ticker": "BBB", "company": "Beta", "segment": "data", "scores": scores()},
        {"ticker": "NVDA", "company": "NVIDIA", "segment": "compute", "scores": scores(ai_medicine_relevance=2)},
        {"ticker": "OUT", "company": "Outside", "segment": "tools", "scores": scores(), "screen_reason": "not core"},
    ]
    theses = [{"ticker": t, "company": t, "thesis": "x", "why_now": "y", "serenity_angle": "z", "bear_case": "b",
               "falsifiers": ["f1", "f2", "f3", "f4"], "sources": ["https://a.example/1", "https://a.example/1"]}
              for t in ("AAA", "BBB", "NVDA")]
    financials = [{"ticker": t, "revenue_growth_pct": 25.0, "price_to_sales_approx": 5.0, "market_cap_m": 2000,
                   "quarterly_revenue_m": 100, "financial_period": "Q3 2026", "price_date": "2026-11-13",
                   "sources": ["https://a.example/1"]} for t in ("AAA", "BBB", "NVDA")]
    gates = [{"ticker": "AAA", "substantiatedScore": 60, "decision": "watch", "hardGateFailures": []},
             {"ticker": "BBB", "substantiatedScore": 30, "decision": "watch", "hardGateFailures": ["customer_dependency"]},
             {"ticker": "NVDA", "substantiatedScore": 20, "decision": "revalidate", "hardGateFailures": []}]
    write(root, "trend-agent/ai-medicine-universe.json", {"companies": universe})
    write(root, "trend-agent/ai-medicine-theses.json", {"candidates": theses, "expanded_deep_dives": []})
    write(root, "state/ai-medicine-financial-scenarios.json", {"companies": financials})
    write(root, "state/serenity-gate-results.json", {"companies": gates})
    write(root, "state/event-revalidation.json", {"revalidationTasks": [{"ticker": "BBB", "title": "CEO departs", "url": "u"}] * 2})
    write(root, "state/fda-ai-devices.json", {"companyCoverage": [{"ticker": "AAA", "matchedDevices": 9}], "summary": {"totalDevices": 1614}})
    reviewed = ("AAA", "BBB") if serenity else ()
    gate_status = {"pure_play": "pass", "chokepoint_evidence": "partial", "customer_dependency": "pass",
                   "multi_node_control": "partial", "earnings_validation": "pass"}
    write(root, "state/serenity-auto-assessments.json", {"companies": [
        {"ticker": t, "review_path": f"state/serenity-reviews/{t}-claude-x.json", **gate_status} for t in reviewed]})
    write(root, "state/serenity-review-status.json", {"summary": {}, "companies": {
        t: {"review": "current", "claudeMemo": "citation-checked"} for t in reviewed}})


def test_ranking_keeps_potential_and_evidence_separate(tmp_path):
    fixture(tmp_path)
    payload = build(tmp_path)
    assert [row["ticker"] for row in payload["ranking"]] == ["AAA", "BBB"]
    beta = payload["ranking"][1]
    assert beta["lowEvidence"] is True  # flagged, still ranked
    assert len(beta["openEvents"]) == 1  # duplicate event titles collapse
    assert [row["ticker"] for row in payload["benchmarks"]] == ["NVDA"]
    assert payload["screenedOut"][0]["ticker"] == "OUT"
    assert payload["ranking"][0]["fdaAiDevices"] == 9
    assert payload["ranking"][0]["sources"] == ["https://a.example/1"]
    assert len(payload["ranking"][0]["falsifiers"]) == 3


def test_milestone_revenue_does_not_count_as_durable_growth():
    steady = potential(scores(), {"revenue_growth_pct": 30.0, "price_to_sales_approx": 6.0})
    milestone = potential(scores(), {"revenue_growth_pct": 250.0, "price_to_sales_approx": None})
    assert steady["parts"]["growth"] > milestone["parts"]["growth"]
    assert abs(sum(steady["parts"].values()) - steady["total"]) < 0.2


def test_html_escapes_text_and_draws_every_company(tmp_path):
    fixture(tmp_path)
    payload = build(tmp_path)
    payload["top"][0]["bearCase"] = "<script>alert(1)</script>"
    page = render_html(payload)
    assert "<script>alert" not in page and "&lt;script&gt;" in page
    svg = scatter_svg(payload["ranking"])
    assert svg.count("<circle") == len(payload["ranking"])


def test_radar_block_appears_only_with_radar_data(tmp_path):
    fixture(tmp_path)
    payload = build(tmp_path)
    assert 'id="radar"' not in render_html(payload, root=tmp_path)
    write(tmp_path, "state/replay/case.json", {"case": "covid-2020", "dailySignals": [{"date": "2020-01-25", "signals": []}],
                                                "detection": None, "groundTruth": {"term": "ncov", "firstInData": None,
                                                "articlesInWindow": 0, "dailyCounts": {}, "firedOn": []}})
    page = render_html(payload, root=tmp_path)
    assert 'id="radar"' in page and "Spotting the next theme early" in page and 'href="#radar"' in page
    assert page.index('id="radar"') < page.index('id="method-h"')


def test_picks_split_into_serenity_buckets(tmp_path):
    fixture(tmp_path)
    fin = json.loads((tmp_path / "state/ai-medicine-financial-scenarios.json").read_text())
    for row in fin["companies"]:
        row["market_cap_m"] = 30000 if row["ticker"] == "AAA" else 1500
    (tmp_path / "state/ai-medicine-financial-scenarios.json").write_text(json.dumps(fin))
    payload = build(tmp_path)
    assert [r["ticker"] for r in payload["picks"]["durable"]] == ["AAA"]
    assert [r["ticker"] for r in payload["picks"]["asymmetric"]] == ["BBB"]
    assert payload["picks"]["asymmetric"][0]["bucketRank"] == 1
    page = render_html(payload, root=tmp_path)
    assert "Durable compounders" in page and "Asymmetric upside" in page


def test_only_serenity_reviewed_companies_are_picked_and_gates_set_scores(tmp_path):
    fixture(tmp_path, serenity=False)
    unreviewed = build(tmp_path)
    assert unreviewed["top"] == []
    assert all(not r["serenityReviewed"] for r in unreviewed["ranking"])
    fixture(tmp_path, serenity=True)
    reviewed = build(tmp_path)
    alpha = next(r for r in reviewed["ranking"] if r["ticker"] == "AAA")
    assert alpha["serenityReviewed"] and alpha["scoreBasis"].startswith("Serenity")
    # chokepoint partial (3) + customer pass (5) + multi-node partial (3) out of 15, times 35
    assert alpha["potential"]["parts"]["moat"] == round(11 / 15 * 35, 1)
    assert alpha["potential"]["parts"]["exposure"] == 20.0  # pure_play pass


def test_order_range_levels_and_status():
    from build_top5_brief import order_range
    fin = {"price": 48.46, "scenario_inputs": {"inputs_verified": False},
           "scenario_model": {"horizon_years": 5, "cases": {
               "base": {"price_for_policy_return": 39.99, "annualized_return": 0.078},
               "bear": {"price_for_policy_return": 39.81, "price_for_zero_return": 23.51, "annualized_return": -0.135}}}}
    o = order_range(fin)
    assert o["upper"] == 39.81 and o["floor"] == 23.51 and o["status"] == "above" and o["gapToUpper"] > 0.2
    cheap = order_range(fin, latest_price=30.0)
    assert cheap["status"] == "in-range" and cheap["baseReturn"] > 0.078  # lower price, higher implied return
    assert order_range(fin, latest_price=20.0)["status"] == "below-floor"
    assert order_range({"price": 10, "scenario_model": {}}) is None


def test_implied_growth_matches_base_case_at_policy_price():
    from build_top5_brief import implied_growth
    # At the base-case policy price, the growth needed for 12% a year equals the base-case growth.
    fin = {"shares": 87887561, "scenario_model": {"horizon_years": 5, "metric": "sales", "revenue_basis_m": 291.6,
           "net_debt_assumption_m": -167.7, "cases": {"base": {"terminal_multiple": 7.0, "annual_share_dilution": 0.03}}}}
    assert abs(implied_growth(fin, 39.99) - 0.28) < 0.002
    assert implied_growth(fin, 47.62) > 0.30  # a higher price assumes faster growth
    assert implied_growth({"scenario_model": {}}, 10) is None


def test_calibrated_multiples_follow_one_rule_and_skip_ebitda_models():
    import calibrate_multiples as cm
    snapshot = {"data_date": "January 2026", "industries": {"Healthcare Products": {"ps": 4.36, "firms": 204},
                                                             "Heathcare Information and Technology": {"ps": 4.7, "firms": 115}}}
    rows = [{"ticker": t, "price": p, "shares": 1e8, "quarterly_revenue_m": 100.0, "scenario_inputs": {"metric": "sales"}}
            for t, p in (("HTFL", 60.0), ("CBLL", 20.0), ("CAI", 24.0), ("TEM", 40.0), ("ISRG", 52.0))]
    rows.append({"ticker": "RDNT", "price": 10.0, "shares": 1e8, "quarterly_revenue_m": 100.0, "scenario_inputs": {"metric": "ebitda"}})
    rows.append({"ticker": "NVDA", "price": 200.0, "shares": 1e8, "quarterly_revenue_m": 100.0})
    out = cm.calibrate(rows, snapshot)
    assert "RDNT" not in out["companies"] and "NVDA" not in out["peers"]
    htfl = out["companies"]["HTFL"]
    assert htfl["bear"] == 4.7 and htfl["bear"] <= htfl["base"] <= htfl["bull"]
    assert htfl["base"] == out["peerQuartiles"]["median"]
    assert "Damodaran" in htfl["basis"]["bear"] and "peers" in htfl["basis"]["base"]


def test_parse_damodaran_reads_industry_rows():
    import calibrate_multiples as cm
    page = ("<html>Date updated: January 2026<table><tr><td>Industry Name</td><td>Number of firms</td><td>Price/Sales</td>"
            "<td>Net Margin</td><td>EV/Sales</td><td>Pre-tax Operating Margin</td></tr>"
            "<tr><td>Healthcare Products</td><td>204</td><td>4.36</td><td>9.61%</td><td>4.76</td><td>15.47%</td></tr></table></html>")
    snap = cm.parse_damodaran(page)
    assert snap["data_date"] == "January 2026" and snap["industries"]["Healthcare Products"]["ps"] == 4.36


def test_growth_paths_fade_and_keep_case_order():
    import calibrate_growth as cg
    m = cg.growth_paths(start=0.40, fundamental=0.053, historical=0.156)
    assert m["paths"]["base"][-1] == 0.053 and m["paths"]["bull"][-1] == 0.156
    assert m["paths"]["bear"][1] == 0.053 and m["paths"]["bear"][4] == 0.053   # bear reaches the industry rate in year 2
    assert m["cagr"]["bear"] < m["cagr"]["base"] < m["cagr"]["bull"] < 0.40


def test_parse_growth_table_reads_rows_split_by_inline_tags():
    import calibrate_growth as cg
    page = ("<table><tr><td>Industry Name</td><td>Number of Firms</td><td>ROE</td><td>Retention Ratio</td><td>Fundamental Growth</td></tr>"
            "<tr><td>Healthcare Products</td><td>204</td><td>11.26%</td><td>64.36%</td><td>7.25%</td></tr>"
            "<tr><td>Financial Svcs. (Non-bank <b>&amp;</b> Insurance)</td><td>10</td><td>NA</td><td>NA</td><td>NA</td></tr>"
            "<tr><td>Total Market</td><td>5994</td><td>17.21%</td><td>65.17%</td><td>11.22%</td></tr></table>")
    rows = cg.parse_growth_table(page, "Fundamental Growth")
    assert rows == {"Healthcare Products": 0.0725, "Total Market": 0.1122}


def test_fiscal_year_revenue_keeps_annual_10k_values_only():
    import calibrate_growth as cg
    facts = {"facts": {"us-gaap": {"RevenueFromContractWithCustomerExcludingAssessedTax": {"units": {"USD": [
        {"start": "2024-01-01", "end": "2024-12-31", "val": 125.8e6, "form": "10-K", "filed": "2025-02-20"},
        {"start": "2025-01-01", "end": "2025-12-31", "val": 176.0e6, "form": "10-K", "filed": "2026-02-18"},
        {"start": "2025-07-01", "end": "2025-09-30", "val": 50.0e6, "form": "10-Q", "filed": "2025-11-01"},
        {"start": "2025-01-01", "end": "2025-09-30", "val": 120.0e6, "form": "10-Q", "filed": "2025-11-01"},
    ]}}}}}
    assert cg.fiscal_year_revenue(facts) == [("2024", 125.8), ("2025", 176.0)]
