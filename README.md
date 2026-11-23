# Serenity Trade Research Agent

一个本地优先、可持续运行、带来源和审计记录的投资研究 Agent。当前跟踪 **AI Medicine** 和 **NVIDIA 公司重大新闻**：系统持续收集前沿信息，把事件映射到相关公司，用 Serenity/Aleabit 方法检查长期投资逻辑，再用市场数据、Kronos 预测、财务情景和独立 Agent 报告交叉验证。

> 当前运行范围为 AI Medicine 与 NVIDIA 公司重大新闻。NVIDIA 主题覆盖产品、客户、财报、出口管制、管理层变动、董事会调查及声誉/法律事件；机器人、AI 数据中心电力、光互连和广义生物科技的
> 历史结果保留用于审计，但不再进入新的每日抓取、LLM 分析、市场验证或 UI 推荐。

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
RSS / RSSHub / changedetection.io / OpenAlex / PubMed / FDA / SEC / ClinicalTrials.gov / Form 4
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
| [TradingAgents](https://github.com/TauricResearch/TradingAgents) | 市场、情绪、新闻、基本面、多空辩论、交易员、三种风险角色和组合经理 | **完整验证层**；已有报告按角色结构化导入，新审查按候选池轮换运行，不能绕过 Serenity 硬门槛 |
| [GPT Researcher](https://github.com/assafelovic/gpt-researcher) | 对高优先级主题执行带来源的深度网页研究 | **适配器已实现**；启用时需要单独模型配置 |
| [changedetection.io](https://github.com/dgtlmoon/changedetection.io) | 监控重要网页变化 | **Webhook 接口已实现**，变化进入 `trend-agent` |
| [RSSHub](https://github.com/DIYgod/RSSHub) | 将不同网站转换成统一 RSS 信息源 | **Feed 接口已实现**，可接自建 RSSHub 路由 |
| Serenity/Aleabit skills | 供应链卡位、选股、研究流程、进出场、仓位和风险框架 | **方法论已转成确定性门槛**；当前核心使用 research-process、stock-selection 和 chokepoint-thesis |
| [OpenAlex](https://docs.openalex.org/) + [PubMed](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | 追踪前沿论文、作者、机构、基金与新技术方向 | **直接接入科研发现层**；技术重合只能产生公司候选，不能自动成为商业证据 |
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

十个仓库均完成最小安装或启动验证。每日研究主流程直接使用 OpenBB、Kronos，并完整导入 TradingAgents 的角色级报告；TradingAgents 模型审查采用轮换/事件触发方式，避免每天无条件消耗订阅额度。其余仓库是独立验证、未来扩展或加密回测分支。详细状态见 [`outputs/10-repo-progress.md`](outputs/10-repo-progress.md)。

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

### FinRobot V2 事件分析（历史实验，当前每日流程已停用）

以下内容保留用于复现实验，不属于当前每日运行链路。当前由 Codex 订阅自动任务完成 Serenity 证据审查，不需要 FinRobot 或 Gemini API Key。FinRobot 官方源码保存在 `work/FinRobot`，新闻事件适配器位于
`scripts/finrobot_event_analyst.py`。接入边界是：规则先筛选主题分达到 70 的事件，
FinRobot 的 provider registry、运行配置验证与模型工厂驱动一个有边界的 Event Analyst，
输出结构化的事实、推断、公司影响、收入传导路径、反方证据和引用。这里不启动完整的
多代理 equity-research 团队，因为每天每条新闻都运行整套工具链会过慢且成本过高；
确定性代码计算“商业影响研究优先级”，随后把有来源的重大变化交给 Serenity 重审。
FinRobot 不能直接通过 Serenity 门槛、改变评级、决定仓位或创建订单。

没有模型或数据供应商配置时，每日流程使用 `pending` 模式，只保存可审计任务：

```bash
python3 scripts/finrobot_event_analyst.py \
  --trends trend-agent/reports/daily/trends/latest-trends.json \
  --theme-links trend-agent/reports/daily/theme-stocks/theme-stock-links.json \
  --serenity trend-agent/serenity-assessments.json \
  --provider pending \
  --json-output state/finrobot-event-analysis.json \
  --markdown-output outputs/finrobot-event-analysis.md
```

网络可用时安装隔离环境：

```bash
./scripts/setup_finrobot.sh
```

配置 FinRobot 模型后启用真实分析。密钥只通过当前终端环境传给隔离的
`finrobot_event_runner.py`，不会写入仓库、任务 JSON 或报告。FMP 是可选的；未设置时
FinRobot V2 会退回 yfinance：

```bash
read -s GEMINI_API_KEY
export GEMINI_API_KEY
FINROBOT_PROVIDER=finrobot-cli \
FINROBOT_MODEL='gemini:gemini-3.8-flash' \
./run-daily-investment-agent.sh
unset GEMINI_API_KEY
```

若需要定时运行或让本地 Agent 启动流程，可将新生成的 Key 保存到 macOS Keychain，
不要保存为仓库内的明文文件：

```bash
./scripts/save_gemini_key_to_keychain.sh
./scripts/run_daily_with_keychain.sh
```

Keychain service 名称为 `serenity-trade-gemini`。运行脚本只把密钥注入子进程，
不会把它打印或写入报告；macOS 首次读取时可能要求用户授权。

若 macOS 将 Terminal 与 Codex 的 Keychain 查询权限隔离，可执行一次：

```bash
./scripts/export_keychain_to_local_secret.sh
```

它会创建权限为 `600` 的 `.secrets/gemini_api_key`；`.secrets/` 已被 Git 明确忽略。
`run_daily_with_keychain.sh` 优先读取 Keychain，访问不到时才读取该本地私密文件。

Gemini 通过 Google 官方 OpenAI-compatible endpoint 注册为 FinRobot 的自定义供应商。
当 `gemini-3.8-flash` 暂时返回 503 时，runner 会尝试
`gemini-3.5-flash-lite`；可通过
`FINROBOT_FALLBACK_MODELS` 覆盖此顺序。503、429、配额限制和请求超时都会触发
同供应商备用模型切换；批处理会逐条显示完成或错误状态。每个模型默认最多等待
45 秒，每条新闻最多等待 120 秒，可通过 `FINROBOT_REQUEST_TIMEOUT` 调整。
也可继续使用 `FINROBOT_LLM_API_KEY` 覆盖供应商专用变量。不要把密钥粘贴到聊天、
README、`.env` 或 Git；曾经公开过的密钥应先在 Google AI Studio 撤销并重新生成。

输出位于 `state/finrobot-event-analysis.json` 和
`outputs/finrobot-event-analysis.md`。任何 `pending-config` 或 `error` 都会在报告和 UI 中明确显示，
不会被当成完成的 LLM 研究。

## 已实现的功能

- 持续抓取 RSS/Atom、RSSHub 和 changedetection.io 事件。
- SQLite 去重、来源记录和信息可用时间记录。
- 主题评分、公司关联度、来源可靠度和词典情绪评分。
- 主题到公司的可审计映射，无需新闻直接出现股票名。
- AI Medicine 与 NVIDIA 公司新闻主题筛选；AI Medicine 当前覆盖数据/诊断、药物发现、医学影像、手术机器人、临床试验数据和医疗算力基础设施。
- FDA 官方 AI-enabled medical-device CSV 每日快照、公司/子公司映射和新增授权检测；监管记录只作为产品证据，不直接产生投资建议。
- ClinicalTrials.gov、SEC 公司披露、Form 4 与财务数字监控。
- 新闻说法与官方披露的矛盾检测。
- Serenity 自动门槛：供应链、卡位、客户依赖、替代压力、财报验证、反方观点。
- 事件触发重新验证：新事件只能把相关门槛标记为待复核，不能自动升级成“买入”。
- 事件日期机器校验：发布时间、首次发现时间和运行 as-of 不一致时隔离事件，不允许它使 Serenity 门槛失效。
- OpenBB 历史行情、20/50 日技术趋势、ATR 风险信息。
- Kronos 五日市场环境预测。
- AI Medicine 同行筛选、5–10 年长期论点和财务情景。
- AI Medicine 当前以同一口径深审 13 家公司：原始 8 家直接/纯主题候选，加上 GEHC、RDNT、ISRG、IQV、NVDA 五个跨细分对照。原始 1–8 编号只代表首批候选内部论点顺序，不是全市场排名。
- 当前结论不写死在 README：以每日自动生成的 `outputs/ai-medicine-5-10-year-thesis.md`（门槛制研究优先级）和 `dashboard/dist/top5.html`（前沿新闻触发 → Serenity 研究意见）为准。截至目前，**没有任何公司通过全部 Serenity 门槛**；各层级表示下一步研究动作，不是买入清单。
- Hidden Gems 小中盘筛选：市值、纯业务、卡位、客户、财报、资金安全和当前关注度；缺少流动性时明确阻止投资结论。
- 近60个交易日平均成交额与波动核验；市场源失败时使用带时间戳缓存并明确显示状态。
- 带来源的证据关系图与 SEC XBRL 数字核验。
- FinMem-compatible 三层研究记忆、真实结果反思、决策引用和 before/after 变化记录。
- 1/5/20/60 日表现回填与 SPY/XLV 基准评测。
- 只读本地 Dashboard；不包含交易按钮和密钥。

## 新兴信号雷达与动态受益者映射

预设主题只能跟踪已知方向。这两个模块用来发现**还没人写进配置的新主题**，并找出真正参与其中的上市公司。

- **新兴信号探测器**（`scripts/emerging_signal_detector.py`）：不预设主题。按文章总量折算基线，统计标题中每个词和短语的提及量，找出突然暴增、出现在至少两个独立来源的话题；新接入信息源的历史积压不计入暴增。广覆盖雷达源（WHO、medRxiv、bioRxiv、STAT、BioPharma Dive）存放在 `state/radar-news.db`，不影响 AI Medicine 评分。输出 `outputs/emerging-signals.md`。
- **动态受益者映射**（`scripts/beneficiary_mapper.py`）：在截至当日的 SEC 全文检索和 ClinicalTrials.gov 中查找提到该话题的公司，按行业代码和 8-K 事项编号区分：医疗公司以事件公告形式提及（7.01/8.01）的进入候选，只在财报中提及（2.02）的多为业务受影响。设置 `SEC_USER_AGENT`（填你自己的联系方式）后会读取原文句子辅助判断。输出 `outputs/beneficiary-map.md`，候选需要再经过 Serenity 筛选。
- **时间机器回放**（`scripts/backfill_preprints.py` + `scripts/replay_case.py`）：两个模块都不使用语言模型，因此可以放回历史日期运行而不泄漏后来的信息。

```bash
# 新冠案例：回填 2019-11 至 2020-02 预印本，逐日回放探测、映射和之后的整篮表现
trend-agent/.venv/bin/python scripts/backfill_preprints.py --start 2019-11-01 --end 2020-02-15 --database state/replay/covid-2020.db
PYTHONPATH=scripts ai-fund-lab/.venv/bin/python scripts/replay_case.py --case covid-2020 \
  --database state/replay/covid-2020.db --start 2020-01-10 --end 2020-02-10
```

新冠回放结果见 `outputs/replay-covid-2020.md`：只用预印本标题，系统在 2020-01-26 确认新话题，当天 SEC 文件中可找到的有能力受益公司为 Moderna 和 Vir。单个案例不能证明普遍的预测能力，必须同时检验结果不好的案例，见 `outputs/replay-*.md`。

## 分数和结论代表什么

每日研究优先级由三部分组成：

- 新闻分：50% 公司相关度 + 30% 来源可靠度 + 20% 归一化词典情绪。
- 市场分：20/50 日技术趋势。
- Kronos 分：五日预测方向所代表的市场环境。
- 综合研究分：45% 新闻 + 35% 技术 + 20% Kronos。

综合分达到 70 且新闻置信度不低，才会进入优先研究。**70 分不是上涨概率，也不是买入信号。** 最终还必须经过 Serenity 的证据门槛；关键材料缺失时只能是 `watch`、`revalidate` 或 `reject`。

AI Medicine 同行的“研究优先分”使用另一套公开公式：AI Medicine 相关性 20% + 专有数据/模型 20% + 工作流锁定 15% + 商业验证 15% + 多节点控制 10% + 财务韧性 10% + 原始证据覆盖 10%。该分数只决定先研究谁；证据完整度、证据质量、估值和硬门槛分别展示，不能用高总分覆盖缺失证据。

“有据分”只诊断证据成熟度，不参与潜力排名或自动升级。资料抓取越完整，完整度和证据质量越高，因此系统会明确承认数据覆盖偏差，并逐项列出缺失门槛而不是用并列总分强行排序。第三方证据采用固定轮次覆盖；13家没有完成同一证据类别前，横向比较保持 provisional。优先深挖要求研究优先分≥75、完整度≥50、证据质量≥50且没有 `revalidate`；升级到“优先关注”还要求连续财报验证、客户依赖和瓶颈通过、有来源反证、无未解决重大事件、完整度与证据质量均≥70，以及与商业模式匹配的估值安全边际。当前研究政策暂定安全边际为基准情景每股年化回报≥12%、悲观情景≥-10%，且净负债和稀释已由原始材料核验。人工情景只作排除性检验：不通过可以阻止升级，通过不能自动升级。

## 如何运行

### 在当前已经配置好的工作区运行一次标准流程

```bash
cd "/Users/rezz/Documents/Codex/2026-10-27/x20-wps-highlight"
./run-daily-investment-agent.sh
```

默认是 `collect` 模式：抓取、规则计算、市场数据、证据包和报告均会更新，但不会调用 Claude、TradingAgents 或任何模型 API，适合每天低成本运行。

只有需要重新做深度辩论和模型抽取时才运行：

```bash
AGENT_MODE=deep ./run-daily-investment-agent.sh
```

`deep` 模式仍使用已有订阅登录，并缓存未变化的结果；它不会连接券商。科研发现报告位于
[`outputs/scientific-frontier.md`](outputs/scientific-frontier.md)，结构化关系图保存在
`state/scientific-frontier.json`。

第一优先级的“科研到商业化”链路由
[`scripts/science_commercialization_graph.py`](scripts/science_commercialization_graph.py) 构建。它把论文/研究者、
专利或技术许可证据、Form D 融资、8-K 药企付款、IND/ClinicalTrials.gov 临床进展和 SEC XBRL 收入放在同一家公司下，
输出 [`outputs/science-commercialization-graph.md`](outputs/science-commercialization-graph.md) 和
`state/science-commercialization-graph.json`。技术相似只进入发现层；合作公告不等于客户收入；没有原始材料的关系会显示为缺口，
不会被自动打成通过。已经核验的创始人、专利受让或大学许可关系可加入
`trend-agent/science-commercialization-links.json`，且必须附原文、链接和 `verified` 状态。

[`scripts/technology_ownership_agent.py`](scripts/technology_ownership_agent.py) 会先从已保存的 SEC 证据包中提取严格的创始人、
“we own…” 专利组合及独家许可原句，输出 [`outputs/technology-ownership.md`](outputs/technology-ownership.md)。
“可能无法保护专利”“即使我们持有专利”等风险或假设句会被排除。SEC 披露只能证明公司这样披露，仍会保留
“等待 USPTO 专利受让记录或大学技术转移材料独立复核”的缺口。

独立核验队列位于 [`outputs/uspto-assignment-validation.md`](outputs/uspto-assignment-validation.md)。USPTO 在 2026 年要求
Open Data Portal 登录/API Key；当前实现不会绕过认证。可以在官方 Assignment Center 按受让人检索，把 reel/frame、
assignor、assignee、recorded date 和官方 URL 规范化加入 `trend-agent/uspto-assignment-evidence.json`，系统下一次运行就会更新
`independentAssignmentVerified`。没有官方记录时保持 pending，不解释成“没有专利”。

[`scripts/institutional_ownership_agent.py`](scripts/institutional_ownership_agent.py) 监控 SEC Schedule 13D/13G 重要股东。
运行前需要设置 SEC 要求的联系信息：

```bash
SEC_USER_AGENT='SerenityResearch your-email@example.com' \
  trend-agent/.venv/bin/python scripts/institutional_ownership_agent.py
```

或者只配置一次，后续每日脚本自动读取本地且 Git 忽略的文件：

```bash
./scripts/save_sec_user_agent.sh
```

13D/13G 证明重要股东持有超过申报门槛的受益所有权，但不代表这些资金进入公司；因此它与 Form D/增发融资分栏展示。

正常完成后，终端会列出主要报告路径。最重要的结果是：

- [`outputs/ai-medicine-5-10-year-thesis.md`](outputs/ai-medicine-5-10-year-thesis.md)：AI Medicine 长期候选和理由。
- [`outputs/ai-medicine-financial-scenarios.md`](outputs/ai-medicine-financial-scenarios.md)：P/S口径、净负债、EV/EBITDA、OCF收益率，以及 RDNT/SOPH/TEM 带主观权重、稀释和数值假设的五年每股敏感度情景；默认使用“稀释后期望终值财富再年化”，并反推达到安全边际所需价格。这些不是模型预测或目标价。
- [`outputs/fda-ai-devices.md`](outputs/fda-ai-devices.md)：FDA AI 医疗设备清单、GEHC/RDNT/ISRG 映射及 IQV/NVDA 相邻层边界。
- [`outputs/serenity-gate-audit.md`](outputs/serenity-gate-audit.md)：各公司通过或缺失的 Serenity 门槛。
- [`outputs/ai-medicine-thesis-memory.md`](outputs/ai-medicine-thesis-memory.md)：历史论点、变化和引用记忆。
- [`outputs/ai-medicine-evidence-graph.md`](outputs/ai-medicine-evidence-graph.md)：公司、事件、证据和风险关系。
- [`outputs/agent-benchmark-validation.md`](outputs/agent-benchmark-validation.md)：与基准比较的真实样本进度。
- [`outputs/daily-investment-agent.md`](outputs/daily-investment-agent.md)：当日综合报告。
- [`outputs/hidden-gems.md`](outputs/hidden-gems.md)：Serenity 冷门小中盘候选与待验证缺口。
- [`outputs/market-profile-audit.md`](outputs/market-profile-audit.md)：市值、成交额、波动和数据新鲜度审计。
- [`outputs/management-radar.md`](outputs/management-radar.md)：核心人物、8-K 管理层变动、Form 4 买卖及受影响的 Serenity 门槛。
- [`outputs/science-commercialization-graph.md`](outputs/science-commercialization-graph.md)：论文 → 技术归属 → 融资 → 药企付款 → 临床 → 收入的可审计证据链和缺口。
- [`outputs/technology-ownership.md`](outputs/technology-ownership.md)：SEC 原文中的创始人、专利组合和独家许可证据，以及独立复核边界。
- [`outputs/uspto-assignment-validation.md`](outputs/uspto-assignment-validation.md)：待核验的专利受让队列、官方记录和导入状态。
- [`outputs/institutional-ownership.md`](outputs/institutional-ownership.md)：13D/13G 重要股东、持股比例及主动/被动申报类别。
- [`outputs/daily-data-inventory.md`](outputs/daily-data-inventory.md)：新闻、冻结预测、主题队列、回填样本和原始运行文件台账。
- [`docs/blind-research-benchmark.md`](docs/blind-research-benchmark.md)：与通用 GPT/Claude 联网深研进行同股票池、同截止时间盲测的协议；样本成熟前不宣称预测更准。

### 运行 TradingAgents 完整多智能体审查

查看轮换队列但不调用模型：

```bash
python3 scripts/run_tradingagents_full_review.py --plan --limit 5
```

对指定公司运行全部 12 个角色输出（四类分析师、牛熊与经理、交易员、三类风险角色、组合经理）：

```bash
python3 scripts/run_tradingagents_full_review.py --tickers RDNT --force --limit 1 --depth 1
```

默认使用已经登录的 ChatGPT 订阅、`gpt-5.6-luna` 快速模型和 `gpt-5.6-sol` 深度模型。默认单轮辩论已覆盖全部角色；`--depth 3` 或 `5` 会增加辩论轮数，但耗时和额度消耗明显上升。完整报告保存在 `work/TradingAgents/data/logs/reports/`，结构化结果写入 `state/tradingagents-reviews.json` 并显示在股票详情 UI。

深度模式默认最多轮换审查一家公司：

```bash
AGENT_MODE=deep ./run-daily-investment-agent.sh
```

默认七天内不会重复审查同一家公司。普通 `./run-daily-investment-agent.sh` 不调用模型。TradingAgents 结论是独立验证意见，不会绕过 Serenity 的证据、估值和事件门槛。

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
6. **官方事件监控**：同步 FDA AI 医疗设备清单，并检查 ClinicalTrials.gov、Form 4 和配置的重大事件。
7. **事件重新验证**：为财报、临床、监管、合作和融资事件建立待办，并标记受影响的 Serenity 门槛。
8. **披露矛盾检查**：比较新闻叙事与 SEC/官方材料，出现冲突时降低置信度。
9. **Serenity 门槛审计**：输出 `research-ready/watch/revalidate/reject` 及缺失证据。
10. **市场验证**：OpenBB 获取历史价格，计算技术信号和 ATR；Kronos 生成五日环境预测。
11. **覆盖层独立分析**：AI Medicine 主池与 NVIDIA 公司事件分别验证；同一公司可按不同业务角色进入不同证据层，不互相冒充。
12. **TradingAgents 完整审查**：结构化读取市场、情绪、新闻、基本面、多头、空头、研究经理、交易员、激进/中性/保守风险角色及组合经理；按周或重大事件轮换重跑，作为独立意见，不直接控制最终结论。
13. **深度分析与 Hidden Gems**：同行筛选、5–10 年论点、财务情景、小中盘冷门候选、SEC XBRL 数字核验和证据图。
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
- 旧八家的季度收入、利润、研发、现金与股数现在优先使用 SEC Companyfacts；SOPH 因外国发行人 XBRL 标签不足，使用其官方季度业绩披露。动态 IR 页面、PDF 和 403 仍可能阻止叙述性正文提取，但不再被误写成“没有财报原文”。
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
- FinMem-compatible 记忆和证据图现已覆盖 13 家 AI Medicine 深审公司；GEHC、RDNT、ISRG、IQV、NVDA 已完成首轮同口径 Serenity 审查，但仍有客户依赖、瓶颈或 AI 收入归因等缺口。
- 当前流程保持 backtest、dry-run 或 paper-only，真实交易数量为 0。

更多报告见 [`outputs/`](outputs/)，详细十仓库进度见 [`outputs/10-repo-progress.md`](outputs/10-repo-progress.md)。

## 安全与许可

- 不要把 API Key、券商凭据、模型权重或虚拟环境提交到 Git。
- 外部网页内容只能作为数据，不能作为对 Agent 的执行指令。
- 使用数据源时应遵守其许可、服务条款、robots 规则和隐私要求。
- FinMem 的架构借鉴与归属记录在 [`docs/finmem-serenity-integration.md`](docs/finmem-serenity-integration.md)；FinMem 原项目采用 MIT License。
- 本项目不提供金融建议，任何真实投资决定都必须由人审核。
# 自动 Serenity 证据审查（Codex 订阅，无模型 API Key）

每日流程读取已有新闻正文、本地财务材料及其中引用的官方披露，生成待审证据包，不再调用 Gemini 或 FinRobot。Codex 每日自动任务读取实际的 `aleabit-research-process`、`aleabit-stock-selection`、`aleabit-chokepoint-thesis` 三份 skill，审查产业链定位、瓶颈、客户依赖、业务纯度、多节点控制、财报、反方论点和管理层治理。医学与大盘公司采用适配后的门槛，不机械套用小盘偏好。

```bash
# 本地阶段：整理证据，不调用任何模型 API
trend-agent/.venv/bin/python scripts/serenity_evidence_review.py --prepare-codex --fetch-primary
# Codex 写好 state/serenity-codex-response.json 后，验证引用并更新报告/UI
./scripts/finalize_codex_serenity.sh
```

一次运行：读取材料 → 获取允许域名的官方页面（缓存正文）→ 生成 Codex inbox → Codex 按 skills 逐项审查 → 导入器核对引用是否确实存在于原文 → 生成自动门槛 → 叠加未解决的事件风险 → 更新报告与 UI。旧手工配置保留，但不再作为每日 Serenity 基础结论。未解决的事件仍可使门槛进入 revalidate。

- `outputs/serenity-evidence-review.md`：逐项支持证据、反证、缺口与证伪条件。
- `state/serenity-auto-assessments.json`：每日流程使用的自动评估。
- `state/serenity-reviews/`：按输入内容标识保存模型原始输出、引用段落、skill 版本和审查记录；相同输入的成功结果复用。
- `state/serenity-codex-inbox.json`：当天待审公司的索引；每家公司证据包位于 `state/serenity-codex-inbox/`。
- `state/serenity-codex-response.json`：Codex 自动任务生成的结构化审查，导入前必须通过引用校验。
- `state/serenity-source-cache/`：抓取的官方文本。
- UI 中点击股票，展开“Serenity 逐项证据审查”。FinRobot 显示已停用。

限制：Codex 自动任务依赖该机器上的 ChatGPT/Codex 登录和可用额度，不能作为网站后端 API。标题、手工摘要及未成功读取的链接不能代替原始披露；PDF 尚未解析。原文匹配只能证明引用可追溯，不能证明模型推理或数字含义正确；当前没有完整的自动财务数字核验。缺证据会得到 unknown/partial，不等于看空；pass 是研究门槛，不是上涨预测或交易授权。全程保持 dry-run。
