> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/exporting_your_portfolio/

# 导出您的投资组合<a id="title"></a>

[Martin Blais](mailto:blais@furius.ca)，2015 年 12 月（v2）

[http://furius.ca/beancount/doc/export](http://furius.ca/beancount/doc/export)

## 概述<a id="overview"></a>

本文档说明了如何从 Beancount 导出您的持仓组合至 Google Finance 投资组合（并最终支持其他投资组合跟踪网站）。

*注意：这是本文档的第二版，于 2015 年 12 月重写，大幅简化了投资组合导出流程，并完全分离了用于价格下载的证券代码指定。这个新的简化版本仅使用单个元数据字段名：“export”。之前的文档可在[此处](https://docs.google.com/document/d/1eZIDRmQZxR6cmDyOJf7U3BnCm4PDMah2twxYFfKPJtM/)找到。*

## 投资组合跟踪工具<a id="portfolio-tracking-tools"></a>

互联网上有多个网站允许用户创建投资组合（或上传 transaction 列表以创建此类投资组合），并报告因价格变动导致的投资组合变化、显示未实现资本利得等。其中一个这样的网站是 [Google Finance](http://finance.google.com) 门户。另一个例子是 [Yahoo Finance](http://finance.yahoo.com)。这些网站很方便，因为它们允许你监控价格变化对你所有 account 中整个资产投资组合的影响，无论是在白天还是其他时间。

然而，这些网站中的每一个都期望用户使用其界面和工作流程，痛苦地逐一手动输入每个持仓。使用 Beancount 的一个巨大优势是，你绝不应该需要手动输入此类信息；相反，你应该能够提取这些信息并将其上传到其中一个网站。你可以独立于你使用的特定投资组合跟踪服务，并且应该能够在它们之间切换而不丢失任何数据；随着你的需求演变，Beancount 可以作为你持仓列表的纯净数据源。

Google Finance 支持一种“导入”功能来创建投资组合数据，该功能支持 Microsoft OFX 金融交换数据格式。在本文档中，我们展示了如何构建一个 Beancount report，将持仓投资组合导出为 OFX 格式，以创建 Google Finance 投资组合。

## 导出到 Google Finance<a id="exporting-to-google-finance"></a>

### 将您的持仓导出为 OFX<a id="exporting-your-holdings-to-ofx"></a>

首先，创建一个对应于您 Beancount 持仓的 OFX 文件。您可以使用以下命令来完成此操作：

    bean-report file.beancount export_portfolio > portfolio.ofx

请参阅该 report 自身的帮助以了解选项：

    bean-report file.beancount export_portfolio --help

### 在 Google Finance 中导入 OFX 文件<a id="importing-the-ofx-file-in-google-finance"></a>

然后，我们需要将该 OFX 文件导入到一个基于 Web 的投资组合中。

1.  访问 [http://finance.google.com](http://finance.google.com) 并点击左侧的“Portfolios”（或者直接访问 [https://www.google.com/finance/portfolio](https://www.google.com/finance/portfolio)，自 2015 年 1 月起此方式有效）

2.  如果您有一个已存在的、之前导入的投资组合，请点击“Delete Portfolio”将其删除。

3.  点击“Import Transactions”，然后点击“Choose File”并选择您导出的 *portfolio.ofx* 文件，接着点击“Preview Import”。

4.  您应该能看到一个导入的 lot 列表，其中包含熟悉的股票代码和名称，类型为“Buy”，并且具有真实的 Shares 和 Price 列。如果没有，请参阅下方的说明。否则，滚动到页面底部并点击“Import”。

5.  您的投资组合现在应该已经显示出来。操作完成。

您永远不应该麻烦通过网站直接更新此投资组合……相反，请更新您的 Beancount 账本文件，重新导出到一个新的 OFX 文件，**删除**之前的投资组合，并在其上重新导入一个全新的投资组合。您纯净的源数据始终是您 Beancount 文件，理想情况下，您永远不需要担心在任何外部网站上损坏或删除投资组合数据。

## 控制导出的商品<a id="controlling-exported-commodities"></a>

### 声明您的商品<a id="declaring-your-commodities"></a>

通常，我们建议您在输入文件中显式声明所使用的每一种商品。这是一个整理这些商品相关信息的合适位置，这些元数据（metadata）您之后可以通过 bean-query 或您编写的脚本加以利用。例如，您可以声明商品的人类可读描述以及其他一些属性，如下所示：

    2001-09-06 commodity XIN
      name: "iShares MSCI EAFE Index ETF (CAD-Hedged)"
      class: "Stock"
      type: "ETF"
      ...

无论是否包含这些声明，Beancount 都能正常工作（如果您未提供声明，它会自动生成 Commodity directive）。如果您喜欢严格并带有一定的纪律性，可以使用插件来*要求*声明每一种商品，当出现未声明的商品时，该插件会发出错误：

    plugin "beancount.plugins.check_commodity"

您可以为该 Commodity directive 使用任何日期。我们建议使用该商品成立（inception）的日期，或者如果是货币，则使用发行国首次引入该货币的日期。您可以在维基百科或发行方的网站上找到合适的日期。Google Finance 可能也包含该日期。

### 默认行为<a id="what-happens-by-default"></a>

默认情况下，所有持仓都会以 position 的形式导出，其 ticker symbol 与您在 Beancount 中用于定义该持仓的 commodity 名称相同。如果您持有 “AAPL” 单位的持仓，系统将创建一个针对 “AAPL” 的导出条目。导出代码默认会尝试导出所有持仓。

然而，除了最简单且无歧义的情况外，这通常不足以生成一个可用的 Google Finance portfolio。您在 Beancount 输入文件中使用的每个 commodity 的名称，可能与 Google Finance 数据库中的金融工具对应，也可能不对应；由于其数据库支持的符号数量极其庞大，仅指定 ticker symbol 往往会产生歧义。Google Finance 会尝试将具有歧义的符号字符串解析为其数据库中最可能的金融工具。这有可能将其解析为您并非意图指向的另一个金融工具。因此，即使您使用了交易所使用的基本符号，通常仍需要通过指定该符号所属的交易所或 symbology 来消除歧义。Google 提供了[这些符号空间的列表](http://www.google.com/googlefinance/disclaimer/)。

以下是一个实际案例。iShares/Blackrock 发行的“[CAD-Hedged MSCI EAFE Index](http://www.blackrock.com/ca/individual/en/products/239624/ishares-msci-eafe-index-etf-cadhedged-fund)” ETF 产品，在多伦多证券交易所（`TSE`）上的符号为 “`XIN`”。如果您只是[在 Google Finance 上查找 “XIN”](https://www.google.com/finance?q=xin)，它默认会选择将其解析为更可能的 “`NYSE:XIN`” 符号（[纽约证券交易所的新源地产公司](https://www.google.com/finance?q=NYSE%3AXIN)）。因此，您需要通过指定该金融工具所需的 ETF ticker 为 “`TSE:XIN`” 来消除歧义。

### 显式指定导出的符号<a id="explicitly-specifying-exported-symbols"></a>

你可以通过为每个 Commodity directive 附加一个“`export`”元数据字段，来指定用于导出该 commodity 的交易所特定符号，如下所示：

    2001-09-06 commodity XIN
      ...
      export: "TSE:XIN"

“`export`”字段用于将你的 commodity 名称映射到 Google Finance 系统中对应的 instrument。如果需要导出该 commodity 的持仓，将使用此代码代替 Beancount 货币名称。

Google Finance 使用的符号体系似乎遵循以下语法：

### *Exchange:Symbol*（交易所:代码） <a id="exchangesymbol"></a>

其中 *Exchange* 是股票交易所在交易所的代码，或者是其他金融数据源的代码，例如“`MUTF`”代表“美国共同基金”，[以及更多](http://www.google.com/googlefinance/disclaimer/)。*Symbol* 是在该交易所内唯一的名称。我建议您在 Google Finance 中搜索您的每一项金融工具，通过检查完整名称、描述和价格来确认该工具与您的工具相对应，然后像这样插入相应的代码。

### 导出为现金等价物<a id="exporting-to-a-cash-equivalent"></a>

为了处理 Google Finance 不支持的头寸，导出 report 可以将持仓转换为其现金等价值。这对于现金头寸（例如，闲置在储蓄账户或支票账户中的现金）也很有用。

例如，我持有一份保险投资工具的单位（这在加拿大很常见，例如 London Life）。这是一种金融工具，但每一份特定的保单发行都有自己对应的价值——这些产品没有公开的数据来源，其透明度较低，我可以通过年度对账单获取其价值，但肯定无法在 Google Finance 中获取。但我仍然希望该资产的价值能反映在我的投资组合中。

告诉导出代码进行此转换的方法是，在 “export” 字段中指定特殊值 “CASH”，如下所示：

    1878-01-01 commodity LDNLIFE
      export: "CASH"

这将在导出前，使用最接近导出日期的价格，将 `LDNLIFE` 商品持仓转换为其对应的报价值。请注意，尝试将没有相应 cost 或 price 可供我们确定其价值的商品转换为现金将产生错误。必须存在 price 才能进行转换。

简单货币也应标记为现金以便导出：

    1999-01-01 commodity EUR
      name: "European Union Euro currency"
      export: "CASH"

最后，所有转换后的持仓都会聚合为单一的现金头寸。将这些现金条目导出为单独的 OFX 条目没有意义，因为 Google Finance 代码无论如何都会将它们聚合为单一条目。

### 声明货币工具<a id="declaring-money-instruments"></a>

在这个现金转换的故事中有一个小插曲：Google Finance 的 importer 似乎无法正确理解（grok）importer 中“cash”金额的 OFX position；我认为这很可能是 Google Finance 导入代码中的一个 bug（或者我可能还没有找到使此功能正常工作的正确 OFX 字段值）。

相反，为了插入一个现金 position，exporter 使用一种现金等价的商品，该商品的价格始终为该货币的 1 个单位，例如，对于美元，价格为 $1.00。例如，对于美元，我使用 [VMMXX](https://www.google.com/finance?q=MUTF:VMMXX)，这是一种 Vanguard Prime Money Market Fund；对于加拿大元，我使用 [IGI806](https://www.google.com/finance?q=MUTF_CA:IGI806)。适合此用途的商品类型是某种 Money Market fund。使用哪一种并不重要，只要其价格非常接近 1 即可。请找到一种。

如果你希望包含现金商品，你需要为账簿中的每种现金货币找到这样一种商品，并告知 Beancount。通常，这只会涉及一两种货币。

你通过为 “`export`” 字段附加特殊值 “`MONEY`” 来声明它们，并指定该商品代表哪种货币，如下所示：

    1900-01-01 commodity VMMXX
      export: "MUTF:VMMXX (MONEY:USD)"

    1900-01-01 commodity IGI806
      export: "MUTF_CA:IGI806 (MONEY:CAD)"

### 忽略商品<a id="ignoring-commodities"></a>

最后，账本中持有的某些商品应当被忽略。例如，在镜像记账中使用的虚拟商品，用于跟踪未归属的就业股票计划股份，或者用于跟踪存入退休账户的金额，就像这样：

    1996-01-01 commodity RSPCAD
      name: "Canada Registered Savings Plan Contributions"

你可以通过为“`export`”字段指定特殊值“`IGNORE`”来告诉导出代码忽略某个商品，如下所示：

    1996-01-01 commodity RSPCAD
      name: "Canada Registered Savings Plan Contributions"
      export: "IGNORE"

因此，所有以 `RSPCAD` 为单位的持仓将不会被导出。

关于某些商品是否应该导出的问题，有时会带来一些有趣的选择。这里有一个例子：我在一个资产账户中跟踪我累积的休假小时数。其单位是“`VACHR`”。我为该商品关联了一个大致相当于我时薪净额的价格。这给了我一个大致的概念，即账面上累积了多少休假时间的价值，例如，如果我辞职，我会得到多少补偿。我希望将它们包含在我的总净资产中吗？这些小时的价值应该反映在我导出的投资组合价值中吗？我认为这主要取决于我是否计划在离开这份工作之前用完这些休假，以及我是否希望这个累积价值出现在我的资产负债表上。

## 与净资产对比<a id="comparing-with-net-worth"></a>

最终结果是，所有导出持仓的总和加上现金头寸应大致等于你所有资产的价值，而 Google Finance 网站计算出的总价值应与该 report 报告的值非常接近：

    bean-report file.beancount networth

作为对比，我自己的投资组合价值通常与报告值相差不超过几百美元。

## OFX 导出的细节<a id="details-of-the-ofx-export"></a>

### 导入失败<a id="import-failures"></a>

如果导出的投资组合中包含 Google Finance 无法识别的符号，Google 的导入功能会**致命地**出错。随后，Google Finance 将无法识别你的**整个**文件。为了避免此问题，建议对所有导出的商品使用显式的 exchange:symbol 名称，本文档后续部分对此有进一步说明。

Google Finance 对于你提供给它导入的特定 OFX 文件格式也可能比较挑剔。`export_portfolio` 命令试图避免使用会导致其损坏的 OFX 特性，但这很脆弱，你的投资组合内容的具体细节可能会触发无法导入的输出。如果发生这种情况，在上述步骤 (4) 中，你不会看到股票符号列表，而是会看到一长串看起来像 XML 标签的头寸列表（这就是失败的表现形式）。如果是这种情况，请向邮件列表发送电子邮件（最好你能隔离出导致损坏的头寸，并且具备 diff 文件和进行一些故障排除的能力）。

### 共同基金与股票<a id="mutual-funds-vs.-stocks"></a>

OFX 格式区分股票和共同基金。在实践中，Google Finance 的导入器似乎并不区分这两者（至少其行为看起来是一样的），因此这很可能是一个无关紧要的实现细节。尽管如此，导出代码能够遵循 OFX 区分 “BUYMF” 和 “BUYSTOCK” XML 元素的约定。

为此，导出代码通过检查与商品关联的 ticker 是否以字母 “MUTF” 开头并后跟冒号，来尝试分类哪些商品代表共同基金。例如，“`MUTF:RGAGX`” 和 “`MUTF_CA:RBF1005`" 都会被检测为共同基金。

### 调试导出<a id="debugging-the-export"></a>

为了调试你的每个持仓是如何被导出的，请使用 `--debug` 标志，它会将每个持仓由导出脚本处理方式的详细记录打印到 **stderr**：

    bean-report file.beancount export_portfolio --debug 2>&1 >/dev/null | more

该脚本应打印导出的头寸及其对应的持仓列表，然后是转换后的头寸及其对应的持仓列表（通常许多现金头寸会被聚合在一起），最后是忽略的持仓列表。这应该足以解释导出投资组合的全部内容。

### 购买日期<a id="purchase-dates"></a>

Beancount 目前并没有所有 lot 的购买日期，因此购买日期被导出为在导出前一天购买。

最终，当 Beancount 中可用购买日期时（取决于 [inventory booking changes](http://furius.ca/beancount/doc/booking-proposal)），导出格式中可能会使用实际的 lot 购买日期。然而，使用正确的日期是否是正确的做法尚不清楚，因为 Google Finance 可能会坚持插入自报告购买日期以来的股息现金……但 Beancount 已经处理了插入一个特殊的 lot 用于现金，其中应该已经包含了这部分。我们拭目以待。

### 禁用股息<a id="disable-dividends"></a>

在 “Edit Portfolio” 选项下，有一个复选框似乎可以禁用所提供股息的计算。如果能找到一种方法在导入时自动禁用此复选框，那就太好了。

### 自动化上传<a id="automate-upload"></a>

如果能通过 Python 脚本自动化替换投资组合，那就太好了。不幸的是，Google Finance API 已被弃用。也许有人可以编写一个屏幕抓取例程来实现这一点。

## 摘要<a id="summary"></a>

每个持仓的导出行为可以通过其 commodity 的处理方式来控制，具体有以下几种方式：

1.  **导出**为投资组合头寸。这是默认行为，但您应使用“`ticker`”或“`export`”元数据字段指定股票代码，格式为“*ExchangeCode:Symbol*”。

2.  **转换**为现金，并导出为货币市场现金等价物头寸，方法是将“`export`”元数据字段的值设置为特殊值“`CASH`”。

3.  **忽略**，方法是将“`export`”元数据字段设置为特殊值“`IGNORE`”。

4.  作为**Money Instrument**提供，用于计算计划转换为现金并包含在投资组合中的每个持仓的现金等价物价值。这些通过“`export`”元数据字段中的特殊值“(`MONEY:<currency>)`”来识别。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
