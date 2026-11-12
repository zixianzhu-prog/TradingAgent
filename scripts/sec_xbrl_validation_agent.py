from __future__ import annotations

import argparse
import json
import re
import ssl
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


METRICS = {
    "quarterly_revenue_m": ("USD", ("RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues", "SalesRevenueNet"), "quarter"),
    "quarterly_net_income_m": ("USD", ("NetIncomeLoss", "ProfitLoss"), "quarter"),
    "research_and_development_m": ("USD", ("ResearchAndDevelopmentExpense",), "quarter"),
    "cash_m": ("USD", ("CashAndCashEquivalentsAtCarryingValue",), "instant"),
    "cash_and_short_investments_m": ("USD", ("CashCashEquivalentsAndShortTermInvestments",), "instant"),
    "shares": ("shares", ("CommonStockSharesOutstanding", "EntityCommonStockSharesOutstanding"), "instant"),
}
LOCAL_COMPARISONS = {
    "quarterly_revenue_m": "quarterly_revenue_m",
    "quarterly_net_income_m": "quarterly_net_income_m",
    "cash_and_short_investments_m": "cash_and_securities_m",
    "shares": "shares",
}


def fetch_companyfacts(cik: str) -> dict:
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    request = urllib.request.Request(url, headers={"User-Agent": "FocusKPI-Research-Agent/0.1"})
    system_ca = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(system_ca) if system_ca.exists() else None)
    with urllib.request.urlopen(request, timeout=40, context=context) as response:
        return json.load(response)


def select_fact(payload: dict, tags: tuple[str, ...], unit: str, mode: str) -> dict | None:
    candidates = []
    for namespace in ("us-gaap", "dei", "ifrs-full"):
        facts = payload.get("facts", {}).get(namespace, {})
        for priority, tag in enumerate(tags):
            entries = facts.get(tag, {}).get("units", {}).get(unit, [])
            for entry in entries:
                if entry.get("form") not in {"10-Q", "10-K", "20-F", "40-F"}:
                    continue
                frame = entry.get("frame", "")
                if mode == "quarter" and not re.fullmatch(r"CY\d{4}Q[1-4]", frame):
                    continue
                if mode == "instant" and entry.get("start"):
                    continue
                candidates.append((entry.get("filed", ""), entry.get("end", ""), -priority, namespace, tag, entry))
    if not candidates:
        return None
    _, _, _, namespace, tag, entry = max(candidates)
    scale = 1_000_000 if unit == "USD" else 1
    return {
        "value": entry["val"] / scale,
        "unit": "USD_m" if unit == "USD" else unit,
        "tag": f"{namespace}:{tag}",
        "periodStart": entry.get("start"),
        "periodEnd": entry.get("end"),
        "filed": entry.get("filed"),
        "form": entry.get("form"),
        "frame": entry.get("frame"),
        "accession": entry.get("accn"),
    }


def extract_metrics(payload: dict) -> dict:
    return {
        name: select_fact(payload, tags, unit, mode)
        for name, (unit, tags, mode) in METRICS.items()
    }


def validate_company(ticker: str, official: dict, local: dict, skip_comparisons: set[str] | None = None) -> dict:
    skip_comparisons = skip_comparisons or set()
    checks = []
    for metric, local_key in LOCAL_COMPARISONS.items():
        fact = official.get(metric)
        local_value = local.get(local_key)
        if metric in skip_comparisons:
            checks.append({"metric": metric, "status": "semantic-skip", "official": fact, "local": local_value})
            continue
        if fact is None or local_value is None:
            checks.append({"metric": metric, "status": "unavailable", "official": fact, "local": local_value})
            continue
        official_value = float(fact["value"])
        local_value = float(local_value)
        ratio = 0.05 if metric == "cash_and_short_investments_m" else 0.02
        tolerance = max(0.5, abs(official_value) * ratio) if fact["unit"] == "USD_m" else max(1_000_000, abs(official_value) * ratio)
        difference = local_value - official_value
        checks.append({
            "metric": metric,
            "status": "pass" if abs(difference) <= tolerance else "review",
            "official": official_value,
            "local": local_value,
            "difference": difference,
            "tolerance": tolerance,
            "tag": fact["tag"],
            "filed": fact["filed"],
            "periodEnd": fact["periodEnd"],
        })
    review = [check for check in checks if check["status"] == "review"]
    available = [check for check in checks if check["status"] not in {"unavailable", "semantic-skip"}]
    return {
        "ticker": ticker,
        "status": "review" if review else "verified" if available else "insufficient-xbrl",
        "checks": checks,
        "reviewMetrics": [check["metric"] for check in review],
        "affectedGates": ["earnings_validation", "valuation", "cash_runway", "dilution"] if review else [],
        "note": "XBRL comparison validates matching accounting concepts only; unavailable tags are not treated as failures.",
    }


def build(config: dict, financials: dict) -> dict:
    local = {row["ticker"]: row for row in financials.get("companies", [])}
    companies = []
    errors = []
    for company in config["companies"]:
        ticker = company["ticker"]
        try:
            payload = fetch_companyfacts(company["cik"])
            official = extract_metrics(payload)
            row = validate_company(ticker, official, local.get(ticker, {}), set(company.get("skip_comparisons", [])))
            row["skipReason"] = company.get("skip_reason")
            row["entityName"] = payload.get("entityName")
            row["cik"] = company["cik"]
            row["source"] = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{company['cik']}.json"
            row["officialFacts"] = official
            companies.append(row)
        except Exception as exc:
            errors.append({"ticker": ticker, "error": str(exc)})
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "method": "Deterministic SEC XBRL Company Facts extraction and local-value comparison; no automatic overwrite.",
        "companies": companies,
        "errors": errors,
        "summary": {
            "verified": sum(row["status"] == "verified" for row in companies),
            "review": sum(row["status"] == "review" for row in companies),
            "insufficient": sum(row["status"] == "insufficient-xbrl" for row in companies),
            "errors": len(errors),
        },
    }


def write_report(payload: dict, output: Path) -> None:
    labels = {
        "quarterly_revenue_m": "季度收入",
        "quarterly_net_income_m": "季度净利润/亏损",
        "cash_and_short_investments_m": "现金及短期投资",
        "shares": "流通股份",
    }
    lines = [
        "# SEC XBRL 财务数字自动核验", "",
        "> 只比较会计含义匹配的字段。缺失的标准标签不会被判定为失败，系统也不会自动覆盖人工确认的数据。", "",
        "| 股票 | 状态 | 通过 | 待审 | 无可比标签 |",
        "| --- | --- | ---: | ---: | ---: |",
    ]
    for row in payload["companies"]:
        lines.append(f"| {row['ticker']} | {row['status']} | {sum(c['status']=='pass' for c in row['checks'])} | {sum(c['status']=='review' for c in row['checks'])} | {sum(c['status'] in {'unavailable','semantic-skip'} for c in row['checks'])} |")
    for row in payload["companies"]:
        lines += ["", f"## {row['ticker']} · {row['status']}", "", f"[SEC Company Facts 原始 JSON]({row['source']})", "", "| 指标 | 本地值 | SEC值 | 差异 | 结果 | XBRL标签 |", "| --- | ---: | ---: | ---: | --- | --- |"]
        for check in row["checks"]:
            fact = check.get("official")
            official_value = fact if isinstance(fact, (int, float)) else "—"
            diff = check.get("difference", "—")
            lines.append(f"| {labels.get(check['metric'], check['metric'])} | {check.get('local') if check.get('local') is not None else '—'} | {official_value} | {diff} | {check['status']} | {check.get('tag', '—')} |")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate local AI Medicine financials against SEC XBRL Company Facts")
    parser.add_argument("--config", required=True)
    parser.add_argument("--financials", required=True)
    parser.add_argument("--json-output", required=True)
    parser.add_argument("--markdown-output", required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    financials = json.loads(Path(args.financials).read_text(encoding="utf-8"))
    payload = build(config, financials)
    target = Path(args.json_output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(payload, Path(args.markdown_output))
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
