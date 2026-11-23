import validate_topic_mapping as v

PAIR = ['"artificial intelligence" "radiology"']


def test_nearest_passage_prefers_the_tightest_span():
    text = "artificial intelligence appears here. " + "filler " * 400 + "our radiology artificial intelligence platform."
    span, passage = v.nearest_passage(text, PAIR)
    assert span < 60 and "platform" in passage


def test_relation_classification():
    cases = {
        "We have developed a proprietary artificial intelligence platform for radiology.": "own-product",
        "Companies using artificial intelligence in radiology could create more competition for us.": "competition",
        "“AI” means artificial intelligence. Radiology services.": "glossary",
    }
    for text, expected in cases.items():
        span, passage = v.nearest_passage(text, PAIR)
        assert v.classify(passage, span) == expected, text
    assert v.classify("", -1) == "not-in-filing"
    assert v.classify("artificial intelligence ... radiology", v.FAR_APART + 1) == "unrelated"


def test_recall_uses_only_makers_with_enough_devices():
    truth = {"Radiology": {"GEHC": ["K1", "K2"], "ONE": ["K3"], "RDNT": ["K4", "K5"]}}
    out = v.recall("imaging", {"GEHC", "XYZ"}, truth)
    assert out["truth"] == ["GEHC", "RDNT"] and out["missed"] == ["RDNT"] and out["recall"] == 0.5
    assert v.recall("remote_care", {"A"}, truth) is None


def test_filing_level_classifier_handles_diversified_and_shell_companies():
    diversified = ("Our imaging segment sells CT and MRI systems. " * 20 + "filler " * 3000
                   + "We have developed AI-enabled software for our imaging products.")
    shell = "We are an artificial intelligence holding company investing in generative AI start-ups."
    competitor = "radiology " * 5 + "Companies using artificial intelligence in radiology pose competitive threats to our business."
    assert v.classify_filing(diversified, "imaging")["relation"] == "own-product"
    assert v.classify_filing(shell, "imaging")["relation"] == "topic-absent"
    assert v.classify_filing(competitor, "imaging")["relation"] == "competition"
    robotics = "robotic surgery " * 4 + "We market our surgical robot to hospitals."
    assert v.classify_filing(robotics, "robotics")["relation"] == "own-product"


def test_exposure_relation_filter_drops_competitors(monkeypatch):
    import topic_exposure as te
    import prepare_claude_review as c
    texts = {"u1": "radiology " * 4 + "We have developed our AI platform for radiology.",
             "u2": "radiology " * 4 + "Competitors use artificial intelligence, which could adversely affect us."}
    monkeypatch.setattr(c, "filing_text", lambda url, allow_fetch=False: texts[url])
    found = {"A": {"company": "A", "filings": 4, "url": "u1", "strength": 1.0}, "B": {"company": "B", "filings": 4, "url": "u2", "strength": 1.0}}
    kept = te.read_relations(found, "imaging")
    assert list(kept) == ["A"] and kept["A"]["relation"] == "own-product"
