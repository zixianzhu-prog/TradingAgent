"""Chinese copy of the demo page from a phrase table.

The English page stays the source of truth. This script walks every text node of the
rendered HTML, replaces each number with {n} to form a lookup key, and substitutes the
Chinese phrase from trend-agent/i18n/top5.zh.json, putting the numbers back in order.
Text with no entry stays in English: news headlines, quotes from filings (they must
match the source word for word), company and applicant names.

    python3 scripts/translate_page.py                      # writes dashboard/dist/top5.zh.html
    python3 scripts/translate_page.py --missing out.json   # also lists untranslated phrases
"""
from __future__ import annotations

import argparse
import html as htmllib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
TOKEN = re.compile(r"(<[^>]+>)")
SKIP_OPEN = re.compile(r"<(style|script)\b", re.I)
SKIP_CLOSE = re.compile(r"</(style|script)>", re.I)


def key_of(text: str) -> tuple[str, list[str]]:
    return NUMBER.sub("{n}", text), NUMBER.findall(text)


def fill(template: str, numbers: list[str]) -> str:
    parts = template.split("{n}")
    if len(parts) - 1 != len(numbers):
        return ""
    return "".join(p + (numbers[i] if i < len(numbers) else "") for i, p in enumerate(parts))


def translate(html: str, table: dict[str, str]) -> tuple[str, set[str]]:
    out, missing, skipping, anchor = [], set(), False, 0
    for piece in TOKEN.split(html):
        if piece.startswith("<"):
            if re.match(r"<a\b", piece, re.I):
                anchor += 1
            elif re.match(r"</a>", piece, re.I):
                anchor = max(0, anchor - 1)
            if SKIP_OPEN.match(piece):
                skipping = True
            elif SKIP_CLOSE.match(piece):
                skipping = False
            out.append(piece)
            continue
        text = piece.strip()
        if skipping or not text or not re.search(r"[A-Za-z]{2}", text):
            out.append(piece)
            continue
        key, numbers = key_of(htmllib.unescape(text))
        chinese = fill(table[key], numbers) if key in table else ""
        if not chinese and "; " in text:
            # Ticket reasons are joined with "; ": translate each reason on its own.
            parts = [fill(table.get(k, ""), n) for k, n in map(key_of, htmllib.unescape(text).split("; "))]
            chinese = "；".join(parts) if all(parts) else ""
        if chinese:
            lead, trail = piece[:len(piece) - len(piece.lstrip())], piece[len(piece.rstrip()):]
            out.append(lead + htmllib.escape(chinese, quote=False) + trail)
        else:
            missing.add(("link: " if anchor else "") + key)
            out.append(piece)
    return "".join(out), missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Write the Chinese copy of the demo page")
    parser.add_argument("--source", default=str(ROOT / "dashboard/dist/top5.html"))
    parser.add_argument("--table", default=str(ROOT / "trend-agent/i18n/top5.zh.json"))
    parser.add_argument("--output", default=str(ROOT / "dashboard/dist/top5.zh.html"))
    parser.add_argument("--missing")
    args = parser.parse_args()
    table = json.loads(Path(args.table).read_text(encoding="utf-8"))
    html, missing = translate(Path(args.source).read_text(encoding="utf-8"), table)
    html = html.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta http-equiv="content-language" content="zh-CN">', 1)
    note = ('<p class="note" style="margin:0">中文版：由英文页按对照表自动生成，每天随英文页更新。'
            '文件原文引用、新闻标题、公司名和股票代码保留英文，便于与来源核对。</p>')
    html = html.replace('<header class="intro">', '<header class="intro">\n    ' + note, 1)
    Path(args.output).write_text(html, encoding="utf-8")
    if args.missing:
        Path(args.missing).write_text(json.dumps(sorted(missing), ensure_ascii=False, indent=0), encoding="utf-8")
    print(json.dumps({"output": args.output, "untranslated": len(missing)}))


if __name__ == "__main__":
    main()
