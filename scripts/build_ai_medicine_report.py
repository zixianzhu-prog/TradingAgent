from __future__ import annotations

import argparse
import json
from pathlib import Path


def latest_report(directory: Path) -> dict:
    files = sorted(directory.glob("run-*.json"), key=lambda path: path.stat().st_mtime)
    return json.loads(files[-1].read_text(encoding="utf-8")) if files else {}


def research_tier(serenity_row: dict, financial: dict) -> str:
    decision = serenity_row.get("serenity_decision", "unreviewed")
    completeness = serenity_row.get("completeness_score", 0)
    if decision == "reject":
        return "暂缓"
    if decision == "research-ready" and completeness >= 70 and financial:
        return "优先关注"
    if decision == "watch" and completeness >= 50 and financial:
        return "深度研究"
    return "观察 / 待补证据"


def action_bucket(ticker: str, peer: dict, serenity_row: dict) -> str:
    if serenity_row.get("serenity_decision") == "revalidate":
        return "事件重验证"
    if serenity_row.get("completeness_score", 0) >= 50 and serenity_row.get("evidence_quality_score", 0) >= 50 and peer.get("screenScore", 0) >= 75:
        return "优先深挖"
    if peer.get("screenScore", 0) >= 90:
        return "高潜力待验证"
    return "观察"


GATE_LABELS = {
    "supply_chain_map": "产业链",
    "customer_dependency": "客户依赖",
    "earnings_validation": "财报",
    "chokepoint_evidence": "瓶颈",
    "pure_play": "纯业务暴露",
    "multi_node_control": "多节点控制",
    "counter_thesis": "反方论点",
    "management_governance": "治理",
}


def evidence_gaps(row: dict) -> str:
    states = row.get("gate_states", {})
    gaps = [f"{GATE_LABELS.get(name, name)}:{status}" for name, status in states.items() if status != "pass"]
    return "；".join(gaps) or "当前门槛均通过"


def completeness_display(row: dict) -> str:
    if row.get("serenity_decision") == "revalidate":
        return "暂停评分（事件重验证）"
    return f"{row.get('completeness_score', 0)}/100"


EXPOSURE_LABELS = {
    "RDNT": "影像中心运营商 + AI期权（非纯AI）",
    "SOPH": "直接精准医疗数据平台",
    "TEM": "直接精准医疗数据平台",
    "ISRG": "高质量手术机器人平台，AI为次要增量",
    "GEHC": "大型影像设备平台，AI为产品功能层",
    "IQV": "临床数据/CRO平台，AI为效率层",
    "NVDA": "算力基准，非AI医疗纯业务",
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the auditable AI Medicine 5–10 year report")
    parser.add_argument("--theses", required=True)
    parser.add_argument("--market-dir", required=True)
    parser.add_argument("--serenity", required=True)
    parser.add_argument("--serenity-gate")
    parser.add_argument("--peer-screen")
    parser.add_argument("--fda-devices")
    parser.add_argument("--financial-scenarios")
    parser.add_argument("--independent-evidence")
    parser.add_argument("--evidence-coverage-plan")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    theses = json.loads(Path(args.theses).read_text(encoding="utf-8"))
    market = latest_report(Path(args.market_dir))
    serenity_payload = json.loads(Path(args.serenity).read_text(encoding="utf-8"))
    serenity = {row["ticker"]: row for row in serenity_payload.get("companies", [])}
    if args.serenity_gate and Path(args.serenity_gate).is_file():
        gate_payload = json.loads(Path(args.serenity_gate).read_text(encoding="utf-8"))
        for row in gate_payload.get("companies", []):
            serenity.setdefault(row["ticker"], {})["serenity_decision"] = row["decision"]
            serenity[row["ticker"]]["completeness_score"] = row["completenessScore"]
            serenity[row["ticker"]]["evidence_quality_score"] = row.get("evidenceQualityScore", 0)
            serenity[row["ticker"]]["substantiated_score"] = row.get("substantiatedScore", 0)
            serenity[row["ticker"]]["gate_states"] = row["gateStates"]
    peer_screen = json.loads(Path(args.peer_screen).read_text(encoding="utf-8")) if args.peer_screen and Path(args.peer_screen).is_file() else {"companies": [], "challengers": []}
    fda_devices = json.loads(Path(args.fda_devices).read_text(encoding="utf-8")) if args.fda_devices and Path(args.fda_devices).is_file() else {"companyCoverage": [], "summary": {}}
    financial_payload = json.loads(Path(args.financial_scenarios).read_text(encoding="utf-8")) if args.financial_scenarios and Path(args.financial_scenarios).is_file() else {"companies": []}
    financials = {row["ticker"]: row for row in financial_payload.get("companies", [])}
    independent_payload = json.loads(Path(args.independent_evidence).read_text(encoding="utf-8")) if args.independent_evidence and Path(args.independent_evidence).is_file() else {"companies": []}
    independent = {row["ticker"]: row for row in independent_payload.get("companies", [])}
    coverage_plan = json.loads(Path(args.evidence_coverage_plan).read_text(encoding="utf-8")) if args.evidence_coverage_plan and Path(args.evidence_coverage_plan).is_file() else {"rounds": []}
    market_rows = {row["signal"]["ticker"]: row for row in market.get("results", [])}
    forecasts = market.get("kronos", {})
    candidates = sorted(theses["candidates"], key=lambda row: row["rank"])
    expanded = theses.get("expanded_deep_dives", [])
    priority_by_ticker = {row["ticker"]: row for row in peer_screen.get("companies", [])}
    all_researched = sorted(
        [*candidates, *expanded],
        key=lambda item: priority_by_ticker.get(item["ticker"], {}).get("screenScore", 0),
        reverse=True,
    )
    action_groups = {name: [] for name in ("优先深挖", "高潜力待验证", "观察", "事件重验证")}
    for item in all_researched:
        ticker = item["ticker"]
        action_groups[action_bucket(ticker, priority_by_ticker.get(ticker, {}), serenity.get(ticker, {}))].append(ticker)

    lines = [
        "# AI Medicine：未来 5–10 年潜力公司研究",
        "",
        "> 研究目标：识别值得长期跟踪的公司，不构成买入建议。系统不再并列展示“潜力第一”和“证据第一”，而是先用硬门槛决定行动层级，再在同一层级比较研究优先级。Kronos 仅提供未来 5 日市场背景，不用于预测 10 年收益。",
        "",
        "## 当前唯一行动输出",
        "",
        "**先看口径：这些层级表示下一步研究动作，不是公司质量排名。** Serenity 的纯业务、瓶颈和证据门槛适合寻找主题性卡位，但会低估 ISRG 这类业务优秀、AI 暴露较低的公司，也会偏向当前资料抓取更完整的公司。",
        "",
        "- **RDNT 定位：** 影像中心运营商附带 AI/软件期权。Q3 2026 Digital Health 收入 $32.9M / 总收入 $638.3M，约 **5.2%**；再按公司披露的63%外部客户占比估算，外部 Digital Health 约 $20.7M、仅占总收入 **3.2%**。后者是组合估算，不是公司单独报告的收入行。",
        "- **SOPH 定位：** AI/数据业务更直接，但规模、亏损、融资和稀释风险显著高于成熟平台公司。",
        "- **ISRG 定位：** 业务质量和客户工作流证据强，但 AI 不是当前主要收入论点；“观察”不等于公司质量差。",
        "",
        f"- **优先深挖：** {', '.join(action_groups['优先深挖']) or '暂无'}。含义是证据已足够支持继续投入研究时间，不是买入通过。",
        f"- **高潜力待验证：** {', '.join(action_groups['高潜力待验证']) or '暂无'}。潜力筛选高，但客户依赖、瓶颈或估值门槛尚未完成。",
        f"- **事件重验证：** {', '.join(action_groups['事件重验证']) or '暂无'}。重大治理、监管、临床或财务事件未解决前不得升级。",
        f"- **其余观察：** {', '.join(action_groups['观察']) or '暂无'}。",
        "",
        f"**当前没有正式投资通过项。** 本期优先深挖：{'、'.join(action_groups['优先深挖']) or '暂无'}；高潜力待验证：{'、'.join(action_groups['高潜力待验证']) or '暂无'}。这里没有另一套主排名。",
        "",
        "## 评分公式与结论边界",
        "",
        "1. **研究优先分（0–100）** = AI Medicine相关性20% + 专有数据/模型20% + 工作流锁定15% + 商业验证15% + 多节点控制10% + 财务韧性10% + 原始证据覆盖10%。它只决定先研究谁，不能代表公司质量或收益概率。",
        "2. **Serenity完整度（0–100）**：供应链图、客户依赖、财报三项硬门槛各15分；瓶颈、纯业务、多节点、治理各10分；反方论点15分。partial只得一半，重大事件会使相关项失效。",
        "3. **证据质量（0–100）**：按原始来源、反证、可证伪条件和缺口计算。完整度与证据质量相关，因此**有据分只用于诊断证据成熟度，不参与潜力排名或投资升级**。",
        "4. **行动层级是门槛制**：优先深挖要求研究优先分≥75、完整度≥50、证据质量≥50且无revalidate；它会受到资料抓取覆盖偏差影响。正式优先关注还需要满足下面全部升级条件。",
        "",
        "### 升级为‘优先关注’的全部条件",
        "",
        "- 当前财报原始数据通过，并至少连续两个报告期验证核心业务指标。",
        "- 供应链/工作流、客户依赖和瓶颈证据均达到 pass，不能只靠公司自述或FDA授权。",
        "- 反方论点包含有来源的反证和明确证伪条件。",
        "- 没有未解决的治理、监管、临床、融资或披露矛盾事件。",
        "- 完整度与证据质量均至少70；关键数字标注来源、报告期和价格日期。",
        "- 使用与商业模式匹配的估值指标；研究政策暂定安全边际为**基准情景每股年化回报≥12%、悲观情景≥-10%**，且净负债和稀释已由原始材料核验。它只作**排除性检验**：不通过则不能升级，通过也不能证明公司值得投资，因为输入仍是人工设定。阈值是研究规则，不是市场事实。",
        "- 不得用P/S跨行业直接比较；最新季度年化口径不是TTM，季节性公司只能作为粗略快照。",
        "",
        "## 候选池与比较边界",
        "",
        f"系统先筛选 {len(peer_screen.get('companies', []))} 家相关上市公司，再对其中 {len(peer_screen.get('deepReviewed', []))} 家决赛公司执行同等级深度审查。筛选分只决定研究优先级，不代表成功概率或预期回报。",
        "",
        "| 股票 | 阶段 | 研究优先分 | 结论 |",
        "|---|---|---:|---|",
    ]
    for peer in peer_screen.get("companies", []):
        lines.append(f"| [{peer['ticker']}]({peer['source']}) | {peer['stage']} | {peer['screenScore']:.1f} | {peer['screen_reason']} |")
    lines += [
        "",
        "**结论边界：** 当前筛选池仍不是全球所有上市与私营 AI Medicine 公司；GEHC、RDNT、ISRG、IQV、NVDA 已进入同等级跨细分深审，ILMN、DHR、MRNA、TWST 作为相邻比较组保留。排名必须随财报、监管、临床和估值变化自动重审。",
        "",
        "## FDA AI 医疗设备官方验证",
        "",
        f"当前 FDA 官方清单包含 {fda_devices.get('summary', {}).get('totalDevices', 0)} 项设备记录。授权记录只证明具体产品完成相应监管路径，不证明收入、客户依赖、竞争壁垒或股票回报。",
        "",
        "| 股票 | FDA 申报方匹配 | 在本系统中的角色 |",
        "|---|---:|---|",
    ]
    for row in fda_devices.get("companyCoverage", []):
        lines.append(f"| {row['ticker']} | {row['matchedDevices']} | {row['interpretation']} |")
    lines += [
        "",
        "## 全覆盖研究分级（13 家）",
        "",
        "| 股票 | AI医疗暴露类型 | 研究优先分 | 完整度 | 证据质量 | 具体未完成门槛 | 价格/日期 | P/S及口径 | EV/EBITDA | OCF收益率 | 行动层级 |",
        "|---|---|---:|---:|---:|---|---|---|---:|---:|---|",
    ]
    for item in all_researched:
        ticker = item["ticker"]
        peer = priority_by_ticker.get(ticker, {})
        financial = financials.get(ticker, {})
        serenity_row = serenity.get(ticker, {})
        price = financial.get("price")
        price_text = f"${price:.2f} / {financial.get('price_date')}" if isinstance(price, (int, float)) else "待核验"
        ps = financial.get("price_to_sales_approx")
        ev_ebitda = financial.get("ev_to_ebitda_approx")
        ocf_yield = financial.get("ocf_yield_approx")
        lines.append(
            f"| {ticker} | {EXPOSURE_LABELS.get(ticker, item['classification'])} | {peer.get('screenScore', 0):.1f} | "
            f"{completeness_display(serenity_row)} | {serenity_row.get('evidence_quality_score', 0)}/100 | "
            f"{evidence_gaps(serenity_row)} | {price_text} | "
            f"{f'{ps:.1f}x' if isinstance(ps, (int, float)) else '不适用'} / {financial.get('revenue_basis_type', '待核验')} | "
            f"{f'{ev_ebitda:.1f}x' if isinstance(ev_ebitda, (int, float)) else ('亏损，不适用' if financial.get('adjusted_ebitda_m') is not None and financial.get('adjusted_ebitda_m') <= 0 else '待核验')} | "
            f"{f'{ocf_yield:.1%}' if isinstance(ocf_yield, (int, float)) else '待核验/不适用'} | "
            f"{action_bucket(ticker, peer, serenity_row)} |"
        )
    lines += [
        "",
        "**当前没有任何公司达到正式‘推荐/投资通过’。** 这是因为至少一项硬门槛、证据质量、估值或事件重验证尚未完成。",
        "",
        "## 两个证据优先对象 + 一个高潜力对照的五年数值情景",
        "",
        "> 这些是手设权重、增长率、稀释率和终值倍数的排除性敏感度测试，不是模型预测、目标价或证据输出。默认采用标准期望财富口径：先对各情景的稀释后终值财富取期望，再年化；直接平均年化率只作分布辅助。TEM/SOPH使用EV/Sales终值；RDNT使用EV/EBITDA终值，三者不能仅凭回报数字横向比较。",
        "",
    ]
    for ticker in ("RDNT", "SOPH", "TEM"):
        model = financials.get(ticker, {}).get("scenario_model")
        if not model:
            continue
        lines += [f"### {ticker}", "", "| 情景 | 主观权重 | 收入CAGR | 年稀释 | 终值利润率 | 终值倍数 | 每股年化回报敏感度 |", "|---|---:|---:|---:|---:|---:|---:|"]
        for name in ("bear", "base", "bull"):
            case = model["cases"][name]
            margin = f"{case['terminal_margin']:.1%}" if case.get("terminal_margin") is not None else "n/a"
            lines.append(f"| {name} | {case['probability']:.0%} | {case['revenue_cagr']:.1%} | {case['annual_share_dilution']:.1%} | {margin} | {case['terminal_multiple']:.1f}x | {case['annualized_return']:.1%} |")
        base_case, bear_case = model["cases"]["base"], model["cases"]["bear"]
        lines += ["", f"**默认期望财富年化回报：{model['expected_wealth_annualized_return']:.1%}。** 它先对稀释后终值财富取期望，再年化。直接加权三个年化率为 {model['probability_weighted_case_annualized_return']:.1%}，仅作分布辅助。", "", f"安全边际仅作排除性检验：基准≥{model['safety_margin_policy']['base_min_return']:.0%}、悲观≥{model['safety_margin_policy']['bear_min_return']:.0%}且输入已核验。当前：**{'通过' if model['exclusion_test_pass'] else '未通过'}**；输入核验：{'是' if model['inputs_verified'] else '否'}。基准达到门槛所需价格 ${base_case['price_for_policy_return']:.2f}（相对当前 {base_case['price_change_to_policy_return']:.1%}）；悲观达到门槛所需价格 ${bear_case['price_for_policy_return']:.2f}（相对当前 {bear_case['price_change_to_policy_return']:.1%}）。", "", f"权重依据：{model['probability_basis']} 净负债假设 ${model['net_debt_assumption_m']:.1f}M。{model['net_debt_assumption_note']}", ""]
    lines += [
        "## 第三方/客户交叉验证与公平覆盖",
        "",
        "> 公司披露、客户/临床研究、独立行业分析和反方材料分开标注。研究发表不等于商业成功；存在公司关联作者时也不标为完全独立。为了避免“先选中者继续积累证据”的自我强化，交叉验证按预设轮次覆盖，不按当前分数挑选；全部13家完成相同证据类别前，比较排名保持 provisional。新增登记不会自动加分，只有下一次逐条引文匹配和反证审查完成后才允许改变门槛。",
        "",
    ]
    for coverage_round in coverage_plan.get("rounds", []):
        lines += [f"- **覆盖轮次 {coverage_round['round']}（{coverage_round['status']}）：** {', '.join(coverage_round['tickers'])}"]
    lines.append("")
    for ticker in ("RDNT", "SOPH", "TEM", "CERT", "NTRA", "GH"):
        record = independent.get(ticker)
        if not record:
            continue
        lines += [f"### {ticker} — {record['ai_exposure_label']}", ""]
        if record.get("ai_revenue_share"):
            share = record["ai_revenue_share"]
            external = f"；外部 Digital Health 估算 ${share['estimated_external_digital_health_revenue_m']:.1f}M，占总收入 **{share['estimated_external_digital_health_share_of_total_pct']:.1f}%**" if share.get("estimated_external_digital_health_revenue_m") is not None else ""
            lines += [f"- **AI收入占比：** {share['period']} Digital Health ${share['digital_health_revenue_m']:.1f}M / 总收入 ${share['total_revenue_m']:.1f}M = **{share['calculated_pct']:.1f}%**{external}。{share['interpretation']}"]
        for evidence in record.get("evidence", []):
            lines += [f"- **{evidence['type']}：** [{evidence['claim']}]({evidence['source']}) 独立性：{evidence['independence']}。限制：{evidence['limitation']}"]
        lines.append("")
    lines += [
        "## NVDA 事件重验证说明",
        "",
        "NVDA 并非因为基本面得分低而被清零，而是硬事件政策把相关证据暂时标为 stale：2026-11-10 董事会公告触发独立调查重审；2026-11-12 CEO 交接公告触发治理与财报重审；Q3 FY2027 财报仍需重新核验。受影响门槛是治理、反方论点、客户依赖和财报验证，因此界面显示**暂停评分（事件重验证）**，不再显示误导性的0/100。事件日期由发布时间、首次发现时间和本地 as-of 三者做机器一致性校验；异常日期进入隔离而不触发结论。研究优先分也已按“医疗收入不单独披露、非纯AI医疗”下调，NVDA 只作为基础设施基准。",
        "",
    ]
    lines += [
        "## 新增跨细分深审",
        "",
    ]
    for item in expanded:
        ticker = item["ticker"]
        financial = financials.get(ticker, {})
        ps = financial.get("price_to_sales_approx")
        ps_text = f"{ps:.1f}x" if isinstance(ps, (int, float)) else "n/a"
        lines += [
            f"### {ticker} — {item['company']}",
            "",
            f"- **当前行动层级：** {action_bucket(ticker, priority_by_ticker.get(ticker, {}), serenity.get(ticker, {}))}；研究优先分 {priority_by_ticker.get(ticker, {}).get('screenScore', 0):.1f}，完整度 {completeness_display(serenity.get(ticker, {}))}，证据质量 {serenity.get(ticker, {}).get('evidence_quality_score', 0)}/100，有据分 {serenity.get(ticker, {}).get('substantiated_score', 0)}/100。",
            f"- **长期逻辑：** {item['thesis']}",
            f"- **为什么现在关注：** {item['why_now']}",
            f"- **Serenity作用：** {item['serenity_angle']}",
            f"- **竞争对手：** {', '.join(item.get('competitors', []))}",
            f"- **估值快照：** 价格 ${financial.get('price', 0):.2f}（{financial.get('price_date', '待核验')}）；估算市值 ${financial.get('market_cap_m', 0)/1000:.2f}B；近似 P/S {ps_text}。",
            f"- **乐观情景：** {financial.get('bull_case', '待补充')}",
            f"- **基准情景：** {financial.get('base_case', '待补充')}",
            f"- **悲观情景：** {financial.get('bear_case', item['bear_case'])}",
            f"- **下一催化剂/验证：** {financial.get('next_validation_event', item['validation_gates'])}",
            f"- **关键风险：** {item['risks']}",
            f"- **财务数据期：** {financial.get('financial_period', '待核验')}（截至 {financial.get('financial_date', '待核验')}）。",
            "- **原始来源：** " + " · ".join(f"[来源 {i+1}]({url})" for i, url in enumerate(item.get("sources", []))),
            "",
        ]
    lines += [
        "",
        "## 公司研究档案：原首批八家（不是当前排名）",
        "",
    ]
    for item in candidates:
        ticker = item["ticker"]
        lines += [
            f"### {ticker} — {item['company']}",
            "",
            f"- **长期逻辑：** {item['thesis']}",
            f"- **为什么现在关注：** {item['why_now']}",
            f"- **Serenity 作用：** {item['serenity_angle']}",
            f"- **关键风险：** {item['risks']}",
            f"- **未来验证：** {item['validation_gates']}",
            f"- **Serenity 结论：** {serenity.get(ticker, {}).get('reason', '尚未评估')}",
            f"- **证据完整度：** {serenity.get(ticker, {}).get('completeness_score', 0)}/100；当前门槛为 {serenity.get(ticker, {}).get('serenity_decision', 'unreviewed')}。",
            "- **官方来源：** " + " · ".join(f"[来源 {index + 1}]({url})" for index, url in enumerate(item["sources"])),
            "",
        ]
    lines += [
        "## 系统如何得到结论",
        "",
        "1. RSS、公司投资者关系页和官方事件源持续发现 AI 医疗、精准医疗、计算生物学与临床 AI 的变化；changedetection.io 保留为可选网页变化监控方案。",
        "2. 主题映射把行业新闻连接到真正有业务暴露的上市公司，不要求新闻标题直接出现公司名。",
        "3. Codex 订阅自动任务读取证据包，并按 Serenity 方法检查数据或供应链卡位、客户依赖、纯业务暴露、多节点控制、反方论点和财报验证。",
        "4. OpenBB 读取真实市场历史数据；Kronos 产生 5 日预测，只用于判断短期市场环境是否与长期论点冲突。",
        "5. 系统每天记录信号，并在未来回填 1/5/20/60 日表现，检验流程是否具有样本外价值。",
        "",
        "## 下一步",
        "",
        "- 每日持续更新 AI Medicine 新闻与候选映射。",
        "- 每季度用财报指标重新执行 Serenity 验证门槛。",
        "- 为尚无可比数值情景的公司补充与其商业模式匹配的估值模型；不得用统一P/S强行排序。",
        "- 补充第三方行业、竞争对手和客户证据，把当前公司自述与SEC/FDA验证扩展为多源交叉验证。",
        "- 完成剩余7家公司的同口径交叉验证；在13家覆盖齐全前不把证据质量差异解释成公司质量差异。",
        "- 执行预先登记的盲测与SPY/XLV/XBI、随机和动量基准回测；样本不足时只报告进度。",
        "- 累积足够样本前，不宣称新闻或模型具有预测能力。",
        "",
    ]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
