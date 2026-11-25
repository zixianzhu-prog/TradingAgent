# AI Medicine 论点长期记忆

> 记录系统在每次运行时知道什么、排名如何变化、哪些事件让 Serenity 门槛失效。它是审计轨迹，不是预测能力证明。

覆盖 16 家公司；保留 19 个不同状态快照；本次 16 家发生变化，共 18 个字段变化。

## 本次变化

### TEM
- `serenityDecision`：`watch` → `research-ready`
- `completenessScore`：`80` → `90`
- `forecastReturn`：`0.047641` → `0.031048`
### SDGR
- `forecastReturn`：`0.040764` → `0.016518`
### RXRX
- `forecastReturn`：`0.022888` → `0.06802`
### ABCL
- `forecastReturn`：`-0.013603` → `0.005054`
### CERT
- `forecastReturn`：`0.029782` → `0.020307`
### NTRA
- `forecastReturn`：`0.001784` → `0.019825`
### SOPH
- `forecastReturn`：`0.061606` → `0.046369`
### GH
- `forecastReturn`：`0.009973` → `0.011802`
### GEHC
- `forecastReturn`：`-0.005973` → `0.004509`
### RDNT
- `forecastReturn`：`0.014331` → `0.00724`
### ISRG
- `forecastReturn`：`0.006042` → `0.005279`
### IQV
- `forecastReturn`：`0.018277` → `0.014089`
### NVDA
- `forecastReturn`：`0.069464` → `0.103818`
- 关联事件：NVIDIA Board of Directors Establishes National Security and Export Control Oversight Committee；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：NVIDIA Announces Financial Results for Third Quarter Fiscal 2027；影响门槛：cash_generation, cash_runway, clinical_validation, counter_thesis, customer_dependency, dilution, earnings_validation, falsifiers, integration_execution, management_governance, partner_economics, reputation_risk, valuation
- 关联事件：NVIDIA Board Reinstates Jensen Huang as President, CEO and Board Director；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：Jensen Huang’s Net Worth Is Now Down 16% Since Start Of Last Week’s Affairs Scandal - Forbes；影响门槛：counter_thesis, management_governance, reputation_risk
- 关联事件：NVIDIA Announces CEO Transition；影响门槛：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, reputation_risk, valuation
- 关联事件：NVIDIA Expands Commitments With Supply Chain Partners to Support AI Infrastructure Buildout；影响门槛：counter_thesis, customer_dependency, earnings_validation, integration_execution, management_governance, partner_economics, reputation_risk, valuation
- 关联事件：Nvidia-Favored Marvell and Lumentum Announce Merger: What Does This Mean for NVDA? - TradingKey；影响门槛：integration_execution, valuation
- 关联事件：NVIDIA Announces Collaboration With IBM and Fermi National Accelerator Laboratory to Launch Quantum-Classical Codesign Platform, Plus Error-Correction Breakthrough to Advance Practical Quantum Computing；影响门槛：customer_dependency, integration_execution, partner_economics, valuation
- 关联事件：Nvidia CEO Jensen Huang’s image tarnished by board investigation and affair, analysts say - Los Angeles Times；影响门槛：counter_thesis, management_governance, reputation_risk
### HTFL
- `forecastReturn`：`0.050252` → `-0.003072`
### CBLL
- `forecastReturn`：`-0.037874` → `-0.033788`
### CAI
- `forecastReturn`：`0.008277` → `0.039234`

## 当前记忆

| 股票 | 排名 | Serenity | 完整度 | 估值 | 融资风险 | 5日环境 |
|---|---:|---|---:|---|---|---:|
| TEM | 1 | research-ready | 90 | growth valuation; requires continued validation | low | +3.10% |
| SDGR | 2 | watch | 87 | premium; execution-sensitive | medium | +1.65% |
| CERT | 3 | watch | 77 | growth valuation; requires continued validation | low | +2.03% |
| NTRA | 4 | watch | 72 | premium; execution-sensitive | low | +1.98% |
| RXRX | 5 | watch | 82 | pipeline optionality; revenue multiple not decision-useful | medium | +6.80% |
| SOPH | 6 | watch | 77 | growth valuation; requires continued validation | high | +4.64% |
| GH | 7 | watch | 38 | premium; execution-sensitive | low | +1.18% |
| ABCL | 8 | watch | 53 | pipeline optionality; revenue multiple not decision-useful | medium | +0.51% |
| GEHC | None | watch | 77 | not obviously premium on sales; inspect quality and dilution | low | +0.45% |
| RDNT | None | research-ready | 90 | not obviously premium on sales; inspect quality and dilution | low | +0.72% |
| ISRG | None | watch | 69 | premium; execution-sensitive | low | +0.53% |
| IQV | None | reject | 56 | not obviously premium on sales; inspect quality and dilution | low | +1.41% |
| NVDA | None | revalidate | 5 | premium; execution-sensitive | low | +10.38% |
| HTFL | None | research-ready | 90 | premium; execution-sensitive | low | -0.31% |
| CBLL | None | research-ready | 95 | premium; execution-sensitive | high | -3.38% |
| CAI | None | research-ready | 95 | growth valuation; requires continued validation | low | +3.92% |

## 决策引用记忆

- **TEM：** `mem_b2f7497dd1ca`, `mem_f3047466ac1f`, `mem_4645d21f8a09`, `mem_73ee9d76d46b`, `mem_6142f69a49ee`
- **SDGR：** `mem_c9797e9b5e57`, `mem_d7409eb7f180`, `mem_1881bdf5663f`, `mem_3a0adab9c157`, `mem_7b18cddfa888`
- **CERT：** `mem_111db09d9597`, `mem_8e7729b470a7`, `mem_9c26e964c49e`, `mem_0c857c1ccf98`, `mem_67def404f8d1`
- **NTRA：** `mem_78e3f2723cb3`, `mem_c72c64a041bb`, `mem_4aa4df572dae`, `mem_44d3e7afd5f2`, `mem_bd08603fd8ec`
- **RXRX：** `mem_a4bcb0441aa1`, `mem_796975290c26`, `mem_4109ca0ee4fa`, `mem_62b7fd225686`, `mem_5e07ecd75742`
- **SOPH：** `mem_f2d4a82e55c3`, `mem_67adcf1bce2e`, `mem_9fdd929ccde9`, `mem_954257fa7131`, `mem_17edc42fdf86`
- **GH：** `mem_963ae78620b2`, `mem_f776df745f4f`, `mem_7ca3c4c11e45`, `mem_7755551c49d0`, `mem_9129fe8a2eaa`
- **ABCL：** `mem_5835179caec0`, `mem_d96018c9348a`, `mem_089b6540b2d3`, `mem_2d794b9fe771`, `mem_ba3d7fd2e2b8`
- **GEHC：** `mem_7ade5fa7e436`, `mem_62de0a6fe442`, `mem_ed4c4183c556`, `mem_52d867d0dc56`, `mem_cec49c72a160`
- **RDNT：** `mem_2c78cc7c3106`, `mem_87a3ecb0a0fb`, `mem_962e42552623`, `mem_c2d5e50ce1c3`, `mem_7ac11cbeeb2a`
- **ISRG：** `mem_69a7bf48f0de`, `mem_c2d0b38e7bdf`, `mem_4437c75c3fc7`, `mem_8c961ac2e85e`, `mem_531d2e38d861`
- **IQV：** `mem_62e9193a7d7f`, `mem_4d092213a4ee`, `mem_6b5d9f20c75b`, `mem_fc86b9d46e13`, `mem_9f6807f5a141`
- **NVDA：** `mem_b14c9771547a`, `mem_4b356174c4a4`, `mem_5ec2b63ee470`, `mem_12e3dcb1dc70`, `mem_673b5bbef4c9`, `mem_77a5893e9e6e`, `mem_7f9b383aa469`, `mem_d6431821612b`, `mem_811c04bf0ce0`, `mem_90d4523b3386`, `mem_c8255d955688`, `mem_e205baf97f1f`, `mem_0d35488d21aa`, `mem_2a5c91cc7787`
- **HTFL：** `mem_7a63552947ff`, `mem_96341927af15`, `mem_b4ccc7ce7f8c`, `mem_1a0ee63ae78e`, `mem_9dd7a06256cf`
- **CBLL：** `mem_5f4631763ab2`, `mem_19b2ea2b2f50`, `mem_cc0560e6d954`, `mem_96c53706f54c`, `mem_3aecd0790711`
- **CAI：** `mem_949b8e08ad68`, `mem_9b3d785255fe`, `mem_06c169b9b11f`, `mem_f8ea6ca59ac8`, `mem_2e6c625a2243`

## 已实现表现反思

| 股票 | 周期 | 实际收益 | 超额 SPY | 超额 XLV | 超额 XBI | 方向正确 |
|---|---:|---:|---:|---:|---:|---|
| TEM | 1 | -3.58% | -1.85% | -2.88% | -1.51% | 否 |
| TEM | 5 | -16.39% | -13.13% | -17.64% | -22.28% | 否 |
| SDGR | 1 | -0.36% | +1.36% | +0.34% | +1.70% | 否 |
| SDGR | 5 | -9.41% | -6.15% | -10.65% | -15.30% | 是 |
| CERT | 1 | -2.58% | -0.85% | -1.87% | -0.51% | 否 |
| CERT | 5 | -3.67% | -0.40% | -4.91% | -9.56% | 否 |
| NTRA | 1 | -0.27% | +1.46% | +0.43% | +1.80% | 否 |
| NTRA | 5 | +1.77% | +5.04% | +0.53% | -4.12% | 否 |
| RXRX | 1 | -5.78% | -4.05% | -5.07% | -3.71% | 否 |
| RXRX | 5 | -10.62% | -7.36% | -11.86% | -16.51% | 否 |
| SOPH | 1 | -1.73% | -0.01% | -1.03% | +0.33% | 否 |
| SOPH | 5 | -16.47% | -13.20% | -17.71% | -22.35% | 否 |
| GH | 1 | -1.39% | +0.33% | -0.69% | +0.67% | 否 |
| GH | 5 | +4.78% | +8.05% | +3.54% | -1.11% | 是 |
| ABCL | 1 | -2.92% | -1.20% | -2.22% | -0.86% | 是 |
| ABCL | 5 | -5.04% | -1.77% | -6.28% | -10.92% | 否 |
| GEHC | 1 | +0.68% | +2.41% | +1.38% | +2.75% | 否 |
| GEHC | 5 | -0.83% | +2.43% | -2.07% | -6.72% | 是 |
| RDNT | 1 | -0.72% | +1.01% | -0.01% | +1.35% | 否 |
| RDNT | 5 | +0.40% | +3.67% | -0.84% | -5.48% | 是 |
| ISRG | 1 | -2.23% | -0.50% | -1.53% | -0.16% | 否 |
| ISRG | 5 | +0.75% | +4.01% | -0.50% | -5.14% | 是 |
| IQV | 1 | -2.21% | -0.48% | -1.51% | -0.14% | 否 |
| IQV | 5 | -2.17% | -0.31% | -1.89% | -10.11% | 否 |
| NVDA | 1 | -5.90% | -4.17% | -5.19% | -3.83% | 否 |
| NVDA | 5 | -4.64% | -1.37% | -5.88% | -10.53% | 否 |
| HTFL | 1 | -0.74% | +0.99% | -0.03% | +1.33% | 否 |
| HTFL | 5 | -0.41% | +2.85% | -1.66% | -6.30% | 否 |
| CBLL | 1 | -0.10% | +1.63% | +0.60% | +1.96% | 是 |
| CBLL | 5 | +15.57% | +18.83% | +14.33% | +9.68% | 是 |
| CAI | 1 | -5.48% | -3.75% | -4.78% | -3.41% | 否 |
| CAI | 5 | -10.67% | -7.40% | -11.91% | -16.55% | 否 |
