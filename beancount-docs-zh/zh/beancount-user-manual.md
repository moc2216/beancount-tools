> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/index/

# Beancount 用户手册<a id="title"></a>

*这是所有与 Beancount 相关的文档的顶级页面。*

[http://furius.ca/beancount/doc/index](http://furius.ca/beancount/doc/index)

## 用户文档<a id="documentation-for-users"></a>

[命令行记账的背景：一篇说明性文档](command-line-accounting-in-context.md)，解释了什么是命令行记账，我*为什么*这样做，并通过一个简单的例子说明我*如何*操作。请将其作为入门阅读。

[复式记账法](the-double-entry-counting-method.md)：对复式记账法的温和介绍，其术语与命令行记账系统所做的假设和简化相兼容。

[安装 Beancount](installing-beancount.md)：在您的计算机上下载和安装的说明，以及软件发布信息。

[运行 Beancount 并生成报告](running-beancount-and-generating-reports.md)：如何运行 Beancount 可执行文件并生成 report。本文包含面向 Beancount 用户的技术信息。

[Beancount 入门](getting-started-with-beancount.md)：解释如何创建、初始化和组织输入文件的基本知识，以及声明 account 和添加 pad 指令的过程。

[Beancount 语言语法](beancount-language-syntax.md)：带有示例的语言语法完整描述。这是 Beancount 语言的主要参考。

[Beancount 选项参考](beancount-options-reference.md)：对所有可能选项值的描述和解释。

[精度与容差](precision-tolerances.md)：transaction 和 balance assertion 允许从上下文中推断出的少量不精确性（tolerance）。本文档解释了其工作原理。

[Beancount 查询语言](beancount-query-language.md)：对 bean-query 命令行客户端工具的高级概述，该工具允许您从 Beancount 账本文件中提取各种数据表。

[Beancount 速查表](beancount-cheat-sheet.md)：单页“速查表”，总结了 Beancount 语法。

[库存如何工作](how-inventories-work.md)：解释库存、其表示方式，以及 lot 如何与库存中持有的头寸进行匹配的详细信息。这是阅读交易文档的预备知识。

[导出您的投资组合](exporting-your-portfolio.md)：如何将您的投资组合导出到外部投资组合跟踪网站。

[教程与示例](tutorial-example.md)：一个现实的示例账本文件，包含假设的 Beancount 用户几年的财务生活。这可用于测试 Beancount，查看其 report 或 Web 界面的样子。这可以快速让您了解使用 Beancount 能获得什么。

[Beancount 邮件列表](https://groups.google.com/forum/#!forum/beancount)：特定于 Beancount 的问题和讨论发生在那里。相关的还有 [Ledger-CLI 论坛](https://groups.google.com/forum/#!forum/ledger-cli)，其中包含更多通用讨论，并作为命令行记账主题的元列表。

[Beancount 历史与致谢：](beancount-history-and-credits.md) 描述 Beancount 的开发历史，并向其贡献者致谢。

[Beancount 与 Ledger 及 HLedger 的比较](a-comparison-of-beancount-and-ledger-hledger.md)：命令行记账系统之间的定性功能比较。

[在 Beancount 中获取价格](fetching-prices-in-beancount.md)：如何使用 Beancount 的工具获取和维护您资产的 price 数据库。

[导入外部数据](importing-external-data.md)：描述从金融机构可下载的外部文件导入数据的过程，以及 Beancount 提供的用于自动化部分工作的工具和库。

## 食谱与示例<a id="cookbook-examples"></a>

*这些文档展示了如何使用复式记账法来完成特定任务。请利用这些文档来培养对如何构建你的 account 结构的直觉。*

[命令行记账食谱](command-line-accounting-cookbook.md)：关于如何记录各种不同类型 financial transaction 的示例。这无疑是建立对如何最佳使用复式记账法直觉的最好方式。

[使用 Beancount 进行交易](trading-with-beancount.md)：对交易损益（P/L）的解释，以及如何使用 Beancount 处理各种 investment 和交易场景的实例。这是食谱的补充。

[Beancount 中的股票归属](stock-vesting-in-beancount.md)：一个示例，展示了如何处理限制性股票单位（RSU）以及科技公司和初创公司常见的归属事件。

[使用 Beancount 分摊费用](sharing-expenses-with-beancount.md)：一个现实且详细的示例，展示了如何使用复式记账法与他人分摊旅行或项目的费用。

[我们如何分摊费用](how-we-share-expenses.md)：对一种持续系统的更详细描述，该系统用于 (a) 在双方都做出贡献的伴侣之间分摊费用，以及 (b) 向拥有自己账本的具体项目（我们的儿子）分摊费用。这描述了我们真实的系统。

[医疗费用](health-care-expenses.md)（未完成）：一份尚未完全完成的文档，解释了如何处理美国网络内和网络外提供者的医疗费用序列。

[追踪医疗索赔](tracking-medical-claims.md)：一个示例结构，用于追踪网络外心理治疗课程，包括自付费用、医疗索赔以及针对未覆盖部分的关联 HSA 报销。

[计算投资组合回报](calculating-portfolio-returns.md)：如何从 Beancount 账本中计算投资组合回报。这描述了在实验脚本中完成的工作，以及提取正确数据所涉及的过程。

## 开发者文档<a id="documentation-for-developers"></a>

[Beancount 脚本与插件](beancount-scripting-plugins.md)：一份指南，介绍如何编写脚本以在内存中加载账本内容并处理 directive，以及如何编写插件来转换它们。

[Beancount 设计文档](beancount-design-doc.md)：关于程序架构和设计选择、代码约定、不变量及方法论的信息。如果你想获得更深入的理解，请阅读此文档。

[LedgerHub 设计文档](ledgerhub-design-doc.md)：在 [beancount.ingest](http://github.com/beancount/beancount/tree/master/beancount/ingest/) 中实现的导入工具和库的设计与架构。这曾是一个名为 LedgerHub 的独立项目（现已停止维护），其有用部分最终被整合进了 Beancount。这是略显过时的原始设计文档。

[源代码](https://github.com/beancount/beancount/)：Beancount 源代码的官方仓库自 2020 年 5 月起位于 [Github](http://github.com/beancount/beancount/)。（2008 年至 2020 年 5 月期间托管在 Bitbucket 上）。

[外部贡献](external-contributions.md)：一份列表，列出了其他人制作并分享的、基于 Beancount 库构建的插件、导入器及其他代码。

## 增强提案与讨论<a id="enhancement-proposals-discussions"></a>

*我偶尔会撰写增强提案，以便在推进工作之前整理和总结我的想法，并向其他用户征求反馈。这是了解我计划添加哪些功能、了解详细工作原理，或与其他类似软件（如 Ledger 或 HLedger）进行比较差异的良好材料。*

[关于库存记账改进的提案](a-proposal-for-an-improvement-on-inventory-booking.md)：一份提案，概述了 Ledger 和 Beancount 在库存记账方面的现状，以及一种更好的方法，该方法将支持平均成本记账并在不计算佣金的情况下计算资本利得。

[Beancount 中的结算日期](settlement-dates-in-beancount.md)：关于结算日期或辅助日期如何在 Beancount 中使用，以及它们在 Ledger 中如何使用的讨论。

[Beancount 中的余额断言](balance-assertions-in-beancount.md)：对 Beancount 和 Ledger 中执行 balance assertion 的不同语义的总结，以及一项扩展 Beancount 语法以支持更复杂断言的提案。

[使用 Beancount 进行基金会计](fund-accounting-with-beancount.md)：关于基金会计以及如何最好地使用 Beancount 在单个账本中跟踪多个基金的讨论。

[Beancount 中的舍入与精度](rounding-precision-in-beancount.md)：关于余额检查中重要的舍入和精度问题的讨论，以及一项推断所需精度的更好方法的提案。（[已实现](precision-tolerances.md)）

## V3 文档<a id="v3-documentation"></a>

*截至 2020 年夏季，向 C++ 的重写工作正在进行中。以下是与此相关的文档。*

[Beancount V3](beancount-v3.md)：目标与设计：版本 3 向 C++ 重写的动机、目标和设计。

[Beancount V3：与 V2 的差异](https://docs.google.com/document/d/1Ia4zYmkB6I6IbWPRlcZYYuMS1ZI55T99dp9LiMJqXCE/)：当前在 v3（位于 "master" 分支）中已完成的变更列表，这些变更尚未纳入 v2 文档集。

[安装 Beancount (v3)](installing-beancount-v3.md)：v3 的安装步骤。

[Beancount V3：依赖项](beancount-v3-dependencies.md)：构建版本 3 所需的软件依赖项。

[Beangulp 新仓库设计文档](beangulp-design-doc-for-new-repo.md)：v3 的更新数据摄取框架。

## 关于本文档<a id="about-this-documentation"></a>

你可能已经注意到，我正在使用 [Google Docs](https://docs.google.com/)。我意识到这对一个开源项目来说并不寻常。如果你 [对此感到不满](https://groups.google.com/d/msg/ledger-cli/u648SA1o-Ek/yom_P38FCAAJ)，那么请知悉，我也喜欢纯文本格式：在研究生期间，我大量使用 [LaTeX](http://www.latex-project.org/)，而在过去十年里，我一直热爱 [reStructuredText](http://docutils.sourceforge.net) 格式，甚至为 Emacs 编写了对其的支持。但大约在 2013 年发生了一些变化：[Google Docs](https://docs.google.com/) 变得足够好，可以编写扎实的技术文档，并且我开始广泛享受其修订和评论功能：我沉迷于此，我热爱它。用户能够提出更正建议或在上下文中放置评论，这是一个极其有用的功能，比邮件列表上的补丁或评论更能极大地帮助提高我写作的质量。它还给了用户指出需要改进段落的机会。我已经收到了比我的其他任何项目多得多的文档反馈；它确实有效。

它的*外观*也非常*好*，这有助于激励我写出更多、更好的内容。我想我可能再次爱上了所见即所得（WYSIWYG）……别误会我：LaTeX 和无标记格式很棒，但世界正在变化，对我来说，拥有社区协作和一份活生生的文档，比一个在我的仓库中缓慢老化的陈旧 TeX 文件更重要。我的目标是产出易于阅读、打印美观的高质量文本，尤其是在当今时代，能够在移动设备或平板电脑上良好渲染，以便你可以随时随地阅读。我还能在外出时编辑它，这对于记录想法或进行更正来说很有趣。最后，Google Docs 有一个 API 提供对文档的访问，因此如果需要，我最终可以下载元数据并将其全部转换为另一种格式。我并非喜欢它的一切，但它所提供的功能，我确实很喜欢。

如果你想留下评论，如果你能在阅读时**登录你的 Google 账户**，以便你的名字显示在你的评论旁边，我将不胜感激。谢谢！

—[Martin Blais](mailto:blais@furius.ca)

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
