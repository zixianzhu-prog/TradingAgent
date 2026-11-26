"""Risk-adjusted NPV (rNPV) order ranges for drug developers that have no revenue to model.

The 5-year scenario model needs sales, so pre-revenue drug developers got "no valuation range".
This gives them one, and also states what today's price assumes, so the range can be argued with.

Method (deterministic, no model calls):
* Lead asset = the company's highest-phase own trial (ClinicalTrials.gov, cached by small_cap_stage).
* Probability of approval and phase durations: BIO / Informa Pharma Intelligence / QLS,
  "Clinical Development Success Rates 2011-2020" (2021), all indications.
* Sales ramp linearly to peak over 5 years after launch, hold to year 10, then fall 50% a year
  (loss of exclusivity); 40% operating margin, 21% tax; nothing after year 15.
* Development spend = today's cash burn, paid only while the program is still alive
  (each phase's burn weighted by the chance of reaching that phase).
* Discount rate = the 12% policy return, so a price at or below the base value meets the policy.
* Peak sales are the one input filings do not give. Bear/base/bull defaults are unverified analyst
  priors (inputsVerified false); trend-agent/rnpv-overrides.json replaces them per company with a source.

    ai-fund-lab/.venv/bin/python scripts/rnpv_valuation.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SMALL = ROOT / "state/small-cap-stage.json"
FINANCIALS = ROOT / "trend-agent/ai-medicine-financials.json"
OVERRIDES = ROOT / "trend-agent/rnpv-overrides.json"
OUT = ROOT / "state/rnpv-valuations.json"
REPORT = ROOT / "outputs/rnpv-valuations.md"

SOURCE = "BIO, Informa Pharma Intelligence & QLS, Clinical Development Success Rates 2011-2020 (2021)"
# Chance of moving to the next stage, and years spent in each stage (4 = NDA/BLA review).
TRANSITION = {1: 0.520, 2: 0.289, 3: 0.578, 4: 0.906}
DURATION = {1: 2.3, 2: 3.6, 3: 3.3, 4: 1.3}
PEAK_PRIORS_M = {"bear": 150.0, "base": 500.0, "bull": 1500.0}
DISCOUNT, MARGIN, TAX, RAMP, PLATEAU_END, LIFE = 0.12, 0.40, 0.21, 5, 10, 15
DRUG_SEGMENTS = ("Drug developer", "Drug discovery")


def approval_odds(phase: int) -> float:
    """Likelihood of approval from the current phase (product of the remaining transitions)."""
    p = 1.0
    for k in range(phase, 5):
        p *= TRANSITION[k]
    return p


def years_to_launch(phase: int) -> float:
    """Assume the company is halfway through its current phase."""
    return DURATION[phase] / 2 + sum(DURATION[k] for k in range(phase + 1, 5))


def sales_curve(peak: float) -> list[float]:
    out = []
    for year in range(1, LIFE + 1):
        if year <= RAMP:
            out.append(peak * year / RAMP)
        elif year <= PLATEAU_END:
            out.append(peak)
        else:
            out.append(out[-1] * 0.5)
    return out


def value_per_peak_dollar(phase: int, rate: float = DISCOUNT, margin: float = MARGIN, years: int = LIFE) -> float:
    """Risk-adjusted present value of $1 of peak sales: rNPV is linear in peak sales.
    margin is the company's share of each sales dollar before tax: its operating margin when it sells the drug
    itself, or the royalty rate when a partner sells it; years caps the sales life (e.g. a royalty end date)."""
    launch = years_to_launch(phase)
    after_tax = margin * (1 - TAX)
    pv = sum(s * after_tax / (1 + rate) ** (launch + t) for t, s in enumerate(sales_curve(1.0), start=1) if t <= years)
    return approval_odds(phase) * pv


def economics_of(o: dict, phase: int) -> tuple[float, int]:
    """(share of sales, sales years) from an override's partner economics, else the self-commercialized default."""
    e = o.get("economics") or {}
    if e.get("type") != "royalty" or not e.get("rate"):
        return MARGIN, LIFE
    years = LIFE
    if e.get("endYear"):
        launch_year = datetime.now().year + years_to_launch(phase)
        years = max(0, min(LIFE, int(e["endYear"] - launch_year)))
    return float(e["rate"]), years


def development_cost_pv(phase: int, burn_per_year: float, rate: float = DISCOUNT) -> float:
    """Burn until launch; each stage's spend is paid only if the program got that far."""
    pv, t, reach = 0.0, 0.0, 1.0
    for k in range(phase, 5):
        years = DURATION[k] / 2 if k == phase else DURATION[k]
        # Mid-point discounting of the stage's spend.
        pv += reach * burn_per_year * years / (1 + rate) ** (t + years / 2)
        t += years
        reach *= TRANSITION[k]
    return pv


def override_peaks(o: dict) -> dict[str, float] | None:
    """Bottom-up peak sales: patients (quoted from the company's own filing) x penetration x yearly net price.
    Penetration and price are analyst assumptions and stay labelled as such."""
    patients, price, pen = (o.get("patients") or {}).get("value"), o.get("netPricePerYearUsd"), o.get("penetration")
    if not (patients and price and pen):
        return None
    # A one-time therapy (gene editing, cell therapy) is paid once per patient: the penetrated pool is treated
    # over the 10 years of sales, so yearly sales are a tenth of pool x price.
    years = 10 if o.get("oneTimeTherapy") else 1
    return {k: round(patients * pen[k] * price / years / 1e6, 1) for k in ("bear", "base", "bull")}


def patients_text(n: float) -> str:
    return f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n:,.0f}"


def implied_share_text(row: dict) -> str | None:
    """Today's price restated as a share of the patients quoted from the 10-K, at the assumed price."""
    basis, implied = row.get("peakBasis"), row.get("impliedPeakSalesM")
    if not basis or not implied or implied <= 0:
        return None
    patients, price = basis["patients"]["value"], basis["netPricePerYearUsd"]
    years = 10 if basis.get("oneTimeTherapy") else 1
    share = implied * 1e6 * years / (patients * price)
    unit = "once (one-time therapy)" if years > 1 else "a year"
    return f"today's price implies {share:.1%} of {patients_text(patients)} patients at ${price:,.0f} {unit}"


def value(company: dict, peaks: dict[str, float], economics: tuple[float, int] = (MARGIN, LIFE)) -> dict:
    phase = int(company["phase"])
    k = value_per_peak_dollar(phase, margin=economics[0], years=economics[1])
    cost = development_cost_pv(phase, company["burnPerYearM"])
    cash, shares = company["cashM"], company["sharesM"]
    cases = {name: round(max(0.0, cash - cost + k * peak) / shares, 2) for name, peak in peaks.items()}
    implied = (company["marketCapM"] - cash + cost) / k if k else None
    upper = cases["base"]
    floor = min(cases["bear"], upper)
    price = company["price"]
    status = ("below-floor" if price <= floor else "in-range" if price <= upper
              else "at-top" if upper and price / upper - 1 < 0.01 else "above")
    return {
        "approvalOdds": round(approval_odds(phase), 3), "yearsToLaunch": round(years_to_launch(phase), 1),
        "developmentCostPvM": round(cost, 1), "valuePerPeakDollar": round(k, 4),
        "peakSalesM": peaks, "valuePerShare": cases,
        "impliedPeakSalesM": round(implied, 0) if implied is not None else None,
        "orderRange": {"price": price, "upper": upper, "floor": floor, "status": status, "method": "rNPV",
                       "gapToUpper": round(price / upper - 1, 3) if upper else None},
    }


DEAD = {"TERMINATED", "WITHDRAWN", "SUSPENDED"}
ACTIVE = {"RECRUITING", "ACTIVE_NOT_RECRUITING", "NOT_YET_RECRUITING", "ENROLLING_BY_INVITATION"}


def lead_trial(company: str) -> dict | None:
    """Highest-phase own trial (last 6 years) that is still alive: terminated, withdrawn or suspended trials
    do not count, so a stopped phase 3 no longer earns phase-3 approval odds. Phase 4 (post-approval) is ignored."""
    import re
    import small_cap_stage as scs
    query = scs.sponsor_query(company)
    path = scs.TRIALS_CACHE / (re.sub(r"[^A-Za-z0-9]+", "-", query).strip("-").lower() + ".json")
    if not path.exists():
        return None
    key = query.lower().split()[0]
    best = None
    for st in json.loads(path.read_text(encoding="utf-8")):
        p = st.get("protocolSection", {})
        sponsor = p.get("sponsorCollaboratorsModule", {}).get("leadSponsor", {}).get("name", "")
        status = p.get("statusModule", {}).get("overallStatus", "")
        start = (p.get("statusModule", {}).get("startDateStruct") or {}).get("date", "")
        phases = [{"EARLY_PHASE1": 1, "PHASE1": 1, "PHASE2": 2, "PHASE3": 3}.get(x) for x in p.get("designModule", {}).get("phases", [])]
        phases = [x for x in phases if x]
        if key not in sponsor.lower() or status in DEAD or not phases or start[:4] < str(datetime.now().year - 6):
            continue
        trial = {"nct": p["identificationModule"]["nctId"], "title": p["identificationModule"].get("briefTitle", ""),
                 "phase": max(phases), "status": status, "start": start}
        rank = (trial["phase"], status in ACTIVE, start)
        if best is None or rank > best[0]:
            best = (rank, trial)
    return best[1] if best else None


def inputs(root: Path = ROOT) -> list[dict]:
    """Drug developers from the small-cap screen, plus covered companies with a clinical lead asset."""
    small = json.loads((root / "state/small-cap-stage.json").read_text(encoding="utf-8")).get("companies", [])
    out = []
    for r in small:
        if r.get("segment") not in DRUG_SEGMENTS:
            continue
        row = {"ticker": r["ticker"], "company": r["company"], "price": r.get("price"), "marketCapM": r.get("marketCapM"),
               "sharesM": r.get("sharesM"), "cashM": r.get("cashM"), "burnPerYearM": (r.get("burnPerMonthM") or 0) * 12,
               "revenueM": r.get("revenueRunRateM"), "phase": (r.get("clinical") or {}).get("highestPhase"),
               "lead": ((r.get("clinical") or {}).get("examples") or [{}])[0],
               "platform": r.get("segment") == "Drug discovery"}
        live = lead_trial(r["company"])
        row["phase"], row["lead"] = (live["phase"], live) if live else (None, {})
        out.append(row)
    return out


def covered_inputs(tickers: dict[str, str], fetch: bool = True) -> list[dict]:
    """Covered companies (5-year scenario file) that lack a scenario model: look up their lead trial."""
    import small_cap_stage as scs
    fin = json.loads(FINANCIALS.read_text(encoding="utf-8"))
    rows = fin["companies"] if isinstance(fin["companies"], list) else list(fin["companies"].values())
    out = []
    for r in rows:
        if r["ticker"] not in tickers:
            continue
        clinical = scs.clinical_stage(tickers[r["ticker"]], fetch)
        burn = max(0.0, -(r.get("quarterly_net_income_m") or 0)) * 4
        out.append({"ticker": r["ticker"], "company": tickers[r["ticker"]], "price": r["price"],
                    "marketCapM": round(r["price"] * r["shares"] / 1e6), "sharesM": r["shares"] / 1e6,
                    "cashM": r.get("cash_and_securities_m"), "burnPerYearM": burn,
                    "revenueM": (r.get("quarterly_revenue_m") or 0) * 4, "phase": clinical.get("highestPhase"),
                    "lead": lead_trial(tickers[r["ticker"]]) or {}, "platform": True})
        out[-1]["phase"] = out[-1]["lead"].get("phase")
    return out


def build(companies: list[dict], overrides: dict) -> dict:
    rows, skipped = [], []
    for c in companies:
        missing = [k for k in ("price", "sharesM", "cashM", "marketCapM") if not c.get(k)]
        if not c.get("phase"):
            skipped.append({"ticker": c["ticker"], "reason": "no live own clinical trial (none, or all terminated): rNPV needs a clinical asset"})
            continue
        if missing:
            skipped.append({"ticker": c["ticker"], "reason": "missing " + ", ".join(missing)})
            continue
        o = overrides.get(c["ticker"], {})
        peaks = override_peaks(o) or {k: float(o.get("peakSalesM", {}).get(k, v)) for k, v in PEAK_PRIORS_M.items()}
        row = {**{k: c[k] for k in ("ticker", "company", "price", "marketCapM", "sharesM", "cashM", "burnPerYearM", "phase")},
               "leadTrial": c.get("lead") or {}, **value(c, peaks, economics_of(o, int(c["phase"]))),
               "economics": o.get("economics") or {"type": "self-commercialized", "operatingMargin": MARGIN},
               "inputsVerified": bool(o.get("source")) and not o.get("penetration"),
               "peakSource": o.get("source") or "analyst prior (unverified)",
               "asset": o.get("asset"), "evidence": o.get("evidence", []), "peakBasis": o.get("patients") and {
                   "patients": o["patients"], "netPricePerYearUsd": o.get("netPricePerYearUsd"),
                   "penetration": o.get("penetration"), "assumptions": o.get("assumptions"),
                   "oneTimeTherapy": bool(o.get("oneTimeTherapy"))}}
        notes = []
        # A discovery platform runs many programs (often partnered); valuing only its lead asset understates it,
        # so its range is shown for reference but never used for an order.
        row["platform"] = bool(c.get("platform"))
        row["rangeUsable"] = not row["platform"]
        if row["platform"]:
            notes.append("discovery platform: one-asset rNPV understates it, range not used for orders")
        if (c.get("revenueM") or 0) > 0.25 * c["marketCapM"]:
            notes.append(f"existing revenue ${c['revenueM']:.0f}M a year is not in the model")
        lead = c.get("lead") or {}
        if lead.get("status") == "COMPLETED":
            notes.append(f"lead trial {lead.get('nct')} is completed: check its result before using the range")
        months = c["cashM"] / (c["burnPerYearM"] / 12) if c.get("burnPerYearM") else None
        if months is not None and months < 12:
            notes.append(f"cash lasts about {months:.0f} months: a share sale is near, expect dilution")
        if months is not None and months < 6:
            # The financing terms, not the drug, set the next price: wait until the raise is done.
            row["rangeUsable"] = False
            notes.append("range not used for orders until the company has raised money")
        econ = o.get("economics") or {}
        if econ.get("type") == "royalty":
            notes.append(f"lead asset is partnered: {econ['rate']:.0%} royalty"
                         + (f" until {econ['endYear']}" if econ.get("endYear") else "") + "; the company's own other programs are not valued")
        line = implied_share_text(row)
        if line:
            notes.append(line)
        notes += [e["quote"] for e in row.get("evidence", [])[:1]]
        row["notes"] = notes
        rows.append(row)
    rows.sort(key=lambda r: (-(r["phase"] or 0), r["ticker"]))
    return {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "source": SOURCE,
            "assumptions": {"discountRate": DISCOUNT, "operatingMargin": MARGIN, "tax": TAX, "rampYears": RAMP,
                            "plateauEndYear": PLATEAU_END, "lifeYears": LIFE, "peakPriorsM": PEAK_PRIORS_M,
                            "transition": TRANSITION, "durationYears": DURATION},
            "companies": rows, "skipped": skipped}


def report(payload: dict) -> str:
    lines = ["# rNPV 下单区间（无收入的药物开发公司）", "",
             f"生成时间：{payload['generatedAt']}。成功率与阶段时长：{payload['source']}。",
             "峰值销售是未核实的分析师先验（熊 150 / 基准 500 / 牛 1500 百万美元），除非标注了来源；“现价隐含峰值销售”是反推结果，用来判断市场假设是否合理。", "",
             "| 代码 | 阶段 | 获批概率 | 距上市(年) | 现价 | 下单上限 | 安全底线 | 状态 | 现价隐含峰值销售 | 备注 |",
             "|---|---:|---:|---:|---:|---:|---:|---|---:|---|"]
    for r in payload["companies"]:
        o = r["orderRange"]
        lines.append(f"| {r['ticker']} | {r['phase']} | {r['approvalOdds']:.0%} | {r['yearsToLaunch']} | ${o['price']:.2f} | "
                     f"${o['upper']:.2f} | ${o['floor']:.2f} | {o['status']} | ${r['impliedPeakSalesM']:,.0f}M | {'；'.join(r['notes'])} |")
    lines += ["", "只有单一管线的药物开发公司（rangeUsable）用这个区间下单；平台型公司只看“现价隐含峰值销售”。"]
    if payload["skipped"]:
        lines += ["", "未估值：" + "；".join(f"{s['ticker']}（{s['reason']}）" for s in payload["skipped"])]
    return "\n".join(lines) + "\n"


def main() -> None:
    overrides = json.loads(OVERRIDES.read_text(encoding="utf-8")).get("companies", {}) if OVERRIDES.exists() else {}
    # Covered drug-discovery/development companies whose 5-year scenario model is missing (needs revenue).
    scenarios = json.loads((ROOT / "state/ai-medicine-financial-scenarios.json").read_text(encoding="utf-8"))["companies"]
    modeled = {r["ticker"] for r in scenarios if (r.get("scenario_model") or {}).get("cases")}
    ranking = json.loads((ROOT / "state/ai-medicine-top5.json").read_text(encoding="utf-8")).get("ranking", [])
    need = {r["ticker"]: r["company"] for r in ranking
            if r["ticker"] not in modeled and any(w in (r.get("segment") or "") for w in ("drug discovery", "antibody discovery"))}
    # The deep-review queue's drug-discovery companies get the same treatment (their counter-thesis gate needs a valuation).
    flt = json.loads((ROOT / "state/candidate-filter.json").read_text(encoding="utf-8")) if (ROOT / "state/candidate-filter.json").exists() else {}
    small_tickers = {r["ticker"] for r in json.loads(SMALL.read_text(encoding="utf-8")).get("companies", [])} if SMALL.exists() else set()
    for t in flt.get("deepReview", []):
        c = (flt.get("companies") or {}).get(t) or {}
        if t not in modeled and t not in small_tickers and c.get("segment") in DRUG_SEGMENTS:
            need.setdefault(t, c.get("company") or t)
    payload = build(inputs() + covered_inputs(need), overrides)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(report(payload), encoding="utf-8")
    print(json.dumps({"valued": len(payload["companies"]), "skipped": len(payload["skipped"])}))


if __name__ == "__main__":
    main()
