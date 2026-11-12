from serenity_gate_engine import build, evaluate_company


def company(**updates):
    row = {
        "ticker": "TEST",
        "supply_chain_map": "pass",
        "chokepoint_evidence": "partial",
        "customer_dependency": "pass",
        "pure_play": "pass",
        "multi_node_control": "pass",
        "counter_thesis": "pass",
        "earnings_validation": "pass",
        "serenity_decision": "research-ready",
    }
    row.update(updates)
    return row


def test_research_ready_requires_all_hard_gates():
    assert evaluate_company(company())["decision"] == "research-ready"
    result = evaluate_company(company(customer_dependency="partial", serenity_decision="watch"))
    assert result["decision"] == "watch"
    assert result["hardGateFailures"] == ["customer_dependency"]


def test_material_event_invalidates_only_affected_gate():
    result = evaluate_company(company(), {"earnings_validation"})
    assert result["decision"] == "revalidate"
    assert result["staleGates"] == ["earnings_validation"]
    assert result["gateStates"]["customer_dependency"] == "pass"


def test_event_tasks_flow_into_gate_engine():
    payload = build(
        {"companies": [company()]},
        {"revalidationTasks": [{"ticker": "TEST", "affectedGates": ["customer_dependency"]}]},
    )
    assert payload["summary"]["revalidate"] == 1
    assert payload["companies"][0]["staleGates"] == ["customer_dependency"]


def test_clinical_change_invalidates_clinical_gate_when_present():
    candidate = company()
    candidate["clinical_validation"] = "pass"
    payload = build(
        {"companies": [candidate]}, {}, {},
        {"changes": [{"ticker": "TEST", "status": "pending-revalidation", "affectedGates": ["earnings_validation"]}]},
    )
    assert payload["companies"][0]["decision"] == "revalidate"
