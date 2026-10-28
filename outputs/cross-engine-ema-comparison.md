# Freqtrade vs NautilusTrader 跨引擎 EMA 基准

生成时间：2026-10-27（America/New_York）

## 公平比较条件

- 同一批 Coinbase BTC/USD、ETH/USD 5 分钟数据
- 同一区间：2026-09-28 00:00 至 2026-10-27 00:00
- 同一策略：EMA(10) 上穿 EMA(20) 买入，下穿卖出，仅做多
- 同一固定数量：BTC 0.01、ETH 0.30
- 同一初始资金：10,000 USD
- 同一费用：买入和卖出各 1.2%
- 两个引擎均在区间末尾强制平仓

## 结果对照

| 指标 | Freqtrade | NautilusTrader | 差异 |
|---|---:|---:|---:|
| 完整交易 | 418 | 417 | +1 |
| 最终资金 | 1,944.38 USD | 1,963.42 USD | -19.04 USD |
| 净利润 | -8,055.62 USD | -8,036.58 USD | -19.04 USD |
| 总收益率 | -80.56% | -80.37% | -0.19 pct |
| 费用前盈亏 | -111.84 USD | -112.20 USD | +0.37 USD |
| 总手续费 | 7,943.79 USD | 7,924.40 USD | +19.39 USD |
| 净盈利交易 | 3 | 3 | 0 |

## 分标的对照

| 标的 | Freqtrade 交易 / 净利润 | Nautilus 交易 / 净利润 |
|---|---:|---:|
| BTC/USD | 207 / -4,176.63 USD | 207 / -4,176.93 USD |
| ETH/USD | 211 / -3,879.00 USD | 210 / -3,859.67 USD |

## 结论

两个独立引擎得到几乎相同的结果，说明数据转换、EMA 信号、固定仓位和费用计算链路基本一致。19.04 USD 的最终差异几乎全部来自 Freqtrade 多执行的一笔 ETH 往返交易；两边费用前盈亏仅相差约 0.37 USD。

这也交叉验证了核心结论：问题不是某一个回测引擎，而是该策略在 5 分钟周期产生约 14 笔/日的交易，1.2% 单边费用会吞噬资金。此策略不能进入 paper trading。下一轮应先降低换手（例如 1 小时周期、延长 EMA，或加入波动/趋势过滤），再做费用敏感性测试。

## 产物

- Freqtrade 策略：`work/freqtrade/user_data/strategies/ema_cross_baseline.py`
- Freqtrade 独立配置：`work/freqtrade/user_data/config.ema-comparison.json`
- Freqtrade 原始结果：`outputs/freqtrade-ema-baseline-2026-10-27_21-34-03.zip`
- NautilusTrader 报告：`outputs/nautilus-ema-report.md`
- NautilusTrader 原始结果：`outputs/nautilus-ema-baseline/raw-results.json`

