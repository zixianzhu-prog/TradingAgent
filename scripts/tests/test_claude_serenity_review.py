import claude_serenity_review as csr
import serenity_evidence_review as ser


def test_schema_requires_every_gate_and_status_enum():
    s = csr.schema()
    gates = s["properties"]["gates"]
    assert set(gates["required"]) == set(ser.GATES)
    assert gates["properties"]["counter_thesis"]["properties"]["status"]["enum"] == csr.STATUSES


def test_precheck_counts_quotes_the_importer_would_reject():
    packet = {"evidence": [{"id": "ev_1", "text": "Revenue grew 65% year over year to $21.6 million in the quarter."}]}
    gates = {"earnings_validation": {"support": [{"id": "ev_1", "quote": "Revenue grew 65% year over year"}],
                                     "counter": [{"id": "ev_1", "quote": "Revenue fell sharply in the quarter"},
                                                 {"id": "ev_9", "quote": "Revenue grew 65% year over year"},
                                                 {"id": "ev_1", "quote": "short"}]}}
    assert csr.precheck(gates, packet) == {"quotes": 4, "unmatched": 3}


def test_instructions_keep_rules_but_drop_file_writing_steps():
    text = csr.instructions()
    assert "exact substring" in text and "financingRisk" in text
    assert "serenity-codex-queue-response.json" not in text
