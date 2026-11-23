import rnpv_valuation as rv


def test_approval_odds_match_bio_2011_2020_benchmarks():
    assert round(rv.approval_odds(1), 3) == 0.079
    assert round(rv.approval_odds(2), 3) == 0.151
    assert round(rv.approval_odds(3), 3) == 0.524


def test_value_is_linear_in_peak_sales_and_implied_peak_round_trips():
    c = {"ticker": "X", "company": "X", "price": 5.0, "marketCapM": 500, "sharesM": 100, "cashM": 200,
         "burnPerYearM": 40, "phase": 3}
    out = rv.value(c, {"bear": 150, "base": 500, "bull": 1500})
    k, cost = out["valuePerPeakDollar"], out["developmentCostPvM"]
    assert abs((200 - cost + k * out["impliedPeakSalesM"]) - 500) < 1
    assert out["orderRange"]["floor"] <= out["orderRange"]["upper"]
    assert out["valuePerShare"]["bear"] < out["valuePerShare"]["base"] < out["valuePerShare"]["bull"]


def test_platforms_and_companies_without_trials_get_no_usable_range():
    base = {"price": 5.0, "marketCapM": 500, "sharesM": 100, "cashM": 200, "burnPerYearM": 40}
    payload = rv.build([{"ticker": "P", "company": "P", "phase": 2, "platform": True, **base},
                        {"ticker": "D", "company": "D", "phase": 2, **base},
                        {"ticker": "N", "company": "N", "phase": None, **base}], {})
    rows = {r["ticker"]: r for r in payload["companies"]}
    assert rows["P"]["rangeUsable"] is False and rows["D"]["rangeUsable"] is True
    assert payload["skipped"][0]["ticker"] == "N"
    assert rows["D"]["inputsVerified"] is False


def test_override_with_source_replaces_priors():
    base = {"ticker": "D", "company": "D", "phase": 3, "price": 5.0, "marketCapM": 500, "sharesM": 100, "cashM": 200, "burnPerYearM": 40}
    payload = rv.build([base], {"D": {"peakSalesM": {"base": 900}, "source": "10-K market size"}})
    row = payload["companies"][0]
    assert row["peakSalesM"]["base"] == 900 and row["inputsVerified"] is True


def test_bottom_up_peaks_and_short_runway_gate():
    o = {"patients": {"value": 10_000_000}, "netPricePerYearUsd": 1500, "penetration": {"bear": 0.005, "base": 0.015, "bull": 0.04}}
    assert rv.override_peaks(o) == {"bear": 75.0, "base": 225.0, "bull": 600.0}
    c = {"ticker": "H", "company": "H", "phase": 3, "price": 1.0, "marketCapM": 50, "sharesM": 50, "cashM": 2, "burnPerYearM": 24}
    row = rv.build([c], {})["companies"][0]
    assert row["rangeUsable"] is False and any("raised money" in n for n in row["notes"])


def test_terminated_phase3_does_not_count(tmp_path, monkeypatch):
    import json
    import small_cap_stage as scs
    monkeypatch.setattr(scs, "TRIALS_CACHE", tmp_path)
    def study(nct, phase, status):
        return {"protocolSection": {"identificationModule": {"nctId": nct, "briefTitle": nct},
                                    "sponsorCollaboratorsModule": {"leadSponsor": {"name": "Acme Bio"}},
                                    "statusModule": {"overallStatus": status, "startDateStruct": {"date": "2025-01"}},
                                    "designModule": {"phases": [phase]}}}
    (tmp_path / "acme-bio.json").write_text(json.dumps([study("N3", "PHASE3", "TERMINATED"), study("N2", "PHASE2", "RECRUITING")]))
    lead = rv.lead_trial("Acme Bio, Inc.")
    assert lead["nct"] == "N2" and lead["phase"] == 2


def test_one_time_therapy_spreads_the_pool_over_ten_years():
    o = {"patients": {"value": 1000}, "netPricePerYearUsd": 3_000_000, "penetration": {"bear": 0.1, "base": 0.1, "bull": 0.1},
         "oneTimeTherapy": True}
    assert rv.override_peaks(o)["base"] == 30.0


def test_royalty_economics_cut_value_versus_selling_it_yourself():
    own = rv.value_per_peak_dollar(3)
    royalty = rv.value_per_peak_dollar(3, margin=0.15, years=11)
    assert royalty < own * 0.4
    assert rv.economics_of({"economics": {"type": "royalty", "rate": 0.15}}, 3) == (0.15, rv.LIFE)
    assert rv.economics_of({}, 3) == (rv.MARGIN, rv.LIFE)
