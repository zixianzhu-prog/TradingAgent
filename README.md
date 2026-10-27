# Serenity Trade

Local-first research, forecasting, risk-control, and paper-trading experiments built from open-source trading tools.

## What is included

- `ai-fund-lab/` — the integration layer for market data, signals, Kronos forecasts, risk controls, and simulated orders.
- `outputs/` — generated research reports, forecasts, backtest summaries, and raw backtest artifacts.
- `outputs/10-repo-progress.md` — implementation and validation status for the ten-repository roadmap.

## Current status

- TradingAgents generated an NVDA market report and investment plan.
- OpenBB and Kronos analyzed NVDA, AAPL, and MSFT in dry-run mode.
- Freqtrade completed a 29-day BTC/USD and ETH/USD engineering baseline backtest.
- CCXT, Qlib, Hummingbot, and NautilusTrader passed local minimum validations.
- No real trades have been placed. All execution remains backtest, dry-run, or paper-only.

## Reports

See [`outputs/`](outputs/) for generated reports and [`outputs/10-repo-progress.md`](outputs/10-repo-progress.md) for detailed progress.

## Safety

This repository does not contain API keys, exchange credentials, model weights, virtual environments, or live brokerage connections. Nothing here is financial advice.

