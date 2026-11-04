#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
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
trend-agent/.venv/bin/python scripts/performance_tracker.py \
  --market-dir outputs/daily-market \
  --news-report trend-agent/reports/daily/company-news/company-news-scores.json \
  --serenity-assessment trend-agent/serenity-assessments.json \
  --database state/investment-score-history.db \
  --output outputs/investment-score-performance.md
trend-agent/.venv/bin/python scripts/performance_tracker.py \
  --market-dir outputs/power-theme-market \
  --news-report trend-agent/reports/daily/company-news/company-news-scores.json \
  --serenity-assessment trend-agent/serenity-assessments.json \
  --theme-stock-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --database state/investment-score-history.db \
  --output outputs/investment-score-performance.md
trend-agent/.venv/bin/python scripts/performance_tracker.py \
  --market-dir outputs/theme-market \
  --news-report trend-agent/reports/daily/company-news/company-news-scores.json \
  --serenity-assessment trend-agent/serenity-assessments.json \
  --theme-stock-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --database state/investment-score-history.db \
  --output outputs/investment-score-performance.md
trend-agent/.venv/bin/python scripts/build_dashboard_data.py

echo "Daily report: $PROJECT_DIR/outputs/daily-investment-agent.md"
echo "Performance report: $PROJECT_DIR/outputs/investment-score-performance.md"
echo "Theme market report: $PROJECT_DIR/outputs/theme-market-validation.md"
echo "Dashboard: $PROJECT_DIR/dashboard/dist/index.html"
