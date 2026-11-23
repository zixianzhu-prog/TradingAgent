import live_demo


def test_phrases_strip_ai_words_from_the_typed_topic():
    phrases, core, _ = live_demo.phrases_for("AI digital pathology")
    assert core == "digital pathology"
    assert phrases[0] == '"artificial intelligence" "digital pathology"'


def test_labels_cover_every_relation_the_classifier_returns():
    for relation in ("own-product", "supplier", "customer", "competition", "topic-absent", "glossary", "mention", "not-in-filing", "unread"):
        assert relation in live_demo.LABELS
