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
   - `fail` needs a quoted, company-specific fact that contradicts the gate: a named substitute or competitor taking share, a lost or shrinking customer, a failed trial, a rejected application, a disclosed shortfall. Generic risk-factor language ("we face significant competition", "we may not achieve profitability", "we have incurred losses"), the disclaimer sentences inside FDA and registry passages, registry fields and XBRL tag names are never counter-evidence; without a specific fact the gate is `unknown` or `partial`, not `fail`.
   - A company with no approved or commercial product (a clinical-stage drug developer of any size) is expected to lose money: losses alone never fail `earnings_validation`; grade it on whether reported cash funds the next milestone.
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

Small caps: packets with a `smallCapContext` come from the under-$1B list (Peter's earlier-and-smaller direction). Its stage, revenue run rate and cash runway were computed from SEC XBRL and prices; use them as context, never as a quote. ClinicalTrials.gov passages are primary but only show that a trial exists and its phase, not results. For a company in the preparation stage (`smallCapContext.stage == "preparation"`), no revenue is expected and is never by itself a reason to fail `earnings_validation`: grade that gate on whether the reported financials show the company can fund its next milestone (cash, burn, runway at least 12 months, spending consistent with the trial plan). Mark it `fail` only with a quoted figure showing the company cannot (for example cash below a year of burn with no disclosed financing); "zero revenue" or "net loss" alone is `partial` at worst. Header or cover-page fragments (company name, dates, form type) are not evidence for or against any gate. Also for a preparation-stage company, check `counter_thesis` against the runway: under 12 months (`financingRisk: true`) means a share sale is likely and must be named as a counter-path.

Do not edit any other file. If time is short, review the small caps (`smallCapContext` present) and the companies whose `screenContext.capBand` starts with "Sweet spot" first.
