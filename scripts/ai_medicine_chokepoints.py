"""Upstream bottleneck map for AI medicine: who do the beneficiaries depend on?

The chokepoint skill says: don't buy the obvious beneficiary, buy what the
beneficiary must depend on. Health companies disclose such dependence in their
risk factors ("we rely on a sole supplier", "single-source"). For each upstream
supplier this counts health operating companies whose filings in the last 15
months name the supplier together with sole/single-source language, and how many
of those are in the AI-medicine screen.

Limits: SEC full-text search has no proximity operator, so "Illumina" and "sole
supplier" may appear in different paragraphs of one filing. Counts are leads for
the supply-chain gate, not proof of dependence; each example links to the filing
so it can be checked. Two non-company bottlenecks are reported from data the agent
already has (FDA AI device clearances) or flagged as not yet tracked (reimbursement).
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import ai_medicine_universe_screen as screen_mod
import beneficiary_mapper as mapper

ROOT = Path(__file__).resolve().parents[1]
DEPENDENCE_PHRASES = ('"sole supplier"', '"single source"', '"sole source"', '"single supplier"')
# layer, supplier as written in filings, US ticker (None = no US listing / private)
SUPPLIERS = [
    ("Sequencing instruments", "Illumina", "ILMN"),
    ("Sequencing instruments", "Pacific Biosciences", "PACB"),
    ("Sequencing instruments", "Oxford Nanopore", None),
    ("Sequencing instruments", "Element Biosciences", None),
    ("Lab instruments & reagents", "Thermo Fisher", "TMO"),
    ("Lab instruments & reagents", "Roche", None),
    ("Lab instruments & reagents", "Agilent", "A"),
    ("Lab instruments & reagents", "Bio-Rad", "BIO"),
    ("Lab instruments & reagents", "QIAGEN", "QGEN"),
    ("Imaging hardware", "Siemens Healthineers", None),
    ("Imaging hardware", "GE HealthCare", "GEHC"),
    ("Imaging hardware", "Philips", "PHG"),
    ("Compute & cloud", "NVIDIA", "NVDA"),
    ("Compute & cloud", "Amazon Web Services", "AMZN"),
    ("Compute & cloud", "Microsoft Azure", "MSFT"),
    ("Compute & cloud", "Google Cloud", "GOOGL"),
    ("Clinical data & EHR", "Epic Systems", None),
    ("Clinical data & EHR", "Oracle Health", "ORCL"),
    ("Contract manufacturing", "Lonza", None),
    ("Contract manufacturing", "Samsung Biologics", None),
    ("Contract manufacturing", "WuXi", None),
]


def mention_total(supplier: str, start: date, end: date, fetch=mapper.http_json) -> int:
    """How many filings name the supplier at all (one request; only the total is read)."""
    import urllib.parse
    params = urllib.parse.urlencode({"q": f'"{supplier}"', "dateRange": "custom", "startdt": start.isoformat(), "enddt": end.isoformat(), "forms": screen_mod.FORMS})
    return int(fetch(f"{mapper.EFTS}?{params}", mapper.DEFAULT_AGENT).get("hits", {}).get("total", {}).get("value", 0))


def scan_supplier(supplier: str, start: date, end: date, fetch=mapper.http_json) -> tuple[dict[str, dict], int]:
    """Health operating companies whose filings name the supplier next to dependence language."""
    found: dict[str, dict] = {}
    filings: set[str] = set()
    for phrase in DEPENDENCE_PHRASES:
        hits = screen_mod.search_all(f'"{supplier}" {phrase}', start, end, max_hits=300, fetch=fetch)
        filings |= {h.get("_source", {}).get("adsh") or h.get("_id", "").split(":")[0] for h in hits}
        for key, row in mapper.aggregate(hits).items():
            if not screen_mod.is_operating(row) or row["sicGroup"] == "Other sector":
                continue
            if screen_mod.core_tokens(supplier)[:1] == screen_mod.core_tokens(row["name"])[:1]:
                continue  # the supplier's own filings
            entry = found.setdefault(row["ticker"], {"ticker": row["ticker"], "company": row["name"], "sicGroup": row["sicGroup"], "phrases": set(), "filing": None})
            entry["phrases"].add(phrase.strip('"'))
            latest = max(row["filings"].values(), key=lambda f: f["filed"] or "")
            if entry["filing"] is None or (latest["filed"] or "") > (entry["filing"]["filed"] or ""):
                entry["filing"] = {"form": latest["form"], "filed": latest["filed"], "url": latest["url"]}
    return found, len(filings)


def build(as_of: date, screen: dict, fda: dict, fetch=mapper.http_json) -> dict:
    start = as_of - timedelta(days=455)
    ai_universe = {r["ticker"] for r in screen.get("companies", [])}  # companies that describe AI as their own product
    nodes = []
    for layer, supplier, ticker in SUPPLIERS:
        try:
            dependents, dependence_filings = scan_supplier(supplier, start, as_of, fetch=fetch)
            mentions = mention_total(supplier, start, as_of, fetch=fetch)
            status = "ok"
        except Exception as exc:
            dependents, dependence_filings, mentions, status = {}, 0, 0, f"error: {str(exc)[:120]}"
        rows = sorted(dependents.values(), key=lambda r: (r["ticker"] not in ai_universe, -len(r["phrases"]), r["ticker"]))
        nodes.append({
            "layer": layer, "supplier": supplier, "ticker": ticker, "status": status,
            "healthDependents": len(rows), "aiMedicineDependents": sum(1 for r in rows if r["ticker"] in ai_universe),
            # Share of all filings naming the supplier that also carry sole/single-source language. Ubiquitous
            # names (partners, competitors) score low; a genuine bottleneck should score high.
            "mentionFilings": mentions, "dependenceShare": round(dependence_filings / mentions, 3) if mentions else None,
            "examples": [{**r, "phrases": sorted(r["phrases"]), "inAiUniverse": r["ticker"] in ai_universe} for r in rows[:8]],
        })
    nodes.sort(key=lambda n: (-n["aiMedicineDependents"], -n["healthDependents"]))
    devices = fda.get("devices", [])
    panels = Counter(d.get("panel") for d in devices)
    return {
        "asOf": as_of.isoformat(), "window": {"start": start.isoformat(), "end": as_of.isoformat()},
        "method": "SEC full-text search: supplier name + sole/single-source language in health operating companies' filings. Co-mention leads, not proven dependence.",
        "nodes": nodes,
        "nonCompanyBottlenecks": [
            {"name": "FDA clearance", "evidence": f"{len(devices):,} AI-enabled device authorizations on FDA's list; {panels.most_common(1)[0][0] if panels else '—'} accounts for "
                                                  f"{(panels.most_common(1)[0][1] / max(1, len(devices))):.0%}." if devices else "FDA list not loaded",
             "status": "tracked"},
            {"name": "Reimbursement (CMS CPT / NTAP codes)", "evidence": "Not tracked yet. Payment codes decide whether an AI product earns revenue; next data source to add.",
             "status": "not tracked"},
        ],
    }


def write_markdown(payload: dict, path: Path) -> None:
    lines = ["# AI 医疗上游瓶颈图", "",
             f"截至 {payload['asOf']}。卡位理论：不买显而易见的受益者，买受益者必须依赖的环节。", "",
             "> 方法：在医疗行业运营公司近 15 个月的 SEC 文件中，检索“供应商名称 + sole supplier / single source”同时出现的文件。"
             "SEC 检索没有邻近搜索，两个词可能出现在不同段落，所以这是线索而不是确证；每个例子都附文件链接以便核对。"
             "“依赖措辞占比”= 提到该供应商的全部文件中，同时带有唯一供应商措辞的比例；无处不在的合作方或竞争对手占比低，真正的瓶颈占比应偏高。", "",
             "| 环节 | 供应商 | 美股代码 | 披露依赖的医疗公司 | 其中 AI 医疗公司 | 依赖措辞占比 | 例子 |", "| --- | --- | --- | ---: | ---: | ---: | --- |"]
    for n in payload["nodes"]:
        ex = ", ".join(f"[{e['ticker']}]({e['filing']['url']})" for e in n["examples"][:5] if e.get("filing"))
        share = f"{n['dependenceShare']:.0%}" if n.get("dependenceShare") is not None else "—"
        lines.append(f"| {n['layer']} | {n['supplier']} | {n['ticker'] or '无美股/未上市'} | {n['healthDependents']} | {n['aiMedicineDependents']} | {share} | {ex} |")
    lines += ["", "## 非公司类瓶颈", ""]
    lines += [f"- **{b['name']}**：{b['evidence']}" for b in payload["nonCompanyBottlenecks"]]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Map upstream bottlenecks that AI-medicine companies depend on")
    parser.add_argument("--as-of")
    parser.add_argument("--screen", default=str(ROOT / "state/ai-medicine-universe-screen.json"))
    parser.add_argument("--fda", default=str(ROOT / "state/fda-ai-devices.json"))
    parser.add_argument("--json-output", default=str(ROOT / "state/ai-medicine-chokepoints.json"))
    parser.add_argument("--markdown-output", default=str(ROOT / "outputs/ai-medicine-chokepoints.md"))
    args = parser.parse_args()
    as_of = date.fromisoformat(args.as_of) if args.as_of else datetime.now(timezone.utc).date()
    load = lambda p: json.loads(Path(p).read_text(encoding="utf-8")) if Path(p).exists() else {}
    payload = build(as_of, load(args.screen), load(args.fda))
    payload["generatedAt"] = datetime.now(timezone.utc).isoformat()
    Path(args.json_output).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    write_markdown(payload, Path(args.markdown_output))
    print(json.dumps([(n["supplier"], n["healthDependents"], n["aiMedicineDependents"]) for n in payload["nodes"]]))


if __name__ == "__main__":
    main()
