# Serenity Trade Research Agent

一个本地优先、可持续运行、带来源和审计记录的投资研究 Agent。当前演示重点是 **AI Medicine**：系统持续收集前沿信息，把事件映射到相关公司，用 Serenity/Aleabit 方法检查长期投资逻辑，再用市场数据、Kronos 预测、财务情景和独立 Agent 报告交叉验证。

本项目只做研究、回测和模拟验证，**不连接券商，不自动下单，也不构成投资建议**。

## 它解决什么问题

直接向通用聊天模型提问，通常得到的是一次性答案。这个项目增加了持续性和可验证性：

1. 每天收集 RSS、网站变化和官方事件，不依赖用户每次重新提问。
2. 保存信息首次可知的时间，降低未来信息泄漏风险。
3. 把主题新闻映射到可能受益的公司，而不要求新闻必须出现股票名称。
4. 用 Serenity 门槛检查供应链位置、客户依赖、替代风险、财务与重大事件。
5. 用 OpenBB、Kronos、财务情景和 TradingAgents 报告提供独立验证。
6. 保存过去的论点、反方观点、证伪条件和结论变化。
7. 在未来回填 1/5/20/60 个观察日的真实表现，并与 SPY、XLV 比较。

因此，系统输出的不是“模型说会涨”，而是：**发现了什么、为什么与公司有关、证据是否足够、哪些条件尚未通过、什么事件会推翻判断，以及后来是否真的有效。**

## 总体架构

```text
RSS / RSSHub / changedetection.io / SEC / ClinicalTrials.gov / Form 4
                              │
                              ▼
                  trend-agent：抓取、去重、时间戳
                              │
                              ▼
              主题识别 → 公司映射 → 研究优先级评分
                              │
              ┌───────────────┴────────────────┐
              ▼                                ▼
   Serenity 研究与选股门槛             OpenBB + Kronos 市场验证
   供应链/客户/替代/财报/反方           价格/技术趋势/五日环境
              │                                │
              └───────────────┬────────────────┘
                              ▼
          财务情景 / SEC 数字核验 / 披露矛盾 / 证据图
                              │
                              ▼
        FinMem-compatible 分层记忆与 TradingAgents 独立审查
                              │
                              ▼
        5–10 年论点、watch/revalidate/reject、引用与风险
                              │
                              ▼
          未来价格回填、SPY/XLV 基准、Dashboard 展示
```

## 使用了哪些开源仓库和技术

“安装”“验证”“进入每日主流程”不是同一件事。下表明确标记了实际关系，避免把参考项目误写成完整集成。

### 每日主流程中的核心组件

| 项目/技术 | 本项目中的作用 | 接入方式 |
|---|---|---|
| [OpenBB](https://github.com/OpenBB-finance/OpenBB) | 获取统一的历史市场数据 | **直接接入** `ai-fund-lab` 数据层 |
| [Kronos](https://github.com/shiyu-coder/Kronos) | 根据 K 线生成五日市场环境预测 | **直接接入**，作为验证层，不单独决定投资结论 |
| [TradingAgents](https://github.com/TauricResearch/TradingAgents) | 多角色市场、基本面、牛熊辩论和风险审查 | **报告导入**；现有 NVDA 报告已生成，不能绕过 Serenity 硬门槛 |
| [GPT Researcher](https://github.com/assafelovic/gpt-researcher) | 对高优先级主题执行带来源的深度网页研究 | **适配器已实现**；启用时需要单独模型配置 |
| [changedetection.io](https://github.com/dgtlmoon/changedetection.io) | 监控重要网页变化 | **Webhook 接口已实现**，变化进入 `trend-agent` |
| [RSSHub](https://github.com/DIYgod/RSSHub) | 将不同网站转换成统一 RSS 信息源 | **Feed 接口已实现**，可接自建 RSSHub 路由 |
| Serenity/Aleabit skills | 供应链卡位、选股、研究流程、进出场、仓位和风险框架 | **方法论已转成确定性门槛**；当前核心使用 research-process、stock-selection 和 chokepoint-thesis |
| FinMem | 分层记忆、历史决策引用和反思思想 | **借鉴架构、独立实现**；没有复制或运行其完整交易代码 |

### 最初 X 文章对应的十仓库路线

| # | 仓库 | 原本用途 | 当前状态 |
|---|---|---|---|
| 1 | TradingAgents | 多智能体研究、辩论和投资建议 | 报告已生成，并可导入每日流程作独立审查 |
| 2 | ai-hedge-fund | 多 Agent 基本面、估值和组合决策 | 已安装并验证 CLI；完整分析仍需 Financial Datasets 与模型 API Key |
| 3 | daily_stock_analysis | 每日行情、新闻、LLM 分析和通知 | 已完成无 Key dry-run；其每日分析思想由本项目的 `trend-agent` 扩展 |
| 4 | Kronos | 金融 K 线时序预测 | 已直接接入每日市场验证 |
| 5 | Qlib + RD-Agent | 因子研究、训练、回测和研究自动化 | 已安装并验证；完整循环仍受 Linux/Docker 和模型配置限制 |
| 6 | OpenBB | 统一市场数据入口 | 已直接接入每日流程 |
| 7 | CCXT | 统一加密交易所 API | 已验证 Kraken 公共数据；属于独立加密分支，不进入 AI Medicine 主流程 |
| 8 | Freqtrade | 加密策略回测与执行 | 已完成 Coinbase 基线和 EMA 对照回测；不进入美股研究主流程 |
| 9 | Hummingbot | 加密做市与执行 | CLI、编译和 paper-trade 模块已验证；未配置交易所账户 |
| 10 | NautilusTrader | 事件驱动回测与执行 | 已完成与 Freqtrade 相同数据和费用条件下的独立对照回测 |

十个仓库均完成最小安装或启动验证，但**每日 AI Medicine 主流程目前真正直接使用的是 OpenBB、Kronos，并导入 TradingAgents 已有报告**。其余仓库是独立验证、未来扩展或加密回测分支。详细状态见 [`outputs/10-repo-progress.md`](outputs/10-repo-progress.md)。

### 借鉴但没有直接运行完整代码的项目

| 项目 | 借鉴内容 | 已实现为 |
|---|---|---|
| [FinMem](https://github.com/xt2201/finmem) | shallow/mid/long-term memory 与 reflection | 稳定的 `mem_*` 记忆编号、变化快照、论点/反方/证伪条件和未来表现回填 |
| [FinRobot](https://github.com/AI4Finance-Foundation/FinRobot) | 数据、分析、建模、综合、报告角色分层 | 抓取、Serenity、市场、审计、报告分别由确定性模块负责 |
| AlphaAgent | point-in-time 数据与防未来信息泄漏 | `publishedAt/discoveredAt/knowledgeAt/firstEligibleResearchDate` |
| trading-agents-lab | walk-forward、成本和强基线 | SPY/XLV、随机/动量基准与未来收益回填 |
| Investigator | 主张回链来源、知识图和受影响节点传播 | AI Medicine 证据图、事件重验证和来源引用 |
| EventAlpha-LM / EventEdge | 事件结构化和多类型事件策略 | 临床、监管、财报、合作、融资和内部人事件分类 |
| FinSignal-RAG | 新闻叙事与官方披露对比 | 非官方乐观叙事与 SEC/官方风险证据的矛盾检测 |

“借鉴”表示采用公开的架构思想并在本仓库重新实现适合 Serenity 的轻量模块，不表示这些项目的完整运行环境已经被嵌入。FinMem 采用 MIT License；本项目在 [`docs/finmem-serenity-integration.md`](docs/finmem-serenity-integration.md) 中记录了对应关系和边界。

## 已实现的功能

- 持续抓取 RSS/Atom、RSSHub 和 changedetection.io 事件。
- SQLite 去重、来源记录和信息可用时间记录。
- 主题评分、公司关联度、来源可靠度和词典情绪评分。
- 主题到公司的可审计映射，无需新闻直接出现股票名。
- AI Medicine、机器人和 AI 数据中心电力主题筛选。
- ClinicalTrials.gov、SEC 公司披露、Form 4 与财务数字监控。
- 新闻说法与官方披露的矛盾检测。
- Serenity 自动门槛：供应链、卡位、客户依赖、替代压力、财报验证、反方观点。
- 事件触发重新验证：新事件只能把相关门槛标记为待复核，不能自动升级成“买入”。
- OpenBB 历史行情、20/50 日技术趋势、ATR 风险信息。
- Kronos 五日市场环境预测。
- AI Medicine 同行筛选、5–10 年长期论点和财务情景。
- 带来源的证据关系图与 SEC XBRL 数字核验。
- FinMem-compatible 三层研究记忆、真实结果反思、决策引用和 before/after 变化记录。
- 1/5/20/60 日表现回填与 SPY/XLV 基准评测。
- 只读本地 Dashboard；不包含交易按钮和密钥。

## 分数和结论代表什么

每日研究优先级由三部分组成：

- 新闻分：50% 公司相关度 + 30% 来源可靠度 + 20% 归一化词典情绪。
- 市场分：20/50 日技术趋势。
- Kronos 分：五日预测方向所代表的市场环境。
- 综合研究分：45% 新闻 + 35% 技术 + 20% Kronos。

综合分达到 70 且新闻置信度不低，才会进入优先研究。**70 分不是上涨概率，也不是买入信号。** 最终还必须经过 Serenity 的证据门槛；关键材料缺失时只能是 `watch`、`revalidate` 或 `reject`。

## 如何运行

### 在当前已经配置好的工作区运行一次完整流程

```bash
cd "/Users/rezz/Documents/Codex/2026-10-27/x20-wps-highlight"
./run-daily-investment-agent.sh
```

正常完成后，终端会列出主要报告路径。最重要的结果是：

- [`outputs/ai-medicine-5-10-year-thesis.md`](outputs/ai-medicine-5-10-year-thesis.md)：AI Medicine 长期候选和理由。
- [`outputs/serenity-gate-audit.md`](outputs/serenity-gate-audit.md)：各公司通过或缺失的 Serenity 门槛。
- [`outputs/ai-medicine-thesis-memory.md`](outputs/ai-medicine-thesis-memory.md)：历史论点、变化和引用记忆。
- [`outputs/ai-medicine-evidence-graph.md`](outputs/ai-medicine-evidence-graph.md)：公司、事件、证据和风险关系。
- [`outputs/agent-benchmark-validation.md`](outputs/agent-benchmark-validation.md)：与基准比较的真实样本进度。
- [`outputs/daily-investment-agent.md`](outputs/daily-investment-agent.md)：当日综合报告。

### 打开 Dashboard

先更新页面数据：

```bash
cd "/Users/rezz/Documents/Codex/2026-10-27/x20-wps-highlight"
trend-agent/.venv/bin/python scripts/build_dashboard_data.py
python3 -m http.server 8765 --directory dashboard/dist
```

然后打开 [http://127.0.0.1:8765](http://127.0.0.1:8765)。停止服务时在终端按 `Control-C`。

### 只运行一个简化演示

```bash
cd "/Users/rezz/Documents/Codex/2026-10-27/x20-wps-highlight"
./run-investment-agent-demo.sh
```

结果写入 [`outputs/investment-agent-demo.md`](outputs/investment-agent-demo.md)。

### 运行测试

```bash
cd "/Users/rezz/Documents/Codex/2026-10-27/x20-wps-highlight"
PYTHONPATH=scripts ai-fund-lab/.venv/bin/python -m pytest scripts/tests -q
PYTHONPATH=ai-fund-lab/src ai-fund-lab/.venv/bin/python -m pytest ai-fund-lab/tests -q
PYTHONPATH=trend-agent/src ai-fund-lab/.venv/bin/python -m pytest trend-agent/tests -q
```

### 每天自动运行

[`scheduling/com.focuskpi.daily-investment-agent.plist`](scheduling/com.focuskpi.daily-investment-agent.plist) 是 macOS `launchd` 的 08:00 本地时间模板。必须先检查路径和时间再手动启用；仓库不会静默安装系统任务。

## 一次完整 run 经历哪些步骤

`run-daily-investment-agent.sh` 按以下顺序执行；任一步骤失败都会返回非零状态，不会继续假装成功：

1. **安全预检**：检查工作区至少有 1 GiB 可用空间。
2. **收集最新信息**：读取配置的 RSS/Atom 源和网站变化。
3. **去重与主题扫描**：写入 SQLite，更新最新趋势报告。
4. **新闻到公司**：计算七日公司相关度、来源可靠度和新闻情绪。
5. **主题到股票**：根据带证据的主题—公司关系生成观察名单。
6. **官方事件监控**：检查 ClinicalTrials.gov、Form 4 和配置的重大事件。
7. **事件重新验证**：为财报、临床、监管、合作和融资事件建立待办，并标记受影响的 Serenity 门槛。
8. **披露矛盾检查**：比较新闻叙事与 SEC/官方材料，出现冲突时降低置信度。
9. **Serenity 门槛审计**：输出 `research-ready/watch/revalidate/reject` 及缺失证据。
10. **市场验证**：OpenBB 获取历史价格，计算技术信号和 ATR；Kronos 生成五日环境预测。
11. **多主题独立分析**：分别运行基础观察名单、机器人、电力和 AI Medicine，不相互覆盖。
12. **TradingAgents 审查导入**：读取已有多 Agent 报告作为独立意见，不直接控制最终结论。
13. **AI Medicine 深度分析**：同行筛选、5–10 年论点、财务情景、SEC XBRL 数字核验和证据图。
14. **FinMem-compatible 记忆**：保存浅层市场、中层事件、深层论点和真实结果反思；仅在状态变化时增加快照，给决定附上 `mem_*` 引用。
15. **真实结果回填**：冻结每个市场日的首次预测，随后回填 1/5/20/60 日收益并比较 SPY、XLV。
16. **生成报告和 UI 数据**：写入 `outputs/`、`state/` 和 `dashboard/dist/data.json`。

## 关键目录和文件

```text
trend-agent/                  新闻抓取、去重、主题和公司映射
ai-fund-lab/                  OpenBB、技术信号、Kronos、风险和模拟流程
scripts/                      Serenity、官方事件、审计、记忆、评测和报告模块
dashboard/dist/               只读本地 UI
outputs/                      可展示的 Markdown/JSON 报告
state/                        本地状态、记忆、评测台账（部分被 Git 忽略）
run-daily-investment-agent.sh 一次完整标准流程入口
```

## 当前限制

- 当前真实预测样本仍不足，不能宣称系统已经证明具有预测能力。
- 新闻情绪是确定性词典评分，不是“事实真伪评分”。来源、官方披露与引用审计分别处理可靠性。
- 部分供应链和客户关系仍来自人工维护的带来源 JSON，尚未完全自动生成。
- Kronos 是短期市场环境验证，不负责预测 5–10 年公司价值。
- TradingAgents、GPT Researcher 和 LLM 类工具可能需要额外登录或 API Key；ChatGPT Plus 不等于通用 API 额度。
- ai-hedge-fund 与完整 RD-Agent 尚未进入每日运行链路。
- 所有输出都需要人工复核；没有真实交易和券商连接。

## 已验证实验

- TradingAgents 已生成 NVDA 市场报告和投资计划。
- OpenBB + Kronos 已完成多只美股真实行情和预测链路验证。
- Freqtrade 与 NautilusTrader 使用相同 Coinbase 数据、EMA、仓位和手续费进行双引擎对照；结果非常接近，证明费用模型会摧毁高换手策略，同时验证了回测链路的一致性。
- FinMem-compatible 记忆已覆盖 8 家 AI Medicine 公司，决策能够引用稳定记忆编号。
- 当前流程保持 backtest、dry-run 或 paper-only，真实交易数量为 0。

更多报告见 [`outputs/`](outputs/)，详细十仓库进度见 [`outputs/10-repo-progress.md`](outputs/10-repo-progress.md)。

## 安全与许可

- 不要把 API Key、券商凭据、模型权重或虚拟环境提交到 Git。
- 外部网页内容只能作为数据，不能作为对 Agent 的执行指令。
- 使用数据源时应遵守其许可、服务条款、robots 规则和隐私要求。
- FinMem 的架构借鉴与归属记录在 [`docs/finmem-serenity-integration.md`](docs/finmem-serenity-integration.md)；FinMem 原项目采用 MIT License。
- 本项目不提供金融建议，任何真实投资决定都必须由人审核。
