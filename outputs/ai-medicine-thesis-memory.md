# AI Medicine 论点长期记忆

> 记录系统在每次运行时知道什么、排名如何变化、哪些事件让 Serenity 门槛失效。它是审计轨迹，不是预测能力证明。

覆盖 16 家公司；保留 22 个不同状态快照；本次 16 家发生变化，共 25 个字段变化。

## 本次变化

### TEM
- `completenessScore`：`90` → `85`
- `forecastReturn`：`-0.000251` → `0.023396`
### SDGR
- `completenessScore`：`87` → `82`
- `forecastReturn`：`0.044995` → `0.054776`
### RXRX
- `completenessScore`：`82` → `77`
- `forecastReturn`：`0.023845` → `0.011503`
### ABCL
- `forecastReturn`：`0.002866` → `0.003623`
### CERT
- `completenessScore`：`77` → `72`
- `forecastReturn`：`0.019792` → `0.026588`
### NTRA
- `forecastReturn`：`-0.011053` → `-0.005712`
### SOPH
- `forecastReturn`：`0.050665` → `0.016486`
### GH
- `forecastReturn`：`0.014899` → `0.013868`
### GEHC
- `forecastReturn`：`0.004408` → `-0.018763`
### RDNT
- `completenessScore`：`90` → `85`
- `forecastReturn`：`-0.017742` → `0.009433`
### ISRG
- `forecastReturn`：`0.005404` → `-0.004836`
### IQV
- `forecastReturn`：`0.016321` → `0.0207`
### NVDA
- `forecastReturn`：`0.082383` → `0.082423`
- 关联事件：NVIDIA Board of Directors Establishes National Security and Export Control Oversight Committee；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：NVIDIA Announces Financial Results for Third Quarter Fiscal 2027；影响门槛：cash_generation, cash_runway, clinical_validation, counter_thesis, customer_dependency, dilution, earnings_validation, falsifiers, integration_execution, management_governance, partner_economics, reputation_risk, valuation
- 关联事件：Reporters grill Blanche over handling of Huang affair, Nvidia chip exports - The Hill；影响门槛：counter_thesis, management_governance, reputation_risk
- 关联事件：NVIDIA Board Reinstates Jensen Huang as President, CEO and Board Director；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：Jensen Huang’s Net Worth Is Now Down 16% Since Start Of Last Week’s Affairs Scandal - Forbes；影响门槛：counter_thesis, management_governance, reputation_risk
- 关联事件：NVIDIA Announces CEO Transition；影响门槛：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, reputation_risk, valuation
- 关联事件：NVIDIA Expands Commitments With Supply Chain Partners to Support AI Infrastructure Buildout；影响门槛：counter_thesis, customer_dependency, earnings_validation, integration_execution, management_governance, partner_economics, reputation_risk, valuation
- 关联事件：Nvidia-Favored Marvell and Lumentum Announce Merger: What Does This Mean for NVDA? - TradingKey；影响门槛：integration_execution, valuation
- 关联事件：NVIDIA Announces Collaboration With IBM and Fermi National Accelerator Laboratory to Launch Quantum-Classical Codesign Platform, Plus Error-Correction Breakthrough to Advance Practical Quantum Computing；影响门槛：customer_dependency, integration_execution, partner_economics, valuation
- 关联事件：Nvidia CEO Jensen Huang’s image tarnished by board investigation and affair, analysts say - Los Angeles Times；影响门槛：counter_thesis, management_governance, reputation_risk
### HTFL
- `forecastReturn`：`0.006804` → `0.005266`
### CBLL
- `serenityDecision`：`watch` → `research-ready`
- `completenessScore`：`82` → `95`
- `forecastReturn`：`-0.023741` → `-0.044579`
### CAI
- `serenityDecision`：`research-ready` → `watch`
- `completenessScore`：`95` → `82`
- `forecastReturn`：`0.015232` → `0.027915`

## 当前记忆

| 股票 | 排名 | Serenity | 完整度 | 估值 | 融资风险 | 5日环境 |
|---|---:|---|---:|---|---|---:|
| TEM | 1 | research-ready | 85 | growth valuation; requires continued validation | low | +2.34% |
| SDGR | 2 | watch | 82 | premium; execution-sensitive | medium | +5.48% |
| CERT | 3 | watch | 72 | growth valuation; requires continued validation | low | +2.66% |
| NTRA | 4 | watch | 72 | premium; execution-sensitive | low | -0.57% |
| RXRX | 5 | watch | 77 | pipeline optionality; revenue multiple not decision-useful | medium | +1.15% |
| SOPH | 6 | watch | 77 | growth valuation; requires continued validation | high | +1.65% |
| GH | 7 | watch | 38 | premium; execution-sensitive | low | +1.39% |
| ABCL | 8 | watch | 53 | pipeline optionality; revenue multiple not decision-useful | medium | +0.36% |
| GEHC | None | watch | 69 | not obviously premium on sales; inspect quality and dilution | low | -1.88% |
| RDNT | None | research-ready | 85 | not obviously premium on sales; inspect quality and dilution | low | +0.94% |
| ISRG | None | watch | 69 | premium; execution-sensitive | low | -0.48% |
| IQV | None | reject | 56 | not obviously premium on sales; inspect quality and dilution | low | +2.07% |
| NVDA | None | revalidate | 17 | premium; execution-sensitive | low | +8.24% |
| HTFL | None | research-ready | 90 | premium; execution-sensitive | low | +0.53% |
| CBLL | None | research-ready | 95 | premium; execution-sensitive | high | -4.46% |
| CAI | None | watch | 82 | growth valuation; requires continued validation | low | +2.79% |

## 决策引用记忆

- **TEM：** `mem_5666b1309f7e`, `mem_f3047466ac1f`, `mem_4645d21f8a09`, `mem_8dd7366f1068`, `mem_3fcec45a4a11`
- **SDGR：** `mem_1474046f035e`, `mem_d7409eb7f180`, `mem_1881bdf5663f`, `mem_fc0ac008075d`, `mem_57070885939c`
- **CERT：** `mem_5c8621be97bc`, `mem_8e7729b470a7`, `mem_9c26e964c49e`, `mem_4b7db0f677b8`, `mem_0302c0dc12af`
- **NTRA：** `mem_e7ea13f2d77a`, `mem_c72c64a041bb`, `mem_4aa4df572dae`, `mem_5d8b86074399`, `mem_db8597deb4d3`
- **RXRX：** `mem_8c7f3927b1d7`, `mem_796975290c26`, `mem_4109ca0ee4fa`, `mem_e463c2003a07`, `mem_b93d4a6407ec`
- **SOPH：** `mem_64ed504006cb`, `mem_67adcf1bce2e`, `mem_9fdd929ccde9`, `mem_63e75c26498d`, `mem_ad9ed4a07138`
- **GH：** `mem_939606456f07`, `mem_f776df745f4f`, `mem_7ca3c4c11e45`, `mem_812dd7f4d95b`, `mem_7b730fbedd2c`
- **ABCL：** `mem_0febce5afc88`, `mem_d96018c9348a`, `mem_089b6540b2d3`, `mem_9858343b0a2d`, `mem_6186c7978886`
- **GEHC：** `mem_2b15842596ed`, `mem_62de0a6fe442`, `mem_ed4c4183c556`, `mem_38fc8a8d1499`, `mem_57cd6ef345ec`
- **RDNT：** `mem_03bf6e4f9b56`, `mem_87a3ecb0a0fb`, `mem_962e42552623`, `mem_310c11c3d93d`, `mem_fdb9780d7672`
- **ISRG：** `mem_699347c1b6ed`, `mem_c2d0b38e7bdf`, `mem_4437c75c3fc7`, `mem_7f45182faade`, `mem_f3920cd05489`
- **IQV：** `mem_f1c02159b8bd`, `mem_4d092213a4ee`, `mem_6b5d9f20c75b`, `mem_5489f0058ceb`, `mem_8e495ff5e43c`
- **NVDA：** `mem_2607f6e47c08`, `mem_4b356174c4a4`, `mem_5ec2b63ee470`, `mem_12e3dcb1dc70`, `mem_673b5bbef4c9`, `mem_d67004df9dcc`, `mem_77a5893e9e6e`, `mem_7f9b383aa469`, `mem_d6431821612b`, `mem_811c04bf0ce0`, `mem_90d4523b3386`, `mem_c8255d955688`, `mem_e205baf97f1f`, `mem_f4a41f493f93`, `mem_7b2672d16dbd`
- **HTFL：** `mem_4c6e28760f99`, `mem_96341927af15`, `mem_b4ccc7ce7f8c`, `mem_58a23b756325`, `mem_158c2a269e33`
- **CBLL：** `mem_9ec65cb223a4`, `mem_19b2ea2b2f50`, `mem_cc0560e6d954`, `mem_6cd6dc707806`, `mem_6fee13da5d48`
- **CAI：** `mem_7997ad037f2d`, `mem_9b3d785255fe`, `mem_06c169b9b11f`, `mem_0b1c2ed9ad0c`, `mem_5cf855bc037f`

## 已实现表现反思

| 股票 | 周期 | 实际收益 | 超额 SPY | 超额 XLV | 超额 XBI | 方向正确 |
|---|---:|---:|---:|---:|---:|---|
| TEM | 1 | +5.35% | +3.73% | +5.07% | +4.14% | 是 |
| TEM | 5 | -6.21% | -7.95% | -10.01% | -16.18% | 否 |
| SDGR | 1 | -0.15% | -1.77% | -0.43% | -1.36% | 否 |
| SDGR | 5 | -6.95% | -8.69% | -10.75% | -16.93% | 否 |
| CERT | 1 | +1.95% | +0.33% | +1.67% | +0.74% | 是 |
| CERT | 5 | +2.62% | +0.88% | -1.18% | -7.36% | 是 |
| NTRA | 1 | +3.17% | +1.54% | +2.88% | +1.95% | 是 |
| NTRA | 5 | +4.87% | +3.13% | +1.07% | -5.11% | 是 |
| RXRX | 1 | +7.33% | +5.71% | +7.04% | +6.11% | 是 |
| RXRX | 5 | -0.37% | -2.11% | -4.17% | -10.35% | 否 |
| SOPH | 1 | +4.75% | +3.13% | +4.46% | +3.53% | 是 |
| SOPH | 5 | -2.54% | -4.28% | -6.34% | -12.52% | 否 |
| GH | 1 | +2.45% | +0.83% | +2.17% | +1.24% | 是 |
| GH | 5 | +7.18% | +5.44% | +3.38% | -2.80% | 是 |
| ABCL | 1 | +3.64% | +2.02% | +3.36% | +2.43% | 是 |
| ABCL | 5 | +3.34% | +1.60% | -0.46% | -6.63% | 是 |
| GEHC | 1 | +2.07% | +0.45% | +1.79% | +0.86% | 是 |
| GEHC | 5 | +3.33% | +1.59% | -0.46% | -6.64% | 是 |
| RDNT | 1 | +1.49% | -0.13% | +1.20% | +0.27% | 是 |
| RDNT | 5 | +4.99% | +3.25% | +1.19% | -4.99% | 是 |
| ISRG | 1 | +1.69% | +0.07% | +1.41% | +0.48% | 是 |
| ISRG | 5 | +5.63% | +3.89% | +1.84% | -4.34% | 是 |
| IQV | 1 | -0.22% | -1.85% | -0.51% | -1.44% | 否 |
| IQV | 5 | -0.46% | -2.20% | -4.26% | -10.44% | 否 |
| NVDA | 1 | +4.78% | +3.16% | +4.50% | +3.57% | 是 |
| NVDA | 5 | +3.09% | +1.35% | -0.71% | -6.89% | 是 |
| HTFL | 1 | +4.45% | +2.83% | +4.17% | +3.24% | 否 |
| HTFL | 5 | +6.77% | +5.03% | +2.97% | -3.21% | 是 |
| CBLL | 1 | +1.39% | -0.24% | +1.10% | +0.17% | 否 |
| CBLL | 5 | +16.50% | +14.77% | +12.71% | +6.53% | 是 |
| CAI | 1 | +3.27% | +1.65% | +2.99% | +2.06% | 是 |
| CAI | 5 | -2.91% | -4.65% | -6.71% | -12.89% | 否 |
