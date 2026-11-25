from candidate_filter import ai_sentences, check


def base(**kw):
    c = {"track": "ai", "aiProduct": {"verdict": "core", "use": "medical_decision"}, "fdaAiDevices": 1, "revenueM": 50,
         "dealOrInd": False, "trials": 0, "marketCapM": 500, "advUsdM": 3, "price": 10, "runwayMonths": 30, "raisedM": 20,
         "segment": "Diagnostics"}
    c.update(kw)
    return c


def test_clean_company_passes():
    assert check(base())["pass"]


def test_marketing_ai_fails_first_check():
    r = check(base(aiProduct={"verdict": "marketing", "use": "other"}))
    assert not r["pass"] and r["firstFailure"].startswith("AI is marketing")


def test_drug_track_skips_ai_but_needs_evidence_and_survival():
    r = check(base(track="drug", aiProduct=None, fdaAiDevices=0, revenueM=0, dealOrInd=True))
    assert r["pass"]
    r = check(base(track="drug", aiProduct=None, fdaAiDevices=0, revenueM=0, dealOrInd=False, trials=0))
    assert not r["pass"] and "no FDA device" in r["firstFailure"]


def test_survival_flags_runway_price_dilution():
    r = check(base(runwayMonths=3, price=0.8, raisedM=600))
    d = next(x for x in r["checks"] if x["check"] == "survivable")["detail"]
    assert "cash for 3 months" in d and "delisting" in d and "120%" in d


def test_tradable_threshold():
    assert not check(base(marketCapM=40))["pass"]
    assert not check(base(advUsdM=0.2))["pass"]


def test_ai_sentences_pick_only_ai_text():
    text = "We sell beds to hospitals across the region. Our machine learning model reads chest CT scans for nodules."
    assert ai_sentences(text) == ["Our machine learning model reads chest CT scans for nodules."]


def test_feature_ai_needs_fda_device():
    assert not check(base(aiProduct={"verdict": "feature", "use": "research_development"}, fdaAiDevices=0))["pass"]
    assert check(base(aiProduct={"verdict": "feature", "use": "clinical_workflow"}, fdaAiDevices=2))["pass"]


def test_queue_is_ai_only():
    import candidate_filter as cf
    passed = [{"ticker": "IRD", "track": "drug", "marketCapM": 400}, {"ticker": "CARL", "track": "ai", "marketCapM": 500},
              {"ticker": "ISRG", "track": "ai", "marketCapM": 150000}]
    assert cf.deep_review_queue(passed) == ["CARL"]
