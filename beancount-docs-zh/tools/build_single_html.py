#!/usr/bin/env python3
"""Build one self-contained HTML file containing the whole translated site."""

from __future__ import annotations

import argparse
import base64
import html
import json
import mimetypes
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_all_site import ICON  # noqa: E402

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
    ("导入 / 插件", ["importing-external-data", "beancount-scripting-plugins"]),
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


def extract_article(page: Path) -> str:
    text = page.read_text(encoding="utf-8")
    match = re.search(r"<article>(.*?)</article>", text, re.S)
    if not match:
        raise ValueError(f"no article in {page}")
    body = match.group(1)
    body = re.sub(r'<div class="backlink">.*?</div>\s*', "", body, flags=re.S)
    return body.strip()


def embed_images(body: str, site: Path) -> str:
    def repl(match: re.Match) -> str:
        src = match.group(1)
        if src.startswith(("http://", "https://", "data:")):
            return match.group(0)
        path = (site / src).resolve()
        if not path.exists():
            return match.group(0)
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return f'src="data:{mime};base64,{data}"'

    return re.sub(r'src="([^"]+)"', repl, body)


def prefix_ids(body: str, prefix: str) -> str:
    return re.sub(r'\bid="([^"]+)"', lambda m: f'id="{prefix}-{m.group(1)}"', body)


def rewrite_links(body: str, slug: str, page_slugs: dict[str, str]) -> str:
    # Cross-page links, preserving fragment by prefixing it.
    def page_repl(match: re.Match) -> str:
        target = match.group(1)
        frag = match.group(2) or ""
        if target == "index":
            return f'href="#home{frag}"' if frag else 'href="#home"'
        if target == "notice":
            return 'href="#notice"'
        if target in page_slugs:
            target_slug = page_slugs[target]
            return f'href="#doc-{target_slug}{frag}"' if frag else f'href="#doc-{target_slug}"'
        return match.group(0)

    body = re.sub(r'href="([^"/#]+)\.html(#[^"]*)?"', page_repl, body)
    body = body.replace('href="../NOTICE.md"', 'href="#notice"')
    body = body.replace('href="NOTICE.md"', 'href="#notice"')

    # Same-page fragments (but not already rewritten shell links).
    def same_repl(match: re.Match) -> str:
        frag = match.group(1)
        if frag.startswith(("doc-", "home", "notice")):
            return match.group(0)
        return f'href="#{slug}-{frag}"'

    return re.sub(r'href="#([^"]+)"', same_repl, body)


def build_tree(manifest: dict[str, dict], current: str = "home") -> str:
    parts = ['<p class="sidebar-label">目录</p>', '<nav class="tree">']
    for group, slugs in GROUPS:
        present = [s for s in slugs if s in manifest]
        if not present:
            continue
        parts.append("<details open>")
        parts.append(f"<summary>{html.escape(group)}</summary>")
        parts.append("<ul>")
        for slug in present:
            title = manifest[slug].get("title", slug)
            parts.append(f'<li><a class="nav-link" href="#doc-{slug}">{html.escape(title)}</a></li>')
        parts.append("</ul></details>")
    parts.append("</nav>")
    return "\n".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--out", default="Beancount中文文档-单文件.html")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    site = root / "site"
    manifest = json.loads((root / "translation-manifest.json").read_text(encoding="utf-8"))
    rows = [r for r in manifest if r.get("status") == "done"]
    by_slug = {r["slug"]: r for r in rows}
    page_slugs = {r["slug"]: r["slug"] for r in rows}

    css = (site / "assets" / "style.css").read_text(encoding="utf-8")
    extra_css = """
    .doc-section[hidden] { display: none; }
    .sidebar details { margin: 0 0 8px; }
    .sidebar summary { cursor: pointer; font-weight: 650; color: var(--ink); padding: 4px 0; }
    .sidebar summary::marker { color: var(--muted); }
    .sidebar details ul { list-style: none; margin: 4px 0 4px 17px; padding: 0; border-left: 1px solid var(--line); }
    .sidebar details li { margin: 1px 0; }
    .sidebar details a { display: block; padding: 3px 8px; color: var(--muted); border-bottom: 0; border-radius: 6px; line-height: 1.45; }
    .sidebar details a:hover { color: var(--accent); background: #f1f7f4; }
    .sidebar details a.active { color: #084d42; background: var(--accent-soft); font-weight: 600; }
    .single-note { font-size: 12px; color: var(--muted); margin-top: 16px; }
    .search-box { margin: 0 0 14px; }
    .search-box input { width: 100%; box-sizing: border-box; padding: 7px 9px; font-size: 13px;
      border: 1px solid var(--line); border-radius: 7px; background: #fff; color: var(--ink); }
    .search-box input:focus { outline: 2px solid var(--accent-soft); border-color: var(--accent); }
    .hits { list-style: none; margin: 0 0 14px; padding: 0; max-height: 46vh; overflow-y: auto; }
    .hits li { margin: 0 0 2px; }
    .hits a { display: block; padding: 5px 8px; border-radius: 6px; border-bottom: 0; font-size: 12.5px;
      line-height: 1.45; color: var(--ink); }
    .hits a:hover { background: #f1f7f4; }
    .hits .hit-doc { display: block; font-size: 11px; color: var(--muted); letter-spacing: .02em; }
    .hits mark { background: #fff2b8; color: inherit; padding: 0 1px; }
    .hits .hit-empty { font-size: 12px; color: var(--muted); padding: 5px 8px; }
    """

    sections = []
    home = extract_article(site / "index.html")
    home = prefix_ids(home, "home")
    home = embed_images(rewrite_links(home, "home", page_slugs), site)
    sections.append(f'<section class="doc-section" id="home">{home}</section>')

    for row in rows:
        slug = row["slug"]
        body = extract_article(site / f"{slug}.html")
        body = prefix_ids(body, slug)
        body = embed_images(rewrite_links(body, slug, page_slugs), site)
        sections.append(f'<section class="doc-section" id="doc-{slug}">{body}</section>')

    notice = extract_article(site / "notice.html")
    notice = prefix_ids(notice, "notice")
    notice = embed_images(rewrite_links(notice, "notice", page_slugs), site)
    sections.append(f'<section class="doc-section" id="notice">{notice}</section>')

    tree = build_tree(by_slug)
    page = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Beancount 中文文档 · 单文件</title>
<meta name="description" content="Beancount 官方文档正文的非官方中文译文，39 篇合订为一个可离线阅读的 HTML 文件。">
<link rel="icon" href="{ICON}">
<style>{css}\n{extra_css}</style>
</head>
<body>
<header class="site-header">
  <div class="header-inner">
    <a class="brand" href="#home">Beancount 中文文档 <span>单文件</span></a>
    <div class="tagline">39 篇正文 · 一个 HTML</div>
  </div>
</header>
<div class="layout">
  <aside class="sidebar">
    <div class="search-box">
      <input id="q" type="search" placeholder="搜索标题与正文…" autocomplete="off" aria-label="搜索文档">
    </div>
    <ul class="hits" id="hits" hidden></ul>
    {tree}
    <div class="single-note">这是自包含 HTML：CSS、图片、正文都已内嵌，不需要旁边的 assets 文件夹。</div>
  </aside>
  <main>
    {''.join(sections)}
  </main>
</div>
<footer class="page-footer">非官方译文 · 原文 © Martin Blais / beancount/docs contributors · MIT License</footer>
<script>
(function () {{
  function show(id) {{
    var target = document.getElementById(id);
    if (!target) return;
    var section = target.closest('.doc-section');
    if (!section) section = document.getElementById('home');
    document.querySelectorAll('.doc-section').forEach(function (s) {{
      s.hidden = s !== section;
    }});
    document.querySelectorAll('.nav-link').forEach(function (a) {{
      a.classList.toggle('active', a.getAttribute('href') === '#' + section.id);
    }});
    if (target !== section) target.scrollIntoView();
    else window.scrollTo(0, 0);
  }}
  function route() {{
    var id = location.hash ? location.hash.slice(1) : 'home';
    show(id);
  }}
  window.addEventListener('hashchange', route);
  route();

  // 离线全文搜索：首次输入时建立索引，之后只做子串匹配。
  var index = null;
  var hits = document.getElementById('hits');
  var input = document.getElementById('q');

  function esc(s) {{
    return s.replace(/[&<>"]/g, function (c) {{
      return {{ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }}[c];
    }});
  }}

  function buildIndex() {{
    var items = [];
    document.querySelectorAll('.doc-section').forEach(function (section) {{
      var docName = section.id === 'home' ? '首页'
        : (section.id === 'notice' ? '版权说明' : '');
      section.querySelectorAll('h1,h2,h3,h4,p,li,td,pre').forEach(function (el) {{
        var id = el.id || (el.closest('[id]') || {{}}).id;
        if (!id) return;
        var text = (el.textContent || '').replace(/\\s+/g, ' ').trim();
        if (!text) return;
        items.push({{ id: id, text: text, doc: docName, head: /^H[1-4]$/.test(el.tagName) }});
      }});
    }});
    return items;
  }}

  function snippet(text, at, q) {{
    var start = Math.max(0, at - 40);
    var end = Math.min(text.length, at + q.length + 60);
    var before = (start > 0 ? '…' : '') + text.slice(start, at);
    var hit = text.slice(at, at + q.length);
    var after = text.slice(at + q.length, end) + (end < text.length ? '…' : '');
    return esc(before) + '<mark>' + esc(hit) + '</mark>' + esc(after);
  }}

  var docTitles = {{}};
  document.querySelectorAll('.nav-link').forEach(function (a) {{
    var id = (a.getAttribute('href') || '').slice(1);
    if (id) docTitles[id] = a.textContent.trim();
  }});

  function search() {{
    var q = input.value.trim().toLowerCase();
    hits.innerHTML = '';
    if (q.length < 1) {{ hits.hidden = true; return; }}
    if (!index) index = buildIndex();
    // 标题命中优先，其次正文命中。
    var out = [];
    for (var pass = 0; pass < 2 && out.length < 30; pass++) {{
      for (var i = 0; i < index.length && out.length < 30; i++) {{
        var it = index[i];
        if (Boolean(it.head) !== (pass === 0)) continue;
        var at = it.text.toLowerCase().indexOf(q);
        if (at < 0) continue;
        out.push({{ it: it, at: at }});
      }}
    }}
    if (!out.length) {{
      hits.innerHTML = '<li class="hit-empty">没有匹配项</li>';
      hits.hidden = false;
      return;
    }}
    out.forEach(function (o) {{
      var section = document.getElementById(o.it.id);
      var sec = section ? section.closest('.doc-section') : null;
      var name = (sec && docTitles[sec.id]) || {{ home: '首页', notice: '版权说明' }}[(sec || {{}}).id] || '文档';
      var li = document.createElement('li');
      li.innerHTML = '<a href="#' + esc(o.it.id) + '"><span class="hit-doc">' + esc(name)
        + '</span>' + snippet(o.it.text, o.at, input.value.trim()) + '</a>';
      li.querySelector('a').addEventListener('click', function () {{
        hits.hidden = true;
      }});
      hits.appendChild(li);
    }});
    hits.hidden = false;
  }}

  var timer;
  input.addEventListener('input', function () {{
    clearTimeout(timer);
    timer = setTimeout(search, 120);
  }});
  input.addEventListener('keydown', function (e) {{
    if (e.key === 'Escape') {{ input.value = ''; hits.hidden = true; hits.innerHTML = ''; }}
    if (e.key === 'Enter') {{
      var first = hits.querySelector('a');
      if (first) {{ location.hash = first.getAttribute('href'); hits.hidden = true; }}
    }}
  }});
  document.addEventListener('keydown', function (e) {{
    if ((e.metaKey || e.ctrlKey) && (e.key === 'k' || e.key === 'K')) {{
      e.preventDefault();
      input.focus();
      input.select();
    }}
  }});
}})();
</script>
</body>
</html>
"""
    out = root / args.out
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
