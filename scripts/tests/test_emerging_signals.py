from datetime import datetime, timedelta, timezone

import beneficiary_mapper as mapper
import emerging_signal_detector as detector
from replay_case import confirm_topics, merge_maps

AS_OF = datetime(2020, 1, 26, 23, 59, tzinfo=timezone.utc)


def doc(i, source, title, days_ago, ingested_days_ago=None):
    at = AS_OF - timedelta(days=days_ago)
    ingested = AS_OF - timedelta(days=ingested_days_ago if ingested_days_ago is not None else days_ago)
    return detector.Doc(f"d{i}", source, title, "", at, detector.extract_terms(title), ingested)


def background(n=80):
    topics = ["protein folding dynamics", "gut microbiome diversity", "tumour immune profiling", "antibiotic resistance genes"]
    return [doc(i, ("medRxiv", "bioRxiv")[i % 2], topics[i % 4], 4 + i % 20) for i in range(n)]


def test_extract_terms_drops_boilerplate_and_keeps_phrases():
    terms = detector.extract_terms("Moderna shares rise as novel coronavirus spreads, analyst says")
    assert "coronavirus" in terms and "novel coronavirus" in terms
    assert "shares" not in terms and "analyst" not in terms and "novel" not in terms


def test_new_topic_bursts_across_sources():
    docs = background() + [doc(100 + i, ("medRxiv", "bioRxiv")[i % 2], f"2019-nCoV coronavirus outbreak estimate {i}", i % 3) for i in range(6)]
    payload = detector.detect(docs, AS_OF)
    labels = [s["label"] for s in payload["signals"]]
    assert any("coronavirus" in label or "ncov" in label for label in labels)
    top = payload["signals"][0]
    assert top["novel"] and top["sourceCount"] == 2 and top["authoritySource"]


def test_single_source_or_rare_topic_does_not_fire():
    docs = background() + [doc(200 + i, "bioRxiv", "coronavirus outbreak estimate", 1) for i in range(6)]
    assert detector.detect(docs, AS_OF)["signals"] == []  # only one source
    # Two sources but only two articles: below the minimum article count.
    docs = background() + [doc(300, "bioRxiv", "coronavirus outbreak", 1), doc(301, "medRxiv", "coronavirus outbreak", 1)]
    assert detector.detect(docs, AS_OF)["signals"] == []


def test_newly_added_feed_backlog_is_not_a_burst():
    # A feed connected yesterday dumps 30 items about a term the baseline never saw.
    dump = [doc(400 + i, "New Feed", "quantum dot imaging", 1, ingested_days_ago=0) for i in range(30)]
    other = [doc(500 + i, "medRxiv", "quantum dot imaging", 1) for i in range(2)]
    payload = detector.detect(background() + dump + other, AS_OF)
    assert "New Feed" in payload["warmingUpSources"]
    assert payload["signals"] == []


def test_volume_normalisation_ignores_busy_days():
    # The recent window simply has more articles of every kind: nothing should spike.
    docs = background(80) + [doc(600 + i, ("medRxiv", "bioRxiv")[i % 2], ["protein folding dynamics", "gut microbiome diversity"][i % 2], i % 3) for i in range(40)]
    assert detector.detect(docs, AS_OF)["signals"] == []


def test_parse_display_name_and_sic_groups():
    who = mapper.parse_display_name("Moderna, Inc.  (MRNA)  (CIK 0001682852)")
    assert who == {"name": "Moderna, Inc.", "ticker": "MRNA", "cik": "1682852"}
    assert mapper.parse_display_name("MERIDIAN BIOSCIENCE INC  (CIK 0000794172)")["ticker"] is None
    assert mapper.sic_group(["2836"]) == "Therapeutics & vaccines"
    assert mapper.sic_group(["5810"]) == "Other sector"


def hit(name, sic, form, items, file_type, filed, adsh):
    return {"_id": f"{adsh}:doc.htm", "_source": {"display_names": [name], "sics": [sic], "form": form, "items": items,
                                                   "file_type": file_type, "file_date": filed, "adsh": adsh}}


def test_announcement_vs_earnings_mention_splits_beneficiaries_from_impacted():
    hits = [
        hit("Moderna, Inc.  (MRNA)  (CIK 0001682852)", "2836", "8-K", ["7.01"], "8-K", "2020-01-22", "a1"),
        hit("ALIGN TECHNOLOGY INC  (ALGN)  (CIK 0001097149)", "3842", "8-K", ["2.02", "9.01"], "EX-99.1", "2020-01-29", "a2"),
        hit("STARBUCKS CORP  (SBUX)  (CIK 0000829224)", "5810", "8-K", ["2.02", "9.01"], "EX-99.1", "2020-01-28", "a3"),
        hit("STARBUCKS CORP  (SBUX)  (CIK 0000829224)", "5810", "8-K", ["2.02", "9.01"], "8-K", "2020-01-28", "a3"),
    ]
    result = mapper.map_topic("coronavirus", AS_OF.date(), fetch=lambda url, agent: {"hits": {"hits": hits, "total": {"value": len(hits)}}}, include_trials=False)
    assert [r["ticker"] for r in result["candidates"]] == ["MRNA"]
    assert [r["ticker"] for r in result["mentionOnly"]] == ["ALGN"]
    assert [r["ticker"] for r in result["exposed"]] == ["SBUX"]
    assert result["exposed"][0]["earningsMentions"] == 1  # same filing's exhibits counted once


def test_edgar_failure_is_reported_not_raised():
    def broken(url, agent):
        raise OSError("network down")
    result = mapper.map_topic("coronavirus", AS_OF.date(), fetch=broken, include_trials=False)
    assert result["status"]["edgar"].startswith("error") and result["candidates"] == []


def test_context_classifier():
    assert mapper.classify_context("we entered a collaboration to develop a vaccine candidate against the novel coronavirus") == "capability"
    assert mapper.classify_context("the coronavirus outbreak caused store closure and adversely affected traffic") == "impact"


def test_confirmation_requires_two_days_and_merges_related_labels():
    days = [
        {"date": "2020-01-18", "signals": [{"label": "protocol", "related": [], "recent": 5}]},
        {"date": "2020-01-25", "signals": [{"label": "coronavirus", "related": ["novel coronavirus"], "recent": 4}]},
        {"date": "2020-01-26", "signals": [{"label": "ncov", "related": ["coronavirus ncov"], "recent": 4}]},
    ]
    confirmed = confirm_topics(days)
    assert len(confirmed) == 1  # one-day "protocol" blip is ignored
    assert confirmed[0]["confirmed"] == "2020-01-26"
    assert set(confirmed[0]["searchTerms"]) <= {"coronavirus", "ncov"}


def test_merge_maps_keeps_best_bucket_per_company():
    row = lambda ticker, score: {"ticker": ticker, "company": ticker, "cik": ticker, "score": score}
    a = {"topic": "ncov", "filingHits": 2, "status": {}, "candidates": [row("MRNA", 10)], "mentionOnly": [], "exposed": []}
    b = {"topic": "coronavirus", "filingHits": 6, "status": {}, "candidates": [], "mentionOnly": [row("MRNA", 3), row("ICCC", 4)], "exposed": []}
    merged = merge_maps([a, b], AS_OF.date())
    assert [r["ticker"] for r in merged["candidates"]] == ["MRNA"]
    assert [r["ticker"] for r in merged["mentionOnly"]] == ["ICCC"]
    assert merged["filingHits"] == 8


def test_daily_history_confirms_topic_on_second_run_with_fresh_articles(tmp_path):
    history_path = tmp_path / "history.json"

    def run(as_of, ids):
        payload = {"asOf": as_of, "signals": [{"label": "monkeypox", "relatedTerms": [], "recentArticles": len(ids),
                                               "baselineArticles": 0, "articleIds": ids, "headlines": []}]}
        detector.mark_confirmed(payload, detector.update_history(history_path, payload))
        return payload

    first = run("2022-05-20T23:59:00+00:00", ["a", "b", "c", "d"])
    assert first["signals"][0]["confirmed"] is False
    same = run("2022-05-21T23:59:00+00:00", ["a", "b", "c", "d"])  # overlapping window, nothing new
    assert same["signals"][0]["confirmed"] is False
    fresh = run("2022-05-22T23:59:00+00:00", ["c", "d", "e", "f"])
    assert fresh["signals"][0]["confirmed"] is True
    assert fresh["confirmedTopics"][0]["confirmed"] == "2022-05-22"


def test_replay_report_handles_silence(tmp_path):
    from replay_case import write_markdown

    payload = {"case": "quiet", "detection": None, "sources": ["db"], "benchmark": "XBI", "otherConfirmed": [],
               "groundTruth": {"term": "monkeypox", "firstInData": "2022-05-29", "articlesInWindow": 3,
                               "dailyCounts": {"2022-05-29": 2, "2022-06-03": 1}, "firedOn": []}}
    out = tmp_path / "quiet.md"
    write_markdown(payload, out)
    text = out.read_text(encoding="utf-8")
    assert "没有话题达到确认标准" in text and "从未报警" in text
