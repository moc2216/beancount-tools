> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/a_proposal_for_an_improvement_on_inventory_booking/

# Inventory Booking

关于命令行记账改进的提案

<a id="title"></a>

Martin Blais，2014 年 6 月

[http://furius.ca/beancount/doc/proposal-booking](http://furius.ca/beancount/doc/proposal-booking)

> [动机](#motivation)
>
> [问题描述](#problem-description)
>
> [Lot 日期](#lot-date)
>
> [平均 cost basis](#average-cost-basis)
>
> [不含佣金的资本利得](#capital-gains-sans-commissions)
>
> [cost basis 调整](#cost-basis-adjustments)
>
> [处理股票拆分](#dealing-with-stock-splits)
>
> [现有解决方案](#previous-solutions)
>
> [Ledger 中的不足](#shortcomings-in-ledger)
>
> [Beancount 中的不足](#shortcomings-in-beancount)
>
> [需求](#requirements)
>
> [调试工具](#debugging-tools)
>
> [显式与隐式 booking 缩减](#explicit-vs.-implicit-booking-reduction)
>
> [设计提案](#design-proposal)
>
> [Inventory](#inventory)
>
> [输入语法与过滤](#input-syntax-filtering)
>
> [算法](#algorithm)
>
> [隐式 booking 方法](#implicit-booking-methods)
>
> [默认插入的日期](#dates-inserted-by-default)
>
> [无信息时的匹配](#matching-with-no-information)
>
> [缩减多个 lot](#reducing-multiple-lots)
>
> [示例](#examples)
>
> [无冲突](#no-conflict)
>
> [按 cost 显式选择](#explicit-selection-by-cost)
>
> [按日期显式选择](#explicit-selection-by-date)
>
> [按标签显式选择](#explicit-selection-by-label)
>
> [按组合显式选择](#explicit-selection-by-combination)
>
> [单位不足](#not-enough-units)
>
> [重复选择同一 lot](#redundant-selection-of-same-lot)
>
> [自动 price 外推](#automatic-price-extrapolation)
>
> [平均成本 booking](#average-cost-booking)
>
> [未来工作](#future-work)
>
> [实现说明](#implementation-notes)
>
> [结论](#conclusion)

## 动机<a id="motivation"></a>

“库存记账”（inventory booking）问题，即在平仓时选择减少库存中哪些交易批次（lot），是一个棘手的问题。迄今为止，在命令行会计社区中，在支持处理许多常见实际案例的灵活性方面，进展相对有限。本文档讨论了当前的现状，描述了我们希望解决的常见用例，确定了一套对更优 booking 方法的需求，并提出了支持这些需求的语法和实现设计，同时为 booking 方法定义了明确的语义。

## 问题描述<a id="problem-description"></a>

我们所考虑的问题在于：对于一笔旨在在特定时间点、特定账户中减少持仓规模的复式记账 transaction，应当减少该时点账户中持有的哪些 inventory lot。这应当通过一种简单的数据录入语法来指定，以最大限度地减轻用户的负担。

例如，可以通过在不同时间点购买两批 HOOL 股票来建立持仓：

    2014-02-01 * "First trade"
      Assets:Investments:Stock        10 HOOL {500 USD}
      Assets:Investments:Cash
      Expenses:Commissions          9.95 USD

    2014-02-15 * "Second trade"
      Assets:Investments:Stock         8 HOOL {510 USD}
      Assets:Investments:Cash
      Expenses:Commissions          9.95 USD

我们将这两组股份称为“交易批次”（trade lots），并假设底层用于计数的系统会分别跟踪每批次的 cost 和获取日期。

这里的问题是，如果我们卖出部分股票，*我们应该选择哪些股份？* 是第一批交易的，还是第二批的？这是一个重要的决定，因为它会影响资本利得，进而影响税务。（如果你需要对此进行解释，资本利得的账户在 Beancount 食谱的[“股票交易”章节](trading-with-beancount.md)中有更详细的描述。）根据我们的财务状况、今年的交易历史以及某笔交易将实现的未实现收益，有时我们可能希望选择其中一个批次而非另一个。如今，大多数折扣券商甚至允许你在下达减少或平仓持仓的交易时，选择具体的批次。

在此强调 inventory booking 的两个方向非常重要：

1.  **增加持仓。** 这是创建新的交易批次，或向现有交易批次添加份额的过程（如果 cost 和其他属性相同）。这很简单，相当于向描述账户余额的某种映射（我称之为“inventory”）中添加一条记录。

2.  **减少持仓。** 这通常是 booking 复杂性的所在，问题本质上是要确定从现有持仓的哪个批次中移除份额。

本文档的大部分内容都致力于第二个方向。

### lot 日期 <a id="lot-date"></a>

即使每个 lot 的 cost 完全相同，你打算平仓的持仓的获取日期仍然很重要，因为可能适用不同的税务规则。例如，在美国，持有超过 12 个月的头寸适用显著较低的税率（“长期资本利得税率”）。例如，如果你这样录入你的持仓：

    2012-05-01 * "First trade"
      Assets:Investments:Stock        10 HOOL {300 USD}
      Assets:Investments:Cash
      Expenses:Commissions          9.95 USD

    2014-02-15 * "Second trade at same price"
      Assets:Investments:Stock         8 HOOL {300 USD}
      Assets:Investments:Cash
      Expenses:Commissions          9.95 USD

并且我们要为 2014-03-01 的 transaction 进行 booking，选择第一个 lot 将产生长期（低）收益，因为自获取以来已过去两年（持仓从 2012-05-01 到 2014-03-01），而针对第二个 lot 进行 booking 将产生短期（高）资本利得税。因此，这不仅仅是 lot 的 cost 问题。我们的系统目前并不旨在自动报税，但我们希望以最终允许进行此类 report 的方式录入数据。

请注意，此讨论假设你能够*决定*可以针对哪个 lot 进行交易。可能有多种税务规则适用，在某些情况下，取决于你居住的国家，你可能没有选择权，政府可能会规定你应如何报告你的收益。

在某些情况下，你甚至可能需要能够对同一个 account 应用多种 booking 方法（例如，如果一个 account 受到多个国家的税务主张）。我们将在本文档中忽略这种罕见情况，因为它非常少见。

### 平均 cost basis <a id="average-cost-basis"></a>

对于税收庇护账户，情况变得更加复杂。由于在这些账户中平仓没有税务后果，经纪商通常会选择将您持仓的账面价值视为一个单一的 lot 进行核算。也就是说，每股的成本是通过您所持头寸成本的加权平均来计算的。这也可以通过将每个头寸的总成本相加，然后除以总股数来等效计算。继续我们第一个例子：

> *10 HOOL x 500 USD/HOOL = 5000 USD*
>
> *8 HOOL x 510 USD/HOOL = 4080 USD*
>
> *Cost basis = 5000 USD + 4080 USD = 9080 USD*
>
> *Total number of shares = 10 HOOL + 8 HOOL = 18 HOOL*
>
> *Cost basis per share = 9080 USD / 18 HOOL = 504.44 USD/HOOL*

因此，如果您要平掉部分头寸并卖出一些股份，您将以 504.44 USD/HOOL 的成本进行。您实现的收益将相对于此成本计算；例如，如果您以 520 USD/HOOL 的价格卖出 5 股，您的收益将按以下方式计算：

    (520 USD/HOOL - 504.44 USD/HOOL) x 5 HOOL = 77.78 USD

这种 booking 方法通过您可能在这些类型账户中观察到的两种财务事件得以体现：

1.  费用可能通过按当前 market price 卖出部分股份来扣除。如果您在美国 Vanguard 持有退休账户，您会看到这种情况。经纪商会每季度收取固定金额的美元（在我的雇主计划中为 5$），并将其折算为每只基金的一小部分零散股份进行卖出。该 transaction 不考虑资本利得：他们只是计算出需要卖出多少股份来覆盖费用，并且不会向您报告收益。您必须假设这无关紧要。大多数人不会跟踪非应税账户中的收益，但像我们这样的怪人可能仍然希望计算回报。

2.  Cost basis 调整可能会自发发生。这种情况很少见，但我曾在加拿大税收递延账户中的共同基金中见过一两次：基于其交易活动的某些未公开细节，基金管理公司不得不发布一项 cost basis 调整，您应该将其应用于您的头寸。您会收到一封电子邮件，告知调整金额是多少。99% 的人可能不会在意，不理解并忽略这条消息……也许这是对的，因为它对他们的税收没有影响，但如果您想核算该账户中的交易回报，您确实需要计入它。因此，我们需要能够增加或减少现有头寸的 cost basis。

请注意，您头寸的平均成本在每次交易时都会发生变化，并且每次向现有头寸添加时都需要重新计算。这里的一个问题是，如果您跟踪每股成本，这些多次重新计算可能会导致一些错误，如果您使用固定的数值表示（通常是十进制数）来存储金额。在我们的数据结构中跟踪 cost 的一种替代方法，一种在数值上更稳定的方法，是简单地跟踪总 cost 而不是每股 cost。另外请注意，使用分数并不能充分解决这个问题：在实践中，经纪商可能会报告一个特定的 cost，该 cost 四舍五入到特定的小数位数，我们可能希望使用报告的数字来记录我们的减少交易，而不是维护分数表示所代表的理想化金额。使用固定十进制或分数表示都存在一些问题。我们将在这里 largely 忽略这些问题。

总之：我们需要能够支持按平均 cost 对 lots 进行 booking，并且我们需要能够调整现有头寸的 cost basis。我一直在思考一种实现此功能的解决方案，该方案不会强制账户被标记为特殊状态。我认为我们可以仅使用 inventory 操作来实现这一点。我们只需要对语法进行一个小改动，允许用户指示系统应该按所有头寸的平均 cost 进行 booking。

使用上面的第一个例子，获取股份的形式与之前相同，即在买入 10 和 8 HOOL 单位的两个 lots 后，我们最终得到一个持有两个 lots 的 inventory，一个是 10 HOOL {500 USD}，另一个是 8 HOOL {510 USD}。然而，当到了卖出时，将使用以下语法（这是一个我打算实现很久的旧想法）：

    2014-02-01 * "Selling 5 shares at market price 550 USD"
      Assets:Investments:Stock               -5 HOOL {*}
      Assets:Investments:Cash           2759.95 USD
      Expenses:Commissions                 9.95 USD
      Income:Investments:CapitalGains

当遇到“`*`”代替 cost 时，就像这样，它会：

1.  将所有 lots 合并并重新计算每股平均价格（504.44 USD）

2.  针对此合并后的库存进行 booking，从而减少生成的 lot。

在 transaction 之后，我们将最终持有一个 13 HOOL {504.44 USD} 的单一 position。如果以不同的 price 向该 position 添加资产，将会创建一个新的 lot，而这些 lot 会在下一次发生基于平均 cost basis 的减少时再次合并。在发生减少之前，我们无需合并 lot。除了累积舍入误差的担忧外，该方案在数学上是正确的，并且保持了账户不被强制使用特定 booking 方法的特性——每次减少都可以使用方法的混合。这是一个很好的特性，即使它并非严格必要，即使我们只想为每个账户指定一个“默认” booking 方法并始终沿用。能够支持例外情况总是很棒的，因为在现实生活中，例外情况有时确实会发生。

### 不含佣金的资本利得<a id="capital-gains-sans-commissions"></a>

我们希望能够支持在不包含佣金的情况下自动计算资本利得。这个问题在[交易文档中的佣金部分](trading-with-beancount.md)以及[邮件列表中的一个帖子](https://groups.google.com/d/msg/ledger-cli/zRSMle5AV3Q/ySUgsMVNg-kJ)中有详细描述。复杂性的本质在于，不能简单地从包含佣金的利得中减去报告期间发生的佣金，因为用于获取持仓的佣金必须按比例分摊到被出售的持仓股份上。实现这一目标最简单且最常见的方法是将获取持仓的成本计入持仓本身的 cost basis，并在减少持仓时从 market value 中扣除卖出成本。

无论我们设计出什么新方案，都必须允许我们将这些调整后的利得计入其中，因为这对许多个人的情况至关重要。在 Beancount 中，我已经找到了这个问题的解决方案，幸运的是，它仅涉及对带有特殊标志的 transaction 进行自动转换……前提是，我能够找到一种方法，在无需指定其 cost 的情况下指定要 booking 的 lot，因为一旦佣金成本被合并到持仓成本中，调整后的成本就不会出现在输入文件的任何地方，用户将不得不手动计算它，这是不合理的。在我提出的解决方案中，以下 transaction 将由“C”标志的存在触发，自动进行转换：

    2014-02-10 * "Buy"
      Assets:US:Invest:Cash    -5009.95 USD
      C Expenses:Commissions       9.95 USD
      Assets:US:Invest:HOOL       10.00 HOOL {500 USD / aa2ba9695cc7}

    2014-04-10 * "Sell #1" 
      Assets:US:Invest:HOOL       -4.00 HOOL {aa2ba9695cc7}
      C Expenses:Commissions       9.95 USD
      Assets:US:Invest:Cash     2110.05 USD
      Income:US:Invest:Gains

    2014-05-10 * "Sell #2"
      Assets:US:Invest:HOOL       -6.00 HOOL {aa2ba9695cc7}
      C Expenses:Commissions       9.95 USD
      Assets:US:Invest:Cash     3230.05 USD
      Income:US:Invest:Gains

它们将由插件自动转换为以下内容，并替换上述原始 transaction：

    2014-02-10 * "Buy"
      Assets:US:Invest:Cash        -5009.95 USD
      X Expenses:Commissions           9.95 USD
      X Income:US:Invest:Rebates      -9.95 USD
      X Assets:US:Invest:HOOL         10.00 HOOL {500.995 USD / aa2ba9695cc7}

    2014-04-10 * "Sell #1" 
      X Assets:US:Invest:HOOL         -4.00 HOOL {aa2ba9695cc7}
      X Expenses:Commissions           9.95 USD
      X Income:US:Invest:Rebates      -9.95 USD
      Assets:US:Invest:Cash         2110.05 USD
      Income:US:Invest:Gains ; Should be (530-500)*4 - 9.95*(4/10) - 9.95 = 
                             ; 106.07 USD

    2014-05-10 * "Sell #2"
      X Assets:US:Invest:HOOL         -6.00 HOOL {aa2ba9695cc7}
      X Expenses:Commissions           9.95 USD
      X Income:US:Invest:Rebates      -9.95 USD
      Assets:US:Invest:Cash         3230.05 USD
      Income:US:Invest:Gains ; Should be (540-500)*6 - 9.95*(6/10) - 9.95 = 
                             ; 224.08 USD

“X”标志仅用于标记已被转换的 posting，因此稍后可以用特殊颜色或属性来渲染它们。Rebates account 作为单独的 counter 包含在内，只是为了使 transaction 保持平衡。

我需要放宽交易 lot 的消歧义，是因为用户需要能够在不指定持仓 cost 的情况下指定匹配的 leg，因为在减少持仓时（2014-04-10），没有办法确定原始 lot 的 cost 是多少。为了明确起见，在上面的例子中，这意味着如果所有信息只有 4 HOOL 和 500 USD，就没有办法反推出 500.995 USD 的 cost 来指定与开仓交易 lot 的匹配，因为那是以 10 HOOL 发生的。

因此，我们需要更明确地处理 booking。在上面的例子中，我通过“标签”选择匹配的 lot，也就是说，用户可以选择在 cost 规范中提供唯一的 lot 标识符，之后可以使用它来消歧义我们要对哪个 lot 进行减少/出售的 booking。上面的例子以这种方式使用了字符串“`aa2ba9695cc7`”。

（这个问题的另一种解决方案涉及同时跟踪*原始* cost（不含佣金）和*实际* cost（含佣金），然后针对前者查找 lot，但使用后者来平衡 transaction。这个想法是允许用户继续使用持仓的 cost 来选择 lot，但我不确定在库存发生各种变化的情况下这是否可行。此事需要进一步思考。）

### cost basis 调整 <a id="cost-basis-adjustments"></a>

为了调整 cost basis，可以显式地替换账户内容，如下所示：

    2014-03-15 * "Adjust cost basis from 500 USD to 510 USD"
      Assets:US:Invest:HOOL      -10.00 HOOL {500 USD}
      Assets:US:Invest:HOOL       10.00 HOOL {510 USD}
      Income:US:Invest:Gains     

这种方法效果良好，并允许系统自动计算收益。但支持以价格单位对持仓总成本进行调整会更方便，例如，“将此持仓的 cost basis 增加 340.51 USD”。问题在于，调整后的每股成本现在需要由用户计算……这很不方便。不过，我们可以很好地支持这一点，方法如下：

    2014-03-15 * "Adjust cost basis from 500 USD to 510 USD"
      Assets:US:Invest:HOOL      -10.00 HOOL {500 USD}
      Assets:US:Invest:HOOL       10.00 HOOL {}
      Income:US:Invest:Gains    -340.51 USD

如果所有 legs 都完全指定——它们具有可计算的 balance——我们允许省略单个 price。这很好地解决了这个问题。

### 处理股票拆分<a id="dealing-with-stock-splits"></a>

对股票拆分进行会计处理在 booking 方面带来了一些复杂性。一般来说，问题在于我们需要处理商品含义随时间的变化。例如，你现在可以在 Beancount 中这样做，并且它是有效的：

    2014-01-04 * "Buy some HOOL"
      Assets:Investments:Stock        10 HOOL {1000.00 USD}
      Assets:Investments:Cash

    2014-04-17 * "2:1 split into Class A and Class B shares"
      Assets:Investments:Stock       -10 HOOL {1000.00 USD}
      Assets:Investments:Stock        10 HOOL  {500.00 USD}
      Assets:Investments:Stock        10 HOOLL {500.00 USD}

以这种方式拆分 lot 的一个问题是，拆分前后 HOOL 单位的价格和含义不同，但让我们暂时假设我们可以接受这一点（这可以通过使用另一个名称来*重新标记*商品来解决，理想情况下以一种对用户不可见的方式 - 我们在其他地方有一个[待讨论的事项](https://docs.google.com/document/d/1Y_h5sjUTJzdK1riRh-mrVQm9KCzqFlU65KMsMsrQgXk/)）。

与 booking 相关的问题是，当你卖出该头寸时，你使用哪个 cost？库存中将包含价格为 500 USD 的头寸，因此你应该使用这个价格，但这对用户来说是否显而易见？我们可以假设这可以通过一个 recipe 来学习。

现在，如果我们自动附加 transaction 日期会怎样？它在拆分时会被重置吗，现在你必须使用 2014-04-17？如果是这样，我们就无法自动检查交易列表来确定这是长期还是短期交易。我们需要以某种方式保留原始事件的某些属性，这些属性增强了该头寸，包括原始交易日期（而不是拆分日期）以及如果提供了的话，原始用户指定的头寸标签。

> Aditya Mehta (2019年4月13日) 提议：
>
> *建议将其纳入现有的 posting 结构：不是添加一个替换拆分前商品的单一条目，而是可以在针对拆分前商品进行的每笔 transaction 中添加带有日期的条目。例如，在上面的例子中，HOOL 在 2014-04-17 拆分，但最初是在 2014-01-04 购买的。不是在 2014-04-17 添加条目，而是可以在 2017-01-04 本身添加条目。这可以作为一个插件，其中拆分被报告为 2017-04-17 的一笔特殊 transaction，但以回溯日期的方式影响 account。*

### 强制每个账户使用单一方法<a id="forcing-a-single-method-per-account"></a>

对于将使用平均 booking 方法的账户，可能很有用[允许指定某账户应仅使用此 booking 方法](https://groups.google.com/d/msg/ledger-cli/aQvbjTZa7HE/55mx1LSM0sIJ)。其想法是，当我们知道某账户只能使用此方法时，避免数据录入错误。

确保这一点的一种方法是在增强（augment）持仓时自动聚合库存 lot。这确保了在任何时间点，每种商品只有一个 lot。如果我们为每个账户关联一种 inventory booking 类型，我们可以定义一种特殊类型，它在添加持仓时也触发聚合。

另一种方法是，不强制这些聚合，而是提供一个插件，用于检查那些被标记为默认使用平均成本 inventory booking 方法的账户，确保实际发生的只有此类 booking。

## 先前方案<a id="previous-solutions"></a>

本节回顾了命令行记账系统中现有的 booking 方法实现，并指出了促使我们需要定义新方法的特定不足之处。

### Ledger 中的不足<a id="shortcomings-in-ledger"></a>

*（请注意：我对 Ledger 内部机制的细微之处并不十分熟悉；我是通过构建测试示例和阅读文档来推断其行为的。如果我有任何错误，请通过留下评论告知我。）*

Ledger 对 booking 的处理方式相当宽松。在内部，[Ledger 不区分以 cost 持有的转换和以常规 price 进行的转换](http://www.google.com/url?q=http%3A%2F%2Fledger-cli.org%2F3.0%2Fdoc%2Fledger3.html%23Prices-versus-costs&sa=D&sntz=1&usg=AFQjCNGAZPEtX3TjQysbqsDnF48d5a29Hw)：所有转换都被假定为以 cost 持有，而交易 lot 仅在生成 report 时出现（使用其 `--lots` 选项）。

其 “`{}`” cost 语法是[旨在用于在减少持仓时区分 lot](http://ledger-cli.org/3.0/doc/ledger3.html#Explicit-posting-costs)，而不是在获取持仓时使用。获取持仓的 cost 是使用 “`@`” price 表示法来指定的：

    2014/05/01 * Buy some stock (Ledger syntax)
      Assets:Investments:Stock        10 HOOL @ 500 USD
      Assets:Investments:Cash

这将导致一个包含 10 HOOL {500 USD} 的库存，也就是说，cost 始终*存储*在持有该持仓的库存中：

    $ ledger -f l1.lgr bal --lots
    10 HOOL {USD500} [2014/05/01]
                USD-5000  Assets:Investments
                USD-5000    Cash
    10 HOOL {USD500} [2014/05/01]    Stock
    --------------------
    10 HOOL {USD500} [2014/05/01]
                USD-5000

以 cost 进行的转换和不带 cost 的转换之间没有区别——所有转换都像是“以 cost”那样被跟踪。正如我们将在下一节中看到的，这种行为与 Beancount 的语义不同，后者要求以 cost 持有的转换必须使用 “`{}`” 表示法来指定其增加和减少的 posting，并区分以 cost 持有的持仓和 price 转换。

Ledger 方法的优势在于更简单的输入机制，但如果在同一个 account 中累积了多种类型的货币转换，就会导致令人困惑的结果。库存很容易在其 lot 构成上变得碎片化。例如，考虑一下如果你在不同的方向上在 5 种不同的货币之间进行转换会发生什么……你很容易最终持有以 CAD、JPY、EUR 和 GBP 计价的 USD，反之亦然……这些货币的任何可能组合都是可能的。例如，以下货币转换将保持其相对于转换后货币的原始 cost：

    2014/05/01 Transfer from Canada
      Assets:CA:Checking             -500 CAD
      Assets:US:Checking              400 USD @ 1.25 CAD

    2014/05/15 Transfers from Europe
      Assets:UK:Checking             -200 GBP
      Assets:US:Checking              500 USD @ 0.4 GBP

    2014/05/21 Transfers from Europe
      Assets:DE:Checking             -100 EUR
      Assets:US:Checking              133.33 USD @ 0.75 EUR

这导致 `Assets:US:Checking` account 中出现以下库存：

    $ ledger -f l2.lgr bal --lots US:Checking
    500.00 USD {0.4 GBP} [2014/05/15]
    133.33 USD {0.75 EUR} [2014/05/21]
    400.00 USD {1.25 CAD} [2014/05/01]  Assets:US:Checking

货币被像股票一样对待。但是[没有人会这样思考他们的货币余额](https://groups.google.com/d/msg/ledger-cli/zRSMle5AV3Q/kBCYjVEB-gsJ)，人们通常将 account 中持有的货币视为其自身的单位，而不是相对于其他货币的 price。在我看来，这是令人困惑的。在这些转换之后，我只认为该 account 的余额是 1033.33 USD。

对此观察的一个可能反驳是，大多数时候用户并不关心仅包含货币的 account 的库存 lot，因此它们只是碰巧没有被打印出来。眼不见，心不烦。但是，没有办法区分渲染例程何时应该渲染 lot。如果被指示生成 report，balance 例程理想情况下应该只为某些 account（例如，investment account，其中单位的 cost 很重要）渲染 lot，而不为其他 account（例如，有时因转换而存入货币的 account）渲染。此外，当我渲染资产负债表时，对于以 cost 持有的单位，我们需要报告 book values 而不是股份数量。但对于货币，货币单位本身必须始终被报告。如果你不区分这两种情况，你如何知道该渲染哪一个？我认为答案是通过选项来选择你想要渲染的视图。问题是，两者都没有提供一个统一的视图，该视图对这两种类型的商品都执行正确的操作。用户不应该被迫指定选项以查看以一种或另一种风格部分错误的视图，这应该是自动的，并取决于我们是否关心这些单位的 cost。如果你区分这两种类型的转换，这个问题就会被正确处理。

但或许最重要的是，这种方法并没有特别解决*转换问题*：通过以不同汇率来回进行转换，仍然可以凭空创造资金：

    2014/05/01 Transfer to Canada
      Assets:US:Checking             -40000 USD
      Assets:CA:Checking              50000 CAD @ 0.80 USD

    2014/05/15 Transfer from Canada
      Assets:CA:Checking             -50000 CAD @ 0.85 USD
      Assets:US:Checking              42500 USD

这导致试算平衡表中只剩下 2500 USD：

    $ ledger -f l3.lgr bal 
                2500 USD  Assets:US:Checking

这不是一个理想的结果。我们应该要求试算平衡表的总和始终为零（虚拟 transaction 除外）。毕竟，这是复式记账法优雅之处的总体体现：因为所有 transaction 的总和为零，所以任何 transaction 子集的总和也应为零……但事实并非如此。在我看来，任何生成的资产负债表都应严格符合会计恒等式。

在我对 Ledger 的探索中，我曾希望凭借其库存跟踪方法，它能以某种方式自动处理这些转换，从而为按 cost 跟踪所有单位提供充分的理由，但我目睹了同样的问题出现。（转换问题在 Beancount 中是一个真正棘手的问题，需要费心寻找解决方案，但它现在运行正常，我认为同样的解决方案也可以应用于 Ledger，以调整这些总和，而无需改变其当前的 booking 方法：在战略位置自动插入一个特殊的转换条目——即在生成资产负债表时。）最终，我发现为每个 transaction 跟踪 cost 似乎并没有比忽略 price 转换中的 cost 更有优势，转换问题与此无关。我非常希望能听到更多关于支持这一设计选择的意见。

现在，由于所有转换都保持其 cost，Ledger 在 booking 方面必须相当宽松，因为在常见货币转换的情况下，强制用户为每种货币指定原始转换汇率会很不方便。这对那些我们希望按 cost 持有的转换产生了不幸的影响：允许任意的 lot 减少，即针对不存在的 lot 进行减少。例如，以下交易在 Ledger 中不会触发错误：

    2014/05/01 Enter a position
      Assets:Investments:Stock        10 HOOL @ 500 USD
      Assets:Investments:Cash

    2014/05/15 Sale of an impossible lot
      Assets:Investments:Stock       -10 HOOL {505 USD} @ 510 USD
      Assets:Investments:Cash

这导致库存中出现 10 HOOL 的多头头寸和 10 HOOL 的空头头寸（cost 不同）：

    $ ledger -f l4.lgr bal --lots stock
    10 HOOL {USD500} [2014/05/01]
       -10 HOOL {USD505}  Assets:Investments:Stock

我认为不应允许减少 505 USD 的 HOOL 头寸；Beancount 选择将此视为错误。

Ledger 显然支持针对现有库存进行 booking，因此其意图肯定是能够针对现有头寸进行减少。例如，以下交易确实会导致库存为空：

    2014/05/01 Enter a position
      Assets:Investments:Stock      10 HOOL @ 500 USD
      Assets:Investments:Cash

    2014/05/15 Sale of matching lot
      Assets:Investments:Stock     -10 HOOL {500 USD} [2014/05/01]  @ 510 USD
      Assets:Investments:Cash

输出如下：

    $ ledger -f l5.lgr bal --lots 
                  USD100  Equity:Capital Gains

如您所见，HOOL 头寸已被消除。（请不要介意输出中自动插入的权益条目，我相信这将在一个[待处理的补丁](http://bugs.ledger-cli.org/show_bug.cgi?id=712)中修复。）然而，必须同时指定日期和 cost 才能使其正常工作。以下交易会导致与上述类似的、具有问题性的多头 + 空头头寸库存：

    2014/05/01 Enter a position
      Assets:Investments:Stock      10 HOOL @ 500 USD
      Assets:Investments:Cash

    2014/05/15 Sale of matching lot?
      Assets:Investments:Stock     -10 HOOL {500 USD} @ 510 USD
      Assets:Investments:Cash

输出如下：

    $ ledger -f l6.lgr bal --lots 
    10 HOOL {USD500} [2014/05/01]
       -10 HOOL {USD500}  Assets:Investments:Stock
                  USD100  Equity:Capital Gains
    --------------------
    10 HOOL {USD500} [2014/05/01]
       -10 HOOL {USD500}
                  USD100

这有点令人惊讶，我预期 lot 会相互抵消。我怀疑这可能是一个未报告的 bug，而非预期行为。

评论：在我看来，inventory 的 booking 机制绝对不应该是一个 report 层面的功能。在 Ledger 中，情况似乎正是如此：如果我阅读其文档，其中提到：“--lot-prices: Report the price at which ...”。这告诉我，Ledger 并不执行任何 inventory 的 booking，它只是将所有这些 lot 添加在一起，然后 booking 发生在 report 期间的“grouping”过程中。是这样吗？这也解释了为什么它允许卖出其 inventory 中不存在的 lot。在 Beancount 中，lot 的减少发生在解析之前。这一点很重要：我强制要求你不应能够卖出一个不存在的 lot。这也为实施本提案打开了大门。

最后，“`{}`” cost 语法也允许在 augmenting legs 上使用。文档[指出这些方法是等效的](http://ledger-cli.org/3.0/doc/ledger3.html#Prices-versus-costs)。这会导致一个没有关联日期的 inventory lot，但另一条 leg 并未转换为 cost：

    2014/05/01 Enter a position
      Assets:Investments:Stock      10 HOOL {500 USD}
      Assets:Investments:Cash

输出如下：

    $ ledger -f l7.lgr bal --lots
                       0  Assets:Investments
       -10 HOOL {USD500}    Cash
        10 HOOL {USD500}    Stock
    --------------------
                       0

我可能只是不理解这是如何被使用的；在 Beancount 中，自动计算的 leg 会向 Cash account 记录 -5000 USD 的金额，而不是股份。

我认为正在发生的事情是，Ledger（可能）累积所有 lot，而不尝试将它们匹配在一起以进行减少，然后在 report 时——且仅在 report 时——根据某些 report 选项将 lot 匹配在一起：

-   使用 --lots 按 cost/price 和日期对 lot 进行分组

-   使用 --lot-prices 仅按 cost/price 对 lot 进行分组

-   使用 --lot-dates 仅按日期对 lot 进行分组

从文档中并不完全清楚其工作原理，但行为与此一致。

（如果这是正确的，我认为这是其设计中的一个问题：inventory 减少如何 booking 到现有 lot 集合的机制绝对不应该是一个 report 功能。它需要在处理 report 之前发生，以便实现单一且确定的 inventory booking 历史。如果支持 booking 的变体——我认为这不是一个好主意——它们应该在 report 阶段之前得到支持。在我看来，通过命令行选项更改 inventory booking 策略是一个坏主意，现有的策略应该完全由语言本身定义。）

### Beancount 的不足之处<a id="shortcomings-in-beancount"></a>

Beancount 也存在各种各样的不足，尽管这些不足与 Ledger 有所不同。

与 Ledger 不同，Beancount [区分](https://groups.google.com/d/msg/ledger-cli/zRSMle5AV3Q/kBCYjVEB-gsJ)了货币兑换和“按成本持有”的转换：

    2014-05-01 * "Convert some Loonies to Franklins"
      Assets:CA:Checking          -6000 CAD
      Assets:Investments:Cash      5000 USD @ 1.2 CAD   ; Currency conversion

    2014-05-01 * "Buy some stock"
      Assets:Investments:Stock        10 HOOL {500 USD} ; Held at cost
      Assets:Investments:Cash

在第一个 transaction 中，`Assets:Investment:Cash` account 的结果是 5000 USD 的库存，且没有关联任何 cost。然而，在第二个 transaction 之后，`Assets:Investment:Stock` account 拥有 10 HOOL 的库存，并关联了 500 USD 的 cost。这或许稍微复杂一些，并且要求用户具备更多的知识：存在两种类型的转换，用户必须理解并区分这两种情况，这对于系统的新手来说并不直观。需要一定的用户教育（我承认，如果我编写更多的文档，这会很有帮助）。

Beancount 的方法也较为严格，它要求严格应用 lot 减少。也就是说，如果你输入一个减少不存在的 lot 的 transaction，它将输出错误。这样做的动机是让用户难以在数据录入时犯错。库存中头寸的任何减少都必须与恰好一个 lot 匹配。

这种选择带来了一些缺点：

-   它要求用户始终找到要匹配的 lot 的 cost。这意味着自动化导入 transaction 需要用户的人工干预，因为用户必须去账本中搜索并插入匹配的 lot。（请注意，理论上导入代码可以加载账本内容以列出其持仓，如果无歧义，可以自行查找 cost 并将其插入输出。但这会使导入代码依赖于用户的账本，而大多数导入代码并没有这样做）。这是一个重要的步骤，因为找到正确的 cost 是正确计算资本利得的必要条件，但人们希望有一种更灵活的方法，允许用户稍微懒一点，在选择明显时（例如，当只有一个该单位的 lot 可供匹配时）不必输入现有头寸的 cost。我希望在一定程度上放宽这种方法。

-   严格地要求针对现有 lot 进行减少，也意味着在同一 account 中，同一商品“按成本持有”的做多和做空头寸不能同时存在。然而，这在实践中并不是一个大问题，因为做空头寸相当罕见——很少有个人参与——如果需要，用户始终可以创建单独的 account 来持有做空头寸。事实上，在 investment account 中为每种商品创建专用的子 account 已经是惯例，因为它能很好地组织交易活动（否则 report 会显得有点混乱，按股票分组查看总头寸价值是很好的，因为它们提供了对不同市场特征的风险敞口）。只要我们在减少时正确处理符号，不同的 account 应该能很好地工作，即，针对现有做空头寸买入股票被视为头寸减少（符号只是反转）。

Beancount booking 方法的另一个问题在于它如何匹配带有日期的 lot。例如，如果你试图区分两个价格相同的 lot，最明显的输入将不起作用：

    2012-05-01 * "First trade"
      Assets:Investments:Stock        10 HOOL {500 USD}
      Assets:Investments:Cash

    2014-02-15 * "Second trade at very same price"
      Assets:Investments:Stock         8 HOOL {500 USD}
      Assets:Investments:Cash

    2014-06-30 * "Trying to sell"
      Assets:Investments:Stock        -5 HOOL {500 USD / 2012-05-01}
      Assets:Investments:Cash

这将报告一个 booking 错误。这令人困惑。在这种情况下，Beancount 出于严格的愿望，对库存 lot 应用严格匹配，尝试将 (HOOL, 500 USD, 2012-05-01) lot 的单位与 (HOOL, 500 USD, *None*) 的单位匹配会直接失败。请注意，lot 日期语法在 Beancount 中既被接受用于增加腿，也被接受用于减少腿，因此“解决方案”是用户被迫在获取头寸时明确提供 lot 日期。例如，这样是可以工作的：

    2012-05-01 * "First trade"
      Assets:Investments:Stock        10 HOOL {500 USD / 2012-05-01}
      Assets:Investments:Cash

    2014-02-15 * "Second trade at very same price"
      Assets:Investments:Stock         8 HOOL {500 USD}
      Assets:Investments:Cash

    2014-06-30 * "Trying to sell"
      Assets:Investments:Stock        -5 HOOL {500 USD / 2012-05-01}
      Assets:Investments:Cash

这里的麻烦在于，当用户输入第一笔交易时，他无法预见到未来会以相同价格再输入另一笔交易，因此通常不会插入 lot-date。更可能的情况是，用户不得不回过头去重新审视该 transaction，以消除歧义。我们可以做得更好。

这是其实现中的一个缺陷，它反映了这样一个事实：头寸减少最初被视为一个精确匹配问题，而非模糊匹配问题——当时我并不清楚如何安全地处理这种情况。在这项提案之后，这需要得到修复。而我在本文档中所做的，很大程度上是一个自我澄清的过程，旨在明确我希望这种模糊匹配意味着什么，并确保我能够提出一个无歧义的设计，便于数据录入。Ledger 始终会自动将 transaction 日期附加到 inventory lot 上，在我看来，这是正确的做法（下文我们还建议附加更多信息）。

## 背景 <a id="context"></a>

*\[Updated on Nov’2014\]*

区分两种类型的 booking 至关重要：

1.  **Booking。** 这是一种严格的 booking 类型，发生在我们考虑整个 transaction 列表时。我们将此称为 “booking” 过程，它应该只发生一次。这个过程应该是严格的：如果无法正确地将减少操作 book 到现有的 lot 上，应该触发致命错误。

2.  **Inventory Aggregation。** 当我们考虑条目子集时，可能会出现某些添加 lot 的条目被移除，而减少或移除这些 lot 的其他条目被保留的情况。这创造了一种必须支持对库存变化进行随时间聚合的情况，而这些变化可能无法匹配到对应的 lot。如果我们希望支持对任意 transaction 子集进行聚合，就必须考虑到这一点。这种聚合过程永远不应导致错误。

让我们举一个例子来说明为什么我们需要非 booking 的汇总。假设我们有一笔股票购买和出售：

    2013-11-03 * "Buy"
      Assets:Investments:VEA      10 AAPL {37.45 USD} ;; (A)
      Assets:Investments:Cash     -370.45 USD

    2014-08-09 * "Sell"
      Assets:Investments:VEA     -5 AAPL {37.45 USD}
      Assets:Investments:Cash     194.40 USD
      Income:Investments:PnL

如果我们按“年份”过滤，只想查看发生在 2014 年的 transaction，并且我们并不“关闭”上一年度，也就是说，我们不会创建在年初将 lot 存入 account 的期初余额条目——这种情况可能发生在我们按 tag 或某些其他条件组合进行过滤时——那么 (A) lot 并不存在于需要从中借出的 inventory 中。我们必须以某种方式在该点容纳 -5 AAPL。在报告时，用户可以决定如何汇总并“尽可能匹配”这些 legs，但可以将它们转换为 units 或 cost，或者将它们转换为按平均成本计算的单个 lot。

然而，booking 过程不应允许这种宽松。它应该是严格的，如果 lot 无法匹配，则应触发错误。这仅应用于 transaction 的总集合，且仅执行一次，绝不对任何子集执行。booking 阶段的目的应该是三重的：

1.  **Match** 现有的 lot，并在不可能时发出错误。使用用户指定的方法执行此操作。

2.  **Replace** 所有部分指定的 lot 为完整的 lot 规格，即在 booking 过程中匹配到的 lot。

3.  **Insert links** 在构成交易的 transaction 上：买入和相应的卖出应该链接在一起。这基本上识别了交易，然后可以在后续报告中加以利用。（按平均成本进行的交易需要特殊考虑。）

我们可以将 Ledger 的方法视为仅具有聚合方法，缺乏 booking 阶段。聚合的具体方法是通过 --lots 或 --lot-dates 或 --lot-prices 选择的。这表明可以在不改变 Ledger 总体结构太多的情况下，为其附加一个 “booking” 阶段：它可以作为前处理或后处理插入，但这要求 Ledger 按日期对 transaction 进行排序，而它目前并没有这样做（它对数据执行单次遍历）。

Beancount 已经同时拥有这两种方法一段时间了，但这两种操作的独立性质此前并未明确陈述——相反，inventory 支持一个可选标志，在 booking 不可能时引发错误。此外，inventory aggregation 并未被认为需要大量定制，它旨在与 booking 过程统一。现在很清楚，它们是两个不同的算法，并且几种不同的聚合方法可能是相关的（尽管它们的功能与 Ledger 的不同。注意：你可以将 inventory aggregation 方法视为 Inventory 对象 lot 中的 GROUP BY：你对哪些列进行分组？这需要用例）。无论如何，完全指定的 lot 默认情况下应该相互匹配：我们需要支持这种退化情况，用于简单货币（不按 cost 持有）……我们不希望将同一货币的所有变化作为 inventory 中的不同 lot 累积，它们需要在应用时立即相互抵消。

我们希望对此进行修改，以使代码更加清晰：应该有一个独立的“booking”阶段，由一个**plugin**提供，该阶段使用本文档中概述的算法来解决部分指定的 lot 减少问题；而独立的库存聚合方法则不应涉及这些细节。实际上，库存聚合可以简单地变为一个累积的 lot 列表，而它们的汇总可以在事后进行，其概念类似于 Ledger 应用其聚合的方式。一旦我们开始输入关于 lot 的更具体数据，例如始终包含获取日期、标签，甚至可能还有指向创建该 lot 的 entry 的链接，使用简单的聚合就变得更为相关。为了合理地触发汇总，可以在 shell 中提供用于转换和汇总累积库存的函数，例如“UNITS(inventory)”。

## 插值的精度<a id="precision-for-interpolation"></a>

插值功能将被扩展，以支持省略任意子集 posting 中的单个数字（任意数量），这些 posting 的“权重”解析为特定货币（例如，“所有权重为 USD 的 posting”）。插值需要在特定精度下发生。插值出的数字应自动进行量化，而量化到的小数位数应自动从 DisplayContext 推断得出，该 DisplayContext 本身派生自输入文件。应使用文件中观察到的最常见或最大位数。

关于一个用例，请参阅[此线程](https://groups.google.com/d/msg/beancount/2fUcidr7oEs/Z-Fpzo0VYZMJ)：

*On Mon, Nov 24, 2014 at 12:33 PM, ELI &lt;eliptus@gmail.com&gt; wrote:*

*关于你我之间似乎存在误解的最后一点，让我提供一个独立示例，脱离插件的上下文。由于 Vanguard 只向我提供三位小数的精度，我需要根据价格和 transaction 金额计算实际的股份数量。*

*例如，我在我的活动页面上有一笔 transaction，详情如下：*

*Shares Transacted: 0.000*

*Share Price: 48.62*

*Amount: 0.02*

*要输入这笔 transaction 并使其平衡，唯一的方法是手动计算具有四位小数精度的 Shares Transacted。我首选的输入方式是输入 Share Price 和 Amount，然后让 Beancount 根据与我 Vanguard 账户关联的精度计算 Shares Transacted。此外，作为元数据，我会记录 "Shares Transacted: 0.000" 作为“对账单上写了什么”的历史记录。*

*也许你可以告诉我，使用计划中的 Beancount 功能或我可以编写的插件，如何处理这种情况？*

可下载的文件中包含什么？是 0.000 还是 0.0004，甚至是 0.00041？

这很可能就是他们收取的季度费用，他们以股份为单位进行定价。如果这是你的 Vanguard 账户，并且你将其周围所有类似的 transaction 相加，你应该会发现总和为每季度 5 美元。

我会这样记录：

      2014-11-23 * "Quarterly fee"
        Assets:US:Vanguard:VIIPX      -0.00041 VIIPX {* 48.62 USD}
        Expenses:Financial:Fees    0.02 USD

“\*” 是必需的，用于将所有 lot 合并为一个（平均成本 booking），因为他们声明的 48.62 USD \_不是\_ 你的某个 lot，而只是他们收取费用那天该资产恰好存在的 price。换句话说，他们以每种资产的单位收取费用，按当前 price 计价，并从你所有 lot 的 cost basis 中扣除（因为这是一个税前账户，所以不报告资本利得，因此具体扣除哪个 lot 并不重要）。

现在你问，我如何避免自己计算 0.00041？

我的第一个回答是：让我们先看看来自 Vanguard 的 OFX 下载是否包含精度。如果是，那就解决了。我相信它包含（我检查了我自己的下载历史，里面有一些具有 4 位小数的数字）。

我的第二个回答是——如果你没有从文件中获取股份数量——在我实现急需的新 inventory booking 提案（[http://furius.ca/beancount/doc/proposal-booking](http://furius.ca/beancount/doc/proposal-booking)）之后，插值功能将大大扩展，以至于甚至可以省略股份数量，如下所示：

      2014-11-23 * "Quarterly fee"
        Assets:US:Vanguard:VIIPX      VIIPX {* 48.62 USD}
        Expenses:Financial:Fees    0.02 USD

仅凭这一点仍然无法解决问题：这将存储 0.000411353353，由于默认 context 的限制，它被限制在 12 位小数。因此这是不正确的。**为了处理这个问题，需要推断 VIIPX 单位上使用的最常见位数，并将结果量化到该位数（我认为这应该是足够安全的）。文件中每种货币出现的位数** 已经在从解析器存储在 options\_map 中的 DisplayContext 对象中跟踪。我必须在 inventory booking 提案中考虑到这一点。我将把它添加到提案中。

## 需求<a id="requirements"></a>

前面的章节介绍了 booking 的一般性问题，并指出了 Beancount 和 Ledger 实现中的重要缺陷。本节将提出一组针对命令行记账软件实现中新的、改进的 booking 机制的期望。

以下是新方法应具备的合理需求：

-   需要支持**显式的 inventory lot 选择**。用户应能够精确地指定针对哪一笔 lot 来减少持仓，且需按 transaction 进行指定。某个 account 或商品不应被强制要求在所有交易中都应用一致的方法。

-   显式的 inventory lot 选择应**支持部分匹配**，也就是说，在待匹配的 lot 存在歧义的情况下，用户应能够仅提供最少量的信息来消除歧义，例如日期、标签、cost 或这些信息的组合。例如，如果只有一个可用的 lot 可供匹配，用户应能够指定 cost 为“`{}`”，指示系统按 cost 进行 booking，但这本质上意味着：“针对任意 lot 进行 booking。”只有当存在多个 lot 时，才应触发错误。

-   应支持多种信息来指定一个现有的 lot，并且这些信息应可组合：

    -   该持仓的获取 cost；

    -   获取该持仓的日期；

    -   用户提供的标签。

-   当提供的信息不足以进行显式 lot 选择时，应允许调用**默认 booking 方法**。用户应能够**全局**以及**按 account** 指定默认的 booking 方法。这为**隐式 lot 选择**铺平了道路。应提供一种退化方法，该方法会触发错误并要求用户显式指定。

-   需要支持**平均 cost booking**，因为它在退休账户或免税账户中非常常见。这是加拿大投资账户中使用的默认方法。

-   同样需要支持**cost basis 调整**。该问题应能够通过提供一个特定的 lot（或按平均 cost 计算的所有某商品的 lot）以及一个*美元金额*来指定，以调整该持仓。

-   **股票拆分**需要能够**保留持仓的部分原始属性**，具体来说，如果提供了原始交易日期和用户指定的标签，则应保留这些属性。这应允许使用一种通用语法，在拆分后减少持仓时指定原始交易 lot。

-   减少持仓时，需要**始终针对现有的 lot 进行 booking**。这里我保留了 Beancount 的行为，正如我之前所论证的，因为它运行良好，并且是避免数据输入错误的好方法。这自然地为 inventory 定义了一个不变量：*在单个 inventory 中，以 cost 持有的特定商品的所有持仓应具有相同的符号*（这可以用作健全性检查）。

-   **改变单位数量符号的 booking 应引发错误**，除非明确要求例外（我甚至不确定我们是否需要这种例外）。再次注意，booking 仅针对以 cost 持有的单位发生，因此货币转换不受此需求影响。Beancount 已经具备此功能一段时间了，并证明在检测错误方面很有用。例如，如果一个 inventory 中有 8 HOOL {500 USD} 的持仓，而你尝试向该 lot 记录 -10 个单位的变更，结果单位数量变为负数：-2。这应表明用户错误。我能想到的允许这种情况的唯一用例是期货价差和货币的交易，这些交易自然会报告在同一个 account 中（货币的空头头寸不像其他工具的空头头寸那样被视为不同的工具）；这是提供例外的唯一原因，我怀疑 99% 的用户不需要它。\]

### 调试工具<a id="debugging-tools"></a>

由于这是录入交易数据过程中一个非平凡但极其重要的部分，我们应该提供工具来详细列出 inventory 的 running balance，包括其所有 lot 的详细信息。

报告的 booking 错误应包含足够的上下文，即：

-   包含违规 posting 的 transaction

-   违规的 posting

-   在应用该 posting 之前 inventory 的当前状态，包括其所有 lot

-   当前生效的隐式 booking 方法，用于区分不同的 lot

-   booking 失败的具体原因

### 显式与隐式 Booking 减少<a id="explicit-vs.-implicit-booking-reduction"></a>

在设计新的 booking 方法时，另一个可能出现的问题是，我们是否要求用户*显式*地表明他认为这是一笔持仓的增加还是减少。例如，可以通过要求对 cost 使用略有不同的语法来实现这一点，比如“`{}`”表示增加，而“`[]`”表示减少。我不确定是否有必要做出这种区分，也许给用户带来的额外负担并不值得，但这可能是一种将预期与实际发生的计算进行交叉核对的方式。我暂时搁置这个想法。

## 设计提案<a id="design-proposal"></a>

本节提出了一个具体设计描述，以满足前文引入的需求。我们力求保持其尽可能简单。

### inventory <a id="inventory"></a>

Inventory 本质上是一个 lot 描述符的列表。每个 inventory lot 将由以下字段定义：

    UNITS, (CURRENCY, COST-UNITS, COST-CURRENCY, DATE, LABEL)

字段说明：

-   UNITS：该 lot 持有的单位数量

-   CURRENCY：持有的商品类型，一个字符串

-   COST-UNITS：该 lot 的 price 中的数量

-   COST-CURRENCY：cost 的计价商品

-   DATE：该 lot 的获取日期

-   LABEL：用于标识此 lot 的任意用户指定字符串

如果这代表一个以 cost 持有的 lot，在此处理之后，只有 LABEL 字段可以可选地为 NULL 值。任何针对此 inventory 编写代码的人都可以预期，所有其他值都已填充为非 NULL 值（或者它们全部为 NULL）。

### 输入语法与过滤<a id="input-syntax-filtering"></a>

输入语法应允许以以下信息的任意组合来指定 cost：

-   **单位成本**，以金额形式表示，例如 “`500 USD`”

-   **总成本**，将自动除以单位数量，如下所示：`{... +9.95 USD}`。您应该能够使用单位成本、总成本，甚至将两者结合使用，如下所示：`{500 + 9.95 USD}`。这对于输入佣金非常有用。此语法还取代了之前的 `{{`...`}}` 语法。

-   **lot-date**，格式为 YYYY-MM-DD 的日期，例如 “`2014-06-20`”

-   **label**，即任何非数字标识符，例如 first-apple 或类似 “`aa2ba9695cc7`” 的随机 uuid

-   一个**特殊标记** “`*`”，表示按库存余额的平均成本进行 booking

以下 posting 均应为有效语法：

    ...
      Assets:Investments:Stock        10 HOOL {500 USD}      ; cost
      Assets:Investments:Stock        10 HOOL {339999615d7a} ; label
      Assets:Investments:Stock        10 HOOL {2014-05-01}   ; lot-date
      Assets:Investments:Stock        10 HOOL {}             ; no information

    ... 组合
      Assets:Investments:Stock        10 HOOL {500 USD, 2014-05-01}
      Assets:Investments:Stock        10 HOOL {2014-05-01, 339999615d7a}

### 算法<a id="algorithm"></a>

所有 posting 应在解析后的独立步骤中，按照日期顺序，针对每个 account 的实时库存余额进行处理。在此阶段，cost 金额应被完全确定；如果无法解析 cost，则应引发错误，并将该 transaction 从 directive 流中删除（在程序大声抱怨之后）。

在处理条目时，我们应根据用户提供的过滤器，对所有库存 lot 进行匹配和筛选。通常，在使用用户限制条件筛选 lot 之后：

-   如果 lot 集合为空，应引发错误；
-   如果只有一个 lot，则应选择该 lot（成功情况）；
-   如果有多个 lot，则应调用对应 account 的**默认隐式 booking 方法**。

### 隐式 Booking 方法<a id="implicit-booking-methods"></a>

如果在 booking 过程中存在多个匹配的 lot 可供选择，则可以调用以下隐式 booking 方法：

-   STRICT：选择库存中唯一的 lot。如果存在多个 lot，则引发错误。

-   FIFO：选择日期最早的 lot。

-   LIFO：选择日期最晚的 lot。

-   AVERAGE：以平均 cost 记录此 transaction。

-   AVERAGE_ONLY：类似于 AVERAGE，但在向持仓添加时也会触发聚合。这可用于强制规定所有 lot 的唯一 booking 方法均为平均 cost。

-   NONE：不在此 account 上执行任何库存 booking。允许同一 commodity 的 lot 混合，或允许库存中出现正数和负数。（这实际上退化为 Ledger 的 booking 方法。）

此方法*仅*在需要对多个 lot 进行消歧时才会被调用，即在根据用户提供的表达式对 lot 进行过滤之后。`STRICT` 方法基本上是一种退化的消歧方式，如果存在任何歧义就会引发错误，并且应当作为默认值。

应该有一个适用于所有 account 的默认方法。默认值应当可以被覆盖。在 Beancount 中，我们将添加一个新的“option”以允许用户更改此设置：

    option "booking_method" "FIFO"

特定 account 中使用的默认值也应该可以指定，因为方法因 account 而异且在 account 内固定是一个常见情况。在 Beancount 中，这可能会成为 open directive 的一部分，类似于以下内容：

    2003-02-17 open Assets:Ameritrade:HOOL  HOOL  booking:FIFO

（我不确定语法。）

#### 解决同日期歧义<a id="resolving-same-date-ambiguity"></a>

如果自动 booking 方法被调用来解决模糊的 lot 减少（例如 FIFO），而存在多个相同日期的 lot，则需要采取措施来确定选择哪个 lot。应选择 transaction 出现的行号。例如，在以下情况中，将选择 8 GBP 的 WIDGET：

    2014-10-15 * "buy widgets"
      Assets:Inventory     10 WIDGET {} ;; Price inferred to 8 GBP/widget
      Assets:Cash         -80 GBP

    2014-10-15 * "buy another widget"
      Assets:Inventory      1 WIDGET {} ;; Price inferred to 9 GBP/widget
      Assets:Cash          -9 GBP

    2014-10-16 * "sell a widget"
      Assets:Cash           11 GBP 
      Assets:Inventory      -1 WIDGET {} ;; Ambiguous lot

### 默认插入的日期<a id="dates-inserted-by-default"></a>

默认情况下，如果 cost 中未显式指定日期，则持有该 posting 的 transaction 的日期会自动附加到交易 lot 上。该日期可以被覆盖，以便通过类似以下 transaction 的转换来实现股票拆分：

    2014-01-04 * "Buy some HOOL"
      Assets:Investments:Stock   10 HOOL {1000.00 USD}
      Assets:Investments:Cash

    2014-04-17 * "2:1 split into Class A and Class B shares"
      Assets:Investments:Stock  -10 HOOL {1000.00 USD, 2014-01-04} ; reducing
      Assets:Investments:Stock   10 HOOL  {500.00 USD, 2014-01-04} ; augment
      Assets:Investments:Stock   10 HOOLL {500.00 USD, 2014-01-04} ; augment

### 无信息匹配<a id="matching-with-no-information"></a>

对于 cost 不提供任何信息应当是被支持的，并且在某些情况下是有用的：在*增加*持仓的情况下，如果其他所有 legs 都指定了值，我们应该能够自动推断出所交易单位的 cost：

    2012-05-01 * "First trade"
      Assets:Investments:Stock            10 HOOL {}
      Assets:Investments:Cash       -5009.95 USD
      Expenses:Commissions              9.95 USD

在*减少*持仓的情况下——我们可以通过查看将 transaction 应用于其 account 余额时的 inventory 来确定是否属于这种情况——空规格应触发默认的 booking 方法。例如，如果方法是 STRICT，那么只有当只有一个 lot 可用时（选择是无歧义的），才会选择该 lot，如果交易不频繁，这很可能是一个常见情况。其他方法将按其定义应用。

请注意，用户仍然必须指定 cost 为“`{}`”，以告知我们此 posting 必须被视为“按成本持有”。这对于区分没有关联 cost 的价格转换非常重要。

### 减少多个 Lot<a id="reducing-multiple-lots"></a>

如果一笔交易需要关闭库存中的多个现有 lot，可以通过为每个 lot 插入一个 posting 来轻松处理。我认为这是一个完全合理的需求。例如，如果你的经纪商允许，这可能代表一笔单一交易：

    2012-05-01 * "Closing my position"
      Assets:Investments:Stock           -10 HOOL {500 USD}
      Assets:Investments:Stock           -12 HOOL {510 USD}
      Assets:Investments:Cash       12000.00 USD
      Income:Investments:Gains

注意：如果 lot 的 cost basis 规格匹配库存中的多个 lot，且结果没有歧义，这些 lot 将被正确选择。例如，如果之前的库存仅包含这两个 lot（总共 22 HOOL），你应该能够使用像这样的单个减少 posting：

    2012-05-01 * "Closing my position"
      Assets:Investments:Stock           -22 HOOL {}
      Assets:Investments:Cash       12000.00 USD
      Income:Investments:Gains

并且它们都会被包含在内。

另一方面，如果结果存在歧义（例如，如果你拥有超过这两个 lot），则会调用该 account 的 booking 策略。默认情况下，该策略将是 "STRICT"，这将生成一个错误，但如果该 account 的策略设置为 "FIFO"（或者未设置且默认全局策略为 "FIFO"），FIFO lot 将按你的意愿自动为你选择。

### lot basis 修改 <a id="lot-basis-modification"></a>

另一个想法是支持在单个 leg 中修改特定 lot 的 cost basis。其实现方式可以是：指定要修改的单位数量，并使用 “+ number currency” 语法来按特定数值调整 cost basis，例如：

    2012-05-01 * "Adjust cost basis by 250 USD for 5 of the 500 USD units"
      Assets:Investments:Stock            ~5 HOOL {500 + 250 USD} 

如果指定的单位数量小于该 lot 中的总单位数量，则在应用 cost basis 调整之前先拆分该 lot。*我不确定我是否喜欢这种方式。*

不指定数量也可以调整整个持仓（我不确定这是否合理，因为它与当前语法差异很大）：

    2012-05-01 * "Adjust cost basis by 250 USD for the 500 USD units"
      Assets:Investments:Stock            HOOL {500 + 250 USD} 

无论如何，除总 cost 调整值以外的所有字段都将用于选择要调整哪个 lot。

### 标签复用<a id="tag-reuse"></a>

在 inventory booking 中，我们必须小心处理 lot 标签的复用问题，并对此发出警告。标签应当是唯一的。

## 示例<a id="examples"></a>

没有什么比具体的例子更能说明问题了。除非另有说明，我们假设 `Assets:Investments:Stock` 账户上的 booking 方法为 `STRICT`。

### 无冲突<a id="no-conflict"></a>

给定以下库存 lot：

> 21, (HOOL, 500, USD, 2012-05-01, null)
>
> 22, (AAPL, 380, USD, 2012-06-01, null)

此 booking 应当成功：

    2013-05-01 *
      Assets:Investments:Stock           -10 HOOL {}
      ...

此 booking 应当失败（因为数量不是有效的 lot 之一）：

    2013-05-01 *
      Assets:Investments:Stock           -10 HOOL {520 USD}
      ...

此 booking 也应当失败（没有匹配货币的 lot）：

    2013-05-01 *
      Assets:Investments:Stock           -10 MSFT {80 USD}
      ...

此 booking 也应当失败（指定日期时日期无效）：

    2013-05-01 *
      Assets:Investments:Stock           -10 HOOL {500 USD, 2010-01-01}
      ...

### 按成本显式选择<a id="explicit-selection-by-cost"></a>

给定以下库存：

> 21, (HOOL, 500, USD, 2012-05-01, null)
>
> 32, (HOOL, 500, USD, 2012-06-01, “abc”)
>
> 25, (HOOL, 510, USD, 2012-06-01, null)

此 booking 应当成功：

    2013-05-01 *
      Assets:Investments:Stock           -10 HOOL {510 USD}
      ...

如果股票账户的 method 为 STRICT（存在歧义），此 booking 应当失败：

    2013-05-01 *
      Assets:Investments:Stock           -10 HOOL {500 USD}
      ...

如果股票账户的 method 为 FIFO，此 booking 应当成功，并针对 2012-05-01 的 lot（最早）进行 booking：

    2013-05-01 *
      Assets:Investments:Stock           -10 HOOL {500 USD}
      ...

### 按日期显式选择<a id="explicit-selection-by-date"></a>

给定与之前相同的库存，此 booking 应当成功：

    2013-05-01 *
      Assets:Investments:Stock           -10 HOOL {2012-05-01}
      ...

如果方法为 STRICT（存在歧义），此 booking 应当失败：

    2013-05-01 *
      Assets:Investments:Stock           -10 HOOL {2012-06-01}
      ...

### 通过标签显式选择<a id="explicit-selection-by-label"></a>

此 booking 应当成功，因为只有一个带有 “abc” 标签的 lot：

    2013-05-01 *
      Assets:Investments:Stock           -10 HOOL {abc}
      ...

如果多个 lot 具有相同的标签，则可能出现歧义情况；例如，对于以下 inventory：

> 32, (HOOL, 500, USD, 2012-06-01, “abc”)
>
> 31, (HOOL, 510, USD, 2012-07-01, “abc”)

相同的 booking 将会失败。

### 通过组合进行显式选择<a id="explicit-selection-by-combination"></a>

在初始 inventory 的情况下，此 booking 应该成功（无歧义）：

    2013-05-01 *
      Assets:Investments:Stock           -10 HOOL {500 USD, 2012-06-01}
      ...

只有一个 lot，其 cost 为 500 USD，获取日期为 2012-06-01。

### 单位不足<a id="not-enough-units"></a>

以下 booking 在语义上是明确的，但会执行失败，因为 inventory 中该 lot 的单位数量不足以进行扣减：

    2013-05-01 *
      Assets:Investments:Stock           -33 HOOL {500 USD, 2012-06-01}
      …

### 同一 Lot 的冗余选择<a id="redundant-selection-of-same-lot"></a>

如果在一个 transaction 中，两个独立的 posting 选择了同一个 inventory lot，它应该能够正常工作：

    2013-05-01 *
      Assets:Investments:Stock           -10 HOOL {500 USD, 2012-06-01}
      Assets:Investments:Stock           -10 HOOL {abc}
      ...

当然，如果股份数量不足，它应该失败：

    2013-05-01 *
      Assets:Investments:Stock           -20 HOOL {500 USD, 2012-06-01}
      Assets:Investments:Stock           -20 HOOL {abc}
      ...

### 自动价格外推<a id="automatic-price-extrapolation"></a>

如果一笔 transaction 的所有 posting 都可以计算其余额，则允许自动计算单一 price——这应该可以正常工作：

    2014-03-15 * "Adjust cost basis from 500 USD to 510 USD"
      Assets:US:Invest:HOOL      -10.00 HOOL {500.00 USD}
      Assets:US:Invest:HOOL       10.00 HOOL {}
      Income:US:Invest:Gains    -340.51 USD

并产生以下等效结果：

    2014-03-15 * "Adjust cost basis from 500 USD to 510 USD"
      Assets:US:Invest:HOOL      -10.00 HOOL {500.00 USD}
      Assets:US:Invest:HOOL       10.00 HOOL {534.51 USD}
      Income:US:Invest:Gains    -340.51 USD

当然，保留 lot 的原始日期也应该可以正常工作，因此以下写法也应该有效：

    2014-03-15 * "Adjust cost basis from 500 USD to 510 USD"
      Assets:US:Invest:HOOL      -10.00 HOOL {500.00 USD}
      Assets:US:Invest:HOOL       10.00 HOOL {2014-02-04}
      Income:US:Invest:Gains    -340.51 USD

### 平均成本 Booking<a id="average-cost-booking"></a>

使用平均成本语法增加 lot 应当失败：

    2014-03-15 * "Buying at average cost, what does this mean?"
      Assets:US:Invest:Stock      10.00 HOOL {*}
      Income:US:Invest:Gains   -5000.00 USD

减少应当有效，这是主要的使用场景：

    2014-03-15 * "Buying a first lot"
      Assets:US:Invest:Stock      10.00 HOOL {500.00 USD}
      Assert:US:Invest:Cash    -5000.00 USD

    2014-04-15 * "Buying a second lot"
      Assets:US:Invest:Stock      10.00 HOOL {510.00 USD}
      Assets:US:Invest:Cash    -5100.00 USD

    2014-04-28 * "Obtaining a dividend in stock"
      Assets:US:Invest:Stock         1.00 HOOL {520.00 USD}
      Income:US:Invest:Dividends  -520.00 USD

    2014-05-20 * "Sell some stock at average cost"
      Assets:US:Invest:Stock      -8.00 HOOL {*}
      Assets:US:Invest:Cash     4240.00 USD
      Income:US:Invest:Gains    ; Automatically calculated: -194.29 USD        

其效果是将 10 HOOL {500.00 USD} 的 lot、10 HOOL {510.00 USD} 的 lot 以及 1.00 HOOL {520.00 USD} 的 lot 聚合为一个 21 HOOL {505.714285 USD} 的单一 lot，并从中移除 8 HOOL，即 8 HOOL x 505.714285 USD/HOOL = 4045.71 USD。我们收到 4240.00 USD，这允许我们自动计算资本利得：4240.00 - 4045.71 = 194.29 USD。减少后，剩余一个 13 HOOL {505.714285 USD} 的单一 lot。

如果 account 中有多种货币，这也应该有效，也就是说，向上述内容添加以下 transaction 不应导致失败：

    2014-04-15 * "Buying another stock"
      Assets:US:Invest:Stock      15.00 AAPL {300.00 USD}
      Assets:US:Invest:Cash    -4500.00 USD

然而，如果在同一个 account 中，同一货币以不同的 cost 货币计价，则应当失败：

    2014-03-15 * "Buying a first lot"
      Assets:US:Invest:Stock      10.00 HOOL {500.00 USD}
      Assert:US:Invest:Cash    -5000.00 USD

    2014-04-15 * "Buying a second lot"
      Assets:US:Invest:Stock      10.00 HOOL {623.00 CAD}
      Assets:US:Invest:Cash    -62300.00 CAD

    2014-05-20 * "Sell some stock at average cost"
      Assets:US:Invest:Stock      -8.00 HOOL {*}  ; Which HOOL, USD or CAD?
      Assets:US:Invest:Cash    4240.00 USD
      Income:US:Invest:Gains

但当然，这种情况在实践中*从未*发生过，所以我不太担心。我们潜在地可以支持指定 cost 货币来解决这种情况，也就是说，将卖出腿替换为以下内容：

    2014-05-20 * "Sell some stock at average cost"
      Assets:US:Invest:Stock      -8.00 HOOL {* USD}
      Assets:US:Invest:Cash    4240.00 USD
      Income:US:Invest:Gains

我相当确定这不会很有用，但我们可以更进一步，尽可能通用。

## 未来工作<a id="future-work"></a>

本提案尚未处理 cost basis 的重估！我们需要一种方式，能够向持仓的 cost basis 添加或移除一个固定的*美元金额*，也就是说，从 (1) 一个 lot 标识符和 (2) 一个 cost 货币金额，我们应该能够更新该 lot 的 cost。该 transaction 仍然必须保持平衡。

以下是一些关于这可能如何实现的思路：

    2014-05-20 * "Adjust cost basis of a specific lot"
      Assets:US:Invest:Stock       10.00 HOOL {500.00 USD + 230.00 USD}
      Income:US:Invest:Gains     -230.00 USD

结果库存将是 10 股 HOOL，每股 523.00 USD，以及原始 lots 的其余部分，减去 10 股每股 500.00 USD 的 HOOL（可能还会剩下一些，这没关系）。这相当于

    2014-05-20 * "Adjust cost basis of a specific lot"
      Assets:US:Invest:Stock      -10.00 HOOL {500.00 USD}
      Assets:US:Invest:Stock       10.00 HOOL {523.00 USD}
      Income:US:Invest:Gains     -230.00 USD

只是你不需要执行计算。因此，这应该实现为一种转换。然而，这并不特别有用，因为这在当前已经得到支持……调整通常是在平均成本 lots 上进行的，而问题正在于此：你必须自己进行计算！这里有一个相关的用例：

    2014-05-20 * "Adjust cost basis of a specific lot"
      Assets:US:Invest:Stock       10.00 HOOL {* + 230.00 USD}
      Income:US:Invest:Gains     -230.00 USD

这将首先将所有 HOOL 的 lots 进行平均，并使用新金额重新计算 cost basis。这应该可以工作：

    2014-03-15 * "Buying a first lot"
      Assets:US:Invest:Stock       5.00 HOOL {500.00 USD}
      Assert:US:Invest:Cash    -2500.00 USD

    2014-04-15 * "Buying a second lot"
      Assets:US:Invest:Stock        5.00 HOOL {520.00 USD}
      Assets:US:Invest:Cash     -2600.00 USD

    2014-05-20 * "Adjust cost basis of the Hooli units"
      Assets:US:Invest:Stock       10.00 HOOL {* + 230.00 USD}
      Income:US:Invest:Gains     -230.00 USD

注意，我们仍然必须指定要重新定价的 HOOL 股份数量。我喜欢这种方式，但我在想是否应该允许像这样指定“所有单位”（这将对语法进行更激进的更改）：

    2014-05-20 * "Adjust cost basis of the Hooli units"
      Assets:US:Invest:Stock           * HOOL {* + 230.00 USD}
      Income:US:Invest:Gains     -230.00 USD

自动计算 cost basis 调整的最佳方式可能是通过强大的 interpolation，如下所示：

    2014-05-20 * "Adjust cost basis of a specific lot"
      Assets:US:Invest:Stock      -10.00 HOOL {500 USD}  ; reduce
      Assets:US:Invest:Stock       10.00 HOOL {}         ; augment, interpolated
      Income:US:Invest:Gains     -230.00 USD

有关该提案的更多细节，请参阅 Smarter Elision 文档。

### 跨账户 Booking<a id="inter-account-booking"></a>

某些税法要求用户根据特定方法进行 booking，这可能适用于所有账户。这意味着需要应用某种 transfer 才能正确处理此问题。有关详细信息，请参阅[单独文档](http://furius.ca/beancount/doc/inter-account)。

***TODO - 使用更多平均成本 booking 测试来完善此部分！***

## 实现说明<a id="implementation-notes"></a>

### 分离解析与插值<a id="separate-parsing-interpolation"></a>

为了实现一种不指定 cost 的 reduction 语法，我们需要对解析器进行修改。由于 posting 上可能没有 cost，因此在解析时执行 balance assertion 变得不可能。因此，我们需要将 balance assertion 推迟到解析*之后*的阶段。这是合理的，从某种意义上说也是有益的：最好是在该阶段 Beancount 解析器不输出许多复杂的错误。将在运行插件之前立即添加一个新的“解析后”阶段。

## 结论<a id="conclusion"></a>

本文档仍在编写中。我非常希望能收到一些反馈，以便改进所建议的方法，这也是我将其以文字形式记录下来，而不是直接编写代码的原因。我认为，通过迭代这一设计，可以达到更好的语义，从而在所有系统中产生更优的效果，并且这可以作为后续文档，帮助开发者理解为何采用这种设计方式。

非常感谢您的反馈。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
