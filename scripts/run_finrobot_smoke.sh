#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$PROJECT_DIR"

: "${GEMINI_API_KEY:?GEMINI_API_KEY is not set in this terminal}"

FINROBOT_PROVIDER=finrobot-cli \
FINROBOT_MODEL="${FINROBOT_MODEL:-gemini:gemini-3.8-flash}" \
trend-agent/.venv/bin/python scripts/finrobot_event_analyst.py \
  --trends trend-agent/reports/daily/trends/latest-trends.json \
  --theme-links trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --serenity trend-agent/serenity-assessments.json \
  --provider finrobot-cli \
  --model "${FINROBOT_MODEL:-gemini:gemini-3.8-flash}" \
  --limit 1 \
  --timeout 120 \
  --json-output /tmp/finrobot-smoke.json \
  --markdown-output /tmp/finrobot-smoke.md

echo "Smoke report: /tmp/finrobot-smoke.md"
