"""After an FDA rejection letter (complete response letter, CRL): does the stock keep falling, or rebound?

The agent reads 455 CRLs (scripts/fda_crl_reasons.py) and grades their severity: "heavy" when FDA asks for a
new trial, "light" for labeling, manufacturing or paperwork fixes. A CRL forces a decision on a holding:
sell into the drop, or hold for a resubmission. This measures, for the ~130 letters to listed companies:

* shock: close the day before the letter to the close 5 trading days after (companies usually announce
  within days of receiving it);
* drift: from that 5th-day close, 6 and 12 months, minus XBI over the same days;
* split by the severity graded from the letter.

Caveat: FDA published most letters only from 2025; before that investors saw the company's own summary, which
can soften the severity. Whether the drug was later approved is reported for description only: it is not
known at the time of the letter.

    PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/crl_drift_study.py
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import insider_buy_study as ibs

ROOT = Path(__file__).resolve().parents[1]
CRL = ROOT / "state/fda-crl-reasons.json"
OUT = ROOT / "state/crl-drift-study.json"
REPORT = ROOT / "outputs/crl-drift-study.md"
SHOCK_DAYS = 5


def shock_and_drift(closes: list[tuple[str, float]], bench: dict[str, float], day: str) -> dict | None:
    """Shock from the last close before `day` to SHOCK_DAYS closes after; drift from there."""
    before = [k for k, (d, _) in enumerate(closes) if d < day]
    if not before:
        return None
    i0 = before[-1]
    i1 = i0 + SHOCK_DAYS
    if i1 >= len(closes):
        return None
    d0, p0 = closes[i0]
    d1, p1 = closes[i1]
    out = {"shock": p1 / p0 - 1 - ((bench[d1] / bench[d0] - 1) if d0 in bench and d1 in bench else 0)}
    for h, n in ibs.HORIZONS.items():
        out[h] = ibs.forward(closes, bench, d1, n)
    return out


def study(rows: list[dict], prices: dict) -> dict:
    bench = dict(prices.get("XBI", []))
    groups: dict[str, dict[str, list[float]]] = {}
    events = []
    for r in rows:
        t = (r.get("listed") or {}).get("ticker")
        if not t or t not in prices or not r.get("issued"):
            continue
        res = shock_and_drift(prices[t], bench, r["issued"])
        if not res:
            continue
        events.append({"ticker": t, "drug": r.get("drug"), "issued": r["issued"], "severity": r.get("severity"),
                       "laterApproved": r.get("set") == "approved", **{k: (round(v, 4) if v is not None else None) for k, v in res.items()}})
        for g in ("all letters", f"severity: {r.get('severity')}", "later approved (hindsight)" if r.get("set") == "approved" else "not approved (hindsight)"):
            for k in ("shock", "6m", "12m"):
                if res.get(k) is not None:
                    groups.setdefault(g, {}).setdefault(k, []).append(res[k])
        # Big first-week drop: the case where "buy the overreaction" would apply.
        if res["shock"] <= -0.30:
            for k in ("shock", "6m", "12m"):
                if res.get(k) is not None:
                    groups.setdefault("first-week drop of 30%+", {}).setdefault(k, []).append(res[k])
    return {"groups": {g: {k: ibs.stats(v) for k, v in hs.items()} for g, hs in groups.items()}, "events": events}


def render(p: dict) -> str:
    lines = ["# FDA 拒批信（CRL）之后：继续跌还是反弹", "",
             f"> {p['events']} 封发给上市公司、且有股价数据的拒批信。冲击 = 拒批信日期前一天收盘到其后第 {SHOCK_DAYS} 个交易日收盘（减 XBI）；"
             f"漂移 = 从第 {SHOCK_DAYS} 个交易日收盘起 6/12 个月，减 XBI。严重度来自拒批信原文：heavy = 要求新试验。", "",
             "> 注意：FDA 大多在 2025 年后才公开拒批信原文，此前投资者看到的是公司自己的说法，可能淡化严重度。“后来获批”是事后信息，只作描述，不能用来决策。", "",
             "| 组别 | 次数 | 一周冲击（中位数） | 6 个月漂移（中位数） | 12 个月漂移（中位数） | 12 个月跑赢 XBI | 12 个月再跌超 50% |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    order = ["all letters", "severity: heavy", "severity: medium", "severity: light", "severity: unknown",
             "first-week drop of 30%+", "later approved (hindsight)", "not approved (hindsight)"]
    for g in order:
        s = p["groups"].get(g)
        if not s:
            continue
        sh, m6, m12 = s.get("shock", {}), s.get("6m", {}), s.get("12m", {})
        fmt = lambda x, k="median": "—" if not x.get("n") else f"{x[k]:+.1%}"
        lines.append(f"| {g} | {sh.get('n', 0)} | {fmt(sh)} | {fmt(m6)} | {fmt(m12)} | "
                     f"{'—' if not m12.get('n') else format(m12['beatXbi'], '.0%')} | {'—' if not m12.get('n') else format(m12['severeLoss'], '.0%')} |")
    lines += ["", "**幸存者偏差很重：** 拒批后破产或退市的公司不在今天的 SEC 股票代码表里，根本没有被算作“上市公司”，所以“一周暴跌 30% 以上后反弹”"
              "这一组被高估，不能当作抄底规则。公司与股票代码按名称匹配，个别是错配（例如 2004 年的 Organon 与今天的 OGN），样本只有几十次。"]
    lines += ["", "对照：同一批医疗公司随机月初买入，12 个月中位数超额约 -21%、跑赢 XBI 约 36%（见 outputs/insider-buy-study.md）。", "",
              "## 跌幅最大的 10 次", "", "| 股票 | 药物 | 日期 | 严重度 | 一周冲击 | 12 个月漂移 |", "|---|---|---|---|---:|---:|"]
    for e in sorted(p["eventRows"], key=lambda e: e["shock"])[:10]:
        lines.append(f"| {e['ticker']} | {e['drug']} | {e['issued']} | {e['severity']} | {e['shock']:+.0%} | "
                     f"{'—' if e['12m'] is None else format(e['12m'], '+.0%')} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    rows = json.loads(CRL.read_text(encoding="utf-8"))["rows"]
    tickers = sorted({(r.get("listed") or {}).get("ticker") for r in rows if r.get("listed")} - {None})
    prices = ibs.fetch_prices(tickers, start="2011-06-01")
    res = study(rows, prices)
    payload = {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "events": len(res["events"]),
               "groups": res["groups"], "eventRows": res["events"]}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(render(payload), encoding="utf-8")
    print(json.dumps({"events": payload["events"], "groups": {g: {k: v.get("median") for k, v in s.items()} for g, s in res["groups"].items()}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
