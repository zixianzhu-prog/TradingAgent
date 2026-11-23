"""Monitor SEC Schedule 13D/13G beneficial owners without treating holdings as financing."""
from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import urllib.request
from datetime import date, datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMS = {"SC 13D", "SC 13D/A", "SC 13G", "SC 13G/A", "SCHEDULE 13D", "SCHEDULE 13D/A", "SCHEDULE 13G", "SCHEDULE 13G/A"}
# Dedicated life-science investors. A 13D/13G from one of these is the "specialist money is coming in"
# signal; generalists (index funds, banks) are recorded but not flagged. Matched on the filer name.
SPECIALISTS = ("RA Capital", "Baker Bros", "Perceptive", "RTW", "Deerfield", "OrbiMed", "Venrock", "EcoR1", "Avoro",
               "Biotechnology Value", "BVF", "Vivo Capital", "Fairmount", "Commodore", "TCG Crossover", "Great Point",
               "Cormorant", "Logos", "Boxer Capital", "Suvretta", "Adage", "Samsara", "Frazier", "5AM", "Foresite",
               "Casdin", "Ally Bridge", "Octagon", "Viking Global", "Redmile", "Janus Henderson Biotech", "Point72 Life",
               "Rock Springs", "Vestal Point", "Darwin Global", "Siren", "Woodline", "Nextech", "Novo Holdings",
               "Bain Capital Life", "Polaris", "ARCH Venture", "Flagship", "Third Rock", "Atlas Venture", "Omega Fund",
               "MPM", "Abingworth", "Sofinnova", "Versant", "Alta Partners", "New Enterprise Associates", "Wellington Biomedical")


def configured_user_agent() -> str:
    value = os.getenv("SEC_USER_AGENT", "").strip()
    secret = ROOT / ".secrets/sec_user_agent"
    if not value and secret.is_file():
        value = secret.read_text(encoding="utf-8").strip()
    return value


class TextParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        if data.strip():
            self.parts.append(data.strip())


def text_from_html(raw: str) -> str:
    parser = TextParser()
    parser.feed(raw)
    return re.sub(r"\s+", " ", " ".join(parser.parts))


def fetch(url: str, agent: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": agent, "Accept-Encoding": "identity"})
    context = ssl.create_default_context(cafile="/etc/ssl/cert.pem" if Path("/etc/ssl/cert.pem").exists() else None)
    with urllib.request.urlopen(req, timeout=40, context=context) as response:
        return response.read().decode("utf-8", errors="replace")


def filing_rows(submissions: dict, ticker: str, cik: str, cutoff: date) -> list[dict]:
    recent = submissions.get("filings", {}).get("recent", {})
    keys = ("form", "accessionNumber", "filingDate", "primaryDocument")
    if not all(k in recent for k in keys):
        return []
    rows = []
    for form, accession, filed, document in zip(*(recent[k] for k in keys)):
        if form.upper() not in FORMS or date.fromisoformat(filed) < cutoff:
            continue
        rows.append({"ticker": ticker, "cik": cik, "form": form.upper(), "accession": accession,
                     "filed": filed, "url": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/{document}"})
    return rows


def raw_url(url: str) -> str:
    """EDGAR's primaryDocument for new-format filings is an XSL rendering (…/xslSCHEDULE_13G_X02/primary_doc.xml);
    the structured XML sits next to it without the xsl folder."""
    return re.sub(r"/xsl[^/]+/", "/", url)


def tag_values(raw: str, tag: str) -> list[str]:
    return [re.sub(r"\s+", " ", v).strip() for v in re.findall(rf"<(?:\w+:)?{tag}>([^<]*)</(?:\w+:)?{tag}>", raw)]


def specialist(name: str | None) -> str | None:
    low = (name or "").lower()
    return next((s for s in SPECIALISTS if s.lower() in low), None)


def parse_filing(raw: str, row: dict) -> dict:
    # New structured Schedule 13D/13G XML (since Dec 2024): explicit fields.
    names = list(dict.fromkeys(tag_values(raw, "reportingPersonName")))
    # Cover-page fields hold a bare number; Item 4 reuses the tag for prose ("Item 11 of the cover page",
    # "111,656,919 Shares outstanding"), so only purely numeric values count. The largest cover value is
    # the group's aggregate stake (the adviser reports all funds it manages).
    pcts = [float(m.group(1)) for v in tag_values(raw, "classPercent") + tag_values(raw, "percentOfClass")
            if (m := re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*%?\s*", v)) and float(m.group(1)) <= 100]
    owner, percent = (names[0] if names else None), (max(pcts) if pcts else None)
    if not owner:  # legacy text filings
        text = text_from_html(raw)
        owner_patterns = [
            r"NAME OF REPORTING PERSON(?:S)?\s+(?:I\.R\.S\.[^A-Z]{0,120})?([A-Z][A-Za-z0-9 .,&'()\-/]{2,120}?)(?=\s+(?:CHECK|2\s|CITIZENSHIP|SOURCE OF FUNDS))",
            r"Item 2\(a\)\s+Name of Person Filing\s*[:.]?\s*([^.;]{3,160})",
        ]
        owner = next((m.group(1).strip() for p in owner_patterns if (m := re.search(p, text, re.I))), None)
        pct_patterns = [r"PERCENT OF CLASS REPRESENTED BY AMOUNT IN ROW \(11\)\s+([0-9.]+)%?",
                        r"percent of the class represented[^0-9]{0,80}([0-9.]+)%"]
        percent = next((float(m.group(1)) for p in pct_patterns if (m := re.search(p, text, re.I))), None)
    form = row["form"]
    fund = next((specialist(n) for n in (names or [owner]) if specialist(n)), None)
    return {**row, "reportingPerson": owner, "otherReportingPersons": names[1:6], "percent": percent,
            "reporterTypes": sorted(set(tag_values(raw, "typeOfReportingPerson"))),
            "eventDate": next(iter(tag_values(raw, "eventDateRequiresFilingThisStatement")), None),
            "initial": not form.endswith("/A"), "specialistFund": fund,
            "intentClass": "potential-control-or-active" if "13D" in form else "passive-or-qualified-institution",
            "parseStatus": "verified" if owner else "partial",
            "quote": (f"{owner} reported beneficial ownership{f' of {percent}%' if percent is not None else ''} on {form}."
                      if owner else None)}


def cik_from_company(row: dict) -> str | None:
    for filing in row.get("filings", []):
        match = re.search(r"/data/(\d+)/", filing.get("url", ""))
        if match:
            return match.group(1)
    return str(row.get("cik")) if row.get("cik") else None


def universe(theme: dict, small_caps: dict, ciks: dict[str, str] | None = None) -> list[dict]:
    """Covered companies plus the small-cap list. Covered rows carry no filing links, so their CIK comes from
    SEC's ticker file (ciks); without it they were silently dropped."""
    rows = list(theme.get("themes", {}).get("ai_medicine", [])) + list(small_caps.get("companies", []))
    out = {}
    for row in rows:
        ticker = row.get("ticker")
        cik = cik_from_company(row) or (ciks or {}).get(str(ticker).upper())
        if ticker and cik:
            out[ticker] = {"ticker": ticker, "company": row.get("company"), "cik": cik}
    return list(out.values())


def build(companies: list[dict], lookback_days: int, agent: str, fetcher=fetch, today: date | None = None) -> dict:
    today = today or date.today()
    if "@" not in agent:
        return {"schemaVersion": 1, "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "status": "pending-config", "method": "SEC submissions and primary Schedule 13D/13G documents.",
                "summary": {"companiesQueued": len(companies), "filings": 0, "activeOwners": 0, "passiveOwners": 0, "errors": 0},
                "filings": [], "errors": [],
                "requiredAction": "Set SEC_USER_AGENT to a descriptive app name and contact email. Missing configuration is not evidence of no institutional owners."}
    filings, errors = [], []
    cutoff = today - timedelta(days=lookback_days)
    for company in companies:
        try:
            submissions = json.loads(fetcher(f"https://data.sec.gov/submissions/CIK{int(company['cik']):010d}.json", agent))
            rows = filing_rows(submissions, company["ticker"], company["cik"], cutoff)
            for row in rows[:8]:
                try:
                    filings.append({**parse_filing(fetcher(raw_url(row["url"]), agent), row), "company": company.get("company")})
                except Exception as exc:
                    errors.append({"ticker": company["ticker"], "url": row["url"], "error": str(exc)[:180]})
        except Exception as exc:
            errors.append({"ticker": company["ticker"], "error": str(exc)[:180]})
    return {"schemaVersion": 1, "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "status": "ok" if not errors else "partial",
            "method": "SEC Schedule 13D/13G. A holding proves beneficial ownership above the reporting threshold; it does not prove new cash went to the company.",
            "summary": {"companiesQueued": len(companies), "filings": len(filings),
                        "activeOwners": sum("13D" in f["form"] for f in filings),
                        "passiveOwners": sum("13G" in f["form"] for f in filings),
                        "specialistFilings": sum(bool(f.get("specialistFund")) for f in filings),
                        "specialistNewPositions": sum(bool(f.get("specialistFund")) and f.get("initial") for f in filings),
                        "parsed": sum(bool(f.get("reportingPerson")) for f in filings), "errors": len(errors)},
            "filings": sorted(filings, key=lambda x: x["filed"], reverse=True), "errors": errors}


def render(payload: dict) -> str:
    s = payload["summary"]
    lines = ["# SEC 13D/13G 重要股东雷达", "",
             f"> 状态：{payload['status']}。覆盖队列 {s['companiesQueued']} 家；文件 {s['filings']} 份；13D {s['activeOwners']}；13G {s['passiveOwners']}。", "",
             "> 13D/13G 证明重要股东的受益所有权，不等于公司获得新融资。13D 可能带有影响控制的意图；13G 通常是被动或合格机构申报。", ""]
    if payload.get("requiredAction"):
        lines += [f"**待配置：** {payload['requiredAction']}", ""]
    spec = [r for r in payload.get("filings", []) if r.get("specialistFund")]
    if spec:
        lines += ["## 专业生物医药基金", "", "首次申报 = 新跨过 5% 门槛（新建仓）；修订 = 持股变化。", "",
                  "| 日期 | 公司 | 基金 | 持股比例 | 首次/修订 | 文件 | 来源 |", "|---|---|---|---:|---|---|---|"]
        for row in spec:
            pct = f"{row['percent']:.2f}%" if row.get("percent") is not None else "—"
            lines.append(f"| {row['filed']} | {row['ticker']} | {row['reportingPerson']} | {pct} | {'首次' if row.get('initial') else '修订'} | {row['form']} | [SEC]({row['url']}) |")
        lines += ["", "## 全部申报", ""]
    lines += ["| 日期 | 公司 | 文件 | 申报人 | 持股比例 | 类型 | 来源 |", "|---|---|---|---|---:|---|---|"]
    for row in payload.get("filings", []):
        pct = f"{row['percent']:.2f}%" if row.get("percent") is not None else "—"
        lines.append(f"| {row['filed']} | {row['ticker']} | {row['form']} | {row.get('reportingPerson') or '待读取'} | {pct} | {row['intentClass']} | [SEC]({row['url']}) |")
    return "\n".join(lines) + "\n"


def load(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--theme", default=str(ROOT / "trend-agent/theme-company-map.json"))
    p.add_argument("--small-caps", default=str(ROOT / "state/small-cap-stage.json"))
    p.add_argument("--lookback-days", type=int, default=365)
    p.add_argument("--state", default=str(ROOT / "state/institutional-ownership.json"))
    p.add_argument("--report", default=str(ROOT / "outputs/institutional-ownership.md"))
    args = p.parse_args()
    agent = configured_user_agent()
    ciks = {}
    if agent:
        try:
            ciks = {str(r["ticker"]).upper(): str(r["cik_str"]) for r in json.loads(fetch("https://www.sec.gov/files/company_tickers.json", agent)).values()}
        except Exception:
            ciks = {}
    payload = build(universe(load(Path(args.theme), {}), load(Path(args.small_caps), {}), ciks), args.lookback_days, agent)
    Path(args.state).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.report).write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
