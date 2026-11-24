"""Join scientific discovery to commercial validation without inventing missing links."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def norm(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").lower())


def evidence(source: str, url: str | None, quote: str | None, relation: str, verified: bool, **extra) -> dict:
    return {"source": source, "url": url, "quote": quote, "relation": relation,
            "verified": bool(verified and quote), **extra}


def aliases(companies: list[dict]) -> dict[str, set[str]]:
    out = {}
    for row in companies:
        ticker = row.get("ticker")
        if not ticker:
            continue
        names = {norm(ticker), norm(row.get("company"))}
        names |= {norm(x) for x in re.split(r"[/(),]", row.get("company") or "") if len(norm(x)) >= 4}
        out[ticker] = {x for x in names if x}
    return out


def name_matches(name: str | None, candidates: set[str]) -> bool:
    n = norm(name)
    return bool(n and any((len(a) >= 4 and (a in n or n in a)) for a in candidates))


def verified_fact(row: dict, key: str) -> dict | None:
    fact = (row.get("facts") or {}).get(key)
    return fact if isinstance(fact, dict) and fact.get("verified") and fact.get("quote") else None


def build(frontier: dict, company_rows: list[dict], pharma: dict, clinical: dict, funding: dict,
          financials: dict, xbrl: dict, manual: dict, ownership: dict | None = None,
          uspto: dict | None = None, institutional: dict | None = None, raises: dict | None = None,
          research: dict | None = None) -> dict:
    company_by_ticker = {r["ticker"]: r for r in company_rows if r.get("ticker")}
    company_aliases = aliases(company_rows)
    records = {ticker: {"ticker": ticker, "company": row.get("company"), "discovery": [],
                        "researcherCompanyRelation": [], "technologyOwnership": [],
                        "funding": [], "institutionalOwnership": [], "pharmaValidation": [], "clinicalValidation": [], "revenueValidation": [],
                        "gaps": []} for ticker, row in company_by_ticker.items()}

    for work in frontier.get("works", []):
        for link in work.get("companyLinks", []):
            ticker = link.get("ticker")
            if ticker not in records:
                continue
            direct = link.get("relation") == "direct_mention"
            records[ticker]["discovery"].append(evidence(
                "OpenAlex", work.get("doi") or work.get("id"), work.get("title"),
                "paper_direct_mention" if direct else "technology_overlap_candidate", direct,
                publishedAt=work.get("publishedAt"), evidenceTerms=link.get("evidence", [])))
        for author in work.get("authors", []):
            for inst in author.get("institutions", []):
                for ticker, names in company_aliases.items():
                    if name_matches(inst.get("name"), names):
                        records[ticker]["researcherCompanyRelation"].append(evidence(
                            "OpenAlex author affiliation", work.get("doi") or work.get("id"),
                            f"{author.get('name')} is affiliated with {inst.get('name')} on {work.get('title')}",
                            "researcher_company_affiliation", True, person=author.get("name"),
                            institution=inst.get("name"), publishedAt=work.get("publishedAt")))

    for link in manual.get("links", []):
        ticker = link.get("ticker")
        if ticker not in records:
            continue
        # Sponsored research is the company paying a lab: a research relationship, not money raised.
        bucket = ("researcherCompanyRelation" if link.get("relation") in {"founder", "sponsored_research", "academic_affiliation"} else
                  "technologyOwnership" if link.get("relation") in {"inventor", "patent_assignee", "license"} else "funding")
        records[ticker][bucket].append(evidence(link.get("sourceType", "primary source"), link.get("url"),
                                               link.get("quote"), link.get("relation", "manual_verified_link"),
                                               link.get("status") == "verified"))

    for company in (ownership or {}).get("companies", []):
        ticker = company.get("ticker")
        if ticker not in records:
            continue
        for item in company.get("evidence", []):
            bucket = "researcherCompanyRelation" if item.get("relation") == "founder_company" else "technologyOwnership"
            records[ticker][bucket].append(evidence(
                item.get("source", "SEC filing"), item.get("url"), item.get("quote"), item.get("relation"),
                item.get("status") == "company-disclosed", evidenceId=item.get("evidenceId"),
                independentAssignmentVerified=False, scopeNote=item.get("scopeNote")))

    for company in (uspto or {}).get("companies", []):
        ticker = company.get("ticker")
        if ticker not in records:
            continue
        for item in company.get("officialAssignments", []):
            if not item.get("independentAssignmentVerified"):
                continue
            quote = (f"USPTO recorded assignment {item.get('reelFrame') or 'record'} from "
                     f"{item.get('assignor') or 'unlisted assignor'} to {item.get('assignee')} on {item.get('recordedAt')}")
            records[ticker]["technologyOwnership"].append(evidence(
                "USPTO Assignment Center", item.get("url"), quote, "uspto_assignment", True,
                independentAssignmentVerified=True, reelFrame=item.get("reelFrame"), recordedAt=item.get("recordedAt")))

    for filing in pharma.get("filings", []) + pharma.get("history", []):  # history: confirmed events older than the window
        ticker = filing.get("ticker")
        if ticker not in records:
            continue
        is_new_deal = (filing.get("facts") or {}).get("isNewDeal")
        if filing.get("kind") == "deal" and (is_new_deal is True or
                                               (isinstance(is_new_deal, dict) and is_new_deal.get("value") is True)):
            partner, upfront, milestone = (verified_fact(filing, key) for key in ("partner", "upfrontUsdM", "milestonesUsdM"))
            anchor = partner or upfront or milestone
            records[ticker]["pharmaValidation"].append(evidence(
                "SEC 8-K exhibit", filing.get("url"), anchor.get("quote") if anchor else None,
                "pharma_paid_or_contracted", True, partner=(partner or {}).get("value"),
                upfrontUsdM=(upfront or {}).get("value"), milestonesUsdM=(milestone or {}).get("value"),
                filed=filing.get("filed"), revenueProof=False))
        is_ind = (filing.get("facts") or {}).get("isIndClearance")
        if filing.get("kind") == "ind" and (is_ind is True or
                                              (isinstance(is_ind, dict) and is_ind.get("value") is True)):
            drug = verified_fact(filing, "drug")
            records[ticker]["clinicalValidation"].append(evidence(
                "SEC 8-K exhibit", filing.get("url"), drug.get("quote") if drug else None,
                "ind_clearance", True, drug=(drug or {}).get("value"), filed=filing.get("filed")))

    for study in clinical.get("studies", []):
        ticker = study.get("ticker")
        if ticker in records:
            quote = f"{study.get('title')} — status {study.get('status')}; lead sponsor {study.get('leadSponsor')}"
            records[ticker]["clinicalValidation"].append(evidence(
                "ClinicalTrials.gov", study.get("url"), quote, "registered_clinical_trial", True,
                nctId=study.get("nctId"), phase=study.get("phases"), status=study.get("status")))

    funding_companies = (funding.get("fundingRadar") or {}).get("companies", [])
    for row in funding_companies:
        ticker = row.get("listedTicker")
        if ticker not in records:
            ticker = next((t for t, names in company_aliases.items() if name_matches(row.get("name"), names)), None)
        if ticker in records and row.get("sold"):
            records[ticker]["funding"].append(evidence(
                "SEC Form D", row.get("url"), f"{row.get('name')} reported ${row.get('sold'):,.0f} sold in this offering",
                "form_d_financing", True, soldUsd=row.get("sold"), filed=row.get("filed"), investorIdentityVerified=False))

    # Papers the company's own scientists publish (scripts/company_research.py): the company does science
    # that reaches the literature, and its authors tie researchers to it. It does not prove a paper became a product.
    for ticker, row in (research or {}).get("companies", {}).items():
        if ticker not in records or not row.get("verified"):
            continue
        top = (row.get("topWorks") or [{}])[0]
        records[ticker]["discovery"].append(evidence(
            "OpenAlex company institution", top.get("doi") or top.get("id") or row.get("openalexId"),
            f"{row['recentWorks']} papers since {row['worksSince']} list {row['institution']} as an author institution; "
            f"most cited: {top.get('title')}", "company_authored_research", True, works=row["recentWorks"],
            openalexInstitution=row.get("openalexId")))
        if top.get("companyAuthors"):
            records[ticker]["researcherCompanyRelation"].append(evidence(
                "OpenAlex author affiliation", top.get("doi") or top.get("id"),
                f"{', '.join(top['companyAuthors'])} affiliated with {row['institution']} on {top.get('title')}",
                "researcher_company_affiliation", True, person=top["companyAuthors"][0], institution=row["institution"]))

    # Listed companies raise through offerings, ATMs and PIPEs that never file a Form D; the cash-flow statement
    # shows the money that came in (scripts/equity_raises.py).
    for ticker, row in (raises or {}).get("companies", {}).items():
        if ticker in records and row.get("totalUsdM", 0) >= 5:
            spans = "; ".join(f"{p['start']} to {p['end']}: ${p['usdM']:,.1f}M ({p['form']})" for p in row["periods"])
            records[ticker]["funding"].append(evidence(
                "SEC XBRL", row["periods"][-1].get("url"), f"Cash received from issuing equity (XBRL {row['periods'][-1]['tag']}): {spans}",
                "equity_raise", True, raisedUsdM=row["totalUsdM"], investorIdentityVerified=False))

    for filing in (institutional or {}).get("filings", []):
        ticker = filing.get("ticker")
        if ticker in records and filing.get("reportingPerson"):
            records[ticker]["institutionalOwnership"].append(evidence(
                "SEC beneficial ownership filing", filing.get("url"), filing.get("quote"),
                "schedule_13d" if "13D" in filing.get("form", "") else "schedule_13g", True,
                reportingPerson=filing.get("reportingPerson"), percent=filing.get("percent"),
                intentClass=filing.get("intentClass"), newCompanyFinancing=False))

    xbrl_by_ticker = {r.get("ticker"): r for r in xbrl.get("companies", [])}
    for row in financials.get("companies", []):
        ticker = row.get("ticker")
        official = xbrl_by_ticker.get(ticker, {})
        revenue_check = next((c for c in official.get("checks", []) if c.get("metric") == "quarterly_revenue_m" and c.get("status") == "pass"), None)
        if ticker in records and revenue_check:
            quote = (f"SEC XBRL {revenue_check.get('tag')} reported quarterly revenue of "
                     f"${revenue_check.get('official')}M for period ending {revenue_check.get('periodEnd')}")
            records[ticker]["revenueValidation"].append(evidence(
                "SEC XBRL", official.get("source"), quote, "reported_company_revenue", True,
                quarterlyRevenueM=revenue_check.get("official"), periodEnd=revenue_check.get("periodEnd"),
                aiSpecificRevenue=False))

    nodes, edges = {}, []
    ordered = []
    for ticker, row in records.items():
        stage_keys = ("discovery", "researcherCompanyRelation", "technologyOwnership", "funding", "institutionalOwnership",
                      "pharmaValidation", "clinicalValidation", "revenueValidation")
        verified = {key: sum(bool(x.get("verified")) for x in row[key]) for key in stage_keys}
        if not verified["researcherCompanyRelation"]:
            row["gaps"].append("缺论文作者/创始人与公司的原始关系证据")
        if not verified["technologyOwnership"]:
            row["gaps"].append("缺公司专利、专利受让或大学技术许可的明确证据")
        elif not any(x.get("independentAssignmentVerified") for x in row["technologyOwnership"]):
            row["gaps"].append("公司已在 SEC 披露专利/许可，但尚缺 USPTO 或大学技术转移材料独立复核")
        if not verified["funding"]:
            row["gaps"].append("缺融资投资人身份及资金进入的原始证据")
        if not verified["institutionalOwnership"]:
            row["gaps"].append("缺 13D/13G 重要股东证据；这与公司融资是两个不同信号")
        if not verified["pharmaValidation"]:
            row["gaps"].append("缺大药厂付费、许可或具有经济条款的合作证据")
        if not verified["clinicalValidation"]:
            row["gaps"].append("缺 IND 生效或已登记临床试验证据")
        if not verified["revenueValidation"]:
            row["gaps"].append("缺经 SEC/XBRL 核验的收入证据")
        if verified["revenueValidation"] and not any(x.get("aiSpecificRevenue") for x in row["revenueValidation"]):
            row["gaps"].append("公司总收入已核验，但尚不能证明收入来自相关 AI/科研技术")
        row["verifiedStages"] = verified
        commercial = verified["pharmaValidation"] or verified["revenueValidation"]
        row["chainStatus"] = ("ownership-and-pharma-validated" if verified["pharmaValidation"] and verified["technologyOwnership"] else
                              "ownership-and-company-revenue-verified" if verified["revenueValidation"] and verified["technologyOwnership"] else
                              "commercial-signal-with-ownership-gap" if commercial else
                              "clinical-signal-with-ownership-gap" if verified["clinicalValidation"] else
                              "science-linked" if verified["discovery"] or verified["researcherCompanyRelation"] or verified["technologyOwnership"] else "evidence-fragment")
        row["interpretation"] = ("已有商业信号，但不能把合作公告当成客户收入；仍按缺口继续核验。" if commercial else
                                 "目前只到科研/关系发现层，不能升级为商业化结论。")
        if any(row[key] for key in stage_keys):
            ordered.append(row)
        company_id = f"company:{ticker}"
        nodes[company_id] = {"id": company_id, "kind": "company", "label": row.get("company"), "ticker": ticker}
        for bucket in stage_keys:
            for i, item in enumerate(row[bucket]):
                node_id = f"evidence:{ticker}:{bucket}:{i}"
                nodes[node_id] = {"id": node_id, "kind": bucket, "label": item.get("relation"), "source": item.get("source")}
                edges.append({"source": node_id, "target": company_id, "relation": item.get("relation"),
                              "verified": item.get("verified"), "url": item.get("url")})
    ordered.sort(key=lambda r: (-sum(r["verifiedStages"].values()), r["ticker"]))
    complete = lambda r: all(r["verifiedStages"].get(k) for k in
                             ("discovery", "researcherCompanyRelation", "technologyOwnership", "funding",
                              "pharmaValidation", "clinicalValidation", "revenueValidation")) and any(
                                  x.get("independentAssignmentVerified") for x in r["technologyOwnership"])
    return {"schemaVersion": 1, "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "method": "Deterministic evidence join. Technology overlap is discovery only; partnership is not revenue; absent primary evidence stays a gap.",
            "summary": {"companiesLinked": len(ordered),
                        "commercialSignals": sum(r["chainStatus"].startswith("commercial") for r in ordered),
                        "researcherCompanyVerified": sum(bool(r["verifiedStages"]["researcherCompanyRelation"]) for r in ordered),
                        "technologyOwnershipDisclosed": sum(bool(r["verifiedStages"]["technologyOwnership"]) for r in ordered),
                        "usptoAssignmentVerified": sum(any(x.get("independentAssignmentVerified") for x in r["technologyOwnership"]) for r in ordered),
                        "institutionalOwnersVerified": sum(bool(r["verifiedStages"]["institutionalOwnership"]) for r in ordered),
                        "completeChains": sum(complete(r) for r in ordered)},
            "companies": ordered, "graph": {"nodes": list(nodes.values()), "edges": edges}}


def render(payload: dict) -> str:
    s = payload["summary"]
    lines = ["# 科研到商业化证据链", "",
             f"> 已连接 {s['companiesLinked']} 家公司；合作或公司收入信号 {s['commercialSignals']} 家；研究者/公司关系 {s['researcherCompanyVerified']} 家；公司披露技术归属 {s['technologyOwnershipDisclosed']} 家；USPTO 独立核验 {s['usptoAssignmentVerified']} 家；13D/13G 重要股东 {s['institutionalOwnersVerified']} 家；完整链路 {s['completeChains']} 家。", "",
             "> 这是可审计研究漏斗，不是股票评分。技术相似、论文提及或合作公告都不能单独证明知识产权、客户收入或买入价值。", "",
             "| 公司 | 科研 | 研究者/公司 | 专利/许可 | 融资 | 13D/G股东 | 药企付费/合作 | IND/临床 | SEC收入 | 当前结论 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
    for row in payload.get("companies", []):
        v = row["verifiedStages"]
        lines.append(f"| {row['ticker']} | {v['discovery']} | {v['researcherCompanyRelation']} | {v['technologyOwnership']} | {v['funding']} | {v['institutionalOwnership']} | {v['pharmaValidation']} | {v['clinicalValidation']} | {v['revenueValidation']} | {row['chainStatus']} |")
    for row in payload.get("companies", [])[:15]:
        lines += ["", f"## {row['ticker']} · {row.get('company')}", "", row["interpretation"], "", "**尚缺证据**"]
        lines += [f"- {gap}" for gap in row["gaps"]] or ["- 无"]
        cited = [x for key in ("discovery", "researcherCompanyRelation", "technologyOwnership", "funding", "institutionalOwnership", "pharmaValidation", "clinicalValidation", "revenueValidation") for x in row[key] if x.get("verified")]
        if cited:
            lines += ["", "**已核验证据**"]
            lines += [f"- [{x['source']}]({x.get('url') or '#'}) · {x['relation']}：{x.get('quote')}" for x in cited[:8]]
    lines += ["", "## 如何补齐", "", "1. 用 USPTO/大学技术转移办公室原文核验专利受让与许可。",
              "2. 用公司 S-1/10-K、Form D 与 13D/13G 核验创始人及投资人。",
              "3. 用 8-K 合同经济条款确认药企是否真实付款；合作公告不等于收入。",
              "4. 用 ClinicalTrials.gov、FDA 与 SEC XBRL 分别核验临床推进和财务兑现。"]
    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--frontier", default=str(ROOT / "state/scientific-frontier.json"))
    p.add_argument("--companies", default=str(ROOT / "trend-agent/theme-company-map.json"))
    p.add_argument("--pharma", default=str(ROOT / "state/pharma-deals-ind.json"))
    p.add_argument("--clinical", default=str(ROOT / "state/clinical-trials-snapshot.json"))
    p.add_argument("--funding", default=str(ROOT / "state/early-signals.json"))
    p.add_argument("--financials", default=str(ROOT / "state/ai-medicine-financial-scenarios.json"))
    p.add_argument("--xbrl", default=str(ROOT / "state/sec-xbrl-validation.json"))
    p.add_argument("--manual-links", default=str(ROOT / "trend-agent/science-commercialization-links.json"))
    p.add_argument("--founders", default=str(ROOT / "state/science-founders.json"),
                   help="founder and university-license links quoted from 10-Ks (scripts/science_founders.py)")
    p.add_argument("--ownership", default=str(ROOT / "state/technology-ownership.json"))
    p.add_argument("--uspto", default=str(ROOT / "state/uspto-assignment-validation.json"))
    p.add_argument("--institutional", default=str(ROOT / "state/institutional-ownership.json"))
    p.add_argument("--research", default=str(ROOT / "state/company-research.json"))
    p.add_argument("--raises", default=str(ROOT / "state/equity-raises.json"))
    p.add_argument("--small-caps", default=str(ROOT / "state/small-cap-stage.json"))
    p.add_argument("--state", default=str(ROOT / "state/science-commercialization-graph.json"))
    p.add_argument("--report", default=str(ROOT / "outputs/science-commercialization-graph.md"))
    args = p.parse_args()
    company_payload = load(Path(args.companies), {"themes": {}})
    rows = list(company_payload.get("themes", {}).get("ai_medicine", []))
    known = {row.get("ticker") for row in rows}
    small_caps = load(Path(args.small_caps), {"companies": []})
    for row in small_caps.get("companies", []):
        if row.get("ticker") and row["ticker"] not in known:
            rows.append({"ticker": row["ticker"], "company": row.get("company"),
                         "exposure": row.get("segment", ""), "serenity_role": row.get("stageDetail", "")})
            known.add(row["ticker"])
    pharma_payload = load(Path(args.pharma), {})
    for filing in pharma_payload.get("filings", []):
        if filing.get("ticker") and filing["ticker"] not in known:
            rows.append({"ticker": filing["ticker"], "company": filing.get("company"), "exposure": "", "serenity_role": ""})
            known.add(filing["ticker"])
    payload = build(load(Path(args.frontier), {}), rows, pharma_payload, load(Path(args.clinical), {}),
                    load(Path(args.funding), {}), load(Path(args.financials), {}), load(Path(args.xbrl), {}),
                    {"links": load(Path(args.manual_links), {"links": []}).get("links", [])
                               + load(Path(args.founders), {"links": []}).get("links", [])},
                    load(Path(args.ownership), {"companies": []}),
                    load(Path(args.uspto), {"companies": []}), load(Path(args.institutional), {"filings": []}),
                    load(Path(args.raises), {"companies": {}}), load(Path(args.research), {"companies": {}}))
    Path(args.state).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.state).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.report).write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
