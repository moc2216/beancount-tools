> 非官方中文译文。术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/beancount_options_reference/

# Beancount Options Reference（配置项参考）

本页列出账本文件可用的 `option` 配置项。写法是独立一行：

```beancount
option "name" "value"
```

多数 option 必须在文件开头、任何 account 名称被解析之前出现。

## 通用信息

### option "title"（账本标题）

```beancount
option "title" "Joe Smith's Personal Ledger"
```

定义本账本 / 输入文件的标题。它会显示在每一页的顶部。

## Account 根名称

### option "name_*"（account 根名称）

```beancount
option "name_assets" "Assets"
option "name_liabilities" "Liabilities"
option "name_equity" "Equity"
option "name_income" "Income"
option "name_expenses" "Expenses"
```

每个 account 的根名称。可用它自定义类别名称：例如你更愿意用 `Revenue` 而不是 `Income`，或用 `Capital` 而不是 `Equity`，就在这里设置。

输入文件中的 account 名称必须与设置匹配，parser 会校验。这些 option 应放在文件开头，因为它们决定 parser 如何识别 account 名称。

## 期初与结转

### option "account_previous_balances"（上期余额结转）

```beancount
option "account_previous_balances" "Opening-Balances"
```

用于把之前的 transaction 汇总为期初余额的 equity account 的叶名称。

### option "account_previous_earnings"（上期留存收益）

```beancount
option "account_previous_earnings" "Earnings:Previous"
```

用于把上一会计期之前累积的收入与费用所生成的留存收益结转到资产负债表的 equity account 的叶名称。

### option "account_previous_conversions"（上期转换）

```beancount
option "account_previous_conversions" "Conversions:Previous"
```

用于插入转换的 equity account 的叶名称。这些转换把期初日期之前的转账所留下的剩余金额清零，本质上是在“修复”由带价格转换引入的误差所破坏的会计恒等式。

### option "account_current_earnings"（当期留存收益）

```beancount
option "account_current_earnings" "Earnings:Current"
```

用于把当前会计期内累积的收入与费用所生成的留存收益结转到资产负债表的 equity account 的叶名称。这通常称为“净利润”（Net Income）。

### option "account_current_conversions"（当期转换）

```beancount
option "account_current_conversions" "Conversions:Current"
```

用于插入转换的 equity account 的叶名称。这些转换把当期转账所留下的剩余金额清零。

### option "account_rounding"（舍入误差 account）

```beancount
option "account_rounding" "Rounding"
```

用于记录并累积舍入误差的 account 名称。此选项默认未设置，功能默认关闭；设为某个 account 名称后，会自动为所有带剩余金额的 transaction 添加一条 posting。

## 货币与单位

### option "conversion_currency"（退化转换货币）

```beancount
option "conversion_currency" "NOTHING"
```

用于以零的退化汇率转换所有单位的虚拟货币。它可以是账本其余部分未使用的任意货币名称；选一个在你的语言里读起来合理的独特名称。

## Tolerance 与 precision

### option "inferred_tolerance_default"（默认 tolerance）

```beancount
option "inferred_tolerance_default" "CHF:0.01"
```

> `default_tolerance` 是它的旧名称，已弃用。

货币到 tolerance 的映射：当无法自动推断时，使用这里指定的 tolerance。该 tolerance 用于校验三件事：

1. transaction 是否平衡；
2. `balance` directive 中的显式 balance assertion 是否成立；
3. `pad` directive 使用的 precision。

取值必须是 `<currency>:<tolerance>` 形式的字符串，例如 `"USD:0.005"`。默认情况下，没有推断值的货币使用零 tolerance，也就是无限 precision。

特殊值 `*` 可作为所有没有显式默认值的货币的回退值，例如 `"*:0.5"`。只用这一个值，就会把所有货币的回退 tolerance 设为 `0.5`。

（此选项可以多次提供。）

### option "inferred_tolerance_multiplier"（tolerance 乘数）

```beancount
option "inferred_tolerance_multiplier" "1.1"
```

推断 tolerance 时的乘数。当 `inferred_tolerance_default` 没有显式给出 tolerance 时，tolerance 由输入文件中的数字推断：例如某条 posting 的值是 `32.424 CAD`，CAD 的 tolerance 会被推断为 `0.001` 乘以这个乘数。

通常假定抄录这条 posting 的机构已经做过舍入，所以默认乘数为 `0.5`，即末位数字的一半。可以调大这个值，把容忍范围扩展到略超常规 tolerance 的金额，例如处理舍入行为不佳或不可预期的机构时。

precision 的处理细节见 <http://furius.ca/beancount/doc/tolerances>。

### option "infer_tolerance_from_cost"（从 cost 推断 tolerance）

```beancount
option "infer_tolerance_from_cost" "True"
```

启用后，把推断出的 transaction 最大 tolerance 扩展为：也包含由 cost 持有、或按 price 转换的 posting 所隐含的 cost 货币 tolerance。

这类 posting 的隐含 tolerance 计算方式是：最小单位数字 × cost 或 price 值 × 0.5。例如一条 posting 的金额为 `2.345 RGAGX {45.00 USD}`，隐含 tolerance 为 `0.001 × 45.00 × M = 0.045 USD`（M 即 `inferred_tolerance_multiplier`）。该值会并入计算，扩大这条 transaction 中 USD 允许的 tolerance。

正常推断的 tolerance 仍然计入。启用此标志只会让 tolerance 变宽，不会变窄。

### option "tolerance"（已弃用）

```beancount
option "tolerance" "0.015"
```

> 已弃用，且无效果。

历史上用于 balance assertion 与 `pad` directive 的 tolerance。现实世界中舍入发生在各处，检查 transaction 余额、以及要求自动插入 padding 条目时需要允许少量（但非常小）的 tolerance；这就是当时的 tolerance 金额。

### option "use_legacy_fixed_tolerances"（恢复固定 tolerance）

```beancount
option "use_legacy_fixed_tolerances" "True"
```

恢复传统的固定 tolerance 处理：Balance 与 Pad directive 固定为 0.015 单位，Transaction 在 0.005 单位处平衡，适用于任何单位。

它的用途是让人可以退回旧行为，方便过渡到新的推断 tolerance 逻辑。细节见 <http://furius.ca/beancount/doc/tolerances>。

### option "experiment_explicit_tolerances"（实验：显式 tolerance）

```beancount
option "experiment_explicit_tolerances" "True"
```

实验性功能：允许在 balance assertion 上显式写 tolerance。启用后，余额金额支持 `<number> ~ <tolerance> <currency>` 语法，例如 `532.23 ~ 0.001 USD`。

> 警告：该功能可能随时被移除。它只是一次探索，用来验证是否真的有用。

## 文件与输出

### option "documents"（document 目录）

```beancount
option "documents" "/path/to/your/documents/archive"
```

相对于当前工作目录（CWD）的目录根列表，document 文件在这些目录下查找。要被自动识别，文件名必须符合 `YYYY-MM-DD.(.*)` 格式。

（此选项可以多次提供。）

### option "operating_currency"（主用货币）

```beancount
option "operating_currency" "USD"
```

在 report 中单独列出、并为其建立专用列的货币列表，用来标明你在现实生活中主要使用的货币。

不要把所有可能的货币都列进来，它只用于日常使用的极少数主要货币。系统对输入文件中出现的单位本身不敏感，这个选项决定表格单元格里显示哪些数值、以及是否附带单位字符串。去掉单位后，数字可以直接导入电子表格：`"101.00 USD"` 无法被电子表格解析，`"101.00"` 可以。

需要多个 operating currency 时，重复整条 directive。

（此选项可以多次提供。）

### option "render_commas"（千位分隔符）

```beancount
option "render_commas" "TRUE"
```

布尔值。为 true 时，数字格式化会在数字中使用逗号作为千位分隔符。

## 插件

### option "plugin_processing_mode"（插件处理模式）

```beancount
option "plugin_processing_mode" "raw"
```

字符串，定义 loader 运行哪一组插件：

- `"default"`：在任何用户插件之前，自动运行一组预设插件。
- `"raw"`：不运行预设插件，只运行用户插件（此时应显式用 `plugin` directive 加载所需插件）。希望在插件执行顺序上拥有完全控制权时使用。

### option "plugin"（已弃用）

> 已弃用；改用 `plugin` directive。

历史上用于指定一组包含转换函数的 Python 模块，在解析后处理条目。

parser 先按原样读取条目，通过一系列标准函数（如 balance assertion 检查、插入 padding 条目）转换，然后交给这些插件生成更多内容。

该列表是 `(plugin-name, plugin-configuration)` 成对列表：

- `plugin-name` 是要导入的 Python 模块名；该模块内应有一个特殊的 `__plugins__` 属性，列出用于处理条目的转换函数名称。
- `plugin-configuration` 是用户提供的可选字符串。

每个转换函数接收 `(entries, options_map)`，返回 `(new_entries, error_instances)`。若提供了插件配置，它作为额外参数传入。错误不要打印到输出，loader 会把它们转成字符串，按输出媒介的要求显示。

（此选项可以多次提供。）

## 其他

### option "long_string_maxlines"（多行字符串行数上限）

```beancount
option "long_string_maxlines" "64"
```

超过此行的多行字符串会触发“过长行”警告。该警告的作用是：通过提示意外很长的字符串，帮助发现漏写的引号。

### option "booking_method"（booking 方法）

```beancount
option "booking_method" "SIMPLE"
```

要应用的 booking 方法，用于 interpolation，以及把 lot 规格与交易时刻库存中可用的 lot 匹配。

- `SIMPLE`：Beancount 使用的原始方法。
- `FULL`：较新的方法，对库存做模糊匹配，并允许对多个金额做 interpolation。详见 <http://furius.ca/beancount/doc/proposal-booking>。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
