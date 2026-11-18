# Agent 使用指南

本目录是 Beancount 官方文档的**非官方中文翻译**，用于人类阅读和 AI Agent 检索/学习。

## 先读什么

1. `INDEX.md` — 39 篇文档的分类、路径和阅读顺序。
2. `GLOSSARY.md` — 术语表；本项目的核心约定是**技术术语保留英文**。
3. 具体文档 — 优先读 `zh/<slug>.md`；网页版在 `site/<slug>.html`。

## 语料状态

- 范围：官方 `beancount/docs` 正文 39 篇；不含 API reference。
- 上游快照：`0db55f6b29156653d626396f77338d7b135888da`（2026-04-20 站点构建）。
- 译文：MTPLX Qwen3.8-27B 生成的初稿，经过结构、链接与占位符检查。
- 这不是官方文档，也不是人工定稿。

## 给 Agent 的使用规则

- **术语不要改写**：`transaction`、`posting`、`directive`、`account`、`balance assertion`、`tolerance`、`precision`、`interpolation`、`cost`、`price`、`lot`、`booking`、`pad` 等保留英文。
- **代码不要重写**：account 名、option 名、货币代码、示例数字以原文为准。
- **先查 INDEX，再读单篇**：不要凭文件名猜内容。
- **涉及版本行为时查上游**：v2/v3、option 默认值、是否已实现，必须以当前 `beancount/docs` 或实际 `bean-check` 为准。
- **区分事实与译文**：译文可能有机器翻译误差；关键结论应回到 `source_url` 核对。

## 已知限制

- 机器翻译可能把 `balance check` 写成 `balance assertion`，或把 `tolerance` / `precision` 的细微差别合并。
- 少数代码块从上游缩进式变成了 fenced code；语义通常不变，但格式不完全一致。
- `beancount-options-reference` 已按 option 重排为 22 个独立小节，每节含示例与说明。
- 上游旧文档中有些“未实现”已过时；涉及版本行为时请回到当前上游或实际 `bean-check` 验证。
- 没有逐句人工审校；公开发布或用于高风险财务决策前应复核关键章节。

## 语料自检

```bash
python3 tools/qa_corpus.py --strict   # 结构性问题会失败
python3 tools/check_site.py           # 产物、锚点、图片、单文件
```

同一套检查在 GitHub Actions 中运行，见仓库根目录 `.github/workflows/beancount-docs-zh.yml`。

## 推荐重点复核

`beancount-language-syntax`、`beancount-options-reference`、`precision-tolerances`、`how-inventories-work`、`trading-with-beancount`、`calculating-portfolio-returns`。

## 许可

- 上游 `beancount/docs`：MIT License。
- 本项目代码与中文译文：MIT License，见 `LICENSE`。
- 上游版权与第三方内容见 `NOTICE.md`。

## 目录与资源

- 正文：`zh/<slug>.md`
- 该篇图片：`zh/<slug>/media/`，正文用相对路径 `<slug>/media/<file>` 引用
- 因此 `zh/` 单独拷走也能显示图片，不依赖 `site/` 或上游仓库
