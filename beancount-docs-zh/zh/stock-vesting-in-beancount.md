> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/stock_vesting_in_beancount/

# Beancount 中的股票归属（Stock Vesting）

> **样章** · 面向已使用 Beancount 一段时间、希望进阶的读者。
>
> 原文：Martin Blais（[blais@furius.ca](mailto:blais@furius.ca)），2015 年 6 月  
> 来源：[Stock Vesting in Beancount](http://furius.ca/beancount/doc/vesting)  
> 翻译原则：中文为主；`transaction`、`posting`、`directive`、`account`、`balance assertion`、`tolerance`、`precision`、`interpolation`、`cost`、`price`、`lot`、`booking`、`pad` 等术语保留英文。此外 `commodity`、`cost basis`、`FMV` 等 Beancount/财务术语也保留英文，以免与代码和 account 名混淆。代码块、option 名、account 名、货币代码、链接与图片路径均保持原样。

> **版本提示**：本文写于 2015 年 6 月，以旧版 `furius.ca` 域名和 `bean-web` 界面为背景。现在 Beancount 的 Web 界面主要是 Fava，示例文件路径也可能有所变化；`bean-query` SQL 命令行仍可用。示例中的个别数字（第二笔转换的股数、转换与归属的日期先后、退款的小数位）存在原文笔误，已在正文以译者注标出。

## 译者导读

这篇短文用一组完整的示例账目，把 RSU（限制性股票单位）从「授予」到「归属」再到「卖出」的整个生命周期在 Beancount 里走了一遍。对高级用户来说，它的价值不在记账语法本身，而在下面几个建模决策：

1. **用独立的 commodity 把「未归属股份」和「真实股份」分开**（`HOOL.UNVEST` 与 `HOOL`）。未归属的 RSU 本质上是一种「定期到账的应收款」，而不是你名下的股票；分开记账才能正确反映你何时、以什么成本基础真正拿到股票。
2. **用中转 account（`Assets:US:Hooli:RSURefund`）解耦「收到现金」和「转换成股票」两步**。因为缴完税后剩余的现金通常不是整数股，先落到中转 account，再单独做转换 transaction，让每笔 transaction 精确对应一张工资单或一张股票释放报告。
3. **成本基础（cost basis）必须用券商给出的精确 FMV**，而不是近似价——这直接决定日后卖出时 `Income:...:Gains` 里的应税差额。
4. **一个授予一个子 account**，再用 `balance assertion` 核对中转 account 清零、未归属余额等，把复杂的归属过程变成可校验的账。

---

*本文通过一个完整的 RSU 示例，说明如何把「授予 → 归属 → 转换为股票 → 卖出」的整个生命周期记录进 Beancount，并正确计算成本基础与税款。*

## 引言

本文通过一个示例，说明如何在 Beancount 中处理限制性股票单位（RSU）的归属。这个示例可能与你自己的情况不完全一致，但细节足够充分，你应该能据此调整，以适配自己的差异。

可以在[这里](http://github.com/beancount/beancount/tree/master/examples/vesting/vesting.beancount)找到一个可运行的示例文件，配合本文一起阅读。

## 限制性股票薪酬

许多科技公司以「授予」（grant，或称「奖励」award）「限制性股票单位」（RSU）的形式向员工发放激励性薪酬。RSU 本质上是一份承诺：未来会把实际股票「释放」给你。之所以说这些股票是「受限」的，是因为你无法动用它们——只有当它们「归属」（vest）时你才真正拿到，而归属是按一个时间表逐步发生的。通常，公司会承诺给你一个固定数量的股份，在 3 到 4 年内按季度或按月分批归属。如果你离开公司，剩余未归属的股份就作废了。

![美剧《硅谷》剧照：两名角色在 Hooli 办公室走廊交谈，原文借 Hooli 说明 RSU 情境](stock-vesting-in-beancount/media/6a910c80cfb0385f9cff8de1b5976716a1eb7324.jpg)

你可以把这些 RSU 看作一种资产——一笔随时间定期到账的应收款。这些 RSU 本质上是「以公司自身股份计价」的薪酬。我们希望跟踪这些未归属单位的逐步兑现过程，并正确记录它们转换为真实股票的过程：带成本基础（cost basis），并计入归属时缴纳的各种税款。

## 跟踪授予

### commodity

首先，我们要定义一些 commodity。在这个例子里，我为「Hooli Inc.」工作，最终会收到该公司的股份（以美元计价）：

    1990-12-02 commodity HOOL
      name: "Common shares of Hooli Inc."
      quote: USD

我们还想跟踪未归属股份的数量：

    2013-01-28 commodity HOOL.UNVEST
      name: "Unvested shares of Hooli from awards."

### 授予的 Accounts

收到的授予属于收入（income）。我用 `Income:US:Hooli` 作为所有来自 Hooli 的收入 accounts 的根，但具体地，我为这些授予单独定义一个 account，其中存放未归属股份的单位：

    2013-01-28 open Income:US:Hooli:Awards        HOOL.UNVEST

当股票归属时，我们需要在某处 book 这笔收入的另一侧，因此定义一个 expenses account，用来统计一段时间内已有多少股票归属：

    2014-01-28 open Expenses:Hooli:Vested         HOOL.UNVEST

### 收到授予

当你收到一笔新授予时（例如可能每年都有一次，有人称之为「stock refresh」，即股票增发），你把它作为收入入账，并存入一个全新的 account，用来跟踪这一笔特定的授予：

    2014-04-02 * "Award S0012345"
      Income:US:Hooli:Awards                -1680 HOOL.UNVEST
      Assets:US:Hooli:Unvested:S0012345      1680 HOOL.UNVEST

    2014-04-02 open Assets:US:Hooli:Unvested:S0012345

你可能同时有多笔在途的授予。为每一笔授予单独开一个 account 是很好的做法，因为它提供了一种自然的方式来列出它们的内容；当某笔授予到期时，你可以关闭该 account——所有仍处于 open 状态的授予 accounts 列表，就是你手上「未结清且仍在归属中」的授予清单。在这个例子里，我用授予编号（`#S0012345`）作为子 account 的名称。使用编号是有用的，因为报表里通常会包含这个编号。

我喜欢把所有授予集中放在一小块专门的区域里。

## 归属事件

### account

首先，当股票归属时，这是一笔应税收入事件。股票的现金价值需要一个 Income account：

    2013-04-04 open Income:US:Hooli:RSU

缴纳的税款应记在「按年度」的 expenses accounts 上——这些 account 你应该已经在别处定义好，用来记录当年的税务（cookbook 的其他部分有讲到）：

    2015-01-01 open Expenses:Taxes:TY2015:US:StateNY
    2015-01-01 open Expenses:Taxes:TY2015:US:Federal
    2015-01-01 open Expenses:Taxes:TY2015:US:SocSec
    2015-01-01 open Expenses:Taxes:TY2015:US:SDI
    2015-01-01 open Expenses:Taxes:TY2015:US:Medicare
    2015-01-01 open Expenses:Taxes:TY2015:US:CityNYC

在缴纳了这笔收入的税款之后，剩余的现金会先存入一个中转 account，之后再转换成股票：

    2013-01-28 open Assets:US:Hooli:RSURefund

此外，在另一处，我们还需要一个券商（brokerage）account，由它代你持有和管理这些股份：

    2013-04-04 open Assets:US:Schwab:HOOL

通常这个券商没得选，因为你所在的公司一般会与一家外部机构签约来管理限制性股票计划。做这类管理的典型机构有 Morgan Stanley、Salomon Smith Barney、Schwab，甚至 E\*Trade。在这个例子里，我们用一个 Schwab account。

我们还需要某种 checking account，用来接收「零股折算的现金」（fractional shares 的现金补偿）。例子里我假设用一个 Bank of America account：

    2001-01-01 open Assets:US:BofA:Checking

### 归属

首先是归属事件本身：

    2015-05-27 * "Vesting Event - S0012345 - HOOL" #award-S0012345 ^392f97dd62d0
      doc: "2015-02-13.hooli.38745783.pdf"
      Income:US:Hooli:RSU                    -4597.95 USD
      Expenses:Taxes:TY2015:US:Medicare         66.68 USD
      Expenses:Taxes:TY2015:US:Federal        1149.48 USD
      Expenses:Taxes:TY2015:US:CityNYC         195.42 USD
      Expenses:Taxes:TY2015:US:SDI               0.00 USD
      Expenses:Taxes:TY2015:US:StateNY         442.32 USD
      Expenses:Taxes:TY2015:US:SocSec          285.08 USD
      Assets:US:Hooli:RSURefund               2458.97 USD

这笔 transaction 与我每次归属事件、每一笔授予所收到的工资单（payroll stub）逐行对应。由于 Hooli 的所有 RSU 授予都在每月的同一天归属，这意味着我会有成簇的这样一组 transaction，每笔授予一组（示例文件里我展示了两笔授予）。

有几点值得说明：

-   Income posting 的金额等于「归属股数 × 股票 FMV」。在这个例子里，就是 35 股 × $131.37/股 = $4597.95。我直接写美元金额，因为这个数字就在工资单上给我了。

-   收到归属的股票是一笔应税收入事件，Hooli 会自动代扣税款并替员工上缴政府。这些就是与你 W-2 对应的 `Expenses:Taxes` accounts。

-   最后，我不会把转换后的股份直接存入券商 account；这是因为缴完税款后剩余的现金不一定刚好是整数股。因此我用了一个中转 account（`Assets:US:Hooli:RSURefund`），把「收到」和「转换」解耦。

这样一来，每笔 transaction 都精确对应一张工资单，录入数据会更容易。

还要注意，我用了一个唯一的 link（`^392f97dd62d0`）来把某一次归属事件的所有 transactions 归为一组。如果你愿意，也可以用标签（tags）来做同样的事。

### 转换为实际股票

现在，我们可以把剩余现金转换成股票单位了。这一步发生在券商那里，你应该会在券商 account 里看到新股份。券商通常会为每一次归属事件、每一笔授予出具一份「股票释放报告」（stock release report），其中包含完成转换所需的细节，即：从现金实际转换出的股数，以及成本基础（cost basis，即归属当日的 FMV）：

    2015-05-25 * "Conversion into shares" ^392f97dd62d0
      Assets:US:Schwab:HOOL                   18 HOOL {131.3700 USD}
      Assets:US:Hooli:RSURefund
      Assets:US:Hooli:Unvested:S0012345      -35 HOOL.UNVEST
      Expenses:Hooli:Vested                   35 HOOL.UNVEST

前两个 postings 存入股份，并从中转 account（归属 transaction 在那里留下剩余现金）中减去相应的美元金额。请务必使用报表给出的精确 FMV price，而不是一个近似价，因为这会在日后产生税务影响。注意，你不能买入零股（fractional shares），所以按整数股数（18 股）折算的成本会在中转 account 里留下一部分剩余现金。

> **译者注 · interpolation**  
> 第二个 posting `Assets:US:Hooli:RSURefund` 没有写金额，Beancount 会自动补全（interpolation）：它等于 `18 HOOL × 131.3700 USD = 2364.66 USD` 的负值，即 `-2364.66 USD`，这样中转 account 的余额就自然减少了。本章多处用这种「留空让 Beancount 补」的写法，注意它不同于「该 posting 金额恰好为零」。

后两个 postings 从未归属股份的 balance 中扣减，同时我「收到」一笔 expenses；这个 expenses account 本质上是统计某一段时间内已有多少股归属。

这里同样是每笔 stock grant 各有一笔这样的转换 transaction。我把它们分开录入，让一张报表对应一笔 transaction。这是一个值得遵循的好习惯。

### 零股退款

当所有转换事件都从中转 account 中转出现金之后，中转 account 里剩下的就是历次转换产生的零股余数。在我的情况里，这些余数由 Hooli 在归属后 3–4 周以一张单独的工资单统一退款，里面包含所有余数（甚至逐条列出每一项）。我也把这笔录成 transaction：

    2015-06-13 * "HOOLI INC       PAYROLL" ^392f97dd62d0
      doc: "2015-02-13.hooli.38745783.pdf"
      Assets:US:Hooli:RSURefund            -94.31 USD
      Assets:US:Hooli:RSURefund             -2.88 USD ; (For second award in example)
      Assets:US:BofA:Checking               97.19 USD

零股现金付清之后，中转 account 应该是空的。我用一条 balance assertion 来验证这一点：

    2015-06-14 balance Assets:US:Hooli:RSURefund  0 USD

这让我能大致确认数字是对的。

### 组织你的输入

我喜欢把所有归属事件放在输入文件的同一处；这让它们更容易更新和对账，尤其在有多笔授予时。例如，有两笔授予时，我会有像下面这样的多组 transactions，彼此之间用 4–5 个空行分隔开：

    2015-05-27 * "Vesting Event - S0012345 - HOOL" #award-S0012345 ^392f97dd62d0
      doc: "2015-02-13.hooli.38745783.pdf"
      Income:US:Hooli:RSU                    -4597.95 USD
      Assets:US:Hooli:RSURefund               2458.97 USD
      Expenses:Taxes:TY2015:US:Medicare         66.68 USD
      Expenses:Taxes:TY2015:US:Federal        1149.48 USD
      Expenses:Taxes:TY2015:US:CityNYC         195.42 USD
      Expenses:Taxes:TY2015:US:SDI               0.00 USD
      Expenses:Taxes:TY2015:US:StateNY         442.32 USD
      Expenses:Taxes:TY2015:US:SocSec          285.08 USD

    2015-05-27 * "Vesting Event - C123456 - HOOL" #award-C123456 ^392f97dd62d0
      doc: "2015-02-13.hooli.38745783.pdf"
      Income:US:Hooli:RSU                    -1970.55 USD
      Assets:US:Hooli:RSURefund               1053.84 USD
      Expenses:Taxes:TY2015:US:Medicare         28.58 USD
      Expenses:Taxes:TY2015:US:Federal         492.63 USD
      Expenses:Taxes:TY2015:US:CityNYC          83.75 USD
      Expenses:Taxes:TY2015:US:SDI               0.00 USD
      Expenses:Taxes:TY2015:US:StateNY         189.57 USD
      Expenses:Taxes:TY2015:US:SocSec          122.18 USD

    2015-05-25 * "Conversion into shares" ^392f97dd62d0
      Assets:US:Schwab:HOOL                        18 HOOL {131.3700 USD}
      Assets:US:Hooli:RSURefund
      Assets:US:Hooli:Unvested:S0012345           -35 HOOL.UNVEST
      Expenses:Hooli:Vested                        35 HOOL.UNVEST

    2015-05-25 * "Conversion into shares" ^392f97dd62d0
      Assets:US:Schwab:HOOL                         9 HOOL {131.3700 USD}
      Assets:US:Hooli:RSURefund
      Assets:US:Hooli:Unvested:C123456            -15 HOOL.UNVEST
      Expenses:Hooli:Vested                        15 HOOL.UNVEST

    2015-06-13 * "HOOLI INC       PAYROLL" ^392f97dd62d0
      doc: "2015-02-13.hooli.38745783.pdf"
      Assets:US:Hooli:RSURefund                -94.30 USD
      Assets:US:Hooli:RSURefund                 -2.88 USD
      Assets:US:BofA:Checking                   97.18 USD

    2015-02-14 balance Assets:US:Hooli:RSURefund    0 USD

> **译者注 · 原文笔误**  
> 上面第二笔转换写成 `9 HOOL`，但按第二笔授予的账目核对：15 股归属、缴税后净额 1053.84 USD，除以 131.37 只能转出 8 股（`8 × 131.37 = 1050.96`，余 2.88，正好对应下文的 `-2.88 USD` 退款）。因此这里应为 `8 HOOL`。此外，两笔转换的日期 `2015-05-25` 早于归属事件 `2015-05-27`，原文如此；实际中转换应发生在归属当日或之后，照抄示例时请自行调整日期顺序。

## 未归属股份

### 断言未归属余额

最后，你可能偶尔想断言未归属股份的数量。例如我喜欢每半年做一次。为 Hooli 管理这些 RSU 的券商机构应该能列出每笔授予还剩多少未归属股份，所以这件事简单到就是在网站上查一下：

    2015-06-04 balance Assets:US:Hooli:Unvested:S0012345  1645 HOOL.UNVEST
    2015-06-04 balance Assets:US:Hooli:Unvested:C123456    705 HOOL.UNVEST

### 为未归属股份定价

你也可以给未归属股份定一个 price，用来估算未归属的美元金额。这里你应该使用一种虚构货币，因为我们希望避免生成的 balance sheet（资产负债表）把这些未归属资产当作普通美元计入：

    2015-06-02 price HOOL.UNVEST               132.4300 USD.UNVEST

在撰写本文时，`bean-web` 界面不会把未按 cost 持有的单位换算成该虚构货币，但通过 SQL 查询接口或写个自定义脚本，你应该能产出这些数字：

    $ bean-query examples/vesting/vesting.beancount 

    beancount> select account, sum(convert(position, 'USD.UNVEST')) as unvested 
               where account ~ 'Unvested' group by account;

                 account                     unvested       
    --------------------------------- ----------------------
    Assets:US:Hooli:Unvested:S0012345 217847.3500 USD.UNVEST
    Assets:US:Hooli:Unvested:C123456   93363.1500 USD.UNVEST

> **译者注 · 版本差异**  
> 文中提到的 `bean-web` 是旧版 Web 界面，如今已基本被 Fava 取代；`bean-query` 命令行 SQL 查询仍可用。若你使用 Fava，也可以直接在 Fava 里用 SQL 查询完成同样的换算。

## 卖出已归属的股票

每次归属事件之后，股票就留在你的券商 account 里。卖出这些股票与任何其他交易 transaction 的流程完全相同（完整细节见[用 Beancount 交易](trading-with-beancount.md)）。例如，卖出示例中的股份大致会像这样：

    2015-09-10 * "Selling shares"
      Assets:US:Schwab:HOOL        -26 HOOL {131.3700 USD} @ 138.23 USD
      Assets:US:Schwab:Cash    3593.98 USD
      Income:US:Schwab:Gains

这里你可以看到，转换事件所用的成本基础（cost basis）为什么必须是正确的那一个：你将就差额缴税（记在 `Income:US:Schwab:Gains`）。在这个例子里，应税差额是每股（138.23 - 131.37）美元。

我喜欢把所有券商 transactions 放在文档里单独的一节，与券商相关的其他 transactions（如手续费、分红和转账）也放在那里。

## 结论

![美剧《硅谷》剧照：两名角色走向 Hooli 园区大门](stock-vesting-in-beancount/media/04de27aeb8e7b7cbc9201ce82ae780d21cec36fb.jpg)

这是一个简单的示例，仿照科技公司处理这类薪酬的方式建模。它绝不全面，某些细节必然因你的具体情况而异。尤其是它没有解释如何处理期权（ISO）。我希望本文有足够的「干货」，让你能够举一反三、适配自己的具体情况。如果你卡住了，欢迎到[邮件列表](http://furius.ca/beancount/doc/mailing-list)上提问。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
