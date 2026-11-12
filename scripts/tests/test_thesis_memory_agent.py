from thesis_memory_agent import compare, load_reflections, memory_event, update_memory


def company(rank=1, decision="research-ready", forecast=0.01):
    return {
        "ticker": "TEST", "rank": rank, "classification": "candidate",
        "serenityDecision": decision, "completenessScore": 90,
        "valuationLabel": "watch", "fundingRisk": "low", "priceToSales": 5,
        "price": 10, "forecastReturn": forecast,
        "layers": {"shallow": {}, "intermediate": {"events": []}, "deep": {}},
    }


def test_compare_records_only_tracked_decision_fields():
    changes = compare(company(), company(rank=2, decision="revalidate"))
    assert {row["field"] for row in changes} == {"rank", "serenityDecision"}


def test_memory_deduplicates_identical_snapshot():
    snapshot = {"generatedAt": "a", "companies": {"TEST": company()}}
    first = update_memory({}, snapshot)
    second = update_memory(first, {"generatedAt": "b", "companies": {"TEST": company()}})
    assert second["summary"]["snapshots"] == 1
    assert second["summary"]["changedCompanies"] == 0


def test_memory_records_change_and_related_event():
    first = update_memory({}, {"generatedAt": "a", "companies": {"TEST": company()}})
    changed = company(decision="revalidate")
    changed["layers"]["intermediate"]["events"] = [{"title": "10-Q", "affectedGates": ["earnings_validation"]}]
    second = update_memory(first, {"generatedAt": "b", "companies": {"TEST": changed}})
    assert second["summary"]["snapshots"] == 2
    assert second["latest"]["changesFromPrevious"][0]["ticker"] == "TEST"


def test_memory_ids_are_stable_and_source_aware():
    first = memory_event("TEST", "deep", "thesis", "claim", 3, ["https://example.com"])
    second = memory_event("TEST", "deep", "thesis", "claim", 3, ["https://example.com"])
    assert first["id"] == second["id"]
    assert first["sources"] == ["https://example.com"]


def test_load_reflections_keeps_latest_prediction_per_horizon(tmp_path):
    database = tmp_path / "history.db"
    connection = __import__("sqlite3").connect(database)
    connection.execute(
        """CREATE TABLE benchmark_outcomes (
        ticker TEXT, prediction_as_of TEXT, horizon INTEGER, target_as_of TEXT,
        realized_return REAL, excess_spy REAL, excess_xlv REAL,
        xbi_return REAL, excess_xbi REAL, direction_correct INTEGER)"""
    )
    connection.executemany(
        "INSERT INTO benchmark_outcomes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            ("TEST", "2026-01-01", 5, "2026-01-08", .10, .08, .07, .04, .06, 1),
            ("TEST", "2026-01-02", 5, "2026-01-09", .05, .03, .02, .04, .01, 1),
            ("TEST", "2026-01-01", 20, "2026-02-01", -.02, -.03, -.01, .01, -.03, 0),
        ],
    )
    connection.commit()
    connection.close()
    rows = load_reflections(database)["TEST"]
    assert len(rows) == 2
    assert next(row for row in rows if row["horizon"] == 5)["prediction_as_of"] == "2026-01-02"
