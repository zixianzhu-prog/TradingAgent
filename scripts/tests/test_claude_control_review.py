import claude_control_review as ccr


def test_chokepoint_rubric():
    controls = lambda kind, quote: {"kind": kind, "quote": quote, "role": "company_controls"}
    assert ccr.chokepoint_status([controls("only_cleared", "aprevo is the only FDA-cleared personalized interbody")])[0] == "pass"
    assert ccr.chokepoint_status([controls("market_share", "we hold 45% of the US market")])[0] == "pass"
    # a strong kind without a specific number or only/sole wording is not specific
    assert ccr.chokepoint_status([controls("switching_cost", "customers may find it costly to change vendors")])[0] == "partial"
    assert ccr.chokepoint_status([controls("patent", "we own 45 issued patents")])[0] == "partial"
    # A model cannot turn an arbitrary number or marketing adjective into a hard moat.
    assert ccr.chokepoint_status([controls("market_share", "we serve 45 customers with a unique platform")])[0] == "partial"
    assert ccr.chokepoint_status([controls("only_cleared", "we received FDA clearance for a unique product")])[0] == "partial"
    assert ccr.chokepoint_status([controls("market_share", "Our revenue grew 45% this year compared with last year")])[0] == "partial"
    assert ccr.chokepoint_status([{"kind": "sole_source", "quote": "We rely on Illumina as our sole supplier of sequencers", "role": "company_depends"}])[0] == "unknown"
    assert ccr.chokepoint_status([])[0] == "unknown"


def test_node_rubric_needs_two_adjacent_in_house_steps():
    assert ccr.node_status([{"id":"p1","node": "model_software", "inHouse": True, "pos": 10, "end": 80, "product": "aprevo"}, {"id":"p1","node": "design", "inHouse": True, "pos": 120, "end": 180, "product": "aprevo"}])[0] == "pass"
    assert ccr.node_status([{"id":"p1","node": "model_software", "inHouse": True, "pos": 10, "end": 80, "product": "aprevo"}, {"id":"p2","node": "design", "inHouse": True, "pos": 20, "end": 70, "product": "aprevo"}])[0] == "partial"
    # same passage but far apart (e.g. two unrelated products): not connected
    assert ccr.node_status([{"id":"p1","node": "model_software", "inHouse": True, "pos": 10, "end": 80, "product": "aprevo"}, {"id":"p1","node": "design", "inHouse": True, "pos": 1500, "end": 1560, "product": "aprevo"}])[0] == "partial"
    assert ccr.node_status([{"node": "data", "inHouse": True}, {"node": "sales", "inHouse": True}])[0] == "partial"
    assert ccr.node_status([{"node": "design", "inHouse": True}, {"node": "manufacturing", "inHouse": False}])[0] == "partial"
    assert ccr.node_status([{"node": "manufacturing", "inHouse": False}])[0] == "unknown"


def test_to_gates_drops_unverified_quotes(monkeypatch):
    text = ("aprevo is the only FDA-cleared personalized spine implant system. We design each implant in-house with our software. "
            "We rely on contract manufacturers to produce our implants. Competitors include Medtronic and Globus Medical.")
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    p = [{"id": "cc_1", "url": "u", "title": "10-K", "text": text}]
    ans = {"barriers": [{"id": "cc_1", "quote": "aprevo is the only FDA-cleared personalized spine implant system", "kind": "only_cleared", "role": "company_controls"},
                        {"id": "cc_1", "quote": "this sentence is not in the filing at all", "kind": "market_share", "role": "company_controls"}],
           "competitors": [{"id": "cc_1", "quote": "Competitors include Medtronic and Globus Medical"}],
           "nodes": [{"id": "cc_1", "quote": "We design each implant in-house with our software", "node": "design", "inHouse": True},
                     {"id": "cc_1", "quote": "We rely on contract manufacturers to produce our implants", "node": "manufacturing", "inHouse": False}],
           "reason": "x"}
    c, m, dropped = ccr.to_gates(ans, p)
    assert c["status"] == "pass" and dropped == 1 and len(c["counter"]) == 1
    assert m["status"] == "partial" and m["counter"] == [] and len(m["outsourced"]) == 1


def test_renamed_passage_ids_fall_back_to_the_quote(monkeypatch):
    text = "aprevo is the only FDA-cleared personalized spine implant system on the market today."
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    p = [{"id": "cc_abc", "url": "u", "title": "10-K", "text": text}]
    ans = {"barriers": [{"id": "b1", "quote": "aprevo is the only FDA-cleared personalized spine implant system", "kind": "only_cleared", "role": "company_controls"}],
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


def test_market_share_needs_share_wording_or_an_explicit_rank():
    ms = lambda q: ccr.barrier_is_specific({"kind": "market_share", "quote": q})
    assert not ms("The addressable market grew 45% during 2026.")          # market growth, not share (Codex T1)
    assert not ms("Our revenue grew 45% this year compared with last year")
    assert ms("We are the number one provider of AI-based coronary analysis in the United States.")  # rank (Codex T1)
    assert ms("we hold 45% of the US market")
    assert ms("our tests represented approximately 30% of the U.S. MRD testing market")
    assert ms("we have a 62% market share in the US")
    assert ms("Our share of the U.S. market was 38% in 2025")


def test_direct_supplier_wording_counts_as_a_named_party():
    import claude_chain_review as chain
    assert chain.PARTIES.search("We depend exclusively on Illumina for all sequencing instruments.")
    assert chain.PARTIES.search("Our reagents are supplied by Thermo Fisher Scientific under a long-term agreement.")


def test_exclusive_license_is_not_a_sole_source():
    q = "Roche will have a worldwide, exclusive license under patents and know-how controlled by us to develop and commercialize products"
    assert not ccr.barrier_is_specific({"kind": "sole_source", "quote": q})


def test_node_control_requires_one_named_product_chain():
    nodes = [
        {"id": "p1", "node": "model_software", "inHouse": True, "pos": 10, "end": 80, "product": "Discovery AI"},
        {"id": "p1", "node": "design", "inHouse": True, "pos": 120, "end": 180, "product": "Surgical Robot"},
    ]
    assert ccr.node_status(nodes)[0] == "partial"


def test_node_control_without_product_stays_partial():
    nodes = [
        {"id": "p1", "node": "model_software", "inHouse": True, "pos": 10, "end": 80},
        {"id": "p1", "node": "design", "inHouse": True, "pos": 120, "end": 180},
    ]
    assert ccr.node_status(nodes)[0] == "partial"


def test_node_control_uses_interval_gap_not_start_distance():
    nodes = [
        {"id": "p1", "node": "model_software", "inHouse": True, "pos": 0, "end": 450, "product": " aprevo "},
        {"id": "p1", "node": "design", "inHouse": True, "pos": 451, "end": 520, "product": "APREVO"},
    ]
    assert ccr.node_status(nodes)[0] == "pass"


def test_upstream_dependency_is_counter_evidence_not_a_company_moat(monkeypatch):
    text = ("We rely on Illumina as the sole supplier of the sequencers used in our laboratories. "
            "If Illumina cannot supply us, our testing operations may be interrupted.")
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    passages = [{"id": "cc_1", "url": "u", "title": "10-K", "text": text}]
    answer = {
        # Deliberately simulate a model direction error.  Deterministic code
        # must override company_controls because the quote says "We rely on".
        "barriers": [{"id": "cc_1", "quote": "We rely on Illumina as the sole supplier of the sequencers used in our laboratories",
                      "kind": "sole_source", "role": "company_controls"}],
        "competitors": [], "nodes": [], "reason": "上游单一来源风险",
    }
    choke, _, dropped = ccr.to_gates(answer, passages)
    assert dropped == 0
    assert choke["status"] == "unknown"
    assert choke["support"] == []
    assert len(choke["counter"]) == 1
    assert choke["barriers"][0]["role"] == "company_depends"


def test_supplying_our_customers_is_not_a_dependency():
    # "we supply our customers" is the company controlling a downstream node, not relying on a supplier
    b = {"kind": "sole_source", "quote": "We supply our hospital customers with the only FDA-cleared rapid EEG system", "role": "company_controls"}
    assert ccr.barrier_role(b) == "company_controls"
    assert ccr.barrier_role({"kind": "sole_source", "quote": "Illumina supplies us with all sequencing reagents", "role": "company_controls"}) == "company_depends"


def test_outsourced_steps_are_not_counter_evidence(monkeypatch):
    text = "Our software plans each implant and we design each implant in-house. We rely on contract manufacturers to produce our implants."
    monkeypatch.setattr(ccr.pcr, "filing_text", lambda url, allow_fetch=True: text)
    p = [{"id": "cc_1", "url": "u", "title": "10-K", "text": text}]
    ans = {"barriers": [], "competitors": [], "reason": "x", "nodes": [
        {"id": "cc_1", "quote": "Our software plans each implant", "node": "model_software", "inHouse": True, "product": "aprevo"},
        {"id": "cc_1", "quote": "we design each implant in-house", "node": "design", "inHouse": True, "product": "aprevo"},
        {"id": "cc_1", "quote": "We rely on contract manufacturers to produce our implants", "node": "manufacturing", "inHouse": False, "product": "aprevo"}]}
    _, m, _ = ccr.to_gates(ans, p)
    assert m["status"] == "pass" and m["counter"] == [] and len(m["outsourced"]) == 1
