"""Extract strict founder/company and patent/license evidence from saved SEC packets."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEC_HOST = "sec.gov"

RULES = {
    "founder_company": [
        r"\bas a co-founder and our (?:chief executive officer|ceo|president)\b",
        r"\b(?:our|the company's) co-founder(?: and|, who| serves| is)\b",
    ],
    "patent_portfolio": [
        r"\bwe (?:own|hold|control) (?:an? |approximately |over |more than )?(?:global |worldwide )?(?:portfolio of )?\d*[\w -]{0,45}\b(?:patents?|patent families|patent applications)\b",
        r"\bour patent portfolio (?:includes|consists|contains|comprises)\b",
        r"\bpatent (?:applications|families) that we own\b",
    ],
    "exclusive_license": [
        r"\bwe (?:have|obtained|entered into) an? (?:exclusive|co-exclusive) [\w -]{0,40}\blicen[cs]e\b",
        r"\b(?:exclusive|co-exclusive) licen[cs]e (?:to|for) us\b",
        r"\blicen[cs]ed exclusively to us\b",
        r"\bwe (?:have )?(?:in-licensed|sublicensed) [^.]{0,100}\bpatents? from\b",
    ],
    "university_license": [
        r"\b(?:exclusive|co-exclusive) licen[cs]e agreement with (?:the )?[A-Z][^.]{0,100}\b(?:University|Institute|Hospital)\b",
        r"\b(?:University|Institute|Hospital)[^.]{0,100}licen[cs]ed exclusively to us\b",
    ],
}


def sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text or "").strip()
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z])", cleaned) if 20 <= len(s.strip()) <= 1200]


def extract_passage(ticker: str, evidence: dict) -> list[dict]:
    url = evidence.get("url") or ""
    if SEC_HOST not in url.lower():
        return []
    out = []
    for sentence in sentences(evidence.get("text") or evidence.get("quote") or ""):
        for relation, patterns in RULES.items():
            if any(re.search(pattern, sentence, re.I) for pattern in patterns):
                if relation == "patent_portfolio" and re.search(r"\b(?:may|might|could) not\b|\beven if we\b|\bif we (?:own|hold|control)\b", sentence, re.I):
                    continue
                out.append({"ticker": ticker, "relation": relation, "status": "company-disclosed",
                            "source": "SEC filing", "evidenceId": evidence.get("id"), "url": url,
                            "quote": sentence[:1200],
                            "scopeNote": ("Founder/company relationship only; not proof that a specific paper or patent transferred."
                                          if relation == "founder_company" else
                                          "Company-disclosed ownership/license evidence; the specific patent and assignment still require USPTO verification.")})
    return out


def packet_files(directory: Path) -> list[Path]:
    """Use all saved packets: later narrow packets must not erase annual-report evidence."""
    paths = []
    for path in directory.glob("*.json"):
        try:
            ticker = json.loads(path.read_text(encoding="utf-8")).get("ticker")
        except (OSError, json.JSONDecodeError):
            continue
        if ticker:
            paths.append(path)
    return paths


def build(directory: Path) -> dict:
    rows, packets = [], packet_files(directory)
    for path in packets:
        packet = json.loads(path.read_text(encoding="utf-8"))
        for item in packet.get("evidence", []):
            rows.extend(extract_passage(packet["ticker"], item))
    unique = {}
    for row in rows:
        unique[(row["ticker"], row["relation"], row["url"], row["quote"])] = row
    rows = sorted(unique.values(), key=lambda r: (r["ticker"], r["relation"], r["url"]))
    companies = {}
    for row in rows:
        companies.setdefault(row["ticker"], []).append(row)
    return {"schemaVersion": 1, "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "method": "Strict deterministic patterns over saved SEC evidence packets. Company disclosure is not independent USPTO assignment verification.",
            "summary": {"packetsRead": len(packets), "companiesWithEvidence": len(companies),
                        "founderRelations": sum(r["relation"] == "founder_company" for r in rows),
                        "technologyOwnershipClaims": sum(r["relation"] != "founder_company" for r in rows)},
            "companies": [{"ticker": ticker, "evidence": evidence} for ticker, evidence in sorted(companies.items())]}


def render(payload: dict) -> str:
    s = payload["summary"]
    lines = ["# 研究者、创始人与技术归属证据", "",
             f"> 读取 {s['packetsRead']} 家公司的最新证据包；创始人/公司关系 {s['founderRelations']} 条；公司披露的专利或许可 {s['technologyOwnershipClaims']} 条。", "",
             "> 只有明确的 SEC 原句才会进入本表。公司披露的专利/许可仍需 USPTO 专利受让记录或大学技术转移材料做独立复核。", "",
             "| 公司 | 类型 | 状态 | SEC 原文 |", "|---|---|---|---|"]
    for company in payload.get("companies", []):
        for row in company["evidence"]:
            quote = row["quote"].replace("|", "/")
            lines.append(f"| {company['ticker']} | {row['relation']} | {row['status']} | [{quote}]({row['url']}) |")
    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--packets", default=str(ROOT / "state/serenity-codex-inbox"))
    p.add_argument("--state", default=str(ROOT / "state/technology-ownership.json"))
    p.add_argument("--report", default=str(ROOT / "outputs/technology-ownership.md"))
    args = p.parse_args()
    payload = build(Path(args.packets))
    Path(args.state).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.report).write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
