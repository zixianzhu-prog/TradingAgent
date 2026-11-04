#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_DIR/ai-fund-lab"
PYTHONPATH=src .venv/bin/python -m ai_fund_lab.cli \
  --config config.trend-biotech-kronos.json \
  --reports ../outputs/ai-fund-lab-trend-biotech-kronos

cd "$PROJECT_DIR"
trend-agent/.venv/bin/python scripts/build_demo_report.py \
  --market-dir outputs/ai-fund-lab-trend-biotech-kronos \
  --output outputs/investment-agent-demo.md

echo "Demo complete: $PROJECT_DIR/outputs/investment-agent-demo.md"
