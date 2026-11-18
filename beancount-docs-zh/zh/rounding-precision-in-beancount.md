> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/rounding_precision_in_beancount/

# 提案：Beancount 中的舍入与精度<a id="title"></a>

[Martin Blais](http://plus.google.com/+MartinBlais)，2014 年 10 月

*本文档描述了 Beancount transaction 中的舍入误差问题及其处理方式。它还包含*

*一项关于在 Beancount 中更好地处理 precision 问题的提案。*

## 动机<a id="motivation"></a>

### 平衡精度<a id="balancing-precision"></a>

Transaction 的平衡无法精确完成。这一点此前已在 [Ledger 邮件列表上讨论过](https://groups.google.com/d/msg/ledger-cli/m-TgILbfrwA/YjkmOM3LHXIJ)。在用于平衡 transaction 的金额上，必须允许一定的 tolerance。

当你考虑到在文本文件中输入数字意味着有限的小数表示时，这种需求就很明显了。例如，如果你要将单位数量与 cost 相乘，假设两者都以 2 位小数记录，结果可能会得到一个具有 4 位小数的数字，然后你需要将该结果与通常仅以 2 位小数输入的现金金额进行比较，就像这个例子一样：

    2014-05-06 * “Buy mutual fund”
      Assets:Investments:RGXGX       4.27 RGAGX {53.21 USD} 
      Assets:Investments:Cash     -227.21 USD

如果你计算一下，第一个 posting 的精确 balance 金额是 227.2067 USD，而不是 227.21 USD。然而，管理 investment 账户的经纪商公司会对现金提取应用四舍五入到最接近的 cent，并且四舍五入后的金额才是应该使用的正确金额。这个 transaction 必须平衡；我们需要以某种方式允许一些灵活性。

发生数学运算的大多数情况都涉及将单位数量和 price 或 cost 转换为相应的现金价值（例如，units x cost = total cost）。我们在表示 transaction 信息时的任务是复制主要发生在机构中的操作。这些操作总是涉及对单位和货币数字的四舍五入（银行确实会应用随机舍入），从这些机构的角度以及从政府的角度来看，要使用的*正确*数字确实是*四舍五入后*的数字本身。这不是数学纯度的问题，而是实用性的问题，我们的系统应该做银行所做的事情。因此，我认为我们应该始终将四舍五入后的数字 post 到 account 中。使用有理数在这方面并不是限制，但我们必须小心地在重要的地方存储四舍五入后的数字。

### 自动舍入<a id="automatic-rounding"></a>

另一个相关问题是自动舍入 interpolation 数字的金额。让我们再次采用最初的问题示例：

    2014-05-06 * “Buy mutual fund”
      Assets:Investments:RGXGX       4.27 RGAGX {53.21 USD} 
      Assets:Investments:Cash     ;; Interpolated posting = -227.2067 USD

这里，第二个 posting 的金额是从第一个 posting 的 balance 金额 interpolation 出来的。理想情况下，我们应该找到一种方法来指定它应如何舍入到 2 位小数的 precision。

请注意，这也影响 interpolation 的 price 和 cost：

    2014-05-06 * “Buy mutual fund”
      Assets:Investments:RGXGX       4.27 RGAGX {USD} 
      Assets:Investments:Cash     -227.21 USD

这里，cost 旨在从现金腿自动计算：227.21 / 4.27 = 53.2107728337… USD。要推断的正确 cost 也是四舍五入后的金额 53.21 USD。我们希望有一种机制来允许我们推断所需的 precision。

不幸的是，这种机制不能仅基于 commodity：不同的 account 可能以不同的 precision 跟踪货币。作为一个现实世界的例子，我有一个零售 FOREX 交易账户，其 price 和存款确实使用 4 位小数的 precision。

### Balance Assertion 的精度<a id="precision-of-balance-assertions"></a>

Balance assertion 的精度也受此问题影响，像这样的 assertion：

    2014-04-01 balance Assets:Investments:Cash   4526.77 USD

用户并不打算让这个 balance 检查精确地加总到 4526.77000000… USD。然而，如果这个现金 account 之前接收了一个具有更高 precision 的存款，如上一节示例所示，那么我们就有问题了。现在，现金金额包含了一些从 interpolation 中存入的碎屑（0.0067 USD）。如果我们能够为上一节中 posting 的自动舍入找到一个良好的解决方案，这就不会是一个问题。但在此期间，我们必须找到一个解决方案。

Beancount 目前的方法是一种权宜之计：它使用 [用户可配置的 tolerance](http://github.com/beancount/beancount/tree/master/beancount/ops/balance.py#L23) 为 0.0150（在任何单位中）。我们希望更改这一点，使得使用的 tolerance 能够依赖于 commodity、account，甚至正在使用的特定 directive。

## 其他系统<a id="other-systems"></a>

其他命令行会计系统在如何确定该 tolerance 方面存在差异：

-   Ledger 尝试通过利用最近解析的上下文（按文件顺序）来自动推导用于其 balance assertion 的 precision。所使用的 precision 是针对特定 commodity 最近一次解析的值的 precision。这可能存在问题：它可能导致 [交易之间不必要的副作用，且难以调试](https://groups.google.com/d/msg/ledger-cli/m-TgILbfrwA/cTHg2juqEJgJ)。

-   另一方面，HLedger 使用全局 precision 设置。[整个文件首先被处理，然后从整个输入文件中看到的最精确的数字中推导出 precision。](https://groups.google.com/d/msg/ledger-cli/m-TgILbfrwA/SoGZDNhlDOkJ)

-   目前，Beancount 在其 [balance checking 算法](http://github.com/beancount/beancount/tree/master/beancount/ops/validation.py) 中使用一个常量值作为 tolerance（任何单位的 0.005）。这很薄弱，至少应该依赖于 commodity，甚至也应该依赖于使用该 commodity 的特定 account。

## 提案<a id="proposal"></a>

### 自动推断 Tolerance<a id="automatically-inferring-tolerance"></a>

Beancount 应使用一种完全*局部*于每个 transaction 的方法来推导其 precision，或许可以有一个全局值作为默认值。也就是说，对于每个 transaction，它将检查具有简单金额（无 cost，无 price）的 postings，并推断用于 tolerance 的 precision 应为用户在此 transaction 中输入的最精确金额的一半。例如：

    2014-05-06 * “Buy mutual fund”
      Assets:Investments:RGXGX       4.278  RGAGX {53.21 USD} 
      Assets:Investments:Cash     -227.6324 USD
      Expenses:Commissions           9.95   USD

此处要使用的 precision 的小数位数是第 2 个和第 3 个 posting 的最大值，即 max(4, 2) = 4。第一个 posting 被忽略，因为其金额是数学运算的结果。tolerance 值应为最精确数字的*一半*，即 0.00005 USD。这应允许用户通过简单地在输入中插入更多位数来使用任意 precision。

仅使用小数位数来推导 precision……整数应意味着精确匹配。用户可以指定单个尾随小数点来暗示亚美元 precision。例如，以下 transaction 应无法平衡，因为计算出的金额为 999.999455 USD：

    2014-05-06 * “Buy mutual fund”
      Assets:Investments:RGXGX       23.45 RGAGX {42.6439 USD} 
      Assets:Investments:Cash        -1000 USD

相反，用户应显式允许使用某些 tolerance：

    2014-05-06 * “Buy mutual fund”
      Assets:Investments:RGXGX       23.45 RGAGX {42.6439 USD} 
      Assets:Investments:Cash       -1000. USD

或者更好，使用 1000.00 USD。这有一个缺点，即它阻止用户指定更简单的整数金额。我不确定这是否是个大问题。

最后，不会应用由 transaction 暗示的任何全局影响。任何 transaction 都不应影响其他 transaction 的平衡上下文。

### 对以 Cost 持有的金额的推断<a id="inference-on-amounts-held-at-cost"></a>

Matthew Harris 提出的一个想法（[此处](https://groups.google.com/d/msg/beancount/5u-xgR-ttjg/sXfU32ItRscJ)）是，我们也可以使用单位数量乘以 cost 的最小十进制值作为建立 transaction 平衡 tolerance 的数字。例如，在以下 transaction 中：

    2014-05-06 * “Buy mutual fund”
      Assets:Investments:RGXGX       23.45 RGAGX {42.6439 USD} 
      ...

可以推导出的 tolerance 值为

0.01 RGAGX x 42.6439 USD = **0.426439 USD**

Matthew 最初提出的用例是一个不包含简单金额的 transaction，只是一个两条腿都以 cost 持有的转换：

      2011-01-25 * "Transfer of Assets, 3467.90 USD"
        * Assets:RothIRA:Vanguard:VTIVX  250.752 VTIVX {18.35 USD} @ 13.83 USD  
        * Assets:RothIRA:DodgeCox:DODGX  -30.892 DODGX {148.93 USD} @ 112.26 USD

我实际上尝试过实现这一点，结果得到的 tolerance 要么宽得不可接受，要么小得不可接受。**它在实践中效果不佳，因此我放弃了这个想法。**

### 自动舍入<a id="automated-rounding"></a>

对于自动计算的值，例如在 auto-postings 中剩余值被自动推导的情况，我们应该考虑对这些值进行舍入。目前尚未就此开展工作；这些值当前未被舍入。

### 修复 Balance Assertions<a id="fixing-balance-assertions"></a>

为了修复 balance assertions，我们将通过查看 balance 金额本身使用的小数位数来推导所需的 precision，通过查看最精确的小数位并使用该数字值的一半来计算 tolerance：

    2014-04-01 balance Assets:Investments:Cash   4526.7702 USD

此 balance 检查暗示 precision 为 0.00005 USD。

如果你使用整数单位，则不允许任何 tolerance。精确的数字应匹配：

    2014-04-01 balance Assets:Investments:Cash   4526 USD

如果你想允许亚美元差异，使用单个逗号：

    2014-04-01 balance Assets:Investments:Cash   4526. USD

此 balance 检查暗示 precision 为 0.50 USD。

### 近似断言<a id="approximate-assertions"></a>

另一个想法，在 [Ledger 上的此工单](https://github.com/ledger/ledger/pull/329) 中提出，建议一种显式的近似断言。

我们可以这样实现（仅是一个想法）：

    2014-04-01 balance Assets:Investments:Cash   4526.00 +/- 0.05 USD

## 累积与报告残差<a id="accumulating-reporting-residuals"></a>

为了显式地呈现并监控 Ledger 中发生的舍入误差金额，我们应该[将其累积到一个 Equity 账户](https://groups.google.com/d/msg/ledger-cli/m-TgILbfrwA/YjkmOM3LHXIJ)，例如 “Equity:Rounding”。此功能应作为可选项开启。用户应能够指定用于累积误差的 account。每当一笔 transaction 无法精确平衡时，残差（即舍入误差）将作为该 transaction 的一个 posting 插入到该 equity 账户中。

默认情况下，此累积功能应处于关闭状态。目前尚不清楚额外的 postings 是否会带来干扰（如果不会，也许应该默认开启此功能；实践将为我们提供答案）。

## 实现<a id="implementation"></a>

本提案的实现[文档在此](precision-tolerances.md)。

## 用户评论<a id="user-comments"></a>

Johannes H - 2014年10月19日

> 我原本预期系统会有相反的行为。整数应当意味着最宽松的匹配。
>
> \* 因为如果用户懒得输入小数位（例如，输入 "1000" 而不是 "1000.00"），这可以被视为用户不太在意 precision 的一个指标。因此，我预期系统在对数字的解释上也应当更加宽松。
>
> \* 相反，如果用户愿意付出额外的努力，通过输入额外的数字或额外的小数点来指定数字的精确 precision（例如，输入 "1000.00" 或 "1000." 而不是简单的 "1000"），这可以被视为用户在意该数字 precision 的一个指标。因此，用户在指定 precision 时所付出的努力和严格程度，应当反映在系统更严格的解释上。
>
> 收起

Martin Blais - 2014年10月25日

> 我们同意你的第二点，但不同意第一点。第二点已由本提案解决。
>
> 如果整数被解释为最宽松的 precision，那么我们如何指定完整的 precision？"xx.000000000"？（这并不美观）还是其他语法，例如 "1000.-"？你希望如何指定？在某些情况下，我们确实需要一种方式来指定完整的 precision。（见下文）。
>
> 那么 "1000" 和 "1000." 之间的区别又是什么？我看到用户输入 "1000." 表示他/她不在乎小数位。"1000" 的含义尚待确定，我们可以让它表示其他含义。我认为它可以是表示完整 precision 的合理位置。
>
> 关键在于，在实践中，没有小数点的整数用于两种情况：
>
> \- 指定整数股数，这必须是精确的。
>
> \- 输入的简洁性。输入 100$ 比输入 100.00$ 更容易。这些整数金额通常用于现金，或用于近似并手动输入的金额，在这些情况下 precision 不是问题（应用完整 precision 不会引起问题）。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
