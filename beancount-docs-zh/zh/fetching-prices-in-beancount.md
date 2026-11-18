> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/fetching_prices_in_beancount/

# Beancount 中的 Price<a id="title"></a>

[Martin](mailto:blais@furius.ca) [Blais](mailto:blais@furius.ca)，2015 年 12 月

[http://furius.ca/beancount/doc/prices](http://furius.ca/beancount/doc/prices)

## 译者导读

这篇讲的是 Beancount 如何获取并维护 price 数据。它对 advanced 用户的价值不在"怎么抓 price"本身，而在下面几点：

1. **Beancount 是 hermetic 的**：price 永远不会自动从网络抓取，任何一次报表运行都是确定性的、可离线的。理解这一点，才能理解为什么需要显式的 Price directive，以及为什么抓取工具是外置的、且默认只抓"当前持仓真正需要的" price。
2. **`bean-price` 的核心抽象是 source string**：`<报价货币>:<module>/[^]<symbol>`。它真正的威力在于 **extensibility**——你可以写自己的 Python 抓取模块放到 PYTHONPATH 上，通过 module 名直接引用，完全不必修改 Beancount 本身。
3. **几个容易踩的细节**：fallback source 用逗号分隔依次尝试；inverted price 用 `^` 前缀，且 `--swap-inverted`（交换货币方向）与"取 price 的倒数"是两种不同的做法；inverted 之后的 precision 可能与抓取到的不一致。
4. **"抓取哪些 asset"其实是三个列表的交集**：`--inactive`、`--undeclared`、`--clobber`、`--all` 这几个 option 的语义，决定了默认只抓"当前持仓所需"的 price，其余都要显式放宽。

> **译者注 · 版本提示**：本文写于 2015 年，当时 `bean-price` 随 Beancount 一起分发。后来它连同各 price source 一起独立为 [beanprice](https://github.com/beancount/beanprice/) 包，Beancount v2 起不再内置该工具；文中提到的 Google Finance source 也已被废弃移除，目前内置抓取源以 Yahoo! Finance 为主。安装方式与命令行入口请以 beanprice 仓库为准。

---

*本文介绍 Beancount 中用于抓取并维护 price 数据的工具。*

## 引言<a id="introduction"></a>

处理一个 Beancount 文件，从定义上说，仅限于文件自身的内容。特别是，commodity 的最新 price **永远不会**自动从互联网抓取。这是有意为之：目的是让任何一次报表运行都是确定性的，并且可以离线运行。没有任何意外。

然而，为了计算资产的市场价值，我们确实需要访问 price 信息。为此，Beancount 提供了一个 Price directive，可以通过在输入文件中内联插入这些 price point，来填充它内存中的 price 数据库：

2015-11-20 price ITOT 95.46 USD  
2015-11-20 price LQD 115.63 USD  
2015-11-21 price USD 1.33495 CAD  
…

当然，你可以手动完成这件事：在线查询 price，然后自己写出这些 directive。但对于公开交易的资产，你可以自动化这个过程——调用一些代码来下载 price 并为你写出 directive。

Beancount 自带了一些工具来帮助你完成这件事。本文介绍这些工具。

## 问题<a id="the-problem"></a>

在维护 Beancount 文件的语境下，我们有几项特定的需求需要解决。

第一，我们不能指望用户总是及时更新输入文件。这意味着我们不仅要能抓取最新 price，还要能抓取**过去的历史 price**。Beancount 提供了一个接口来提供这些 price，并提供了若干实现（从 Yahoo! Finance 和 Google Finance 抓取）。

第二，我们不想为那些在某个时间点上与我们无关的持仓存储太多 price。文件中持有的资产列表随时间变化。理想情况下，我们希望只包含那些**正在持有期间**的资产的 price 列表。Beancount 的 price 维护工具能够判断出：在某个特定日期，它需要为哪些 commodity 抓取 price。

第三，如果某个 price 已经出现在输入文件中，我们不想重复抓取。这些工具会检测到这种情况并跳过这些 price。此外还有一个 caching 机制，可以避免冗余的网络请求。

最后，虽然我们提供了一些 price source 的基础实现，但我们无法为所有可能的在线数据源和网站都提供这样的代码。这个问题类似于从各种机构导入和提取数据。为了解决它，我们提供了一个 **extensibility（可扩展性）** 机制：你可以在 Python 模块中实现自己的 price source 抓取器，并在输入文件中通过把模块名指定为该 commodity 的 source 来指向它。

## “bean-price” 工具<a id="the-bean-price-tool"></a>

Beancount 自带一个名为 “bean-price” 的命令行工具，整合了上述思路。默认情况下，这个脚本接受一个 Beancount 输入文件名列表，并抓取为计算当前 account 中持仓的最新市场价值所需的 price：

    bean-price /home/joe/finances/joe.beancount

你也可以提供一个要运行的特定 price 抓取任务列表，例如：

    bean-price -e USD:google/TSE:XUS CAD:mysources.morningstar/RBF1005

这些任务会并发运行，所以应该相当快。

### source 字符串 <a id="source-strings"></a>

每个这种 "job source string" 的通用格式是：

    <quote-currency>:<module>/[^]<symbol>

例如：

    USD:beancount.prices.sources.google/NASDAQ:AAPL

“quote-currency” 是 commodity 被报价所用的货币。例如，苹果的股票以美元报价。

"module" 是一个 Python module 的名字，该 module 包含一个可以被实例化、并能连接到数据源提取 price 数据的 Source 类。这些 module 会被自动导入，其中的 Source 类会被实例化，以便从它们所支持的特定在线数据源拉取 price。这使得你可以编写自己的抓取代码而无需修改这个脚本。你的代码可以放在 Python PYTHONPATH 上的任何位置，而且你完全不必为了让它工作而修改 Beancount 本身。

“symbol” 是传给 price 抓取器用于查询该货币的字符串。例如，苹果股票在 Nasdaq 交易，它在 Google Finance source 中对应的 symbol 是 “NASDAQ:AAPL”。其他 price source 可能使用不同的符号体系，例如有的可能要求资产的 CUSIP。

我们提供了 price source 的默认实现；内置了 Yahoo! Finance 和 Google Finance 的抓取器，它们覆盖了一大类常见的公开投资类型（例如股票和一些共同基金）。为方便起见，module 名总是先在 "`beancount.prices.sources`" 这个 package 下搜索，这些实现就放在那里。这就是为什么，例如要使用内置的 Yahoo! Finance 数据抓取器时，你不需要写出完整的 "`beancount.prices.sources.yahoo/AAPL`"，而只需写 "`yahoo/AAPL`"。

### 回退 source <a id="fallback-sources"></a>

在实践中，在线抓取 price 经常失败。数据源通常只支持数量有限的资产，而且即便是支持的资产，支持程度也可能各不相同。例如，Google Finance 支持股票的历史 price，但不返回货币类 instrument 的历史 price（这些限制可能更多与它们和上游数据提供商之间的合同约定有关，而非技术限制）。

为此，一个 source string 可以提供多个数据 source，用逗号分隔。例如：

    USD:google/CURRENCY:GBPUSD,yahoo/GBPUSD

每个 source 会依次尝试，如果其中一个无法返回有效的 price，就尝试下一个作为 fallback。希望是指定的 source 中至少有一个能成功。

### 反向 price <a id="inverted-prices"></a>

有时候，只能获取某个 instrument 的逆方向的 price。货币尤其常见。例如，以美元报价的加元 price，由 USD/CAD 市场提供，而该市场给出的是 1 美元兑多少加元（即倒数）。为了使用它，你可以在 instrument 名前加 "`^`" 前缀，指示工具计算所抓取 price 的倒数：

    USD:google/^CURRENCY:USDCAD

如果要像这样对 source price 取倒数，precision 可能与抓取到的不同。例如，如果 USD/CAD 的 price 是 1.32759，那么上面这条 directive 在为 “CAD” 这个 instrument 定价时会输出：

    2015-10-28 price CAD  0.753244601119 USD

默认情况下，倒数汇率会按照其他 Price directive 对这些数字取整的同样方式进行取整。

你可能已经知道，Beancount 的内存 price 数据库是双向工作的（所有汇率的倒数都会被自动存储）。所以，如果你更希望输出的 Price 条目是交换了货币、而不是对汇率数字本身取倒数，可以使用 `--swap-inverted` option。在前面那个为 CAD 定价的例子中，它会输出：

    2015-10-28 price USD   1.32759 CAD

### 日期 <a id="date"></a>

默认情况下，抓取的是资产的最新 price。你可以用一个 option 改为抓取过去某个指定日期的 price：

    bean-price --date=2015-02-03 …

如果你用输入文件来指定要抓取的 price 列表，工具会判断出**在那个时间点**账面上持有的资产列表，并只为这些资产抓取历史 price。

### 缓存 <a id="caching"></a>

Price 会被自动缓存（如果是当前且最新的 price，只缓存很短的时间，大约半小时）。当你需要连续多次运行这个脚本进行排错时，这很方便。

你可以用一个 option 禁用缓存：

    bean-price --no-cache

你也可以让脚本在抓取 price 之前先清空缓存：

    bean-price --clear-cache

## 从 Beancount 输入文件获取 Price<a id="prices-from-a-beancount-input-file"></a>

通常，人们用 Beancount 输入文件来指定要抓取的货币列表。为此，你应该在输入文件中为每一个想要抓取 price 的货币提供一个 Commodity directive，像这样：

    2007-07-20 commodity VEA

      price: "USD:google/NYSEARCA:VEA"

"price" metadata 应该包含一个 price source string 列表。例如，一个股票产品可能长这样：

    2007-07-20 commodity CAD

      price: "USD:google/CURRENCY:USDCAD,yahoo/USDCAD"

而一个货币可能需要换算到多个目标货币：

    1990-01-01 commodity GBP

      price: "USD:yahoo/GBPUSD CAD:yahoo/GBPCAD CHF:yahoo/GBPCHF"

### 抓取哪些 Asset<a id="which-assets-are-fetched"></a>

从一个 Beancount 输入文件计算"需要 price 的 commodity 列表"有很多种方法：

1.  **Commodity directives。** 文件中所有带有 “price” metadata 的 Commodity directive 组成的列表。对于其中每个持仓，会查阅该 directive，并用它的 "`price`" metadata 字段来指定从哪里抓取 price。

2.  **按 cost 持有的资产的 commodity。** 在某个特定日期所有按 cost 持有的持仓的 price。因为这些持仓是按 cost 持有的，我们可以假设它们的 commodity 有一个对应的、随时间变化的 price。

3.  **被换算的 commodity。** 那些过去从其他 commodity 换算而来的持仓的 price（例如，把某种货币的现金从另一种货币换算过来）。

默认情况下，要抓取的 ticker 列表只包括这三个列表的**交集**。这是因为这个脚本最常见的用途是：为某个特定日期抓取缺失的 price，而且只抓需要的那些。

**不活跃的 commodity。** 你可以用 “`--inactive`” option 来抓取 (1) 的完整 price 集合，而不考虑 (2) 和 (3) 中确定的资产持仓。

**未声明的 commodity。** 没有对应 “Commodity” directive 的 commodity 默认会被忽略。要包含输入文件中出现过的完整 commodity 列表，使用 “`--undeclared`” option。

**Clobber。** 对于同一数据已经存在的 price directive 默认会被排除，因为该 price 已经在文件里了。你可以用 “`--clobber`” 来忽略已有的 price directive，从而不把抓取到的内容过滤掉。

最后，你可以用 “--all” 来包含不活跃和未声明的 commodity，并允许覆盖已有的。除了测试之外，你可能不想用它。

如果你想排错并打印出所见到的 commodity 列表，把 “`--verbose`” option 用两次，即 “`-vv`”。你也可以只用 “`--dry-run`” option 打印出将要抓取的 price 列表，它会在真正抓取缺失 price 之前停下来。

## 结论<a id="conclusion"></a>

### 编写你自己的脚本<a id="writing-your-own-script"></a>

如果这个工具定义的工作流不适合你的需求，你想自己写一个脚本，你不必从零开始；你应该能够复用现有的 price 抓取代码。例如，给定一个已有文件，每周五抓取所有资产的 price 来补齐缺失 price 的历史记录会很方便。另一个例子是：抓取在有投入和分配的情况下正确计算投资收益所需的全部 price directive。

你可以在 [beanprice](https://github.com/beancount/beanprice/) 仓库里找到多个 price source 的代码，以及其他 price source，比如 pricehist 模块。

### 贡献<a id="contributions"></a>

如果这个工作流很适合你，你想向 Beancount 贡献某个 price source 抓取器，请联系邮件列表。我愿意纳入那些经过了非常仔细的单元测试、并且已经使用了一段时间的通用抓取器。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
