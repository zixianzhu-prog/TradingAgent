from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True)
class Article:
    source: str
    title: str
    url: str
    content: str
    published_at: str = ""
    discovered_at: str = field(default_factory=utc_now)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ThemeResult:
    name: str
    label: str
    score: int
    status: str
    article_count: int
    source_count: int
    matched_terms: tuple[str, ...]
    evidence: tuple[dict[str, Any], ...]
    counter_terms: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["matched_terms"] = list(self.matched_terms)
        result["counter_terms"] = list(self.counter_terms)
        result["evidence"] = list(self.evidence)
        return result
