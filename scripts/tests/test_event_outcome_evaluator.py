import sqlite3

from event_outcome_evaluator import collapse_episodes, evaluate


def test_consecutive_repeats_are_one_episode_and_direction_flip_is_new():
    rows = [
        {"ticker":"AAA","as_of":"2026-01-01","claim":"positive","numeric_value":0.5,"confidence_score":40},
        {"ticker":"AAA","as_of":"2026-01-03","claim":"positive","numeric_value":0.7,"confidence_score":70},
        {"ticker":"AAA","as_of":"2026-01-04","claim":"negative","numeric_value":-0.5,"confidence_score":80},
    ]
    episodes = collapse_episodes(rows)
    assert len(episodes) == 2
    assert episodes[0]["repeat_count"] == 2
    assert episodes[0]["max_confidence"] == 70
    assert episodes[1]["claim"] == "negative"


def test_only_mature_high_confidence_directional_episode_is_scored():
    c = sqlite3.connect(":memory:")
    c.executescript("""
      CREATE TABLE prediction_tasks (
        ticker TEXT, as_of TEXT, task_type TEXT, horizon_sessions INTEGER,
        claim TEXT, numeric_value REAL, confidence_score REAL,
        evidence_basis TEXT, recorded_at TEXT
      );
      CREATE TABLE benchmark_outcomes (
        ticker TEXT, prediction_as_of TEXT, horizon INTEGER, target_as_of TEXT,
        realized_return REAL, excess_xbi REAL
      );
    """)
    c.executemany("INSERT INTO prediction_tasks VALUES (?,?,?,?,?,?,?,?,?)", [
        ("UP","2026-01-01","event_impact",20,"positive",0.5,80,"{}","now"),
        ("LOW","2026-01-01","event_impact",20,"negative",-0.5,20,"{}","now"),
        ("NEUTRAL","2026-01-01","event_impact",20,"neutral",0,90,"{}","now"),
    ])
    c.execute("INSERT INTO benchmark_outcomes VALUES (?,?,?,?,?,?)",
              ("UP","2026-01-01",20,"2026-02-01",0.12,0.08))
    payload = evaluate(c)
    assert payload["summary"]["rawDirectionalCalls"] == 2
    assert payload["summary"]["eligibleEpisodes"] == 1
    assert payload["summary"]["maturedEpisodes"] == 1
    assert payload["summary"]["hitRate"] == 1
    c.close()


def test_eligibility_uses_first_day_confidence_only():
    import sqlite3
    import event_outcome_evaluator as eoe
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE prediction_tasks (ticker, as_of, task_type, claim, numeric_value, confidence_score)")
    con.executemany("INSERT INTO prediction_tasks VALUES (?,?,?,?,?,?)", [
        ("AAA", "2026-11-02", "event_impact", "positive", 0.3, 40.0),
        ("AAA", "2026-11-03", "event_impact", "positive", 0.4, 70.0)])
    assert eoe.evaluate(con)["summary"]["eligibleEpisodes"] == 0
