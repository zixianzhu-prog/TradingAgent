#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
FREE_KB=$(df -Pk "$PROJECT_DIR" | awk 'NR==2 {print $4}')
MIN_FREE_KB=1048576
if [ "${FREE_KB:-0}" -lt "$MIN_FREE_KB" ]; then
  echo "Daily agent stopped before data collection: less than 1 GiB free disk space." >&2
  echo "Free generated caches or disk space, then run again. No market workflow was started." >&2
  exit 2
fi
cd "$PROJECT_DIR/trend-agent"
./trend-agent cycle \
  --sources sources.ai-medicine.json \
  --config config.ai-medicine.json \
  --database state/daily-news.db \
  --output reports/daily/trends
./trend-agent company-scores \
  --database state/daily-news.db \
  --companies companies.example.json \
  --output reports/daily/company-news \
  --lookback-days 7
./trend-agent theme-stocks \
  --trends reports/daily/trends/latest-trends.json \
  --mapping theme-company-map.json \
  --output reports/daily/theme-stocks

cd "$PROJECT_DIR"
# Emerging-signal radar: no preset themes. Broad health feeds go into their own
# database; bursts across sources are mapped to companies through SEC filings and
# trial registrations. Network failures are recorded in the outputs, not fatal.
trend-agent/.venv/bin/python scripts/emerging_signal_detector.py \
  --collect trend-agent/sources.radar.json \
  --database trend-agent/state/daily-news.db \
  --theme-config trend-agent/config.ai-medicine.json
trend-agent/.venv/bin/python scripts/beneficiary_mapper.py \
  --signals state/emerging-signals.json \
  --top-signals 3
ai-fund-lab/.venv/bin/python scripts/pricing_check.py
# News-driven recommendations, step 1: one news search per covered company, so today's
# company events are in the Serenity evidence packets prepared below.
# Primary sources: SEC filings for every covered company and FDA/CMS/HHS Federal Register rules.
PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/official_feeds.py
# FDA device decisions (openFDA 510(k), De Novo, PMA): AI/software devices mapped to listed companies.
# Uses SEC_USER_AGENT, if set, to flag listed applicants the agent does not cover yet.
(cd scripts && ../trend-agent/.venv/bin/python fda_device_feed.py --days 45)
# A new FDA decision by a reviewed company reopens its chokepoint, AI-purity and counter-thesis gates:
# the FDA record and summary join its evidence packet and the review shows as pending until re-checked.
(cd scripts && ../trend-agent/.venv/bin/python event_gate_recheck.py prepare)
trend-agent/.venv/bin/python scripts/news_signal_engine.py --collect
trend-agent/.venv/bin/python scripts/fda_ai_devices_agent.py \
  --config trend-agent/fda-ai-company-map.json \
  --state state/fda-ai-devices.json \
  --report outputs/fda-ai-devices.md
trend-agent/.venv/bin/python scripts/clinical_trials_agent.py \
  --config trend-agent/clinical-watchlist.json \
  --state state/clinical-trials-snapshot.json \
  --report outputs/clinical-trials-monitor.md
trend-agent/.venv/bin/python scripts/form4_agent.py \
  --config trend-agent/form4-watchlist.json \
  --state state/form4-snapshot.json \
  --report outputs/form4-insider-monitor.md
trend-agent/.venv/bin/python scripts/event_revalidation_agent.py \
  --config trend-agent/event-watchlist.json \
  --database trend-agent/state/daily-news.db \
  --json-output state/event-revalidation.json \
  --markdown-output outputs/event-revalidation-queue.md
trend-agent/.venv/bin/python scripts/disclosure_conflict_agent.py \
  --config trend-agent/event-watchlist.json \
  --database trend-agent/state/daily-news.db \
  --json-output state/disclosure-divergences.json \
  --markdown-output outputs/disclosure-divergence-report.md
trend-agent/.venv/bin/python scripts/sec_xbrl_validation_agent.py \
  --config trend-agent/sec-companyfacts-watchlist.json \
  --financials trend-agent/ai-medicine-financials.json \
  --json-output state/sec-xbrl-validation.json \
  --markdown-output outputs/sec-xbrl-validation.md
# Prepare auditable evidence packets. The scheduled Codex agent reviews these with
# the user's ChatGPT/Codex allowance; this shell workflow never calls a model API.
trend-agent/.venv/bin/python scripts/serenity_evidence_review.py --prepare-codex --fetch-primary
trend-agent/.venv/bin/python scripts/serenity_gate_engine.py \
  --assessments state/serenity-auto-assessments.json \
  --events state/event-revalidation.json \
  --divergences state/disclosure-divergences.json \
  --clinical state/clinical-trials-snapshot.json \
  --json-output state/serenity-gate-results.json \
  --markdown-output outputs/serenity-gate-audit.md

cd "$PROJECT_DIR"
trend-agent/.venv/bin/python scripts/build_theme_market_config.py \
  --theme-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --base-config ai-fund-lab/config.trend-biotech-kronos.json \
  --theme ai_medicine \
  --limit 16 \
  --include-ticker GEHC \
  --include-ticker RDNT \
  --include-ticker ISRG \
  --include-ticker IQV \
  --include-ticker NVDA \
  --include-ticker HTFL \
  --include-ticker CBLL \
  --include-ticker CAI \
  --output state/config.ai-medicine-kronos.json
cd "$PROJECT_DIR/ai-fund-lab"
PYTHONPATH=src .venv/bin/python -m ai_fund_lab.cli \
  --config ../state/config.ai-medicine-kronos.json \
  --reports ../outputs/ai-medicine-market

cd "$PROJECT_DIR"
trend-agent/.venv/bin/python scripts/build_theme_market_config.py \
  --theme-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --base-config ai-fund-lab/config.trend-biotech-kronos.json \
  --theme nvidia_company_news \
  --limit 1 \
  --fallback-ticker NVDA \
  --output state/config.nvidia-kronos.json
cd "$PROJECT_DIR/ai-fund-lab"
PYTHONPATH=src .venv/bin/python -m ai_fund_lab.cli \
  --config ../state/config.nvidia-kronos.json \
  --reports ../outputs/nvidia-market

cd "$PROJECT_DIR"
if [ "${RUN_TRADINGAGENTS_FULL_REVIEW:-1}" = "1" ]; then
  python3 scripts/run_tradingagents_full_review.py \
    --limit "${TRADINGAGENTS_REVIEW_LIMIT:-1}" \
    --cadence-days "${TRADINGAGENTS_REVIEW_CADENCE_DAYS:-7}" \
    --depth "${TRADINGAGENTS_REVIEW_DEPTH:-1}"
fi
trend-agent/.venv/bin/python scripts/import_tradingagents_reports.py \
  --input-root outputs \
  --tradingagents-root work/TradingAgents/data/logs \
  --output state/tradingagents-reviews.json
trend-agent/.venv/bin/python scripts/build_demo_report.py \
  --market-dir outputs/ai-medicine-market \
  --news-report trend-agent/reports/daily/company-news/company-news-scores.json \
  --trend-report trend-agent/reports/daily/trends/latest-trends.json \
  --serenity-assessment state/serenity-auto-assessments.json \
  --theme-stock-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --output outputs/daily-investment-agent.md
trend-agent/.venv/bin/python scripts/build_theme_market_report.py \
  --market-dir outputs/ai-medicine-market \
  --theme-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --output outputs/ai-medicine-market-validation.md
trend-agent/.venv/bin/python scripts/build_theme_market_report.py \
  --market-dir outputs/nvidia-market \
  --theme-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --output outputs/nvidia-company-news-impact.md
trend-agent/.venv/bin/python scripts/build_nvidia_event_report.py
trend-agent/.venv/bin/python scripts/ai_medicine_peer_screen.py \
  --universe trend-agent/ai-medicine-universe.json \
  --json-output state/ai-medicine-peer-screen.json \
  --markdown-output outputs/ai-medicine-peer-screen.md
trend-agent/.venv/bin/python scripts/build_financial_scenarios.py \
  --financials trend-agent/ai-medicine-financials.json \
  --json-output state/ai-medicine-financial-scenarios.json \
  --markdown-output outputs/ai-medicine-financial-scenarios.md
trend-agent/.venv/bin/python scripts/build_ai_medicine_report.py \
  --theses trend-agent/ai-medicine-theses.json \
  --market-dir outputs/ai-medicine-market \
  --serenity state/serenity-auto-assessments.json \
  --serenity-gate state/serenity-gate-results.json \
  --peer-screen state/ai-medicine-peer-screen.json \
  --fda-devices state/fda-ai-devices.json \
  --financial-scenarios state/ai-medicine-financial-scenarios.json \
  --independent-evidence trend-agent/ai-medicine-independent-evidence.json \
  --evidence-coverage-plan trend-agent/ai-medicine-evidence-coverage-plan.json \
  --output outputs/ai-medicine-5-10-year-thesis.md
# One-page answer: AI-medicine leaders over 5-10 years (dashboard/dist/top5.html).
# Market-wide AI-medicine screen (SEC full-text search + FDA + market data). Weekly is
# enough: filings change slowly and each run makes ~100 SEC requests.
SCREEN_STATE=state/ai-medicine-universe-screen.json
if [ ! -f "$SCREEN_STATE" ] || [ -n "$(find "$SCREEN_STATE" -mtime +6 2>/dev/null)" ]; then
  PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/ai_medicine_universe_screen.py
  # Upstream bottleneck map and Serenity evidence packets for newly shortlisted names.
  PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/ai_medicine_chokepoints.py
  PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/prepare_serenity_queue.py
  # Which companies' filings describe each AI-medicine topic (frontier news -> company mapping).
  PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/topic_exposure.py
fi
# News-driven recommendations, step 2: recompute with today's Serenity gate results.
trend-agent/.venv/bin/python scripts/news_signal_engine.py
# Which Serenity reviews match today's evidence, and which Claude memos are still unchecked.
trend-agent/.venv/bin/python scripts/serenity_review_status.py
trend-agent/.venv/bin/python scripts/build_top5_brief.py
# Emerging-signal radar page (dashboard/dist/radar.html): today's signals, mapped companies, replays.
trend-agent/.venv/bin/python scripts/build_radar_page.py
ai-fund-lab/.venv/bin/python scripts/market_profile_agent.py \
  --theme-links trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --financials state/ai-medicine-financial-scenarios.json \
  --state state/market-profiles.json \
  --report outputs/market-profile-audit.md
trend-agent/.venv/bin/python scripts/hidden_gems_agent.py \
  --theme-links trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --serenity state/serenity-auto-assessments.json \
  --financials state/ai-medicine-financial-scenarios.json \
  --news trend-agent/reports/daily/company-news/company-news-scores.json \
  --market-profiles state/market-profiles.json \
  --json-output state/hidden-gems.json \
  --markdown-output outputs/hidden-gems.md
trend-agent/.venv/bin/python scripts/evidence_graph_agent.py \
  --theses trend-agent/ai-medicine-theses.json \
  --assessments state/serenity-auto-assessments.json \
  --clinical state/clinical-trials-snapshot.json \
  --events state/event-revalidation.json \
  --financials trend-agent/ai-medicine-financials.json \
  --json-output state/ai-medicine-evidence-graph.json \
  --markdown-output outputs/ai-medicine-evidence-graph.md
trend-agent/.venv/bin/python scripts/audit_investment_theses.py \
  --theses trend-agent/ai-medicine-theses.json \
  --serenity state/serenity-auto-assessments.json \
  --market-dir outputs/ai-medicine-market \
  --output state/ai-medicine-thesis-audit.json
# Backfill earlier frozen predictions on real trading-day prices first; the
# tracker then freezes today's scores and reports from benchmark_outcomes.
ai-fund-lab/.venv/bin/python scripts/benchmark_evaluator.py \
  --database state/investment-score-history.db \
  --cohort ai-medicine \
  --output outputs/agent-benchmark-validation.md
trend-agent/.venv/bin/python scripts/performance_tracker.py \
  --market-dir outputs/ai-medicine-market \
  --cohort ai-medicine \
  --news-report trend-agent/reports/daily/company-news/company-news-scores.json \
  --serenity-assessment state/serenity-auto-assessments.json \
  --theme-stock-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --database state/investment-score-history.db \
  --output outputs/investment-score-performance.md
# Freeze Serenity research tiers (weekly or on change) in the same ledger, score them
# against XBI on real trading days, then rebuild the demo page with the track record.
(cd scripts && ../ai-fund-lab/.venv/bin/python serenity_call_ledger.py)
# Market validation (OpenBB prices, Kronos 5-day forecasts) beside the 5-10 year ranking; context only.
ai-fund-lab/.venv/bin/python scripts/market_validation.py
trend-agent/.venv/bin/python scripts/build_top5_brief.py
trend-agent/.venv/bin/python scripts/thesis_memory_agent.py \
  --theses trend-agent/ai-medicine-theses.json \
  --gates state/serenity-gate-results.json \
  --financials state/ai-medicine-financial-scenarios.json \
  --market-dir outputs/ai-medicine-market \
  --events state/event-revalidation.json \
  --performance-db state/investment-score-history.db \
  --state state/ai-medicine-thesis-memory.json \
  --report outputs/ai-medicine-thesis-memory.md
trend-agent/.venv/bin/python scripts/build_dashboard_data.py
trend-agent/.venv/bin/python scripts/daily_data_inventory.py \
  --json-output state/daily-data-inventory.json \
  --markdown-output outputs/daily-data-inventory.md

echo "Daily report: $PROJECT_DIR/outputs/daily-investment-agent.md"
echo "Performance report: $PROJECT_DIR/outputs/investment-score-performance.md"
echo "Benchmark report: $PROJECT_DIR/outputs/agent-benchmark-validation.md"
echo "AI Medicine report: $PROJECT_DIR/outputs/ai-medicine-5-10-year-thesis.md"
echo "NVIDIA company news and market validation: $PROJECT_DIR/outputs/nvidia-company-news-impact.md"
echo "AI Medicine peer screen: $PROJECT_DIR/outputs/ai-medicine-peer-screen.md"
echo "AI Medicine thesis memory: $PROJECT_DIR/outputs/ai-medicine-thesis-memory.md"
echo "AI Medicine financial scenarios: $PROJECT_DIR/outputs/ai-medicine-financial-scenarios.md"
echo "Market profile audit: $PROJECT_DIR/outputs/market-profile-audit.md"
echo "Hidden Gems screen: $PROJECT_DIR/outputs/hidden-gems.md"
echo "Serenity gate audit: $PROJECT_DIR/outputs/serenity-gate-audit.md"
echo "Disclosure divergence report: $PROJECT_DIR/outputs/disclosure-divergence-report.md"
echo "Clinical trials monitor: $PROJECT_DIR/outputs/clinical-trials-monitor.md"
echo "FDA AI medical-device monitor: $PROJECT_DIR/outputs/fda-ai-devices.md"
echo "SEC Form 4 monitor: $PROJECT_DIR/outputs/form4-insider-monitor.md"
echo "AI Medicine evidence graph: $PROJECT_DIR/outputs/ai-medicine-evidence-graph.md"
echo "SEC XBRL validation: $PROJECT_DIR/outputs/sec-xbrl-validation.md"
echo "Dashboard: $PROJECT_DIR/dashboard/dist/index.html"
echo "Daily data inventory: $PROJECT_DIR/outputs/daily-data-inventory.md"
