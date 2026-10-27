from __future__ import annotations

import math
import random
from datetime import date, timedelta
from typing import Protocol

from .models import Bar


class MarketDataProvider(Protocol):
    def history(self, ticker: str, bars: int) -> list[Bar]: ...


class SyntheticDataProvider:
    """Deterministic fake prices for installation tests and dry runs."""

    def history(self, ticker: str, bars: int) -> list[Bar]:
        rng = random.Random(f"ai-fund-lab:{ticker}")
        price = 80.0 + (sum(ord(c) for c in ticker) % 120)
        result: list[Bar] = []
        day = date.today() - timedelta(days=bars * 2)
        while len(result) < bars:
            day += timedelta(days=1)
            if day.weekday() >= 5:
                continue
            drift = 0.0007 + 0.0004 * math.sin(len(result) / 17)
            change = drift + rng.gauss(0, 0.012)
            open_price = price * (1 + rng.gauss(0, 0.002))
            close = max(1.0, price * (1 + change))
            spread = abs(rng.gauss(0.009, 0.003))
            high = max(open_price, close) * (1 + spread)
            low = min(open_price, close) * (1 - spread)
            result.append(
                Bar(day, open_price, high, low, close, rng.randint(800_000, 8_000_000))
            )
            price = close
        return result


class YFinanceDataProvider:
    def history(self, ticker: str, bars: int) -> list[Bar]:
        try:
            import yfinance as yf
        except ImportError as exc:
            raise RuntimeError(
                "yfinance is not installed; run: pip install -e '.[market-data]'"
            ) from exc
        frame = yf.download(
            ticker, period="2y", interval="1d", auto_adjust=True, progress=False
        ).tail(bars)
        result: list[Bar] = []
        for index, row in frame.iterrows():
            def value(name: str) -> float:
                item = row[name]
                if hasattr(item, "iloc"):
                    item = item.iloc[0]
                return float(item)

            result.append(
                Bar(
                    index.date(), value("Open"), value("High"), value("Low"),
                    value("Close"), value("Volume")
                )
            )
        if len(result) < bars:
            raise RuntimeError(f"Only {len(result)} bars returned for {ticker}; need {bars}.")
        return result


class OpenBBDataProvider:
    """OpenBB data layer backed explicitly by its Yahoo Finance provider."""

    def history(self, ticker: str, bars: int) -> list[Bar]:
        try:
            from openbb import obb
        except ImportError as exc:
            raise RuntimeError(
                "OpenBB is not installed; run: pip install -e '.[openbb-data]'"
            ) from exc

        # Request extra calendar days so weekends and exchange holidays do not
        # leave the strategy with too few observations.
        start = date.today() - timedelta(days=max(120, bars * 3))
        response = obb.equity.price.historical(
            ticker,
            start_date=start,
            provider="yfinance",
        )
        frame = response.to_dataframe().tail(bars)
        result: list[Bar] = []
        for index, row in frame.iterrows():
            result.append(
                Bar(
                    index.date() if hasattr(index, "date") else index,
                    float(row["open"]),
                    float(row["high"]),
                    float(row["low"]),
                    float(row["close"]),
                    float(row.get("volume", 0.0)),
                )
            )
        if len(result) < bars:
            raise RuntimeError(f"OpenBB returned {len(result)} bars for {ticker}; need {bars}.")
        return result


def build_provider(name: str) -> MarketDataProvider:
    if name == "synthetic":
        return SyntheticDataProvider()
    if name == "yfinance":
        return YFinanceDataProvider()
    if name == "openbb":
        return OpenBBDataProvider()
    raise ValueError(f"Unsupported data provider: {name}")
