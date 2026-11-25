from datetime import date

import patent_status as ps


def app(kind="Utility", filed="2015-01-01", granted="2018-01-01", pta=100, events=(), status="Patented Case"):
    return {"applicationMetaData": {"applicationTypeLabelName": kind, "effectiveFilingDate": filed, "filingDate": filed,
                                    "grantDate": granted, "patentNumber": "1", "applicationStatusDescriptionText": status},
            "patentTermAdjustmentData": {"adjustmentTotalQuantity": pta}, "eventDataBag": [{"eventCode": e} for e in events]}


def test_expiry_rules():
    assert ps.expiry(app()) == date(2035, 1, 1) + (date(2035, 4, 11) - date(2035, 1, 1))
    assert ps.expiry(app(kind="Design", granted="2020-06-01")).year == 2035


def test_summary_counts_and_lapsed():
    s = ps.summarize([app(filed="2009-01-01", pta=0), app(filed="2016-01-01", events=("DIST",)),
                      app(filed="2010-01-01", status="Patent Expired Due to NonPayment of Maintenance Fees Under 37 CFR 1.362")],
                     40, date(2026, 11, 24))
    assert s["grantedTotal"] == 40 and s["utilitySampled"] == 2 and s["lapsed"] == 1
    assert s["expireBy2031"] == 1 and s["terminalDisclaimerShare"] == 0.5


def test_term_expired_patent_is_not_live():
    s = ps.summarize([app(filed="2004-01-01", pta=0), app(filed="2016-01-01")], 2, date(2026, 11, 24))
    assert s["utilitySampled"] == 1
