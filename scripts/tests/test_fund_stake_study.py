from fund_stake_study import events, pairs


def test_pairs_match_filer_and_subject_by_accession_and_skip_amendments():
    lines = [
        "1224962|PERCEPTIVE ADVISORS LLC|SC 13D|2023-02-02|edgar/data/1224962/0001193125-23-022824.txt",
        "1300699|Athenex, Inc.|SC 13D|2023-02-02|edgar/data/1300699/0001193125-23-022824.txt",
        "1000097|KINGDON CAPITAL|SC 13G|2023-01-25|edgar/data/1000097/0000919574-23-000469.txt",
        "1300699|Athenex, Inc.|SC 13G|2023-01-25|edgar/data/1300699/0000919574-23-000469.txt",
        "1224962|PERCEPTIVE ADVISORS LLC|SC 13D/A|2023-03-02|edgar/data/1224962/0001193125-23-099999.txt",
        "1300699|Athenex, Inc.|SC 13D/A|2023-03-02|edgar/data/1300699/0001193125-23-099999.txt",
    ]
    got = sorted(pairs(lines, {"1300699"}), key=lambda r: r["filed"])
    assert [(r["filer"], r["specialist"]) for r in got] == [("KINGDON CAPITAL", None), ("PERCEPTIVE ADVISORS LLC", "Perceptive")]


def test_events_one_per_company_and_group_within_30_days():
    rows = [{"cik": "1", "filed": "2023-01-01", "form": "SC 13G", "filer": "A", "specialist": "RA Capital", "accession": "a"},
            {"cik": "1", "filed": "2023-01-10", "form": "SC 13D", "filer": "B", "specialist": "Perceptive", "accession": "b"},
            {"cik": "1", "filed": "2023-01-12", "form": "SC 13G", "filer": "C", "specialist": None, "accession": "c"}]
    e = events(rows)
    assert [(x["group"], x["kind"]) for x in e] == [("specialist fund", "13G"), ("other institution", "13G")]
