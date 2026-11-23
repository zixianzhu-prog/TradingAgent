from datetime import date

import order_tickets as ot

CTX = {"risk": {}, "small": {}, "events": {}, "departures": {}, "deals": {}, "watch": {}, "bull": {}}


def row(**kw):
    base = {"ticker": "X", "company": "X Inc", "rank": 1, "gateDecision": "research-ready", "serenityReviewed": True, "openEvents": [],
            "lowEvidence": False, "falsifiers": ["growth below 15%"], "serenityVerdict": {"tier": "standard"},
            "orderRange": {"price": 10.0, "upper": 12.0, "floor": 8.0, "status": "in-range", "gapToUpper": -0.17,
                           "impliedGrowth": 0.1, "baseGrowth": 0.12}}
    base.update(kw)
    return base


def test_in_range_standard_name_gets_standard_size_and_falsifiers():
    t = ot.ticket(row(), CTX, 100_000, date(2026, 11, 17))
    assert t["action"] == "buy" and t["positionPct"] == 0.05 and t["limitPrice"] == 12.0
    assert "growth below 15%" in t["invalidation"]


def test_wait_when_above_range_or_evidence_pending_and_avoid_on_reject():
    above = row(orderRange={"price": 15.0, "upper": 12.0, "floor": 8.0, "status": "above", "gapToUpper": 0.25,
                            "impliedGrowth": 0.2, "baseGrowth": 0.12})
    assert ot.ticket(above, CTX, 100_000, date(2026, 11, 17))["positionPct"] == 0
    assert ot.ticket(row(lowEvidence=True), CTX, 100_000, date(2026, 11, 17))["action"] == "wait"
    watch = ot.ticket(row(gateDecision="watch"), CTX, 100_000, date(2026, 11, 17))
    assert watch["action"] == "starter" and 0 < watch["positionPct"] <= ot.STARTER
    unreviewed = ot.ticket(row(gateDecision="watch", serenityReviewed=False), CTX, 100_000, date(2026, 11, 17))
    assert unreviewed["action"] == "wait" and unreviewed["positionPct"] == 0
    assert ot.ticket(row(gateDecision="reject"), CTX, 100_000, date(2026, 11, 17))["action"] == "avoid"


def test_risk_caps_halve_on_drawdown_and_cap_short_runway_and_liquidity():
    ctx = {**CTX, "risk": {"X": {"worstDay": -0.3, "advUsd": 50e6, "price": 10.0}}}
    assert ot.ticket(row(), ctx, 100_000, date(2026, 11, 17))["positionPct"] == 0.025
    ctx = {**CTX, "small": {"X": {"marketCapM": 400, "runwayMonths": 6}}}
    assert ot.ticket(row(), ctx, 100_000, date(2026, 11, 17))["positionPct"] == 0.01
    ctx = {**CTX, "risk": {"X": {"worstDay": -0.05, "advUsd": 100_000, "price": 10.0}}}
    assert ot.ticket(row(), ctx, 100_000, date(2026, 11, 17))["positionPct"] == 0.02   # 2% of $100K a day = $2K


def test_slowing_growth_turns_a_price_buy_into_wait():
    ctx = {**CTX, "trends": {"X": {"fiscalEnd": "2025-12-31", "growth": 0.10, "previousGrowth": 0.20, "slowing": True}}}
    t = ot.ticket(row(), ctx, 100_000, date(2026, 11, 17))
    assert t["action"] == "wait" and any("slowed" in r for r in t["reasons"])
    ctx["trends"]["X"]["slowing"] = False
    assert ot.ticket(row(), ctx, 100_000, date(2026, 11, 17))["action"] == "buy"


def test_small_cap_rows_need_memo_and_usable_rnpv(tmp_path, monkeypatch):
    import json
    (tmp_path / "state").mkdir()
    w = lambda name, obj: (tmp_path / "state" / name).write_text(json.dumps(obj))
    w("rnpv-valuations.json", {"companies": [
        {"ticker": "IRD", "rangeUsable": True, "phase": 3, "impliedPeakSalesM": 780, "orderRange": {"price": 3.9, "upper": 6.9, "floor": 2.2, "status": "in-range"}},
        {"ticker": "HURA", "rangeUsable": False, "phase": 3, "impliedPeakSalesM": 271, "orderRange": {"price": 1.4, "upper": 3.1, "floor": 0.4, "status": "in-range"}},
        {"ticker": "SGMT", "rangeUsable": True, "phase": 3, "impliedPeakSalesM": 318, "orderRange": {"price": 10, "upper": 8.5, "floor": 6, "status": "above"}}]})
    w("serenity-review-status.json", {"companies": {"IRD": {"claudeMemo": "citation-checked"}, "HURA": {"claudeMemo": "citation-checked"}}})
    w("serenity-auto-assessments.json", {"companies": [{"ticker": "IRD", "review_path": "state/serenity-reviews/IRD-claude-x.json"},
                                                        {"ticker": "HURA", "review_path": "state/serenity-reviews/HURA-claude-x.json"},
                                                        {"ticker": "SGMT", "review_path": "state/serenity-reviews/SGMT-claudecli-x.json"}]})
    w("serenity-gate-results.json", {"companies": [{"ticker": "IRD", "decision": "watch", "substantiatedScore": 52}]})
    w("serenity-claude-verdicts.json", {"companies": [{"ticker": "IRD", "tier": "starter until X"}]})
    w("small-cap-stage.json", {"companies": [{"ticker": t, "company": t} for t in ("IRD", "HURA", "SGMT")]})
    monkeypatch.setattr(ot, "ROOT", tmp_path)
    monkeypatch.setattr(ot, "SMALL_CAPS", tmp_path / "state/small-cap-stage.json")
    monkeypatch.setattr(ot, "EVENTS", tmp_path / "state/none.json")
    rows = ot.small_cap_rows(set())
    assert [r["ticker"] for r in rows] == ["IRD"]  # HURA range unusable, SGMT has no Claude memo
    t = ot.ticket(rows[0], {**CTX, "small": {"IRD": {"marketCapM": 380}}}, 100_000, date(2026, 11, 23))
    assert t["action"] == "starter" and 0 < t["positionPct"] <= ot.STARTER


def test_rnpv_range_above_gives_wait_with_peak_sales_reason():
    r = row(orderRange={"price": 4.0, "upper": 2.4, "floor": 0.7, "status": "above", "gapToUpper": 0.64, "method": "rNPV"},
            rnpv={"impliedPeakSalesM": 2162, "platform": False})
    t = ot.ticket(r, CTX, 100_000, date(2026, 11, 23))
    assert t["action"] == "wait" and "rNPV base value" in t["reasons"][0]


def test_deep_discount_waits():
    r = row(orderRange={"price": 10.0, "upper": 20.0, "floor": 15.0, "status": "below-floor", "gapToUpper": -0.5,
                        "impliedGrowth": 0.02, "baseGrowth": 0.30})
    t = ot.ticket(r, CTX, 100_000, date(2026, 11, 23))
    assert t["action"] == "wait" and t["reasons"][-1].startswith("Deep discount")


def test_flip_points_state_the_room_left():
    pts = ot.flip_points({"price": 50.0, "upper": 62.5, "impliedGrowth": 0.10, "baseGrowth": 0.12}, None)
    assert "2.0 points" in pts[0] and "20%" in pts[1]
    assert "1,000M" in ot.flip_points({"price": 4, "upper": 3, "method": "rNPV"}, {"impliedPeakSalesM": 1000})[0]
