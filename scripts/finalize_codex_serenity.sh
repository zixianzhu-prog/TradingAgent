#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
RESPONSE_PATH=${1:-state/serenity-codex-response.json}
cd "$PROJECT_DIR"

trend-agent/.venv/bin/python scripts/serenity_evidence_review.py \
  --import-codex "$RESPONSE_PATH"
trend-agent/.venv/bin/python scripts/serenity_gate_engine.py \
  --assessments state/serenity-auto-assessments.json \
  --events state/event-revalidation.json \
  --divergences state/disclosure-divergences.json \
  --clinical state/clinical-trials-snapshot.json \
  --json-output state/serenity-gate-results.json \
  --markdown-output outputs/serenity-gate-audit.md
trend-agent/.venv/bin/python scripts/build_demo_report.py \
  --market-dir outputs/ai-medicine-market \
  --news-report trend-agent/reports/daily/company-news/company-news-scores.json \
  --trend-report trend-agent/reports/daily/trends/latest-trends.json \
  --serenity-assessment state/serenity-auto-assessments.json \
  --theme-stock-report trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --output outputs/daily-investment-agent.md
trend-agent/.venv/bin/python scripts/build_ai_medicine_report.py \
  --theses trend-agent/ai-medicine-theses.json \
  --market-dir outputs/ai-medicine-market \
  --serenity state/serenity-auto-assessments.json \
  --serenity-gate state/serenity-gate-results.json \
  --peer-screen state/ai-medicine-peer-screen.json \
  --output outputs/ai-medicine-5-10-year-thesis.md
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
trend-agent/.venv/bin/python scripts/build_dashboard_data.py
trend-agent/.venv/bin/python scripts/daily_data_inventory.py \
  --json-output state/daily-data-inventory.json \
  --markdown-output outputs/daily-data-inventory.md

echo "Codex Serenity review imported: $PROJECT_DIR/outputs/serenity-evidence-review.md"
echo "Dashboard refreshed: $PROJECT_DIR/dashboard/dist/index.html"
