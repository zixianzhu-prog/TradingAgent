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
