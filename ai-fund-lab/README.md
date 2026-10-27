# AI Fund Lab（模拟交易版）

这是对帖子中“10 个仓库拼成 AI 对冲基金”思路的安全实现。当前版本只做研究和本地模拟成交，**不会发送真实券商订单**。

## 当前已实现

- 可替换行情源：内置确定性模拟行情；可选 Yahoo Finance
- 可解释的趋势信号：20/50 日均线 + ATR
- 确定性风险控制：单笔风险、单仓上限、总敞口和持仓数量上限
- 本地 Paper Broker：模拟成交并保存账户状态
- 每次运行生成完整 JSON 审计报告
- 配置明确拒绝 `allow_live_trading=true`

## 第一步：创建环境

```bash
cd ai-fund-lab
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

如果电脑暂时不能联网安装构建依赖，可以直接运行：

```bash
PYTHONPATH=src python -m ai_fund_lab.cli --config config.example.json
```

## 第二步：无网络演示

只生成建议，不改变模拟账户：

```bash
ai-fund-lab --config config.example.json
```

执行本地模拟成交：

```bash
ai-fund-lab --config config.example.json --execute-paper
```

报告保存在 `reports/`，模拟账户保存在 `state/paper.json`。

## 第三步：使用延迟市场数据

```bash
python -m pip install -e '.[market-data]'
cp config.example.json config.local.json
```

将 `config.local.json` 中的 `data_provider` 改成 `yfinance`，再运行 dry-run。Yahoo Finance 适合研究演示，不应被当成生产交易数据源。

## 第四步：使用 OpenBB 数据层

```bash
python -m pip install -e '.[openbb-data]'
ai-fund-lab --config config.openbb.json
```

该配置通过 OpenBB 的统一接口明确选择 `yfinance` provider。数据源故障会直接报错，不会悄悄切换供应商，以免回测和线上运行读取不同数据。

## 后续接入顺序

1. OpenBB：已接入行情数据层，下一步扩展基本面。
2. TradingAgents：已独立运行，下一步输出标准化信号，不获得订单权限。
3. Kronos：作为一个可回测的附加信号，不解释为真实概率。
4. Alpaca Paper：仅接模拟账户，增加幂等订单 ID、交易时段和对账。
5. RD-Agent/Qlib：离线因子研究，与每日交易进程隔离。
6. NautilusTrader：当策略通过滚动回测和长期模拟后，再替换执行引擎。

Freqtrade、Hummingbot 和 CCXT 属于加密交易分支，不应与美股 MVP 混在同一个进程中。

## Kronos 隔离过滤器

Kronos 使用独立 Python 3.11 环境，并通过子进程返回一个 5 日预测收益分数：

```bash
ai-fund-lab --config config.kronos.json
```

当预测收益低于 `kronos_min_return` 时，原始买入信号会降级为 `hold`。这个数值是模型采样后平均路径的预测收益，**不是上涨概率**。在完成滚动样本外回测前，它只能充当研究过滤器。

## 安全边界

- 不把 API key 写进配置或仓库。
- 不运行真实交易。
- LLM 和预测模型只能生成 `Signal`，不能调用 Broker。
- Broker 只接受经过 `risk.py` 计算的 `OrderIntent`。
- 在接真实模拟券商前，必须加入重复订单保护、开盘日历、滑点、手续费和每日对账。
