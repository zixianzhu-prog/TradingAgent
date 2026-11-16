"""Download and map the FDA's official AI-enabled medical-device list."""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import ssl
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_COLUMNS = {
    "Date of Final Decision",
    "Submission Number",
    "Device",
    "Company",
    "Panel (Lead)",
    "Primary Product Code",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch_csv(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "SerenityTradeResearch/1.0"})
    # Match the project's other official-source collectors on macOS, where the
    # Python.org interpreter may not inherit Keychain trust automatically.
    cert_file = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(cert_file) if cert_file.exists() else None)
    with urllib.request.urlopen(request, timeout=45, context=context) as response:
        final_url = response.geturl()
        if not final_url.startswith("https://www.fda.gov/"):
            raise ValueError("FDA download redirected outside fda.gov")
        raw = response.read(10_000_001)
        if len(raw) > 10_000_000:
            raise ValueError("FDA CSV exceeds the 10 MB safety limit")
    return raw.decode("utf-8-sig")


def parse_csv(text: str) -> list[dict]:
    rows = list(csv.DictReader(io.StringIO(text)))
    if not rows or not REQUIRED_COLUMNS.issubset(rows[0]):
        raise ValueError("FDA CSV schema is missing required columns")
    parsed = []
    for row in rows:
        submission = row["Submission Number"].strip()
        if not submission:
            continue
        parsed.append(
            {
                "decisionDate": row["Date of Final Decision"].strip(),
                "submissionNumber": submission,
                "device": row["Device"].strip(),
                "manufacturer": row["Company"].strip(),
                "panel": row["Panel (Lead)"].strip(),
                "productCode": row["Primary Product Code"].strip(),
                "fdaUrl": (
                    f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={submission}"
                    if submission.upper().startswith("K")
                    else ""
                ),
            }
        )
    return parsed


def map_companies(rows: list[dict], config: dict) -> tuple[dict[str, list[dict]], list[dict]]:
    mapped = {item["ticker"]: [] for item in config["companies"]}
    ownership_notes = []
    for item in config["companies"]:
        patterns = [re.compile(pattern, re.I) for pattern in item.get("manufacturer_patterns", [])]
        mapped[item["ticker"]] = [row for row in rows if any(pattern.search(row["manufacturer"]) for pattern in patterns)]
        ownership_notes.append(
            {
                "ticker": item["ticker"],
                "company": item["company"],
                "matchedDevices": len(mapped[item["ticker"]]),
                "interpretation": (
                    "direct-or-subsidiary-device-sponsor-evidence"
                    if mapped[item["ticker"]]
                    else "no-direct-device-sponsor-match; retain as adjacent workflow/infrastructure exposure"
                ),
            }
        )
    return mapped, ownership_notes


def build_payload(rows: list[dict], config: dict, previous: dict | None = None) -> dict:
    mapped, notes = map_companies(rows, config)
    prior_ids = {row["submissionNumber"] for row in (previous or {}).get("devices", [])}
    current_ids = {row["submissionNumber"] for row in rows}
    return {
        "generatedAt": utc_now(),
        "status": "ok",
        "source": {
            "publisher": "U.S. Food and Drug Administration",
            "url": config["source_url"],
            "listUrl": config["list_url"],
            "scopeNote": "FDA says the list is periodically updated and is not comprehensive; authorization is product evidence, not proof of revenue, moat, or stock returns.",
        },
        "summary": {
            "totalDevices": len(rows),
            "newSincePreviousSnapshot": len(current_ids - prior_ids) if previous else 0,
            "removedSincePreviousSnapshot": len(prior_ids - current_ids) if previous else 0,
            "latestDecisionDate": rows[0]["decisionDate"] if rows else None,
            "topPanels": Counter(row["panel"] for row in rows).most_common(8),
        },
        "companyCoverage": notes,
        "companyDevices": mapped,
        "devices": rows,
    }


def render(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# FDA AI 医疗设备监控",
        "",
        "> 官方 FDA 授权记录只证明具体设备通过相应上市前路径，不自动证明公司收入、竞争壁垒或股票会上涨。",
        "",
        f"- FDA 清单设备数：**{summary['totalDevices']}**",
        f"- 最新决定日期：**{summary['latestDecisionDate'] or 'n/a'}**",
        f"- 较上次新增/移除：**+{summary['newSincePreviousSnapshot']} / -{summary['removedSincePreviousSnapshot']}**",
        f"- [FDA 官方清单]({payload['source']['listUrl']})",
        "",
        "## 候选公司映射",
        "",
        "| 股票 | 公司 | 匹配设备数 | 解释 | 最近设备 |",
        "|---|---|---:|---|---|",
    ]
    for company in payload["companyCoverage"]:
        devices = payload["companyDevices"].get(company["ticker"], [])
        recent = "；".join(f"{row['decisionDate']} {row['device']} ({row['submissionNumber']})" for row in devices[:3]) or "无直接申报方匹配"
        lines.append(f"| {company['ticker']} | {company['company']} | {company['matchedDevices']} | {company['interpretation']} | {recent} |")
    lines += [
        "",
        "## Serenity 使用边界",
        "",
        "- GEHC、RDNT、ISRG 的匹配记录可支持产品落地与监管验证，但仍需客户采用、收入贡献、替代难度和财报证据。",
        "- IQV 属于临床试验数据与服务层，NVDA 属于算力基础设施层；没有直接设备申报匹配是合理结果，不应被误判为负面信号。",
        "- 新记录只触发证据包更新和 Serenity 重新审查，不会自动产生买入建议或订单。",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor the official FDA AI-enabled medical-device list")
    parser.add_argument("--config", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--input-csv", help="Optional local fixture/offline CSV")
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    state_path, report_path = Path(args.state), Path(args.report)
    previous = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else None
    try:
        text = Path(args.input_csv).read_text(encoding="utf-8-sig") if args.input_csv else fetch_csv(config["source_url"])
        payload = build_payload(parse_csv(text), config, previous)
    except Exception as exc:
        if previous:
            payload = {**previous, "generatedAt": utc_now(), "status": "stale", "fetchError": type(exc).__name__}
        else:
            raise
    state_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(render(payload), encoding="utf-8")
    print(json.dumps({"status": payload["status"], **payload["summary"], "report": str(report_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
