#!/usr/bin/env python3
"""语料体检：只读检查 zh/ 下的译文格式与术语问题，不改文件。

用法：
    python3 tools/qa_corpus.py            # 全部检查
    python3 tools/qa_corpus.py --top 10   # 每类只列前 10 条

检查项：
    codeblock  4 空格缩进的正文行（会被 Markdown 当成代码块）
    heading    没有中文的标题
    fence      代码围栏数量为奇数
    mixed      同一篇里术语译法混用（如“余额断言”与 balance assertion）
    empty      空文件或几乎没有正文
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ZH = ROOT / "zh"

CJK = re.compile(r"[\u4e00-\u9fff\u3000-\u303f\uff00-\uffef]")
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
LIST_OR_CODE = re.compile(r"^\s{4,}(\S.*)$")

# 术语应保留英文；出现中文替代写法时提示，供人工判断。
TERMS = {
    "balance assertion": [r"余额断言", r"余额声明"],
    "posting": [r"分录条目"],
    "transaction": [r"交易记录(?!\w)"],
    "tolerance": [r"容差"],
    "precision": [r"精度"],
    "cost": [r"成本基础"],
}

# 按术语约定保留英文的标题，不算“无中文标题”。
TERM_HEADINGS = {
    "commodity", "account", "inventory", "flag", "posting", "directive",
    "transaction", "tag", "link", "metadata", "balance assertion", "holdings",
    "amount", "cost", "cost spec", "position", "realization", "pad", "note",
    "document", "price", "event", "query", "custom", "plugin", "include",
    "distinct", "parser", "cash flow", "padding", "equity", "precision",
    "inventory booking", "strict booking", "average booking",
}

DATE = re.compile(r"^\s*\d{4}-\d{1,2}-\d{1,2}\b")
DIRECTIVE = re.compile(
    r"^\s*(option|plugin|include|open|close|commodity|balance|pad|note|document|"
    r"price|event|query|custom|pushtag|poptag)\b"
)
CODE_HINT = re.compile(r"(->|<-|^\s*[/~.…]\S|^\s*[#;]\s|^\s*(bn\.|def |class |import |from |assert |sudo|brew|pip|git|apt|npm)\b)")


def is_code(line: str) -> bool:
    return bool("\t" in line or DATE.match(line) or DIRECTIVE.match(line) or CODE_HINT.search(line))


def check_codeblock(path: Path, text: str) -> list[str]:
    out: list[str] = []
    in_fence = False
    in_list = False
    for no, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not line.strip():
            continue
        if re.match(r"^\s*([-*+]|\d+\.)\s", line):
            in_list = True
            continue
        m = LIST_OR_CODE.match(line)
        if m and CJK.search(line) and not in_list and not is_code(line) and not line.strip().startswith("… "):
            out.append(f"{path.name}:{no}: {line.strip()[:60]}")
        if line and not line.startswith((" ", "\t")):
            in_list = False
    return out


def check_heading(path: Path, text: str) -> list[str]:
    out = []
    for no, line in enumerate(text.splitlines(), 1):
        m = HEADING.match(line)
        if m and not CJK.search(m.group(2)):
            plain = re.sub(r'<a id="[^"]*"></a>', "", m.group(2)).strip().lower()
            if plain in TERM_HEADINGS or plain.startswith("bean-") or plain.startswith("!["):
                continue
            out.append(f"{path.name}:{no}: {line.strip()[:70]}")
    return out


def check_fence(path: Path, text: str) -> list[str]:
    lines = [l for l in text.splitlines() if l.startswith("```")]
    return [f"{path.name}: 围栏 {len(lines)} 个（奇数）"] if len(lines) % 2 else []


def check_mixed(path: Path, text: str) -> list[str]:
    out = []
    for term, variants in TERMS.items():
        for v in variants:
            if re.search(v, text) and term.lower() in text.lower():
                out.append(f"{path.name}: 同时出现 `{term}` 与“{v}”")
    return out


def check_image(path: Path, text: str) -> list[str]:
    out = []
    for src in re.findall(r"!\[[^\]]*\]\(([^)\s]+)\)", text):
        if src.startswith(("http://", "https://")):
            continue
        if not (path.parent / src).exists():
            out.append(f"{path.name}: 图片不存在 {src}")
    return out


def check_empty(path: Path, text: str) -> list[str]:
    body = len(CJK.findall(text))
    return [f"{path.name}: 正文中文仅 {body} 字"] if body < 200 else []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument(
        "--strict",
        action="store_true",
        help="有结构性问题时以非零退出码结束（CI 用）。术语混用只提示，不判失败。",
    )
    args = ap.parse_args()

    files = sorted(ZH.glob("*.md"))
    if not files:
        print("zh/ 下没有 Markdown。")
        return

    results = {
        "codeblock": [],
        "heading": [],
        "fence": [],
        "mixed": [],
        "empty": [],
        "image": [],
    }
    for path in files:
        text = path.read_text(encoding="utf-8")
        results["codeblock"] += check_codeblock(path, text)
        results["heading"] += check_heading(path, text)
        results["fence"] += check_fence(path, text)
        results["mixed"] += check_mixed(path, text)
        results["empty"] += check_empty(path, text)
        results["image"] += check_image(path, text)

    print(f"文档数：{len(files)}\n")
    labels = {
        "codeblock": "疑似误成代码块的正文行",
        "heading": "无中文标题",
        "fence": "未闭合代码围栏",
        "mixed": "术语译法混用",
        "empty": "内容偏少",
        "image": "图片缺失",
    }
    for key, label in labels.items():
        items = results[key]
        print(f"[{label}] {len(items)}")
        for item in items[: args.top]:
            print("  " + item)
        if len(items) > args.top:
            print(f"  … 另有 {len(items) - args.top} 条")
        print()

    if args.strict:
        blocking = sum(len(results[k]) for k in ("codeblock", "heading", "fence", "image", "empty"))
        if blocking:
            print(f"严格模式：{blocking} 项结构性问题，退出码 1。")
            raise SystemExit(1)
        if results["mixed"]:
            print(f"提示：{len(results['mixed'])} 处术语译法混用，不阻塞（建议人工复核）。")


if __name__ == "__main__":
    main()
