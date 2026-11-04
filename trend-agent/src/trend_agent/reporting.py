from __future__ import annotations

import json
from pathlib import Path

from .models import ThemeResult, utc_now


def write_reports(results: list[ThemeResult], output_dir: str | Path) -> tuple[Path, Path]:
    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)
    json_path = target / "latest-trends.json"
    markdown_path = target / "latest-trends.md"
    json_path.write_text(
        json.dumps({"generated_at": utc_now(), "themes": [item.as_dict() for item in results]}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = ["# 趋势监控报告", "", f"生成时间：{utc_now()}", ""]
    if not results:
        lines.append("当前没有匹配的趋势。")
    for result in sorted(results, key=lambda item: item.score, reverse=True):
        lines.extend(
            [
                f"## {result.label}",
                "",
                f"- 趋势评分：{result.score}/100",
                f"- 状态：{result.status}",
                f"- 匹配内容：{result.article_count} 条",
                f"- 独立来源：{result.source_count} 个",
                f"- 关键词：{', '.join(result.matched_terms) or '无'}",
                f"- 反向信号：{', '.join(result.counter_terms) or '无'}",
                "",
                "### 证据",
                "",
            ]
        )
        for evidence in result.evidence:
            title = evidence["title"]
            url = evidence["url"]
            source = evidence["source"]
            lines.append(f"- [{title}]({url})，来源：{source}" if url else f"- {title}，来源：{source}")
        lines.extend(
            [
                "",
                "> 该评分用于决定是否启动进一步研究，不构成投资建议。",
                "",
            ]
        )
    markdown_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return json_path, markdown_path
