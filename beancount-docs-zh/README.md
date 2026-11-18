# Beancount 中文文档

> 本目录是 `beancount-tools` 的翻译文档子项目。为了保持仓库精简，`source/`（官方 Git 底本）不随仓库提交；需要同步上游时，按下方“上游更新 / 维护”先 clone 到 `source/`。

官方 `beancount/docs` 正文的全量非官方译文，共 **39 篇**。除 API reference 外，正文页面已全部覆盖。

- 单文件版：`Beancount中文文档-单文件.html`（可直接下载/打开）
- 全站索引：`site/index.html`
- 中文 Markdown：`zh/`
- Agent 使用指南：`AGENT-GUIDE.md`
- 文档索引：`INDEX.md`
- 术语表：`GLOSSARY.md`
- 翻译模型：MTPLX Qwen3.8-27B（thinking off）
- 翻译约定：中文为主；`transaction`、`posting`、`directive`、`account`、`balance assertion`、`tolerance`、`precision`、`interpolation`、`cost`、`price`、`lot`、`booking`、`pad` 等术语保留英文；代码、account、option、币种原样保留。

## 覆盖范围

- 入门 / 安装 / 运行
- 语言 / 查询
- 会计方法 / 校验
- 投资账本
- 导入 / 插件
- 架构 / 版本
- 对比 / 导出 / 社区
- 专题建模
- 历史

不包含：

- API reference（`beancount.core`、`loader`、`ops`、`parser`、`plugins`、`scripts`、`tools`、`utils`）
- `README.md`、`CONTRIBUTING.md`、脚本、评论工具

## 说明

- 这是非官方译文，不是人工定稿。建议先按主题选读，再对关键章节做术语、代码和语义审校。
- 代码块、account 名、option 名、货币代码已尽量原样保留；仍建议对关键账本示例运行 `bean-check` 验证。
- 全量翻译过程中出现过 MTPLX 的 `HTTP 507` 和占位符问题；已通过重启服务、缩小 chunk、重试解决，39 篇均有输出。
- 外部贡献文档的项目索引来自原文链接与 GitHub API 元数据；非 GitHub 页面未逐个深读。

## 构建

```bash
python3 tools/build_all_site.py
```

或启动本地服务器：

```bash
python3 -m http.server 8765 --bind 127.0.0.1
# http://127.0.0.1:8765/site/index.html
```

## 语料体检

```bash
python3 tools/qa_corpus.py --top 10
```

只读检查：误成代码块的正文行、无中文标题、未闭合围栏、术语混用。

## 持续集成

仓库根目录的 `.github/workflows/beancount-docs-zh.yml` 在每次改动本目录时运行：

1. `python tools/qa_corpus.py --strict` — 结构性问题（误成代码块的正文、无中文标题、未闭合围栏、图片缺失）会直接失败；术语混用只提示。
2. `python tools/update_docs.py build` — 重新生成 `site/` 与单文件 HTML。
3. `python tools/check_site.py` — 校验产物齐全、锚点、页面链接、图片、单文件 section 数。
4. `git diff --exit-code` — 生成文件必须与提交内容一致。

本地一次跑完：

```bash
python3 tools/qa_corpus.py --strict
python3 tools/update_docs.py build
python3 tools/check_site.py
git diff --exit-code -- site zh Beancount中文文档-单文件.html translation-manifest.json
```

## 上游更新 / 维护

`site/` 是生成产物，不要直接改；要改内容请改 `zh/`，然后重新构建。

`source/` 是官方 `beancount/docs` 的 Git clone（不随仓库提交），`translation-state.json` 记录每篇译文对应的上游文件 hash 和状态。

```bash
# 查看当前状态和 stale 文档
python3 tools/update_docs.py status

# 只检查上游有没有变化，不写文件
python3 tools/update_docs.py check

# 拉取上游更新，并把变化的译文标为 stale
python3 tools/update_docs.py pull

# 翻译 stale 文档后，标记为 current
python3 tools/update_docs.py mark <slug>

# 重建 HTML + 修链接
python3 tools/update_docs.py build

# 一步完成 pull + build
python3 tools/update_docs.py sync
```

更新报告会写到 `update-report.md`。如果某篇译文对应的上游文档变了，页面顶部会出现“原文已有更新，当前译文尚未同步”的提示，直到你翻译并 `mark` 它。

`pull` 只更新 `source/` 和状态，不会自动覆盖 `zh/`，所以人工修改不会被机器译文冲掉。

## 许可

官方 `beancount/docs` 仓库为 MIT License。本目录中的中文译稿仅用于个人学习；如要公开发布，请保留上游版权与许可声明。
