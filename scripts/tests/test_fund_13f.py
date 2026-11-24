import fund_13f as f


def test_issuer_key_matches_truncated_13f_names():
    assert f.issuer_key("TEMPUS AI INC") == f.issuer_key("Tempus AI, Inc.") == "tempus ai"
    assert f.issuer_key("CARIS LIFE SCIENCES INC") == f.issuer_key("Caris Life Sciences, Ltd.")


def test_positions_skip_options_and_sum():
    rows = [{"issuer": "TEMPUS AI INC", "shares": 100, "value": 5, "putCall": None},
            {"issuer": "TEMPUS AI INC", "shares": 50, "value": 2, "putCall": None},
            {"issuer": "TEMPUS AI INC", "shares": 999, "value": 9, "putCall": "Call"},
            {"issuer": "UNRELATED CO", "shares": 1, "value": 1, "putCall": None}]
    out = f.positions(rows, {"tempus ai": "TEM"})
    assert out == {"TEM": {"shares": 150, "value": 7, "issuer": "TEMPUS AI INC"}}


def test_change_labels():
    assert f.change({"shares": 10}, None) == "new"
    assert f.change(None, {"shares": 10}) == "exited"
    assert f.change({"shares": 12}, {"shares": 10}) == "added"
    assert f.change({"shares": 8}, {"shares": 10}) == "trimmed"
    assert f.change({"shares": 10.5}, {"shares": 10}) == "held"
