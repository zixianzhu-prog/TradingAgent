"""Do insider open-market purchases predict returns in health-care stocks? An event study on SEC Form 4 data.

The pipeline tracks Form 4 buying as a signal. Before it is trusted, this checks the record: every open-market
purchase (transaction code P) by an officer, director or 10% holder of ~500 listed health-care companies,
2018 through mid-2025, from SEC's quarterly Insider Transactions Data Sets.

* Event: the first purchase of at least $25K at a company, with later purchases within 30 days folded in
  (value summed, buyers counted). Split by who bought: officer/director, or 10% holder only (usually a fund).
* Entry: the close on the first trading day after the Form 4 filing date, the day the market could know.
* Outcome: 6- and 12-month return minus XBI over the same days.
* Control: the same companies from every month start in the same years, so the comparison is with simply
  owning these stocks, not with zero.

Survivorship: only companies listed today have prices, which flatters both events and control alike.

    SEC_USER_AGENT="Name email" PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/insider_buy_study.py
"""
from __future__ import annotations

import csv
import io
import json
import os
import re
import statistics
import sys
import time
import urllib.request
import zipfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "state/serenity-source-cache/form345"
OUT = ROOT / "state/insider-buy-study.json"
REPORT = ROOT / "outputs/insider-buy-study.md"
INDEX = "https://www.sec.gov/data-research/sec-markets-data/insider-transactions-data-sets"
QUARTERS = [f"{y}q{q}" for y in range(2018, 2026) for q in range(1, 5)][:30]  # 2018q1 .. 2025q2
MIN_USD = 25_000
WINDOW_DAYS = 30
HORIZONS = {"6m": 126, "12m": 252}
csv.field_size_limit(10**8)


def get(url: str, agent: str) -> bytes:
    import serenity_evidence_review as ser

    req = urllib.request.Request(url, headers={"User-Agent": agent, "Accept-Encoding": "identity"})
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
    with opener.open(req, timeout=300) as resp:
        return resp.read()


def health_ciks() -> set[str]:
    out = set()
    for d in ("xbrl", "xbrl-oos"):
        for p in (ROOT / "state/serenity-source-cache" / d).glob("companyfacts-*.json"):
            try:
                cik = json.loads(p.read_text(encoding="utf-8")).get("cik")
            except Exception:
                continue
            if cik:
                out.add(str(int(cik)))
    return out


def rows(z: zipfile.ZipFile, name: str):
    with z.open(name) as fh:
        yield from csv.DictReader(io.TextIOWrapper(fh, encoding="utf-8", errors="replace"), delimiter="\t")


def parse_quarter(blob: bytes, ciks: set[str]) -> list[dict]:
    """Open-market purchases (code P, acquired) in health-care issuers from one quarterly zip."""
    z = zipfile.ZipFile(io.BytesIO(blob))
    subs = {}
    for r in rows(z, "SUBMISSION.tsv"):
        cik = str(int(r["ISSUERCIK"])) if r["ISSUERCIK"].strip().isdigit() else None
        if cik in ciks and r["DOCUMENT_TYPE"] in ("4", "4/A"):
            subs[r["ACCESSION_NUMBER"]] = {"cik": cik, "filed": datetime.strptime(r["FILING_DATE"], "%d-%b-%Y").date().isoformat(),
                                           "symbol": r["ISSUERTRADINGSYMBOL"]}
    owners: dict[str, list[str]] = {}
    for r in rows(z, "REPORTINGOWNER.tsv"):
        if r["ACCESSION_NUMBER"] in subs:
            owners.setdefault(r["ACCESSION_NUMBER"], []).append(f"{r['RPTOWNERCIK']}|{r['RPTOWNER_RELATIONSHIP']}")
    out = []
    for r in rows(z, "NONDERIV_TRANS.tsv"):
        s = subs.get(r["ACCESSION_NUMBER"])
        if not s or r["TRANS_CODE"] != "P" or r["TRANS_ACQUIRED_DISP_CD"] != "A":
            continue
        try:
            value = float(r["TRANS_SHARES"] or 0) * float(r["TRANS_PRICEPERSHARE"] or 0)
        except ValueError:
            continue
        rel = owners.get(r["ACCESSION_NUMBER"], [])
        insider = any(re.search(r"Director|Officer", x) for x in rel)
        out.append({**s, "value": round(value), "owners": sorted({x.split("|")[0] for x in rel}),
                    "role": "officer/director" if insider else "10% holder"})
    return out


def events(purchases: list[dict]) -> list[dict]:
    """First purchase per company, later ones within WINDOW_DAYS folded in; at least MIN_USD in total."""
    out, by_cik = [], {}
    for p in sorted(purchases, key=lambda x: (x["cik"], x["filed"])):
        by_cik.setdefault(p["cik"], []).append(p)
    for cik, ps in by_cik.items():
        i = 0
        while i < len(ps):
            start = date.fromisoformat(ps[i]["filed"])
            group = [p for p in ps[i:] if (date.fromisoformat(p["filed"]) - start).days <= WINDOW_DAYS]
            i += len(group)
            total = sum(p["value"] for p in group)
            if total < MIN_USD:
                continue
            buyers = {o for p in group for o in p["owners"]}
            out.append({"cik": cik, "filed": group[0]["filed"], "symbol": group[0]["symbol"], "valueUsd": total,
                        "buyers": len(buyers), "role": "officer/director" if any(p["role"] == "officer/director" for p in group) else "10% holder"})
    return out


def forward(closes: list[tuple[str, float]], bench: dict[str, float], day: str, n: int) -> float | None:
    """Excess return over n trading days, entering at the first close after `day`."""
    idx = next((k for k, (d, _) in enumerate(closes) if d > day), None)
    if idx is None or idx + n >= len(closes):
        return None
    d0, p0 = closes[idx]
    d1, p1 = closes[idx + n]
    if d0 not in bench or d1 not in bench or p0 <= 0:
        return None
    return (p1 / p0 - 1) - (bench[d1] / bench[d0] - 1)


def trimmed_mean(xs: list[float], cut: float = 0.05) -> float:
    """Mean of the middle 90%: split-adjusted penny-stock prices produce absurd outliers (+10,000%)."""
    ys = sorted(xs)
    k = int(len(ys) * cut)
    ys = ys[k:len(ys) - k] or ys
    return statistics.fmean(ys)


def stats(xs: list[float]) -> dict:
    if not xs:
        return {"n": 0}
    return {"n": len(xs), "mean": round(trimmed_mean(xs), 4), "median": round(statistics.median(xs), 4),
            "beatXbi": round(sum(x > 0 for x in xs) / len(xs), 3), "severeLoss": round(sum(x < -0.5 for x in xs) / len(xs), 3)}


def study(evts: list[dict], prices: dict[str, list[tuple[str, float]]], tickers: dict[str, str], first: str, last: str) -> dict:
    bench = dict(prices.get("XBI", []))
    groups: dict[str, dict[str, list[float]]] = {}
    def add(name, h, v):
        groups.setdefault(name, {}).setdefault(h, []).append(v)
    for e in evts:
        t = tickers.get(e["cik"])
        if not t or t not in prices:
            continue
        for h, n in HORIZONS.items():
            v = forward(prices[t], bench, e["filed"], n)
            if v is None:
                continue
            add("all purchases", h, v)
            add(f"by {e['role']}", h, v)
            if e["buyers"] >= 2:
                add("2+ buyers within 30 days", h, v)
            if e["valueUsd"] >= 1_000_000:
                add("$1M+ bought", h, v)
    # Control: every month start in the same span, same companies.
    for t, series in prices.items():
        if t == "XBI":
            continue
        months = sorted({d[:7] for d, _ in series if first <= d <= last})
        for m in months:
            for h, n in HORIZONS.items():
                v = forward(series, bench, f"{m}-00", n)
                if v is not None:
                    add("control: any month", h, v)
    out = {g: {h: stats(v) for h, v in hs.items()} for g, hs in groups.items()}
    control = out.get("control: any month", {})
    for g, hs in out.items():
        for h, st in hs.items():
            c = control.get(h)
            if g.startswith("control") or not c or not st.get("n"):
                continue
            se = (c["beatXbi"] * (1 - c["beatXbi"]) / st["n"]) ** 0.5
            st["zBeat"] = round((st["beatXbi"] - c["beatXbi"]) / se, 2) if se else None
    return out


def fetch_prices(tickers: list[str], start: str = "2017-12-01") -> dict[str, list[tuple[str, float]]]:
    import yfinance as yf

    out = {}
    names = sorted(set(tickers) | {"XBI"})
    for i in range(0, len(names), 100):
        chunk = names[i:i + 100]
        frame = yf.download(chunk, start=start, auto_adjust=True, progress=False, group_by="ticker", threads=True)
        for t in chunk:
            try:
                col = frame[t]["Close"].dropna()
                if len(col) > 300:
                    out[t] = [(d.date().isoformat(), float(v)) for d, v in col.items()]
            except Exception:
                continue
    return out


def z_text(s: dict) -> str:
    return "—" if s.get("zBeat") is None else f"{s['zBeat']:+.1f}"


def render(p: dict) -> str:
    lines = ["# 内部人公开市场买入能预测回报吗（医疗股事件研究）", "",
             f"> 样本：{p['companies']} 家上市医疗公司，{p['span'][0]} 至 {p['span'][1]} 的 Form 4 公开市场买入（代码 P，≥ ${MIN_USD // 1000}K；同一公司 30 天内合并为一次）。"
             "买入价 = Form 4 提交后第一个交易日收盘；超额 = 同期减 XBI。对照组 = 同一批公司每个月初买入。", "",
             "> 幸存者偏差：只有今天仍上市的公司有价格，事件组和对照组同样受影响。", "",
             "| 组别 | 期限 | 次数 | 截尾平均超额 | 中位数超额 | 跑赢 XBI | z（对照组） | 跌超 50% |", "|---|---|---:|---:|---:|---:|---:|---:|"]
    order = ["control: any month", "all purchases", "by officer/director", "by 10% holder", "2+ buyers within 30 days", "$1M+ bought"]
    for g in order:
        for h in HORIZONS:
            s = p["groups"].get(g, {}).get(h)
            if s and s.get("n"):
                lines.append(f"| {g} | {h} | {s['n']} | {s['mean']:+.1%} | {s['median']:+.1%} | {s['beatXbi']:.0%} | {z_text(s)} | {s['severeLoss']:.0%} |")
    lines += ["", "## 读法", "", p["verdict"]]
    return "\n".join(lines) + "\n"


def verdict(groups: dict) -> str:
    c = groups.get("control: any month", {}).get("12m", {})
    out = []
    for g in ("all purchases", "by officer/director", "by 10% holder", "2+ buyers within 30 days", "$1M+ bought"):
        s = groups.get(g, {}).get("12m", {})
        if s.get("n", 0) >= 30 and c.get("n"):
            diff = s["median"] - c["median"]
            out.append(f"- {g}：12 个月中位数超额比对照组{'高' if diff > 0 else '低'} {abs(diff):.1%}（{s['n']} 次）；"
                       f"跑赢 XBI 的比例 {s['beatXbi']:.0%}，对照组 {c['beatXbi']:.0%}（z = {s.get('zBeat', 0):+.1f}；|z| < 2 视为可能是运气）。")
    out.append("- 截尾平均去掉两端各 5%：拆股调整后的低价股会出现上万个百分点的异常值。"
               "同一公司 30 天内的多次买入合并为一次，但相邻事件的持有期仍会重叠，z 值因此偏乐观。")
    out.append("- 中位数比平均数可靠：少数暴涨股会把平均数拉高。样本数少于 30 的组不下结论。")
    return "\n".join(out)


def main() -> None:
    agent = os.getenv("SEC_USER_AGENT", "")
    if "@" not in agent:
        sys.exit("Set SEC_USER_AGENT with your contact email (SEC fair-access policy).")
    import beneficiary_mapper as mapper

    ciks = health_ciks()
    page = get(INDEX, agent).decode("utf-8", "replace")
    links = dict((m.group(2), m.group(1)) for m in re.finditer(r'href="([^"]*/(\d{4}q\d)_form345\.zip)"', page))
    CACHE.mkdir(parents=True, exist_ok=True)
    purchases = []
    for q in QUARTERS:
        path = CACHE / f"{q}-health-purchases.json"
        if not path.exists():
            if q not in links:
                print(f"  {q}: not listed")
                continue
            path.write_text(json.dumps(parse_quarter(get("https://www.sec.gov" + links[q], agent), ciks)), encoding="utf-8")
            time.sleep(0.5)
        got = json.loads(path.read_text(encoding="utf-8"))
        purchases += got
        print(f"  {q}: {len(got)} purchases")
    evts = events(purchases)
    current = {str(r["cik_str"]): r["ticker"] for r in mapper.http_json("https://www.sec.gov/files/company_tickers.json", agent).values()}
    tickers = {c: current[c] for c in {e["cik"] for e in evts} | ciks if c in current}
    prices = fetch_prices(list(set(tickers.values())))
    span = (QUARTERS[0][:4] + "-01-01", "2025-06-30")
    groups = study(evts, prices, tickers, *span)
    payload = {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "span": span,
               "companies": len([t for t in set(tickers.values()) if t in prices]), "events": len(evts),
               "groups": groups, "verdict": verdict(groups)}
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(render(payload), encoding="utf-8")
    print(json.dumps({"events": len(evts), "companies": payload["companies"],
                      "12m": {g: v.get("12m") for g, v in groups.items()}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
