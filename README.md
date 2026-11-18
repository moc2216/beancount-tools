# Beancount 中文文档与工具

[![docs check](https://github.com/moc2216/beancount-tools/actions/workflows/beancount-docs-zh.yml/badge.svg)](https://github.com/moc2216/beancount-tools/actions/workflows/beancount-docs-zh.yml)
[![pages](https://github.com/moc2216/beancount-tools/actions/workflows/pages.yml/badge.svg)](https://moc2216.github.io/beancount-tools/)

把 Beancount 官方文档翻译成中文，并附一个把微信 / 支付宝账单转成 Beancount 条目的个人工具。

**在线阅读：<https://moc2216.github.io/beancount-tools/>**

## 仓库内容

| 目录 | 是什么 |
|---|---|
| [`beancount-docs-zh/`](beancount-docs-zh/) | 官方 `beancount/docs` 正文的**非官方中文译文**，39 篇；含静态站点、离线单文件 HTML、构建与校验脚本 |
| [`beancount-importer账单导入工具/`](beancount-importer账单导入工具/) | 把微信支付、支付宝导出的账单 CSV 转成 Beancount 条目的个人脚本 |

## 文档：三种读法

| 方式 | 适合 | 入口 |
|---|---|---|
| 在线网页 | 手机上随手查、按主题浏览 | <https://moc2216.github.io/beancount-tools/> |
| 单文件 HTML | 离线保存、发给别人 | [`Beancount中文文档-单文件.html`](beancount-docs-zh/Beancount中文文档-单文件.html)，约 8 MB，图片与样式已内嵌，自带全文搜索（`Ctrl/Cmd + K`） |
| Markdown | 喂给 AI Agent、做二次加工 | [`beancount-docs-zh/zh/`](beancount-docs-zh/zh/)，39 个文件，一篇一个 |

给 Agent 的入口文档：[`AGENT-GUIDE.md`](beancount-docs-zh/AGENT-GUIDE.md)、[`INDEX.md`](beancount-docs-zh/INDEX.md)、[`GLOSSARY.md`](beancount-docs-zh/GLOSSARY.md)。

### 覆盖范围

| 分类 | 篇数 |
|---|---|
| 入门 / 安装 / 运行 | 5 |
| 语言 / 查询 | 4 |
| 会计方法 / 校验 | 8 |
| 投资账本 | 5 |
| 导入 / 插件 | 2 |
| 架构 / 版本 | 6 |
| 对比 / 导出 / 社区 | 3 |
| 专题建模 | 5 |
| 历史 | 1 |

不含 API reference，那部分保持英文。

### 翻译约定

- 中文为主，术语保留英文：`transaction`、`posting`、`directive`、`account`、`balance assertion`、`tolerance`、`precision`、`interpolation`、`cost`、`price`、`lot`、`booking`、`pad`
- 代码、account 名、option 名、货币代码原样不动
- 这是**非官方译文**，不是人工定稿；涉及版本行为请回到原文或实际运行 `bean-check` 核对

## 本地构建

```bash
cd beancount-docs-zh
pip install -r requirements.txt

python3 tools/update_docs.py build     # 生成 site/ 与单文件 HTML
python3 tools/qa_corpus.py --strict    # 语料体检
python3 tools/check_site.py            # 产物、锚点、图片、sitemap 校验
```

`source/`（官方 Git 底本）不随仓库提交。需要同步上游时：

```bash
python3 tools/update_docs.py pull      # 拉取上游并更新 translation-state.json
python3 tools/update_docs.py mark      # 标记受影响的译文
python3 tools/update_docs.py sync      # 重新构建
```

维护流程见 [`beancount-docs-zh/README.md`](beancount-docs-zh/README.md)。

## 账单导入工具

把微信 / 支付宝导出的账单 CSV 解析成 Beancount 条目，按自定义规则分配 account。

```bash
cd beancount-importer账单导入工具
# 把账单文件放进项目目录，然后：
python3 -m src.main
```

- 必须从项目目录以模块方式运行；`python3 src/main.py` 会因 `No module named 'src'` 失败
- 输出是同目录下的 `wechat_transaction.bean` 与运行日志
- 末尾会调用可选的 `bh format` 格式化工具；没装 `bh` 只会提示 command not found，不影响生成结果
- 自定义 account：[`src/custom/custom_accounts.py`](beancount-importer账单导入工具/src/custom/custom_accounts.py)
- 自定义分类规则：[`src/custom/custom_rules.py`](beancount-importer账单导入工具/src/custom/custom_rules.py)
- 仓库里的 `微信支付账单(...).csv` 是脱敏测试样本，不是真实消费记录

## 自动化

| Workflow | 做什么 |
|---|---|
| `beancount-docs-zh` | 语料体检 → 重新构建 → 产物自洽检查 → 生成文件必须与提交一致 |
| `pages` | 同上，并把 `beancount-docs-zh/site` 部署到 GitHub Pages |

当前基线：结构性问题 0，失效链接 0，图片缺失 0；术语译法混用 17 处，待人工复核。

## 许可与免责

- 原文与图片：© Martin Blais / `beancount/docs` contributors，MIT License
- 中文译文：非官方 derivative work，按 MIT 分发，仅供学习参考
- 本站与 Beancount 官方无关，不要把它当作官方文档引用
- 详见 [`NOTICE.md`](beancount-docs-zh/NOTICE.md)

## 反馈

- 译文错误、术语不统一、某段读不懂：欢迎开 issue，附上文件路径和原文段落
- 导入工具的问题：请说明账单来源（微信 / 支付宝）和报错信息，不要贴真实账单内容
