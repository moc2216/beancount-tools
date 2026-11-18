> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/beancount_v3_dependencies/

# Beancount C++ 版本：依赖项<a id="title"></a>

[Martin Blais](mailto:blais@furius.ca)，2020 年 6 月

Beancount 将使用 C++ 重写，以下是我测试过并愿意长期维护的依赖项集合：

## 基础环境<a id="base-environment"></a>

-   [**Bazel 构建**](https://bazel.build/) ([https://github.com/bazelbuild/bazel](https://github.com/bazelbuild/bazel)): Google 的构建系统是我所知的最稳定的构建方法，远优于 SCons，也绝对远优于 CMake。它允许通过显式引用其他仓库以及特定提交版本（包括未发布的版本）的 git 仓库，来固定一组特定的依赖项。它有时强加的繁琐约束，使得构建具有其他构建系统无法实现的完全可复现性（hermetically reproducible builds）。这最大限度地减少了意外情况，并有望减少平台相关的可移植性问题。它还最小化了我们对系统预装软件包的假设（例如，它会自行下载并编译自己的 Bison）。它运行速度快，能够计算需要重新构建的最小测试和目标集合，并且高度可配置。

> 选择 Bazel 的缺点与其他 Google 发布的开源项目相同：该产品的原始版本是内部使用的，因此存在许多需要处理的奇怪怪癖（例如 //external、@bazel\_tools 仓库等），其中许多在公司外部文档记录不佳，且存在大量未解决的工单。然而，到目前为止，我已经成功[创建了一个可用的构建](https://github.com/beancount/beancount/tree/bazel)，涵盖了本节中描述的大多数依赖项。

-   **[C++14](https://en.wikipedia.org/wiki/C%2B%2B14)，配合 [GCC](https://gcc.gnu.org/) 和 [Clang/LLVM](https://clang.llvm.org/)**: 将同时支持这两种编译器。Clang 提供了更好的前端和标准库实现，但构建速度稍慢。GCC 在野外更为常见，但其错误信息……嗯，我想我们都已经习惯了。请注意，尽管要求使用 C++14，我将避免使用该语言中过于奇特的特性（包括类）。关于 Windows 支持可能还会有疑问。

-   [**Abseil-Cpp 基础库**](https://abseil.io/) ([https://github.com/abseil/abseil-cpp](https://github.com/abseil/abseil-cpp)): 这个函数基础库源自 Google 庞大的内部代码库，经过实战考验和测试，无出其右——Google 的产品就是运行在其上的。它提供了最稳定的 API 供开发使用（鉴于有如此多的代码依赖于它，它不太可能发生大的变化），很好地补充了 stdc++，并且其现有的接触面注定会保持相当静态。它比 Boost 更简单、更稳定，并且不提供我们反正不需要的众多库（此外，我喜欢 [Titus'](https://github.com/tituswinters) 对 C++ 的方法）。它填补了许多在 Python 中免费获得但在 C++ 中令人渴望的基本字符串操作函数（例如 absl::StrCat）。

-   **[Google Test](https://en.wikipedia.org/wiki/Google_Test)** ([https://github.com/google/googletest](https://github.com/google/googletest)): 这是我已经熟悉的广泛使用的 C++ 测试框架，支持匹配器（matchers）和模拟（mocking）。

## 数据表示<a id="data-representation"></a>

-   [**Protocol Buffers**](https://developers.google.com/protocol-buffers) ([https://github.com/protocolbuffers/protobuf](https://github.com/protocolbuffers/protobuf)): 在这次 C++ 重写中，我将保持函数式风格，并且需要一个替代 Python 中 nametuples 的机制来表示 directive。这意味着需要创建大量简单的裸结构化数据，这些数据需要在测试中动态创建（有一个很好的文本格式解析器），并且需要序列化到磁盘，因为核心与查询语言之间的边界将变成一个 protobuf 消息文件。Protobuf 提供了一种带有重复字段的良好层次化数据结构，并且受多种语言支持（这有可能为用例如 Go 编写的插件打开大门），并且可以为它们提供 Python 绑定。
    它还将成为 Beancount 核心与查询语言输入之间的接口。我们将使用 proto3，版本 &gt;=3.12，以支持 [optional presence fields](https://www.google.com/url?q=https://github.com/protocolbuffers/protobuf/blob/master/docs/field_presence.md&sa=D&ust=1593922864811000&usg=AFQjCNH4AQawCGimgvXDz1vOL3CVzTyuZQ)（空值）。

-   [**Riegeli** (https://github.com/google/riegeli)](https://github.com/google/riegeli): 一种高效且压缩的二进制格式，用于将 protobuf 消息序列存储到文件中。我认为 Beancount 核心将输出此格式；它紧凑且读取速度快。它也是另一个 Google 项目，理应受到比目前更多的关注，并且支持 C++、Python 和 protobufs。

-   [**mpdecimal**](https://www.bytereef.org/mpdecimal/) ([https://www.bytereef.org/mpdecimal/](https://www.bytereef.org/mpdecimal/))**:** 这是 Python 的 Decimal 数字实现所使用的同一个 C 级库。使用此库将允许在 C++ 核心和 Python 运行时之间轻松操作。我需要在 C++ 内存中表示十进制数，功能最小化，范围合理较小（BigNum 类通常超出了我们的需求）。我们不需要太多的十进制范围……主要是基本算术运算 + quantizing。
    还有其他库可用：[GMP](https://gmplib.org/)、[decNumber](http://speleotrove.com/decimal/decnumber.html)*.* 在这个线程中有一些相关信息：([https://stackoverflow.com/questions/14096026/c-decimal-data-types](https://stackoverflow.com/questions/14096026/c-decimal-data-types)。对于磁盘上的表示，我需要为这些定义一个 protobuf 消息定义，我正在考虑定义一个字符串（易于阅读，但从字符串到十进制的转换很多）与更高效的指数 + 尾数十进制等效项的联合。

## parser <a id="parser"></a>

-   **[RE/flex lexer](https://www.genivia.com/doc/reflex/html/)** ([https://github.com/Genivia/RE-flex](https://github.com/Genivia/RE-flex)): 这款基于现代正则表达式的扫描器生成器原生支持 Unicode，速度极快且文档完善。它为日渐老化的 GNU flex 提供了一个极佳的替代方案，后者在字符串字面量之外（例如，对于 account 名称）难以支持非 ASCII 字符。我在其他项目中使用它取得了成功。许多用户希望使用母语作为 account 名称；这将使得为整个文件提供 UTF-8 parser 变得轻而易举。

-   **[GNU Bison](https://www.gnu.org/software/bison/)** ([https://git.savannah.gnu.org/git/bison.git](https://git.savannah.gnu.org/git/bison.git)): 我们将继续使用 GNU Bison，但转而使用其支持的 C++ 完整模式。我对于继续使用该 parser 生成器持犹豫态度，因为它已显出老态，但它相当稳定，且我尚无法证明升级到 ANTLR 所付出的额外工作是值得的。  
    为了支持相同的 grammar 以生成 v2 的 C 代码和下一版本的 C++ 代码，我们将不得不采用一些技巧；parser 代码可以提供一个函数分派表，在 v2 中这些是静态 C 函数，而在 C++ 版本中则是方法。一些生成参数（% directives）将有所不同（参见[此处](https://github.com/blais/oblique/blob/master/oblique/parser.yxx#L8)以获取示例）。

-   [I**nternational Components for Unicode (ICU)**](http://site.icu-project.org/home) ([https://github.com/unicode-org/icu.git](https://github.com/unicode-org/icu.git)): 这是用于 Unicode 支持的标准依赖库。我们的 C++ 代码将不使用 std::wstring/std::wchar，而是使用常规的 std::string，并在必要时调用此库的函数。

## Python（运行时） <a id="python"></a>

-   [**Python3** (https://www.python.org/)](https://www.python.org/): 没什么好说的。我会继续使用最新版本。Python 是一种极其强大的扩展语言，我没有任何改变这一点的计划。

-   **[pybind11](https://pybind11.readthedocs.io/en/stable/)** ([https://github.com/pybind/pybind11](https://github.com/pybind/pybind11)): 我希望提供一个与当前 Beancount 中几乎完全相同（或更好，即更简单）的 Python API。我的一项要求是，在 C++ 和 Python 之间传递用于 directives 的 protobuf 对象列表给 Python 回调时，成本要低，且无需复制（即在 C++ 和 Python 之间进行序列化和反序列化）——这对于插件尤为重要。我调研了多个用于 Python 和 C++ 互操作的库：Cython、CLIF、SWIG 等，但序列化一直是个问题（参见[这个部分解决方案](https://github.com/google/nucleus/blob/master/nucleus/util/proto_ptr.h)）。目前势头最猛的是 pybind11，它是一个纯头文件库，是 Boost::Python 的演进版本，提供了对生成 API 的最大控制权。它与使用 fast\_cpp\_protos 构建的 protocol buffer 目标配合得也很好：只传递指针，因此插件传入和传出完整的 directives 列表应该是可行的。我恰好对 Boost::Python 也很熟悉，因为我在 20 年前使用过它，实际上它们非常相似（只是去掉了 Boost 的其他部分）。

-   **[Type annotations](https://docs.python.org/3/library/typing.html), [PyType](https://github.com/google/pytype)** (或 [MyPy](http://mypy-lang.org/)?)：我此前已经遵守了针对 Python 的自定义 PyLint 配置，但代码库并未使用日益普及的[type annotations](https://docs.python.org/3/library/typing.html)。在重写后保留的代码子集中，我希望为所有函数添加注解，并用更自由的文档形式取代有时显得冗余的 Args/Returns docstring（类型注解可能足以避免 Args/Returns 块的正式性）。我将不得不看看这对[自动生成的文档](https://github.com/beancount/docs)有何影响。  
    一个重要的补充是，我希望开始不仅进行注解，还要在构建过程中自动运行其中一个类型检查器。我已经熟悉 Google 的 pytype，但 mypy 可能是一个不错的替代方案。无论如何，唯一的障碍是制定 Bazel 规则，以便在整个代码库中自动调用这些工具，作为 py\_library() 和 py\_binary() 规则的一部分。我还将尝试以同样的方式（作为构建的一部分）运行 pylint，并添加一个自定义标志以便在开发期间禁用它，而不是拥有一个单独的 lint 目标。

-   **Subpar** ([https://github.com/google/subpar](https://github.com/google/subpar)): 我目前还不清楚如何为 Bazel 构建执行 pip 兼容的 setup.py[^1]，但我们肯定能找到一种方法，使用 Bazel 构建的二进制文件来构建用于 PyPI 的 wheels。对于打包自包含的 Python + 扩展二进制文件，"subpar" Bazel 规则应该能处理这一点。然而，[目前它不支持 C 扩展](https://github.com/google/subpar/issues/59)。  
    Filip Filmar 报告：我使用类似的方法，利用 \`shar\` 将任何内容打包成自解压归档。这是一个以这种方式打包的非平凡二进制文件的示例：https://github.com/filmil/bazel\_rules\_fusesoc\_2/blob/main/extensions/fusesoc\_repo.bzl\#L22 在运行之前需要修复 PYTHONPATH，但它确实有效。

[^1]: (Filip Filmar): 你可能不需要这样做。我想出了一种方法，让 bazel 在构建中调用 docker 容器，因此你可以预先准备一个环境，然后在构建时使用它来调用二进制文件。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
