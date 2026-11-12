from clinical_trials_agent import compare, normalize


def sample_study(status="RECRUITING"):
    return {
        "protocolSection": {
            "identificationModule": {"nctId": "NCT1", "briefTitle": "Trial"},
            "statusModule": {"overallStatus": status, "studyLastUpdatePostDateStruct": {"date": "2026-11-10"}},
            "designModule": {"phases": ["PHASE2"], "enrollmentInfo": {"count": 50}},
            "conditionsModule": {"conditions": ["Condition"]},
            "sponsorCollaboratorsModule": {"leadSponsor": {"name": "Sponsor"}},
        }
    }


def test_normalize_extracts_auditable_fields():
    row = normalize(sample_study(), "TEST", "ASSET")
    assert row["nctId"] == "NCT1"
    assert row["status"] == "RECRUITING"
    assert row["enrollment"] == 50
    assert row["url"].endswith("NCT1")


def test_first_snapshot_is_baseline_not_false_event():
    row = normalize(sample_study(), "TEST", "ASSET")
    assert compare({}, [row], baseline=True) == []


def test_termination_creates_critical_revalidation():
    old = normalize(sample_study("RECRUITING"), "TEST", "ASSET")
    new = normalize(sample_study("TERMINATED"), "TEST", "ASSET")
    change = compare({"NCT1": old}, [new], baseline=False)[0]
    assert change["severity"] == "critical-review"
    assert "clinical_validation" in change["affectedGates"]
