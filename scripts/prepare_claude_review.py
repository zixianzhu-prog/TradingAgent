"""Turn the Claude Serenity memos into citation-checked reviews the importer accepts.

The memos quote 10-K, 20-F, 10-Q and 8-K text. This script:
1. fetches every cited SEC filing (needs SEC_USER_AGENT with your own contact, per
   SEC's fair-access policy) into state/serenity-source-cache/;
2. finds each quote in the filing text (typography such as curly quotes and
   non-breaking hyphens is normalised, wording is not) and keeps the surrounding
   ~2,400 characters as an evidence passage;
3. writes one packet per company plus a manifest (state/serenity-claude-queue.json)
   and the review (state/serenity-claude-response.json, reviewer "Claude").

Quotes not found in the filing are dropped and listed under "missing", so the
importer's own checks decide what survives. Then run:
    ./scripts/finalize_codex_serenity.sh state/serenity-claude-response.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import serenity_evidence_review as ser

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "state/serenity-source-cache"
TYPO = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "‑": "-", "‐": "-", "–": "-", " ": " "})
WINDOW = 1200
MAX_BYTES = 25_000_000  # inline-XBRL 10-K files run 5-15 MB, above the 2 MB cap used for press pages


def fetch_sec(url: str) -> str:
    """Download an SEC filing with the caller's contact User-Agent and return clean text."""
    import urllib.request

    request = urllib.request.Request(url, headers={"User-Agent": os.environ["SEC_USER_AGENT"], "Accept-Encoding": "identity"})
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
    with opener.open(request, timeout=60) as response:
        if not ser.host_matches(response.geturl(), {"sec.gov"}):
            raise ValueError("Redirect left sec.gov")
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Filing exceeds 25 MB")
    return ser.clean(data.decode("utf-8", errors="replace"))


def filing_text(url: str, allow_fetch: bool) -> str | None:
    path = CACHE / (ser.digest(url) + ".json")
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8")).get("text")
    if not allow_fetch:
        return None
    text = fetch_sec(url)
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"title": url, "text": text, "url": url, "publishedAt": "", "observedAt": ser.now(),
                                "provenance": "primary-document", "primary": True, "path": str(path.relative_to(ROOT))},
                               ensure_ascii=False), encoding="utf-8")
    return text


def locate(text: str, quote: str) -> tuple[str, str] | None:
    """Return (exact quote as it appears, surrounding passage), or None if absent.

    The typography map replaces single characters with single characters, so an index
    found in the normalised text is the same index in the original.
    """
    normalised_text, normalised_quote = text.translate(TYPO), ser.clean(quote).translate(TYPO)
    index = normalised_text.find(normalised_quote)
    if index < 0:
        return None
    exact = text[index:index + len(normalised_quote)]
    return exact, text[max(0, index - WINDOW): index + len(normalised_quote) + WINDOW]


def passage_for(by_id: dict, q: dict) -> dict | None:
    """The passage a quoted fact came from. The model sometimes renames passage ids (b1, b2, ...) while quoting them
    verbatim, so an unknown id falls back to the passage that contains the quote; the quote is still checked against the
    full filing afterwards."""
    p = by_id.get(q.get("id"))
    if p:
        return p
    quote = q.get("quote") or ""
    return next((x for x in by_id.values() if quote and locate(x.get("text", ""), quote)), None)


def build(citations: dict, skills: list[dict], allow_fetch: bool) -> tuple[dict, dict, dict]:
    skill_files = [{k: s[k] for k in ("name", "path", "sha256")} for s in skills]
    manifest = {"generatedAt": ser.now(), "provider": "Claude", "requiresApiKey": False, "rubric": ser.GATES,
                "skillFiles": skill_files, "responsePath": "state/serenity-claude-response.json", "companies": []}
    response = {"generatedAt": ser.now(), "reviewer": "Claude", "reviews": []}
    report = {}
    inbox = ROOT / "state/serenity-codex-inbox"
    inbox.mkdir(parents=True, exist_ok=True)
    for ticker, company in citations["companies"].items():
        passages, found, lost = {}, 0, []
        gates_out = {}
        for gate, item in company["gates"].items():
            out = {k: item.get(k, []) for k in ("missing", "falsifiers")}
            out.update({"status": item["status"], "reason": item["reason"], "support": [], "counter": []})
            for side in ("support", "counter"):
                for ref in item.get(side, []):
                    try:
                        text = filing_text(ref["url"], allow_fetch)
                    except Exception as exc:  # one unreachable filing must not stop the others
                        text = None
                        report.setdefault("_fetchErrors", {})[ref["url"]] = str(exc)[:120]
                    hit = locate(text, ref["quote"]) if text else None
                    if not hit:
                        lost.append(ref["quote"][:60])
                        out["missing"] = out["missing"] + [f"未在原文中找到引用：{ref['quote'][:60]}"]
                        continue
                    exact, passage = hit
                    pid = "ev_" + ser.digest([ref["url"], passage])[:16]
                    passages[pid] = {"id": pid, "title": ref["url"].rsplit("/", 1)[-1], "text": passage, "url": ref["url"],
                                     "publishedAt": "", "observedAt": ser.now(), "provenance": "primary-document", "primary": True,
                                     "path": "state/serenity-source-cache", "sha256": ser.digest(passage)}
                    out[side].append({"id": pid, "quote": exact})
                    found += 1
            gates_out[gate] = out
        evidence = list(passages.values())
        identity = ser.digest([ser.VERSION, "claude", ser.GATES, [s["sha256"] for s in skills],
                               [{k: v for k, v in p.items() if k != "observedAt"} for p in evidence]])
        packet_path = inbox / f"{ticker}-claude-{identity[:20]}.json"
        packet_path.write_text(json.dumps({"ticker": ticker, "inputHash": identity, "generatedAt": ser.now(), "reviewer": "Claude",
                                           "rubric": ser.GATES, "skillFiles": skill_files, "evidence": evidence}, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest["companies"].append({"ticker": ticker, "inputHash": identity, "packetPath": str(packet_path.relative_to(ROOT)),
                                      "status": "pending", "evidencePassages": len(evidence)})
        response["reviews"].append({"ticker": ticker, "inputHash": identity, "gates": gates_out})
        report[ticker] = {"quotesFound": found, "quotesMissing": len(lost), "missing": lost}
    return manifest, response, report


def main() -> None:
    parser = argparse.ArgumentParser(description="Build citation-checked Claude Serenity reviews from the memo quotes")
    parser.add_argument("--citations", default=str(ROOT / "state/serenity-claude-citations.json"))
    parser.add_argument("--cache-only", action="store_true", help="Use cached filings only; do not fetch")
    args = parser.parse_args()
    allow_fetch = not args.cache_only
    if allow_fetch and "@" not in os.getenv("SEC_USER_AGENT", ""):
        sys.exit("SEC requires a User-Agent with your contact email to download filings. Run:\n"
                 '  export SEC_USER_AGENT="Your Name your.email@example.com"\n'
                 "then run this script again (or pass --cache-only to use filings already cached).")
    citations = json.loads(Path(args.citations).read_text(encoding="utf-8"))
    manifest, response, report = build(citations, ser.methodology(), allow_fetch)
    (ROOT / "state/serenity-claude-queue.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "state/serenity-claude-response.json").write_text(json.dumps(response, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"report": report, "next": "./scripts/finalize_codex_serenity.sh state/serenity-claude-response.json"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
