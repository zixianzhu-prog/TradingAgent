import rnpv_patients as rp

TEXT = "Intro. Merkel cell carcinoma affects approximately 3,000 people in the United States each year. Other text."


def test_passages_keep_only_patient_count_sentences():
    out = rp.passages(TEXT)
    assert out == ["Merkel cell carcinoma affects approximately 3,000 people in the United States each year."]


def test_override_requires_verbatim_quote_and_applies_covered_share():
    answer = {"found": True, "patients": 3000, "scope": "US annual incidence", "addressableShare": 0.5,
              "quote": "Merkel cell carcinoma affects approximately 3,000 people in the United States each year.",
              "netPricePerYearUsd": 150000, "penetration": {"bear": 0.05, "base": 0.15, "bull": 0.3}}
    o = rp.to_override(answer, TEXT, "u", {"title": "T", "nct": "N"})
    assert o["patients"]["value"] == 1500 and o["netPricePerYearUsd"] == 150000
    assert rp.to_override({**answer, "quote": "Merkel affects 30,000 people."}, TEXT, "u", {}) is None
    assert rp.to_override({**answer, "found": False}, TEXT, "u", {}) is None


def test_economics_need_verbatim_quote_and_use_range_midpoint():
    text = "We granted Partner Co an exclusive license in the United States. We receive tiered royalties from 10% to 20% on net sales."
    a = {"partnered": True, "partner": "Partner Co", "royaltyLow": 0.10, "royaltyHigh": 0.20,
         "quote": "We receive tiered royalties from 10% to 20% on net sales."}
    e = rp.to_economics(a, text, "u")
    assert e["type"] == "royalty" and e["rate"] == 0.15 and e["rateAssumed"] is False
    assert rp.to_economics({**a, "quote": "made up"}, text, "u") is None
    assert rp.to_economics({**a, "partnered": False}, text, "u") is None
    e2 = rp.to_economics({"partnered": True, "quote": "We granted Partner Co an exclusive license in the United States."}, text, "u")
    assert e2["rate"] == rp.UNDISCLOSED_RATE and e2["rateAssumed"] is True
