"""Build an auditable paper -> people -> institution/funder -> company-candidate graph.

This is a discovery layer, not an investment scorer. OpenAlex supplies structured
authorship, institution, funder and grant metadata; PubMed is an independent medical
literature entry point. A technology-overlap company link is only a research candidate.
It cannot support a Serenity pass unless a later primary filing, customer disclosure,
clinical record or earnings report verifies the commercial relationship.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import ssl
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "trend-agent/frontier-science-watchlist.json"
DEFAULT_COMPANIES = ROOT / "trend-agent/theme-company-map.json"
DEFAULT_STATE = ROOT / "state/scientific-frontier.json"
DEFAULT_REPORT = ROOT / "outputs/scientific-frontier.md"
OPENALEX = "https://api.openalex.org/works"
PUBMED_SEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
PUBMED_SUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

STOP = {
    "artificial", "intelligence", "machine", "learning", "clinical", "medical", "medicine",
    "health", "platform", "technology", "using", "based", "enabled", "system", "data",
    "and", "for", "with", "across", "other", "rather", "than", "candidate", "challenger",
    "watchlist", "embedded", "workflow", "workflows", "products", "base", "direct", "sponsor",
}


def fetch_json(url: str, data: bytes | None = None, timeout: int = 40) -> dict:
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "SerenityFrontierResearch/0.1"})
    # The project venv may not inherit macOS's CA path. Use the system bundle when
    # present; never disable TLS verification.
    system_ca = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(system_ca) if system_ca.exists() else None)
    with urllib.request.urlopen(req, timeout=timeout, context=context) as response:
        return json.loads(response.read().decode("utf-8"))


def abstract_text(inverted: dict | None) -> str:
    if not inverted:
        return ""
    positions = [(pos, word) for word, values in inverted.items() for pos in values]
    return " ".join(word for _, word in sorted(positions))


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z0-9-]{2,}", (text or "").lower()) if w not in STOP}


# Phrases every AI-medicine paper uses; matching on them linked NVIDIA to an envenomation review.
GENERIC_PHRASES = {"drug discovery", "medical imaging", "clinical data", "precision medicine", "drug development",
                   "healthcare workflows", "clinical workflows", "ai-enabled", "ai-native", "ai-supported"}


FILLER = {"the", "was", "were", "are", "used", "use", "via", "from", "into", "this", "that", "these", "its", "has", "have"}


def phrases(text: str) -> set[str]:
    """Hyphenated terms and adjacent word pairs: the specific vocabulary a company link must share."""
    out = set()
    for clause in re.split(r"[^a-z0-9\s-]", (text or "").lower()):
        raw = clause.split()
        ok = [len(w) >= 3 and w[0].isalpha() and w not in STOP and w not in FILLER for w in raw]
        out |= {w for w, good in zip(raw, ok) if good and "-" in w}
        # Pairs only of truly adjacent words, so "used in imaging" never becomes "used imaging".
        out |= {f"{a} {b}" for a, b, ga, gb in zip(raw, raw[1:], ok, ok[1:]) if ga and gb}
    return out - GENERIC_PHRASES


def company_catalog(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for item in payload.get("themes", {}).get("ai_medicine", []):
        company = item.get("company", "")
        aliases = {company.lower(), item.get("ticker", "").lower()}
        aliases |= {x.strip() for x in re.split(r"[/()]", company.lower()) if len(x.strip()) >= 4}
        exposure = " ".join([item.get("exposure", ""), item.get("serenity_role", "")])
        rows.append({"ticker": item.get("ticker"), "company": company, "aliases": sorted(aliases),
                     "exposure": exposure, "tokens": tokens(exposure), "phrases": phrases(exposure)})
    return rows


def direct_company_links(text: str, affiliations: list[str], companies: list[dict]) -> list[dict]:
    low, aff = text.lower(), " ".join(affiliations).lower()
    out = []
    for company in companies:
        # Tickers must be full tokens: NTRA must not match "central" and TEM must
        # not match "system". The same boundary rule keeps company aliases honest.
        matched = [a for a in company["aliases"] if len(a) >= 4 and
                   (re.search(rf"(?<![a-z0-9]){re.escape(a)}(?![a-z0-9])", low) or
                    re.search(rf"(?<![a-z0-9]){re.escape(a)}(?![a-z0-9])", aff))]
        if matched:
            out.append({"ticker": company["ticker"], "company": company["company"], "relation": "direct_mention",
                        "evidence": sorted(set(matched))})
    return out


def candidate_company_links(text: str, companies: list[dict], direct: set[str]) -> list[dict]:
    doc, doc_phrases = tokens(text), phrases(text)
    out = []
    for company in companies:
        if company["ticker"] in direct:
            continue
        # One shared specific phrase (e.g. "cell-free dna", "antibody discovery") plus shared words;
        # single generic words like "model" or "drug" alone are not a technology overlap.
        shared = sorted(doc_phrases & company.get("phrases", phrases(company.get("exposure", ""))))
        overlap = sorted(doc & company["tokens"])
        if shared and len(overlap) >= 3:
            out.append({"ticker": company["ticker"], "company": company["company"], "relation": "technology_overlap_candidate",
                        "evidence": (shared + [w for w in overlap if not any(w in x for x in shared)])[:8]})
    return sorted(out, key=lambda row: (-len(row["evidence"]), row["ticker"]))[:3]


def openalex_works(theme: dict, start: date, end: date, limit: int, fetch=fetch_json) -> list[dict]:
    fields = "id,doi,display_name,publication_date,type,cited_by_count,authorships,topics,keywords,awards,funders,primary_location,abstract_inverted_index,is_retracted"
    query = urllib.parse.urlencode({
        "search": theme["query"],
        "filter": f"from_publication_date:{start.isoformat()},to_publication_date:{end.isoformat()}",
        "sort": "publication_date:desc",
        "per-page": limit,
        "select": fields,
    })
    return fetch(f"{OPENALEX}?{query}").get("results", [])


def pubmed_records(theme: dict, start: date, end: date, limit: int, fetch=fetch_json) -> list[dict]:
    term = f'({theme["query"]}) AND ({start.isoformat()}:{end.isoformat()}[pdat])'
    search = urllib.parse.urlencode({"db": "pubmed", "term": term, "retmode": "json", "retmax": limit, "sort": "pub date"})
    ids = fetch(f"{PUBMED_SEARCH}?{search}").get("esearchresult", {}).get("idlist", [])
    if not ids:
        return []
    summary = urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
    payload = fetch(f"{PUBMED_SUMMARY}?{summary}").get("result", {})
    return [payload[i] for i in ids if i in payload]


def normalize_openalex(raw: dict, theme: dict, target_institutions: list[str], companies: list[dict]) -> dict:
    authors, institutions, affiliations = [], {}, []
    for authorship in raw.get("authorships") or []:
        author = authorship.get("author") or {}
        author_institutions = []
        for inst in authorship.get("institutions") or []:
            if inst.get("id"):
                normalized_inst = {"id": inst["id"], "name": inst.get("display_name"), "ror": inst.get("ror"),
                                   "country": inst.get("country_code"), "type": inst.get("type")}
                institutions[inst["id"]] = normalized_inst
                author_institutions.append(normalized_inst)
        if author.get("id"):
            authors.append({"id": author["id"], "name": author.get("display_name"), "orcid": author.get("orcid"),
                            "institutions": author_institutions})
        affiliations += authorship.get("raw_affiliation_strings") or []
    abstract = abstract_text(raw.get("abstract_inverted_index"))
    # Company similarity must come from the work itself. Appending the configured
    # theme keywords here would make every paper appear related to every company.
    text = " ".join([raw.get("display_name") or "", abstract])
    direct = direct_company_links(text, affiliations, companies)
    links = direct + candidate_company_links(text, companies, {x["ticker"] for x in direct})
    relevance = sorted(tokens(text) & tokens(" ".join(theme.get("keywords", []))))
    target_hits = sorted({inst["name"] for inst in institutions.values() if inst.get("name") and
                          any(t.lower() in inst["name"].lower() for t in target_institutions)})
    grants = raw.get("awards") or []
    score = 15 + min(15, int(math.log1p(raw.get("cited_by_count") or 0) * 4))
    score += min(15, len(institutions) * 3) + min(10, len(grants) * 3) + min(20, len(target_hits) * 10)
    score += 15 if any(x["relation"] == "direct_mention" for x in links) else (5 if links else 0)
    if raw.get("is_retracted"):
        score = 0
    source = ((raw.get("primary_location") or {}).get("source") or {}).get("display_name")
    return {
        "id": raw.get("id"), "doi": raw.get("doi"), "title": raw.get("display_name"),
        "publishedAt": raw.get("publication_date"), "publicationType": raw.get("type"), "source": source,
        "citedBy": raw.get("cited_by_count") or 0, "retracted": bool(raw.get("is_retracted")),
        "theme": theme["id"], "themeLabel": theme["label"], "authors": authors, "institutions": list(institutions.values()),
        "targetInstitutionHits": target_hits, "funders": grants, "companyLinks": links,
        "themeRelevance": relevance, "researchPriority": min(100, score), "abstractAvailable": bool(abstract), "provenance": "openalex",
    }


def merge_previous(current: list[dict], previous: dict, cutoff: date) -> list[dict]:
    merged = {row.get("id"): row for row in previous.get("works", []) if row.get("id") and
              (not row.get("publishedAt") or row["publishedAt"] >= cutoff.isoformat())}
    merged.update({row["id"]: row for row in current if row.get("id")})
    return sorted(merged.values(), key=lambda row: (row.get("publishedAt") or "", row.get("researchPriority") or 0), reverse=True)


def relationship_graph(works: list[dict]) -> dict:
    """Materialize the discovery relationships without upgrading candidates to evidence."""
    nodes: dict[str, dict] = {}
    edges: dict[tuple[str, str, str], dict] = {}

    def add_node(node_id: str, kind: str, label: str | None, **extra) -> None:
        if node_id:
            nodes[node_id] = {"id": node_id, "kind": kind, "label": label or node_id, **extra}

    def add_edge(source: str, target: str, relation: str, **extra) -> None:
        if source and target:
            edges[(source, target, relation)] = {
                "source": source, "target": target, "relation": relation, **extra,
            }

    for work in works:
        work_id = work.get("id")
        if not work_id:
            continue
        theme_id = f"theme:{work.get('theme')}"
        add_node(theme_id, "theme", work.get("themeLabel"))
        add_node(work_id, "work", work.get("title"), publishedAt=work.get("publishedAt"), doi=work.get("doi"))
        add_edge(work_id, theme_id, "IN_THEME")
        for author in work.get("authors", []):
            author_id = author.get("id")
            add_node(author_id, "author", author.get("name"), orcid=author.get("orcid"))
            add_edge(work_id, author_id, "AUTHORED_BY")
            for institution in author.get("institutions", []):
                institution_id = institution.get("id")
                add_node(institution_id, "institution", institution.get("name"), ror=institution.get("ror"),
                         institutionType=institution.get("type"))
                add_edge(author_id, institution_id, "AFFILIATED_WITH")
        for institution in work.get("institutions", []):
            institution_id = institution.get("id")
            add_node(institution_id, "institution", institution.get("name"), ror=institution.get("ror"))
            add_edge(work_id, institution_id, "AFFILIATED_WITH")
        for grant in work.get("funders", []):
            funder_id = grant.get("funder") or grant.get("funder_id") or grant.get("id")
            if not funder_id:
                continue
            funder_name = grant.get("funder_display_name") or grant.get("display_name") or funder_id
            add_node(funder_id, "funder", funder_name)
            add_edge(work_id, funder_id, "FUNDED_BY", awardId=grant.get("funder_award_id") or grant.get("award_id"))
        for company in work.get("companyLinks", []):
            company_id = f"company:{company.get('ticker')}"
            add_node(company_id, "company_candidate", company.get("company"), ticker=company.get("ticker"))
            relation = "DIRECTLY_MENTIONS" if company.get("relation") == "direct_mention" else "TECHNOLOGY_OVERLAP_CANDIDATE"
            add_edge(work_id, company_id, relation, evidence=company.get("evidence", []),
                     commercialEvidence=False,
                     note="A paper mention creates a relationship to investigate, not proof of customers or revenue.")
    return {"nodes": list(nodes.values()), "edges": list(edges.values())}


def build(config: dict, companies: list[dict], previous: dict | None = None, fetch=fetch_json, today: date | None = None) -> dict:
    today = today or date.today()
    start = today - timedelta(days=int(config.get("lookback_days", 30)))
    errors, works, pubmed = [], [], []
    for theme in config.get("themes", []):
        try:
            normalized = [normalize_openalex(raw, theme, config.get("target_institutions", []), companies)
                          for raw in openalex_works(theme, start, today, int(config.get("per_query", 25)), fetch)]
            works += [row for row in normalized if len(row.get("themeRelevance", [])) >= 2]
        except Exception as exc:
            errors.append({"source": "OpenAlex", "theme": theme["id"], "error": f"{type(exc).__name__}: {str(exc)[:180]}"})
        try:
            for raw in pubmed_records(theme, start, today, min(20, int(config.get("per_query", 25))), fetch):
                pubmed.append({"pmid": raw.get("uid"), "title": raw.get("title"), "publishedAt": raw.get("pubdate"),
                               "authors": [a.get("name") for a in raw.get("authors", [])], "source": raw.get("fulljournalname"),
                               "theme": theme["id"], "provenance": "pubmed"})
        except Exception as exc:
            errors.append({"source": "PubMed", "theme": theme["id"], "error": f"{type(exc).__name__}: {str(exc)[:180]}"})
    compatible_previous = previous if (previous or {}).get("schemaVersion") == 3 else {}
    works = merge_previous(works, compatible_previous or {}, today - timedelta(days=int(config.get("history_days", 180))))
    direct = sum(any(x["relation"] == "direct_mention" for x in w.get("companyLinks", [])) for w in works)
    graph = relationship_graph(works)
    return {
        "schemaVersion": 3, "generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "asOf": today.isoformat(),
        "method": "Deterministic OpenAlex/PubMed discovery graph; technology-overlap links are candidates, not commercial evidence.",
        "summary": {"works": len(works), "pubmedRecords": len(pubmed), "directCompanyWorks": direct,
                    "targetInstitutionWorks": sum(bool(w.get("targetInstitutionHits")) for w in works), "errors": len(errors)},
        "works": works, "pubmed": pubmed, "graph": graph, "errors": errors,
    }


def report(payload: dict) -> str:
    s = payload["summary"]
    lines = ["# 前沿科研信号与公司候选", "",
             f"> 截至 {payload['asOf']}。OpenAlex 论文 {s['works']} 篇，PubMed 独立记录 {s['pubmedRecords']} 条；"
             f"目标研究机构相关 {s['targetInstitutionWorks']} 篇，直接公司提及 {s['directCompanyWorks']} 篇。", "",
             "> 论文和技术重合只产生研究候选，不证明公司拥有知识产权、客户、收入或供应链瓶颈；必须再经过 Serenity 原始证据审查。", "",
             "| 日期 | 方向 | 论文 | 机构 | 公司关系 | 优先级 |", "|---|---|---|---|---|---:|"]
    for w in sorted(payload.get("works", []), key=lambda x: (-x.get("researchPriority", 0), x.get("publishedAt") or ""))[:30]:
        institutions = ", ".join(x.get("name", "") for x in w.get("institutions", [])[:3]) or "—"
        links = ", ".join(f"{x['ticker']} ({'直接' if x['relation']=='direct_mention' else '候选'})" for x in w.get("companyLinks", [])) or "—"
        url = w.get("doi") or w.get("id") or ""
        title = (w.get("title") or "（无标题）").replace("|", "/")
        lines.append(f"| {w.get('publishedAt') or '—'} | {w.get('themeLabel')} | [{title}]({url}) | {institutions} | {links} | {w.get('researchPriority', 0)} |")
    if payload.get("errors"):
        lines += ["", "## 数据源警告", ""] + [f"- {e['source']} / {e['theme']}：{e['error']}" for e in payload["errors"]]
    lines += ["", "## 下一验证步骤", "",
              "1. 核对论文知识产权、作者与公司之间的真实关系。",
              "2. 查找专利、公司成立、融资和药企许可材料。",
              "3. 用临床、FDA、客户与财报证据验证能否形成商业瓶颈。",
              "4. 未完成上述步骤前，不进入估值或模拟订单。"]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    parser.add_argument("--companies", default=str(DEFAULT_COMPANIES))
    parser.add_argument("--state", default=str(DEFAULT_STATE))
    parser.add_argument("--report", default=str(DEFAULT_REPORT))
    args = parser.parse_args()
    state = Path(args.state)
    previous = json.loads(state.read_text(encoding="utf-8")) if state.exists() else {}
    payload = build(json.loads(Path(args.config).read_text(encoding="utf-8")), company_catalog(Path(args.companies)), previous)
    state.parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    state.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(args.report).write_text(report(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
