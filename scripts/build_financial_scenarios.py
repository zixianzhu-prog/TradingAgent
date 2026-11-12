from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def analyze(row: dict) -> dict:
    market_cap_m = row["price"] * row["shares"] / 1_000_000
    guide = row.get("full_year_revenue_guide_m")
    annualized_revenue = guide or row["quarterly_revenue_m"] * 4
    price_to_sales = market_cap_m / annualized_revenue if annualized_revenue > 0 else None
    quarterly_burn = None
    if row.get("adjusted_ebitda_m", 0) and row["adjusted_ebitda_m"] > 0:
        quarterly_burn = None
    elif row.get("quarterly_operating_cash_flow_m") is not None:
        quarterly_burn = max(0.0, -row["quarterly_operating_cash_flow_m"])
    elif row.get("nine_month_operating_cash_flow_m") is not None:
        quarterly_burn = max(0.0, -row["nine_month_operating_cash_flow_m"] / 3)
    elif row.get("quarterly_net_income_m") is not None:
        quarterly_burn = max(0.0, -row["quarterly_net_income_m"])
    runway_years = row["cash_and_securities_m"] / (quarterly_burn * 4) if quarterly_burn else None
    if row.get("adjusted_ebitda_m", 0) and row["adjusted_ebitda_m"] > 0:
        funding_risk = "low"
    elif runway_years is not None and runway_years >= 3:
        funding_risk = "medium" if row["dilution_flag"] == "high" else "low"
    elif runway_years is not None and runway_years >= 2:
        funding_risk = "medium"
    else:
        funding_risk = "high"
    if row["ticker"] in {"RXRX", "ABCL"}:
        valuation_label = "pipeline optionality; revenue multiple not decision-useful"
        price_to_sales = None
    elif price_to_sales is not None and price_to_sales >= 8:
        valuation_label = "premium; execution-sensitive"
    elif price_to_sales is not None and price_to_sales >= 4:
        valuation_label = "growth valuation; requires continued validation"
    else:
        valuation_label = "not obviously premium on sales; inspect quality and dilution"
    action = "valuation-watch" if row["data_freshness"].startswith("current") else "wait-for-earnings"
    if funding_risk == "low" and row["revenue_growth_pct"] >= 20:
        action = "deep-valuation-research"
    return {
        **row,
        "market_cap_m": round(market_cap_m, 1),
        "annualized_revenue_basis_m": round(annualized_revenue, 1),
        "price_to_sales_approx": round(price_to_sales, 1) if price_to_sales is not None else None,
        "quarterly_burn_proxy_m": round(quarterly_burn, 1) if quarterly_burn is not None else None,
        "runway_years_proxy": round(runway_years, 1) if runway_years is not None else None,
        "funding_risk": funding_risk,
        "valuation_label": valuation_label,
        "research_action": action,
        "calculation_note": "Runway is a simple cash/burn proxy, not company guidance. P/S uses guidance when available, otherwise annualized latest-quarter revenue and is unreliable for milestone-driven biotech.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build transparent AI Medicine valuation and funding scenarios")
    parser.add_argument("--financials", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()
    source = json.loads(Path(args.financials).read_text(encoding="utf-8"))
    companies = [analyze(row) for row in source["companies"]]
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "asOf": source["as_of"],
        "methodNote": source["method_note"],
        "companies": companies,
    }
    json_output = Path(args.json_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# AI Medicine 估值与资金安全情景",
        "",
        f"> 数据截至 {source['as_of']}。估值标签和现金跑道是透明规则生成的研究辅助，不是目标价或买卖建议。",
        "",
        "| 股票 | 市值估算 | 收入增长 | 近似P/S | 现金/证券 | 跑道代理 | 融资风险 | 研究动作 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in companies:
        ps = f"{row['price_to_sales_approx']:.1f}x" if row["price_to_sales_approx"] is not None else "n/a"
        runway = f"{row['runway_years_proxy']:.1f}年" if row["runway_years_proxy"] is not None else "正向EBITDA/不适用"
        lines.append(f"| {row['ticker']} | ${row['market_cap_m']/1000:.2f}B | {row['revenue_growth_pct']:+.1f}% | {ps} | ${row['cash_and_securities_m']:.1f}M | {runway} | {row['funding_risk']} | {row['research_action']} |")
    for row in companies:
        lines += [
            "",
            f"## {row['ticker']}",
            "",
            f"- 估值判断：{row['valuation_label']}",
            f"- 乐观情景：{row['bull_case']}",
            f"- 中性情景：{row['base_case']}",
            f"- 悲观情景：{row['bear_case']}",
            f"- 下一验证事件：{row['next_validation_event']}",
            f"- 数据状态：{row['data_freshness']}；财务期：{row['financial_period']}",
            "- 官方来源：" + " · ".join(f"[来源 {i+1}]({url})" for i, url in enumerate(row["sources"])),
        ]
    Path(args.markdown_output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json_output)
    print(args.markdown_output)


if __name__ == "__main__":
    main()
