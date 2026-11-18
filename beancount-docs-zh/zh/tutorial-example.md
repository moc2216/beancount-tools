> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/tutorial_example/

# Beancount 示例与教程<a id="title"></a>

[Martin Blais](mailto:blais@furius.ca)，2014 年 10 月

[http://furius.ca/beancount/doc/example](http://furius.ca/beancount/doc/example)

> [示例文件生成器](#example-file-generator)
>
> [转换为 Ledger 输入](#converting-to-ledger-input)
>
> [示例用户简介](#profile-of-example-user)
>
> [未来新增内容](#future-additions)
>
> [教程](#tutorial)
>
> [生成示例文件](#generate-an-example-file)
>
> [生成 Report](#generating-reports)
>
> [生成余额](#generating-balances)
>
> [生成资产负债表和利润表](#generating-a-balance-sheet-and-income-statement)
>
> [Journal](#journals)
>
> [持仓](#holdings)
>
> [其他 Report](#other-reports)
>
> [其他格式](#other-formats)
>
> [通过 Web 界面查看 Report](#viewing-reports-through-the-web-interface)
>
> [Beancount Report 的未来](#_vlh1pclqsgq8)

## 示例文件生成器<a id="example-file-generator"></a>

Beancount 提供了一个命令，用于生成某位真实用户过去几年的历史 transaction 数据：

    bean-example > example.beancount

该脚本会检查输出文件是否能在 Beancount 中顺利处理（如果处理失败，请尝试重新运行，或联系作者 [blais@furius.ca](mailto:blais@furius.ca)）。请注意，有一个选项可以固定随机生成器的种子，用于生成这些条目。

你可以为该用户生成多年的账本数据；使用以下命令查看可用选项：

    bean-example --help

该脚本的用途包括：

-   为用户提供一组匿名的、贴近真实场景的数据语料，以便进行实验、测试 Beancount 的功能、生成 report 等。

-   将生成的 report 与 Ledger 生成的 report 进行对比。

-   作为本教程中使用的示例文件。

-   作为对 Beancount 进行压力测试的输入数据。

### 转换为 Ledger 输入<a id="converting-to-ledger-input"></a>

应该可以将脚本生成的示例文件转换为 Ledger 语法，例如：

    bean-report example.beancount ledger > example.lgr

如果你在转换过程中遇到任何问题，请告知我。虽然我有一个自动化测试来检查转换是否成功，但我目前将精力集中在 Beancount 本身，除了偶尔进行对比或在邮件列表上演示某些内容外，我很少使用 Ledger。

## 示例用户画像<a id="profile-of-example-user"></a>

以下是该用户的高层画像。在后续文本中，为了简洁起见，我将使用男性代词“他”。

-   他居住在美国某地，使用单一记账货币：“USD”。他租住公寓。

-   **收入**：他是一名软件工程师（抱歉，我忍不住这么写），从一家软件公司获得适度的工资收入。

    -   他每两周领取一次工资。

    -   他最大限度地缴纳公司 401k 计划。他的公司会为其缴纳额提供匹配。

    -   他的工资以直接存款形式存入其支票账户。

    -   他享受雇主提供的健康保险计划，并支付相关保费。

    -   他明确跟踪其休假时间。

-   **支出**：

    -   **支票账户**：他通过支票支付公寓租金。他还直接从支票账户支付电费、互联网 ISP 费用和手机话费。他的银行还会收取每月银行手续费。

    -   **信用卡**：他还有其他常规支出，例如杂货和与朋友外出就餐，这些费用通过信用卡支付。

<!-- -->

-   **资产**：

    -   **银行**：他在一家主要美国银行拥有账户。

    -   **退休账户**：他的 401k 账户托管在 Fidelity 或 Vanguard，并全部分配到两只基金中，包含股票和债券的组合。该账户中从未发生任何销售。该账户按平均成本持有。

    -   **其他投资**：他能够储蓄的额外资金会从支票账户转入一个应税投资账户，在该账户中他购买股票和 ETF 的组合，并偶尔进行销售以实现利润。

-   **负债**：

    -   **信用卡**：他拥有一到两张由另一家银行发行的信用卡。

-   **事件/标签**：他每年会进行一两次短途度假，前往一些有趣的地方旅行。

### 未来添加内容<a id="future-additions"></a>

请注意，随着我增强示例生成脚本，此画像的复杂度将会增加。如果您希望示例文件中包含 [cookbook](command-line-accounting-cookbook.md) 或其他特定情况，请告诉我（提交补丁是告知我的最佳方式）。

-   为文档生成伪造的 PDF 文件（通过一个选项），并为其生成合适的 document 指令，其中大部分是隐式的，但有些是显式的。

-   生成更多支出：

    -   一定数量的现实现金支出。

    -   添加车辆：汽车维修、汽油等。移除有轨电车示例，因为它过于特定于城市环境。

    -   添加慈善捐赠。

    -   添加第二张信用卡，并多样化支出来源。

-   为链接添加一些实际用途，例如对于 401k 匹配，雇主缴纳部分应与员工缴纳部分建立链接。或者其他情况。

-   生成学生贷款及其还款。拥有大额负债是一种常见情况，我希望表示这种情况，即使它不是抵押贷款。

-   将退休账户转换为使用平均成本法进行记账，并添加相应的费用，否则使用显式 lot 将无法跟踪这些费用。

-   按照 cookbook 添加医疗保健支出的跟踪。

-   添加另一种货币的外币账户，以及该货币下的 transaction 和转账。

## 教程 <a id="tutorial"></a>

本节提供了使用 Beancount 生成 report 的基本示例，基于其典型输出文件。此处的 report 列表并非详尽无遗。

你可以跟随教程生成自己的示例文件，或者查看 [beancount/examples/tutorial](http://github.com/beancount/beancount/tree/v2/examples/tutorial/) 中的文件（如果你更倾向于这样做）。

### 生成示例文件<a id="generate-an-example-file"></a>

首先，生成示例文件：

    bean-example > example.beancount

打开 `example.beancount` 并查看其内容。

接下来，在开始生成 report 之前，验证该文件能否无错误地加载：

    bean-check example.beancount

它应该静默返回，不输出任何内容（bean-check 仅在存在错误时才会写入错误信息，否则在成功时不写入任何内容）。

### 生成报告<a id="generating-reports"></a>

让我们生成一份所有账户最终余额的 report [\[output\]](http://furius.ca/beancount/examples/tutorial/balances.output)：

    bean-report example.beancount balances

如你所见，bean-report 脚本为它生成的各种 report 提供了子命令。要列出可用的 report，请使用 --help-reports [\[output\]](http://furius.ca/beancount/examples/tutorial/help-reports.output)：

    bean-report --help-reports

要列出特定 report 的可用选项，请对其使用 --help [\[output\]](http://furius.ca/beancount/examples/tutorial/help-subcmd.output)：

    bean-report example.beancount balances --help

针对特定 report 的选项因 report 类型而异。

你还可以列出该脚本的全局选项 [\[output\]](http://furius.ca/beancount/examples/tutorial/help-global.output)：

    bean-report --help

全局选项允许你指定 report 所需的输出格式。要查看哪些 report 支持哪些格式，请使用 --help-formats [\[output\]](http://furius.ca/beancount/examples/tutorial/help-formats.output)：

    bean-report --help-formats

### 生成余额<a id="generating-balances"></a>

好的，现在我们知道如何生成所有账户的余额 report。不过，这是一个相当详细的账户列表。让我们将输出限制为我们感兴趣的账户 [\[output\]](http://furius.ca/beancount/examples/tutorial/balances-restrict.output)：

    bean-report example.beancount balances -e ETrade

在这里，你可以查看每个 investment 子账户中持有的单位数量。要显示 cost，请使用 --cost 选项 [\[output\]](http://furius.ca/beancount/examples/tutorial/balances-restrict-cost.output)：

    bean-report example.beancount balances -e ETrade --cost

### 格式化工具<a id="formatting-tools"></a>

有时，将账户的层级列表渲染为树状结构会很有用。你可以使用 Beancount 提供的 “treeify” 工具来实现这一点：

    bean-report example.beancount balances | treeify

该工具可以处理任何看起来像账户名称列的数据列（你也可以配置它以处理文件名或其他模式）。

### 生成资产负债表和利润表<a id="generating-a-balance-sheet-and-income-statement"></a>

让我们生成一份资产负债表：

    bean-report example.beancount balsheet

不幸的是，目前唯一支持的输出格式是 HTML。此外，也不支持从命令行过滤资产负债表条目。请将其生成到文件中，并在浏览器中打开 [\[output\]](http://furius.ca/beancount/examples/tutorial/balsheet.output)：

    bean-report example.beancount balsheet > /tmp/balsheet.html

你可以对利润表执行相同的操作：

    bean-report example.beancount income > /tmp/income.html

### 日记账 <a id="journals"></a>

你还可以生成 journals（在 Ledger 术语中，这些被称为“registers”）。例如，查看一个 checking account 的 postings [\[output\]](http://furius.ca/beancount/examples/tutorial/journal.output)：

    bean-report example.beancount journal -a Assets:US:BofA:Checking

要渲染一列 running balances，请添加 --balance 选项 [\[output\]](http://furius.ca/beancount/examples/tutorial/journal-with-balance.output)：

    bean-report example.beancount journal -a Assets:US:BofA:Checking --balance

inventories 会以它们持有的单位数量进行渲染 [\[output\]](http://furius.ca/beancount/examples/tutorial/invest.output)：

    bean-report example.beancount journal -a Assets:US:ETrade:GLD

如果你想以 cost 值进行渲染，请使用 --cost 选项 [\[output\]](http://furius.ca/beancount/examples/tutorial/invest-with-cost.output)：

    bean-report example.beancount journal -a Assets:US:ETrade:GLD --cost

要渲染 journals，你通常需要对想要查看的 postings 集合进行限制。如果不这样做，postings 将不会显示任何变化，因为 transactions 的所有 legs 都会应用于 running balance，且总和为零。但尽管如此，还是可以尝试一下 [\[output\]](http://furius.ca/beancount/examples/tutorial/journal-unrestricted.output)：

    bean-report example.beancount journal --balance

### holdings <a id="holdings"></a>

有多种方式可以获取持仓总列表的聚合数据。列出详细的持仓 [\[output\]](http://furius.ca/beancount/examples/tutorial/holdings.output)：

    bean-report example.beancount holdings

若要按 account 聚合持仓，请执行以下操作 [\[output\]](http://furius.ca/beancount/examples/tutorial/holdings-by-account.output)：

    bean-report example.beancount holdings --by=account

由于在实际账户中为每种持有的商品创建并使用专用的 Beancount 子 account 名称是常见做法，我们可以进一步细化，将这些子 account 聚合到其父（“root”）account [\[output\]](http://furius.ca/beancount/examples/tutorial/holdings-by-root-account.output)：

    bean-report example.beancount holdings --by=root-account

我们可以按商品聚合 [\[output\]](http://furius.ca/beancount/examples/tutorial/holdings-by-commodity.output)：

    bean-report example.beancount holdings --by=commodity

或者按商品报价的货币进行聚合，这让我们可以一窥我们的货币敞口 [\[output\]](http://furius.ca/beancount/examples/tutorial/holdings-by-currency.output)：

    bean-report example.beancount holdings --by=currency

最后，我们可以聚合所有持仓以获取净资产 [\[output\]](http://furius.ca/beancount/examples/tutorial/networth.output)：

    bean-report example.beancount networth

还有几个用于将金额转换为通用货币的选项。请参阅帮助以获取详细信息。

### 其他报告<a id="other-reports"></a>

还有许多其他杂项报告可用。请尝试其中几个。

列出所有 account [\[output\]](http://furius.ca/beancount/examples/tutorial/accounts.output):

    bean-report example.beancount accounts

列出事件 [\[output\]](http://furius.ca/beancount/examples/tutorial/events.output):

    bean-report example.beancount events

按类型统计 directive 数量 [\[output\]](http://furius.ca/beancount/examples/tutorial/stats-directives.output):

    bean-report example.beancount stats-directives

按类型统计 posting 数量 [\[output\]](http://furius.ca/beancount/examples/tutorial/stats-postings.output):

    bean-report example.beancount stats-postings

### 其他格式<a id="other-formats"></a>

Reports 可能支持多种输出格式。你可以使用 --format (-f) 全局选项 [\[output\]](http://furius.ca/beancount/examples/tutorial/holdings-csv.output) 来更改输出格式：

    bean-report -f csv example.beancount holdings

请注意，“beancount” 和 “ledger” 是有效的输出格式：它们分别指代 Beancount 和 Ledger 的输入语法。

### 通过 Web 界面查看报告<a id="viewing-reports-through-the-web-interface"></a>

[Fava](https://beancount.github.io/fava/) 是一个独立项目，为本地机器上的 Beancount 提供 Web 界面。请参见[此处演示](https://fava.pythonanywhere.com/example-beancount-file/income_statement/)。Fava 的 [github 页面](https://github.com/beancount/fava?tab=readme-ov-file) 展示了如何安装和使用它。Fava 显示您的 account 树、balance assertion 和 income statements、journal 以及 holdings，并允许在其 Web 界面内运行 Beancount 查询。Fava 还拥有针对特定需求的自有插件。

*注意：如果您正在寻找 bean-web（随 Beancount 一起发布的 Web 服务器），它现已弃用。Fava 是推荐的 Web 界面。*

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
