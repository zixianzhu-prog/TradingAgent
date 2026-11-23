"""Do new 5% stakes by specialist biotech funds predict returns? An event study on EDGAR's quarterly indexes.

The insider study (scripts/insider_buy_study.py) found one group that did better than owning the same stocks
at random: 10% holders, usually funds. The 13D/13G radar already flags specialist life-science funds
(institutional_ownership_agent.SPECIALISTS). This tests that flag over 2018 to mid-2025:

* EDGAR full-index master files list every Schedule 13D/13G twice, under the filer and under the subject
  company, with one accession number; pairing them gives "who disclosed a 5%+ stake in whom".
* Only initial filings (no /A). Subject must be one of ~500 listed health-care companies; the filer is a
  specialist if its name matches the radar's list, otherwise "other institution".
* One event per company and group within 30 days; entry at the first close after the filing date;
  6- and 12-month excess vs XBI; control = the same companies bought at every month start.

    SEC_USER_AGENT="Name email" PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/fund_stake_study.py
"""
from __future__ import annotations

import gzip
import json
import os
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path

import insider_buy_study as ibs
from institutional_ownership_agent import SPECIALISTS

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "state/serenity-source-cache/13dg-index"
OUT = ROOT / "state/fund-stake-study.json"
REPORT = ROOT / "outputs/fund-stake-study.md"
QUARTERS = [(y, q) for y in range(2018, 2026) for q in range(1, 5)][:30]  # 2018 Q1 .. 2025 Q2
FORMS = {"SC 13D", "SC 13G", "SCHEDULE 13D", "SCHEDULE 13G"}


def specialist(name: str) -> str | None:
    low = (name or "").lower()
    return next((s for s in SPECIALISTS if s.lower() in low), None)


def pairs(master_lines: list[str], ciks: set[str]) -> list[dict]:
    """Initial 13D/13G filings on health-care subjects: (subject cik, filer name, form, date)."""
    by_acc: dict[str, list[tuple[str, str, str, str]]] = {}
    for line in master_lines:
        parts = line.split("|")
        if len(parts) != 5 or parts[2] not in FORMS:
            continue
        acc = parts[4].rsplit("/", 1)[-1].removesuffix(".txt")
        by_acc.setdefault(acc, []).append((parts[0], parts[1], parts[2], parts[3]))
    out = []
    for acc, rows in by_acc.items():
        subjects = [r for r in rows if r[0] in ciks]
        filers = [r for r in rows if r[0] not in ciks]
        if len(subjects) != 1 or not filers:
            continue  # no health-care subject, or ambiguous (two covered companies on one filing)
        s = subjects[0]
        names = [f[1] for f in filers]
        fund = next((specialist(n) for n in names if specialist(n)), None)
        out.append({"cik": s[0], "filed": s[3], "form": s[2], "filer": names[0], "specialist": fund, "accession": acc})
    return out


def events(rows: list[dict]) -> list[dict]:
    """One event per company and group (specialist / other) within 30 days."""
    out, last = [], {}
    for r in sorted(rows, key=lambda x: (x["cik"], x["filed"])):
        group = "specialist fund" if r["specialist"] else "other institution"
        key = (r["cik"], group)
        if key in last and (date.fromisoformat(r["filed"]) - date.fromisoformat(last[key])).days <= ibs.WINDOW_DAYS:
            continue
        last[key] = r["filed"]
        out.append({**r, "group": group, "kind": "13D" if "13D" in r["form"] else "13G"})
    return out


def study(evts: list[dict], prices: dict, tickers: dict[str, str], first: str, last: str) -> dict:
    bench = dict(prices.get("XBI", []))
    groups: dict[str, dict[str, list[float]]] = {}
    def add(name, h, v):
        groups.setdefault(name, {}).setdefault(h, []).append(v)
    for e in evts:
        t = tickers.get(e["cik"])
        if not t or t not in prices:
            continue
        for h, n in ibs.HORIZONS.items():
            v = ibs.forward(prices[t], bench, e["filed"], n)
            if v is None:
                continue
            add(e["group"], h, v)
            add(f"{e['group']}, {e['kind']}", h, v)
    for t, series in prices.items():
        if t == "XBI":
            continue
        for m in sorted({d[:7] for d, _ in series if first <= d <= last}):
            for h, n in ibs.HORIZONS.items():
                v = ibs.forward(series, bench, f"{m}-00", n)
                if v is not None:
                    add("control: any month", h, v)
    out = {g: {h: ibs.stats(v) for h, v in hs.items()} for g, hs in groups.items()}
    control = out.get("control: any month", {})
    for g, hs in out.items():
        for h, st in hs.items():
            c = control.get(h)
            if g.startswith("control") or not c or not st.get("n"):
                continue
            se = (c["beatXbi"] * (1 - c["beatXbi"]) / st["n"]) ** 0.5
            st["zBeat"] = round((st["beatXbi"] - c["beatXbi"]) / se, 2) if se else None
    return out


def render(p: dict) -> str:
    lines = ["# 专业生物医药基金新建 5% 仓位能预测回报吗（13D/13G 事件研究）", "",
             f"> 样本：{p['companies']} 家上市医疗公司，{p['span'][0]} 至 {p['span'][1]} 的首次 13D/13G 申报（不含修订）。"
             "申报人名称与雷达的专业基金名单匹配即为“专业基金”，其余为“其他机构”。同一公司同一组 30 天内只算一次。"
             "买入价 = 申报日后第一个交易日收盘；超额 = 同期减 XBI；对照组 = 同一批公司每个月初买入。", "",
             "> 幸存者偏差：只有今天仍上市的公司有价格。13G 多为被动持股，13D 表示可能影响公司。", "",
             "| 组别 | 期限 | 次数 | 截尾平均超额 | 中位数超额 | 跑赢 XBI | z（对照组） | 跌超 50% |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    order = ["control: any month", "specialist fund", "specialist fund, 13D", "specialist fund, 13G",
             "other institution", "other institution, 13D", "other institution, 13G"]
    for g in order:
        for h in ibs.HORIZONS:
            s = p["groups"].get(g, {}).get(h)
            if s and s.get("n"):
                lines.append(f"| {g} | {h} | {s['n']} | {s['mean']:+.1%} | {s['median']:+.1%} | {s['beatXbi']:.0%} | {ibs.z_text(s)} | {s['severeLoss']:.0%} |")
    c = p["groups"].get("control: any month", {}).get("12m", {})
    lines += ["", "## 读法", ""]
    for g in ("specialist fund", "specialist fund, 13D", "specialist fund, 13G", "other institution"):
        s = p["groups"].get(g, {}).get("12m", {})
        if s.get("n", 0) >= 30 and c.get("n"):
            d = s["median"] - c["median"]
            lines.append(f"- {g}：12 个月中位数超额比对照组{'高' if d > 0 else '低'} {abs(d):.1%}（{s['n']} 次）；跑赢 XBI {s['beatXbi']:.0%}，对照组 {c['beatXbi']:.0%}（z = {s.get('zBeat', 0):+.1f}）。")
    lines.append("- |z| < 2 视为可能是运气；同一公司的事件持有期会重叠，z 值偏乐观。")
    return "\n".join(lines) + "\n"


def main() -> None:
    agent = os.getenv("SEC_USER_AGENT", "")
    if "@" not in agent:
        sys.exit("Set SEC_USER_AGENT with your contact email (SEC fair-access policy).")
    import beneficiary_mapper as mapper

    ciks = ibs.health_ciks()
    CACHE.mkdir(parents=True, exist_ok=True)
    rows = []
    for y, q in QUARTERS:
        path = CACHE / f"{y}q{q}-health-13dg.json"
        if not path.exists():
            blob = ibs.get(f"https://www.sec.gov/Archives/edgar/full-index/{y}/QTR{q}/master.gz", agent)
            lines = gzip.decompress(blob).decode("latin-1").splitlines()
            path.write_text(json.dumps(pairs(lines, ciks)), encoding="utf-8")
            time.sleep(0.3)
        got = json.loads(path.read_text(encoding="utf-8"))
        rows += got
        print(f"  {y}q{q}: {len(got)} filings, {sum(bool(r['specialist']) for r in got)} by specialists")
    evts = events(rows)
    current = {str(r["cik_str"]): r["ticker"] for r in mapper.http_json("https://www.sec.gov/files/company_tickers.json", agent).values()}
    tickers = {c: current[c] for c in ciks if c in current}
    prices = ibs.fetch_prices(list(set(tickers.values())))
    span = ("2018-01-01", "2025-06-30")
    groups = study(evts, prices, tickers, *span)
    payload = {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "span": span,
               "companies": len([t for t in set(tickers.values()) if t in prices]), "events": len(evts), "groups": groups}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(render(payload), encoding="utf-8")
    print(json.dumps({"events": len(evts), "12m": {g: v.get("12m") for g, v in groups.items()}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
