> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/beancount_cheat_sheet/

# Beancount 语法速查表<a id="title"></a>

<table><tbody><tr class="odd"><td><p><em>示例账户名称：</em> Assets:US:BofA:Checking</p><table><tbody><tr class="odd"><td><h2 id="account-types">账户类型<a id="account-types"></a></h2><table><tbody><tr class="odd"><td><p>Assets</p><p>Liabilities</p><p>Income</p><p>Expenses</p><p>Equity</p></td><td><p><strong>+</strong></p><p><strong>-</strong></p><p><strong>-</strong></p><p><strong>+</strong></p><p><strong>-</strong></p></td></tr></tbody></table></td><td><h2 id="commodities">商品<a id="commodities"></a></h2><p><em>全部大写：</em></p><p>USD, EUR, CAD, AUD</p><p>GOOG, AAPL, RBF1005</p><p>HOME_MAYST, AIRMILES<br />
HOURS</p></td></tr></tbody></table><h2 id="directives">指令<a id="directives"></a></h2><blockquote><p><em>通用语法：</em></p><p><strong>YYYY-MM-DD <em>&lt;directive&gt; &lt;arguments...&gt;</em></strong></p></blockquote><h2 id="opening-closing-accounts">开设与关闭账户<a id="opening-closing-accounts"></a></h2><p>2001-05-29 open Expenses:Restaurant</p><p>2001-05-29 open Assets:Checking USD,EUR <em>；货币约束</em></p><p>2015-04-23 close Assets:Checking</p><h2 id="declaring-commodities">声明商品<a id="declaring-commodities"></a></h2><p><em>这是可选的；仅当您想按货币附加元数据时使用。</em></p><p>1998-07-22 commodity AAPL<br />
name: "Apple Computer Inc."</p><h2 id="prices">价格<a id="prices"></a></h2><p><em>多次使用以填充历史价格数据库：</em></p><p>2015-04-30 price AAPL 125.15 USD</p><p>2015-05-30 price AAPL 130.28 USD</p><h2 id="notes">备注<a id="notes"></a></h2><p>2013-03-20 note Assets:Checking "Called to ask about rebate"</p><h2 id="documents">文档<a id="documents"></a></h2><p>2013-03-20 document Assets:Checking "path/to/statement.pdf"</p></td><td><h2 id="transactions">交易<a id="transactions"></a></h2><p>2015-05-30 * "Some narration about this transaction"<br />
Liabilities:CreditCard -101.23 USD<br />
Expenses:Restaurant 101.23 USD</p><p>2015-05-30 ! "Cable Co" "Phone Bill" #tag ˆlink</p><p>id: "TW378743437" <em>；元数据</em><br />
Expenses:Home:Phone 87.45 USD<br />
Assets:Checking <em>；您可以省略一个金额</em></p><h3 id="postings">分录<a id="postings"></a></h3><p>... 123.45 USD <em>简单</em><br />
... 10 GOOG <strong>{502.12 USD}</strong> <em>带单位成本<br />
</em> ... 10 GOOG <strong>{{5021.20 USD}}</strong> <em>带总成本</em></p><p>... 10 GOOG <strong>{502.12 # 9.95 USD}</strong> <em>带两种成本</em><br />
... 1000.00 USD <strong>@ 1.10 CAD</strong> <em>带单位价格</em><br />
... 10 GOOG {502.12 USD} @ 1.10 CAD <em>带成本与价格</em><br />
... 10 GOOG {502.12 USD, <strong>2014-05-12</strong>} <em>带日期</em><br />
<strong>!</strong> ... 123.45 USD ... <em>带标志</em></p><h2 id="balance-assertions-and-padding">余额断言与填充<a id="balance-assertions-and-padding"></a></h2><p><em>仅断言给定货币的金额：</em></p><p>2015-06-01 balance Liabilities:CreditCard -634.30 USD</p><p><em>自动插入 transaction 以满足以下断言：</em></p><p>YYYY-MM-DD pad Assets:Checking Equity:Opening-Balances</p><h2 id="events">事件<a id="events"></a></h2><p>YYYY-MM-DD event "location" "New York, USA"<br />
YYYY-MM-DD event "address" "123 May Street"</p><h2 id="options">选项 <a id="options"></a></h2><p>option "title" "My Personal Ledger"</p><p><em>请参阅 <a href="beancount_options_reference.md">此文档</a> 获取支持的完整选项列表。</em></p><h2 id="other">其他<a id="other"></a></h2><p>pushtag #trip-to-peru</p><p>...</p><p>poptag #trip-to-peru</p><p>; 注释以分号开头</p></td></tr></tbody></table>

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
