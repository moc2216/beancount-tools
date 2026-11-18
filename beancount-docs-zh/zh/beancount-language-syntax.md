> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/beancount_language_syntax/

# Beancount 语言语法<a id="title"></a>

[Martin Blais](mailto:blais@furius.ca)，更新于：2016 年 4 月

[http://furius.ca/beancount/doc/syntax](http://furius.ca/beancount/doc/syntax)

[简介](#introduction)

[语法概览](#syntax-overview)

> [Directive](#directives)
>
> [Directive 的顺序](#ordering-of-directives)
>
> [Account](#accounts)
>
> [商品 / 货币](#commodities-currencies)
>
> [字符串](#strings)
>
> [注释](#comments)

[Directive](#directives-1)

> [Open](#open)
>
> [Close](#close)
>
> [Commodity](#commodity)
>
> [Transaction](#transactions)
>
> [元数据](#metadata)
>
> [收款方与摘要](#payee-narration)
>
> [Cost 与 Price](#costs-and-prices)
>
> [平衡规则 - Posting 的“权重”](#balancing-rule---the-weight-of-postings)
>
> [减少持仓](#reducing-positions)
>
> [金额 Interpolation](#amount-interpolation)
>
> [标签](#tags)
>
> [标签栈](#the-tag-stack)
>
> [链接](#links)
>
> [Balance assertion](#balance-assertions)
>
> [多种商品](#multiple-commodities)
>
> [Lot 的聚合](#lots-are-aggregated)
>
> [对父级 Account 的检查](#checks-on-parent-accounts)
>
> [Close 之前](#before-close)
>
> [Pad](#pad)
>
> [未使用的 Pad directive](#unused-pad-directives)
>
> [商品](#commodities)
>
> [Cost basis](#padding-cost-basis)
>
> [多次 Pad](#multiple-paddings)
>
> [备注](#notes)
>
> [文档](#documents)
>
> [来自目录的文档](#documents-from-a-directory)
>
> [Price](#prices)
>
> [来自 Posting 的 Price](#prices-from-postings)
>
> [同一天的 Price](#prices-on-the-same-day)
>
> [事件](#events)
>
> [查询](#query)
>
> [Custom](#custom)

[元数据](#metadata-1)

[选项](#options)

> [运营货币](#operating-currencies)

[插件](#plugins)

[包含](#includes)

[接下来是什么？](#whats-next)

## 简介<a id="introduction"></a>

这是 Beancount 语言的用户手册，Beancount 是一个命令行复式记账系统。Beancount 定义了一种计算机语言，允许你在文本文件中录入财务 transaction，并从中提取各种 report。它是一个通用的计数工具，支持多种货币、以 cost 持有的商品（例如股票），甚至允许你追踪一些不寻常的事物，如休假时间、航空里程和奖励积分，以及你可能想要计数的任何其他东西，甚至豆子。

本文档介绍了 Beancount 的语法以及理解其如何执行计算所需的一些技术细节。本文档*不*提供[复式记账法的介绍](the-double-entry-counting-method.md)、[动机](command-line-accounting-in-context.md)、在输入文件中[录入 transaction 的示例和指南](command-line-accounting-cookbook.md)，也不介绍如何[运行工具](running-beancount-and-generating-reports.md)。这些主题有[各自专门文档](beancount-user-manual.md)，建议在深入阅读本用户手册之前先浏览那些文档。本手册涵盖了使用 Beancount 的技术细节。

## 语法概览<a id="syntax-overview"></a>

### directive <a id="directives"></a>

Beancount 是一种声明式语言。输入由一个文本文件组成，其中主要包含一系列 **directives**（或 **entries**（我们在代码和文档中互换使用这两个术语））；此外，还有用于定义各种 **options** 的语法。每个 directive 都以一个关联的 *date* 开头，该日期决定了 directive 生效的时间点，以及一个 *type*，它定义了该 directive 代表哪种类型的事件。所有 directive 都以如下形式的语法开头：

    YYYY-MM-DD <type> …

其中 YYYY 是年份，MM 是数字月份，DD 是数字日期。所有数字都是必需的，例如，2007 年 5 月 7 日应写作 “2007-05-07”，包括其零。Beancount 支持国际 ISO 8601 标准日期格式，使用连字符（例如，“2014-02-03”），或使用相同顺序的斜杠（例如，“2014/02/03”）。

以下是一些示例 directives，仅供您了解其风格：

    2014-02-03 open Assets:US:BofA:Checking

    2014-04-10 note Assets:US:BofA:Checking "Called to confirm wire transfer."

    2014-05-02 balance Assets:US:BofA:Checking   154.20 USD

解析后的输入文件的最终产物是一个简单的 entries 列表，以数据结构的形式存在。Beancount 中的所有操作都是针对这些 entries 执行的。

每种特定的 directive 类型都在下面的章节中进行了文档说明。

#### directive 的顺序 <a id="ordering-of-directives"></a>

directives 的声明顺序并不重要。实际上，entries 在解析后、处理前会按时间顺序重新排序。这是该语言的一个重要特性，因为它允许您以任何喜欢的方式组织输入文件，而无需担心影响 directives 的含义。

除了 transactions 之外，每个 directive 都被假定发生在每一天的 *beginning*（开始）。例如，您可以声明一个账户在其第一笔 transaction 的同一天开立：

    2014-02-03 open Assets:US:BofA:Checking

    2014-02-03 * "Initial deposit"
      Assets:US:BofA:Checking         100 USD
      Assets:Cash                    -100 USD

然而，如果您假设立即关闭该账户，则不能在同一天声明其关闭，您必须将日期向后调整，在 2/4 声明关闭：

    2014-02-04 close Assets:US:BofA:Checking

这也解释了为什么 balance assertions 会在同一日期发生的任何 transactions 之前进行验证。这是为了保持一致性。

### 账户<a id="accounts"></a>

Beancount 在 account 中累积商品。这些 account 的名称无需在文件中被使用之前进行声明，仅凭其语法即可被识别为“account”[^1]。account 名称是由冒号分隔的组件列表，其第一个组件必须是以下五种 account 类型之一：

    Assets Liabilities Equity Income Expenses

account 名称的每个组件以大写字母或数字开头，后跟字母、数字或连字符（-）字符。不允许使用其他任何字符。

以下是一些真实的 account 名称示例：

    Assets:US:BofA:Checking
    Liabilities:CA:RBC:CreditCard
    Equity:Retained-Earnings
    Income:US:Acme:Salary
    Expenses:Food:Groceries

在输入文件中看到的所有 account 名称的集合隐式地定义了一个 account 层级结构（有时称为**chart-of-accounts**），类似于文件系统中文件的组织方式。例如，以下 account 名称：

    Assets:US:BofA:Checking
    Assets:US:BofA:Savings
    Assets:US:Vanguard:Cash
    Assets:US:Vanguard:RGAGX
    Assets:Receivables

隐式地声明了一个如下所示的 account 树：

    `-- Assets
        |-- Receivables
        `-- US
            |-- BofA
            |   |-- Checking
            |   `-- Savings
            `-- Vanguard
                |-- Cash
                `-- RGAGX

我们可以说“`Assets:US:BofA`”是“`Assets:US:BofA:Checking`”的父 account，而后者是前者的子 account。

### 商品 / 货币<a id="commodities-currencies"></a>

账户包含**货币**，我们有时也称之为**商品**（这两个术语可以互换使用）。与账户名称类似，货币名称通过其语法来识别，但与账户名称不同的是，它们无需在使用前声明）。货币的语法是一个全大写的单词，例如：

    USD
    CAD
    EUR
    MSFT
    IBM
    AIRMILE

（从技术上讲，货币名称最长可达 24 个字符，必须以大写开头，必须以大写或数字结尾，且其余字符只能是大写字母、数字或以下标点符号：“'.\_-”（撇号、句点、下划线、连字符）。前三个可能会让你联想到现实世界中的货币（美元、加元、欧元）；接下来的两个是股票交易代码（微软和 IBM）。而最后一个：奖励积分（航空里程）。Beancount 并不知晓这些概念；从它的角度来看，所有这些工具都被同等对待。不存在任何预先存在的货币的内置概念。这些货币名称只是可以放入账户并在与这些账户相关的库存中累积的“事物”的名称。

所有商品都被同等对待，没有“特殊”的货币单位，这一点颇具优雅之处：Beancount 本质上是一个多货币系统。如果你和我们中的许多人一样是外籍人士，你的生活分布在两到三个大洲之间，你会对此表示赞赏。你可以毫无问题地处理国际账户账簿。

你对货币的使用可以变得非常有创意：例如，你可以为你的家创建一个货币（例如 `MYLOFT`），一个用于计算累积休假时数的货币（`VACHR`），或者一个用于计算每年允许向退休账户缴纳潜在贡献额的货币（`IRAUSD`）。你实际上可以通过这种方式解决许多问题。[食谱](command-line-accounting-cookbook.md) 描述了许多此类具体示例。

Beancount 不支持美元符号语法，例如 “$120.00”。你应该始终在输入文件中使用货币名称。这使得输入更加规范，是一种设计选择。对于货币单位，我建议你将标准的 [ISO 4217 货币代码](http://en.wikipedia.org/wiki/ISO_4217#Active_codes) 作为参考；这些代码很快就会变得熟悉。然而，如上所述，你可以在货币名称中包含一些其他字符，如下划线（_）、连字符（-）、句点（.）或撇号（‘），但不能包含空格。

最后，你会注意到存在一个 “`commodity`” directive，可用于声明货币。这是完全可选的：货币在你使用时即产生。该 directive 的目的仅仅是为其附加元数据。

### 字符串<a id="strings"></a>

每当我们需要在条目中插入自由文本时，应使用双引号将其包围。这主要适用于 payee 和 narration 字段；基本上，任何不是日期、数字、货币或 account 名称的内容都适用。

字符串可以跨多行拆分。（包含多行的字符串将包含其换行符，在渲染时需要相应地处理这些换行符。）

### 注释<a id="comments"></a>

Beancount 输入文件并不旨在仅包含你的 directive：你可以自由地在其中放置注释和标题来组织文件。任何在字符 “;” 之后的行内文本都会被忽略，例如这样的文本：

    ; I paid and left the taxi, forgot to take change, it was cold.
    2015-01-01 * "Taxi home from concert in Brooklyn"
      Assets:Cash      -20 USD  ; inline comment
      Expenses:Taxi

如果你愿意，可以使用一个或多个 “;” 字符。如果你想输入较大的注释文本，可以在所有行前添加。如果你希望注释文本被解析并在你的日志中渲染，请参阅本文档其他地方的 Note directive。

（在某个时间点，任何未以有效的 Beancount 语法 directive（例如以日期开头）开始的行都会被静默忽略。这在 2019 年某时发生了变化。TODO(blais): 重新审视。）

这样，你可以插入标记以用于各种大纲模式来组织你的文件，例如 Emacs 中的 [org-mode](http://orgmode.org/)。例如，你可以按机构组织你的输入文件，如下所示，并独立地折叠和展开每个部分：

    * Banking
    ** Bank of America

    2003-01-05 open Assets:US:BofA:Checking
    2003-01-05 open Assets:US:BofA:Savings

    ;; Transactions follow …

    ** TD Bank

    2006-03-15 open Assets:US:TD:Cash

    ;; More transactions follow …

不匹配的行将被简单地忽略。

给访问 Ledger 用户的提示：在 Ledger 中，“;” 既用于标记注释，也用于将 “Ledger tags”（Beancount metadata）附加到 posting 上。在 Beancount 中并非如此。在 Beancount 中，注释始终只是注释。Metadata 有其自己的独立语法。

## 指令<a id="directives-1"></a>

如需快速参考和指令语法概览，请参阅[语法速查表](beancount-cheat-sheet.md)。

### open（开户） <a id="open"></a>

所有 account 都必须声明为“open”才能接受 posting 到其中的金额。你可以通过编写如下形式的 directive 来实现：

    2014-05-01 open Liabilities:CreditCard:CapitalOne     USD

Open directive 的一般格式为：

    YYYY-MM-DD open Account [ConstraintCurrency,...] ["BookingMethod"]

逗号分隔的可选 constraint currency 列表强制要求 posting 到该 account 的所有变更均以所声明货币之一为单位。建议指定 currency constraint：你为 Beancount 提供的约束越多，就越不容易犯数据录入错误，因为如果你犯了错误，它会向你发出警告。

每个 account 都应声明在某个特定日期“opened”，该日期必须早于（或等于）第一个 posting 金额到该 account 的 transaction 的日期。为了明确起见：Open directive 不必在*文件中*出现在 transaction 之前，而是 Open directive 的*日期*必须早于 posting 到该 account 的日期。文件中声明的顺序并不重要。因此，例如，这是一个合法的输入文件：

    2014-05-05 * "Using my new credit card"
      Liabilities:CreditCard:CapitalOne         -37.45 USD
      Expenses:Restaurant

    2014-05-01 open Liabilities:CreditCard:CapitalOne     USD
    1990-01-01 open Expenses:Restaurant

打开 account 的另一个可选声明是“booking method”，即当减少 lot 导致从库存中匹配 lot 的选择存在歧义时（0 个、2 个或多个 lot 匹配）将被调用的算法。目前，它可以取的可能值有：

-   **STRICT**：lot 规格必须精确匹配一个 lot。这是默认方法。如果调用了此 booking method，它将简单地引发一个错误。这确保你的输入文件显式选择了所有匹配的 lot。

-   **NONE**：不执行 lot 匹配。任何 price 的 lot 都会被接受。允许同一 currency 的 lot 数量出现正数和负数的混合。（这与 Ledger 处理匹配的方式类似……它忽略匹配。）

TODO(blais): 上述列表已过时。

### close（销户） <a id="close"></a>

与 Open directive 类似，存在一个 Close directive，可用于告知 Beancount 某个 account 已变为非活动状态，例如：

    ; Closing credit card after fraud was detected.
    2016-11-28 close Liabilities:CreditCard:CapitalOne 

Close directive 的一般格式为：

    YYYY-MM-DD close Account

该 directive 有几种用途：

-   如果在关闭日期之后向该 account 记录 posting，会引发错误消息（这是一种健全性检查）。这有助于避免数据录入错误。

-   它有助于 report 代码确定哪些 account 仍处于活动状态，并过滤掉报告期间之外已关闭的 account。随着账本随时间积累大量数据，这一点尤其有用，因为会有 account 停止存在，而你并不希望在它们关闭后的多年报告中看到它们。

请注意，Close directive 目前不会生成隐式的零 balance assertion。你可能希望在关闭日期之前添加一个，以确保该 account 以空内容正确关闭。

目前，一旦 account 被关闭，你就无法在该日期之后重新打开它。（当然，你可以删除或注释掉关闭它的 directive。）最后，代码中存在实用函数，允许你确定在特定日期哪些 account 是打开的。我强烈建议你在 account 实际关闭时将其关闭，这将使你的账本更加整洁。

### commodity <a id="commodity"></a>

存在一个 “Commodity” directive，可用于声明货币、金融工具或商品（在 Beancount 中，这些是同一事物的不同名称）：

    1867-07-01 commodity CAD

Commodity directive 的一般格式为：

    YYYY-MM-DD commodity Currency

此 directive 是后期加入的，且完全可选：你可以直接使用商品，而无需通过这种方式正式声明它们。此 directive 的目的是为其附加特定于商品的元数据字段，以便后续由插件收集。例如，你可能希望为每个商品提供一个较长的描述性名称，例如为商品 “CHF” 提供 “Swiss Franc”，或为 “HOOL” 提供 “Hooli Corporation Class C Shares”，如下所示：

    1867-07-01 commodity CAD
      name: "Canadian Dollar"
      asset-class: "cash"

    2012-01-01 commodity HOOL
      name: "Hooli Corporation Class C Shares"
      asset-class: "stock"

例如，插件随后可以收集元数据属性名称，并按资产类别执行某些聚合操作。

你可以为商品使用任何日期……但一个相关的日期是其创建或引入的日期，例如加元最早于 1867 年引入，ILS（新以色列谢克尔）自 1986-01-01 起使用。对于公司而言，公司成立和股份创建的日期可能是一个合适的日期。由于此 directive 的主要目的是收集每个商品的信息，因此你选择的具体日期并不那么重要。

重复声明同一商品是一个错误。

### transaction <a id="transactions"></a>

Transaction 是账本中最常见的 directive 类型。它们与其他 directive 略有不同，因为后面可以跟一个 posting 列表。以下是一个示例：

    2014-05-05 txn "Cafe Mogador" "Lamb tagine with wine"
      Liabilities:CreditCard:CapitalOne         -37.45 USD
      Expenses:Restaurant

与其他所有 directive 一样，transaction directive 以 *YYYY-MM-DD* 格式的日期开头，随后是 directive 名称，在本例中为“`txn`”。然而，由于 transaction 是我们复式记账系统的*raison d’être*（存在理由），并且是 Beancount 输入文件中应出现的最常见类型的 directive，我们将其作为特殊情况处理，允许用户省略“txn”关键字，仅使用一个 flag 代替：

    2014-05-05 * "Cafe Mogador" "Lamb tagine with wine"
      Liabilities:CreditCard:CapitalOne         -37.45 USD
      Expenses:Restaurant

Flag 用于指示 transaction 的状态，而 flag 的具体含义由您自行定义。我们建议采用以下解释：

-   *: 已完成的 transaction，金额已知，“这看起来是正确的。”

-   !: 未完成的 transaction，需要确认或修改，“这看起来是不正确的。”

TODO(blais): 在此处列出所有有效 flag 的完整列表 [from the parser](https://github.com/beancount/beancount/blob/master/beancount/parser/lexer.l#L134)。

在第一个使用“txn”使 transaction 未标记 flag 的示例中，默认 flag（“\*”）将被设置在 transaction 对象上。（我几乎总是使用“\*”变体，而从不使用关键字形式，它主要存在于那里以与其他所有 directive 格式保持一致。）

如果您想特别标记 transaction 的某一条腿（leg），也可以将 flag 附加到 posting 本身：

    2014-05-05 * "Transfer from Savings account"
      Assets:MyBank:Checking            -400.00 USD
      ! Assets:MyBank:Savings

这在去重 transaction 的中间阶段很有用（有关更多详细信息，请参阅 [Getting Started](getting-started-with-beancount.md) 文档）。

Transaction directive 的一般格式为：

    YYYY-MM-DD [txn|Flag] [[Payee] Narration] [Flag] Account Amount [{Cost}] [@ Price] [Flag] Account Amount [{Cost}] [@ Price] ...

第一行之后的行用于“Postings”。您可以向一个 transaction 附加任意数量的 posting。例如，工资条目可能如下所示：

    2014-03-19 * "Acme Corp" "Bi-monthly salary payment"
      Assets:MyBank:Checking             3062.68 USD     ; Direct deposit
      Income:AcmeCorp:Salary            -4615.38 USD     ; Gross salary
      Expenses:Taxes:TY2014:Federal       920.53 USD     ; Federal taxes
      Expenses:Taxes:TY2014:SocSec        286.15 USD     ; Social security
      Expenses:Taxes:TY2014:Medicare       66.92 USD     ; Medicare
      Expenses:Taxes:TY2014:StateNY       277.90 USD     ; New York taxes
      Expenses:Taxes:TY2014:SDI             1.20 USD     ; Disability insurance

“Postings”中的 Amount 也可以是使用 `( ) * / - +` 的算术表达式。例如，

    2014-10-05 * "Costco" "Shopping for birthday"
      Liabilities:CreditCard:CapitalOne         -45.00          USD
      Assets:AccountsReceivable:John            ((40.00/3) + 5) USD
      Assets:AccountsReceivable:Michael         40.00/3         USD
      Expenses:Shopping

Posting 的关键且唯一的约束是它们的 balance 金额之和必须为零。这将在下文详细解释。

#### metadata <a id="metadata"></a>

还可以将 metadata 附加到 transaction 和/或其任何 posting，因此完全通用的格式为：

    YYYY-MM-DD [txn|Flag] [[Payee] Narration] [Key: Value] ... [Flag] Account Amount [{Cost}] [@ Price] [Key: Value] ... [Flag] Account Amount [{Cost}] [@ Price] [Key: Value] ... ...

请参阅下文关于 metadata 的专门章节。

#### payee 与 narration <a id="payee-narration"></a>

Transaction 可以有一个可选的“payee”和/或“narration”。在上面的第一个示例中，payee 是“Cafe Mogador”，narration 是“Lamb tagine with wine”。

Payee 是一个表示参与 transaction 的外部实体的字符串。Payee 有时对于将金额记入 Expense account 的 transaction 很有用，其中 account 会累积来自多家企业的某一类费用。一个好的例子是“`Expenses:Restaurant`”，它将包含一个人可能访问的各种餐厅的所有 posting。

Narration 是您编写的 transaction 描述。它可以是关于背景、陪同您的人、关于您购买的产品的一些注释……无论您想让它是什么。它是供您插入任何您喜欢的内容的。我喜欢在对账时插入注释，这很快，我可以在以后参考我的注释，例如，回答“去年冬天我和 Andreas 在西边访问的那家很棒的小寿司店叫什么名字？”这个问题。

如果在 transaction 行上放置一个单独的字符串，它将成为该 transaction 的 narration：

    2014-05-05 * "Lamb tagine with wine"
       … 

如果你只想设置 payee，请提供一个空的 narration 字符串：

    2014-05-05 * "Cafe Mogador" ""
       … 

你也可以省略其中任意一个（但你必须提供 flag）：

    2014-05-05 *
       …

***给 Ledger 用户的注意。*** Ledger 没有独立的 narration 和 payee 字段，它只有一个字段，该字段由 “Payee” 元数据标签引用，而 narration 最终会保存在一个注释中（即“persistent note”）。在 Beancount 中，Transaction 对象简单地具有两个字段：payee 和 narration，其中 payee 的值经常恰好为空。

关于何时以及如何使用 payee 的更深入讨论，请参阅 [Payees, Subaccounts, and Assets](http://furius.ca/beancount/doc/payee)。

#### cost 与 price <a id="costs-and-prices"></a>

Posting 表示存入或从 account 中提取的单一金额。最简单的 posting 类型仅包含其金额：

    2012-11-03 * "Transfer to pay credit card"
      Assets:MyBank:Checking            -400.00 USD
      Liabilities:CreditCard             400.00 USD

如果你将金额从另一种货币转换而来，你必须提供一个转换率以使 transaction 平衡（参见下一节）。这是通过为 posting 附加一个 “price” 来实现的，该 price 即为转换率：

    2012-11-03 * "Transfer to account in Canada"
      Assets:MyBank:Checking            -400.00 USD @ 1.09 CAD
      Assets:FR:SocGen:Checking          436.01 CAD

你也可以使用 “@@” 语法来指定总 cost：

    2012-11-03 * "Transfer to account in Canada"
      Assets:MyBank:Checking            -400.00 USD @@ 436.01 CAD
      Assets:FR:SocGen:Checking          436.01 CAD

Beancount 将自动计算单位 price，即 1.090025 CAD（请注意，最后两个示例中的 precision 会有所不同）。

在 transaction 之后，我们并不关心追踪存入 account 的 USD 单位的汇率；这些 “USD” 单位只是被简单地存入。从某种意义上说，它们被转换时的汇率已被遗忘。

然而，某些存入 account 的商品必须以 “held at cost” 的方式持有。当你希望追踪这些商品的 *cost basis* 时，就会发生这种情况。典型的用例是 investment，例如当你将股票股份存入 account 时。在这种情况下，你希望将存入商品的获取 cost 附加到单位上，以便当你稍后移除这些单位（即卖出）时，能够根据 cost 识别出应移除哪些单位，从而控制税收影响（并避免错误）。你可以想象，account 中的每个单位都附带了一个 cost basis。这将使我们能够自动计算资本利得。

为了指定对 account 的 posting 应以特定 cost 持有，请在花括号中包含 cost：

    2014-02-11 * "Bought shares of S&P 500"
      Assets:ETrade:IVV                10 IVV {183.07 USD}
      Assets:ETrade:Cash         -1830.70 USD

这是更深入讨论的主题。请参阅 “[How Inventories Work](how-inventories-work.md)” 和 “[Trading with Beancount](trading-with-beancount.md)” 文档，以深入了解这些主题。

最后，你可以在一个 posting 中同时包含 cost 和 price：

    2014-07-11 * "Sold shares of S&P 500"
      Assets:ETrade:IVV               -10 IVV {183.07 USD} @ 197.90 USD
      Assets:ETrade:Cash          1979.00 USD
      Income:ETrade:CapitalGains  -148.30 USD

Price 仅用于在价格数据库中插入一条 price 条目（参见下文 Price 部分）。本文档的 Balancing Postings 部分对此进行了更详细的讨论。

***重要说明。*** 指定为每股或总 price 或 cost 的金额*始终是无符号的*。使用负号或负 cost 是错误的，如果你尝试这样做，Beancount 将引发错误。

#### 配平规则：posting 的“weight” <a id="balancing-rule---the-weight-of-postings"></a>

复式记账法的一个关键方面是确保其所有 posting 上的金额总和在所有货币中等于零。这是产生会计等式的核心、不可协商的条件，并使得可以过滤任何 transaction 子集并绘制平衡为零的资产负债表。

但是，对于不同类型的单位，以及前面介绍的 price 转换和 “held at cost” 的单位，这一切意味着什么？

很简单：我们制定了一条简单明了的规则，用于从每个 posting 中获取金额和货币，以便将它们一起平衡。我们称这为 posting 的 “weight”，或平衡金额。以下是使用四种可能的 cost/price 组合从 posting 中推导出的 weight 的简短示例：

YYYY-MM-DD
      Account       10.00 USD                       -> 10.00 USD
      Account       10.00 CAD @ 1.01 USD            -> 10.10 USD
      Account       10 SOME {2.02 USD}              -> 20.20 USD
      Account       10 SOME {2.02 USD} @ 2.50 USD   -> 20.20 USD

以下是其计算方式的说明：

1.  如果 posting **仅包含金额**而没有 cost，则该 posting 的余额金额即为该 posting 上的金额和货币。使用上一节中的第一个示例，金额为 -400.00 USD，它与第二笔分录的 400.00 USD 相抵。

2.  如果 posting **仅包含 price**，则将 price 乘以单位数量，并使用 price 的货币。在前一节的第二个示例中，即 -400.00 USD x 1.09 CAD(/USD) = -436.00 CAD，这与另一笔 436.00 CAD 的 posting 相抵[^2]。

3.  如果 posting **包含 cost**，则将 cost 乘以单位数量，并使用 cost 的货币。在前一节的第三个示例中，即 10 IVV x 183.08 USD(/IVV) = 1830.70 USD。这与现金分录的 -1830.70 USD 相抵，因此一切正常。

4.  最后，如果 posting **同时包含 cost 和 price**，我们简单地忽略 price。这个可选的 price 稍后用于在内存价格数据库中生成条目，但在平衡计算中完全不被使用。

根据此规则，你应该能够轻松平衡所有 transaction。此外，此规则使得 Beancount 能够自动为你计算资本利得（详见 [Trading with Beancount](trading-with-beancount.md)）。

#### 减少 position <a id="reducing-positions"></a>

当你向 account 中的持仓发布*减少*（reduction）时，该减少必须始终与现有的 lot 匹配。例如，如果一个 account 持有 3200 USD，而一个 transaction 向该 account 发布 -1200 USD 的变更，则 1200 USD 与现有的 3200 USD 匹配，结果是单个 2000 USD 的持仓。这对于负值也适用。例如，如果一个 account 有 -1300 USD 的余额，而你向它发布 +2000 USD 的变更，你将获得 700 USD 的余额。

无论 account 类型如何，向 account 发布的变更都可能导致正或负的余额；对于简单商品金额（即没有关联 cost 的金额）的余额没有限制。例如，虽然 Assets account *通常*具有正余额，Liabilities account *通常*具有负余额，但你可以合法地将 Assets account 贷记为负余额，或将 Liabilities account 借记为正余额。这是因为在现实世界中确实会发生这种情况：你可能开具了过多的支票，从而从你的银行支票账户获得临时信用（通常伴随着高昂的“透支”费用），或者错误地两次支付了信用卡余额。

对于按 cost 持有的商品，posting 的 cost 规范必须与 transaction 应用前库存中持有的某个 lot 匹配。lot 列表会被收集，并与 posting 中 {...} 部分的规范进行匹配。例如，如果你提供了 cost，只有那些 cost 匹配的 lot 才会保留。如果你提供了日期，只有那些日期匹配的 lot 才会保留。你还可以使用标签。如果你提供了 cost 和日期，这两者都会与候选 lot 列表进行匹配。这本质上是对 lot 列表的一个过滤器。

如果过滤后的列表结果为单个 lot，则选择该 lot 进行减少。如果列表结果为多个 lot，但被减少的总金额等于这些 lot 中的总金额，则所有这些 lot 都会由该 posting 进行减少。

例如，如果你过去有以下 transaction：

    2014-02-11 * "Bought shares of S&P 500"
      Assets:ETrade:IVV                20 IVV {183.07 USD, "ref-001"}
      … 

    2014-03-22 * "Bought shares of S&P 500"
      Assets:ETrade:IVV                15 IVV {187.12 USD}
      … 

以下每个减少操作都是明确的：

    2014-05-01 * "Sold shares of S&P 500"
      Assets:ETrade:IVV               -20 IVV {183.07 USD}
      … 

    2014-05-01 * "Sold shares of S&P 500"
      Assets:ETrade:IVV               -20 IVV {2014-02-11}
      … 

    2014-05-01 * "Sold shares of S&P 500"
      Assets:ETrade:IVV               -20 IVV {"ref-001"}
      … 

    2014-05-01 * "Sold shares of S&P 500"
      Assets:ETrade:IVV               -35 IVV {}
      … 

然而，以下操作将是模糊的：

    2014-05-01 * "Sold shares of S&P 500"
      Assets:ETrade:IVV               -20 IVV {}
      …

如果多个 lot 与减少 posting 匹配，且其数量并非全部，则我们处于*模糊匹配*的情况。此时，将调用该 account 的*booking 方法*。存在多种 booking 方法，但默认情况下，所有 account 均设置为使用“STRICT” booking 方法。该方法在模糊情况下会直接发出错误。

您可以将 account 的 booking 方法设置为“FIFO”，以指示 Beancount 选择最旧的 lot。或者设置为“LIFO”以选择最新（最年轻）的 lot。这将自动选择所有必要的匹配 lot 以满足减少需求。

<table><tbody><tr class="odd"><td><em><strong>请注意！</strong></em> 要求日期匹配的问题将在近期得到更合理的处理。有关此即将进行的更改的详细信息，请参阅 <a href="a_proposal_for_an_improvement_on_inventory_booking.md">关于改进库存预订的提案</a>。</td></tr></tbody></table>

对于此类 posting，导致单位数量为负数的变化通常是不可能的。Beancount 目前不允许持有以 cost 计价的负数商品单位。例如，仅包含此 transaction 的输入将失败：

    2014-05-23 *
      Assets:Investments:MSFT        -10 MSFT {43.40 USD}
      Assets:Investments:Cash     434.00 USD

如果允许这样做，这将导致 MSFT 的余额为 -10 个单位。另一方面，如果该 account 在 5/23 持有 12 个单位的 MSFT，cost 为 43.40 USD，则该 transaction 将正常记账，将现有的 12 个单位减少到 2 个。最常见的错误是，该 account 将持有 10 个或更多单位的 MSFT，但其*不同的 cost*，而用户指定了错误的 cost 值。例如，如果该 account 持有 20 MSFT {42.10 USD} 的正余额，上述 transaction 仍将失败，因为没有 10 个或更多单位的 MSFT 以 43.40 USD 的 cost 可供移除。

出于以下几个原因，强制执行此约束：

-   股票单位的数据输入错误并不罕见，它们对 Ledger 的正确性有重要的负面影响——金额通常很大——并且通常会触发此约束的错误。因此，错误检查是检测此类错误的有用方法。

-   以 cost 计价的负数单位相当罕见。您可能根本不需要它们。例外情况包括：股票卖空、持有期货合约价差，以及取决于您如何记账，货币交易中的空头头寸。

这就是为什么默认启用此检查的原因。

<table><tbody><tr class="odd"><td><em><strong>请注意！</strong></em> 在 Beancount 的未来版本中，我们将稍微放宽此约束。当且仅当该 account 中没有其他该商品的单位时，我们将允许 account 持有负数单位的商品。或者，我们将允许您将 account 标记为完全不受此类约束。目的是允许商品空头头寸的 account。唯一的阻碍因素就是此约束。</td></tr></tbody></table>

有关库存预订算法的更多详细信息，请参阅 [库存如何工作](how-inventories-work.md) 文档。

#### 金额插值<a id="amount-interpolation"></a>

Beancount 能够自动填充 transaction 的某些详细信息。目前，您可以在 transaction 中省略*最多*一个 posting 的金额：

    2012-11-03 * "Transfer to pay credit card"
      Assets:MyBank:Checking            -400.00 USD
      Liabilities:CreditCard            

在上面的示例中，信用卡 posting 的金额已被省略。Beancount 会自动将其计算为 400.00 USD 以使 transaction 平衡。这也适用于多个 posting，以及带有 cost 的 posting：

    2014-07-11 * "Sold shares of S&P 500"
      Assets:ETrade:IVV                 -10 IVV {183.07 USD}
      Assets:ETrade:Cash            1979.00 USD
      Income:ETrade:CapitalGains

在这种情况下，IVV 的单位以高于购买价格（$183.07）的价格（$197.90）出售。第一个现金 posting 的权重为 -10 x 183.07 = -1830.70，第二个 posting 为直接的 $1979.00。最后一个 posting 将被赋予差额，即余额为 `-148.30 USD`，也就是说，*收益*为 $148.30。

在计算要平衡的金额时，用于检查 transaction 是否平衡为零的相同余额金额也用于填充缺失的金额。例如，以下情况不会触发错误：

    2014-07-11 * "Sold shares of S&P 500"
      Assets:ETrade:IVV                 -10 IVV {183.07 USD} @ 197.90 USD
      Assets:ETrade:Cash

现金账户将自动收到 1830.70 USD，因为 IVV posting 的余额金额为 -1830.70 USD（如果一个 posting 同时具有 cost 和 price，则始终使用 cost basis，而忽略可选的 price）。虽然从平衡角度来看这是可接受且正确的，但从会计角度来看这是不完整的：销售产生的资本利得需要单独核算，此外，如果按照上述操作，存入现金账户的金额将低于实际存款金额（1979.00 USD），希望随后在现金账户中的 balance assertion 能通过触发错误来指出这一疏忽。

最后，当余额包含多种商品时，这也适用：

    2014-07-12 * "Uncle Bob gave me his foreign currency collection!"
      Income:Gifts                 -117.00 ILS
      Income:Gifts                -3000.00 INR
      Income:Gifts                 -800.00 JPY
      Assets:ForeignCash

将插入多个 posting（每种用于平衡的商品各一个）来替换被省略的那个。

#### 标签<a id="tags"></a>

Transaction 可以标记任意字符串：

    2014-04-23 * "Flight to Berlin" #berlin-trip-2014
      Expenses:Flights              -1230.27 USD
      Liabilities:CreditCard

这类似于 Twitter 等平台上流行的“哈希标签”概念。这些标签本质上允许你标记 transaction 的一个子集。然后，它们可以作为过滤器，仅针对该子集生成 report。它们有许多用途。我喜欢用它们来标记我所有的旅行。

也可以指定多个标签：

    2014-04-23 * "Flight to Berlin" #berlin-trip-2014 #germany
      Expenses:Flights              -1230.27 USD
      Liabilities:CreditCard

（如果你想在 directive 上存储键值对，请参阅下面的元数据部分。）

##### 标签栈<a id="the-tag-stack"></a>

通常，与单个标签相关的多个 transaction 会在文件中连续输入。作为一种便利，解析器可以自动为文本块内的 transaction 添加标签。其工作原理很简单：解析器维护一个当前标签的“栈”，并在逐个读取 transaction 时将其应用于所有 transaction。你可以像这样向该栈推送和弹出标签：

    pushtag #berlin-trip-2014

    2014-04-23 * "Flight to Berlin"
      Expenses:Flights              -1230.27 USD
      Liabilities:CreditCard

    poptag #berlin-trip-2014

这样，你也可以将多个标签推送到一长串连续的 transaction 上，而无需逐一输入它们。

#### 链接<a id="links"></a>

Transaction 也可以相互链接。你可以将链接视为一种特殊的标签，用于在时间上分组一组财务相关的 transaction。例如，你可以使用链接来分组与特定发票相关的 transaction。这使得可以跟踪与该发票相关的付款（或核销）：

    2014-02-05 * "Invoice for January" ^invoice-pepe-studios-jan14
      Income:Clients:PepeStudios           -8450.00 USD
      Assets:AccountsReceivable

    2014-02-20 * "Check deposit - payment from Pepe" ^invoice-pepe-studios-jan14
      Assets:BofA:Checking                  8450.00 USD
      Assets:AccountsReceivable

或者跟踪与单一不当目的相关的多次转账：

    2014-02-05 * "Moving money to Isle of Man" ^transfers-offshore-17
      Assets:WellsFargo:Savings          -40000.00 USD
      Assets:WellsFargo:Checking          40000.00 USD

    2014-02-09 * "Wire to FX broker" ^transfers-offshore-17
      Assets:WellsFargo:Checking         -400025.00 USD
      Expenses:Fees:WireTransfers            25.00 USD
      Assets:OANDA:USDollar               40000.00

    2014-03-16 * "Conversion to offshore beans" ^transfers-offshore-17
      Assets:OANDA:USDollar          -40000.00 USD
      Assets:OANDA:GBPounds           23391.81 GBP @ 1.71 USD

    2014-03-16 * "God save the Queen (and taxes)" ^transfers-offshore-17
      Assets:OANDA:GBPounds             -23391.81 GBP
      Expenses:Fees:WireTransfers           15.00 GBP
      Assets:Brittania:PrivateBanking    23376.81 GBP

无论当前视图/过滤的 transaction 集合如何，链接的 transaction 都可以在 Web 界面中渲染在其专用的日志中（链接列表是一个全局页面）。

### balance assertion <a id="balance-assertions"></a>

Balance assertion 是一种将您的对账单余额输入到 transaction 流中的方法。它告诉 Beancount 验证在某个时间点，某个 account 中特定商品的数量应等于某个预期值。例如，以下指令

    2014-12-26 balance Liabilities:US:CreditCard   -3492.02 USD

表示“检查 2014 年 12 月 26 日*早晨*，account “`Liabilities:US:CreditCard`” 中的 USD 数量是否为 -3492.02 USD。”在处理条目列表时，如果 Beancount 遇到与 USD 不同的余额，它将报告错误。

如果没有报告错误，您应该可以确信，该 account 中位于其前面的 transaction 列表极有可能是正确的。这在实践中非常有用，因为在许多情况下，某些 transaction 可能会与其 posting 的各自 account 分开导入（参见 [去重问题](getting-started-with-beancount.md)）。这可能导致您在未察觉的情况下对同一 transaction 进行两次 booking，而定期插入 balance assertion 将每次都能捕获该问题。

Balance directive 的一般格式为：

    YYYY-MM-DD balance Account Amount

请注意，balance assertion 与其他所有非 transaction directive 一样，适用于其日期的**开始**（即当天午夜）。只需想象余额检查发生在该日午夜之后即可。

Balance assertion 仅对资产负债表 account（Assets 和 Liabilities）有意义。因为 Income 和 Expenses account 上的 posting 仅因其瞬时价值而有趣，即对于这些 account，我们感兴趣的是时间段内变化的总和（而非绝对值），所以在损益表 account 上使用 balance assertion 意义不大。

此外，请注意，每个 account 都受益于一个隐式的 balance assertion，即该 account 在其 Open directive 日期打开后为空。您不需要在打开 account 时显式断言零余额。

#### 多 commodity <a id="multiple-commodities"></a>

Beancount account 可能包含多种商品（尽管在实践中，您会发现这种情况并不常见，但为每种商品创建专用的子 account 是合理的，例如，持有一个股票投资组合）。Balance assertion 仅适用于该 assertion 的商品；它不会检查余额中的其他商品。如果您想检查多种商品，请使用多个 balance assertion，如下所示：

    ; Check cash balances from wallet
    2014-08-09 balance Assets:Cash     562.00 USD
    2014-08-09 balance Assets:Cash     210.00 CAD
    2014-08-09 balance Assets:Cash      60.00 EUR

目前没有办法穷尽地检查 account 中的完整商品列表（[一项提案正在进行中](balance-assertions-in-beancount.md)）。

请注意，在此示例中，如果穷尽检查对您确实很重要，您可以通过定义现金 account 的子 account 来规避，从而单独隔离每种商品，如下所示 `Assets:Cash:USD`, `Assets:Cash:CAD`。

#### lot 会被聚合 <a id="lots-are-aggregated"></a>

Balance assertion 适用于特定商品单位数量的总和，无论其 cost 如何。例如，如果您在一个 account 中持有同一商品的三个 lot，例如 5 HOOL {500 USD} 和 6 HOOL {510 USD}，则以下余额检查应成功：

    2014-08-09 balance Assets:Investing:HOOL     11 HOOL

所有 lot 都会聚合在一起，您可以验证它们的单位数量。

#### 对父 account 的检查 <a id="checks-on-parent-accounts"></a>

可以在父 account 上执行 balance assertion，并将包括其自身及其子 account 的余额：

    2014-01-01 open Assets:Investing
    2014-01-01 open Assets:Investing:Apple       AAPL
    2014-01-01 open Assets:Investing:Amazon      AMZN
    2014-01-01 open Assets:Investing:Microsoft   MSFT
    2014-01-01 open Equity:Opening-Balances

    2014-06-01 *
      Assets:Investing:Apple       5 AAPL {578.23 USD}
      Assets:Investing:Amazon      5 AMZN {346.20 USD}
      Assets:Investing:Microsoft   5 MSFT {42.09 USD}
      Equity:Opening-Balances

    2014-07-13 balance Assets:Investing 5 AAPL
    2014-07-13 balance Assets:Investing 5 AMZN
    2014-07-13 balance Assets:Investing 5 MSFT

请注意，这要求父 account 已被声明为 Open，以便在 balance assertions directive 中合法使用。

#### close 之前 <a id="before-close"></a>

在关闭 account 之前插入一个 0 单位的 balance assertion 很有用，只需确保在关闭时其内容为空。Close directive 不会自动为您插入该断言（我们最终可能会为此构建一个插件）。

#### 局部 tolerance <a id="local-tolerance"></a>

如果情况并非如此，这将导致 MSFT 的余额为 -10 个单位。另一方面，如果该账户在 5/23 持有 12 个单位的 MSFT，成本为 43.40 USD，那么该 transaction 将正常 booking，将现有的 12 个单位减少到 2 个。最常见的错误是，账户将持有 10 个或更多单位的 MSFT，但 *cost* 不同，而用户指定了错误的 cost 值。例如，如果账户持有 20 MSFT {42.10 USD} 的正余额，上述 transaction 仍然会失败，因为没有 10 个或更多单位的 MSFT 以 43.40 USD 的成本可供移除。

出于以下几个原因，强制执行此约束：

-   股票单位的数据录入错误并不罕见，它们对 Ledger 的正确性有重要的负面影响——金额通常很大——并且通常会触发此约束的错误。因此，错误检查是检测此类错误的一种有用方法。
-   以 cost 持有的负数单位相当罕见。你可能根本不需要它们。例外包括：股票的 short sales、期货合约的价差持有，以及取决于你如何记账，货币交易中的空头头寸。

这就是为什么此检查默认启用的原因。

<table><tbody><tr class="odd"><td><em><strong>请注意！</strong></em> 在 Beancount 的未来版本中，我们将稍微放宽此约束。我们将允许账户持有某种商品的负数单位，当且仅当该账户中没有持有该商品的其他单位。或者，我们将允许你将账户标记为完全没有此类约束。目的是允许商品空头头寸的账户。唯一的阻碍因素就是此约束。</td></tr></tbody></table>

有关 inventory booking 算法的更多详细信息，请参阅 [How Inventories Work](how-inventories-work.md) 文档。

#### 金额 interpolation <a id="amount-interpolation"></a>

Beancount 能够自动填充 transaction 的一些细节。目前，你可以在一个 transaction 中省略 *最多* 一个 posting 的金额：

    2012-11-03 * "Transfer to pay credit card"
      Assets:MyBank:Checking            -400.00 USD
      Liabilities:CreditCard            

在上面的示例中，信用卡 posting 的金额已被省略。Beancount 会自动将其计算为 400.00 USD 以平衡该 transaction。这也适用于多个 posting，以及带有 cost 的 posting：

    2014-07-11 * "Sold shares of S&P 500"
      Assets:ETrade:IVV                 -10 IVV {183.07 USD}
      Assets:ETrade:Cash            1979.00 USD
      Income:ETrade:CapitalGains

在这种情况下，IVV 的卖出价格（$197.90）高于其买入价格（$183.07）。第一个现金 posting 的权重为 -10 x 183.07 = -1830.70，第二个 posting 则直接为 $1979.00。最后一个 posting 将被赋予差额，即余额为 `-148.30 USD`，这意味着产生了 $148.30 的*收益*。

在计算需要平衡的金额时，用于检查 transaction 是否平衡为零的相同 balance 金额也被用于填充缺失的金额。例如，以下情况不会触发错误：

    2014-07-11 * "Sold shares of S&P 500"
      Assets:ETrade:IVV                 -10 IVV {183.07 USD} @ 197.90 USD
      Assets:ETrade:Cash            

现金账户将自动接收 1830.70 USD，因为 IVV posting 的 balance 金额为 -1830.70 USD（如果一个 posting 同时具有 cost 和 price，则始终使用 cost basis，而忽略可选的 price）。虽然从平衡角度来看这是被接受且正确的，但从会计角度来看这是不完整的：销售产生的资本利得需要单独核算，此外，如果如上所述操作，存入现金账户的金额将低于实际存款（1979.00 USD），希望随后在现金账户中的 balance assertion 能通过触发错误来指出这一疏忽。

最后，当 balance 包含多种商品时，这也适用：

    2014-07-12 * "Uncle Bob gave me his foreign currency collection!"
      Income:Gifts                 -117.00 ILS
      Income:Gifts                -3000.00 INR
      Income:Gifts                 -800.00 JPY
      Assets:ForeignCash

将插入多个 posting（每种需要平衡的商品一个）来替换被省略的那个。

#### tag <a id="tags"></a>

Transaction 可以标记任意字符串：

    2014-04-23 * "Flight to Berlin" #berlin-trip-2014
      Expenses:Flights              -1230.27 USD
      Liabilities:CreditCard

这类似于 Twitter 等平台上流行的“标签”（hash tagging）概念。这些标签基本上允许你标记 transaction 的一个子集。然后，它们可以作为过滤器，仅针对该子集生成 report。它们有多种用途。我喜欢用它们来标记我所有的旅行。

也可以指定多个标签：

    2014-04-23 * "Flight to Berlin" #berlin-trip-2014 #germany
      Expenses:Flights              -1230.27 USD
      Liabilities:CreditCard

（如果你想在 directive 上存储键值对，请参阅下面的 metadata 部分。）

##### tag 栈 <a id="the-tag-stack"></a>

在许多情况下，与单个 tag 相关的多笔 transaction 会在文件中连续录入。作为一种便利功能，解析器可以自动为文本块内的 transaction 添加 tag。其工作原理很简单：解析器维护一个当前 tag 的“栈”，在逐条读取 transaction 时，会将这些 tag 应用到所有 transaction 上。你可以像这样向该栈中压入（push）和弹出（pop）tag：

    pushtag #berlin-trip-2014

    2014-04-23 * "Flight to Berlin"
      Expenses:Flights              -1230.27 USD
      Liabilities:CreditCard

    poptag #berlin-trip-2014

通过这种方式，你无需逐一输入，即可将多个 tag 压入到一长串连续的 transaction 上。

#### link <a id="links"></a>

Transaction 之间也可以相互链接。你可以将 link 视为一种特殊的 tag，用于在时间维度上将一组财务相关的 transaction 分组。例如，你可以使用 link 来分组那些各自与特定发票相关的 transaction。这使得追踪与该发票相关的付款（或核销）成为可能：

    2014-02-05 * "Invoice for January" ^invoice-pepe-studios-jan14
      Income:Clients:PepeStudios           -8450.00 USD
      Assets:AccountsReceivable

    2014-02-20 * "Check deposit - payment from Pepe" ^invoice-pepe-studios-jan14
      Assets:BofA:Checking                  8450.00 USD
      Assets:AccountsReceivable

或者追踪与单一不当目的相关的多笔转账：

    2014-02-05 * "Moving money to Isle of Man" ^transfers-offshore-17
      Assets:WellsFargo:Savings          -40000.00 USD
      Assets:WellsFargo:Checking          40000.00 USD

    2014-02-09 * "Wire to FX broker" ^transfers-offshore-17
      Assets:WellsFargo:Checking         -40025.00 USD
      Expenses:Fees:WireTransfers            25.00 USD
      Assets:OANDA:USDollar               40000.00

    2014-03-16 * "Conversion to offshore beans" ^transfers-offshore-17
      Assets:OANDA:USDollar          -40000.00 USD
      Assets:OANDA:GBPounds           23391.81 GBP @ 1.71 USD

    2014-03-16 * "God save the Queen (and taxes)" ^transfers-offshore-17
      Assets:OANDA:GBPounds             -23391.81 GBP
      Expenses:Fees:WireTransfers           15.00 GBP
      Assets:Brittania:PrivateBanking    23376.81 GBP

无论当前的视图或过滤后的 transaction 集合如何，Web 界面都可以在其专用的日志中渲染这些已链接的 transaction（link 列表是一个全局页面）。

### balance assertion <a id="balance-assertions"></a>

Balance assertion 是一种将您的对账单余额输入到 transaction 流中的方法。它告诉 Beancount 验证在某个时间点，某个 account 中特定商品的数量应等于某个预期值。例如，以下指令

    2014-12-26 balance Liabilities:US:CreditCard   -3492.02 USD

表示“检查 2014 年 12 月 26 日*早晨*，account “`Liabilities:US:CreditCard`” 中的 USD 数量是否为 -3492.02 USD。”在处理条目列表时，如果 Beancount 遇到与 USD 不同的余额，它将报告错误。

如果没有报告错误，您应该可以确信，该 account 中位于其前面的 transaction 列表极有可能是正确的。这在实践中非常有用，因为在许多情况下，某些 transaction 可能会与其 posting 所属的 account 分开导入（参见 [去重问题](getting-started-with-beancount.md)）。这可能导致您在未察觉的情况下对同一 transaction 进行两次 booking，而定期插入 balance assertion 可以每次捕获该问题。

Balance directive 的一般格式为：

    YYYY-MM-DD balance Account Amount

请注意，balance assertion 与其他所有非 transaction directive 一样，适用于其日期的**开始**（即当天午夜）。只需想象余额检查发生在该日午夜之后即可。

Balance assertion 仅对资产负债表 account（Assets 和 Liabilities）有意义。因为 Income 和 Expenses account 上的 posting 仅因其瞬时价值而有趣，即对于这些 account，我们感兴趣的是某段时间内变化的总和（而非绝对值），所以在损益表 account 上使用 balance assertion 意义不大。

此外，请注意，每个 account 都受益于一个隐式的 balance assertion，即该 account 在其 Open directive 日期打开后为空。您无需在打开 account 时显式断言零余额。

#### 多 commodity <a id="multiple-commodities"></a>

Beancount account 可能包含多种商品（尽管在实践中，您会发现这种情况并不常见，但为每种商品创建专用的子 account 是合理的，例如，持有一个股票投资组合）。Balance assertion 仅适用于该 assertion 的商品；它不会检查余额中的其他商品。如果您想检查多种商品，请使用多个 balance assertion，如下所示：

    ; Check cash balances from wallet
    2014-08-09 balance Assets:Cash     562.00 USD
    2014-08-09 balance Assets:Cash     210.00 CAD
    2014-08-09 balance Assets:Cash      60.00 EUR

目前尚无方法对账户中的完整商品列表进行穷举检查（[一项提案正在进行中](balance-assertions-in-beancount.md)）。

请注意，在此示例中，如果穷举检查对您确实至关重要，您可以通过定义现金账户的子账户来规避此问题，从而将每种商品单独隔离，例如 `Assets:Cash:USD`、`Assets:Cash:CAD`。

#### Lots 是聚合的<a id="lots-are-aggregated"></a>

Balance assertion 适用于特定商品单位数量的总和，而不论其 cost 如何。例如，如果您在账户中持有同一商品的三个 lot，例如 5 HOOL {500 USD} 和 6 HOOL {510 USD}，则以下 balance 检查应成功：

    2014-08-09 balance Assets:Investing:HOOL     11 HOOL

所有 lot 都会聚合在一起，您可以验证其单位数量。

#### 对父账户的检查<a id="checks-on-parent-accounts"></a>

可以在父账户上执行 balance assertion，这将包括其自身及其子账户的余额：

    2014-01-01 open Assets:Investing
    2014-01-01 open Assets:Investing:Apple       AAPL
    2014-01-01 open Assets:Investing:Amazon      AMZN
    2014-01-01 open Assets:Investing:Microsoft   MSFT
    2014-01-01 open Equity:Opening-Balances

    2014-06-01 *
      Assets:Investing:Apple       5 AAPL {578.23 USD}
      Assets:Investing:Amazon      5 AMZN {346.20 USD}
      Assets:Investing:Microsoft   5 MSFT {42.09 USD}
      Equity:Opening-Balances

    2014-07-13 balance Assets:Investing 5 AAPL
    2014-07-13 balance Assets:Investing 5 AMZN
    2014-07-13 balance Assets:Investing 5 MSFT

请注意，这要求父账户必须已声明为 Open，以便在 balance assertions directive 中合法使用。

#### 在 Close 之前<a id="before-close"></a>

在关闭账户之前插入一个 0 单位的 balance assertion 是很有用的，以确保在关闭时其内容为空。Close directive 不会自动为您插入该断言（我们最终可能会为此构建一个插件）。

#### 本地 Tolerance<a id="local-tolerance"></a>

有时需要覆盖 balance check 的 tolerance 以放宽该 balance assertion 的情况相当常见。这可以通过使用基于 balance 金额的本地 tolerance 金额来实现，如下所示：

    2013-09-20 balance Assets:Investing:Funds     319.020 ~ 0.002 RGAGX

### pad <a id="pad"></a>

Pad 指令会自动插入一笔 transaction，以确保后续的 balance assertion 能够成功（如果需要的话）。它会插入满足该 balance assertion 所需的差额。（LaTeX 中的“弹性空间”之于排版，就如同 Beancount 中 Pad 指令之于 balance。）

请注意，这里的“后续”是指*日期顺序*，而不是文件中声明的顺序。这在概念上等价于一笔会随时间自动扩展或收缩，以填补两个 balance assertion 之间差额的 transaction。其形式如下：

    2014-06-01 pad Assets:BofA:Checking Equity:Opening-Balances

Pad 指令的一般格式为：

    YYYY-MM-DD pad Account AccountPad

第一个 account 是自动计算金额所贷记的 account。该 account 后面应该跟随一个 balance assertion（如果该 account 没有 balance assertion，pad 条目是无害的，不会执行任何操作）。

第二个 account 用于该 transaction 的另一方，它是资金的来源，这几乎总是某个 Equity account。之所以如此，是因为该指令通常用于初始化新 account 的余额，从而避免我们手动插入此类指令，或者避免输入将 account 带到当前余额的完整历史 transaction。

以下是一个现实的使用场景示例：

    ; Account was opened way back in the past.
    2002-01-17 open Assets:US:BofA:Checking

    2002-01-17 pad Assets:US:BofA:Checking Equity:Opening-Balances

    2014-07-09 balance Assets:US:BofA:Checking  987.34 USD

这将导致在 Pad 指令之后、同一日期插入以下 transaction：

    2002-01-17 P "(Padding inserted for balance of 987.34 USD)"
      Assets:US:BofA:Checking        987.34 USD
      Equity:Opening-Balances       -987.34 USD

这是一笔普通的 transaction——你会看到它与其他 transaction 一起出现在渲染后的 journal 中。（注意特殊的“P”标志，脚本可以使用它来查找这些条目。）

请注意，如果没有 balance assertion，Pad 指令就没有意义。因此，与 balance assertion 一样，它们通常仅用于资产负债表 account（Assets 和 Liabilities）。

你也可以在 balance assertion *之间*插入 Pad 条目，这也是可行的。例如：

    2014-07-09 balance Assets:US:BofA:Checking  987.34 USD
    … more transactions… 
    2014-08-08 pad Assets:US:BofA:Checking Equity:Opening-Balances

    2014-08-09 balance Assets:US:BofA:Checking  1137.23 USD

如果没有中间的 transaction，这将插入以下 padding transaction：

2014-08-08 P "(Padding inserted for balance of 1137.23 USD)"
      Assets:US:BofA:Checking        149.89 USD
      Equity:Opening-Balances       -149.89 USD

如果这一点不明显，149.89 USD 是 1137.23 USD 和 987.34 USD 之间的差额。如果在支票账户中还有更多 posting 金额的中间 transaction，该金额会自动调整，以使第二个 assertion 通过。

#### 未使用的 Pad Directives<a id="unused-pad-directives"></a>

目前，您不能在输入文件中保留未使用的 Pad directives。它们会触发错误：

    2014-01-01 open Assets:US:BofA:Checking

    2014-02-01 pad Assets:US:BofA:Checking Equity:Opening-Balances

    2014-06-01 * "Initializing account"
      Assets:US:BofA:Checking                   212.00 USD
      Equity:Opening-Balances

    2014-07-09 balance Assets:US:BofA:Checking  212.00 USD

（我认为，如此严格是一个值得讨论的问题，最终可能会将其移至一个可选的 plugin 中。）

#### commodity <a id="commodities"></a>

请注意，Pad directive 并不指定任何 commodities。该 account 中所有具有相应 balance assertion 的 commodities 都会受到影响。例如，以下代码中的 padding directive 将插入一个 transaction，其中包含针对 USD 和 CAD 的独立 postings：

    2002-01-17 open Assets:Cash

    2002-01-17 pad Assets:Cash Equity:Opening-Balances

    2014-07-09 balance Assets:Cash    987.34 USD
    2014-07-09 balance Assets:Cash    236.24 CAD  

如果该 account 包含其他未进行 balance assertion 的 commodities，则不会为这些 commodities 插入 posting。

#### padding 的 cost basis <a id="padding-cost-basis"></a>

目前，Pad directives 不适用于持有以 cost 计价的头寸的 accounts。该 directive 实际上仅对现金账户有用。（这主要是因为 balance assertions 目前尚不允许指定要断言的 cost basis。未来我们可能会决定支持断言总 cost basis，届时我们可以考虑支持带有 cost basis 的 padding。）

#### 多次 padding <a id="multiple-paddings"></a>

目前，您不能为同一个 account 和 commodity 插入多个 padding 条目：

    2002-01-17 open Assets:Cash

    2002-02-01 pad Assets:Cash Equity:Opening-Balances

    2002-03-01 pad Assets:Cash Equity:Opening-Balances

    2014-04-19 balance Assets:Cash    987.34 USD

（有一个 [proposal](http://furius.ca/beancount/doc/proposal-padding) 正在等待批准，以允许这样做并将 padding 金额均匀分布在所有中间的 Pad directives 之间，但截至目前尚未实现。）

### note <a id="notes"></a>

Note directive 仅用于为特定 account 的日志附加一条带日期的注释，例如：

    2013-11-03 note Liabilities:CreditCard "Called about fraudulent card."

当渲染日志时，该注释应在上下文中显示。这对于记录与财务事件相关的事实和声明非常有用。我经常使用它来记录那些否则无法归入 transaction 的信息片段。

Note directive 的一般格式为：

    YYYY-MM-DD note Account Description

描述字符串可以跨多行拆分。

### document <a id="documents"></a>

Document directive 可用于将外部文件附加到某个 account 的日志中：

    2013-11-03 document Liabilities:CreditCard "/home/joe/stmts/apr-2014.pdf"

文件名会在 Web 界面中对应 account 的日志中渲染为浏览器链接，你应该能够点击它以查看文件本身的内容。这对于将账户对账单和其他下载内容整合到账户流程中非常有用，从而可以通过几次点击轻松访问它们。还可以编写脚本，根据 account 名称获取此文档列表并对它们执行某些操作。

Document directive 的一般格式为：

    YYYY-MM-DD document Account PathToDocument

#### 来自目录的 Documents<a id="documents-from-a-directory"></a>

创建这些条目的更便捷方法是使用一个特殊选项，指定包含子目录层级的目录，该层级镜像了账户表（chart of accounts）的结构。例如，上一节中显示的 Document directive 可以由如下目录层级创建：

    stmts
    `-- Liabilities
        `-- CreditCard
            `-- 2014-04-27.apr-2014.pdf

只需将根目录作为选项指定即可（注意末尾没有斜杠）：

    option "documents" "/home/joe/stmts"

将被选取的文件是那些以日期开头的文件，格式为 *YYYY-MM-DD*。如果你有多个此类文档归档，可以多次指定此选项。过去，我每年使用一个目录（如果你扫描所有文档，目录可能会变得很大，扫描的文档往往是大文件）。

使用账本 account 的层级结构来组织你的电子对账单和扫描件，是一种极好的组织方式，可以为这些文档建立一个清晰、无歧义的位置，以便在需要时找到它们。

### price <a id="prices"></a>

Beancount 有时会为每种商品（commodity）创建一个内存中的价格数据存储，用于多种目的。特别是，它用于报告账户持仓的未实现收益。Price directive 可用于为该数据库提供数据点。Price directive 确立了一种商品（基础货币）与另一种商品（报价货币）之间的汇率：

    2014-07-09 price HOOL  579.18 USD

该 directive 表示：“2014 年 7 月 9 日，一单位 HOOL 的价格为 579.18 USD。” 用于货币汇率的 Price 条目工作方式相同：

    2014-07-09 price USD  1.08 CAD

Price directive 的一般格式为：

    YYYY-MM-DD price Commodity Price

请记住，Beancount 对 HOOL、USD 或 CAD 是什么一无所知。它们是不透明的“事物”。你赋予它们含义。因此，如果你以这种方式记录未使用的假期，为你的假期小时数设定每小时价格是完全有效且有用的：

    2014-07-09 price VACHR  38.46 USD  ; Equiv. $80,000 year

#### 来自 posting 的 price <a id="prices-from-postings"></a>

如果你使用 `beancount.plugins.implicit_prices` 插件，每当出现一个声明了 cost 或可选 price 的 Posting 时，它将使用该 cost 或 price 自动合成一个 Price directive。例如，此 transaction：

    2014-05-23 *
      Assets:Investments:MSFT         10 MSFT {43.40 USD}
      Assets:Investments:Cash     -434.00 USD

在解析后自动变为：

    2014-05-23 *
      Assets:Investments:MSFT         10 MSFT {43.40 USD}
      Assets:Investments:Cash     -434.00 USD

    2014-05-23 price MSFT  43.40 USD

这很方便，如果你启用了它，账本价格数据库中的大多数价格点可能都来自这里。你可以从账本中打印解析后的价格表（它只是另一种类型的 report）。

#### 同一天的 price <a id="prices-on-the-same-day"></a>

请注意，这里没有时间的概念；Beancount 并非旨在解决日内交易者的问题，当然，它确实能够处理每天的多笔交易。它只是按天存储价格。（通常，如果你需要许多需要日内时间概念的功能，最好使用其他系统，这超出了记账系统的范围。）

如果同一天存在多个 Price directive，文件中最后出现的那个将被选中并包含在 Price 数据库中。

### event <a id="events"></a>

Event 指令[^3]用于跟踪*您选择的某个变量*随时间的变化。例如，您的位置：

    2014-07-09 event "location" "Paris, France"

上述指令表示：“从 2014 年 7 月 9 日起，将 ‘location’ 事件的值更改为 ‘Paris, France’。” 特定事件类型每天只有一个值。

Event 指令的一般格式为：

    YYYY-MM-DD event Name Value

事件的 *Name* 字符串无需在任何地方声明，它从您第一次使用该指令时开始存在。*Value* 字符串可以是您喜欢的任何内容；它没有规定的结构。

如何最好地解释这些用法，通过提供示例来说明：

-   **Location**：您可以使用事件来跟踪您所在的城市或国家。在账本中，这是一种合理的用法，因为您的支出性质与您所在的位置高度相关。这很方便：如果您经常使用 Beancount，将此信息添加到文件中所需的努力非常少。我通常有一个“现金日记账”部分，用于记录杂项现金支出，我在那里输入这些指令。

-   **Address**：如果您经常搬家，记录您过去的家庭住址会很有用。移民的政府表格有时会要求提供这些信息。例如，美国的绿卡申请流程，

-   **Employer**：您可以以这种方式记录每份工作的入职和离职日期。然后您可以计算您在那里工作的天数。

-   **Trading window**：如果您是上市公司的员工，您可以记录允许您交易其股票的日期。这可以用来确保您在窗口关闭时没有交易该股票。

事件通常用于报告天数。例如，在魁北克省（加拿大），如果您“[在日历年中度过 183 天或更多，不包括 21 天或更短的旅行](http://www.ramq.gouv.qc.ca/en/citizens/health-insurance/registration/Pages/eligibility.aspx)”，您将获得免费的医疗保健保险。如果您经常出国旅行，您可以轻松编写一个脚本来提醒您剩余的天数配额，以避免失去保险资格。许多外籍人士处于类似的情况。

同理，美国国税局（IRS）将美国移民认定为“居民外国人”——因此需要申报纳税，太好了！——如果你通过了[实质性存在测试](http://www.irs.gov/Individuals/International-Taxpayers/Substantial-Presence-Test)。该测试定义为：“在本年度内实际在美国停留至少 31 天，且在包含本年度及之前两年的三年期间内停留 193 天，计算方式为：本年度所有在美的天数，加上前一年天数的 ⅓，再加上前两年天数的 ⅙。”哎呀……我头都疼了。这变得很复杂。如果你掌握了随时间变化的位置信息，就可以自动报告它。

Events 还将可用于过滤语言中，以指定不连续的时间段。例如，如果你使用 Event 指令来追踪你的位置，就可以生成仅包含你在特定位置时发生的 transaction 的 report，例如：“显示我在所有德国旅行期间的支出”，或者“列出我在蒙特利尔时餐厅 transaction 的收款方列表”。

<table><tbody><tr class="odd"><td><em><strong>请注意！</strong></em> 过滤器尚未实现。此外，关于 events 的 report 在 Beancount 2.0 中尚未重新实现。它们将很快重新引入，过滤器也是如此。</td></tr></tbody></table>

值得注意的是，Price 和 Event 指令是唯一不与 account 关联的指令。

### query <a id="query"></a>

在 Beancount 文件中关联 SQL 查询可能非常方便，以便能够自动将这些查询作为 report 运行。这仍然是一个早期开发/实验性的 directive。无论如何，你可以像这样在 transaction 流中插入查询：

    2014-07-09 query "france-balances" "
      SELECT account, sum(position) WHERE ‘trip-france-2014’ in tags"

其语法为

    YYYY-MM-DD query Name SqlContents

每个查询都有一个名称，该名称很可能用于将其作为 report 类型调用以运行。此外，查询的日期旨在表示该查询预期运行的日期，也就是说，应忽略其后的 transaction。如果你熟悉 SQL 语法，这相当于一个隐式的 CLOSE。

### custom <a id="custom"></a>

Beancount 的长期计划是允许插件和外部客户端定义自己的 directive 类型，由 Beancount 输入语言解析器进行声明和验证。在此期间，提供了一个通用的 directive，供客户端**原型**开发新功能，例如预算（budgeting）。

    2014-07-09 custom "budget" "..." TRUE 45.30 USD

该 directive 的语法是灵活的：

    YYYY-MM-DD custom TypeName Value1 ...

第一个参数是一个字符串，旨在使其对于您的 directive 具有唯一性。可以将其视为您的 directive 的类型。在其后，您可以放置任意数量的字符串、日期、布尔值、金额和数字。请注意，没有验证机制来检查特定类型后跟随的参数数量和类型是否一致。

（有关此功能起源的故事，请参阅[此线程](https://groups.google.com/d/msg/beancount/R9wWrdP6mVU/yfCaD3XaDgAJ)。）

## metadata <a id="metadata-1"></a>

您可以为每个 entry 和 posting 附加任意数据。其语法如下所示：

    2013-03-14 open Assets:BTrade:HOOLI
      category: "taxable"

    2013-08-26 * "Buying some shares of Hooli"
      statement: "confirmation-826453.pdf"
      Assets:BTrade:HOOLI      10 HOOL @ {498.45 USD}
        decision: "scheduled"
      Assets:BTrade:Cash

在此示例中，一个 “category” 属性被附加到 account 的 Open directive 上，一个 “statement” 属性被附加到 Transaction directive 上（其值为表示文件名的字符串），而一个 “decision” 属性则被附加到该 transaction 的第一个 posting 上（posting 的额外缩进并非严格必要，但有助于提高可读性）。

Metadata 可以附加到任何类型的 directive 上。键必须以 a-z 中的小写字母开头，并且可以包含（大写或小写）字母、数字、连字符和下划线。此外，值可以是以下数据类型之一：

-   Strings

-   Accounts

-   Currency

-   Dates (datetime.date)

-   Tags

-   Numbers (Decimal)

-   Amount (beancount.core.amount.Amount)

使用这些数据有两种方式：

1.  Beancount 附带的查询工具（如 bean-query）允许您利用 metadata 值进行过滤和聚合。

2.  您可以在自定义脚本中访问和使用 metadata。Metadata 值可以通过所有 directive 上的 “`.meta`” 属性访问，它是一个 Python dict。

特定属性没有特殊含义，这些属性旨在由用户自行定义。然而，所有 directive 都保证包含一个 ‘`filename`’（字符串）和一个 ‘`lineno`’（整数）属性，它们反映了创建该 directive 的位置。

最后，没有值的属性将被解析，其值为 'None'。如果一个属性被重复多次，则只解析并保留该属性的第一个值，后续的值将被忽略。

## 选项<a id="options"></a>

Beancount 输入文件的大部分内容由 directive 组成，如上一节所述。然而，也可以使用一种特殊的无日期 “option” directive 在输入文件中设置一些全局选项：

    option "title" "Ed’s Personal Ledger"

Option directive 的一般格式为：

    option Name Value

其中 *Name* 和 *Value* 均为字符串。

请注意，根据选项的不同，其效果可能是设置单个值，也可能是向现有值列表中添加内容。换句话说，某些选项是列表。

有三种方式可以查看选项列表：

-   在[本文档](beancount-options-reference.md)中，我会定期更新此文档。

-   要查看您安装的版本所支持的权威选项列表，请使用以下命令：`bean-doctor list-options`

-   最后，您也可以[查看源代码](http://github.com/beancount/beancount/tree/master/beancount/parser/options.py)。

### 运营货币<a id="operating-currencies"></a>

一个值得注意的选项是“`operating_currency`”。默认情况下，Beancount 不会将任何商品区别对待。特别是，它不知道用户最常使用的商品——即货币——有什么特殊之处。例如，如果您居住在新西兰，您的 transaction 中将会有大量 NZD 商品。

但有用的 report 会尝试将所有非货币商品归约为所使用的几种主要货币之一。此外，将货币单位拆分到其专用的列中也是有用的。这对于导出也很有用，可以避免为该列指定单位，并导入到电子表格中以处理数字。

因此，您可以通过选项声明您最常使用的货币：

    option "operating_currency" "USD" 

您可以声明多个货币。

无论如何，此选项仅由报告代码使用，它永远不会改变 Beancount 的处理行为或语义。

## plugin <a id="plugins"></a>

为了加载插件 Python 模块，请使用专用的 “plugin” directive：

    plugin "beancount.plugins.module_name"

插件的名称应该是你 PYTHONPATH 中某个 Python 模块的名称。这些模块将被 Beancount loader 导入，并按顺序在已解析的条目列表上运行，以便插件对条目进行转换或输出错误。这允许你将部分代码集成到 Beancount 中，对条目进行任意转换。有关详细信息，请参阅 [Scripting & Plugins](beancount-scripting-plugins.md)。

插件还可选地接受一些配置参数。这些参数可以通过一个可选的最终字符串参数提供，如下所示：

    plugin "beancount.plugins.module_name" "configuration data"

Option directive 的一般格式为：

    plugin ModuleName StringConfig

配置数据的格式取决于具体的插件。目前，任意字符串都会被传递给插件。有关其可接受内容的具体细节，请参阅各插件的文档。

另请参阅 “plugin processing mode” 选项，该选项会影响所运行的内置插件列表。

## include <a id="includes"></a>

支持 include directive。这允许你将大型输入文件拆分为多个文件。语法如下：

    include "path/to/include/file.beancount"

通用格式为

    include Filename

指定的路径可以是绝对路径或相对路径。如果文件名为相对路径，则相对于包含该文件的目录。这使得在目录层级中使用相对 include 变得容易，这些目录可以放置在版本控制下，并可在任何位置检出。

Include directive 并非严格处理（例如不像 C 语言那样）。Beancount 解析器会累积 include directive，并由 loader 单独处理。这是可行的，因为 Beancount 输入文件中声明的顺序并不重要。

然而，目前，options 会在每个文件内重新解析。用于后解析处理的 options-map 是顶层文件返回的 options-map。（供参考，这一点定义不佳，是在没有适当设计的情况下添加 include 文件时的次要影响；由于已引发问题，未来肯定会对其进行审查。）

## 接下来做什么？<a id="whats-next"></a>

本文档描述了 Beancount 语言的所有可能语法。如果你还没有编写任何 Beancount 输入，可以前往 [入门指南](getting-started-with-beancount.md)，或者浏览 [命令行会计食谱](command-line-accounting-cookbook.md) 中的实用用例列表。

[^1]: 请注意，存在一个 “Open” directive，用于提供每个 account 的起始日期。它可以位于文件中的任何位置，不必出现在你使用 account 名称之前的文件中。你可以立即开始在 transaction 中使用 account 名称，尽管所有接收 posting 的 account 名称最终都必须有一个对应的 Open directive，其日期必须早于输入文件中该 account 的所有 transaction。

[^2]: 请注意，无论 price 是使用 @ 语法指定为单位价格，还是使用 @@ 语法指定为总价，这都是有效的。

[^3]: 我真的很不喜欢这个 directive 的 “event” 这个名字。我一直在寻找更好的替代方案，但至今未果。“register” 可能更合适，因为它类似于处理器的寄存器，但这可能会与 *account register* report 混淆。“variable” 可能可行，但听起来太计算机科学化且不合语境。如果你能想到更好的名字，请提出建议，我会认真考虑完全重命名（并保留对 “event” 的遗留支持）。Ajit Singh 建议的另一个名字是 "temporal"。Micah Duke 建议 "mark"。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
