from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def score_company(company: dict, weights: dict) -> float:
    return round(sum(float(company["scores"].get(key, 0)) / 5 * weight for key, weight in weights.items()), 1)


def build(universe: dict) -> dict:
    weights = universe["criteria"]
    companies = []
    for company in universe["companies"]:
        companies.append({**company, "screenScore": score_company(company, weights)})
    companies.sort(key=lambda row: row["screenScore"], reverse=True)
    deep_reviewed = [row for row in companies if row["stage"] == "deep-reviewed"]
    challengers = [row for row in companies if row["stage"] in {"deep-dive-next", "deep-review-active"}]
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "title": universe["title"],
        "scopeNote": universe["scope_note"],
        "criteria": weights,
        "companies": companies,
        "deepReviewed": deep_reviewed,
        "challengers": challengers,
        "claimBoundary": "Scores prioritize research using disclosed evidence; they are not expected returns, price targets, or probabilities of success.",
        "sectorWinnerStatus": "provisional-until-challengers-reviewed" if challengers else "reviewed-finalists-complete",
    }


def render(payload: dict) -> str:
    lines = [
        "# AI Medicine 候选池与横向筛选", "",
        "> 这是一套研究优先级筛选，不是收益率预测。只有完成同等级官方来源、财报、临床与反方审计后，才允许比较长期潜力。", "",
        "公式：AI Medicine相关性20% + 专有数据/模型20% + 工作流锁定15% + 商业验证15% + 多节点控制10% + 财务韧性10% + 原始证据覆盖10%。各项先按0–5评分，再换算为加权总分。", "",
        f"覆盖 {len(payload['companies'])} 家上市公司；已完成同口径深度审查 {len(payload['deepReviewed'])} 家；尚待深审挑战者 {len(payload['challengers'])} 家。深审完成不等于通过投资门槛。", "",
        "## 筛选结果", "",
        "| 股票 | 公司 | 细分定位 | 阶段 | 相关性 | 数据/模型 | 锁定 | 商业 | 多节点 | 财务 | 证据 | 总分 | 为什么进入/暂缓 |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["companies"]:
        s = row["scores"]
        lines.append(f"| [{row['ticker']}]({row['source']}) | {row['company']} | {row['segment']} | {row['stage']} | {s['ai_medicine_relevance']}/5 | {s['proprietary_data_or_models']}/5 | {s['workflow_or_customer_lock_in']}/5 | {s['commercial_validation']}/5 | {s['multi_node_control']}/5 | {s['financial_resilience']}/5 | {s['primary_evidence_coverage']}/5 | {row['screenScore']:.1f} | {row['screen_reason']} |")
    lines += ["", "## 当前结论边界", ""]
    leaders = ", ".join(row["ticker"] for row in payload["deepReviewed"])
    challengers = ", ".join(row["ticker"] for row in payload["challengers"])
    lines.append(f"- `{leaders}` 是已完成同口径深度审查的当前候选，不等于全行业最终赢家，也不等于推荐。")
    if challengers:
        lines.append(f"- `{challengers}` 得分足以挑战当前排序，必须完成同等级尽调后才能下最终结论。")
    else:
        lines.append("- 当前高优先候选已完成同口径审查；下一步是补齐缺失门槛，而不是强行选出赢家。")
    lines.append("- 横向分数只决定先研究谁；最终排序还必须通过估值、财报、临床/监管和可证伪事件门槛。")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a reproducible AI Medicine peer screen")
    parser.add_argument("--universe", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()
    payload = build(json.loads(Path(args.universe).read_text(encoding="utf-8")))
    json_path, markdown_path = Path(args.json_output), Path(args.markdown_output)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    markdown_path.write_text(render(payload), encoding="utf-8")
    print(json.dumps({"screened": len(payload["companies"]), "deepReviewed": len(payload["deepReviewed"]), "challengers": len(payload["challengers"])}, ensure_ascii=False))


if __name__ == "__main__":
    main()
