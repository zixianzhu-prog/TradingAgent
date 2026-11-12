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
  --sources sources.daily.json \
  --config config.example.json \
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
trend-agent/.venv/bin/python scripts/serenity_gate_engine.py \
  --assessments trend-agent/serenity-assessments.json \
  --events state/event-revalidation.json \
  --divergences state/disclosure-divergences.json \
  --clinical state/clinical-trials-snapshot.json \
  --json-output state/serenity-gate-results.json \
  --markdown-output outputs/serenity-gate-audit.md

cd "$PROJECT_DIR/ai-fund-lab"
PYTHONPATH=src .venv/bin/python -m ai_fund_lab.cli \
  --config config.trend-biotech-kronos.json \
  --reports ../outputs/daily-market

cd "$PROJECT_DIR"
trend-agent/.venv/bin/python scripts/build_theme_market_config.py \
  --theme-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --base-config ai-fund-lab/config.trend-biotech-kronos.json \
  --theme robotics_automation \
  --limit 4 \
  --output state/config.daily-theme-kronos.json
cd "$PROJECT_DIR/ai-fund-lab"
PYTHONPATH=src .venv/bin/python -m ai_fund_lab.cli \
  --config ../state/config.daily-theme-kronos.json \
  --reports ../outputs/theme-market

cd "$PROJECT_DIR"
trend-agent/.venv/bin/python scripts/build_theme_market_config.py \
  --theme-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --base-config ai-fund-lab/config.trend-biotech-kronos.json \
  --theme ai_data_center_power \
  --limit 4 \
  --output state/config.power-theme-kronos.json
cd "$PROJECT_DIR/ai-fund-lab"
PYTHONPATH=src .venv/bin/python -m ai_fund_lab.cli \
  --config ../state/config.power-theme-kronos.json \
  --reports ../outputs/power-theme-market

cd "$PROJECT_DIR"
trend-agent/.venv/bin/python scripts/build_theme_market_config.py \
  --theme-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --base-config ai-fund-lab/config.trend-biotech-kronos.json \
  --theme ai_medicine \
  --limit 8 \
  --output state/config.ai-medicine-kronos.json
cd "$PROJECT_DIR/ai-fund-lab"
PYTHONPATH=src .venv/bin/python -m ai_fund_lab.cli \
  --config ../state/config.ai-medicine-kronos.json \
  --reports ../outputs/ai-medicine-market

cd "$PROJECT_DIR"
trend-agent/.venv/bin/python scripts/import_tradingagents_reports.py \
  --input-root outputs \
  --tradingagents-root work/TradingAgents/data/logs \
  --output state/tradingagents-reviews.json
trend-agent/.venv/bin/python scripts/build_demo_report.py \
  --market-dir outputs/daily-market \
  --news-report trend-agent/reports/daily/company-news/company-news-scores.json \
  --trend-report trend-agent/reports/daily/trends/latest-trends.json \
  --serenity-assessment trend-agent/serenity-assessments.json \
  --theme-stock-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --output outputs/daily-investment-agent.md
trend-agent/.venv/bin/python scripts/build_theme_market_report.py \
  --market-dir outputs/theme-market \
  --theme-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --output outputs/theme-market-validation.md
trend-agent/.venv/bin/python scripts/build_theme_market_report.py \
  --market-dir outputs/power-theme-market \
  --theme-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --output outputs/power-theme-market-validation.md
trend-agent/.venv/bin/python scripts/build_theme_market_report.py \
  --market-dir outputs/ai-medicine-market \
  --theme-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --output outputs/ai-medicine-market-validation.md
trend-agent/.venv/bin/python scripts/ai_medicine_peer_screen.py \
  --universe trend-agent/ai-medicine-universe.json \
  --json-output state/ai-medicine-peer-screen.json \
  --markdown-output outputs/ai-medicine-peer-screen.md
trend-agent/.venv/bin/python scripts/build_ai_medicine_report.py \
  --theses trend-agent/ai-medicine-theses.json \
  --market-dir outputs/ai-medicine-market \
  --serenity trend-agent/serenity-assessments.json \
  --serenity-gate state/serenity-gate-results.json \
  --peer-screen state/ai-medicine-peer-screen.json \
  --output outputs/ai-medicine-5-10-year-thesis.md
trend-agent/.venv/bin/python scripts/build_financial_scenarios.py \
  --financials trend-agent/ai-medicine-financials.json \
  --json-output state/ai-medicine-financial-scenarios.json \
  --markdown-output outputs/ai-medicine-financial-scenarios.md
trend-agent/.venv/bin/python scripts/sec_xbrl_validation_agent.py \
  --config trend-agent/sec-companyfacts-watchlist.json \
  --financials trend-agent/ai-medicine-financials.json \
  --json-output state/sec-xbrl-validation.json \
  --markdown-output outputs/sec-xbrl-validation.md
trend-agent/.venv/bin/python scripts/evidence_graph_agent.py \
  --theses trend-agent/ai-medicine-theses.json \
  --assessments trend-agent/serenity-assessments.json \
  --clinical state/clinical-trials-snapshot.json \
  --events state/event-revalidation.json \
  --financials trend-agent/ai-medicine-financials.json \
  --json-output state/ai-medicine-evidence-graph.json \
  --markdown-output outputs/ai-medicine-evidence-graph.md
trend-agent/.venv/bin/python scripts/audit_investment_theses.py \
  --theses trend-agent/ai-medicine-theses.json \
  --serenity trend-agent/serenity-assessments.json \
  --market-dir outputs/ai-medicine-market \
  --output state/ai-medicine-thesis-audit.json
trend-agent/.venv/bin/python scripts/performance_tracker.py \
  --market-dir outputs/daily-market \
  --cohort core-biotech \
  --news-report trend-agent/reports/daily/company-news/company-news-scores.json \
  --serenity-assessment trend-agent/serenity-assessments.json \
  --database state/investment-score-history.db \
  --output outputs/investment-score-performance.md
trend-agent/.venv/bin/python scripts/performance_tracker.py \
  --market-dir outputs/power-theme-market \
  --cohort ai-data-center-power \
  --news-report trend-agent/reports/daily/company-news/company-news-scores.json \
  --serenity-assessment trend-agent/serenity-assessments.json \
  --theme-stock-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --database state/investment-score-history.db \
  --output outputs/investment-score-performance.md
trend-agent/.venv/bin/python scripts/performance_tracker.py \
  --market-dir outputs/theme-market \
  --cohort robotics-automation \
  --news-report trend-agent/reports/daily/company-news/company-news-scores.json \
  --serenity-assessment trend-agent/serenity-assessments.json \
  --theme-stock-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --database state/investment-score-history.db \
  --output outputs/investment-score-performance.md
trend-agent/.venv/bin/python scripts/performance_tracker.py \
  --market-dir outputs/ai-medicine-market \
  --cohort ai-medicine \
  --news-report trend-agent/reports/daily/company-news/company-news-scores.json \
  --serenity-assessment trend-agent/serenity-assessments.json \
  --theme-stock-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --database state/investment-score-history.db \
  --output outputs/investment-score-performance.md
ai-fund-lab/.venv/bin/python scripts/benchmark_evaluator.py \
  --database state/investment-score-history.db \
  --cohort ai-medicine \
  --output outputs/agent-benchmark-validation.md
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

echo "Daily report: $PROJECT_DIR/outputs/daily-investment-agent.md"
echo "Performance report: $PROJECT_DIR/outputs/investment-score-performance.md"
echo "Benchmark report: $PROJECT_DIR/outputs/agent-benchmark-validation.md"
echo "Theme market report: $PROJECT_DIR/outputs/theme-market-validation.md"
echo "AI Medicine report: $PROJECT_DIR/outputs/ai-medicine-5-10-year-thesis.md"
echo "AI Medicine peer screen: $PROJECT_DIR/outputs/ai-medicine-peer-screen.md"
echo "AI Medicine thesis memory: $PROJECT_DIR/outputs/ai-medicine-thesis-memory.md"
echo "AI Medicine financial scenarios: $PROJECT_DIR/outputs/ai-medicine-financial-scenarios.md"
echo "Serenity gate audit: $PROJECT_DIR/outputs/serenity-gate-audit.md"
echo "Disclosure divergence report: $PROJECT_DIR/outputs/disclosure-divergence-report.md"
echo "Clinical trials monitor: $PROJECT_DIR/outputs/clinical-trials-monitor.md"
echo "SEC Form 4 monitor: $PROJECT_DIR/outputs/form4-insider-monitor.md"
echo "AI Medicine evidence graph: $PROJECT_DIR/outputs/ai-medicine-evidence-graph.md"
echo "SEC XBRL validation: $PROJECT_DIR/outputs/sec-xbrl-validation.md"
echo "Dashboard: $PROJECT_DIR/dashboard/dist/index.html"
