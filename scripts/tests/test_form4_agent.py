from datetime import date

from form4_agent import build, parse_form4


SAMPLE = b"""<ownershipDocument><periodOfReport>2026-11-01</periodOfReport><issuer><issuerName>Test Co</issuerName></issuer><reportingOwner><reportingOwnerId><rptOwnerName>Jane Doe</rptOwnerName></reportingOwnerId><reportingOwnerRelationship><isOfficer>1</isOfficer><officerTitle>CEO</officerTitle></reportingOwnerRelationship></reportingOwner><nonDerivativeTable><nonDerivativeTransaction><securityTitle><value>Common Stock</value></securityTitle><transactionDate><value>2026-11-01</value></transactionDate><transactionCoding><transactionCode>P</transactionCode></transactionCoding><transactionAmounts><transactionShares><value>100</value></transactionShares><transactionPricePerShare><value>12.50</value></transactionPricePerShare><transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode></transactionAmounts><postTransactionAmounts><sharesOwnedFollowingTransaction><value>1100</value></sharesOwnedFollowingTransaction></postTransactionAmounts></nonDerivativeTransaction><nonDerivativeTransaction><securityTitle><value>Common Stock</value></securityTitle><transactionDate><value>2026-11-01</value></transactionDate><transactionCoding><transactionCode>A</transactionCode></transactionCoding><transactionAmounts><transactionShares><value>50</value></transactionShares><transactionAcquiredDisposedCode><value>A</value></transactionAcquiredDisposedCode></transactionAmounts></nonDerivativeTransaction></nonDerivativeTable></ownershipDocument>"""


def test_parse_distinguishes_purchase_from_award():
    result = parse_form4(SAMPLE, {"ticker": "TEST", "accession": "1", "filingDate": "2026-11-02", "url": "u", "rawUrl": "r"})
    assert result["owner"] == "Jane Doe"
    assert result["transactions"][0]["value"] == 1250
    assert result["transactions"][0]["isOpenMarket"] is True
    assert result["transactions"][1]["isOpenMarket"] is False


def test_first_run_is_baseline_and_second_run_alerts_new_filing():
    config = {"lookback_days": 120, "companies": [{"ticker": "TEST", "cik": "1"}]}
    submissions = b'{"filings":{"recent":{"form":["4"],"accessionNumber":["0000000001-26-000001"],"filingDate":["2026-11-02"],"primaryDocument":["xslF345X06/test.xml"]}}}'
    def fetcher(url):
        return submissions if "submissions" in url else SAMPLE
    first = build(config, None, date(2026, 11, 10), fetcher)
    assert first["mode"] == "baseline"
    assert first["summary"]["newFilings"] == 0
    previous = {"knownAccessions": []}
    second = build(config, previous, date(2026, 11, 10), fetcher)
    assert second["summary"]["newFilings"] == 1
    assert second["summary"]["openMarketTransactions"] == 1
