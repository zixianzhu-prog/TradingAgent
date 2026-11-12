from ai_medicine_peer_screen import build, score_company


def test_weighted_screen_score_is_reproducible():
    weights = {"a": 60, "b": 40}
    assert score_company({"scores": {"a": 5, "b": 2.5}}, weights) == 80.0


def test_challenger_prevents_sector_winner_claim():
    payload = build({
        "title": "x", "scope_note": "n", "criteria": {"a": 100},
        "companies": [
            {"ticker": "A", "stage": "deep-reviewed", "scores": {"a": 5}},
            {"ticker": "B", "stage": "deep-dive-next", "scores": {"a": 4}},
        ],
    })
    assert payload["sectorWinnerStatus"] == "provisional-until-challengers-reviewed"
    assert payload["challengers"][0]["ticker"] == "B"
