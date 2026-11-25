"""Build an auditable USPTO assignment-validation queue and import official results."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_HOSTS = ("assignmentcenter.uspto.gov", "data.uspto.gov", "api.uspto.gov", "www.uspto.gov")


def load(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def company_names(theme: dict, small_caps: dict) -> dict[str, str]:
    rows = list(theme.get("themes", {}).get("ai_medicine", [])) + list(small_caps.get("companies", []))
    return {r.get("ticker"): r.get("company") for r in rows if r.get("ticker")}


ODP = "https://api.uspto.gov/api/v1/patent/applications"
SUFFIX = re.compile(r",?\s*\b(inc|corp|corporation|ltd|limited|plc|llc|n\.?v|s\.?a|ag|holdings?|co)\b\.?|/nv\b", re.I)


def base_name(name: str) -> str:
    return re.sub(r"\s+", " ", SUFFIX.sub("", name or "").replace(",", " ")).strip()


def applicant_words(name: str) -> set[str]:
    """Significant words of an applicant name: every one of the company's words must appear, so "Tempus" does not
    match "Tempus Steel Ltd" unless the company is called that."""
    return {w for w in re.sub(r"[^a-z0-9 ]", " ", base_name(name).lower()).split() if len(w) > 1}


def odp_get(url: str, key: str) -> dict:
    """GET an Open Data Portal endpoint; the key goes only in the request header, never to disk or logs."""
    req = urllib.request.Request(url, headers={"X-API-KEY": key, "Accept": "application/json", "User-Agent": "serenity-research-agent"})
    cafile = "/etc/ssl/cert.pem" if Path("/etc/ssl/cert.pem").exists() else None
    try:
        with urllib.request.urlopen(req, timeout=40, context=ssl.create_default_context(cafile=cafile)) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {}
        raise


def odp_records(ticker: str, name: str, key: str, fetch=odp_get, max_apps: int = 6) -> tuple[list[dict], int]:
    """Applications filed by the company (applicant field) and their recorded assignments from USPTO ODP.
    Returns (records in the import format, number of applications found)."""
    query = base_name(name)
    wanted = applicant_words(query)
    url = f"{ODP}/search?" + urllib.parse.urlencode({"q": f'applicationMetaData.firstApplicantName:"{query}"', "limit": 25})
    found = fetch(url, key)
    apps = [a for a in found.get("patentFileWrapperDataBag", [])
            if wanted and wanted <= applicant_words(a.get("applicationMetaData", {}).get("firstApplicantName") or "")]
    records = []
    for app in apps[:max_apps]:
        number, meta = app.get("applicationNumberText"), app.get("applicationMetaData", {})
        for bag in fetch(f"{ODP}/{number}/assignment", key).get("patentFileWrapperDataBag", []):
            for a in bag.get("assignmentBag", []):
                records.append({"ticker": ticker, "applicationNumber": number, "inventionTitle": meta.get("inventionTitle"),
                                "applicant": meta.get("firstApplicantName"),
                                "assignee": "; ".join(x.get("assigneeNameText", "") for x in a.get("assigneeBag", [])),
                                "assignor": "; ".join(x.get("assignorName", "") for x in a.get("assignorBag", [])),
                                "recordedAt": a.get("assignmentRecordedDate"), "reelFrame": a.get("reelAndFrameNumber"),
                                "conveyance": a.get("conveyanceText"), "url": a.get("assignmentDocumentLocationURI"),
                                "source": "USPTO Open Data Portal"})
    return records, int(found.get("count") or 0)


def official(record: dict) -> bool:
    url = (record.get("url") or "").lower()
    return bool(record.get("assignee") and record.get("recordedAt") and any(host in url for host in OFFICIAL_HOSTS))


def cached_api_records(previous: dict) -> tuple[list[dict], dict, str | None]:
    """Records from the last live ODP lookup, so a run without the key does not erase them."""
    recs = [r for c in previous.get("companies", []) for r in c.get("officialAssignments", []) + c.get("securityInterests", [])
            if r.get("source") == "USPTO Open Data Portal"]
    clean = [{k: v for k, v in r.items() if k != "independentAssignmentVerified"} for r in recs]
    api = previous.get("api", {})
    return clean, api.get("applicationsFound", {}), api.get("lastLiveLookup")


def build(ownership: dict, names: dict[str, str], imported: dict, api_key_present: bool) -> dict:
    imported_by_ticker: dict[str, list[dict]] = {}
    rejected = []
    for row in imported.get("records", []):
        if official(row):
            imported_by_ticker.setdefault(row.get("ticker"), []).append({**row, "independentAssignmentVerified": True})
        else:
            rejected.append({"ticker": row.get("ticker"), "reason": "Missing assignee, recordedAt, or official USPTO URL"})
    companies = []
    for company in ownership.get("companies", []):
        ticker = company.get("ticker")
        technology = [e for e in company.get("evidence", []) if e.get("relation") != "founder_company"]
        if not technology:
            continue
        all_records = imported_by_ticker.get(ticker, [])
        # A security interest pledges the patents to a lender: it proves debt against the IP, not ownership.
        liens = [r for r in all_records if "SECURITY" in (r.get("conveyance") or "").upper()]
        records = [r for r in all_records if r not in liens]
        name = names.get(ticker) or ticker
        companies.append({"ticker": ticker, "company": name, "status": "verified" if records else "pending-official-search",
                          "secClaims": technology, "officialAssignments": records, "securityInterests": liens,
                          "search": {"assignee": name,
                                     "url": "https://assignmentcenter.uspto.gov/search/intellectualProperty/search",
                                     "instructions": f"Search Assignee for {name}; export the reel/frame, assignor, assignee, recorded date and official result URL."}})
    verified = sum(c["status"] == "verified" for c in companies)
    return {"schemaVersion": 1, "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "status": "verified-partial" if verified else "pending-official-export",
            "method": "SEC claims create the queue; only normalized records from official USPTO hosts independently verify assignment. Name similarity alone never verifies ownership.",
            "api": {"keyConfigured": api_key_present,
                    "note": "USPTO ODP requires an account/API key after June 18, 2026. Assignment Center remains the official manual search source."},
            "summary": {"queued": len(companies), "verifiedCompanies": verified,
                        "companiesWithPatentLiens": sum(bool(c["securityInterests"]) for c in companies),
                        "officialRecords": sum(len(c["officialAssignments"]) for c in companies), "rejectedImports": len(rejected)},
            "companies": companies, "rejectedImports": rejected}


def render(payload: dict) -> str:
    s = payload["summary"]
    lines = ["# USPTO 专利受让独立核验", "",
             f"> 待核验 {s['queued']} 家；已由官方记录核验 {s['verifiedCompanies']} 家；官方记录 {s['officialRecords']} 条。", "",
             "> SEC 中的专利/许可说法只负责建立队列。只有 USPTO Assignment Center/Open Data Portal 的受让记录才能把独立核验改为通过。", "",
             "| 公司 | SEC 说法 | USPTO 状态 | 官方检索 |", "|---|---:|---|---|"]
    for c in payload.get("companies", []):
        lines.append(f"| {c['ticker']} · {c['company']} | {len(c['secClaims'])} | {c['status']} | [按受让人检索]({c['search']['url']}) |")
    liens = [(c["ticker"], r) for c in payload.get("companies", []) for r in c.get("securityInterests", [])]
    if liens:
        lines += ["", "## 专利被抵押给债权人（担保权益）", "", "这不是所有权证明，而是风险：违约时专利可能被债权人取得。", "",
                  "| 公司 | 债权人（登记的受让方） | 申请号 | 登记日 | 卷/帧 |", "|---|---|---|---|---|"]
        for t, r in liens:
            lines.append(f"| {t} | {r['assignee']} | {r.get('applicationNumber', '')} | {r['recordedAt']} | [{r.get('reelFrame', '')}]({r['url']}) |")
    recs = [(c["ticker"], r) for c in payload.get("companies", []) for r in c["officialAssignments"]]
    if recs:
        lines += ["", "## USPTO 官方受让记录", "", "| 公司 | 申请号 | 发明名称 | 受让人 | 转让人 | 登记日 | 卷/帧 |", "|---|---|---|---|---|---|---|"]
        for t, r in recs:
            lines.append(f"| {t} | {r.get('applicationNumber', '')} | {(r.get('inventionTitle') or '')[:60]} | {r['assignee']} | {(r.get('assignor') or '')[:60]} | {r['recordedAt']} | [{r.get('reelFrame', '')}]({r['url']}) |")
    lines += ["", "## 导入规则", "",
              "把官方搜索结果规范化写入 `trend-agent/uspto-assignment-evidence.json`：必须包括 ticker、assignee、assignor、recordedAt、reelFrame、url。",
              "URL 必须来自 USPTO 官方域名；公司网页、Google Patents 或名称相似都不能把状态改为 verified。"]
    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--ownership", default=str(ROOT / "state/technology-ownership.json"))
    p.add_argument("--theme", default=str(ROOT / "trend-agent/theme-company-map.json"))
    p.add_argument("--small-caps", default=str(ROOT / "state/small-cap-stage.json"))
    p.add_argument("--official-evidence", default=str(ROOT / "trend-agent/uspto-assignment-evidence.json"))
    p.add_argument("--state", default=str(ROOT / "state/uspto-assignment-validation.json"))
    p.add_argument("--report", default=str(ROOT / "outputs/uspto-assignment-validation.md"))
    args = p.parse_args()
    ownership = load(Path(args.ownership), {})
    names = company_names(load(Path(args.theme), {}), load(Path(args.small_caps), {}))
    imported = load(Path(args.official_evidence), {"records": []})
    key = os.getenv("USPTO_API_KEY", "").strip()
    api_errors, app_counts, last_live = [], {}, None
    if not key:
        cached, app_counts, last_live = cached_api_records(load(Path(args.state), {}))
        imported["records"] = imported.get("records", []) + cached
    else:
        last_live = datetime.now(timezone.utc).date().isoformat()
        # Live lookup for every queued company; manual exports in the evidence file still count.
        for company in ownership.get("companies", []):
            t = company.get("ticker")
            if not any(e.get("relation") != "founder_company" for e in company.get("evidence", [])):
                continue
            try:
                recs, n = odp_records(t, names.get(t) or t, key)
                imported["records"] = imported.get("records", []) + recs
                app_counts[t] = n
            except Exception as exc:
                api_errors.append({"ticker": t, "error": f"{type(exc).__name__}: {str(exc)[:120]}"})
    payload = build(ownership, names, imported, bool(key))
    payload["api"]["applicationsFound"] = app_counts
    payload["api"]["errors"] = api_errors
    payload["api"]["lastLiveLookup"] = last_live
    Path(args.state).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.report).write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
