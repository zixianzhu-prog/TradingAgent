from evidence_graph_agent import build


def test_graph_links_company_asset_trial_gate_and_source():
    graph = build(
        {"candidates": [{"ticker": "TEST", "company": "Test Bio", "rank": 1, "sources": ["https://example.com/source"]}]},
        {"companies": [{"ticker": "TEST", "supply_chain_map": "pass"}]},
        {"studies": [{"ticker": "TEST", "asset": "T-1", "nctId": "NCT1", "status": "RECRUITING", "phases": ["PHASE1"], "url": "https://clinicaltrials.gov/study/NCT1"}]},
        {"scheduledEvents": [{"ticker": "TEST", "type": "clinical", "label": "Readout", "status": "upcoming"}]},
        {"companies": [{"ticker": "TEST", "financial_period": "Q3", "financial_date": "2026-09-30", "data_freshness": "current"}]},
    )
    relations = {edge["relation"] for edge in graph["edges"]}
    assert {"SUPPORTED_BY", "EVALUATED_BY", "VALIDATED_BY", "DEVELOPS", "REGISTERED_AS", "HAS_VALIDATION_EVENT"} <= relations
    assert graph["summary"]["trials"] == 1
