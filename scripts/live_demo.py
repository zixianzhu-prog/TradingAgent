"""Three short live demos, each under a minute, for showing the agent in a meeting.

  topic "digital pathology"   Any AI-medicine area named in the room: search SEC full text now,
                              open the top filings and say which companies build it (own product),
                              supply or use it, or only mention it as competition.
  fda                         Latest FDA AI/software device decisions from openFDA, mapped to listed
                              companies. Read-only: nothing is written to the news database.
  quote                       The citation check on a real Serenity quote: original passes, the same
                              quote with one word changed is rejected. Offline.

    export SEC_USER_AGENT="Your Name you@example.com"   # needed to open filings not yet cached
    python3 scripts/live_demo.py topic "digital pathology"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

BOLD, DIM, RESET = "\033[1m", "\033[2m", "\033[0m"
COLOURS = {"own-product": "\033[32m", "supplier": "\033[36m", "customer": "\033[36m", "competition": "\033[31m",
           "topic-absent": "\033[33m", "glossary": "\033[33m", "mention": "\033[37m", "not-in-filing": "\033[33m", "unread": "\033[33m"}
LABELS = {"own-product": "自己在做", "supplier": "供应商", "customer": "使用者", "competition": "多为竞争/风险表述",
          "topic-absent": "主题词几乎不出现", "glossary": "术语表", "mention": "提及，关系不明", "not-in-filing": "文件中未找到", "unread": "未读取"}
SYNONYMS = {"approximately": "roughly", "include": "are", "including": "such as", "representing": "covering",
            "established": "set up", "received": "obtained", "reimbursed": "paid", "more than": "over", "primary": "main"}
AI_WORDS = re.compile(r"\b(?:ai|artificial intelligence|machine learning|deep learning)\b", re.I)


def say(text: str = "") -> None:
    print(text, flush=True)


def tag(relation: str) -> str:
    return f"{COLOURS.get(relation, '')}{LABELS.get(relation, relation)}{RESET}"


# ---------------------------------------------------------------- A. topic -> companies
def phrases_for(topic: str) -> tuple[list[str], str, bool]:
    """SEC search phrases for a topic typed in the room, plus the non-AI core term."""
    core = AI_WORDS.sub(" ", topic).strip(" -") or topic
    core = re.sub(r"\s+", " ", core)
    asks_for_ai = bool(AI_WORDS.search(topic)) or True  # AI-medicine demo: always pair with AI
    phrases = [f'"artificial intelligence" "{core}"', f'"machine learning" "{core}"', f'"{core}"']
    return phrases, core, asks_for_ai


def topic_demo(topic: str, limit: int, days: int) -> None:
    import beneficiary_mapper as mapper
    import prepare_claude_review as claude
    import urllib.parse
    from ai_medicine_universe_screen import FORMS, is_operating
    from validate_topic_mapping import classify_filing

    started = time.time()
    phrases, core, uses_ai = phrases_for(topic)
    end = date.today()
    start = end - timedelta(days=days)
    say(f"{BOLD}主题：{topic}{RESET}   SEC 全文检索 {start} 至 {end}，短语：{', '.join(phrases[:2])}")
    found: dict[str, dict] = {}
    for phrase in phrases[:2]:
        params = urllib.parse.urlencode({"q": phrase, "dateRange": "custom", "startdt": start.isoformat(),
                                         "enddt": end.isoformat(), "forms": FORMS})
        payload = mapper.http_json(f"{mapper.EFTS}?{params}", mapper.DEFAULT_AGENT)
        total = payload.get("hits", {}).get("total", {}).get("value", 0)
        say(f"  {phrase}: {total:,} 份文件命中")
        for row in mapper.aggregate(payload.get("hits", {}).get("hits", [])).values():
            if not is_operating(row):
                continue
            entry = found.setdefault(row["ticker"], {"name": row["name"], "filings": {}, "sic": row.get("sicGroup", "")})
            entry["filings"].update(row["filings"])
    ranked = sorted(found.items(), key=lambda kv: -len(kv[1]["filings"]))[:limit]
    say(f"  上市公司 {len(found)} 家；打开前 {len(ranked)} 家的最新文件逐份阅读…")
    terms = re.compile(re.escape(core), re.I)

    def pick(filings: dict) -> dict:
        """Annual report first, then quarterly, then anything else; skip exhibits such as contracts."""
        order = {"10-K": 0, "20-F": 0, "10-Q": 1, "6-K": 2, "8-K": 3}
        main = [f for f in filings.values() if not re.search(r"/(?:ex|exhibit)[^/]*$", f["url"], re.I)] or list(filings.values())
        return min(main, key=lambda f: (order.get(f.get("form", ""), 4), "".join(chr(255 - ord(c)) for c in (f.get("filed") or ""))))

    def snippet(text: str) -> str:
        """The passage where the topic and an AI term appear together, else the first topic mention."""
        first = None
        for m in terms.finditer(text):
            window = text[max(0, m.start() - 260): m.end() + 260]
            first = first or window
            if AI_WORDS.search(window):
                return window
        return first or ""

    def read(item):
        ticker, entry = item
        latest = pick(entry["filings"])
        try:
            text = claude.filing_text(latest["url"], allow_fetch=True) or ""
        except Exception:
            text = ""
        view = classify_filing(text, "live", terms=terms, uses_ai=uses_ai) if text else {"relation": "unread", "aiMentions": 0, "topicMentions": 0, "example": ""}
        view["snippet"] = snippet(text) if text else ""
        return ticker, entry, latest, view

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(read, ranked))
    say()
    say(f"{BOLD}{'代码':<7}{'公司':<34}{'判断':<12}{'AI提及':>7}{'主题词':>7}{RESET}")
    keep = {"own-product", "supplier", "customer"}
    results.sort(key=lambda r: (r[3]["relation"] not in keep, -r[3]["topicMentions"]))
    shown_divider = False
    for ticker, entry, latest, view in results:
        if view["relation"] not in keep and not shown_divider:
            say(f"{DIM}—— 以下剔除：文件里看不出这家公司在做这件事 ——{RESET}")
            shown_divider = True
        say(f"{ticker:<7}{entry['name'][:32]:<34}{tag(view['relation']):<21}{view['aiMentions']:>7}{view['topicMentions']:>7}")
        if view.get("snippet"):
            text_ = re.sub(r"\s+", " ", view["snippet"])
            hit = terms.search(text_)
            centre = hit.start() if hit else len(text_) // 2
            say(f"       {DIM}“…{text_[max(0, centre - 110): centre + 150].strip()}…”{RESET}")
        say(f"       {DIM}{latest.get('form', '')} {latest.get('filed', '')} · {latest['url']}{RESET}")
    kept = sum(1 for *_, v in results if v["relation"] in {"own-product", "supplier", "customer"})
    say()
    say(f"{BOLD}{kept}/{len(results)} 家保留{RESET}（自己在做 / 供应商 / 使用者）；其余剔除。用时 {time.time() - started:.0f} 秒。")


# ---------------------------------------------------------------- B. FDA
def fda_demo(days: int, rows: int) -> None:
    import fda_device_feed as feed

    started = time.time()
    end = date.today()
    start = end - timedelta(days=days)
    say(f"{BOLD}openFDA：{start} 至 {end} 的器械决定{RESET}（只读，不写入数据库）")
    decisions = []
    for endpoint in ("510k", "pma"):
        decisions += [d for d in (feed.normalise(r, endpoint) for r in feed.pull(endpoint, start, end)) if d]
    fda_list = json.loads((ROOT / "state/fda-ai-devices.json").read_text(encoding="utf-8"))
    known = {d.get("submissionNumber") for d in fda_list.get("devices", [])}
    events = feed.build(decisions, feed.company_index(), feed.ai_product_codes(fda_list), known, feed.sec_listed())
    high = [e for e in events if e["aiConfidence"] == "high"]
    latest = max((d["decisionDate"] for d in decisions), default="—")
    say(f"  扫描 {len(decisions)} 条决定；明确的 AI/软件器械 {len(high)} 条；数据中最新决定日期 {latest}（openFDA 比 FDA 晚 1–2 周）")
    say()
    say(f"{BOLD}{'日期':<12}{'类型':<10}{'器械':<44}{'上市公司'}{RESET}")
    for e in high[:rows]:
        who = (f"\033[32m{e['ticker']} 已覆盖{RESET}" if e.get("covered") else
               f"\033[36m{e['ticker']} 已上市，未覆盖{RESET}" if e.get("ticker") else f"{DIM}私营：{e['applicant'][:28]}{RESET}")
        say(f"{e['decisionDate']:<12}{e['kind']:<10}{e['device'][:42]:<44}{who}")
    say()
    say(f"用时 {time.time() - started:.0f} 秒。")


# ---------------------------------------------------------------- C. citation check
def quote_demo(ticker: str, change: str | None) -> None:
    import serenity_evidence_review as ser

    review = next(r for r in json.loads((ROOT / "state/serenity-claude-response.json").read_text(encoding="utf-8"))["reviews"] if r["ticker"] == ticker)
    manifest = {c["ticker"]: c for c in json.loads((ROOT / "state/serenity-claude-queue.json").read_text(encoding="utf-8"))["companies"]}
    passages = {p["id"]: p for p in json.loads((ROOT / manifest[ticker]["packetPath"]).read_text(encoding="utf-8"))["evidence"]}
    refs = [(g, r) for g, item in review["gates"].items() for r in item.get("support", []) if len(r["quote"]) > 40]
    # Prefer a quote with a number in it: changing a figure is the error that matters most.
    gate, ref = next(((g, r) for g, r in refs if re.search(r"\d", r["quote"])), refs[0])
    passage = passages[ref["id"]]
    original = ref["quote"]
    variants = []
    if change and "=>" in change:
        old, new = [part.strip() for part in change.split("=>", 1)]
        variants.append((f"改一个词（{old} → {new}）", original.replace(old, new, 1)))
    else:
        number = re.search(r"\d+(?:\.\d+)?%?", original)
        if number:
            changed = number.group(0).replace("9", "8") if "9" in number.group(0) else str(int(re.sub(r"\D", "", number.group(0)) or 0) + 1)
            variants.append((f"改一个数字（{number.group(0)} → {changed}）", original.replace(number.group(0), changed, 1)))
        for old, new in SYNONYMS.items():
            if re.search(rf"\b{old}\b", original, re.I):
                variants.append((f"同义改写（{old} → {new}），AI 复述时常见", re.sub(rf"\b{old}\b", new, original, count=1, flags=re.I)))
                break

    def check(quote: str) -> bool:
        """The importer's rule: the cleaned quote must appear verbatim in the cleaned passage."""
        return ser.clean(quote) in ser.clean(passage["text"])

    say(f"{BOLD}{ticker} · 门槛 {gate}{RESET}")
    say(f"  来源文件：{passage['url']}")
    say()
    for label, quote in [("原文引用", original)] + variants:
        ok = check(quote)
        mark = "\033[32m✔ 通过：在 SEC 原文中逐字找到" if ok else "\033[31m✘ 拒绝：原文中找不到，该门槛降级"
        say(f"{BOLD}{label}{RESET}")
        say(f"  “{quote}”")
        say(f"  {mark}{RESET}")
        say()


def main() -> None:
    parser = argparse.ArgumentParser(description="Live demos: topic mapping, FDA feed, citation check")
    sub = parser.add_subparsers(dest="command", required=True)
    t = sub.add_parser("topic")
    t.add_argument("topic")
    t.add_argument("--limit", type=int, default=12)
    t.add_argument("--days", type=int, default=365)
    f = sub.add_parser("fda")
    f.add_argument("--days", type=int, default=45)
    f.add_argument("--rows", type=int, default=10)
    q = sub.add_parser("quote")
    q.add_argument("--ticker", default="HTFL")
    q.add_argument("--change", help='e.g. "Category I=>Category III"')
    args = parser.parse_args()
    if args.command == "topic":
        topic_demo(args.topic, args.limit, args.days)
    elif args.command == "fda":
        fda_demo(args.days, args.rows)
    else:
        quote_demo(args.ticker, args.change)


if __name__ == "__main__":
    main()
