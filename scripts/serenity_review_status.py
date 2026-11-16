"""Which Serenity reviews are current, and which are research views only.

An assessment counts as current only if it was graded on the evidence packet the
pipeline would build today (same input hash). Evidence changes (new filings, fixed
FDA matching, aligned financial periods) make an older review stale even though it
still shows "complete". Claude memos count as research views until their quotes pass
the importer's citation check (a review file tagged -claude- exists).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def build(root: Path = ROOT) -> dict:
    assessed = {r["ticker"]: r for r in load(root / "state/serenity-auto-assessments.json", {}).get("companies", [])}
    packets: dict[str, str] = {}
    for manifest in ("state/serenity-codex-inbox.json", "state/serenity-codex-queue.json"):
        for row in load(root / manifest, {}).get("companies", []):
            packets[row["ticker"]] = row["inputHash"]
    claude_packets = {row["ticker"]: row["inputHash"] for row in load(root / "state/serenity-claude-queue.json", {}).get("companies", [])}
    memos = {r["ticker"] for r in load(root / "state/serenity-claude-verdicts.json", {}).get("companies", [])}
    companies = {}
    for ticker in sorted(set(assessed) | set(packets) | memos):
        row = assessed.get(ticker)
        imported_claude = bool(row and "-claude-" in str(row.get("review_path", "")))
        if row is None:
            review = "not reviewed"
        elif imported_claude:
            # A Claude review is current if it matches the citation-checked packet built from today's filings.
            review = "current" if row.get("input_hash") == claude_packets.get(ticker) else "stale"
        elif ticker not in packets:
            review = "no current packet"
        elif row.get("input_hash") == packets[ticker]:
            review = "current"
        else:
            review = "stale"
        imported = bool(row and "-claude-" in str(row.get("review_path", "")))
        companies[ticker] = {
            "review": review,
            "reviewer": "Claude" if imported else ("Codex" if row else None),
            "claudeMemo": ("citation-checked" if imported else "pending citation check") if ticker in memos else None,
        }
    count = lambda key, value: sum(1 for c in companies.values() if c[key] == value)
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {"current": count("review", "current"), "stale": count("review", "stale"),
                    "notReviewed": count("review", "not reviewed"), "noCurrentPacket": count("review", "no current packet"),
                    "claudePending": count("claudeMemo", "pending citation check"), "claudeChecked": count("claudeMemo", "citation-checked")},
        "anyFullPass": any(r.get("serenity_decision") == "research-ready" for r in assessed.values()),
        "companies": companies,
    }


def main() -> None:
    payload = build()
    (ROOT / "state/serenity-review-status.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(payload["summary"]))


if __name__ == "__main__":
    main()
