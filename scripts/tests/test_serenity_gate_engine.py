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


def test_new_codex_evidence_marks_previous_review_stale_until_imported():
    payload = build({"companies": [company(codex_pending=True)]}, {})
    result = payload["companies"][0]
    assert result["decision"] == "revalidate"
    assert set(result["staleGates"]) >= {"supply_chain_map", "customer_dependency", "earnings_validation"}


def test_clinical_change_invalidates_clinical_gate_when_present():
    candidate = company()
    candidate["clinical_validation"] = "pass"
    payload = build(
        {"companies": [candidate]}, {}, {},
        {"changes": [{"ticker": "TEST", "status": "pending-revalidation", "affectedGates": ["earnings_validation"]}]},
    )
    assert payload["companies"][0]["decision"] == "revalidate"


def test_sourced_finrobot_finding_can_only_mark_gate_stale():
    finrobot = {"events": [{"status": "complete", "analysis": {"companies": [{
        "ticker": "TEST", "directCompanyRelationship": True, "materiality": "high",
        "supportingSourceUrls": ["https://www.sec.gov/example"],
        "affectedSerenityGates": ["customer_dependency"],
    }]}}]}
    payload = build({"companies": [company()]}, {}, {}, {}, finrobot)
    assert payload["companies"][0]["decision"] == "revalidate"
    assert payload["companies"][0]["staleGates"] == ["customer_dependency"]


def test_unsourced_finrobot_inference_does_not_change_serenity():
    finrobot = {"events": [{"status": "complete", "analysis": {"companies": [{
        "ticker": "TEST", "directCompanyRelationship": True, "materiality": "high",
        "supportingSourceUrls": [], "affectedSerenityGates": ["customer_dependency"],
    }]}}]}
    payload = build({"companies": [company()]}, {}, {}, {}, finrobot)
    assert payload["companies"][0]["decision"] == "research-ready"
    assert payload["companies"][0]["staleGates"] == []


def test_primary_evidence_breaks_gate_completeness_ties():
    bare = evaluate_company(company())
    reviewed = company(gate_reviews={
        gate: {"support": [{"primary": True}], "counter": [], "falsifiers": ["test"], "missing": []}
        for gate in ("supply_chain_map", "chokepoint_evidence", "customer_dependency", "pure_play", "multi_node_control", "counter_thesis", "earnings_validation")
    })
    strong = evaluate_company(reviewed)
    assert strong["completenessScore"] == bare["completenessScore"]
    assert strong["evidenceQualityScore"] > bare["evidenceQualityScore"]
    assert strong["substantiatedScore"] > bare["substantiatedScore"]
