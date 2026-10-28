# 十仓库交易系统进度

更新时间：2026-10-28（America/New_York）

> “已安装”不等于“已接入”。只有数据或信号进入本地 `ai-fund-lab` 主流程，才标记为已接入。

| # | 项目 | 用途 | 安装 | 验证 | 接入主流程 |
|---|---|---|---|---|---|
| 1 | TradingAgents | 多智能体研究、辩论与投资建议 | ✅ | ✅ NVDA 报告 | ⏳ 报告已产出，待结构化导入 |
| 2 | ai-hedge-fund | 多代理基本面/估值决策 | ✅ Python 3.12 环境 | ✅ CLI 启动 | ⛔ 实际分析需 Financial Datasets + LLM API Key |
| 3 | daily_stock_analysis | 每日行情、新闻、LLM 仪表盘与推送 | ✅ | ✅ AAPL 无密钥 dry-run | ⏳ |
| 4 | Kronos | K 线时序预测 | ✅ | ✅ NVDA/AAPL/MSFT | ✅ 5 日收益过滤器 |
| 5 | Qlib + RD-Agent | 因子研究、训练、回测自动化 | ✅ Qlib + RD-Agent 环境 | ✅ Qlib 导入、RD-Agent CLI | ⛔ 完整循环需 Linux/Docker + LLM/Embedding |
| 6 | OpenBB | 统一市场数据入口 | ✅ | ✅ 三只美股真实行情 | ✅ 数据提供器 |
| 7 | CCXT | 加密交易所统一 API | ✅ | ✅ Kraken 公共 BTC/USD | 不接美股主流程 |
| 8 | Freqtrade | 加密策略回测与执行 | ✅ Python 3.12 | ✅ Coinbase 29 日正式基线回测 | 独立加密分支 |
| 9 | Hummingbot | 做市与加密执行 | ✅ 项目内 Conda 环境 | ✅ CLI 与 paper-trade 模块 | 独立加密分支 |
| 10 | NautilusTrader | 事件驱动回测及执行引擎 | ✅ | ✅ Coinbase 29 日 EMA 基线回测 | 独立加密分支 |

## 当前已验证结果

- `ai-fund-lab`：风险规则与模拟订单骨架，3 个单元测试通过。
- TradingAgents：通过 ChatGPT 登录运行，已生成 NVDA 市场报告和投资计划。
- OpenBB + Kronos：读取 NVDA、AAPL、MSFT 真实行情并完成预测；5 日预测收益分别为 -1.65%、-1.59%、-1.35%，全部低于 0% 门槛，因此本轮为 `hold`，0 笔订单。
- daily_stock_analysis：AAPL 取得 41 条日线并写入本地 SQLite；无 API Key 时按设计跳过 LLM、新闻和通知。
- CCXT：无 Key 从 Kraken 公共接口读取 BTC/USD 行情。
- Freqtrade：启用 `dry_run=true`，禁用 Telegram/API server，成功载入 Kraken 公共市场。
- Freqtrade 正式基线：Coinbase 公共数据，BTC/USD + ETH/USD，29 天、5 分钟周期；9 笔交易，总收益 -3.26%，最大回撤 3.55%。默认示例策略不合格，仅验证回测链路。
- Hummingbot：本地源码与 61 个 Cython 模块编译成功，`hbot --help` 和 paper-trade 模块验证通过；没有配置交易所凭据。
- Qlib：PyQLib v0.9.7 可导入；RD-Agent 1.0.0 已安装，`rdagent --help` 可用。完整量化研究循环受官方 Linux/Docker 要求及 LLM/Embedding 配置限制。
- ai-hedge-fund：2.6.2 已安装，`aihf --help` 可用。当前上游版本不支持 Ollama；实际分析同时需要 Financial Datasets API Key 和受支持模型供应商的 API Key。ChatGPT Plus 登录不能替代 API Key。
- Ollama：0.40.12 本地服务和 `llama3.2:1b`、`llama3.2:3b` 模型已安装；2026-10-28 再次确认服务可启动并识别 CPU 后端，但 Metal 仍无法创建 command queue，尚未通过生成测试。
- NautilusTrader：使用与 Freqtrade 相同的 Coinbase BTC/USD + ETH/USD 5 分钟数据完成 29 日 EMA(10/20) 基线；417 笔完整交易，总收益 -80.37%，其中 7,924.40 USD 为手续费，证明该高换手策略在 1.2% 单边费用下不可行。
- 跨引擎验证：将相同 EMA、固定数量和费用放入 Freqtrade，得到 418 笔交易、-80.56%；与 NautilusTrader 仅差一笔 ETH 交易和 19.04 USD，验证两个引擎结果一致。

## 完成口径

- 编号仓库安装并完成最小验证：10/10。这里的“最小验证”是安装、导入或 CLI 启动成功，不代表每个项目都已跑出投资报告。
- 可在当前无新增 Key 条件下产出分析或回测结果：TradingAgents（使用既有 ChatGPT 登录流程）、daily_stock_analysis、Kronos、OpenBB、Freqtrade、NautilusTrader。Qlib、CCXT、Hummingbot 已完成组件或公共数据链路验证，但本轮没有单独投资报告。
- 暂不能跑完整分析：ai-hedge-fund（两个 API Key）；RD-Agent（Linux/Docker 与模型服务）。
- 已接入统一美股主流程：2/10（OpenBB、Kronos）。
- 本地真实交易：0；当前全部为 dry-run / paper-only。
