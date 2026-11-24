from serenity_evidence_review import validate, host_matches, failed_run
from serenity_gate_engine import evaluate_company

P = {"id": "ev_real", "text": "Customers used the platform and revenue increased by 20 percent.", "primary": True, "url": "https://example.com/disclosure", "provenance": "primary-document", "publishedAt": "2026-11-01", "observedAt": "2026-11-13"}


def review(quote=None, ref_id="ev_real"):
    return {"gates": {"earnings_validation": {"status": "pass", "reason": "Financial disclosure", "support": [{"id": ref_id, "quote": quote or P["text"]}], "counter": [], "missing": []}}}


def test_fabricated_quote_or_citation_never_passes():
    assert validate(review("Invented high revenue and future growth"), [P])["earnings_validation"]["status"] == "unknown"
    assert validate(review(ref_id="ev_fiction"), [P])["earnings_validation"]["status"] == "unknown"


def test_local_summary_does_not_become_verified_disclosure():
    passage = {**P, "primary": False, "provenance": "local-unverified-notes"}
    assert validate(review(), [passage])["earnings_validation"]["status"] == "partial"
    assert validate(review(), [P])["earnings_validation"]["status"] == "pass"


def test_missing_data_and_unresolved_governance_not_ready():
    assert all(v["status"] == "unknown" for v in validate({}, []).values())
    row = {"ticker": "X", "supply_chain_map": "pass", "customer_dependency": "pass", "earnings_validation": "pass", "counter_thesis": "pass", "management_governance": "pending"}
    assert evaluate_company(row)["decision"] == "watch"
    assert evaluate_company({**row, "management_governance": "fail"})["decision"] == "reject"


def test_hostname_spoof_is_not_primary():
    assert host_matches("https://investor.nvidia.com/release", {"nvidia.com"})
    assert not host_matches("https://nvidia.com.attacker.test/release", {"nvidia.com"})


def test_conflicting_evidence_prevents_pass():
    raw = review()
    raw["gates"]["earnings_validation"]["counter"] = [{"id": "ev_real", "quote": P["text"]}]
    assert validate(raw, [P])["earnings_validation"]["status"] == "partial"


def test_claude_review_is_not_marked_stale_by_new_codex_packet(tmp_path, monkeypatch):
    import json
    import serenity_evidence_review as ser
    monkeypatch.setattr(ser, "ROOT", tmp_path)
    (tmp_path / "state").mkdir()
    (tmp_path / "state/serenity-auto-assessments.json").write_text(json.dumps({"companies": [
        {"ticker": "RXRX", "review_status": "complete", "input_hash": "claude-hash", "review_path": "state/serenity-reviews/RXRX-claude-abc.json",
         **{g: "pass" for g in ser.GATES}, "gate_reviews": {}}]}))
    monkeypatch.setattr(ser, "collect", lambda company, fetch: ([], []))
    monkeypatch.setattr(ser, "write_outputs", lambda rows, provider: {"companies": list(rows.values())})
    ser.prepare_codex([{"ticker": "RXRX", "name": "Recursion"}], [], False)
    manifest = json.loads((tmp_path / "state/serenity-codex-inbox.json").read_text())
    assert manifest["companies"][0]["status"] == "claude-reviewed"


def test_counter_thesis_pass_rests_on_sourced_counter_evidence():
    ct = lambda counter, falsifiers: {"gates": {"counter_thesis": {"status": "pass", "reason": "examined", "support": [],
                                                                  "counter": counter, "missing": [], "falsifiers": falsifiers}}}
    ref = [{"id": "ev_real", "quote": P["text"]}]
    assert validate(ct(ref, ["growth turns negative"]), [P])["counter_thesis"]["status"] == "pass"
    assert validate(ct(ref, []), [P])["counter_thesis"]["status"] == "partial"  # falsifiers still required
    assert validate(ct([], ["x"]), [P])["counter_thesis"]["status"] == "unknown"  # no sourced counter-evidence


def test_failed_run_keeps_last_grade():
    assert failed_run({"support": [], "counter": []}, 5)
    assert not failed_run({"support": [{"quote": "x"}], "counter": []}, 5)
    assert not failed_run({"support": [], "counter": [{"quote": "y"}]}, 2)
    assert not failed_run({"support": [], "counter": []}, 0)
