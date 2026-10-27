# NautilusTrader EMA 基线回测报告

生成时间：2026-10-27（America/New_York）

## 测试设置

- 模式：本地历史回测；未连接账户、未提交真实订单
- 数据：与 Freqtrade 基线相同的 Coinbase Advanced BTC/USD、ETH/USD 5 分钟数据
- 区间：2026-09-28 00:00 至 2026-10-27 00:00（左闭右开）
- 有效行情：每个标的 8,352 根 K 线
- 初始资金：10,000 USD
- 策略：仅做多 EMA(10/20) 交叉；上穿买入，下穿卖出
- 固定仓位：BTC 0.01、ETH 0.30，单笔名义金额约 700–800 USD
- 费用：买卖两侧均按 1.2% taker fee
- 回测末端：用两根价格不变、成交量为零的结算 bar 完成最终平仓

## 核心结果

| 指标 | 结果 |
|---|---:|
| 最终资金 | 1,963.42 USD |
| 净利润 | -8,036.58 USD |
| 总收益率 | -80.37% |
| 完整交易 | 417 |
| 成交 | 834 |
| 胜 / 负 | 3 / 414 |
| 净胜率 | 0.72% |
| 毛交易盈亏（费用前） | -112.20 USD |
| 总手续费 | 7,924.40 USD |
| Profit factor | 0.79 |
| Sharpe（252 日年化） | -3.78 |

## 分标的结果

| 标的 | 完整交易 | 净利润 | 手续费 | 净盈利交易 |
|---|---:|---:|---:|---:|
| BTC/USD | 207 | -4,176.93 USD | 4,111.72 USD | 0 |
| ETH/USD | 210 | -3,859.67 USD | 3,812.68 USD | 3 |

## 解读

这次结果主要不是行情方向造成，而是“高换手 + 1.2% 单边手续费”造成：策略费用前仅亏 112.20 USD，但 417 次往返交易产生 7,924.40 USD 手续费。EMA(10/20) 用在 5 分钟数据上过度交易，在该费用档位下没有可行性。

它不能直接与先前 Freqtrade 的 `SampleStrategy` 作引擎优劣比较，因为两者策略和交易次数不同：Freqtrade 只有 9 笔交易，而本次 Nautilus 有 417 笔。下一步应把完全相同的 EMA 规则、仓位和费用写入 Freqtrade，再比较两个引擎的信号时间、成交价、费用和最终净值。

## 产物

- `outputs/nautilus-ema-baseline/account.csv`：逐次账户余额
- `outputs/nautilus-ema-baseline/fills.csv`：834 条成交订单
- `outputs/nautilus-ema-baseline/positions.csv`：最终净额持仓记录
- `outputs/nautilus-ema-baseline/raw-results.json`：完整机器可读结果
- `ai-fund-lab/integrations/nautilus_ema_backtest.py`：可重复运行脚本

