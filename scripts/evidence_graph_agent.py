from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


GATE_FIELDS = (
    "supply_chain_map", "chokepoint_evidence", "customer_dependency", "pure_play",
    "multi_node_control", "counter_thesis", "earnings_validation",
)


def source_id(url: str) -> str:
    return "source:" + hashlib.sha256(url.encode()).hexdigest()[:14]


def build(theses: dict, assessments: dict, clinical: dict, events: dict, financials: dict) -> dict:
    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    research_universe = [*theses.get("candidates", []), *theses.get("expanded_deep_dives", [])]
    candidates = {row["ticker"]: row for row in research_universe}
    assessment_rows = {row["ticker"]: row for row in assessments.get("companies", [])}
    financial_rows = {row["ticker"]: row for row in financials.get("companies", [])}

    for ticker, candidate in candidates.items():
        company_id = f"company:{ticker}"
        nodes[company_id] = {
            "id": company_id, "type": "company", "ticker": ticker,
            "label": candidate.get("company", ticker), "rank": candidate.get("rank"),
            "classification": candidate.get("classification"),
        }
        for url in candidate.get("sources", []):
            sid = source_id(url)
            nodes[sid] = {"id": sid, "type": "source", "label": urlparse(url).netloc, "url": url}
            edges.append({"from": company_id, "to": sid, "relation": "SUPPORTED_BY", "provenance": "thesis source"})
        assessment = assessment_rows.get(ticker, {})
        for gate in GATE_FIELDS:
            gid = f"gate:{ticker}:{gate}"
            nodes[gid] = {"id": gid, "type": "serenity_gate", "label": gate, "status": assessment.get(gate, "unreviewed")}
            edges.append({"from": company_id, "to": gid, "relation": "EVALUATED_BY", "provenance": "Serenity deterministic gate"})
        financial = financial_rows.get(ticker)
        if financial:
            fid = f"financial:{ticker}:{financial.get('financial_period', 'latest')}"
            nodes[fid] = {
                "id": fid, "type": "financial_snapshot", "label": financial.get("financial_period"),
                "date": financial.get("financial_date"), "freshness": financial.get("data_freshness"),
            }
            edges.append({"from": company_id, "to": fid, "relation": "VALIDATED_BY", "provenance": "official financial release"})

    asset_nodes: dict[tuple[str, str], str] = {}
    for study in clinical.get("studies", []):
        ticker, asset = study["ticker"], study["asset"]
        company_id = f"company:{ticker}"
        aid = asset_nodes.setdefault((ticker, asset), f"asset:{ticker}:{asset}")
        nodes[aid] = {"id": aid, "type": "asset", "label": asset, "ticker": ticker}
        if company_id in nodes and not any(edge["from"] == company_id and edge["to"] == aid for edge in edges):
            edges.append({"from": company_id, "to": aid, "relation": "DEVELOPS", "provenance": "ClinicalTrials.gov mapping"})
        tid = f"trial:{study['nctId']}"
        nodes[tid] = {
            "id": tid, "type": "clinical_trial", "label": study["nctId"], "url": study.get("url"),
            "status": study.get("status"), "phases": study.get("phases", []), "lastUpdated": study.get("lastUpdated"),
        }
        edges.append({"from": aid, "to": tid, "relation": "REGISTERED_AS", "provenance": "ClinicalTrials.gov API v2"})

    for event in events.get("scheduledEvents", []):
        ticker = event["ticker"]
        company_id = f"company:{ticker}"
        if company_id not in nodes:
            continue
        eid = "event:" + hashlib.sha256(f"{ticker}|{event.get('type')}|{event.get('label')}".encode()).hexdigest()[:14]
        nodes[eid] = {
            "id": eid, "type": "validation_event", "label": event.get("label"),
            "date": event.get("date"), "status": event.get("status"), "evidenceUrl": event.get("evidence_url"),
        }
        edges.append({"from": company_id, "to": eid, "relation": "HAS_VALIDATION_EVENT", "provenance": "event watchlist"})

    companies = []
    for ticker in candidates:
        company_id = f"company:{ticker}"
        linked = [edge for edge in edges if edge["from"] == company_id]
        gates = [node for node in nodes.values() if node.get("type") == "serenity_gate" and node["id"].startswith(f"gate:{ticker}:")]
        trials = [edge for edge in edges if edge["relation"] == "DEVELOPS" and edge["from"] == company_id]
        companies.append({
            "ticker": ticker,
            "sourceCount": sum(edge["relation"] == "SUPPORTED_BY" for edge in linked),
            "assetCount": len(trials),
            "gatePassCount": sum(node.get("status") == "pass" for node in gates),
            "gateCount": len(gates),
        })
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "method": "Deterministic provenance graph assembled from thesis sources, Serenity gates, financial snapshots, event watchlists and ClinicalTrials.gov records.",
        "nodes": sorted(nodes.values(), key=lambda row: row["id"]),
        "edges": edges,
        "companies": companies,
        "summary": {
            "nodes": len(nodes), "edges": len(edges),
            "sources": sum(row["type"] == "source" for row in nodes.values()),
            "trials": sum(row["type"] == "clinical_trial" for row in nodes.values()),
        },
    }


def write_report(payload: dict, output: Path) -> None:
    lines = [
        "# AI Medicine 可审计证据关系图", "",
        "> 每条关系都标明来源类型；图表示研究证据连接，不表示因果已被证明或股票具有预期收益。", "",
        f"节点：{payload['summary']['nodes']}；关系：{payload['summary']['edges']}；官方/原始来源：{payload['summary']['sources']}；临床试验：{payload['summary']['trials']}", "",
        "| 股票 | 官方来源 | 临床资产 | Serenity通过门槛 |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in payload["companies"]:
        lines.append(f"| {row['ticker']} | {row['sourceCount']} | {row['assetCount']} | {row['gatePassCount']}/{row['gateCount']} |")
    lines += ["", "## 关系明细", ""]
    labels = {row["id"]: row.get("label", row["id"]) for row in payload["nodes"]}
    for edge in payload["edges"]:
        lines.append(f"- **{labels.get(edge['from'], edge['from'])}** — `{edge['relation']}` → **{labels.get(edge['to'], edge['to'])}** · {edge['provenance']}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an auditable AI Medicine evidence graph")
    for name in ("theses", "assessments", "clinical", "events", "financials"):
        parser.add_argument(f"--{name}", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()
    load = lambda path: json.loads(Path(path).read_text(encoding="utf-8"))
    payload = build(load(args.theses), load(args.assessments), load(args.clinical), load(args.events), load(args.financials))
    target = Path(args.json_output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(payload, Path(args.markdown_output))
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
