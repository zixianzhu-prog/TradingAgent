import early_signals as es

FORM_D = b"""<?xml version="1.0"?><edgarSubmission><primaryIssuer><entityName>Contrast Cube Inc.</entityName>
<yearOfInc><withinFiveYears>true</withinFiveYears><value>2026</value></yearOfInc></primaryIssuer>
<relatedPersonsList><relatedPersonInfo><relatedPersonName><firstName>Zachary</firstName><lastName>Manta</lastName></relatedPersonName>
<relatedPersonRelationshipList><relationship>Executive Officer</relationship></relatedPersonRelationshipList></relatedPersonInfo></relatedPersonsList>
<offeringData><industryGroup><industryGroupType>Other Health Care</industryGroupType></industryGroup>
<typeOfFiling><dateOfFirstSale><value>2026-10-13</value></dateOfFirstSale></typeOfFiling>
<typesOfSecuritiesOffered><isEquityType>true</isEquityType></typesOfSecuritiesOffered>
<offeringSalesAmounts><totalOfferingAmount>1000000</totalOfferingAmount><totalAmountSold>310000</totalAmountSold></offeringSalesAmounts></offeringData></edgarSubmission>"""


def test_parse_form_d():
    d = es.parse_form_d(FORM_D)
    assert d["industry"] == "Other Health Care" and d["sold"] == 310000 and d["offering"] == 1000000
    assert d["young"] and d["firstSale"] == "2026-10-13" and d["people"] == [{"name": "Zachary Manta", "roles": ["Executive Officer"]}]


def test_news_mentions_need_the_full_name():
    texts = ["frontier ai model released today", "bighat biosciences raises series c", "contrast agents for mri"]
    assert es.news_mentions("Frontier Bio Corp", texts) == 0
    assert es.news_mentions("BigHat Biosciences, Inc.", texts) == 1
    assert es.news_mentions("Contrast Cube Inc.", texts) == 0


def test_departure_filter_rejects_compensation_clauses():
    real = "On October 22, 2026, Jeannette Bankes notified GE HealthCare that she will resign as President and CEO, Patient Care Solutions."
    clause = "Assumed awards will vest in full upon a qualifying termination, death or disability (subject to the Co-CEO's release)."
    ok = lambda s: bool(es.DEPARTURE.search(s) and es.KEY_ROLE.search(s) and not es.HYPOTHETICAL.search(s))
    assert ok(real) and not ok(clause)


def test_insider_buys_keep_open_market_purchases_only():
    snap = {"marketTransactions": [
        {"ticker": "ABCL", "isOpenMarket": True, "code": "P", "date": "2026-11-13", "owner": "Booth Andrew", "roles": ["高管", "Chief Financial Officer"], "shares": 8600, "price": 11.33, "value": 97438, "url": "u1"},
        {"ticker": "TEM", "isOpenMarket": True, "code": "S", "date": "2026-11-12", "owner": "X", "roles": ["董事"], "value": 1000, "url": "u2"},
        {"ticker": "TEM", "isOpenMarket": False, "code": "M", "date": "2026-11-12", "owner": "Y", "roles": [], "value": 5, "url": "u3"}]}
    from datetime import date
    out = es.insider_buys(snap, date(2026, 10, 17))
    assert [b["owner"] for b in out["ABCL"]["buys"]] == ["Booth Andrew"] and out["ABCL"]["buys"][0]["roles"] == ["Officer", "Chief Financial Officer"]
    assert out["TEM"]["sellCount"] == 1 and out["TEM"]["buys"] == []
