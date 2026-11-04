from pathlib import Path

from import_tradingagents_reports import import_directory, import_report_tree


def test_imports_final_rating_and_conclusion(tmp_path: Path):
    report = tmp_path / "tradingagents-test"
    report.mkdir()
    (report / "market_report.md").write_text("## Market\nTrend is mixed.", encoding="utf-8")
    (report / "investment_plan.md").write_text(
        "### Bear Researcher Analysis\nDownside.\n\n## 投资结论\nWait for proof.\n\n"
        "**Rating**: SELL\n\nFINAL TRANSACTION PROPOSAL: SELL / AVOID\n",
        encoding="utf-8",
    )
    result = import_directory(report)
    assert result["ticker"] == "TEST"
    assert result["rating"] == "SELL"
    assert result["proposal"] == "SELL / AVOID"
    assert "Wait for proof" in result["conclusion"]
    assert result["components"]["debate"] is True


def test_complete_tree_uses_portfolio_rating(tmp_path: Path):
    report = tmp_path / "VRT_20261103"
    (report / "1_analysts").mkdir(parents=True)
    (report / "2_research").mkdir()
    (report / "4_risk").mkdir()
    (report / "5_portfolio").mkdir()
    (report / "1_analysts/market.md").write_text("Market", encoding="utf-8")
    (report / "2_research/manager.md").write_text("**Rating**: Buy", encoding="utf-8")
    (report / "5_portfolio/decision.md").write_text(
        "**Rating**: Overweight\n\n**Executive Summary**: Stage entries.", encoding="utf-8"
    )
    result = import_report_tree(report, "VRT", complete=True)
    assert result["rating"] == "OVERWEIGHT"
    assert result["status"] == "reviewed"
