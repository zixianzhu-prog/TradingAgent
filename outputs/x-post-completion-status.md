# X 帖十项目本地实现：最终状态

更新时间：2026-10-28（America/New_York）

## 结论

十个编号项目均已下载到 `work/`，并完成安装、Python 导入或 CLI 启动级别的最小验证。当前没有连接真实券商，也没有真实下单；执行类项目全部保持 dry-run / paper-only。

“安装完成”和“产生投资报告”是两个不同口径。目前已经产生可读分析或回测结果的是 TradingAgents、OpenBB + Kronos、Freqtrade 和 NautilusTrader。其余项目主要完成了运行环境与链路验证。

## 已生成的报告

- TradingAgents NVDA：`outputs/tradingagents-nvda/market_report.md`
- TradingAgents 投资计划：`outputs/tradingagents-nvda/investment_plan.md`
- OpenBB + Kronos 三股结果：`outputs/ai-fund-lab-results/openbb-kronos-nvda-aapl-msft.json`
- Freqtrade 基线：`outputs/freqtrade-report.md`
- NautilusTrader EMA 基线：`outputs/nautilus-ema-report.md`
- Freqtrade / Nautilus 公平对照：`outputs/cross-engine-ema-comparison.md`

## 尚不能完整运行的两项

### ai-hedge-fund

- 版本 2.6.2 已安装在 `work/ai-hedge-fund/.venv`。
- `aihf --help` 已验证。
- 当前上游代码没有 Ollama provider。
- 实际分析同时依赖 Financial Datasets API Key 和受支持 LLM provider 的 API Key。
- ChatGPT Plus 订阅不等于 OpenAI API 额度，不能直接填入该项目。

### RD-Agent

- 版本 1.0.0 已安装在 `work/RD-Agent/.venv`。
- `rdagent --help` 及 Python 导入已验证。
- 官方完整场景以 Linux 为支持平台，并普遍依赖 Docker。
- 当前 Mac 未运行 Docker daemon，且尚无 RD-Agent 所需的 LLM / Embedding 配置，因此没有伪造“完整跑通”。

## 本地 Ollama

- Ollama 0.40.12 位于 `tools/ollama-v0.40.12/`。
- 模型文件位于 `tools/ollama-models/`。
- 已下载 `llama3.2:1b` 和 `llama3.2:3b`。
- 服务可启动并识别 CPU 后端。
- 2026-10-28 重新启动服务并测试 1B 模型，Metal 仍无法创建 command queue；模型尚未完成一次生成。
- 关闭占用内存较大的应用或重启 Mac 后，运行 `ai-fund-lab/integrations/start_ollama_local.sh`，再执行 `tools/ollama-v0.40.12/ollama run llama3.2:1b` 复测。

## 下一步

1. 关闭占用 GPU/统一内存的应用或重启系统，复测 Ollama 1B；如果仍失败，改用云端 API 或另一台内存更大的机器。
2. 若要运行 ai-hedge-fund，准备 Financial Datasets API Key 和受支持模型 API Key。
3. 若要运行 RD-Agent 完整循环，优先使用 Linux/Docker 环境，再配置 LLM 与 Embedding。
4. 在任何实盘连接前，继续使用 paper-only，并为策略设定最大仓位、最大回撤和人工批准门槛。
