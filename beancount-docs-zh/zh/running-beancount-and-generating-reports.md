> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/running_beancount_and_generating_reports/

# 运行 Beancount 与生成 Report<a id="title"></a>

[Martin Blais](mailto:blais@furius.ca)，2014 年 7 月至 9 月

[http://furius.ca/beancount/doc/tools](http://furius.ca/beancount/doc/tools)

[简介](#introduction)

[工具](#tools)

> [bean-check](#bean-check)
>
> [bean-report](#bean-report)
>
> [bean-query](#bean-query)
>
> [bean-web](#bean-web)
>
> [全局页面](#global-pages)
>
> [查看 Report 页面](#view-reports-pages)
>
> [bean-bake](#bean-bake)
>
> [bean-doctor](#bean-doctor)
>
> [上下文](#context)
>
> [bean-format](#bean-format)
>
> [bean-example](#bean-example)

[过滤 Transaction](#filtering-transactions)

[Report](#reports)

> [余额 Report](#balance-reports)
>
> [试算平衡表 (balances)](#trial-balance-balances)
>
> [资产负债表 (balsheet)](#balance-sheet-balsheet)
>
> [期初余额 (openbal)](#opening-balances-openbal)
>
> [利润表 (income)](#income-statement-income)
>
> [日记账 Report](#journal-reports)
>
> [日记账 (journal)](#journal-journal)
>
> [按 Cost 渲染](#rendering-at-cost)
>
> [添加余额列](#adding-a-balance-column)
>
> [字符宽度](#character-width)
>
> [Precision](#precision)
>
> [紧凑、普通或详细](#compact-normal-or-verbose)
>
> [摘要](#summary)
>
> [等效 SQL 查询](#equivalent-sql-query)
>
> [转换 (conversions)](#conversions-conversions)
>
> [文档 (documents)](#documents-documents)
>
> [持仓 Report](#holdings-reports)
>
> [持仓与聚合 (holdings\*)](#holdings-aggregations-holdings)
>
> [净资产 (networth)](#net-worth-networth)
>
> [其他 Report 类型](#other-report-types)
>
> [现金](#cash)
>
> [价格 (prices)](#prices-prices)
>
> [统计 (stats)](#statistics-stats)
>
> [更新活动 (activity)](#update-activity-activity)

## 重要提示：本文档适用于 v2 分支中已弃用的工具。其中许多工具在 v3 及更高版本中已被删除。 <a id="important-this-document-applies-to-tools-from-the-v2-branch-which-have-been-deprecated.-many-of-these-tools-have-been-deleted-for-v3-and-beyond."></a>

## 简介<a id="introduction"></a>

本文档介绍了用于处理 Beancount 输入文件的工具，以及从中生成的多种 report。该语言的语法在 [Beancount 语言语法](beancount-language-syntax.md) 文档中有详细说明。本手册仅涵盖从命令行使用 Beancount 的技术细节。

## 工具<a id="tools"></a>

### bean-check（校验） <a id="bean-check"></a>

**bean-check** 是用于验证您的输入语法和 transaction 是否正确的程序。它所做的全部工作就是加载您的输入文件，并运行其中配置的各种插件，外加一些额外的验证检查。它会报告错误（如果有的话），然后退出。您需要在输入文件上运行它，例如：

    bean-check /path/to/my/file.beancount

如果没有错误，则不应有任何输出，程序应安静地退出。如果存在错误，它们将连同文件名、行号和错误描述一起打印到 stderr（采用 Emacs 可理解的格式，因此如果您愿意，可以直接使用 `next-error` 和 `previous-error` 导航到该文件）：

    /home/user/myledger.beancount:44381:   Transaction does not balance: 34.46 USD

       2014-07-12 * "Black Iron Burger" ""
         Expenses:Food:Restaurant               17.23 USD
         Assets:Cash                            17.23 USD

在生成 report 之前，您应该始终修复所有错误。

### bean-report（报表） <a id="bean-report"></a>

这是用于将专用 report 以文本或其他多种格式提取到控制台的主要工具。调用方式如下：

    bean-report /path/to/my/file.beancount <report-name>

例如：

    bean-report /path/to/my/file.beancount balances

有许多可用的 report。请参阅 report 章节以了解主要 report 的说明。如果您想生成完整的 report 列表，可以请求帮助：

    bean-report --help-reports

Report 名称有时可以接受参数。目前，参数作为 report 名称的一部分指定，通常用冒号 (:) 分隔，如下所示：

    bean-report /path/to/my/file.beancount balances:Vanguard

有几个特殊的 report 您应该了解：

-   check 或 validate：这与运行 bean-check 命令相同。

-   print：这仅打印出 Beancount 已解析的条目，使用 Beancount 语法。这可用于确认 Beancount 是否正确读取和解释了您的输入数据（如果您正在调试某些困难的问题）。

其他 report 则是您预期的那样：它们打印出各种金额聚合的表格。您可以生成的 report 在下方的专用章节中进行了描述。

<table><tbody><tr class="odd"><td><em><strong>请注意！</strong></em> 在发布时，从网页可用的 report 列表将与从控制台可用的列表不同。在未来的版本中，我将整合这两个列表，所有从网页可用的 report 也将可以从控制台使用，并且支持多种不同的格式。敬请期待。</td></tr></tbody></table>

### bean-query（查询） <a id="bean-query"></a>

Beancount 解析后的 transaction 和 posting 列表就像一个内存数据库。**bean-query** 是一个命令行工具，它充当该内存数据库的客户端，你可以在其中输入 SQL 变体查询。调用方式如下：

    bean-query /path/to/my/file.beancount
    Input file: "/path/to/my/file.beancount"
    Ready with 14212 directives (21284 postings in 8879 transactions).
    beancount> _

更多详细信息请参见其[独立文档](beancount-query-language.md)。

### bean-web（Web 界面） <a id="bean-web"></a>

**bean-web** 在运行于您计算机上的 web 服务器上提供所有 report。运行方式如下：

    bean-web /path/to/my/file.beancount

它将在您机器的 8080 端口上提供所有页面。使用 web 浏览器导航至 [http://localhost:8080](http://localhost:8080)。您应该能够轻松地点击浏览所有 report。

该 web 界面提供一组全局页面，以及针对每个“view”的一组 report 页面。

#### 全局页面<a id="global-pages"></a>

顶层目录页面在顶部提供了指向所有全局页面的链接：

-   目录（即您正在查看的页面）

-   您的 ledger 文件中出现的错误列表

-   您的 Ledger 文件的源代码视图（当其他链接引用您输入文件中的位置时，会使用此视图。）

目录提供了指向所有常见 view 的便捷链接列表，例如

-   “按年查看”，

-   “按 tag 查看”，当然还有

-   “查看所有 transaction。”

还有更多。

#### View Report 页面<a id="view-reports-pages"></a>

当您点击一个 view report 页面时，您会进入针对该 view 的 transaction 子集的一组页面。可以从这里获取关于这些 transaction 的各种 report：

-   期初余额（view 开始时的资产负债表）

-   资产负债表（view 结束时的资产负债表）

-   利润表（针对 view 的期间）

-   每个 account 的各种 journal（只需点击 account 名称）

-   view 结束时持仓的各种 report

-   包含在 view 条目中的文档和 price 列表

-   关于 view 数据的一些统计信息

……以及更多内容。应该有一个所有可用 view report 的索引。

### bean-bake（打包） <a id="bean-bake"></a>

**bean-bake** 会运行一个 **bean-web** 实例，并将所有页面烘焙（bake）到一个目录中：

    bean-bake /path/to/my/file.beancount myfinances

它也支持直接烘焙到归档文件：

    bean-bake /path/to/my/file.beancount myfinances.zip

支持多种压缩方式，例如 .tar.gz。

这在需要与会计师或其他通常无法运行 Beancount 的人共享 web 界面时非常有用。页面链接已全部转换为相对链接，他们只需将归档文件解压到一个目录，即可像使用 **bean-web** 一样浏览所有 report。

### bean-doctor（诊断） <a id="bean-doctor"></a>

这是一个调试工具，用于执行各种诊断和运行调试命令，并帮助提供报告 bug 所需的信息。例如，它可以执行以下操作：

-   列出您机器上已安装的 Beancount 依赖项以及缺失的依赖项。它可以告诉您缺少哪些应该安装的组件。

-   打印输入文件的解析器词法分析器（lexer）token 转储。如果您报告解析 bug，查看词法分析器输出可能很有用（如果您知道自己在做什么的话）。

-   它可以对输入文件进行解析往返测试，即打印出文件并重新读取它，然后进行比较。这是一个有用的解析器和打印器测试。

-   它可以检查目录层次结构是否与 Beancount 输入文件的账户表（chart-of-accounts）对应，并报告不合规的目录。如果您决定更改某些 account 名称，并且正在维护一个需要相应调整的文档归档，这将非常有用。

#### 上下文 <a id="context"></a>

它可以列出 transaction 应用时的上下文，即该 transaction 的 postings 所修改的每个 account 的库存余额，分别显示在应用之前和应用之后。请像这样使用它：

    $ bean-doctor context /home/blais/accounting/blais.beancount 28514
    /home/blais/accounting/blais.beancount:28513:

    ;   Assets:US:ETrade:BND             100.00 BND {81.968730000000 USD}
    ;   Assets:US:ETrade:Cash           8143.97 USD

    2014-07-25 * "(TRD) BOT +50 BND @82.10" ^273755872
     Assets:US:ETrade:BND                 50.00 BND {82.10 USD}  
     Assets:US:ETrade:Cash             -4105.00 USD         

    ;   Assets:US:ETrade:BND                    100.00 BND {81.968730000000 USD}

    ; ! Assets:US:ETrade:BND              50.00 BND {82.10 USD}
    ; ! Assets:US:ETrade:Cash           4038.97 USD

有一个对应的 Emacs 绑定（C-c x）可以在光标周围调用此功能。

### bean-format（格式化） <a id="bean-format"></a>

这个纯文本处理工具会重新格式化 Beancount 输入，将所有数字右对齐到相同的最小列。它会将所有货币左对齐。它仅修改空白字符。该工具接受文件名作为参数，并将对齐后的文件输出到 stdout（类似于 UNIX `cat`）。

### bean-example（示例账本） <a id="bean-example"></a>

此程序生成一个示例 Beancount 输入文件。有关此示例文件内容的更多详细信息，请参阅[教程](tutorial-example.md)。

## 过滤交易<a id="filtering-transactions"></a>

为了生成财务交易的不同视图，我们会从解析后的完整交易列表中选择一个子集，例如“2013 年发生的所有交易”，然后使用它来生成 Beancount 提供的各种可用 report。

目前，Web 界面仅将预定义的过滤器列表作为“视图”提供。这些视图包括：

-   所有 transaction
-   在特定年份发生的 transaction
-   带有特定 tag 的 transaction
-   具有特定 payee 的 transaction
-   涉及至少一个具有特定名称组件的 account 的 transaction

目前，为了访问这些交易子集的 report，您需要使用 **bean-web** Web 界面，并在根全局页面中点击相关的关键词，这将使您进入该视图的一组 report。

## 报表 <a id="reports"></a>

将 transaction 录入到单一输入文件中的根本目的，在于允许你对数据的各个子集进行求和、过滤、聚合和整理，从而生成各种常见的 report。从 Beancount 生成 report 有三种不同的方式：使用 **bean-web** 浏览到某个视图，然后选择特定的 report（这是最简单的方式）；使用 **bean-report** 并提供所需 report 的名称（以及可能的 report 特定参数）；或者使用 **bean-query** 并通过指定 SQL 语句来请求数据。

Report 有时可以渲染为不同的文件格式。每种 report 类型都支持渲染为一系列常见格式，例如控制台文本、HTML 和 CSV。有些 report 直接以 Beancount 语法本身进行渲染，我们将这种格式名称简单地称为“beancount”。

目前可用的 report 类型有很多，未来还会有更多，因为路线图上的许多功能都涉及新的输出类型。本节概述了其中最常见的一些。使用 bean-report 可以查询你的安装版本所支持的完整列表：

    bean-report --help-reports

<table><tbody><tr class="odd"><td><em><strong>请注意！</strong></em> 目前，从 web 界面和从控制台可用的 report 集合是不同的，尽管存在一些重叠。在后续版本中，report 列表将得到统一，所有 report 都将通过 web 界面和控制台以多种数据格式（文本、CSV、HTML 以及可能的其他格式）提供。目前，我们将在下面的章节中分别记录这些内容。</td></tr></tbody></table>

### 余额报告<a id="balance-reports"></a>

所有余额报告都类似，它们都会生成一组 account 及其关联余额的表格：[\[output\]](http://furius.ca/beancount/examples/tutorial/balances.output)

    |-- Assets                               
    |   `-- US                               
    |       |-- BofA                         
    |       |   `-- Checking                       596.05 USD
    |       |-- ETrade                       
    |       |   |-- Cash                         5,120.50 USD
    |       |   |-- GLD                             70.00 GLD
    |       |   |-- ITOT                            17.00 ITOT
    |       |   |-- VEA                             36.00 VEA
    |       |   `-- VHT                            294.00 VHT
    |       |-- Federal                      
    |       |   `-- PreTax401k               
    |       |-- Hoogle                       
    |       |   `-- Vacation                       337.26 VACHR
    |       `-- Vanguard                     
    ...

以“成本”持有的商品余额会按其账面价值显示。（未实现收益，如果存在，会通过一个可选插件作为单独的 transaction 插入，如果在与 cost basis 相同的 account 中渲染，结果金额会与 cost basis 混合在一起。）

如果一个 account 的余额包含许多不同类型的货币（非“成本”持有的商品，例如美元、欧元、日元），每种货币都会单独打印在一行上。这可能会使余额列显得过于杂乱，并破坏 account 名称的垂直规律性。这在一定程度上是不可避免的妥协，但实际上，只有少数几种商品构成了用户账本的大多数：即本国的货币单位。因此，可以使用“`operating_currency`”选项将常用货币的金额拆分到单独的列中：

    option "operating_currency" "USD"
    option "operating_currency" "CAD"

如果您拥有多种此类货币，可以多次使用此选项（例如，我就是一个例子，因为我是外籍人士，在居住国和祖国都持有资产）。声明运营货币还有一个优点，即无需渲染货币名称，因此更容易导入电子表格。

最后，如果某些 account 尚未关闭，则被视为“活跃”。在过滤后的 transaction 集合中没有 transaction 的已关闭 account 将不会被渲染。

#### 试算平衡表 (`balances`)<a id="trial-balance-balances"></a>

[试算平衡表](http://en.wikipedia.org/wiki/Trial_balance) 报告简单地生成所有活跃 account 的最终余额表格，所有 account 垂直渲染。

所有余额的总和会在底部报告。与资产负债表不同，由于货币转换，它不一定总是平衡为零。（这相当于 Ledger 的 `bal` 报告。）

等效的 bean-query 命令是：

    SELECT account, sum(position) 
    GROUP BY account 
    ORDER BY account;

#### 资产负债表 (`balsheet`)<a id="balance-sheet-balsheet"></a>

[资产负债表](http://en.wikipedia.org/wiki/Balance_sheet) 是 Assets、Liabilities 和 Equity account 在特定时间点的余额快照。为了构建这样的报告，我们必须将其他 account 的余额转移到其中：

1.  计算该时间点 Income 和 Expenses account 的余额，

2.  插入 transaction，通过将这些 account 的余额转移到 Equity account (`Equity:Earnings:Current`) 来将其余额清零，

3.  在左侧渲染 Assets account 余额的树状结构，

4.  在右侧渲染 Liabilities account 的树状结构，

5.  在 Liabilities account 下方渲染 Equity account 的树状结构。

请参阅[介绍文档](the-double-entry-counting-method.md)查看示例。

请注意，Equity account 包括从 Income 和 Expenses account 报告的金额，通常也称为“净利润”。

此外，在实践中，我们进行*两次*转移，因为我们通常查看的是一个报告期间，并且我们希望区分在期间开始之前转移的净利润金额（`Equity:Earnings:Previous`）和期间本身转移的金额（`Equity:Earnings:Current`）。并且，为了处理货币转换，也会执行类似的成对转移（这是一个有点棘手的话题，但有一个很好的解决方案；如果您想要所有细节，请参阅[专用文档](http://furius.ca/beancount/doc/conversions)）。

等效的 bean-query 命令是：

    SELECT account, sum(position) 
    FROM CLOSE ON 2016-01-01 
    GROUP BY account ORDER BY account;      

#### 期初余额 (`openbal`)<a id="opening-balances-openbal"></a>

期初余额报告只是在报告期间开始时绘制的资产负债表。此报告仅对于代表一段时间（例如“2014 年”）的过滤条目列表有意义。资产负债表仅使用在过滤 transaction 时合成的汇总条目生成（请参阅[复式记账法文档](the-double-entry-counting-method.md)）。

所有余额的总和会在底部报告。与资产负债表不同，由于货币转换的原因，它不一定总是平衡为零。（这相当于 Ledger 的 `bal` 报告。）

等效的 bean-query 命令是：

    SELECT account, sum(position) 
    GROUP BY account 
    ORDER BY account;

#### 资产负债表 (`balsheet`)<a id="balance-sheet-balsheet"></a>

[资产负债表](http://en.wikipedia.org/wiki/Balance_sheet) 是 Assets、Liabilities 和 Equity 账户在特定时间点的余额快照。为了构建这样的报告，我们必须将其他账户的余额转移到该报告中：

1.  计算该时间点 Income 和 Expenses 账户的余额，

2.  插入 transaction，通过将这些账户的余额转移到 Equity 账户（`Equity:Earnings:Current`）来将其余额清零，

3.  在左侧渲染 Assets 账户余额的树状结构，

4.  在右侧渲染 Liabilities 账户的树状结构，

5.  在 Liabilities 账户下方渲染 Equity 账户的树状结构。

请参阅 [入门文档](the-double-entry-counting-method.md) 以获取示例。

请注意，Equity 账户包括从 Income 和 Expenses 账户报告的金额，这些金额通常也被称为“Net Income”。

此外，在实践中，我们进行*两次*转移，因为我们通常查看的是一个报告期间，并且我们希望区分在期间开始之前转移的 Net Income 金额（`Equity:Earnings:Previous`）和在该期间内转移的金额（`Equity:Earnings:Current`）。为了处理货币转换，也会执行类似的成对转移（这是一个有点棘手的话题，但有一个很好的解决方案；如果您想要所有细节，请参阅 [专用文档](http://furius.ca/beancount/doc/conversions)）。

等效的 bean-query 命令是：

    SELECT account, sum(position) 
    FROM CLOSE ON 2016-01-01 
    GROUP BY account ORDER BY account;      

#### 期初余额 (`openbal`)<a id="opening-balances-openbal"></a>

期初余额报告只是在报告期间开始时绘制的资产负债表。该报告仅对于代表一段时间（例如“2014 年”）的过滤条目列表有意义。资产负债表仅使用在过滤 transaction 时合成的汇总条目生成（请参阅 [复式记账法文档](the-double-entry-counting-method.md)）。

#### 利润表 (`income`)<a id="income-statement-income"></a>

[利润表](http://en.wikipedia.org/wiki/Income_statement) 列出了 Income 和 Expenses 账户的最终余额。它代表了这些账户中临时活动的汇总。如果说资产负债表是特定时间点的快照，那么利润表则是一个期间（在我们的情况下：一组经过筛选的 transaction）开始与结束之间的差异。活跃的 Income 账户余额显示在左侧，活跃的 Expenses 账户余额显示在右侧。请参阅 [入门文档](the-double-entry-counting-method.md) 以查看示例。

Income 和 Expenses 余额的总和之差即为 Net Income。

请注意，Income 和 Expenses 账户的初始余额应通过在该期间开始时发生的汇总 transaction 清零，因为我们只关心这些账户中的变化。

### 日记账报表 <a id="journal-reports"></a>

本节中的 report 以线性方式渲染 transaction 和其他 directive 的列表。

#### 日记账报表（`journal`）<a id="journal-journal"></a>

此 report 相当于机构提供的“账户对账单”，即列出至少有一个 posting 在该 account 中的 transaction 列表。这相当于 Ledger 的 register report（`reg`）。

你可以通过以下方式生成 journal report：

    bean-report myfile.beancount journal …

默认情况下，这会渲染*所有* transaction 的 journal，这通常不是你所需要的。选择特定的 account 进行渲染，如下所示：

    bean-report myfile.beancount journal -a Expenses:Restaurant

目前，“`-a`” 选项仅接受完整的 account 名称或其中一个父 account 的名称。最终我们将扩展它以处理表达式。

##### 按 cost 渲染 <a id="rendering-at-cost"></a>

右侧的数字列显示所选 account 的 posting 带来的变化。请注意，仅渲染影响给定 account 的 posting 的余额。

Change 列渲染受影响单位的变化。例如，如果选中此 posting：

      Assets:Investments:Apple      2 AAPL {402.00 USD}

报告的 change 值将为“`2 AAPL`”。如果你希望以 cost 渲染值，请使用“`--at-cost`”或“`-c`”选项，在这种情况下，它将渲染“`804.00 USD`”而不是前者。

没有“market value”选项。未实现收益会自动由“`beancount.plugins.unrealized`”插件插入到历史记录末尾。请参阅该插件的选项以插入其未实现收益。

请注意，如果所选 posting 的总和为零，change 列中不会渲染任何金额。

##### 增加余额列 <a id="adding-a-balance-column"></a>

如果你想添加一列来汇总报告变化的 running balance，请使用“`--render-balance`”或“`-b`”选项。这并不总是有意义，因此是否想要 running balance 由你决定。

##### 字符宽度 <a id="character-width"></a>

默认情况下，report 的宽度将尽可能宽，以适配你的终端。使用“-w”选项将宽度限制为特定字符数。

##### precision <a id="precision"></a>

数字渲染的小数位数可以通过“`--precision`”或“`-k`”指定。

##### 三种详略（compact / normal / verbose） <a id="compact-normal-or-verbose"></a>

在正常操作下，Beancount 会在 transaction 之间渲染一个空行。这有助于区分涉及多种货币的 transaction，因为它们会渲染在不同的行上。如果你希望更紧凑的渲染，请使用“`--compact`”或“`-x`”选项。

另一方面，如果你希望在 transaction 行下方渲染受影响的 posting，请使用“`--verbose`”或“`-X`”选项。

##### 摘要 <a id="summary"></a>

以下是其参数的摘要：

    optional arguments:
      -h, --help            show this help message and exit
      -a ACCOUNT, --account ACCOUNT
                            Account to render
      -w WIDTH, --width WIDTH
                            The number of characters wide to render the report to
      -k PRECISION, --precision PRECISION
                            The number of digits to render after the period
      -b, --render-balance, --balance
                            If true, render a running balance
      -c, --at-cost, --cost
                            If true, render values at cost
      -x, --compact         Rendering compactly
      -X, --verbose         Rendering verbosely

##### 等价 SQL query <a id="equivalent-sql-query"></a>

等效的 bean-query 命令是：

    SELECT date, flag, description, account, cost(position), cost(balance);

#### 换算（`conversions`） <a id="conversions-conversions"></a>

此 report 列出了由所选 transaction 产生的货币转换总额。（大多数人不需要此功能。）

#### document 报表（`documents`） <a id="documents-documents"></a>

此 report 生成一个 HTML 列表，列出在账本中发现的所有外部文档，这些文档可能来自显式的 directive，也可能来自自动查找文档并将其添加到 transaction 流中的插件。

### holdings 报表 <a id="holdings-reports"></a>

这些 report 生成按 cost 持有的资产的聚合数据。

#### holdings 与聚合（`holdings*`） <a id="holdings-aggregations-holdings"></a>

此 report 生成账本中所有持仓的详细列表。您可以使用 “-g” 选项按商品和 account 生成聚合数据。

#### 净资产（`networth`） <a id="net-worth-networth"></a>

此 report 生成账本净资产（权益）的简短摘要，分别以每种运营货币表示。

### 其他报告类型<a id="other-report-types"></a>

#### 现金<a id="cash"></a>

此报告以非 cost 持有的商品（即现金）显示余额：

    bean-report example.beancount cash -c USD

    Account                         Units  Currency  Cost Currency  Average Cost  Price  Book Value  Market Value

    --------------------------  ---------  --------  -------------  ------------  -----  ----------  ------------

    Assets:US:BofA:Checking        596.05       USD            USD                           596.05        596.05

    Assets:US:ETrade:Cash        5,120.50       USD            USD                         5,120.50      5,120.50

    Assets:US:Hoogle:Vacation      337.26     VACHR                                                              

    Assets:US:Vanguard:Cash         -0.02       USD            USD                            -0.02         -0.02

    Liabilities:US:Chase:Slate  -2,891.85       USD            USD                        -2,891.85     -2,891.85

    --------------------------  ---------  --------  -------------  ------------  -----  ----------  ------------

该报告允许将所有货币转换为一种通用货币（在上面的示例中，“将所有内容转换为 USD”）。还有一个选项仅报告运营货币。我使用此功能来获取所有未投资 cash 的概览。

#### 价格（`prices`）<a id="prices-prices"></a>

此报告以报价货币表示基础货币的价格点列表。列表按日期排序。您也可以以 beancount 格式输出此表格。这便于将价格数据库保存到文件中，然后将其合并并加载到另一个输入文件中。

#### 统计信息（`stats`）<a id="statistics-stats"></a>

此报告仅提供有关已解析条目的各种统计信息。

#### 更新活动（`activity`）<a id="update-activity-activity"></a>

此表格为每个 account 显示最后一条条目的日期。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
