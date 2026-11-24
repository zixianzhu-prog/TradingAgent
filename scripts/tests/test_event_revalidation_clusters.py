import event_revalidation_agent as era


def task(day, source, title, kinds, score=60):
    return {"ticker": "NVDA", "publishedAt": f"{day}T12:00:00+00:00", "source": source, "title": title, "url": f"https://x/{title}",
            "eventTypes": kinds, "materialityScore": score, "affectedGates": ["management_governance"]}


def test_coverage_joins_company_release():
    tasks = [task("2026-11-12", "NVIDIA News", "NVIDIA Announces CEO Transition", ["leadership"], 70),
             task("2026-11-09", "CNBC", "Huang affair puts future at risk", ["leadership", "reputational"]),
             task("2026-11-13", "Yahoo Finance", "Huang resigns", ["leadership"]),
             task("2026-11-17", "NVIDIA News", "NVIDIA Announces Financial Results", ["earnings"], 75),
             task("2026-11-18", "CNN", "Four takeaways from earnings", ["earnings", "reputational"]),
             task("2026-11-03", "TradingKey", "Marvell merger", ["integration"], 65)]
    out = era.cluster_tasks(tasks, {"NVDA": ["NVIDIA"]})
    by = {t["title"]: t for t in out}
    assert len(out) == 3
    assert by["NVIDIA Announces CEO Transition"]["articles"] == 3 and by["NVIDIA Announces CEO Transition"]["primarySource"]
    assert by["NVIDIA Announces Financial Results"]["articles"] == 2
    assert not by["Marvell merger"]["primarySource"]


def test_wire_release_counts_as_primary_only_with_company_title():
    assert era.is_primary({"source": "GlobeNewswire", "title": "Tempus Announces Q3"}, ["Tempus"])
    assert not era.is_primary({"source": "GlobeNewswire", "title": "Analysts on Tempus"}, ["Tempus"])
    assert era.is_primary({"source": "SEC TEM 8-K", "title": "x"}, ["Tempus"])
