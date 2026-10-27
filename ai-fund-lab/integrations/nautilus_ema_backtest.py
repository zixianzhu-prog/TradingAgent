#!/usr/bin/env python3
"""Run a reproducible NautilusTrader EMA baseline on Freqtrade Coinbase data."""

from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

import pandas as pd

from nautilus_trader.analysis.reporter import ReportProvider
from nautilus_trader.backtest.engine import BacktestEngine
from nautilus_trader.config import BacktestEngineConfig, RiskEngineConfig, StrategyConfig
from nautilus_trader.backtest.models.fee import MakerTakerFeeModel
from nautilus_trader.indicators import ExponentialMovingAverage
from nautilus_trader.model.data import Bar, BarType
from nautilus_trader.model.enums import AccountType, OmsType, OrderSide
from nautilus_trader.model.identifiers import InstrumentId, Symbol, TraderId, Venue
from nautilus_trader.model.objects import Money, Price, Quantity
from nautilus_trader.model.currencies import Currency
from nautilus_trader.model.instruments import CurrencyPair
from nautilus_trader.trading import Strategy


VENUE = Venue("COINBASE")
USD = Currency.from_str("USD")
BAR_NANOS = 5 * 60 * 1_000_000_000


class LongOnlyEmaConfig(StrategyConfig):
    instrument_id: InstrumentId
    bar_type: BarType
    trade_size: Decimal
    final_market_ts: int
    fast_period: int = 10
    slow_period: int = 20


class LongOnlyEmaCross(Strategy):
    """Enter on EMA cross-up and exit on cross-down; never short."""

    def __init__(self, config: LongOnlyEmaConfig) -> None:
        super().__init__(config)
        self.fast = ExponentialMovingAverage(config.fast_period)
        self.slow = ExponentialMovingAverage(config.slow_period)
        self.previous_above: bool | None = None
        self.final_exit_sent = False

    def on_start(self) -> None:
        self.register_indicator_for_bars(self.config.bar_type, self.fast)
        self.register_indicator_for_bars(self.config.bar_type, self.slow)
        self.subscribe_bars(self.config.bar_type)

    def on_bar(self, bar: Bar) -> None:
        if not self.indicators_initialized():
            return

        if bar.ts_event >= self.config.final_market_ts:
            if self.portfolio.is_net_long(self.config.instrument_id) and not self.final_exit_sent:
                self.close_all_positions(self.config.instrument_id)
                self.final_exit_sent = True
            return

        above = self.fast.value >= self.slow.value
        if self.previous_above is None:
            self.previous_above = above
            return

        is_flat = not self.portfolio.is_net_long(
            self.config.instrument_id,
        ) and not self.portfolio.is_net_short(self.config.instrument_id)
        if above and not self.previous_above and is_flat:
            instrument = self.cache.instrument(self.config.instrument_id)
            order = self.order_factory.market(
                self.config.instrument_id,
                OrderSide.BUY,
                instrument.make_qty(self.config.trade_size),
            )
            self.submit_order(order)
        elif not above and self.previous_above and self.portfolio.is_net_long(self.config.instrument_id):
            self.close_all_positions(self.config.instrument_id)

        self.previous_above = above


def make_instrument(asset: str) -> CurrencyPair:
    instrument_id = InstrumentId(Symbol(f"{asset}USD"), VENUE)
    return CurrencyPair(
        instrument_id=instrument_id,
        raw_symbol=Symbol(f"{asset}-USD"),
        base_currency=Currency.from_str(asset),
        quote_currency=USD,
        price_precision=2,
        size_precision=6,
        price_increment=Price.from_str("0.01"),
        size_increment=Quantity.from_str("0.000001"),
        maker_fee=Decimal("0.012"),
        taker_fee=Decimal("0.012"),
        ts_event=0,
        ts_init=0,
    )


def load_bars(path: Path, instrument: CurrencyPair, start: str, end: str) -> tuple[list[Bar], int]:
    frame = pd.read_feather(path)
    frame["date"] = pd.to_datetime(frame["date"], utc=True)
    mask = (frame["date"] >= pd.Timestamp(start, tz="UTC")) & (
        frame["date"] < pd.Timestamp(end, tz="UTC")
    )
    frame = frame.loc[mask].sort_values("date")
    if frame.empty:
        raise RuntimeError(f"No bars in requested range: {path}")

    bar_type = BarType.from_str(f"{instrument.id}-5-MINUTE-LAST-EXTERNAL")
    bars: list[Bar] = []
    for row in frame.itertuples(index=False):
        close_ts = int(row.date.value) + BAR_NANOS
        bars.append(
            Bar(
                bar_type=bar_type,
                open=instrument.make_price(row.open),
                high=instrument.make_price(row.high),
                low=instrument.make_price(row.low),
                close=instrument.make_price(row.close),
                volume=instrument.make_qty(row.volume),
                ts_event=close_ts,
                ts_init=close_ts,
            ),
        )

    final_market_ts = bars[-1].ts_event
    last = bars[-1]
    for offset in (BAR_NANOS, 2 * BAR_NANOS):
        bars.append(
            Bar(
                bar_type=bar_type,
                open=last.close,
                high=last.close,
                low=last.close,
                close=last.close,
                volume=instrument.make_qty(0),
                ts_event=final_market_ts + offset,
                ts_init=final_market_ts + offset,
            ),
        )
    return bars, final_market_ts


def dataframe_records(frame: pd.DataFrame) -> list[dict[str, object]]:
    clean = frame.reset_index()
    return json.loads(clean.to_json(orient="records", date_format="iso"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--start", default="2026-09-28")
    parser.add_argument("--end", default="2026-10-27")
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    engine = BacktestEngine(
        BacktestEngineConfig(
            trader_id=TraderId("BACKTESTER-001"),
            risk_engine=RiskEngineConfig(bypass=True),
        ),
    )
    engine.add_venue(
        venue=VENUE,
        oms_type=OmsType.NETTING,
        account_type=AccountType.CASH,
        base_currency=None,
        starting_balances=[Money.from_str("10000 USD")],
        fee_model=MakerTakerFeeModel(),
    )

    specifications = (("BTC", "BTC_USD-5m.feather", Decimal("0.01")), ("ETH", "ETH_USD-5m.feather", Decimal("0.30")))
    bar_counts: dict[str, int] = {}
    for asset, filename, trade_size in specifications:
        instrument = make_instrument(asset)
        engine.add_instrument(instrument)
        bars, final_market_ts = load_bars(args.data_dir / filename, instrument, args.start, args.end)
        bar_counts[asset] = len(bars) - 2
        engine.add_data(bars)
        bar_type = BarType.from_str(f"{instrument.id}-5-MINUTE-LAST-EXTERNAL")
        engine.add_strategy(
            LongOnlyEmaCross(
                LongOnlyEmaConfig(
                    instrument_id=instrument.id,
                    bar_type=bar_type,
                    trade_size=trade_size,
                    final_market_ts=final_market_ts,
                ),
            ),
        )

    engine.run()
    account = ReportProvider.generate_account_report(engine.cache.account_for_venue(VENUE))
    fills = ReportProvider.generate_order_fills_report(engine.cache.orders())
    positions = ReportProvider.generate_positions_report(engine.cache.positions())
    account.to_csv(args.output_dir / "account.csv")
    fills.to_csv(args.output_dir / "fills.csv")
    positions.to_csv(args.output_dir / "positions.csv")

    result = {
        "engine": "NautilusTrader",
        "strategy": "Long-only EMA(10/20) crossover",
        "period": {"start": args.start, "end_exclusive": args.end},
        "starting_balance_usd": 10000,
        "fee_rate": 0.012,
        "trade_sizes": {"BTC": 0.01, "ETH": 0.30},
        "market_bars": bar_counts,
        "account": dataframe_records(account),
        "fills": dataframe_records(fills),
        "positions": dataframe_records(positions),
    }
    (args.output_dir / "raw-results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"bars": bar_counts, "fills": len(fills), "positions": len(positions)}, indent=2))
    print(account.tail())


if __name__ == "__main__":
    main()
