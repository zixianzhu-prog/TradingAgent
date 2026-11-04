# Serenity Trade

Local-first research, forecasting, risk-control, and paper-trading experiments built from open-source trading tools.

## One-command investment-agent demo

This demo reads the completed trend research and company map, uses OpenBB for real MRNA and DHR
history, runs 20/50-day trend signals, ATR risk controls, and a five-day Kronos forecast, then
creates one Chinese presentation report. It is always a dry run and never connects to a broker.

```bash
cd "/Users/rezz/Documents/Codex/2026-10-27/x20-wps-highlight"
./run-investment-agent-demo.sh
```

Open `outputs/investment-agent-demo.md` when it finishes.

## Daily news-to-investment research run

The daily pipeline fetches news, deduplicates it, updates company relevance, source reliability,
and deterministic sentiment scores, then combines them with OpenBB technical signals and Kronos.
The combined score is a research-priority heuristic, not a return probability.

```bash
./run-daily-investment-agent.sh
```

Open `outputs/daily-investment-agent.md` when it finishes. The script remains dry-run only.
It also updates `outputs/investment-score-performance.md` and the ignored local SQLite ledger at
`state/investment-score-history.db`. The first run for a market date is frozen; re-running cannot
rewrite it or create a duplicate. Later distinct market dates automatically fill the 1, 5, 20,
and 60-observation returns, direction hit rate, and high-score versus low-score performance.

On macOS, `scheduling/com.focuskpi.daily-investment-agent.plist` is a ready-to-install launchd
template for an 08:00 local-time run. Review the time and paths before copying it into
`~/Library/LaunchAgents/`; the template is included but is not silently enabled by this repository.

The daily score is calculated in three layers:

- News score: 50% company relevance + 30% source reliability + 20% normalized lexicon sentiment.
- Market score: the existing 20/50-day technical signal plus the five-day Kronos direction.
- Combined research score: 45% news + 35% technical + 20% Kronos.

Only scores at or above 70 with non-low news confidence are promoted to priority research. This
gate changes research priority only; it cannot place an order.

The final report also applies the local Aleabit/Serenity research-process and stock-selection
skills. Their gates require a mapped physical supply chain, defensible chokepoint, confirmed
customer dependency, substitution pressure test, and earnings validation. A high model score can
therefore trigger deeper research while still remaining `watch` under the Serenity framework.

Broad themes are also mapped to companies without requiring the company name to appear in each
article. `theme-company-map.json` supplies the auditable business/supply-chain link. Eligible
robotics candidates are selected into a generated, ignored config, analyzed separately with
OpenBB + Kronos, and written to `outputs/theme-market-validation.md`. They do not enter the broker
or overwrite the original biotech analysis.

## Local dashboard

The read-only dashboard summarizes live theme scores, mapped stocks, OpenBB/Kronos validation,
Serenity gates, and out-of-sample progress. Refresh its data and serve it locally with:

```bash
trend-agent/.venv/bin/python scripts/build_dashboard_data.py
python3 -m http.server 8765 --directory dashboard/dist
```

Then open `http://127.0.0.1:8765`. The daily pipeline refreshes `dashboard/dist/data.json`
automatically. The dashboard contains no API keys and cannot place orders.

## What is included

- `ai-fund-lab/` — the integration layer for market data, signals, Kronos forecasts, risk controls, and simulated orders.
- `trend-agent/` — continuous RSS and website-change ingestion, deduplication, theme scoring, and deep-research queueing.
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

