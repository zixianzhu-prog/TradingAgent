from datetime import date

from institutional_ownership_agent import build, filing_rows, parse_filing


def test_filing_rows_only_keeps_recent_13d_13g():
    recent = {"form": ["SC 13G", "10-K", "SC 13D/A"], "accessionNumber": ["a-1", "a-2", "a-3"],
              "filingDate": ["2026-10-01", "2026-10-02", "2024-01-01"], "primaryDocument": ["g.htm", "k.htm", "d.htm"]}
    rows = filing_rows({"filings": {"recent": recent}}, "TEST", "123", date(2026, 1, 1))
    assert len(rows) == 1 and rows[0]["form"] == "SC 13G"


def test_parse_structured_ownership_fields():
    raw = "<html><body>NAME OF REPORTING PERSON BlackRock, Inc. CHECK THE APPROPRIATE BOX PERCENT OF CLASS REPRESENTED BY AMOUNT IN ROW (11) 6.4%</body></html>"
    row = parse_filing(raw, {"form": "SC 13G", "ticker": "TEST"})
    assert row["reportingPerson"] == "BlackRock, Inc."
    assert row["percent"] == 6.4
    assert row["intentClass"] == "passive-or-qualified-institution"


def test_missing_user_agent_is_pending_not_zero_ownership():
    result = build([{"ticker": "TEST", "cik": "123", "company": "Test"}], 365, "", today=date(2026, 11, 23))
    assert result["status"] == "pending-config"
    assert result["summary"]["filings"] == 0
    assert "not evidence" in result["requiredAction"]


def test_new_format_xml_reads_filer_percent_and_specialist():
    from institutional_ownership_agent import raw_url
    raw = ("<edgarSubmission><coverPageHeader><issuerInfo><issuerName>X</issuerName></issuerInfo></coverPageHeader>"
           "<reportingPersonInfo><reportingPersonName>RA Capital Management, L.P.</reportingPersonName>"
           "<classPercent>9.8</classPercent><typeOfReportingPerson>IA</typeOfReportingPerson></reportingPersonInfo>"
           "<reportingPersonInfo><reportingPersonName>Peter Kolchinsky</reportingPersonName><classPercent>9.8</classPercent>"
           "</reportingPersonInfo></edgarSubmission>")
    row = parse_filing(raw, {"form": "SCHEDULE 13G", "ticker": "X"})
    assert row["reportingPerson"] == "RA Capital Management, L.P." and row["percent"] == 9.8
    assert row["specialistFund"] == "RA Capital" and row["initial"] is True
    assert parse_filing(raw, {"form": "SCHEDULE 13G/A", "ticker": "X"})["initial"] is False
    assert raw_url("https://www.sec.gov/Archives/edgar/data/1/0001/xslSCHEDULE_13G_X02/primary_doc.xml") == \
        "https://www.sec.gov/Archives/edgar/data/1/0001/primary_doc.xml"


def test_covered_companies_get_cik_from_ticker_file():
    from institutional_ownership_agent import universe
    out = universe({"themes": {"ai_medicine": [{"ticker": "TEM", "company": "Tempus"}]}}, {}, {"TEM": "1717115"})
    assert out == [{"ticker": "TEM", "company": "Tempus", "cik": "1717115"}]


def test_item4_prose_in_percent_tag_is_ignored():
    raw = ("<reportingPersonName>Biotechnology Value Fund L P</reportingPersonName><classPercent>4.4</classPercent>"
           "<classPercent>8.4</classPercent><classPercent>The following percentages are based on 111,656,919 Shares "
           "outstanding</classPercent><classPercent>The information in Item 11 of each cover page</classPercent>")
    assert parse_filing(raw, {"form": "SCHEDULE 13G", "ticker": "X"})["percent"] == 8.4
