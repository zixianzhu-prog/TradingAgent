# rNPV 下单区间（无收入的药物开发公司）

生成时间：2026-11-24T17:51:19+00:00。成功率与阶段时长：BIO, Informa Pharma Intelligence & QLS, Clinical Development Success Rates 2011-2020 (2021)。
峰值销售是未核实的分析师先验（熊 150 / 基准 500 / 牛 1500 百万美元），除非标注了来源；“现价隐含峰值销售”是反推结果，用来判断市场假设是否合理。

| 代码 | 阶段 | 获批概率 | 距上市(年) | 现价 | 下单上限 | 安全底线 | 状态 | 现价隐含峰值销售 | 备注 |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| AVXL | 3 | 52% | 3.0 | $0.59 | $3.40 | $1.48 | below-floor | $-11M | lead trial NCT04304482 is completed: check its result before using the range |
| ELDN | 3 | 52% | 3.0 | $1.92 | $0.03 | $0.00 | above | $531M | cash lasts about 10 months: a share sale is near, expect dilution；today's price implies 36.4% of 32,400 patients at $45,000 a year |
| HURA | 3 | 52% | 3.0 | $1.40 | $0.00 | $0.00 | above | $275M | cash lasts about 1 months: a share sale is near, expect dilution；range not used for orders until the company has raised money；today's price implies 58.4% of 2,547 patients at $185,000 a year |
| IRD | 3 | 52% | 3.0 | $3.97 | $2.42 | $0.68 | above | $2,162M | lead asset is partnered: 15% royalty until 2040; the company's own other programs are not valued；today's price implies 14.4% of 8.4M patients at $1,800 a year |
| SGMT | 3 | 52% | 3.0 | $9.69 | $8.55 | $6.06 | above | $293M | today's price implies 2.0% of 10.0M patients at $1,500 a year；In June 2025, Ascletis announced that denifanstat met all primary and secondary endpoints in its Phase 3 trial in moderate to severe acne vulgaris in China. |
| ABCL | 2 | 15% | 6.4 | $11.23 | $1.39 | $1.28 | above | $32,515M | discovery platform: one-asset rNPV understates it, range not used for orders |
| ALEC | 2 | 15% | 6.4 | $2.42 | $0.00 | $0.00 | above | $5,675M | existing revenue $652M a year is not in the model；lead trial NCT04592874 is completed: check its result before using the range；cash lasts about 12 months: a share sale is near, expect dilution |
| ANTX | 2 | 15% | 6.4 | $5.07 | $2.23 | $0.76 | above | $2,086M | today's price implies 37.4% of 62,000 patients at $90,000 a year |
| CGEM | 2 | 15% | 6.4 | $9.29 | $0.00 | $0.00 | above | $7,211M |  |
| FATE | 2 | 15% | 6.4 | $0.95 | $0.00 | $0.00 | above | $2,380M | today's price implies 37.3% of 21,250 patients at $300,000 a year |
| GLUE | 2 | 15% | 6.4 | $9.46 | $2.79 | $2.38 | above | $6,222M | discovery platform: one-asset rNPV understates it, range not used for orders；existing revenue $218M a year is not in the model |
| ODTX | 2 | 15% | 6.4 | $17.23 | $0.08 | $0.00 | above | $8,778M | discovery platform: one-asset rNPV understates it, range not used for orders |
| PALI | 2 | 15% | 6.4 | $0.90 | $0.53 | $0.35 | above | $1,217M | today's price implies 15.3% of 209,701 patients at $38,000 a year |
| PRME | 2 | 15% | 6.4 | $3.82 | $0.00 | $0.00 | above | $10,207M | cash lasts about 5 months: a share sale is near, expect dilution；range not used for orders until the company has raised money；today's price implies 61.9% of 55,000 patients at $3,000,000 once (one-time therapy) |
| RNA | 2 | 15% | 6.4 | $6.94 | $4.15 | $2.54 | above | $1,106M | existing revenue $61M a year is not in the model |
| RXRX | 2 | 15% | 6.4 | $3.20 | $0.00 | $0.00 | above | $23,938M | discovery platform: one-asset rNPV understates it, range not used for orders |
| TECX | 2 | 15% | 6.4 | $21.34 | $5.54 | $3.79 | above | $3,670M |  |
| YARW | 2 | 15% | 6.4 | $13.54 | $0.89 | $0.00 | above | $2,433M |  |
| IBIO | 1 | 8% | 9.4 | $0.82 | $0.00 | $0.00 | above | $2,231M | discovery platform: one-asset rNPV understates it, range not used for orders |

只有单一管线的药物开发公司（rangeUsable）用这个区间下单；平台型公司只看“现价隐含峰值销售”。

未估值：OABI（no live own clinical trial (none, or all terminated): rNPV needs a clinical asset）；AGPU（no live own clinical trial (none, or all terminated): rNPV needs a clinical asset）；NAUT（no live own clinical trial (none, or all terminated): rNPV needs a clinical asset）；AGMB（missing cashM）；KALA（no live own clinical trial (none, or all terminated): rNPV needs a clinical asset）
