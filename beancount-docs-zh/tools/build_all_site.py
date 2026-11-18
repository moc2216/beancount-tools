#!/usr/bin/env python3
"""Build the full Chinese Beancount docs site from the translation manifest."""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parents[1]
ZH = ROOT / "zh"
SITE = ROOT / "site"
SRC = ROOT / "source" / "docs"
MANIFEST = ROOT / "translation-manifest.json"
STATE = ROOT / "translation-state.json"

GROUPS = [
    ("入门 / 安装 / 运行", [
        "beancount-user-manual", "getting-started-with-beancount", "installing-beancount",
        "installing-beancount-v3", "running-beancount-and-generating-reports",
    ]),
    ("语言 / 查询", [
        "beancount-language-syntax", "beancount-options-reference",
        "beancount-cheat-sheet", "beancount-query-language",
    ]),
    ("会计方法 / 校验", [
        "the-double-entry-counting-method", "command-line-accounting-in-context",
        "command-line-accounting-cookbook", "balance-assertions-in-beancount",
        "precision-tolerances", "rounding-precision-in-beancount",
        "settlement-dates-in-beancount", "tutorial-example",
    ]),
    ("投资账本", [
        "how-inventories-work", "trading-with-beancount",
        "calculating-portfolio-returns", "fetching-prices-in-beancount",
        "stock-vesting-in-beancount",
    ]),
    ("导入 / 插件", [
        "importing-external-data", "beancount-scripting-plugins",
    ]),
    ("架构 / 版本", [
        "beancount-design-doc", "beancount-v3", "beancount-v3-dependencies",
        "beangulp-design-doc-for-new-repo", "ledgerhub-design-doc",
        "a-proposal-for-an-improvement-on-inventory-booking",
    ]),
    ("对比 / 导出 / 社区", [
        "a-comparison-of-beancount-and-ledger-hledger", "exporting-your-portfolio",
        "external-contributions",
    ]),
    ("专题建模", [
        "fund-accounting-with-beancount", "health-care-expenses",
        "how-we-share-expenses", "sharing-expenses-with-beancount",
        "tracking-medical-claims",
    ]),
    ("历史", ["beancount-history-and-credits"]),
]

PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} · Beancount 中文文档</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="{title} · Beancount 中文文档">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="article">
  <link rel="icon" href="{icon}">
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="index.html">Beancount 中文文档 <span>译文</span></a>
      <div class="tagline">{subtitle}</div>
    </div>
  </header>
  <div class="layout">
    <aside class="sidebar">{sidebar}</aside>
    <main>
      <article>
        <div class="backlink"><a id="backlink" href="{parent}" data-parent="{parent}">← 返回分类</a></div>
        <div class="article-meta">
          <span class="badge">译文</span>
          <span>原文作者：Martin Blais</span>
          <a href="{source}" target="_blank" rel="noreferrer">查看原文 ↗</a>
        </div>
        {stale_notice}
        {body}
      </article>
    </main>
  </div>
  <footer class="page-footer">Beancount 中文文档 · 非官方译文 · 原文 © Martin Blais / beancount/docs contributors · MIT License</footer>
  <script src="assets/nav.js"></script>
</body>
</html>
"""

INDEX = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Beancount 中文文档</title>
  <meta name="description" content="{desc}">
  <meta property="og:title" content="Beancount 中文文档">
  <meta property="og:description" content="{desc}">
  <meta property="og:type" content="website">
  <link rel="icon" href="{icon}">
  <link rel="stylesheet" href="assets/style.css">
</head>
<body>
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="index.html">Beancount 中文文档 <span>译文</span></a>
      <div class="tagline">全量正文 · {count} 篇</div>
    </div>
  </header>
  <div class="layout">
    <aside class="sidebar">
      <p class="sidebar-label">目录</p>
      <nav class="toc">{nav}</nav>
    </aside>
    <main>
      <article>
        <div class="article-meta">
          <span class="badge">译文</span>
          <span>MTPLX Qwen3.8-27B</span>
          <span>术语保留英文 · 代码原样</span>
        </div>
        <h1>Beancount 中文文档</h1>
        <p>本页是官方 <code>beancount/docs</code> 正文的全量中文译文，共 39 篇。除 API reference 外，正文页面已全部覆盖。</p>
        <p><strong>说明：</strong>这是非官方译文，不是人工定稿。代码、account、option、币种已尽量原样保留；术语按约定保留英文。建议按主题选读，再对关键章节人工审校。</p>
        {sections}
      </article>
    </main>
  </div>
  <footer class="page-footer">Beancount 中文文档 · 非官方译文 · 原文 © Martin Blais / beancount/docs contributors · MIT License</footer>
</body>
</html>
"""


def load_manifest() -> list[dict]:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def load_state() -> dict:
    if not STATE.exists():
        return {"docs": {}}
    return json.loads(STATE.read_text(encoding="utf-8"))


def slug_map(rows: list[dict]) -> dict[str, str]:
    mapping = {}
    for row in rows:
        mapping[row["slug"]] = row["slug"] + ".html"
        mapping[Path(row["source"]).stem] = row["slug"] + ".html"
    return mapping


def rewrite_links(body: str, mapping: dict[str, str]) -> str:
    body = body.replace('href="../NOTICE.md"', 'href="notice.html"')
    body = body.replace('href="NOTICE.md"', 'href="notice.html"')

    def repl(match: re.Match) -> str:
        target = match.group(1)
        base = Path(target).name
        if base.endswith(".md"):
            key = base[:-3]
            if key in mapping:
                return 'href="%s"' % mapping[key]
        return match.group(0)

    return re.sub(r'href="([^"]+)"', repl, body)


def copy_media(row: dict) -> None:
    stem = Path(row["source"]).stem
    dst = SITE / "assets" / "images" / row["slug"]
    # 优先用 zh/ 内的镜像，保证没有 source/ 也能构建；旧布局再回退到 source/。
    candidates = [ROOT / "zh" / row["slug"] / "media", SRC / stem / "media"]
    src = next((c for c in candidates if c.is_dir()), None)
    if src is None:
        return
    dst.mkdir(parents=True, exist_ok=True)
    for f in src.iterdir():
        if f.is_file():
            shutil.copy2(f, dst / f.name)


def rewrite_media(body: str, row: dict) -> str:
    stem = Path(row["source"]).stem
    body = body.replace(f'src="{stem}/media/', f'src="assets/images/{row["slug"]}/')
    body = body.replace(f'src="../{stem}/media/', f'src="assets/images/{row["slug"]}/')
    body = body.replace(f'src="{row["slug"]}/media/', f'src="assets/images/{row["slug"]}/')
    return body


def render(text: str) -> tuple[str, str]:
    md = markdown.Markdown(
        extensions=["extra", "toc", "sane_lists", "footnotes", "fenced_code", "tables"],
        extension_configs={"toc": {"toc_depth": "2-3", "permalink": False}},
    )
    body = md.convert(text)
    toc = re.sub(r'^<div class="toc">\s*', "", md.toc)
    toc = re.sub(r"\s*</div>\s*$", "", toc)
    return body, toc


ICON = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='7' fill='%230d5c4f'/%3E"
    "%3Ctext x='16' y='23' font-size='17' text-anchor='middle' fill='%23ffffff'"
    " font-family='serif'%3E%E8%B4%9D%3C/text%3E%3C/svg%3E"
)


def describe(body: str) -> str:
    """从正文第一个段落生成 meta description（跳过标题与译文说明块）。"""
    tail = re.sub(r"<blockquote>.*?</blockquote>", "", body.split("</h1>", 1)[-1], flags=re.S)
    for para in re.findall(r"<p>(.*?)</p>", tail, re.S):
        text = re.sub(r"<[^>]+>", "", para)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) < 20 or text.startswith(("非官方", "原文：", "原文:", "面向", "样章")):
            continue
        cut = text[:120]
        end = max(cut.rfind("。"), cut.rfind("；"))
        if end >= 40:
            cut = cut[: end + 1]
        return html.escape(cut.rstrip("，、,;"))
    return "Beancount 官方文档正文的非官方中文译文。"


def find_group(slug: str):
    for index, (name, slugs) in enumerate(GROUPS, start=1):
        if slug in slugs:
            return index, name, slugs
    return None


def build_sidebar(row: dict, by_slug: dict[str, dict], toc: str) -> str:
    current = find_group(row["slug"])
    parts = ['<p class="sidebar-label">目录</p>', '<nav class="tree">']
    for index, (name, slugs) in enumerate(GROUPS, start=1):
        present = [by_slug[s] for s in slugs if s in by_slug and by_slug[s].get("status") == "done"]
        if not present:
            continue
        if current and current[0] == index:
            parts.append(
                f'<div class="group current"><div class="group-title">'
                f'<span class="chev">▾</span> {html.escape(name)} '
                f'<span class="count">{len(present)}</span></div><ul>'
            )
            for item in present:
                active = ' class="active"' if item["slug"] == row["slug"] else ""
                parts.append(
                    f'<li{active}><a href="{item["slug"]}.html">'
                    f'{html.escape(item["title"])}</a></li>'
                )
            parts.append("</ul></div>")
        else:
            parts.append(
                f'<div class="group collapsed"><div class="group-title">'
                f'<span class="chev">▸</span> '
                f'<a href="index.html#group-{index:02d}">{html.escape(name)}</a> '
                f'<span class="count">{len(present)}</span></div></div>'
            )
    parts.append("</nav>")
    parts.append('<div class="local-toc"><p class="sidebar-label">On this page</p>')
    parts.append(toc)
    parts.append("</div>")
    return "\n".join(parts)


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    rows = load_manifest()
    state = load_state()
    by_slug = {r["slug"]: r for r in rows}
    mapping = slug_map(rows)
    done = [r for r in rows if r.get("status") == "done"]
    print("done docs", len(done))

    for row in done:
        copy_media(row)
        path = ZH / (row["slug"] + ".md")
        if not path.exists():
            print("MISSING", path)
            continue
        body, toc = render(path.read_text(encoding="utf-8"))
        body = rewrite_media(rewrite_links(body, mapping), row)
        group = find_group(row["slug"])
        parent = f"index.html#group-{group[0]:02d}" if group else "index.html"
        sidebar = build_sidebar(row, by_slug, toc)
        status = state.get("docs", {}).get(row["slug"], {}).get("status")
        stale_notice = (
            '<div class="note"><strong>原文已有更新。</strong> '
            "当前译文尚未同步，请先运行更新流程并复核这一篇。</div>"
            if status and status != "current"
            else ""
        )
        page = PAGE.format(
            title=html.escape(row["title"]),
            subtitle=html.escape(row["slug"]),
            source=html.escape(row["source_url"]),
            parent=parent,
            sidebar=sidebar,
            stale_notice=stale_notice,
            body=body,
            desc=describe(body),
            icon=ICON,
        )
        (SITE / (row["slug"] + ".html")).write_text(page, encoding="utf-8")
        print("built", row["slug"])

    nav = []
    sections = []
    for group_index, (group, slugs) in enumerate(GROUPS, start=1):
        present = [by_slug[s] for s in slugs if s in by_slug and by_slug[s].get("status") == "done"]
        if not present:
            continue
        group_id = f"group-{group_index:02d}"
        nav.append(f'<li><a href="#{group_id}">{html.escape(group)}</a></li>')
        sections.append(f'<h2 id="{group_id}">{html.escape(group)}</h2>')
        sections.append("<ul>")
        for row in present:
            sections.append(
                f'<li><a href="{row["slug"]}.html">{html.escape(row["title"])}</a></li>'
            )
        sections.append("</ul>")

    index = INDEX.format(
        nav="\n".join(nav),
        sections="\n".join(sections),
        count=len(rows),
        desc="Beancount 官方文档正文的非官方中文译文，共 %d 篇，含语言语法、查询、精度与 tolerance、投资账本、导入插件等主题。" % len(rows),
        icon=ICON,
    )
    (SITE / "index.html").write_text(index, encoding="utf-8")
    print("built site/index.html")


if __name__ == "__main__":
    main()
