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
    challengers = [row for row in companies if row["stage"] == "deep-dive-next"]
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
        f"覆盖 {len(payload['companies'])} 家上市公司；深度审查 {len(payload['deepReviewed'])} 家；下一批挑战者 {len(payload['challengers'])} 家。", "",
        "## 筛选结果", "",
        "| 股票 | 公司 | 细分定位 | 阶段 | 研究优先分 | 为什么进入/暂缓 |",
        "|---|---|---|---|---:|---|",
    ]
    for row in payload["companies"]:
        lines.append(f"| [{row['ticker']}]({row['source']}) | {row['company']} | {row['segment']} | {row['stage']} | {row['screenScore']:.1f} | {row['screen_reason']} |")
    lines += ["", "## 当前结论边界", ""]
    leaders = ", ".join(row["ticker"] for row in payload["deepReviewed"])
    challengers = ", ".join(row["ticker"] for row in payload["challengers"])
    lines.append(f"- `{leaders}` 是已完成深度审查的当前候选，不等于全行业最终赢家。")
    lines.append(f"- `{challengers}` 得分足以挑战当前排序，必须完成同等级尽调后才能下最终结论。")
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
