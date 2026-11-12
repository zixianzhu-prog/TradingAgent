# AI Medicine 论点长期记忆

> 记录系统在每次运行时知道什么、排名如何变化、哪些事件让 Serenity 门槛失效。它是审计轨迹，不是预测能力证明。

覆盖 8 家公司；保留 5 个不同状态快照；本次 0 家发生变化，共 0 个字段变化。

## 本次变化

### TEM
- `forecastReturn`：`0.022487` → `0.035017`
### SDGR
- `serenityDecision`：`revalidate` → `research-ready`
- `completenessScore`：`78` → `94`
- `forecastReturn`：`0.031403` → `0.014539`
### RXRX
- `forecastReturn`：`-0.000273` → `0.023607`
### ABCL
- `forecastReturn`：`0.007632` → `0.032754`
### CERT
- `forecastReturn`：`-0.035069` → `-0.015526`
### NTRA
- `forecastReturn`：`-0.005012` → `0.00402`
### SOPH
- `forecastReturn`：`0.037554` → `0.022682`
### GH
- `forecastReturn`：`0.011925` → `0.013013`

## 当前记忆

| 股票 | 排名 | Serenity | 完整度 | 估值 | 融资风险 | 5日环境 |
|---|---:|---|---:|---|---|---:|
| TEM | 1 | research-ready | 94 | premium; execution-sensitive | low | +3.50% |
| SDGR | 2 | research-ready | 94 | premium; execution-sensitive | medium | +1.45% |
| CERT | 3 | research-ready | 94 | growth valuation; requires continued validation | low | -1.55% |
| NTRA | 4 | research-ready | 89 | premium; execution-sensitive | low | +0.40% |
| RXRX | 5 | watch | 69 | pipeline optionality; revenue multiple not decision-useful | medium | +2.36% |
| SOPH | 6 | research-ready | 89 | growth valuation; requires continued validation | high | +2.27% |
| GH | 7 | research-ready | 94 | premium; execution-sensitive | low | +1.30% |
| ABCL | 8 | watch | 80 | pipeline optionality; revenue multiple not decision-useful | medium | +3.28% |

## 决策引用记忆

- **TEM：** `mem_ccd042dd627a`, `mem_f3047466ac1f`, `mem_4645d21f8a09`, `mem_2a86109f8258`, `mem_4bc847966f42`
- **SDGR：** `mem_991e6e2d3045`, `mem_d7409eb7f180`, `mem_1881bdf5663f`, `mem_2941255f8597`, `mem_edb0dda05909`
- **CERT：** `mem_9a084c5b000d`, `mem_8e7729b470a7`, `mem_9c26e964c49e`
- **NTRA：** `mem_bacf9df6c158`, `mem_c72c64a041bb`, `mem_4aa4df572dae`
- **RXRX：** `mem_4812f0dbc752`, `mem_796975290c26`, `mem_4109ca0ee4fa`, `mem_52ab1ba931f5`, `mem_96fef5534ae1`
- **SOPH：** `mem_de4b9d0a0d1a`, `mem_67adcf1bce2e`, `mem_9fdd929ccde9`
- **GH：** `mem_b6e3567c1098`, `mem_f776df745f4f`, `mem_7ca3c4c11e45`
- **ABCL：** `mem_edbcfe2403dd`, `mem_d96018c9348a`, `mem_089b6540b2d3`, `mem_69884890986e`, `mem_66ef8cc43b61`

## 已实现表现反思

| 股票 | 周期 | 实际收益 | 超额 SPY | 超额 XLV | 超额 XBI | 方向正确 |
|---|---:|---:|---:|---:|---:|---|
| TEM | 1 | -0.54% | -1.86% | -0.58% | -1.34% | 否 |
| TEM | 5 | +5.04% | +5.95% | +5.41% | +6.79% | 是 |
| SDGR | 1 | -1.25% | -2.57% | -1.29% | -2.06% | 否 |
| SDGR | 5 | +15.16% | +16.08% | +15.54% | +16.92% | 是 |
| RXRX | 1 | +1.70% | +0.38% | +1.66% | +0.89% | 否 |
| RXRX | 5 | -8.18% | -7.27% | -7.81% | -6.43% | 否 |
| ABCL | 1 | -1.65% | -2.96% | -1.68% | -2.45% | 否 |
| ABCL | 5 | -1.07% | -0.15% | -0.69% | +0.69% | 否 |
