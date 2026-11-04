from __future__ import annotations

import argparse
import json
from pathlib import Path

from investment_scoring import calculate_scores


def main() -> None:
    parser = argparse.ArgumentParser(description="Build market validation for theme-linked stocks")
    parser.add_argument("--market-dir", required=True)
    parser.add_argument("--theme-report", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    market_files = sorted(Path(args.market_dir).glob("run-*.json"), key=lambda path: path.stat().st_mtime)
    if not market_files:
        raise SystemExit("No theme market report found")
    market_path = market_files[-1]
    market = json.loads(market_path.read_text(encoding="utf-8"))
    theme = json.loads(Path(args.theme_report).read_text(encoding="utf-8"))
    links = {row["ticker"]: row for row in theme.get("companies", [])}
    lines = ["# 宽主题股票市场验证", "", f"市场数据时间：{market['generated_at']}", "",
             "> 主题新闻无需出现公司名；公司必须先通过业务/供应链映射。本报告仅用于研究排序。", "",
             "| 股票 | 主题 | 传导分 | 收盘价 | 技术分 | Kronos 5日 | 综合分 | 结论 |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for item in market["results"]:
        signal = item["signal"]
        ticker = signal["ticker"]
        link = links.get(ticker, {})
        forecast_return = float(market.get("kronos", {}).get(ticker, {}).get("forecast_return", 0.0))
        thematic = {"news_score": int(link.get("transmission_score", 0))}
        scores = calculate_scores(signal, forecast_return, thematic)
        eligible = link.get("theme_score", 0) >= 70 and scores["combined"] >= 70
        decision = "priority-research" if eligible else "watch"
        lines.append(
            f"| {ticker} | {link.get('theme_label', 'unknown')} | {thematic['news_score']} | "
            f"{signal['price']:.2f} | {scores['technical']} | {forecast_return:+.2%} | "
            f"{scores['combined']} | {decision} |"
        )
    lines.extend(["", "综合分 = 主题传导分45% + 技术分35% + Kronos方向分20%。",
                  "主题本身必须达到70，才能升级为优先研究；任何结果都不会自动下单。", "",
                  f"原始市场JSON：`{market_path}`", ""])
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
