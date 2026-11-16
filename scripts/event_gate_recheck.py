"""Event -> Serenity gate re-check -> recorded outcome.

A primary-source event (today: an FDA device decision from fda_device_feed.py) does not
change a rating by itself. It reopens specific Serenity gates, and the re-check must
quote primary text like any other review. This script makes that loop explicit and
auditable.

  prepare  For each new FDA AI-device decision by a company with a current Claude
           review: fetch the FDA record page and the 510(k)/De Novo summary PDF,
           keep the passages a reviewer needs (indications, predicate comparison, AI
           description, change-control plan), append them to the company's evidence
           packet, and write a task with the gate questions and the gate statuses
           before the re-check. A reading sheet is written for the reviewer.

  apply    Merge the reviewer's updated gates (state/event-recheck-response.json)
           into the Claude review, run the normal import (every quote re-checked
           word for word), then record the statuses after the re-check.

Trace: state/event-rechecks.json, one entry per event:
  event -> gates reopened -> before -> after -> citation check -> what changed.

PDF text needs pypdf. If this environment lacks it, set PDF_TEXT_PYTHON to an
interpreter that has it (the GPT Researcher environment does); without either the
re-check uses the FDA record page only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import urllib.request
from datetime import datetime, timezone
from html import unescape
from pathlib import Path

import serenity_evidence_review as ser

ROOT = Path(__file__).resolve().parents[1]
TRACE = ROOT / "state/event-rechecks.json"
CACHE = ROOT / "state/serenity-source-cache/fda"
WINDOW = 600
# What an FDA decision can and cannot tell Serenity.
GATE_QUESTIONS = {
    "chokepoint_evidence": "Does this decision add a regulatory barrier competitors lack (De Novo, first-of-kind, new indication), "
                           "or is it substantially equivalent to a device that already exists?",
    "pure_play": "Does the cleared device put AI at the core of the product, or is AI a feature of a broader system?",
    "counter_thesis": "Does the predicate device show a competitor with equal or broader cleared functions?",
}
SUMMARY_MARKERS = ["Indications for Use (Describe)", "Predicate Device", "Substantial Equivalence", "artificial intelligence",
                   "machine learning", "deep learning", "AI ", "Predetermined Change Control Plan", "does not include"]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fetch(url: str, binary: bool = False):
    request = urllib.request.Request(url, headers={"User-Agent": "serenity-research-agent"})
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
    with opener.open(request, timeout=60) as response:
        data = response.read()
    return data if binary else data.decode("utf-8", "ignore")


def record_text(html: str) -> str:
    """The decision table from an FDA 510(k)/De Novo record page."""
    text = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", html)))
    start = text.find("Device Classification Name")
    end = text.find("This website has been translated")
    return text[start:end if end > start else start + 1500].strip() if start >= 0 else ""


def summary_url(event: dict) -> str:
    """Summary PDF location: cdrh_docs/pdfYY/<number>.pdf, YY from the submission number."""
    number = event["id"]
    year = number[3:5] if number.upper().startswith("DEN") else number[1:3]
    return f"https://www.accessdata.fda.gov/cdrh_docs/{'reviews' if number.upper().startswith('DEN') else 'pdf' + year}/{number}.pdf"


def pdf_text(path: Path) -> str:
    try:
        import pypdf  # noqa: F401
        reader = pypdf.PdfReader(str(path))
        return re.sub(r"\s+", " ", " ".join((p.extract_text() or "") for p in reader.pages))
    except ImportError:
        pass
    interpreter = os.getenv("PDF_TEXT_PYTHON") or str(ROOT / "work/gpt-researcher-venv/bin/python")
    if not Path(interpreter).exists():
        return ""
    code = ("import re,sys,pypdf;r=pypdf.PdfReader(sys.argv[1]);"
            "print(re.sub(r'\\s+',' ',' '.join((p.extract_text() or '') for p in r.pages)))")
    result = subprocess.run([interpreter, "-I", "-c", code, str(path)], capture_output=True, text=True, timeout=120)
    return result.stdout.strip() if result.returncode == 0 else ""


def passages_for(event: dict) -> tuple[list[dict], list[str]]:
    """Primary passages from the FDA record and summary, in the evidence-packet shape."""
    errors, out = [], []

    def add(title: str, text: str, url: str) -> None:
        pid = "ev_" + ser.digest([url, text])[:16]
        out.append({"id": pid, "topic": "fda-decision", "title": title, "text": text, "url": url, "publishedAt": event["decisionDate"],
                    "observedAt": now(), "provenance": "primary-document", "primary": True,
                    "path": "state/serenity-source-cache/fda", "sha256": ser.digest(text)})

    try:
        record = record_text(fetch(event["url"]))
        if record:
            add(f"FDA record {event['id']}", record, event["url"])
    except Exception as exc:
        errors.append(f"record: {str(exc)[:100]}")
    CACHE.mkdir(parents=True, exist_ok=True)
    pdf_path = CACHE / f"{event['id']}.pdf"
    try:
        if not pdf_path.exists():
            pdf_path.write_bytes(fetch(summary_url(event), binary=True))
        text = pdf_text(pdf_path)
        taken: list[int] = []
        for marker in SUMMARY_MARKERS:
            for match in list(re.finditer(re.escape(marker), text))[:2]:
                if any(abs(match.start() - t) < WINDOW for t in taken):
                    continue
                taken.append(match.start())
                add(f"FDA summary {event['id']} · {marker.strip()}", text[max(0, match.start() - 150): match.start() + WINDOW], summary_url(event))
        if not text:
            errors.append("summary: no PDF text extractor available")
    except Exception as exc:
        errors.append(f"summary: {str(exc)[:100]}")
    return out, errors


def load(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


def prepare(root: Path = ROOT, tickers: set[str] | None = None) -> list[dict]:
    feed = load(root / "state/fda-device-events.json", {})
    trace = load(TRACE, {"rechecks": []})
    done = {r["eventId"] for r in trace["rechecks"]}
    manifest_path = root / "state/serenity-claude-queue.json"
    manifest = load(manifest_path, {"companies": []})
    entries = {c["ticker"]: c for c in manifest["companies"]}
    assessments = {a["ticker"]: a for a in load(root / "state/serenity-auto-assessments.json", {}).get("companies", [])}
    verdicts = {v["ticker"]: v for v in load(root / "state/serenity-claude-verdicts.json", {}).get("companies", [])}
    skills = ser.methodology()
    tasks, sheet = [], []
    for event in feed.get("events", []):
        ticker = event.get("ticker")
        if (event.get("aiConfidence") != "high" or not event.get("covered") or event["id"] in done
                or (tickers and ticker not in tickers) or ticker not in entries):
            continue
        new_passages, errors = passages_for(event)
        if not new_passages:
            continue
        entry = entries[ticker]
        packet = load(root / entry["packetPath"], {})
        evidence = [p for p in packet.get("evidence", []) if p["id"] not in {n["id"] for n in new_passages}] + new_passages
        identity = ser.digest([ser.VERSION, "claude-event", ser.GATES, [s["sha256"] for s in skills],
                               [{k: v for k, v in p.items() if k != "observedAt"} for p in evidence]])
        packet_path = root / "state/serenity-codex-inbox" / f"{ticker}-claude-{identity[:20]}.json"
        packet_path.write_text(json.dumps({**packet, "inputHash": identity, "generatedAt": now(), "evidence": evidence}, ensure_ascii=False, indent=2),
                               encoding="utf-8")
        entry.update({"inputHash": identity, "packetPath": str(packet_path.relative_to(root)), "status": "pending",
                      "evidencePassages": len(evidence)})
        before = {gate: assessments.get(ticker, {}).get(gate, "unknown") for gate in GATE_QUESTIONS}
        task = {"eventId": event["id"], "ticker": ticker, "event": {k: event.get(k) for k in ("label", "device", "applicant", "decisionDate", "url", "publicAt")},
                "gatesReopened": list(GATE_QUESTIONS), "questions": GATE_QUESTIONS, "before": before,
                "tierBefore": verdicts.get(ticker, {}).get("tier"), "newPassages": [p["id"] for p in new_passages],
                "inputHash": identity, "sourceErrors": errors, "status": "awaiting review", "preparedAt": now()}
        tasks.append(task)
        sheet.append(f"### {ticker} · FDA {event['label']} {event['id']} ({event['decisionDate']}): {event['device']}\ninputHash {identity}")
        for gate, question in GATE_QUESTIONS.items():
            current = assessments.get(ticker, {}).get("gate_reviews", {}).get(gate, {})
            sheet.append(f"- {gate} (now {before[gate]}): {question}\n  current reason: {current.get('reason', '')}")
        sheet += [f"[{p['id']}] ({p['title']}) {p['text']}" for p in new_passages]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    trace["rechecks"] = [r for r in trace["rechecks"] if r["eventId"] not in {t["eventId"] for t in tasks}] + tasks
    TRACE.write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "state/event-recheck-sheet.md").write_text("\n\n".join(sheet), encoding="utf-8")
    return tasks


def apply(response_path: Path, root: Path = ROOT, run_import: bool = True) -> list[dict]:
    """Merge re-checked gates into the Claude review, import with citation checks, record before/after."""
    updates = load(response_path, {"rechecks": []})["rechecks"]
    trace = load(TRACE, {"rechecks": []})
    by_event = {r["eventId"]: r for r in trace["rechecks"]}
    review_path = root / "state/serenity-claude-response.json"
    reviews = load(review_path, {"reviews": []})
    verdict_path = root / "state/serenity-claude-verdicts.json"
    verdicts = load(verdict_path, {"companies": []})
    for update in updates:
        task = by_event[update["eventId"]]
        review = next(r for r in reviews["reviews"] if r["ticker"] == task["ticker"])
        review["gates"].update(update["gates"])
        review["inputHash"] = task["inputHash"]
        if update.get("tierAfter"):
            for v in verdicts["companies"]:
                if v["ticker"] == task["ticker"]:
                    v["tier"] = update["tierAfter"]
        current_tier = next((v.get("tier") for v in verdicts["companies"] if v["ticker"] == task["ticker"]), None)
        task.update({"reviewerNote": update.get("note", ""), "tierAfter": update.get("tierAfter") or current_tier or task.get("tierBefore")})
    review_path.write_text(json.dumps(reviews, ensure_ascii=False, indent=2), encoding="utf-8")
    verdict_path.write_text(json.dumps(verdicts, ensure_ascii=False, indent=2), encoding="utf-8")
    if run_import:
        subprocess.run([str(root / "scripts/finalize_codex_serenity.sh"), "state/serenity-claude-response.json"], cwd=root,
                       check=True, capture_output=True)
    assessments = {a["ticker"]: a for a in load(root / "state/serenity-auto-assessments.json", {}).get("companies", [])}
    for update in updates:
        task = by_event[update["eventId"]]
        current = assessments.get(task["ticker"], {})
        reviews_now = current.get("gate_reviews", {})
        task["after"] = {gate: current.get(gate, "unknown") for gate in task["gatesReopened"]}
        task["citationChecks"] = {gate: reviews_now.get(gate, {}).get("citationChecks", "—") for gate in task["gatesReopened"]}
        task["quotes"] = {gate: [q["quote"] for side in ("support", "counter") for q in reviews_now.get(gate, {}).get(side, [])
                                 if q["id"] in task["newPassages"]] for gate in task["gatesReopened"]}
        task["changed"] = {g: [task["before"][g], task["after"][g]] for g in task["gatesReopened"] if task["before"][g] != task["after"][g]}
        task["status"] = "re-checked"
        task["recheckedAt"] = now()
    TRACE.write_text(json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
    return [by_event[u["eventId"]] for u in updates]


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-check Serenity gates reopened by primary-source events")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("tickers", nargs="*")
    a = sub.add_parser("apply")
    a.add_argument("--response", default=str(ROOT / "state/event-recheck-response.json"))
    args = parser.parse_args()
    if args.command == "prepare":
        tasks = prepare(tickers=set(args.tickers) or None)
        print(json.dumps([{k: t[k] for k in ("eventId", "ticker", "before", "newPassages", "sourceErrors")} for t in tasks], ensure_ascii=False, indent=1))
    else:
        done = apply(Path(args.response))
        print(json.dumps([{k: t.get(k) for k in ("eventId", "ticker", "before", "after", "changed", "citationChecks")} for t in done], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
