from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import OrderIntent, Portfolio, Position


class PaperBroker:
    """Local fill simulator. It never sends network orders."""

    def __init__(self, state_path: str | Path, starting_cash: float):
        self.state_path = Path(state_path)
        self.portfolio = self._load(starting_cash)

    def _load(self, starting_cash: float) -> Portfolio:
        if not self.state_path.exists():
            return Portfolio(cash=starting_cash)
        raw = json.loads(self.state_path.read_text(encoding="utf-8"))
        positions = {k: Position(**v) for k, v in raw.get("positions", {}).items()}
        return Portfolio(cash=float(raw["cash"]), positions=positions)

    def submit(self, order: OrderIntent) -> dict[str, object]:
        if order.side != "buy":
            raise ValueError("The MVP supports buy intents only.")
        cost = order.quantity * order.reference_price
        if cost > self.portfolio.cash:
            raise ValueError("Insufficient paper cash.")
        self.portfolio.cash -= cost
        self.portfolio.positions[order.ticker] = Position(
            ticker=order.ticker,
            quantity=order.quantity,
            average_price=order.reference_price,
            stop_price=order.stop_price,
            take_profit_price=order.take_profit_price,
        )
        self.save()
        return {
            "status": "paper_filled",
            "ticker": order.ticker,
            "quantity": order.quantity,
            "price": order.reference_price,
        }

    def save(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(asdict(self.portfolio), indent=2, sort_keys=True),
            encoding="utf-8",
        )

