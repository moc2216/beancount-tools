> 非官方中文译文 · 术语保留英文；代码、account、option、币种原样。
> 原文：https://beancount.github.io/docs/tracking_medical_claims/

# 在 Beancount 中追踪网络外医疗理赔<a id="title"></a>

[Martin Blais](mailto:blais@furius.ca) - 更新于：2023 年 11 月

让我们通过一个例子来说明如何处理涉及保险和 HSA（健康储蓄账户）理赔的医疗支出。这里以心理治疗为例，该治疗属于网络外服务，先由个人垫付，随后获得报销。

当接受一次治疗时，将其记录为应收账款和应付账款：


       2023-09-06 * "Dr. Freud" "Session" #freud-2023-09
         Assets:AccountsReceivable:Psychotherapy     260.00 USD
         Liabilities:AccountsPayable:Psychotherapy  -260.00 USD

       2023-09-11 * "Dr. Freud" "Session" #freud-2023-09
         Assets:AccountsReceivable:Psychotherapy     260.00 USD
         Liabilities:AccountsPayable:Psychotherapy  -260.00 USD

随后，进行部分付款以清除应付账款：


       2023-09-12 * "ZELLE SENT" #freud-2023-09
         Assets:US:BofA:Checking                     -520.00 USD
         Liabilities:AccountsPayable:Psychotherapy    520.00 USD

整个月份的情况类似：


       2023-09-20 * "Dr. Freud" "Session" #freud-2023-09
         Assets:AccountsReceivable:Psychotherapy     260.00 USD
         Liabilities:AccountsPayable:Psychotherapy  -260.00 USD

       2023-09-23 * "ZELLE SENT" #freud-2023-09
         Assets:US:BofA:Checking                     -260.00 USD
         Liabilities:AccountsPayable:Psychotherapy  260.00 USD


       2023-09-27 * "Dr. Freud" "Session" #freud-2023-09
         Assets:AccountsReceivable:Psychotherapy     260.00 USD
         Liabilities:AccountsPayable:Psychotherapy  -260.00 USD

       2023-09-28 * "ZELLE SENT" #freud-2023-09
         Assets:US:BofA:Checking                     -260.00 USD
         Liabilities:AccountsPayable:Psychotherapy  260.00 USD

月底，治疗师会生成一份理赔单。我们将理赔单提交给保险公司，清除应收账款，并将剩余部分转移至待开具的保险公司支票：


       2023-09-28 * "Claim for September filed with insurance" #freud-2023-09
         Assets:AccountsReceivable:Psychotherapy  -1040.00 USD
         Expenses:Mental:Psychotherapy              312.00 USD
         Assets:AccountsReceivable:Anthem           728.00 USD

最终，保险公司会出具 EOB（福利说明单）以确认覆盖金额（在本例中为 70%，这一比例在条款中已明确），随后收到支票并存入银行：


       2023-10-24 * "ATM CHECK DEPOSIT" #freud-2023-09
         Assets:US:BofA:Checking             728.00 USD
         Assets:AccountsReceivable:Anthem   -728.00 USD

此时，我们已知剩余部分中可由 HSA 支付的金额，因此向 HSA 公司提交理赔申请，再次将其记录为应收账款和应付账款：


       2023-10-25 * "HealthEquity" "Filed for reimbursement" #freud-2023-09
         Liabilities:AccountsPayable:HealthEquity  -312.00 USD
         Assets:AccountsReceivable:HealthEquity     312.00 USD

HSA 公司直接将该款项存入我们的支票账户：


       2023-11-01 * "BofA bank (Claim ID:1234567-890); EFT to bank" #freud-2023-09
         Assets:US:HealthEquity:Cash               -312.00 USD
         Liabilities:AccountsPayable:HealthEquity   312.00 USD

在银行端，当我们导入这笔 transaction 时，将其与应收账款进行对冲：


       2023-11-01 * "HEALTHEQUITY INC" #freud-2023-09
         Assets:US:BofA:Checking                    312.00 USD
         Assets:AccountsReceivable:HealthEquity    -312.00 USD

最终结果是，HSA 被用于覆盖未由保险报销的费用部分。

    |-- Assets                       
    |   |-- AccountsReceivable       
    |   |   |-- Anthem                
    |   |   |-- HealthEquity         
    |   |   `-- Psychotherapy        
    |   `-- US                       
    |       |-- HealthEquity         
    |       |   `-- Cash                  -312.00               USD
    |       `-- BofA                   
    |           `-- Checking         
    |-- Expenses                     
    |   `-- Mental                   
    |       `-- Psychotherapy              312.00               USD
    `-- Liabilities                  
        `-- AccountsPayable          
            |-- HealthEquity         
            `-- Psychotherapy        

    Net Income: (-312.00 USD)

上述方法存在一些缺陷：

-   保险覆盖的金额是预先已知的；但在许多情况下，在保险公司出具 EOB 之前，该金额是未知的（毕竟 EOB 的作用就是“福利说明”）。这需要对上述方法进行修改。

---

> **版权与许可**：原文 © Martin Blais / beancount/docs contributors，MIT License。中文翻译为非官方 derivative work，仅供个人学习；详见 [NOTICE.md](../NOTICE.md)。
