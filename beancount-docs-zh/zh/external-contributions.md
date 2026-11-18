> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/external_contributions/

# Beancount 的外部贡献<a id="title"></a>

[Martin Blais](mailto:blais@furius.ca) - 更新于：2024 年 6 月

[http://furius.ca/beancount/doc/contrib](http://furius.ca/beancount/doc/contrib)

指向由其他人编写的、基于 Beancount 和/或 Ledgerhub 构建或与之相关的代码的链接。

## 索引<a id="indexes"></a>

本文档仅包含那些曾被讨论过或已向邮件列表发送过公告的包。你可以在公共索引上找到其他包：

-   PyPI：你可以在 [PyPI](https://pypi.org/search/?q=beancount&o=) 上找到许多其他与 Beancount 相关的项目。

-   GitHub：截至 2020 年 9 月，[搜索 "beancount"](https://github.com/search?p=5&q=beancount&ref=opensearch&type=Repositories) 会显示 318 个项目。

-   [awesome-beancount.com](https://awesome-beancount.com)：一个精选的 Beancount 资源列表，Beancount 是一个基于命令行、使用纯文本文件的双式记账系统。

## 书籍与文章<a id="books-and-articles"></a>

[使用 Python 管理个人财务](https://personalfinancespython.com/)（Siddhant Goel）：一本关于纯文本会计和 Beancount 的 2020 年出版的书籍。

[五分钟账本更新](https://reds-rants.netlify.app/personal-finance/the-five-minute-ledger-update/)（RedStreet）：一系列文章，展示了如何自动化从机构（银行、信用卡、经纪商等）下载数据，以便在五分钟以内完成账本更新。[邮件列表讨论串](https://groups.google.com/g/beancount/c/_NclCTXaExs/m/EFjqkqElAQAJ)。

[使用 Beancount 进行税务亏损收割](https://reds-rants.netlify.app/personal-finance/tax-loss-harvesting-with-beancount/)（RedStreet）：一篇从美国视角探讨 TLH 的文章，涵盖了相关要求、wash sale 的细微差别以及安全的卖出/买入日期，并与 robo-advisors 进行了比较。（相关：[fava\_investor TLH 模块](https://github.com/redstreet/fava_investor/tree/main/fava_investor/modules/tlh)，适用于 fava 和纯 Beancount 命令行版本）。

[共同基金 NAV 的缩放估算](https://reds-rants.netlify.app/personal-finance/scaled-estimates-of-mutual-fund-navs/)（RedStreet）：问题在于：共同基金的 NAV（至少在美国）每天仅在收盘时更新一次。当需要在交易窗口仍开放时做出财务决策（例如：进行税务亏损收割时），而当日收盘 NAV 尚未可用时，有时对 NAV 进行粗略估算会很有用，尤其是在市场波动剧烈的日子。

[从 Fidelity 抓取交易历史的快捷方式](https://noisysignal.com/trade_hist_shortcut/)（David Avraamides）：我撰写了一篇描述，说明如何使用 Shortcut 从 Fidelity 网站抓取交易历史，通过 Python 脚本将其转换为 Beancount 的账本格式，然后将其保存到剪贴板，以便粘贴到账本文件中。

[懒人的 Beancount](https://lazy-beancount.xyz/)（Vasily M）/ [Evernight/lazy-beancount](https://github.com/Evernight/lazy-beancount)：一份关于如何开始（并继续）使用开源 Beancount 会计系统追踪个人财务的观点鲜明的指南。它附带了一些代码。该指南的主要目标是为您提供一种方式，使用纯文本会计逐步且增量地开始管理自己的财务。同时也包含并配置了各种有用的工具。

[平衡之道 — https://academy.beanhub.io/](https://academy.beanhub.io/)（Fang-Pen Lin）：使用可视化和图表解释复式记账法。

[Beancount 中的多周期 hledger 风格报告：透视表 | Altynbek Isabekov](https://www.isabekov.pro/multiperiod-hledger-style-reports-in-beancount-pivoting-a-table/)：一篇展示如何生成账户余额透视表摘要的文章，例如按年份汇总，并附有[相关代码 (github)](https://github.com/isabekov/beancount-multiperiod-reports)。

[我信任的一个数字：多币种家庭的纯文本会计 - Lalit Maganti](https://lalitm.com/post/one-number-i-trust/) - 一篇记录 DEB 各种使用示例的文章。

[交互式 beanquery 手册](https://github.com/Ev2geny/beanquery-interactive-manual)（Chary Ev2geny）：涵盖了 beanquery 的最新功能，包含许多使用实际账本的实例，具有自文档化特性：所有查询输出都是作为 notebook 执行的一部分通过运行 beanquery 计算得出的；具有交互性：当作为 marimo notebook 运行时，读者可以通过更改默认账本和/或查询进行实验，输出会自动更新。

[Beancount 或黑客的会计](https://cdeguet.net/blog/beancount-comptabilite-pour-hackers/)（Cyril Deguet）

## 插件<a id="plugins"></a>

[split\_transactions](https://www.google.com/url?q=https%3A%2F%2Fgist.github.com%2Fkljohann%2Faebac3f0146680fd9aa5&sa=D&sntz=1&usg=AFQjCNGn2AkL35onTeXgOQzLzkjVpvLcpg)：Johann Klähn [编写了一个插件](https://groups.google.com/d/msg/beancount/z9sPboW4U3c/1qIIzro4zFoJ)，可以将单个 transaction 拆分到多个针对 limbo account 的 posting 中，类似于折旧处理。

[zerosum](https://github.com/redstreet/beancount_reds_plugins)：Red S [编写了一个插件](https://groups.google.com/d/msg/beancount/MU6KozsmqGQ/sehD3dqZslEJ)，用于匹配那些合在一起总和应为零的 transaction，并将它们移动到一个单独的 account 中。

[effective\_dates](https://github.com/redstreet/beancount_reds_plugins)：Red S 编写了一个插件，用于将 transaction 的不同部分 booking 到不同的日期。

[beancount-plugins](https://github.com/davidastephens/beancount-plugins)：Dave Stephens 创建了一个仓库，用于分享他编写的与折旧相关的各种插件。

[beancount-plugins-zack](https://github.com/zacchiro/beancount-plugins-zack)：Stefano Zacchiroli 创建了这个仓库来分享他的插件。包含 directive 排序等功能。

b[eancount-oneliner](https://github.com/Akuukis/beancount-oneliner)：Akuukis 创建了一个插件，用于在一行中写入 entry（[PyPi](https://pypi.python.org/pypi/beancount-oneliner/1.0.0)）。

[beancount-interpolate](https://github.com/Akuukis/beancount-interpolate)：Akuukis 为 Beancount 创建了用于 transaction interpolation 的插件（recur, split, depr, spread）（[PyPi](https://pypi.python.org/pypi/beancount-interpolate)）。

[metadata-spray](https://github.com/seltzered/beancount-plugins-metadata-spray)：通过正则表达式跨 entries 添加元数据，而不是使用显式的 entries（由 Vivek Gani 编写）。

[Akuukis/beancount\_share](https://github.com/Akuukis/beancount_share)：一个 Beancount 插件，用于在一个 ledger 内将费用在多个合伙人之间分摊。这个插件功能非常强大，很可能可以满足你所有的分摊需求。

[w1ndy/beancount\_balexpr](https://github.com/w1ndy/beancount_balexpr)（Di Weng）：一个提供“balance expressions”的插件，可作为 Custom directive 针对 Beancount entries 运行。参见[此线程](https://groups.google.com/d/msgid/beancount/cdcf2cc7-8061-4f69-ae6a-c82564463652n%40googlegroups.com?utm_medium=email&utm_source=footer)。

[autobean.narration](https://git.io/autobean.narration)（Archimedes Smith）：允许通过从行内注释填充 per-posting narration 元数据，以简洁的方式为每个 posting 添加注释。

[autobean.sorted](https://github.com/SEIAROTg/autobean/)：检查每个文件中的 transaction 是否按非降序排列。通过警告那些未按日期非降序排列的 directive，帮助识别位置错误或日期错误的 directive。

[hoostus/beancount-asset-transfer-plugin](https://github.com/hoostus/beancount-asset-transfer-plugin)：一个插件，用于在两个 Beancount account 之间自动生成实物转移，同时保留 cost basis 和获取日期。

[PhracturedBlue/fava-portfolio-summary](https://github.com/PhracturedBlue/fava-portfolio-summary)（Phractured Blue）：一个 Fava 插件，用于显示带有收益率的投资组合摘要。

[rename\_accounts](https://github.com/redstreet/beancount_reds_plugins)：Red S 编写的用于重命名 account 的插件。例如：将“Expenses:Taxes”重命名为“Income:Taxes”有助于费用分析。[更多详情在此](https://github.com/redstreet/beancount_reds_plugins/tree/main/beancount_reds_plugins/rename_accounts#readme)。

[Long\_short capital gains classifier](https://github.com/redstreet/beancount_reds_plugins/tree/master/beancount_reds_plugins/capital_gains_classifier)：Red S 编写的插件，根据资产持有期限将资本利得分类为长期和短期，并根据价值分类为收益和损失。

[Autoclose\_tree](https://github.com/redstreet/beancount_reds_plugins/tree/main/beancount_reds_plugins/autoclose_tree)：当关闭一个 account 时，自动关闭该 account 的所有后代。

[Evernight/beancount-valuation](https://github.com/Evernight/beancount-valuation)（Vasily M）：一个 Beancount 插件，用于跟踪不透明基金的总价值。你可以使用它代替 balance assertion 来断言 account 的总价值。如果 account 的当前价值不同，它将改为调整由插件用于技术目的创建的底层合成商品的 price。

[Evernight/beancount-plugin-tax-uk](https://github.com/Evernight/beancount-plugin-tax-uk/)（Vasily M）：一个为 Beancount 生成英国资本利得、股息和其他 investment income 税务 report 的插件。

[beancount\_reds\_plugins/…/box\_accrual](https://github.com/redstreet/beancount_reds_plugins/tree/main/beancount_reds_plugins/box_accrual)（Redstreet）：自动按比例将合成贷款（box spread）的资本损失分摊到各个日历年，创建用于报告的准确年度应计 entry。

[scanta2/ESPPresso](https://github.com/scanta2/ESPPresso)（Stefano Mihai Canta）：一个用于计算 ESPP 处置普通收入的 Beancount 插件。

## 工具<a id="tools"></a>

[alfred-beancount](https://github.com/blaulan/alfred-beancount) (Yue Wu)：macOS 工具 “Alfred” 的插件，用于快速在 Beancount 文件中录入 transaction。支持完整的 account 名称和收款方匹配。

[bean-add](https://github.com/simon-v/bean-add) (Simon Volpert)：Beancount transaction 录入助手。

[hoostus/fincen\_114](https://github.com/hoostus/fincen_114) (Justus Pendleton)：FBAR / FinCEN 114 report 生成器。

[ghislainbourgeois/beancount\_portfolio\_allocation](https://github.com/ghislainbourgeois/beancount_portfolio_allocation) ([Ghislain Bourgeois](https://groups.google.com/d/msgid/beancount/b36d9b67-8496-4021-98ea-0470e5f09e4b%40googlegroups.com?utm_medium=email&utm_source=footer))：一种快速计算不同投资组合中资产配置的方法。

[hoostus/portfolio-returns](https://github.com/hoostus/portfolio-returns) (Justus Pendleton)：投资组合回报率计算器

[costflow/syntax](https://github.com/costflow/syntax) (Leplay Li)：一款允许用户从常用即时通讯应用中保存纯文本记账的产品。一种将单行消息转换为 beancount/\*ledger 格式的语法。

[process control chart](https://github.com/hoostus/beancount-control-chart) (Justus Pendleton)：相对于投资组合规模的支出。[讨论帖。](https://groups.google.com/d/msgid/beancount/0cd47f9a-37d6-444e-8516-25e247a9e0cd%40googlegroups.com?utm_medium=email&utm_source=footer)

[Pinto](https://pypi.org/project/pinto/) (Sean Leavey)：Beancount 的增强型命令行界面。支持在 ledger 文件中自动插入 transaction。

[PhracturedBlue/fava-encrypt](https://github.com/PhracturedBlue/fava-encrypt)：一种基于 docker 的解决方案，用于在保持 Fava 在线的同时，对静态存储的 beancount 数据进行加密。请参阅[此讨论帖](https://groups.google.com/d/msgid/beancount/ece6f424-a86b-4e6d-8ecc-4e05c8e74373n%40googlegroups.com?utm_medium=email&utm_source=footer)以了解背景。

[kubauk/beancount-import-gmail](https://github.com/kubauk/beancount-import-gmail)：beancount-import-gmail 使用 gmail API 和 OAuth 登录您的邮箱并下载订单详情，然后用于增强您的 transaction 以便于分类。

[sulemankm/budget\_report](https://github.com/sulemankm/budget_report)：一个非常简单的命令行预算跟踪工具，用于 beancount ledger 文件。

[fdavies93/minibudget](https://github.com/fdavies93/minibudget) (Frank Davies)：MiniBudget 是一个旨在使用纯文本格式实现个人和小型企业预算管理的工具。它受 beancount 和 plainbudget 的启发。

[dyumnin/dyu\_accounting](https://github.com/dyumnin/dyu_accounting)：一套会计配置，用于自动化生成各种财务报表，以符合印度政府的规定。

[Gains Minimizer](https://github.com/redstreet/fava_investor/tree/main/fava_investor/modules/minimizegains) (RedStreet)：自动确定要出售的 lot 以最小化资本利得税。[在线示例。](http://favainvestor.pythonanywhere.com/example-beancount-file/extension/Investor/?module=minimizegains)

[beanahead](https://github.com/maread99/beanahead) (Marcus Read)：增加了包含未来 transaction 的功能（自动生成定期 transaction，提供临时预期 transaction，预期 transaction 与导入的 transaction 进行对账；所有功能均可通过 cli 访问）。

[autobean-format](https://github.com/SEIAROTg/autobean-format) (Archimedes Smith)：又一个 beancount 格式化程序，由早期项目 autobean-refactor 提供支持，autobean-refactor 是一个用于解析和以编程方式操作 beancount 文件的库。基于正确的解析器，使其能够格式化 ledger 的每个角落，包括算术表达式。

[akirak/flymake-bean-check](https://github.com/akirak/flymake-bean-check) (Akira Komamura)：Emacs 的 flymake 支持。

[bean-download](https://reds-rants.netlify.app/personal-finance/direct-downloads/) (Red Street)：随 beancount-reds-importers 一起提供的下载器，您可以配置它运行任意命令来下载您的 account 对账单。它现在有一个新功能：needs-update 子命令。

[gerdemb/beanpost](https://github.com/gerdemb/beanpost) (Ben Gerdemann)：Beanpost 由一个 PostgreSQL 架构和导入/导出命令组成，允许您在 beancount 文件和 PostgreSQL 数据库之间传输数据。Beancount 的许多功能是使用自定义 PostgreSQL 函数实现的，允许进行复杂的查询和数据操作。此设置提供了一个灵活的后端，可以与 web 应用程序或 report 系统等其他工具集成

[LaunchPlatform/beanhub-cli](https://github.com/LaunchPlatform/beanhub-cli) (Fang-Pen Lin)：BeanHub 或 Beancount 用户的命令行工具。

[zacchiro/beangrep](https://github.com/zacchiro/beangrep)：Beangrep 是 Beancount 纯文本会计系统的类 grep 过滤器。

[Ev2geny/evbeantools](https://github.com/Ev2geny/evbeantools)：该工具使得在汇率变动以及资金从一种商品转移到另一种商品（包括基于 cost 和非基于 cost 的跟踪）的多币种/多商品 ledger 情况下，能够解释任意两个日期之间净资产的变化。这是通过创建一个转换/等效 ledger 来实现的，可以使用 beanquery 在其上进行进一步分析。

[d-k-c/bean-acb](https://github.com/d-k-c/bean-acb) (Damien Riegel)：一个帮助跟踪财产调整后成本基础（ACB）的脚本。该规则在加拿大用于计算处置财产时必须申报的资本利得。

[tesujimath/bean-sort](https://github.com/tesujimath/bean-sort) (Simon Guest)：bean-sort 是一个用于 Beancount 文件的简单排序实用程序。它之所以简单，是因为它不尝试解析文件，只是按日期字段进行分割。

Beanquick ([https://twobitsware.com/beanquick](https://twobitsware.com/beanquick))：一款 macOS 应用程序，提供三种录入 transaction 的方式，从引导式表单到快速语法。

[paulsc/fava-edit-replay](https://github.com/paulsc/fava-edit-replay) (Paul S)：此扩展允许你一次性对多个 Beancount transaction 应用批量编辑，将编辑操作（搜索过滤器与 diff 的组合）保存为“replays”，以便稍后应用；可按 account、时间段或自定义过滤器筛选 transaction，并根据最近修改的 transaction 建议过滤器。

[alensiljak/ledger2bql](https://github.com/alensiljak/ledger2bql) (Alen Šiljak)：为 Beancount 提供 ledger 风格的查询。

[bean-inquiry](https://pypi.org/project/bean-inquiry/) (Oscar & Ale)：运行带参数的查询。

[slimslickner/beanschedule](https://github.com/slimslickner/beanschedule) (Tim Tichner)：beanschedule 提供两个主要功能：一个用于预测计划 transaction 的 plugin，以及一个用于增强导入 transaction 的 hook。每个 schedule 都定义为一个 yaml 文件，包含匹配逻辑、重复规则和预期的 posting。目前，唯一的“动态” posting 是贷款摊销，其中会包含 Interest 和 Principal 等 account；基本的匹配仅是一个 cost 范围。

[romamo/beancount-cli](https://github.com/romamo/beancount-cli) (Roman Medvedev)：这是一个基于 Beancount v3 和 Pydantic 构建的现代 CLI。除了标准的 ledger 任务外，我一直致力于使其“agent-friendly”——即通过描述性的帮助字符串和内置的 JSON schema 发现机制，使其能与 AI 助手和自动化工作流良好配合。

## AI 工具<a id="ai-tools"></a>

### MCP 服务器<a id="mcp-servers"></a>

[vanto/beanquery-mcp](https://github.com/vanto/beanquery-mcp)（Tammo van Lessen）：一个实验性的 MCP 服务器，用于演示如何结合 Claude 处理 BQL 的 beanquery。[截图](https://github.com/vanto/beanquery-mcp/blob/main/docs/screenshot-expanded.png)。（这是一个概念验证（PoC），您应谨慎选择希望与哪个 LLM 共享的数据。）

[StdioA/beancount-mcp](https://github.com/StdioA/beancount-mcp)（David Dai）：一个 Beancount MCP 服务器，可以执行 beancount 查询，并向账本提交 (a) transaction。

## 替代实现<a id="alternative-implementations"></a>

[yagebu/uromyces](https://github.com/yagebu/uromyces) (Jakob Schnitzer)：uromyces 是 Beancount 部分功能的 Rust 玩具级重新实现。

[themoritz/turbobean](https://github.com/themoritz/turbobean) (Moritz Drexl)：Beancount 的 Zig 语言替代实现。这是一个从零开始实现的 Beancount，速度快且不依赖 Python 生态系统。

[tesujimath/limabean](https://github.com/tesujimath/limabean) (Simon Guest)：这是一个使用 Rust、Clojure 和 Lima 解析器实现的 Beancount 新版本。

## 替代解析器<a id="alternative-parsers"></a>

### Bison（parser generator） <a id="bison"></a>

Beancount v2 解析器使用 GNU flex + GNU bison（以实现最大可移植性）。

Beancount v3 解析器使用 [RE/flex](https://www.genivia.com/doc/reflex/html/) + GNU bison（以支持 Unicode 和 C++）。

### 使用 Antlr<a id="using-antlr"></a>

[jord1e/jbeancount](https://github.com/jord1e/jbeancount)（Jordie Biemold）/ 使用 Antlr：一个用于 Beancount 输入语法的替代解析器，以 Java 实现（使用 Antlr4 解析器生成器）。这允许从 JVM 语言访问解析后的 Beancount 数据——而不受插件影响。详情请参阅[此帖子](https://groups.google.com/d/msgid/beancount/72ee8adb-a376-4e30-b6d4-ea8749f5f666n%40googlegroups.com?utm_medium=email&utm_source=footer)。

### 使用 Tree-sitter<a id="using-tree-sitter"></a>

[polarmutex/tree-sitter-beancount](https://github.com/polarmutex/tree-sitter-beancount)（Bryan Ryall）：一个用于 Beancount 语法的 tree-sitter 解析器。

[https://github.com/dnicolodi/tree-sitter-beancount](https://github.com/dnicolodi/tree-sitter-beancount)（Daniele Nicolodi）：另一个基于 tree-sitter 的 Beancount 语法解析器。

### Rust 实现<a id="in-rust"></a>

[jcornaz/beancount-parser](https://github.com/jcornaz/beancount-parser)（Jonathan Cornaz）：一个用于 Rust 的 beancount 文件解析库。使用 nom。

[beancount\_parser\_lima](https://docs.rs/beancount-parser-lima/latest/beancount_parser_lima/)（Simon Guest）：一个 Rust 中的 Beancount 零拷贝解析器。它旨在完整实现 Beancount 文件格式，除了那些已弃用的部分以及此处记录的其他功能（该列表可能并不全面）。使用 [Logos](https://docs.rs/logos/latest/logos/)、[Chumsky](https://docs.rs/chumsky/latest/chumsky/) 和 [Ariadne](https://docs.rs/ariadne/latest/ariadne/)。

### Emacs Lisp（编辑器脚本） <a id="emacs-lisp"></a>

[trs-80/beancount-txn-elisp/](https://sr.ht/~trs-80/beancount-txn-elisp/)：beancount-txn-elisp：一个用 Emacs Lisp 实现的库，用于读取/解析和写入/插入单个 Beancount transaction。

## 导入器<a id="importers"></a>

[reds importers](https://github.com/redstreet/beancount_reds_importers)：针对[多家](https://github.com/redstreet/beancount_reds_importers/tree/main/beancount_reds_importers)美国机构及多种文件类型的简单导入器和工具。它通过提供维护良好的通用库（涵盖银行、信用卡、投资机构以及各种文件类型），强调编写自定义导入器的便捷性，从而最大限度地减少你需要编写的特定机构代码。这是 **[五分钟账本更新](https://reds-rants.netlify.app/personal-finance/the-five-minute-ledger-update/)** 中所表达原则的参考实现。欢迎贡献。由 RedStreet 开发。

[plaid2text](https://github.com/madhat2r/plaid2text)：一个从 [Plaid](http://www.plaid.com/) 获取数据的导入器，它将 transaction 存储到 Mongo DB 中，并能够将其渲染为 Beancount 语法。由 Micah Duke 开发。

[jbms/beancount-import](https://github.com/jbms/beancount-import)：一个用于从外部数据源半自动导入 transaction 的工具，支持将导入的 transaction 彼此之间以及与 beancount 日志中现有 transaction 进行合并和对账。其 UI 基于 Web。([公告](https://github.com/jbms/beancount-import)，[旧版本链接](https://groups.google.com/d/msg/beancount/YN3xL09QFsQ/qhL8U6JDCgAJ))。由 Jeremy Maitin-Shepard 开发。

[awesome-beancount](https://github.com/wzyboy/awesome-beancount)：针对中国银行的导入器集合 + 技巧与窍门。由 [Zhuoyun Wei](https://github.com/wzyboy) 开发。

[beansoup](https://github.com/fxtlabs/beansoup)：Filippo Tampieri 在此项目中分享了他的一些 Beancount 导入器和自动补全器。

[montaropdf/beancount-importers](https://github.com/montaropdf/beancount-importers/)：一个用于从工时表格式中提取加班费和休假以向客户开具发票的导入器。

[siddhantgoel/beancount-dkb](https://github.com/siddhantgoel/beancount-dkb) (Siddhant Goel)：用于 DKB CSV 文件的导入器。

[prabusw/beancount-importer-zerodha](https://github.com/prabusw/beancount-importer-zerodha)：用于印度券商 Zerodha 的导入器。

[prabusw/beancount-importers-india](https://github.com/prabusw/beancount-importers-india)：用于部分印度银行和券商的导入器（已更新以使用 beangulp + v3）。

[swapi/beancount-utils](https://github.com/swapi/beancount-utils)：另一个用于 Zerodha 的导入器。

[Dr-Nuke/drnuke-bean](https://github.com/Dr-Nuke/drnuke-bean) (Dr Nuke)：一个基于 flex query（类似 API）的 IBKR 导入器，以及一个用于瑞士邮政银行（Swiss PostFinance）的导入器。

[Beanborg](https://github.com/luciano-fiandesio/beanborg) (Luciano Fiandesio)：Beanborg 自动从外部 CSV 文件导入财务 transaction 到 Beancount 记账系统中。

[szabootibor/beancount-degiro](https://gitlab.com/szabootibor/beancount-degiro) ([PyPI](https://pypi.org/project/beancount-degiro))：用于荷兰券商 Degiro 交易账户的导入器。

[siddhantgoel/beancount-ing-diba](https://github.com/siddhantgoel/beancount-ing-diba) ([PyPI](https://pypi.org/project/beancount-ing-diba/))：ING 账户导入器（荷兰）。

[PaulsTek/csv2bean](https://github.com/PaulsTek/csv2bean)：一个使用 Google Sheets 预处理 CSV 文件的简单 Go 应用程序。

[ericaltendorf/magicbeans](https://github.com/ericaltendorf/magicbeans) (Eric Altendorf)：用于加密货币数据的 Beancount 导入器。提供详细的 lot 跟踪以及加密货币资产的资本利得/损失 report。"我编写它是因为我对现有商业加密货币税务 report 服务的准确性或透明度不满意。"

[OSadovy/uabean](https://github.com/OSadovy/uabean/) (Oleksii Sadovyi)：一套针对乌克兰流行银行及其他机构的 Beancount 导入器和脚本。

[fdavies93/seneca](https://github.com/fdavies93/seneca) (Frank Davies)：用于 Wise 的导入器。支持多币种转账。

[LaunchPlatform/beanhub-import](https://github.com/LaunchPlatform/beanhub-import)：带有 UI 的新 Beancount 导入器。

[rlan/beancount-multitool](https://github.com/rlan/beancount-multitool) (Rick Lan)：Beancount Multitool 是一个命令行界面 (CLI) 工具，用于将金融机构的财务数据转换为 Beancount 文件（支持：JA Bank ＪＡネットバンク, Rakuten Card 楽天カード, Rakuten Bank 楽天銀行, SBI Shinsei Bank 新生银行）。相关文章：[https://www.linkedin.com/feed/update/urn:li:activity:7198125470662500352/](https://www.linkedin.com/feed/update/urn:li:activity:7198125470662500352/)

[LaunchPlatform/beanhub-import](https://github.com/LaunchPlatform/beanhub-import) (Fang-Pen Lin)：Beanhub-import 是一个简单、声明式、智能且易于使用的库，用于从 beanhub-extract 导入提取的 transaction。它基于预定义规则生成 Beancount transaction。

[Sieboldianus/beancount-hibiscus-importer](https://github.com/Sieboldianus/beancount-hibiscus-importer)：Hibiscus 是德国广泛使用的开源软件。它支持使用 HBCI 或 FinTS 标准从银行获取 transaction，并（通过插件）通过网页抓取（信用卡）或 API（例如 Paypal）获取。此 Beancount Hibiscus Importer 提供导入功能，用于从 Hibiscus H2DB（直接或通过 XML-RPC）获取 transaction，并使用 v3 Beangulp 接口将其转换为 Beancount 格式。

[flowerbug/bcgt](https://github.com/flowerbug/bcgt)：一个用于生成股票买入、卖出和拆股 Beancount Transaction 的工具。Bcgt 改编自 beangrow 中引用的 export.py 程序，该程序在早期 beancount 版本中可用。

[AmmarShaqeel/maybank-importer](https://github.com/AmmarShaqeel/maybank-importer) (Ammar Shaqeel)：用于 Maybank（马来西亚）PDF 对账单的导入器。

[AmmarShaqeel/rajhi-importer](https://github.com/AmmarShaqeel/rajhi-importer) (Ammar Shaqeel)：用于 Rajhi（沙特阿拉伯）PDF 对账单的导入器。

[redstreet/beancount\_reds\_importers//amazon](https://github.com/redstreet/beancount_reds_importers/tree/main/beancount_reds_importers/importers/amazon)（Redstreet）：用于处理 Amazon GDPR 数据导出的 Beancount Reds Importers。

[tarioch/beancounttools](https://github.com/tarioch/beancounttools/)：针对 [AwardWallet](https://awardwallet.com/) 的 importer，该服务提供（免费的）API，并集成了约 460 个航空公司、租车、购物及其他领域的忠诚度计划。

[https://github.com/tesujimath/limabean-harvest](https://github.com/tesujimath/limabean-harvest)（Simon Guest）：limabean-harvest 是一个新的 Beancount importer，基于与 limabean 相似的原则构建，即混合使用 Rust 和 Clojure。其引人注目的特性包括：以数据而非代码进行配置，从 payee 和 narration 字段推断 secondary accounts，特别是这使得在同一组中导入的两个账户之间的 transaction 配对成为可能。

## 转换器<a id="converters"></a>

[plaid2text](https://github.com/madhat2r/plaid2text)：用于导出 Plaid transaction 并将其转换为 Ledger 或 Beancount 语法格式文件的 Python 脚本。

[gnucash-to-beancount](https://github.com/henriquebastos/gnucash-to-beancount/)：Henrique Bastos 编写的脚本，用于将 GNUcash SQLite 数据库转换为等效的 Beancount 输入文件。

[debanjum/gnucash-to-beancount](https://github.com/debanjum/gnucash-to-beancount)：上述项目的 fork。

[andrewStein/gnucash-to-beancount](https://github.com/AndrewStein/gnucash-to-beancount)：基于上述两个项目的进一步 fork，修复了许多问题（参见[此讨论串](https://groups.google.com/d/msg/beancount/MaaASKR1SSI/GX5I8lOkBgAJ)）。

[hoostus/beancount-ynab](https://github.com/hoostus/beancount-ynab)：从 YNAB 到 Beancount 的转换器。

[hoostus/beancount-ynab5](https://github.com/hoostus/beancount-ynab5)：同一作者针对 YNAB 的相同转换器，但适用于较新的版本 5。

[ledger2beancount](https://github.com/zacchiro/ledger2beancount/)：用于将 ledger 文件转换为 beancount 的脚本。由 Stefano Zacchiroli 和 Martin Michlmayr 开发。

[smart\_importer](https://github.com/johannesjh/smart_importer)：beancount 和 fava 的智能导入器，提供 account 名称的智能建议。作者为 Johannes Harms。

[beancount-export-patreon.js](https://gist.github.com/riking/0f0dab2b7761d2f6895c5d58c0b62a66)：用于导出您的 Patreon transaction 的 JavaScript，以便您可以查看确切向谁提供了资金的详细信息。作者为 kanepyork@gmail。

[alensiljak/pta-converters](https://gitlab.com/alensiljak/pta-converters)（Alen Šiljak）：GnuCash -&gt; Beancount 转换器（2019 年）。

[grostim/Beancount-myTools](https://github.com/grostim/Beancount-myTools)（Timothee Gros）：作者为法国银行开发的个人导入工具。

## 下载器<a id="downloaders"></a>

[bean-download](https://github.com/redstreet/beancount_reds_importers) (RedStreet)：bean-download 是一个用于从支持的机构便捷下载 transaction 的工具。你通过配置机构列表和任意下载命令（通常通过 [ofxget](https://ofxtools.readthedocs.io/en/latest/)）来使用它。它会并行下载所有文件，正确命名它们，并将其放入你选择的目录中，之后你可以从中导入。该工具作为 [beancount-reds-importers](https://github.com/redstreet/beancount_reds_importers) 的一部分进行安装。请参阅 [配套文章](https://reds-rants.netlify.app/personal-finance/direct-downloads/)。

[ofx-summarize](https://github.com/redstreet/beancount_reds_importers) (RedStreet)：在构建 importer 时，能够查看你试图导入的 .ofx 或 .qfx 文件的内容会很有帮助。ofx-summarize 命令正是为此而设计的。它随 [beancount-reds-importers](https://github.com/redstreet/beancount_reds_importers) 一起提供，通常只需调用该命令即可使用。在文件上运行该命令会显示文件中的几笔 transaction。非常有用的是，你可以通过 python 调试器或解释器来探索你的 .ofx 文件。

## 价格来源<a id="price-sources"></a>

[hoostus/beancount-price-sources](https://github.com/hoostus/beancount-price-sources) : 一个 Morningstar 价格获取器，可聚合多个交易所的数据，包括非美国交易所。

[andyjscott/beancount-financequote](https://github.com/andyjscott/beancount-financequote) : 为 bean-price 提供 Finance::Quote 支持。

[aamerabbas/beancount-coinmarketcap](https://github.com/aamerabbas/beancount-coinmarketcap): coinmarketcap 的价格获取器（[参见帖子](https://medium.com/@danielcimring/downloading-historical-data-from-coinmarketcap-41a2b0111baf)）。

[grostim/Beancount-myTools/.../iexcloud.py](https://github.com/grostim/Beancount-myTools/blob/master/price/iexcloud.py) : 由 Timothee Gros 编写的 iexcloud 价格获取器。

[xuhcc/beancount-cryptoassets](https://github.com/xuhcc/beancount-cryptoassets) (Kirill Goncharov): 加密货币的价格来源。

[xuhcc/beancount-ethereum-importer](https://github.com/xuhcc/beancount-ethereum-importer) (Kirill Goncharov): 用于 Beancount 的以太坊 transaction 导入器。包含一个从 Etherscan 下载 transaction 的脚本，以及一个用于导入已下载 transaction 的导入器。

[xuhcc/beancount-exchangerates](https://github.com/xuhcc/beancount-exchangerates) (Kirill Goncharov): [http://exchangeratesapi.io](http://exchangeratesapi.io) 的价格来源。

[tarioch/beancounttools](https://github.com/tarioch/beancounttools) (Patrick Ruckstuhl): 价格来源和导入器。

[https://gitlab.com/chrisberkhout/pricehist](https://gitlab.com/chrisberkhout/pricehist) (Chris Berkhout): 一个命令行工具，可从多个来源获取每日历史价格，并以多种格式输出。支持 CoinDesk、欧洲中央银行、Alpha Vantage、CoinMarketCap 的部分来源。用户可以请求特定的价格类型，如最高价、最低价、开盘价、收盘价或调整后收盘价。它也可以通过 bean-price 使用。

## 开发<a id="development"></a>

[Py3k 类型注解](https://github.com/yegle/beancount-type-stubs)：Yuchen Ying 正在为 Beancount 实现 python3 类型注解。

[bryall/tree-sitter-beancount](https://github.com/bryall/tree-sitter-beancount)（Bryan Ryall）：一个用于 beancount 语法的 tree-sitter 解析器。

[jmgilman/beancount-stubs](https://github.com/jmgilman/beancount-stubs)：部分 Beancount 源代码的 Typing .pyi 存根文件。

## 文档<a id="documentation"></a>

[Beancount 文档](https://beancount.github.io/docs/)（[Kirill Goncharov](http://github.com/xuhcc)）：将 Beancount 文档从 Google Docs 源文件正式转换为 Markdown 和 HTML 格式。这包括大部分 Google Docs 文档，并由 Kirill Goncharov 在 Beancount 组织仓库中[维护于此](http://github.com/beancount/docs)。

[Beancount 源代码文档](http://aumayr.github.io/beancount-docs-static/)（[Dominik Aumayr](http://github.com/aumayr)）：由 Sphinx 生成的 Beancount 代码库源代码文档。生成此文档的代码[位于此处](https://github.com/aumayr/beancount-docs)。

[Beancount 的 SQL 查询](http://aumayr.github.io/beancount-sql-queries/)（Dominik Aumayr）：示例 SQL 查询。

[Beancount —— 命令行复式簿记](https://wzyboy.im/post/1063.html)（Zhuoyun Wei）：一篇关于如何使用 Beancount 的中文教程（博客文章）。

[使用 Beancount 管理我的个人财务](https://alexjj.com/blog/2016/2/managing-my-personal-finances-with-beancount/)（Alex Johnstone）

[使用 Beancount 数豆子——以及更多](https://lwn.net/SubscriberLink/751874/a38128abb72e45c5/)（LWN）

## 接口 / Web<a id="interfaces-web"></a>

[fava: Beancount 的 Web 界面](https://github.com/aumayr/fava)（Dominik Aumayr, Jakob Schnitzer）：Beancount 自带一个简单的 Web 前端（“bean-web”），其目的仅作为一个薄壳，用于调用并显示其 report 的 HTML 版本。“Fava” 是一个具有更多且不同功能的替代 Web 应用前端，最初旨在作为一个试验场和概念验证，以探索一种更新、更好的设计来呈现 Beancount 文件的内容。

[Fava Classy Portfolio](https://github.com/seltzered/fava-classy-portfolio)（Vivek Gani）：Classy Portfolio 是 Fava 的一个扩展，Fava 是 Beancount 纯文本会计软件的 Web 界面。该扩展显示不同投资组合（例如 'taxable' 与 'retirement'）的列表，并使用商品上的 'asset-class' 和 'asset-subclass' 元数据标签进行细分。

[Fava Investor](https://github.com/redstreet/fava_investor) 项目（RedStreet）：Fava\_investor 旨在成为一套针对 Beancount 和 Fava 的综合性 investment 报告、分析工具和工具集。它是一组模块的集合，每个模块提供一个 Fava 插件、一个 Beancount 库以及一个基于 Beancount 的 CLI（命令行界面）。当前模块包括：Visual、按类别划分的树状资产分配、按 account 划分的资产分配、税务亏损收割器、cash drag 分析。

[Fava Miler](https://github.com/redstreet/fava_miler)（RedStreet）：航空里程和奖励积分：到期日和价值报告。

[Fava Envelope](https://github.com/bryall/fava-envelope)（Brian Ryall）：一个 beancount fava 扩展，为 fava 和 beancount 添加信封预算功能。它作为 Fava 插件和 CLI 开发。

[scauligi/refried](https://github.com/scauligi/refried)（Sunjay Cauligi）：一个受 YNAB 启发的 Fava 信封预算插件：所有支出 account 都成为独立的预算类别，预算通过向这些 account 的 transaction 执行，并且该插件自动为所有重新预算的 transaction 应用标签，以便轻松过滤。提供类似 YNAB 的预算和 account 视图。

[BeanHub.io](https://beanhub.io/)：Beancount 内容的 Web 前端。“*自从我开始使用 Beancount 以来，我一直梦想让它完全自动化。过去几年，我一直在为此目标构建工具。连接银行并直接从那里获取数据是我想要实现的目标之一。我构建了此功能，并一直在我的账本中测试了一段时间。现在我的 Beancount 账本有 80% 是完全自动化的。我可以打开我的仓库，银行的 transaction 会自动像这样作为新的 commit 出现，而我无需动手。*

*整个导入系统基于我们的开源 beanhub-import 和 beanhub-extract。导入流程中唯一的专有部分是 Plaid 集成。因此，假设你不信任我，但仍希望自动导入 transaction。只要你连接到 Plaid 并根据从 Plaid 获取的 transaction 编写 CSV 文件，你就应该能够在不使用 BeanHub 服务的情况下拥有相同的自动 transaction 导入系统。*”

博客文章：

> [https://beanhub.io/blog/2024/06/24/introduction-of-beanhub-connect/](https://beanhub.io/blog/2024/06/24/introduction-of-beanhub-connect/)
>
> [https://beanhub.io/blog/2024/04/23/how-beanhub-works-part1-sandboxing/](https://beanhub.io/blog/2024/04/23/how-beanhub-works-part1-sandboxing/)
>
> [https://beanhub.io/blog/2024/06/26/how-beanhub-works-part2-layer-based-git-repos/](https://beanhub.io/blog/2024/06/26/how-beanhub-works-part2-layer-based-git-repos/)

[jmgilman/bdantic](https://github.com/jmgilman/bdantic)：一个用于使用 [pydantic](https://pydantic-docs.helpmanual.io/) 扩展 beancount 的包。使用此包，你可以将你的账本转换为 JSON，等等。

[autobean/refactor](https://github.com/SEIAROTg/autobean/tree/master/autobean/refactor)（Archimedes Smith）：用于以编程方式编辑账本的工具，包括格式化、排序、重构、重新排列 account、通过插件优化、从 v2 迁移、在导入时在账本中插入 transaction 等。

[seltzered/beancolage](https://github.com/seltzered/beancolage)（Vivek Gani）：一个 Eclipse Theia（供应商中立的 vscode）应用，试图打包现有的基于 beancount 的包，例如 vscode-beancount 和 Fava。

[fengkx/beancount-lsp-client](https://github.com/fengkx/beancount-lsp-client) / [Beancount language service - Visual Studio Marketplace](https://marketplace.visualstudio.com/items?itemName=fengkx.beancount-lsp-client)（Vito Leung）：一个 Beancount VSCode 扩展（Language Server），提供语义高亮、补全、诊断、重命名等功能。

[aaronstacy.com/personal-finances-dashboard](http://aaronstacy.com/personal-finances-dashboard/)：用于 Beancount 数据的 HTML + D3.js 可视化 dashboard。

[https://github.com/aleyoscar/beancount-pulsar](https://github.com/aleyoscar/beancount-pulsar)：一个用于 Beancount - Plain Text Accounting 的 Pulsar 包，具有语法高亮、切换注释、某些 directive 的代码片段和自动缩进。Pulsar 包：[https://web.pulsar-edit.dev/packages/beancount-pulsar](https://web.pulsar-edit.dev/packages/beancount-pulsar)

## 移动/手机数据录入<a id="mobilephone-data-entry"></a>

[Beancount Mobile](https://play.google.com/store/apps/details?id=link.beancount.mobile) App（Kirill Goncharov）：一款用于 Beancount 的移动数据录入应用。（目前仅支持 Android。）仓库：[https://github.com/xuhcc/beancount-mobile](https://github.com/xuhcc/beancount-mobile)（[公告](https://groups.google.com/d/msgid/beancount/014e0879-70e0-4cac-b884-82d8004e1b43%40googlegroups.com?utm_medium=email&utm_source=footer)）。

[http://costflow.io](http://costflow.io/)：微信中的纯文本记账。“*向我们在 Telegram、Facebook Messenger、Whatsapp、LINE、微信等平台的机器人发送消息。Costflow 会神奇地将你的消息转换为 Beancount / Ledger / hledger 格式的 transaction。将该 transaction 追加到你 Dropbox / Google Drive 中的文件。借助它们的应用程序，该文件将同步到你的计算机。*”

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
