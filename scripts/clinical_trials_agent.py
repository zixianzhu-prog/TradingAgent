from __future__ import annotations

import argparse
import json
import ssl
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


ADVERSE_STATUSES = {"TERMINATED", "SUSPENDED", "WITHDRAWN"}
TRACKED_FIELDS = ("status", "phases", "enrollment", "completionDate", "resultsFirstPosted", "lastUpdated")


def fetch_studies(api_base: str, query: str, page_size: int = 20) -> list[dict]:
    url = api_base + "?" + urllib.parse.urlencode({"query.term": query, "pageSize": page_size, "format": "json"})
    request = urllib.request.Request(url, headers={"User-Agent": "FocusKPI-Research-Agent/0.1"})
    system_ca = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(system_ca) if system_ca.exists() else None)
    with urllib.request.urlopen(request, timeout=30, context=context) as response:
        return json.load(response).get("studies", [])


def _date(module: dict, key: str) -> str | None:
    value = module.get(key) or {}
    return value.get("date") if isinstance(value, dict) else value


def normalize(study: dict, ticker: str, asset: str) -> dict:
    protocol = study.get("protocolSection", {})
    identification = protocol.get("identificationModule", {})
    status = protocol.get("statusModule", {})
    design = protocol.get("designModule", {})
    conditions = protocol.get("conditionsModule", {})
    sponsor = protocol.get("sponsorCollaboratorsModule", {})
    nct_id = identification.get("nctId")
    return {
        "ticker": ticker,
        "asset": asset,
        "nctId": nct_id,
        "title": identification.get("briefTitle"),
        "status": status.get("overallStatus"),
        "whyStopped": status.get("whyStopped"),
        "phases": design.get("phases", []),
        "enrollment": (design.get("enrollmentInfo") or {}).get("count"),
        "conditions": conditions.get("conditions", []),
        "leadSponsor": (sponsor.get("leadSponsor") or {}).get("name"),
        "completionDate": _date(status, "completionDateStruct"),
        "resultsFirstPosted": _date(status, "resultsFirstPostDateStruct"),
        "lastUpdated": _date(status, "lastUpdatePostDateStruct") or status.get("lastUpdateSubmitDate") or status.get("studyFirstSubmitDate"),
        "url": f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else "",
    }


def compare(previous: dict[str, dict], current: list[dict], baseline: bool) -> list[dict]:
    if baseline:
        return []
    changes = []
    for row in current:
        old = previous.get(row["nctId"])
        if old is None:
            changed = {"newStudy": {"from": None, "to": row["nctId"]}}
        else:
            changed = {
                field: {"from": old.get(field), "to": row.get(field)}
                for field in TRACKED_FIELDS if old.get(field) != row.get(field)
            }
        if not changed:
            continue
        adverse = row.get("status") in ADVERSE_STATUSES
        changes.append({
            "ticker": row["ticker"],
            "asset": row["asset"],
            "nctId": row["nctId"],
            "title": row["title"],
            "url": row["url"],
            "changes": changed,
            "severity": "critical-review" if adverse else "material-review",
            "affectedGates": ["clinical_validation", "falsifiers", "valuation"],
            "status": "pending-revalidation",
        })
    return changes


def build(config: dict, previous_payload: dict | None = None) -> dict:
    studies = []
    errors = []
    for asset in config["assets"]:
        try:
            raw = fetch_studies(config["api_base"], asset["query"], int(config.get("page_size", 20)))
            studies.extend(normalize(study, asset["ticker"], asset["asset"]) for study in raw)
        except Exception as exc:
            errors.append({"ticker": asset["ticker"], "asset": asset["asset"], "error": str(exc)})
    unique = {row["nctId"]: row for row in studies if row.get("nctId")}
    current = sorted(unique.values(), key=lambda row: (row["ticker"], row["asset"], row["nctId"]))
    previous = {row["nctId"]: row for row in (previous_payload or {}).get("studies", [])}
    changes = compare(previous, current, baseline=previous_payload is None)
    risks = [row for row in current if row.get("status") in ADVERSE_STATUSES]
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": "ClinicalTrials.gov API v2",
        "method": "Daily structured snapshot and field-level change detection; changes trigger research only.",
        "studies": current,
        "changes": changes,
        "currentRisks": risks,
        "errors": errors,
        "summary": {
            "studies": len(current),
            "changes": len(changes),
            "adverseStatusStudies": len(risks),
            "errors": len(errors),
        },
    }


def write_report(payload: dict, output: Path) -> None:
    lines = [
        "# ClinicalTrials.gov 临床事件监控", "",
        "> 官方试验状态用于重新验证临床论点，不代表药物有效、获批概率或投资回报。", "",
        "| 股票 | 项目 | NCT | 阶段 | 状态 | 入组 | 最后更新 |",
        "| --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for row in payload["studies"]:
        phases = "/".join(row.get("phases") or []) or "未标注"
        lines.append(f"| {row['ticker']} | {row['asset']} | [{row['nctId']}]({row['url']}) | {phases} | {row['status']} | {row.get('enrollment') or '—'} | {row.get('lastUpdated') or '—'} |")
    lines += ["", "## 今日结构化变化", ""]
    if not payload["changes"]:
        lines.append("没有检测到相对于上一份快照的结构化字段变化；首次运行只建立基线。")
    for row in payload["changes"]:
        lines += [f"### {row['ticker']} · {row['asset']} · {row['severity']}", f"- [{row['title']}]({row['url']})", f"- 变化：`{json.dumps(row['changes'], ensure_ascii=False)}`", f"- 重新检查：{', '.join(row['affectedGates'])}", ""]
    lines += ["", "## 当前不利状态", ""]
    if not payload["currentRisks"]:
        lines.append("当前监控记录中没有 TERMINATED / SUSPENDED / WITHDRAWN 状态。")
    for row in payload["currentRisks"]:
        lines.append(f"- {row['ticker']} · {row['asset']} · [{row['nctId']}]({row['url']})：{row['status']}；{row.get('whyStopped') or '终止原因需查阅完整记录'}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor ClinicalTrials.gov records and emit Serenity revalidation tasks")
    parser.add_argument("--config", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    state_path = Path(args.state)
    previous = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else None
    payload = build(config, previous)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(payload, Path(args.report))
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
