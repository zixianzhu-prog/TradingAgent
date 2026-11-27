import claude_control_review as ccr


def test_chokepoint_rubric():
    assert ccr.chokepoint_status([{"kind": "only_cleared", "quote": "aprevo is the only FDA-cleared personalized interbody"}])[0] == "pass"
    assert ccr.chokepoint_status([{"kind": "market_share", "quote": "we hold 45% of the US market"}])[0] == "pass"
    # a strong kind without a specific number or only/sole wording is not specific
    assert ccr.chokepoint_status([{"kind": "switching_cost", "quote": "customers may find it costly to change vendors"}])[0] == "partial"
    assert ccr.chokepoint_status([{"kind": "patent", "quote": "we own 45 issued patents"}])[0] == "partial"
    # A model cannot turn an arbitrary number or marketing adjective into a hard moat.
    assert ccr.chokepoint_status([{"kind": "market_share", "quote": "we serve 45 customers with a unique platform"}])[0] == "partial"
    assert ccr.chokepoint_status([{"kind": "only_cleared", "quote": "we received FDA clearance for a unique product"}])[0] == "partial"
    assert ccr.chokepoint_status([])[0] == "unknown"


def test_node_rubric_needs_two_adjacent_in_house_steps():
    assert ccr.node_status([{"id":"p1","node": "model_software", "inHouse": True}, {"id":"p1","node": "design", "inHouse": True}])[0] == "pass"
    assert ccr.node_status([{"id":"p1","node": "model_software", "inHouse": True}, {"id":"p2","node": "design", "inHouse": True}])[0] == "partial"
    assert ccr.node_status([{"node": "data", "inHouse": True}, {"node": "sales", "inHouse": True}])[0] == "partial"
    assert ccr.node_status([{"node": "design", "inHouse": True}, {"node": "manufacturing", "inHouse": False}])[0] == "partial"
    assert ccr.node_status([{"node": "manufacturing", "inHouse": False}])[0] == "unknown"


def test_to_gates_drops_unverified_quotes(monkeypatch):
    text = ("aprevo is the only FDA-cleared personalized spine implant system. We design each implant in-house with our software. "
            "We rely on contract manufacturers to produce our implants. Competitors include Medtronic and Globus Medical.")
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    p = [{"id": "cc_1", "url": "u", "title": "10-K", "text": text}]
    ans = {"barriers": [{"id": "cc_1", "quote": "aprevo is the only FDA-cleared personalized spine implant system", "kind": "only_cleared"},
                        {"id": "cc_1", "quote": "this sentence is not in the filing at all", "kind": "market_share"}],
           "competitors": [{"id": "cc_1", "quote": "Competitors include Medtronic and Globus Medical"}],
           "nodes": [{"id": "cc_1", "quote": "We design each implant in-house with our software", "node": "design", "inHouse": True},
                     {"id": "cc_1", "quote": "We rely on contract manufacturers to produce our implants", "node": "manufacturing", "inHouse": False}],
           "reason": "x"}
    c, m, dropped = ccr.to_gates(ans, p)
    assert c["status"] == "pass" and dropped == 1 and len(c["counter"]) == 1
    assert m["status"] == "partial" and len(m["counter"]) == 1


def test_renamed_passage_ids_fall_back_to_the_quote(monkeypatch):
    text = "aprevo is the only FDA-cleared personalized spine implant system on the market today."
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    p = [{"id": "cc_abc", "url": "u", "title": "10-K", "text": text}]
    ans = {"barriers": [{"id": "b1", "quote": "aprevo is the only FDA-cleared personalized spine implant system", "kind": "only_cleared"}],
           "competitors": [], "nodes": [], "reason": "x"}
    c, _, dropped = ccr.to_gates(ans, p)
    assert c["status"] == "pass" and dropped == 0
    assert c["support"][0]["id"] == "cc_abc"


def test_fallback_uses_real_passage_ids_for_node_connectivity(monkeypatch):
    one = "We develop our prediction software in-house for the clinical platform."
    two = "We design each patient-specific medical device in-house before production."
    filings = {"u1": one, "u2": two}
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: filings[url])
    passages = [
        {"id": "cc_one", "url": "u1", "title": "10-K", "text": one},
        {"id": "cc_two", "url": "u2", "title": "10-Q", "text": two},
    ]
    # The model incorrectly assigns the same alias to quotes from two real
    # passages.  They must remain separate and cannot prove a connected chain.
    answer = {
        "barriers": [],
        "competitors": [],
        "nodes": [
            {"id": "n1", "quote": one, "node": "model_software", "inHouse": True},
            {"id": "n1", "quote": two, "node": "design", "inHouse": True},
        ],
        "reason": "x",
    }
    _, multi, dropped = ccr.to_gates(answer, passages)
    assert dropped == 0
    assert multi["status"] == "partial"
    assert [item["id"] for item in multi["nodes"]] == ["cc_one", "cc_two"]


def test_non_exclusive_is_not_a_sole_source():
    q = "the Company granted Tempus a non-exclusive, non-sublicensable worldwide license to the TxFM Model"
    assert not ccr.barrier_is_specific({"kind": "sole_source", "quote": q})
    assert ccr.barrier_is_specific({"kind": "sole_source", "quote": "we are the sole supplier of the reagent to all US labs"})


def test_failed_cli_call_returns_no_answer(monkeypatch):
    def boom(result):
        raise ccr.claude_cli.ClaudeCLIError("timed out")
    monkeypatch.setattr(ccr.claude_cli, "run", lambda *a, **k: None)
    monkeypatch.setattr(ccr.claude_cli, "require_success", boom)
    assert ccr.ask("CARL", [], "sonnet") is None
