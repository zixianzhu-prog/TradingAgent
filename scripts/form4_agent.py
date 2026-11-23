from __future__ import annotations

import argparse
import json
import os
import ssl
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

# www.sec.gov answers 403 without a contact in the User-Agent (SEC fair-access policy).
USER_AGENT = os.getenv("SEC_USER_AGENT") or "FocusKPI-Research-Agent/0.1"
CODE_LABELS = {
    "P": "公开市场买入",
    "S": "公开市场卖出",
    "A": "授予/奖励",
    "M": "期权行权或转换",
    "F": "以股份支付税款",
    "G": "赠与",
    "D": "处置给发行人",
}


def fetch(url: str) -> bytes:
    context = ssl.create_default_context(cafile="/etc/ssl/cert.pem")
    # A blocked SEC endpoint must not hold the entire daily pipeline for minutes.
    # The report records the failure explicitly and the next scheduled run retries it.
    for attempt in range(1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json, application/xml, text/xml, */*"})
            with urllib.request.urlopen(request, context=context, timeout=8) as response:
                result = response.read()
            time.sleep(0.15)
            return result
        except urllib.error.HTTPError as exc:
            if exc.code not in {403, 429} or attempt == 0:
                raise
            time.sleep(2 ** attempt)
    raise RuntimeError("unreachable")


def text(node: ET.Element | None, path: str, default: str = "") -> str:
    if node is None:
        return default
    value = node.findtext(path)
    return value.strip() if value else default


def number(value: str) -> float | None:
    try:
        return float(value.replace(",", ""))
    except (AttributeError, ValueError):
        return None


def parse_form4(xml: bytes, filing: dict) -> dict:
    root = ET.fromstring(xml)
    owner = root.find("reportingOwner")
    relationship = owner.find("reportingOwnerRelationship") if owner is not None else None
    roles = []
    for tag, label in (("isDirector", "董事"), ("isOfficer", "高管"), ("isTenPercentOwner", "10%股东"), ("isOther", "其他")):
        if text(relationship, tag) in {"1", "true", "True"}:
            roles.append(label)
    officer_title = text(relationship, "officerTitle")
    if officer_title:
        roles.append(officer_title)
    transactions = []
    for item in root.findall("./nonDerivativeTable/nonDerivativeTransaction"):
        code = text(item, "transactionCoding/transactionCode")
        shares = number(text(item, "transactionAmounts/transactionShares/value"))
        price = number(text(item, "transactionAmounts/transactionPricePerShare/value"))
        acquired_disposed = text(item, "transactionAmounts/transactionAcquiredDisposedCode/value")
        transaction = {
            "security": text(item, "securityTitle/value"),
            "date": text(item, "transactionDate/value"),
            "code": code,
            "codeLabel": CODE_LABELS.get(code, "其他申报交易"),
            "shares": shares,
            "price": price,
            "value": round(shares * price, 2) if shares is not None and price is not None else None,
            "direction": acquired_disposed,
            "sharesAfter": number(text(item, "postTransactionAmounts/sharesOwnedFollowingTransaction/value")),
            "isOpenMarket": code in {"P", "S"},
        }
        transactions.append(transaction)
    return {
        **filing,
        "issuer": text(root, "issuer/issuerName"),
        "owner": text(owner, "reportingOwnerId/rptOwnerName", "未标注"),
        "roles": roles,
        "periodOfReport": text(root, "periodOfReport"),
        "transactions": transactions,
    }


def filing_rows(submissions: dict, ticker: str, cik: str, cutoff: date) -> list[dict]:
    recent = submissions.get("filings", {}).get("recent", {})
    keys = ("form", "accessionNumber", "filingDate", "primaryDocument")
    if not all(key in recent for key in keys):
        return []
    rows = []
    for form, accession, filing_date, primary in zip(*(recent[key] for key in keys)):
        if form != "4" or date.fromisoformat(filing_date) < cutoff:
            continue
        accession_plain = accession.replace("-", "")
        raw_document = primary.split("/")[-1]
        base = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_plain}"
        rows.append({
            "ticker": ticker,
            "accession": accession,
            "filingDate": filing_date,
            "url": f"{base}/{primary}",
            "rawUrl": f"{base}/{raw_document}",
        })
    return rows


def build(config: dict, previous: dict | None, today: date | None = None, fetcher=fetch) -> dict:
    today = today or datetime.now(timezone.utc).date()
    cutoff = today - timedelta(days=int(config.get("lookback_days", 120)))
    known = set((previous or {}).get("knownAccessions", []))
    cached = {row["accession"]: row for row in (previous or {}).get("filings", [])}
    baseline = previous is None
    filings, errors = [], []
    for company in config.get("companies", []):
        cik, ticker = company["cik"].zfill(10), company["ticker"]
        try:
            submissions = json.loads(fetcher(f"https://data.sec.gov/submissions/CIK{cik}.json"))
            rows = filing_rows(submissions, ticker, cik, cutoff)[: int(config.get("max_filings_per_company", 5))]
            for filing in rows:
                if filing["accession"] in cached and cached[filing["accession"]].get("parseStatus") == "verified":
                    filings.append(cached[filing["accession"]])
                    continue
                try:
                    filings.append({**parse_form4(fetcher(filing["rawUrl"]), filing), "parseStatus": "verified"})
                except Exception as exc:
                    filings.append({**filing, "issuer": company.get("name", ticker), "owner": "待读取", "roles": [], "periodOfReport": "", "transactions": [], "parseStatus": "error"})
                    errors.append({"ticker": ticker, "accession": filing["accession"], "error": str(exc)})
        except Exception as exc:
            errors.append({"ticker": ticker, "error": str(exc)})
    filings.sort(key=lambda row: (row["filingDate"], row["accession"]), reverse=True)
    new_filings = [] if baseline else [row for row in filings if row["accession"] not in known]
    market_transactions = [
        {**transaction, "ticker": filing["ticker"], "owner": filing["owner"], "roles": filing["roles"], "accession": filing["accession"], "url": filing["url"], "isNew": filing in new_filings}
        for filing in filings for transaction in filing["transactions"] if transaction["isOpenMarket"]
    ]
    unresolved = sum(row.get("parseStatus") == "error" for row in filings)
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "mode": "baseline" if baseline else "monitor",
        "method": "SEC Form 4 deterministic XML parsing; P/S are open-market transactions, while A/M/F/G are not treated as insider buying or selling.",
        "summary": {
            "filings": len(filings),
            "newFilings": len(new_filings),
            "openMarketTransactions": len(market_transactions),
            "errors": max(len(errors), unresolved),
        },
        "filings": filings,
        "newFilings": new_filings,
        "marketTransactions": market_transactions,
        "errors": errors,
        "knownAccessions": sorted({row["accession"] for row in filings} | known),
        "researchPolicy": "A new filing triggers research only. It never changes a rating or creates an order automatically.",
        "affectedGates": ["management_alignment", "ownership_signal", "valuation_review"],
    }


def render(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# SEC Form 4 内幕交易监控", "",
        "> 只把 P（公开市场买入）与 S（公开市场卖出）视为主动市场交易；A/M/F/G 等授予、行权、纳税或赠与不会被误报为买卖。新申报仅触发研究，不改变评级、不下单。", "",
        f"模式：`{payload['mode']}`；近期开表 {summary['filings']} 份；本次新增 {summary['newFilings']} 份；已确认公开市场交易 {summary['openMarketTransactions']} 笔；读取错误 {summary['errors']}。", "",
        "## 公开市场交易", "",
        "| 日期 | 股票 | 内部人 | 类型 | 股数 | 价格 | 金额 | 申报 |",
        "|---|---|---|---|---:|---:|---:|---|",
    ]
    for row in payload["marketTransactions"]:
        value = f"${row['value']:,.0f}" if row["value"] is not None else "—"
        price = f"${row['price']:,.2f}" if row["price"] is not None else "—"
        lines.append(f"| {row['date']} | {row['ticker']} | {row['owner']} | {row['code']} {row['codeLabel']} | {row['shares'] or 0:,.0f} | {price} | {value} | [SEC]({row['url']}) |")
    if not payload["marketTransactions"]:
        lines.append("| — | — | — | 近期开表中未发现 P/S 交易 | — | — | — | — |")
    lines += ["", "## 最近申报（含非市场交易）", ""]
    for filing in payload["filings"][:20]:
        codes = ", ".join(f"{row['code']} {row['codeLabel']}" for row in filing["transactions"]) or ("原始 XML 暂未读取" if filing.get("parseStatus") == "error" else "无非衍生交易明细")
        marker = " **NEW**" if filing in payload["newFilings"] else ""
        lines.append(f"- {filing['filingDate']} · {filing['ticker']} · {filing['owner']} · {codes} · [SEC 原始申报]({filing['url']}){marker}")
    lines += ["", "## 解释规则", "", "- P：内部人在公开市场用资金买入，可作为管理层信心的一个辅助信号。", "- S：公开市场卖出，需要结合预设交易计划、持股比例、税务和连续性判断，不能单独视为看空。", "- A/M/F/G：奖励、期权行权、代扣税或赠与，不等于主动买卖。", "- Form 4 只是一个验证信号，不能替代临床、财报、估值和 Serenity 供应链证据。", ""]
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Monitor official SEC Form 4 filings")
    parser.add_argument("--config", required=True)
    parser.add_argument("--state", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()
    state_path, report_path = Path(args.state), Path(args.report)
    previous = json.loads(state_path.read_text()) if state_path.is_file() else None
    payload = build(json.loads(Path(args.config).read_text()), previous)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
