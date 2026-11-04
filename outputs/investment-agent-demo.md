# 前沿趋势投资研究 Agent：演示结果

生成时间：2026-11-03 00:25:02 EST

> 研究与 dry-run 演示，不构成投资建议；未连接券商，未产生任何成交。

## 1. 趋势发现

- 主题：前沿生物科技、AI 临床研究与 mRNA 供应链
- 固定规则评分：35/100（watch）
- 原因：3 条匹配内容，但只有 1 个独立来源
- 深度报告是在测试时临时降低触发门槛后生成；正式门槛已恢复为 70

## 2. 公司证据门槛

自动公司映射在严格筛选后保留两家公司：

- MRNA / Moderna：mRNA、LNP 与制造平台直接暴露
- DHR / Danaher：子公司 Aldevron 提供 mRNA cGMP、LNP 封装和无菌灌装能力

## 3. OpenBB + Kronos 验证

| 股票 | 收盘价 | MA20 | MA50 | ATR14 | 技术方向 | Kronos 5日 | 研究动作 |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| MRNA | $220.83 | 216.03 | 184.00 | 23.11 | buy | +5.42% | paper intent |
| DHR | $227.97 | 226.98 | 219.03 | 6.96 | buy | +2.27% | paper intent |

## 4. 风险控制产生的订单意图

| 股票 | 数量 | 参考价 | 止损参考 | 止盈参考 | 成交 |
| --- | ---: | ---: | ---: | ---: | --- |
| MRNA | 21 | $220.83 | $174.61 | $313.27 | 否（dry-run） |
| DHR | 71 | $227.97 | $214.05 | $255.82 | 否（dry-run） |

仓位由单笔风险 1%、单仓上限 20%、总敞口上限 60% 和现金约束共同决定。
订单意图仅用于展示风险计算，未写入模拟账户，也没有发送到券商。

## 5. 结论

当前结果支持把 MRNA 与 DHR 留在研究观察名单：二者具备主题直接证据，
20/50 日趋势为正，且本次 Kronos 五日平均路径预测为正。它不等于已经证明策略有效，
更不代表未来上涨概率。下一道正式门槛是财报/估值验证和滚动样本外回测。

## 6. 审计文件

- 市场与模型原始 JSON：`outputs/ai-fund-lab-trend-biotech-kronos/run-20261103-002518.json`
- 趋势深度报告：`trend-agent/reports/research/research-1-frontier_biotech.md`
- 自动公司映射：`trend-agent/reports/company-maps/research-2-frontier_biotech_company_map.md`
- 人工证据桥接：`outputs/frontier-biotech-investment-bridge.md`
