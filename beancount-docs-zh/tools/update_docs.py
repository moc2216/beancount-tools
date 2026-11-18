#!/usr/bin/env python3
"""Minimal maintenance workflow for the Beancount Chinese docs.

Commands:
  status  show upstream/current commit and stale translations
  check   fetch upstream and list changed docs (no writes)
  pull    fast-forward source/ and mark changed translations stale
  build   rebuild HTML from zh/ and run link fixes
  sync    pull + build
  mark    mark one/all stale translations as current
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
MANIFEST = ROOT / "translation-manifest.json"
STATE = ROOT / "translation-state.json"
REPORT = ROOT / "update-report.md"


def run(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=SOURCE,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def git(*args: str, check: bool = True) -> str:
    return run("git", *args, check=check).stdout.strip()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def ensure_source() -> None:
    if not (SOURCE / ".git").exists():
        print(
            "source/ 中缺少上游 Git 仓库。请先在项目根目录运行：\n"
            "  git clone https://github.com/beancount/docs.git source"
        )
        sys.exit(2)


def manifest_rows() -> list[dict]:
    return load_json(MANIFEST)


def seed_state() -> dict:
    if STATE.exists():
        return load_json(STATE)
    docs = {}
    for row in manifest_rows():
        src = SOURCE / "docs" / row["source"]
        if not src.exists():
            continue
        docs[row["slug"]] = {
            "source": row["source"],
            "source_sha256": sha256(src),
            "status": "current",
        }
    state = {
        "source_commit": git("rev-parse", "HEAD"),
        "last_sync": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "docs": docs,
    }
    save_json(STATE, state)
    return state


def upstream_commit() -> str:
    return git("rev-parse", "origin/master")


def changed_docs(old: str, new: str) -> list[str]:
    if old == new:
        return []
    out = git("diff", "--name-only", old, new, "--", "docs")
    return [line for line in out.splitlines() if line.endswith(".md")]


def doc_slug_for_source(source_name: str, rows: list[dict]) -> str | None:
    for row in rows:
        if row["source"] == source_name:
            return row["slug"]
    return None


def mark_changes(state: dict, changed: list[str], new_commit: str) -> list[dict]:
    rows = manifest_rows()
    changed_rows = []
    for name in changed:
        slug = doc_slug_for_source(name, rows)
        if not slug:
            slug = Path(name).stem.replace("_", "-")
        entry = state["docs"].setdefault(
            slug,
            {"source": name, "source_sha256": "", "status": "missing"},
        )
        entry["source"] = name
        entry["status"] = "stale" if (ROOT / "zh" / f"{slug}.md").exists() else "missing"
        changed_rows.append({"slug": slug, "source": name, "status": entry["status"]})
    state["source_commit"] = new_commit
    state["last_sync"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return changed_rows


def write_report(state: dict, changed_rows: list[dict]) -> None:
    lines = [
        "# 上游更新报告",
        "",
        f"- 生成时间：{state['last_sync']}",
        f"- 当前 source commit：`{state['source_commit']}`",
        "",
        "## 本次变化的文档",
        "",
    ]
    if not changed_rows:
        lines.append("无变化。")
    else:
        lines += ["| slug | source | 状态 |", "|---|---|---|"]
        for item in changed_rows:
            lines.append(f"| `{item['slug']}` | `{item['source']}` | {item['status']} |")
        lines += [
            "",
            "## 下一步",
            "",
            "1. 只翻译状态为 `stale` / `missing` 的文档；",
            "2. 翻译后运行 `python3 tools/update_docs.py mark <slug>`；",
            "3. 运行 `python3 tools/update_docs.py build` 重建 HTML。",
        ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_status() -> None:
    ensure_source()
    state = seed_state()
    try:
        upstream = upstream_commit()
    except subprocess.CalledProcessError:
        upstream = "unknown (run check first)"
    stale = [slug for slug, item in state["docs"].items() if item.get("status") != "current"]
    print(f"source HEAD:   {git('rev-parse', 'HEAD')}")
    print(f"origin/master: {upstream}")
    print(f"last sync:     {state.get('last_sync', '')}")
    print(f"stale/missing: {len(stale)}")
    for slug in sorted(stale):
        print(f"  - {slug}: {state['docs'][slug].get('status')}")


def cmd_check() -> None:
    ensure_source()
    state = seed_state()
    print("fetching origin/master ...")
    run("git", "fetch", "origin", "master")
    old = state["source_commit"]
    new = upstream_commit()
    changed = changed_docs(old, new)
    print(f"current: {old[:12]}  upstream: {new[:12]}  changed docs: {len(changed)}")
    for name in changed:
        print("  -", name)
    if not changed:
        print("no upstream document changes.")


def cmd_pull() -> None:
    ensure_source()
    state = seed_state()
    run("git", "fetch", "origin", "master")
    old = state["source_commit"]
    new = upstream_commit()
    if old == new:
        print("already up to date.")
        write_report(state, [])
        return
    dirty = run("git", "status", "--porcelain", "--untracked-files=no", check=False).stdout.strip()
    if dirty:
        print("source has tracked local changes; refusing to pull:")
        print(dirty)
        sys.exit(1)
    run("git", "merge", "--ff-only", "origin/master")
    changed = changed_docs(old, new)
    changed_rows = mark_changes(state, changed, new)
    save_json(STATE, state)
    write_report(state, changed_rows)
    print(f"pulled {old[:12]} -> {new[:12]}; changed docs: {len(changed_rows)}")
    for item in changed_rows:
        print(f"  - {item['slug']} ({item['status']})")
    print(f"report: {REPORT}")


def cmd_build() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_all_site.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "tools" / "fix_site_links.py")], cwd=ROOT, check=True)
    subprocess.run([sys.executable, str(ROOT / "tools" / "build_single_html.py")], cwd=ROOT, check=True)
    print("built site/, fixed links, and rebuilt the single-file HTML.")


def cmd_mark(slug: str | None, all_: bool) -> None:
    ensure_source()
    state = seed_state()
    rows = manifest_rows()
    targets = []
    if all_:
        targets = [s for s, d in state["docs"].items() if d.get("status") != "current"]
    elif slug:
        targets = [slug]
    else:
        print("provide a slug or --all")
        sys.exit(1)
    for target in targets:
        entry = state["docs"].get(target)
        if not entry:
            print(f"unknown slug: {target}")
            continue
        src = SOURCE / "docs" / entry["source"]
        if not src.exists():
            print(f"source missing for {target}: {src}")
            continue
        entry["source_sha256"] = sha256(src)
        entry["status"] = "current"
        print(f"marked current: {target}")
    save_json(STATE, state)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status")
    sub.add_parser("check")
    sub.add_parser("pull")
    sub.add_parser("build")
    sub.add_parser("sync")
    p_mark = sub.add_parser("mark")
    p_mark.add_argument("slug", nargs="?")
    p_mark.add_argument("--all", action="store_true")
    args = parser.parse_args()

    if args.command == "status":
        cmd_status()
    elif args.command == "check":
        cmd_check()
    elif args.command == "pull":
        cmd_pull()
    elif args.command == "build":
        cmd_build()
    elif args.command == "sync":
        cmd_pull()
        cmd_build()
    elif args.command == "mark":
        cmd_mark(args.slug, args.all)


if __name__ == "__main__":
    main()
