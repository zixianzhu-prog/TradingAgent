# 模拟订单条件（研究用，需人工确认）

生成：2026-11-24T18:06；假设组合规模 $100,000。只在模拟盘执行，真实交易关闭。

> 规则对每家公司相同：动作由 Serenity 结论和价格相对下单区间决定；仓位按 Serenity 分档（试探 1%、标准 5%、单只上限 10%），再按单日回撤、日成交额和现金跑道下调；只在财报、客户或合作披露验证后加仓；不设紧止损，论点被证伪才退出。

合计目标仓位 4.0%，现在可买 4.0%；模拟买入 1，模拟试探仓 4，等待 10，回避 1。

| 动作 | 股票 | 价格 | 限价 | 安全底线 | 仓位（现在） | 理由 |
|---|---|---:|---:|---:|---:|---|
| **模拟买入** | TEM | $55.14 | $62.92 | $45.44 | 1.0%（1.0%） | Price $55.14 is inside the order range (consider at or below $62.92) |
| **模拟试探仓** | CAI | $18.40 | $31.61 | $23.38 | 0.5%（0.5%） | Price $18.4 is below the safety floor $23.38: cheaper than the bear case, so a starter only until a fundamental problem is ruled out |
| **模拟试探仓** | SDGR | $24.74 | $26.75 | $23.59 | 1.0%（1.0%） | Price $24.74 is inside the order range (consider at or below $26.75)；Serenity verdict is watch (gates still open): starter only until the up |
| **模拟试探仓** | SOPH | $6.36 | $7.95 | $5.77 | 0.5%（0.5%） | Price $6.36 is inside the order range (consider at or below $7.95)；Serenity verdict is watch (gates still open): starter only until the upgr |
| **模拟试探仓** | CERT | $11.04 | $13.13 | $13.06 | 1.0%（1.0%） | Price $11.04 is below the safety floor $13.06: cheaper than the bear case, so a starter only until a fundamental problem is ruled out |
| **等待** | CBLL | $29.64 | $24.62 | $16.11 | — | Price $29.64 is 20% above $24.62; it implies 21% growth a year against 16% in the base case |
| **等待** | HTFL | $46.09 | $32.38 | $20.90 | — | Price $46.09 is 42% above $32.38; it implies 28% growth a year against 19% in the base case |
| **等待** | ISRG | $433.48 | $301.66 | $247.15 | — | Price $433.48 is 44% above $301.66; it implies 21% growth a year against 12% in the base case |
| **等待** | RDNT | $72.82 | $58.63 | $34.62 | — | Price $72.82 is 24% above $58.63; it implies 13% growth a year against 9% in the base case |
| **等待** | GEHC | $82.45 | $50.51 | $50.51 | — | Price $82.45 is 63% above $50.51; it implies 14% growth a year against 5% in the base case |
| **等待** | NTRA | $294.89 | $202.48 | $131.59 | — | Price $294.89 is 46% above $202.48; it implies 27% growth a year against 18% in the base case |
| **等待** | RXRX | $2.70 | — | — | — | No valuation range: discovery platform; a sales multiple or one-asset rNPV would mislead. Today's price: market value $1,683M less cash $749 |
| **等待** | GH | $154.10 | $88.40 | $55.00 | — | Evidence incomplete: primary-source completeness 48 is below the bar |
| **等待** | ABCL | $10.89 | — | — | — | No valuation range: discovery platform; a sales multiple or one-asset rNPV would mislead. Today's price: market value $3,529M less cash $790 |
| **等待** | IRD | $3.97 | $2.42 | $0.68 | — | Price $3.97 is 64% above the rNPV base value $2.42; it implies $2,162M peak sales for the lead asset |
| **回避** | IQV | $256.53 | — | — | — | Serenity verdict is reject: a gate is contradicted by a primary source |

## TEM · 模拟买入 1.0%（$1,000）

- 理由：Price $55.14 is inside the order range (consider at or below $62.92)
- Serenity：research-ready，分档 starter
- 加仓：add after earnings, a customer or a deal confirms the thesis, up to 5%; never because the price rose
- 减仓：consider trimming above $148.88, where even the bull case earns less than 12% a year
- 认错条件：Diagnostic volume growth stalls for two consecutive reported quarters；Data-and-services growth materially trails total company growth；Gross margin or cash-flow progress deteriorates despite higher volume；open counter-point: related-party revenue (~20% of data revenue from Pathos)；open counter-point: debt exceeds cash

## CAI · 模拟试探仓 0.5%（$500）

- 理由：Price $18.4 is below the safety floor $23.38: cheaper than the bear case, so a starter only until a fundamental problem is ruled out
- Serenity：research-ready，分档 starter
- 仓位调整：worst day in 6 months -22%: halved for the drawdown budget
- 加仓：add after earnings, a customer or a deal confirms the thesis, up to 5%; never because the price rose
- 减仓：consider trimming above $73.77, where even the bull case earns less than 12% a year
- 认错条件：The material weakness is not remediated by the next annual report；Revenue growth falls below 15%；Pharma services revenue declines；open counter-point: material weakness in internal control；open counter-point: $400M term loan; sole-source sequencers

## SDGR · 模拟试探仓 1.0%（$1,000）

- 理由：Price $24.74 is inside the order range (consider at or below $26.75)；Serenity verdict is watch (gates still open): starter only until the upgrade condition in the memo is met
- Serenity：watch，分档 starter
- 加仓：add after earnings, a customer or a deal confirms the thesis, up to 5%; never because the price rose
- 减仓：consider trimming above $60.11, where even the bull case earns less than 12% a year
- 认错条件：Software ACV or retention weakens for two consecutive reported periods；Software gross margin fails to recover during the hosted transition；Major pharmaceutical collaborations contract without replacement；open counter-point: software growth slowed to 6%

## SOPH · 模拟试探仓 0.5%（$500）

- 理由：Price $6.36 is inside the order range (consider at or below $7.95)；Serenity verdict is watch (gates still open): starter only until the upgrade condition in the memo is met
- Serenity：watch，分档 starter
- 仓位调整：market value $457M, under $1B: smaller cap
- 加仓：add after earnings, a customer or a deal confirms the thesis, up to 5%; never because the price rose
- 减仓：consider trimming above $19.04, where even the bull case earns less than 12% a year
- 认错条件：Revenue growth falls below the mid-teens before profitability；Adjusted EBITDA improvement stalls or reverses；Cash runway falls below two years without financing；open counter-point: repeated dilution；open counter-point: high-cost debt

## CERT · 模拟试探仓 1.0%（$1,000）

- 理由：Price $11.04 is below the safety floor $13.06: cheaper than the bear case, so a starter only until a fundamental problem is ruled out
- Serenity：watch，分档 starter
- 加仓：add after earnings, a customer or a deal confirms the thesis, up to 5%; never because the price rose
- 减仓：consider trimming above $33.1, where even the bull case earns less than 12% a year
- 认错条件：Organic software growth falls back below high single digits for two consecutive quarters；Bookings or retention weaken despite new AI products；Customers can replace core workflows without meaningful switching cost；open counter-point: modest growth；open counter-point: $295.5M credit-agreement debt

## 局限

- 仓位规则来自 Serenity 的公开方法，没有经过本项目自己的回测；下单区间规则也还没有回测。
- 组合层面的相关性还没考虑：几只同方向的股票可能一起跌。下一步用 Riskfolio-Lib 控制。
- 这是研究建议，不是投资建议；每张单都需要人看过再执行。
