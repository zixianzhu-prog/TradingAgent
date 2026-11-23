import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fda_crl_reasons as crl  # noqa: E402

PROSE = """U.S. Food & Drug Administration
Our STN: BL 125827 COMPLETE RESPONSE
  APRIL 10, 2026

Replimune, Inc.
Attention: Kari Jeschke
500 Unicorn Park Drive

Dear Kari Jeschke:

Please refer to your Biologics License Application (BLA) received ,
for vusolimogene oderparepvec, submitted under section 351(a) of the Public Health Service Act.
The review team unanimously determined data presented are insufficient to conclude substantial evidence of effectiveness of vusolimogene oderparepvec.
To address this deficiency, conduct an additional adequate and well-controlled clinical trial. We reserve comment on the proposed labeling until the application is otherwise adequate.
"""

SECTIONED = """NDA 018680/S-074
COMPLETE RESPONSE
CooperSurgical, Inc.
Attention: Regina Shih
Dear Regina Shih:
Please refer to your supplemental new drug application (sNDA) dated and received February 28, 2023, submitted under section 505(b) of the Federal Food, Drug, and Cosmetic Act for Paragard (intrauterine copper contraceptive).
FACILITY INSPECTIONS
During our recent inspection of the CooperSurgical, Inc, manufacturing facility, our field investigator conveyed deficiencies to the representative of the facility. Satisfactory inspection is required before this application may be approved.
PRESCRIBING INFORMATION
We reserve comment on the proposed labeling until the application is otherwise adequate.
SAFETY UPDATE
When you respond to the above deficiency, include a safety update describing serious adverse events and deaths.
"""


def test_prose_letter_is_heavy_with_a_citation_and_new_trial():
    v = crl.classify(PROSE)
    assert v["severity"] == "heavy" and v["newTrialRequired"]
    assert "substantial evidence of effectiveness" in v["reasons"]["efficacy"]["quote"]
    assert v["reasons"]["efficacy"]["quote"] in PROSE.replace("\n", " ")  # citation is the letter's own sentence


def test_sectioned_letter_counts_only_deficiency_sections():
    v = crl.classify(SECTIONED)
    assert v["severity"] == "light" and list(v["reasons"]) == ["manufacturing"]
    assert v["facilityInspectionFailed"] and not v["newTrialRequired"]
    assert "safety" not in v["reasons"]  # the SAFETY UPDATE boilerplate is not a reason


def test_metadata_from_new_and_old_filenames():
    new = crl.metadata("CRL_BLA125827_20260410.pdf", PROSE)
    assert new == {"application": "BLA 125827", "issued": "2026-04-10", "company": "Replimune, Inc",
                   "drug": "vusolimogene oderparepvec", "metadataSource": "letter"}
    old = crl.metadata("018680-s074_OtherActionLtrs.pdf", SECTIONED)
    assert old["application"] == "NDA 018680" and old["company"] == "CooperSurgical, Inc" and old["drug"].startswith("Paragard")


def test_redacted_letter_is_flagged_not_unknown():
    text = "NDA 217294\nPage 2\n" + "(b) (4)\n" * 8 + "SAFETY UPDATE\nWhen you respond to the above deficiencies, include a safety update."
    v = crl.classify(text)
    assert v["severity"] == "redacted" and v["redacted"]


def test_ticker_match_ignores_corporate_suffixes():
    tickers = {crl.normalize("Trevena, Inc."): {"ticker": "TRVN"}, crl.normalize("Replimune Group, Inc."): {"ticker": "REPL"}}
    assert crl.match_tickers("Trevena, Inc", tickers)["ticker"] == "TRVN"
    assert crl.match_tickers("Replimune, Inc.", tickers)["ticker"] == "REPL"
    assert crl.match_tickers("Food and Drug Administration", tickers) is None


def test_crl_letter_becomes_recheck_task_scaled_by_severity():
    from datetime import date
    import event_revalidation_agent as era

    config = {"materiality_threshold": 60, "crl_lookback_days": 180, "event_keywords": {},
              "companies": [{"ticker": "RXRX", "aliases": ["Recursion", "REC-4881"], "events": []},
                            {"ticker": "TEM", "aliases": ["Tempus"], "events": []}]}
    letter = {"file": "CRL_NDA999_20261101.pdf", "issued": "2026-11-01", "company": "Partner Bio",
              "drug": "REC-4881", "severity": "heavy", "newTrialRequired": True,
              "newTrialQuote": "conduct an adequate and well-controlled trial",
              "reasons": {"efficacy": {"sentences": 4, "quote": "did not demonstrate"}},
              "listed": None, "source": "https://download.open.fda.gov/unapproved_CRLs.zip"}
    old = {**letter, "file": "old.pdf", "issued": "2025-01-01"}
    light = {**letter, "file": "light.pdf", "drug": "X", "company": "Tempus AI", "severity": "light", "newTrialRequired": False}
    payload = era.build(config, [], date(2026, 11, 17), {"rows": [letter, old, light]})
    tasks = {t["ticker"]: t for t in payload["revalidationTasks"]}
    assert set(tasks) == {"RXRX", "TEM"}                      # the 2025 letter is outside the window
    assert tasks["RXRX"]["materialityScore"] > tasks["TEM"]["materialityScore"]
    assert "clinical_validation" in tasks["RXRX"]["affectedGates"]
    assert "clinical_validation" not in tasks["TEM"]["affectedGates"]
    assert "FDA 要求新试验" in tasks["RXRX"]["reasons"]
    assert tasks["RXRX"]["crl"]["quotes"]["efficacy"] == "did not demonstrate"
