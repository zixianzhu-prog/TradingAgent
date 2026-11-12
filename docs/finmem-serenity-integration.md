# FinMem-compatible Serenity integration

This project adopts the layered-memory design described by FinMem without importing its LLM trading runtime.

- Upstream inspiration: <https://github.com/xt2201/finmem>
- Upstream license: MIT
- Local implementation: `scripts/thesis_memory_agent.py`
- Local state: `state/ai-medicine-thesis-memory.json`
- Human-readable report: `outputs/ai-medicine-thesis-memory.md`

## Why an adapter instead of a direct dependency

The upstream repository currently declares Python `>=3.10,<3.11` and its full workflows can require external market, embedding, and LLM credentials. This repository uses Python 3.11/3.12 across its active research environments. Keeping a small compatibility layer avoids dependency conflicts and preserves the local, key-optional daily pipeline.

## Serenity mapping

| FinMem idea | Serenity implementation |
|---|---|
| Short memory | Current price and five-day model context |
| Mid memory | Earnings, clinical, regulatory and filing events; affected gates |
| Long memory | Chokepoint thesis, customer dependency, valuation scenario and falsifiers |
| Reflection | Realized 1/5/20/60-day returns versus SPY, XLV and AI Medicine-specific XBI; no validity claim below sample thresholds |
| Memory citation | Stable `mem_*` IDs attached to every company research decision |

No upstream source code is copied. The design attribution is retained here and in the README.
