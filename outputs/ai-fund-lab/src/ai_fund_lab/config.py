from __future__ import annotations

import json
from dataclasses import dataclass, fields
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    watchlist: tuple[str, ...] = ("NVDA", "AAPL", "MSFT")
    starting_cash: float = 100_000.0
    risk_per_trade: float = 0.01
    max_position_fraction: float = 0.20
    max_total_exposure_fraction: float = 0.60
    max_positions: int = 5
    fast_window: int = 20
    slow_window: int = 50
    stop_atr_multiple: float = 2.0
    reward_to_risk: float = 2.0
    minimum_signal_score: float = 0.65
    data_provider: str = "synthetic"
    broker: str = "paper"
    allow_live_trading: bool = False
    kronos_enabled: bool = False
    kronos_python: str = ""
    kronos_repo: str = ""
    kronos_model: str = "NeoQuasar/Kronos-mini"
    kronos_tokenizer: str = "NeoQuasar/Kronos-Tokenizer-2k"
    kronos_forecast_days: int = 5
    kronos_sample_count: int = 20
    kronos_min_return: float = 0.0

    def validate(self) -> None:
        if self.allow_live_trading:
            raise ValueError("Live trading is deliberately disabled in this project.")
        if not 0 < self.risk_per_trade <= 0.02:
            raise ValueError("risk_per_trade must be in (0, 0.02].")
        if not 0 < self.max_position_fraction <= 0.25:
            raise ValueError("max_position_fraction must be in (0, 0.25].")
        if not 0 < self.max_total_exposure_fraction <= 1:
            raise ValueError("max_total_exposure_fraction must be in (0, 1].")
        if self.fast_window >= self.slow_window:
            raise ValueError("fast_window must be smaller than slow_window.")
        if self.data_provider not in {"synthetic", "yfinance", "openbb"}:
            raise ValueError("data_provider must be synthetic, yfinance, or openbb.")
        if self.broker not in {"paper", "alpaca-paper"}:
            raise ValueError("broker must be paper or alpaca-paper.")
        if self.kronos_enabled:
            if not self.kronos_python or not self.kronos_repo:
                raise ValueError("kronos_python and kronos_repo are required when Kronos is enabled.")
            if not 1 <= self.kronos_forecast_days <= 20:
                raise ValueError("kronos_forecast_days must be in [1, 20].")
            if not 1 <= self.kronos_sample_count <= 100:
                raise ValueError("kronos_sample_count must be in [1, 100].")


def load_settings(path: str | Path | None) -> Settings:
    if path is None:
        settings = Settings()
    else:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        allowed = {f.name for f in fields(Settings)}
        unknown = set(raw) - allowed
        if unknown:
            raise ValueError(f"Unknown configuration keys: {sorted(unknown)}")
        if "watchlist" in raw:
            raw["watchlist"] = tuple(str(x).upper() for x in raw["watchlist"])
        settings = Settings(**raw)
    settings.validate()
    return settings
