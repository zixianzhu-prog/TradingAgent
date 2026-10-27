from __future__ import annotations

from statistics import mean

from .models import Bar, Signal


def average_true_range(bars: list[Bar], window: int = 14) -> float:
    sample = bars[-(window + 1):]
    ranges = []
    for previous, current in zip(sample, sample[1:]):
        ranges.append(
            max(
                current.high - current.low,
                abs(current.high - previous.close),
                abs(current.low - previous.close),
            )
        )
    return mean(ranges)


def trend_signal(
    ticker: str,
    bars: list[Bar],
    fast_window: int,
    slow_window: int,
    stop_atr_multiple: float,
) -> Signal:
    if len(bars) < slow_window + 1:
        raise ValueError(f"{ticker}: need at least {slow_window + 1} bars")
    close = bars[-1].close
    fast = mean(bar.close for bar in bars[-fast_window:])
    slow = mean(bar.close for bar in bars[-slow_window:])
    atr = average_true_range(bars)
    separation = (fast - slow) / slow
    score = max(0.0, min(1.0, 0.5 + separation * 12))
    direction = "buy" if fast > slow and close > fast else "hold"
    reasons = (
        f"close={close:.2f}",
        f"MA{fast_window}={fast:.2f}",
        f"MA{slow_window}={slow:.2f}",
        f"ATR14={atr:.2f}",
    )
    return Signal(
        ticker=ticker,
        score=score,
        direction=direction,
        price=close,
        stop_price=max(0.01, close - stop_atr_multiple * atr),
        reasons=reasons,
        as_of=bars[-1].day,
    )

