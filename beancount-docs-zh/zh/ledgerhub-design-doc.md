> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/ledgerhub_design_doc/

# Ledgerhub 设计文档<a id="title"></a>

[Martin Blais](mailto:blais@furius.ca)，2014 年 2 月

[http://furius.ca/beancount/doc/ledgerhub-design-doc](http://furius.ca/beancount/doc/ledgerhub-design-doc)

> [动机](#motivation)
>
> [目标与阶段](#goals-stages)
>
> [阶段详情](#details-of-stages)
>
> [获取](#fetching)
>
> [识别](#identification)
>
> [提取](#extraction)
>
> [转换](#transform)
>
> [渲染](#rendering)
>
> [归档](#filing)
>
> [实现细节](#implementation-details)
>
> [导入器接口](#importers-interface)
>
> [参考文献](#references)

***请注意，本文档是 LedgerHub 的原始设计文档。LedgerHub 正在回归 Beancount。详情请参阅[此事后分析文档](https://docs.google.com/document/d/1Bln8Zo11Cvez2rdEgpnM-oBHC1B6uPC18Qm7ulobolM/) \[blais, 2015-12\]。***

## 动机<a id="motivation"></a>

目前存在多个开源项目，它们提供了从文本文件输入创建复式记账 transaction 的能力。这些复式记账项目包括 [Beancount](http://furius.ca/beancount/)、[Ledger](http://ledger-cli.org/)、[HLedger](http://hledger.org/) 和 [Abandon](https://github.com/hrj/abandon)，它们都是针对相似目标的独立实现：从文本文件创建复式记账 transaction 的内存表示，并从中生成各种 report，例如资产负债表、损益表、日记账等。每个实现探索的功能集略有不同，但本质上都是通过读取文件来工作，该文件的格式是一种自定义的声明式语言，用于描述 transaction。这种语言旨在由人类编写，其语法设计也以此为目标。尽管这些语言在细节上有所不同，但它们定义的基础数据结构相当相似。

定期更新个人日记账文件的一个关键部分，是将真实世界账户的 transaction 详情以一致的数据格式复制到单个输入文件中。这本质上是一个翻译步骤，旨在将众多机构的账户 transaction 详情整合到一个系统中。许多银行和信用卡公司提供可下载的 transaction 数据，格式为 Quicken 或 Microsoft Money (OFX)，许多机构还提供包含 transaction 详情的自定义 CSV 文件。此外，许多机构还提供定期账单供下载，格式为 PDF 文件，这些文件可以与个人的 ledger account 相关联。

将这些外部数据格式进行翻译的过程可以在一定程度上自动化。这些各种文件可以被翻译为输出文本，然后由用户进行整理，以整合到复式记账软件包接受的输入文件格式中。几个项目已经开始在该领域取得进展：[Ledger-autosync](https://pypi.python.org/pypi/ledger-autosync/) 旨在从 OFX 服务器自动获取 transaction 并将其翻译为 Ledger 和 HLedger 的格式，而 [Reckon](https://github.com/cantino/reckon) 则将 CSV 文件转换为 Ledger 格式。[Beancount](http://furius.ca/beancount/) 包含一些代码，可以自动化识别从 ledger 下载的 file 对应的 account，提取其 transaction 详情，并自动将其归档到镜像 ledger 科目表的目录层级中。这些代码可能应该位于 Beancount 之外。[Ledger](http://ledger-cli.org/) 也提供了一个 “convert” 命令，试图做类似的事情，并且有一个 [CSV2Ledger](https://github.com/jwiegley/CSV2Ledger) Perl 脚本可用于转换 CSV 文件。HLedger 也曾有一个 convert 命令，用于翻译 CSV 文件，并支持在单独文件中定义的可选转换提示；HLedger 现在 [在输入文件为 CSV 时即时执行相同的转换](http://hledger.org/manual#csv-files)（即，CSV 被视为一等输入格式）。

获取和转换外部数据文件的程序不必绑定到单一系统。此外，这通常是一段繁琐的代码，如果能有大量贡献者参与，将受益匪浅，因为每个贡献者都可以从为各种机构准备好的通用 parser 中获益，这些机构是他们正在使用或未来可能使用的。我——Beancount 的作者——决定将 Beancount 的导入和归档源代码移出其主项目，并与 Beancount 源代码解耦，以便其他人可以为其做出贡献，旨在提供与项目无关的功能。本文档描述了该项目的目标和设计。

## 目标与阶段<a id="goals-stages"></a>

这个新项目应当以与项目无关的方式解决以下方面：

-   **获取 (Fetching)**：通过直接连接数据源，自动化*获取*外部数据文件。可以利用诸如 [ofxclient](https://github.com/captin411/ofxclient) 等外部工具和库来处理 OFX 源。在可能的情况下，可以使用网络爬虫来获取可下载的文件。此阶段的输出是下载到目录中的一组特定于机构的文件。
    请注意，这里的获取不仅适用于 transaction 数据；我们还将支持获取 *prices*。可以从这些数据中创建 (date, price) 条目的列表。我们可能希望支持一种中间格式，用于表示持仓列表（并在 ledgerhub-Ledger/Beancount/HLedger 接口中提供相应的支持以获取它）。

-   **识别 (Identification)**：给定文件名及其内容，自动*猜测*该文件属于哪个机构以及哪个 account 配置，理想情况下还能从文件或对账单中提取日期。这也应该适用于 PDF 文件。此阶段的输出是将每个输入文件与特定的提取器和配置（例如特定的 account 名称）进行关联。

-   **提取 (Extraction)**：*解析每个文件*（如果可能），并从中提取生成复式记账 transaction 数据结构所需的信息列表，以一种*通用*的数据结构形式，例如字符串和数字的字典，独立于底层项目所需的输出。如果可能，应将与生成该 transaction 的原始文本片段逐字附加到输出数据结构上。此阶段的输出是一个数据结构，例如，以某种定义格式表示的 Python 字典列表。

-   **转换 (Transform)**：给定包含在日志中的过去 transaction 历史中的一些信息，使用简单的学习算法，程序应能够对上一步提取的 transaction 信息应用转换。此过程最常见的用例是为仅有一个 posting 的 transaction 自动添加分类 posting。例如，来自信用卡对账单的 transaction 通常包含信用卡 account 余额的变化，但所有 transaction 都需要手动关联到特定的费用 account。此阶段可以自动化其中一部分流程。

<!-- -->

-   **渲染 (Rendering)**：将内部 transaction 数据结构转换为特定复式记账项目实现的特定语法，以及特定的期望语法变体（例如货币格式、逗号与点作为小数分隔符、本地化输入日期格式）。此步骤输出文本，以便插入到与所选记账软件兼容的输入文件中。

-   **归档 (Filing)**：清理下载文件的文件名，并将它们移动到与识别出的 account 相对应的、组织良好且结构化的目录层级中。这可以基于识别步骤中推导出的相同关联关系来运行。

除了 Render 阶段外，所有其他阶段都应在不考虑特定项目的情况下实现，这应该适用于所有记账实现。然而，Rendering 代码应当进行特化，导入源代码，并尝试将每个项目提供的尽可能多的特定功能添加到其输出文本中。

在必要时，应提供接口以从每个记账实现的输入文件中获取特定的数据集，从而将通用代码与该项目的特定实现细节隔离开来。例如，分类 Transform 步骤需要基于部分 transaction 数据（即 narration 字段，可能还包括一些金额、account 名称和日期）来训练其算法。每个项目都应提供一种方式，以相同的格式从其输入数据文件中获取必要的数据。

## 阶段详情<a id="details-of-stages"></a>

### 获取<a id="fetching"></a>

默认情况下，用户应能够点击导航至其机构的网站，并将文档下载到其 ~/Downloads 目录。包含一些文件的目录应作为识别阶段的合理默认输入。该目录应允许包含其他/垃圾文件，识别步骤应能自动跳过这些文件。

需要实现一个能够自动获取数据的模块。理想情况下，这不应依赖外部工具。提取的数据也应保存一份副本到某个 Downloads 目录中。

这属于 ledger-autosync 项目的领域。也许我们应该在此阶段协调输入/输出，甚至集成调用其部分库代码。作者指出，从 OFX 服务器获取数据相当容易，但开始/结束日期需要进行处理和过滤。

自动获取支持将因机构所在地而异。某些地区支持良好，某些地区则较差。使用 [ofxhome.com](http://ofxhome.com) 的数据进行配置。

#### 获取价格<a id="fetching-prices"></a>

对于获取价格，市面上有许多库。最初，我们将把 Beancount 的 bean-prices 移植到 ledgerhub。

### 识别<a id="identification"></a>

识别阶段包括运行一个驱动程序，该程序执行以下操作：

-   在目录层级中搜索文件（通常是您的 ~/Downloads 文件夹）

-   如有必要，将文件转换为某种文本/ASCII 格式，以便可以对其进行正则表达式匹配（即使输出杂乱无章，例如将 PDF 文件转换为 ASCII）。这对 PDF 文件效果很好：尽管我们通常无法从中提取 transaction 数据，但我们通常可以相当可靠地识别出它们属于哪个 account，并且几乎总能提取出对账单日期。

-   将一组正则表达式与 ASCII 化的内容进行检查。如果所有正则表达式都匹配，则将该配置与文件名关联起来。

请注意，由于某些文件包含许多部分，而不同的 importer 可能被调用来提取这些部分的数据，因此多个配置可能与同一个文件关联（例如，OFX 银行 + OFX 信用卡可以混合在同一个文件中，某些机构确实如此）。

此过程的净结果是将每个文件名与在配置文件中实例化的特定 importer 对象关联起来。这些 importer 对象使用一组必需的 account 名称创建，它们利用这些名称从与其关联的下载文件中生成类似 Ledger 的语法。以下是两个 importer 的示例配置：

from ledgerhub.sources.rbc import rbcinvesting, rbcpdf

CONFIG = \[

...

(('FileType: application/vnd.ms-excel', r'Filename: .\*Activity-123456789-', ),  
rbcinvesting.Importer({  
'FILE' : 'Assets:CA:RBC-Investing:Taxable',  
'cash' : 'Assets:CA:RBC-Investing:Taxable:Cash',  
'positions' : 'Assets:CA:RBC-Investing:Taxable',  
'interest' : 'Income:CA:RBC-Investing:Taxable:Interest',  
'dividend' : 'Income:CA:RBC-Investing:Taxable:Dividends',  
'fees' : 'Expenses:Financial:Fees',  
'commission' : 'Expenses:Financial:Commissions',  
'transfer' : 'Assets:CA:RBC:Checking',  
})),  
  
(('FileType: application/pdf',  
'Filename:.\*/123456789-\\d\\d\\d\\d\[A-Z\]\[a-z\]\[a-z\]\\d\\d-\\d\\d\\d\\d\[A-Z\]\[a-z\]\[a-z\]\\d\\d.pdf'),  
rbcpdf.Importer({  
'FILE': 'Assets:CA:RBC-Investing:RRSP',  
})),

配置由一个列表组成，对于每个可能的 importer，包含一对元素：1) 一组正则表达式，它们都应该与“匹配文本”匹配，该“匹配文本”是待导入文件内容的“文本化”版本；以及 2) 一个 importer 对象，该对象配置了用于生成 transaction 的一组特定 account。每个 importer 都需要一组特定的输出 account，它使用这些 account 来创建其 transaction 和 posting。Ledger 的文件名以及这些 (regexps, importer) 对的列表，是驱动程序完成其所有工作所需的全部信息。

文本化是指将二进制格式的下载文件简单且不完美地转换为我们可以对其运行正则表达式的形式。对于 OFX 文件或 CSV 文件，文本化不需要转换，我们只需直接匹配这些文件的文本内容即可；对于 Excel/XLS 文件，我们需要将其转换为 CSV 文件，然后才能进行搜索；对于 PDF 文件，会尝试多种不同的 PDF 转文本转换器，直到其中一个成功为止（用于此目的的工具以不可靠著称，因此我们必须尝试各种工具）。请注意，这种转换后的“匹配文本”只是临时创建的，仅用于识别目的；importer 将获取原始二进制文件来执行其工作。

尚不完全清楚是否可以标准化正则表达式，以避免用户手动配置它们。在实践中，我发现通常有必要，或者至少非常方便，在我的导入配置中放置一个 account ID。诚然，配置每种可能的下载可能是一件麻烦事，需要用户在查看每个文件的内容时进行一些猜测，但在实践中，这比尝试规范化此过程要可靠得多，可能是因为唯一区分特定用户的所有文件比区分所有类型的文件要容易得多。在其中一个正则表达式中使用 account ID 是做到这一点的简单方法，并且效果很好。这也提供了一个清晰的位置，将 account 列表附加到特定的 importer，而这本来就需要用户输入。

### 提取 <a id="extraction"></a>

一旦建立关联，我们就会对每个文件运行 importer。这会生成某种数据结构。每个 importer 各司其职——那些丑陋的技巧就在这里。理想情况下，我们应该构建一个通用工具库，以协助解析相似类型的文件。

尽管每个 importer 模块应当基本上相互独立，但可以设想一些通用功能，例如，如何处理单个 investment 账户中持有的不同股票，可以在每个 importer 之外进行配置（例如，首选方法可以是创建该账户的一个 subaccount，并以股票的 symbol 命名，或者采用其他方式）。

注意 \[AMaffei\]：如果你希望将各个步骤作为独立的 UNIX 风格工具运行，和/或使用常规文本处理工具处理中间文件，那么可以输出一种通用且定义明确的 CSV 文件格式。

### 转换 <a id="transform"></a>

某些转换应当独立于 importer。特别是，自动对不完整的 transaction 进行分类，并不依赖于创建该 transaction 的 importer。我希望将此步骤保持尽可能通用，以便未来可以在此处插入其他修饰步骤。目前，我只能想到以下用途：

1.  对仅包含单个 posting 的 transaction 进行自动分类

2.  检测重复的 transaction：导入的文件中经常包含已经存在于 ledger 中的 transaction；这些 transaction 应当被忽略或标记为重复。实际上，这并不像听起来那么简单，因为简单的日期 + narration 比较会失败：如果同一笔 transaction 来自两个输入数据文件，其中一侧总是会被合并到另一侧，有时甚至日期也会有细微差异。需要一定程度的模糊匹配。

3.  规范化 payee 名称：导入的 payee 名称经常被截断或包含一些无关的词语，例如 “LLC”、城市名称和/或数字代码。可能希望以某种方式自动清理这些内容。

此步骤涉及一个引导阶段，我们将从中提取一些数据，这些数据来自 transaction 旨在导入的实际 ledger。我们将实现一个通用接口，允许每种 ledger 语言实现提供用于训练的相关数据。

此处的输出数据格式应与其输入格式相同，以便我们可以选择跳过此阶段。

### 渲染<a id="rendering"></a>

输出渲染器应由驱动程序选择。在此处，我们将提取的数据结构转换为您所使用的特定 ledger 实现风格。每个渲染器实现都应可以自由地导入其特定实现中的模块，并且我们应谨慎地将这些导入依赖限制为仅这些模块，以确保代码运行只需要单一的 ledger 实现。

渲染风格的选项可以在此处为每个渲染器定义，因为每种语言都有其特殊性。

\[AMaffei\] 此外，应该能够提供一个通用渲染器，它接受 printf 风格的格式字符串，以输出任何所需的格式。

### 归档 <a id="filing"></a>

Importer 应当能够查看文件的文本化内容，并从中找到文件/对账单日期。这非常有用，因为我们可以通过对账单日期作为前缀来重命名文件，而我们下载对账单或 transaction 文件的日期很少与其生成日期相同。如果无法从文件中提取日期，我们将回退到使用文件名的最后修改时间。

应提供一个目标目录，并且我们应将每个文件移动到与其关联的 account 中。例如，像这样的文件：

    ~/Downloads/ofx32755.qbo

如果通过识别步骤与 Assets:US:RBC:Checking account 的 importer 关联，则应被移动到如下目录：

    .../Assets/US/RBC/Checking/2013-11-27.ofx32755.qbo

为此，所有 importer 都应关联一个必需的“filing” account。

据我所知，目前只有 Beancount 实现了这一功能，但我怀疑这种组织和保留导入文件的便捷机制也会被其他人发现其价值。给定一个目录列表，Beancount 会自动找到这些文件，并利用文件名中的日期，能够在 journal 网页中将文件渲染为行项目的链接，并在用户点击链接时提供其内容。即使没有此功能，它也可以用于维护文档的缓存（我将我的文档维护在一个仓库中，并同步到外部驱动器进行备份）。

## 实现细节<a id="implementation-details"></a>

关于初始实现的说明：

-   本项目的实现将使用 Python3 进行。为什么选择 Python？

    -   导入和提取的性能在很大程度上无关紧要，动态语言非常适合此类任务

    -   在动态语言中进行解析效果极佳，且有许多可用的库

    -   Python3 目前分布广泛，且目前所有所需的解析库通常都可用于它

-   所有模块都应进行测试，包括使用示例输入进行测试。如果你想添加一个新模块，你需要为其提供一个匿名化的示例文件。我们将必须拥有一个自动化测试套件，因为过去的经验表明，这类代码对于新的和意外的输入非常脆弱和易碎。它很容易编写，但也很容易出错。

    -   为了测试无法匿名化的二进制文件，我们将提供从匹配文本而非原始二进制对账单 PDF 进行测试的能力。这些文件通常无论如何都无法提取，它们仅用于识别和归档（例如，PDF 对账单，我们除了可能对账单日期外，无法从中提取任何有意义的数据）。

-   应该有一种快速的方法，可以在零配置的情况下，使用特定的下载文件测试特定的 importer，即使输出的 account 名称有点奇怪。

-   需要为 importer 正在执行的操作提供清晰且可读的跟踪，包括调试/详细选项。

-   我们提供一个单一函数作为你自己导入脚本的驱动程序。你的配置是一个脚本 / 你的脚本就是配置。你在最后调用一个函数。我们还将提供一个脚本，用于导入文件名并从中获取属性，供那些希望使用更传统调用方式的人使用。

-   我们应该保持类型简单，但使用标准的 datetime 类型表示日期，decimal.Decimal 表示数字，字符串表示货币/商品。

这显然基于我在 Beancount 中当前的 importer 代码。我非常欢迎针对此项目的新想法和建议。合作将受到最热烈的欢迎。我们能支持的 importer 越多越好。

## importer 接口 <a id="importers-interface"></a>

每个 importer 都应实现为一个继承自以下类的类：

class ImporterBase:  
"所有 source importers 的基类/接口。"  
  
\# 必需配置变量到其 docstring 的字典。  
\# 这声明了 importer 需要提供的选项列表及其含义。  
**REQUIRED\_CONFIG** = {}  
  
def \_\_init\_\_(self, config):  
"""创建一个 importer。  
大多数具体实现可以直接使用此方法而无需重写。  
  
Args:  
config: 一个配置 accounts 的字典，必须与  
REQUIRED\_CONFIG 的值匹配。  
"""  
\# 一个 Configuration 值的字典。这可以公开访问。  
assert isinstance(config, dict)  
self.config = config  
  
\# 检查 config 是否仅包含所需的配置值。  
if not verify\_config(self, config, self.REQUIRED\_CONFIG):  
raise ValueError("Invalid config {}, requires {}".format(  
config, self.REQUIRED\_CONFIG))  
  
def get\_filing\_account(self):  
"""返回用于移动输入文件的 account。  
  
Returns:  
与此 importer 对应的 account 名称。  
"""  
return self.config\['FILE'\]  
  
def **import\_file**(self, filename):  
"""尝试导入一个文件。  
  
Args:  
filename: 要导入的文件名。  
Returns:  
从文件中提取的新导入 entries 列表。  
"""  
raise NotImplementedError  
  
def **import\_date**(self, filename, text\_contents):  
"""尝试获取与给定文件对应的日期。  
  
Args:  
filename: 要从中提取日期的文件名  
text\_contents: 文件内容的 ASCII 文本版本，  
无论其原始格式如何。  
Returns:  
如果成功，则返回一个 date 对象，否则返回 None。  
"""  
raise NotImplementedError

对于每个 importer，应提供关于如何在机构网站上找到并下载原始输入文件的详细说明，以帮助那些在添加此 importer 时找到正确的下载（某些机构提供多种下载格式）。此外，应提供一行关于输入文件支持的描述，以便我们可以在运行时渲染支持的文件类型列表。

## 参考资料<a id="references"></a>

以下列出了其他旨在将账户数据导入 Ledger 的项目。

-   [Ledger 的 “convert” 命令](http://ledger-cli.org/3.0/doc/ledger3.html#The-convert-command)

-   HLedger 及其 [内置](http://hledger.org/manual#csv-files) [读取器](http://hledger.org/manual#timelog-files)

-   Reckon

-   [OFXmate](https://github.com/captin411/ofxmate)（ledger-autosync 的 GUI）

-   [CSV2Ledger](https://github.com/jwiegley/CSV2Ledger)

-   [icsv2ledger](https://github.com/quentinsf/icsv2ledger)

-   [csv2ledger](http://www.khjk.org/log/2009/oct/csv2ledger.hs)（似乎缺乏活跃的维护者）

更新（2015 年 11 月）：本设计文档已实现，该项目正在回归 Beancount。详情见[此处](https://docs.google.com/document/d/1Bln8Zo11Cvez2rdEgpnM-oBHC1B6uPC18Qm7ulobolM/)。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
