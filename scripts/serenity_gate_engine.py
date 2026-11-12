from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


PASS = "pass"
INCOMPLETE = {"partial", "pending", "unknown", "unreviewed"}
HARD_GATES = ("supply_chain_map", "customer_dependency", "earnings_validation")
SUPPORTING_GATES = ("chokepoint_evidence", "pure_play", "multi_node_control", "counter_thesis")


def evaluate_company(company: dict, affected_gates: set[str] | None = None) -> dict:
    """Calculate a Serenity research gate from auditable component states.

    The score measures gate completeness, not expected return. A new material event
    invalidates only the gates it affects until a reviewer confirms the new evidence.
    """
    affected_gates = affected_gates or set()
    states = {gate: company.get(gate, "unreviewed") for gate in (*HARD_GATES, *SUPPORTING_GATES)}
    stale = sorted(gate for gate in affected_gates if gate in states)
    effective = {gate: ("stale" if gate in stale else state) for gate, state in states.items()}

    points = 0
    maximum = 0
    weights = {gate: 15 for gate in HARD_GATES} | {gate: 10 for gate in SUPPORTING_GATES}
    weights["counter_thesis"] = 15
    for gate, weight in weights.items():
        maximum += weight
        state = effective[gate]
        if state == PASS:
            points += weight
        elif state == "partial":
            points += weight // 2

    hard_failures = [gate for gate in HARD_GATES if effective[gate] != PASS]
    explicit_failures = [gate for gate, state in effective.items() if state == "fail"]
    if stale:
        decision = "revalidate"
    elif not hard_failures and effective["counter_thesis"] == PASS:
        decision = "research-ready"
    elif explicit_failures:
        decision = "reject"
    else:
        decision = "watch"

    return {
        "ticker": company["ticker"],
        "decision": decision,
        "completenessScore": round(points / maximum * 100),
        "hardGateFailures": hard_failures,
        "staleGates": stale,
        "gateStates": effective,
        "storedDecision": company.get("serenity_decision", "unreviewed"),
        "decisionConsistent": company.get("serenity_decision") == decision or decision == "revalidate",
        "note": "Completeness and validation status only; not a return forecast or buy signal.",
    }


def build(assessments: dict, event_payload: dict, divergence_payload: dict | None = None, clinical_payload: dict | None = None) -> dict:
    affected: dict[str, set[str]] = {}
    for task in event_payload.get("revalidationTasks", []):
        affected.setdefault(task["ticker"], set()).update(task.get("affectedGates", []))
    for row in (divergence_payload or {}).get("companies", []):
        if row.get("status") == "revalidate":
            affected.setdefault(row["ticker"], set()).update(row.get("affectedGates", []))
    for row in (clinical_payload or {}).get("changes", []):
        if row.get("status") == "pending-revalidation":
            affected.setdefault(row["ticker"], set()).update(row.get("affectedGates", []))
    companies = [evaluate_company(row, affected.get(row["ticker"], set())) for row in assessments.get("companies", [])]
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "method": "Deterministic Serenity gate engine; material events mark affected evidence gates stale.",
        "companies": companies,
        "summary": {
            "researchReady": sum(row["decision"] == "research-ready" for row in companies),
            "watch": sum(row["decision"] == "watch" for row in companies),
            "revalidate": sum(row["decision"] == "revalidate" for row in companies),
            "reject": sum(row["decision"] == "reject" for row in companies),
            "inconsistentStoredDecisions": sum(not row["decisionConsistent"] for row in companies),
        },
    }


def write_report(payload: dict, output: Path) -> None:
    lines = [
        "# Serenity 自动门槛审计", "",
        "> 本分数衡量研究证据完整度，不代表预期收益，也不是买入信号。重大事件会把相关门槛标为 stale，等待重新验证。", "",
        "| 股票 | 自动结论 | 完整度 | 未通过硬门槛 | 事件失效门槛 | 与手工结论一致 |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for row in payload["companies"]:
        lines.append(
            f"| {row['ticker']} | {row['decision']} | {row['completenessScore']}/100 | "
            f"{', '.join(row['hardGateFailures']) or '无'} | {', '.join(row['staleGates']) or '无'} | "
            f"{'是' if row['decisionConsistent'] else '否'} |"
        )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute auditable Serenity research gates")
    parser.add_argument("--assessments", required=True)
    parser.add_argument("--events", required=True)
    parser.add_argument("--divergences")
    parser.add_argument("--clinical")
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()
    assessments = json.loads(Path(args.assessments).read_text(encoding="utf-8"))
    events_path = Path(args.events)
    events = json.loads(events_path.read_text(encoding="utf-8")) if events_path.is_file() else {}
    divergence_path = Path(args.divergences) if args.divergences else None
    divergences = json.loads(divergence_path.read_text(encoding="utf-8")) if divergence_path and divergence_path.is_file() else {}
    clinical_path = Path(args.clinical) if args.clinical else None
    clinical = json.loads(clinical_path.read_text(encoding="utf-8")) if clinical_path and clinical_path.is_file() else {}
    payload = build(assessments, events, divergences, clinical)
    target = Path(args.json_output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(payload, Path(args.markdown_output))
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
