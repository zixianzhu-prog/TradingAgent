# Serenity review prompt for newly screened companies

Paste everything below the line into Codex, opened in this repository.

---

Review the companies queued in `state/serenity-codex-queue.json` with the Serenity method.

1. Read the three skill files listed under `skillFiles` in that manifest (aleabit-research-process, aleabit-stock-selection, aleabit-chokepoint-thesis).
2. For each entry in `companies`, open its `packetPath`. Grade all eight gates in `rubric` using only the passages in that packet's `evidence` array.
3. Rules:
   - Every `support` and `counter` item must quote an exact substring (at least 20 characters) of the cited passage, with that passage's `id`. Do not paraphrase inside `quote`.
   - A gate with no supporting primary evidence stays `unknown` or `partial`. Never mark `pass` from the company name, the market-cap band or the bucket hint in `screenContext`; those are context, not evidence.
   - FDA device records prove a cleared product only, not revenue, customers or a moat.
   - Write `reason` in Chinese. List what is missing in `missing` and concrete falsifiers in `falsifiers`.
4. Copy each packet's `ticker` and `inputHash` unchanged.
5. Write one JSON file to `state/serenity-codex-queue-response.json`:

```json
{
  "generatedAt": "<ISO timestamp>",
  "reviewer": "Codex subscription",
  "reviews": [
    {"ticker": "HTFL", "inputHash": "<from packet>", "gates": {"supply_chain_map": {"status": "pass|partial|pending|unknown|fail", "reason": "...", "support": [{"id": "ev_...", "quote": "..."}], "counter": [], "missing": [], "falsifiers": []}}}
  ]
}
```

Do not edit any other file. If time is short, review the companies whose `screenContext.capBand` starts with "Sweet spot" first.
