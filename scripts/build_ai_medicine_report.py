from __future__ import annotations

import argparse
import json
from pathlib import Path


def latest_report(directory: Path) -> dict:
    files = sorted(directory.glob("run-*.json"), key=lambda path: path.stat().st_mtime)
    return json.loads(files[-1].read_text(encoding="utf-8")) if files else {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the auditable AI Medicine 5–10 year report")
    parser.add_argument("--theses", required=True)
    parser.add_argument("--market-dir", required=True)
    parser.add_argument("--serenity", required=True)
    parser.add_argument("--serenity-gate")
    parser.add_argument("--peer-screen")
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
    peer_screen = json.loads(Path(args.peer_screen).read_text(encoding="utf-8")) if args.peer_screen and Path(args.peer_screen).is_file() else {"companies": [], "challengers": []}
    market_rows = {row["signal"]["ticker"]: row for row in market.get("results", [])}
    forecasts = market.get("kronos", {})
    candidates = sorted(theses["candidates"], key=lambda row: row["rank"])

    lines = [
        "# AI Medicine：未来 5–10 年潜力公司研究",
        "",
        "> 研究目标：识别值得长期跟踪的公司，不构成买入建议。长期排序来自商业壁垒与验证证据；Kronos 仅提供未来 5 日市场背景，不用于预测 10 年收益。",
        "",
        "## 结论摘要",
        "",
        "| 排名 | 公司 | 定位 | Serenity | 当前价格 | Kronos 5日 |",
        "| ---: | --- | --- | --- | ---: | ---: |",
    ]
    for item in candidates:
        ticker = item["ticker"]
        row = market_rows.get(ticker, {})
        signal = row.get("signal", {})
        forecast = float(forecasts.get(ticker, {}).get("forecast_return", 0.0))
        lines.append(
            f"| {item['rank']} | {ticker} · {item['company']} | {item['classification']} | "
            f"{serenity.get(ticker, {}).get('serenity_decision', 'unreviewed')} | "
            f"{signal.get('price', 'n/a')} | {forecast:+.2%} |"
        )
    lines += [
        "",
        "**当前 12 家候选池、8 家深度审查后的研究优先级：TEM > SDGR > CERT > NTRA > RXRX > SOPH > GH > ABCL。** 这是长期研究优先级，不是预期收益率；Serenity 通过只表示证据链达到继续估值和跟踪的标准，重大新事件会临时改为 revalidate。",
        "",
        "## 为什么当前是 TEM，而不是其他决赛公司",
        "",
        "- **相对 SDGR：** TEM 更直接连接临床数据、诊断和医生工作流；SDGR 的软件卡位成熟，但云化利润率和药物项目波动仍需重新验证。",
        "- **相对 RXRX：** TEM 已有更直接的商业收入和医疗系统工作流验证；RXRX 的平台弹性更大，但临床成功、现金消耗和稀释风险更高。",
        "- **相对 ABCL：** TEM 的 AI 与数据飞轮更容易从披露中识别；ABCL 的抗体平台价值存在，但 AI 差异化和伙伴经济转化仍不充分。",
        "- **相对 CERT：** CERT 的工作流嵌入和利润质量更成熟，但整体增长较慢，AI 是否带来新的定价权尚未验证。",
        "- **相对 NTRA：** NTRA 的诊断增长和商业验证更强，但当前市值与估值更高，且长期价值并非主要来自 AI 卡位本身。",
        "- **相对 SOPH：** SOPH 的 AI 精准医疗纯度很高，但规模、现金安全边际与盈利路径明显弱于 TEM。",
        "- **相对 GH：** GH 的肿瘤检测与早筛增长强劲，但自由现金流仍为负，筛查商业化和报销风险更高。",
        "- **最强反方观点：** 如果 Tempus 的数据不能形成独占优势、诊断量无法转化为利润和现金流，或者估值已经提前反映多年增长，TEM 的第一名应被撤销。",
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
        "**结论边界：** 当前筛选池仍不是全球所有上市与私营 AI Medicine 公司；ILMN、DHR、MRNA、TWST 作为相邻比较组保留。排名必须随财报、监管、临床和估值变化自动重审。",
        "",
        "## 公司研究",
        "",
    ]
    for item in candidates:
        ticker = item["ticker"]
        lines += [
            f"### {item['rank']}. {ticker} — {item['company']}",
            "",
            f"- **长期逻辑：** {item['thesis']}",
            f"- **为什么现在关注：** {item['why_now']}",
            f"- **Serenity 作用：** {item['serenity_angle']}",
            f"- **关键风险：** {item['risks']}",
            f"- **未来验证：** {item['validation_gates']}",
            f"- **Serenity 结论：** {serenity.get(ticker, {}).get('reason', '尚未评估')}",
            "- **官方来源：** " + " · ".join(f"[来源 {index + 1}]({url})" for index, url in enumerate(item["sources"])),
            "",
        ]
    lines += [
        "## 系统如何得到结论",
        "",
        "1. changedetection.io / RSS 新闻源持续发现 AI 医疗、精准医疗、计算生物学与临床 AI 的变化。",
        "2. 主题映射把行业新闻连接到真正有业务暴露的上市公司，不要求新闻标题直接出现公司名。",
        "3. Serenity 方法检查数据或供应链卡位、客户依赖、纯业务暴露、多节点控制、反方论点和财报验证。",
        "4. OpenBB 读取真实市场历史数据；Kronos 产生 5 日预测，只用于判断短期市场环境是否与长期论点冲突。",
        "5. 系统每天记录信号，并在未来回填 1/5/20/60 日表现，检验流程是否具有样本外价值。",
        "",
        "## 下一步",
        "",
        "- 每日持续更新 AI Medicine 新闻与候选映射。",
        "- 每季度用财报指标重新执行 Serenity 验证门槛。",
        "- 对前三名补充估值、竞争格局、监管与临床里程碑情景分析。",
        "- 累积足够样本前，不宣称新闻或模型具有预测能力。",
        "",
    ]
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
