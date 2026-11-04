from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ThemeConfig:
    name: str
    label: str
    keywords: tuple[str, ...]
    counter_keywords: tuple[str, ...]
    trusted_sources: tuple[str, ...]
    excluded_sources: tuple[str, ...] = ()


@dataclass(frozen=True)
class Settings:
    themes: tuple[ThemeConfig, ...]
    alert_score: int = 60
    deep_research_score: int = 70
    lookback_days: int = 7


def load_settings(path: str | Path) -> Settings:
    data: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    themes = tuple(
        ThemeConfig(
            name=item["name"],
            label=item.get("label", item["name"]),
            keywords=tuple(term.lower() for term in item.get("keywords", [])),
            counter_keywords=tuple(term.lower() for term in item.get("counter_keywords", [])),
            trusted_sources=tuple(source.lower() for source in item.get("trusted_sources", [])),
            excluded_sources=tuple(source.lower() for source in item.get("excluded_sources", [])),
        )
        for item in data["themes"]
    )
    return Settings(
        themes=themes,
        alert_score=int(data.get("alert_score", 60)),
        deep_research_score=int(data.get("deep_research_score", 70)),
        lookback_days=int(data.get("lookback_days", 7)),
    )
