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
        if not re.search(r'<link rel="canonical" href="https://[^"]+"', html):
            problems.append(f"{page.name}: 缺少 canonical 链接")
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
        pagers = html.count('class="pager"')
        if pagers != len(slugs):
            problems.append(f"单文件翻页数 {pagers}，应为 {len(slugs)}")

    sitemap = SITE / "sitemap.xml"
    if not sitemap.exists():
        problems.append("缺少 site/sitemap.xml")
    else:
        locs = re.findall(r"<loc>([^<]+)</loc>", sitemap.read_text(encoding="utf-8"))
        if len(locs) != len(slugs) + 2:
            problems.append(f"sitemap 条目 {len(locs)}，应为 {len(slugs) + 2}")
        bad = [u for u in locs if not u.startswith("https://")]
        if bad:
            problems.append(f"sitemap 含非绝对地址：{bad[:3]}")

    robots = SITE / "robots.txt"
    if not robots.exists():
        problems.append("缺少 site/robots.txt")
    elif "Sitemap: https://" not in robots.read_text(encoding="utf-8"):
        problems.append("robots.txt 未指向 sitemap")

    not_found = SITE / "404.html"
    if not not_found.exists():
        problems.append("缺少 site/404.html")
    elif "<h1>" not in not_found.read_text(encoding="utf-8"):
        problems.append("404.html 缺少标题")

    # 翻页链路：从第一篇按“下一篇”走到底，应恰好覆盖每篇一次
    prev_of: dict[str, str | None] = {}
    next_of: dict[str, str | None] = {}
    for slug in slugs:
        html = (SITE / f"{slug}.html").read_text(encoding="utf-8")
        if 'class="pager"' not in html:
            problems.append(f"{slug}.html: 缺少文末翻页")
            continue
        m_prev = re.search(r'class="pager-card pager-prev" href="([^"]+)"', html)
        m_next = re.search(r'class="pager-card pager-next" href="([^"]+)"', html)
        prev_of[slug] = m_prev.group(1) if m_prev else None
        next_of[slug] = m_next.group(1) if m_next else None

    starts = [s for s in slugs if prev_of.get(s) is None]
    if len(starts) != 1:
        problems.append(f"翻页起点应有 1 个，实际 {len(starts)} 个")
    else:
        seen: list[str] = []
        cur: str | None = starts[0] + ".html"
        while cur and cur.endswith(".html"):
            slug = cur[:-5]
            if slug in seen:
                problems.append(f"翻页出现循环：{slug}")
                break
            seen.append(slug)
            cur = next_of.get(slug)
        if len(seen) != len(slugs) or set(seen) != set(slugs):
            problems.append(f"翻页链路覆盖 {len(seen)} 篇，应为 {len(slugs)} 篇")

    if problems:
        print(f"检查未通过，共 {len(problems)} 项：")
        for item in problems:
            print("  -", item)
        return 1

    print(f"检查通过：{len(docs)} 篇文档、{len(pages)} 个页面、单文件 section {len(slugs) + 2} 个。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
