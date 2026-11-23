"""FDA complete response letters (CRLs): why an application was not approved, from FDA's own words.

Since July 2025 FDA publishes CRLs on openFDA. A rejection is not one thing: a failed
efficacy trial takes years to fix, a facility inspection takes months. This script reads every
published letter and classifies the reasons with a quote from the letter for each one, so
the classification can be checked word for word, the same rule as the Serenity citation gate.

Sources
- https://download.open.fda.gov/approved_CRLs.zip    letters for drugs later approved
- https://download.open.fda.gov/unapproved_CRLs.zip  letters for drugs still not approved
Cached under state/serenity-source-cache/crl/. Text extraction needs pypdf once; the extracted
text is cached in letters.json so later runs (and the daily pipeline) need no PDF library.

Categories (rule-based proxy, each with the first matching sentence as the citation):
  efficacy       substantial evidence of effectiveness not shown, endpoints, trial design
  safety         adverse events, deaths, benefit-risk, toxicity
  manufacturing  product quality, CGMP, facility inspections, stability, sterility
  pharmacology   clinical pharmacology, nonclinical, bioequivalence, carcinogenicity
  usability      human factors, device constituent, labeling deficiencies (not boilerplate)
Severity: heavy = efficacy or a new trial required; medium = safety or new pharmacology
studies; light = manufacturing, usability or data-format items only.

    python3 scripts/fda_crl_reasons.py            # download if missing, extract, classify
    python3 scripts/fda_crl_reasons.py --offline  # cached letters only
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.request
import zipfile
from collections import Counter
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "state/serenity-source-cache/crl"
LETTERS = CACHE / "letters.json"
OUTPUT = ROOT / "state/fda-crl-reasons.json"
REPORT = ROOT / "outputs/fda-crl-reasons.md"
# One record per letter with FDA's own sponsor name, letter date and OCR text. Preferred over the
# zip files, where one PDF can bundle several letters to the same application.
API_URL = "https://api.fda.gov/transparency/crl.json?limit=1000"
API_CACHE = CACHE / "api.json"
BUNDLES = {"approved": "https://download.open.fda.gov/approved_CRLs.zip",
           "unapproved": "https://download.open.fda.gov/unapproved_CRLs.zip"}

HEADING = re.compile(r"^\s*([A-Z][A-Z &/,\-()]{2,44})\s*$", re.M)
DEFICIENCY_SECTIONS = {
    "CLINICAL": "efficacy", "CLINICAL/STATISTICAL": "efficacy", "STATISTICAL": "efficacy",
    "NONCLINICAL": "pharmacology", "CLINICAL PHARMACOLOGY": "pharmacology", "BIOPHARMACEUTICS": "pharmacology",
    "PRODUCT QUALITY": "manufacturing", "FACILITY INSPECTIONS": "manufacturing", "MICROBIOLOGY": "manufacturing",
    "HUMAN FACTORS": "usability", "DEVICE": "usability", "LABELING": "usability",
}
BOILERPLATE = {"SAFETY UPDATE", "PRESCRIBING INFORMATION", "CARTON AND CONTAINER LABELING", "PROPRIETARY NAME",
               "MEDICATION GUIDE", "OTHER ACTION LETTERS", "OTHER", "ADDITIONAL COMMENTS", "COMPLETE RESPONSE",
               "CENTER FOR DRUG EVALUATION AND", "RESEARCH", "DEPARTMENT OF HEALTH AND HUMAN SERVICES", "REGULATORY"}
KEYWORDS = {
    "efficacy": re.compile(r"substantial evidence of (?:effectiveness|efficacy)|(?:primary|secondary|surrogate) endpoint|did not demonstrate|fail(?:ed|ure) to (?:demonstrate|show|meet)|adequate and well[- ]controlled|treatment effect|efficacy|effectiveness|historical control|single[- ]arm|clinical benefit", re.I),
    "safety": re.compile(r"\bsafety (?:concern|signal|database|data|finding|issue|risk)|adverse (?:event|reaction)|\bdeaths?\b|toxicit|benefit[- ]risk|risk[- ]benefit|hepatotoxic|cardiovascular risk|serious risk|unacceptable risk|REMS\b", re.I),
    "manufacturing": re.compile(r"\bCGMP\b|current good manufacturing|facilit(?:y|ies) (?:inspection|listed|named)|pre-approval inspection|manufactur(?:ing|e) (?:process|site|facility|deficienc)|product quality|drug (?:substance|product) (?:specification|manufactur|stability)|\bCMC\b|chemistry, manufacturing|\bstability (?:data|stud)|impurit|steril|container closure|batch|lot release|official action indicated|\bOAI\b", re.I),
    "pharmacology": re.compile(r"clinical pharmacology|nonclinical|non-clinical|bioequivalen|pharmacokinetic|carcinogenicity|toxicology|dose[- ]response|exposure[- ]response|immunogenicity|drug[- ]drug interaction", re.I),
    "usability": re.compile(r"human factors|use[- ]related risk|device constituent|delivery device|instructions for use|labeling deficienc", re.I),
}
NEW_TRIAL = re.compile(r"(?:additional|new|another|second)\s+(?:adequate and well[- ]controlled\s+)?(?:clinical\s+)?(?:trial|stud(?:y|ies))|conduct (?:an? )?(?:additional |new )?(?:adequate and well[- ]controlled )?(?:clinical )?(?:trial|study)", re.I)
RESUBMISSION_CLASS = re.compile(r"[Cc]lass\s*(1|2)\b")
INSPECTION_FAIL = re.compile(r"(?:conveyed|identified|cited|issued)\s+(?:\w+\s+){0,3}deficienc|not (?:yet )?(?:in|achieved|come into) compliance|official action indicated|\bOAI\b|withhold(?:ing)? recommendation", re.I)
COMPANY = re.compile(r"\n[ \t]*([A-Z][^\n]{1,90}?)[ \t]*\n[ \t]*(?:Attention|Attn|ATTN)[:\s]")
LETTER_DATE = re.compile(r"\b(January|February|March|April|May|June|July|August|September|October|November|December|JANUARY|FEBRUARY|MARCH|APRIL|MAY|JUNE|JULY|AUGUST|SEPTEMBER|OCTOBER|NOVEMBER|DECEMBER)\s+(\d{1,2}),\s*(\d{4})")
REDACTION = re.compile(r"\(b\)\s*\(4\)")
CLINICAL_SAFETY = re.compile(r"safety|adverse|\brisk|death|toxic|\bQT\b|tolerab|hepat|cardiac", re.I)
DRUGSFDA = "https://api.fda.gov/drug/drugsfda.json?search=application_number:%22{app}%22&limit=1"
DRUG = re.compile(r"(?:Application|BLA|NDA)[^.]{0,120}?\bfor\s+([A-Za-z][^,\n]{2,80}?)(?:,|\s+submitted|\s+\(|\.\s)", re.S)
SUFFIX = re.compile(r"\b(incorporated|inc|corporation|corp|company|co|ltd|limited|llc|plc|holdings?|group|pharmaceuticals?|pharma|therapeutics|biosciences|biotherapeutics|biopharma|biopharmaceuticals?|laboratories|labs|sa|ag|nv|bv|gmbh|lp|usa|us)\b\.?", re.I)


def normalize(name: str) -> str:
    s = re.sub(r"[^a-z0-9 ]", " ", name.lower())
    s = SUFFIX.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def download_bundles() -> None:
    import serenity_evidence_review as ser

    CACHE.mkdir(parents=True, exist_ok=True)
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
    for name, url in BUNDLES.items():
        target = CACHE / f"{name}_CRLs.zip"
        if target.exists():
            continue
        with opener.open(urllib.request.Request(url, headers={"User-Agent": "serenity-research-agent"}), timeout=120) as resp:
            target.write_bytes(resp.read())


def api_letters(offline: bool) -> list[dict] | None:
    """Letters from the openFDA CRL API, cached; None when no copy is available."""
    if not offline:
        try:
            import serenity_evidence_review as ser

            opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
            with opener.open(urllib.request.Request(API_URL, headers={"User-Agent": "serenity-research-agent"}), timeout=120) as resp:
                data = resp.read()
            if len(json.loads(data).get("results", [])) > 100:
                CACHE.mkdir(parents=True, exist_ok=True)
                API_CACHE.write_bytes(data)
        except Exception as exc:
            print(f"CRL API refresh skipped: {exc}")
    if not API_CACHE.exists():
        return None
    out = []
    for r in json.loads(API_CACHE.read_text(encoding="utf-8"))["results"]:
        if r.get("letter_type") not in (None, "COMPLETE RESPONSE"):
            continue                       # tentative approvals, refusals to file, rescissions
        if r.get("letter_type") is None and "COMPLETE RESPONSE" not in (r.get("text") or "")[:4000].upper():
            continue
        apps = [a for a in r.get("application_number") or [] if re.fullmatch(r"(NDA|BLA) \d+", a)] or r.get("application_number") or []
        m, d, y = (r.get("letter_date") or "//").split("/")
        out.append({"file": r["file_name"], "set": "approved" if r.get("approval_status") == "Approved" else "unapproved",
                    "text": r.get("text") or "", "issued": f"{y}-{m}-{d}" if y else None,
                    "company": (r.get("company_name") or "").strip(" ,.") or None,
                    "application": apps[0] if apps else None})
    return out


def extract_letters() -> dict:
    """PDF text per letter, cached. Needs pypdf only when the cache is missing a letter."""
    letters = json.loads(LETTERS.read_text(encoding="utf-8")) if LETTERS.exists() else {}
    changed = False
    for name in BUNDLES:
        bundle = CACHE / f"{name}_CRLs.zip"
        if not bundle.exists():
            continue
        with zipfile.ZipFile(bundle) as zf:
            for member in zf.namelist():
                base = Path(member).name
                if not base.lower().endswith(".pdf") or base in letters:
                    continue
                try:
                    from pypdf import PdfReader
                except ImportError:
                    print("pypdf not installed: letters missing from the cache were skipped")
                    return letters
                import io
                reader = PdfReader(io.BytesIO(zf.read(member)))
                letters[base] = {"set": name, "pages": len(reader.pages),
                                 "text": "\n".join((p.extract_text() or "") for p in reader.pages)}
                changed = True
    if changed:
        LETTERS.write_text(json.dumps(letters, ensure_ascii=False), encoding="utf-8")
    return letters


def sections(text: str) -> list[tuple[str, str]]:
    """(heading, body) pairs; text before the first heading is under 'PREAMBLE'."""
    out, last, name = [], 0, "PREAMBLE"
    for m in HEADING.finditer(text):
        head = re.sub(r"\s+", " ", m.group(1)).strip()
        if head in DEFICIENCY_SECTIONS or head in BOILERPLATE:
            out.append((name, text[last:m.start()]))
            name, last = head, m.end()
    out.append((name, text[last:]))
    return out


PAGE_NOISE = re.compile(r"Reference ID: \d+|\(b\)\s*\(4\)|^(?:NDA|BLA|STN BL) [\d /S-]+\s*$|^Page \d+.*$|U\.S\. Food (?:&|and) Drug Administration|Silver Spring, MD \d+|www\.fda\.gov|^\s*\d+\s*$", re.M)


def sentences(body: str):
    for s in re.split(r"(?<=[.;:])\s+(?=[A-Z(•])", re.sub(r"\s+", " ", PAGE_NOISE.sub(" ", body))):
        s = s.strip(" •")
        if 25 <= len(s) <= 400:
            yield s


def classify(text: str) -> dict:
    hits: dict[str, list[str]] = {k: [] for k in KEYWORDS}
    deficiency_sections = []
    for head, body in sections(text):
        if head in BOILERPLATE:
            continue
        if head in DEFICIENCY_SECTIONS:
            if "reserve comment" in body.lower() and len(body) < 600:
                continue
            deficiency_sections.append(head)
            home = DEFICIENCY_SECTIONS[head]
            for s in sentences(body):
                if home == "efficacy" and CLINICAL_SAFETY.search(s):
                    hits["safety"].append(s)
                elif home == "manufacturing" and head == "FACILITY INSPECTIONS" and not INSPECTION_FAIL.search(s):
                    continue
                else:
                    hits[home].append(s)
            continue
        for s in sentences(body):   # prose letters (older style) have no headings
            for cat, rx in KEYWORDS.items():
                if rx.search(s):
                    hits[cat].append(s)
                    break
    # One stray sentence is not a reason: efficacy/safety/pharmacology need two unless a deficiency heading says so.
    section_homes = {DEFICIENCY_SECTIONS[h] for h in deficiency_sections}
    reasons = {cat: {"sentences": len(v), "quote": v[0]} for cat, v in hits.items()
               if v and (len(v) >= 2 or cat in section_homes or cat in ("manufacturing", "usability"))}
    redacted = len(REDACTION.findall(text)) >= 5 and sum(1 for _ in sentences(text)) < 40
    new_trial = NEW_TRIAL.search(text)
    klass = RESUBMISSION_CLASS.search(text)
    if "efficacy" in reasons and (reasons["efficacy"]["sentences"] >= 2 or new_trial):
        severity = "heavy"
    elif "safety" in reasons and reasons["safety"]["sentences"] >= 2 or "pharmacology" in reasons and reasons["pharmacology"]["sentences"] >= 2:
        severity = "medium"
    elif reasons:
        severity = "light"
    else:
        severity = "redacted" if redacted else "unknown"
    return {"reasons": reasons, "severity": severity, "deficiencySections": deficiency_sections, "redacted": redacted,
            "newTrialRequired": bool(new_trial), "newTrialQuote": next((s for s in sentences(text) if NEW_TRIAL.search(s)), None),
            "resubmissionClass": int(klass.group(1)) if klass else None,
            "facilityInspectionFailed": "FACILITY INSPECTIONS" in deficiency_sections and bool(INSPECTION_FAIL.search(text))}


def drugsfda(app: str, fetch: bool) -> dict:
    """Sponsor and brand name from Drugs@FDA for the application number (cached)."""
    key = app.replace(" ", "")
    cache = CACHE / "drugsfda.json"
    known = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
    if key in known or not fetch:
        return known.get(key) or {}
    import serenity_evidence_review as ser

    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ser.context()))
    try:
        with opener.open(urllib.request.Request(DRUGSFDA.format(app=key), headers={"User-Agent": "serenity-research-agent"}), timeout=30) as resp:
            r = json.load(resp)["results"][0]
        known[key] = {"sponsor": r.get("sponsor_name"), "brand": next((p.get("brand_name") for p in r.get("products", []) if p.get("brand_name")), None)}
    except Exception:
        known[key] = {}
    cache.write_text(json.dumps(known, ensure_ascii=False, indent=1), encoding="utf-8")
    return known[key]


def metadata(name: str, text: str, fetch: bool = False) -> dict:
    m = re.match(r"CRL_(NDA|BLA)(\d+)_(\d{8})", name)
    if m:
        app, issued = f"{m.group(1)} {m.group(2)}", datetime.strptime(m.group(3), "%Y%m%d").date().isoformat()
    else:
        n = re.match(r"(\d{6})", name)
        kind = "BLA" if n and n.group(1).startswith("76") or re.search(r"\bBLA\b|Biologics License", text[:3000]) else "NDA"
        app = f"{kind} {n.group(1)}" if n else name
        issued = None
    head = text[:3000]
    before_dear = head.split("Dear")[0]
    if issued is None:
        d = LETTER_DATE.search(before_dear)
        if d:
            issued = datetime.strptime(f"{d.group(1).title()} {d.group(2)} {d.group(3)}", "%B %d %Y").date().isoformat()
        else:
            y = re.search(r"_(20\d\d)_", name)
            issued = f"{y.group(1)}-01-01" if y else None
    company = next((c.strip(" ,.") for c in COMPANY.findall(head)
                    if not re.search(r"Food|Drug Administration|Silver Spring|Avenue|Hampshire|COMPLETE RESPONSE|Page \d|STN|Our |^NDA|^BLA", c)), None)
    if company and re.match(r"c/o\b", company, re.I):   # 'C/O <agent>' follows the sponsor's own line
        lines = [l.strip() for l in head.split("\n") if l.strip()]
        idx = next((i for i, l in enumerate(lines) if l.startswith(company)), None)
        company = lines[idx - 1].strip(" ,.") if idx else company
    drug = DRUG.search(text[:6000])
    drug = re.sub(r"\s+", " ", drug.group(1)).strip() if drug else None
    source = "letter"
    if not company or not drug:
        fallback = drugsfda(app, fetch)
        if fallback:
            company, drug, source = company or fallback.get("sponsor"), drug or fallback.get("brand"), "letter+drugsfda"
    return {"application": app, "issued": issued, "company": company, "drug": drug, "metadataSource": source}


def match_tickers(company: str | None, tickers: dict[str, dict]) -> dict | None:
    if not company:
        return None
    key = normalize(company)
    if not key:
        return None
    exact = tickers.get(key)
    if exact:
        return exact
    for k, v in tickers.items():
        if len(k) >= 5 and (key.startswith(k + " ") or k.startswith(key + " ")):
            return v
    return None


def build(offline: bool) -> dict:
    if not offline:
        try:
            download_bundles()
        except Exception as exc:
            print(f"CRL download skipped: {exc}")
    pdfs = extract_letters()
    records = api_letters(offline)
    if records is None:                    # offline without the API copy: one row per zip PDF
        records = [{"file": name, "set": l["set"], "text": l["text"]} for name, l in sorted(pdfs.items())]
    per_file = Counter(r["file"] for r in records)
    tickers = {normalize(v["title"]): {"ticker": v["ticker"], "cik": f"{int(v['cik_str']):010d}", "name": v["title"]}
               for v in json.loads((ROOT / "state/sec-company-tickers.json").read_text(encoding="utf-8")).values()}
    universe = {c["ticker"] for c in json.loads((ROOT / "trend-agent/ai-medicine-universe.json").read_text(encoding="utf-8")).get("companies", [])}
    rows = []
    for letter in records:
        meta = metadata(letter["file"], letter["text"], fetch=not offline)
        if letter.get("issued"):            # FDA's structured fields beat parsing the letterhead
            meta.update({"issued": letter["issued"], "company": letter["company"] or meta["company"],
                         "application": letter["application"] or meta["application"],
                         "metadataSource": "openfda-api" + ("+drugsfda" if "drugsfda" in meta["metadataSource"] else "")})
        verdict = classify(letter["text"])
        pdf = pdfs.get(letter["file"])
        if letter.get("issued") and pdf and per_file[letter["file"]] == 1:
            # Same single letter in two renderings. OCR reads scanned pages pypdf misses, but it
            # garbles FDA's '(b) (4)' redaction marks and some headings; keep the fuller reading.
            from_pdf = classify(pdf["text"])
            if len(from_pdf["reasons"]) > len(verdict["reasons"]) or verdict["severity"] == "unknown" and from_pdf["severity"] != "unknown":
                verdict = from_pdf
            if from_pdf["redacted"] and not verdict["reasons"]:
                verdict.update(redacted=True, severity="redacted")
        listed = match_tickers(meta["company"], tickers)
        rows.append({"file": letter["file"], "set": letter["set"], **meta, **verdict, "listed": listed,
                     "inUniverse": bool(listed and listed["ticker"] in universe),
                     "source": API_URL.split("?")[0] if letter.get("issued") else BUNDLES[letter["set"]]})
    by_severity = Counter(r["severity"] for r in rows)
    by_reason = Counter(cat for r in rows for cat in r["reasons"])
    approved_by_severity = {s: {"approved": sum(1 for r in rows if r["severity"] == s and r["set"] == "approved"),
                                "total": by_severity[s]} for s in by_severity}
    return {"generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"), "letters": len(rows),
            "method": "Rule-based proxy over FDA's own letter text; each reason carries the first matching sentence as its citation. Severity: heavy = efficacy or new trial; medium = safety or new pharmacology studies; light = manufacturing, usability or format only.",
            "sources": {"api": API_URL.split("?")[0], **BUNDLES}, "bySeverity": dict(by_severity), "byReason": dict(by_reason),
            "laterApprovedBySeverity": approved_by_severity,
            "newTrialRequired": sum(r["newTrialRequired"] for r in rows),
            "facilityInspectionFailed": sum(r["facilityInspectionFailed"] for r in rows),
            "listedCompanies": sum(1 for r in rows if r["listed"]), "rows": rows}


def company_statement(row: dict, agent: str) -> dict | None:
    """The sponsor's own 8-K about the same CRL, from EDGAR full-text search, classified with the same rules."""
    import time
    import urllib.parse
    from datetime import timedelta

    import beneficiary_mapper as mapper

    issued = date.fromisoformat(row["issued"])
    query = urllib.parse.urlencode({"q": '"complete response letter"', "dateRange": "custom", "forms": "8-K",
                                    "ciks": row["listed"]["cik"], "startdt": issued.isoformat(),
                                    "enddt": (issued + timedelta(days=21)).isoformat()})
    hits = mapper.http_json(f"{mapper.EFTS}?{query}", agent).get("hits", {}).get("hits", [])
    if not hits:
        return None
    best = next((h for h in hits if re.search(r"99", h["_id"].split(":", 1)[1])), hits[0])  # press release exhibit over the cover 8-K
    hit = best["_source"]
    adsh, filename = best["_id"].split(":", 1)
    url = f"https://www.sec.gov/Archives/edgar/data/{int(row['listed']['cik'])}/{adsh.replace('-', '')}/{filename}"
    time.sleep(0.2)
    html = mapper.http_text(url, agent)
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    text = __import__("html").unescape(text)
    said = {}
    for s in sentences(text):
        for cat, rx in KEYWORDS.items():
            if rx.search(s) and cat not in said:
                said[cat] = s
    fda = set(row["reasons"])
    return {"url": url, "filed": hit.get("file_date"), "form": hit.get("form"), "chars": len(text),
            "companyMentioned": said, "fdaCited": sorted(fda), "omitted": sorted(fda - set(said)),
            "companyMentionsNewTrial": bool(NEW_TRIAL.search(text)) if row["newTrialRequired"] else None,
            "companyStatesClass": (m.group(1) if (m := RESUBMISSION_CLASS.search(text)) else None)}


def compare_disclosures(payload: dict, agent: str, limit: int) -> None:
    rows = [r for r in payload["rows"] if r["listed"] and r["issued"] and r["severity"] not in ("redacted", "unknown")]
    rows.sort(key=lambda r: r["issued"], reverse=True)
    done = 0
    for r in rows:
        if done >= limit:
            break
        try:
            c = company_statement(r, agent)
        except Exception as exc:
            r["disclosure"] = {"error": type(exc).__name__}
            continue
        if c:
            r["disclosure"] = c
            done += 1
    compared = [r for r in payload["rows"] if r.get("disclosure") and "url" in r["disclosure"]]
    payload["disclosureComparison"] = {
        "compared": len(compared),
        "withOmissions": sum(1 for r in compared if r["disclosure"]["omitted"]),
        "newTrialOmitted": sum(1 for r in compared if r["disclosure"]["companyMentionsNewTrial"] is False),
    }


def report(payload: dict) -> str:
    lines = ["# FDA 拒批信（CRL）原因分类", "",
             f"> {payload['letters']} 封 openFDA 公开的 CRL（2020 年至今）。分类是规则代理，每条原因附信件原句；严重度：重 = 有效性不足或需要新试验，中 = 安全性或需补药理研究，轻 = 生产、可用性或资料格式。生成时间 {payload['generatedAt'][:10]}。", "",
             "## 严重度与后来是否获批", "", "| 严重度 | 封数 | 其中后来获批 | 比例 |", "|---|---:|---:|---:|"]
    for sev in ("heavy", "medium", "light", "unknown", "redacted"):
        a = payload["laterApprovedBySeverity"].get(sev)
        if a:
            lines.append(f"| {sev} | {a['total']} | {a['approved']} | {a['approved']/a['total']:.0%} |")
    lines += ["", "原因出现次数：" + "，".join(f"{k} {v}" for k, v in sorted(payload["byReason"].items(), key=lambda x: -x[1])) + "。",
              f"要求新试验 {payload['newTrialRequired']} 封；工厂检查未通过 {payload['facilityInspectionFailed']} 封；可对应上市公司 {payload['listedCompanies']} 封。", "",
              "## 最近 25 封", "", "| 日期 | 申请 | 公司 | 药物 | 严重度 | 原因 | 新试验 | 后来获批 |", "|---|---|---|---|---|---|---|---|"]
    for r in sorted(payload["rows"], key=lambda r: r["issued"] or "", reverse=True)[:25]:
        tick = f" ({r['listed']['ticker']})" if r["listed"] else ""
        lines.append(f"| {r['issued']} | {r['application']} | {(r['company'] or '?')}{tick} | {r['drug'] or '?'} | {r['severity']} | {', '.join(r['reasons'])} | {'是' if r['newTrialRequired'] else ''} | {'是' if r['set']=='approved' else '否'} |")
    if payload.get("disclosureComparison"):
        c = payload["disclosureComparison"]
        lines += ["", "## FDA 信件 vs 公司 8-K 公告", "",
                  f"对比了 {c['compared']} 封有上市公司 8-K 的信：{c['withOmissions']} 封公司公告未提及 FDA 引用的至少一类原因；FDA 要求新试验的信里，{c['newTrialOmitted']} 封公司公告没有用\"新试验 / 补做试验\"的措辞（通常改说在研试验的数据）。关键词对比只能发现遗漏，不能证明披露完整。", "",
                  "| 日期 | 公司 | 药物 | FDA 原因 | 公司提到 | 公司未提 | FDA 要求新试验：公司措辞 | 8-K |", "|---|---|---|---|---|---|---|---|"]
        for r in sorted((r for r in payload["rows"] if r.get("disclosure") and "url" in r["disclosure"]), key=lambda r: r["issued"], reverse=True):
            d = r["disclosure"]
            trial = "" if d["companyMentionsNewTrial"] is None else ("用了" if d["companyMentionsNewTrial"] else "**未用**")
            lines.append(f"| {r['issued']} | {r['company']} ({r['listed']['ticker']}) | {r['drug'] or '?'} | {', '.join(d['fdaCited'])} | {', '.join(d['companyMentioned']) or '—'} | {', '.join(d['omitted']) or '—'} | {trial} | [8-K]({d['url']}) |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--compare", type=int, default=0, help="compare up to N letters with the sponsor's 8-K (needs SEC_USER_AGENT)")
    args = parser.parse_args()
    payload = build(args.offline)
    agent = __import__("os").getenv("SEC_USER_AGENT", "")
    if args.compare and "@" in agent:
        compare_disclosures(payload, agent, args.compare)
        print("disclosure comparison:", payload["disclosureComparison"])
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(report(payload), encoding="utf-8")
    print(f"{payload['letters']} letters; severity {payload['bySeverity']}; reasons {payload['byReason']}; listed {payload['listedCompanies']}")


if __name__ == "__main__":
    main()
