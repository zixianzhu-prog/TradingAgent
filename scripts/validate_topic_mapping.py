"""Validate the SEC topic -> company mapping: recall, precision and relation.

The mapping (topic_exposure.py) marks a company as exposed to a topic when its filings
match the topic's phrase pairs. That can be wrong in two directions:

  recall     companies that clearly do the work but never use the exact phrases
             (ground truth: listed makers of FDA AI-enabled devices, by review panel);
  precision  companies that match the phrases without doing the work (a competitor
             mentioned in a risk factor, a glossary line, two unrelated mentions far apart).

For every mapped company this script opens the filing, finds the closest place where
the topic's phrases occur together, and classifies the passage:

  own-product   first-person product language ("our ... platform", "we have developed")
  competition   competitor / risk-factor language
  supplier      the company supplies the topic's players
  customer      the company buys or uses the topic's products
  glossary      a definition line
  unrelated     phrases more than FAR_APART characters apart
  not-in-filing the phrases are not both in the opened filing (checked separately)

Writes state/topic-mapping-validation.json and outputs/topic-mapping-validation.md.
Needs SEC_USER_AGENT to download filings (cached under state/serenity-source-cache).
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import urllib.parse

import beneficiary_mapper as mapper
import prepare_claude_review as claude
from ai_medicine_topics import TOPICS

ROOT = Path(__file__).resolve().parents[1]
FAR_APART = 1500
PANEL_FOR_TOPIC = {"imaging": "Radiology", "cardiac": "Cardiovascular", "neuro": "Neurology", "pathology": "Pathology"}
MIN_DEVICES = 2  # a maker with one device on a panel is weak ground truth
RELATION_RULES = [
    ("glossary", r"[“\"]\w[^”\"]{0,30}[”\"]\s+means\b|\bmeans\s+artificial intelligence"),
    ("competition", r"\bcompet(?:itor|itors|ition|itive threats?|e)\b|could (?:materially )?adversely affect|may be unable to compete|other companies|third parties (?:may|could)|failure to develop or acquire"),
    ("supplier", r"\bwe (?:supply|sell|provide|license) (?:to|our)\b|\bour customers (?:include|use)\b|\boriginal equipment manufacturer|\bsole[- ]source supplier\b"),
    ("customer", r"\bwe (?:use|utilize|rely on|purchase|license from)\b|\bthird[- ]party (?:software|tools|models)\b|\bwe invested in\b"),
    ("own-product", r"\bour (?:proprietary |novel |first |flagship |ai[- ]powered |ai[- ]driven |ai[- ]enabled |commercial )?(?:platform|product|products|system|software|algorithm|algorithms|device|solution|solutions|technology|pipeline|engine|portfolio|offerings)\b"
                    r"|\bwe (?:have )?(?:developed|develop|offer|commercialize|market|designed|built|provide|acquired)\b"
                    r"|\b(?:the company|we) (?:is|are) an? (?:[\w-]+ )*?company\b|\bthe company (?:provides|develops|offers|markets|has developed|leverag\w+)\b"
                    r"|\bour (?:ai|artificial intelligence|machine learning|deep learning|r&d team)\b|\bby leveraging our\b|\bacquisition (?:of|allows)\b"),
]
WINDOW = 500


def phrase_words(phrase: str) -> list[str]:
    return [w for w in re.sub(r'"', "", phrase).split() if w]


def nearest_passage(text: str, phrases: list[str]) -> tuple[int, str]:
    """Smallest span containing every word of one phrase pair; returns (span length, passage)."""
    best_len, best_pos = None, -1
    for phrase in phrases:
        words = phrase_words(phrase)
        positions = [[m.start() for m in re.finditer(re.escape(w), text, re.I)] for w in words]
        if any(not p for p in positions):
            continue
        for start in positions[0]:
            span_end = start
            ok = True
            for others in positions[1:]:
                after = [p for p in others if p >= start - 200]
                if not after:
                    ok = False
                    break
                span_end = max(span_end, after[0])
            if ok and (best_len is None or span_end - start < best_len):
                best_len, best_pos = span_end - start, start
    if best_pos < 0:
        return -1, ""
    passage = re.sub(r"\s+", " ", text[max(0, best_pos - WINDOW): best_pos + best_len + WINDOW])
    return best_len, passage


AI_TERM = re.compile(r"artificial intelligence|machine learning|deep learning|\bAI\b|neural network|foundation model", re.I)
AI_WORDS = {"artificial", "intelligence", "machine", "learning", "deep", "ai", "algorithm", "neural", "generative"}


def filing_terms(topic: dict) -> re.Pattern | None:
    """Non-AI words from the topic's own SEC search phrases (e.g. "drug discovery", "radiology").

    The news regexes contain greedy patterns such as "drug discovery .*(ai|machine learning)",
    which match once across a whole 10-K and made every drug-discovery filer look topic-absent.
    """
    terms = []
    for phrase in topic.get("filings", []):
        for part in re.findall(r'"([^"]+)"', phrase):
            if not set(part.lower().split()) <= AI_WORDS:
                terms.append(re.escape(part))
    return re.compile(r"\b(?:" + "|".join(sorted(set(terms), key=len, reverse=True)) + r")", re.I) if terms else None


TOPIC_ARTICLE = {t["key"]: (filing_terms(t) or re.compile(t["article"], re.I)) for t in TOPICS}
LOCAL = 300
MIN_TOPIC_MENTIONS = 3


NEEDS_AI = {t["key"]: t.get("needs_ai", False) for t in TOPICS}
PHRASES = {t["key"]: t.get("filings", []) for t in TOPICS}


def classify_filing(text: str, topic: str, terms: re.Pattern | None = None, uses_ai: bool | None = None) -> dict:
    """Relation from the whole filing: how the company talks about AI, and how much it talks about the topic.

    A diversified company (GE HealthCare, Medtronic) describes its AI products in one section and
    radiology hundreds of times elsewhere, so a single nearest-span rule calls it unrelated. Instead:
    label every AI mention by its surrounding sentence, and count topic keywords across the filing.
    """
    labels: dict[str, int] = {}
    example = ""
    # AI topics: judge every AI mention. Other topics (robotics, sequencing...): judge the topic's own keywords.
    # `terms` / `uses_ai` let a caller classify an ad-hoc topic that is not in TOPICS (live demo).
    topic_terms = terms or TOPIC_ARTICLE.get(topic)
    if uses_ai is None:
        uses_ai = NEEDS_AI.get(topic, True) or any(AI_TERM.search(p) for p in PHRASES.get(topic, []))
    anchor = AI_TERM if uses_ai else (topic_terms or AI_TERM)
    for m in anchor.finditer(text):
        window = text[max(0, m.start() - LOCAL): m.end() + LOCAL]
        label = "mention"
        for name, pattern in RELATION_RULES:
            if re.search(pattern, window, re.I):
                label = name
                break
        labels[label] = labels.get(label, 0) + 1
        if label == "own-product" and not example:
            example = re.sub(r"\s+", " ", window)
    topic_mentions = len(topic_terms.findall(text)) if topic_terms else 0
    own, comp = labels.get("own-product", 0), labels.get("competition", 0)
    if not labels:
        relation = "not-in-filing"
    elif topic_mentions < MIN_TOPIC_MENTIONS:
        relation = "topic-absent"
    elif own >= 2 or (own and own >= comp):  # large filers name many competitors in risk factors
        relation = "own-product"
    elif labels.get("supplier") or labels.get("customer"):
        relation = "supplier" if labels.get("supplier", 0) >= labels.get("customer", 0) else "customer"
    elif comp:
        relation = "competition"
    elif set(labels) <= {"glossary"}:
        relation = "glossary"
    else:
        relation = "mention"
    return {"relation": relation, "aiMentions": sum(labels.values()), "aiLabels": labels, "topicMentions": topic_mentions, "example": example[:900]}


def classify(passage: str, span: int) -> str:
    if span < 0:
        return "not-in-filing"
    if span > FAR_APART:
        return "unrelated"
    lowered = passage.lower()
    for label, pattern in RELATION_RULES:
        if re.search(pattern, lowered, re.I):
            return label
    return "mention"


def recall(topic: str, mapped: set[str], truth_by_panel: dict) -> dict | None:
    panel = PANEL_FOR_TOPIC.get(topic)
    if not panel:
        return None
    truth = {t for t, devices in truth_by_panel.get(panel, {}).items() if len(devices) >= MIN_DEVICES}
    if not truth:
        return None
    hit = truth & mapped
    return {"panel": panel, "truth": sorted(truth), "found": sorted(hit), "missed": sorted(truth - hit), "recall": round(len(hit) / len(truth), 2)}


def cik_table(root: Path) -> dict[str, str]:
    path = root / "state/sec-company-tickers.json"
    if not path.exists():
        return {}
    return {r["ticker"]: str(r["cik_str"]) for r in json.loads(path.read_text(encoding="utf-8")).values()}


def matching_filing(cik: str, phrases: list[str], window: dict, fetch=mapper.http_json) -> str | None:
    """The filing EFTS actually matched for this company, when the recorded (latest) filing lacks the phrases."""
    for phrase in phrases:
        params = urllib.parse.urlencode({"q": phrase, "ciks": f"{int(cik):010d}", "dateRange": "custom",
                                         "startdt": window["start"], "enddt": window["end"], "forms": "10-K,10-Q,20-F,8-K"})
        hits = fetch(f"{mapper.EFTS}?{params}", mapper.DEFAULT_AGENT).get("hits", {}).get("hits", [])
        main = [h for h in hits if str(h["_source"].get("file_type", "")).upper() == h["_source"].get("form", "")]
        if main:
            return mapper.filing_url(cik, main[0]["_id"])
    return None


def validate(topics: list[str], root: Path = ROOT, allow_fetch: bool = True) -> dict:
    exposure_file = json.loads((root / "state/topic-exposure.json").read_text(encoding="utf-8"))
    exposure, window = exposure_file["topics"], exposure_file["window"]
    ciks = cik_table(root)
    truth_path = root / "state/fda-ai-listed-by-panel.json"
    truth = json.loads(truth_path.read_text(encoding="utf-8")) if truth_path.exists() else {}
    phrases = {t["key"]: t["filings"] for t in TOPICS}
    result = {"generatedAt": datetime.now(timezone.utc).isoformat(), "farApart": FAR_APART, "topics": {}}
    for topic in topics:
        companies = exposure[topic]["companies"]
        rows = []
        for ticker, item in companies.items():
            try:
                text = claude.filing_text(item["url"], allow_fetch=allow_fetch) or ""
            except Exception as exc:
                text = ""
                item = {**item, "error": str(exc)[:80]}
            span, passage = nearest_passage(text, phrases[topic]) if text else (-1, "")
            if span < 0 and allow_fetch and ticker in ciks:
                other = matching_filing(ciks[ticker], phrases[topic], window)
                if other and other != item["url"]:
                    try:
                        text = claude.filing_text(other, allow_fetch=True) or ""
                        span, passage = nearest_passage(text, phrases[topic]) if text else (-1, "")
                        item = {**item, "url": other}
                    except Exception as exc:
                        item = {**item, "error": str(exc)[:80]}
            filing_view = classify_filing(text, topic) if text else {"relation": "not-in-filing", "aiMentions": 0, "aiLabels": {}, "topicMentions": 0, "example": ""}
            rows.append({"ticker": ticker, "company": item["company"], "filings": item["filings"], "url": item["url"],
                         "span": span, "spanRelation": classify(passage, span), "passage": passage[:900],
                         **filing_view, "error": item.get("error")})
        counts = {}
        for r in rows:
            counts[r["relation"]] = counts.get(r["relation"], 0) + 1
        core = {"own-product", "supplier", "customer"}
        result["topics"][topic] = {
            "label": exposure[topic]["label"], "mapped": len(rows), "relations": counts,
            "precisionProxy": round(sum(1 for r in rows if r["relation"] in core) / len(rows), 2) if rows else None,
            "recall": recall(topic, set(companies), truth), "companies": rows,
        }
    return result


def report(result: dict) -> str:
    lines = ["# SEC 主题映射验证", "", f"生成时间：{result['generatedAt']}", "",
             "> 召回率：FDA AI 器械清单上、同一评审科室有 ≥2 个器械的上市公司，被主题映射找到的比例。",
             "> 精确率（代理）：映射到的公司中，整份文件判定为自有产品/供应商/客户关系的比例。每处 AI 提及按前后 300 字判断语境，主题关键词在全文出现不足 3 次的算\"主题词几乎不出现\"；竞争对手提及、术语表、主题词几乎不出现算误报。", "",
             "| 主题 | 映射公司数 | 召回率 | 漏掉 | 精确率（代理） | 自有产品 | 供应商/客户 | 竞争提及 | 术语表 | 主题词几乎不出现 | 文件中未找到 | 其他提及 |",
             "| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for key, t in result["topics"].items():
        c = t["relations"]
        rc = t["recall"]
        recall_cell = f"{rc['recall']:.0%}" if rc else "—"
        missed_cell = ", ".join(rc["missed"]) if rc else "—"
        precision_cell = f"{t['precisionProxy']:.0%}" if t["precisionProxy"] is not None else "—"
        lines.append(f"| {t['label']} | {t['mapped']} | {recall_cell} | {missed_cell} | {precision_cell} | {c.get('own-product', 0)} | "
                     f"{c.get('supplier', 0) + c.get('customer', 0)} | {c.get('competition', 0)} | {c.get('glossary', 0)} | {c.get('topic-absent', 0)} | {c.get('not-in-filing', 0)} | {c.get('mention', 0)} |")
    lines += ["", "## 判定为误报的例子（每主题最多 5 个）", ""]
    for key, t in result["topics"].items():
        bad = [r for r in t["companies"] if r["relation"] in {"competition", "glossary", "topic-absent"}][:5]
        for r in bad:
            lines.append(f"- **{t['label']} · {r['ticker']}** ({r['relation']}; AI 提及 {r['aiMentions']} 次，主题词 {r['topicMentions']} 次): {r['passage'][:220]}…")
    return "\n".join(lines) + "\n"


def compare(before: dict, after: dict) -> str:
    """Before/after table for the same topics (recall, precision proxy, mapped count)."""
    lines = ["", "## 升级前后对比", "",
             "| 主题 | 映射公司数 前→后 | 召回率 前→后 | 精确率（代理）前→后 | 升级后仍漏掉 |", "| --- | ---: | ---: | ---: | --- |"]
    pct = lambda v: f"{v:.0%}" if v is not None else "—"
    for key, a in after["topics"].items():
        b = before.get("topics", {}).get(key)
        if not b:
            continue
        rb, ra = (b.get("recall") or {}).get("recall"), (a.get("recall") or {}).get("recall")
        lines.append(f"| {a['label']} | {b['mapped']}→{a['mapped']} | {pct(rb)}→{pct(ra)} | {pct(b['precisionProxy'])}→{pct(a['precisionProxy'])} | "
                     f"{', '.join((a.get('recall') or {}).get('missed', [])) or '—'} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SEC topic-to-company mapping")
    parser.add_argument("--topics", nargs="*", default=list(PANEL_FOR_TOPIC))
    parser.add_argument("--cache-only", action="store_true")
    parser.add_argument("--compare", help="earlier validation JSON to show a before/after table")
    args = parser.parse_args()
    result = validate(args.topics, allow_fetch=not args.cache_only)
    (ROOT / "state/topic-mapping-validation.json").write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    text = report(result)
    if args.compare and Path(args.compare).exists():
        text += compare(json.loads(Path(args.compare).read_text(encoding="utf-8")), result)
    (ROOT / "outputs/topic-mapping-validation.md").write_text(text, encoding="utf-8")
    print(json.dumps({k: {"mapped": v["mapped"], "precisionProxy": v["precisionProxy"], "recall": (v["recall"] or {}).get("recall"), "relations": v["relations"]}
                      for k, v in result["topics"].items()}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
