# 趋势情报 Agent MVP 状态

更新时间：2026-11-02（America/New_York）

## 已完成

- 建立独立的 `trend-agent/` 项目，不修改原有十仓库运行逻辑。
- 支持 RSS 与 Atom 信息源，包括未来的 RSSHub 路由。
- 支持接收 `changedetection.io` JSON webhook。
- 使用 SQLite 保存文章、趋势运行记录和深度研究队列。
- 使用内容指纹阻止重复入库。
- 按主题关键词、独立来源、覆盖度、可信来源和反向证据进行确定性评分。
- 支持排除不适合某一主题的信息源，降低关键词误报。
- 生成带原始链接的 JSON 和中文 Markdown 报告。
- 达到门槛时生成 GPT Researcher / Serenity / FinRobot 后续研究请求。
- 深度研究任务可以被领取、完成、失败并写回数据库，避免重复处理。
- 已加入 GPT Researcher 进程内适配器，避免默认无认证的开发服务器暴露到公网。
- 深度研究提示已经包含 Serenity 的因果链、多阶影响、供应链瓶颈、反方证据和验证门槛。
- 无模型模式只导出明确标注的研究任务，不会伪装成已经完成的 AI 研究报告。
- 提供批量监控周期命令，单个信息源故障不会中断整个周期。

## 真实数据验证

使用公开 RSS 完成一次端到端运行：

- arXiv Artificial Intelligence：297 条。
- SEC Press Releases：25 条。
- Federal Reserve Press Releases：20 条。
- 合计读取：342 条。
- 去重后首次入库：341 条。
- 相同来源第二次运行：新增 0 条，识别重复 342 条。

首次关键词扫描将一篇讨论关税谈判的 AI 论文错误识别为政治供应链信号。系统随后增加主题级信息源排除规则，复测后该误报被移除。这说明关键词评分只能作为低成本触发器，不能替代后续语义研究。

## 当前边界

- 当前评分属于规则模型，用于决定是否启动深度研究，不是股票价格预测。
- GPT Researcher 适配器已经完成，但尚未真实调用；需要选择 LLM 与搜索服务并配置 API Key。
- FinRobot 尚未接入深度研究结果。
- `changedetection.io` webhook 已兼容，但服务本身尚未部署到常驻 Linux/Docker 环境。
- 尚未配置邮件、Slack 或 Qurio 通知。
- 尚未进行历史时间切片评估。
- 不连接券商，不执行真实交易。

## 下一步

1. 部署 `changedetection.io` 或 RSSHub，并建立第一批可信来源白名单。
2. 配置 GPT Researcher 的 LLM 与搜索服务，执行第一份真实的带引用深度报告。
3. 将候选上市公司交给 FinRobot 与 OpenBB 做财务验证。
4. 增加趋势评分变化通知和历史时间切片测试。
