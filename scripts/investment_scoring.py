from __future__ import annotations

from typing import Any


def calculate_scores(signal: dict[str, Any], forecast_return: float, news: dict[str, Any]) -> dict[str, int]:
    technical = round(float(signal["score"]) * 100)
    kronos = round(max(0, min(100, 50 + forecast_return * 500)))
    news_score = int(news.get("news_score", 0))
    combined = round(news_score * 0.45 + technical * 0.35 + kronos * 0.20)
    return {"news": news_score, "technical": technical, "kronos": kronos, "combined": combined}
