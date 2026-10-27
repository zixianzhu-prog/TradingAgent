from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass(frozen=True)
class Bar:
    day: date
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class Signal:
    ticker: str
    score: float
    direction: str
    price: float
    stop_price: float
    reasons: tuple[str, ...]
    as_of: date


@dataclass(frozen=True)
class OrderIntent:
    ticker: str
    side: str
    quantity: int
    reference_price: float
    stop_price: float
    take_profit_price: float
    signal_score: float
    reasons: tuple[str, ...]


@dataclass
class Position:
    ticker: str
    quantity: int
    average_price: float
    stop_price: float
    take_profit_price: float


@dataclass
class Portfolio:
    cash: float
    positions: dict[str, Position] = field(default_factory=dict)

    def market_value(self, prices: dict[str, float]) -> float:
        return sum(
            p.quantity * prices.get(ticker, p.average_price)
            for ticker, p in self.positions.items()
        )

    def equity(self, prices: dict[str, float]) -> float:
        return self.cash + self.market_value(prices)

