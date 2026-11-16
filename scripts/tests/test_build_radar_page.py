import json

from build_radar_page import counts_chart, render


def write(root, rel, payload):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_render_shows_hit_and_miss_and_empty_today(tmp_path):
    write(tmp_path, "state/emerging-signals.json", {"asOf": "2026-11-15T00:00:00+00:00", "articles": {"recent": 10, "baseline": 50}, "signals": [
        {"label": "<b>x</b>", "confirmed": False, "status": "new-topic", "recentArticles": 5, "baselineArticles": 1, "burstRatio": 4.0,
         "sourceCount": 3, "headlines": [{"title": "t", "url": "https://e.example"}]}]})
    write(tmp_path, "state/beneficiary-map.json", {"topics": []})
    days = [{"date": "2020-01-24", "signals": []}, {"date": "2020-01-25", "signals": []}, {"date": "2020-01-26", "signals": []}]
    write(tmp_path, "state/replay/hit.json", {
        "case": "hit", "benchmark": "XBI", "dailySignals": days,
        "detection": {"topic": "coronavirus", "firstFired": "2020-01-25", "confirmed": "2020-01-26"},
        "groundTruth": {"term": "coronavirus", "firstInData": "2020-01-24", "articlesInWindow": 3, "dailyCounts": {"2020-01-25": 2, "2020-01-26": 1}, "firedOn": ["2020-01-25", "2020-01-26"]},
        "mapping": {"candidates": [{"ticker": "MRNA", "company": "Moderna", "sicGroup": "Therapeutics & vaccines", "firstFiled": "2020-01-22"}]},
        "pricing": {"companies": {"MRNA": {"verdict": "partly priced"}}},
        "outcomes": {"MRNA": {"r30": 0.28, "r365": 5.68}, "XBI": {"r30": 0.02, "r365": 0.72}},
        "basket": {"365": {"n": 1, "mean": 5.68, "winners": 1, "benchmark": 0.72}}})
    write(tmp_path, "state/replay/miss.json", {"case": "miss", "dailySignals": days, "detection": None,
        "groundTruth": {"term": "monkeypox", "firstInData": None, "articlesInWindow": 0, "dailyCounts": {}, "firedOn": []}})
    page = render(tmp_path)
    assert "&lt;b&gt;x&lt;/b&gt;" in page and "<b>x</b>" not in page
    assert "No confirmed topic needs company mapping today" in page
    assert "Caught" in page and "Missed · stayed silent" in page
    assert "Partly priced" in page and "+568%" in page
    assert page.index("Caught") < page.index("Missed")  # hit first, but the miss is on the same page


def test_counts_chart_marks_fired_days_and_confirmation():
    truth = {"term": "ncov", "dailyCounts": {"2020-01-25": 2, "2020-01-26": 4}, "firedOn": ["2020-01-25", "2020-01-26"]}
    svg = counts_chart(truth, "2020-01-20", "2020-01-31", "2020-01-26")
    assert svg.count('class="bar"') == 2
    assert svg.count('class="fire"') == 2
    assert "confirmed 01-26" in svg
