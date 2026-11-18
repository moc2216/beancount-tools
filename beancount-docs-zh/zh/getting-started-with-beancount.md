> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/getting_started_with_beancount/

# 开始使用 Beancount<a id="title"></a>

[Martin Blais](mailto:blais@furius.ca)，2014 年 7 月

[http://furius.ca/beancount/doc/getting-started](http://furius.ca/beancount/doc/getting-started)

## 简介<a id="introduction"></a>

本文档是一份温和的指南，旨在帮助你创建第一个 Beancount 文件，初始化一些选项，提供关于如何组织文件的指导，并说明如何声明 account 以及确保其初始 balance assertion 不会引发错误。如果你使用 Emacs 文本编辑器，本文档还包含一些关于配置 Emacs 的内容。

你可能希望先阅读一些 [用户手册](beancount-language-syntax.md) 的内容，以熟悉语法和可用的 directive 类型；或者，如果你已经设置了一个文件或知道如何操作，可以直接前往 [食谱](command-line-accounting-cookbook.md)。如果你熟悉 Ledger，可能希望先阅读 [Ledger 与 Beancount 之间的差异](a-comparison-of-beancount-and-ledger-hledger.md)。

## 编辑器支持<a id="editor-support"></a>

Beancount 账本文件是简单的文本文件。您可以使用任何文本编辑器来编写输入文件。然而，一个能够理解足够 Beancount 语法并提供针对性功能（如语法高亮、自动补全和自动缩进）的优秀文本编辑器，在编译和维护您的账本时，有潜力极大地提高生产力。

### Emacs（编辑器） <a id="emacs"></a>

在 Emacs 中编辑 Beancount 账本文件的支持功能传统上是随 Beancount 一起分发的。现在它作为一个独立的项目存在于[这个 Github 仓库](https://github.com/beancount/beancount-mode/)中。

### Vim（编辑器） <a id="vim"></a>

在 Vim 中编辑 Beancount 账本文件的支持功能由 Nathan Grigg 实现，并可在[这个 Github 仓库](https://www.google.com/url?q=https%3A%2F%2Fgithub.com%2Fnathangrigg%2Fvim-beancount&sa=D&sntz=1&usg=AFQjCNFgEjRsUHfpvOFxn8gD4-c_eK_wsA)中获取。

### Sublime Text（编辑器） <a id="sublime"></a>

Sublime 的编辑支持功能由 Martin Andreas Andersen 贡献，可在[这个 github 仓库](https://www.google.com/url?q=https%3A%2F%2Fgithub.com%2Fdraug3n%2Fsublime-beancount&sa=D&sntz=1&usg=AFQjCNExx6wdX5QF1hnixgHcKJV-5XJwMA)中获取，或者作为 Sublime 包在[这里](https://packagecontrol.io/packages/Beancount)下载。

### VSCode（编辑器） <a id="vscode"></a>

有许多用于处理 Beancount 文本文件的插件，包括 Lencerf 开发的[VSCode-Beancount](https://marketplace.visualstudio.com/items?itemName=Lencerf.beancount)。

## 创建你的第一个输入文件<a id="creating-your-first-input-file"></a>

为了开始，让我们创建一个包含两个 account 和一笔 transaction 的最小输入文件。将以下输入输入或复制到文本文件中：

    2014-01-01 open Assets:Checking
    2014-01-01 open Equity:Opening-Balances

    2014-01-02 * "Deposit"
      Assets:Checking           100.00 USD
      Equity:Opening-Balances

## 简要语法概览<a id="brief-syntax-overview"></a>

以下是一些注意事项以及 Beancount 语法的极简概览：

-   货币代码必须全部使用大写字母（允许包含数字和某些特殊字符，如 “\_” 或 “-”）。不支持货币符号（例如 $ 或 €）。

-   账户名称中不允许包含空格（尽管可以使用连字符），并且必须至少包含两个由冒号分隔的组件。账户名称的每个组件必须以大写英文字母或数字开头。

-   描述字符串必须加引号，例如：`"AMEX PMNT"`。

-   日期仅解析为 ISO8601 格式，即 YYYY-MM-DD。

-   标签必须以 “\#” 开头，链接必须以 “^” 开头。

如需完整的语法说明，请访问 [用户手册](beancount-language-syntax.md)。

## 验证你的文件<a id="validating-your-file"></a>

Beancount 的目的是根据你的输入文件生成 report（无论是在控制台上还是通过其 web 界面提供）。不过，你可以使用一个工具来简单地加载其内容并进行一些验证检查，以确保你的输入不包含错误。Beancount 可能相当严格；这是一个在你输入数据时使用的工具，用于确保你的输入文件是合法的。该工具名为 “bean-check”，你可以通过以下方式调用它：

    bean-check /path/to/your/file.beancount

现在就在你从上一节创建的文件上尝试一下。它应该没有任何输出地退出。如果有错误，它们将打印在控制台上。错误以 Emacs 默认识别的格式打印，因此你可以使用 Emacs 的 `next-error` 和 `previous-error` 内置函数将光标移动到问题所在的位置。

## 查看 Web 界面<a id="viewing-the-web-interface"></a>

查看 report 的一种便捷方式是针对你的输入文件启动 “bean-web” 工具。请尝试：

    bean-web /path/to/your/file.beancount

然后，你可以将 web 浏览器指向 [http://localhost:8080](http://localhost:8080)，并在 Beancount 生成的各个 report 之间进行浏览。之后，你可以修改输入文件并重新加载浏览器当前指向的 web 页面——bean-web 会自动重新加载文件内容。

此时，你最好阅读一下 [Language Syntax](beancount-language-syntax.md) 文档中的部分内容。

## 如何组织你的文件<a id="how-to-organize-your-file"></a>

在本节中，我们提供关于如何组织文件的通用指南。这假设你已经阅读了[语言语法](beancount-language-syntax.md)文档。

### 输入文件的序言<a id="preamble-to-your-input-file"></a>

我建议你从一个单一的文件开始[^1]。我的文件有一个头部，用于告诉 Emacs 以何种模式打开该文件，随后是一些常见的选项：

    ;; -*- mode: beancount; coding: utf-8; fill-column: 400; -*-
    option "title" "My Personal Ledger"
    option "operating_currency" "USD"
    option "operating_currency" "CAD"

title 选项用于 report 中。“operating currencies”列表标识了你最常用作“货币”的那些商品，并且值得在 report 中拥有其专属的列（此声明对任何计算的行为没有其他影响）。

### 章节与声明账户<a id="sections-declaring-accounts"></a>

我喜欢将我的输入文件组织成与每个现实世界账户相对应的章节。每个章节通过使用 Open directive 来定义与该现实世界账户相关的所有 account。例如，这是一个支票账户：

    2007-02-01 open Assets:US:BofA:Savings              USD
    2007-02-01 open Income:US:BofA:Savings:Interest     USD

我尽可能多地声明货币约束，以避免错误。另外，请注意我是如何声明一个特定于该账户的收入账户的。这有助于在 report 中细分收入以用于报税，因为你很可能会收到与该特定账户收入相关的税务文件（在美国，这将是由你的银行产生的 1099-INT 表格）。

以下是投资账户的初始账户可能看起来的样子：

    2012-03-01 open Assets:US:Etrade:Main:Cash            USD
    2012-03-01 open Assets:US:Etrade:Main:ITOT            ITOT
    2012-03-01 open Assets:US:Etrade:Main:IXUS            IXUS
    2012-03-01 open Assets:US:Etrade:Main:IEFA            IEFA
    2012-03-01 open Income:US:Etrade:Main:Interest        USD
    2012-03-01 open Income:US:Etrade:Main:PnL             USD
    2012-03-01 open Income:US:Etrade:Main:Dividend        USD
    2012-03-01 open Income:US:Etrade:Main:DividendNoTax   USD

重点在于所有这些 account 都以某种方式相互关联。cookbook 的各个章节将描述建议为每个章节创建的一组 account。

关于上述内容的一个说明：如果你不喜欢货币同时出现在账户名称和约束中的冗余，你可以在一个 account 中放置多个货币，Beancount 可以很好地处理这种情况。按照上述示例这样做只是有助于某些配置，例如 beangrow。

并非所有章节都必须如此。例如，我有以下章节：

-   **永恒账户。** 我在顶部有一个专门用于包含特殊和“永恒”账户的章节，例如应付账款和应收账款。

-   **日记账。** 我在底部有一个“日记账”章节，按时间顺序包含所有现金支出。

-   **支出账户。** 我所有的支出账户（类别）都在其自己的章节中定义。

-   **雇主。** 对于每个雇主，我都定义了一个章节，其中包含其直接存款的条目，并跟踪休假、股票归属和其他与工作相关的 transaction。

-   **税务。** 我有一个按纳税年度组织的税务章节。

你可以按任何你喜欢的方式组织它，因为 Beancount 不关心声明的顺序。

### 关闭账户<a id="closing-accounts"></a>

如果一个现实世界账户已经关闭，或者永远不会再有任何 posting 记录到其中，你可以使用 Close directive 在特定日期将其声明为“closed”：

    ; Moving to another bank.
    2013-06-13 close Assets:US:BofA:Savings

这告诉 Beancount 不要在未包含其活跃日期的 report 中显示该 account。它还会通过在你尝试在稍后日期向其 posting 时触发错误来避免错误。

## 去重<a id="de-duping"></a>

一个经常出现的问题是，一旦你设置了[某种代码或流程](http://furius.ca/beancount/doc/ingest)来自动从下载的文件中提取 posting，你最终会导入提供同一笔 transaction 两个不同侧面的 posting。一个例子是通过从支票账户转账来支付信用卡余额。如果你下载支票账户的 transaction，你会提取出类似这样的内容：

    2014-06-08 * "ONLINE PAYMENT - THANK YOU"
      Assets:CA:BofA:Checking           -923.24 USD

信用卡下载会给你这样的结果：

    2014-06-10 * "AMEX EPAYMENT    ACH PMT"
      Liabilities:US:Amex:Platinum       923.24 USD

很多时候，来自这些账户的 transaction 需要 booking 到费用 account，但在这种情况下，这是同一笔 transaction 的两个独立部分：一笔转账。当你导入其中一个时，你通常通常寻找另一侧并将它们合并在一起：

    ;2014-06-08 * "ONLINE PAYMENT - THANK YOU"
    2014-06-10 * "AMEX EPAYMENT    ACH PMT"
      Liabilities:US:Amex:Platinum       923.24 USD
      Assets:CA:BofA:Checking           -923.24 USD

我经常将其中一行描述保留在注释中——这只是我的选择，Beancount 会忽略它。还要注意，我不得不选择两个日期中的一个。只要不破坏任何 balance assertion，我就选择我更喜欢的那个。

如果你忘记合并这两个导入的 transaction，别担心！这正是 balance assertion 的用途。定期在这些 account 中的任何一个放置 balance assertion，例如每次导入时，如果你最终重复输入了 transaction，你会得到一个很好的错误提示。这很常见，过一段时间后，解释该编译器错误并迅速修复它就变得习以为常了。

最后，当我知道我只导入这些 transaction 的一侧时，我会手动选择另一个 account，并在我知道稍后会被导入的 posting 上标记一个 flag，这告诉我我还没有对这笔 transaction 进行去重：

    2014-06-10 * "AMEX EPAYMENT    ACH PMT"
      Liabilities:US:Amex:Platinum       923.24 USD
      ! Assets:CA:BofA:Checking

稍后，当我导入支票账户的 transaction 并寻找这笔付款的另一侧时，我会找到这个，并感到世界正在按预期运行。

（如果你有兴趣了解更多关于 transaction 去重和合并的讨论，请参阅此[功能提案](settlement-dates-in-beancount.md)。此外，你可能对[“effective\_date” 插件](https://www.google.com/url?q=https://github.com/redstreet/beancount_plugins_redstreet&sa=D&ust=1458615376548000&usg=AFQjCNGY-CWtCRP75-3p8Yr02BC_itG76g)外部贡献感兴趣，它将 transaction 分为两部分。）

### 哪一侧？<a id="which-side"></a>

因此，如果你按照我上面建议的方式将 account 组织成各个部分，你应该将这种“合并”的 transaction 留在文件的哪个部分，即涉及两个独立 account 的 transaction？嗯，这由你决定。例如，在两个 account 之间的转账情况下，如果它们被组织成拥有自己专用部分，能够在那里保留两个 transaction 会很好，这样当你编辑输入文件时，你可以在任何部分看到它们，但不幸的是，transaction 必须只出现在你的文档中的一个位置。你必须选择一个。

个人而言，我在选择将 transaction 留在哪个部分时有点随意；有时我为同一对 account 选择输入文件的一个部分，或另一个 account 的部分。这并没有成为问题，因为我使用 Emacs 并大量使用 i-search，这使得在我的巨大输入文件中挖掘变得容易。如果你想保持输入更整洁有序，你可以为自己制定一条规则，例如“信用卡付款总是留在付款 account 的部分，而不是信用卡 account 的部分”，或者你可以将 transaction 留在两个部分中并注释掉其中一个[^2]。

### 挂账账户<a id="suspense-accounts"></a>

最终，正确的做法将是支持[挂账账户](https://www.google.com/url?q=http://en.wikipedia.org/wiki/Suspense_account&sa=D&source=docs&ust=1776012592990052&usg=AOvVaw0ucmanriL2B86xf-AgKu1l)（我在这些文档中也称之为“转账账户”）。这将通过一种输入风格实现，涉及输入两个不完整的 transaction，并有一种方法自动将这些 transaction 链接在一起，以避免将忘记的金额 posting 到转账/挂账账户。请参阅[此文档](settlement-dates-in-beancount.md)进行讨论。

## padding <a id="padding"></a>

如果你刚刚开始使用——如果你正在阅读本文，那你很可能就是这种情况——你将没有任何历史数据。这意味着你在 Beancount 中的 Assets 和 Liabilities 账户的余额都将为零。但在定义了一些账户之后，你首先应该做的是建立资产负债表，并将这些金额调整到其实际的当前值。

以你的支票账户为例，假设你很久以前就开立了它。你不记得确切的时间，所以让我们使用一个近似日期：

    2000-05-28 open Assets:CA:BofA:Checking  USD

接下来，你查询当前的余额，并为相应的金额添加一个 balance assertion：

    2014-07-01 balance Assets:CA:BofA:Checking    1256.35 USD

仅运行 Beancount 处理这些内容会正确地产生一个错误，因为 Beancount 假设在你开立账户时存在一个隐含的“空” balance assertion。你必须通过插入一个 *balance adjustment* 来“pad”你的账户，使其达到今天的余额。这个调整发生在开立日期和余额日期之间的某个时间点，针对某个权益账户，该账户是记录“初始余额来源”的任意位置。为此，通常使用“`Equity:Opening-Balances`”账户。因此，让我们包含这个 padding transaction，并回顾一下我们目前的内容：

    2000-05-28 open Assets:CA:BofA:Checking  USD

    2000-05-28 * "Initialize account"
      Equity:Opening-Balances                    -1256.35 USD
      Assets:CA:BofA:Checking                     1256.35 USD

    2014-07-01 balance Assets:CA:BofA:Checking    1256.35 USD

从这里开始，你将开始添加反映 7 月 1 日之后发生的所有事情的条目。但是，如果你想*回溯*时间怎么办？一旦你设置好了账户体系，想要填补至少直到今年年初的缺失历史，这是完全合理的。

假设你在 2014 年 6 月有一笔 transaction，让我们添加它：

    2000-05-28 open Assets:CA:BofA:Checking  USD

    2000-05-28 * "Initialize account"
      Equity:Opening-Balances                    -1256.35 USD
      Assets:CA:BofA:Checking                     1256.35 USD

    2014-06-28 * "Paid credit card bill"
      Assets:CA:BofA:Checking                     -700.00 USD
      Liabilities:US:Amex:Platinum                 700.00 USD

    2014-07-01 balance Assets:CA:BofA:Checking    1256.35 USD

现在 balance assertion 失败了！你需要调整初始化条目来修复这个问题：

    2000-05-28 open Assets:CA:BofA:Checking  USD

    2000-05-28 * "Initialize account"
      Equity:Opening-Balances                    -1956.35 USD
      Assets:CA:BofA:Checking                     1956.35 USD

    2014-06-28 * "Paid credit card bill"
      Assets:CA:BofA:Checking                     -700.00 USD
      Liabilities:US:Amex:Platinum                 700.00 USD

    2014-07-01 balance Assets:CA:BofA:Checking    1256.35 USD

现在这可以工作了。所以基本上，每次你在过去插入一个条目，你都必须调整余额。这不是很烦人吗？嗯，是的。

幸运的是，我们可以提供一些帮助：你可以使用 Pad directive 来替换并自动合成 balance adjustment，以匹配下一个 balance check，如下所示：

    2000-05-28 open Assets:CA:BofA:Checking  USD

    2000-05-28 pad Assets:CA:BofA:Checking Equity:Opening-Balances

    2014-06-28 * "Paid credit card bill"
      Assets:CA:BofA:Checking                     -700.00 USD
      Liabilities:US:Amex:Platinum                 700.00 USD

    2014-07-01 balance Assets:CA:BofA:Checking    1256.35 USD

请注意，这仅对资产负债表账户（Assets 和 Liabilities）是必需的，因为我们不关心 Income 和 Expenses 账户的初始余额，我们只关心它们的过渡值（它们在期间内 posting 的变化）。例如，将 Expenses:Restaurant 账户调整到你出生以来所有餐费成本的总和是没有意义的。

因此，你可能希望为每个 Assets 和 Liabilities 账户从 Open 和 Pad directives 开始。

## 接下来做什么？<a id="whats-next"></a>

此时，你很可能要继续前往 [食谱](command-line-accounting-cookbook.md)，或者如果你还没有这样做的话，阅读 [用户手册](beancount-language-syntax.md)。

[^1]: 将一个大文件拆分成许多小文件是很诱人的，但尤其是在一开始，将所有内容集中在一个地方的便利性是很大的。

[^2]: 有些人建议 Beancount 基于启发式方法自动检测重复的 transaction，并自动忽略（删除）其中两个中的一个，但这尚未被尝试过。特别是，这将非常适合不仅按部分组织 transaction，而且将它们放在单独的文件中，即，所有文件都将包含它们所代表的 account 的所有 transaction。如果你有兴趣添加此功能，你可以轻松地将此实现为一个 plugin，而不会干扰系统的其余部分。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
