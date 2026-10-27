from __future__ import annotations

from .config import Settings
from .models import OrderIntent, Portfolio, Signal


def build_order(
    signal: Signal,
    portfolio: Portfolio,
    prices: dict[str, float],
    settings: Settings,
) -> OrderIntent | None:
    if signal.direction != "buy" or signal.score < settings.minimum_signal_score:
        return None
    if signal.ticker in portfolio.positions:
        return None
    if len(portfolio.positions) >= settings.max_positions:
        return None

    equity = portfolio.equity(prices)
    exposure = portfolio.market_value(prices)
    remaining_exposure = max(0.0, equity * settings.max_total_exposure_fraction - exposure)
    per_share_risk = signal.price - signal.stop_price
    if per_share_risk <= 0:
        return None

    risk_quantity = int((equity * settings.risk_per_trade) / per_share_risk)
    position_cap_quantity = int((equity * settings.max_position_fraction) / signal.price)
    exposure_quantity = int(remaining_exposure / signal.price)
    cash_quantity = int(portfolio.cash / signal.price)
    quantity = min(risk_quantity, position_cap_quantity, exposure_quantity, cash_quantity)
    if quantity < 1:
        return None
    risk = signal.price - signal.stop_price
    return OrderIntent(
        ticker=signal.ticker,
        side="buy",
        quantity=quantity,
        reference_price=signal.price,
        stop_price=signal.stop_price,
        take_profit_price=signal.price + settings.reward_to_risk * risk,
        signal_score=signal.score,
        reasons=signal.reasons,
    )

