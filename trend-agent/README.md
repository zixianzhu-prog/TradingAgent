# Trend Agent MVP

This project is a paper-only trend intelligence monitor. It collects RSS/Atom items and
`changedetection.io` events, removes duplicates, scores configured themes, writes cited
reports, and queues high-scoring themes for deeper research.

It never connects to a brokerage account and never places an order.

## Current pipeline

```text
RSSHub / RSS / changedetection.io
                  |
                  v
        SQLite + deduplication
                  |
                  v
       deterministic theme scoring
                  |
                  v
       JSON and Markdown reports
                  |
                  v
       deep-research request queue
```

The queue is the integration point for GPT Researcher, Serenity Skills, and FinRobot.
Those external model calls are deliberately disabled in the no-key MVP.

## Run the local demo

```bash
cd trend-agent
./trend-agent init-db --database state/demo.db
./trend-agent ingest-feed \
  --file tests/fixtures/sample-feed.xml \
  --source-name example \
  --database state/demo.db
./trend-agent run \
  --config config.example.json \
  --database state/demo.db \
  --output reports/demo
```

Open `reports/demo/latest-trends.md` to inspect the result.

## Run one monitoring cycle

Edit `sources.example.json`, then run:

```bash
./trend-agent cycle \
  --sources sources.example.json \
  --config config.example.json \
  --database state/trends.db \
  --output reports/latest
```

The command fetches every enabled feed, continues when one source fails, removes duplicate
content, rescans configured themes, and writes new reports. Schedule this command with cron,
Qurio, or another workflow runner for continuous monitoring.

## Process the deep-research queue

Without a model or search API, export the next task as a transparent research brief:

```bash
./trend-agent research-next \
  --database state/trends.db \
  --output reports/research \
  --provider brief
```

After installing GPT Researcher in a separate environment and configuring its model and search
provider keys, use:

```bash
TREND_AGENT_PYTHON=/path/to/gpt-researcher-venv/bin/python \
  ./trend-agent research-next \
  --database state/trends.db \
  --output reports/research \
  --provider gpt-researcher
```

The adapter imports GPT Researcher directly instead of exposing its unauthenticated development
server. If a server deployment is needed later, keep it on localhost or place authentication and
network controls in front of it.

### Gemini setup used by this workspace

GPT Researcher 0.16.1 is installed in `../work/gpt-researcher-venv` with the optional Gemini
provider. Configure a newly generated Google AI Studio key locally; never paste it into chat or
commit it:

```bash
cd trend-agent
chmod +x setup-gemini.sh
./setup-gemini.sh
```

The generated `.env` uses Gemini Flash-Lite and DuckDuckGo so the first test does not require a
second paid search key. To process a queued research task:

```bash
set -a
. ./.env
set +a
TREND_AGENT_PYTHON=../work/gpt-researcher-venv/bin/python \
  ./trend-agent research-next \
  --database state/trends.db \
  --output reports/research \
  --provider gpt-researcher
```

## Map a trend to an investment watchlist

Company mapping is a separate evidence gate. It requires direct product, revenue, manufacturing,
or disclosed-partnership evidence and produces a research watchlist only; it cannot place orders.

```bash
./trend-agent enqueue-company-map \
  reports/research/research-1-frontier_biotech.md \
  --theme frontier_biotech \
  --database state/live-test-2.db

set -a; . ./.env; set +a
TREND_AGENT_PYTHON=../work/gpt-researcher-venv/bin/python \
  ./trend-agent research-next \
  --database state/live-test-2.db \
  --output reports/company-maps \
  --provider gpt-researcher
```

## Connect an RSSHub feed

```bash
./trend-agent ingest-feed \
  --url "http://YOUR_RSSHUB_HOST:1200/ROUTE" \
  --source-name "source-name" \
  --database state/trends.db
```

Run this command from cron or another scheduler. The fingerprint-based insert is safe to
repeat because duplicate content is ignored.

## Connect changedetection.io

Start the local webhook receiver:

```bash
./trend-agent serve-webhook --database state/trends.db --port 8787
```

Configure a JSON webhook in changedetection.io that sends fields such as `title`, `url`,
`source`, and `diff` to `http://HOST:8787/`. The receiver accepts flexible JSON payloads.

For offline testing, save a JSON payload and run:

```bash
./trend-agent ingest-change change.json --database state/trends.db
```

The wrapper uses only the Python standard library, so the MVP runs offline without a package
installation. An editable install remains available for development environments with build
dependencies already installed.

## Safety and limitations

- A high score means that a theme deserves further research. It is not a price forecast.
- Repeated articles may still share one original source. Source independence needs a later
  citation-graph stage.
- Web content is untrusted data. It must never be treated as instructions by a research model.
- Comply with source terms, robots policies, privacy rules, and applicable licenses.
- Human review is required before any financial decision.
