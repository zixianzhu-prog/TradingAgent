# 前沿趋势投资研究 Agent：演示结果

生成时间：2026-11-03 09:17:48 EST

> 研究与 dry-run 演示，不构成投资建议；未连接券商，未产生任何成交。

## 1. 趋势发现

- 主题：前沿生物科技、AI 临床研究与 mRNA 供应链
- 当日趋势评分：73/100（emerging）
- 证据：9 条近期匹配内容，来自 9 个独立来源
- 正式研究触发门槛：70；评分用于排列研究优先级，不代表新闻真实性或上涨概率

## 2. 公司证据门槛

自动公司映射在严格筛选后保留两家公司：

- MRNA / Moderna：mRNA、LNP 与制造平台直接暴露
- DHR / Danaher：子公司 Aldevron 提供 mRNA cGMP、LNP 封装和无菌灌装能力

## 3. OpenBB + Kronos 验证

| 股票 | 收盘价 | MA20 | MA50 | ATR14 | 技术方向 | Kronos 5日 | 研究动作 |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| MRNA | $220.83 | 216.03 | 184.00 | 23.11 | buy | +5.42% | paper intent |
| DHR | $227.97 | 226.98 | 219.03 | 6.96 | buy | +2.27% | paper intent |

## 4. 新闻与市场综合研究评分

| 股票 | 新闻关联度 | 来源可靠度 | 新闻情绪 | 新闻评分 | 技术评分 | Kronos评分 | 综合分 | 置信度 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| MRNA | 100 | 40 | -0.07 | 71 | 100 | 77 | 82 | high |
| DHR | 0 | 0 | +0.00 | 0 | 94 | 61 | 45 | low |

综合分 = 新闻评分45% + 技术评分35% + Kronos方向评分20%。
这是透明的MVP研究优先级，不是收益概率；新闻证据不足时置信度会保持低。

## 5. Serenity 供应链投资门槛

| 股票 | 供应链图 | 卡位证据 | 客户依赖 | 纯业务暴露 | 财报验证 | Serenity结论 |
| --- | --- | --- | --- | --- | --- | --- |
| MRNA | pass | partial | unknown | pass | pending | watch |
| DHR | pass | partial | unknown | fail | pending | watch |

Serenity 方法把新闻和模型信号当作假设起点，而不是买入依据。
只有卡位、客户依赖和财报验证均有直接证据，才允许从观察升级为可投资论点。

- MRNA：Moderna 对 mRNA 的业务暴露直接且相对纯粹，但当前证据尚不能证明它控制不可替代的供应节点，也没有确认下游客户依赖；需要等待管线、收入和现金消耗的财报验证。
- DHR：Aldevron 直接参与 mRNA 制造，但 Danaher 是多元化集团；该业务对集团的收入贡献、客户依赖和产能利用率均未得到确认。

## 6. 风险控制产生的订单意图

| 股票 | 数量 | 参考价 | 止损参考 | 止盈参考 | 成交 |
| --- | ---: | ---: | ---: | ---: | --- |
| MRNA | 21 | $220.83 | $174.61 | $313.27 | 否（dry-run） |
| DHR | 71 | $227.97 | $214.05 | $255.82 | 否（dry-run） |

仓位由单笔风险 1%、单仓上限 20%、总敞口上限 60% 和现金约束共同决定。
这些是市场模型单独产生的技术面订单意图；新闻综合分尚未授权触发交易。
订单未写入模拟账户，也没有发送到券商。

## 7. 结论

- 进入优先深度研究（综合分≥70且新闻置信度不低）：MRNA
- Serenity 门槛尚未通过，不升级为投资建议：MRNA
- 保持观察、等待更多公司相关新闻证据：DHR
- 该结论只改变研究优先级，不等于买入建议，也不会自动下单。
- 下一道正式门槛是财报/估值验证和滚动样本外回测。

## 8. 宽主题关联股票

新闻无需提及股票名称；以下结果来自主题强度与已配置业务/供应链关系的传导。

| 主题 | 股票 | 主题分 | 传导分 | 结论 |
| --- | --- | ---: | ---: | --- |
| 前沿生物科技与公共卫生 | MRNA | 73 | 66 | deep-research |
| 机器人与自动化 | SYM | 69 | 62 | watch |
| 机器人与自动化 | TER | 69 | 47 | watch |
| 前沿生物科技与公共卫生 | DHR | 73 | 43 | watch |
| 机器人与自动化 | ROK | 69 | 41 | watch |
| 机器人与自动化 | NVDA | 69 | 35 | watch |

这些股票只进入候选研究池；进入行情、估值或订单流程前仍需单独验证。

## 9. 审计文件

- 市场与模型原始 JSON：`outputs/daily-market/run-20261103-091829.json`
- 每日公司新闻评分：`trend-agent/reports/daily/company-news/company-news-scores.json`
- 每日趋势评分：`trend-agent/reports/daily/trends/latest-trends.json`
- Serenity 门槛：`trend-agent/serenity-assessments.json`
- 主题股票传导：`trend-agent/reports/daily/theme-stocks/theme-stock-links.json`
- 趋势深度报告：`trend-agent/reports/research/research-1-frontier_biotech.md`
- 自动公司映射：`trend-agent/reports/company-maps/research-2-frontier_biotech_company_map.md`
- 人工证据桥接：`outputs/frontier-biotech-investment-bridge.md`
