> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/beangulp_design_doc_for_new_repo/

# Beangulp 新仓库设计文档<a id="title"></a>

[Martin Blais](mailto:blais@furius.ca)，2021 年 1 月

为 Beancount 导入数据的功能最初由 LedgerHub 项目提供支持，并附带一个导入器库；随后，该功能被重新整合为 Beancount 仓库中一个纯框架库（附带一些示例），即 beancount.ingest。现在，我们将再次拆分该仓库，并将导入框架提取到另一个仓库中，以便于维护和演进。本文档概述了此新版本中期望进行的一些更改。

## 新仓库<a id="new-repo"></a>

新仓库将位于

> [http://github.com/beancount/beangulp](http://github.com/beancount/beangulp)

Beangulp 将仅针对 v3 分支的最新 beancount 发布版本保持兼容。

Beancount v3 在初期预计会快速演进，因此，为了减轻早期采用者的痛苦，应谨慎使用版本号递增和版本化依赖。理想情况下，Beangulp 应仅依赖于 Beancount 的当前次要版本，例如，如果发布了 Beancount 3.0.0，Beangulp 应声明

    install_requires: beancount >3.0, <3.1

参见 [setuptools 文档](https://setuptools.readthedocs.io/en/latest/userguide/dependency_management.html#declaring-required-dependency) 和 [PEP-440](https://www.python.org/dev/peps/pep-0440/#version-specifiers)。

## 状态<a id="status"></a>

截至 2022 年 1 月，本提案的大部分内容已完成并实现。（感谢 Daniele Nicolodi 完成了大部分工作。）

## 变更<a id="changes"></a>

### 仅作为库使用<a id="library-only"></a>

当前实现允许用户：

1.  在“配置文件”上使用 bean-identify、bean-extract 和 bean-file 工具，该配置文件是求值的 Python 代码；或者
2.  创建一个脚本，并调用一个单一端点来实现子命令。

为了使这得以实现，使用了一个极其复杂的蹦床（trampoline）机制，将求值弹回相同的代码。我承认，即使是我这个编写者，每次需要进入其中编辑该代码时，都会觉得它令人望而却步。此外，这也使得让用户在其导入过程中添加自定义的前置/后置定制变得不方便。

下一个版本将仅支持方式 (2)。bean-identify、bean-extract 和 bean-file 程序都将被移除。用户将被期望编写自己的脚本。

### 单文件<a id="one-file"></a>

目前，每个 importer 由两个文件组成：实现文件和相关的测试文件，例如：

    soandso_bank.py
    soandso_bank_test.py

测试文件很小，通常调用库函数来查找模型文件和预期输出。由于几乎没有实际的测试代码，我们希望能够使用单个 Python 文件来包含其测试调用。

将添加一个新的 endpoint，用于在 importer 实现中定义测试。

### 自运行<a id="self-running"></a>

此外，该新函数应当与用于组装配置脚本的函数相同。换言之，importer 的 main() 函数应等效于调用一个仅包含单个已配置 importer 的实例，且该实例使用的是测试所用的配置。

这将允许用户无需定义配置，直接使用测试配置，针对特定的一组文件“运行 importer”，例如：

    soandso_bank.py extract ~/Downloads/transactions.csv

拥有此选项使得人们可以非常方便地分享单个文件并立即进行测试，而无需创建配置或主程序。

我认为，除了像下面这样在 importer 定义文件中包含类似内容外，没有简单且干净的方式来实现这一点：

`if __name__ == ‘__main__’:`

        	    main = Ingest([SoAndSoBankImporter()])
        	    main()

这在当前无需任何更改即可正常工作。不过，目前的情况往往是 importer 需要一些配置才能工作（我不确定，因为我并不使用 Beancount 分发的或广泛使用的任何 importer）。

### **Test** 子命令与 **Generate**<a id="test-subcommand-generate"></a>

由于 importer 是可执行的，并且定义了供 pytest 运行的测试用例，我们还应添加一个 "test" 子命令，以完善 "identify"、"extract" 和 "file"。该位置也是替换 --generate 选项的理想场所，因为该选项需要丑陋地注入 pytestconfig；相反，我们可以自行实现它，并添加第二个子命令 "genexpect" 来生成用于测试的期望文件。

接口变为：

    soandso_bank.py identify ~/Downloads/
    soandso_bank.py extract ~/Downloads/
    soandso_bank.py file ~/Downloads/ ~/documents
    soandso_bank.py test ~/documents/testdocs
    soandso_bank.py generate ~/Downloads/transactions.csv

这样，我们就可以移除 pytestconfig 的依赖注入，并简化单元测试的逻辑，因为单元测试原本必须同时处理 check 和 generate 两种场景。这应该能带来更简洁的代码。

### 单一预期文件<a id="one-expected-file"></a>

导入器的预期输出存储在多个文件中，后缀分别为 .extract、.file\_name、.file\_date 等。如果我们将所有输出放在一个文件中，"genexpect" 子命令就可以将所有内容生成到 stdout。这样非常方便。

> myimporter.py
>
> myimporter.beancount

利用 Beancount 语法来存储 "file\_name()"、"file\_date()" 及其他输出的预期值。将这些值存储在 Event 或 Custom directive 中，并让测试代码对其进行断言。新的测试目录内容应简化为成对的 (a) 原始下载文件和 (b) 预期输出，其中不仅包含 transaction，还包含所有其他方法的输出。

### 重复项识别<a id="duplicates-identification"></a>

这功能从未真正正常工作过。我认为，如果基于每个 importer 单独实现此功能——换句话说，让每个 importer 定义如何识别重复项，例如，假设可以插入一个唯一的 transaction ID 作为 link 以消除歧义——我们可以更干净地实现这一点。

理想情况下，每个 importer 都能在 importer 内部指定重复 ID 检测。它可以调用一种更通用但可靠性较低的方法，而该代码应位于 Beangulp 中。

### CSV 工具<a id="csv-utils"></a>

我拥有许多非常便捷的实用工具，用于从丑陋的 CSV 下载文件中切片和处理数据。CSV 下载文件通常用于承载多个表格和不同类型的数据，因此往往需要对这些文件进行更高层次的处理。

我到处都有类似的代码。这值得拥有一个漂亮的库。更重要的是，我在 Baskets 项目下有一个不错的表格处理库，但它尚未得到适当的质量处理。

清理我的小表格库，并将其与所有 CSV 工具合并。将其放入 beangulp，甚至可以考虑将其作为独立项目，包括一个 CSV 导入器。“CSV 世界。”

*在发现 petl 之后，不确定这是否还那么重要。我们可以依赖 petl。*

### 缓存<a id="caching"></a>

在对大文件运行转换任务时，最好能有一个缓存，以避免重复执行。可以将（较小的）转换后数据缓存起来并重新加载，从而避免多次运行昂贵的转换过程。一个难点在于，需要运行的转换取决于 importers 的配置，而每个 importer 对其他 importer 一无所知。

所有命令行参数以及至少文件内容的头部都应被纳入哈希计算。这个库可以相当独立于 Beancount。

### API 变更<a id="api-changes"></a>

-   "file\_date()" 不够清晰；"get\_filing\_date()" 会更好。

-   extract() 的额外参数与其他所有方法相比显得不规整。能否找到更好的方式？

-   我不完全确定是否喜欢我那个带缓存的小文件包装器（"cache"）。将其替换为仅基于磁盘的实现。

### 自动插入<a id="automatic-insertion"></a>

新代码应具备的一个非常便捷且易于构建的功能是，将提取的输出自动插入到现有账本中，插入位置为文件中某个特殊字符串标记之前。将此功能作为库的一部分，作为存储导入器输出的替代方案，例如：

`$ ./myimport.py extract | bean-insert ledger.beancount Amex`

这也可以作为 "extract" 的一个标志

`$ ./myimport.py extract -f ledger.beancount -F Amex`

## 用户评论<a id="user-comments"></a>

-   Red S: [https://github.com/redstreet/beancount\_reds\_importers/blob/master/beancount\_reds\_importers/libimport/csv\_multitable\_reader.py](https://github.com/redstreet/beancount_reds_importers/blob/master/beancount_reds_importers/libimport/csv_multitable_reader.py) - 一个我实际在用的、功能完备但较为基础的 csv 和 xlsx 多表格读取器。

-   Huruka Momo:

> 是否可以将 find\_duplicate\_entries 分离为一个对象，例如 Comparator？
>
> 如前所述，账单文件可能有各种类型，且每个金融机构提供的账单也需要使用不同的解析规则。
>
> 通过解析获得的原始 transaction 记录（以下简称 OriTxns）应当被标准化（包含导入 beans 所需的必填字段）并具备可扩展性。然后，OriTxns 可以由 Comparator 进行处理，并设置各种 flags 和补充信息。例如，与现有的 bean txns 进行比较并标记重复项，或者与另一份账单进行比较以补充信息，然后再与现有的 bean txns 进行比较。为了实现 Comparator，用户可以选择他们喜欢的方法。例如，我选择使用 Pandas 进行比较。
>
> 相应的费用分类可以在这一步骤中一起完成，或者由一个 classifier 对象执行？因为我在 Github 上看到有人使用机器学习来处理它。
>
> 但在这里，我还没有弄清楚解析后的 OriTxns 应该使用什么通用数据格式。现在我使用 Pandas DataFrame，但这显然不是通用的。
>
> 处理后的 OriTxns 可以传递给 Importer，然后由 Importer 导入到 Beancount 中。它可以相对简单，因为像 account 关联这样的信息已经预先知晓，并且 Headers 和数据都是整齐干净的。必要的数据默认被导入，用户可以告诉 Importer 指定哪些列的数据应以 Tag、Link 或 MetaData 的形式导入到 Beancount 中。
>
> 编辑：哦，我在查看源代码后发现已经有一个 comparator 了。名字 similar 真的不够直观，而 Comparator 又有点深奥。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
