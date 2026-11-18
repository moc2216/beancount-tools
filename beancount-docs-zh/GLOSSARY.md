# 术语表

> 本项目约定：技术术语保留英文。Agent 阅读、引用、生成新内容时，不要把这些词随意改成中文别名。

| 术语 | 含义 | 注意 |
|---|---|---|
| transaction | 一组 postings，带日期、payee、narration、tags/links、metadata | 不是单条“分录” |
| posting | 对某个 account 的一次增减 | 可带 cost、price、flag、metadata |
| directive | 以日期开头的声明，如 open、balance、price、transaction | 也叫 entry |
| account | 五类根账户下的冒号分层账户 | 必须先 `open` |
| balance assertion | `balance` directive 的余额断言 | 不是 transaction 平衡检查 |
| tolerance | 允许的 imprecision 范围 | 逐笔 transaction 推导；整数金额贡献 0 |
| precision | 数字的小数位数/显示精度 | 与 tolerance 不是同一个概念 |
| interpolation | 自动补全省略的金额 | 最多省略一个 posting 金额 |
| pad | 自动插入 transaction 以匹配后续 balance assertion | 不能未使用/对 cost 账户/重复 |
| cost | 持仓的成本基础 | 决定 book value / 资本利得 |
| price | 估值价格 | 不替代 cost basis |
| lot | 一批带成本/日期/标签的持仓 | 减仓时用来匹配 |
| booking | 多个 lot 的匹配方法 | STRICT/FIFO/LIFO/AVERAGE/NONE |
| inventory | 某个 account 的全部 positions | 余额、cost basis、PnL 的核心 |
| position | inventory 中的一项：units + cost/date/label | 也叫 lot/leg |
| augmentation | 增持：正号带 cost，建立新 lot | cost/label/date 是“赋值” |
| reduction | 减持：负号，按 cost/label/date 过滤 lot | 写错会 ambiguous match |
| cost basis | 成本基础 | 只影响税务，不参与 returns |
| market value | 市值 | 用于报表/收益，不等于 cost basis |
| cash flow | 投入/取出投资的现金流 | returns 计算的输入 |
| IRR | money-weighted return | 回答“我的钱赚了多少” |
| TWR | time-weighted return | 回答“策略本身表现如何” |
| beangulp | v3 的 importer 框架 | 取代 v2 的 ingest |
| importer | 把外部账单转成 Beancount 的模块 | 至少 `identify()` + `account()` |
| plugin | 处理 entries 的 Python 模块 | v2 中在 booking 后运行 |
| loader | 解析 + 插件 + 校验的管线 | `load_file()` 返回 entries/options/errors |
| parser | 只负责文本 → directives | parsing ≠ loading |
| option | `option "name" "value"` 配置 | 版本差异大 |
| metadata | directive/posting 上的 key-value | 核心不读用户 metadata |
| tag / link | `#tag` 分类 / `^link` 跨条目关联 | link 用于发票核销、资金链 |
| open / close | 声明 account 的生命周期 | close 不自动补零余额断言 |
| operating currency | 主要报告货币 | `option "operating_currency"` |
| quote currency | 某个价格/金额的计价货币 | 多币种换算时注意 |
| inventory booking | 同一 account 内多 lot 的匹配 | 与“账户类型”无关 |
