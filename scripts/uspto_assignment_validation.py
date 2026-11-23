"""Build an auditable USPTO assignment-validation queue and import official results."""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_HOSTS = ("assignmentcenter.uspto.gov", "data.uspto.gov", "api.uspto.gov", "www.uspto.gov")


def load(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else default


def company_names(theme: dict, small_caps: dict) -> dict[str, str]:
    rows = list(theme.get("themes", {}).get("ai_medicine", [])) + list(small_caps.get("companies", []))
    return {r.get("ticker"): r.get("company") for r in rows if r.get("ticker")}


def official(record: dict) -> bool:
    url = (record.get("url") or "").lower()
    return bool(record.get("assignee") and record.get("recordedAt") and any(host in url for host in OFFICIAL_HOSTS))


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
        records = imported_by_ticker.get(ticker, [])
        name = names.get(ticker) or ticker
        companies.append({"ticker": ticker, "company": name, "status": "verified" if records else "pending-official-search",
                          "secClaims": technology, "officialAssignments": records,
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
    payload = build(load(Path(args.ownership), {}),
                    company_names(load(Path(args.theme), {}), load(Path(args.small_caps), {})),
                    load(Path(args.official_evidence), {"records": []}), bool(os.getenv("USPTO_API_KEY")))
    Path(args.state).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.report).write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
