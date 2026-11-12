# 公开金融 Agent 学习与升级记录

> 目标不是堆叠仓库，而是吸收能提高可验证性、长期连续性和演示说服力的设计。所有交易执行继续关闭。

| 项目 | 值得学习的能力 | 本系统状态 |
|---|---|---|
| [FinMem](https://github.com/xt2201/finmem) | 分层长期记忆，把短期观察、中期事件和长期论点分开，并要求决策引用记忆 | 已实现确定性的三层论点记忆与变化日志 |
| [FinRobot](https://github.com/AI4Finance-Foundation/FinRobot) | 数据、分析、建模、综合、报告角色分离；确定性计算与 LLM 分工 | 已有数据、Serenity、市场、审计和报告分层；估值继续由确定性代码计算 |
| [AlphaAgent](https://github.com/kamendula/AlphaAgent) | point-in-time 防泄漏；LLM 不进入可测量收益计算环节 | 已用发布时间、事件时间和真实未来价格回填；仍需更长样本 |
| [trading-agents-lab](https://github.com/Kantamaniprakash/trading-agents-lab) | 匿名化、防知识截止泄漏、walk-forward、成本和强基线 | 已有 SPY/XLV/随机/动量基准；匿名化和完整 walk-forward 尚待补充 |
| [Investigator](https://github.com/dsivov/investigator) | 每条主张回链来源、跨事件知识图、持续监控受影响节点 | 已有 121 节点证据图；下一阶段补逐条 claim-level 引用和影响传播 |
| [TradingAgents](https://github.com/TauricResearch/TradingAgents) | 专业角色、牛熊辩论和风险经理 | 已用于独立审查，不允许绕过 Serenity 与确定性门槛 |

## 本次采用

1. 为八家 AI Medicine 决赛公司建立浅层/中层/深层记忆。
2. 浅层保存价格与 Kronos 五日环境；中层保存事件、失效门槛；深层保存长期论点、反方和证伪条件。
3. 只有状态真正改变时才增加快照，避免每天复制相同报告。
4. 每次改变记录 before/after 和关联事件，Peter 可以看到系统为什么改观点。

## 明确没有采用

- 不接真实券商，不自动执行订单。
- 不让 LLM 自己计算收益、财务比率或回测结果。
- 不因为其他项目展示高回测收益就复制策略。
- 不在样本不足时宣称新闻或 Agent 具有预测能力。
