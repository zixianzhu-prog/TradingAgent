# Serenity 研究备忘录：Recursion Pharmaceuticals（RXRX）

- 日期：2026-11-15；价格 $3.20（2026-11-13 收盘），市值约 $20 亿，流通股约 6.23 亿
- 审查者：Claude，按 `~/.codex/skills` 中全部 8 个 Aleabit/Serenity skill 执行
- 触发原因：本周新闻驱动推荐第一名（新闻信号 +75，Serenity 证据分 55）
- 性质：研究分析，不是投资建议；仓位与买卖部分只是对 Serenity 框架的推演

---

## 结论先行

**Serenity 判断：真实的 AI 原生多节点平台，但不是 Serenity 意义上的"卡位"公司；两条反方论点成立，只适合"观察 / 试探级"，不适合高确信度。**

| 维度 | 判断 |
|---|---|
| 是否卡位（chokepoint） | **否**。RXRX 自己依赖别人的瓶颈（NVIDIA GPU、单一来源原料药、WuXi），它的护城河是数据和自动化实验室，属于"数据壁垒"，不是供应垄断 |
| 下游拉动（客户依赖） | **已确认**。Sanofi 首次选择权行权、Genentech 选定首个神经科学靶点，合作方累计付款超过 5.35 亿美元 |
| 多节点控制 | **是**。自动化湿实验室 + 50PB 数据 + 自有超算 + 模型 + 自有临床管线 |
| 分组 | **高赔率型**（市值 $20 亿，在 4 亿–50 亿美元区间内） |
| 反方论点 | **两条成立**：持续稀释；临床证据样本太小。按研究流程 skill："任何一条反方成立，论点就不适合高确信度仓位" |
| 框架对应的仓位级别 | **试探级（0.5–1%）**：论点仍在成熟中，未经多个财报周期验证 |
| 对新闻推荐的影响 | 保留在推荐中，但标注"Serenity：试探级，非卡位"；推荐理由中的一条 Stocktwits 标题有误（见第 9 节） |

---

## 1. 产业链图（研究流程 Step 1）

```text
上游投入                          RXRX（核心）                          下游
────────                          ───────────                          ────
NVIDIA H100 ×504（BioHive-2）  ─┐   自动化湿实验室：每周 200 万+ 实验   ┌─ Roche/Genentech：已接收 6 张 Phenomap，
Google Cloud（数据存储/计算）   ─┤   多模态数据：>50 PB                  │   选定首个神经科学靶点；累计 $2.16 亿
细胞、试剂、实验耗材            ─┼─→ 模型：表型组/转录组基础模型      ─┼─ Sanofi：首个开发候选物行权，2027 年进入 I 期；累计 $1.44 亿
单一来源原料药（API）供应商     ─┤   化学：DMTL 设计-合成-测试循环      ├─ Bayer、Merck KGaA：合作中
CRO（含 WuXi AppTec）、CDMO     ─┘   自有临床管线：REC-4881、REC-1245 等 └─ 患者（经未来上市或合作方商业化）
```

关键原文（RXRX 2025 年 10-K）：

- 单一来源："the API used in our drug candidates, are obtained from single-source suppliers." 且 "We do not currently have arrangements in place for a redundant or second-source supply of any such equipment or ingredients."
- 制造外包："we have obtained drug substance and drug product for our drug candidates from third party contract manufacturers."
- 算力："our own supercomputer, BioHive-2"，"built in collaboration with NVIDIA"；云："partnering with Google Cloud"；依赖："We rely on third-party data centers and telecommunications solutions, including cloud infrastructure services"
- 实验室规模："our automated high throughput labs, which can run over 2 million experiments per week"

**门槛判断：产业链位置 → 通过**（上中下游都有一手来源；缺口：原料药供应商的具体名称未披露）。

## 2. 卡位候选（研究流程 Step 2 + 卡位理论 5 问）

| 卡位理论的问题 | RXRX 的答案 |
|---|---|
| ① 下游"显而易见的受益者"依赖什么投入？ | 大药企的新药研发依赖经过验证的靶点和候选分子；RXRX 提供表型图谱和候选物 |
| ② 谁供应这个投入，集中度如何？ | **不集中**：Isomorphic Labs、Insilico、Xaira、Schrödinger、AbCellera，以及大药企内部 AI、科技巨头，都在供应。10-K 自己点名了 "Relay Therapeutics, Isomorphic Labs, Schrodinger, and AbCellera" 和 "Alphabet, Microsoft, and Amazon" |
| ③ 有没有西方公开市场的方式持有这个节点？ | 有，而且不止一家：RXRX 是最大的上市 AI 原生药物发现公司之一，但 SDGR、ABCL、RLAY 也是公开标的，不具备"唯一"属性 |
| ④ 是否纵向整合多个瓶颈节点？ | 是：实验 + 数据 + 算力 + 模型 + 化学 + 临床 |
| ⑤ 机构是否已经覆盖？ | **已经覆盖**：JPMorgan、Morgan Stanley、Jefferies、KeyBanc 都在财报电话会上提问；共识评级为"持有" |

**唯一可能的卡位是"数据 + 自动化实验室"**：50PB 专有表型数据需要多年和大量资本才能复制。但它不是供应垄断，基础模型或大药企自建实验室都可能在 3–5 年内削弱它的价值。

反过来，**RXRX 自己处在别人的瓶颈下游**：单一来源原料药没有备份；WuXi AppTec 被 BIOSECURE 法案列为"关注对象"；算力依赖 NVIDIA 硬件和 Google Cloud。

**门槛判断：卡位证据 → 部分通过**（偏弱）。

## 3. 客户依赖（研究流程 Step 3）

- "we have now achieved more than $535 million in cash inflows from our partners."（Q3 2026 电话会）
- Sanofi："This is the first development candidate Sanofi has optioned from our collaboration"，"with phase I expected to begin in 2027"
- Genentech："Genentech has now optioned the first target from that work, and small molecule discovery is underway"
- Roche 与 Sanofi 合作"have produced more than $100 million from nine progress-based milestones"

这相当于选股 skill 里"已确认的下游设计订单"在药企领域的对应物：合作方已经付了钱，并且行使了选择权，不只是一纸合作公告。

但锁定程度有限：Q3 收入只有 $1,860 万，而且主要来自合作研发款；合作方随时可能终止。

**门槛判断：客户依赖 → 通过**（有付款和行权，超出"合作公告"）。

## 4. 多层推演（研究流程 Step 4）

| 层级 | 推演 |
|---|---|
| 一阶 | 平台有效 → 更多里程碑付款 + 管线价值上升 |
| 二阶 | 如果 REC-4881 的注册性试验成功，将成为 AI 平台发现药物的标志性验证 → 整个 AI 制药板块重估（SDGR、ABCL 及私营公司），CRO/CDMO 同样受益 |
| 三阶 | AI 制药成为共识后，大药企自建能力，Isomorphic 等资金雄厚的 AI 实验室直接与药企合作 → 平台合作的议价能力下降 |
| 四阶（地缘政治） | BIOSECURE 法案若扩大适用范围，原料药和 CRO 需要转移供应链；10-K 称目前"it would only impact U.S. companies that contract with or receive funding from the U.S. government" |
| 五阶（3–5 年替代） | 用公开或合作方数据训练的"虚拟细胞"基础模型，可能降低专有表型数据的稀缺性 |

## 5. 压力测试：最强的 5 条反对理由（研究流程 Step 5）

| # | 反对理由 | 证据 | 是否成立 |
|---|---|---|---|
| 1 | **持续稀释** | Q3 净亏损 $1.19 亿；10 月完成 $2 亿融资；另有 $3 亿 ATM 增发计划；累计亏损 $21 亿；股价从 10 月 4 日约 $4.12 跌到 11 月 13 日 $3.20 | **成立** |
| 2 | **临床证据样本太小** | REC-4881 主要疗效终点只有 15 名可评估患者，单臂；公司自己也说需要更多证据；注册性试验要到 2027 年下半年才启动 | **成立** |
| 3 | **REC-1245 安全性和对比不清** | 65mg 剂量超过最大耐受剂量；Jefferies 问到与 RBM39 化疗基准（17% 缓解率）的比较时，管理层没有正面回答 | 部分成立 |
| 4 | **竞争加剧** | Isomorphic Labs 据报道完成 $21 亿 B 轮；科技巨头入场 | 部分成立（影响合作议价，短期不改变管线价值） |
| 5 | **战略股东退出** | 据 CMC Markets 引用 13F 报道，NVIDIA 已于 2026 年 2 月清仓 RXRX，尽管双方合作仍在继续 | 信号偏负面（来源为二手报道，待核实） |

**按研究流程 skill 的规则："任何一条反方成立，论点就不适合高确信度仓位。"** 第 1、2 条成立。

缓解因素：现金跑道延长到 2029 年；2027 年现金运营费用指引降到 $3.6 亿以下（"it is not common to be lowering guidance"）。

**门槛判断：反方观点 → 通过**（已用一手来源逐条检验；"通过"表示反方被认真审查过，不表示风险消失）。

## 6. 验证节点与预先承诺（研究流程 Step 6 + 买卖时机 + 心理）

| 时间 | 验证事件 | 看到什么 → 加强论点 | 看到什么 → 论点失效 |
|---|---|---|---|
| 2027 年 2 月左右 | Q4/全年财报 | 2026 年现金运营费用 < $3.75 亿；没有新的融资 | 现金跑道指引缩短；12 个月内再次融资 |
| 2027 年上半年 | REC-4881 的 FDA 沟通 | FDA 同意注册性试验设计，2027 年下半年按时启动 | 要求更大规模或更长时间的试验，推迟到 2028 年以后 |
| 2027 年 | Sanofi 候选物进入 I 期 | 按时启动，触发里程碑付款 | 合作方推迟或放弃选择权 |
| 2027 年下半年 | REC-1245 子宫内膜癌队列初步数据 | 缓解率明显高于 RBM39 类药物基准 | 缓解率与化疗相当，或安全性问题扩大 |

心理 skill 的检验：上表右侧任何一项出现 = 论点被证伪；没有新消息时股价下跌 25% = 噪音。

## 7. 选股清单（选股 skill）

| 标准 | 通过条件 | RXRX |
|---|---|---|
| 市值 | $4 亿–$50 亿 | ✅ 约 $20 亿 |
| 供应集中度 | 全球份额 >50%，或唯一的西方公开标的 | ❌ 竞争者众多 |
| 客户依赖 | 已确认的下游订单 | ✅ Sanofi、Genentech 行权并付款 |
| 纵向整合 | 控制 ≥2 个节点 | ✅ 实验 + 数据 + 算力 + 模型 + 临床 |
| 分组 | 稳健复利 / 高赔率 | 高赔率（亏损、稀释、临床二元风险） |
| 持有人结构 | 高频/做市机构的波动预警 | ⚪ 未核实，没有找到机构持股数据 |

6 项中 3 项通过、1 项不通过、1 项未核实。按 skill 的说法，"大部分标准通过，才进入深度研究流程"——RXRX 勉强够格，但不是典型的 Serenity 标的。

## 8. 轮动、仓位与风控（板块轮动 + 仓位 + 风控 skill）

- **板块轮动所处阶段**：AI 制药经历了 2021 年热潮、2022–2024 年泡沫破裂、2024 年行业整合（RXRX 合并 Exscientia），2026 年出现新一轮"AI for Science"资金潮。本系统的雷达也显示，本周"AI 药物研发"主题明显升温。但新资金主要流向私营 AI 实验室（Isomorphic、Xaira），而不是上市公司；NVIDIA 退出是负面的二阶信号。RXRX 已经被机构充分覆盖，**不属于"抢在机构前面"的早期阶段**。
- **仓位级别（框架推演）**：试探级 0.5–1%。理由：论点仍在成熟中，未经多个财报周期验证，且两条反方论点成立。
- **价格目标**：买卖时机 skill 要求每个持仓都有明确的目标价和时间周期。**目前不具备设定条件**：管线价值取决于 2027 年的 FDA 沟通和临床数据，收入倍数没有参考意义。按框架，没有目标价就不应建立有规模的仓位。
- **风控**：52 周股价区间 $2.77–$7.18，几周内下跌约 22%；融资和临床数据都可能造成跳空。按风控 skill，不应设置紧止损，风险控制靠仓位大小。持有人结构未核实。

## 9. 对本系统的反馈

1. **新闻推荐依据中有一条错误标题**：Stocktwits 的"RXRX Stock Soars Pre-Market On Q4 Beat"把 Q3 写成了 Q4，只有一家低可信度来源。它贡献了 RXRX 新闻信号中约 1.7（总分约 5.9 中）。去掉它，信号仍约 +60，推荐结论不变。但心理 skill 明确说："来自社交媒体的信号不是确信度。"
2. **门槛分高，不等于 Serenity 判断好**：按本备忘录的门槛结论（5 通过、3 部分），门槛完整度会从 59 升到 82，证据分预计明显高于现在的 55（准确数字要等引用导入、证据质量计算完成后才知道）。但 Serenity 的整体判断只是"试探级"。证据分衡量的是"资料是否齐全"，不是"是否值得投资"。建议系统增加一个独立的 **Serenity 结论字段**（是否卡位、反方是否成立、对应仓位级别），推荐时同时参考。

## 10. 门槛结论对比（Claude 本次 vs Codex 之前）

| 门槛 | Codex（基于证据包） | Claude（联网读 10-K 和电话会后） | 变化原因 |
|---|---|---|---|
| 产业链位置 | 部分通过 | **通过** | 10-K 原文补齐了上游（单一来源原料药、WuXi、NVIDIA、Google Cloud）和下游 |
| 卡位证据 | 部分通过 | 部分通过（偏弱） | 一致；并确认 RXRX 是瓶颈的下游，而非持有者 |
| 客户依赖 | 部分通过 | **通过** | 有行权和付款，超出合作公告 |
| 业务纯度 | 部分通过 | **通过** | AI 药物发现就是全部业务 |
| 多节点控制 | 部分通过 | **通过** | 实验、数据、算力、模型、临床均有原文支持 |
| 财报验证 | 通过 | **部分通过**（下调） | 财报验证了现金消耗和合作款，没有验证"平台 → 药物"的核心论点 |
| 反方观点 | 通过 | 通过 | 一致 |
| 管理与治理 | 未知 | 部分通过 | 新任董事长 Fred Hassan；内部人减持等报道未核实 |

---

## 来源

- RXRX 2025 年 10-K（SEC EDGAR）：https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm
- Q3 2026 财报电话会文字稿（The Motley Fool）：https://www.fool.com/earnings/call-transcripts/2026/11/03/recursion-rxrx-q3-2026-earnings-call-transcript/
- Q3 2026 财报新闻稿（公司官网，本次抓取被拒绝，标题与数字经电话会和新闻交叉核对）：https://ir.recursion.com/news-releases/news-release-details/recursion-reports-third-quarter-2026-financial-results-and
- 2026 年 10 月增发招股书补充（424B5）：https://www.sec.gov/Archives/edgar/data/0001601830/000160183026000134/rxrx-finalprosuppxoct2026o.htm
- Q3 业绩与 REC-4881 数据报道（RTTNews）：https://www.rttnews.com/3707529/recursion-pharma-q3-net-loss-narrows-reports-positive-rec-4881-data-advances-pipeline.aspx
- BioHive-2 配置（BiopharmaTrend）：https://biopharmatrend.com/post/800-recursion-unveils-biohive-2-fastest-pharma-owned-supercomputer
- NVIDIA 清仓报道（CMC Markets，二手来源）：https://www.cmcmarkets.com/en/optox/rxrx-stock-why-did-nvidia-offload-ai-drug-developer-recursion
- 分析师评级与价格区间（Investing.com）：https://www.investing.com/equities/recursion-pharmaceuticals
- AI 制药竞争格局（IntuitionLabs，行业综述）：https://intuitionlabs.ai/articles/ai-discovered-drugs-clinical-trials-2026
