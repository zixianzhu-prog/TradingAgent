from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import utc_now


def build_theme_stock_report(trends_path: str, mapping_path: str, output_dir: str) -> dict[str, Any]:
    trends = json.loads(Path(trends_path).read_text(encoding="utf-8"))
    mappings = json.loads(Path(mapping_path).read_text(encoding="utf-8")).get("themes", {})
    rows: list[dict[str, Any]] = []
    evidence_multipliers = {"confirmed": 1.0, "partial": 0.65, "hypothesis": 0.35}
    for theme in trends.get("themes", []):
        for company in mappings.get(theme["name"], []):
            multiplier = evidence_multipliers.get(company.get("evidence_status", "hypothesis"), 0.35)
            pure_play_multiplier = 1.0 if company.get("pure_play") else 0.85
            transmission = round(theme["score"] * float(company["exposure_strength"]) * multiplier * pure_play_multiplier)
            decision = "deep-research" if theme["score"] >= 70 and transmission >= 60 else "watch" if transmission >= 35 else "weak-link"
            rows.append({
                **company,
                "theme": theme["name"],
                "theme_label": theme["label"],
                "theme_score": theme["score"],
                "transmission_score": transmission,
                "decision": decision,
            })
    rows.sort(key=lambda item: item["transmission_score"], reverse=True)
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / "theme-stock-links.json"
    markdown_path = target / "theme-stock-links.md"
    payload = {"generated_at": utc_now(), "method": "theme-to-company evidence transmission; not a return probability", "companies": rows}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["# 主题到股票传导报告", "", f"生成时间：{payload['generated_at']}", "",
             "> 新闻不必出现公司名；股票必须有预先验证的产品或供应链关系。", "",
             "| 主题 | 股票 | 业务关联 | 主题分 | 传导分 | Serenity角色 | 结论 |",
             "| --- | --- | --- | ---: | ---: | --- | --- |"]
    for row in rows:
        lines.append(
            f"| {row['theme_label']} | {row['ticker']} | {row['exposure']} | {row['theme_score']} | "
            f"{row['transmission_score']} | {row['serenity_role']} | {row['decision']} |"
        )
    lines.extend(["", "传导分 = 主题分 × 业务暴露强度 × 证据状态 × 纯业务暴露修正。",
                  "它只决定下一步研究顺序，不会直接生成订单。", ""])
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json_report": str(json_path), "markdown_report": str(markdown_path), "companies": len(rows)}
