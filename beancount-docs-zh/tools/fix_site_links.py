#!/usr/bin/env python3
"""Post-process the generated site: remove dead same-page anchors and add notice page."""

from __future__ import annotations

import html
import re
from pathlib import Path

import markdown

from build_all_site import BASE_URL, ICON

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
NOTICE = ROOT / "NOTICE.md"


def strip_dead_anchors(text: str) -> str:
    ids = set(re.findall(r'\bid="([^"]+)"', text))

    def repl(match: re.Match) -> str:
        frag = match.group(1)
        if frag in ids:
            return match.group(0)
        # Keep the <a> element but remove the dead href.
        return ""

    return re.sub(r'\s+href="#([^"]+)"', repl, text)


def dedupe_ids(text: str) -> str:
    """Keep the first occurrence of each HTML id and remove later duplicates."""
    seen: set[str] = set()

    def repl(match: re.Match) -> str:
        tag = match.group(0)
        value = match.group(1)
        if value in seen:
            return re.sub(r'\s+id="[^"]+"', "", tag, count=1)
        seen.add(value)
        return tag

    return re.sub(r'<[^>]+\sid="([^"]+)"[^>]*>', repl, text)


def build_notice() -> None:
    md = markdown.Markdown(extensions=["extra", "toc", "sane_lists", "fenced_code", "tables"])
    body = md.convert(NOTICE.read_text(encoding="utf-8"))
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>版权与许可 · Beancount 中文文档</title>
  <meta name="description" content="Beancount 中文文档的版权、许可与免责说明：原文 MIT License，中文为非官方翻译。">
  <link rel="canonical" href="{BASE_URL}/notice.html">
  <link rel="icon" href="{ICON}">
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="index.html">Beancount 中文文档 <span>版权</span></a>
      <div class="tagline">NOTICE · MIT · 非官方翻译</div>
    </div>
  </header>
  <div class="layout">
    <aside class="sidebar">
      <p class="sidebar-label">On this page</p>
      <nav class="toc">{md.toc}</nav>
    </aside>
    <main>
      <article>
        <div class="article-meta">
          <span class="badge">版权与许可</span>
          <a href="index.html">← 返回索引</a>
        </div>
        {body}
      </article>
    </main>
  </div>
  <footer class="page-footer">Beancount 中文文档 · 非官方机器翻译 · 原文 MIT License</footer>
</body>
</html>
"""
    (SITE / "notice.html").write_text(page, encoding="utf-8")


def main() -> None:
    for path in SITE.glob("*.html"):
        text = path.read_text(encoding="utf-8")
        text = dedupe_ids(text)
        text = strip_dead_anchors(text)
        text = text.replace('href="../NOTICE.md"', 'href="notice.html"')
        text = text.replace('href="NOTICE.md"', 'href="notice.html"')
        path.write_text(text, encoding="utf-8")
    build_notice()
    print("fixed site links; built notice.html")


if __name__ == "__main__":
    main()
