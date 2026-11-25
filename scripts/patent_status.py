"""Patent life of each covered company from USPTO Open Data Portal file wrappers.

For each company the script fetches granted applications whose first applicant is the company (every word of the
company's name must appear in the applicant name, so "Tempus" does not pick up "Tempus Steel"). For each patent:

* expiry estimate: utility patents 20 years from the effective filing date plus the patent-term adjustment days;
  design patents 15 years from grant;
* terminal disclaimer filed (event DIST): the patent may expire earlier, tied to an earlier family member;
* already expired or lapsed (status text), e.g. for unpaid maintenance fees.

Per company: granted count, how many of the sampled utility patents expire before 2031 and before 2036, the median
expiry, and the share with terminal disclaimers. What this cannot tell: whether a patent covers the core product,
how easily it can be designed around, or whether it would survive a challenge; those need the claims and are left
for the memo.

    USPTO_API_KEY=... python3 scripts/patent_status.py
"""
from __future__ import annotations

import json
import os
import statistics
import time
import urllib.error
import urllib.parse
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import uspto_assignment_validation as usv

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "state/patent-status.json"
REPORT = ROOT / "outputs/patent-status.md"
THEME = ROOT / "trend-agent/theme-company-map.json"
FILTER = ROOT / "state/candidate-filter.json"
PAUSE = 1.6


def load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def companies() -> dict[str, str]:
    names = {r["ticker"]: r["company"] for r in load(THEME, {}).get("themes", {}).get("ai_medicine", []) if r.get("ticker") and r.get("company")}
    flt = load(FILTER, {})
    rows = flt.get("companies", {})
    for t in flt.get("deepReview", []):
        c = rows.get(t) if isinstance(rows, dict) else None
        if c and c.get("company"):
            names.setdefault(t, c["company"])
    return names


# Patents held under a subsidiary's name.
APPLICANTS = {"GEHC": ["GE Precision Healthcare"], "CAI": ["Caris Life Sciences", "Caris MPI", "Caris Science"]}


def fetch_page(name: str, key: str, fetch=usv.odp_get, limit: int = 100, sort: str | None = None) -> tuple[list[dict], int]:
    q = f'applicationMetaData.firstApplicantName:"{usv.base_name(name)}" AND applicationMetaData.patentNumber:*'
    found = {}
    for attempt in range(6):
        params = {"q": q, "limit": limit, **({"sort": sort} if sort else {})}
        url = f"{usv.ODP}/search?" + urllib.parse.urlencode(params)
        try:
            found = fetch(url, key)
            break
        except urllib.error.HTTPError as exc:
            if exc.code == 413 and limit > 10:
                limit //= 2
                continue
            if exc.code == 429 and attempt < 5:
                time.sleep(PAUSE * (attempt + 2) * 2)
                continue
            raise
    wanted = usv.applicant_words(name)
    apps = [a for a in found.get("patentFileWrapperDataBag", [])
            if wanted and wanted <= usv.applicant_words(a.get("applicationMetaData", {}).get("firstApplicantName") or "")]
    return apps, int(found.get("count") or 0)


def fetch_granted(ticker: str, name: str, key: str, fetch=usv.odp_get, pause: float = PAUSE) -> tuple[list[dict], int, bool]:
    """All granted patents when there are up to 100; otherwise the 50 oldest and 50 newest, so the earliest expiries are
    always in the sample. Returns (applications, total granted, complete)."""
    apps: dict[str, dict] = {}
    total, complete = 0, True
    for applicant in APPLICANTS.get(ticker, [name]):
        newest, count = fetch_page(applicant, key, fetch, 100)
        total += count
        for a in newest:
            apps[a.get("applicationNumberText")] = a
        if count > 100:
            complete = False
            time.sleep(pause)
            oldest, _ = fetch_page(applicant, key, fetch, 50, "applicationMetaData.effectiveFilingDate asc")
            for a in oldest:
                apps[a.get("applicationNumberText")] = a
        time.sleep(pause)
    return list(apps.values()), total, complete


def expiry(app: dict) -> date | None:
    m = app.get("applicationMetaData", {})
    try:
        if (m.get("applicationTypeLabelName") or "").lower() == "design":
            return date.fromisoformat(m["grantDate"]) + timedelta(days=round(15 * 365.25))
        start = date.fromisoformat(m.get("effectiveFilingDate") or m["filingDate"])
    except (KeyError, TypeError, ValueError):
        return None
    pta = (app.get("patentTermAdjustmentData") or {}).get("adjustmentTotalQuantity") or 0
    return start + timedelta(days=round(20 * 365.25) + int(pta))


def summarize(apps: list[dict], total: int, today: date, complete: bool = True) -> dict:
    rows = []
    for a in apps:
        m = a.get("applicationMetaData", {})
        events = {e.get("eventCode") for e in a.get("eventDataBag", [])}
        status = m.get("applicationStatusDescriptionText") or ""
        rows.append({"patent": m.get("patentNumber"), "title": m.get("inventionTitle"), "type": m.get("applicationTypeLabelName"),
                     "granted": m.get("grantDate"), "expiry": (expiry(a) or date.min).isoformat() if expiry(a) else None,
                     "terminalDisclaimer": "DIST" in events, "lapsed": "expired" in status.lower() or "EXP." in events,
                     "status": status})
    utility = [r for r in rows if (r["type"] or "").lower() == "utility" and r["expiry"] and not r["lapsed"]
               and r["expiry"] > today.isoformat()]  # past its estimated term: no longer protects anything
    exp = sorted(date.fromisoformat(r["expiry"]) for r in utility)
    return {"grantedTotal": total, "sampled": len(rows), "utilitySampled": len(utility), "complete": complete,
            "expireBy2031": sum(d.year <= 2030 for d in exp), "expireBy2036": sum(d.year <= 2035 for d in exp),
            "medianExpiry": exp[len(exp) // 2].isoformat() if exp and complete else None,
            "earliestLiveExpiry": exp[0].isoformat() if exp else None,
            "terminalDisclaimerShare": round(sum(r["terminalDisclaimer"] for r in utility) / len(utility), 2) if utility else None,
            "lapsed": sum(r["lapsed"] for r in rows), "designPatents": sum((r["type"] or "").lower() == "design" for r in rows),
            "examples": sorted(utility, key=lambda r: r["expiry"])[:3]}


def render(payload: dict) -> str:
    lines = ["# 专利寿命（USPTO 开放数据平台）", "", f"生成：{payload['generatedAt']}", "",
             "> 发明专利按有效申请日 + 20 年 + 专利期调整估算到期；外观设计按授权后 15 年。提交终端声明的可能更早到期。"
             "无法判断专利是否覆盖核心产品、能否被绕开或能否经受无效挑战，这些需要读权利要求。", "",
             "| 股票 | 授权专利总数 | 样本中有效发明专利 | 2030 年前到期 | 2035 年前到期 | 到期中位数（仅全量时） | 终端声明占比 | 已失效 |",
             "|---|---:|---:|---:|---:|---|---:|---:|"]
    for t, c in payload["companies"].items():
        td = f"{c['terminalDisclaimerShare']:.0%}" if c["terminalDisclaimerShare"] is not None else "—"
        at_least = "" if c.get("complete", True) else "≥"
        lines.append(f"| {t} | {c['grantedTotal']} | {c['utilitySampled']} | {at_least}{c['expireBy2031']} | {at_least}{c['expireBy2036']} | {c['medianExpiry'] or '—'} | {td} | {c['lapsed']} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    key = os.getenv("USPTO_API_KEY", "").strip()
    if not key:
        print(json.dumps({"note": "USPTO_API_KEY not set; keeping the last result"}))
        return
    today = date.today()
    out, failed = {}, []
    for ticker, name in sorted(companies().items()):
        try:
            apps, total, complete = fetch_granted(ticker, name, key)
        except urllib.error.HTTPError as exc:
            failed.append(f"{ticker} ({exc.code})")
            continue
        out[ticker] = {"company": name, **summarize(apps, total, today, complete)}
        c = out[ticker]
        print(f"  {ticker}: {total} granted ({'all' if complete else 'oldest+newest'}), {c['utilitySampled']} live utility, "
              f"earliest {c['earliestLiveExpiry']}, by 2030 {c['expireBy2031']}, median {c['medianExpiry']}")
    payload = {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "method": __doc__.split("\n\n")[1].strip(),
               "limits": "Claims coverage, design-around risk and validity are not assessed.", "failed": failed, "companies": out}
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(render(payload), encoding="utf-8")
    print(json.dumps({"companies": len(out), "failed": failed}))


if __name__ == "__main__":
    main()
