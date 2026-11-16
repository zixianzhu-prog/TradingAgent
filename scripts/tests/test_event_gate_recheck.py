import json
from pathlib import Path

import event_gate_recheck as recheck


def test_record_text_keeps_only_the_decision_table():
    html = ("<html><b>Device Classification Name</b> EEG Software <td>Decision</td> Substantially Equivalent (SESE) "
            "Predetermined Change Control Plan Authorized No This website has been translated to Spanish</html>")
    text = recheck.record_text(html)
    assert text.startswith("Device Classification Name") and "SESE" in text and "translated" not in text


def test_summary_url_follows_fda_layout():
    assert recheck.summary_url({"id": "K261712"}).endswith("/cdrh_docs/pdf26/K261712.pdf")
    assert recheck.summary_url({"id": "DEN250044"}).endswith("/cdrh_docs/reviews/DEN250044.pdf")


def write(root: Path, rel: str, payload) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_apply_merges_gates_and_records_before_after(tmp_path, monkeypatch):
    monkeypatch.setattr(recheck, "TRACE", tmp_path / "state/event-rechecks.json")
    task = {"eventId": "K1", "ticker": "AAA", "event": {}, "gatesReopened": ["chokepoint_evidence", "pure_play"],
            "before": {"chokepoint_evidence": "unknown", "pure_play": "partial"}, "newPassages": ["ev_new"],
            "inputHash": "h2", "tierBefore": None, "status": "awaiting review"}
    write(tmp_path, "state/event-rechecks.json", {"rechecks": [task]})
    write(tmp_path, "state/serenity-claude-response.json", {"reviews": [{"ticker": "AAA", "inputHash": "h1", "gates": {"pure_play": {"status": "partial"}}}]})
    write(tmp_path, "state/serenity-claude-verdicts.json", {"companies": [{"ticker": "AAA", "tier": "starter"}]})
    new_gate = {"status": "partial", "reason": "r", "support": [{"id": "ev_new", "quote": "cleared a change control plan"}], "counter": []}
    write(tmp_path, "state/event-recheck-response.json", {"rechecks": [{"eventId": "K1", "gates": {"chokepoint_evidence": new_gate}, "note": "n"}]})
    # what the importer would produce after its citation check
    write(tmp_path, "state/serenity-auto-assessments.json", {"companies": [{"ticker": "AAA", "chokepoint_evidence": "partial", "pure_play": "partial",
        "gate_reviews": {"chokepoint_evidence": {"citationChecks": "exact-quote-matched", "support": [{"id": "ev_new", "quote": "cleared a change control plan"}], "counter": []}}}]})
    done = recheck.apply(tmp_path / "state/event-recheck-response.json", root=tmp_path, run_import=False)[0]
    review = json.loads((tmp_path / "state/serenity-claude-response.json").read_text())["reviews"][0]
    assert review["inputHash"] == "h2" and review["gates"]["chokepoint_evidence"]["status"] == "partial"
    assert done["changed"] == {"chokepoint_evidence": ["unknown", "partial"]}
    assert done["quotes"]["chokepoint_evidence"] == ["cleared a change control plan"]
    assert done["tierAfter"] == "starter" and done["status"] == "re-checked"
