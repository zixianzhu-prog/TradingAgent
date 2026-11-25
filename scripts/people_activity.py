"""Where the company and its key people show up: conference presentations, fireside chats, keynotes, academic talks.

For each company in the deep-review queue, and for its founders and scientists (state/key-people.json), the script
runs a Google News search over the last 60 days and keeps headlines that name a talk: "to present at", "to participate
in", "fireside chat", "keynote", "panel discussion", "webcast", "symposium", "grand rounds". A person counts only when the
headline names that person; a company event only when it names the company. No model is used.

This is visibility, not evidence of value: management presenting at an investor conference is routine. It feeds the
key-people watch list (what to read or listen to next), not the Serenity gates.

    python3 scripts/people_activity.py
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "state/people-activity.json"
REPORT = ROOT / "outputs/people-activity.md"
KEY_PEOPLE = ROOT / "state/key-people.json"
FILTER = ROOT / "state/candidate-filter.json"
LOOKBACK = 60
TALK = re.compile(r"\bto (?:present|participate|host|speak)\b|fireside chat|keynote|panel discussion|webcast|symposium|grand rounds|"
                  r"\bpresents?\b.*\b(?:data|conference|meeting|congress)\b|\bat the [A-Z][\w&' ]+ (?:Conference|Summit|Meeting|Congress)", re.I)
CONFERENCE = re.compile(r"((?:[A-Z][\w&.'-]*\s){0,6}(?:Conference|Summit|Meeting|Congress|Symposium|Forum|Week|Day))")


def load(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def feed(query: str) -> list[dict]:
    sys.path.insert(0, str(ROOT / "trend-agent/src"))
    from trend_agent.feeds import fetch_feed  # noqa: E402

    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": f"{query} when:{LOOKBACK}d", "hl": "en-US", "gl": "US", "ceid": "US:en"})
    try:
        return [a.as_dict() for a in fetch_feed(url, "Google News", 20)[:40]]
    except Exception:  # one failed search must not stop the rest
        return []


def when(article: dict) -> str | None:
    raw = article.get("published_at") or article.get("published") or ""
    try:
        return parsedate_to_datetime(raw).date().isoformat()
    except (TypeError, ValueError):
        return raw[:10] or None


def talks(articles: list[dict], must: str) -> list[dict]:
    out, seen = [], set()
    for a in articles:
        title = a.get("title", "")
        head = title.rpartition(" - ")[0] or title
        if must.lower() not in head.lower() or not TALK.search(head):
            continue
        key = re.sub(r"\W+", " ", head.lower()).strip()[:80]
        if key in seen:
            continue
        seen.add(key)
        conf = CONFERENCE.search(head)
        out.append({"date": when(a), "headline": head.strip(), "venue": conf.group(1).strip() if conf else None, "url": a.get("url")})
    return sorted(out, key=lambda r: r["date"] or "", reverse=True)


def build(queue: list[str], companies: dict, people: dict, fetch=feed, pause: float = 1.0) -> dict:
    rows = {}
    for t in queue:
        name = (companies.get(t) or {}).get("company") or t
        short = re.sub(r",?\s+(Inc|Corp|Corporation|Ltd|plc|N\.V\.|S\.A\.|SA|Holdings?)\.?$", "", name).strip()
        company_talks = talks(fetch(f'"{short}"'), short.split()[0])
        time.sleep(pause)
        person_talks = []
        for p in (people.get(t) or {}).get("people", []):
            if not (p.get("founder") or p.get("scientist")):
                continue
            found = talks(fetch(f'"{p["name"]}"'), p["name"].split()[-1])
            person_talks += [{**f, "person": p["name"], "title": p.get("title")} for f in found]
            time.sleep(pause)
        rows[t] = {"company": name, "companyTalks": company_talks[:8], "peopleTalks": person_talks[:8]}
    return {"generatedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"), "lookbackDays": LOOKBACK,
            "method": __doc__.split("\n\n")[1].strip(), "companies": rows,
            "summary": {"companies": len(rows), "companyTalks": sum(len(r["companyTalks"]) for r in rows.values()),
                        "peopleTalks": sum(len(r["peopleTalks"]) for r in rows.values())}}


def render(payload: dict) -> str:
    s = payload["summary"]
    lines = ["# 公司和核心人物的公开活动（近 60 天）", "", f"生成：{payload['generatedAt']}", "",
             f"{s['companies']} 家公司；公司层面活动 {s['companyTalks']} 条，核心人物活动 {s['peopleTalks']} 条。"
             "只是曝光，不是价值证据；用于决定接下来读什么、听什么。", ""]
    for t, r in payload["companies"].items():
        if not r["companyTalks"] and not r["peopleTalks"]:
            continue
        lines += [f"## {t} · {r['company']}", ""]
        for x in r["peopleTalks"]:
            lines.append(f"- {x['date']} **{x['person']}**：[{x['headline']}]({x['url']})")
        for x in r["companyTalks"]:
            lines.append(f"- {x['date']} [{x['headline']}]({x['url']})")
        lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    flt = load(FILTER, {})
    companies = flt.get("companies", {}) if isinstance(flt.get("companies"), dict) else {}
    people = load(KEY_PEOPLE, {}).get("companies", {})
    payload = build(flt.get("deepReview", []), companies, people)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT.write_text(render(payload), encoding="utf-8")
    print(json.dumps(payload["summary"]))


if __name__ == "__main__":
    main()
