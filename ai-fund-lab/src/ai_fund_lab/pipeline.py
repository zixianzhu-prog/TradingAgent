from __future__ import annotations

import json
from dataclasses import asdict, replace
from datetime import datetime, timezone
from pathlib import Path

from .broker import PaperBroker
from .config import Settings
from .data import build_provider
from .forecast import run_kronos_forecast
from .risk import build_order
from .signals import trend_signal


def run_pipeline(
    settings: Settings,
    state_path: str | Path,
    reports_dir: str | Path,
    execute: bool = False,
) -> dict[str, object]:
    if settings.broker != "paper":
        raise RuntimeError("Alpaca adapter is not enabled in the safe MVP yet.")
    provider = build_provider(settings.data_provider)
    broker = PaperBroker(state_path, settings.starting_cash)
    report: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "paper-execute" if execute else "dry-run",
        "data_provider": settings.data_provider,
        "results": [],
    }
    prices: dict[str, float] = {}
    bars_by_ticker = {}
    needed = settings.slow_window + 30
    for ticker in settings.watchlist:
        bars = provider.history(ticker, needed)
        bars_by_ticker[ticker] = bars
        prices[ticker] = bars[-1].close

    forecasts = run_kronos_forecast(bars_by_ticker, settings)
    report["kronos"] = forecasts

    for ticker in settings.watchlist:
        signal = trend_signal(
            ticker,
            bars_by_ticker[ticker],
            settings.fast_window,
            settings.slow_window,
            settings.stop_atr_multiple,
        )
        forecast = forecasts.get(ticker)
        if forecast is not None:
            forecast_return = float(forecast["forecast_return"])
            reasons = signal.reasons + (f"Kronos5D={forecast_return:+.2%}",)
            if forecast_return < settings.kronos_min_return:
                signal = replace(signal, direction="hold", reasons=reasons)
            else:
                signal = replace(signal, reasons=reasons)
        order = build_order(signal, broker.portfolio, prices, settings)
        item: dict[str, object] = {"signal": asdict(signal), "order": None, "fill": None}
        if order:
            item["order"] = asdict(order)
            if execute:
                item["fill"] = broker.submit(order)
        report["results"].append(item)

    report["portfolio"] = asdict(broker.portfolio)
    output_dir = Path(reports_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output = output_dir / f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    output.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    report["report_path"] = str(output)
    return report
