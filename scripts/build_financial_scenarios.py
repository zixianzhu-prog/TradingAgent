from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def analyze(row: dict) -> dict:
    market_cap_m = row["price"] * row["shares"] / 1_000_000
    guide = row.get("full_year_revenue_guide_m")
    annualized_revenue = guide or row["quarterly_revenue_m"] * 4
    revenue_basis_type = "full-year guidance" if guide else "latest quarter annualized (not TTM)"
    price_to_sales = market_cap_m / annualized_revenue if annualized_revenue > 0 else None
    net_debt = row.get("net_debt_m")
    enterprise_value_m = market_cap_m + net_debt if net_debt is not None else None
    annualized_ebitda_m = row.get("adjusted_ebitda_m") * 4 if row.get("adjusted_ebitda_m") is not None else None
    ev_to_ebitda = enterprise_value_m / annualized_ebitda_m if enterprise_value_m is not None and annualized_ebitda_m and annualized_ebitda_m > 0 else None
    annualized_ocf_m = row.get("quarterly_operating_cash_flow_m") * 4 if row.get("quarterly_operating_cash_flow_m") is not None else None
    ocf_yield = annualized_ocf_m / market_cap_m if annualized_ocf_m is not None and annualized_ocf_m > 0 else None
    quarterly_burn = None
    profitable_or_cash_generative = any(
        row.get(field) is not None and row.get(field) > 0
        for field in ("adjusted_ebitda_m", "quarterly_operating_cash_flow_m", "quarterly_net_income_m")
    )
    if profitable_or_cash_generative:
        quarterly_burn = None
    elif row.get("quarterly_operating_cash_flow_m") is not None:
        quarterly_burn = max(0.0, -row["quarterly_operating_cash_flow_m"])
    elif row.get("nine_month_operating_cash_flow_m") is not None:
        quarterly_burn = max(0.0, -row["nine_month_operating_cash_flow_m"] / 3)
    elif row.get("quarterly_net_income_m") is not None:
        quarterly_burn = max(0.0, -row["quarterly_net_income_m"])
    runway_years = row["cash_and_securities_m"] / (quarterly_burn * 4) if quarterly_burn else None
    if profitable_or_cash_generative:
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
    scenario_model = None
    scenario_inputs = row.get("scenario_inputs")
    if scenario_inputs:
        years = int(scenario_inputs["horizon_years"])
        if years <= 0:
            raise ValueError(f"{row['ticker']}: scenario horizon must be positive")
        probability_total = sum(float(case["probability"]) for case in scenario_inputs["cases"].values())
        if abs(probability_total - 1.0) > 1e-9:
            raise ValueError(f"{row['ticker']}: scenario probabilities must sum to 1")
        assumed_net_debt = float(scenario_inputs.get("net_debt_assumption_m", net_debt or 0))
        cases = {}
        weighted_terminal_equity = 0.0
        weighted_dilution_adjusted_terminal_equity = 0.0
        weighted_case_annualized_return = 0.0
        for name, assumptions in scenario_inputs["cases"].items():
            future_revenue = annualized_revenue * (1 + float(assumptions["revenue_cagr"])) ** years
            if scenario_inputs["metric"] == "ebitda":
                terminal_ebitda = future_revenue * float(assumptions["terminal_margin"])
                terminal_ev = terminal_ebitda * float(assumptions["terminal_multiple"])
            else:
                terminal_ebitda = None
                terminal_ev = future_revenue * float(assumptions["terminal_multiple"])
            terminal_equity = max(0.0, terminal_ev - assumed_net_debt)
            annual_dilution = float(assumptions.get("annual_share_dilution", 0.0))
            if annual_dilution < 0:
                raise ValueError(f"{row['ticker']}: annual dilution cannot be negative")
            diluted_share_factor = (1 + annual_dilution) ** years
            per_share_equity_factor = terminal_equity / (market_cap_m * diluted_share_factor)
            annualized_return = per_share_equity_factor ** (1 / years) - 1 if terminal_equity > 0 else -1.0
            probability = float(assumptions["probability"])
            weighted_terminal_equity += probability * terminal_equity
            weighted_dilution_adjusted_terminal_equity += probability * terminal_equity / diluted_share_factor
            weighted_case_annualized_return += probability * annualized_return
            cases[name] = {
                **assumptions,
                "future_revenue_m": round(future_revenue, 1),
                "terminal_ebitda_m": round(terminal_ebitda, 1) if terminal_ebitda is not None else None,
                "terminal_enterprise_value_m": round(terminal_ev, 1),
                "terminal_equity_value_m": round(terminal_equity, 1),
                "annual_share_dilution": annual_dilution,
                "diluted_share_factor": round(diluted_share_factor, 4),
                "annualized_return": round(annualized_return, 4),
            }
        expected_wealth_annualized_return = (
            (weighted_dilution_adjusted_terminal_equity / market_cap_m) ** (1 / years) - 1
            if weighted_dilution_adjusted_terminal_equity > 0 else -1.0
        )
        policy = scenario_inputs.get("safety_margin_policy", {"base_min_return": 0.12, "bear_min_return": -0.10})
        base_min_return = float(policy["base_min_return"])
        bear_min_return = float(policy["bear_min_return"])
        for case_name, target_return in (("base", base_min_return), ("bear", bear_min_return)):
            case = cases[case_name]
            terminal_per_current_share_equity = case["terminal_equity_value_m"] / case["diluted_share_factor"]
            max_entry_market_cap = terminal_per_current_share_equity / (1 + target_return) ** years
            target_price = row["price"] * max_entry_market_cap / market_cap_m
            case["price_for_policy_return"] = round(target_price, 2)
            case["price_change_to_policy_return"] = round(target_price / row["price"] - 1, 4)
            case["policy_return_threshold"] = target_return
            case["passes_policy_return"] = case["annualized_return"] >= target_return
        inputs_verified = bool(scenario_inputs.get("inputs_verified", False))
        exclusion_pass = cases["base"]["passes_policy_return"] and cases["bear"]["passes_policy_return"] and inputs_verified
        scenario_model = {
            "horizon_years": years,
            "metric": scenario_inputs["metric"],
            "revenue_basis_m": round(annualized_revenue, 1),
            "net_debt_assumption_m": assumed_net_debt,
            "net_debt_assumption_note": scenario_inputs.get("net_debt_assumption_note", "No assumption note supplied."),
            "cases": cases,
            "probability_weighted_terminal_equity_m": round(weighted_terminal_equity, 1),
            "probability_weighted_dilution_adjusted_terminal_equity_m": round(weighted_dilution_adjusted_terminal_equity, 1),
            "expected_wealth_annualized_return": round(expected_wealth_annualized_return, 4),
            "probability_weighted_case_annualized_return": round(weighted_case_annualized_return, 4),
            "probability_basis": scenario_inputs.get("probability_basis", "Analyst-set sensitivity weights; not empirically estimated probabilities."),
            "safety_margin_policy": {"base_min_return": base_min_return, "bear_min_return": bear_min_return},
            "inputs_verified": inputs_verified,
            "exclusion_test_pass": exclusion_pass,
            "limitation": "Illustrative per-share exclusion test, not a DCF or target price. Growth, dilution, probabilities and terminal multiples are analyst-set assumptions, not evidence-generated forecasts. Passing cannot upgrade a company; failing can only keep it from upgrade.",
        }
    return {
        **row,
        "market_cap_m": round(market_cap_m, 1),
        "annualized_revenue_basis_m": round(annualized_revenue, 1),
        "revenue_basis_type": revenue_basis_type,
        "price_to_sales_approx": round(price_to_sales, 1) if price_to_sales is not None else None,
        "enterprise_value_m": round(enterprise_value_m, 1) if enterprise_value_m is not None else None,
        "net_debt_m": net_debt,
        "annualized_ebitda_m": round(annualized_ebitda_m, 1) if annualized_ebitda_m is not None else None,
        "ev_to_ebitda_approx": round(ev_to_ebitda, 1) if ev_to_ebitda is not None else None,
        "annualized_ocf_m": round(annualized_ocf_m, 1) if annualized_ocf_m is not None else None,
        "ocf_yield_approx": round(ocf_yield, 4) if ocf_yield is not None else None,
        "scenario_model": scenario_model,
        "quarterly_burn_proxy_m": round(quarterly_burn, 1) if quarterly_burn is not None else None,
        "runway_years_proxy": round(runway_years, 1) if runway_years is not None else None,
        "funding_risk": funding_risk,
        "valuation_label": valuation_label,
        "research_action": action,
        "calculation_note": f"Price date: {row.get('price_date', 'not-provided')}. P/S denominator is {revenue_basis_type} ({annualized_revenue:.1f}M). Annualizing one quarter can distort seasonal businesses. Runway is a simple cash/burn proxy, not company guidance. EV/EBITDA and OCF yield appear only when meaningful inputs exist. Metrics are not directly comparable across business models.",
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
        "| 股票 | 价格日期 | 市值估算 | 净负债 | 收入口径 | 收入基数 | 近似P/S | EV/EBITDA | OCF收益率 | 融资风险 |",
        "| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in companies:
        ps = f"{row['price_to_sales_approx']:.1f}x" if row["price_to_sales_approx"] is not None else "n/a"
        net_debt_text = f"${row['net_debt_m']/1000:.2f}B" if row["net_debt_m"] is not None else "未核验"
        ev_ebitda = f"{row['ev_to_ebitda_approx']:.1f}x" if row["ev_to_ebitda_approx"] is not None else ("亏损，不适用" if row.get("adjusted_ebitda_m") is not None and row.get("adjusted_ebitda_m") <= 0 else "缺少可比数据")
        ocf_yield = f"{row['ocf_yield_approx']:.1%}" if row["ocf_yield_approx"] is not None else ("负值，不适用" if row.get("quarterly_operating_cash_flow_m") is not None and row.get("quarterly_operating_cash_flow_m") <= 0 else "未核验")
        lines.append(f"| {row['ticker']} | {row['price_date']} | ${row['market_cap_m']/1000:.2f}B | {net_debt_text} | {row['revenue_basis_type']} | ${row['annualized_revenue_basis_m']:.1f}M | {ps} | {ev_ebitda} | {ocf_yield} | {row['funding_risk']} |")
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
            f"- 主要竞争对手：{', '.join(row.get('competitors', [])) or '待补充'}",
            f"- 价格日期：{row['price_date']}；财务期：{row['financial_period']}（截至 {row['financial_date']}）",
            f"- 数据状态：{row['data_freshness']}",
            f"- 计算口径：{row['calculation_note']}",
            "- 官方来源：" + " · ".join(f"[来源 {i+1}]({url})" for i, url in enumerate(row["sources"])),
        ]
        if row.get("scenario_model"):
            model = row["scenario_model"]
            lines += ["", f"### {row['ticker']} 五年数值情景（{model['metric']}终值法）", "", "| 情景 | 主观权重 | 收入CAGR | 年稀释 | 终值利润率 | 终值倍数 | 五年收入 | 每股年化回报敏感度 |", "|---|---:|---:|---:|---:|---:|---:|---:|"]
            for name in ("bear", "base", "bull"):
                case = model["cases"][name]
                margin = f"{case['terminal_margin']:.1%}" if case.get("terminal_margin") is not None else "n/a"
                lines.append(f"| {name} | {case['probability']:.0%} | {case['revenue_cagr']:.1%} | {case['annual_share_dilution']:.1%} | {margin} | {case['terminal_multiple']:.1f}x | ${case['future_revenue_m']:.1f}M | {case['annualized_return']:.1%} |")
            base_case, bear_case = model["cases"]["base"], model["cases"]["bear"]
            lines += ["", f"**默认期望财富口径：{model['expected_wealth_annualized_return']:.1%}。** 先对每个情景的稀释后终值财富取期望，再年化，符合期望财富定义。直接加权三个年化率仅作分布辅助：{model['probability_weighted_case_annualized_return']:.1%}。", "", f"排除性安全边际：基准≥{model['safety_margin_policy']['base_min_return']:.0%}、悲观≥{model['safety_margin_policy']['bear_min_return']:.0%}且输入已核验。当前结果：{'通过' if model['exclusion_test_pass'] else '未通过'}；输入核验：{'是' if model['inputs_verified'] else '否'}。基准达到门槛所需价格 ${base_case['price_for_policy_return']:.2f}（相对当前 {base_case['price_change_to_policy_return']:.1%}）；悲观达到门槛所需价格 ${bear_case['price_for_policy_return']:.2f}（相对当前 {bear_case['price_change_to_policy_return']:.1%}）。", "", f"权重依据：{model['probability_basis']} 净负债假设：{model['net_debt_assumption_note']} {model['limitation']}"]
    Path(args.markdown_output).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json_output)
    print(args.markdown_output)


if __name__ == "__main__":
    main()
