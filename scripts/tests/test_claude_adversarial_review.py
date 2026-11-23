import claude_adversarial_review as car


def test_verify_keeps_quoted_challenges_and_flags_hard_gate_fails():
    ev = [{"id": "ev_1", "url": "u", "title": "t", "text": "Our top three customers accounted for 72% of revenue in 2025."}]
    answer = {"overall": "Customer concentration is high.", "challenges": [
        {"gate": "customer_dependency", "proposedStatus": "fail", "argument": "72% from three customers", "id": "ev_1",
         "quote": "Our top three customers accounted for 72% of revenue"},
        {"gate": "chokepoint_evidence", "proposedStatus": "fail", "argument": "made up", "id": "ev_1", "quote": "We have no moat"},
        {"gate": "pure_play", "proposedStatus": "fail", "argument": "x", "id": "ev_1", "quote": "Our top three customers"}]}
    out = car.verify(answer, ev)
    assert out["droppedQuotes"] == 1 and len(out["challenges"]) == 2
    assert [b["gate"] for b in out["blocking"]] == ["customer_dependency"] and out["verdict"] == "challenged"


def test_ticket_waits_on_blocking_adversarial_challenge():
    from datetime import date
    import order_tickets as ot
    from test_order_tickets import CTX, row
    ctx = {**CTX, "adversarial": {"X": {"model": "opus", "blocking": [{"gate": "customer_dependency", "argument": "72% from three customers"}]}}}
    t = ot.ticket(row(), ctx, 100_000, date(2026, 11, 23))
    assert t["action"] == "wait" and "Adversarial review" in t["reasons"][-1]
