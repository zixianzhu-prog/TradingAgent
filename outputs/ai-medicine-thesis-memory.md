# AI Medicine 论点长期记忆

> 记录系统在每次运行时知道什么、排名如何变化、哪些事件让 Serenity 门槛失效。它是审计轨迹，不是预测能力证明。

覆盖 16 家公司；保留 18 个不同状态快照；本次 16 家发生变化，共 28 个字段变化。

## 本次变化

### TEM
- `completenessScore`：`85` → `80`
- `forecastReturn`：`0.024803` → `0.047641`
### SDGR
- `completenessScore`：`77` → `87`
- `forecastReturn`：`0.021495` → `0.040764`
### RXRX
- `forecastReturn`：`0.044002` → `0.022888`
### ABCL
- `forecastReturn`：`0.004233` → `-0.013603`
### CERT
- `forecastReturn`：`0.058112` → `0.029782`
### NTRA
- `forecastReturn`：`0.019236` → `0.001784`
### SOPH
- `completenessScore`：`64` → `77`
- `forecastReturn`：`0.031424` → `0.061606`
### GH
- `completenessScore`：`33` → `38`
- `forecastReturn`：`0.001356` → `0.009973`
### GEHC
- `forecastReturn`：`0.018611` → `-0.005973`
### RDNT
- `serenityDecision`：`watch` → `research-ready`
- `completenessScore`：`80` → `90`
- `forecastReturn`：`-0.004105` → `0.014331`
### ISRG
- `forecastReturn`：`0.005099` → `0.006042`
### IQV
- `forecastReturn`：`0.007653` → `0.018277`
### NVDA
- `forecastReturn`：`0.020723` → `0.069464`
- 关联事件：NVIDIA Board of Directors Establishes National Security and Export Control Oversight Committee；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：NVIDIA Announces Financial Results for Third Quarter Fiscal 2027；影响门槛：cash_generation, cash_runway, clinical_validation, counter_thesis, customer_dependency, dilution, earnings_validation, falsifiers, integration_execution, management_governance, partner_economics, valuation
- 关联事件：NVIDIA Board Reinstates Jensen Huang as President, CEO and Board Director；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：What we learned from Nvidia’s first earnings call without Jensen Huang - SiliconANGLE；影响门槛：cash_generation, cash_runway, customer_dependency, earnings_validation, valuation
- 关联事件：Ex-CEO Jensen Huang signals interest in returning to Nvidia after resigning amid scandal - PBS；影响门槛：counter_thesis, management_governance, reputation_risk
- 关联事件：Jensen Huang’s Net Worth Is Now Down 16% Since Start Of Last Week’s Affairs Scandal - Forbes；影响门槛：counter_thesis, management_governance, reputation_risk
- 关联事件：NVIDIA Announces CEO Transition；影响门槛：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, valuation
- 关联事件：Nvidia (NVDA) CEO Jensen Huang Resigned As The SEC Opened An Accounting Probe - Yahoo Finance；影响门槛：counter_thesis, earnings_validation, management_governance
- 关联事件：NVIDIA Expands Commitments With Supply Chain Partners to Support AI Infrastructure Buildout；影响门槛：counter_thesis, customer_dependency, earnings_validation, integration_execution, management_governance, partner_economics, valuation
- 关联事件：Nvidia-Favored Marvell and Lumentum Announce Merger: What Does This Mean for NVDA? - TradingKey；影响门槛：integration_execution, valuation
- 关联事件：Timeline of a scandal: How Jensen Huang's resignation and return at Nvidia unfolded - CBS News；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：Jensen Huang Returns: Timeline Of The Scandal That Led To Resignation And Comeback - Forbes；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：Nvidia Earnings Live Updates: First Report Since Jensen Huang’s Resignation Beats Expectations - The New York Times；影响门槛：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, valuation
- 关联事件：Four takeaways from Nvidia’s first earnings report after Jensen Huang scandal | CNN Business - CNN；影响门槛：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, reputation_risk, valuation
- 关联事件：Four takeaways from Nvidia’s first earnings report after Jensen Huang scandal - CNN；影响门槛：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, reputation_risk, valuation
- 关联事件：Jensen Huang Scandal: Timeline That Led To His Resignation—And Potential Comeback - Forbes；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：Nvidia to report Q3 earnings amid Huang scandal - Yahoo Finance；影响门槛：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, reputation_risk, valuation
- 关联事件：Nvidia stock falls ahead of earnings as company reels from Huang resignation - CNBC；影响门槛：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, valuation
- 关联事件：NVIDIA Announces Collaboration With IBM and Fermi National Accelerator Laboratory to Launch Quantum-Classical Codesign Platform, Plus Error-Correction Breakthrough to Advance Practical Quantum Computing；影响门槛：customer_dependency, integration_execution, partner_economics, valuation
- 关联事件：Nvidia CEO Huang resigns amid affair scandals, board names CFO Colette Kress interim CEO - Yahoo Finance；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：Timeline of a scandal: How Jensen Huang's abrupt resignation unfolded at Nvidia - CBS News；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：Lawmakers Urge Federal Probe Into Jensen Huang Over Affair With Chinese Spy—And Call For His Resignation - Forbes；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：Jensen Huang affair in DC: Resignation calls and moves to tighten Nvidia China exports - CNBC；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：Jensen Huang affair puts Nvidia's future at risk, with no clear successor to the renowned CEO - CNBC；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：Nvidia CEO Jensen Huang’s image tarnished by board investigation and affair, analysts say - Los Angeles Times；影响门槛：counter_thesis, management_governance, reputation_risk
### HTFL
- `serenityDecision`：`watch` → `research-ready`
- `completenessScore`：`85` → `90`
- `forecastReturn`：`-0.029242` → `0.050252`
### CBLL
- `serenityDecision`：`watch` → `research-ready`
- `completenessScore`：`77` → `95`
- `forecastReturn`：`-0.024971` → `-0.037874`
### CAI
- `serenityDecision`：`watch` → `research-ready`
- `completenessScore`：`82` → `95`
- `forecastReturn`：`0.00668` → `0.008277`

## 当前记忆

| 股票 | 排名 | Serenity | 完整度 | 估值 | 融资风险 | 5日环境 |
|---|---:|---|---:|---|---|---:|
| TEM | 1 | watch | 80 | growth valuation; requires continued validation | low | +4.76% |
| SDGR | 2 | watch | 87 | premium; execution-sensitive | medium | +4.08% |
| CERT | 3 | watch | 77 | growth valuation; requires continued validation | low | +2.98% |
| NTRA | 4 | watch | 72 | premium; execution-sensitive | low | +0.18% |
| RXRX | 5 | watch | 82 | pipeline optionality; revenue multiple not decision-useful | medium | +2.29% |
| SOPH | 6 | watch | 77 | growth valuation; requires continued validation | high | +6.16% |
| GH | 7 | watch | 38 | premium; execution-sensitive | low | +1.00% |
| ABCL | 8 | watch | 53 | pipeline optionality; revenue multiple not decision-useful | medium | -1.36% |
| GEHC | None | watch | 77 | not obviously premium on sales; inspect quality and dilution | low | -0.60% |
| RDNT | None | research-ready | 90 | not obviously premium on sales; inspect quality and dilution | low | +1.43% |
| ISRG | None | watch | 69 | premium; execution-sensitive | low | +0.60% |
| IQV | None | reject | 56 | not obviously premium on sales; inspect quality and dilution | low | +1.83% |
| NVDA | None | revalidate | 5 | premium; execution-sensitive | low | +6.95% |
| HTFL | None | research-ready | 90 | premium; execution-sensitive | low | +5.03% |
| CBLL | None | research-ready | 95 | premium; execution-sensitive | high | -3.79% |
| CAI | None | research-ready | 95 | growth valuation; requires continued validation | low | +0.83% |

## 决策引用记忆

- **TEM：** `mem_0dc4f8fd28ed`, `mem_f3047466ac1f`, `mem_4645d21f8a09`, `mem_783e67a804cd`, `mem_d804b9a36215`
- **SDGR：** `mem_e1e3b5228afc`, `mem_d7409eb7f180`, `mem_1881bdf5663f`, `mem_5f47c00530c8`, `mem_c25c6902a8b9`
- **CERT：** `mem_b9883e3323f8`, `mem_8e7729b470a7`, `mem_9c26e964c49e`, `mem_94b6549be5f8`, `mem_be8aaf784a5c`
- **NTRA：** `mem_fd76ff8701fc`, `mem_c72c64a041bb`, `mem_4aa4df572dae`, `mem_c80e7ef61855`, `mem_fef43b67eb4d`
- **RXRX：** `mem_3d2704d45a99`, `mem_796975290c26`, `mem_4109ca0ee4fa`, `mem_2311bd77384d`, `mem_d60945e42413`
- **SOPH：** `mem_1680d340dfe8`, `mem_67adcf1bce2e`, `mem_9fdd929ccde9`, `mem_e9f3e3cb3ec9`, `mem_8c7e99fc7a2b`
- **GH：** `mem_ef9ea4d8c1ef`, `mem_f776df745f4f`, `mem_7ca3c4c11e45`, `mem_076da8be0cd7`, `mem_889a6824dd21`
- **ABCL：** `mem_5fc843c8e96a`, `mem_d96018c9348a`, `mem_089b6540b2d3`, `mem_aacfd37ea4fb`, `mem_9cbcb131960c`
- **GEHC：** `mem_4e6f168d9a57`, `mem_62de0a6fe442`, `mem_ed4c4183c556`, `mem_dcf0ed85b9e9`, `mem_78a9d827beb7`
- **RDNT：** `mem_baca915f4ff3`, `mem_87a3ecb0a0fb`, `mem_962e42552623`, `mem_877c2d7bb4da`, `mem_44d3a53382ab`
- **ISRG：** `mem_12ecdd40b5b9`, `mem_c2d0b38e7bdf`, `mem_4437c75c3fc7`, `mem_33c133efeeb6`, `mem_6089209b6def`
- **IQV：** `mem_da91680de4a5`, `mem_4d092213a4ee`, `mem_6b5d9f20c75b`, `mem_f9c68f46fe8d`, `mem_dfc7d629df5f`
- **NVDA：** `mem_9b215871a9f2`, `mem_4b356174c4a4`, `mem_5ec2b63ee470`, `mem_12e3dcb1dc70`, `mem_f2732a2d3e86`, `mem_77a5893e9e6e`, `mem_0dd11c849133`, `mem_202f8ddebb54`, `mem_7f9b383aa469`, `mem_d04ab0ac0ee9`, `mem_f98b5513a07e`, `mem_5159bd284e74`, `mem_90d4523b3386`, `mem_59c8dbb7fd9a`, `mem_4b5f0d628fe0`, `mem_5bd8c898d783`, `mem_f87b1c8c8d15`, `mem_080235ae6adc`, `mem_8793d27ce045`, `mem_e922e6a67042`, `mem_07a724e8a0c9`, `mem_c8255d955688`, `mem_ff485b97c5b0`, `mem_4e75bf386aa9`, `mem_7cf97106f519`, `mem_7fbd836d39c5`, `mem_a2217779ed40`, `mem_e205baf97f1f`, `mem_eefd29960657`, `mem_7997a552e44e`
- **HTFL：** `mem_c40213f60b6a`, `mem_96341927af15`, `mem_b4ccc7ce7f8c`, `mem_beae6beefb88`, `mem_242d1c2f924b`
- **CBLL：** `mem_b75d6a98bbc4`, `mem_19b2ea2b2f50`, `mem_cc0560e6d954`, `mem_4e11fa43a053`, `mem_5a28f958cecc`
- **CAI：** `mem_7ef2da2a7c82`, `mem_9b3d785255fe`, `mem_06c169b9b11f`, `mem_45f4dcd49955`, `mem_6470ade49012`

## 已实现表现反思

| 股票 | 周期 | 实际收益 | 超额 SPY | 超额 XLV | 超额 XBI | 方向正确 |
|---|---:|---:|---:|---:|---:|---|
| TEM | 1 | -3.66% | -3.13% | -6.53% | -9.32% | 否 |
| TEM | 5 | -12.97% | -11.07% | -12.62% | -20.01% | 否 |
| SDGR | 1 | -1.10% | -0.57% | -3.98% | -6.76% | 否 |
| SDGR | 5 | -3.60% | -1.70% | -3.25% | -10.64% | 否 |
| CERT | 1 | +2.41% | +2.93% | -0.47% | -3.26% | 是 |
| CERT | 5 | +0.00% | +1.91% | +0.36% | -7.03% | 是 |
| NTRA | 1 | +1.66% | +2.18% | -1.22% | -4.01% | 是 |
| NTRA | 5 | +2.69% | +4.59% | +3.04% | -4.35% | 是 |
| RXRX | 1 | +0.60% | +1.13% | -2.27% | -5.06% | 是 |
| RXRX | 5 | -1.43% | +0.48% | -1.07% | -8.46% | 否 |
| SOPH | 1 | -5.15% | -4.62% | -8.03% | -10.81% | 否 |
| SOPH | 5 | -14.70% | -12.79% | -14.34% | -21.73% | 否 |
| GH | 1 | -0.70% | -0.17% | -3.58% | -6.37% | 否 |
| GH | 5 | +7.55% | +9.46% | +7.91% | +0.52% | 是 |
| ABCL | 1 | +2.20% | +2.72% | -0.68% | -3.47% | 是 |
| ABCL | 5 | -2.18% | -0.27% | -1.82% | -9.21% | 否 |
| GEHC | 1 | +1.78% | +2.31% | -1.10% | -3.88% | 是 |
| GEHC | 5 | +0.82% | +2.73% | +1.18% | -6.21% | 是 |
| RDNT | 1 | +0.47% | +1.00% | -2.41% | -5.19% | 否 |
| RDNT | 5 | -2.81% | -0.90% | -2.45% | -9.84% | 否 |
| ISRG | 1 | +4.10% | +4.63% | +1.22% | -1.56% | 是 |
| ISRG | 5 | +0.67% | +2.57% | +1.02% | -6.36% | 是 |
| IQV | 1 | +1.30% | +1.82% | -1.58% | -4.37% | 是 |
| IQV | 5 | -0.58% | +1.33% | -0.22% | -7.61% | 否 |
| NVDA | 1 | -7.50% | -6.97% | -10.37% | -13.16% | 否 |
| NVDA | 5 | -1.65% | +0.26% | -1.29% | -8.68% | 否 |
| HTFL | 1 | -6.07% | -5.55% | -8.95% | -11.74% | 是 |
| HTFL | 5 | -2.08% | -0.18% | -1.73% | -9.11% | 否 |
| CBLL | 1 | +2.99% | +3.52% | +0.11% | -2.68% | 否 |
| CBLL | 5 | +14.11% | +16.02% | +14.47% | +7.08% | 是 |
| CAI | 1 | -4.11% | -3.59% | -6.99% | -9.78% | 否 |
| CAI | 5 | -7.67% | -5.77% | -7.32% | -14.70% | 否 |
