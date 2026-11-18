> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/installing_beancount/

# 安装 Beancount<a id="title"></a>

[Martin Blais](mailto:blais@furius.ca) - 更新日期：2024 年 11 月

[http://furius.ca/beancount/doc/install](http://furius.ca/beancount/doc/install)

*在你的计算机上下载和安装 Beancount 的说明。*

## 版本发布<a id="releases"></a>

Beancount 是一个成熟的项目：其第一个版本编写于 2008 年。Beancount 的当前版本——分支 "v3"——是稳定的，并持续接受维护和开发。有一个 [邮件列表](https://groups.google.com/forum/#!forum/beancount) 和一个 [PyPI](https://pypi.python.org/pypi/beancount) 页面。"master" 分支是开发分支。

（注意：如果您过去使用过 "v2" 分支，许多工具已从分支 "v3" 中移除，并迁移到 [http://github.com/beancount](http://github.com/beancount) 下的各自独立的 github 项目中。一些工具，例如 bean-report、bean-web，已被弃用。）

## 获取方式<a id="where-to-get-it"></a>

这是源代码的官方位置：

> [https://github.com/beancount/beancount](https://github.com/beancount/beancount)

使用 Git 在您的机器上克隆仓库，如下所示：

    git clone https://github.com/beancount/beancount

## 如何安装<a id="how-to-install"></a>

### 安装 Python<a id="installing-python"></a>

Beancount 使用 Python 3.8 或更高版本，这是相当新的 Python 版本（截至本文撰写时），并且需要一些常见的库依赖项。我尽量将依赖项减到最少，但你确实需要安装几个。这非常简单。

首先，你应该有一个可用的 Python 安装。使用从 [python.org](http://python.org) 下载的最新稳定版本（>=3.8）进行安装。确保你也安装了开发头文件和库（例如，“Python.h” 头文件）。例如，在 Debian/Ubuntu 系统上，你需要安装 **`python3-dev`** 软件包。

Beancount 自 2016 年 2 月起支持 setuptools，你需要安装依赖项。你需要安装 “pip3” 工具。如今，它通常随 Python3 默认安装——通过运行 “python3 -m pip --help” 命令来测试这一点。

### 安装 Beancount<a id="installing-beancount"></a>

#### 使用 uv 安装 Beancount<a id="installing-beancount-using-uv"></a>

在 2026 年，运行 beancount 最简单的方式是通过 uv，例如：

    uvx --from beancount <command>

有关更多详细信息，请参阅 uv 手册。

#### 使用 pipx 安装 Beancount<a id="installing-beancount-using-pipx"></a>

如果你还没有安装，请先[安装 pipx](https://github.com/pypa/pipx)。

接下来，使用 pipx 安装 Beancount。这应该会自动下载并在虚拟环境中安装所有依赖项。

    pipx install beancount

确认 Beancount 已安装。

    pipx list

从版本 3.1.0 开始，这将安装

-   bean-check

-   bean-doctor

-   bean-example

-   bean-format

-   treeify

（没有 bean-report，尽管教程中引用了它。它已被弃用。）

#### 使用 pip 安装 Beancount<a id="installing-beancount-using-pip"></a>

不再建议使用 pip 安装 Beancount，但你仍可以使用以下命令安装 Beancount：

    sudo -H python3 -m pip install beancount

这应该会自动下载并安装所有依赖项。

但请注意，这将安装推送到[PyPI 仓库](https://pypi.python.org/pypi/beancount/)的最新版本，而不是从源代码获取的最新版本。向 PyPI 发布版本是不定期的，但频率足够高，不会落后太多。

**警告：请谨慎操作，这可能会破坏系统库。**

#### 使用 pip 从仓库安装 Beancount<a id="installing-beancount-using-pip-from-the-repository"></a>

你也可以使用 pip 直接从其源代码仓库安装 Beancount：

    sudo -H python3 -m pip install git+https://github.com/beancount/beancount#egg=beancount

#### 从源代码安装 Beancount<a id="installing-beancount-from-source"></a>

从源代码安装的优势在于，它为你提供稳定分支（“master”）的最新版本。大多数时候，master 分支应该与发布版本一样稳定。

从官方仓库获取源代码：

    git clone https://github.com/beancount/beancount

你可能需要安装一些非 Python 库依赖项，例如 bison 和 flex，也许还有更多（当你尝试构建时你会发现）。缺什么应该很明显。如果在 Ubuntu 上，请使用 apt get 安装它们。

如果在 Windows 上安装，请参阅下面的 Windows 部分。

##### 使用 pip3 从源代码构建和安装 Beancount<a id="build-and-install-beancount-from-source-using-pip3"></a>

然后，你可以使用 pip 安装所有依赖项和 Beancount 本身：

    sudo -H python3 -m pip install .

##### 用于开发的安装<a id="installing-for-development"></a>

如果你想就地编译和执行源代码以对其进行修改，可以这样做：

    make build

为此，你需要安装 "meson" 和 "ninja"。需要更新 PATH 和 PYTHONPATH 环境变量，以在本地获取导入和二进制文件，如下所示：

    export PATH=$PATH:/path/to/beancount/bin
    export PYTHONPATH=$PYTHONPATH:/path/to/beancount

###### 开发依赖项<a id="dependencies-for-development"></a>

Beancount 开发需要一些额外的工具。如果你正在阅读这部分内容，说明你是一名开发者，所以我假设你知道如何安装包，跳过细节，只列出你可能需要的内容：

-   pytest：用于单元测试

-   meson, meson-python, ninja：用于构建（在 master 分支上）

-   ruff：用于代码检查

-   [**GNU flex**](https://www.gnu.org/software/flex/)：如果你打算修改词法分析器，则需要此词法分析器生成器。它生成 C 代码，将输入文件切分为 token，供解析器使用。

-   [**GNU bison**](http://www.gnu.org/software/bison/)：如果你打算修改语法，则需要此传统解析器生成器。它生成 C 代码，解析由 flex 生成的 token。（我喜欢使用像这样的旧工具，因为它们的依赖项很少，只是 C 代码。它应该在任何地方都能工作。）\`

-   python-dateutil：用于运行 beancount.scripts.example 示例生成器脚本。

#### 从发行版软件包安装<a id="installing-from-distribution-packages"></a>

各种发行版可能会打包 Beancount。以下是已知存在的链接：

-   Arch: [https://aur.archlinux.org/packages/beancount/](https://aur.archlinux.org/packages/beancount/)

#### Windows 安装<a id="windows-installation"></a>

##### beancount v3（当前） <a id="beancount-v3"></a>

如果你打算使用 beancount v3，那么没有理由在不安装 beanquery 的情况下安装它，因为自定义 report 和 bean-web 在 v3 中已停止维护。

在这种情况下，安装 beancount 最简单的方法是安装 beanquery，它会将 beancount 作为依赖项安装。

要执行此操作，只需运行以下命令

    pip install beanquery

或者

    python -m pip install beanquery 

或者，如果你更喜欢使用 uv，

    uv tool install beanquery

要测试安装，请创建一个简单的 beancount 账本

例如：

    ====================================

    2024-01-01 open Assets:Bank

    2024-01-01 open Equity:Opening-Balances

    2024-01-01 * "Opening Balance"

      Assets:Bank  1000.00 USD

      Equity:Opening-Balances

    ======================================

将其保存到某个文件（例如 tst.bean）

然后运行

bean-query tst.bean

或者

    python -m beanquery tst.bean

确认你得到了如下提示符

    Input file: "Beancount"

    Ready with 3 directives (2 postings in 1 transactions).

    beanquery>

恭喜！安装成功

如果出于某种原因你仍然希望独立安装 beancount，你可以这样做：

    pip install beancount

或者

    python -m pip install beancount

##### beancount v2（旧版） <a id="beancount-v2"></a>

要安装 beancount 的最后一个 v2 版本，请执行以下操作：

**`pip install "beancount<3"`**

或者

                    python -m pip install "beancount<3"

##### 原生开发环境<a id="native-for-development"></a>

###### 安装编译器<a id="install-compiler"></a>

通过 pip 安装此包需要在安装过程中编译一些 C++ 代码，这只有在计算机上存在适当的编译器时才可能实现，否则你将收到关于缺少 *vsvarsall.bat* 或 *cl.exe* 的错误消息。

为了能够编译 Python 的 C++ 代码，你需要安装与你的 Python 安装所使用的相同主要版本的 C++ 编译器。通过在控制台中运行 *python* 并查找类似于 *\[MSC v.1900 64 bit (AMD64)\]* 的文本，你可以确定用于你的特定 Python 发行版的编译器。在此示例中，它是 *v.1900*。

使用此数字在 [此处](https://stackoverflow.com/questions/2676763/what-version-of-visual-studio-is-python-on-my-computer-compiled-with) 找到所需的 Visual C++ 版本。由于只要前两位数字相同，不同版本似乎就是兼容的，因此理论上你可以使用 1900 到 1999 之间的任何 Visual C++ 编译器。

根据我的经验，Python 3.8 和 3.6 都是使用 MSC v.1900 编译的，因此你可以执行以下任一操作来满足此要求：

-   安装独立的 [Build Tools for Visual Studio 2017](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=BuildTools&rel=15) 或

-   安装独立的 [Visual C++ Build Tools 2015](http://go.microsoft.com/fwlink/?LinkId=691126) 或

-   修改现有的 Visual Studio 2017 安装

    -   从 *Add or remove programs* 启动 Visual Studio 2017 安装程序

    -   选择 *Individual components*

    -   在 *Compilers, build tools, and runtimes* 下勾选 *VC++ 2017 version 15.9 v14.16 latest v141 tools* 或更新版本

    -   安装

-   Visual Studio 2019, 2022

    -   添加 C++ 构建工具：C++ core features, MSVC v142 build tools

如果安装后 cl.exe 不在你的路径中，请运行 Developer Command Prompt for Visual Studio 并在其中运行命令。

######  安装 winflexbison<a id="install-winflexbison"></a>

下载包含 winflexbison 最新版本的 zip 文件

[https://github.com/lexxmark/winflexbison/releases](https://github.com/lexxmark/winflexbison/releases)

将存档解压到某个目录（例如 `C:\Program Files (x86)\winflexbison`）

[更新 Path 环境变量](https://www.youtube.com/watch?v=9umV9jD6n80) 以包含该目录（例如 ‘`C:\Program Files (x86)\winflexbison`’）

重启 PC

打开命令提示符

发出命令

    win_bison --version

确认你得到了包含 win\_bizon 版本的响应

######  安装构建工具<a id="install-build-utilities"></a>

    python -m pip install meson-python meson ninja

###### 获取并安装 beancount<a id="get-and-install-beancount"></a>

从 github 获取 **beancount** 的最新版本并构建它

    git clone https://github.com/beancount/beancount.git

    cd beancount

以可编辑模式从源代码安装 beancount

    python -m pip install --no-build-isolation -e .

###### 测试 beancount<a id="test-beancount"></a>

安装 pytest

    python -m pip install pytest

进入内部目录并运行单元测试

    cd beancount

    python -m pytest

确认大多数测试已通过（截至 2024 年 11 月，在 Windows 上，大约 1100 个总测试中有约 70 个测试失败，这主要与单元测试是假设 POSIX 环境编写的事实有关（参见问题 [222](https://github.com/beancount/beancount/issues/222), [550](https://github.com/beancount/beancount/issues/550) ))

#### 使用 Cygwin<a id="with-cygwin"></a>

Windows 安装当然有些不同。如果你使用 Cygwin，那就轻而易举了。你只需要先准备好你的机器。方法如下。

-   安装最新的 [Cygwin](https://www.cygwin.com/)。这可能需要一段时间（它会下载很多东西），但无论如何都是值得的。但在你开始安装之前，请确保以下所有包都在 setup.exe 提供的界面中手动启用（它们默认未选中）：

    -   python3

    -   python3-devel

    -   python3-setuptools

    -   git

    -   make

    -   gcc-core

    -   flex

    -   bison

-   启动一个新的 Cygwin bash shell（桌面上应该有一个新图标），并通过运行此命令安装 pip3 安装工具：  
    **easy\_install-3.4 pip  
    ** 确保你调用与你的 Python 版本匹配的 easy\_install 版本，例如，如果你安装了 Python 3.8 或更高版本，则使用 easy\_install-3.8。

此时，你应该能够按照前面章节中的说明进行操作，从“使用 pip 安装 Beancount”开始。

#### 使用 WSL<a id="with-wsl"></a>

新发布的 Windows 10 周年更新带来了 WSL（“Windows 子系统 for Linux”），支持 [在 Windows 上的 Ubuntu 中运行 bash](https://blogs.msdn.microsoft.com/wsl/2016/07/08/bash-on-ubuntu-on-windows-10-anniversary-update/)（安装说明及更多信息见 [https://msdn.microsoft.com/commandline/wsl/about](https://msdn.microsoft.com/commandline/wsl/about)）。

这使得从 bash 安装 beancount 变得轻而易举：

    sudo apt-get install python3-pip
    sudo pip3 install m3-cdecimal  # 可能已不再需要
    sudo pip3 install beancount --pre

这并非完全“兼容 Windows”，因为它运行在一个微型进程中，但提供了一种在 Windows 上获得 Linux 命令行体验的便捷方式。*(贡献者：willwray)*

### 检查你的安装<a id="checking-your-install"></a>

你应该能够运行[本文档](running-beancount-and-generating-reports.md)中提到的二进制文件。例如，运行 bean-check 应该会产生类似以下的内容：

    $ bean-check

    usage: bean-check [-h] [-v] filename
    bean-check: error: the following arguments are required: filename

如果这能正常工作，你现在可以前往[教程](tutorial-example.md)，开始学习 Beancount 的工作原理。

### 报告问题<a id="reporting-problems"></a>

如果您需要报告一个问题，可以通过邮件列表发送邮件，或者在 Github 上[提交一个 ticket](https://github.com/beancount/beancount/issues)。运行以下命令可以列出您计算机上已安装的依赖项及其版本，在 bug 报告中包含此命令的输出可能很有用：

    python3 -m beancount.scripts.deps

### 使用 uv 的替代安装方式<a id="alternative-installation-with-uv"></a>

-   从 Astral 网站安装 uv。

-   使用 uv 安装 Beancount

<!-- -->

    uv tool install beancount

    uv tool install beanquery

这将安装二进制文件（在 Windows 上为 .exe），并将其添加到你的 PATH 中，以便你在安装完成后可以直接运行这些命令：

    beancount v3.1.0

-   bean-check.exe

-   bean-doctor.exe

-   bean-example.exe

-   bean-format.exe

-   treeify.exe

<!-- -->

    beanquery v0.2.0

-   bean-query.exe

## 编辑器支持<a id="editor-support"></a>

目前支持以下编辑器：

-   Emacs 支持在[单独的仓库](https://github.com/beancount/beancount-mode)中提供。请参阅[入门指南](getting-started-with-beancount.md)以获取安装说明。

-   [使用 Sublime 进行编辑](https://sublime.wbond.net/packages/Beancount)的支持由 [Martin Andreas Andersen](https://groups.google.com/d/msg/beancount/WvlhcCjNl-Q/s4wOBQnRVxYJ) 贡献。请参阅[他的 GitHub 仓库](https://github.com/draug3n/sublime-beancount)。

-   使用 Vim 进行编辑的支持由 [Nathan Grigg](https://github.com/nathangrigg) 贡献。请参阅[他的 GitHub 仓库](https://github.com/nathangrigg/vim-beancount)。

-   Visual Studio Code 目前有两个可用的扩展。两者均已在 Linux 上测试。

    -   [Beancount](https://marketplace.visualstudio.com/items?itemName=Lencerf.beancount)，提供语法检查（bean-check）以及对 account、currency 等的支持。它不仅允许选择现有的开放 account，还显示其 balance 和其他元数据。非常实用！

    -   [Beancount Formatter](https://marketplace.visualstudio.com/items?itemName=dongfg.vscode-beancount-formatter)，可以使用 bean-format 格式化整个文档，对齐数字等。

## 如果你遇到问题<a id="if-you-have-problems"></a>

如果你在安装过程中遇到任何问题，请[提交工单](https://github.com/beancount/beancount/issues/)或发送邮件至[邮件列表](https://groups.google.com/forum/#!forum/beancount)。

## 安装后使用<a id="post-installation-usage"></a>

通常，[位于 beancount/bin 下的脚本](https://github.com/beancount/beancount/tree/v2/bin) 应自动安装到可执行路径中的某个位置。例如，您应该能够直接在命令行中运行 “bean-check”。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
