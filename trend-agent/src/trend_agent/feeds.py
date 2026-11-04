from __future__ import annotations

import html
import json
import re
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from .models import Article


TAG_RE = re.compile(r"<[^>]+>")


def clean_text(value: str | None) -> str:
    return " ".join(html.unescape(TAG_RE.sub(" ", value or "")).split())


def _child_text(node: ET.Element, names: tuple[str, ...]) -> str:
    for child in node.iter():
        local_name = child.tag.rsplit("}", 1)[-1].lower()
        if local_name in names and child.text:
            return clean_text(child.text)
    return ""


def _link(node: ET.Element) -> str:
    for child in node.iter():
        if child.tag.rsplit("}", 1)[-1].lower() != "link":
            continue
        if child.attrib.get("href"):
            return child.attrib["href"]
        if child.text:
            return child.text.strip()
    return ""


def parse_feed(payload: bytes, source: str) -> list[Article]:
    root = ET.fromstring(payload)
    entries = [node for node in root.iter() if node.tag.rsplit("}", 1)[-1].lower() in {"item", "entry"}]
    articles: list[Article] = []
    for entry in entries:
        entry_source = _child_text(entry, ("source",))
        title = _child_text(entry, ("title",))
        content = _child_text(entry, ("content", "summary", "description"))
        published_at = _child_text(entry, ("published", "updated", "pubdate"))
        url = _link(entry)
        if title or content:
            articles.append(Article(entry_source or source, title or "Untitled", url, content, published_at))
    return articles


def fetch_feed(url: str, source: str, timeout: int = 20) -> list[Article]:
    request = urllib.request.Request(url, headers={"User-Agent": "TrendAgent/0.1"})
    system_ca = Path("/etc/ssl/cert.pem")
    context = ssl.create_default_context(cafile=str(system_ca) if system_ca.exists() else None)
    with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
        return parse_feed(response.read(), source)


def load_feed_file(path: str | Path, source: str) -> list[Article]:
    return parse_feed(Path(path).read_bytes(), source)


def article_from_change(payload: dict[str, Any]) -> Article:
    source = str(payload.get("source") or payload.get("watch_url") or payload.get("url") or "changedetection")
    title = str(payload.get("title") or payload.get("watch_title") or "Website changed")
    url = str(payload.get("url") or payload.get("watch_url") or "")
    content = str(
        payload.get("content")
        or payload.get("diff")
        or payload.get("message")
        or payload.get("body")
        or json.dumps(payload, ensure_ascii=False)
    )
    return Article(source=source, title=title, url=url, content=clean_text(content))
