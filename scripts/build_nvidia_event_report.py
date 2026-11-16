from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def latest_market() -> tuple[dict, Path | None]:
    paths = sorted((ROOT / "outputs/nvidia-market").glob("run-*.json"), key=lambda p: p.stat().st_mtime)
    return (load(paths[-1], {}), paths[-1]) if paths else ({}, None)


def main() -> None:
    trends = load(ROOT / "trend-agent/reports/daily/trends/latest-trends.json", {"themes": []})
    links = load(ROOT / "trend-agent/reports/daily/theme-stocks/theme-stock-links.json", {"companies": []})
    events = load(ROOT / "state/event-revalidation.json", {"revalidationTasks": [], "scheduledEvents": []})
    theme = next((row for row in trends.get("themes", []) if row.get("name") == "nvidia_company_news"), {})
    nvda_link = next((row for row in links.get("companies", []) if row.get("ticker") == "NVDA"), {})
    market, market_path = latest_market()
    signal = next((row.get("signal", {}) for row in market.get("results", []) if row.get("signal", {}).get("ticker") == "NVDA"), {})
    forecast = market.get("kronos", {}).get("NVDA", {}).get("forecast_return")
    nvda_tasks = [row for row in events.get("revalidationTasks", []) if row.get("ticker") == "NVDA"]
    evidence = theme.get("evidence", [])
    lines = [
        "# NVIDIA 公司重大新闻与管理层事件影响", "",
        f"生成时间：{datetime.now(timezone.utc).isoformat()}", "",
        "> 本报告区分公司/监管正式披露与媒体报道。事件影响是情景分析；价格方向由独立市场模型验证，不代表因果证明或投资指令。", "",
        "## 当前研究信号", "",
        f"- NVIDIA 主题分：{theme.get('score', '—')}/100；主题传导分：{nvda_link.get('transmission_score', '—')}/100。",
        f"- NVDA 最新本地市场快照：${float(signal['price']):.2f}；技术方向：{signal.get('direction', '—')}；Kronos 五日预测：{float(forecast):+.2%}" if forecast is not None and signal.get("price") is not None else "- 尚无有效的 NVDA Kronos 预测。",
        f"- Serenity 事件重审任务：{len(nvda_tasks)} 项；受影响门槛：{', '.join(sorted({gate for task in nvda_tasks for gate in task.get('affectedGates', [])})) or '无'}。", "",
        "## 已确认事实", "",
        "- NVIDIA 于 2026-11-12 公告，黄仁勋辞去总裁、CEO 和董事职务，即时生效；CFO Colette Kress 暂任 CEO，董事会开始寻找正式继任者。",
        "- SEC 8-K 于 2026-11-12 披露董事会接受上述辞职，并任命 Colette Kress 为 interim CEO。",
        "- NVIDIA 董事会此前公告将就媒体所称的 foreign intelligence effort 开展独立调查；公司公告称目前没有理由相信国家安全或 NVIDIA 机密已遭泄露，但调查仍在进行。",
        "- 黄仁勋公开向员工和家人道歉，承认对妻子不忠；其公开道歉没有点名对象，也没有说明辞职原因。", "",
        "来源：",
        "- [NVIDIA CEO 交接公告](https://investor.nvidia.com/news/press-release-details/2026/NVIDIA-Announces-CEO-Transition/default.aspx)",
        "- [SEC Form 8-K](https://www.sec.gov/Archives/edgar/data/1045810/000104581026000082/nvda-20261111.htm)",
        "- [NVIDIA 董事会独立调查声明](https://nvidianews.nvidia.com/news/statement-from-nvidia-board-of-directors)",
        "- [NVIDIA 员工信件](https://nvidianews.nvidia.com/news/a-message-to-our-company)",
        "- [Associated Press：CEO 辞职及报道与调查进展](https://apnews.com/article/nvidia-jensen-huang-resigns-ceo-affairs-314714d463cf578cbb0dbd49de903107)", "",
        "## 需要分级处理的报道", "",
        "媒体报道涉及一段与 Megaspeed 前高管的关系、可能的外国情报关联，以及另一段涉及 NVIDIA 员工的关系。NVIDIA 官方确认的是调查启动和 CEO 交接；间谍指控、是否发生信息泄露、第二段关系的具体情况，以及这些报道是否导致辞职，均不能从公司交接公告直接推出。相关结论需要后续公司/监管披露或多家可靠媒体独立交叉验证。", "",
        "## 对业务与股票的可能影响", "",
        "1. **管理层连续性**：黄仁勋长期主导产品路线、客户关系和公司战略；临时 CEO 同时保留 CFO 职责，正式继任者尚未确定，增加执行和沟通不确定性。",
        "2. **客户与合作承诺**：公司表示产品路线和客户承诺预期继续，但这属于管理层表态；后续财报、订单、客户支出与交付情况才是验证。",
        "3. **治理与声誉**：独立调查和报道可能影响员工、客户、合作伙伴及投资者信心；实际收入或订单影响目前未被上述公告量化。",
        "4. **政策与地缘风险**：若调查或国会审查带来更严格的芯片出口措施，可能影响中国市场销售、库存与竞争格局；政策变化尚不能视为必然。",
        "5. **市场反应**：美联社报道 NVDA 周四收盘下跌超过 4%，盘中跌幅一度更大；这是事件发生后的同期表现，不能据此认定跌幅完全由此事件造成。",
        "6. **近期验证点**：NVIDIA 已预告 2026-11-17 发布 FY2027 Q3 业绩。重点检查管理层对需求、客户承诺、出口限制、库存及正式 CEO 搜寻的更新。", "",
        "## Serenity 结论", "",
        "本事件使 `management_governance`、`counter_thesis` 和 `earnings_validation` 进入重新核验。当前保持 watch/revalidate：公司运营连续性仍是待验证命题，管理层交接和独立调查增加风险，但现有材料不足以量化长期盈利影响，也不足以把短期股价变动归因于单一事件。", "",
        "## 自动发现的相关报道", "",
    ]
    for item in evidence[:10]:
        title = item.get("title", "Untitled").replace("[", "(").replace("]", ")")
        url = item.get("url", "")
        lines.append(f"- [{title}]({url}) — {item.get('source', '来源未知')} · {item.get('published_at', '时间未知')}")
    if not evidence:
        lines.append("- 本轮暂无主题证据。")
    lines += ["", f"市场快照文件：`{market_path.relative_to(ROOT) if market_path else '暂无'}`", ""]
    target = ROOT / "outputs/nvidia-company-news-impact.md"
    target.write_text("\n".join(lines), encoding="utf-8")
    print(target)


if __name__ == "__main__":
    main()
