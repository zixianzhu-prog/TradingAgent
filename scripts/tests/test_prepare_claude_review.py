import json

import prepare_claude_review as prep
import serenity_evidence_review as ser

FILING = "https://www.sec.gov/Archives/edgar/data/1/x.htm"
TEXT = ("Risk factors. " * 200) + "We rely on Illumina as the sole supplier of the sequencers we use. " + \
       "Our stockholders’ ownership interests will be diluted. " + ("More text. " * 200)


def test_locate_tolerates_typography_not_wording():
    exact, passage = prep.locate(TEXT, "Our stockholders' ownership interests will be diluted.")
    assert exact == "Our stockholders’ ownership interests will be diluted."  # returns the filing's own characters
    assert exact in passage and len(passage) > 2000
    assert prep.locate(TEXT, "We rely on Roche as the sole supplier of the sequencers") is None


def test_build_keeps_found_quotes_and_flags_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(prep, "ROOT", tmp_path)
    monkeypatch.setattr(prep, "CACHE", tmp_path / "cache")
    (tmp_path / "cache").mkdir()
    (tmp_path / "cache" / (ser.digest(FILING) + ".json")).write_text(json.dumps({"text": TEXT}))
    citations = {"companies": {"TEM": {"gates": {
        "supply_chain_map": {"status": "pass", "reason": "r", "support": [
            {"url": FILING, "quote": "We rely on Illumina as the sole supplier of the sequencers"},
            {"url": FILING, "quote": "This sentence is not in the filing at all, honestly."}]}}}}}
    manifest, response, report = prep.build(citations, [], allow_fetch=False)
    gate = response["reviews"][0]["gates"]["supply_chain_map"]
    assert len(gate["support"]) == 1 and report["TEM"] == {"quotesFound": 1, "quotesMissing": 1, "missing": ["This sentence is not in the filing at all, honestly."]}
    assert any("未在原文中找到引用" in m for m in gate["missing"])
    packet = json.loads((tmp_path / manifest["companies"][0]["packetPath"]).read_text())
    # The importer's validator accepts the surviving quote against the packet passage...
    checked = ser.validate({"gates": {"supply_chain_map": gate}}, packet["evidence"])["supply_chain_map"]
    assert checked["citationChecks"] == "exact-quote-matched"
    # ...and does not let a gate pass while evidence is listed as missing.
    assert checked["status"] == "partial"
