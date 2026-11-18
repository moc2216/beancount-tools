> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/settlement_dates_in_beancount/

# Beancount 中的结算日期与转账账户<a id="title"></a>

Martin Blais，2014 年 7 月

[http://furius.ca/beancount/doc/proposal-dates](http://furius.ca/beancount/doc/proposal-dates)

> [动机](#motivation)
>
> [提案描述](#_1t2cyy3ee86k)
>
> [遗留问题](#remaining-questions)
>
> [先前工作](#_svp0j511dy5a)
>
> [账本有效日期与辅助日期](#ledger-effective-and-auxiliary-dates)
>
> [参考文献](#references)

## 动机<a id="motivation"></a>

当在 investment account 中执行交易时，transaction 的执行日期（“transaction date”）与资金存入关联现金账户的日期（“settlement date”）之间通常存在延迟。这导致导入的 balance assertion 有时需要对其日期进行人为调整，有时甚至根本无法处理。本文档建议为 transaction 或 posting 添加一个可选的“settlement date”，并定义相应的语义以解决该问题。

## 提案描述<a id="proposal-description"></a>

### 结算日期<a id="settlement-dates"></a>

在 Beancount 的第一版实现中，我曾在 transaction 上附加两个日期，但从未对其进行处理。备用日期会被附加，但随后被忽略。其含义是应该将 transaction 拆分为两个，并配合某种 transfer account，这可能是一种有用的语义，但我从未将其开发出来。

输入可能类似于这样：

    2014-06-23=2014-06-28 * "Sale"
       Assets:ScottTrade:GOOG    -10 GOOG {589.00 USD}
       S Assets:ScottTrade:Cash

其中，“S” posting 标志标记了“应推迟到结算日期”的那一侧。

或者，你可以将日期附加到 posting 上：

    2014-06-23 * "Sale"
       Assets:ScottTrade:GOOG    -10 GOOG {589.00 USD}
       2014-06-28 Assets:ScottTrade:Cash

上述两种语法提案都允许你指定哪些 posting 应推迟到结算。第二种更灵活，因为每个 posting 可能具有不同的日期，但第一种更受限的语法会带来更少的复杂性。

这两种方式都可以被转换为多个 transaction，并使用 transfer account 来吸收待定金额：

    2014-06-23 * "Sale" ^settlement-3463873948
       Assets:ScottTrade:GOOG    -10 GOOG {589.00 USD}
       Assets:ScottTrade:Transfer

    2014-06-28 * "Sale" ^settlement-3463873948
       Assets:ScottTrade:Transfer
       Assets:ScottTrade:Cash        5890.00 USD

到目前为止，我通过在不必要的地方对 balance assertion 的日期进行模糊处理来应对。我的销售交易相对较少，所以这目前还不是一个大问题。我不确定它现在是否需要一个解决方案，也许最好的做法只是记录当此问题出现时如何处理。

也许有人能说服我改变看法。

### 转账账户<a id="transfer-accounts"></a>

在上一节中，我们讨论了一种风格，其中单个 entry 在两个 account 之间移动资金，包含两个日期并导致两个独立的 entry。一个相关的辅助问题，其解决方案与此相关，是如何执行反向操作，即如何*合并*两个 posting 到共同 transfer account（有时称为“[suspense account](https://en.wikipedia.org/wiki/Suspense_account)”）的独立 entry。

例如，用户可能希望分别输入 transaction 的两边，例如通过对单独的输入文件运行导入脚本，而不是必须手动对账和合并这些内容，我们希望明确支持这一点，通过识别这些 transfer account 的匹配 transaction 并在它们之间创建共同链接。

最重要的是，我们希望能够轻松识别哪些 transaction 在另一边没有匹配，这表明数据缺失。

-   此功能的原型位于 [beancount.plugins.tag\_pending](https://github.com/beancount/beancount/tree/v2/beancount/plugins/tag_pending.py)。

-   另请参阅 redstreet0 的“[zerosum](https://groups.google.com/d/msgid/beancount/8adbb83d-a7c7-476a-97ca-d600d110db20%40googlegroups.com?utm_medium=email&utm_source=footer)”插件，来自[此线程](https://groups.google.com/d/msgid/beancount/8adbb83d-a7c7-476a-97ca-d600d110db20%40googlegroups.com?utm_medium=email&utm_source=footer)。

## 遗留问题<a id="remaining-questions"></a>

*我们如何确定合适的 transfer account 名称？使用子账户是否是一种合理的方法？如果用户希望拥有一个全局的 limbo account 怎么办？*

    TODO

*这个属性是否解决了在 trade 和 settlement 之间进行 balance assertion 的问题？*

> TODO \[编写一个详细的示例\]
>
> *评论线程：*
>
> *Martin Blais \[12:00 PM\]*
>
> *Filippo，之前的提议能否解决该问题？如果在某些金额正在结算途中时绘制资产负债表，这些金额将显示在 limbo account 中。*
>
> *Filippo Tampieri \[12:15 PM\]*
>
> *是的，我喜欢保留 trade date 作为主要日期的想法，这样所有 report 只需关注该日期，而检查可以使用 settlement date。*
>
> *观察：Scotia iTRADE 在登录时的摘要余额页面上，将“trade date cash”和“settlement date cash”分为单独的行显示，但在月度对账单上，所有 transaction 仅显示 settlement date（没有进一步解释）。*
>
> *Martin Blais \[12:45 PM\]*
>
> *顺便提一下，如果 transfer account 是 investment 基础账户的子账户（例如 Assets:US:ScottTrade），并且你有两个现金子账户——例如 :Cash 和 :Transfer——你可以对父账户执行 balance assertion。*
>
> *这允许你针对该商品的子账户总和进行检查，从而有效验证可用现金和用于结算的 limbo 金额：*
>
> *2014-06-30 balance Assets:US:ScottTrade xxx USD*
>
> *在这种情况下，xxx 代表你当前的现金 + 待结算金额。此功能目前受支持；你可以对父账户执行 balance assertion。*

*有什么缺点吗？*

    TODO

*这对资产负债表和损益表有何影响（如果有的话）？用户是否能明显看出这些 limbo/transfer account 中的金额是什么？*

    TODO

## 解除 Transaction 的根节点约束<a id="unrooting-transactions"></a>

一个更大胆的想法是在 transaction-posting 层级中增加一个额外的层级，从而具备将多个部分 transaction 进行分组的能力，并将平衡规则移至该层级。基本上，两个分别输入的 transaction 随后通过某种规则（或简单地通过自身）进行分组，可以形成一个新的平衡规则单元。

这将对 schema 和 Beancount 的设计提出更为苛刻的要求，但能够原生支持部分 transaction，同时保留它们各自的日期、描述等信息。也许这是一个更好的模型？请考虑其优势。

## 先前工作<a id="previous-work"></a>

### Ledger 中的生效日期与辅助日期<a id="ledger-effective-and-auxiliary-dates"></a>

Ledger 拥有“[辅助日期](http://ledger-cli.org/3.0/doc/ledger3.html#Auxiliary-dates)”的概念。其工作原理很直接：任何 transaction 都可以有一个第二日期，用户可以在运行时（通过 `--aux-date`）选择是使用主日期还是辅助日期。

我不清楚在存在 balance assertion 的情况下，这在实践中应如何使用。如果没有 balance assertion，我能看出它是如何正常工作的：你只需使用结算日期来渲染所有内容。这可能仅对特定的 report 有意义。

我更希望保持被解析的 transaction 集合具有单一的语义；transaction 的含义随调用条件而变化的想法会在 Beancount 中树立一个先例，我宁愿不破坏这一良好特性，因此默认情况下我倾向于避免实现此解决方案。

辅助日期也被称为“[生效日期](http://ledger-cli.org/3.0/doc/ledger3.html#Effective-Dates)”，并且可以与每个单独的 posting 相关联。辅助日期从属于“主日期”或“实际日期”（即记录的 posting 日期）：

    2008/10/16 * (2090) Bountiful Blessings Farm
        Expenses:Food:Groceries                  $ 37.50  ; [=2008/10/01]
        Expenses:Food:Groceries                  $ 37.50  ; [=2008/11/01]
        Expenses:Food:Groceries                  $ 37.50  ; [=2008/12/01]
        Expenses:Food:Groceries                  $ 37.50  ; [=2009/01/01]
        Expenses:Food:Groceries                  $ 37.50  ; [=2009/02/01]
        Expenses:Food:Groceries                  $ 37.50  ; [=2009/03/01]
        Assets:Checking

这一功能的原始动机是用于预算，允许将费用的核算转移到相邻的预算期间，以便将实际支付金额结转至那些期间。某个月的银行金额可以根据需要与紧邻的前一个月或后一个月的预算进行核对。（注：John Wiegley）

这与我上面建议的语法之一类似——允许用户为每个 posting 指定一个日期——但其他 posting 并未拆分为独立的 transaction。这些日期的使用同样由命令行选项（`--effective`）触发。我假设上述 checking account 上的 posting 在 2008/10/16 一次性发生，无论报告日期如何。让我们来验证一下：

    $ ledger -f settlement1.lgr reg checking --effective
    08-Oct-16 Bountiful Blessings.. Assets:Checking           $ -225.00    $ -225.00

正如我所想。这行得通，但这种方法的一个问题是，在 2008/10/01（最早的生效日期）和 2009/03/01（最晚的生效日期）之间绘制的任何资产负债表都不会平衡。在这些日期之间，某些金额处于“悬而未决”状态，在这些日期之一绘制资产负债表将无法平衡。

这将破坏 Beancount 中的一个不变量：我们要求你始终能够在任何时间点绘制资产负债表，并且任何 transaction 子集都应保持平衡。我宁愿通过将示例 transaction 拆分为许多其他 transaction 来实现这一点，如上所述，将那些处于“悬而未决”状态的临时金额移入一个显式的“limbo”或“transfer” account，使每个 transaction 都保持平衡。此外，这一步骤可以作为转换阶段实现，用每个 posting 对应一个 transaction 来替换具有生效日期的 transaction，其中生效日期与 transaction 日期不同（这可以通过插件按需启用）。

### GnuCash（对账软件） <a id="gnucash"></a>

*TODO(blais) - 这在 GnuCash 和其他 GUI 系统中是如何处理的？是否有标准的 account 方法？*

> *Alen Šiljak (2019年5月8日)*
>
> *GnuCash 有 Post Date 和 Enter Date 字段，但我不确定它们在何时或如何产生实际差异。*

## 参考文献<a id="references"></a>

美国国税局（IRS）[要求你在税务申报中使用交易日期，而不是结算日期](http://www.irs.gov/publications/p17/ch14.html)；摘自 IRS 出版物 17：

> **在成熟市场交易的证券。** 对于在成熟证券市场交易的证券，你的持有期从你购买证券的交易日次日开始，到你出售证券的交易日结束。
>
> ![CAUTION 警告图标，原文用它标示注意事项](settlement-dates-in-beancount/media/1336b54a60f8aa4b92957260378207d6479e7c39.gif)不要将交易日期与结算日期混淆，后者是股票必须交付且款项必须支付的截止日期。
>
> **示例。**
>
> 你是一名采用现金收付制、日历年度纳税期的纳税人。你在 2013 年 12 月 30 日以盈利出售了股票。根据证券交易所的规则，该笔交易在出售后的 4 个交易日，即 2014 年 1 月 6 日，通过交付股票完成交割。你在同一天收到了销售款项。尽管你在 2014 年收到了款项，但你仍需在 2013 年的报税表中申报这笔收益。该收益是长期还是短期，取决于你持有该股票是否超过 1 年。你的持有期于 12 月 30 日结束。如果你是以亏损出售该股票，你也需在 2013 年的报税表中申报。

匿名评论：

德国税务机关可能会让你选择使用哪个日期。这就是为什么我关注你是如何处理这一点的。Gnucash 显然可以“几乎”使用结算日期，但根据文档来看，它似乎做得不好，或者根本就没做好。

### 讨论串<a id="threads"></a>

-   [一个有趣的“巧合特性”](https://groups.google.com/d/msg/ledger-cli/ooxbPVRinSs/ymkRCerhxjcJ)

-   [来自 Ledger 的初步意见](https://groups.google.com/d/msg/beancount/z9sPboW4U3c/UfJbIVzwmpMJ)

预算编制：

> *Martin Blais - /2014 年 7 月 1 日*
>
> *有没有使用 Ledger 中此功能的人能提供一个示例，说明你是如何使用它的？*
>
> *John Wiegley - 2014 年 7 月 1 日*
>
> *实际上，我不确定我是否曾尝试过将这些功能组合使用。*
>
> *Martin Blais - 2014 年 7 月 1 日*
>
> *谢谢 John。我打算尝试整理一个更具体的示例来解决结算日期问题，并更好地理解它。*
>
> *John Wiegley - 2014 年 7 月 1 日*
>
> *我最初希望辅助日期能帮助预算编制（这样，某个月的银行金额就可以与紧邻的前一个月或后一个月的预算进行对比，视需要而定），但必须说，由于我现在很少做预算，所以我根本不使用它们。不过，对于那一种情况，它们确实很有用。*
>
> *Martin Blais - 2014 年 7 月 1 日*
>
> *很有趣，感谢提供背景信息，我会更新文档。*
>
> *预算编制对我来说仍然有点难以捉摸；和你一样，我自己也不太做预算，但当我思考它时，似乎有两种情况：(1) “目标”情况，其中未使用的金额不在月份之间结转（如果是按月计算），以及 (2) 未使用的金额可以结转并用于抵消另一个月份的情况，如果我没理解错的话，这就是你提到的用例。*
>
> *(1) 很容易通过一个新的 directive 来实现（这是我目前的计划），它只需在总和超出约束条件时发出警告。*
>
> *(2) 让我感到困惑。我认为这需要一组平行的 account。我还没有想到一个优雅的解决方案。*
>
> *我会将此分叉到另一个提案文档中，这是另一个讨论。*

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
