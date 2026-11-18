#!/usr/bin/env python3
"""检查构建产物是否自洽，供 CI 使用。

检查项：
    产物齐全    manifest 里每篇都有 zh/*.md 与 site/*.html
    图片        zh/ 与 site/ 引用的本地图片都存在
    锚点        site/ 页面内 href="#..." 都能命中 id
    页面链接    site/ 里指向 .html 的链接都存在
    单文件      section 数量正确、图片全部内嵌、无外链图片

用法：
    python3 tools/check_site.py
退出码 0 表示全部通过，1 表示有问题。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZH = ROOT / "zh"
SITE = ROOT / "site"
MANIFEST = ROOT / "translation-manifest.json"


def main() -> int:
    problems: list[str] = []

    docs = json.loads(MANIFEST.read_text(encoding="utf-8"))
    slugs = [d["slug"] for d in docs]

    for d in docs:
        slug = d["slug"]
        if not (ZH / f"{slug}.md").exists():
            problems.append(f"缺少 Markdown：zh/{slug}.md")
        if not (SITE / f"{slug}.html").exists():
            problems.append(f"缺少页面：site/{slug}.html")

    md_files = sorted(ZH.glob("*.md"))
    for p in md_files:
        text = p.read_text(encoding="utf-8")
        for src in re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", text):
            if src.startswith(("http://", "https://")):
                continue
            if not (p.parent / src).exists():
                problems.append(f"{p.name}: 图片不存在 {src}")

    known = {f"{slug}.html" for slug in slugs} | {"index.html", "notice.html"}
    pages = sorted(p for p in SITE.glob("*.html") if p.name in known)
    for page in pages:
        html = page.read_text(encoding="utf-8")
        ids = set(re.findall(r'id="([^"]+)"', html))
        for anchor in re.findall(r'href="#([^"]+)"', html):
            if anchor not in ids:
                problems.append(f"{page.name}: 锚点不存在 #{anchor}")
        for href in re.findall(r'href="([^"]+)"', html):
            if href.startswith(("http://", "https://", "#", "mailto:", "data:")):
                continue
            target = href.split("#")[0]
            if target and not (SITE / target).exists():
                problems.append(f"{page.name}: 链接目标不存在 {href}")
        if not re.search(r'<meta name="description" content="[^"]+"', html):
            problems.append(f"{page.name}: 缺少 meta description")
        if 'rel="icon"' not in html:
            problems.append(f"{page.name}: 缺少 favicon")
        for src in re.findall(r'<img[^>]+src="([^"]+)"', html):
            if src.startswith(("http://", "https://", "data:")):
                continue
            if not (SITE / src).exists():
                problems.append(f"{page.name}: 图片不存在 {src}")

    single = ROOT / "Beancount中文文档-单文件.html"
    if not single.exists():
        problems.append("缺少 Beancount中文文档-单文件.html")
    else:
        html = single.read_text(encoding="utf-8")
        expected = len(slugs) + 2  # 首页 + 正文 + 版权页
        got = html.count('class="doc-section"')
        if got != expected:
            problems.append(f"单文件 section 数量 {got}，应为 {expected}")
        external = [s for s in re.findall(r'<img[^>]+src="([^"]+)"', html) if not s.startswith("data:")]
        if external:
            problems.append(f"单文件仍有 {len(external)} 张外链图片")
        if 'id="q"' not in html:
            problems.append("单文件缺少搜索框")

    if problems:
        print(f"检查未通过，共 {len(problems)} 项：")
        for item in problems:
            print("  -", item)
        return 1

    print(f"检查通过：{len(docs)} 篇文档、{len(pages)} 个页面、单文件 section {len(slugs) + 2} 个。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
