> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/precision_tolerances/

# Beancount 的 precision 与 tolerance

> **样章** · 面向已使用 Beancount 一段时间、希望从 intermediate 进阶到 advanced 的读者。
>
> 原文：Martin Blais，2015 年 5 月，2025 年 5 月更新  
> 来源：[Beancount Precision & Tolerances](https://beancount.github.io/docs/precision_tolerances/)  
> 翻译原则：中文为主；`transaction`、`posting`、`directive`、`account`、`balance assertion`、`tolerance`、`precision`、`interpolation`、`cost`、`price`、`lot`、`booking`、`pad` 等术语保留英文。代码块、option 名、account 名、货币代码均保持原样。

> **版本提示**：原文末尾有一条 2026 年 4 月的更新说明，指出 tolerance 与 precision 的配置仍在 review。阅读时请以你实际使用的 Beancount 版本的 option reference 为准。

## 进阶导读

如果你已经能用 Beancount 记账，这一页真正值得带走的是下面几点：

1. **tolerance 是逐笔 transaction 推导的**，不是全局设置。同一份文件里，不同 transaction 可以有不同的 tolerance；顺序不影响结果。这一点与 Ledger 的“跨 transaction 推导”正好相反。
2. **整数金额不贡献 precision**。`-384 USD` 不会推出 `0.5 USD` 的 tolerance，而是零。遇到“看起来应该平、却报不平衡”的情况，先检查是不是写了整数。
3. **cost 和 price 不参与 tolerance 推导**。它们通常比基础金额更精确；如果你需要把 cost 的 rounding 纳入，必须显式开启 `infer_tolerance_from_cost`。
4. **`inferred_tolerance_default` 只在推导失败时兜底**。它不是“把 tolerance 调大”的万能开关；如果 transaction 自己推出了 tolerance，这个 option 会被忽略。
5. **balance assertion 的 tolerance 是最后一位的 1 个单位**，不是 transaction 那种“半个单位”。`4.271 RGAGX` 接受 `4.270` 到 `4.272`。
6. **interpolation 的 rounding 取决于推导出的 tolerance**；推导不出来时，才看 default tolerance。是否启用 `account_rounding`，会影响 residual 如何落账。
7. **display precision 与 print 的 round-trip 是两件事**。前者用于报表好看，后者必须保证重新读入后数字不变。

---

*本文说明 Beancount 如何处理数字的有限 precision，包括 transaction balance check 与 balance assertion 中的近似比较，以及自动推导数字时可能发生的 rounding。*

## 引言

Beancount 把所有数字都以 decimal 形式存储。也就是说，你在输入文件里写下的数字，会在计算机内存中被**精确**表示。我们不使用 floating-point numbers。原因另文说明，本质上是为了在做精确求和时不引入任何 rounding error。

在这些 decimal numbers 中，小数位数会涉及四个方面。本节依次讨论：

- **Tolerances**：做 balance check 计算时，必须考虑数字存储的 precision，例如美元精确到 1 cent。由于机构以有限 precision 存储货币，balance 中自然会发生 rounding。我们既要容许这种 rounding，又要能检测出大于该范围的、由错误导致的不平衡。
- **Interpolation**：Beancount 语法允许用户省略某些数字，由系统自动补全。计算这些缺失数字时，我们希望使用该货币的惯用 precision，使显示出来的数值自然，符合机构自己可能计算出的结果。
- **Display**：显示数字时，每种货币都有惯用的位数。如果数字是除法结果，就需要 rounding，避免向用户展示大量无意义的小数位。
- **Computation**：进行计算时，decimal numbers 不会像硬件 floating-point 表示那样天然受限。对于会产生大量小数位的计算（例如除法），我们要指定计算结果的 precision。

本文依次讨论这些问题，说明 Beancount 如何尝试自动推导合理的默认值，以及如何通过配置控制它使用的 precision 与 tolerance。

### 定义

“**Precision**”：在 Beancount 的语境里，这个词被原作者历史上用得有点随意。在本文中，precision 指以下两者之一：(a) 表示一个 decimal number 的小数位数，例如 `12.356` 的 precision 是 3；(b) 该 precision 下最小单位的示例值，例如配置时用 `0.01` 表示 precision 3。

“**Tolerance**” 则是直接使用的数字，例如 `0.0005`。它不受下文提到的 `tolerance_multiplier` 影响；你可以说 `tolerance_multiplier` 调整的是 precision 数字，而不是 tolerance 本身。

## Tolerances：balance check 中的 imprecision

Beancount 会自动要求：输入文件中 transaction 的 postings 金额之和为零。为了以现实的方式验证这一点，它必须容忍少量 imprecision。因为 Beancount 允许你**复现真实账户交易**，而现实中机构会出于实际原因对金额进行 rounding。

看一个例子：下面是一笔两个不同货币账户之间的转账（美元与欧元）：

```beancount
2015-05-01 * "Transfer from secret Swiss bank account"
  Assets:CH:SBS:Checking   -9000.00 CHF
  Assets:US:BofA:Checking   9643.82 USD @ 0.93324 CHF
```

这个例子使用的汇率是 `0.93324 USD/CHF`，即 1 美元兑 0.93324 瑞士法郎。银行报价精确到 5 位。按全精度换算，`9000.00 CHF / 0.93324 CHF` 得到 **9643.82152501...** USD。反过来，用给定汇率把美元换算成法郎，结果也不精确：`9643.82 x 0.93324 = 8999.9985768…`。

另一个会发生这类 rounding 的例子：买入共同基金的小数份额：

```beancount
2013-04-03 * "Buy Mutual Fund - Price as of date based on closing price"
  Assets:US:Vanguard:RGAGX       10.22626 RGAGX {37.61 USD}
  Assets:US:Vanguard:Cash         -384.61 USD
```

这笔 transaction 同样发生了 rounding：不仅基金 NAV 被四舍五入到分（`$37.61`），份额数也按 Vanguard 的固定位数 rounding（`10.22626` 份 VPMBX）。整笔 transaction 的 balance 需要容忍一定 imprecision，无论你从份额算金额（`10.22626 x $37.61 = $384.6096386`），还是从目标美元金额算份额（`$384.61 / $37.61 = 10.2262696091`）。

从 Beancount 的角度看，上面两个例子都是 balancing transactions。显然，如果要把外部账户的交易表示并复现到输入文件，balance 验证算法就必须有一定 tolerance。

### 默认 tolerance 如何确定

Beancount 会尝试**自动**从输入中推导每笔 transaction 的 tolerance，而且是对每笔 transaction **单独**推导[^1]。再看上面的例子：

```beancount
2013-04-03 * "Buy Mutual Fund - Price as of date based on closing price"
  Assets:US:Vanguard:RGAGX       10.22626 RGAGX {37.61 USD}
  Assets:US:Vanguard:Cash         -384.61 USD
```

在这笔 transaction 中，Beancount 会推导出：

- RGAGX 的 tolerance 为 5 位小数，即 **0.000005 RGAGX**；
- USD 的 tolerance 为 2 位小数，即 **0.005 USD**。

注意，使用的 tolerance 是用户提供的最后一位 precision 的一个分数（通常是**一半**）。这完全从输入推导，不需要读取任何全局 tolerance 声明。同时注意，tolerance 是**按每种货币分别计算**的。

虽然推导了 RGAGX 的 tolerance，但它实际上没有参与这笔 transaction 的 balancing，因为第一个 posting 的 weight 是 USD（`10.22626 x 37.61 = 384.6096386 USD`）。

那么实际发生了什么？每个 posting 的 weight 被计算出来：

- 第一个 posting：`384.6096386 USD`
- 第二个 posting：`-384.61 USD`

它们按货币相加（这笔 transaction 的 weight 只有 USD），得到 **residual**：`-0.0003614 USD`。把这个值与 USD 的 tolerance 比较：`|-0.0003614| < 0.005`，因此 transaction balances。

> **译者注 · 进阶**  
> “逐笔 transaction 单独推导”意味着：同样一组数字，放在不同 transaction 里，可能得到不同的 tolerance；文件的先后顺序也不影响结果。这一点比 Ledger 的“按文件顺序、参考最近 parse 过的 transaction”更可预测。代价是：你无法通过全局设置一次性改变所有 transaction 的 tolerance，只能通过 `inferred_tolerance_default` 兜底，或调整数字本身的写法。

#### Prices 与 Costs

为了推导 tolerance，transaction 的 postings 上声明的 price 和 cost 金额**会被忽略**。这是合理的：它们通常比 posting 的基础金额 precision 更高，有时正是这种额外 precision 才让 transaction 平衡；它们不应被用来设定整笔 transaction 的 tolerance。

例如下面这笔 transaction：

```beancount
1999-09-30 * "Vest ESPP - Bought at discount: 18.5980 USD"
  Assets:US:Schwab:ESPP            54 HOOL {21.8800 USD}
  Income:CA:ESPP:PayContrib  -1467.84 CAD @ 0.6842 USD
  Income:CA:ESPP:Discount     -259.03 CAD @ 0.6842 USD
```

这里唯一推导出的 tolerance 是 CAD 的 `0.005`。`54 HOOL` 是整数，不产生 tolerance（下一节解释）。USD 没有推导出 tolerance：既不来自第一个 posting 的 cost（`21.8800 USD`），也不来自其余 postings 的 price（`0.6842 USD`）。

> **译者注 · 进阶**  
> 这解释了一个常见困惑：为什么 cost/price 写了 4 位小数，transaction 仍然按 2 位小数的 tolerance 判断？因为 cost/price 被排除在推导之外。若你确实希望把 cost 的 rounding 纳入 tolerance，需要开启 `infer_tolerance_from_cost`（见后文）。

#### 整数金额

对于输入中的整数金额，tolerance **不会**被推导为 `0.5`；也就是说，下面这笔 transaction 应该 balance 失败：

```beancount
2013-04-03 * "Buy Mutual Fund - Price as of date based on closing price"
  Assets:US:Vanguard:RGAGX    10.21005 RGAGX {37.61 USD}
  Assets:US:Vanguard:Cash         -384 USD
```

换句话说，整数金额不会为其货币的 tolerance 推导贡献任何小数位数。

默认情况下，没有小数位的金额所用 tolerance 为**零**。因此在这个例子里，由于无法推导 USD 的 precision（记住 cost 被忽略），transaction 会 balance 失败，因为 residual 非零（`|-0.0003614| > 0`）。

你可以分别为每种货币、以及为所有货币自定义默认 tolerance 值（见下文配置部分）。

（这种对整数金额的处理意味着：仅通过输入数字能指定的**最大 precision** 是 `0.05` 个单位。例如输入 `10.7`，precision 为 `0.1`，再乘以 tolerance multiplier `0.5`，得到 `0.05`。另一方面，default tolerance 设置允许指定任意数字。）

> **译者注 · 实操**  
> 这是最常见的“为什么不平”来源之一。银行流水里经常出现整数金额（如 `-384 USD`），而另一条 posting 带小数。最简单的修复不是调大 tolerance，而是把整数补成 `-384.00 USD`，让输入本身提供 2 位 precision。

#### 解决歧义

少数情况下，同一种货币会输入多个不同 precision。此时使用推导出的输入 tolerance 中**最大（最粗）**的那个。

例如，如果我们想把收入跟踪到比“分”更细的精度，可能会这样写：

```beancount
1999-08-20 * "Sell"
  Assets:US:BRS:ESPP           -81 HOOL {26.3125 USD}
  Assets:US:BRS:Cash       2141.36 USD
  Expenses:Financial:Fees     0.08 USD
  Income:CA:ESPP:PnL       -10.125 USD
```

这里 USD 金额有 `2141.36`、`0.08` 和 `-10.125`，分别推导出 `0.005` 或 `0.0005` 的 tolerance。我们选择最粗的：这笔 transaction 容忍 `0.005 USD` 的 imprecision。

#### 默认 tolerance 的配置

当 transaction 的数字不足以在**本地**推导 tolerance 时，我们回退到某个 default tolerance 值。如前面的例子，这可能是因为：(a) 所需货币相关的数字是整数，或 (b) 输入中根本没有足够的数字。

默认情况下，所有货币的 default tolerance 都是**零**。可以用 option 指定：

```beancount
option "inferred_tolerance_default" "*:0.001"
```

default tolerance 还可以按货币进一步细化：

```beancount
option "inferred_tolerance_default" "USD:0.003"
```

如果提供了货币特定的 tolerance，它会覆盖全局值。这个 option 的通用形式是：

```beancount
option "inferred_tolerance_default" "<currency>:<tolerance>"
```

需要明确：这个 option **只在 tolerance 无法推导时**使用。如果你的 rounding error 过大，而 transaction 中的数字确实推导出了某个 tolerance，那么这个 option 会被忽略（例如，把它设得更大来修复问题不会生效）。如果需要放宽 tolerance，见下一节的 `tolerance_multiplier`。

> **译者注 · 版本差异**  
> 原文在 interpolation 一节的示例里使用了 `option "default_tolerance" ...`。这个旧名字已废弃，当前应使用 `inferred_tolerance_default`；旧名仍可能被接受，但会产生 warning。后文保留原文示例，阅读时请按当前版本替换。

#### tolerance 乘数

前面展示过：当 tolerance 未显式提供时，会从 postings 的数字推导。默认情况下，找到的最小位数除以 2 得到 tolerance，因为我们假设所复现的机构会做 rounding，误差不应超过一半。

但现实中，rounding error 有时会超过这个值。因此提供一个 option 设置推导 tolerance 的 multiplier：

```beancount
option "tolerance_multiplier" "0.6"
```

这个值覆盖默认 multiplier `0.5`。在这个例子里，对于只有 `24.45 CHF` 这类值的 transaction，CHF 的推导 tolerance 为 `+/- 0.012 CHF`。

注意：作者认为你大概永远不需要改这个（他自己用默认值），但万一他错了，这个 option 就在那里。

> **译者注 · 版本差异**  
> 在较新的 option reference 中，这个 option 也写作 `inferred_tolerance_multiplier`。两者指向同一类行为；以你所用版本的 option 名为准。

#### 从 cost 推导 tolerance

还有一个 feature：把 at-cost 或按 price 转换的 postings 所推导出的 cost currency 值，纳入 transaction 的最大 tolerance。这些 postings 可以通过“把 unit 的最小位数乘以 cost 或 price 值，再取一半”来暗示一个 tolerance。

例如，一个 posting 的金额为 `2.345 RGAGX {45.00 USD}`，它暗示 tolerance 为 `0.001 x 45.00 / 2 = 0.045 USD`。所有 at-cost 或按 price 转换的 postings 的可能 rounding error 会相加，得到的 tolerance 加入候选列表（最终取所有推导 tolerance 的最大值）。

开启方式：

```beancount
option "infer_tolerance_from_cost" "TRUE"
```

启用这个 flag 只会让 tolerance 可能**更宽**，绝不会更小。

### Balance Assertions 与 Padding

还有几个地方需要近似比较。Balance assertions 也比较两个数字：

```beancount
2015-05-08 balance Assets:Investments:RGAGX       4.271 RGAGX
```

这断言该 account 的累计 balance 为 `4.271 RGAGX`，正负 `0.001 RGAGX`。因此，`4.270` 到 `4.272 RGAGX` 都会通过断言。

tolerance 会自动推导为 balance assertion 数字最低有效位的 **1 个单位**。如果你想要更宽松的断言，可以写：

```beancount
2015-05-08 balance Assets:Investments:RGAGX       4.27 RGAGX
```

这会接受 `4.26` 到 `4.28 RGAGX`。

注意，推导出的 tolerance 也会被前面讨论的 tolerance multiplier 放大。

> **译者注 · 进阶**  
> 注意这里的“1 个单位”与 transaction 的“半个单位”不同。`4.271` 的 transaction tolerance 逻辑会给 `0.0005`，但 balance assertion 给 `0.001`。这是两套相近但不同的规则，排查 balance 错误时要分开看。

#### 触发 padding 的 tolerance

`pad` directives 会自动插入 transactions，使 account balance 与后续 balance assertion 对齐。只有当 balance 与期望值不同时才触发；触发所用的 tolerance 行为与 balance assertions 完全相同。

#### Balance assertion 上的显式 tolerance

Beancount 支持显式指定 tolerance：

```beancount
2015-05-08 balance Assets:Investments:RGAGX       4.271 ~ 0.01 RGAGX
```

这个 feature 是因为观察到 Vanguard 投资账户的一些特殊行为（rounding 似乎遵循奇怪规则，balance 对不上）而加入的。

### 迁移现有输入

从 transaction 数字推导 tolerance 的方法，通常足以让现有文件不改也能工作。用本文方法处理旧文件时，可能会出现新的错误，但这些错误要么指向输入中以前未检测到的错误，要么只需补上合适的小数位就能修复。

作为佐证，作者本人的超大输入文件迁移过程相对无痛，不到 1 小时。

为了便于过渡，你可能想把所有货币的 default tolerance 改成 Beancount 以前使用的值：

```beancount
option "inferred_tolerance_default" "*:0.005"
```

建议先这样，修完文件中所有错误，再移除这个设置，修剩下的错误。这样更容易适应新行为。

举例：把“整数金额”一节中原本失败的 transaction：

```beancount
2013-04-03 * "Buy Mutual Fund - Price as of date based on closing price"
  Assets:US:Vanguard:RGAGX    10.21005 RGAGX {37.61 USD}
  Assets:US:Vanguard:Cash         -384 USD
```

通过补零提供本地推导值：

```beancount
2013-04-03 * "Buy Mutual Fund - Price as of date based on closing price"
  Assets:US:Vanguard:RGAGX    10.21005 RGAGX {37.61 USD}
  Assets:US:Vanguard:Cash      -384.00 USD
```

足以让 balance check 安静。

## Interpolation：用 round numbers 补全

Beancount 允许用户省略某些数字，由系统补全，即 **interpolated**。例如下面 profit 的值留空：

```beancount
2013-04-03 * "Buy Mutual Fund - Price as of date based on closing price"
  Assets:US:Vanguard:RGAGX       -10.22626 RGAGX {37.61 USD}
  Assets:US:Vanguard:Cash         645.61 USD
  Income:US:Vanguard:Profit
```

虽然 Beancount 可以填入精确差额，但现实中 broker 会以两位 precision 计算 profit/loss，得到 `$216.00`，尽管未 rounding 的数字是 `$261.0003614`。Beancount 会按特定 precision 对数字进行 rounding，这个 precision 也取决于金额代表的货币。这里会插入 **`216.00 USD`**。

> **译者注 · 原文疑误**  
> 按上下文计算，`645.61 - 10.22626 x 37.61 = 261.0003614`，因此 broker 两位 precision 的结果应是 `$261.00`，不是原文写的 `$216.00`。此处保留原文，供你对照；实际理解时以 `$261.00` 为准。

### 推导数字的 precision

Beancount 能推导输入中缺失的某些数字。例如，下面 transaction 的第二个 posting 会被自动 interpolate：

```beancount
2014-05-06 * "Buy mutual fund"
  Assets:Investments:RGXGX        4.27 RGAGX {53.21 USD}
  Assets:Investments:Cash
```

从第一个 posting 计算出的插入金额是 `-227.2067 USD`。你可能会问：插入的 precision 是多少？是完整精度 `227.2067 USD`，还是 rounding 到分，例如 `227.21 USD`？

这取决于该货币推导出的 tolerance。在这个例子里，没有可推导的 tolerance（除了 cost 金额之外，没有提供 USD 金额，而 cost 在推导 tolerance 时被忽略），所以只能使用 default tolerance。

如果 default tolerance 未在输入文件中覆盖（因此为零），则使用完整 precision，不发生 rounding。结果如下：

```beancount
2014-05-06 * "Buy mutual fund"
  Assets:Investments:RGXGX        4.27 RGAGX {53.21 USD}
  Assets:Investments:Cash    -227.2067 USD
```

注意，如果可以从该 transaction 的其他数字推导出 tolerance，则会用于 rounding。例如下面这个例子，Cash posting 因 Commissions posting 上的 `9.95 USD` 而 rounding 到两位：

```beancount
2014-05-06 * "Buy mutual fund"
  Assets:Investments:RGXGX        4.27 RGAGX {53.21 USD}
  Expenses:Commissions            9.95 USD
  Assets:Investments:Cash      -237.16 USD
```

但是，如果无法推导，且 USD 的 default tolerance 设为 `0.001`，数字会在插入前 quantize 到 `0.001`，即存储 `227.207 USD`：

```beancount
option "default_tolerance" "USD:0.001"

2014-05-06 * "Buy mutual fund"
  Assets:Investments:RGXGX        4.27 RGAGX {53.21 USD}
  Assets:Investments:Cash     -227.207 USD
```

最后，如果启用了 rounding error 的累积，posting 金额会反映正确的 residual，并考虑自动插入的 rounding 金额：

```beancount
option "default_tolerance" "USD:0.01"
option "account_rounding" "Equity:RoundingError"

2014-05-06 * "Buy mutual fund"
  Assets:Investments:RGXGX        4.27 RGAGX {53.21 USD}
  Assets:Investments:Cash     -227.207 USD
  Equity:RoundingError          0.0003 USD
```

> **译者注 · 进阶**  
> interpolation 的 rounding 不是“固定两位小数”，而是“看这笔 transaction 能推导出什么 tolerance”。这也是为什么同样的 `4.27 RGAGX {53.21 USD}`，在不同 transaction 里可能补出 `-227.2067`、`-227.21` 或 `-227.207`。如果你要可复现的结果，最好显式写出金额，或固定 `inferred_tolerance_default`。

### 保存 rounding error

如前所述，transactions 不必精确 balance，允许少量 imprecision。有些人对此不舒服。如果你想跟踪并衡量 tolerance 允许的 residual，Beancount 提供 option 自动插入 postings，使每笔 transaction 精确 balance。

开启方式：

```beancount
option "account_rounding" "Equity:RoundingError"
```

这告诉 Beancount 把 rounding error 补偿到 `Equity:RoundingError` account。例如，启用后，下面这笔 transaction：

```beancount
2013-02-23 * "Buying something"
  Assets:Invest     1.245 RGAGX {43.23 USD}
  Assets:Cash      -53.82 USD
```

会自动变成：

```beancount
2013-02-23 * "Buying something"
  Assets:Invest             1.245 RGAGX {43.23 USD}
  Assets:Cash              -53.82 USD
  Equity:RoundingError   -0.00135 USD
```

你可以验证这笔 transaction 精确 balance。如果 transaction 本来已经精确 balance（大多数如此），不会插入 posting。注意，以这种方式插入的 rounding errors **不会像其他 interpolated numbers 那样被 rounding**。

最后，如果你要求所有 accounts 显式 open，记得在合适日期声明 rounding account：

```beancount
2000-01-01 open Equity:RoundingError
```

## Display：为显示而 rounding

显示数字时，看到一个除法结果带着异常多的小数位会很不协调[^3]。例如，一个 cost 显示为 `134.2374736427639678237437 USD`，对读者没有用；多余的数字很小、没有意义；我们更愿意显示 `134.24 USD`。因此，数字必须 rounding 到一定 precision。

位数取决于几件事：

- **数字代表的货币。** 美元通常分辨率是 1 分（`$0.01`），precision 为 2；日元通常用整数（1 JPY 本身很小）；共同基金份额通常至少 3 位，因为一份可能代表较大金额；汇率可能用 5 位（例如 USD/JPY）。
- **数字的上下文。** 表示另一商品单位成本时，所需 precision 有时不同于该数字总值的常用 precision。

截至 2025 年，有一个新的配置 option，可以按示例指定某货币的 intended precision：

```beancount
option "display_precision" "USD:0.01"
option "display_precision" "AUD:0.01"
```

## Computation：有限 precision 下的运算

最后，对 decimal numbers 进行计算时，必须 rounding。Beancount 内部所有数字都以 decimal 形式表示。

这是没学过计算机科学的人可能不熟悉、但很重要的话题。绝大多数时候，计算机使用 floating-point numbers，即实数的二进制近似；由于表示位数有限，rounding 自然发生。为了用 decimal numbers 表示和计算，我们使用软件实现，不受硬件限制，因此能以任意 precision 计算（代价是慢不少）。

对于 decimal numbers，某些操作会产生大量小数位，我们必须决定结果 rounding 到哪个 precision，以免用大量空间表示极小的数字。

产生大量小数位的计算会执行到 **28 位小数**（Python IEEE decimal 实现的默认 precision）。这足够，因为我们上面提出的方法很少让这类数字在整个系统中流动：tolerance 允许我们按用户声明的精确金额入账，只有自动推导的 prices 和 costs 可能产生不现实的小数位，并可能渗入系统其余部分的聚合。

参考 [Decimal fixed-point and floating-point arithmetic](https://docs.python.org/3/library/decimal.html) 与 [What Every Computer Scientist Should Know About Floating-Point Arithmetic](http://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html#689) 了解更多。

## 参考

导致该实现的[原始 proposal](https://beancount.github.io/docs/rounding_precision_in_beancount/)可以在[这里找到](https://beancount.github.io/docs/rounding_precision_in_beancount/)。特别地，proposal 强调了其他系统如何处理这个问题。邮件列表上还有[一些讨论](https://groups.google.com/forum/#!msg/ledger-cli/m-TgILbfrwA/YjkmOM3LHXIJ)。

注意，很长一段时间里，Beancount 对所有货币使用固定 tolerance `0.005`。本文方法实现后，这个做法被取消。

另外，对于 Balance 和 Pad directives，过去有一个默认 `0.015` 的 tolerance option；随着本文所述变更合并，该 option 已废弃。

## 历史说明

以下是 2016 年 3 月 Beancount 数字 render 状态的概览，[来自邮件列表](https://groups.google.com/d/msg/beancount/frfN1zc6TEc/d5OjuDnREgAJ)：

> 首先，重要的是理解这些数字在内存中如何表示。它们使用 Decimal 表示；除了能精确表示十进制数（相对于 binary floats 的近似），还包含特定的 precision。也就是说，数字 `2.00` 与 `2.0`、`2.000` 的表示不同。数字“记得”自己表示到哪个 precision。这很重要。当我说把数字 render 到它们的“natural precision”，我指的是它们被表示时的 precision，即 `2.0` render 为 `"2.0"`，`2.000` render 为 `"2.000"`。
>
> 然后，有两个**不同**的话题：(1) tolerances，(2) precision。
>
> - “Tolerances”是用于确定 balancing transactions 时可接受多少 imprecision 的值。它在验证阶段使用，决定允许多大的松弛。它不应影响数字如何 render。
> - “Precision”可能有点用词不当：我指的是数字 render 时用多少位。
>
> 很久以前——shell 已经写完之后——这些概念在 Beancount 中还没有很好定义，我也没有一致地处理。后来我清楚需要做什么，创建了一个叫 `DisplayContext` 的类，包含每种货币数字 render precision 的合适设置（每种货币通常有自己的最常见 render precision，例如 USD 两位、MXN 一位、JPY 零位；报表中通常可以把实际数字 rounding 到该 precision）。parser 中会自动实例化 `DisplayContext`；为了避免用户手动设置——让 Beancount 默认“做正确的事”——它能累积输入中见过的数字，推导出最常用和最大的位数，作为 render 的默认位数。最常用格式/位数用于 render units，见过的最大位数用于 render costs 和 prices。此外，这个类还能按小数点对齐、插入千位分隔符。它把格式控制与数字本身分离。
>
> 大多数 render 数字的代码都使用 `DisplayContext`（通过 `to_string()` 方法）把数字转成字符串，例如 web interface 和显式文本报表。但**不是全部**……这里有点历史……SQL shell 使用一些旧的专用代码 render 数字，我一直没改成 `DisplayContext`。有一个 TODO item。它需要在某个时候转换，但我一直没做，因为我对 SQL query engine 有更大的计划，包括完整重写和许多改进，我想那时再做。如果你记得，SQL query engine 是 prototype，实际上能用，但单元测试覆盖不好。我的目的是通过使用发现什么有用，然后写一个更好的 v2。
>
> 关于 `PRINT` command……它不是作为 reporting tool 设计的。printer 的目的是打印能准确表示 transaction 内容的输入。为此，它需要按数字的“natural” precision render，这样读回去时能 parse 成完全相同的数字，即相同位数（即使有零）。因此 `PRINT` command 不尝试使用从输入文件推导的 `DisplayContext` 实例 render——这是故意的。我可以改，但那样 round-trip 会坏：使用 display context 格式化产生的 rounding 可能输出不再 balance 的 transactions。
>
> 如你所见，这不是一个显而易见的话题……希望这能让你理解 Beancount 在数字 render precision 方面的输出。
>
> 注意：`default_tolerances` 最近改名为 `inferred_tolerance_default`，因为原名太泛、容易混淆。旧名仍可用，但会产生 warning。
>
> 我刚从你的评论和 grep 中注意到 `render_commas` option 不再使用。我不知道怎么发生的，但我会马上修，并把 `DisplayContext` 的默认值设为从输入推导。
>
> 我可能也应该把 SQL shell rendering 改成使用 display context，不管未来计划如何，这样它和其余部分一致。不确定这周末能做，但我会开 ticket，在[这里](https://github.com/beancount/beancount/issues/105)。
>
> 希望有帮助。如果上面不清楚，欢迎提问。抱歉这不是完全显而易见……那里有相当多历史和大量代码。我应该 review option 命名，tolerance options 名字里都有 “tolerance”，但还没有 override rendering 的 options；等我加上时，它们也应该有共同命名。

**注意：截至 2026 年 4 月，tolerances 和 precision 的配置设置仍在 review。这长期以来一直是个痛点。**

[^1]: 这与 Ledger 相反：Ledger 试图根据文件中最近 parse 的其他 transactions 推导 precision，按文件顺序。这会产生 transactions 之间在 precision 上的“cross-talk”。

[^2]: 注意，由于 Beancount 内部表示数字的方式，它也无法区分 `"230"` 和 `"230."`；两者 parse 成相同表示。因此无法利用这个区别来支持 `0.5` 的 precision。

[^3]: 调试时除外。调试时应该显示完整值，不 rounding。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
