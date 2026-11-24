#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
AGENT_MODE=${AGENT_MODE:-collect}
case "$AGENT_MODE" in
  collect|deep) ;;
  *) echo "Unknown AGENT_MODE=$AGENT_MODE (use collect or deep)" >&2; exit 2 ;;
esac
echo "Agent mode: $AGENT_MODE (collect=no model calls except the daily Serenity re-review of changed packets; deep=all model validation)"
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
# Theory-first discovery: recent papers -> researchers/institutions/funders ->
# explicitly labelled company candidates. This layer uses public structured APIs,
# not an LLM, and cannot pass a Serenity gate by itself.
trend-agent/.venv/bin/python scripts/scientific_frontier_agent.py \
  || echo "Scientific frontier refresh failed; keeping the last saved graph"
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
# Earlier signals: Form D private raises in health/biotech, insider open-market buys, key departures (8-K 5.02).
# Insider buys and departures are written to the news store, so the re-check rule below sees them.
(cd scripts && ../trend-agent/.venv/bin/python early_signals.py --days 30)
trend-agent/.venv/bin/python scripts/management_radar.py
trend-agent/.venv/bin/python scripts/event_revalidation_agent.py \
  --config trend-agent/event-watchlist.json \
  --database trend-agent/state/daily-news.db \
  --crl state/fda-crl-reasons.json \
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
# Daily Serenity re-review with Claude Code (your Claude subscription, Sonnet by default): only covered
# companies whose evidence packet changed since their last review. Reviews are cached by packet hash,
# so an unchanged packet costs nothing. Set RUN_DAILY_SERENITY_REVIEW=0 to skip.
# Runs in collect mode too (user rule: Serenity re-review every day); cached packets cost nothing.
if [ "${RUN_DAILY_SERENITY_REVIEW:-1}" = "1" ]; then
  if PYTHONPATH=scripts python3 scripts/claude_serenity_review.py --source pending --model "${CLAUDE_REVIEW_MODEL:-sonnet}" \
       --parallel 2 --response state/serenity-claude-daily-response.json; then
    trend-agent/.venv/bin/python scripts/serenity_evidence_review.py --import-codex state/serenity-claude-daily-response.json
  else
    echo "Daily Serenity re-review: nothing changed or review failed; keeping previous verdicts"
  fi
  # Memo companies: re-grade management_governance when the management radar shows new SEC events
  # (8-K Item 5.02, Form 4). Unchanged event lists cost nothing (exit 3).
  if PYTHONPATH=scripts python3 scripts/claude_management_review.py --model "${CLAUDE_REVIEW_MODEL:-sonnet}"; then
    PYTHONPATH=scripts python3 scripts/prepare_claude_review.py >/dev/null \
      && ./scripts/finalize_codex_serenity.sh state/serenity-claude-response.json
  else
    echo "Management gate review: no new SEC management events or review failed; keeping memo verdicts"
  fi
fi
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
if [ "$AGENT_MODE" = "deep" ] && [ "${RUN_TRADINGAGENTS_FULL_REVIEW:-1}" = "1" ]; then
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
# Exit multiples with a source: Damodaran industry P/S (bear), AI-medicine peer median (base), peer top quartile (bull).
PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/calibrate_multiples.py
# Growth with a source: the company's own reported growth fading to Damodaran industry rates (SEC XBRL needs SEC_USER_AGENT).
PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/calibrate_growth.py
trend-agent/.venv/bin/python scripts/build_financial_scenarios.py \
  --financials trend-agent/ai-medicine-financials.json \
  --multiples state/multiple-calibration.json \
  --growth state/growth-calibration.json \
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
  # IND clearances and big-pharma deals from 8-K press releases (facts extracted by Claude Code on your
  # Claude subscription, cached per filing). Feeds the small-cap list below as a second candidate source.
  if [ "$AGENT_MODE" = "deep" ]; then
    PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/pharma_deals_ind.py --days 90 --parallel 3 --model "${CLAUDE_EXTRACT_MODEL:-sonnet}" \
      || echo "IND/deal tracker failed; small-cap list uses the last saved result"
  else
    PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/pharma_deals_ind.py --days 90 --no-extract \
      || echo "IND/deal search failed; small-cap list uses the last saved result"
  fi
  # Peter's earlier-and-smaller direction: AI-medicine companies under $1B, tagged preparation / growth / slowing.
  PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/small_cap_stage.py
  # Weekly: money raised by listed companies (XBRL equity proceeds) and papers each company publishes (OpenAlex);
  # both feed the lab-to-company chain. No model calls.
  PYTHONPATH=scripts python3 scripts/equity_raises.py || echo "Equity-raise check failed; keeping the last result"
  PYTHONPATH=scripts python3 scripts/company_research.py || echo "Company research lookup failed; keeping the last result"
  # Key people: officer titles from SEC Forms 3/4/5, founders from 10-Ks, their PubMed papers; LinkedIn linked, never fetched.
  PYTHONPATH=scripts python3 scripts/key_people.py || echo "Key-people tracker failed; keeping the last result"
  # Weekly: replay the order rule on 2014+ 10-K filings (deterministic; outputs/order-rule-backtest.md).
  PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/backtest_order_rule.py \
    || echo "Order-rule backtest failed; keeping the last result"
  # Same rules on health-care companies outside that sample (state/serenity-source-cache/xbrl-oos, scripts/backtest_universe.py).
  PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/backtest_order_rule.py --xbrl-dir state/serenity-source-cache/xbrl-oos \
    --state state/order-rule-backtest-oos.json --report outputs/order-rule-backtest-oos.md --label out-of-sample \
    || echo "Out-of-sample backtest failed; keeping the last result"
  # Patient counts from 10-Ks for rNPV peak sales: only companies without an entry in trend-agent/rnpv-overrides.json
  # (Claude Code on your subscription, Sonnet; deep mode only).
  if [ "$AGENT_MODE" = "deep" ]; then
    PYTHONPATH=scripts python3 scripts/rnpv_patients.py --model "${CLAUDE_EXTRACT_MODEL:-sonnet}" \
      || echo "rNPV patient extraction failed; keeping existing overrides"
    # Who sells the lead drug: a partner (company earns royalties) or the company itself. Only unchecked companies.
    PYTHONPATH=scripts python3 scripts/rnpv_patients.py --economics --model "${CLAUDE_EXTRACT_MODEL:-sonnet}" \
      || echo "Partner-economics check failed; keeping existing overrides"
    # Founders and university/institute licenses quoted from 10-Ks (cached per filing).
    PYTHONPATH=scripts python3 scripts/science_founders.py --model "${CLAUDE_EXTRACT_MODEL:-sonnet}" \
      || echo "Founder/licensor extraction failed; keeping the last links"
    # Opus argues against the memos behind live tickets (cached on unchanged evidence); a verified hard-gate fail makes the ticket wait.
    PYTHONPATH=scripts python3 scripts/claude_adversarial_review.py --model "${CLAUDE_ADVERSARIAL_MODEL:-opus}" \
      || echo "Adversarial review failed; keeping the last result"
  fi
  # Upstream bottleneck map and Serenity evidence packets for newly shortlisted names.
  PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/ai_medicine_chokepoints.py
  PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/prepare_serenity_queue.py
  # Optional: review newly queued small caps with Claude Code (your Claude subscription) when the
  # ChatGPT/Codex allowance is used up. Off by default; set RUN_CLAUDE_SERENITY_REVIEW=1 to enable.
  if [ "$AGENT_MODE" = "deep" ] && [ "${RUN_CLAUDE_SERENITY_REVIEW:-0}" = "1" ]; then
    PYTHONPATH=scripts python3 scripts/claude_serenity_review.py --source small-cap --model "${CLAUDE_REVIEW_MODEL:-sonnet}" \
      && ./scripts/finalize_codex_serenity.sh state/serenity-claude-queue-response.json
  fi
  # Which companies' filings describe each AI-medicine topic (frontier news -> company mapping).
  PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/topic_exposure.py
  # Check the mapping against FDA's AI-device makers (recall) and the filing text (precision).
  (cd scripts && ../trend-agent/.venv/bin/python validate_topic_mapping.py --cache-only)
  # FDA complete response letters: why applications were not approved, in FDA's words, with the sponsor's 8-K alongside.
  PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/fda_crl_reasons.py --compare 25
fi
# Extract explicit founder, patent and license claims from saved SEC evidence.
# Generic patent-risk boilerplate is deliberately ignored.
PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/technology_ownership_agent.py
PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/uspto_assignment_validation.py
PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/institutional_ownership_agent.py
# Biodefense: ASPR/BARDA contract actions (USAspending) and WHO outbreak reports; no model calls.
PYTHONPATH=scripts python3 scripts/biodefense_radar.py || echo "Biodefense radar failed; keeping the last result"
# Join papers, researchers, ownership evidence, financing, pharma payments,
# clinical progress and SEC revenue into one auditable company-level chain.
# Missing ownership evidence stays explicit and never becomes a positive score.
PYTHONPATH=scripts trend-agent/.venv/bin/python scripts/science_commercialization_graph.py
# News-driven recommendations, step 2: recompute with today's Serenity gate results.
trend-agent/.venv/bin/python scripts/news_signal_engine.py
# Which Serenity reviews match today's evidence, and which Claude memos are still unchecked.
trend-agent/.venv/bin/python scripts/serenity_review_status.py
trend-agent/.venv/bin/python scripts/build_top5_brief.py
# rNPV order ranges for drug developers with no revenue (deterministic; uses the ranking just built).
PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/rnpv_valuation.py \
  || echo "rNPV valuation failed; keeping the last saved ranges"
python3 scripts/translate_page.py  # Chinese copy: dashboard/dist/top5.zh.html
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
python3 scripts/translate_page.py  # Chinese copy: dashboard/dist/top5.zh.html
# Order tickets (research suggestions, paper only): action, limit, size, scale plan, invalidation per company.
PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/order_tickets.py
# Hard filter before deep review: AI as product, hard evidence, tradability, survival; deep-review queue of up to 15.
# Sonnet reads new 10-Ks only in deep mode; otherwise cached AI judgments are reused.
if [ "$AGENT_MODE" = "deep" ]; then
  PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/candidate_filter.py --model "${CLAUDE_EXTRACT_MODEL:-sonnet}" \
    || echo "Candidate filter failed; keeping the last result"
else
  PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/candidate_filter.py --no-model || echo "Candidate filter failed; keeping the last result"
fi
# Forward record: freeze today's tickets (append-only, committed) and score earlier calls against XBI.
PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/ticket_ledger.py || echo "ticket ledger skipped"
# Rebuild the page so it shows today's tickets (they are computed from the ranking the first build wrote).
trend-agent/.venv/bin/python scripts/build_top5_brief.py
python3 scripts/translate_page.py
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
echo "Management radar: $PROJECT_DIR/outputs/management-radar.md"
echo "AI Medicine evidence graph: $PROJECT_DIR/outputs/ai-medicine-evidence-graph.md"
echo "SEC XBRL validation: $PROJECT_DIR/outputs/sec-xbrl-validation.md"
echo "Scientific frontier graph: $PROJECT_DIR/outputs/scientific-frontier.md"
echo "Science-to-commercialization graph: $PROJECT_DIR/outputs/science-commercialization-graph.md"
echo "Technology ownership evidence: $PROJECT_DIR/outputs/technology-ownership.md"
echo "USPTO assignment validation: $PROJECT_DIR/outputs/uspto-assignment-validation.md"
echo "SEC 13D/13G ownership radar: $PROJECT_DIR/outputs/institutional-ownership.md"
echo "Dashboard: $PROJECT_DIR/dashboard/dist/index.html"
echo "Daily data inventory: $PROJECT_DIR/outputs/daily-data-inventory.md"
