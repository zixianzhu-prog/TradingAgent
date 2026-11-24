# Serenity 自动证据审查

审查方式：Claude review; no model API key; FinRobot disabled。每个门槛均关联支持材料、反证和缺口。引用匹配只是可追溯性检查，不保证推论正确。历史手工评分不作为已验证证据。

## ABCL · complete

审查记录：`state/serenity-reviews/ABCL-claude-0e9f14832ea4a73fe686.json`

### supply_chain_map: partial

10-K披露了公司上游原料（生物试剂、微流控组件）和自有GMP制造设施，可识别基本供应链节点，但证据中无具名下游客户关系，整体供应链图谱不完整。

- 支持 [ev_ef6c5902faf8738b](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): Our GMP facility in Vancouver, British Columbia houses our manufacturing and manufacturing support infrastructure.
- 支持 [ev_47416c5f8e272fad](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): We work with materials, including chemicals, biological agents and compounds that could be hazardous to human health and safety or the environment.
- 反证 [ev_34052e90ad6a0cc6](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): We historically have not entered into agreements with our suppliers but secure our raw materials and component parts we use in our equipment on a purchase order basis.
- 缺口：具名下游合作药企及合同条款
- 缺口：上游关键原料供应商名单及集中度
- 缺口：公司产品在完整价值链中的节点定位描述
- 证伪条件：证明主要合作伙伴已终止合同或转向竞争平台的披露
- 证伪条件：显示关键上游供应商已停止供货的事件记录

### chokepoint_evidence: partial

公司持有涵盖单细胞微流控抗体发现方法的多个专利家族，专利保护期延伸至2031-2037年，构成一定的知识产权壁垒；但证据中无市场份额量化数据，亦无替代平台的全球竞争格局分析，无法确认供应集中度符合卡点标准。

- 支持 [ev_569304248360c9e1](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): This patent family includes thirteen issued U.S. patents and one pending U.S. non-provisional patent application.
- 支持 [ev_67b053abf535120f](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): This patent family includes thirteen issued patents including in the U.S., Australia, the Russian Federation, Europe, India, Israel, Canada, China, and Japan.
- 反证 [ev_8f3b87bf75b058d4](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): our rights to certain components of our discovery and development capabilities are licensed to us on a non-exclusive basis. The owners of these non-exclusively licensed technologies are therefore free to license them to third parties, including our competitors
- 缺口：全球单细胞抗体发现平台供应商数量及市场份额数据
- 缺口：竞争性替代平台（如10x Genomics、Twist Bioscience等）的具体对比分析
- 缺口：客户从ABCL平台迁移至替代方案所需时间的量化估计
- 证伪条件：披露竞争平台已获相同或更多大型药企设计授权的具体事实
- 证伪条件：记录ABCL专利被无效化或核心许可协议被终止的事件

### customer_dependency: partial

证据显示公司从合作伙伴收到里程碑付款（包括8400万美元TCE多特异性抗体预付款），且存在专利许可特许权使用费收入，但证据中无任何具名客户，无法评估客户集中度或依赖强度。

- 支持 [ev_5d540b3c9be0a360](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000059/abcl-20260930.htm) (primary-document): $84.0 million in upfront payments received to discover and develop next-generation T-cell engaging (TCE) multispecific antibodies
- 支持 [ev_deb4ad8a48a17c09](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): Royalty revenue is recognized in the period in which the obligation is satisfied and the corresponding sales by our partner or licensee occur.
- 缺口：具名合作药企（如礼来、阿斯利康等）及其合同规模
- 缺口：客户集中度披露（前五大客户收入占比）
- 缺口：已签订的具体授权协议数量及阶段
- 证伪条件：披露某一主要合作伙伴已终止或不续签合作协议的具体事实
- 证伪条件：记录里程碑付款被退还或研究合同被取消的事件

### pure_play: partial

公司业务聚焦于抗体发现与开发平台，同时推进内部管线项目，业务主题集中度较高；但证据中无分部收入数据，无法量化平台服务收入与其他收入来源的比例。

- 支持 [ev_f93f7c4ba2a079e5](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000059/abcl-20260930.htm) (primary-document): Our commercial success depends on the quality of our antibody discovery and development capabilities, technological capabilities, the advancement of internal programs, and their acceptance by new and existing partners in our industry.
- 支持 [ev_4f53b353415ccde3](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000059/abcl-20260930.htm) (primary-document): We intend to continue to invest in research and development efforts towards expanding our capabilities and expertise, grow and advance our internal pipeline.
- 缺口：各业务线分部收入明细（平台服务费 vs 里程碑 vs 特许权使用费）
- 缺口：内部管线与合作项目的资本分配比例
- 证伪条件：证明公司存在与抗体发现无关的重大收入来源的分部披露

### multi_node_control: partial

公司同时控制上游微流控发现平台（核心技术）与GMP制造设施，理论上跨越发现和制造两个节点；但证据未充分展示两个节点在同一供应链中的整合深度，2024年Trianni和TetraGenetics并购减值也表明节点整合存在不确定性。

- 支持 [ev_ef6c5902faf8738b](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): Our GMP facility in Vancouver, British Columbia houses our manufacturing and manufacturing support infrastructure.
- 反证 [ev_6d702fe0c7278d2d](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): in 2024, we recognized a full impairment charge of the Trianni and TetraGenetics in-process research and development and there could be additional future impairments of the corresponding intangible asset, goodwill
- 缺口：发现平台与GMP制造之间的一体化流程描述
- 缺口：公司在同一供应链中控制的具体节点数量及名称
- 缺口：节点整合产生的定价权或客户锁定证据
- 缺口：未在原文中找到引用：Dr Lecault received her Ph.D. in Chemical and Biological Eng
- 证伪条件：证明GMP制造独立外包或已出售的披露
- 证伪条件：显示核心节点被竞争对手复制且客户已转移的具体事实

### earnings_validation: partial

截至2026年9月30日，公司持有7.644亿美元现金及有价证券（含1.638亿美元现金等价物），管理层明确表示流动性足够覆盖未来至少36个月运营；Q3 2026净亏损较Q3 2025下降（4076万 vs 5712万），资金状况支撑当前研究阶段业务持续推进。

- 支持 [ev_5286e22629f35ac4](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000059/abcl-20260930.htm) (primary-document): As of September 30, 2026, we had $764.4 million of cash, cash equivalents and marketable securities, comprising $163.8 million in cash and cash equivalents and $600.6 million in marketable securities.
- 支持 [ev_e37c764359303fe3](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000059/abcl-20260930.htm) (primary-document): we believe that our available liquidity from existing total cash balances (cash, cash equivalents, and restricted cash), marketable securities, and government contributions, will be sufficient to meet our working capital and capital expenditures over at least the next 36 months following the date of this report.
- 支持 [ev_bd5766b236ccb4d2](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000059/abcl-20260930.htm) (primary-document): Net loss $ ( 57,119 ) $ ( 40,758 ) $ ( 137,467 ) $ ( 139,350 )
- 缺口：各收入来源的季度增长轨迹
- 缺口：距盈亏平衡点的量化路径
- 缺口：未在原文中找到引用：Nine months ended September 30, Basic and diluted loss per s
- 缺口：通过需要直接相关的原始披露及完整证据
- 证伪条件：披露现金消耗速度显著加快致36个月跑道不可持续的具体财务数据
- 证伪条件：记录重大合同取消导致现金流入骤降的事件

### counter_thesis: partial

证据揭示了三项具体反驳因素：非独家许可允许竞争对手获取相同技术、单一供应商依赖构成供应链风险、2024年Trianni/TetraGenetics并购减值显示整合失败；但证据未覆盖地缘政治风险（加拿大研发基地）、估值压力或需求侧系统性压力测试，反驳论点不完整。

- 支持 [ev_22f2476170323116](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): The owners of these non-exclusively licensed technologies are therefore free to license them to third parties, including our competitors, on terms that may be superior to those offered to us
- 支持 [ev_6d702fe0c7278d2d](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): in 2024, we recognized a full impairment charge of the Trianni and TetraGenetics in-process research and development and there could be additional future impairments of the corresponding intangible asset, goodwill
- 支持 [ev_ea39bc3822f3a73c](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): We anticipate that some of our suppliers of critical components or materials for our processes may be single- or sole-source suppliers and the replacement of these suppliers or the identification and qualification of suitable second sources may require significant time, effort and expense
- 反证 [ev_4672d63fe89db739](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000059/abcl-20260930.htm) (primary-document): we believe that our available liquidity from existing total cash balances (cash, cash equivalents, and restricted cash), marketable securities, and government contributions, will be sufficient to meet our working capital and capital expenditures over at least the next 36 months
- 缺口：加拿大监管/地缘政治风险对研发基地的潜在影响分析
- 缺口：竞争性抗体发现平台（AI驱动平台如Absci等）的替代威胁量化分析
- 缺口：估值相对于同类平台公司的溢价/折价分析
- 缺口：主要合作伙伴收入集中度风险的具体量化
- 证伪条件：披露某竞争平台已赢得原属ABCL的重要合作伙伴的具体合同
- 证伪条件：显示AI驱动抗体设计工具已替代实验性发现平台的行业数据

### management_governance: pass

联合创始人Hansen自2012年起持续担任CEO兼董事长，CTO Lecault与CFO Booth均在任，审计师出具无保留意见，无未决调查或继任空缺；CFO Booth于2026年11月公开市场增持8,600股，提供额外支持性证据，治理结构稳定。

- 支持 [ev_0c5afb4f4bd11b78](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): Dr. Hansen is our co-founder and has served as our Chief Executive Officer, President and as the Chairman of our Board of Directors since our inception in November 2012.
- 支持 [ev_a4330e7a0ddd3045](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): Dr Lecault was our Chief Operating Officer from January 2019 to February 2025, and has served as our Chief Technology Officer since February 2025, and a member of our Board of Directors since August 2018.
- 支持 [ev_1550a8d1af91f2b3](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): our report dated February 24, 2026 expressed an unqualified opinion on those consolidated financial statements.
- 支持 [ev_cf534b0bd8bee4f4](https://www.sec.gov/Archives/edgar/data/1703057/000170305726000012/abcl-20251231.htm) (primary-document): Dr. Quake has served as a member of our Board of Directors since November 2025. Dr. Quake has been a Professor at Stanford University since 2005 and is currently the Lee Otterson Professor of Bioengineering and Professor of Applied Physics.
- 支持 [ev_ea764ee6443473d0](https://www.sec.gov/Archives/edgar/data/1703057/000183441126000010/xslF345X06/wk-form4_1794591678.xml) (primary-document): Common Shares 11/13/2026 P V 8,600 A $ 11.33 491,400 D
- 证伪条件：CEO or CFO departure
- 证伪条件：open investigation or regulatory inquiry against leadership
- 证伪条件：unresolved succession announcement
- 证伪条件：auditor qualified opinion or restatement

## ADPT · complete

审查记录：`state/serenity-reviews/ADPT-claudecli-a73c33670ac38fb9987f.json`

### supply_chain_map: unknown

证据显示ADPT有两个业务分部（MRD和免疫医学），拥有专有数据集和ML模型，并通过Harell平台向下游授权客户提供服务。但上游输入（测序技术、生物样本来源）在证据中缺失，无法绘制完整供应链图。

- 支持 [ev_1cca85903ef5d9f8](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-ex10_2.htm) (primary-document): Adaptive has developed and owns the proprietary datasets set forth in Exhibit A
- 支持 [ev_1cca85903ef5d9f8](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-ex10_2.htm) (primary-document): Adaptive has also developed and owns the proprietary machine-learning model(s) set forth in Exhibit E
- 支持 [ev_1cca85903ef5d9f8](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-ex10_2.htm) (primary-document): Harell operates a data hosting and compute platform that enables its Authorized Customers to run computational workloads on datasets and machine-learning models
- 支持 [ev_739a8bfedd281cee](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-20260930.htm) (primary-document): adpt:ImmuneMedicineBusinessMember us-gaap:OperatingSegmentsMember
- 缺口：上游输入：测序平台供应商（如Illumina）、生物样本采集来源、试剂供应链
- 缺口：MRD业务的具体下游客户（医院、实验室）身份披露
- 缺口：免疫医学业务的合作伙伴具体身份和依赖程度
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现ADPT依赖单一测序平台供应商且存在替代路径
- 证伪条件：发现Harell协议为非排他性且替代数据提供商已存在

### chokepoint_evidence: unknown

证据中没有任何关于供应集中度或替代壁垒的具体数据。ADPT拥有专有免疫组学数据和ML模型，但证据未证明其在任何供应链节点上具有垄断或寡头地位。仅有AI相关性不足以构成瓶颈证据。

- 缺口：免疫组学数据集市场中ADPT的全球市场份额
- 缺口：竞争对手数量及其数据集质量/规模的对比
- 缺口：下游客户替换ADPT数据的时间成本和技术壁垒量化
- 缺口：MRD检测市场中ADPT clonoSEQ的独占性或替代检测方案
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现多家竞争对手拥有同等规模的免疫组学数据集
- 证伪条件：发现下游药企可在短时间内切换至替代数据供应商

### customer_dependency: unknown

Harell Data Corp协议是明确的客户/平台合作关系，包含数据集和模型授权、收入分成机制。XBRL中显示有MRD收入（包含Medicare报销）和免疫医学合作收入。但缺少具体终端客户身份和收入集中度披露。

- 支持 [ev_1cca85903ef5d9f8](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-ex10_2.htm) (primary-document): AMENDED AND RESTATED DATA AND MODEL PARTNERSHIP AND PLATFORM HOSTING TRIAL AND AGREEMENT
- 支持 [ev_381fb73d4cb9cf0e](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-20260930.htm) (primary-document): adpt:MedicareReimbursementsMember 2026-07-01 2026-09-30
- 支持 [ev_739a8bfedd281cee](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-20260930.htm) (primary-document): adpt:CollaborationRevenueMember adpt:ImmuneMedicineRevenueMember 2025-07-01 2025-09-30
- 缺口：Harell协议的具体收入金额或预期收入规模
- 缺口：MRD业务的前5大客户及收入集中度
- 缺口：免疫医学合作方具体身份（Genentech等大药企是否仍为合作方）
- 缺口：hyperscaler或AI基础设施客户的确认（与Serenity方法论相关）
- 缺口：引用不存在或原文无法匹配
- 证伪条件：Harell协议仍处于试用期且尚未产生实质收入
- 证伪条件：主要合作伙伴已终止或缩减合作规模

### pure_play: partial

XBRL显示ADPT有两个运营分部：MRD业务和免疫医学业务，均围绕免疫组学平台。收入来源包括测序收入、MRD服务收入、监管里程碑收入和免疫医学合作/服务收入。整体集中于免疫组学/诊断领域，但缺少各分部收入的具体占比数据来量化主题纯度。

- 支持 [ev_739a8bfedd281cee](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-20260930.htm) (primary-document): adpt:SequencingRevenueMember 2026-01-01 2026-09-30
- 支持 [ev_6bb4d7ae0f0061b3](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-20260930.htm) (primary-document): adpt:MRDRevenueMember 2026-07-01 2026-09-30
- 支持 [ev_314137ce745dd75f](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-20260930.htm) (primary-document): adpt:ImmuneMedicineRevenueMember adpt:CollaborationRevenueMember 2026-01-01 2026-09-30
- 支持 [ev_9fcf0af132b3b4aa](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478320.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 83,902,000 for 2026-07-01 to 2026-09-30
- 缺口：MRD分部与免疫医学分部各自的收入金额
- 缺口：AI/ML相关收入在总收入中的具体占比
- 缺口：Harell数据平台协议预计贡献的收入比例
- 证伪条件：发现MRD诊断收入占比超过80%，AI/药物发现贡献微乎其微

### multi_node_control: partial

ADPT同时拥有专有免疫组学数据集和专有ML模型，并通过Harell平台将两者一起授权。数据+模型可视为两个相连节点（数据生产→模型推理）。但这更像是垂直整合的产品体系，而非对供应链多个节点的控制，缺少传统意义上的上下游供应链节点控制证据。

- 支持 [ev_e99603a8e1e52af2](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-ex10_2.htm) (primary-document): Adaptive retains all right, title, and interest in and to the Dataset, excluding Customer Models
- 支持 [ev_e99603a8e1e52af2](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-ex10_2.htm) (primary-document): Adaptive retains all right, title, and interest in and to the Adaptive Model, including all weights, parameters, architecture, configuration
- 支持 [ev_d236cc2b97d9daa6](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-ex10_2.htm) (primary-document): Harell will host the Dataset and the Adaptive Model on its servers or the servers of its cloud hosting providers
- 缺口：ADPT是否控制上游样本采集或测序环节
- 缺口：数据集与模型之间是否形成真正的供应链锁定（即客户必须同时使用两者）
- 缺口：与Serenity方法论中半导体供应链节点控制的类比证据
- 证伪条件：发现Harell客户可仅使用数据集而不使用ADPT模型，或反之
- 证伪条件：发现竞争对手提供同等数据+模型的捆绑方案

### earnings_validation: partial

Q3 2026实际财务数据已披露：收入8390万美元，净利润287.6万美元（实现盈利），但收入同比下降10.7%。YTD经营现金流为负633万美元，现金仅7561万美元。有实际的日期化财务数据，但收入下滑趋势不支持增长论点。净利润转正是积极信号但幅度很小。

- 支持 [ev_9fcf0af132b3b4aa](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478320.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 83,902,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_9fcf0af132b3b4aa](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478320.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 2,876,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_9fcf0af132b3b4aa](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478320.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 75,615,000 for as of 2026-09-30
- 反证 [ev_9fcf0af132b3b4aa](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478320.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 93,973,000, a change of -10.7%
- 反证 [ev_9fcf0af132b3b4aa](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478320.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -6,332,000 for 2026-01-01 to 2026-09-30
- 缺口：各分部（MRD vs 免疫医学）的收入明细
- 缺口：Harell协议是否已开始贡献收入
- 缺口：收入下滑的具体原因（竞争、定价、客户流失？）
- 缺口：管理层对收入趋势的展望
- 证伪条件：收入继续下滑且免疫医学合作收入未能弥补MRD下降
- 证伪条件：现金消耗加速导致融资需求

### counter_thesis: partial

可以从证据中识别出多个风险：收入同比下降10.7%、YTD经营现金流为负、现金余额仅7561万美元、发行了2031年到期可转换票据。但证据中缺少替代竞争、地缘政治风险、估值分析等维度的完整压力测试。

- 支持 [ev_9fcf0af132b3b4aa](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478320.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 93,973,000, a change of -10.7%
- 支持 [ev_9fcf0af132b3b4aa](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478320.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -6,332,000 for 2026-01-01 to 2026-09-30
- 支持 [ev_739a8bfedd281cee](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-20260930.htm) (primary-document): adpt:ZeroPercentConvertibleSeniorNotesDueTwoThousandThirtyOneMember 2026-06-22 2026-06-22
- 支持 [ev_739a8bfedd281cee](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447411/adpt-20260930.htm) (primary-document): adpt:OrbimedRoyaltyCreditOpportunitiesIvLpMember adpt:PurchaseAgreementMember 2026-09-30
- 反证 [ev_9fcf0af132b3b4aa](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478320.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 2,876,000 for 2026-07-01 to 2026-09-30
- 缺口：MRD检测市场竞争格局（Guardant、Natera等竞争对手威胁）
- 缺口：免疫医学药物发现管线的临床验证风险
- 缺口：Harell协议实际商业化进展和收入预期
- 缺口：估值合理性分析（$4.7B市值 vs 收入下滑趋势）
- 缺口：可转换票据的稀释风险量化
- 证伪条件：MRD市场被液体活检竞争对手蚕食导致收入持续下滑
- 证伪条件：免疫医学合作方终止或缩减合作
- 证伪条件：Harell数据平台未能吸引足够的授权客户
- 证伪条件：现金跑道不足需要额外融资（可转换票据+OrbiMed信贷已到位但YTD现金流为负）
- 证伪条件：4.7B市值对应收入下滑的公司估值偏高

### management_governance: unknown

证据显示多位高管在任：Kyle Piskel（CFO，签署8-K）、Chad Robins（CEO，出现在XBRL中）、Susan Bobulsky（MRD首席商务官，Form 4）。2026年6月完成可转换票据发行显示融资能力。但缺少董事会构成、治理结构、管理层变动历史等深度评估。

- 支持 [ev_5daff779ab12a8f1](https://www.sec.gov/Archives/edgar/data/1478320/000119312526447290/adpt-20261104.htm) (primary-document): By: /s/ Kyle Piskel Kyle Piskel Chief Financial Officer
- 支持 [ev_d5652ffe1acd3814](https://news.google.com/rss/articles/CBMi7gFBVV95cUxOVVlZZm1VSE5ubHhyZFVEWXROYXhScTJGSFlPakpYWmxVVG80cks5a0xwc2FnSzJMeGExWG44RVpwYlQwWHdQcWN1NEc4NWNvc2xsaW0zUmpiQUdrRElXSTI0V1VqOGxCb29Ua2xHbUswV3dNa3dTSFhKdGthVDdUcEVyLWwtT3VQYnJUellWRGRHWENWOXNoQWtCejhlWXgzLVV3MEZCS2NCM0pXbFVJVl9uZUkzcUFiaURQUHczMzB6S3lJMF9xZXpyVmF3ZmFjN2drZ3ktS0wwMWYyRmFvU29GN2FrcHRKZWUyOGJR?oc=5) (news-feed): Form 4 Adaptive Biotechnologies Corp: Susan Bobulsky (Chief Commercial Officer, MRD) For: 11 November
- 缺口：董事会独立性和构成详情
- 缺口：近期管理层变动或离职情况
- 缺口：内部人交易的方向和规模（Susan Bobulsky的Form 4具体内容未披露）
- 缺口：高管薪酬结构和激励机制
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现关键高管大量减持
- 证伪条件：发现未披露的关联方交易或治理缺陷

## AGMB · complete

审查记录：`state/serenity-reviews/AGMB-claudecli-48a1b9d94a5ecba7020f.json`

### supply_chain_map: partial

临床试验记录显示产品（ontunisertib / AGMB-129）和下游患者群体（纤维狭窄型克罗恩病），但无上游原材料、CMO或供应链关系的证据。XBRL为结构化标签，无可读供应链描述。

- 支持 [ev_9472815ed642b8a9](https://clinicaltrials.gov/study/NCT05843578) (clinicaltrials-gov): STENOVA - A Study to Evaluate Safety, Tolerability, PK and PD of AGMB-129 in Patients With Fibrostenotic Crohn's Disease
- 支持 [ev_2856e77a87b7823a](https://clinicaltrials.gov/study/NCT07683325) (clinicaltrials-gov): NOV-ERA - A Clinical Trial to Assess the Efficacy and Safety of Ontunisertib Compared to Placebo in Patients With Fibrostenosing Crohn's Disease
- 缺口：上游API/原料药供应商及CMO合同详情
- 缺口：药物生产流程及供应链地理分布
- 缺口：关键供应商集中度数据
- 证伪条件：发现公司无自主生产能力且唯一CMO出现产能问题
- 证伪条件：关键原材料被单一供应商垄断且无替代来源

### chokepoint_evidence: unknown

证据中无任何关于供应集中度或替代壁垒的信息。Agomab是一家临床阶段生物制药公司，所提供的证据仅显示临床试验存在，不涉及供应链瓶颈。

- 缺口：该药物靶点或机制的独占性证据
- 缺口：竞争对手管线对比及替代疗法分析
- 缺口：纤维狭窄型克罗恩病治疗领域的供应/竞争格局
- 证伪条件：多家竞争对手拥有同靶点或同适应症的临床管线
- 证伪条件：该机制可被已上市药物或通用疗法替代

### customer_dependency: unknown

公司处于临床Phase 2阶段，无已上市产品，无客户或采购方的披露。临床试验记录仅证明试验存在及招募状态，不构成客户依赖证据。

- 缺口：任何合作伙伴、许可协议或商业化安排的披露
- 缺口：支付方（保险公司/医疗系统）的潜在采纳信号
- 缺口：与大型药企的合作开发或分销协议
- 证伪条件：适应症患者群体极小导致商业化不可行
- 证伪条件：支付方拒绝纳入报销目录

### pure_play: partial

两项临床试验均针对纤维狭窄型克罗恩病（AGMB-129/ontunisertib），表明公司聚焦单一治疗领域，符合纯正标的特征。但缺乏收入分部或业务线多元化的具体披露来完整评估。

- 支持 [ev_9472815ed642b8a9](https://clinicaltrials.gov/study/NCT05843578) (clinicaltrials-gov): A Study to Evaluate Safety, Tolerability, PK and PD of AGMB-129 in Patients With Fibrostenotic Crohn's Disease
- 支持 [ev_2856e77a87b7823a](https://clinicaltrials.gov/study/NCT07683325) (clinicaltrials-gov): A Clinical Trial to Assess the Efficacy and Safety of Ontunisertib Compared to Placebo in Patients With Fibrostenosing Crohn's Disease
- 缺口：公司其他管线（若有）的详细信息
- 缺口：业务分部或收入来源的正式披露
- 缺口：公司战略中对AI医疗主题的关联度说明
- 证伪条件：公司实际拥有多个不相关治疗领域的管线，稀释主题集中度

### multi_node_control: unknown

证据中无任何关于公司控制多个供应链节点的信息。作为临床阶段药物开发公司，XBRL标签显示有许可证和在研研发资产，但无法从中推断多节点控制。

- 缺口：公司是否拥有自主生产设施或关键技术平台
- 缺口：是否纵向整合了药物发现、生产和分销环节
- 缺口：是否控制了关键知识产权和生产工艺
- 证伪条件：公司完全依赖外部CRO/CMO，无自主控制的供应链节点

### earnings_validation: unknown

公司处于preparation阶段（Phase 2），预期无收入。SEC 20-F的XBRL数据为结构化标签，无法从中提取可读的现金余额、烧钱率或跑道月数。smallCapContext中cashM、burnPerMonthM、runwayMonths均为null。无法评估公司是否有足够资金推进下一里程碑。

- 缺口：可读的现金及现金等价物余额
- 缺口：季度/年度运营支出和烧钱率
- 缺口：资金跑道（至少12个月）的明确数据
- 缺口：IPO融资净额的具体数字
- 证伪条件：现金余额不足12个月烧钱率且无已披露融资安排
- 证伪条件：运营支出急剧增加且无对应资金来源

### counter_thesis: partial

可识别关键风险但证据不足以充分压力测试。Phase 2试验（STENOVA已完成，NOV-ERA正在招募）面临临床失败风险。公司2026年2月刚IPO，融资风险标记为false但无现金数据支持。作为$202M市值的临床阶段公司，二次发行稀释风险存在。缺乏竞争格局、替代疗法和地缘政治风险的引用证据。

- 支持 [ev_9472815ed642b8a9](https://clinicaltrials.gov/study/NCT05843578) (clinicaltrials-gov): Highest listed phase: Phase 2. Overall status: COMPLETED
- 支持 [ev_2856e77a87b7823a](https://clinicaltrials.gov/study/NCT07683325) (clinicaltrials-gov): Highest listed phase: Phase 2. Overall status: RECRUITING. Start date: 2026-10-30
- 缺口：Phase 2临床数据结果及成功概率基线
- 缺口：竞争对手同适应症管线进展对比
- 缺口：现金跑道数据以评估融资稀释风险
- 缺口：该适应症市场规模及定价预期
- 证伪条件：Phase 2试验未达主要终点
- 证伪条件：竞争对手率先获批同适应症疗法
- 证伪条件：现金不足被迫在低估值时增发
- 证伪条件：FDA对该类药物提出额外安全性要求

### management_governance: unknown

XBRL标签中出现KeyManagementPersonnelOfEntityOrParentMember引用，但无可读的管理层姓名、背景、任期或治理结构信息。无法评估领导层连续性或治理质量。

- 缺口：CEO及关键高管的背景和任期
- 缺口：董事会构成及独立性
- 缺口：近期管理层变动记录
- 缺口：公司治理结构及内部控制评估
- 证伪条件：关键高管近期离职且未有合适继任者
- 证伪条件：存在未解决的监管调查或治理争议

## AGPU · complete

审查记录：`state/serenity-reviews/AGPU-claudecli-7a47bea1b503e8681776.json`

### supply_chain_map: partial

XBRL标签显示公司有两个业务板块——计算服务(Compute Services)和药物发现服务(Drug Discovery Services)，但证据中未披露具体的上游输入供应商、GPU/算力来源或下游客户名称。客户集中度风险已披露但客户匿名化处理。

- 支持 [ev_1179348dae1d4fc7](https://www.sec.gov/Archives/edgar/data/1446159/000117184326003484/agpu20260331_10q.htm) (primary-document): agpu:ComputeServicesMember 2026-03-31 0001446159 agpu:DrugDiscoveryServicesMember 2026-03-31
- 支持 [ev_09a8f35353602cbc](https://www.sec.gov/Archives/edgar/data/1446159/000117184326005556/agpu20260630_10q.htm) (primary-document): us-gaap:RevenueFromContractWithCustomerMember us-gaap:CustomerConcentrationRiskMember agpu:CustomerAMember 2026-01-01 2026-06-30
- 缺口：上游GPU/算力硬件供应商名称及采购条款
- 缺口：药物发现服务所用AI平台/模型来源
- 缺口：下游客户实际名称及所属行业
- 证伪条件：若公司仅转售第三方算力而非自有基础设施，则供应链定位完全不同

### chokepoint_evidence: unknown

证据中无任何信息表明Axe Compute在药物发现或计算服务领域拥有供应集中度或替代壁垒。计算服务和AI药物发现均为竞争激烈的市场，无垄断/寡占证据。

- 缺口：全球市场份额数据
- 缺口：专有技术或专利壁垒证据
- 缺口：客户转换成本或锁定机制说明
- 缺口：不通过需要直接反证，缺少证据不能等同失败
- 证伪条件：若有多家公司提供同类AI药物发现计算服务，则不存在瓶颈

### customer_dependency: partial

10-Q XBRL披露了客户集中度风险（CustomerA、CustomerB、CustomerC），且应收账款从$32K增至$3.3M、合同负债从$144K激增至$60.7M，表明有实际客户在付款和预付。但所有客户均匿名，无法确认具体采用情况。

- 支持 [ev_09a8f35353602cbc](https://www.sec.gov/Archives/edgar/data/1446159/000117184326005556/agpu20260630_10q.htm) (primary-document): us-gaap:AccountsReceivableMember us-gaap:CustomerConcentrationRiskMember agpu:CustomerCMember 2026-01-01 2026-06-30
- 支持 [ev_361bd661b7dfa7e1](https://www.sec.gov/Archives/edgar/data/1446159/000117184326005556/agpu20260630_10q.htm) (primary-document): Accounts receivable 3,321,426 32,120 Compute prepayments 11,148,981
- 支持 [ev_361bd661b7dfa7e1](https://www.sec.gov/Archives/edgar/data/1446159/000117184326005556/agpu20260630_10q.htm) (primary-document): Contract liabilities 33,645,987 144,076
- 缺口：客户名称及行业（制药公司、生物科技、CRO等）
- 缺口：合同期限及续约条款
- 缺口：客户各自的收入贡献百分比
- 证伪条件：合同负债激增可能来自计算服务而非药物发现
- 证伪条件：若主要客户为关联方或crypto项目（如Aethir），则药物发现主题不成立

### pure_play: unknown

公司同时经营计算服务和药物发现两个板块，且持有大量数字资产（Aethir ATH代币）。Q2 2026数字资产损失$13.1M远超同期收入$3.2M。数字资产头寸使公司实质上是加密币+AI计算+药物发现的混合体，远非AI药物发现纯标的。

- 支持 [ev_ee22a7a720db2a9f](https://www.sec.gov/Archives/edgar/data/1446159/000117184326005556/agpu20260630_10q.htm) (primary-document): Gains (losses) on digital assets ( 13,125,352 ) - ( 17,421,620 )
- 支持 [ev_361bd661b7dfa7e1](https://www.sec.gov/Archives/edgar/data/1446159/000117184326005556/agpu20260630_10q.htm) (primary-document): Digital assets 11,268,342 24,439,598 Digital asset receivable 7,547,221 7,226,475
- 支持 [ev_1179348dae1d4fc7](https://www.sec.gov/Archives/edgar/data/1446159/000117184326003484/agpu20260331_10q.htm) (primary-document): agpu:AethirATHMember 2025-01-01 2025-12-31 0001446159 agpu:AethirATHMember 2025-12-31
- 缺口：药物发现服务收入占比
- 缺口：计算服务与药物发现各自的毛利率
- 缺口：不通过需要直接反证，缺少证据不能等同失败
- 证伪条件：若药物发现收入占比低于20%，该公司本质上是crypto计算服务公司

### multi_node_control: unknown

无证据显示公司控制两个相连的供应链节点。计算服务和药物发现可视为两个业务板块，但不构成同一供应链上的上下游关系，也无纵向整合证据。

- 缺口：自有算力基础设施vs租赁的说明
- 缺口：药物发现中是否使用自有计算资源的关联描述
- 缺口：技术栈的纵向整合证据
- 缺口：不通过需要直接反证，缺少证据不能等同失败
- 证伪条件：若计算服务仅为转售第三方GPU算力则不构成任何节点控制

### earnings_validation: partial

XBRL显示Q3 2026收入$7.24M（同比从$3.6K增长），Q2收入$3.21M，收入增长趋势明确。但公司持续大额亏损（H1 2026净亏损$24.9M），且亏损主要来自数字资产减值而非运营。收入快速增长但无法判断多少来自药物发现vs计算服务，且盈利能力远未验证。

- 支持 [ev_5489b029c0b9b8c0](https://data.sec.gov/api/xbrl/companyfacts/CIK0001446159.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerIncludingAssessedTax): 7,243,043 for 2026-07-01 to 2026-09-30
- 支持 [ev_ee22a7a720db2a9f](https://www.sec.gov/Archives/edgar/data/1446159/000117184326005556/agpu20260630_10q.htm) (primary-document): Revenue $ 3,214,992 $ 2,682 $ 3,250,303 $ 112,992
- 支持 [ev_5489b029c0b9b8c0](https://data.sec.gov/api/xbrl/companyfacts/CIK0001446159.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 11,503,607 for 2026-07-01 to 2026-09-30
- 反证 [ev_ee22a7a720db2a9f](https://www.sec.gov/Archives/edgar/data/1446159/000117184326005556/agpu20260630_10q.htm) (primary-document): Total operating (loss) $ ( 17,328,010 ) $ ( 2,659,868 ) $ ( 25,056,691 ) $ ( 4,946,915 )
- 反证 [ev_10ac329c3d2a3ab1](https://www.sec.gov/Archives/edgar/data/1446159/000117184326003484/agpu20260331_10q.htm) (primary-document): Revenue $ 35,311 $ 110,310 Gains (losses) on digital assets ( 4,296,268 )
- 缺口：按业务板块的收入拆分
- 缺口：Q3 2026净利润为正$11.5M的具体原因（可能是数字资产收益而非运营利润）
- 证伪条件：Q3净利润为正可能完全源于数字资产升值而非经营改善
- 证伪条件：Q1 2026收入仅$35K说明收入波动极大、可持续性存疑

### counter_thesis: unknown

反面论证已充分检视：(1) 数字资产占总资产巨大比例，价格波动直接冲击损益；(2) 累计亏损$4.38亿，远超总收入；(3) 大量股权稀释（从4M股增至11.6M股仅半年）；(4) 收入季度间波动极大（Q1仅$35K vs Q2 $3.2M vs Q3 $7.2M）；(5) 药物发现收入占比不明，可能为crypto计算服务公司包装。作为小盘股，虽现金$147.7M、跑道充裕(financingRisk: false)，但数字资产占比意味着实际现金缓冲远低于表面数字。

- 支持 [ev_ee22a7a720db2a9f](https://www.sec.gov/Archives/edgar/data/1446159/000117184326005556/agpu20260630_10q.htm) (primary-document): Gains (losses) on digital assets ( 13,125,352 ) - ( 17,421,620 )
- 支持 [ev_c38862fec812c64a](https://www.sec.gov/Archives/edgar/data/1446159/000117184326005556/agpu20260630_10q.htm) (primary-document): As of August 13, 2026, the registrant had 11,591,124 shares of common stock, par value $0.01 per share outstanding
- 支持 [ev_7aff5da4f9e1ecad](https://www.sec.gov/Archives/edgar/data/1446159/000117184326003484/agpu20260331_10q.htm) (primary-document): As of May 11, 2026, the registrant had 10,404,641 shares of common stock, par value $0.01 per share outstanding
- 缺口：Aethir代币持仓的锁仓/归属条款
- 缺口：同行业AI药物发现公司估值对比
- 缺口：引用不存在或原文无法匹配
- 证伪条件：数字资产大幅贬值可能导致资产负债表恶化和被迫减持
- 证伪条件：持续稀释可能使股价长期受压
- 证伪条件：若Aethir项目失败，数字资产应收款项可能无法回收
- 证伪条件：药物发现业务可能始终无法规模化

### management_governance: unknown

证据中仅能看到CEO获得RSU授予以及各类股权激励安排，但无管理层姓名、背景、任期或治理结构的实质性描述。未发现公开调查或诉讼披露（Legal Proceedings条目存在但无内容摘录），信息不足以评估。

- 缺口：CEO及高管姓名、任期和行业背景
- 缺口：董事会独立性及构成
- 缺口：管理层持股比例
- 缺口：关联交易详情（特别是与Aethir/Renovaro的关系）
- 缺口：引用不存在或原文无法匹配
- 证伪条件：Renovaro Extension Agreement和多次PIPE交易暗示可能存在关联方利益安排
- 证伪条件：若管理层此前有不良记录则治理评估需降级

## AIAI · complete

审查记录：`state/serenity-reviews/AIAI-claudecli-eef7227de7411019a92d.json`

### supply_chain_map: unknown

证据仅包含S-1 XBRL元数据标签，无可读叙述描述上游输入、公司产品或下游用户的具体关系。标签显示该公司是控股公司，拥有建筑、医疗、AI研究等子公司（BondStreetLimited、CCCarlton、VanguardHealthcare、AIResearchCorporation等），但无法从元数据中提取实际供应链映射。

- 缺口：公司产品/服务的可读描述
- 缺口：上游供应商及原材料的具体信息
- 缺口：下游客户及使用场景的叙述性说明
- 缺口：各子公司业务之间的供应链关系
- 证伪条件：发现该公司各子公司之间无实际供应链联系，仅为财务并购拼盘
- 证伪条件：建筑业务与AI药物发现之间无任何技术或供应链关联

### chokepoint_evidence: unknown

无任何证据表明AIAI在任何供应链节点具有供给集中度或替代壁垒。XBRL元数据仅显示多个子公司跨行业运营（建筑、医疗、IT、AI研究），未显示任何关键输入的垄断或寡头地位。'AI'相关命名本身不构成瓶颈证据。

- 缺口：全球市场份额数据
- 缺口：替代供应商分析
- 缺口：技术壁垒或专利护城河的说明
- 缺口：任何供给集中度指标
- 证伪条件：该公司所处领域（建筑、通用医疗、AI咨询）均为高度竞争市场，无固有瓶颈

### customer_dependency: partial

XBRL标签中存在客户集中度风险披露（CustomerConcentrationRiskMember），表明公司确实有客户，但元数据未包含客户名称、收入占比等可读信息。仅能确认存在客户集中度披露义务，不足以判断具体采用情况。

- 支持 [ev_42ab0028df2f7edb](https://www.sec.gov/Archives/edgar/data/2096362/000149315226047623/forms-1.htm) (primary-document): us-gaap:AccountsReceivableMember AIAI:CustomerOneMember us-gaap:CustomerConcentrationRiskMember 2026-01-01 2026-06-30
- 支持 [ev_42ab0028df2f7edb](https://www.sec.gov/Archives/edgar/data/2096362/000149315226047623/forms-1.htm) (primary-document): us-gaap:SalesRevenueNetMember AIAI:CustomerOneMember us-gaap:CustomerConcentrationRiskMember 2026-05-07 2026-06-30
- 缺口：客户名称及具体收入占比
- 缺口：合同或设计锁定证据
- 缺口：客户使用公司产品的具体场景描述
- 证伪条件：客户集中度标签可能仅来自建筑子公司的政府合同，与AI药物发现无关

### pure_play: unknown

XBRL标签明确显示AIAI是多元化控股公司，业务横跨建筑（ConstructionMember/ConstructionRevenueStreamMember）、医疗（HealthCareMember）、AI研究等多个不相关行业。子公司包括建筑公司CCCarlton、网络公司ConstellationNetwork、医疗公司VanguardHealthcare等。这不是药物发现纯参与者，而是典型的收购拼盘控股公司。

- 反证 [ev_b3146c4e1d122199](https://www.sec.gov/Archives/edgar/data/2096362/000149315226047623/forms-1.htm) (primary-document): AIAI:PublicSectorMember us-gaap:ConstructionMember 2026-05-07 2026-06-30
- 反证 [ev_b3146c4e1d122199](https://www.sec.gov/Archives/edgar/data/2096362/000149315226047623/forms-1.htm) (primary-document): AIAI:PublicSectorMember us-gaap:HealthCareMember 2026-05-07 2026-06-30
- 反证 [ev_a7c8ac4634317e10](https://www.sec.gov/Archives/edgar/data/2096362/000149315226047623/forms-1.htm) (primary-document): AIAI:ConstructionEquipmentMember srt:MinimumMember 2026-06-30
- 缺口：各业务线收入分拆数据
- 缺口：AI药物发现业务的具体收入贡献比例
- 缺口：引用不存在或原文无法匹配
- 证伪条件：建筑和通用医疗收入流表明主题敞口被严重稀释
- 证伪条件：多子公司跨行业结构与纯参与者定义根本矛盾

### multi_node_control: unknown

虽然AIAI拥有多个子公司，但无证据表明它们在同一供应链中控制两个以上连续节点。子公司分布在建筑、医疗、AI研究等不相关行业，属于多元化控股而非垂直整合。拥有多个产品不等于控制连续供应链节点。

- 反证 [ev_a7c8ac4634317e10](https://www.sec.gov/Archives/edgar/data/2096362/000149315226047623/forms-1.htm) (primary-document): AIAI:VanguardHealthcareSolutionsLLCMember us-gaap:CommonClassAMember 2026-05-06 2026-05-06
- 缺口：子公司之间供应链关系的说明
- 缺口：垂直整合或连续节点控制的证据
- 缺口：引用不存在或原文无法匹配
- 证伪条件：建筑公司与AI研究公司之间无供应链联系，仅为财务并表关系

### earnings_validation: unknown

作为准备阶段公司，核心评估标准是能否资助下一个里程碑。XBRL数据显示2026年3月31日现金为零，Q1净亏损271.8万美元，经营现金流为负173万。即便考虑2026年5月IPO后的融资（上下文显示1120万现金），月烧钱率约592万，跑道仅约1.9个月——远低于12个月安全线。公司明显无法以现有现金资助下一个里程碑。

- 支持 [ev_5eb248c830390128](https://data.sec.gov/api/xbrl/companyfacts/CIK0002096362.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 0 for as of 2026-03-31
- 支持 [ev_5eb248c830390128](https://data.sec.gov/api/xbrl/companyfacts/CIK0002096362.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -2,718,000 for 2026-01-01 to 2026-03-31
- 支持 [ev_5eb248c830390128](https://data.sec.gov/api/xbrl/companyfacts/CIK0002096362.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -1,730,000 for 2026-01-01 to 2026-03-31
- 缺口：IPO后最新季度的现金余额披露
- 缺口：融资计划或信贷额度信息
- 缺口：烧钱率趋势及成本控制措施
- 缺口：不通过需要直接反证，缺少证据不能等同失败
- 证伪条件：即使IPO募资后现金仅够不到2个月运营
- 证伪条件：S-1注册声明可能预示进一步股权融资，加剧稀释

### counter_thesis: partial

基于证据可识别以下重大反面论点：(1) 现金跑道极短（~1.9个月），financingRisk为true，稀释性股权融资几乎确定；(2) 多元化控股结构与AI药物发现主题严重不符；(3) 零收入且现金耗尽。S-1注册声明（2026-10-19提交）强烈暗示即将进行股票增发。但证据包仅含XBRL元数据，无法进行完整的供给、需求、替代、地缘政治压力测试。

- 支持 [ev_5eb248c830390128](https://data.sec.gov/api/xbrl/companyfacts/CIK0002096362.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 0 for 2026-01-01 to 2026-03-31
- 支持 [ev_5eb248c830390128](https://data.sec.gov/api/xbrl/companyfacts/CIK0002096362.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 0 for as of 2026-03-31
- 缺口：竞争对手分析及替代路径评估
- 缺口：地缘政治风险评估
- 缺口：估值合理性分析（83M市值 vs 零收入控股公司）
- 缺口：管理层增发意图的明确披露
- 证伪条件：跑道不足2个月，稀释性增发（S-1已提交）几乎板上钉钉——这是最关键的反面路径
- 证伪条件：控股公司结构可能仅为壳公司借AI概念炒作
- 证伪条件：建筑+医疗+AI拼盘结构缺乏协同效应逻辑

### management_governance: unknown

证据包中无关于管理层背景、治理结构、董事会组成或领导层连续性的可读信息。XBRL标签中出现ChiefExecutiveOfficerMember引用，但无具体人名或任职信息。双重股权结构（ClassA/ClassB）可能暗示投票权集中，但无详细信息可供评估。

- 缺口：CEO及高管团队背景信息
- 缺口：董事会独立性及组成
- 缺口：双重股权结构的具体投票权比例
- 缺口：关联方交易详情（XBRL中有RelatedPartyMember标签）
- 缺口：任何正在进行的调查或诉讼信息
- 证伪条件：双重股权结构可能导致少数股东权益受损
- 证伪条件：RelatedPartyMember标签暗示可能存在关联方交易风险

## ALEC · complete

审查记录：`state/serenity-reviews/ALEC-claudecli-75310e8b1d414504491d.json`

### supply_chain_map: unknown

上游：依赖CDMO合作伙伴和第三方原材料供应商进行药物生产，但未披露具体供应商名称。公司产品：ABC血脑屏障递送平台及多条管线（AL050 GCase ERT、抗Aβ抗体、Tau siRNA等）。下游：Genentech（Roche）获AL050全球独家许可，GSK合作开发nivisnebart。整体供应链结构可辨识，但上游供应商具体身份缺失。

- 支持 [ev_aa275e7284d20d05](https://www.sec.gov/Archives/edgar/data/1653087/000119312526413090/alec-ex99_01.htm) (sec-8k): Alector grants Genentech exclusive rights to develop and commercialize AL050, an investigational GCase Enzyme Replacement Therapy (ERT) enabled by Alector Brain Carrier (ABC)
- 支持 [ev_e82e655ade8b45bf](https://www.sec.gov/Archives/edgar/data/1653087/000119312526071593/alec-20251231.htm) (primary-document): Under the terms of the GSK Agreement, we received $700 million in upfront payments, of which $500 million was received in August 2021 and $200 million was received in January 2022
- 缺口：具体CDMO合作伙伴名称（如Lonza、Catalent等）
- 缺口：关键原材料供应商身份及地理集中度
- 缺口：备用供应商或双重来源安排的披露
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现CDMO已终止合作或无法交付
- 证伪条件：关键原材料出现长期供应中断

### chokepoint_evidence: unknown

Alector拥有ABC血脑屏障递送平台专利（TfR结合组合物专利至2043-2046年），以及工程化GCase酶技术，但证据中未显示供应集中度或替代壁垒的具体数据。生物技术公司的专利保护是标准做法，不等同于物理供应链瓶颈。没有证据表明ABC平台在BBB递送领域具有寡头或垄断地位。

- 支持 [ev_c90e4aa57fa0bff1](https://www.sec.gov/Archives/edgar/data/1653087/000119312526071593/alec-20251231.htm) (primary-document): Two of those patent families relate to compositions that bind to transferrin receptor (TfR) and methods of use. The first of those two patent families is 16 expected to expire in 2043
- 支持 [ev_aa275e7284d20d05](https://www.sec.gov/Archives/edgar/data/1653087/000119312526413090/alec-ex99_01.htm) (sec-8k): AL050 addresses this by pairing an engineered GCase enzyme with our proprietary Alector Brain Carrier technology designed to cross the blood-brain barrier
- 缺口：BBB递送平台领域的竞争格局数据（如Denali的TV平台等竞品对比）
- 缺口：ABC平台相对竞品的技术替代难度和时间线
- 缺口：市场份额或技术采用集中度数据
- 证伪条件：竞争对手的BBB递送平台在临床中展示出同等或更优效果
- 证伪条件：大型药企自主开发出可绕过ABC平台的替代递送技术

### customer_dependency: unknown

两大合作伙伴已确认：Genentech（Roche）签署AL050全球独家许可协议，支付1亿美元预付款加最高11.7亿里程碑付款；GSK签署合作协议支付7亿美元预付款加最高15亿里程碑付款。这些是已签约的许可/合作关系而非产品销售客户，公司尚无商业化产品。合作依赖明确但终端用户（患者）采用尚未发生。

- 支持 [ev_aa275e7284d20d05](https://www.sec.gov/Archives/edgar/data/1653087/000119312526413090/alec-ex99_01.htm) (sec-8k): Alector will receive an upfront payment of $100 million and is also eligible to receive additional payments of up to $1.17 billion upon the achievement of development, regulatory, and commercial milestones
- 支持 [ev_e82e655ade8b45bf](https://www.sec.gov/Archives/edgar/data/1653087/000119312526071593/alec-20251231.htm) (primary-document): In addition, we may be eligible to receive up to an additional $1.5 billion in clinical development, regulatory, and commercial launch-related milestone payments, subject to successful advancement and commercialization of product candidates
- 缺口：除GSK和Genentech外是否有其他潜在合作伙伴或客户
- 缺口：合作协议的终止条款和退出机制细节
- 缺口：GSK合作项目nivisnebart的最新临床进展
- 缺口：引用不存在或原文无法匹配
- 证伪条件：GSK或Genentech终止合作协议
- 证伪条件：合作项目临床试验失败导致里程碑付款无法实现

### pure_play: unknown

Alector 100%专注于神经退行性疾病治疗药物开发，以ABC血脑屏障递送平台为核心技术，管线覆盖帕金森病、阿尔茨海默病、FTD等适应症。所有收入均来自相关许可和合作协议。无其他业务分散主题敞口。

- 支持 [ev_aa275e7284d20d05](https://www.sec.gov/Archives/edgar/data/1653087/000119312526413090/alec-ex99_01.htm) (sec-8k): Alector, Inc. (Nasdaq: ALEC), a biotechnology company focused on developing therapies to counteract the devastating progression of neurodegeneration
- 支持 [ev_e82e655ade8b45bf](https://www.sec.gov/Archives/edgar/data/1653087/000119312526071593/alec-20251231.htm) (primary-document): We have not generated any product or royalty revenue from product sales and do not expect to do so in the near future
- 缺口：引用不存在或原文无法匹配
- 证伪条件：公司进入与神经退行性疾病无关的治疗领域并分散资源

### multi_node_control: unknown

Alector同时拥有ABC递送平台技术（载体/递送节点）和工程化治疗蛋白（如GCase酶、抗Aβ抗体等有效载荷节点），两者结合形成最终产品。公司保留ABC平台所有权并可在全部自有管线中应用。但这属于典型生物技术垂直整合，证据不足以证明这构成供应链上两个相连节点的独占控制。

- 支持 [ev_10d192aa148ea684](https://www.sec.gov/Archives/edgar/data/1653087/000119312526413090/alec-ex99_01.htm) (primary-document): Alector retains ownership of ABC and full rights to apply the platform across its wholly owned pipeline
- 缺口：ABC平台是否被第三方许可用于其他药物（作为独立供应节点的证据）
- 缺口：公司是否控制关键生产环节而非依赖CDMO
- 缺口：引用不存在或原文无法匹配
- 证伪条件：ABC平台被证明可由其他BBB递送技术轻松替代
- 证伪条件：公司失去对关键技术节点的专利保护

### earnings_validation: unknown

临床阶段公司，无产品收入属预期。Q3 2026收入1.629亿美元（主要为GSK合作里程碑确认），净利润1.246亿美元。2026-09-30现金7,547万美元，但10月Genentech支付1亿美元预付款。CEO明确表示Genentech交易将现金跑道延长至2029年。月均烧钱率约1,200万美元。虽然smallCapContext显示financingRisk为true（基于9月底现金），但10月到账的1亿美元显著改善了状况。整体来看公司可以资助下一个里程碑，但仍依赖里程碑付款实现，存在不确定性。

- 支持 [ev_5f58d8022d2cde8f](https://data.sec.gov/api/xbrl/companyfacts/CIK0001653087.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 162,866,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_5f58d8022d2cde8f](https://data.sec.gov/api/xbrl/companyfacts/CIK0001653087.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 75,472,000 for as of 2026-09-30
- 反证 [ev_5f58d8022d2cde8f](https://data.sec.gov/api/xbrl/companyfacts/CIK0001653087.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -108,184,000 for 2026-01-01 to 2026-09-30
- 缺口：Genentech 1亿美元到账后的最新现金余额确认
- 缺口：2027-2029年详细烧钱率预测和里程碑付款时间表
- 缺口：Hercules Capital贷款的具体条款和偿还时间
- 缺口：引用不存在或原文无法匹配
- 证伪条件：Genentech或GSK终止合作导致里程碑付款中断
- 证伪条件：烧钱率大幅超出预期缩短跑道至12个月以内
- 证伪条件：临床试验失败导致需要额外融资

### counter_thesis: partial

关键反面论据：（1）两项Phase 3试验（INFRONT-3和latozinemab延续研究）均已终止，说明管线存在重大失败风险；（2）9月底现金仅7,547万，financingRisk为true，虽然Genentech交易缓解但跑道依赖里程碑实现；（3）完全依赖CDMO生产，无自有产能；（4）BBB递送领域存在竞争者。积极因素：Genentech和GSK两大合作验证了平台价值，专利保护至2043-2046年。鉴于financingRisk为true，股权融资稀释是明确的反面路径。需要更多竞争格局和替代技术数据来完整评估。

- 支持 [ev_616d6eebbd3b50b4](https://clinicaltrials.gov/study/NCT04374136) (clinicaltrials-gov): A Phase 3 Study to Evaluate Efficacy and Safety of AL001 in Frontotemporal Dementia (INFRONT-3). Highest listed phase: Phase 3. Overall status: TERMINATED
- 支持 [ev_62dfd2e1588d1990](https://clinicaltrials.gov/study/NCT06111014) (clinicaltrials-gov): Continuation Study for Latozinemab. Highest listed phase: Phase 3. Overall status: TERMINATED
- 支持 [ev_603801f878c63c3d](https://www.sec.gov/Archives/edgar/data/1653087/000119312526071593/alec-20251231.htm) (primary-document): We do not have long-term supply agreements, and we purchase our required drug product on a development manufacturing services agreement or purchase order basis
- 反证 [ev_616d6eebbd3b50b4](https://clinicaltrials.gov/study/NCT04374136) (clinicaltrials-gov): A Phase 3 Study to Evaluate Efficacy and Safety of AL001 in Frontotemporal Dementia (INFRONT-3). Highest listed phase: Phase 3. Overall status: TERMINATED
- 反证 [ev_62dfd2e1588d1990](https://clinicaltrials.gov/study/NCT06111014) (clinicaltrials-gov): Continuation Study for Latozinemab. Highest listed phase: Phase 3. Overall status: TERMINATED
- 缺口：BBB递送领域竞争对手（Denali TV平台、JCR等）的详细对比
- 缺口：帕金森GCase ERT领域其他在研疗法的进展
- 缺口：阿尔茨海默抗Aβ领域竞品的竞争压力分析
- 缺口：估值合理性分析（$383M市值 vs 管线价值）
- 证伪条件：AL050（GCase ERT）临床试验失败
- 证伪条件：Genentech终止AL050许可协议
- 证伪条件：GSK终止nivisnebart合作
- 证伪条件：竞争对手BBB递送平台在临床中展示优越数据
- 证伪条件：公司被迫在不利条件下进行股权融资（稀释风险）
- 证伪条件：ABC平台核心专利被无效化

### management_governance: partial

EY审计确认截至2025年12月31日内部控制有效。CEO Arnon Rosenthal持续领导公司并主导Genentech交易。但证据显示Sara Kenkare-Mitra博士于2025年12月22日签署离职协议，高管变动未见继任披露。整体治理框架健全，但关键高管离职的背景和继任安排信息不足。

- 支持 [ev_7e06c1e2cb2985e3](https://www.sec.gov/Archives/edgar/data/1653087/000119312526071593/alec-20251231.htm) (primary-document): Based on this assessment, management concluded that our internal control over financial reporting was effective as of December 31, 2025
- 支持 [ev_7e06c1e2cb2985e3](https://www.sec.gov/Archives/edgar/data/1653087/000119312526071593/alec-20251231.htm) (primary-document): In our opinion, Alector, Inc. (the Company) maintained, in all material respects, effective internal control over financial reporting as of December 31, 2025, based on the COSO criteria
- 支持 [ev_aa275e7284d20d05](https://www.sec.gov/Archives/edgar/data/1653087/000119312526413090/alec-ex99_01.htm) (sec-8k): said Arnon Rosenthal, Ph.D., Chief Executive Officer of Alector
- 反证 [ev_c5ecd79ea9a856b9](https://www.sec.gov/Archives/edgar/data/1653087/000119312526071593/alec-20251231.htm) (primary-document): Separation Agreement, dated December 22, 2025, by and between Alector, Inc. and Saraswati (Sara) Kenkare-Mitra, Ph.D.
- 缺口：Sara Kenkare-Mitra离职原因及其原职位
- 缺口：继任者任命信息
- 缺口：董事会组成和独立性详情
- 缺口：高管薪酬与公司绩效的对齐情况
- 证伪条件：CEO Arnon Rosenthal离职
- 证伪条件：发现重大内控缺陷或财务重述
- 证伪条件：董事会成员大规模更替引发治理不稳定

## ANIK · complete

审查记录：`state/serenity-reviews/ANIK-claudecli-3196c0cc080832c505df.json`

### supply_chain_map: partial

上游：透明质酸（HA）原料来自少数供应商，Bedford工厂自主生产；下游：J&J MedTech（美国OA疼痛管理分销）、Boehringer Ingelheim（Hyvisc兽用分销）、医院和门诊手术中心。但上游具体供应商名称未披露，供应链图谱不完整。

- 支持 [ev_1e7a041875ec0f3e](https://www.sec.gov/Archives/edgar/data/898437/000117184326001275/anik20251231_10k.htm) (primary-document): We manufacture all of our HA-based products, including our OA Pain Management and Regenerative Solutions products, as well as certain additional products, at our facility in Bedford, Massachusetts
- 支持 [ev_23bc7a8aedc9ae36](https://www.sec.gov/Archives/edgar/data/898437/000117184326001275/anik20251231_10k.htm) (primary-document): We rely on a small number of suppliers for certain key raw materials and components for the manufacturing and delivery of our products
- 支持 [ev_80c91812c2ff4c26](https://www.sec.gov/Archives/edgar/data/898437/000117184326001275/anik20251231_10k.htm) (primary-document): Our largest customer, J&J MedTech, represented 50% of total revenues for the year ended December 31, 2025
- 支持 [ev_24a824879d0559b4](https://www.sec.gov/Archives/edgar/data/898437/000117184326007211/exh_991.htm) (primary-document): Anika entered a new 10-year partnership for the distribution of Hyvisc with its existing partner, Boehringer Ingelheim
- 缺口：上游HA原料具体供应商名称及份额
- 缺口：关键原材料地理集中度信息
- 缺口：替代供应商资质认定周期
- 证伪条件：发现HA原料有大量可替代供应商，Anika无任何上游议价权
- 证伪条件：Bedford单一工厂出现重大生产中断

### chokepoint_evidence: unknown

无证据表明Anika在任何供应链节点拥有垄断或寡头地位。HA技术有多家竞争对手，公司自身披露替代供应商可能存在。知识产权段落均为通用风险语言，不构成瓶颈证据。与AI医疗无关。

- 缺口：HA注射市场份额数据（Anika vs Ferring vs 其他）
- 缺口：透明质酸基材料在骨科领域的替代壁垒量化
- 缺口：任何证明供应集中度（<5家全球供应商）的数据
- 证伪条件：发现多家公司可生产同类HA产品且已获批
- 证伪条件：下游客户（如J&J）启用替代供应商

### customer_dependency: partial

客户依赖度证据充分：J&J MedTech占2025年总收入50%（2024年57%，2023年62%），且有长期独家供应合同（Orthovisc 2003年、Monovisc 2011年签署）。Boehringer Ingelheim签订新10年Hyvisc分销协议。医院和门诊中心通过寄售模式采购Integrity等产品。

- 支持 [ev_57b13d6f145d8852](https://www.sec.gov/Archives/edgar/data/898437/000117184326001275/anik20251231_10k.htm) (primary-document): For the year ended December 31, 2025, J&J MedTech accounted for 50% of revenue, as compared to 57% in prior year
- 支持 [ev_80c91812c2ff4c26](https://www.sec.gov/Archives/edgar/data/898437/000117184326001275/anik20251231_10k.htm) (primary-document): Our collaboration agreement with J&J MedTech includes contracts with Orthovisc and Monovisc products, which were entered into in 2003 and 2011, respectively
- 支持 [ev_e2041ebd65ae8b7d](https://www.sec.gov/Archives/edgar/data/898437/000117184326007211/exh_991.htm) (sec-8k): Anika entered a new 10-year partnership for the distribution of Hyvisc with its existing partner, Boehringer Ingelheim
- 支持 [ev_24a824879d0559b4](https://www.sec.gov/Archives/edgar/data/898437/000117184326007211/exh_991.htm) (primary-document): Integrity contributed $7.5 million in revenue for the trailing 12 months
- 缺口：除J&J和Boehringer外其他主要客户的具体名称和收入占比
- 缺口：通过需要直接相关的原始披露及完整证据
- 证伪条件：J&J MedTech终止或不续签Orthovisc/Monovisc供应协议
- 证伪条件：J&J引入替代HA供应商

### pure_play: fail

Anika是纯透明质酸（HA）骨科/再生医疗公司，与AI医疗主题零相关。全部收入来自OA疼痛管理、再生解决方案和非骨科OEM产品，无任何AI技术、AI诊断或AI药物研发业务。

- 反证 [ev_e2041ebd65ae8b7d](https://www.sec.gov/Archives/edgar/data/898437/000117184326007211/exh_991.htm) (sec-8k): Anika Therapeutics, Inc. (Nasdaq: ANIK), the global leader in the design, development, manufacturing and commercialization of hyaluronic acid (HA) innovations
- 反证 [ev_14aac14fbb99f345](https://www.sec.gov/Archives/edgar/data/898437/000117184326001275/anik20251231_10k.htm) (primary-document): OEM Channel $ 64,406 57 % $ 77,770 65 % $ 84,645 70 % Commercial Channel 48,413 43 % 42,137 35 % 36,147 30 % Total $ 112,819 100 %
- 缺口：任何AI相关业务收入或战略计划
- 缺口：任何AI诊断、AI辅助手术或数字健康产品线
- 证伪条件：公司宣布进入AI医疗领域的战略或收购
- 证伪条件：发现HA产品线中嵌入AI技术组件

### multi_node_control: unknown

Anika控制HA产品的研发和制造（Bedford工厂），并通过Commercial Channel直接销售部分产品，具备一定纵向整合。但无证据表明其控制上游原料节点，且OEM渠道依赖J&J进行下游销售。不满足控制两个相连供应链节点的标准。

- 支持 [ev_1e7a041875ec0f3e](https://www.sec.gov/Archives/edgar/data/898437/000117184326001275/anik20251231_10k.htm) (primary-document): we have developed significant manufacturing expertise in procedures such as homogenized mixing and filling of highly viscous liquids and creation and manipulation of solid HA into scaffolds
- 缺口：上游HA原料自产能力的证据
- 缺口：对下游分销渠道的直接控制力度量化
- 证伪条件：上游原料供应商同时为竞争对手供货
- 证伪条件：J&J获得替代制造商资质

### earnings_validation: partial

财务数据扎实：Q3 2026收入$30.6M同比增10%，毛利率62%（同比提升6pp），调整后EBITDA $5.1M，现金$45M。公司上调2026全年收入指引下限和调整后EBITDA指引。但这些财务表现验证的是HA骨科业务，与AI医疗投资论点无关。Hyalofast PMA被FDA拒绝是重大负面。

- 支持 [ev_e243b465da5f6895](https://data.sec.gov/api/xbrl/companyfacts/CIK0000898437.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 30,594,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_e243b465da5f6895](https://data.sec.gov/api/xbrl/companyfacts/CIK0000898437.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 44,957,000 for as of 2026-09-30
- 支持 [ev_24a824879d0559b4](https://www.sec.gov/Archives/edgar/data/898437/000117184326007211/exh_991.htm) (primary-document): Gross margin: 62%, compared with 56% in the prior-year period
- 支持 [ev_5e5bd33cb54e92d5](https://www.sec.gov/Archives/edgar/data/898437/000117184326007211/exh_991.htm) (primary-document): Adjusted EBITDA margin: 15% to 17%, compared to 13% to 17% previously
- 反证 [ev_d7e840162311704a](https://www.sec.gov/Archives/edgar/data/898437/000117184326007211/exh_991.htm) (primary-document): the Company received formal notification from the FDA that the Hyalofast® pre-market approval (PMA) application is not approvable, primarily based on the clinical data included in the submission
- 缺口：任何与AI医疗相关的收入或投资数据
- 缺口：Hyalofast后续监管路径的具体时间表和成本估算
- 证伪条件：J&J订单量大幅下降导致OEM渠道收入骤降
- 证伪条件：Cingal NDA提交失败或被FDA拒绝
- 证伪条件：毛利率回落至55%以下

### counter_thesis: partial

已识别多个反面论点：(1) J&J高度集中风险（50%收入），(2) Hyalofast PMA被FDA拒绝削弱管线价值，(3) 2027收入指引仅Flat-5%增长，(4) $182M市值反映市场对增长前景有限的定价，(5) 与AI医疗主题完全无关。但缺乏竞品替代分析和估值压力测试。

- 支持 [ev_57b13d6f145d8852](https://www.sec.gov/Archives/edgar/data/898437/000117184326001275/anik20251231_10k.htm) (primary-document): we expect to continue to be dependent on a small number of large customers, especially J&J MedTech, for a sizeable portion of our revenues in the near-term future
- 支持 [ev_d7e840162311704a](https://www.sec.gov/Archives/edgar/data/898437/000117184326007211/exh_991.htm) (primary-document): the Company received formal notification from the FDA that the Hyalofast® pre-market approval (PMA) application is not approvable, primarily based on the clinical data included in the submission
- 支持 [ev_5e5bd33cb54e92d5](https://www.sec.gov/Archives/edgar/data/898437/000117184326007211/exh_991.htm) (primary-document): Total Company revenue growth: Flat to 5%
- 反证 [ev_e2041ebd65ae8b7d](https://www.sec.gov/Archives/edgar/data/898437/000117184326007211/exh_991.htm) (sec-8k): Integrity revenue grew both sequentially and by more than 30% year over year despite more market-wide seasonality than usual in the summer months
- 反证 [ev_24a824879d0559b4](https://www.sec.gov/Archives/edgar/data/898437/000117184326007211/exh_991.htm) (primary-document): The agreement provides higher transfer pricing, a royalty on end-market sales, higher contractual purchases and upfront and milestone payments
- 缺口：HA注射市场竞争格局分析（Ferring、Bioventus等）
- 缺口：DCF或可比公司估值压力测试
- 缺口：地缘政治或供应链中断场景分析
- 证伪条件：J&J终止分销协议或引入替代供应商
- 证伪条件：Cingal NDA提交被FDA拒绝
- 证伪条件：HA注射市场被生物制剂或基因疗法替代
- 证伪条件：Integrity增长停滞、无法达到规模化
- 证伪条件：现金消耗加速导致融资稀释

### management_governance: partial

CEO Steve Griffin在任并在财报电话会议中发言。Deloitte对2025年内控出具无保留意见。无披露的调查或继任问题。但缺乏董事会构成、高管任期、关联交易等详细治理信息。

- 支持 [ev_e2041ebd65ae8b7d](https://www.sec.gov/Archives/edgar/data/898437/000117184326007211/exh_991.htm) (sec-8k): said Steve Griffin, President and Chief Executive Officer
- 支持 [ev_5e96f4f157851d1d](https://www.sec.gov/Archives/edgar/data/898437/000117184326001275/anik20251231_10k.htm) (primary-document): In our opinion, the Company maintained, in all material respects, effective internal control over financial reporting as of December 31, 2025
- 支持 [ev_9f3d2028fe76b3f7](https://www.sec.gov/Archives/edgar/data/898437/000117184326001275/anik20251231_10k.htm) (primary-document): our management believes that our company maintained effective internal control over financial reporting as of December 31, 2025
- 缺口：董事会独立性和构成详情
- 缺口：高管薪酬与业绩挂钩的具体条款
- 缺口：CEO任期和管理团队稳定性历史
- 证伪条件：高管突然离职或继任危机
- 证伪条件：内控重大缺陷披露
- 证伪条件：股东诉讼或SEC调查

## ANTX · complete

审查记录：`state/serenity-reviews/ANTX-claudecli-49c38101300d68746557.json`

### supply_chain_map: partial

上游：第三方CMO负责生产（未披露具体名称），Anacor/GSK授权知识产权。产品：epetraborole及硼化学平台衍生小分子药物。下游：PV、M. abscessus、Chagas、HPP等适应症患者群体。供应链关系有框架但缺乏具体供应商名称和物料来源。

- 支持 [ev_44184c4377f953f7](https://www.sec.gov/Archives/edgar/data/1880438/000119312526110693/antx-20251231.htm) (primary-document): We do not currently have any agreements with third-party manufacturers for the long-term commercial supply of any of our product candidates
- 支持 [ev_6959aefdf527d5f6](https://www.sec.gov/Archives/edgar/data/1880438/000119312526110693/antx-20251231.htm) (primary-document): We do not control the manufacturing process of, and are completely dependent on, third-party manufacturers for compliance with cGMP requirements
- 支持 [ev_5e5893bf5451099a](https://www.sec.gov/Archives/edgar/data/1880438/000119312526452660/antx-ex99_1.htm) (sec-8k): a clinical stage biopharmaceutical company focused on the discovery and development of novel small molecule therapeutics derived from its boron chemistry platform
- 支持 [ev_5d49383a53d6fc1e](https://www.sec.gov/Archives/edgar/data/1880438/000119312526110693/antx-20251231.htm) (primary-document): We have sublicensed certain patents from Anacor that are owned, maintained and prosecuted by GlaxoSmithKline plc
- 缺口：具体CMO供应商名称及合同条款
- 缺口：硼化合物原材料来源和供应集中度
- 缺口：制造产能与备选供应商信息
- 证伪条件：发现公司已签署长期商业供应协议且有多元化CMO
- 证伪条件：发现硼化学原料高度集中于单一供应商构成瓶颈

### chokepoint_evidence: unknown

AN2是临床阶段药企，依赖第三方CMO生产，自身不控制任何供应链瓶颈节点。硼化学平台是专有技术但无证据表明其在供应链中构成不可替代的卡位。无供应集中度或替代壁垒的具体数据。

- 缺口：硼化学平台在全球药物供应链中的不可替代性证据
- 缺口：epetraborole作为唯一在研疗法的竞品分析
- 缺口：供应集中度或替代周期的具体数据
- 证伪条件：发现多家公司拥有类似硼化学平台且进入相同适应症
- 证伪条件：发现epetraborole在PV或M. abscessus适应症中存在多个竞争管线

### customer_dependency: unknown

临床阶段公司，无已获批产品，无营收，无客户。尚未进入商业化阶段，无法评估客户依赖性。

- 缺口：商业化后的潜在付费方（保险公司、医院等）信息
- 缺口：PV及M. abscessus市场中的处方医生/KOL采纳意向
- 缺口：任何预购或承购协议
- 证伪条件：发现大型药企已签署epetraborole商业化分销协议
- 证伪条件：发现KOL公开表态不会采用epetraborole

### pure_play: partial

AN2是纯粹的硼化学平台药企，所有管线均来源于同一平台。但该公司与AI医疗主题无明确关联，未披露任何AI相关业务或技术。作为纯药企，主题敞口清晰但不在AI医疗赛道。

- 支持 [ev_5e5893bf5451099a](https://www.sec.gov/Archives/edgar/data/1880438/000119312526452660/antx-ex99_1.htm) (sec-8k): focused on the discovery and development of novel small molecule therapeutics derived from its boron chemistry platform
- 支持 [ev_403e96ec1c588461](https://www.sec.gov/Archives/edgar/data/1880438/000119312526452660/antx-ex99_1.htm) (primary-document): AN2-504661 selected as an oral development candidate for hypophosphatasia (HPP)
- 缺口：任何AI技术在药物发现或开发中应用的披露
- 缺口：AI医疗主题的营收或业务敞口数据
- 证伪条件：发现公司使用AI平台进行药物发现并有明确披露
- 证伪条件：发现公司与AI医疗公司有合作关系

### multi_node_control: unknown

公司不控制制造（依赖第三方CMO），不控制上游IP（从Anacor/GSK授权），仅拥有硼化学平台的研发能力。无证据表明公司控制供应链中两个或以上相连节点。

- 反证 [ev_6959aefdf527d5f6](https://www.sec.gov/Archives/edgar/data/1880438/000119312526110693/antx-20251231.htm) (primary-document): We do not control the manufacturing process of, and are completely dependent on, third-party manufacturers
- 缺口：自有制造能力或垂直整合计划
- 缺口：上游原材料控制权或独家供应协议
- 证伪条件：发现公司建立自有GMP生产设施
- 证伪条件：发现公司收购上游原料供应商

### earnings_validation: partial

准备阶段公司，无营收符合预期。截至2026年9月30日现金及投资为8020万美元，公司预计可支撑运营至2029年。Q3 2026净亏损800万美元，季度烧钱可控。财务数据显示公司能够资助下一个里程碑（PV Phase 2入组、M. abscessus数据读出），但无营收验证任何投资论点。

- 支持 [ev_c2ca391b73a10209](https://www.sec.gov/Archives/edgar/data/1880438/000119312526452660/antx-ex99_1.htm) (primary-document): The Company projects that existing cash, cash equivalents, and investments will sustain operations into 2029 under the current operating plan
- 支持 [ev_c2ca391b73a10209](https://www.sec.gov/Archives/edgar/data/1880438/000119312526452660/antx-ex99_1.htm) (primary-document): Net loss for the third quarter of 2026 was $8.0 million, compared to $9.4 million for the same period during 2025
- 支持 [ev_7d75149d25994f71](https://www.sec.gov/Archives/edgar/data/1880438/000119312526452660/antx-ex99_1.htm) (primary-document): Cash and cash equivalents $ 20,207 $ 19,941 Short-term investments 44,193 38,060
- 缺口：具体里程碑达成时间与对应资金需求的匹配分析
- 缺口：未来融资计划或稀释风险的管理层说明
- 证伪条件：发现烧钱速度大幅加速导致runway低于12个月
- 证伪条件：发现公司宣布需要紧急融资

### counter_thesis: unknown

主要风险已部分识别：1）Phase 3 MAC试验已终止（NCT05327803），表明关键管线存在失败先例；2）核心IP来自Anacor/GSK授权，存在许可终止风险；3）内部控制存在重大缺陷；4）完全依赖第三方CMO。但缺乏竞品管线的具体对比分析和估值压力测试。

- 支持 [ev_55592ce6debde0e7](https://clinicaltrials.gov/study/NCT05327803) (clinicaltrials-gov): Study of Epetraborole in Patients With Treatment-refractory MAC Lung Disease. Highest listed phase: Phase 3. Overall status: TERMINATED
- 支持 [ev_e085c75baeae1724](https://www.sec.gov/Archives/edgar/data/1880438/000119312526110693/antx-20251231.htm) (primary-document): we lacked a sufficient complement of resources with (i) an appropriate level of accounting knowledge, experience and training
- 支持 [ev_6959aefdf527d5f6](https://www.sec.gov/Archives/edgar/data/1880438/000119312526110693/antx-20251231.htm) (primary-document): There are a limited number of manufacturers that operate under cGMP regulations and that might be capable of manufacturing for us
- 缺口：PV适应症中现有疗法和竞争管线的详细对比
- 缺口：M. abscessus领域其他在研药物的分析
- 缺口：估值合理性的量化压力测试
- 缺口：硼化学平台与其他化学平台的替代性分析
- 缺口：引用不存在或原文无法匹配
- 证伪条件：PV Phase 2试验因安全性问题终止
- 证伪条件：Anacor/GSK许可协议被终止
- 证伪条件：竞品在相同适应症中获得突破性疗法认定或获批
- 证伪条件：现金烧钱加速导致被迫在不利条件下融资

### management_governance: partial

CEO Eric Easom为联合创始人，领导连续性有保障。2026年8月任命Cameron Trenor博士为CMO，CFO Lucy Day在任。但自2022年IPO以来内部控制存在重大缺陷至今未修复（截至2025年12月31日仍存在），包括人员不足和IT缺陷，治理存在明确短板。

- 支持 [ev_403e96ec1c588461](https://www.sec.gov/Archives/edgar/data/1880438/000119312526452660/antx-ex99_1.htm) (primary-document): In August, the Company appointed Cameron Trenor, M.D., as Chief Medical Officer
- 支持 [ev_5e5893bf5451099a](https://www.sec.gov/Archives/edgar/data/1880438/000119312526452660/antx-ex99_1.htm) (sec-8k): said Eric Easom, Co-Founder, Chairman, President and CEO of AN2 Therapeutics
- 反证 [ev_e085c75baeae1724](https://www.sec.gov/Archives/edgar/data/1880438/000119312526110693/antx-20251231.htm) (primary-document): The material weaknesses identified were as follows, and continue to exist as of December 31, 2025
- 反证 [ev_a71325a88d59f9ed](https://www.sec.gov/Archives/edgar/data/1880438/000119312526110693/antx-20251231.htm) (primary-document): the IT deficiencies, when aggregated, could impact maintaining effective segregation of duties
- 缺口：董事会独立性和构成详情
- 缺口：重大缺陷修复的具体时间表和进展
- 缺口：高管薪酬和激励结构
- 证伪条件：内部控制重大缺陷导致财务重述
- 证伪条件：关键高管（CEO/CFO）突然离职
- 证伪条件：SEC对内部控制缺陷发起调查

## ATRC · complete

审查记录：`state/serenity-reviews/ATRC-claudecli-3ff486379e02b2ad4238.json`

### supply_chain_map: partial

证据中可识别公司产品（房颤手术器械：夹钳、消融设备、冷冻探头等），但缺乏上游原材料供应商和下游具体客户/医院系统的详细信息。XBRL标签显示存在客户集中度披露，但实际内容未包含在证据包中。

- 支持 [ev_5e92a8e652da94e5](https://www.sec.gov/Archives/edgar/data/1323885/000132388526000007/atrc-20251231.htm) (primary-document): Isolator ® Synergy ™ clamp, EPi-Sense ® coagulation device, EnCompass ® clamp, AtriClip ® Flex·V ® device, and cryoSPHERE ® probes
- 支持 [ev_cdc10ce303f0023b](https://www.sec.gov/Archives/edgar/data/1323885/000132388526000007/atrc-20251231.htm) (primary-document): atrc:MedicalDevicesMember us-gaap:CustomerConcentrationRiskMember us-gaap:SalesRevenueNetMember
- 缺口：上游关键材料和组件供应商名称及集中度
- 缺口：下游客户（医院系统、经销商）的具体名称和依赖关系
- 缺口：地理收入分布的详细数据
- 证伪条件：发现公司产品可被廉价替代品轻松替换
- 证伪条件：上游供应完全大宗商品化，无任何供应链优势

### chokepoint_evidence: unknown

证据包中没有任何信息表明AtriCure在供应链中占据瓶颈位置。公司是一家房颤手术器械制造商，未见供应集中度、替代壁垒或AI相关瓶颈的证据。仅与AI医疗主题相关不构成瓶颈证据。

- 缺口：公司产品在特定治疗领域的市场份额数据
- 缺口：竞争对手数量和替代产品的可用性分析
- 缺口：专利或技术壁垒的具体描述
- 证伪条件：发现多家竞争对手提供相同功能的手术器械
- 证伪条件：该领域不存在实质性供应集中

### customer_dependency: unknown

XBRL标签显示公司在10-K中披露了客户集中度风险（SalesRevenueNetMember和AccountsReceivableMember），但证据包中未包含实际的客户名称、采用数据或合作关系详情。无法确认具体客户依赖情况。

- 支持 [ev_cdc10ce303f0023b](https://www.sec.gov/Archives/edgar/data/1323885/000132388526000007/atrc-20251231.htm) (primary-document): atrc:MedicalDevicesMember us-gaap:CustomerConcentrationRiskMember us-gaap:AccountsReceivableMember
- 缺口：主要客户名称及各自收入占比
- 缺口：临床采用数据或医院使用量
- 缺口：长期合同或采购协议详情
- 证伪条件：发现客户群高度分散，无单一客户超过10%收入
- 证伪条件：主要客户正在转向竞争产品

### pure_play: partial

商标列表显示公司所有产品均为房颤/心脏手术相关器械，暗示业务聚焦度较高。但证据包中缺少分部收入数据，无法量化AI医疗相关收入敞口。筛选标记为'Clinical data & software'，但实际证据显示公司是医疗器械公司。

- 支持 [ev_5e92a8e652da94e5](https://www.sec.gov/Archives/edgar/data/1323885/000132388526000007/atrc-20251231.htm) (primary-document): Isolator ® Synergy ™ clamp, EPi-Sense ® coagulation device, EnCompass ® clamp, AtriClip ® Flex·V ® device, and cryoSPHERE ® probes
- 缺口：按产品线或治疗领域的分部收入明细
- 缺口：AI或数字健康相关收入的具体占比
- 缺口：公司战略中AI/软件组件的角色说明
- 证伪条件：公司实际上大部分收入来自与AI医疗无关的传统手术器械
- 证伪条件：AI/软件仅为边缘业务，不构成纯正敞口

### multi_node_control: unknown

证据包中没有显示AtriCure控制供应链中两个或以上相连节点的信息。公司拥有多种产品，但这些均为终端手术器械，未见纵向整合（如同时控制关键组件制造和终端设备）的证据。

- 缺口：公司是否自主生产关键组件的信息
- 缺口：纵向整合或供应链控制的证据
- 缺口：内部制造vs外包的比例数据
- 证伪条件：公司所有关键组件均外采，不存在多节点控制

### earnings_validation: pass

XBRL数据提供了2026年Q3实际财务结果：收入1.545亿美元（同比+15%），净利润406.4万美元（已盈利），经营现金流YTD 4851.8万美元，现金1.87亿美元。公司已实现盈利并保持双位数增长，财务状况健康。研发投入3211.6万美元显示持续创新投资。

- 支持 [ev_5a7d1c01c88553f3](https://data.sec.gov/api/xbrl/companyfacts/CIK0001323885.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 154,450,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_5a7d1c01c88553f3](https://data.sec.gov/api/xbrl/companyfacts/CIK0001323885.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 134,269,000, a change of +15.0%
- 支持 [ev_5a7d1c01c88553f3](https://data.sec.gov/api/xbrl/companyfacts/CIK0001323885.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 4,064,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_5a7d1c01c88553f3](https://data.sec.gov/api/xbrl/companyfacts/CIK0001323885.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 187,031,000 for as of 2026-09-30
- 支持 [ev_5a7d1c01c88553f3](https://data.sec.gov/api/xbrl/companyfacts/CIK0001323885.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): 48,518,000 for 2026-01-01 to 2026-09-30
- 证伪条件：后续季度收入增长大幅放缓或转为负增长
- 证伪条件：净利润重新转为亏损，表明盈利不可持续

### counter_thesis: partial

可从10-K结构中推断公司披露了风险因素，但证据包仅包含目录和前瞻性声明的免责条款，未包含实际风险内容。无法对供应、需求、替代、地缘政治和估值进行充分压力测试。已知公司市值约29亿美元、Q3收入1.545亿（年化约6亿），估值不低。

- 支持 [ev_a40cf370f1eced6d](https://www.sec.gov/Archives/edgar/data/1323885/000132388526000007/atrc-20251231.htm) (primary-document): ITEM 1A . RISK FACTORS 17 ITEM 1B. UNRESOLVED STAFF COMMENTS 33
- 反证 [ev_229910fe2233b919](https://www.sec.gov/Archives/edgar/data/1323885/000132388526000007/atrc-20251231.htm) (primary-document): actual results may differ materially from assumptions, estimates or expectations reflected or contained in the forward-looking statements
- 缺口：竞争对手产品和市场份额变化的具体分析
- 缺口：监管风险（FDA审批、报销政策变化）的详细评估
- 缺口：AI医疗主题与公司实际业务关联性的深入论证
- 缺口：估值合理性分析（P/S约5x基于年化收入）
- 证伪条件：竞争对手推出更优手术方案导致市场份额流失
- 证伪条件：FDA监管变化限制公司核心产品使用
- 证伪条件：医保报销政策收紧压缩终端需求
- 证伪条件：公司与AI医疗主题关联性实际极弱，估值溢价不可持续
- 证伪条件：大型医疗器械公司进入该细分市场

### management_governance: unknown

证据包中仅包含10-K封面信息（2026年2月12日流通股49,809,901股）和文件结构。治理详情引用了尚未包含在证据中的代理声明。未发现调查或继任问题，但也无正面治理证据。

- 缺口：CEO和高管团队的任期及背景信息
- 缺口：董事会独立性和构成
- 缺口：高管薪酬结构与业绩挂钩情况
- 缺口：近期高管变动或继任计划
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现正在进行的SEC调查或诉讼
- 证伪条件：关键高管近期离职且无明确继任者

## AVXL · complete

审查记录：`state/serenity-reviews/AVXL-claudecli-bd7720ad9d43867656f9.json`

### supply_chain_map: unknown

可以识别公司产品（blarcamesine用于CNS疾病：阿尔茨海默病、Rett综合征、脆性X综合征）以及上游许可方（Life Science Research Israel Ltd.），但缺乏具体的原料药供应商、CMO制造关系和下游支付方/分销渠道的披露。

- 支持 [ev_9515ba1a712386f4](https://www.sec.gov/Archives/edgar/data/1314052/000173112226001351/e8011_ex99-1.htm) (sec-8k): a clinical-stage biopharmaceutical company developing innovative treatments for central nervous system diseases with significant unmet medical needs
- 支持 [ev_e95d07b5b76891a8](https://www.sec.gov/Archives/edgar/data/1314052/000173112225001596/e7052_10-k.htm) (primary-document): We are party to an exclusive license agreement with Life Science Research Israel Ltd., with respect to certain in-licensed intellectual property related to our ANAVEX ® 3-71 product candidate
- 缺口：原料药（API）供应商身份
- 缺口：合同生产组织（CMO）关系
- 缺口：下游分销或支付方渠道细节
- 缺口：引用不存在或原文无法匹配
- 证伪条件：披露CMO或API供应商丢失或更换
- 证伪条件：监管机构因制造问题发出警告信

### chokepoint_evidence: unknown

AVXL是临床阶段药物开发公司，不存在供应链瓶颈或替代壁垒的证据。公司持有30项美国专利和Orphan Drug Designation，但这些是知识产权保护，不构成物理供应集中度意义上的chokepoint。

- 支持 [ev_088f14f1b2656245](https://www.sec.gov/Archives/edgar/data/1314052/000173112225001596/e7052_10-k.htm) (primary-document): We hold ownership or exclusive rights to thirty (30) U.S. patents, seventeen (17) pending U.S. patent applications
- 支持 [ev_9515ba1a712386f4](https://www.sec.gov/Archives/edgar/data/1314052/000173112226001351/e8011_ex99-1.htm) (sec-8k): Blarcamesine for the treatment of Fragile X syndrome has been granted Orphan Drug Designation by the FDA
- 缺口：供应集中度数据
- 缺口：替代药物的转换成本或壁垒证据
- 缺口：市场份额数据
- 证伪条件：竞争对手获得相同适应症的Orphan Drug Designation
- 证伪条件：blarcamesine专利被成功挑战

### customer_dependency: unknown

公司尚无商业化产品，无客户收入或采用证据。所有项目处于临床阶段，无法验证下游客户依赖关系。

- 缺口：商业化产品的客户或支付方
- 缺口：任何收入或采购协议
- 缺口：医疗机构或保险公司的采用意向
- 证伪条件：临床试验失败导致无法获得任何客户
- 证伪条件：FDA拒绝批准申请

### pure_play: partial

10-K披露公司为单一可报告分部，专注于CNS疾病药物开发，符合纯粹主题暴露。但由于无收入，无法用收入占比量化主题暴露度。

- 支持 [ev_debe6e5047301fb8](https://www.sec.gov/Archives/edgar/data/1314052/000173112225001596/e7052_10-k.htm) (primary-document): a public entity that has a single reportable segment to provide all the disclosures required by the amendments in ASU No. 2023-07
- 支持 [ev_9515ba1a712386f4](https://www.sec.gov/Archives/edgar/data/1314052/000173112226001351/e8011_ex99-1.htm) (sec-8k): a publicly traded clinical stage biopharmaceutical company engaged in the development of novel therapeutics for the treatment of central nervous system diseases
- 缺口：收入分部数据（尚无收入）
- 缺口：AI医疗相关性的具体证据
- 证伪条件：公司进入与CNS无关的多元化业务领域

### multi_node_control: unknown

无证据表明公司控制供应链中两个以上相连节点。公司拥有IP许可和临床开发能力，但缺乏制造、分销等节点控制的证据。

- 缺口：纵向整合证据（如自有生产设施）
- 缺口：多个供应链节点的控制证据
- 证伪条件：CMO或关键供应商拒绝续约导致公司失去开发能力

### earnings_validation: unknown

准备阶段公司，亏损属预期。10-K报告FY2025净亏损4,638万美元。smallCapContext显示现金1.183亿美元、月消耗230万美元、跑道51.5个月，远超12个月，可支撑下一个里程碑。但现金数据来自上下文而非可引用段落，仅有亏损数字可从证据中引用。

- 支持 [ev_48261ccfd90a4bb1](https://www.sec.gov/Archives/edgar/data/1314052/000173112225001596/e7052_10-k.htm) (primary-document): United States $ ( 44,500 ) $ ( 39,195 ) $ ( 41,198 )
- 缺口：可引用的现金余额和烧钱率段落
- 缺口：未来12个月资本需求的具体披露
- 缺口：引用不存在或原文无法匹配
- 证伪条件：现金低于12个月烧钱率且无融资计划
- 证伪条件：审计师对持续经营的疑虑

### counter_thesis: unknown

可识别多项风险：(1)临床试验失败风险——三个核心适应症均未有已公布的关键结果；(2)对单一化合物blarcamesine的高度依赖；(3)IP许可依赖Life Science Research Israel Ltd.可能终止；(4)Interim CEO表明领导层过渡未完成。但缺乏具体竞争对手夺取份额或试验失败的引用事实，无法完全通过。

- 支持 [ev_e95d07b5b76891a8](https://www.sec.gov/Archives/edgar/data/1314052/000173112225001596/e7052_10-k.htm) (primary-document): our licensors might conclude that we have materially breached our obligations under such license agreements and might therefore terminate the license agreements
- 支持 [ev_9515ba1a712386f4](https://www.sec.gov/Archives/edgar/data/1314052/000173112226001351/e8011_ex99-1.htm) (sec-8k): Terrie Kellmeyer, Ph.D., Interim Chief Executive Officer
- 支持 [ev_088f14f1b2656245](https://www.sec.gov/Archives/edgar/data/1314052/000173112225001596/e7052_10-k.htm) (primary-document): Competitors may claim that we are not entitled to an issued patent for a variety of legal reasons
- 缺口：具体竞争对手在相同适应症的进展
- 缺口：blarcamesine临床试验结果数据
- 缺口：估值分析（市值67M vs 现金118M的折价原因）
- 缺口：引用不存在或原文无法匹配
- 证伪条件：Phase 3 Rett综合征或Alzheimer试验未达主要终点
- 证伪条件：FDA拒绝NDA/BLA申请
- 证伪条件：IP许可被终止
- 证伪条件：现金不足以完成关键试验

### management_governance: partial

内部控制有效，董事会有独立主席（Dr. Jiong Ma），审计委员会等治理结构齐全。但CEO为Interim（Terrie Kellmeyer），表明领导层继任尚未解决，这是一个治理待决事项，不能给予pass。

- 支持 [ev_cca2cdfe6a2e29fe](https://www.sec.gov/Archives/edgar/data/1314052/000173112225001596/e7052_10-k.htm) (primary-document): In our opinion, the Company maintained, in all material respects, effective internal control over financial reporting as of September 30, 2025
- 支持 [ev_7e1f58de669a7891](https://www.sec.gov/Archives/edgar/data/1314052/000173112225001596/e7052_10-k.htm) (primary-document): Our Board of Directors has appointed an independent Board Chair, Dr. Jiong Ma
- 支持 [ev_7e1f58de669a7891](https://www.sec.gov/Archives/edgar/data/1314052/000173112225001596/e7052_10-k.htm) (primary-document): The Company believes separation of the positions of Board Chair and Chief Executive Officer reinforces the independence of our Board
- 反证 [ev_9515ba1a712386f4](https://www.sec.gov/Archives/edgar/data/1314052/000173112226001351/e8011_ex99-1.htm) (sec-8k): said Terrie Kellmeyer, Ph.D., Interim Chief Executive Officer
- 缺口：正式CEO搜寻进展或时间表
- 缺口：前任CEO离职原因
- 证伪条件：Interim CEO长期未转正且无搜寻计划
- 证伪条件：审计师发现重大内控缺陷
- 证伪条件：董事会成员大规模辞职

## BDSX · complete

审查记录：`state/serenity-reviews/BDSX-claudecli-9f9011168a19512d0cfa.json`

### supply_chain_map: partial

上游：披露了关键单一来源供应商（Bio-Rad供应GeneStrat试剂、Freenome供应Nodify CDT试剂），以及位于美国、欧洲和中国的单一来源组件供应商。公司产品：诊断测试（VeriStrat、Nodify XL2、Nodify CDT）及MALDI-ToF/DeepMALDI AI平台。下游：Medicare为主要付款方（浓度风险披露），AVEO Oncology和Daiichi Sankyo为合作伙伴。但缺乏完整的物理流程图和终端用户具体分布。

- 支持 [ev_ce512952cc9bebb8](https://www.sec.gov/Archives/edgar/data/1439725/000119312526076547/bdsx-20251231.htm) (primary-document): We rely on third-party suppliers to provide certain components of our diagnostic tests, including a select few (located in the United States, Europe and China), as critical single source providers of components.
- 支持 [ev_ce512952cc9bebb8](https://www.sec.gov/Archives/edgar/data/1439725/000119312526076547/bdsx-20251231.htm) (primary-document): Bio-Rad, as described below, is the sole source supplier for our GeneStrat test. Freenome is also the sole source supplier for our Nodify CDT tests but there are known secondary suppliers for these materials.
- 支持 [ev_3a9f6df623ca2199](https://www.sec.gov/Archives/edgar/data/1439725/000119312526076547/bdsx-20251231.htm) (primary-document): we entered into a Co-Development and Collaboration Agreement with AVEO Oncology (formerly known as AVEO Pharmaceuticals, Inc.)
- 缺口：终端客户（医院、肿瘤科）的具体名称和地理分布
- 缺口：各诊断测试的检测量或市场份额数据
- 缺口：除Medicare外的付款方和渠道结构
- 证伪条件：发现Biodesix诊断测试已被主要医疗系统或付款方停止使用
- 证伪条件：Bio-Rad或Freenome终止供应且无替代来源

### chokepoint_evidence: unknown

Biodesix拥有60项美国专利和84项外国专利，涵盖MALDI-ToF和AI分类器技术，但这只是知识产权保护，不构成供应链瓶颈。诊断测试市场存在多家竞争者（液体活检、NGS等），没有证据表明Biodesix控制着不可替代的供应节点。AI平台的存在本身不足以满足瓶颈门槛。

- 支持 [ev_42a2d5d418365cc5](https://www.sec.gov/Archives/edgar/data/1439725/000119312526076547/bdsx-20251231.htm) (primary-document): our patent portfolio includes 60 issued United States patents, 84 issued foreign patents, and 18 pending applications
- 缺口：Biodesix在肺癌诊断领域的市场份额数据
- 缺口：替代诊断方法（NGS、液体活检）的转换成本或时间
- 缺口：MALDI-ToF平台是否具有不可替代性的证据
- 证伪条件：发现多家公司提供功能等价的MALDI-ToF肺癌诊断测试
- 证伪条件：主要医疗指南推荐替代诊断方法取代Biodesix测试

### customer_dependency: unknown

Medicare被披露为收入和应收账款的集中客户（XBRL标签中出现浓度风险披露），AVEO Oncology有合作协议，Daiichi Sankyo出现在XBRL中暗示合作关系。但缺乏具体的测试量、收入占比或医院采用率数据。

- 支持 [ev_a0e620b57b37d610](https://data.sec.gov/api/xbrl/companyfacts/CIK0001439725.json) (sec-companyfacts): Revenue (Revenues): 24,041,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05
- 缺口：Medicare收入占总收入的具体百分比
- 缺口：使用Nodify或VeriStrat测试的医院/肿瘤中心数量
- 缺口：制药合作伙伴的开发服务收入明细
- 缺口：引用不存在或原文无法匹配
- 证伪条件：Medicare降低或取消Biodesix测试的报销覆盖
- 证伪条件：主要合作伙伴终止协议

### pure_play: partial

从供应链和产品描述来看，Biodesix专注于肺癌及相关领域的诊断测试（VeriStrat、Nodify系列）和AI平台（DeepMALDI），以及为第三方合作伙伴开发测试。但证据包中缺乏收入分部披露，无法量化各业务线的收入占比。

- 支持 [ev_42a2d5d418365cc5](https://www.sec.gov/Archives/edgar/data/1439725/000119312526076547/bdsx-20251231.htm) (primary-document): tection relating to our core classifier development program, our AI platform and our approaches to using MALDI-ToF technology (DeepMALDI® techniques)
- 支持 [ev_ce512952cc9bebb8](https://www.sec.gov/Archives/edgar/data/1439725/000119312526076547/bdsx-20251231.htm) (primary-document): We need to maintain and continuously improve the performance and reliability of our diagnostic tests to achieve our profitability objectives.
- 缺口：诊断测试收入与开发服务收入的分部数据
- 缺口：AI/机器学习相关收入的具体占比
- 缺口：业务线收入分解（Nodify vs VeriStrat vs 合作开发）
- 证伪条件：发现大部分收入来自与AI诊断无关的业务
- 证伪条件：公司转向与核心诊断业务无关的多元化方向

### multi_node_control: unknown

Biodesix开发了AI分类器平台和诊断测试产品，但没有证据表明其控制了供应链中两个以上的连接节点。公司依赖第三方单一来源供应商（Bio-Rad、Freenome），自身不控制上游试剂生产。多个产品不等于多节点控制。

- 缺口：Biodesix是否自主生产任何关键试剂或仪器
- 缺口：AI平台与测试产品之间的垂直整合程度
- 缺口：是否控制样本采集到结果报告的完整流程
- 证伪条件：发现Biodesix仅为测试服务提供商，所有关键组件均外采

### earnings_validation: partial

XBRL数据显示Q3 2026收入2404万美元（同比+10.4%），年化收入约9600万美元。净亏损803万美元，现金2841万美元，月度消耗约210万美元，跑道约13.5个月。公司有收入但仍未盈利，增长放缓至10%。现金跑道勉强超过12个月，存在一定融资风险但尚不构成失败。

- 支持 [ev_a0e620b57b37d610](https://data.sec.gov/api/xbrl/companyfacts/CIK0001439725.json) (sec-companyfacts): Revenue (Revenues): 24,041,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05, accession 0001193125-26-449763. Same quarter a year earlier (2025-07-01 to 2025-09-30): 21,768,000, a change of +10.4%.
- 支持 [ev_a0e620b57b37d610](https://data.sec.gov/api/xbrl/companyfacts/CIK0001439725.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -8,032,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05.
- 支持 [ev_a0e620b57b37d610](https://data.sec.gov/api/xbrl/companyfacts/CIK0001439725.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 28,409,000 for as of 2026-09-30; form 10-Q filed 2026-11-05.
- 缺口：毛利率和运营杠杆趋势
- 缺口：盈亏平衡时间表或管理层指引
- 缺口：ATM融资工具的实际使用情况和剩余额度
- 证伪条件：收入增速进一步下滑至个位数或负增长
- 证伪条件：现金跑道降至12个月以下且无融资安排
- 证伪条件：Medicare报销费率下调导致收入大幅下降

### counter_thesis: unknown

已识别的反面论点：(1)关键专利即将到期（Nodify CDT 2027年、VeriStrat 2026-2032年），竞争者可进入；(2)单一来源供应商风险（Bio-Rad、Freenome）；(3)收入增速放缓至10%，仍未盈利；(4)现金仅2841万美元，跑道约13.5个月，存在ATM股权融资稀释风险。但缺乏来自竞争对手的具体市场份额抢夺证据或替代技术取代的具体案例。

- 支持 [ev_42a2d5d418365cc5](https://www.sec.gov/Archives/edgar/data/1439725/000119312526076547/bdsx-20251231.htm) (primary-document): The patents relating to the VeriStrat test are scheduled to expire between 2026 and 2032 and are actively under review for additional protection.
- 支持 [ev_ce512952cc9bebb8](https://www.sec.gov/Archives/edgar/data/1439725/000119312526076547/bdsx-20251231.htm) (primary-document): Bio-Rad, as described below, is the sole source supplier for our GeneStrat test. Freenome is also the sole source supplier for our Nodify CDT tests
- 支持 [ev_a0e620b57b37d610](https://data.sec.gov/api/xbrl/companyfacts/CIK0001439725.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -18,933,000 for 2026-01-01 to 2026-09-30 (year-to-date total as reported)
- 缺口：具体竞争对手（如Guardant Health、Foundation Medicine）的市场份额趋势
- 缺口：NGS液体活检技术替代MALDI-ToF的速度和可能性
- 缺口：估值分析（P/S倍数与同行对比）
- 缺口：引用不存在或原文无法匹配
- 证伪条件：Nodify CDT专利2027年到期后竞争者推出等效测试
- 证伪条件：Medicare大幅削减分子诊断报销费率
- 证伪条件：现金耗尽前无法实现盈亏平衡或获得融资
- 证伪条件：主要供应商（Bio-Rad）终止供应协议

### management_governance: unknown

CEO和CFO评估认为截至2025年12月31日内部控制有效（基于COSO 2013框架），披露控制和程序在合理保证水平上有效。但该年报不包含独立审计师的内部控制鉴证报告，且缺乏管理层连续性、董事会组成和高管变动的信息。

- 支持 [ev_3125376df9d9dd5b](https://www.sec.gov/Archives/edgar/data/1439725/000119312526076547/bdsx-20251231.htm) (primary-document): Based on our assessment, our Chief Executive Officer and Chief Financial Officer concluded that, as of December 31, 2025, the Company's internal control over financial reporting was effective based on the criteria set forth by COSO.
- 支持 [ev_3125376df9d9dd5b](https://www.sec.gov/Archives/edgar/data/1439725/000119312526076547/bdsx-20251231.htm) (primary-document): our Chief Executive Officer and Chief Financial Officer have concluded that, as of such date, our disclosure controls and procedures were effective at the reasonable assurance level.
- 缺口：CEO/CFO的任期和背景信息
- 缺口：董事会组成和独立董事比例
- 缺口：高管近期变动情况
- 缺口：独立审计师对内部控制的鉴证意见
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现重大内部控制缺陷或财务重述
- 证伪条件：关键高管突然离职
- 证伪条件：SEC调查或审计师出具保留意见

## CAI · complete

审查记录：`state/serenity-reviews/CAI-claude-d0fdacdba550527e6a84.json`

### supply_chain_map: pass

测序仪与试剂依赖少数或单一供应商；收款依赖保险付款方。

- 支持 [ev_ce7f74d58cd888ec](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): We rely on a limited number of third-party suppliers or, in many cases, sole suppliers, for some of our next-generation sequencers, lab materials, reagents, and supplies
- 支持 [ev_eb0f977292f1da17](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000069/cai-20260930.htm) (primary-document): Collection of consideration the Company expects to receive typically occurs within 90 to 120 days of billing.

### chokepoint_evidence: partial

超过 100 万例测序数据与 FDA 伴随诊断批准构成壁垒；但精准肿瘤行业竞争激烈。

- 支持 [ev_90bfb101ae56380f](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): As of December 31, 2025, we have performed sequencing on over 1,000,000 cases.
- 支持 [ev_b77ed4426b98bf65](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): MI Cancer Seek has obtained FDA approval for use as a companion diagnostic device
- 反证 [ev_99eb15cf6c686904](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): The precision oncology industry is intensely competitive.

### customer_dependency: pass

按 Serenity 规则：一手文件披露了客户采用或使用。通道中存在实质性采用证据：公司已确认来自协作安排的收入（2025年$11.4M、2024年$16.2M），并向医院、机构及生物制药客户提供分子分析服务并收取费用；但未披露具体案例量或客户数量。同时存在显著的客户集中风险，前三大商业付款方合计占收入约70%，且生物制药协议可随时终止。

- 支持 [ev_6b5902a128d379dd](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): For the years ended December 31, 2025, 2024, and 2023, the Company recognized collaboration revenue of $ 11.4 million, $ 16.2 million, and $ 5.8 million, respectively, which is included in revenue from pharma research and development services on the consolidated statements of operations
- 支持 [ev_9ca1cb80960da805](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000069/cai-20260930.htm) (primary-document): For the three months ended September 30, 2026 and 2025 , the Company recognized collaboration revenue of $ 1.5 million and $ — million , respectively, and $ 4.1 million and $ 6.9 million for the nin
- 支持 [ev_be8f3217456713c0](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): The Company derives revenue from two distinct channels: • Molecular profiling services involving the provision of precision oncology solutions utilizing MI Profile and Caris Assure. • Pharma research and development services involving delivery of laboratory, strategic data, and research services to biopharmaceutical customers.
- 支持 [ev_6bddc139894087e7](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000069/cai-20260930.htm) (primary-document): The Company derives revenue from two distinct channels: • Molecular profiling services involving the provision of precision oncology solutions utilizing MI Profile, Caris Assure, Caris Detect, Caris MI Clarity and Caris ChromoSeq • Pharma research and development services involving delivery of laboratory, strategic data, and research services to biopharmaceutical customers
- 支持 [ev_aefe7f0416e2701d](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): The Company is party to various collaboration and licensing agreements under which the Company out-licenses certain know-how and molecular data. The collaboration arrangements are intended to solidify the Company’s third-party partnerships to align oncology capabilities and create industry-leading molecular oncology research platforms to accelerate drug development and novel research.
- 支持 [ev_38e58c63ecdcd652](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): We deploy our proprietary profiling and signature offerings to analyze tissue and blood samples provided by biopharma partners, identify potential drug targets and help biopharma partners develop drug therapeutics through our drug target and therapeutic discovery business, Caris Discovery.

### pure_play: pass

公司定位为 AI TechBio，新产品以 AI 分析全基因组信号。

- 支持 [ev_37dfd881523323db](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): We are a leading, patient-centric, next-generation AI TechBio company and precision medicine pioneer.
- 支持 [ev_43410ecdf42b79bc](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000069/cai-20260930.htm) (primary-document): Caris Detect utilizes ultra-deep Whole Genome Sequencing, Whole Transcriptome Sequencing and advanced artificial intelligence to analyze molecular and biological signals associated with cancer.

### multi_node_control: pass

检测数据同时支撑数字产品与药企服务。

- 支持 [ev_c591aa539989492d](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000069/cai-20260930.htm) (primary-document): which now also serves as the foundation for our digital solutions such as Caris MI Clarity
- 支持 [ev_e7105bd021da8a34](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): Leverage our platform to provide solutions to biopharma companies to drive advances in personalized medicine

### earnings_validation: pass

2025 年收入 8.12 亿美元，增长 97%。

- 支持 [ev_dd575673d0545762](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): Total revenue was $812.0 million for the year ended December 31, 2025, compared to $412.3 million for the year ended December 31, 2024, an increase of $399.8 million, or 97.0%.

### counter_thesis: pass

债务与竞争风险已检验。

- 支持 [ev_17c530fbbecabc2f](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): we incurred net losses of $68.1 million and $281.9 million, respectively
- 反证 [ev_59a6b8364cef97ef](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): we and our subsidiaries had approximately $400.0 million aggregate principal amount of debt outstanding under the 2023 Term Loan
- 反证 [ev_99eb15cf6c686904](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): The precision oncology industry is intensely competitive.
- 证伪条件：收入增速跌破 30%
- 证伪条件：内控缺陷未在下一份年报前整改

### management_governance: pass

按 Serenity 规则：领导层连续，且无未结调查或未定继任。10-Q签署页（2026-11-04）明确确认David Dean Halbert仍以CEO兼主席在任，Luke Power以CFO兼首席会计官在任；所有通道均未披露开放性调查，亦无职位空缺或继任未定情形；存在CEO兼任主席、家族关联及关联方交易等治理事项，已记录于otherRisks。

- 支持 [ev_2dee1de182900397](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000032/cai-20260423.htm) (primary-document): David Dean Halbert serves as both our Chief Executive Officer and as Chairman of our Board of Directors.
- 支持 [ev_3250e30b40b43824](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000069/cai-20260930.htm) (primary-document): By: /s/ David Dean Halbert David Dean Halbert Founder, Chairman, and Chief Executive Officer (Principal Executive Officer) Date: November 04, 2026 By: /s/ Luke Power Luke Power Senior Vice President, Chief Financial Officer, and Chief Accounting Officer (Principal Financial and Accounting Officer)

## CARL · complete

审查记录：`state/serenity-reviews/CARL-claudecli-59c963d7d783227d074f.json`

### supply_chain_map: partial

证据显示了产品（aprevo椎间融合器+插入器械+数字手术规划）和下游客户类型（医院和门诊手术中心），也提及了合同制造和第三方服务作为上游。但缺乏具体供应商名称、地理集中度或替代周期数据。

- 支持 [ev_65958018e8052c93](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): Cost of sales includes the costs of creating patient-specific digital surgical plans and the manufacturing costs of our aprevo interbody implants and the accompanying inserter instruments
- 支持 [ev_65958018e8052c93](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): contract manufacturing and other third-party services, packaging, shipping, provision for excess and obsolete inventory
- 支持 [ev_0820d5aa6a7ef9f9](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): designing, manufacturing, and marketing of aprevo, a comprehensive technology platform for spine fusion surgical procedures
- 缺口：具体上游供应商名称及其全球数量
- 缺口：关键原材料的地理集中度
- 缺口：合同制造商的替代周期和依赖度
- 证伪条件：发现aprevo植入物使用的材料或制造工艺广泛可得无集中度
- 证伪条件：公司披露多家可互换的合同制造商

### chokepoint_evidence: unknown

证据中无任何供应集中度或替代壁垒的数据。专利段落反而强调IP可能被挑战无效化或绕过，表明公司自身缺乏不可替代的技术壁垒。FDA设备许可仅证明产品已获批不构成瓶颈证据。仅有AI相关性不足以通过此门。

- 反证 [ev_474085fa27557c19](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): its issuance is not conclusive as to its validity or its enforceability, and it may not provide us with adequate proprietary protection or competitive advantages against competitors with similar products
- 反证 [ev_474085fa27557c19](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): We cannot offer any assurances that the breadth of our issued patents will be sufficient to stop a competitor from developing, manufacturing, and commercializing one or more products
- 缺口：全球AI辅助脊柱手术规划市场的供应商数量和市场份额数据
- 缺口：患者定制椎间融合器的替代供应商分析
- 缺口：技术替代周期
- 缺口：反证只是通用风险条款或记录字段，不是针对公司的直接反证
- 证伪条件：发现Carlsmed在AI脊柱规划领域占有超50%市场份额且替代周期超过2年
- 证伪条件：发现其数字分割技术有不可绕过的专利壁垒

### customer_dependency: unknown

证据中未披露任何具体客户名称采用量或设计锁定关系。仅有泛泛的医院和门诊手术中心描述，无法确认下游对Carlsmed产品的具体依赖程度。

- 支持 [ev_0820d5aa6a7ef9f9](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): The Company typically derives its current revenues from selling aprevo to its hospital and ambulatory surgical center customers
- 缺口：具名的医院系统或ASC客户及其采购规模
- 缺口：客户集中度数据
- 缺口：外科医生培训切换成本导致的锁定效应证据
- 证伪条件：发现客户高度分散且无切换壁垒
- 证伪条件：披露前几大客户收入占比极高但关系不稳定

### pure_play: pass

公司明确披露仅有一个运营和报告分部，100%收入来自aprevo脊柱融合AI平台。属于纯正的AI医疗器械纯粹标的。

- 支持 [ev_0820d5aa6a7ef9f9](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): The Company has one business activity and operates as a single operating and reportable segment: the designing, manufacturing, and marketing of aprevo, a comprehensive technology platform for spine fusion surgical procedures
- 支持 [ev_65958018e8052c93](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): We sell our aprevo interbody implants and accompanying inserter instruments to customers under standard pricing schedules
- 证伪条件：公司进入与AI脊柱融合无关的新业务线稀释主题敞口

### multi_node_control: partial

公司同时拥有AI数字手术规划平台和患者定制植入物制造，可视为软件加硬件两个相连节点。但制造依赖合同制造商，上游材料控制缺失，不构成真正的多节点供应链控制。

- 支持 [ev_65958018e8052c93](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): Cost of sales includes the costs of creating patient-specific digital surgical plans and the manufacturing costs of our aprevo interbody implants
- 反证 [ev_36bb39f21c7a4e9a](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): we purchase equipment or materials, including hardware and software, from suppliers, and the design of these equipment or materials may be outside of our direct control
- 缺口：公司是否自有制造能力还是完全依赖合同制造
- 缺口：AI平台与植入物之间是否形成闭环控制
- 缺口：是否控制关键上游材料或工艺
- 证伪条件：发现AI规划软件和植入物制造均可由第三方独立替代
- 证伪条件：发现公司完全外包制造

### earnings_validation: partial

XBRL数据提供了实际财务结果：Q3 2026收入2155万美元同比增长64.9%，增长强劲。但净亏损1225万美元每季，现金3595万美元，9个月经营现金流出2904万美元。增长趋势支持AI医疗设备采纳故事，但缺乏将增长归因于AI技术壁垒的数据，且盈利尚未实现。

- 支持 [ev_ec2e60166b31f002](https://data.sec.gov/api/xbrl/companyfacts/CIK0001794546.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerIncludingAssessedTax): 21,554,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_ec2e60166b31f002](https://data.sec.gov/api/xbrl/companyfacts/CIK0001794546.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 13,074,000, a change of +64.9%
- 支持 [ev_ec2e60166b31f002](https://data.sec.gov/api/xbrl/companyfacts/CIK0001794546.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 35,945,000 for as of 2026-09-30
- 反证 [ev_ec2e60166b31f002](https://data.sec.gov/api/xbrl/companyfacts/CIK0001794546.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -12,245,000 for 2026-07-01 to 2026-09-30
- 反证 [ev_ec2e60166b31f002](https://data.sec.gov/api/xbrl/companyfacts/CIK0001794546.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -29,039,000 for 2026-01-01 to 2026-09-30
- 缺口：毛利率趋势及是否改善
- 缺口：收入增长中AI技术驱动的具体贡献比例
- 缺口：实现盈亏平衡的时间表
- 证伪条件：收入增速大幅放缓至低于20%
- 证伪条件：现金消耗加速导致跑道低于12个月且无融资计划

### counter_thesis: partial

证据中可识别多项风险：专利可被挑战或绕过IP护城河不确定；CMS拒绝TPT报销申请报销路径受阻；持续亏损现金3595万美元但每季烧约1000万美元；依赖第三方合同制造。但缺乏竞争格局分析估值压力测试和替代技术路径评估，反论证尚不完整。

- 支持 [ev_474085fa27557c19](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): Patents, if issued, may be challenged, deemed unenforceable, invalidated, narrowed, or circumvented
- 支持 [ev_65958018e8052c93](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): Our requested Transitional Pass-Through ("TPT") payment for aprevo cervical in outpatient settings was not approved by CMS in its November 2025 OPPS Final Rule
- 支持 [ev_36bb39f21c7a4e9a](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): Our competitors, many of which have substantially greater resources and have made substantial investments in patent portfolios, trade secrets, trademarks, and competing technologies
- 反证 [ev_ec2e60166b31f002](https://data.sec.gov/api/xbrl/companyfacts/CIK0001794546.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerIncludingAssessedTax): 21,554,000 for 2026-07-01 to 2026-09-30
- 缺口：主要竞争对手的AI脊柱手术产品对比
- 缺口：当前486M市值的估值合理性分析
- 缺口：AI脊柱规划技术的替代路径时间表
- 证伪条件：大型脊柱器械公司推出等效AI规划加定制植入物平台
- 证伪条件：CMS持续拒绝差异化报销限制定价权
- 证伪条件：现金跑道不足被迫稀释性增发
- 证伪条件：关键专利被无效化或竞争对手成功绕过
- 证伪条件：收入增速因市场饱和或竞争而骤降

### management_governance: partial

证据显示CEO和CFO评估了披露控制并认为有效，无会计分歧或调查记录。但缺乏管理层背景任期继任计划等关键治理信息。作为近期上市公司尚无管理层内控评估报告（过渡期豁免），治理成熟度有待观察。

- 支持 [ev_1ce600e308376456](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): our Chief Executive Officer and Chief Financial Officer have concluded that these disclosures controls were effective at a reasonable assurance level as of December 31, 2025
- 支持 [ev_1ce600e308376456](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): Changes in and Disagreements With Accountants on Accounting and Financial Disclosure. None.
- 反证 [ev_1ce600e308376456](https://www.sec.gov/Archives/edgar/data/1794546/000119312526071551/carl-20251231.htm) (primary-document): This Annual Report does not include a report of management's assessment regarding internal control over financial reporting or an attestation report of the company's registered public accounting firm due to a transition period
- 缺口：CEO和关键高管的任期背景和行业经验
- 缺口：董事会独立性和组成
- 缺口：继任计划和关键人物依赖风险
- 缺口：内部人交易模式
- 证伪条件：发现关键高管大量减持或离职
- 证伪条件：内控出现重大缺陷或重述财报
- 证伪条件：监管调查或治理丑闻

## CBLL · complete

审查记录：`state/serenity-reviews/CBLL-claude-6bb12db42646a85283ff.json`

### supply_chain_map: pass

头带由中国和越南的合同制造商组装，主要部件有双来源；最终检验在加州完成。

- 支持 [ev_92be1b830854373c](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): Contract manufacturers in China and Vietnam assemble the headbands, with final inspection and labeling completed at our California facilities.
- 支持 [ev_664d88f2418dc809](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): We have dual sources for major components of the Wearables.

### chokepoint_evidence: partial

原有瓶颈证据不变（癫痫持续状态首个 510(k)、唯一获许可的谵妄监测设备）。2026-09-16 的新许可 K261712 是实质等同许可，对比器械是竞品 encevis，且功能只是其子集、不含自动癫痫检测，因此不构成新的监管壁垒，维持 partial。

- 支持 [ev_2ca76098b5258cd6](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): became the first device to receive 510(k) clearance from the U.S. Food and Drug Administration
- 支持 [ev_d13e8c57307a5a7a](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): the first and only FDA-cleared delirium screening and monitoring device
- 反证 [ev_74b3f4fc2fcb6454](https://www.sec.gov/Archives/edgar/data/1861107/000119312526067238/cbll-20251231.htm) (primary-document): Alternative technologies addressing seizure, non-convulsive status epilepticus, delirium, LVO stroke or other indications we intend to expand into could materially adversely affect our business
- 反证 [ev_7b37c7ff6410c044](https://www.accessdata.fda.gov/cdrh_docs/pdf26/K261712.pdf) (primary-document): the subject device does not include any automatic seizure or spike detection functions and is claiming a subset of functions compared to the predicate device
- 反证 [ev_7c88c2dc65d29a26](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K261712) (primary-document): Decision Substantially Equivalent (SESE)

### customer_dependency: pass

按 Serenity 规则：一手文件披露了客户采用或使用。文件披露截至2025年12月31日已部署逾600家医院，截至2026年9月30日增至逾700家，2025年全年收入8906万美元，构成明确的产品采用证据。未发现任何合作伙伴关系公告。

- 支持 [ev_1e3bb72577f60435](https://www.sec.gov/Archives/edgar/data/1861107/000119312526067238/cbll-20251231.htm) (primary-document): As of December 31, 2025, we have successfully deployed the Ceribell System to more than 600 hospitals, ranging from top academic centers to small community hospitals.
- 支持 [ev_b985533a9d0ef40c](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): As of September 30, 2026, the Ceribell System has been adopted by more than 700 hospitals, ranging from top academic centers to small community hospitals.
- 支持 [ev_b6f0f05022a6ffaa](https://www.sec.gov/Archives/edgar/data/1861107/000119312526067238/cbll-20251231.htm) (primary-document): EEG recorders and EEG headbands, point in time $ 67,335 $ 50,079 EEG portal and Clarity subscriptions, over time 21,728 15,365 Total Revenue $ 89,063 $ 65,444

### pure_play: pass

核心产品是硬件加 AI 算法的床旁脑电平台。新许可的软件提供定量脑电指标，不涉及 AI 判读，不改变本门槛。

- 支持 [ev_0ee916a511fa4063](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): By combining proprietary, highly portable and rapidly deployable hardware with sophisticated artificial intelligence

### multi_node_control: pass

自管制造、供应链与分销，并拥有 AI 判读算法。

- 支持 [ev_45d79d7939e82b4e](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): We manage all aspects of manufacturing, supply chain, and distribution of the Wearables and recorder from our facilities in Sunnyvale, California.
- 支持 [ev_d104b1d63bc68a9b](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): EEG data captured by the recorder is interpreted by our proprietary AI-powered seizure detection algorithms

### earnings_validation: pass

2025 年收入 8,910 万美元，增长 36%，毛利率 88%。

- 支持 [ev_36ab480dcf5d383b](https://www.sec.gov/Archives/edgar/data/1861107/000119312526067238/cbll-20251231.htm) (primary-document): We recognized revenue of $89.1 million for the year ended December 31, 2025, compared to revenue of $65.4 million for the year ended December 31, 2024, representing 36% year-over-year growth.
- 支持 [ev_32f71ead8845267c](https://www.sec.gov/Archives/edgar/data/1861107/000119312526067238/cbll-20251231.htm) (primary-document): we recognized a gross margin of 88%

### counter_thesis: pass

亏损扩大、海外制造风险已检验；新增：FDA 摘要显示竞品 encevis 已有更完整的已许可脑电分析功能，替代风险有一手证据。

- 支持 [ev_9cc54b72cf1839b8](https://www.sec.gov/Archives/edgar/data/1861107/000119312526067238/cbll-20251231.htm) (primary-document): a net loss of $53.4 million
- 反证 [ev_ba9acbccac45b05a](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): Net loss $ ( 60,357 ) $ ( 39,885 )
- 反证 [ev_59265832cfe9f6c3](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): The Company utilizes contract manufacturers in China and Vietnam to supply key sub-assemblies for its primary products.
- 反证 [ev_9d1efc98354ed67f](https://www.accessdata.fda.gov/cdrh_docs/pdf26/K261712.pdf) (primary-document): Primary Predicate Device encevis (K240993) Subject Device Ceribell EEG Analysis Software
- 证伪条件：收入增速跌破 25%
- 证伪条件：NTAP 到期后医院使用量下降
- 证伪条件：竞品已获许可的自动癫痫检测功能（如 encevis）进入 ICU 和急诊快速脑电场景并获得报销

### management_governance: pass

按 Serenity 规则：领导层连续，且无未结调查或未定继任。2026年4月6日代理声明（DEF 14A）确认Chao任CEO、Blumberg任CFO、Robertson任董事会主席，三职均有在任证据；通篇段落未披露任何公开调查，Iancovici辞职仅涉及普通董事席位，非关键高管职位，无继任悬空问题。注意：最新高管状态证据截至2026年4月，三份11月Form 4均为董事股票交易，无法独立证明高管职务在2026年11月的持续状态。

- 支持 [ev_9692ffd439d7c745](https://www.sec.gov/Archives/edgar/data/1861107/000119312526163290/cbll-20260420.htm) (primary-document): The following is biographical information for our executive officers as of April 6, 2026: Name Age Position Xingjuan (Jane) Chao, Ph.D. 46 President, Chief Executive Officer, Co-Founder, and Director Scott Blumberg 44 Chief Financial Officer
- 支持 [ev_47a90dbbd7315cdf](https://www.sec.gov/Archives/edgar/data/1861107/000119312526163290/cbll-20260420.htm) (primary-document): In 2025, our NEOs and their positions were as follows: • Xingjuan (Jane) Chao, Ph.D., President, Chief Executive Officer, and Co-Founder; • Scott Blumberg, Chief Financial Officer; and • Raymond Woo, Ph.D., Chief Technology Officer.
- 支持 [ev_1f6d56fa27258256](https://www.sec.gov/Archives/edgar/data/1861107/000119312526163290/cbll-20260420.htm) (primary-document): Ms. Robertson currently serves as the Chair of the Board. In that role, Ms. Robertson presides over the executive sessions of the Board and serves as a liaison between management and the Board.
- 支持 [ev_a629f5ab415304f0](https://www.sec.gov/Archives/edgar/data/1861107/000119312526163290/cbll-20260420.htm) (primary-document): Former Director Lucian Iancovici, M.D. (1) — — (1) Dr. Iancovici resigned from service on the Board on December 31, 2025.

## CCLD · complete

审查记录：`state/serenity-reviews/CCLD-claudecli-f8ebade43f8b29f8d3a7.json`

### supply_chain_map: partial

XBRL标签揭示了多个业务线（Healthcare IT下的Technology-Enabled Business Solutions、Professional Services、Printing & Mailing、Group Purchasing Services；Medical Practice Management；Chronic Care Management；Remote Patient Monitoring），但证据中缺乏对上游供应商和下游具体客户的叙述性描述。无法绘制完整的供应链图。

- 支持 [ev_6a59ff199addbd2d](https://www.sec.gov/Archives/edgar/data/1582982/000149315226050254/form10-q.htm) (primary-document): CCLD:HealthcareITMember CCLD:TechnologyEnabledBusinessSolutionsMember 2026-07-01 2026-09-30
- 支持 [ev_6a59ff199addbd2d](https://www.sec.gov/Archives/edgar/data/1582982/000149315226050254/form10-q.htm) (primary-document): CCLD:MedicalPracticeManagementMember 2026-07-01 2026-09-30
- 支持 [ev_6a59ff199addbd2d](https://www.sec.gov/Archives/edgar/data/1582982/000149315226050254/form10-q.htm) (primary-document): CCLD:ChronicCareManagementMember 2026-07-01 2026-09-30
- 支持 [ev_6a59ff199addbd2d](https://www.sec.gov/Archives/edgar/data/1582982/000149315226050254/form10-q.htm) (primary-document): CCLD:RemotePatientMonitoringMember 2026-07-01 2026-09-30
- 缺口：上游技术供应商（云基础设施、EHR数据源）的具体披露
- 缺口：下游客户类型和集中度的叙述性说明
- 缺口：各业务线收入分拆数据
- 证伪条件：如果10-K年报显示客户高度分散且无关键供应商依赖，则供应链图无投资意义

### chokepoint_evidence: fail

CareCloud经营的是竞争激烈的医疗IT/RCM市场，证据中无任何供应集中度、替代壁垒或独占性地位的信息。Healthcare IT领域有大量竞争对手（athenahealth、eClinicalWorks等），不构成chokepoint。

- 反证 [ev_f03b50f7b7e7d6c7](https://www.sec.gov/Archives/edgar/data/1582982/000149315226050254/form10-q.htm) (primary-document): our ability to maintain operations in Pakistan, Azad Jammu and Kashmir, and Sri Lanka in a manner that continues to enable us to offer competitively priced products and services
- 缺口：市场份额数据或供应集中度证据
- 缺口：客户转换成本或锁定机制的披露
- 缺口：任何技术专利或独占性壁垒的说明
- 证伪条件：若CareCloud的某一细分产品（如RPM或CCM）被证实在特定细分市场占据>50%份额，则需重新评估

### customer_dependency: unknown

证据包中无任何具体客户名称、客户集中度或采用情况的披露。XBRL标签仅显示收入类别（RevenueCycleManagement、GroupPurchasingServices、ReferralFees等），未提供下游客户身份。

- 支持 [ev_0e77e5c64b98b762](https://www.sec.gov/Archives/edgar/data/1582982/000149315226050254/form10-q.htm) (primary-document): CCLD:RevenueCycleManagementMember 2026-09-30 0001582982 CCLD:GroupPurchasingServicesMember 2026-09-30
- 缺口：主要客户名称及收入占比
- 缺口：客户数量和留存率指标
- 缺口：与医疗机构或支付方的具体合同披露
- 证伪条件：若10-K披露单一客户占比>10%，则存在集中风险而非依赖优势

### pure_play: partial

CareCloud专注于医疗保健IT，属于纯医疗行业公司，但并非AI-medicine纯玩家。业务横跨Healthcare IT和Medical Practice Management两大板块，涵盖RCM、打印邮寄、集团采购等传统服务，AI相关收入占比不明。

- 支持 [ev_67d26bbda4b73d3a](https://www.sec.gov/Archives/edgar/data/1582982/000149315226036363/form10-q.htm) (primary-document): CCLD:HealthcareITMember CCLD:TechnologyEnabledBusinessSolutionsMember 2026-04-01 2026-06-30
- 支持 [ev_67d26bbda4b73d3a](https://www.sec.gov/Archives/edgar/data/1582982/000149315226036363/form10-q.htm) (primary-document): CCLD:HealthcareITMember CCLD:PrintingAndMailingServicesMember 2026-04-01 2026-06-30
- 反证 [ev_67d26bbda4b73d3a](https://www.sec.gov/Archives/edgar/data/1582982/000149315226036363/form10-q.htm) (primary-document): CCLD:HealthcareITMember CCLD:GroupPurchasingServicesMember 2026-04-01 2026-06-30
- 缺口：AI相关收入或AI功能的具体披露
- 缺口：各业务板块收入分拆金额
- 缺口：AI产品路线图或AI研发投入占比
- 证伪条件：若AI相关收入占总收入不足10%，则不能视为AI-medicine纯玩家

### multi_node_control: unknown

CareCloud拥有多条产品线（RCM、EHR/Medsphere、CCM、RPM、打印邮寄），但这些是独立的服务产品，不构成对同一供应链上下游连续节点的控制。证据中无垂直整合或供应链节点控制的说明。

- 缺口：产品之间供应链上下游关系的说明
- 缺口：垂直整合带来的定价权或锁定效应证据
- 缺口：数据流或工作流跨节点控制的具体披露
- 缺口：不通过需要直接反证，缺少证据不能等同失败
- 证伪条件：若CareCloud的EHR数据被其RCM和CCM产品独占使用且客户无法替换，可能构成多节点控制

### earnings_validation: partial

Q3 2026财务数据扎实：收入$33.7M（同比+8.6%），净利润$4.7M为正，前9月经营现金流$16.3M。公司盈利，但这些数据仅验证了一家盈利的医疗IT公司，未验证AI-medicine chokepoint投资论点。增速仅~9%，属于缓慢增长。

- 支持 [ev_dd0d7694033299dd](https://data.sec.gov/api/xbrl/companyfacts/CIK0001582982.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 33,725,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_dd0d7694033299dd](https://data.sec.gov/api/xbrl/companyfacts/CIK0001582982.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 4,727,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05
- 支持 [ev_dd0d7694033299dd](https://data.sec.gov/api/xbrl/companyfacts/CIK0001582982.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): 16,327,000 for 2026-01-01 to 2026-09-30
- 支持 [ev_dd0d7694033299dd](https://data.sec.gov/api/xbrl/companyfacts/CIK0001582982.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 31,067,000, a change of +8.6%
- 缺口：各业务板块收入增长分解
- 缺口：毛利率和EBITDA利润率趋势
- 缺口：AI相关产品的收入贡献指标
- 证伪条件：若收入增长来自收购叠加（Medsphere、Empower、MapApp、RevNu）而非有机增长，则增长质量存疑

### counter_thesis: partial

证据揭示多项风险：1）海外运营依赖（巴基斯坦/AJK/斯里兰卡）带来地缘政治风险；2）收购驱动增长（Medsphere、Empower、MapApp、RevNu四次收购）带来整合风险；3）ATM协议（2026-04-13）意味着潜在稀释；4）市值仅$96M，流动性风险高。但缺少对竞争、替代和估值角度的系统压力测试。

- 支持 [ev_f03b50f7b7e7d6c7](https://www.sec.gov/Archives/edgar/data/1582982/000149315226050254/form10-q.htm) (primary-document): our ability to maintain operations in Pakistan, Azad Jammu and Kashmir, and Sri Lanka in a manner that continues to enable us to offer competitively priced products and services
- 支持 [ev_6a59ff199addbd2d](https://www.sec.gov/Archives/edgar/data/1582982/000149315226050254/form10-q.htm) (primary-document): CCLD:ATMAgreementMember 2026-04-13 2026-04-13
- 支持 [ev_8ee8500ffc426ca9](https://www.sec.gov/Archives/edgar/data/1582982/000149315226036363/form10-q.htm) (primary-document): CCLD:MedsphereSystemsCorporationMember 2025-08-22 0001582982 CCLD:MedsphereSystemsCorporationMember 2025-08-22 2025-08-22
- 反证 [ev_dd0d7694033299dd](https://data.sec.gov/api/xbrl/companyfacts/CIK0001582982.json) (sec-companyfacts): R&D expense (ResearchAndDevelopmentExpense): 1,052,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05
- 缺口：竞争格局分析（vs athenahealth、Veeva等）
- 缺口：客户流失率和NRR数据
- 缺口：收购整合进展和协同效应量化
- 缺口：估值对比（EV/Revenue、EV/EBITDA vs 同业）
- 证伪条件：海外运营中断（巴基斯坦/斯里兰卡政治动荡）导致成本优势丧失
- 证伪条件：ATM协议下持续增发导致股东严重稀释
- 证伪条件：收购整合失败导致商誉减值
- 证伪条件：大型医疗IT厂商以AI功能侵蚀中小客户市场
- 证伪条件：R&D仅$1M/季度，在AI竞赛中技术投入严重不足

### management_governance: unknown

证据包中仅有XBRL标签提及ExecutiveChairmanMember，无管理层姓名、背景、任期或治理结构的叙述性信息。存在Series A和Series B优先股以及ATM协议，暗示复杂的股本结构，但无法评估治理质量。

- 支持 [ev_43f19e499af3a780](https://www.sec.gov/Archives/edgar/data/1582982/000149315226050254/form10-q.htm) (primary-document): CCLD:ExecutiveChairmanMember 2026-09-30
- 缺口：CEO/CFO姓名、任期和背景
- 缺口：董事会独立性和构成
- 缺口：内部人持股比例和交易记录
- 缺口：优先股投票权和治理影响
- 缺口：审计意见和内控评估
- 证伪条件：若存在管理层频繁变动或SEC调查，治理评级应降为fail

## CERT · complete

审查记录：`state/serenity-reviews/CERT-claude-13e3c5f84c1f20750570.json`

### supply_chain_map: pass

软件托管依赖第三方云；客户覆盖药企及动物健康、作物科学、医疗器械与公共部门。

- 支持 [ev_1a135a4d844acfdc](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): We rely on third-party providers of cloud-based infrastructure to host our software solutions.
- 支持 [ev_81e1a24c42482487](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): Certara serves customers in animal health, crop science, bio science, medical devices, and public sector industries.

### chokepoint_evidence: partial

软件被全球 20 家药品监管机构采用，验证模型构成进入壁垒；但生物模拟软件竞争者众多。

- 支持 [ev_f959761c846bd098](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): our software products are licensed by 20 global drug regulatory agencies, including the FDA
- 支持 [ev_1e005be68517709e](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): presents a significant barrier to new entrants
- 反证 [ev_9d4c7c030d4667f3](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): In the biosimulation software market, we compete with other technology companies including Mathworks, Dassault Systemes, Ansys, Simulations Plus, and NONMEM, a division of ICON.

### customer_dependency: pass

客户分散，无单一客户超过 10%，前十大客户占 24%。

- 支持 [ev_aa3f4f89ef926ba4](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): No single customer accounted for more than 10% of our revenues in 2025. Our ten largest customers accounted for 24% and 27% of revenues for the years ended December 31, 2025 and 2024, respectively.

### pure_play: partial

AI 与机器学习正在融入软件和咨询业务，核心仍是生物模拟。

- 支持 [ev_6ed90a9fc23571cb](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): Native AI and machine learning technologies are being incorporated across our technology and consulting services portfolios
- 缺口：AI 相关收入占比

### multi_node_control: pass

同时提供生物模拟软件、技术服务和数据解决方案。

- 支持 [ev_4f768a8421510200](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): We compete in both the biosimulation software market and technology-enabled services markets
- 支持 [ev_c3ce9222bb72a0f6](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000035/cert-20260930.htm) (primary-document): These data solutions are used internally and industry wide by life sciences companies.

### earnings_validation: partial

2025 年收入增长 3,370 万美元，但缺少 2026 年持续经营业务增速原文。

- 支持 [ev_03ec1922ce47d667](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): The increase in net income was primarily due to a $33.7 million increase in revenue
- 缺口：2026 年持续经营业务增速原文

### counter_thesis: pass

债务与客户研发预算受药价政策压力的风险已检验。

- 支持 [ev_0d8e85f78d0bc614](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): Our ten largest customers accounted for 24% of revenues for the year ended December 31, 2025.
- 反证 [ev_c923e9eb7aeea916](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): we had $295.5 million in total borrowings under our credit agreement
- 反证 [ev_fe3d8144e5f86357](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): may continue to have an economic impact on the incentive structure related to drug development R&D spending by our customers
- 证伪条件：软件续约率下降
- 证伪条件：监管机构转向开源或自研工具

### management_governance: partial

内控审计按 PCAOB 标准执行；未取得管理层变动材料。

- 支持 [ev_cd02d4349d1d0549](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): We conducted our audit in accordance with the standards of the PCAOB.
- 缺口：管理层变动与内部人交易

## CGEM · complete

审查记录：`state/serenity-reviews/CGEM-claudecli-223387b2396793ec6926.json`

### supply_chain_map: partial

证据显示Cullinan依赖第三方CMO生产候选药物，上游为合同制造商和关键试剂供应商，产品为T细胞接合器（CLN-978、CLN-049、velinotamig、zipalertinib），下游为自身免疫疾病和癌症患者群体。但无具体CMO名称或供应商关系披露，供应链图谱不完整。

- 支持 [ev_aedb7c554309cb83](https://www.sec.gov/Archives/edgar/data/1789972/000119312526099362/cgem-20251231.htm) (primary-document): We do not currently own any facility that may be used as our clinical-scale manufacturing and processing facility and must currently rely on outside vendors to manufacture our product candidates.
- 支持 [ev_c3ee8399b2a51ff2](https://www.sec.gov/Archives/edgar/data/1789972/000119312526454408/cgem-ex99_1.htm) (sec-8k): a clinical-stage biopharmaceutical company accelerating potential first- or best-in-class, disease-modifying T cell engagers in autoimmune diseases and cancer
- 支持 [ev_caf666055d8ebec5](https://www.sec.gov/Archives/edgar/data/1789972/000119312526099362/cgem-20251231.htm) (primary-document): raw materials and components used in the manufacturing process, particularly those for which we have no other source or supplier, may not be available
- 缺口：具体合同制造商（CMO）名称
- 缺口：关键原料供应商身份
- 缺口：供应链各节点的地理分布
- 证伪条件：发现Cullinan已建立自有生产设施
- 证伪条件：公开披露的具体CMO合同

### chokepoint_evidence: unknown

Cullinan是临床阶段药物开发商，无证据显示其在任何供应链节点拥有供应集中度或替代壁垒。专利相关段落均为通用风险因素语言，不构成瓶颈证据。T细胞接合器领域有多家竞争者。

- 缺口：任何供应集中度数据
- 缺口：独家制造工艺或不可替代技术证据
- 缺口：市场份额或竞争格局量化数据
- 证伪条件：发现Cullinan拥有某种独有且难以替代的技术平台
- 证伪条件：证据显示其候选药物在靶点上具有不可绕开的专利壁垒

### customer_dependency: unknown

临床阶段公司，无商业化产品，无客户收入。Zipalertinib与Taiho合作属合作伙伴关系但尚未获批销售。Genrix为velinotamig的许可方而非客户。无任何下游采购方的披露。

- 缺口：商业客户或支付方的采纳证据
- 缺口：上市后产品的处方或采购数据
- 缺口：保险覆盖或报销确认
- 证伪条件：zipalertinib获FDA批准并产生商业销售
- 证伪条件：任何产品获得医院或支付方采纳的披露

### pure_play: partial

公司明确聚焦于T细胞接合器用于自身免疫疾病和癌症，属纯粹的临床阶段生物制药公司。但无收入可衡量主题敞口，且zipalertinib（EGFR抑制剂）并非TCE，显示一定程度的治疗领域多元化。

- 支持 [ev_72ee89875616cad2](https://www.sec.gov/Archives/edgar/data/1789972/000119312526454408/cgem-ex99_1.htm) (primary-document): Cullinan Therapeutics, Inc. (Nasdaq: CGEM) is a biopharmaceutical company developing potential first- or best-in-class, disease-modifying T cell engagers for autoimmune diseases and cancer.
- 支持 [ev_c3ee8399b2a51ff2](https://www.sec.gov/Archives/edgar/data/1789972/000119312526454408/cgem-ex99_1.htm) (sec-8k): we remain focused on strengthening our leadership position in the T cell engager space
- 缺口：收入分部数据（尚无收入）
- 缺口：各管线资源分配的量化信息
- 证伪条件：公司收购非TCE资产导致主题稀释
- 证伪条件：zipalertinib收入占比远超TCE管线

### multi_node_control: unknown

无证据显示Cullinan控制供应链中两个或更多相连节点。公司依赖外部CMO制造，仅持有候选药物的知识产权许可，不控制上游原料或下游分销。

- 缺口：自有制造能力证据
- 缺口：垂直整合的披露
- 缺口：对上游供应或下游渠道的控制证据
- 证伪条件：Cullinan收购CMO或建立自有生产能力
- 证伪条件：公司建立自有销售团队并控制分销渠道

### earnings_validation: unknown

准备阶段公司，零收入符合预期。Q3 2026净亏损$49.4M，现金及投资$313.8M，管理层预计运营资金可支撑至2029年。研发支出从$42.0M降至$40.2M显示支出可控。现金充裕可支持当前临床里程碑推进，但无收入验证。

- 支持 [ev_d2b5d503e73c1659](https://www.sec.gov/Archives/edgar/data/1789972/000119312526454408/cgem-ex99_1.htm) (primary-document): Research and development $ 40,169 $ 41,968 $ 126,729 $ 144,457 General and administrative 12,431 13,627 36,822 41,932 Total operating expenses 52,600 55,595 163,551 186,389
- 支持 [ev_d2b5d503e73c1659](https://www.sec.gov/Archives/edgar/data/1789972/000119312526454408/cgem-ex99_1.htm) (primary-document): Cash, cash equivalents, investments, and interest receivable $ 313,813 $ 438,960 Total assets $ 322,559 $ 448,374
- 缺口：商业收入数据（预计在产品获批后才有）
- 缺口：具体里程碑付款时间表
- 缺口：引用不存在或原文无法匹配
- 证伪条件：现金烧完速度大幅加快导致runway低于12个月
- 证伪条件：关键临床试验失败迫使重大战略调整

### counter_thesis: partial

已识别多项风险：1）CLN-617已因临床数据审查后终止开发；2）依赖第三方CMO制造；3）TCE领域竞争者众多；4）zipalertinib NDA尚待审批（PDUFA日期2027年2月27日）。但缺乏对具体竞争对手市场份额、替代疗法进展的量化分析。现金runway至2029年，无近期融资风险。

- 支持 [ev_fda22f8683b98c77](https://www.sec.gov/Archives/edgar/data/1789972/000119312526099362/cgem-20251231.htm) (primary-document): In November 2025, after a review of the emerging clinical data in patients with advanced solid tumors, Cullinan decided not to pursue further development of CLN-617.
- 支持 [ev_aedb7c554309cb83](https://www.sec.gov/Archives/edgar/data/1789972/000119312526099362/cgem-20251231.htm) (primary-document): Our anticipated reliance on a limited number of third-party manufacturers exposes us to a number of risks
- 支持 [ev_2f28eeb451dfa0f2](https://www.sec.gov/Archives/edgar/data/1789972/000119312526454408/cgem-ex99_1.htm) (primary-document): An NDA for zipalertinib monotherapy for relapsed EGFR ex20ins NSCLC remains under review with a Prescription Drug User Fee Act target action date of February 27, 2027.
- 反证 [ev_fda22f8683b98c77](https://www.sec.gov/Archives/edgar/data/1789972/000119312526099362/cgem-20251231.htm) (primary-document): Cullinan decided not to pursue further development of CLN-617. In connection with the decision not to pursue further development of CLN-617, the Company notified MIT of its decision to terminate the MIT License Agreement.
- 缺口：TCE领域具体竞争对手管线进展对比
- 缺口：zipalertinib对比其他EGFR ex20ins抑制剂的竞争分析
- 缺口：估值倍数与同行对比
- 缺口：地缘政治风险评估（Genrix中国合作）
- 证伪条件：CLN-978或CLN-049关键试验失败
- 证伪条件：zipalertinib NDA被FDA拒绝
- 证伪条件：竞争对手TCE药物率先获批并占领市场
- 证伪条件：Genrix合作因中国监管变化受阻
- 证伪条件：现金消耗超预期导致被迫稀释融资

### management_governance: partial

CEO Nadim Ahmed在8-K中发表声明显示在任。内部控制截至2025年12月31日被评估为有效。无公开调查或继任问题披露。但缺乏管理团队履历、董事会独立性、高管变动历史等详细治理信息。

- 支持 [ev_49ad8cffcc01a3f7](https://www.sec.gov/Archives/edgar/data/1789972/000119312526099362/cgem-20251231.htm) (primary-document): Based on the results of its evaluation, management has concluded that our internal control over financial reporting was effective as of December 31, 2025
- 支持 [ev_c3ee8399b2a51ff2](https://www.sec.gov/Archives/edgar/data/1789972/000119312526454408/cgem-ex99_1.htm) (sec-8k): said Nadim Ahmed, President and CEO of Cullinan Therapeutics.
- 缺口：管理团队完整履历和行业经验
- 缺口：董事会构成和独立性详情
- 缺口：高管薪酬结构
- 缺口：近期高管变动记录
- 证伪条件：CEO或关键高管离职
- 证伪条件：内部控制重大缺陷披露
- 证伪条件：监管调查或公司治理诉讼

## ELDN · complete

审查记录：`state/serenity-reviews/ELDN-claudecli-36e88204e6db74ef6bad.json`

### supply_chain_map: unknown

可以部分绘制供应链：上游为第三方CMO（Lonza提供生产技术许可）和ALS TDI（专利许可方），产品为tegoprubart（抗CD40L抗体），下游为肾移植、胰岛细胞移植、肝移植及ALS患者。但具体原料供应商、API生产细节缺失，仅有风险因素中对第三方制造商依赖的概括性描述。

- 支持 [ev_a16309e795344918](https://www.sec.gov/Archives/edgar/data/1404281/000119312526116164/eldn-20251231.htm) (primary-document): We also expect to rely on other third parties to label, store, and distribute drug supplies for our clinical trials
- 缺口：具体API原料药供应商名称
- 缺口：生产设施地点和产能信息
- 缺口：供应链各节点的集中度数据
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现tegoprubart有多个合格CMO且切换成本低，则供应链风险降低

### chokepoint_evidence: unknown

Eledon是临床阶段药企，不具备Serenity方法所定义的供应链瓶颈特征。专利组合提供的排他性是标准药企IP保护，不等同于物理供应集中度或替代壁垒。没有证据表明公司控制任何稀缺的物理输入或不可替代的供应节点。

- 支持 [ev_2170c0c9fc31b036](https://www.sec.gov/Archives/edgar/data/1404281/000119312526116164/eldn-20251231.htm) (primary-document): The second exclusively-licensed family is directed to tegoprubart, with 11 pending applications, and issued patents including five issued United States patents and 23 issued foreign patents
- 缺口：供应集中度或替代壁垒的具体证据
- 缺口：全球同类抗CD40L抗体竞争格局分析
- 缺口：tegoprubart相对竞品的不可替代性数据
- 证伪条件：发现tegoprubart是唯一进入Phase 3的抗CD40L抗体且竞品需5年以上追赶
- 证伪条件：发现关键生产工艺具有不可复制的技术壁垒

### customer_dependency: partial

无商业化产品，无付费客户。但有多个知名移植中心的研究者发起试验和同情用药，表明临床社区对tegoprubart有真实需求和采纳意愿：杜克大学、麻省总医院、芝加哥大学医学中心均在使用tegoprubart。这属于临床验证而非商业客户依赖。

- 支持 [ev_7ab38568bfcf2462](https://www.sec.gov/Archives/edgar/data/1404281/000119312526458378/eldn-ex99_1.htm) (sec-8k): The first highly sensitized kidney transplant patient was dosed with tegoprubart under a compassionate-use protocol at Duke University Medical Center
- 支持 [ev_7ab38568bfcf2462](https://www.sec.gov/Archives/edgar/data/1404281/000119312526458378/eldn-ex99_1.htm) (sec-8k): The third patient was treated as part of the investigator-initiated study evaluating tegoprubart for kidney transplant tolerance induction at Massachusetts General Hospital (MGH)
- 支持 [ev_ca2a490eba00e40d](https://www.sec.gov/Archives/edgar/data/1404281/000119312526458378/eldn-ex99_1.htm) (primary-document): The University of Chicago Medicine Transplant Institute expanded its ongoing investigator-initiated study evaluating tegoprubart as the core immunosuppressant for T1D patients undergoing islet cell transplantation by enrolling three additional subjects
- 缺口：商业化后的预期客户或分销协议
- 缺口：支付方（保险/医保）覆盖意向
- 缺口：与大型药企的合作或授权协议
- 证伪条件：研究者发起试验报告负面结果导致临床社区丧失兴趣
- 证伪条件：主要移植中心转向竞品抗CD40L抗体

### pure_play: pass

公司明确为单一经营分部，完全聚焦于tegoprubart的开发。CODM以净亏损作为分部损益指标，无其他业务线稀释主题敞口。100%收入敞口（未来如获批）集中于移植排斥和ALS领域。

- 支持 [ev_10f9f23fc8874147](https://www.sec.gov/Archives/edgar/data/1404281/000119312526116164/eldn-20251231.htm) (primary-document): The Company operates as one operating and one reportable segment, focused on the development of tegoprubart, to develop therapies to protect transplanted organs and prevent rejection, and to treat ALS
- 支持 [ev_b40244b328c50cd2](https://www.sec.gov/Archives/edgar/data/1404281/000119312526458378/eldn-ex99_1.htm) (primary-document): Eledon Pharmaceuticals, Inc. is a clinical stage biotechnology company that is developing immune-modulating therapies for the management and treatment of life-threatening conditions
- 证伪条件：公司收购或引进与移植/ALS无关的资产，稀释纯度

### multi_node_control: unknown

公司依赖第三方CMO（Lonza）进行生产，依赖ALS TDI的专利许可。公司不控制上游制造节点，也不控制下游分销。仅拥有自有专利族和独家许可，但这不构成对多个连接供应链节点的控制。

- 缺口：自有生产设施或垂直整合的证据
- 缺口：对上下游多个节点的控制权证据
- 证伪条件：公司收购CMO或建立自有生产线
- 证伪条件：公司建立自有分销/给药网络

### earnings_validation: partial

准备阶段公司，零收入符合预期。截至2026年9月30日现金及短期投资为6970万美元，公司声明资金可维持到2027年Q2，约9.8个月跑道。R&D支出Q3为1780万美元。跑道不足12个月，存在融资风险，但足以启动Q4 2026的Phase 3 LEGACY试验这一近期里程碑。现金虽可资助试验启动，但无法覆盖整个Phase 3（约600名患者），后续需额外融资。

- 支持 [ev_7ab38568bfcf2462](https://www.sec.gov/Archives/edgar/data/1404281/000119312526458378/eldn-ex99_1.htm) (sec-8k): Cash, cash equivalents and short-term investments of $69.7 million with cash runway into Q2 2027
- 支持 [ev_b40244b328c50cd2](https://www.sec.gov/Archives/edgar/data/1404281/000119312526458378/eldn-ex99_1.htm) (primary-document): Cash, cash equivalents and short-term investments totaled $69.7 million as of September 30, 2026, compared to $133.3 million as of December 31, 2025
- 支持 [ev_b40244b328c50cd2](https://www.sec.gov/Archives/edgar/data/1404281/000119312526458378/eldn-ex99_1.htm) (primary-document): Research and development (R&D) expenses for the third quarter of 2026 were $17.8 million, including $0.9 million of non-cash stock-based compensation expense
- 支持 [ev_629f8bbff72acaf2](https://www.sec.gov/Archives/edgar/data/1404281/000119312526458378/eldn-ex99_1.htm) (primary-document): Common stock, $0.001 par value, 450,000,000 shares authorized at September 30, 2026 and 300,000,000 shares authorized at December 31, 2025; 81,442,402 and 75,430,033 shares issued
- 缺口：具体融资计划或时间表
- 缺口：Phase 3试验完整预算估算
- 证伪条件：现金低于一年烧钱率且无已披露的融资安排（已接近此状态）
- 证伪条件：Phase 3费用大幅超出预期加速现金消耗

### counter_thesis: unknown

已识别多项关键风险：(1) 跑道不足12个月（financingRisk: true），稀释性融资几乎确定——授权股数已从3亿增至4.5亿，已发行从7543万增至8144万；(2) 完全依赖单一资产tegoprubart，Phase 3失败即公司价值归零；(3) tacrolimus为数十年标准疗法，替换壁垒高；(4) 第三方制造依赖风险。但缺乏竞品抗CD40L抗体的具体对比数据和估值压力测试。

- 支持 [ev_a16309e795344918](https://www.sec.gov/Archives/edgar/data/1404281/000119312526116164/eldn-20251231.htm) (primary-document): reliance on the third party for regulatory compliance and quality assurance; • the possible breach of the manufacturing agreement by the third party
- 支持 [ev_b40244b328c50cd2](https://www.sec.gov/Archives/edgar/data/1404281/000119312526458378/eldn-ex99_1.htm) (primary-document): The Company expects cash, cash equivalents and short-term investments currently on hand to fund operations into Q2 2027
- 支持 [ev_629f8bbff72acaf2](https://www.sec.gov/Archives/edgar/data/1404281/000119312526458378/eldn-ex99_1.htm) (primary-document): Common stock, $0.001 par value, 450,000,000 shares authorized at September 30, 2026 and 300,000,000 shares authorized at December 31, 2025; 81,442,402 and 75,430,033 shares issued
- 反证 [ev_7ab38568bfcf2462](https://www.sec.gov/Archives/edgar/data/1404281/000119312526458378/eldn-ex99_1.htm) (sec-8k): Tegoprubart-treated patients maintained statistically significantly higher mean estimated glomerular filtration rate (eGFR) at 18, 21, and 24 months, with an approximately 13 mL/min/1.73m 2 advantage over tacrolimus at month 24
- 反证 [ev_ca2a490eba00e40d](https://www.sec.gov/Archives/edgar/data/1404281/000119312526458378/eldn-ex99_1.htm) (primary-document): the 12 patients treated to date, who have achieved 100% insulin independence and demonstrated stable islet graft function through 22 months of follow-up with a favorable tolerability profile
- 缺口：竞品抗CD40L抗体（如Bristol-Myers等）的开发进度对比
- 缺口：tegoprubart定价与支付方接受度分析
- 缺口：Phase 3 LEGACY试验的完整统计设计与失败概率估算
- 缺口：估值相对于同类Phase 3移植药企的对比
- 缺口：引用不存在或原文无法匹配
- 证伪条件：Phase 3 LEGACY试验未达非劣效性主要终点
- 证伪条件：竞品抗CD40L抗体率先获批抢占市场
- 证伪条件：融资条件恶化导致极端稀释或无法完成试验
- 证伪条件：FDA要求额外安全性研究延迟审批时间线
- 证伪条件：tacrolimus仿制药价格进一步下降压缩tegoprubart定价空间

### management_governance: partial

CEO David-Alexandre C. Gros, M.D.已明确披露并持续领导公司。重大弱点（内控缺陷涉及优先股等复杂权益工具会计处理）已于2025年12月31日完成整改并通过测试。但该重大弱点历史记录本身是治理风险信号，公司承认无法保证不会再次发生。反收购条款（特拉华州章程保护）也已披露。整体治理架构可接受但有历史瑕疵。

- 支持 [ev_84269d669b6b3629](https://www.sec.gov/Archives/edgar/data/1404281/000119312526116164/eldn-20251231.htm) (primary-document): During the fourth quarter of the year ended December 31, 2025, we successfully completed the testing necessary to conclude that the material weakness has been remediated
- 支持 [ev_7ab38568bfcf2462](https://www.sec.gov/Archives/edgar/data/1404281/000119312526458378/eldn-ex99_1.htm) (sec-8k): said David-Alexandre C. Gros, M.D., Chief Executive Officer of Eledon
- 支持 [ev_84269d669b6b3629](https://www.sec.gov/Archives/edgar/data/1404281/000119312526116164/eldn-20251231.htm) (primary-document): Engaged with external technical accounting experts to advise and review all equity instruments, ensuring appropriate technical analysis, documentation, and oversight prior to the preparation of our financial statements
- 反证 [ev_01d1f6ce56573754](https://www.sec.gov/Archives/edgar/data/1404281/000119312526116164/eldn-20251231.htm) (primary-document): the Company cannot provide assurances that the remediated material weakness will not reoccur, or that a new material weakness will not occur in the future
- 缺口：董事会组成、独立董事比例及审计委员会详情
- 缺口：高管薪酬结构与激励对齐情况
- 缺口：关键管理层（CFO、CMO）的任期和背景
- 证伪条件：新的重大内控缺陷被发现
- 证伪条件：CEO或关键高管突然离职
- 证伪条件：SEC执法行动或会计调查

## FATE · complete

审查记录：`state/serenity-reviews/FATE-claudecli-923174a5bdf891bf07fd.json`

### supply_chain_map: partial

证据描述了iPSC衍生CAR T细胞的三阶段制造流程（上游：供体细胞、cGMP试剂、第三方供应商；中游：公司自有iPSC平台与制造；下游：自身免疫疾病和肿瘤患者），并提及依赖唯一来源供应商，但缺乏具体供应商名称和下游付费客户/支付方的披露。

- 支持 [ev_5bf6b4e7408cf0a5](https://www.sec.gov/Archives/edgar/data/1434316/000119312526073699/fate-20251231.htm) (primary-document): The manufacture of our off-the-shelf, multiplexed-engineered, iPSC-derived CAR T-cell and CAR NK cell product candidates involves a three-stage process
- 支持 [ev_5bf6b4e7408cf0a5](https://www.sec.gov/Archives/edgar/data/1434316/000119312526073699/fate-20251231.htm) (primary-document): we obtain key components required for the manufacture of our iPSC-derived cell product candidates from third-party manufacturers and suppliers, which include, in some instances, sole source manufacturers and suppliers
- 支持 [ev_1462e68ca113df3c](https://www.sec.gov/Archives/edgar/data/1434316/000119312526073699/fate-20251231.htm) (primary-document): We rely on the general commercial availability of materials and equipment required for the manufacture of our product candidates, and do not have supply contracts with many of these suppliers
- 缺口：具体供应商名称（如试剂、设备供应商）
- 缺口：下游支付方或合作伙伴的具体披露
- 缺口：CMO名称及合同条款
- 证伪条件：发现关键供应商已停止供应或无法扩产
- 证伪条件：CMO无法满足cGMP商业化生产需求

### chokepoint_evidence: unknown

FATE是临床阶段药物开发公司，拥有iPSC平台专有技术和TSRI独家许可，但这属于知识产权壁垒而非物理供应链瓶颈。没有证据表明公司控制了某个供应集中度高、替代周期长的关键节点。

- 支持 [ev_069ee67e1dadd72d](https://www.sec.gov/Archives/edgar/data/1434316/000119312526073699/fate-20251231.htm) (primary-document): we acquired exclusive royalty-bearing, sublicensable, worldwide licenses to make, use and sell products covered by the licensed patent rights
- 缺口：供应集中度数据（如全球iPSC-CAR T供应份额）
- 缺口：替代技术的转换成本或替代周期的量化证据
- 缺口：下游客户无法绕过该节点的具体证据
- 证伪条件：多家竞争者拥有类似iPSC-CAR T平台并进入临床阶段
- 证伪条件：自体CAR-T疗法持续主导市场使异体平台边缘化

### customer_dependency: unknown

公司处于临床阶段，无商业产品，无付费客户。临床试验中有患者入组（17个活跃中心，29名自身免疫患者），但这不构成商业客户依赖证据。CIRM拨款是非商业性资助。

- 支持 [ev_eef0673db6d0b82a](https://www.sec.gov/Archives/edgar/data/1434316/000119312526448530/fate-ex99_1.htm) (sec-8k): enrollment currently open across 17 active sites. In August, the study was initiated and the first patient was treated in an outpatient setting
- 支持 [ev_80ecc8b10bfd2951](https://www.sec.gov/Archives/edgar/data/1434316/000119312526448530/fate-ex99_1.htm) (primary-document): $15.0 million CIRM CLIN2 grant awarded to support RECLAIM-LN
- 缺口：商业客户或合作伙伴的收入贡献
- 缺口：药品采购协议或预购承诺
- 缺口：支付方覆盖或报销协议
- 证伪条件：潜在合作伙伴选择竞争对手的异体CAR-T平台
- 证伪条件：临床试验入组困难导致项目延迟或终止

### pure_play: unknown

FATE完全专注于iPSC衍生的细胞免疫疗法，覆盖自身免疫疾病和肿瘤两大适应症，所有管线（FT819、FT839、FT836）均基于同一iPSC平台。公司是纯粹的细胞治疗公司，无其他业务线稀释主题暴露。

- 支持 [ev_eef0673db6d0b82a](https://www.sec.gov/Archives/edgar/data/1434316/000119312526448530/fate-ex99_1.htm) (sec-8k): a clinical-stage biopharmaceutical company dedicated to bringing a transformative and broadly accessible pipeline of induced pluripotent stem cell (iPSC)-derived cellular immunotherapies to patients with cancer and autoimmune disease
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：公司进入与iPSC细胞治疗无关的业务领域
- 证伪条件：收购非核心业务导致主题暴露稀释

### multi_node_control: unknown

公司控制从iPSC克隆主细胞库生成（上游节点）到CAR T细胞产品制造和分化（中游节点）的垂直整合流程，并拥有专有基因编辑技术。但关键试剂和设备依赖第三方唯一来源供应商，且无商业产品证明节点控制的市场效力。

- 支持 [ev_5bf6b4e7408cf0a5](https://www.sec.gov/Archives/edgar/data/1434316/000119312526073699/fate-20251231.htm) (primary-document): isolation and selection of a single iPSC, followed by clonal expansion of the single iPSC to produce a clonal master iPSC line for cell product manufacture
- 支持 [ev_dde4c45ac95a71ca](https://www.sec.gov/Archives/edgar/data/1434316/000119312526448530/fate-ex99_1.htm) (primary-document): Analogous to master cell banks used to mass produce biopharmaceutical drug products such as monoclonal antibodies, a precisely engineered clonal master induced pluripotent stem cell (iPSC) bank serves as the starting cell source to manufacture FT819
- 反证 [ev_1462e68ca113df3c](https://www.sec.gov/Archives/edgar/data/1434316/000119312526073699/fate-20251231.htm) (primary-document): we may be limited to a sole third-party for the supply of certain required components and equipment
- 缺口：对上游关键试剂供应的自主控制能力
- 缺口：商业规模制造能力的验证
- 缺口：相对竞争者的节点控制优势量化
- 缺口：引用不存在或原文无法匹配
- 证伪条件：关键唯一来源供应商中断供应
- 证伪条件：竞争者开发出同等或更优的iPSC平台实现垂直整合

### earnings_validation: partial

临床阶段公司，无商业收入符合预期。Q3 2026净亏损$30.7M，现金$139.1M，加上$15M CIRM拨款，管理层表示现金跑道延伸至2028年中（约20个月）。运营费用同比下降，显示支出纪律。跑道超过12个月（smallCapContext显示15.2个月），足以资助下一里程碑（RECLAIM-LN Phase 2）。但无收入验证且依赖现有现金消耗速率保持稳定。

- 支持 [ev_eef0673db6d0b82a](https://www.sec.gov/Archives/edgar/data/1434316/000119312526448530/fate-ex99_1.htm) (sec-8k): $139.1 million in cash, cash equivalents, and investments; cash runway expected to mid-2028
- 支持 [ev_80ecc8b10bfd2951](https://www.sec.gov/Archives/edgar/data/1434316/000119312526448530/fate-ex99_1.htm) (primary-document): Total operating expenses for the nine months ended September 30, 2026, decreased by $18.5 million compared to the same period in 2025
- 支持 [ev_704a6b5314a01889](https://www.sec.gov/Archives/edgar/data/1434316/000119312526073699/fate-20251231.htm) (primary-document): The Company determined that there are no conditions or events that raise substantial doubt about its ability to continue as a going concern for a period of at least twelve months from the date of issuance of these financial statements
- 支持 [ev_dde4c45ac95a71ca](https://www.sec.gov/Archives/edgar/data/1434316/000119312526448530/fate-ex99_1.htm) (primary-document): Cash, cash equivalents, and investments of $139.1 million, along with the newly awarded $15.0 million CIRM grant, extends the cash runway to mid-2028
- 反证 [ev_85f31165fbfd30d1](https://data.sec.gov/api/xbrl/companyfacts/CIK0001434316.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 0 for 2026-07-01 to 2026-09-30
- 缺口：Phase 2试验完成时间表与现金跑道的匹配分析
- 缺口：若需额外融资的具体计划
- 证伪条件：现金消耗速率大幅上升导致跑道缩短至12个月以下
- 证伪条件：CIRM拨款未按预期到账
- 证伪条件：临床试验成本超出预算

### counter_thesis: partial

反面论点需要审视：(1) 供应端：依赖唯一来源供应商且无长期合同；(2) 需求端：无商业产品，自身免疫CAR-T尚未被广泛接受；(3) 替代：自体CAR-T已获批且有安全性警告（FDA黑框警告T细胞恶性肿瘤），竞争者众多；(4) 临床风险：Phase 2数据仅2例肾脏应答患者，样本极小；(5) 估值：$128M市值对应无收入公司。跑道15.2个月且financingRisk为false，短期内无强制融资稀释风险。但缺乏对具体竞争对手管线进展的系统比较。

- 支持 [ev_e94c73d515713755](https://www.sec.gov/Archives/edgar/data/1434316/000119312526073699/fate-20251231.htm) (primary-document): The use of cellular immunotherapies for the potential treatment of autoimmune diseases is a recent development, and may not become widely accepted by patients, physicians, treatment centers, and third-party payors
- 支持 [ev_e94c73d515713755](https://www.sec.gov/Archives/edgar/data/1434316/000119312526073699/fate-20251231.htm) (primary-document): in January 2024, the FDA determined that new safety information related to T-cell malignancies should be included in the labeling with boxed warning language on these malignancies for all BCMA- and CD19-directed genetically modified autologous T-cell immunotherapies
- 支持 [ev_1462e68ca113df3c](https://www.sec.gov/Archives/edgar/data/1434316/000119312526073699/fate-20251231.htm) (primary-document): do not have supply contracts with many of these suppliers and may not be able to obtain supply contracts with them on acceptable terms or at all
- 支持 [ev_0b6cddb8cbdc139a](https://www.sec.gov/Archives/edgar/data/1434316/000119312526448530/fate-ex99_1.htm) (primary-document): patients with Month 6 follow-up (n=2) achieved a CRR or primary efficacy renal response (PERR)
- 缺口：具体竞争对手异体CAR-T管线的对比分析（如Allogene、CRISPR Therapeutics等）
- 缺口：自体CAR-T疗法在自身免疫适应症的竞争数据
- 缺口：地缘政治或监管变化对细胞治疗行业的影响评估
- 证伪条件：RECLAIM-LN Phase 2未达主要终点（CRR at Week 26）
- 证伪条件：竞争者的异体或自体CAR-T在自身免疫适应症获批
- 证伪条件：FDA对iPSC衍生细胞疗法施加额外监管要求
- 证伪条件：关键专利被无效化或TSRI许可终止
- 证伪条件：现金跑道不足以完成Phase 2导致强制融资稀释

### management_governance: partial

CEO Bob Valamehr在任并领导公司战略执行，新任商业负责人Jamie Harrell加入扩展领导团队。内部控制截至2025年12月31日有效。但证据中无董事会构成、独立性、关键人员风险的详细披露，且公司为较小报告公司（smaller reporting company），审计师无需对内部控制出具鉴证报告。

- 支持 [ev_d9ea3d5d12a6892e](https://www.sec.gov/Archives/edgar/data/1434316/000119312526073699/fate-20251231.htm) (primary-document): Based on this assessment, our management concluded that, as of December 31, 2025, our internal control over financial reporting was effective based on those criteria
- 支持 [ev_80ecc8b10bfd2951](https://www.sec.gov/Archives/edgar/data/1434316/000119312526448530/fate-ex99_1.htm) (primary-document): The Company appointed Jamie Harrell to its executive leadership team in a newly created role leading commercial and market development strategy across its autoimmunity and oncology programs
- 支持 [ev_eef0673db6d0b82a](https://www.sec.gov/Archives/edgar/data/1434316/000119312526448530/fate-ex99_1.htm) (sec-8k): said Bob Valamehr, Ph.D., MBA, President and Chief Executive Officer of Fate Therapeutics
- 支持 [ev_d9ea3d5d12a6892e](https://www.sec.gov/Archives/edgar/data/1434316/000119312526073699/fate-20251231.htm) (primary-document): We have adopted a written code of business conduct and ethics that applies to our directors, officers and employees
- 反证 [ev_d9ea3d5d12a6892e](https://www.sec.gov/Archives/edgar/data/1434316/000119312526073699/fate-20251231.htm) (primary-document): Our auditors will not be required to opine on the effectiveness of our internal control over financial reporting pursuant to Section 404(b) of the Sarbanes-Oxley Act of 2002 as the Company is classified as a smaller reporting company
- 缺口：董事会独立性和构成详情
- 缺口：关键人员依赖风险及继任计划
- 缺口：高管薪酬与公司业绩的关联分析
- 证伪条件：发现财务报告重大缺陷
- 证伪条件：关键高管突然离职无继任安排
- 证伪条件：监管调查或治理丑闻

## FRNM · complete

审查记录：`state/serenity-reviews/FRNM-claudecli-f9ce1d896302364d26e9.json`

### supply_chain_map: partial

可以识别公司产品（SimpleScreen CRC/Lung血液检测）和下游用户（Abbott独家商业化、Exact Sciences和Roche合作），但上游具体供应商（试剂、测序设备、实验室自动化组件）在证据中未披露，无法完整绘制供应链。

- 支持 [ev_75233e5f38839fa9](https://www.sec.gov/Archives/edgar/data/2017526/000114036126033585/ny20080283x1_s1.htm) (primary-document): Abbott will exclusively commercialize SimpleScreen CRC in the U.S. pursuant to the commercial agreement entered into between Freenome and Abbott in August 2025
- 支持 [ev_09d9c3e7ae94f22f](https://www.sec.gov/Archives/edgar/data/2017526/000114036126033585/ny20080283x1_s1.htm) (primary-document): We believe our partnerships with Exact Sciences and Roche will expand our dataset, expand our potential commercial reach, bolster our research and development efforts
- 支持 [ev_aba1363092a65d6b](https://www.sec.gov/Archives/edgar/data/2017526/000114036126033585/ny20080283x1_s1.htm) (primary-document): Our common platform is designed to evaluate and integrate multiple analytes (e.g., DNA, RNA and proteins) with differentiated wet lab automation capabilities
- 缺口：上游试剂、测序平台和实验室设备的具体供应商名称
- 缺口：关键原材料的供应集中度和替代性数据
- 缺口：生产SimpleScreen检测所需的完整BOM
- 证伪条件：如果上游检测试剂或测序平台完全依赖单一供应商（如Illumina），则存在未披露的供应链风险

### chokepoint_evidence: unknown

Freenome是一家液体活检诊断公司，不是半导体/光子供应链中的瓶颈节点。虽然其multiomics平台和$1B+投资构成壁垒，但证据中没有供应集中度或替代障碍的具体数据。竞争对手（Guardant Shield、Grail/Galleri）存在，不符合寡头垄断特征。

- 支持 [ev_09d9c3e7ae94f22f](https://www.sec.gov/Archives/edgar/data/2017526/000114036126033585/ny20080283x1_s1.htm) (primary-document): The technology backbone of Freenome is underpinned by more than a decade of development and engineering, robust intellectual property, algorithms and more than $1 billion of invested capital
- 缺口：Freenome在液体活检CRC筛查市场的市场份额数据
- 缺口：与Guardant Shield、Grail等竞品的直接比较
- 缺口：替代检测技术的转换成本或锁定效应证据
- 证伪条件：如果多家竞争对手获得CRC血液筛查FDA批准，则Freenome不具备chokepoint地位
- 证伪条件：如果大型诊断公司（Roche、Abbott）可自研类似技术，则平台替代性较高

### customer_dependency: partial

Abbott独家商业化SimpleScreen CRC已通过SEC披露确认；Exact Sciences有许可协议含预付款、里程碑付款和可转换票据；Roche有许可及期权协议并持有转换后股份。三大战略合作伙伴均有明确的合同关系和资金流。

- 支持 [ev_75233e5f38839fa9](https://www.sec.gov/Archives/edgar/data/2017526/000114036126033585/ny20080283x1_s1.htm) (primary-document): Abbott will exclusively commercialize SimpleScreen CRC in the U.S. pursuant to the commercial agreement entered into between Freenome and Abbott in August 2025
- 支持 [ev_df75d64fdc37512a](https://www.sec.gov/Archives/edgar/data/2017526/000201752626000027/frnm-20260930.htm) (primary-document): ExactScienceLicenseAgreementUpfrontPaymentsMember frnm:LicenseAndCollaborationMember 2025-11-03
- 支持 [ev_8354785f87378289](https://www.sec.gov/Archives/edgar/data/2017526/000114036126033585/ny20080283x1_s1.htm) (primary-document): 6,460,616 shares of Common Stock issued to Roche (as defined below) pursuant to conversion of the Roche Convertible Note
- 缺口：Abbott商业化后的实际检测量或销售额数据
- 缺口：终端患者/医疗系统的实际采用率
- 缺口：通过需要直接相关的原始披露及完整证据
- 证伪条件：如果Abbott商业化进展缓慢或终止协议，则收入预期将大幅下降
- 证伪条件：如果Exact Sciences选择不行使后续里程碑条款

### pure_play: pass

Freenome专注于基于血液的AI/ML早期癌症检测，所有收入来源（许可合作、诊断服务、EarlyCDT Lung试剂盒/板/版税）均围绕这一主题。没有非相关业务分散主题敞口。

- 支持 [ev_aba1363092a65d6b](https://www.sec.gov/Archives/edgar/data/2017526/000114036126033585/ny20080283x1_s1.htm) (primary-document): We are an early cancer detection company developing blood-based tests leveraging AI/ML to transform multi-cancer and ultimately multi-disease detection
- 支持 [ev_09d9c3e7ae94f22f](https://www.sec.gov/Archives/edgar/data/2017526/000114036126033585/ny20080283x1_s1.htm) (primary-document): We are pursuing multi-product commercialization supported by a robust data moat that we believe supports rapid test development
- 支持 [ev_eae38a593cffbee0](https://www.sec.gov/Archives/edgar/data/2017526/000201752626000027/frnm-20260930.htm) (primary-document): frnm:DiagnosticAndResearchServicesMember 2026-07-01 2026-09-30
- 证伪条件：如果公司大规模进入非诊断领域（如治疗药物开发），则纯度降低

### multi_node_control: partial

Freenome拥有multiomics发现平台（上游研发节点）和多个检测产品（CRC、Lung），且有自有湿实验室自动化能力，但这更像是垂直整合的单一节点（检测开发+生产），而非控制两个相连的供应链节点。商业化节点已交给Abbott。

- 支持 [ev_aba1363092a65d6b](https://www.sec.gov/Archives/edgar/data/2017526/000114036126033585/ny20080283x1_s1.htm) (primary-document): Our common platform is designed to evaluate and integrate multiple analytes (e.g., DNA, RNA and proteins) with differentiated wet lab automation capabilities
- 支持 [ev_4ae39ebf012a2d90](https://www.sec.gov/Archives/edgar/data/2017526/000114036126040186/ef20084075_8k.htm) (primary-document): the Company announced the launch of SimpleScreen™ Lung and a first-of-its-kind offering that enables eligible patients to be screened for both lung and colorectal cancer
- 反证 [ev_75233e5f38839fa9](https://www.sec.gov/Archives/edgar/data/2017526/000114036126033585/ny20080283x1_s1.htm) (primary-document): Abbott will exclusively commercialize SimpleScreen CRC in the U.S. pursuant to the commercial agreement
- 缺口：Freenome是否自有测序或样本处理能力的证据
- 缺口：平台技术能否独立于外部测序供应商运行的信息
- 证伪条件：如果关键实验室流程依赖第三方外包，则multi-node控制更弱

### earnings_validation: partial

Q3 2026收入$183.5M、净利润$60.1M看似强劲，但同比从$1M暴增17628%，主要来自Exact Sciences许可协议确认收入（LicenseAndCollaboration），而非经常性商业检测收入。YTD经营现金流为-$58.7M，说明核心业务仍在烧钱。收入结构尚不能持续验证商业化论点。

- 支持 [ev_388b16a6075a68b3](https://data.sec.gov/api/xbrl/companyfacts/CIK0002017526.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 183,489,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_388b16a6075a68b3](https://data.sec.gov/api/xbrl/companyfacts/CIK0002017526.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 60,110,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-12
- 反证 [ev_388b16a6075a68b3](https://data.sec.gov/api/xbrl/companyfacts/CIK0002017526.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 1,035,000, a change of +17628.4%
- 反证 [ev_388b16a6075a68b3](https://data.sec.gov/api/xbrl/companyfacts/CIK0002017526.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -58,696,000 for 2026-01-01 to 2026-09-30
- 缺口：许可收入与经常性检测收入的具体拆分
- 缺口：SimpleScreen CRC商业化后的实际检测量
- 缺口：下一季度收入是否可持续在此水平的指引
- 证伪条件：如果Q3收入主要为一次性许可确认（cumulative catch-up），Q4收入可能大幅回落
- 证伪条件：经营现金流持续为负表明盈利能力尚未建立

### counter_thesis: partial

反面论点已从多个角度审视：竞争替代（液体活检市场多家竞争者）、收入质量（许可确认vs经常性收入）、现金消耗（YTD -$58.7M运营现金流、$180M现金）、SPAC来源（稀释风险、Selling Securityholders S-1登记）、商业化依赖Abbott单一渠道、以及FDA后续监管风险。风险已识别但未消失。

- 支持 [ev_388b16a6075a68b3](https://data.sec.gov/api/xbrl/companyfacts/CIK0002017526.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 180,379,000 for as of 2026-09-30
- 支持 [ev_388b16a6075a68b3](https://data.sec.gov/api/xbrl/companyfacts/CIK0002017526.json) (sec-companyfacts): R&D expense (ResearchAndDevelopmentExpense): 68,417,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-12
- 支持 [ev_8354785f87378289](https://www.sec.gov/Archives/edgar/data/2017526/000114036126033585/ny20080283x1_s1.htm) (primary-document): We will not receive any proceeds from the sale of shares of common stock by the Selling Securityholders pursuant to this prospectus
- 反证 [ev_789e779171a56513](https://www.sec.gov/Archives/edgar/data/2017526/000114036126040186/ef20084075_8k.htm) (primary-document): ability to negotiate definitive contractual arrangements with potential customers; the impact of competitive products and tests; ability to obtain sufficient supply of materials
- 反证 [ev_388b16a6075a68b3](https://data.sec.gov/api/xbrl/companyfacts/CIK0002017526.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -58,696,000 for 2026-01-01 to 2026-09-30
- 缺口：Guardant Shield和Grail等竞品的CRC筛查性能直接对比
- 缺口：保险报销覆盖率和定价压力的具体数据
- 缺口：通过需要直接相关的原始披露及完整证据
- 证伪条件：如果竞争对手获得CRC血液筛查FDA批准且性能更优，SimpleScreen CRC市场份额将受到严重威胁
- 证伪条件：S-1中Selling Securityholders大量抛售可能造成持续的股价压力
- 证伪条件：如果Abbott商业化不力或终止协议，Freenome缺乏自有销售渠道
- 证伪条件：R&D季度支出$68M但现金仅$180M，若无新融资或收入增长，现金跑道有限

### management_governance: unknown

CEO Aaron Elliott在多份SEC文件中签名确认（8-K、10-Q），公司通过SPAC合并于2026年7月20日上市，属于新兴成长型公司。但证据中缺乏董事会构成、独立董事比例、管理层任期和背景等详细治理信息。SPAC来源增加了治理审查的必要性。

- 支持 [ev_789e779171a56513](https://www.sec.gov/Archives/edgar/data/2017526/000114036126040186/ef20084075_8k.htm) (primary-document): By: /s/ Aaron Elliott Name: Aaron Elliott Title: Chief Executive Officer Date: October 20, 2026
- 缺口：董事会成员名单和独立董事比例
- 缺口：CEO及高管团队的详细背景和任期
- 缺口：SPAC合并后的治理结构变化细节
- 缺口：是否存在未决诉讼或监管调查
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：如果存在重大未披露的关联方交易或治理缺陷
- 证伪条件：如果新兴成长型公司的减免报告要求掩盖了治理问题

## GEHC · complete

审查记录：`state/serenity-reviews/GEHC-claude-27f3ea175dba2473b121.json`

### supply_chain_map: partial

有多个尚无替代的单一来源供应商，部分分子影像药物依赖合同生产；文件未点名具体供应商。

- 支持 [ev_a5fc148eb08e8e25](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): we have multiple single-source or sole-source suppliers with no alternatives yet identified
- 支持 [ev_eaa0936475660d67](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): we rely on contract manufacturing organizations to produce certain of our molecular imaging pharmaceutical products
- 缺口：具体单一来源供应商名称

### chokepoint_evidence: partial

FDA 在 K261623 中一并许可了预定变更控制计划（PCCP），AI 模型后续更新无需每次重新申报，这是运营上的优势；但本次许可的对比器械是其自身上一版本（实质等同，增量更新），且影像设备市场有西门子、飞利浦、联影、迈瑞、佳能等多家竞争，不构成瓶颈。

- 支持 [ev_934cbee4282fe414](https://www.accessdata.fda.gov/cdrh_docs/pdf26/K261623.pdf) (primary-document): FDA's substantial equivalence determination also included the review and clearance of your Predetermined Change Control Plan (PCCP)
- 反证 [ev_8ab12ae5fd924639](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): we believe our primary global competitors include Siemens Healthineers, Philips Healthcare, United Imaging, Mindray, and Canon
- 反证 [ev_00528b59502bc0a9](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K261623) (primary-document): Decision Substantially Equivalent (SESE)
- 缺口：装机份额数据

### customer_dependency: pass

2023–2025 年没有任何单一客户收入占比超过 10%。

- 支持 [ev_ece1631c99c6d50e](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): No single customer accounted for more than 10% of the Company’s revenues for the years ended December 31, 2025, 2024, or 2023.

### pure_play: partial

AI 是影像设备和软件上的功能（如 EchoPAC 的 AI 多普勒周期检测模型）；另有 29 亿美元的药物诊断业务与 AI 无关。

- 支持 [ev_f10be1161de47dd4](https://www.accessdata.fda.gov/cdrh_docs/pdf26/K261623.pdf) (primary-document): through an AI Doppler Spectrum Cycle Detection model
- 反证 [ev_3e64d25ed2062c00](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): Total PDx 2,900 2,508 2,306
- 缺口：AI 或软件收入占比

### multi_node_control: pass

同时覆盖影像硬件、影像软件与工作流（收购 Intelerad）以及 PET 放射性药物生产（拟收购 SOFIE）。

- 支持 [ev_c302150040211d1a](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000059/gehc-20260930.htm) (primary-document): Intelerad is a leading medical imaging software and digital enterprise workflow solutions company
- 支持 [ev_eabe36c8c84d3cee](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000059/gehc-20260930.htm) (primary-document): we announced an agreement to acquire SOFIE Biosciences, a U.S.-based contract manufacturing organization for positron emission tomography

### earnings_validation: pass

2025 年收入 206 亿美元（2024 年 197 亿），自由现金流 15 亿美元；增长温和，约 5%。

- 支持 [ev_32d8819288c41a73](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): Total revenues $ 20,625 $ 19,672 $ 19,552
- 支持 [ev_59393a7e3fa61213](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): Free cash flow* $ 1,505 $ 1,554

### counter_thesis: pass

已检验：95 亿美元优先票据、GE 合并报税期间可能的 IRS 追税、中国市场与关税；FDA 摘要显示本次许可为自身上一版本的增量更新。

- 支持 [ev_c1f56fb451ce85f5](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): We have historically generated positive cash flows from operating activities.
- 反证 [ev_96fefcf66b850fda](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000059/gehc-20260930.htm) (primary-document): $ 9,500 million aggregate principal amount of senior unsecured notes
- 反证 [ev_8bbf3f796ed5c7d2](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000059/gehc-20260930.htm) (primary-document): may assert a material amount of additional taxes and penalties
- 反证 [ev_54e7cb99ab6a3923](https://www.accessdata.fda.gov/cdrh_docs/pdf26/K261623.pdf) (primary-document): have identical clinical indications for use
- 证伪条件：有机收入增长连续两个季度低于 3%
- 证伪条件：中国采购持续下滑
- 证伪条件：AI 和软件收入长期不单独披露、无法验证增长

### management_governance: partial

患者护理解决方案部门总裁兼CEO（事业部负责人）已辞职，属于事业部级别离职，严重性低于公司CEO/CFO；首席科学与技术官仍主导AI影像战略；但与GE分拆的应税风险赔偿敞口尚未解除，整体治理延续性仍存疑。

- 支持 [ev_4aa8116dd0668411](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): he is driving advancements in AI-based medical imaging, diagnostics, and health system operational efficiency
- 反证 [ev_6a0d1f6bae27477a](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): If the Spin-Off is determined to be a taxable transaction, it could result in significant tax liability to GE and its stockholders
- 反证 [ev_209ca8051864ea86](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000058/gehc-20261022.htm) (primary-document): On October 22, 2026, Jeannette Bankes notified GE HealthCare that she will resign as President and CEO, Patient Care Solutions. Ms. Bankes' last day at GE HealthCare will be November 15, 2026.
- 缺口：Successor for Bankes' Patient Care Solutions role not announced in the 8-K
- 缺口：No update on GE spin-off tax indemnification resolution in the available passages
- 证伪条件：Company-level CEO or CFO departure without named successor would push status to pending
- 证伪条件：Resolution of the GE spin-off tax indemnification exposure would remove the primary counter and support upgrade to pass

## GENB · complete

审查记录：`state/serenity-reviews/GENB-claudecli-1ed42091cce2da995903.json`

### supply_chain_map: unknown

证据表明GENB是AI驱动的药物发现公司，下游合作伙伴包括Amgen、Novartis和Zealand（2026年10月新签），还有学术合作伙伴Roswell Park和MD Anderson。上游输入（计算基础设施、生物数据、临床前资源）在证据中未具体描述。XBRL标签确认了合作关系的存在，但缺少详细的供应链物理流描述。

- 支持 [ev_1a87c99978cd0ce4](https://www.sec.gov/Archives/edgar/data/2100782/000119312526456890/ck0002100782-20260930.htm) (primary-document): ck0002100782:AmgenCollaborationAgreementMember 2025-07-01 2025-09-30
- 支持 [ev_1a87c99978cd0ce4](https://www.sec.gov/Archives/edgar/data/2100782/000119312526456890/ck0002100782-20260930.htm) (primary-document): us-gaap:SubsequentEventMember ck0002100782:CollaborationAndLicenseAgreementWithZealandMember 2026-10-08
- 支持 [ev_6dd2f326b197c983](https://www.sec.gov/Archives/edgar/data/2100782/000119312526456890/ck0002100782-20260930.htm) (primary-document): ck0002100782:AgreementWithRoswellParkComprehensiveCancerCenterMember 2026-01-01 2026-09-30
- 支持 [ev_7aeb26103a78583d](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Generate Biomedicines, Inc.
- 缺口：上游输入的具体描述（计算平台、训练数据来源、CRO/CDMO服务商）
- 缺口：各合作协议的具体内容和交易条款
- 缺口：公司产品管线的详细技术路线描述
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现公司实际上是CRO/平台型而非药物发现型，供应链结构完全不同

### chokepoint_evidence: unknown

证据中没有任何关于供应集中度或替代壁垒的具体数据。AI药物发现领域竞争激烈（Recursion、Absci、Relay等），GENB未展示出在关键物理输入节点上的垄断或寡头控制地位。仅凭AI相关性不足以构成瓶颈证据。

- 缺口：公司在特定技术或物理输入上的市场份额数据
- 缺口：替代供应商分析及替代成本/时间
- 缺口：专利或独占许可等构成壁垒的证据
- 证伪条件：发现多家竞争对手拥有相同或类似的AI药物发现能力
- 证伪条件：合作伙伴（Amgen、Novartis）同时与其他AI药物发现公司签约

### customer_dependency: partial

XBRL数据确认存在Amgen合作协议（始于2022-2023年）、Novartis合作协议（2024年9月）以及Zealand合作许可协议（2026年10月后续事件）。Q3 2026收入为422万美元，但同比下降56.2%，表明客户依赖存在但在减弱。缺少具体客户采用规模、续约条款和收入构成细分。

- 支持 [ev_7aeb26103a78583d](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 4,220,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_4dc5a34758f98d3c](https://www.sec.gov/Archives/edgar/data/2100782/000119312526456890/ck0002100782-20260930.htm) (primary-document): ck0002100782:AmgenCollaborationAgreementMember 2026-01-01 2026-09-30
- 支持 [ev_d920d0de886b3d52](https://www.sec.gov/Archives/edgar/data/2100782/000119312526456890/ck0002100782-20260930.htm) (primary-document): ck0002100782:ZealandCollaborationMember us-gaap:SubsequentEventMember 2026-10-01 2026-10-31
- 支持 [ev_6dd2f326b197c983](https://www.sec.gov/Archives/edgar/data/2100782/000119312526456890/ck0002100782-20260930.htm) (primary-document): ck0002100782:NovartisCollaborationAgreementMember 2024-09-19 2024-09-19
- 反证 [ev_7aeb26103a78583d](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 9,634,000, a change of -56.2%
- 缺口：各合作协议的具体里程碑付款和特许权使用费条款
- 缺口：收入按客户细分的明细
- 缺口：合作协议的剩余交易价格和未确认收入
- 证伪条件：Amgen或Novartis终止合作协议
- 证伪条件：收入持续快速下降表明合作关系未产生持续价值

### pure_play: partial

GENB主要专注于AI驱动的生成式药物发现，收入来自合作协议。有子公司Cellarity（细胞治疗相关），也涉及肿瘤和哮喘等多个治疗领域。公司看起来较为纯粹聚焦于AI药物发现，但缺乏按业务线的收入分部数据来量化主题敞口。

- 支持 [ev_7aeb26103a78583d](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): R&D expense (ResearchAndDevelopmentExpense): 82,254,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_7ab5b4e24196801c](https://news.google.com/rss/articles/CBMi5gFBVV95cUxNRVkzLWcyR2RKWGhRSGJFY1o0TXE5X2tYa1hMUXZkY3c1ai02UUlVV2NtTVFLUThTNnJxN1ZjVFFXUk5ia0VYelJlZWt2eGd0aExyTWNUVXRyV2o2TmQxMWdSeHQtYmRWZDhlT3kyMmxydFhneWdYQlF4X3kzeG53X3FYVEJOMVpxODJTZ2JROFVnS1lLd2l6Y2gzTVdsZnlnU3MxajlxVV92enV4SFZTMGJqNEJtS2JTc0FpU2tJN181ZUtfYmFkbWpTZFd0NDB3ZWpOQjU3SkFIMmZBTFl2M0dQTnd6dw?oc=5) (news-feed): Generate Biomedicines Reports Third-Quarter 2026 Results, Advances GB-0895, Oncology Pipeline and New Partnerships
- 反证 [ev_6dd2f326b197c983](https://www.sec.gov/Archives/edgar/data/2100782/000119312526456890/ck0002100782-20260930.htm) (primary-document): ck0002100782:CellarityMember srt:MaximumMember 2025-01-01 2025-09-30
- 缺口：按业务分部或治疗领域的收入细分
- 缺口：AI药物发现平台收入与传统药物开发收入的比例
- 缺口：Cellarity子公司的业务范围和财务贡献
- 证伪条件：发现大部分收入来自非AI相关的传统药物开发服务

### multi_node_control: unknown

证据中未显示GENB控制两个或以上相连的供应链节点。公司主要是AI药物发现平台，合作模式为与大型药企共同开发。没有垂直整合（如同时控制AI计算基础设施和临床开发CRO能力）的证据。

- 缺口：公司是否拥有自主的计算基础设施
- 缺口：是否有内部临床开发或生产能力
- 缺口：供应链垂直整合程度的描述
- 证伪条件：发现公司依赖第三方完成供应链中的所有其他节点

### earnings_validation: partial

有实际财务数据：Q3 2026收入422万美元（同比-56.2%），净亏损8766万美元，研发费用8225万美元，前9个月经营现金流-1.93亿美元，现金仅1.4亿美元。按季度烧钱速度约6400万美元计算，现金跑道仅约6-7个月，非常紧张。非主要来源新闻称cash lasting into 2028，暗示可能有其他流动资产（可交易证券、定期存款），但主要证据中缺乏该数据。收入大幅下降与高烧钱率是重大风险信号。

- 支持 [ev_7aeb26103a78583d](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 4,220,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_7aeb26103a78583d](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -87,657,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_7aeb26103a78583d](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 140,350,000 for as of 2026-09-30
- 支持 [ev_7aeb26103a78583d](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -193,189,000 for 2026-01-01 to 2026-09-30
- 反证 [ev_7aeb26103a78583d](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 9,634,000, a change of -56.2%
- 缺口：可交易证券和定期存款的总额（XBRL标签中出现但无金额）
- 缺口：完整的资产负债表以计算总流动资产和实际跑道
- 缺口：管理层对未来融资计划的指引
- 证伪条件：总流动资产（含可交易证券）实际远高于现金余额，跑道充足
- 证伪条件：新合作协议（如Zealand）带来大额预付款改善现金状况

### counter_thesis: partial

已识别多项关键风险：(1)现金仅1.4亿美元，季度烧钱约6400万，跑道紧张，可能需要稀释性融资；(2)收入同比下降56%，合作收入不稳定；(3)AI药物发现领域竞争激烈；(4)研发费用高达季度8200万美元但无已批准产品。但缺乏对地缘政治风险、替代技术路线和估值合理性的系统性反驳材料。

- 支持 [ev_7aeb26103a78583d](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): R&D expense (ResearchAndDevelopmentExpense): 82,254,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_7aeb26103a78583d](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 140,350,000 for as of 2026-09-30
- 支持 [ev_158a72c135f20cf1](https://news.google.com/rss/articles/CBMi0gFBVV95cUxNdDhVMHRHTmx4UGJKc0l4NkJJNS1qR3gzcEcySkhQSV9tV3Y1RFpwb0lUc3pJQlF6UFpXbU9ibmJyaWI1elpoSkoxMGpNdWo4dXRTbmxUaVJNVl9VYzE3bG9Pc0hEU3lZLVNDV2dnc3BhNW5QQXJUZWFZaFg1aHZrSTdDNEpnRkFlTmROZmJzdHlwOEgyc25OaFBKZjZyQ2JxNjhRcC1JUF9feHBlb0JibUFYSWc2WDFCeElTZXdfY01kd18xM2sxS282QVBGRlRpa1E?oc=5) (news-feed): Generate Biomedicines' quarterly loss widens to $88 million as Phase 3 asthma trials ramp, with cash lasting into 2028
- 反证 [ev_7aeb26103a78583d](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 9,634,000, a change of -56.2%
- 缺口：竞争对手对比分析（Recursion、Absci、Relay等）
- 缺口：AI药物发现技术的可替代性分析
- 缺口：估值合理性论证（$1.56B市值 vs 年化收入不足2000万）
- 缺口：Phase 3试验失败概率及对公司价值的影响
- 证伪条件：Phase 3哮喘试验失败导致管线价值归零
- 证伪条件：现金跑道不足迫使在不利条件下融资，严重稀释股东
- 证伪条件：Amgen或Novartis终止合作导致收入进一步下降
- 证伪条件：竞争对手率先获批同类AI发现药物，削弱平台价值

### management_governance: partial

8-K由Jason Silvers签署，职位为总裁兼首席财务官，显示其同时担任两个高管职位，这在小型生物科技公司中常见但也表明管理层厚度有限。公司2026年3月IPO上市，由Flagship Pioneering孵化（关联方交易存在）。缺乏董事会构成、CEO信息、独立董事比例和管理层稳定性的详细证据。

- 支持 [ev_ab81afdb10dc8da7](https://www.sec.gov/Archives/edgar/data/2100782/000119312526456921/ck0002100782-20261112.htm) (primary-document): By: /s/ Jason Silvers Jason Silvers, President and Chief Financial Officer
- 支持 [ev_71c60a51aaf05937](https://www.sec.gov/Archives/edgar/data/2100782/000119312526456890/ck0002100782-20260930.htm) (primary-document): Non-accelerated filer ☒ Smaller reporting company ☒ Emerging growth company ☒
- 支持 [ev_6dd2f326b197c983](https://www.sec.gov/Archives/edgar/data/2100782/000119312526456890/ck0002100782-20260930.htm) (primary-document): us-gaap:RelatedPartyMember ck0002100782:FlagshipPioneeringMember 2025-12-31
- 缺口：CEO身份和背景信息
- 缺口：董事会构成和独立董事比例
- 缺口：高管团队完整名单和任期
- 缺口：与Flagship Pioneering关联交易的具体金额和条款
- 证伪条件：发现管理层近期大量离职或公司治理评级低
- 证伪条件：关联方交易存在利益冲突损害少数股东利益

## GH · complete

审查记录：`state/serenity-reviews/GH-claude-3588ae11347d1297dd98.json`

### supply_chain_map: partial

证据显示上游依赖Illumina独家测序仪和试剂供应，下游客户涵盖临床医生、生物制药公司和国际实验室合作伙伴，但各节点之间的具体商业关系和物流流程未完整呈现；单一实验室设施构成供应链集中风险。

- 支持 [ev_73eacf9bd68b87c3](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000013/gh-20251231.htm) (primary-document): We rely on a limited number of suppliers or, in some cases, sole suppliers, including Illumina Inc., or Illumina, for certain sequencers, reagents, blood tubes and other equipment
- 支持 [ev_00a853a6fe15467f](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000013/gh-20251231.htm) (primary-document): We currently derive the majority of our revenue from tests performed at a single laboratory facility located in Redwood City, California
- 支持 [ev_b3856b78ca3a64f6](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000044/gh-20260930.htm) (primary-document): A significant customer is any biopharmaceutical customer, clinical testing payer, or international laboratory partner that represents 10% or more of the Company’s total revenue
- 缺口：上游原材料到测序仪的完整物料清单
- 缺口：各下游客户群体的收入拆分比例
- 缺口：国际分销合作伙伴的具体名称
- 证伪条件：披露Illumina替代供应商的资质认证时间表
- 证伪条件：新建第二实验室设施的公告

### chokepoint_evidence: unknown

证据仅显示GH依赖Illumina作为独家测序仪供应商，说明GH处于一个瓶颈节点的下游，而非自身控制瓶颈节点；专利组合处于多项挑战之中，不能构成可靠的替代壁垒；没有任何证据表明GH在其所在供应链中拥有高度集中的供应控制力。

- 反证 [ev_6d14fba502e30c82](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000013/gh-20251231.htm) (primary-document): We rely on Illumina as the sole supplier of the sequencers and as the sole provider of maintenance and repair services for these sequencers
- 反证 [ev_a9e79848eb284e9d](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000013/gh-20251231.htm) (primary-document): Some of such patent rights are being challenged, including at the United States Patent and Trademark Office, or USPTO, in post-grant proceedings, at the European Patent Office, or EPO, in opposition proceedings
- 缺口：GH在液体活检检测市场的全球市占率数据
- 缺口：竞争对手替代GH测试所需的再认证时间
- 缺口：GH独有技术壁垒的具体描述
- 证伪条件：Foundation Medicine、Roche或Exact Sciences取得与GH相当的市场份额的披露
- 证伪条件：任何主要医院系统从GH转向竞争对手的记录

### customer_dependency: partial

10-Q披露客户A在2026年第三季度和前九个月均占总收入的28%，表明客户集中度显著；收入来自肿瘤临床检测和生物制药服务两条线，说明存在真实客户采购关系，但客户身份匿名，无法核实是否为超大规模云计算或科技公司。

- 支持 [ev_af188616d5eded96](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000044/gh-20260930.htm) (primary-document): Customer A 28 % 29 % 28 % 29 % 15 % 23 %
- 支持 [ev_4bc09d04bb038a92](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000044/gh-20260930.htm) (primary-document): Oncology revenue is recognized at the time results of the test are reported to physicians
- 支持 [ev_3df8ea70c2bd5d4e](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000044/gh-20260930.htm) (primary-document): Biopharma and data revenue includes amounts derived from the delivery of the Company's tests for biopharmaceutical customers
- 缺口：客户A的具体身份
- 缺口：主要生物制药合同的披露名称和合同期限
- 缺口：设计锁定条款或独家协议的证据
- 证伪条件：客户A明确被识别为非生物制药/非系统性买家
- 证伪条件：客户A收入份额在未来季度显著下降

### pure_play: partial

两个收入板块（肿瘤临床检测和生物制药/数据服务）均属精准肿瘤学液体活检领域，未见无关多元化，符合纯标的特征；但证据未提供各板块的具体收入金额或占比，无法量化主题敞口。

- 支持 [ev_a64bb5619310a1db](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000044/gh-20260930.htm) (primary-document): Biopharma and data revenue also includes amounts derived from the performance of the Company's service agreements with biopharmaceutical customers, primarily comprised of companion diagnostic development and regulatory approval, monitoring and maintenance, GuardantINFORM data services and GuardantConnect referral services
- 缺口：各收入板块的具体金额或百分比占比
- 缺口：任何非肿瘤业务线的披露
- 证伪条件：非肿瘤业务收入超过总收入20%的披露

### multi_node_control: unknown

证据仅显示GH在单一实验室设施运营液体活检检测服务，GuardantINFORM为数据服务产品，但这两者均属于同一服务层次，不构成供应链上相互关联的不同节点控制；无垂直整合证据。

- 反证 [ev_00a853a6fe15467f](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000013/gh-20251231.htm) (primary-document): We currently derive the majority of our revenue from tests performed at a single laboratory facility located in Redwood City, California
- 缺口：GH是否控制测序试剂、文库制备或生物信息学分析等上游节点的证据
- 缺口：GH是否向其他实验室提供技术平台或授权的披露
- 证伪条件：GH收购或自建上游原材料/测序基础设施的公告

### earnings_validation: partial

10-Q提供了截至2026年9月30日的实际财务数据：前九个月净亏损3.566亿美元（同比扩大约24%），第三季度净亏损1.244亿美元；公司有实际收入（客户A占28%），为商业化阶段公司，但亏损持续扩大且证据中未披露现金余额，无法评估资金充足性。

- 支持 [ev_1ab5407c65d0763d](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000044/gh-20260930.htm) (primary-document): Net loss, basic and diluted $ ( 124,362 ) $ ( 92,725 ) $ ( 356,579 ) $ ( 287,783 )
- 支持 [ev_857b934b5e234eb4](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000044/gh-20260930.htm) (primary-document): The majority of the Company’s accounts receivable arises from the delivery of the Company's tests, and the performance of the Company's service and partnership agreements with biopharmaceutical companies and international laboratory partners
- 反证 [ev_5a198d590bd07d38](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000044/gh-20260930.htm) (primary-document): Net loss per share, basic and diluted $ ( 0.93 ) $ ( 0.74 ) $ ( 2.68 ) $ ( 2.32 )
- 缺口：现金及现金等价物余额
- 缺口：收入同比增长数据
- 缺口：毛利率趋势
- 证伪条件：收入环比下降或客户A收入份额显著萎缩的季度披露

### counter_thesis: partial

证据中存在多个具体反驳因素：TwinStrand专利诉讼陪审团裁决（2023年11月）对公司不利，构成实质性法律风险；Illumina独家供应商依赖造成供应端集中风险；亏损持续扩大（前九个月同比增加约6900万美元）。估值压力、替代技术路径（如纳米孔测序）和地缘政治维度在证据中未被检验。

- 支持 [ev_556845b39882c12a](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000013/gh-20251231.htm) (primary-document): TwinStrand Biosciences, Inc. and the University of Washington filed a lawsuit for patent infringement against us in August 2021 and a jury verdict was entered against us in November 2023
- 支持 [ev_33420cd07324a421](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000013/gh-20251231.htm) (primary-document): Any disruption in operations of Illumina or other sole or limited suppliers or termination or suspension of our relationships with them could materially and adversely impact our supply chain and laboratory ope
- 支持 [ev_1ab5407c65d0763d](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000044/gh-20260930.htm) (primary-document): Net loss, basic and diluted $ ( 124,362 ) $ ( 92,725 ) $ ( 356,579 ) $ ( 287,783 )
- 缺口：竞争对手（Foundation Medicine、Exact Sciences）市场份额数据
- 缺口：Oxford Nanopore等替代测序技术对Illumina依赖的颠覆性评估
- 缺口：CMS报销政策变化的影响分析
- 缺口：估值倍数与同类公司的比较
- 证伪条件：TwinStrand判决赔偿金额超过公司现金储备
- 证伪条件：Illumina终止与GH的供应协议
- 证伪条件：主要商业保险公司拒绝报销GH核心检测产品

### management_governance: partial

按 Serenity 规则：一手材料尚未证明领导层连续。通道文件中联合CEO架构经章程条款证实，但未出现任何CEO或CFO的具体姓名及在职确认；Monroe为首席人事官，Potter为董事，两者均不是CEO/CFO；无调查披露，无继任空缺迹象；CEO/CFO个人在职情况无法从现有通道中得出结论。

- 支持 [ev_7e80a3f28aa94c27](https://www.sec.gov/Archives/edgar/data/1576280/000157628026000013/gh-20251231.htm) (primary-document): a special meeting of stockholders may be called only by our board of directors, its chairman, or our co-chief executive officers
- 缺口：CEO姓名及在职确认
- 缺口：CFO姓名及在职确认
- 缺口：董事长具体身份确认

## GLUE · complete

审查记录：`state/serenity-reviews/GLUE-claudecli-770891df5d11ecd36cbe.json`

### supply_chain_map: partial

10-K披露了上游依赖（合同生产商、乌克兰和中国供应商提供药物物质/产品）、公司核心产品（MGD分子胶降解剂）以及下游客户（Roche、Novartis合作协议）。但未具名关键供应商，缺乏具体的物料-节点映射。

- 支持 [ev_546134fa25481de8](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): we do not currently have arrangements in place for a redundant or second-source supply of all drug product or drug substance
- 支持 [ev_caf7183d6e80a95e](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): We also have a supplier based in China which supplies us with services and materials to support the ongoing expansion of our library of MGDs
- 支持 [ev_e6ef0c36017aa695](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): we entered into a collaboration and license agreement, or the Roche Agreement, with Roche for the discovery and development of MGDs against targets in cancer and neurological diseases
- 缺口：具名的合同生产商及其地理位置
- 缺口：药物物质和药物产品各环节的具体供应商数量
- 缺口：从原料到成品的完整物料流图
- 证伪条件：发现公司实际拥有多家冗余供应商，降低供应链集中度
- 证伪条件：关键供应商被收购或停产导致供应链中断

### chokepoint_evidence: unknown

GLUE是一家生物技术药物发现公司，不控制任何上游物理瓶颈节点。10-K反而表明公司自身面临供应集中风险（单一来源供应商、乌克兰/中国地缘政治风险）。专利保护存在但面临挑战，不构成Serenity方法论要求的供应浓度或替代壁垒型chokepoint。

- 反证 [ev_546134fa25481de8](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): It may be difficult for us to assess their ability to timely meet our demand in the future based on past performance
- 反证 [ev_b84213068232740c](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): Competitors may also contest our patents by arguing before an administrative patent authority or judge that the invention was not patent-eligible, was not novel, was obvious
- 缺口：公司在任何供应链节点的全球市场份额数据
- 缺口：MGD技术平台相对于竞争对手PROTAC/其他降解剂的替代壁垒量化证据
- 缺口：下游客户无法绕开GLUE技术的具体证据
- 缺口：反证只是通用风险条款或记录字段，不是针对公司的直接反证
- 证伪条件：公司MGD平台被证明为唯一能针对某类靶点的降解技术，形成事实垄断
- 证伪条件：多家竞争对手开发出同等MGD平台，彻底消除稀缺性

### customer_dependency: partial

Roche和Novartis两大全球制药巨头均已签署合作/许可协议，并支付了大额前期款项（Roche $50M + $12M里程碑；Novartis $150M前期款）。Q3 2026协作收入$54.4M同比增长326%，表明下游客户实际付费且依赖度在提升。

- 支持 [ev_e6ef0c36017aa695](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): We received an upfront payment of $50.0 million and milestone payments of $12.0 million from Roche under the terms of the Roche Agreement
- 支持 [ev_e6ef0c36017aa695](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): In December 2024, we received a $150 million non-refundable upfront payment
- 支持 [ev_1f641be580067132](https://data.sec.gov/api/xbrl/companyfacts/CIK0001826457.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerIncludingAssessedTax): 54,366,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_e6ef0c36017aa695](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): we are entitled to receive from Novartis up to $2.1 billion in development, regulatory, and sales milestones
- 缺口：除Roche和Novartis外是否有其他合作客户
- 缺口：客户集中度风险的量化（前两大客户占收入比例）
- 缺口：通过需要直接相关的原始披露及完整证据
- 证伪条件：Roche或Novartis终止合作协议
- 证伪条件：临床试验失败导致里程碑付款无法触发

### pure_play: unknown

公司明确为单一经营和报告分部，专注于MGD分子胶降解剂的开发。所有收入均来自MGD相关协作，无其他业务线稀释主题敞口。

- 支持 [ev_f6ecf85ccd814b96](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): The Company manages its operations as a single operating and reportable segment committed to developing a portfolio of novel and proprietary MGDs
- 缺口：引用不存在或原文无法匹配
- 证伪条件：公司进入与MGD无关的新治疗领域或业务线

### multi_node_control: unknown

GLUE是药物发现平台公司，拥有QuEEN发现引擎和多条MGD管线，但这些属于同一节点（药物发现/开发）的多个产品，而非对供应链上下游多个相连节点的控制。公司依赖外部合同生产商，不控制生产节点。

- 反证 [ev_546134fa25481de8](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): we have no control over the ability of our contract manufacturers to maintain adequate quality control, quality assurance and qualified personnel
- 缺口：公司向上游原料或生产整合的证据
- 缺口：公司控制下游商业化渠道的证据
- 缺口：反证只是通用风险条款或记录字段，不是针对公司的直接反证
- 证伪条件：公司收购或自建GMP生产设施，实现发现+生产的双节点控制
- 证伪条件：公司获得下游分销或商业化能力

### earnings_validation: partial

准备阶段公司。FY2025协作收入$123.7M，Q3 2026收入$54.4M（同比+326%），Q3 2026实现净利润$3.1M。XBRL报告现金$45.2M（仅现金等价物），但公司持有大量短期投资（上下文显示总流动资金$577.7M，约42.5个月跑道）。YTD运营现金流为负$122.5M，说明烧钱速度较快。公司能够资助下一个里程碑，但长期盈利依赖临床进展和里程碑触发，尚未完全验证投资论点。

- 支持 [ev_1f641be580067132](https://data.sec.gov/api/xbrl/companyfacts/CIK0001826457.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 3,063,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05
- 支持 [ev_b82ba6e9093bd82f](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): Collaboration revenue $ 123,672 $ 75,622
- 支持 [ev_1f641be580067132](https://data.sec.gov/api/xbrl/companyfacts/CIK0001826457.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -122,461,000 for 2026-01-01 to 2026-09-30
- 支持 [ev_1f641be580067132](https://data.sec.gov/api/xbrl/companyfacts/CIK0001826457.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 45,180,000 for as of 2026-09-30
- 反证 [ev_f6ecf85ccd814b96](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): Net loss $ ( 38,626 ) $ ( 72,700 )
- 缺口：包含短期投资在内的总流动资金明细（10-Q引用）
- 缺口：2026年全年收入指引或里程碑付款预期时间表
- 缺口：各管线里程碑达成对收入的具体影响测算
- 证伪条件：Novartis或Roche终止协议导致协作收入归零
- 证伪条件：临床失败导致里程碑付款无法触发，烧钱耗尽现金
- 证伪条件：2026 Offering所募资金低于预期

### counter_thesis: partial

已从供应、需求、替代、地缘政治和估值多角度压力测试。主要风险：1）单一来源供应商+乌克兰/中国地缘政治风险可能中断供应链；2）专利可能被挑战或绕开；3）高度依赖Roche/Novartis两大客户，协议终止即收入消失；4）临床Phase 2失败风险（MRT-2359、MRT-8102尚在进行中）；5）FY2025仍为净亏损$38.6M。反面论点已被检视，风险未消除但跑道充足（>12个月），不存在紧迫融资风险。

- 支持 [ev_caf7183d6e80a95e](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): We currently have a supplier based in Ukraine which supplies us with services and materials related to the ongoing expansion of our library of MGDs
- 支持 [ev_b84213068232740c](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): If a court or administrative patent authority agrees, we would lose our protection of those challenged patents
- 支持 [ev_546134fa25481de8](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): our single-source and dual source suppliers will be able to meet our demand for their products, either because of the nature of our agreements with those suppliers
- 支持 [ev_dc0d80abff63d187](https://clinicaltrials.gov/study/NCT05546268) (clinicaltrials-gov): Study of Oral MRT-2359 in Selected Cancer Patients. Highest listed phase: Phase 2. Overall status: ACTIVE_NOT_RECRUITING
- 反证 [ev_e6ef0c36017aa695](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): we are eligible to receive additional contingent payments from Roche upon the occurrence of defined research, development, regulatory and sales-based events exceeding $2 billion
- 缺口：竞争对手PROTAC/其他降解剂平台的直接对比数据
- 缺口：目标适应症市场规模及竞争格局分析
- 缺口：通过需要直接相关的原始披露及完整证据
- 证伪条件：MRT-2359或MRT-8102 Phase 2数据readout显示无效或严重安全性问题
- 证伪条件：Roche行使退出权终止合作
- 证伪条件：Novartis放弃MRT-6160的Phase 2开发
- 证伪条件：竞争对手MGD平台获得FDA突破性疗法认定
- 证伪条件：美中贸易制裁升级切断中国供应商

### management_governance: partial

CEO Markus Warmuth在任并签署8-K（2026年11月5日），管理层评估FY2025内控有效。但公司仍为'新兴成长型公司'，无独立审计师对内控的鉴证报告。代理声明（Part III）尚未提交，董事会详细构成和治理信息不在证据包内。CEO有10b5-1交易计划（出售最多32,000股），规模较小，无异常信号。

- 支持 [ev_190c281476e11cef](https://www.sec.gov/Archives/edgar/data/1826457/000119312526448527/glue-20261105.htm) (primary-document): By: /s/ Markus Warmuth Markus Warmuth President and Chief Executive Officer
- 支持 [ev_5544ccb277c82e75](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): Based on this assessment, our management concluded that, as of December 31, 2025, our internal control over financial reporting was effective
- 支持 [ev_5544ccb277c82e75](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): Markus Warmuth Chief Executive Officer Adopt May 14, 2025 August 13, 2025 - August 13, 2026 Y Up to 32,000 shares of common stock to be sold
- 反证 [ev_5544ccb277c82e75](https://www.sec.gov/Archives/edgar/data/1826457/000119312526109360/glue-20251231.htm) (primary-document): This Annual Report on Form 10-K does not include an attestation report of our independent registered public accounting firm due to a transition period
- 缺口：董事会成员完整名单及独立性评估
- 缺口：高管团队完整背景（CSO、CMO等关键科学/医学领导）
- 缺口：代理声明中的薪酬和治理细节
- 证伪条件：CEO或关键高管突然离职
- 证伪条件：SEC调查或内控重大缺陷披露
- 证伪条件：独立审计师出具否定意见

## GRAL · complete

审查记录：`state/serenity-reviews/GRAL-claudecli-85e6ea0b42183574bd3d.json`

### supply_chain_map: partial

证据显示GRAIL有两个收入来源（Screening筛查和Developmental Services开发服务），客户分为商业和政府渠道，美国和国际市场。XBRL标签显示Illumina曾为关联方（2024-06-24剥离）。但缺乏上游具体投入物（测序试剂、仪器供应商）的映射，无法完整描绘供应链。

- 支持 [ev_0527d953ce045617](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): Short-term marketable securities 759,700 654,703
- 支持 [ev_89cd6e64e2a6b160](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): gral:ScreeningRevenueMember 2026-07-01 2026-09-30
- 支持 [ev_89cd6e64e2a6b160](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): gral:DevelopmentalServicesRevenueMember 2026-07-01 2026-09-30
- 支持 [ev_1cb2fab96340f5e7](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): country:US gral:ScreeningRevenueMember 2026-01-01 2026-09-30
- 支持 [ev_543c155464909631](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): gral:ReportableSegmentMember gral:ScreeningRevenueMember 2026-07-01 2026-09-30
- 缺口：上游关键投入物（测序仪器、试剂、样本采集耗材）的具体供应商及集中度
- 缺口：下游具体医院/健康系统/保险覆盖客户的名称和依赖关系
- 缺口：GRAIL Galleri检测产品在供应链中的具体位置描述
- 证伪条件：发现GRAIL上游有多个可替代供应商，不存在供应集中风险
- 证伪条件：发现GRAIL产品可被多种竞品轻易替代，无供应链壁垒

### chokepoint_evidence: unknown

证据中没有任何段落显示GRAIL控制供应链瓶颈或拥有替代壁垒。GRAIL是液体活检/多癌早筛的检测服务提供商，属于供应链下游消费者而非瓶颈控制者。仅有AI相关性不足以通过此门。

- 缺口：GRAIL在多癌早筛市场的供应集中度数据（全球竞争对手数量、市场份额）
- 缺口：技术替代壁垒的具体证据（专利独占性、数据护城河的量化描述）
- 缺口：下游客户无法绕过GRAIL的具体证据
- 证伪条件：出现多个液体活检竞品（Exact Sciences、Guardant等）获得同等或更优的MCED检测批准
- 证伪条件：GRAIL核心检测技术被开源或通用化

### customer_dependency: partial

XBRL标签明确显示存在单一客户集中风险（OneCustomerMember覆盖收入和应收账款），Illumina曾为关联方贡献收入。但证据未披露该客户名称、集中度百分比或设计锁定机制。仅有集中度标签支持partial。

- 支持 [ev_659995c1de1b2b1a](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): us-gaap:CustomerConcentrationRiskMember gral:OneCustomerMember us-gaap:SalesRevenueNetMember 2026-07-01 2026-09-30
- 支持 [ev_659995c1de1b2b1a](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): us-gaap:CustomerConcentrationRiskMember gral:OneCustomerMember us-gaap:AccountsReceivableMember 2026-01-01 2026-09-30
- 支持 [ev_543c155464909631](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): gral:IlluminaInc.Member gral:ScreeningRevenueMember us-gaap:RelatedPartyMember 2025-07-01 2025-09-30
- 缺口：单一客户的名称及其占收入比例
- 缺口：除集中度风险标签外的具体客户采用/使用Galleri检测的披露
- 缺口：保险覆盖/报销决定对客户依赖性的影响
- 证伪条件：该单一大客户终止合作或大幅减少采购
- 证伪条件：CMS或主要商业保险拒绝报销Galleri检测

### pure_play: partial

GRAIL的两个收入来源（Screening和Developmental Services）均与多癌早期检测相关，重组计划也聚焦'核心MCED业务'。这暗示高主题集中度。但缺乏各业务分部的收入占比数据来量化AI医学主题敞口。

- 支持 [ev_543c155464909631](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): gral:ReportableSegmentMember gral:DevelopmentalServicesRevenueMember 2026-07-01 2026-09-30
- 支持 [ev_54fc01d940b9bdff](https://www.sec.gov/Archives/edgar/data/1699031/000169903125000193/gral-20250930.htm) (primary-document): gral:RestructuringPlanCoreMCEDBusinessMember 2025-01-01 2025-09-30
- 支持 [ev_6ea13ac8afac6d8a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001699031.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 37,535,000 for 2026-07-01 to 2026-09-30
- 缺口：Screening vs Developmental Services各自的收入金额或百分比
- 缺口：GRAIL产品中AI/机器学习技术的具体贡献和不可替代性说明
- 证伪条件：发现Developmental Services收入与AI医学主题无关且占比过大
- 证伪条件：GRAIL大幅进入与癌症早筛无关的业务领域

### multi_node_control: unknown

证据中未显示GRAIL控制供应链中两个以上相连节点。GRAIL运营检测服务和开发服务，但这些是同一业务的不同收入类型，不构成供应链上下游的多节点控制。

- 缺口：GRAIL是否自有测序平台或试剂生产能力的证据
- 缺口：GRAIL是否同时控制样本采集、检测分析和报告解读等多个节点的证据
- 缺口：垂直整合程度的具体披露
- 证伪条件：GRAIL核心检测依赖第三方平台（如Illumina测序仪），无法自主控制关键节点

### earnings_validation: partial

有实际Q3 2026财务数据：收入$37.5M（同比+3.7%），净亏损-$103.6M，现金$29M但短期有价证券$759.7M（流动性充足）。然而收入增长仅3.7%，远不能验证高增长AI医学论点。公司仍在大幅亏损，经营现金流YTD -$242M。财务数据存在但不支持强增长论点。

- 支持 [ev_6ea13ac8afac6d8a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001699031.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 37,535,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05
- 支持 [ev_6ea13ac8afac6d8a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001699031.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 36,194,000, a change of +3.7%
- 支持 [ev_6ea13ac8afac6d8a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001699031.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -103,568,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_0527d953ce045617](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): Cash and cash equivalents $ 28,976 $ 249,727
- 支持 [ev_0527d953ce045617](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): Accumulated deficit ( 10,518,683 ) ( 10,211,681 )
- 反证 [ev_6ea13ac8afac6d8a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001699031.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -242,459,000 for 2026-01-01 to 2026-09-30
- 反证 [ev_6ea13ac8afac6d8a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001699031.json) (sec-companyfacts): R&D expense (ResearchAndDevelopmentExpense): 44,073,000 for 2026-07-01 to 2026-09-30
- 缺口：收入增长加速的趋势数据（逐季对比）
- 缺口：毛利率或单位经济学数据以验证规模化路径
- 缺口：管理层对收入增长驱动因素的定性说明
- 证伪条件：收入增速持续放缓至个位数或转负
- 证伪条件：短期有价证券因市场波动大幅缩水导致流动性危机
- 证伪条件：运营现金流烧钱速度加快使现有资金不足以支撑至盈利

### counter_thesis: partial

基于证据可识别多个重大反面风险：(1)收入增长极慢（+3.7%），与$5.2B市值严重不匹配；(2)季度净亏损$103.6M远超季度收入$37.5M；(3)累计亏损超$105亿；(4)现金从$249.7M降至$29M（9个月降88%），虽有$759.7M有价证券缓冲；(5)单一客户集中风险；(6)核心MCED业务正在重组。反面论点已被审视。

- 支持 [ev_6ea13ac8afac6d8a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001699031.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 28,976,000 for as of 2026-09-30
- 支持 [ev_0527d953ce045617](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): Accumulated deficit ( 10,518,683 ) ( 10,211,681 )
- 支持 [ev_659995c1de1b2b1a](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): us-gaap:CustomerConcentrationRiskMember gral:OneCustomerMember us-gaap:SalesRevenueNetMember 2026-01-01 2026-09-30
- 支持 [ev_54fc01d940b9bdff](https://www.sec.gov/Archives/edgar/data/1699031/000169903125000193/gral-20250930.htm) (primary-document): gral:RestructuringPlanCoreMCEDBusinessMember 2025-07-01 2025-09-30
- 反证 [ev_0527d953ce045617](https://www.sec.gov/Archives/edgar/data/1699031/000162828026071041/gral-20260930.htm) (primary-document): Short-term marketable securities 759,700 654,703
- 缺口：竞争对手（Exact Sciences Cologuard、Guardant Shield等）的市场份额和进展对比
- 缺口：FDA审批路径和时间线的不确定性分析
- 缺口：地缘政治或监管变化对液体活检行业的影响评估
- 缺口：通过需要直接相关的原始披露及完整证据
- 证伪条件：FDA拒绝批准Galleri作为处方筛查检测
- 证伪条件：CMS决定不覆盖多癌早筛检测
- 证伪条件：竞争对手率先获批并占领市场
- 证伪条件：现金+有价证券耗尽前未能实现收入显著增长，被迫大幅稀释融资
- 证伪条件：单一大客户流失导致收入骤降

### management_governance: partial

证据仅显示CFO Aaron Freidin签署了8-K报告。公司进行了核心MCED业务重组（含裁员和其他重组费用）。缺乏CEO身份、董事会构成、高管变动历史等关键治理信息。重组表明管理层在调整战略方向，但无法充分评估领导层稳定性。

- 支持 [ev_641efa06b51c0bd7](https://www.sec.gov/Archives/edgar/data/1699031/000162828026070118/gral-20261104.htm) (primary-document): Name: Aaron Freidin Title: Chief Financial Officer
- 支持 [ev_40953ade3876dd75](https://www.sec.gov/Archives/edgar/data/1699031/000162828026017319/gral-20251231.htm) (primary-document): gral:RestructuringPlanCoreMCEDBusinessMember 2024-08-09 2024-12-31
- 缺口：CEO身份及任期
- 缺口：董事会构成和独立性
- 缺口：高管团队变动历史（特别是Illumina剥离后）
- 缺口：任何正在进行的调查或诉讼对管理层的影响
- 证伪条件：发现CEO或其他关键高管近期离职
- 证伪条件：发现SEC调查或重大诉讼影响公司治理
- 证伪条件：发现Illumina剥离后治理结构存在重大缺陷

## GSK · complete

审查记录：`state/serenity-reviews/GSK-claudecli-200582e0f0ff127e2555.json`

### supply_chain_map: unknown

证据显示GSK的治疗领域（HIV、呼吸/免疫、肿瘤、疫苗、肝病）和部分上游许可来源（Hansoh Pharma授权Ris-Rez和Mo-Rez，Ionis授权bepirovirsen，AnaptysBio/TESARO授权dostarlimab），但缺乏完整的物理供应链映射（原料→制造→分销→终端用户），无法识别集中度瓶颈节点。

- 支持 [ev_2988321eb4c612ba](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009062/a7767z.htm) (primary-document): GSK licensed bepirovirsen from Ionis Pharmaceuticals and collaborated with them on its development
- 支持 [ev_90ab54fddf673183](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009036/a5712z.htm) (primary-document): Jemperli was discovered by AnaptysBio, Inc. and licensed to TESARO, Inc., under a collaboration and exclusive license agreement signed in March 2014
- 缺口：完整的原料药/API供应商清单及地理集中度
- 缺口：制造设施产能及外包比例
- 缺口：分销渠道及终端客户结构
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：如果GSK的关键API全部可从多家供应商获得，则不存在供应链瓶颈

### chokepoint_evidence: fail

GSK是一家大型多元化生物制药公司，证据中未显示任何供应集中度或替代壁垒。其药物许可来自多个合作伙伴（Hansoh、Ionis、AnaptysBio），表明GSK是下游买家而非瓶颈控制者。仅凭AI相关性不足以通过此门。

- 反证 [ev_ba413165f9f7c4bb](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009127/a3306a.htm) (primary-document): GSK acquired exclusive worldwide rights (excluding mainland China, Hong Kong, Macau and Taiwan) from Hansoh Pharma to progress clinical development and commercialisation of Mo-Rez globally
- 反证 [ev_2988321eb4c612ba](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009062/a7767z.htm) (primary-document): GSK licensed bepirovirsen from Ionis Pharmaceuticals and collaborated with them on its development
- 缺口：GSK在任何关键输入材料上的全球市场份额数据
- 缺口：替代供应商的转换成本或时间证据
- 缺口：任何节点的寡头垄断或双寡头证据
- 证伪条件：若发现GSK控制某关键生物制药输入的50%以上全球供应

### customer_dependency: partial

证据显示GSK产品已获FDA批准并进入临床使用（Jemperli获批用于MSI-H/dMMR直肠癌，Hibsago获批用于慢性乙肝），表明存在真实的下游患者/医疗系统采用。但缺乏具体客户集中度、处方量或市场份额数据，无法确认关键客户依赖关系。

- 支持 [ev_2577be90e3408916](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009036/a5712z.htm) (primary-document): GSK plc (LSE/NYSE: GSK) today announced the US Food and Drug Administration (FDA) has approved Jemperli (dostarlimab) as the first and only immunotherapy for adults with stage II and III microsatellite instability-high
- 支持 [ev_6d1a9f3d2abed57e](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009062/a7767z.htm) (primary-document): GSK plc (LSE/NYSE: GSK) today announced that the US Food and Drug Administration (FDA) has approved Hibsago (bepirovirsen) for the treatment of chronic hepatitis B (CHB) virus infection
- 支持 [ev_1210e0f325c874e8](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009062/a7767z.htm) (primary-document): Pooled data from the B-Well phase III trials showed that six-month treatment with bepirovirsen achieved a clinically meaningful 19% functional cure response rate (233 of 1,220 vs. 0 of 614 in the placebo group)
- 缺口：按客户/付款方分类的收入集中度
- 缺口：具体处方量或市场份额数据
- 缺口：与医疗系统或保险公司的合同关系
- 证伪条件：如果GSK的新获批药物未能获得保险覆盖或市场接受度极低

### pure_play: unknown

GSK是高度多元化的全球生物制药公司，业务覆盖HIV、呼吸/免疫/炎症、肿瘤、疫苗、肝病等多个治疗领域。XBRL数据明确显示多个商业运营分部。这不是对AI医疗或任何单一主题的纯粹敞口，与Serenity方法偏好的纯粹瓶颈型公司不符。

- 反证 [ev_bdf6d5c6af72de5a](https://www.sec.gov/Archives/edgar/data/1131399/000113139926000004/gsk-20251231.htm) (primary-document): gsk:CommercialOperationsMember gsk:OncologyMember 2025-01-01 2025-12-31 0001131399 gsk:CommercialOperationsMember gsk:OncologyMember 2024-01-01 2024-12-31
- 缺口：各治疗领域的收入占比
- 缺口：AI相关收入的具体金额或比例
- 缺口：引用不存在或原文无法匹配
- 证伪条件：如果某单一治疗领域（如肿瘤ADC）贡献超过60%收入

### multi_node_control: unknown

证据显示GSK拥有多种药物产品和治疗领域，但这是产品多元化，不是对同一供应链中两个相连节点的控制。GSK的关键分子来自外部授权（Hansoh、Ionis），GSK主要在开发和商业化节点运营，不控制上游原料或中间体生产节点。

- 反证 [ev_ba413165f9f7c4bb](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009127/a3306a.htm) (primary-document): GSK acquired exclusive worldwide rights (excluding mainland China, Hong Kong, Macau and Taiwan) from Hansoh Pharma to progress clinical development and commercialisation of Mo-Rez globally
- 缺口：GSK自有原料药生产能力的证据
- 缺口：垂直整合至上游供应节点的证据
- 缺口：引用不存在或原文无法匹配
- 证伪条件：如果GSK自主控制关键ADC连接子或payload的全球生产

### earnings_validation: unknown

证据中的20-F文件仅包含XBRL标签元数据（成员名称和日期范围），不含可引用的实际财务数字（收入、利润、利润率等）。6-K文件是产品新闻稿，不含财务业绩。无法从现有证据中验证AI医疗相关论点的财务支撑。

- 缺口：可引用的收入、净利润或每股收益数字
- 缺口：按治疗领域分列的收入明细
- 缺口：毛利率或营业利润率趋势
- 缺口：AI/数字化投入的具体支出
- 证伪条件：如果GSK肿瘤业务收入同比下降或利润率恶化

### counter_thesis: partial

可识别若干反面风险：1）核心药物依赖外部授权（Hansoh、Ionis），供应端受制于人；2）Jemperli适用于仅5-10%的直肠癌亚群（MSI-H/dMMR），市场天花板有限；3）ADC竞争激烈（多家公司开发B7-H3和B7-H4靶向ADC）；4）Hibsago功能性治愈率仅19%。但缺乏估值分析和完整竞争格局数据。

- 支持 [ev_7332a19f2015490b](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009036/a5712z.htm) (primary-document): Around 5–10% of rectal cancers are microsatellite instability-high (MSI-H) or mismatch repair-deficient (dMMR)
- 支持 [ev_1210e0f325c874e8](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009062/a7767z.htm) (primary-document): six-month treatment with bepirovirsen achieved a clinically meaningful 19% functional cure response rate (233 of 1,220 vs. 0 of 614 in the placebo group)
- 支持 [ev_43c2b9e685640fe8](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009023/a4743z.htm) (primary-document): Ris-Rez has received several global regulatory designations to date, including orphan drug designations in the US, Japan and the EU for SCLC
- 反证 [ev_2577be90e3408916](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009036/a5712z.htm) (primary-document): Jemperli (dostarlimab) approved in US as first and only immunotherapy for adults with MSI-H/dMMR locally advanced rectal cancer
- 反证 [ev_6d1a9f3d2abed57e](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009062/a7767z.htm) (primary-document): Bepirovirsen is a first in class antisense oligonucleotide (ASO) and offers unprecedented functional cure rates compared to current standard of care
- 缺口：当前估值与同业的对比分析
- 缺口：ADC领域竞争对手（如第一三共、Seagen/辉瑞）的市场份额
- 缺口：地缘政治风险评估（中国市场排除条款的影响）
- 缺口：专利到期时间表
- 证伪条件：Ris-Rez或Mo-Rez的III期试验失败
- 证伪条件：竞争对手ADC在相同适应症中显示优越疗效
- 证伪条件：Hibsago在真实世界中功能性治愈率显著低于试验数据
- 证伪条件：Hansoh Pharma终止授权或提出更苛刻条款

### management_governance: unknown

证据中提及Tony Wood（首席科学官）和Victoria Whyte（授权签署人），以及多位投资者关系和媒体联系人，表明有运营中的治理结构。但缺乏CEO身份、董事会构成、高管变动、薪酬结构或任何调查/诉讼信息。无法充分评估治理质量和领导层连续性。

- 支持 [ev_5d77a493221fa34b](https://www.sec.gov/Archives/edgar/data/1131399/000165495426009127/a3306a.htm) (primary-document): Victoria Whyte Authorised Signatory for and on behalf of GSK plc
- 缺口：CEO身份及任期
- 缺口：董事会构成及独立性
- 缺口：高管薪酬结构
- 缺口：未决诉讼或监管调查信息
- 缺口：近期高管变动记录
- 缺口：引用不存在或原文无法匹配
- 证伪条件：CEO或其他关键高管突然离职
- 证伪条件：重大监管调查或合规问题被披露

## HCAT · complete

审查记录：`state/serenity-reviews/HCAT-claudecli-83c96d2e875840f0e105.json`

### supply_chain_map: partial

证据显示HCAT提供数据平台（DOS、Ignite）和分析应用给医疗系统客户，包含Technology和Professional Services两个业务段，上游依赖Microsoft云计算和托管服务。但缺乏对具体上游数据来源、EHR集成伙伴及下游具体医院客户名称的披露，供应链图谱不完整。

- 支持 [ev_09030847822706f7](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): Our technology segment (Technology) includes our data platform, analytics applications and support services and generates revenues primarily from contracts that are cloud-based subscription arrangements
- 支持 [ev_3c61deb39a20c021](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): The increase was primarily due to a $3.1 million increase in cloud computing and hosting costs largely from the expanded use of Microsoft
- 支持 [ev_f7a15528843d167f](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): Platform Clients have historically been defined as clients who directly or indirectly access our platform via a technology subscription contract
- 缺口：具体上游EHR/数据供应商名称
- 缺口：具体下游医院或健康系统客户名称
- 缺口：数据采集与集成的完整流程描述
- 证伪条件：发现HCAT平台被竞争对手完全替代
- 证伪条件：上游Microsoft或其他云提供商终止合作

### chokepoint_evidence: unknown

证据中无任何关于HCAT在临床数据或健康分析供应链中具备供应集中度或替代壁垒的具体事实。IP相关段落为通用风险披露语言，不构成瓶颈证据。HCAT的市场地位、市占率、客户转换成本等关键信息均缺失。

- 缺口：HCAT在临床数据分析市场的市占率数据
- 缺口：客户转换成本或锁定周期的具体证据
- 缺口：与竞品（如Epic、Cerner/Oracle Health）的差异化壁垒说明
- 证伪条件：出现直接证据表明健康系统可在短期内迁移至竞品平台
- 证伪条件：市占率数据显示HCAT份额极低且无集中度优势

### customer_dependency: unknown

证据显示2025年新增32个Platform Clients，平均ARR在$300K-$700K之间，合同一般3-5年期限，但Dollar-based Retention Rate从2024年的102%降至2025年的93%，表明客户流失和缩减。无任何具体客户名称披露，客户依赖度无法验证。

- 支持 [ev_be7c3509bbc0f01d](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): Our total 2025 Platform Clients was 32, which is higher than recent years
- 支持 [ev_be7c3509bbc0f01d](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): Our actual aggregated average total ARR and non-recurring revenue from 2025 Platform Clients was near the midpoint of the expected range
- 反证 [ev_be7c3509bbc0f01d](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): Dollar-based Retention Rate (Tech + TEMS) 93 % 102 %
- 缺口：任何具体医院或健康系统客户名称
- 缺口：Top 10客户收入集中度
- 缺口：客户续约率背后的流失原因细节
- 缺口：引用不存在或原文无法匹配
- 证伪条件：Retention Rate继续下滑至90%以下
- 证伪条件：大型客户公开宣布迁移至竞品

### pure_play: pass

HCAT是相对纯粹的临床数据和分析平台公司。两个业务段（Technology 67%，Professional Services 33%）均围绕医疗数据分析，无非相关多元化业务。Technology收入占比逐年提升（2023年63%→2025年67%），显示向核心平台聚焦的趋势。

- 支持 [ev_57b8a5bb72f7c869](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): For the years ended December 31, 2025, 2024, and 2023, technology revenue represented 67%, 64%, and 63% of total revenue, respectively, and professional services revenue represented 33%, 36%, and 37% of total revenue, respectively
- 支持 [ev_09030847822706f7](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): Our business is organized based on our technology offerings and professional services. Accordingly, our segments are
- 证伪条件：HCAT进入与医疗数据无关的业务领域
- 证伪条件：Professional Services收入占比大幅回升稀释技术平台聚焦度

### multi_node_control: unknown

证据未显示HCAT控制供应链中两个以上相连节点。公司提供数据平台和专业服务，但这是产品与服务的组合，不构成对供应链多节点的控制。无上游数据采集/整合环节与下游应用交付构成纵向整合的具体证据。

- 缺口：HCAT在数据采集、清洗、建模、交付等环节纵向控制力的证据
- 缺口：与上下游整合形成壁垒的具体案例
- 证伪条件：证据显示HCAT各环节均依赖第三方且可被替代

### earnings_validation: partial

XBRL数据显示Q3 2026收入$56.3M，同比下降26.3%（去年同期$76.3M）。但Q3 2026净利润$40.5M为正，YTD经营现金流$16.9M为正，现金$53.7M。FY2025全年收入$311.1M同比仅增1%。收入大幅下滑与AI医疗增长论点矛盾，但公司已实现盈利，财务状况暂时稳定。近期Medicaid政策和研究资金削减构成额外逆风。

- 支持 [ev_09ffd0a3f683ce9a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001636422.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 56,283,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_09ffd0a3f683ce9a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001636422.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 40,496,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_3c61deb39a20c021](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): Total revenue was $311.1 million for the year ended December 31, 2025, compared to $306.6 million for the year ended December 31, 2024, an increase of $4.6 million, or 1%
- 反证 [ev_09ffd0a3f683ce9a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001636422.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 76,323,000, a change of -26.3%
- 反证 [ev_57b8a5bb72f7c869](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): We expect our near-term revenue growth to be negatively impacted by policy developments around Medicaid and research funding reductions
- 缺口：Q3 2026净利润$40.5M的驱动因素（是否为一次性项目如资产出售）
- 缺口：FY2026全年收入指引
- 缺口：收入下降26%的具体原因拆解（是否为业务剥离导致）
- 证伪条件：Q3净利润$40.5M来自一次性收益而非持续经营
- 证伪条件：收入持续下滑导致现金消耗加速
- 证伪条件：主要客户因Medicaid削减大规模退订

### counter_thesis: partial

部分反面论点可从证据中识别：(1)收入同比下降26.3%，增长论点受严重挑战；(2)Dollar-based Retention Rate从102%降至93%，客户净缩减；(3)Medicaid和研究资金削减带来政策逆风；(4)DOS向Ignite迁移导致技术收入流失；(5)Professional Services低利润率业务退出。但缺乏竞品替代、估值对比、地缘政治等多维度的反面分析来源。

- 支持 [ev_57b8a5bb72f7c869](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): We expect our near-term revenue growth to be negatively impacted by policy developments around Medicaid and research funding reductions
- 支持 [ev_be7c3509bbc0f01d](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): Dollar-based Retention Rate (Tech + TEMS) 93 % 102 %
- 支持 [ev_3c61deb39a20c021](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): elevated churn levels primarily from the migration of DOS clients to Ignite
- 支持 [ev_3c61deb39a20c021](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): The professional services revenue decrease was primarily due to lower utilization rates in our professional services organization, our exit of unprofitable pilot ambulatory operations TEMS
- 缺口：与Epic、Oracle Health等竞品的正面对比
- 缺口：当前估值合理性分析（市值仅$104M vs 收入$311M）
- 缺口：替代产品的转换时间和成本评估
- 缺口：政策风险（Medicaid削减）的量化影响
- 证伪条件：Retention Rate回升至100%+证明客户粘性恢复
- 证伪条件：Ignite迁移完成后收入企稳回升
- 证伪条件：新客户增长（如2025年32个新Platform Clients）加速抵消流失
- 证伪条件：Medicaid政策逆转或资金恢复

### management_governance: partial

EY出具了无保留意见的内部控制审计报告（截至2025年12月31日），表明财务内控有效。公司采用分级董事会和多项反收购条款。但证据中未披露管理层具体人员、CEO/CFO任期、近期高管变动等信息，无法全面评估领导层连续性。另外2025年下半年暂停了401(k)雇主匹配，可能暗示成本压力。

- 支持 [ev_3b6a543c3a5bad67](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): In our opinion, Health Catalyst, Inc. (the Company) maintained, in all material respects, effective internal control over financial reporting as of December 31, 2025
- 支持 [ev_9779f073e07f5377](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): provide that our board of directors is classified into three classes of directors with staggered three-year terms
- 反证 [ev_09030847822706f7](https://www.sec.gov/Archives/edgar/data/1636422/000163642226000035/hcat-20251231.htm) (primary-document): these employer contributions were paused during the second half of 2025
- 缺口：CEO/CFO姓名、任期和背景
- 缺口：近期高管或董事变动情况
- 缺口：是否存在未决调查或诉讼
- 缺口：管理层持股比例
- 证伪条件：披露重大高管离职或继任问题
- 证伪条件：出现SEC调查或审计师更换
- 证伪条件：内控出现重大缺陷

## HIMS · complete

审查记录：`state/serenity-reviews/HIMS-claudecli-cf19075e50837151cd57.json`

### supply_chain_map: unknown

证据包中没有任何段落描述HIMS的上游供应商、关键物料投入或下游供应链关系。HIMS是DTC远程医疗/健康平台，不是物理供应链节点。无法从现有证据构建供应链图。

- 缺口：药品/补剂供应商及其集中度信息
- 缺口：物流/配送合作伙伴及替代性分析
- 缺口：处方药来源（自有药房 vs 第三方）的披露
- 缺口：平台技术基础设施供应商信息
- 证伪条件：发现HIMS的核心药品供应完全依赖单一来源供应商
- 证伪条件：发现配送或药房基础设施存在不可替代的瓶颈节点

### chokepoint_evidence: unknown

HIMS是消费者直达远程医疗平台，不控制任何稀缺物理投入或具有高替代壁垒的供应节点。证据中无任何段落表明供应集中度或替代障碍。与AI相关性仅来自非一手新闻标题提及'AI Investments'，根据规则这不足以支持通过。

- 缺口：任何表明供应集中度（<5家全球供应商）的证据
- 缺口：替代壁垒或多年替代周期的证据
- 缺口：HIMS在任何供应链节点具有定价权的证据
- 缺口：不通过需要直接反证，缺少证据不能等同失败
- 证伪条件：HIMS获得独家药物配方或AI诊断技术的专利壁垒
- 证伪条件：发现HIMS控制某种稀缺医疗数据集且无替代来源

### customer_dependency: unknown

一手证据仅有XBRL财务数据显示营收$890M，但未披露具体客户、订阅用户数量或客户集中度。非一手新闻标题提及'Subscriber Losses'和'international expansion'，但新闻标题不可作为通过依据。无超大客户设计赢单或采购协议披露。

- 缺口：订阅用户总数及留存率数据
- 缺口：客户集中度披露（前10大客户占比）
- 缺口：企业客户或保险合作伙伴的具体采购协议
- 缺口：用户获取成本（CAC）和生命周期价值（LTV）数据
- 证伪条件：10-Q中披露具体订阅用户数和流失率表明依赖度可量化
- 证伪条件：发现大型企业客户或保险公司合同占收入主要比例

### pure_play: unknown

证据包中无业务分部收入拆分数据。HIMS被筛选器标记为'Imaging & devices'分部，但无一手证据支持AI医疗主题的收入敞口比例。公司主营DTC远程医疗和健康产品，AI主题敞口不明。

- 缺口：按业务线/产品类别的收入分部数据
- 缺口：AI相关产品或服务的收入占比
- 缺口：远程医疗 vs 产品销售 vs 订阅收入的拆分
- 证伪条件：10-Q中披露的分部数据显示AI相关收入占比极低
- 证伪条件：业务主要为传统药品销售而非AI驱动的医疗服务

### multi_node_control: unknown

证据中无任何段落表明HIMS控制两个或以上相连的供应链节点。公司是DTC平台，非垂直整合的供应链控制者。

- 缺口：HIMS拥有自有药房或制造能力的证据
- 缺口：HIMS控制上下游相连节点的证据
- 缺口：垂直整合战略的披露
- 缺口：不通过需要直接反证，缺少证据不能等同失败
- 证伪条件：发现HIMS同时拥有药品制造和配送基础设施形成纵向整合

### earnings_validation: partial

XBRL数据显示Q3 2026营收$890M同比增长48.6%，现金$605M，经营性现金流YTD $118.8M为正，但净亏损$33M。财务数据强劲但无法验证AI医疗瓶颈论点——增长来源不明，无法确认是否由AI驱动。非一手新闻提及全年指引不及预期和'transition year'，但这些不可作为一手证据引用。

- 支持 [ev_9ecca142a4b1e072](https://data.sec.gov/api/xbrl/companyfacts/CIK0001773751.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 890,373,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_9ecca142a4b1e072](https://data.sec.gov/api/xbrl/companyfacts/CIK0001773751.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 598,976,000, a change of +48.6%
- 支持 [ev_9ecca142a4b1e072](https://data.sec.gov/api/xbrl/companyfacts/CIK0001773751.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 605,604,000 for as of 2026-09-30
- 支持 [ev_9ecca142a4b1e072](https://data.sec.gov/api/xbrl/companyfacts/CIK0001773751.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -33,040,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_9ecca142a4b1e072](https://data.sec.gov/api/xbrl/companyfacts/CIK0001773751.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): 118,810,000 for 2026-01-01 to 2026-09-30
- 缺口：按产品线或AI相关业务的收入拆分
- 缺口：毛利率趋势以验证定价权
- 缺口：用户增长/流失的具体数据以验证可持续性
- 缺口：R&D支出数据（XBRL中标注未报告）
- 证伪条件：后续季度显示营收增长大幅放缓或转负
- 证伪条件：经营现金流转负且现金快速消耗
- 证伪条件：订阅用户持续大量流失导致收入不可持续

### counter_thesis: partial

可从证据中识别部分反面论点：净亏损持续、非独立董事Huberman的大额关联交易（每年$3.5M咨询+$5M播客营销）引发资本配置疑问。非一手新闻提及订阅用户流失、全年指引不及预期、KeyBanc预计'transition year'和定价下行压力，但这些均为非一手来源。缺乏对替代竞争、监管风险、GLP-1药物可及性变化等核心反面论点的一手证据支撑。

- 支持 [ev_0e061d6dc24d06d3](https://www.sec.gov/Archives/edgar/data/1773751/000177375126000245/hims-20261104.htm) (primary-document): he will provide certain scientific and brand marketing advisory services to Hims for a two-year period and will receive an annual advisory fee of $3,500,000 in cash
- 支持 [ev_0e061d6dc24d06d3](https://www.sec.gov/Archives/edgar/data/1773751/000177375126000245/hims-20261104.htm) (primary-document): Scicomm Media will provide podcast advertising services to Hims for up to three years for an annual fee of $5,000,000 in cash
- 支持 [ev_9ecca142a4b1e072](https://data.sec.gov/api/xbrl/companyfacts/CIK0001773751.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -33,040,000 for 2026-07-01 to 2026-09-30
- 缺口：竞争对手（Ro, GoodRx等）市场份额变化的一手数据
- 缺口：FDA对复合药监管政策变化的一手文件
- 缺口：GLP-1品牌药价格下降对HIMS复合药业务冲击的量化分析
- 缺口：客户获取成本上升趋势的一手证据
- 缺口：估值与同业对比的定量分析
- 证伪条件：FDA禁止或严格限制复合GLP-1药物销售
- 证伪条件：品牌GLP-1药物大幅降价使复合药失去价格优势
- 证伪条件：主要竞争对手以更低价格和更好服务抢夺大量用户
- 证伪条件：订阅用户流失率持续加速导致营收增长停滞

### management_governance: unknown

CEO Andrew Dudum和CFO Oluyemi Okupe在位。但2026年11月4日任命Dr. Andrew Huberman为非独立董事引发治理疑虑：(1)董事会明确认定其不符合独立性要求；(2)同时签订大额关联交易（咨询$3.5M/年+播客营销$5M/年，Huberman个人利益约$2.1M/年）；(3)未被任命至任何委员会。非独立董事+大额关联交易的组合构成治理风险，需进一步审查其对股东利益的影响。

- 支持 [ev_94da73204b31775e](https://www.sec.gov/Archives/edgar/data/1773751/000177375126000245/hims-20261104.htm) (primary-document): appointed Dr. Andrew Huberman, 51, to fill the newly created directorship, effective immediately
- 支持 [ev_8e169f33339d5a4e](https://www.sec.gov/Archives/edgar/data/1773751/000177375126000242/hims-20261109.htm) (primary-document): By: /s/ Oluyemi Okupe Oluyemi Okupe Chief Financial Officer (Principal Financial Officer)
- 支持 [ev_89e3fdbf58a0994c](https://www.sec.gov/Archives/edgar/data/1773751/000177375126000245/hims-20261104.htm) (primary-document): By: /s/ Andrew Dudum Andrew Dudum Chief Executive Officer
- 反证 [ev_0e061d6dc24d06d3](https://www.sec.gov/Archives/edgar/data/1773751/000177375126000245/hims-20261104.htm) (primary-document): Dr. Huberman has not been appointed to any committee of the Board and is not currently expected to be appointed to any committee
- 缺口：董事会其他九位成员的独立性信息
- 缺口：CEO/创始人持股比例及投票权结构
- 缺口：高管薪酬与业绩挂钩的具体条款
- 缺口：审计委员会对关联交易的审批记录
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现Huberman关联交易未经审计委员会正式批准
- 证伪条件：更多非独立董事被任命导致独立董事占比低于NYSE要求
- 证伪条件：CEO或其他高管面临调查或诉讼

## HNGE · complete

审查记录：`state/serenity-reviews/HNGE-claudecli-fb2f57b70dcd3ba13029.json`

### supply_chain_map: unknown

证据显示Hinge Health是数字化MSK（肌骨）健康平台公司，下游用户为雇主和健康计划客户，产品包括MSK平台、偏头痛护理和胃肠道护理。但上游供应链（如合同医疗专业人员来源、AI基础设施供应商）在证据包中未具体披露，无法完整绘制供应链图。

- 支持 [ev_8928605ab02c5633](https://www.sec.gov/Archives/edgar/data/1673743/000162828026072251/hnge-20260930.htm) (primary-document): our ability to contract with qualified licensed health professionals
- 支持 [ev_8928605ab02c5633](https://www.sec.gov/Archives/edgar/data/1673743/000162828026072251/hnge-20260930.htm) (primary-document): our ability to enhance our platform and programs or develop new programs, capabilities, features, and products, including HingeSelect, our high-performance provider network for MSK care, our Migraine Care Program, offering rapid drug-free pain relief, personalized trigger management, and proactive prevention and our integrated Gastrointestinal Care Program
- 缺口：上游关键供应商（云基础设施、传感器硬件、AI模型供应商）的具体披露
- 缺口：供应商集中度或替代壁垒的数据
- 缺口：具体客户名称和合同关系
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现Hinge Health依赖单一云供应商或传感器制造商且无法替代
- 证伪条件：下游客户（雇主/健康计划）高度集中于少数大客户

### chokepoint_evidence: unknown

Hinge Health是数字健康SaaS平台，非物理供应链瓶颈型公司。数字MSK治疗市场竞争者众多（Omada、Sword Health等），不存在供应集中度或替代壁垒的证据。AI相关性本身不构成chokepoint。

- 反证 [ev_8928605ab02c5633](https://www.sec.gov/Archives/edgar/data/1673743/000162828026072251/hnge-20260930.htm) (primary-document): our ability to compete successfully in our competitive market
- 缺口：任何表明供应集中度（>50%市场份额）的证据
- 缺口：替代壁垒或转换成本的具体数据
- 缺口：下游客户无法绕开Hinge Health的证据
- 缺口：反证只是通用风险条款或记录字段，不是针对公司的直接反证
- 证伪条件：发现Hinge Health在某一关键环节拥有不可替代的专利或独占许可

### customer_dependency: partial

XBRL数据中披露了客户集中度风险（SignificantClients），表明存在重要客户，但证据包中未披露具体客户名称或合同细节。营收增长52.4%暗示客户采纳度强劲，但缺乏具体客户依赖关系的直接证据。

- 支持 [ev_0bd158e028f6df7a](https://www.sec.gov/Archives/edgar/data/1673743/000162828026072251/hnge-20260930.htm) (primary-document): us-gaap:CustomerConcentrationRiskMember hnge:SignificantClientsMember us-gaap:SalesRevenueNetMember 2026-07-01 2026-09-30
- 支持 [ev_781f3cbe2288ad56](https://data.sec.gov/api/xbrl/companyfacts/CIK0001673743.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 234,970,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_8928605ab02c5633](https://www.sec.gov/Archives/edgar/data/1673743/000162828026072251/hnge-20260930.htm) (primary-document): our ability to attract and retain clients
- 缺口：具体大客户名称（如Fortune 500雇主或大型健康计划）
- 缺口：客户集中度的百分比数据
- 缺口：合同期限和续约率数据
- 证伪条件：发现前几大客户占收入超50%且合同即将到期
- 证伪条件：主要客户转向竞争对手的公开报道

### pure_play: unknown

Hinge Health核心业务为数字MSK治疗平台，属于AI医疗主题的纯粹暴露。但公司正扩展至偏头痛和胃肠道护理，并收购了Cylinder Health，业务逐渐多元化。作为AI医疗主题投资，主题纯度尚可但正在稀释。

- 反证 [ev_8928605ab02c5633](https://www.sec.gov/Archives/edgar/data/1673743/000162828026072251/hnge-20260930.htm) (primary-document): our ability to successfully develop, launch, and scale our Migraine Care Program and our Gastrointestinal Care Program, achieve clinical validation of such programs
- 反证 [ev_9b6e50ed804dcc5f](https://www.sec.gov/Archives/edgar/data/1673743/000162828026072251/hnge-20260930.htm) (primary-document): hnge:CylinderHealthInc.Member 2026-08-31 2026-08-31
- 缺口：各业务线的收入分拆数据
- 缺口：MSK业务占总收入的具体百分比
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：新业务线（偏头痛、GI）收入占比快速上升导致MSK主题稀释
- 证伪条件：未来大型非相关收购进一步分散业务焦点

### multi_node_control: unknown

证据中未发现Hinge Health控制两个或以上相连供应链节点的证据。公司是SaaS平台型企业，提供软件+临床服务，但这不构成传统供应链中的多节点垂直整合控制。

- 缺口：公司在供应链上下游的垂直整合证据
- 缺口：独占性上游技术或数据来源的披露
- 缺口：任何表明公司控制多个关键节点的证据
- 证伪条件：发现Hinge Health同时控制传感器硬件制造和AI算法两个关键环节且竞争者无法复制

### earnings_validation: pass

Q3 2026财报强劲：营收$2.35亿，同比增长52.4%；净利润$5740万（已盈利）；年初至今经营性现金流$2.59亿；现金$2.12亿。公司已从亏损转为盈利，财务数据有力验证增长论点。

- 支持 [ev_781f3cbe2288ad56](https://data.sec.gov/api/xbrl/companyfacts/CIK0001673743.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 234,970,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_781f3cbe2288ad56](https://data.sec.gov/api/xbrl/companyfacts/CIK0001673743.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 154,211,000, a change of +52.4%
- 支持 [ev_781f3cbe2288ad56](https://data.sec.gov/api/xbrl/companyfacts/CIK0001673743.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 57,398,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_781f3cbe2288ad56](https://data.sec.gov/api/xbrl/companyfacts/CIK0001673743.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): 259,098,000 for 2026-01-01 to 2026-09-30
- 支持 [ev_781f3cbe2288ad56](https://data.sec.gov/api/xbrl/companyfacts/CIK0001673743.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 211,553,000 for as of 2026-09-30
- 证伪条件：下一季度营收增速大幅放缓至20%以下
- 证伪条件：净利润转为亏损或经营性现金流转负
- 证伪条件：客户流失导致收入下降

### counter_thesis: partial

证据包涵盖部分风险因素（竞争、监管、客户留存），但缺乏对估值风险（$94亿市值对应约$9.4亿年化收入＝10x PS）、替代风险（其他数字健康平台）、以及宏观医疗支出压缩风险的深入分析。总裁离职和业务多元化也构成额外风险。

- 支持 [ev_8928605ab02c5633](https://www.sec.gov/Archives/edgar/data/1673743/000162828026072251/hnge-20260930.htm) (primary-document): our ability to compete successfully in our competitive market
- 支持 [ev_3146accd75511adf](https://www.sec.gov/Archives/edgar/data/1673743/000162828026072251/hnge-20260930.htm) (primary-document): changes in the healthcare regulatory environment, particularly in states where new regulations regarding telehealth and the use of AI in healthcare are being enacted
- 支持 [ev_8928605ab02c5633](https://www.sec.gov/Archives/edgar/data/1673743/000162828026072251/hnge-20260930.htm) (primary-document): our ability to attract and retain clients
- 反证 [ev_5a5b55675ef26313](https://news.google.com/rss/articles/CBMi4AFBVV95cUxNb2RPMERXUFdKMkxZbjhTQmJnNlZxcDdyY3VtbFd4RTFTbWZSUVFvdV9RRldJSUdjSWxHaDlSdkVNLVZIckZKRlpIXzR0ZzJjSGNfclhOaUk2V09sOHEydDJCMVFtQlpBWWs1NW0wRGFvZWNXdG54R2t0VzhFZkM5bHVlc1lMWUZyamRyQzRnRDlpWW5VRnd1eDZmU203WDlHeEwxUGlSeWYwMGkzNnEydnpDb1ZDVkh6YTdhWG1IaHItaVlPMVM2WUtPM2tqeHdveVVMbko4a1VsWVl4RUlNMw?oc=5) (news-feed): Hinge Health Clears Consensus But Misses The Whisper As Its Third Straight Raise Meets A Stock Priced Near Its Highs
- 缺口：具体竞争对手市场份额对比数据
- 缺口：估值倍数与同行业对比分析
- 缺口：医疗AI监管变化对业务模式的具体影响评估
- 缺口：客户续约率和净收入留存率数据
- 证伪条件：大型雇主客户转向竞争平台（如Sword Health、Omada）
- 证伪条件：FDA对AI医疗设备的新监管要求大幅增加合规成本
- 证伪条件：宏观经济下行导致雇主削减健康福利支出
- 证伪条件：股价已接近高点，估值压缩风险（news提到stock priced near its highs）

### management_governance: unknown

总裁James Pursley于2026年10月29日宣布辞职（2027年1月1日生效），CEO Daniel Perez兼任总裁。虽然披露称辞职非因分歧，且Pursley转任董事，但领导层过渡期仍需观察。公司联合创始人兼CEO的双重角色集中了权力。

- 缺口：Pursley离职的真实原因和背景
- 缺口：董事会独立性评估
- 缺口：其他高管稳定性数据
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：更多高管接连离职形成管理层动荡
- 证伪条件：CEO兼任总裁后决策质量下降
- 证伪条件：发现Pursley离职与未披露的业务问题有关

## HTFL · complete

审查记录：`state/serenity-reviews/HTFL-claude-5a16695d01f5b4cd6d9c.json`

### supply_chain_map: pass

上游为 CT 设备厂商与云，下游为医疗机构与付款方。

- 支持 [ev_077c4910f58a9b45](https://www.sec.gov/Archives/edgar/data/1464521/000146452126000042/htfl-20251231x10k.htm) (primary-document): The primary providers of imaging systems that perform these tests include Siemens Healthineers AG,
- 支持 [ev_5fea41e6c4e6e853](https://www.sec.gov/Archives/edgar/data/1464521/000146452126000042/htfl-20251231x10k.htm) (primary-document): Our cloud-based technology has enabled us to rapidly scale

### chokepoint_evidence: partial

I 类医保编码与 99% 覆盖构成报销壁垒；竞争者处于早期，但缺市场份额数据。

- 支持 [ev_90bebad72348b2f2](https://www.sec.gov/Archives/edgar/data/1464521/000146452126000042/htfl-20251231x10k.htm) (primary-document): Our Heartflow FFR CT Analysis is reimbursed under a Category I CPT code, 75580, effective as of January 1, 2024
- 支持 [ev_424579d58b144b0c](https://www.sec.gov/Archives/edgar/data/1464521/000146452126000042/htfl-20251231x10k.htm) (primary-document): has established coverage policies representing approximately 99% of covered lives in the United States
- 反证 [ev_8acb623e2fbaf122](https://www.sec.gov/Archives/edgar/data/1464521/000146452126000042/htfl-20251231x10k.htm) (primary-document): earlier-stage companies such as Cleerly, Inc., Elucid Bioimaging Inc. and Keya Medical Technology Co., Ltd.

### customer_dependency: pass

超过 1,800 家机构采用。

- 支持 [ev_4bcdceb6fc930ce8](https://www.sec.gov/Archives/edgar/data/1464521/000146452126000042/htfl-20251231x10k.htm) (primary-document): installed base of more than 1,465 accounts in the United States as of December 31, 2025
- 支持 [ev_ffe70cc39b08dfdf](https://www.sec.gov/Archives/edgar/data/0001464521/000146452126000171/htfl-20261112xex99_1.htm) (primary-document): Heartflow has been adopted by more than 1, 8 00 institutions globally

### pure_play: pass

全部业务为 AI 冠脉分析软件，有大量临床证据支持。

- 支持 [ev_bf318173bc5e1b97](https://www.sec.gov/Archives/edgar/data/1464521/000146452126000042/htfl-20251231x10k.htm) (primary-document): results published in over 600 peer-reviewed clinical publications

### multi_node_control: partial

软件、临床证据与报销联动，但不控制扫描设备。

- 缺口：节点控制的一手证据

### earnings_validation: pass

Q3 收入增长 57%，毛利率 83.6%。

- 支持 [ev_0a15101a0bff206e](https://www.sec.gov/Archives/edgar/data/0001464521/000146452126000171/htfl-20261112xex99_1.htm) (primary-document): Total revenue of $72.9 million, a 57% increase year-over-year
- 支持 [ev_7f2b61c3942377b2](https://www.sec.gov/Archives/edgar/data/0001464521/000146452126000171/htfl-20261112xex99_1.htm) (primary-document): Gross margin of 83.6%, non-GAAP gross margin of 83.8%

### counter_thesis: pass

估值与设备厂商替代风险已检验。

- 支持 [ev_2e5d800df6ce6c8b](https://www.sec.gov/Archives/edgar/data/1464521/000146452126000042/htfl-20251231x10k.htm) (primary-document): Current AHA and ACC guidelines support CCTA + Heartflow FFR CT Analysis as a more efficient care pathway.
- 反证 [ev_248c97e644075f2f](https://www.sec.gov/Archives/edgar/data/1464521/000146452126000042/htfl-20251231x10k.htm) (primary-document): These companies also manufacture CT scanners and therefore have a vested interest in growing the
- 证伪条件：斑块分析覆盖停滞在 75% 以下
- 证伪条件：医保支付标准下调

### management_governance: pass

按 Serenity 规则：领导层连续，且无未结调查或未定继任。通道文件确认：Farquhar（CEO）与Verghese（CFO）于2026年11月仍以各自职务提交Form 4，代理声明确认Weldon任董事会主席（任期至2028年）；所有文件均未披露任何政府、监管机构或董事会层面的公开调查，亦无职位空缺或未命名继任者的高管变动；主要治理风险为薪酬委员会成员Lightcap与Tansey控制公司主要股东实体，且含CFO在内的多名董事/高管参与了IPO前关联方融资。

- 支持 [ev_0f2a3aece7a9c478](https://www.sec.gov/Archives/edgar/data/1464521/000146452126000168/xslF345X06/form4.xml) (primary-document): Relationship of Reporting Person(s) to Issuer (Check all applicable) X Director 10% Owner X Officer (give title below) Other (specify below) Chief Executive Officer
- 支持 [ev_65ddc8fb3a55e593](https://www.sec.gov/Archives/edgar/data/1464521/000146452126000166/xslF345X06/form4.xml) (primary-document): Relationship of Reporting Person(s) to Issuer (Check all applicable) Director 10% Owner X Officer (give title below) Other (specify below) Chief Financial Officer
- 支持 [ev_87b994d2fe944e2c](https://www.sec.gov/Archives/edgar/data/1464521/000119312526189307/d54880ddef14a.htm) (primary-document): John C.M. Farquhar 54 President, Chief Executive Officer & Director Vikram Verghese 42 Chief Financial Officer Campbell D.K. Rogers, M.D. 64 Chief Medical Officer
- 支持 [ev_fe60fe626eea4aa4](https://www.sec.gov/Archives/edgar/data/1464521/000119312526189307/d54880ddef14a.htm) (primary-document): The Board believes that the current Board leadership structure, with Mr. Weldon serving as our Chair and Mr. Farquhar serving as our Chief Executive Officer, provides effective independent oversight of management.
- 支持 [ev_9e1fc550f01bcf15](https://www.sec.gov/Archives/edgar/data/1464521/000119312526189307/d54880ddef14a.htm) (primary-document): Class III directors consist of William C. Weldon and Wayne J. Riley, M.D., whose terms expire at the 2028 annual meeting of stockholders.
- 支持 [ev_1e8a37612e5a3b2a](https://www.sec.gov/Archives/edgar/data/1464521/000146452126000168/xslF345X06/form4.xml) (primary-document): The option vests and becomes exercisable in monthly installments until July 1, 2027, subject to continued service through the applicable vesting date. /s/ Nga Van, by power of attorney 11/10/2026

## HURA · complete

审查记录：`state/serenity-reviews/HURA-claudecli-a090acf913e35a2cec2b.json`

### supply_chain_map: unknown

上游依赖有限数量的第三方CMO和sole-source试剂/设备供应商，产品为IFx-2.0（固有免疫激动剂）、TBS-2025（VISTA抑制抗体）和DOR ADC，下游面向MCC和AML癌症患者。供应链有初步描述但缺乏具体供应商名称和定量关系。

- 支持 [ev_356ecb2a8a0f13ba](https://www.sec.gov/Archives/edgar/data/1498382/000119312526134950/hura-20251231.htm) (primary-document): We currently depend on a limited number of vendors for certain materials and equipment used in the manufacture of our product candidates
- 支持 [ev_356ecb2a8a0f13ba](https://www.sec.gov/Archives/edgar/data/1498382/000119312526134950/hura-20251231.htm) (primary-document): For some of these reagents, equipment, and materials, we rely and may in the future rely on sole source vendors or a limited number of vendors
- 支持 [ev_191a607c3bcd0922](https://www.sec.gov/Archives/edgar/data/1498382/000119312526134950/hura-20251231.htm) (primary-document): We anticipate reliance on a limited number of third-party manufacturers exposes us to the following risks
- 缺口：具体CMO供应商名称（除被诉的VGXI外）
- 缺口：试剂和关键原材料的具体供应商身份
- 缺口：下游患者群体的定量规模估计
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现公司已建立自有生产能力，不再依赖第三方CMO
- 证伪条件：发现关键供应商合同已解除且无替代方案

### chokepoint_evidence: unknown

TuHURA是临床阶段肿瘤免疫药企，无证据表明其在任何供应链节点拥有垄断或寡头地位。其技术（DOR平台、VISTA抑制）有专利保护但未证明构成不可替代的瓶颈。与Serenity方法关注的物理供应链瓶颈不同。

- 支持 [ev_e617d8a5b46f3e4c](https://www.sec.gov/Archives/edgar/data/1498382/000119312526459311/hura-ex99_1.htm) (primary-document): Received a new U.S. Patent broadening coverage for its VISTA Inhibitor, TBS-2025. The patent extends coverage to include bispecific/multi-specific antibodies across all classes of human antibodies
- 缺口：VISTA靶点药物竞争格局分析
- 缺口：DOR技术平台相对于其他免疫疗法的不可替代性证据
- 缺口：MCC治疗领域的供应集中度数据
- 证伪条件：发现多个竞争对手拥有类似VISTA抑制或DOR技术的产品进入临床
- 证伪条件：发现MCC免疫治疗有多种等效替代方案

### customer_dependency: unknown

公司处于临床阶段，无已上市产品，零收入，无客户采用数据。IFx-2.0与Keytruda联用的初步临床数据显示3名患者有客观应答，但这是临床试验而非商业客户关系。

- 支持 [ev_9c60748efd89a683](https://www.sec.gov/Archives/edgar/data/1498382/000119312526459311/hura-ex99_1.htm) (sec-8k): Preliminary results demonstrated major objective partial responses in each of the first 3 patients, constituting major objective tumor responses, which are ongoing for more than six months
- 缺口：任何商业客户、医院或支付方的采用/合作协议
- 缺口：与Merck（Keytruda生产商）的正式合作或供应协议
- 缺口：目标患者人群的市场渗透预期
- 证伪条件：发现公司已与医疗系统或药企签订商业合作或预购协议
- 证伪条件：发现Keytruda联用方案被Merck正式纳入研发管线

### pure_play: partial

公司明确在单一可报告业务部门运营，专注于癌症免疫治疗。但无收入，因此无法用收入比例衡量主题暴露度。作为临床阶段公司，100%资源投入肿瘤免疫领域。

- 支持 [ev_bbca7a0fc71e3699](https://www.sec.gov/Archives/edgar/data/1498382/000119312526134950/hura-20251231.htm) (primary-document): The Company operates in one reportable segment, which includes all activities related to advancing therapies for cancer treatment
- 支持 [ev_bbca7a0fc71e3699](https://www.sec.gov/Archives/edgar/data/1498382/000119312526134950/hura-20251231.htm) (primary-document): There is no segment revenue for the years ended December 31, 2025, and 2024
- 缺口：收入分部数据（公司尚无收入）
- 缺口：AI医药主题的具体关联性论证
- 证伪条件：发现公司正在开发与肿瘤免疫无关的业务线分散资源

### multi_node_control: unknown

公司拥有多个产品候选（IFx-2.0、TBS-2025、DOR ADC），但这些是不同的药物项目，非同一供应链的多个节点控制。公司许可外部IP（Moffitt、WVURC），依赖第三方CMO生产，不控制上下游节点。

- 缺口：公司控制供应链上下游连接节点的证据
- 缺口：垂直整合生产能力的证据
- 证伪条件：发现公司已收购或建立覆盖从原料到成品的垂直整合能力

### earnings_validation: unknown

临床准备阶段公司，零收入符合预期。Q3 2026末现金仅190万美元，9个月经营现金流出1810万美元（月均约200万），独立现金仅支撑不到1个月。但公司披露了来自最大股东Parkview的5000万美元信贷额度，已提取920万美元，剩余约4080万美元可用，管理层称此为非稀释性融资。尽管如此，前瞻性声明警告信贷额度资金可能不足。现金极低但有已披露融资渠道，不满足fail标准（需无已披露融资），但无法确认能完整资助下一里程碑。

- 支持 [ev_a35552eb6911f3e5](https://www.sec.gov/Archives/edgar/data/1498382/000119312526459311/hura-ex99_1.htm) (primary-document): Cash and cash equivalents of $1.9 million at September 30, 2026. The Company received $9.2 million in gross proceeds as of September 30, 2026, on the Parkview credit facility
- 支持 [ev_a35552eb6911f3e5](https://www.sec.gov/Archives/edgar/data/1498382/000119312526459311/hura-ex99_1.htm) (primary-document): Net cash outflows from operating activities were ($18.1) million and ($22.1) million for the 9 months ended September 30, 2026, and 2025, respectively
- 缺口：Parkview信贷额度的具体条款和提取条件
- 缺口：信贷额度剩余可用额度的确认
- 缺口：未来12个月预期现金需求的详细预算
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现Parkview信贷额度已终止或附有无法满足的提取条件
- 证伪条件：发现公司已宣布稀释性融资（增发股份）
- 证伪条件：发现下一季度现金降至零且无新融资到位

### counter_thesis: unknown

关键反面论点：(1)现金仅190万，runway不到1个月，financingRisk为true，即使有信贷额度也面临严重融资风险，股权稀释性融资极可能发生；(2)与VGXI的诉讼表明关键CMO未能交付GMP级质粒DNA，直接威胁临床试验材料供应；(3)肿瘤免疫领域竞争激烈，IFx-2.0仅有3名患者初步数据；(4)TBS-2025刚获IND许可，处于极早期。按小盘准备阶段规则，runway不到12个月且financingRisk为true，股权融资稀释是必须指出的反面路径。但缺乏具体竞品数据和替代疗法的定量比较。

- 支持 [ev_a35552eb6911f3e5](https://www.sec.gov/Archives/edgar/data/1498382/000119312526459311/hura-ex99_1.htm) (primary-document): Cash and cash equivalents of $1.9 million at September 30, 2026. The Company received $9.2 million in gross proceeds as of September 30, 2026, on the Parkview credit facility
- 支持 [ev_ea1ee4433d1486f8](https://www.sec.gov/Archives/edgar/data/1498382/000119312526134950/hura-20251231.htm) (primary-document): The immuno-oncology industry is also rapidly developing, and our competitors may introduce new technologies improving the immune response to cancer that render our technologies obsolete or less attractive
- 缺口：具体竞品（如其他VISTA抑制剂、MCC疗法）的临床进展对比
- 缺口：Parkview信贷额度可用余额的独立确认
- 缺口：VGXI诉讼对Phase 3时间线的具体影响评估
- 缺口：MCC和AML适应症的竞争格局定量数据
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：Parkview信贷额度被终止或冻结，公司被迫进行大规模稀释性增发
- 证伪条件：VGXI诉讼导致Phase 3临床试验材料供应长期中断
- 证伪条件：竞争对手在MCC适应症获得FDA加速批准，抢占先机
- 证伪条件：IFx-2.0在更大样本中未能重复初步3名患者的应答结果
- 证伪条件：TBS-2025 Phase 1b安全性数据出现剂量限制性毒性

### management_governance: partial

CEO为Dr. James Bianco（总裁兼首席执行官），有Dan Dearborn的雇佣协议。内部控制截至2025年12月31日被评估为有效。公司已采纳道德准则。但董事会详细构成、独立董事比例、审计委员会信息均引用至尚未提交的代理声明，无法验证。公司正在进行针对供应商VGXI的诉讼，这是公司主动起诉而非被调查。

- 支持 [ev_979a16445aa7819b](https://www.sec.gov/Archives/edgar/data/1498382/000119312526134950/hura-20251231.htm) (primary-document): our management concluded that, as of December 31, 2025, our internal control over financial reporting was effective
- 支持 [ev_9c60748efd89a683](https://www.sec.gov/Archives/edgar/data/1498382/000119312526459311/hura-ex99_1.htm) (sec-8k): said Dr. James Bianco, President and Chief Executive Officer of TuHURA Biosciences
- 支持 [ev_b71c35249c809196](https://www.sec.gov/Archives/edgar/data/1498382/000119312526134950/hura-20251231.htm) (primary-document): On December 12, 2025, we filed an action filed in the Delaware Court of Chancery styled TuHURA Biosciences, Inc. v. VGXI, Inc. and GeneOne Life Sciences, Inc.
- 缺口：董事会完整成员名单及独立性
- 缺口：审计委员会和薪酬委员会构成
- 缺口：CEO/管理层的详细履历和任期
- 缺口：2026年代理声明中的治理详情
- 证伪条件：发现管理层面临SEC调查或股东诉讼
- 证伪条件：发现关键高管突然离职或继任计划缺失
- 证伪条件：发现内部控制在2026年出现重大缺陷

## HYPR · complete

审查记录：`state/serenity-reviews/HYPR-claudecli-da0fe078c99ff322c561.json`

### supply_chain_map: partial

上游信息较充分：Benchmark为合同制造商，欧洲单一来源磁体供应商，有限数量的零部件供应商。产品为Swoop®便携式MRI系统。下游客户未具名，仅知美国收入占77%，三个客户各占应收账款10%以上但未披露身份。供应链上游→产品映射清晰，但下游客户关系缺乏具体信息。

- 支持 [ev_ee69aac98d0a28ab](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): we rely on Benchmark to purchase the magnet used in our Swoop® system, which is a key custom-made component manufactured by a single source supplier in Europe
- 支持 [ev_ee69aac98d0a28ab](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): We rely on a limited number of suppliers to manufacture components for our products, including in some cases only a single supplier for some of our components
- 支持 [ev_dec7f4d2c972b9a4](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): U.S. revenue accounted for 77 % and 50 % of total revenue, respectively, while outside of the U.S. revenue accounted for 23 % and 50 %
- 缺口：下游客户具体名称（医院、医疗系统等）
- 缺口：磁体单一来源供应商的具体名称
- 缺口：Benchmark以外的其他关键零部件供应商名称
- 证伪条件：发现Benchmark或欧洲磁体供应商已被替换或增加备选供应商
- 证伪条件：下游客户集中度发生重大变化的披露

### chokepoint_evidence: unknown

Hyperfine自身不控制任何供应链瓶颈节点。相反，公司依赖单一来源供应商，说明它处于瓶颈的下游被动端。便携式MRI是一种差异化产品，但没有证据表明其在供应链中构成不可替代的卡脖子节点。FDA设备授权仅证明产品获批，不构成供应集中度证据。

- 反证 [ev_ee69aac98d0a28ab](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): Our reliance on a limited number of suppliers increases our risks, since we do not currently have alternative or replacement suppliers beyond these key parties
- 缺口：Hyperfine在便携式MRI市场的市场份额数据
- 缺口：便携式MRI领域竞争对手数量和替代品信息
- 缺口：客户转换成本或锁定机制的证据
- 证伪条件：发现Hyperfine占便携式MRI全球出货量的绝大部分且无可替代
- 证伪条件：发现医院系统一旦采用Swoop®即面临多年替换壁垒

### customer_dependency: partial

2025年无单一客户占收入10%以上，说明客户分散。但三个客户各占应收账款10%以上（$1,346K、$1,041K、$922K），表明存在一定集中度。所有客户均未具名，无法确认具体采用情况或设计锁定关系。

- 支持 [ev_dec7f4d2c972b9a4](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): For the year ended December 31, 2025 , there were no customers that represented 10% or more of total net revenue
- 支持 [ev_dec7f4d2c972b9a4](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): As of December 31, 2025 , there were three customers that each accounted for more than 10% of the Company's total gross accounts receivable in the amount of $ 1,346 , $ 1,041 , and $ 922 , respectively
- 缺口：具名客户（医院名称或医疗系统名称）
- 缺口：客户采用案例或部署数量
- 缺口：客户续约率或合同期限信息
- 证伪条件：发现主要客户退回设备或终止合同
- 证伪条件：发现竞争对手便携式MRI被大型医院系统采用替代Swoop®

### pure_play: pass

公司明确披露仅运营单一业务分部，所有活动均围绕Swoop®系统的生产、供应、服务和商业化。2025年收入拆分为设备$11,398K和服务$2,165K，全部与便携式MRI相关。属于纯正的便携式MRI标的。

- 支持 [ev_9fc53ff92f3e169e](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): The Company operates in one business segment, which includes all activities related to production, supply, service and commercialization of the Swoop® system
- 支持 [ev_a0e2d98bfbea9a4c](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): Device Point in time $ 11,398 $ 10,450 Service Over time 2,165 2,440 Total revenue $ 13,563 $ 12,890
- 证伪条件：公司进入与便携式MRI无关的新业务线，稀释主题敞口

### multi_node_control: unknown

无证据表明Hyperfine控制供应链中两个或以上相连节点。公司依赖外部合同制造商Benchmark和单一来源磁体供应商，自身仅进行产品设计和商业化，不具备垂直整合特征。

- 反证 [ev_bbbb5033d7dfd8de](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): We rely on contract manufacturers and component suppliers to provide the specific components and manufacturing services necessary to produce our finished medical devices
- 缺口：自有制造能力或关键零部件内部生产的证据
- 缺口：对上游材料或下游分销渠道的控制证据
- 证伪条件：发现Hyperfine内部制造关键组件（如磁体）并控制分销渠道

### earnings_validation: partial

有明确的财务数据：Q3 2026收入$5.96M，同比增长73.4%；净亏损$5.98M；现金$37.87M，约15个月跑道。作为成长期小盘股，收入增长强劲但仍亏损。现金可支撑未来12个月以上运营。但$59M市值对应~$24M年化收入，盈利路径尚不明确。

- 支持 [ev_e7e6c34680f95f60](https://data.sec.gov/api/xbrl/companyfacts/CIK0001833769.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 5,960,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_e7e6c34680f95f60](https://data.sec.gov/api/xbrl/companyfacts/CIK0001833769.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 37,872,000 for as of 2026-09-30
- 支持 [ev_e7e6c34680f95f60](https://data.sec.gov/api/xbrl/companyfacts/CIK0001833769.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -5,981,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_dec7f4d2c972b9a4](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): the Company believes that it will have sufficient cash resources and anticipated cash flows to fund its operations for at least the next 12 months
- 缺口：毛利率趋势及盈亏平衡时间表
- 缺口：运营杠杆或规模化后的单位经济模型
- 缺口：管理层对盈利路径的指引
- 证伪条件：现金跑道降至12个月以下且无融资安排
- 证伪条件：收入增速大幅放缓或客户流失导致收入下降

### counter_thesis: partial

识别到多项风险：(1)供应端——依赖单一来源磁体供应商和Benchmark，中断风险高；(2)治理——历史上存在内控重大缺陷；(3)估值——$59M市值极小，流动性风险；(4)现金消耗——月均烧钱$2.48M，15个月跑道；(5)ATM融资计划存在稀释风险。但缺乏具名竞争对手抢占份额的具体证据，替代产品威胁未量化，地缘政治风险（欧洲磁体供应商）未充分评估。

- 支持 [ev_ee69aac98d0a28ab](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): In the event of interruption from any of our suppliers, we may not be able to increase capacity from other sources or develop alternate or secondary sources without incurring material additional costs and substantial delays
- 支持 [ev_09fa513934559994](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): We have in the past experienced material weaknesses in our internal control over financial reporting, and if we experience such material weaknesses in our internal control over financial reporting in the future
- 支持 [ev_ee69aac98d0a28ab](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): Third-party suppliers utilized by our manufacturer, Benchmark have and may continue to impose pricing pressures
- 缺口：便携式MRI市场中具名竞争对手及其市场份额
- 缺口：传统MRI厂商（如Siemens、GE、Philips）推出便携式产品的可能性评估
- 缺口：地缘政治对欧洲磁体供应的具体影响分析
- 缺口：估值与同行对比分析
- 证伪条件：大型MRI厂商推出竞品便携式MRI并获FDA批准
- 证伪条件：欧洲磁体供应商中断导致无法交付
- 证伪条件：关键客户转向竞争产品
- 证伪条件：融资失败导致现金不足以支撑运营

### management_governance: partial

管理团队已披露：CEO Maria Sainz、CFO Brett Hale、COO Thomas Teisseyre。创始人Jonathan Rothberg为知名连续创业者，获总统科技创新奖章。董事会承诺合规治理。但公司曾存在财务报告内控重大缺陷，虽声称已修复，但历史记录构成治理风险。无法确认继任计划的具体内容。

- 支持 [ev_9ff9f094f5a8b08d](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): Legacy Hyperfine was founded in 2014 by Dr. Jonathan Rothberg, a serial entrepreneur that received the Presidential Medal of Technology and Innovation in 2016
- 支持 [ev_9ff9f094f5a8b08d](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): Maria Sainz President, Chief Executive Officer and Director Brett Hale Chief Administrative Officer, Chief Financial Officer, Treasurer and Corporate Secretary
- 支持 [ev_9ff9f094f5a8b08d](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): Our board of directors is committed to robust corporate governance practices, risk oversight, stockholder rights, corporate sustainability, ethics and compliance
- 反证 [ev_09fa513934559994](https://www.sec.gov/Archives/edgar/data/1833769/000119312526114044/hypr-20251231.htm) (primary-document): We have in the past experienced material weaknesses in our internal controls over financial reporting that have required us to expend substantial time and effort to remediate
- 缺口：继任计划的具体细节
- 缺口：内控重大缺陷修复后的独立审计确认
- 缺口：高管薪酬与股东利益对齐情况
- 证伪条件：内控重大缺陷再次出现
- 证伪条件：关键高管突然离职且无继任安排
- 证伪条件：发现未披露的关联方交易或治理违规

## IBIO · complete

审查记录：`state/serenity-reviews/IBIO-claudecli-3aabfb68e13b5fb4a1f8.json`

### supply_chain_map: partial

证据显示iBio是一家药物发现公司，拥有IBIO-600和IBIO-610两个临床阶段候选药物（靶向肥胖症），并与Astralbio签有许可协议（肌肉抑制素、激活素E、淀粉素）。可识别出上游为许可的知识产权和研发投入，下游为合作伙伴（Astralbio）。但证据包中缺乏对具体原料供应商、CDMO/CMO生产关系的描述，供应链图谱不完整。

- 支持 [ev_134b7379bf17f666](https://clinicaltrials.gov/study/NCT07487376) (clinicaltrials-gov): A Study to Evaluate the Safety, Tolerability, Pharmacokinetics, and Pharmacodynamics of a Single Dose of IBIO-600 in Overweight or Obese Adults
- 支持 [ev_284e9ecdb025afeb](https://clinicaltrials.gov/study/NCT07890870) (clinicaltrials-gov): A Study to Evaluate a Single Dose of IBIO-610 in Participant With Obesity.
- 支持 [ev_917906f6062a4e2e](https://www.sec.gov/Archives/edgar/data/1420720/000142072026000036/ibio-20260930x10q.htm) (primary-document): ibio:ExclusiveLicenseAgreementWithAstralbioForAmylinMember 2026-08-27 2026-08-27
- 支持 [ev_60f1bc7bb25f9d24](https://www.sec.gov/Archives/edgar/data/1420720/000142072026000036/ibio-20260930x10q.htm) (primary-document): ibio:CollaborativeRevenuesMember 2026-07-01 2026-09-30
- 缺口：具体CDMO/CMO合同制造商信息
- 缺口：原料药(API)供应商关系
- 缺口：下游患者群体或商业化渠道的具体描述
- 证伪条件：发现公司使用通用外包CRO/CDMO，无任何专有供应关系
- 证伪条件：产品管线全部终止，供应链关系不再存在

### chokepoint_evidence: unknown

iBio是一家早期阶段药物发现公司，处于Phase 1临床试验阶段。证据包中没有任何供应集中度、替代壁垒或关键投入品瓶颈的信息。肥胖症药物领域竞争者众多（GLP-1类药物已商业化），iBio不控制任何稀缺供应节点。仅凭AI相关性不足以通过此门。

- 反证 [ev_134b7379bf17f666](https://clinicaltrials.gov/study/NCT07487376) (clinicaltrials-gov): Highest listed phase: Phase 1. Overall status: RECRUITING. Start date: 2026-05-24
- 反证 [ev_284e9ecdb025afeb](https://clinicaltrials.gov/study/NCT07890870) (clinicaltrials-gov): Highest listed phase: Phase 1. Overall status: NOT_YET_RECRUITING. Start date: 2026-12
- 缺口：供应集中度数据（如全球供应商数量、市场份额）
- 缺口：替代品切换成本或时间证据
- 缺口：任何专有原料或平台技术的不可替代性证据
- 缺口：反证只是通用风险条款或记录字段，不是针对公司的直接反证
- 证伪条件：发现该公司拥有独特的不可替代的药物递送平台
- 证伪条件：发现某关键原料仅有极少数供应商且iBio控制其中之一

### customer_dependency: partial

XBRL标签显示存在客户集中度风险和合作收入，且有与Astralbio的多项独家许可协议。Q1 FY2027合作收入约107.5万美元。但证据包中没有具体披露客户名称、采用规模或设计胜出详情，仅有XBRL字段名称级别的信息。

- 支持 [ev_9df67b9cf32943c9](https://www.sec.gov/Archives/edgar/data/1420720/000142072026000036/ibio-20260930x10q.htm) (primary-document): us-gaap:SalesRevenueNetMember us-gaap:CustomerConcentrationRiskMember 2026-07-01 2026-09-30
- 支持 [ev_60f1bc7bb25f9d24](https://www.sec.gov/Archives/edgar/data/1420720/000142072026000036/ibio-20260930x10q.htm) (primary-document): ibio:CollaborativeRevenuesMember 2025-07-01 2025-09-30
- 支持 [ev_917906f6062a4e2e](https://www.sec.gov/Archives/edgar/data/1420720/000142072026000036/ibio-20260930x10q.htm) (primary-document): ibio:ExclusiveLicenseAgreementWithAstralbioForActivinEMember 2025-04-21 2025-04-21
- 支持 [ev_d3c7121718573d2a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001420720.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 1,075,000 for 2026-07-01 to 2026-09-30
- 缺口：Astralbio合作的具体条款、里程碑付款和商业化分成
- 缺口：除Astralbio外的其他客户或合作伙伴详情
- 缺口：下游药企对iBio管线的具体采用/承诺证据
- 证伪条件：Astralbio终止许可协议
- 证伪条件：发现合作收入为一次性款项而非持续关系

### pure_play: partial

iBio专注于药物发现领域，拥有针对肥胖症的IBIO-600和IBIO-610管线，以及与Astralbio的多个许可协议（肌肉抑制素、激活素E、淀粉素）。从管线来看主题集中于代谢/肥胖领域。但证据包缺乏分部收入或业务分部的明确描述，无法精确量化主题收入占比。作为准备阶段公司，收入极少，纯度评估主要依赖管线方向。

- 支持 [ev_134b7379bf17f666](https://clinicaltrials.gov/study/NCT07487376) (clinicaltrials-gov): A Study to Evaluate the Safety, Tolerability, Pharmacokinetics, and Pharmacodynamics of a Single Dose of IBIO-600 in Overweight or Obese Adults
- 支持 [ev_284e9ecdb025afeb](https://clinicaltrials.gov/study/NCT07890870) (clinicaltrials-gov): A Study to Evaluate a Single Dose of IBIO-610 in Participant With Obesity.
- 支持 [ev_917906f6062a4e2e](https://www.sec.gov/Archives/edgar/data/1420720/000142072026000036/ibio-20260930x10q.htm) (primary-document): ibio:ExclusiveLicenseAgreementWithAstralbioForMyostatinMember 2025-01-28 2025-01-28
- 缺口：分部收入或业务分部的正式披露
- 缺口：AI药物发现平台技术的具体描述
- 缺口：非肥胖管线资产的详细说明以评估多元化程度
- 证伪条件：发现公司大部分资产或未来收入来自非AI/非药物发现业务
- 证伪条件：发现已出售或停止核心药物发现业务

### multi_node_control: unknown

证据包中没有任何信息表明iBio控制供应链中的两个或以上相连节点。公司是一家早期药物发现公司，拥有许可协议和临床候选药物，但没有垂直整合（如同时控制药物发现+生产+分销）的证据。许可协议将部分商业化权利授予了Astralbio，这反而表明公司并不控制下游。

- 反证 [ev_917906f6062a4e2e](https://www.sec.gov/Archives/edgar/data/1420720/000142072026000036/ibio-20260930x10q.htm) (primary-document): ibio:ExclusiveLicenseAgreementWithAstralbioForAmylinMember 2026-08-27 2026-08-27
- 缺口：垂直整合生产或分销能力的证据
- 缺口：自有生产设施的描述
- 缺口：控制上游原料供应的证据
- 缺口：反证只是通用风险条款或记录字段，不是针对公司的直接反证
- 证伪条件：发现公司拥有自有GMP生产设施并直接控制临床试验供应链

### earnings_validation: unknown

作为准备阶段（Phase 1）公司，不以收入评判。关键指标：现金45,435,000美元（2026-09-30），季度运营现金流出-9,387,000美元（约每月313万美元），估算跑道约24.5个月，足以支撑下一阶段里程碑。R&D支出650万美元/季度与Phase 1临床试验计划一致。但净亏损-755万美元/季度，且历史上频繁进行股权融资（多次证券购买协议和ATM协议），稀释风险存在。标记为partial而非pass，因为缺乏对财务可持续性的管理层叙述性讨论。

- 支持 [ev_d3c7121718573d2a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001420720.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 45,435,000 for as of 2026-09-30
- 支持 [ev_d3c7121718573d2a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001420720.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -9,387,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_d3c7121718573d2a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001420720.json) (sec-companyfacts): R&D expense (ResearchAndDevelopmentExpense): 6,650,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_d3c7121718573d2a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001420720.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -7,551,000 for 2026-07-01 to 2026-09-30
- 缺口：管理层对未来12-18个月资金充足性的讨论（going concern语言）
- 缺口：现金储备中短期投资的流动性详情
- 缺口：未来临床试验预算和里程碑时间表
- 缺口：引用不存在或原文无法匹配
- 证伪条件：going concern意见或审计师对持续经营能力的质疑
- 证伪条件：现金跑道低于12个月且无已落实的融资安排

### counter_thesis: partial

识别出以下反面论点：1）Phase 1阶段药物成功率极低（历史上约10%进入Phase 2），两个候选药物均处于最早期；2）肥胖症市场已被GLP-1类药物（Lilly、Novo Nordisk）主导，新进入者面临巨大竞争壁垒；3）公司历史上频繁通过股权融资稀释股东（2022、2023、2024、2025、2026年均有证券发行），尽管当前跑道约24.5个月（financingRisk为false），但长期稀释模式明显；4）市值仅5300万美元，流动性风险高；5）XBRL数据显示季度收入仅107.5万美元，远不足以覆盖运营支出。但证据包缺乏竞争格局和替代疗法的详细比较数据，counter分析不完整。

- 支持 [ev_134b7379bf17f666](https://clinicaltrials.gov/study/NCT07487376) (clinicaltrials-gov): A registry record shows the trial exists and its stage; it does not show results, approval or revenue
- 支持 [ev_9df67b9cf32943c9](https://www.sec.gov/Archives/edgar/data/1420720/000142072026000036/ibio-20260930x10q.htm) (primary-document): ibio:SecuritiesPurchaseAgreement2026Member 2026-01-08 2026-01-08
- 支持 [ev_d3c7121718573d2a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001420720.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 1,075,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_9df67b9cf32943c9](https://www.sec.gov/Archives/edgar/data/1420720/000142072026000036/ibio-20260930x10q.htm) (primary-document): ibio:PreFundedWarrants2026Member ibio:SecuritiesPurchaseAgreement2026Member 2026-01-08
- 反证 [ev_d3c7121718573d2a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001420720.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 100,000, a change of +975.0%
- 缺口：肥胖症竞争格局详细分析（GLP-1对比IBIO-600/610作用机制差异）
- 缺口：IBIO-600/610的具体靶点和差异化机制描述
- 缺口：管理层对竞争定位和市场策略的讨论
- 缺口：机构持仓和内部人交易数据
- 证伪条件：Phase 1临床数据显示安全性或药代动力学未达标
- 证伪条件：GLP-1或其他肥胖药物覆盖iBio靶点，使差异化论点失效
- 证伪条件：主要合作伙伴Astralbio终止许可协议
- 证伪条件：现金消耗速度加快导致跑道缩短至12个月以下
- 证伪条件：Nasdaq最低市值或股价合规警告

### management_governance: unknown

证据包中缺乏管理层和治理的实质性信息。XBRL数据显示存在高管股票期权授予（ExercisePrice1.40，行权价1.40美元）和非雇员董事RSU授予（2026-10-14后续事项），以及2023年和2020年的综合股权激励计划，但没有CEO/CFO姓名、任期、背景或任何治理问题的信息。无法评估领导层连续性或治理质量。

- 支持 [ev_60f1bc7bb25f9d24](https://www.sec.gov/Archives/edgar/data/1420720/000142072026000036/ibio-20260930x10q.htm) (primary-document): srt:ExecutiveOfficerMember us-gaap:ShareBasedPaymentArrangementEmployeeMember ibio:StockOptionIssuanceEmploymentInducementGrantMember
- 缺口：CEO/CFO姓名、任期和行业背景
- 缺口：董事会独立性和组成
- 缺口：管理层变动历史
- 缺口：任何正在进行的调查或诉讼详情
- 缺口：公司治理评级或机构投票建议
- 证伪条件：发现SEC执法行动或重大内部控制缺陷
- 证伪条件：发现CEO/CFO近期离职且无继任计划
- 证伪条件：发现重大关联交易或利益冲突

## IMTX · complete

审查记录：`state/serenity-reviews/IMTX-claudecli-2a4b8adac93b1e92ee4c.json`

### supply_chain_map: unknown

证据显示Immatics的产品为靶向PRAME的TCR T细胞疗法（IMA203CD8细胞治疗）和TCR双特异性分子（IMA402 TCER），下游为黑色素瘤、卵巢癌等实体瘤患者。但证据中未披露上游原材料供应商、制造合作方或关键物料的具体供应关系，供应链上游不完整。

- 支持 [ev_bb2b3f4ad149d97b](https://www.sec.gov/Archives/edgar/data/1809196/000095010326016136/dp255472_6k.htm) (primary-document): the Company announced updated clinical trial data from its ongoing phase 1b study with IMA402 PRAME TCR bispecific (TCER ® ) in a heavily pretreated patient population
- 支持 [ev_8e5bffae725dc44b](https://www.sec.gov/Archives/edgar/data/1809196/000095010326016061/dp255331_6k.htm) (primary-document): In 20 patients with gynecologic cancers (ovarian and uterine cancer) treated at clinically relevant dose levels
- 缺口：上游原材料与关键物料供应商披露
- 缺口：制造合作伙伴或CDMO关系
- 缺口：物料供应集中度与替代性数据
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现关键制造外包给单一CDMO且无备选方案
- 证伪条件：慢病毒载体或T细胞采集等关键上游物料出现供应瓶颈

### chokepoint_evidence: unknown

Immatics是临床阶段生物技术公司，非半导体/AI基础设施供应链企业。证据中未见任何供应集中度或替代壁垒的具体数据。PRAME靶点和TCR技术平台可能具有差异化，但证据中未量化竞争格局或供应瓶颈。

- 缺口：PRAME靶向TCR疗法领域的竞争者数量和市场集中度
- 缺口：TCR发现平台的技术壁垒或专利保护数据
- 缺口：替代疗法的开发周期与转换成本
- 证伪条件：多家竞争者拥有类似PRAME TCR疗法且进入同期临床阶段
- 证伪条件：靶点PRAME被证明非独特，其他免疫疗法可轻易替代

### customer_dependency: unknown

公司处于临床准备阶段，尚无商业化产品，因此无客户收入或采购关系可引用。证据仅显示临床试验入组患者，未见任何商业合作伙伴或下游客户的正式采购/使用披露。

- 缺口：商业客户或合作伙伴的正式采购/许可协议
- 缺口：医院或支付方的采纳意向数据
- 缺口：任何合作开发协议的财务条款
- 证伪条件：产品获批后主要市场支付方拒绝纳入报销目录
- 证伪条件：关键适应症中竞争疗法率先获批并锁定市场份额

### pure_play: unknown

证据显示Immatics所有已披露管线均聚焦于PRAME靶向TCR免疫疗法，包括细胞治疗（IMA203CD8）、双特异性分子（IMA402）和液体活检伴随诊断，高度集中于单一治疗方向。但因公司无收入，无法用收入占比量化主题暴露度。

- 支持 [ev_bb2b3f4ad149d97b](https://www.sec.gov/Archives/edgar/data/1809196/000095010326016136/dp255472_6k.htm) (primary-document): IMA402 PRAME TCR bispecific (TCER ® ) in a heavily pretreated patient population with a median of three prior lines of therapy
- 缺口：收入分部数据（公司尚无商业收入）
- 缺口：非PRAME管线或非TCR业务的占比信息
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：公司大量资源转向非PRAME或非肿瘤领域，稀释主题集中度

### multi_node_control: unknown

证据表明Immatics在同一PRAME靶向治疗链上拥有多种模式：自体TCR T细胞疗法（IMA203CD8）、TCR双特异性分子（IMA402）以及专有液体活检PRAME伴随诊断。这构成了'诊断选患者→治疗'的两个连接节点，但尚未商业化验证这些节点的协同控制力。

- 缺口：诊断与治疗节点之间商业化协同的具体证据
- 缺口：制造环节是否自有或外包的信息
- 缺口：节点间排他性或锁定效应的数据
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：伴随诊断被第三方标准化测试替代，丧失患者筛选控制权
- 证伪条件：制造完全外包导致无法控制供应链关键节点

### earnings_validation: unknown

公司处于preparation阶段（Phase 3），无商业收入属正常情况。smallCapContext显示现金$345.9M、月度消耗$14.72M、跑道约23.5个月，表明可资助下一里程碑。但证据中的6-K仅为封面页，未包含具体财务数字可供引用。Q3 2026财报已发布但详细数据不在证据包中。

- 缺口：Q3 2026实际现金余额、运营费用和净亏损的具体数字
- 缺口：未来12个月资金需求的详细分解
- 缺口：任何合作里程碑付款或授权收入的披露
- 缺口：引用不存在或原文无法匹配
- 证伪条件：实际现金余额大幅低于smallCapContext数据，跑道不足12个月
- 证伪条件：Phase 3 SUPRAME试验费用超预期导致烧钱速度骤增

### counter_thesis: unknown

主要反面论点已部分识别：临床失败风险（Phase 3尚在招募中）、竞争替代风险、以及预期商业化前持续亏损。跑道>12个月（约23.5个月），融资风险较低，但Phase 3试验耗资巨大可能加速消耗。证据中公司自身也明确警示了前瞻性声明的不确定性。但缺乏竞品管线、定价压力和地缘政治风险的具体数据。

- 支持 [ev_76f8c72e41670651](https://www.sec.gov/Archives/edgar/data/1809196/000095010326016061/dp255331_6k.htm) (primary-document): These forward-looking statements are based upon estimates and assumptions that, while considered reasonable by Immatics and its management, are inherently uncertain
- 支持 [ev_b8cab158dc0b2695](https://www.sec.gov/Archives/edgar/data/1809196/000095010326016061/dp255331_6k.htm) (primary-document): All the scientific and clinical data presented within this report are – by definition prior to completion of the clinical trial and a clinical study report – preliminary in nature
- 支持 [ev_c2026176b28de31c](https://clinicaltrials.gov/study/NCT06743126) (clinicaltrials-gov): SUPRAME-ACTengine® IMA203 vs. Investigator's Choice of Treatment in Previously Treated, Unresectable or Metastatic Cutaneous Melanoma
- 缺口：竞争对手PRAME靶向疗法或替代免疫疗法的管线对比
- 缺口：预期定价与支付方报销风险分析
- 缺口：欧洲/美国监管路径差异对审批时间的影响
- 缺口：PRAME表达异质性对可及患者群体规模的限制
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：Phase 3 SUPRAME试验未达到主要终点
- 证伪条件：竞争性PRAME疗法或其他TCR疗法率先获批
- 证伪条件：关键安全信号在更大样本中出现
- 证伪条件：PRAME-high患者比例低于预期，大幅缩小可及市场
- 证伪条件：制造成本过高导致商业化不可行

### management_governance: partial

证据中显示CEO Harpreet Singh在多份6-K文件上签字，治理结构可追溯。但证据包中未包含完整的治理信息（董事会构成、独立董事比例、关键管理层变动历史、薪酬结构等），无法做全面评估。

- 支持 [ev_b8cab158dc0b2695](https://www.sec.gov/Archives/edgar/data/1809196/000095010326016061/dp255331_6k.htm) (primary-document): By: /s/ Harpreet Singh Name: Harpreet Singh Title: Chief Executive Officer
- 支持 [ev_6fa9a292fb64622d](https://www.sec.gov/Archives/edgar/data/1809196/000119312526454401/immatics_n.v._6-k_q3_26.htm) (primary-document): by: /s/ Harpreet Singh Harpreet Singh Chief Executive Officer
- 缺口：董事会构成与独立董事比例
- 缺口：关键管理层变动历史与继任计划
- 缺口：高管薪酬结构与激励机制
- 缺口：任何未决调查或治理争议的披露
- 证伪条件：发现未披露的关键管理层离职或内部调查
- 证伪条件：董事会独立性不足或存在利益冲突

## IQV · complete

审查记录：`state/serenity-reviews/IQV-claude-3056b12059b5c25b4308.json`

### supply_chain_map: partial

上游供应商（数据供应商、试剂供应商、交通运输商等）有提及，三大业务线（TAS、R&DS、CS&MS）的产品结构清晰，下游客户明确为生物制药公司。但证据中缺乏具体命名的客户关系或供应商名称，供应链节点之间的具体依赖程度未量化。

- 支持 [ev_7d00299c71787951](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): we depend on third parties for support services to our business. Such support services include, but are not limited to, third- party transportation providers, suppliers of drugs for patients participating in clinical trials, suppliers of kits for use in our clinical trial laboratories business, suppliers of reagents for use in our testing equipment
- 支持 [ev_df28dd69707fdd45](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): Technology & Analytics Solutions provides mission critical information, technology solutions and real world insights and services to the Company’s life science clients. Research & Development Solutions, which primarily serves biopharmaceutical customers, provides outsourced clinical research and clinical trial related services.
- 支持 [ev_32912c5be3ead7da](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): Total revenues $ 6,626 $ 8,896 $ 788 $ 16,310
- 缺口：具体命名的上游数据供应商
- 缺口：具体命名的下游客户及合同金额
- 缺口：各节点的市场集中度数据
- 证伪条件：若单一客户收入占比超过10%则可确认集中依赖
- 证伪条件：若数据供应商集中于少数几家则可确认上游瓶颈

### chokepoint_evidence: fail

10-K明确披露'进入壁垒极少'，并点名列出大量直接竞争对手（ICON、Parexel、PPD/Thermo Fisher、Syneos Health等），且AI技术进步可能使客户绕过IQV直接在内部完成同类工作。这三点共同构成对瓶颈地位的直接否定。

- 反证 [ev_90abee258b62e2ec](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): There are few barriers to entry for companies considering offering any one or more of the services we offer.
- 反证 [ev_3d5542865eea401b](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): Some of our larger competitors include ICON plc, Parexel International Corporation, Pharmaceutical Product Development, Inc. (part of Thermo Fisher Scientific Inc.), and Syneos Health, among others.
- 反证 [ev_11ece7fa39749fb3](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): If customers are able to obtain comparable insights through alternative AI‑enabled solutions, develop such capabilities internally, or shift spending toward lower‑cost providers, demand for certain of our services and offerings could decline
- 缺口：任何证明IQV在某一节点具有垄断或双寡头地位的市场份额数据
- 缺口：客户重新认证替代供应商所需的时间或成本
- 证伪条件：若IQV在某关键数据集或监管认证节点拥有>50%全球份额，可推翻
- 证伪条件：若存在多年独家合同锁定条款，可推翻

### customer_dependency: partial

2025年总收入达163亿美元，剩余绩效义务积压约342亿美元，显示客户群广泛且有长期合同支撑。但无单一客户超过总收入10%，且证据中未披露任何具体命名客户的采用案例或合同细节，仅能确认收入规模而无法确认具体依赖关系。

- 支持 [ev_addce00265bbd85f](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): approximately $ 34.2 billion of revenues are expected to be recognized in the future from remaining performance obligations.
- 支持 [ev_32912c5be3ead7da](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): Total revenues $ 6,626 $ 8,896 $ 788 $ 16,310
- 反证 [ev_8ffe44924c457ed7](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): No individual customer represented 10% or more of total revenues for the years ended December 31, 2025, 2024 and 2023.
- 缺口：具体命名的大客户及其采用产品/服务的案例
- 缺口：主要客户的合同续签率或客户流失率数据
- 缺口：Top 10客户的收入集中度
- 证伪条件：若出现大型生物制药客户终止合同或转向竞争对手的披露，则客户依赖度进一步下降

### pure_play: pass

IQV三个业务板块（TAS、R&DS、CS&MS）全部服务于生命科学和生物制药客户，2025年总收入163亿美元均来自同一主题（制药服务和数据分析）。尽管按服务类型存在多元化，但主题敞口高度集中于医药行业，符合主题纯粹性要求。

- 支持 [ev_dec2209067ff1aa3](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): Technology & Analytics Solutions provides mission critical information, technology solutions and real world insights and services to the Company’s life science clients. Research & Development Solutions, which primarily serves biopharmaceutical customers, provides outsourced clinical research and clinical trial related services. Contract Sales & Medical Solutions provides health care provider (including contract sales) and patient engagement services to both biopharmaceutical customers and the broader healthcare market.
- 支持 [ev_d83ebf6b13f5714b](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): Revenues Technology & Analytics Solutions $ 6,626 $ 6,160 $ 5,862 Research & Development Solutions 8,896 8,527 8,395 Contract Sales & Medical Solutions 788 718 727 Total revenues 16,310 15,405 14,984
- 证伪条件：若IQV进入非医药行业收购并形成重大收入来源，则纯粹性受损

### multi_node_control: partial

IQV在制药价值链上横跨数据分析（TAS）、临床研究外包（R&DS）和合同销售（CS&MS）三个环节，这些确实属于相互关联的节点。但证据未显示IQV在上述节点中具有控制性地位或独家能力——它只是在各节点提供服务，而非控制这些节点的物理资产或关键投入。

- 支持 [ev_63b9e2d90f74fd13](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): The Company is managed through three reportable segments, Technology & Analytics Solutions, Research & Development Solutions and Contract Sales & Medical Solutions.
- 支持 [ev_d83ebf6b13f5714b](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): Revenues Technology & Analytics Solutions $ 6,626 $ 6,160 $ 5,862 Research & Development Solutions 8,896 8,527 8,395 Contract Sales & Medical Solutions 788 718 727 Total revenues 16,310 15,405 14,984
- 反证 [ev_90abee258b62e2ec](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): There are few barriers to entry for companies considering offering any one or more of the services we offer.
- 缺口：证明在至少两个节点具有控制性市场份额或独家技术能力的数据
- 缺口：节点间的垂直整合协同效应的具体量化证据
- 证伪条件：若竞争对手可以分别在各节点提供可替代服务，则多节点控制论点不成立

### earnings_validation: pass

2026年10月27日发布的10-Q提供了2026年Q3实际业绩：收入44.28亿美元（同比增长8.0%），净利润3.52亿美元，前九个月收入129.47亿美元、净利润8.85亿美元。2025年全年收入163.10亿美元，均为有日期的实际已审计/已报告财务数据，支持论文中收入增长和盈利能力的假设。

- 支持 [ev_bb5d2eac3fc44f99](https://www.sec.gov/Archives/edgar/data/1478242/000162828026067646/iqv-20260930.htm) (primary-document): Revenues $ 4,428 $ 4,100 $ 12,947 $ 11,946
- 支持 [ev_6401c5c4937f6f35](https://www.sec.gov/Archives/edgar/data/1478242/000162828026067646/iqv-20260930.htm) (primary-document): Net income attributable to IQVIA Holdings Inc. $ 350 $ 331 $ 880 $ 846
- 支持 [ev_32912c5be3ead7da](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): Total revenues $ 6,626 $ 8,896 $ 788 $ 16,310
- 证伪条件：若下季度收入出现同比下滑或积压订单大幅减少，则盈利验证需重新评估

### counter_thesis: partial

证据中确实包含多条具体的反论点：（1）AI工具可使客户内部化IQV提供的数据分析和洞察服务；（2）大型科技公司（有资金、技术和品牌）可进入该市场；（3）行业整合导致下游客户可能自建信息服务能力；（4）数据隐私法规的不确定性可能限制跨境数据流通。但证据中缺乏地缘政治压力分析、估值压力测试和管理层对这些风险的量化响应措施。

- 支持 [ev_95a3bcab6ce1e000](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): If customers are able to obtain comparable insights through alternative AI‑enabled solutions, develop such capabilities internally, or shift spending toward lower‑cost providers, demand for certain of our services and offerings could decline, pricing pressure could increase, and our margins and growth prospects could be adversely affected.
- 支持 [ev_e207de31824b4d14](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): Large technology companies with substantial resources, technical expertise and greater brand power could also decide to enter or further expand in the markets where our business operates and compete with us.
- 支持 [ev_045f6ffd28f0f4ce](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): shift of business to a competitor or internal resources
- 反证 [ev_addce00265bbd85f](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): approximately $ 34.2 billion of revenues are expected to be recognized in the future from remaining performance obligations.
- 缺口：地缘政治风险分析（如数据本地化要求对跨境业务的影响）
- 缺口：估值倍数与同行对比的压力测试
- 缺口：生物制药客户研发预算削减对积压订单影响的量化分析
- 证伪条件：若出现大客户终止合同并转向内部AI能力或竞争对手的具体披露
- 证伪条件：若积压订单取消率大幅上升
- 证伪条件：若监管机构对跨境健康数据传输实施禁令

### management_governance: partial

CEO Ari Bousbib与CFO Ronald E. Bruehlman均在职并签署内控报告，PwC已确认截至2025年12月31日内部控制有效；EVP总法律顾问Sherbet行权后出售4,446股（代码S，无10b5-1计划标注），但其仍直接持有约21,000股，且EVP/GC职位级别低于CEO/CFO，该交易不构成领导层稳定性、未决调查或继任问题。

- 支持 [ev_b1440ec26b43db44](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): /s/ Ari Bousbib /s/ Ronald E. Bruehlman Ari Bousbib Ronald E. Bruehlman Chairman and Chief Executive Officer Executive Vice President and Chief Financial Officer
- 支持 [ev_522d047e20bf8ed3](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): management has concluded that, as of December 31, 2025, the Company’s internal control over financial reporting was effective.
- 支持 [ev_e1a5e866b27c61d0](https://www.sec.gov/Archives/edgar/data/1478242/000162828026008322/iqv-20251231.htm) (primary-document): the Company maintained, in all material respects, effective internal control over financial reporting as of December 31, 2025
- 反证 [ev_484329e7f00ee65b](https://www.sec.gov/Archives/edgar/data/1478242/000119312526458941/xslF345X06/ownership.xml) (primary-document): Common Stock 11/09/2026 S 4,446 D $ 278.83 24,989 D
- 反证 [ev_6bb59afa81499a3a](https://www.sec.gov/Archives/edgar/data/1478242/000119312526458941/xslF345X06/ownership.xml) (primary-document): Check this box to indicate that a transaction was made pursuant to a contract, instruction or written plan for the purchase or sale of equity securities of the issuer that is intended to satisfy the affirmative defense conditions of Rule 10b5-1(c).
- 反证 [ev_d8a8b42bdf4957fc](https://www.sec.gov/Archives/edgar/data/1478242/000119312526458941/xslF345X06/ownership.xml) (primary-document): Remarks: Executive Vice President, General Counsel /s/ Abigail Jeck, Attorney-in-Fact for Eric Sherbet 11/12/2026
- 缺口：Sherbet此次S交易及D交易是否依据10b5-1(c)预设计划执行的明确披露（表格中该复选框未标注选中）
- 缺口：Sherbet在所有IQV证券中的总持股比例及其占个人净资产的背景信息
- 缺口：通过需要直接相关的原始披露及完整证据
- 证伪条件：SEC就IQV或其高管启动正式调查的披露
- 证伪条件：CEO Bousbib或CFO Bruehlman离职或继任悬而未决的公告
- 证伪条件：CEO/CFO级别高管发生无10b5-1计划的大规模开市场出售

## IRD · complete

审查记录：`state/serenity-reviews/IRD-claude-82511e3db9c9186c38eb.json`

### supply_chain_map: partial

可以部分绘制供应链：上游依赖合同制造商和意大利单一药物原料供应商；公司产品为基因治疗和眼科药物；下游通过Viatris许可协议商业化RYZUMVI。但缺乏对基因治疗载体（AAV）供应商的具体披露，供应链细节不完整。

- 支持 [ev_42ad18da69eff0b2](https://www.sec.gov/Archives/edgar/data/1228627/000114036126009247/ef20060643_10k.htm) (primary-document): we presently rely on one supplier in Italy for the drug substance for PS
- 支持 [ev_e68deb0fdb42dad6](https://www.sec.gov/Archives/edgar/data/1228627/000114036126009247/ef20060643_10k.htm) (primary-document): some raw materials are available only from a single source or only one supplier has been identified, even in instances where multiple sources exist
- 支持 [ev_2c31f13f9ca07b28](https://www.sec.gov/Archives/edgar/data/1228627/000162828026072697/ird-20260930.htm) (primary-document): We have one product, RYZUMVI®, approved for sale that is generating royalties based on sales by Viatris
- 缺口：AAV载体供应商的具体名称和集中度
- 缺口：基因治疗生产所需关键原材料的详细供应商清单
- 缺口：下游患者群体规模和地域分布数据
- 证伪条件：发现公司已实现完全垂直整合的内部生产能力
- 证伪条件：发现关键原材料有多个可替代供应商且切换成本极低

### chokepoint_evidence: unknown

IRD（Opus Genetics）是一家临床阶段基因治疗公司，不具备供应链瓶颈特征。公司本身依赖单一来源供应商，是瓶颈的下游受害方而非控制方。没有证据表明公司在任何关键节点拥有供应集中度或替代壁垒。

- 缺口：公司控制的具有高供应集中度的关键节点
- 缺口：替代供应商进入的时间和成本壁垒
- 缺口：公司在某一领域的全球市场份额数据
- 证伪条件：发现公司的某项专有技术或平台是整个基因治疗行业的必要投入且无法替代

### customer_dependency: partial

Viatris是RYZUMVI的独家商业化合作伙伴，产生版税收入，但Processa已终止RX-3117许可协议。基因治疗管线尚在临床阶段，无终端客户采用证据。仅有一个活跃的许可合作关系。

- 支持 [ev_2c31f13f9ca07b28](https://www.sec.gov/Archives/edgar/data/1228627/000162828026072697/ird-20260930.htm) (primary-document): We have one product, RYZUMVI®, approved for sale that is generating royalties based on sales by Viatris
- 反证 [ev_2030ea7e3c856f48](https://www.sec.gov/Archives/edgar/data/1228627/000114036126009247/ef20060643_10k.htm) (primary-document): On June 27, 2025, Processa notified the Company that it would not be developing RX-3117 and terminated the Processa License Agreement, effective October 25, 2025
- 缺口：Viatris的RYZUMVI具体销售额和增长趋势
- 缺口：基因治疗管线的潜在客户或合作伙伴意向
- 缺口：RYZUMVI的市场渗透率和处方医生数量
- 证伪条件：Viatris终止RYZUMVI许可协议
- 证伪条件：发现RYZUMVI销售额持续大幅下降

### pure_play: pass

公司仅有一个运营部门，完全专注于视觉健康和基因治疗领域。所有管线（LCA5、BEST1、RHO、MERTK等）及已获批产品RYZUMVI均围绕眼科适应症，属于纯粹的眼科基因治疗公司。

- 支持 [ev_da9287bdc1785794](https://www.sec.gov/Archives/edgar/data/1228627/000114036126009247/ef20060643_10k.htm) (primary-document): The Company’s Chief Executive Officer views the Company’s operations and manages its business in one operating segment, which is the business of development of products related to vision performance and health
- 证伪条件：公司进入与视觉健康无关的治疗领域且该领域收入占比超过30%

### multi_node_control: unknown

无证据表明公司控制两个或以上相连的供应链节点。公司依赖外部合同制造商和分析实验室，仅拥有知识产权和临床开发能力，不具备垂直整合特征。

- 缺口：公司在供应链多个环节的自有生产能力
- 缺口：纵向整合的具体证据（如自有AAV生产设施）
- 证伪条件：发现公司建立了内部GMP生产设施并同时控制载体设计和生产

### earnings_validation: partial

临床阶段公司，亏损预期合理。截至2026年9月30日现金$89.0M，九个月经营活动现金流出$38.7M（年化约$51.6M），现金跑道约20个月。公司声称现金足以支持运营，但净亏损$120.1M（含$72.1M非现金项目）。有融资活动补充现金，但持续依赖外部融资。

- 支持 [ev_aa68e07933bed0b3](https://www.sec.gov/Archives/edgar/data/1228627/000162828026072697/ird-20260930.htm) (primary-document): Cash and cash equivalents $ 88,974 $ 45,091
- 支持 [ev_adebfbf0084f9fef](https://www.sec.gov/Archives/edgar/data/1228627/000162828026072697/ird-20260930.htm) (primary-document): cash used in operating activities of $38.7 million was attributable to a net loss of $120.1 million , partially offset by non-cash expense of $78.6 million
- 反证 [ev_76667ce050aaf7ff](https://www.sec.gov/Archives/edgar/data/1228627/000162828026072697/ird-20260930.htm) (primary-document): As of September 30, 2026, we had an accumulated deficit of $308.7 million
- 缺口：公司对现金跑道的具体预期时间（如足够到哪一年）
- 缺口：RYZUMVI的具体版税收入金额
- 缺口：未来12个月的资本需求详细预测
- 缺口：未在原文中找到引用：our net loss was $46.5 million and $120.1 million for the th
- 证伪条件：现金余额降至不足12个月经营支出且无已确认融资渠道
- 证伪条件：关键临床试验失败导致管线价值归零

### counter_thesis: partial

已识别部分风险：Processa终止合作、累计亏损$308.7M、依赖持续融资、单一来源供应商风险。但缺乏对竞争格局（其他IRD基因治疗公司如Spark/Roche）、基因治疗定价和报销风险、以及估值合理性的系统性压力测试。

- 支持 [ev_2030ea7e3c856f48](https://www.sec.gov/Archives/edgar/data/1228627/000114036126009247/ef20060643_10k.htm) (primary-document): On June 27, 2025, Processa notified the Company that it would not be developing RX-3117 and terminated the Processa License Agreement, effective October 25, 2025
- 支持 [ev_42ad18da69eff0b2](https://www.sec.gov/Archives/edgar/data/1228627/000114036126009247/ef20060643_10k.htm) (primary-document): we presently rely on one supplier in Italy for the drug substance for PS
- 支持 [ev_a10818336af6e432](https://www.sec.gov/Archives/edgar/data/1228627/000162828026072697/ird-20260930.htm) (primary-document): we expect to finance our cash needs through a combination of equity, debt and alternative financings as well as through collaborations, strategic alliances and licensing arrangements
- 缺口：竞争对手在同一适应症的临床进展对比
- 缺口：基因治疗定价和商业保险覆盖风险分析
- 缺口：估值与同类公司的对比
- 缺口：FDA审批风险的具体量化
- 证伪条件：竞争对手在LCA5或BEST1适应症获批上市
- 证伪条件：基因治疗报销政策发生不利变化
- 证伪条件：关键临床试验未达到主要终点
- 证伪条件：无法在现金耗尽前完成融资导致被迫稀释或停止试验

### management_governance: partial

内部控制有效，CEO和CFO评估确认截至2025年12月31日内控有效。无重大变更或调查。但缺乏对具体管理层成员的背景、任期、薪酬以及董事会构成的详细信息。

- 支持 [ev_aa489dee86f9120d](https://www.sec.gov/Archives/edgar/data/1228627/000114036126009247/ef20060643_10k.htm) (primary-document): management has concluded that the Company’s internal control over financial reporting was effective as of December 31, 2025
- 支持 [ev_e065486ab55dc048](https://www.sec.gov/Archives/edgar/data/1228627/000114036126009247/ef20060643_10k.htm) (primary-document): no director or officer of the Company adopted or terminated a “Rule 10b5-1 trading arrangement” or “non-Rule 10b5-1 trading arrangement,”
- 缺口：CEO和CFO的具体姓名、背景和任期
- 缺口：董事会独立性和构成详情
- 缺口：高管薪酬结构
- 缺口：近期是否有管理层变动
- 证伪条件：发现正在进行的SEC调查或审计意见保留
- 证伪条件：关键高管突然离职且无继任计划

## ISRG · complete

审查记录：`state/serenity-reviews/ISRG-claude-41c862f3068dd66678f4.json`

### supply_chain_map: partial

上游有单一来源供应商和半导体元件，器械主要在墨西哥生产；下游为医院。文件未点名具体单一来源供应商。

- 支持 [ev_8009d39084d67370](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): our reliance on sole- and single-sourced suppliers; extended lead times and price volatility for certain semiconductor components
- 支持 [ev_9ec0ed69fdb65e27](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): including Mexico, where we currently manufacture a significant majority of our instruments
- 缺口：具体单一来源供应商名称与占比

### chokepoint_evidence: partial

装机量和手术量形成生态壁垒，法院认定机器人与 EndoWrist 器械是独立产品市场；但面临其他机器人系统竞争，中国尤其明显。

- 支持 [ev_15a7b5bf2fd59125](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): Approximately 906,000 da Vinci procedures were performed during the three months ended September 30, 2026, a growth of 14%
- 支持 [ev_19f4b9f0c07cdbf0](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): the da Vinci robot and EndoWrist instruments occupy separate product markets for antitrust purposes
- 反证 [ev_e3f3141976b2b049](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): competition from companies offering alternative surgical approaches or robotic-assisted surgical systems, including domestic competitors in certain geographic markets, such as China
- 缺口：市场份额数据

### customer_dependency: partial

客户是大量医院，2025 年手术量 315 万例、增长 18%，不依赖单一客户；但医院采购取决于手术的医保报销。

- 支持 [ev_839e6619d3b1e099](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): Approximately 3,153,000 da Vinci procedures were performed during the year ended December 31, 2025, an increase of 18%
- 反证 [ev_ec35db08142de98f](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): If hospitals are unable to obtain coverage and reimbursement for procedures using our products
- 缺口：客户集中度数据

### pure_play: partial

核心是手术机器人硬件与器械，AI 是功能（如 Ion 导航中的 AI），不是收入来源。

- 支持 [ev_03362daa1b963cee](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): This software release introduces artificial intelligence across Ion’s entire navigational workflow
- 反证 [ev_c5a614a89ff9da3b](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): Systems revenue increased 26% to $2.47 billion in 2025

### multi_node_control: pass

同时控制系统、器械与耗材生产，并从手术延伸到肺部活检诊断。

- 支持 [ev_534246ae256a4070](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): Our Ion system extends our commercial offering beyond surgery into diagnostic, endoluminal procedures
- 支持 [ev_4ddb4b177230f01e](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): where we currently manufacture a significant majority of our instruments

### earnings_validation: pass

Q3 2026 收入增长 22% 至 30.5 亿美元；2025 年收入增长 21% 至 101 亿美元。

- 支持 [ev_04013d0471c44eee](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): Total revenue increased by 22% to $3.05 billion for the three months ended September 30, 2026
- 支持 [ev_7a8990fc9af28a88](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): Total revenue increased by 21% to $10.1 billion for the year ended December 31, 2025

### counter_thesis: pass

已检验：反垄断和解（4.5 亿美元并附禁令救济，可能放开第三方器械维修）、中国集采与统一定价、其他机器人竞争；另有估值约 14 倍收入（非文件数据）。

- 支持 [ev_15a7b5bf2fd59125](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): Approximately 906,000 da Vinci procedures were performed during the three months ended September 30, 2026, a growth of 14%
- 反证 [ev_eb41b1adb8be8c13](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): to settle the case for a one-time payment of $ 450 million and mutually agreed injunctive relief
- 反证 [ev_dd240fe019083f3f](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): including the implementation of a unified national pricing framework in China
- 证伪条件：手术量增速连续两个季度低于装机量增速
- 证伪条件：和解的禁令救济让第三方器械明显挤压器械收入
- 证伪条件：中国统一定价导致海外系统收入下滑

### management_governance: partial

新Form 4文件显示Brosius（EVP制造与供应链）和Loeb（EVP法务与合规）的所有出售均在10b5-1预定计划下执行，均为EVP级别非CEO/CFO，出售后持仓显著（Loeb保留6,236股，Brosius保留227股），不构成治理警示；但反垄断和解中行为禁令救济义务是否完全解除仍无任何新披露，原有未决问题未关闭，治理门维持partial。

- 支持 [ev_acf8b8ba65302d9d](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): The Company recorded a charge of $ 450 million in operating
- 反证 [ev_eec247964452de61](https://www.sec.gov/Archives/edgar/data/1035267/000201030026000039/xslF345X06/edgardoc.xml) (primary-document): EVP & Chief Mfg and Supply Cha
- 反证 [ev_e14e4d94b22fbf81](https://www.sec.gov/Archives/edgar/data/1035267/000201030026000039/xslF345X06/edgardoc.xml) (primary-document): The transaction took place in accordance with a Trading Plan that complies with SEC Rule 10b5-1 and expires on February 14, 2027.
- 反证 [ev_e262ea3a62aca926](https://www.sec.gov/Archives/edgar/data/1035267/000201030026000039/xslF345X06/edgardoc.xml) (primary-document): Common Stock 11/18/2026 S (1) 46 D $ 430.63 319 D
- 反证 [ev_1f37f529a0a53801](https://www.sec.gov/Archives/edgar/data/1035267/000201030026000041/xslF345X06/edgardoc.xml) (primary-document): The transaction took place in accordance with a Trading Plan that complies with SEC Rule 10b5-1 and expires on February 14, 2027.
- 反证 [ev_bf4e40b95ccc9d69](https://www.sec.gov/Archives/edgar/data/1035267/000201030026000041/xslF345X06/edgardoc.xml) (primary-document): Common Stock 11/20/2026 S (1) 46 D $ 407.24 227 D
- 反证 [ev_7efdb057b474f35e](https://www.sec.gov/Archives/edgar/data/1035267/000156173326000018/xslF345X06/edgardoc.xml) (primary-document): EVP & Chief Legal and Complian
- 反证 [ev_cd401389090cf4a3](https://www.sec.gov/Archives/edgar/data/1035267/000156173326000018/xslF345X06/edgardoc.xml) (primary-document): The transaction took place in accordance with a Trading Plan that complies with SEC Rule 10b5-1 and expires on January 29, 2027.
- 反证 [ev_0deea2a346202b5f](https://www.sec.gov/Archives/edgar/data/1035267/000156173326000018/xslF345X06/edgardoc.xml) (primary-document): Common Stock 11/10/2026 S (1) 400 D $ 458.15 6,236 D
- 缺口：无任何文件披露反垄断和解中行为禁令救济义务的解除或终止情况，原有未决问题无法关闭
- 证伪条件：若出现CEO或CFO在无10b5-1计划下的大额出售，或有文件披露高管离职/继任空缺，或有新监管调查开启，则应降级至pending
- 证伪条件：若有SEC或法院文件明确披露反垄断行为禁令救济义务已全部解除，则可升级至pass

## KALA · complete

审查记录：`state/serenity-reviews/KALA-claudecli-7d87b168bbf8431d453c.json`

### supply_chain_map: unknown

证据包仅含XBRL标签和封面页，无任何关于上游原材料、公司产品（KPI-012）的具体供应链描述，也无下游用户/患者群体的叙述性内容。无法构建供应链图谱。

- 缺口：KPI-012药物的原材料和生产供应商信息
- 缺口：药物递送技术的具体上游依赖
- 缺口：目标适应症和患者群体描述
- 缺口：CMO/CDMO合同制造商信息
- 证伪条件：发现公司仅为空壳无实际管线
- 证伪条件：关键原料药供应商已停止合作

### chokepoint_evidence: unknown

证据中无任何关于供应集中度或替代壁垒的信息。KALA是药物发现阶段的生物技术公司，与AI供应链瓶颈无关，也未见其在任何供应节点具有垄断或寡头地位的证据。

- 缺口：公司技术平台的独特性和不可替代性证据
- 缺口：竞争对手数量和市场份额数据
- 缺口：专利保护范围和到期时间
- 证伪条件：多家公司拥有相同或更优的技术平台
- 证伪条件：专利挑战成功导致技术壁垒消失

### customer_dependency: unknown

证据中无任何客户、合作伙伴采用或商业协议的叙述性描述。XBRL标签显示Younet许可协议和CIRM拨款，但缺乏具体内容。临床前阶段公司尚无商业客户属正常情况，但仍无法评估。

- 缺口：与制药公司的合作或许可协议详情
- 缺口：临床试验合作方信息
- 缺口：Younet许可协议的具体范围和条款
- 证伪条件：合作方终止协议
- 证伪条件：临床试验因缺乏合作方支持而搁置

### pure_play: partial

XBRL标签表明公司为单一报告分部，暗示业务聚焦，但缺乏叙述性证据说明具体业务构成和主题收入敞口。

- 支持 [ev_f06ebf7f4a2196b2](https://www.sec.gov/Archives/edgar/data/1479419/000110465926043782/kala-20251231x10k.htm) (primary-document): kala:SingleReportingSegmentMember 2025-01-01 2025-12-31
- 缺口：业务描述和收入来源的叙述性段落
- 缺口：管线资产与AI医药主题的关联度
- 缺口：研发支出在各项目间的分配
- 证伪条件：公司大部分资源投入与核心主题无关的项目

### multi_node_control: unknown

证据中无任何关于公司控制多个供应链节点的信息。作为临床前阶段药企，通常不具备多节点垂直整合特征，且证据包未提供相关描述。

- 缺口：公司是否同时拥有药物发现平台和生产能力
- 缺口：技术平台是否覆盖多个治疗领域
- 缺口：垂直整合程度的描述
- 证伪条件：公司完全依赖外部CRO/CMO，无自有研发或生产能力

### earnings_validation: partial

临床前准备阶段公司，零收入本身不构成失败理由。但证据仅含XBRL标签，显示2024-2026年间多轮稀释性融资（Series G/H/I/Aa/Aaa优先股及ATM发行），表明现金紧张。背景数据显示现金$7.2M、跑道仅9.8个月（低于12个月），融资风险为真。缺乏可引用的具体财务数字（现金余额、烧钱率），无法完整评估是否能资助下一里程碑。

- 支持 [ev_c6fb1f11baa03de6](https://www.sec.gov/Archives/edgar/data/1479419/000110465926043782/kala-20251231x10k.htm) (primary-document): kala:SeriesAaConvertibleNonRedeemablePreferredStockMember kala:SecuritiesPurchaseAgreementNovember2025Member 2025-11-24
- 支持 [ev_f06ebf7f4a2196b2](https://www.sec.gov/Archives/edgar/data/1479419/000110465926043782/kala-20251231x10k.htm) (primary-document): kala:SeriesAaaConvertibleNonRedeemablePreferredStockMember us-gaap:SubsequentEventMember kala:SecuritiesPurchaseAgreementJanuary2026Member 2026-01-30
- 反证 [ev_6077eca959b8ef8b](https://www.sec.gov/Archives/edgar/data/1479419/000110465926043782/kala-20251231x10k.htm) (primary-document): us-gaap:CommonStockMember kala:AtMarketOfferingMember 2024-01-01 2024-12-31
- 缺口：可引用的现金及等价物余额
- 缺口：季度/年度烧钱率的叙述性数据
- 缺口：管理层关于资金充裕性的声明（going concern）
- 缺口：下一临床里程碑的预计费用
- 证伪条件：going concern意见已出具
- 证伪条件：现金不足以支撑6个月运营
- 证伪条件：融资渠道已耗尽

### counter_thesis: partial

跑道不足12个月（约9.8个月），financingRisk为真，股权稀释几乎确定。XBRL标签显示2024年3月至2026年1月期间至少5轮优先股融资加ATM发行，稀释模式明确。但证据包缺乏叙述性内容，无法充分压力测试供给侧、需求侧、替代、地缘政治和估值角度。主要反论点：(1) 稀释风险极高——跑道<12个月必然导致新一轮融资；(2) 临床前阶段失败率极高；(3) 缺乏chokepoint属性，无定价权或供应稀缺性。

- 支持 [ev_f06ebf7f4a2196b2](https://www.sec.gov/Archives/edgar/data/1479419/000110465926043782/kala-20251231x10k.htm) (primary-document): kala:SeriesAaaConvertibleNonRedeemablePreferredStockMember us-gaap:SubsequentEventMember kala:SecuritiesPurchaseAgreementJanuary2026Member 2026-01-30
- 支持 [ev_6077eca959b8ef8b](https://www.sec.gov/Archives/edgar/data/1479419/000110465926043782/kala-20251231x10k.htm) (primary-document): us-gaap:CommonStockMember kala:AtMarketOfferingMember 2024-01-01 2024-12-31
- 缺口：竞争对手管线和替代疗法的详细分析
- 缺口：目标市场规模和商业化路径
- 缺口：管理层对融资计划的叙述
- 缺口：临床数据或临床前数据的有效性证据
- 证伪条件：获得大型药企战略投资或合作，解决融资问题
- 证伪条件：临床前数据显示突破性疗效
- 证伪条件：获得FDA突破性疗法认定

### management_governance: unknown

证据包中仅有10-K目录页提及治理章节，但无任何董事、高管或治理实践的实质内容。无法评估领导团队稳定性、独立董事比例、薪酬结构或任何调查/诉讼情况。

- 缺口：CEO和关键高管的背景和任期
- 缺口：董事会构成和独立性
- 缺口：高管离职或继任计划
- 缺口：任何未解决的调查或诉讼
- 缺口：薪酬与绩效的关联度
- 证伪条件：关键高管近期离职
- 证伪条件：SEC调查或审计意见保留
- 证伪条件：内部控制重大缺陷

## MDT · complete

审查记录：`state/serenity-reviews/MDT-claudecli-12b8b0c1256843a42f24.json`

### supply_chain_map: unknown

XBRL标签显示MDT拥有心血管(Cardiovascular)、神经科学(Neuroscience)和医疗外科(Medical Surgical)三大业务板块，新闻证实Hugo机器人手术系统、Symplicity血压治疗、Affera心律系统、TAVR瓣膜等产品线。但证据中缺乏上游供应商、关键原材料和具体下游医院/支付方的详细映射。

- 支持 [ev_2554dde7bf79fb2b](https://news.google.com/rss/articles/CBMi_AFBVV95cUxNcG5tZmwzbGtnZmxOYTZQdEVLSmY3eTVFTG1qbnBLdy1KcTgxQ19zVVJueDBudlI0MGs1d1JfV2UyeGo4TnNNT2tPeVd6ZTQtMG9Ya1hFYjVrNW9iRDR5ZDN2OG9Ma0MwMlVXZjhLUlhJc3lQekQzOFNyOHdHWXJnOXpJWWZONDJGUDRIemFGRFloX1RqM3VlZWdaV2o3dGpoby1CUGlOa1FBcTVHQVRYSkZMVV84MkVSWHpuLThzLUpMQnhtQVlVd3ZsUUlHZ3RBUWZJZ1NJUWlFNE8yb1kyVnZZbFZqdlJSLUFuNmVOaVhBRk4zVDdVOWo4VUw?oc=5) (news-feed): Medtronic announces FDA clearance of general surgery procedures for the Hugo™ robotic-assisted surgery (RAS) system
- 缺口：上游关键零部件及原材料供应商名称
- 缺口：下游主要客户（医院系统、GPO）的具体披露
- 缺口：各产品线的供应链地理集中度
- 缺口：引用不存在或原文无法匹配
- 证伪条件：若10-K全文披露显示MDT供应链高度分散且无关键依赖，则该映射对chokepoint论点无意义

### chokepoint_evidence: unknown

MDT是市值$1,310亿的多元化医疗器械巨头，证据中无任何供应集中度或替代壁垒的数据。FDA AI设备审批记录仅证明产品获批，不构成竞争护城河证据。Hugo机器人手术系统面临Intuitive Surgical等竞争对手，无垄断或双寡头地位的证据。

- 反证 [ev_58421c64da0963d6](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K253984) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：AI医疗设备市场份额数据
- 缺口：竞品替代分析（如Intuitive Surgical的达芬奇系统）
- 缺口：任何节点的供应集中度定量数据
- 缺口：反证只是通用风险条款或记录字段，不是针对公司的直接反证
- 证伪条件：若MDT在某AI诊断或手术机器人子领域占据>50%份额且有切换成本证据，则可能通过

### customer_dependency: unknown

证据中没有任何具名客户、采购协议或收入集中度披露。新闻提及新加坡客户体验中心和Michael J. Fox基金会合作伙伴关系，但未披露实际采购量或依赖关系。

- 缺口：前五大客户收入占比
- 缺口：具名医院系统或GPO采购协议
- 缺口：AI产品线的具体客户采纳数据
- 证伪条件：若10-K全文显示无单一客户超过10%收入，则客户高度分散，不符合chokepoint框架的客户依赖逻辑

### pure_play: unknown

MDT是高度多元化的医疗器械公司，拥有心血管、神经科学、医疗外科三大板块。AI相关收入（AI辅助设备）在近$400亿年收入中占比极小。13项FDA AI设备获批但无收入拆分数据证明AI主题曝光度。公司刚完成MiniMed分拆，说明业务组合仍在调整中。

- 支持 [ev_cdf18e740d074907](https://www.sec.gov/Archives/edgar/data/1613103/000162828026044354/mdt-20260424.htm) (primary-document): mdt:CardiovascularMember 2026-04-24 0001613103 mdt:NeuroscienceGroupMember 2026-04-24 0001613103 mdt:MedicalSurgicalMember 2026-04-24
- 支持 [ev_44a8421f5b8d39b6](https://www.sec.gov/Archives/edgar/data/1613103/000162828026066291/mdt-20261015.htm) (primary-document): the Company announced that the exchange offer relating to the separation of MiniMed Group, Inc. had settled and that the separation was complete
- 缺口：AI相关产品线收入占总收入比例
- 缺口：各业务板块的AI渗透率数据
- 缺口：不通过需要直接反证，缺少证据不能等同失败
- 证伪条件：若MDT披露AI产品收入超过总收入20%，则需重新评估

### multi_node_control: unknown

证据中无任何MDT控制AI医疗供应链两个或以上相连节点的数据。MDT产品线广泛但属于同一层级（终端医疗设备），不构成纵向供应链节点控制。

- 缺口：纵向整合证据（如同时控制AI芯片/算法与终端设备）
- 缺口：供应链上下游节点的控制力证据
- 缺口：不通过需要直接反证，缺少证据不能等同失败
- 证伪条件：若MDT自研AI芯片或独家控制关键训练数据集并同时拥有终端设备，则可能通过

### earnings_validation: partial

XBRL数据确认MDT 2026年Q1（截至7月31日）收入$97.56亿、净利润$14.7亿、经营现金流$17.93亿，财务表现稳健。但这些是整体公司数据，无法验证AI医疗主题论点——缺乏AI产品线的收入拆分或增长率数据。

- 支持 [ev_e9bea23ae3369534](https://data.sec.gov/api/xbrl/companyfacts/CIK0001613103.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 9,756,000,000 for 2026-04-25 to 2026-07-31
- 支持 [ev_e9bea23ae3369534](https://data.sec.gov/api/xbrl/companyfacts/CIK0001613103.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 1,470,000,000 for 2026-04-25 to 2026-07-31
- 缺口：AI相关产品线的独立收入和增长率
- 缺口：AI设备对整体毛利率的贡献
- 缺口：AI业务的前瞻性指引
- 证伪条件：若AI产品线收入增速低于整体公司增速，则AI论点被削弱

### counter_thesis: partial

可识别的反论点包括：(1) 高度多元化稀释AI主题曝光；(2) Hugo机器人面临Intuitive Surgical强竞争；(3) MiniMed分拆后业务组合仍在重组中；(4) $1,310亿市值意味着AI增量对估值影响有限。但证据包中缺乏竞品数据和估值分析，无法完整压力测试。

- 支持 [ev_e9bea23ae3369534](https://data.sec.gov/api/xbrl/companyfacts/CIK0001613103.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 1,691,000,000 for as of 2026-07-31
- 支持 [ev_44a8421f5b8d39b6](https://www.sec.gov/Archives/edgar/data/1613103/000162828026066291/mdt-20261015.htm) (primary-document): the exchange offer relating to the separation of MiniMed Group, Inc. had settled and that the separation was complete
- 反证 [ev_3ff104d1e1876156](https://news.google.com/rss/articles/CBMiygFBVV95cUxOZEYxRmVETUJSMGVfenlobVNKSFRUbm52ZTFiTzliUjhtT0hCaW5sQzdRRXB1OWs4NXl4VVFFN05zMWUxSDFBNWtfb3ZVYnBLcjZTeW9OXzhacWp3UmFNMVp5MGtoZ1I0OEREb1JqakZvaFJqbEIwMUxjWlJqSlZsblFNQW9vOTJJR0tpcFE2b0ZrcmtUOUMxNUQ5RF9pR3Z3dEhHT1hsSHdyZzhhQng3NHppZU5TMzJySHYwVnh0dkNIT3BtRy1pNUxB?oc=5) (news-feed): Medtronic: $380 Million Acquisition Of Contego Medical To Expand Carotid Artery And Vascular Treatment Portfolio
- 缺口：与Intuitive Surgical等竞品的市场份额对比
- 缺口：AI医疗设备的定价权分析
- 缺口：地缘政治风险（中国市场暴露度）
- 证伪条件：Hugo系统在手术机器人市场份额持续低于5%
- 证伪条件：AI设备获批后无法转化为收入增长
- 证伪条件：监管收紧导致AI诊断设备审批放缓

### management_governance: unknown

8-K披露治理结构清晰：Geoffrey Martha继续担任董事长兼CEO，Michael Marinaro于2026年10月14日升任Medtronic总裁（扩大职责）。2026年10月15日年度股东大会选举12名董事，全部获多数票通过。PwC继续担任审计师。薪酬方案经股东非约束性批准。无公开调查或继任危机。

- 缺口：董事会成员的AI/技术专业背景详情
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：若出现SEC调查、高管突然离职或审计意见保留，则需降级

## MRNA · complete

审查记录：`state/serenity-reviews/MRNA-claudecli-39034579f9e83c981292.json`

### supply_chain_map: partial

证据列出了下游客户（FFF Enterprises、Cardinal Health、加拿大政府、英国UKHSA、日本厚生省等政府机构）及产品线（COVID-19疫苗、RSV疫苗），但缺乏对上游关键原料（脂质纳米颗粒、核苷酸、质粒DNA等）供应商的具体描述。10-Q仅泛泛提及第三方供应商和制造商，未具体列出。

- 支持 [ev_a773f7aef015c0e1](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000033/mrna-20251231.htm) (primary-document): mrna:FFFEnterprisesMember us-gaap:CustomerConcentrationRiskMember us-gaap:RevenueFromContractWithCustomerMember
- 支持 [ev_a773f7aef015c0e1](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000033/mrna-20251231.htm) (primary-document): mrna:CardinalHealthMember us-gaap:CustomerConcentrationRiskMember us-gaap:RevenueFromContractWithCustomerMember
- 支持 [ev_f22b0b34a58efbf6](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000197/mrna-20260930.htm) (primary-document): our ability to successfully contract with third-party suppliers, distributors and manufacturers
- 支持 [ev_3a86fb8c85c697e8](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000033/mrna-20251231.htm) (primary-document): mrna:COVID19Member 2025-01-01 2025-12-31 0001682852 mrna:COVID19Member 2024-01-01 2024-12-31
- 缺口：上游脂质纳米颗粒(LNP)供应商名称及集中度
- 缺口：核苷酸及mRNA原料供应商详细信息
- 缺口：CDMO/制造合作方的具体合同或依赖关系
- 证伪条件：发现Moderna已完全垂直整合上游原料生产，无需外部供应商
- 证伪条件：发现上游供应商极为分散，无集中风险

### chokepoint_evidence: fail

证据中没有显示Moderna控制任何供应链瓶颈节点。Moderna是mRNA疫苗的制造商和销售方，但mRNA技术本身有多个竞争者（BioNTech/Pfizer、CureVac等）。$90B市值的大型药企不符合aleabit方法中的'供应集中度'或'替代壁垒'标准。NVIDIA Nemotron新闻提及Therna做mRNA设计，说明mRNA领域存在多个参与者。

- 反证 [ev_2902f3f1b8cf0f67](https://nvidianews.nvidia.com/news/nvidia-introduces-nemotron-for-science-to-accelerate-discoveries-with-agents) (news-feed): Therna collaborated with NVIDIA to post-train Nemotron for agentic mRNA therapeutic design
- 反证 [ev_954bcfab2ea956c8](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000205/mrna-20261113.htm) (primary-document): current and any related future litigation proceedings with Pfizer, Inc., BioNTech SE and related parties
- 缺口：Moderna在mRNA供应链中的全球市场份额数据
- 缺口：mRNA疫苗原料（如伪尿苷、LNP）的全球供应商集中度分析
- 缺口：替代mRNA平台技术的可行性与时间线
- 证伪条件：证明Moderna拥有某个不可替代的专利原料或工艺节点，全球仅1-2家供应商

### customer_dependency: unknown

10-K的XBRL标签显示客户集中风险披露，包括FFF Enterprises、Cardinal Health、加拿大政府、英国UKHSA、日本厚生省、墨西哥Medistik、韩国Boryung、台湾FDA等。但这些仅是XBRL标签，缺乏具体收入金额或百分比的引用。合作方面有Merck（个性化癌症疫苗）、Vertex、Blackstone的披露。

- 支持 [ev_a773f7aef015c0e1](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000033/mrna-20251231.htm) (primary-document): mrna:PublicWorksAndGovernmentServicesCanadaMember us-gaap:CustomerConcentrationRiskMember us-gaap:RevenueFromContractWithCustomerMember
- 支持 [ev_a773f7aef015c0e1](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000033/mrna-20251231.htm) (primary-document): mrna:UKHealthSecurityAgencyMember us-gaap:CustomerConcentrationRiskMember us-gaap:RevenueFromContractWithCustomerMember
- 支持 [ev_67cf91dba89cbf77](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000033/mrna-20251231.htm) (primary-document): mrna:PersonalizedMRNACancerVaccinesPCVCollaborationAndLicenseAgreementWithMerckSharpAndDohmeCorpMember
- 缺口：各主要客户的具体收入占比数据
- 缺口：长期供应协议(APAs)的具体条款和金额
- 缺口：2026年新签订的政府合同详情
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现主要政府客户未续签2027年合同
- 证伪条件：发现FFF Enterprises或Cardinal Health已转向竞争对手产品

### pure_play: partial

Moderna几乎100%收入来自mRNA平台产品。收入分为COVID-19疫苗和RSV疫苗两个主要产品线，加上少量合作收入、拨款和许可费。所有业务均围绕mRNA技术，是典型的纯mRNA平台公司。但注意：mRNA药物开发是否属于'AI医药'主题需要更多证据。

- 支持 [ev_2ae172e085c453b0](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000197/mrna-20260930.htm) (primary-document): Net product sales $ 1,273 $ 973 $ 1,719 $ 1,172
- 支持 [ev_72f7d78a50f7dd9d](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000197/mrna-20260930.htm) (primary-document): mrna:COVID19Member 2026-07-01 2026-09-30 0001682852 mrna:COVID19Member 2025-07-01 2025-09-30
- 支持 [ev_72f7d78a50f7dd9d](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000197/mrna-20260930.htm) (primary-document): mrna:RSVMember 2026-07-01 2026-09-30 0001682852 mrna:RSVMember 2025-07-01 2025-09-30
- 支持 [ev_2ae172e085c453b0](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000197/mrna-20260930.htm) (primary-document): Other revenue 40 43 128 94
- 缺口：AI在Moderna药物研发流程中的具体应用占比
- 缺口：mRNA技术与AI drug discovery主题的直接关联证据
- 缺口：通过需要直接相关的原始披露及完整证据
- 证伪条件：发现Moderna有大量非mRNA业务收入
- 证伪条件：发现Moderna已经收购传统小分子药企，大幅分散业务

### multi_node_control: unknown

证据中未显示Moderna控制两个或以上相连的供应链节点。Moderna拥有mRNA设计、制造和商业化能力，但这属于单一企业的垂直整合，不等同于控制供应链上的多个瓶颈节点。缺乏Moderna控制上游关键原料或下游分销渠道瓶颈的证据。

- 缺口：Moderna在LNP递送系统上的专有控制力证据
- 缺口：Moderna是否控制关键原料（如伪尿苷修饰核苷酸）的生产
- 缺口：Moderna制造能力相对全球mRNA产能的占比
- 证伪条件：证明Moderna拥有LNP配方专利且无替代方案，同时控制mRNA生产关键原料

### earnings_validation: partial

Q3 2026实际财务数据充分：收入$1.313B（同比+29.2%），净利润$162M（去年同期亏损$200M），实现季度盈利。净产品销售$1.273B。总资产$13.468B，现金+投资合计约$7.976B。但YTD经营现金流为-$2.715B，新增$2.958B可转换债券。财务数据支持公司仍有充足运营资金。

- 支持 [ev_03d3cc0f752ca4f1](https://data.sec.gov/api/xbrl/companyfacts/CIK0001682852.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 1,313,000,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_03d3cc0f752ca4f1](https://data.sec.gov/api/xbrl/companyfacts/CIK0001682852.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 1,016,000,000, a change of +29.2%
- 支持 [ev_2ae172e085c453b0](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000197/mrna-20260930.htm) (primary-document): Net income (loss) $ 162 $ ( 200 ) $ ( 1,963 ) $ ( 1,996 )
- 支持 [ev_c6fc1c3c44e43f4d](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000197/mrna-20260930.htm) (primary-document): Cash and cash equivalents $ 1,195 $ 2,595 Investments 3,976 3,204 Accounts receivable, net 1,367
- 支持 [ev_c6fc1c3c44e43f4d](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000197/mrna-20260930.htm) (primary-document): Convertible notes 2,958 — Other non-current liabilities 285 285 Total liabilities 6,631 3,688
- 反证 [ev_03d3cc0f752ca4f1](https://data.sec.gov/api/xbrl/companyfacts/CIK0001682852.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -2,715,000,000 for 2026-01-01 to 2026-09-30
- 反证 [ev_2ae172e085c453b0](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000197/mrna-20260930.htm) (primary-document): Cost of sales 318 207 1,366 416
- 缺口：2026全年收入指引及管理层对2027年展望
- 缺口：COVID-19与RSV各自的具体收入拆分金额
- 缺口：毛利率趋势分析
- 缺口：通过需要直接相关的原始披露及完整证据
- 证伪条件：Q4 2026收入大幅低于Q3，表明季节性后无增长动力
- 证伪条件：现金消耗速度加剧导致需要额外稀释性融资

### counter_thesis: partial

部分反面论点已有证据支持：(1)YTD经营现金流为负$2.715B，尽管Q3盈利但全年仍在消耗现金；(2)新增$2.958B可转换债券，增加了杠杆和潜在稀释；(3)与Pfizer/BioNTech及Arbutus的专利诉讼仍在进行中；(4)首席法务官Klinger离职，诉讼管理可能受影响；(5)mRNA领域竞争加剧（Therna等新进入者）。但缺乏对COVID疫苗需求下降风险、地缘政治风险、估值角度的系统压力测试。

- 支持 [ev_03d3cc0f752ca4f1](https://data.sec.gov/api/xbrl/companyfacts/CIK0001682852.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -2,715,000,000 for 2026-01-01 to 2026-09-30
- 支持 [ev_954bcfab2ea956c8](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000205/mrna-20261113.htm) (primary-document): current and any related future litigation proceedings with Pfizer, Inc., BioNTech SE and related parties
- 支持 [ev_954bcfab2ea956c8](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000205/mrna-20261113.htm) (primary-document): current and any related future litigation proceedings with Arbutus Biopharma Corporation and Genevant Sciences, GmbH
- 支持 [ev_d0c5bd88e36970e2](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000208/mrna-20261109.htm) (primary-document): The Amendment reduces the applicable interest rate margins for the initial term loans and delayed draw term loans by 0.75 percentage points
- 反证 [ev_2ae172e085c453b0](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000197/mrna-20260930.htm) (primary-document): Research and development 583 801 1,883 2,357
- 缺口：COVID-19疫苗需求长期可持续性分析
- 缺口：mRNA平台在肿瘤领域（intismeran等）的竞争格局
- 缺口：估值与同行（BioNTech、Pfizer疫苗业务）的系统性对比
- 缺口：地缘政治风险（如政府疫苗采购政策变化）的深入分析
- 证伪条件：WHO宣布COVID-19不再需要年度接种，疫苗需求崩塌
- 证伪条件：专利诉讼败诉导致巨额赔偿或关键专利失效
- 证伪条件：intismeran III期临床失败，肿瘤管线价值归零
- 证伪条件：可转换债券转股大幅稀释现有股东

### management_governance: unknown

证据显示首席法务官Shannon Thyme Klinger已签署退休协议，将离职。CFO James M. Mock正常签署多份SEC文件。Klinger的离职发生在公司与Pfizer/BioNTech及Arbutus的关键专利诉讼期间，法务领导层的更替是治理风险。信贷协议修订由Ares Capital进行，利率降低0.75个百分点，显示贷款方对公司信用的认可。但缺乏CEO及董事会整体治理评估。

- 支持 [ev_b284b3c261799400](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000194/mrna-20261106.htm) (primary-document): MODERNA, INC. Date: November 6, 2026 By: /s/ James M. Mock James M. Mock Chief Financial Officer
- 反证 [ev_954bcfab2ea956c8](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000205/mrna-20261113.htm) (primary-document): Until the Retirement Date, Ms. Klinger will continue to receive her current base salary and benefits and to vest in any outstanding equity awards
- 反证 [ev_954bcfab2ea956c8](https://www.sec.gov/Archives/edgar/data/1682852/000168285226000205/mrna-20261113.htm) (primary-document): Ms. Klinger will receive severance payments paid out in substantially equal biweekly installments over the twelve months following the Retirement Date in an aggregate amount of $1,628,300
- 缺口：CEO Stéphane Bancel的治理评估及近期表态
- 缺口：董事会组成及独立性分析
- 缺口：Klinger离职后法务团队继任安排
- 缺口：内部人交易（Form 4）的近期趋势
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现CEO或其他C-suite高管近期大量抛售股票
- 证伪条件：发现董事会调查或SEC执法行动

## NAUT · complete

审查记录：`state/serenity-reviews/NAUT-claudecli-d2b68987b30112ed3462.json`

### supply_chain_map: unknown

证据显示NAUT开发蛋白质组学平台（Nautilus Voyager），收入来自拨款（GrantRevenue）和服务（ServiceRevenue），但证据包中缺少具体上游供应商、关键原材料输入及下游终端用户的详细披露。仅能从10-Q前瞻性声明中确认产品定位。

- 支持 [ev_78ac054923691a93](https://www.sec.gov/Archives/edgar/data/1808805/000180880526000034/naut-20260630.htm) (primary-document): naut:GrantRevenueMember 2026-04-01 2026-06-30 0001808805 naut:GrantRevenueMember 2025-04-01 2025-06-30
- 支持 [ev_78ac054923691a93](https://www.sec.gov/Archives/edgar/data/1808805/000180880526000034/naut-20260630.htm) (primary-document): naut:ServiceRevenueMember 2026-04-01 2026-06-30 0001808805 naut:ServiceRevenueMember 2025-04-01 2025-06-30
- 缺口：上游关键原材料与仪器供应商名称
- 缺口：下游客户或合作药企的具体身份
- 缺口：供应链各节点的地理集中度信息
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现Nautilus Voyager平台的关键组件有多个现成替代供应商，无供应链独特性

### chokepoint_evidence: unknown

证据包中没有任何段落证明NAUT在蛋白质组学供应链中拥有供应集中度、替代壁垒或不可绕过的瓶颈地位。平台仍处于开发阶段，尚未商业化，无法评估其是否构成chokepoint。

- 缺口：蛋白质组学检测市场的供应集中度数据
- 缺口：竞争对手数量及替代技术路线分析
- 缺口：客户转换成本或锁定机制的证据
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现多家公司提供类似单分子蛋白质组学平台且已商业化
- 证伪条件：下游药企可轻松切换至质谱或其他蛋白质组学方法

### customer_dependency: unknown

证据仅显示收入分为拨款和服务两类，Q3 2026收入仅$234K，但无任何具体客户名称、采用案例或合作协议的披露。无法判断是否有实际客户依赖。

- 支持 [ev_71005e3236979ca2](https://data.sec.gov/api/xbrl/companyfacts/CIK0001808805.json) (sec-companyfacts): Revenue (Revenues): 234,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-10-27
- 缺口：具体客户名称或合作药企披露
- 缺口：设计验证合作或beta测试用户信息
- 缺口：拨款来源机构（如NIH等）的具体信息
- 证伪条件：发现已有药企或研究机构公开确认使用Nautilus Voyager平台

### pure_play: partial

NAUT仅有一个报告分部（ReportableSegment），前瞻性声明明确围绕Nautilus Voyager蛋白质组学平台，收入来源为相关拨款和服务。这表明高度聚焦于蛋白质组学/药物发现主题，但因平台尚在开发阶段、收入极低，主题收入敞口尚无法充分验证。

- 支持 [ev_04a516112b435eb7](https://www.sec.gov/Archives/edgar/data/1808805/000180880526000034/naut-20260630.htm) (primary-document): naut:ReportableSegmentMember 2026-04-01 2026-06-30 0001808805 naut:ReportableSegmentMember 2025-04-01 2025-06-30
- 支持 [ev_76c2233b9aa9cd00](https://www.sec.gov/Archives/edgar/data/1808805/000180880526000052/naut-20260930.htm) (primary-document): our expectations regarding the timing and progress of the development of the Nautilus Voyager platform (including our broadscale assay) and any commercialization timelines
- 缺口：商业化后主题收入占比的预估或指引
- 缺口：蛋白质组学以外是否有其他业务线的说明
- 证伪条件：公司宣布进入与蛋白质组学无关的业务领域，稀释主题敞口

### multi_node_control: unknown

证据包中没有任何段落表明NAUT控制供应链中两个或以上相连节点。公司专注于单一平台开发，无纵向整合的披露。

- 缺口：公司是否自研关键试剂、仪器硬件及软件分析的整合证据
- 缺口：从样品制备到数据分析全链条控制的证据
- 证伪条件：发现NAUT的平台硬件、试剂、软件均外包或依赖第三方

### earnings_validation: partial

准备阶段公司，以资金能力而非收入评判。XBRL显示现金仅$10.5M，但公司持有大量可供出售证券（国债、商业票据、公司债、政府机构债券），背景数据显示总流动性约$86.6M。9个月运营现金流出$40.1M（约$4.5M/月），R&D支出$10.2M/季度与平台开发一致。预估跑道约19个月，超过12个月门槛，可支撑下一阶段里程碑。但证据包内无法直接引用投资总额的确切数字，仅能确认现金偏低。

- 支持 [ev_71005e3236979ca2](https://data.sec.gov/api/xbrl/companyfacts/CIK0001808805.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 10,467,000 for as of 2026-09-30
- 支持 [ev_71005e3236979ca2](https://data.sec.gov/api/xbrl/companyfacts/CIK0001808805.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -40,107,000 for 2026-01-01 to 2026-09-30
- 支持 [ev_71005e3236979ca2](https://data.sec.gov/api/xbrl/companyfacts/CIK0001808805.json) (sec-companyfacts): R&D expense (ResearchAndDevelopmentExpense): 10,176,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_71005e3236979ca2](https://data.sec.gov/api/xbrl/companyfacts/CIK0001808805.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -15,636,000 for 2026-07-01 to 2026-09-30
- 缺口：可供出售证券总额的直接引用（证据仅含XBRL标签，未含汇总金额）
- 缺口：管理层对资金充足性的明确声明（going concern评估）
- 证伪条件：总流动资产（含投资）实际低于12个月烧钱所需
- 证伪条件：发现going concern警告或即将到期的重大债务

### counter_thesis: unknown

可识别多个反面论据：1）平台仍处开发阶段，科学和技术验证风险高；2）收入极低（$234K/季），商业化时间不确定；3）每季度亏损$15.6M，持续消耗现金；4）蛋白质组学市场竞争激烈（质谱、SomaScan等替代路线）。跑道约19个月（financingRisk: false），短期内无强制融资稀释风险。但证据包缺少竞争格局、地缘政治和估值角度的具体数据，压力测试不完整。

- 支持 [ev_71005e3236979ca2](https://data.sec.gov/api/xbrl/companyfacts/CIK0001808805.json) (sec-companyfacts): Revenue (Revenues): 234,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-10-27
- 支持 [ev_71005e3236979ca2](https://data.sec.gov/api/xbrl/companyfacts/CIK0001808805.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -15,636,000 for 2026-07-01 to 2026-09-30
- 缺口：蛋白质组学市场竞争对手的具体数据与市场份额
- 缺口：估值倍数与同行对比分析
- 缺口：监管审批路径和时间表的风险评估
- 缺口：引用不存在或原文无法匹配
- 证伪条件：Nautilus Voyager平台在科学验证中未达预期性能指标
- 证伪条件：竞争对手率先推出更优蛋白质组学平台并获药企广泛采用
- 证伪条件：现金耗尽前未能实现关键商业化里程碑导致高度稀释性融资
- 证伪条件：蛋白质组学在药物发现中的应用未如预期般增长

### management_governance: unknown

证据包中除了标准SEC合规声明外，没有关于管理层背景、治理结构、领导层变动或调查的具体信息。10-Q包含风险因素章节但证据未抽取相关内容。无法评估治理质量或领导层连续性。

- 支持 [ev_1dc83268797943b4](https://www.sec.gov/Archives/edgar/data/1808805/000180880526000034/naut-20260630.htm) (primary-document): Smaller reporting company ☒ Emerging growth company o If an emerging growth company, indicate by check mark
- 缺口：CEO/CTO背景与任期信息
- 缺口：董事会独立性与构成
- 缺口：高管离职或继任计划
- 缺口：是否存在未决调查或诉讼
- 证伪条件：发现关键高管近期离职或正在接受SEC调查
- 证伪条件：治理结构存在严重缺陷（如创始人过度控制无制衡）

## NTRA · complete

审查记录：`state/serenity-reviews/NTRA-claude-cf2f1b7716378cec9cbf.json`

### supply_chain_map: pass

依赖少数供应商（含单一来源），与医疗机构和合作实验室协作；收入集中于 Signatera、Panorama、Horizon 三类检测。

- 支持 [ev_17316dcd0d39652c](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): we rely on a limited number of suppliers or, in some cases, single suppliers, for some of our laboratory instruments and materials
- 支持 [ev_ac41dadc6e2f188f](https://www.sec.gov/Archives/edgar/data/1604821/000162828026071145/ntra-20260930.htm) (primary-document): our reliance on collaborators such as medical institutions, contract laboratories, laboratory partners, and other third parties
- 支持 [ev_46f50f9b9515aaa6](https://www.sec.gov/Archives/edgar/data/1604821/000162828026071145/ntra-20260930.htm) (primary-document): a significant portion of our revenues will be derived from sales of Signatera, Panorama, and Horizon

### chokepoint_evidence: partial

Signatera 获 CMS 的 ADLT 资格，形成报销与证据壁垒；但肿瘤检测领域竞争者众多。

- 支持 [ev_fe65f50c562babf1](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): Signatera has been granted Advanced Diagnostic Laboratory Test, or ADLT, status by the Centers for Medicare & Medicaid Services.
- 反证 [ev_1075f4b7876dd90e](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): In the field of oncology, we compete with various companies that offer or seek to offer competing solutions

### customer_dependency: partial

商业保险覆盖政策提供需求支撑，但缺少客户或付款方集中度数据。

- 支持 [ev_8c31d250beea7102](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): Signatera is also covered under the coverage policies of certain commercial third-party payers
- 缺口：客户或付款方集中度数据

### pure_play: partial

AI 用于 Panorama 检测的结果判定，是诊断业务中的辅助组件，不是核心业务。

- 支持 [ev_e68c4fbe73f4c865](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): Panorama leverages artificial intelligence to enable highly accurate results on samples for which a result would otherwise be difficult to determine.
- 缺口：AI 相关收入占比

### multi_node_control: partial

自建实验室并扩张产能，但证据包未显示对上游或数据节点的控制。

- 支持 [ev_baffcad7aeab18b0](https://www.sec.gov/Archives/edgar/data/1604821/000162828026071145/ntra-20260930.htm) (primary-document): our ability to operate our laboratory facilities and meet expected demand, and to successfully scale our operations
- 缺口：节点控制的一手证据

### earnings_validation: pass

2026 年前三季度经营活动现金流为正，约 1.389 亿美元。

- 支持 [ev_384411bbb373592b](https://www.sec.gov/Archives/edgar/data/1604821/000162828026071145/ntra-20260930.htm) (primary-document): Net cash provided by operating activities 138,895 141,413

### counter_thesis: pass

持续亏损、股权稀释与 FDA 监管 LDT 的风险已用原文检验。

- 支持 [ev_44145ae63992e6ce](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): We have incurred net losses each year since our inception in 2003.
- 反证 [ev_bdb814a354081548](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): investors in our common stock may be materially diluted.
- 反证 [ev_3e2c79fcdfa5410e](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): if the FDA were to begin actively regulating our tests, we could incur substantial costs and delays
- 证伪条件：Signatera 检测量连续两个季度放缓
- 证伪条件：经营现金流转负

### management_governance: partial

内控有效；联合创始人兼董事 Sheena Jonathan 的三笔卖出均依据 10b5-1 计划执行，属董事级别（非 CEO/CFO），且规模相对持仓极小，不构成治理负面信号；但 1,000 万美元关联方投资仍存在，治理门维持 partial。

- 支持 [ev_bacf046749658560](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): we determined that our internal controls over financial reporting were effective as of December 31, 2025
- 支持 [ev_3868aff26caa5ae9](https://www.sec.gov/Archives/edgar/data/1604821/000164664926000045/xslF345X06/form4-11132026_091101.xml) (primary-document): The sale of shares was effected pursuant to a Rule 10b5-1 trading plan adopted by the Reporting Person on June 11, 2026.
- 支持 [ev_7b06502178433b63](https://www.sec.gov/Archives/edgar/data/1604821/000164664926000044/xslF345X06/form4-11102026_091101.xml) (primary-document): The sale of shares was effected pursuant to a Rule 10b5-1 trading plan adopted by the Reporting Person on December 12, 2025.
- 支持 [ev_d8a41d16d8a3e7c9](https://www.sec.gov/Archives/edgar/data/1604821/000164664926000043/xslF345X06/form4-11042026_091115.xml) (primary-document): The sale of shares was effected in order to satisfy tax withholding and remittance obligations in connection with the vesting of RSUs and was made pursuant to a written instruction that is intended to satisfy the affirmative defense conditions of Rule 10b5-1(c) under the Exchange Act
- 反证 [ev_a2f5fe2a1a923286](https://www.sec.gov/Archives/edgar/data/1604821/000162828026071145/ntra-20260930.htm) (primary-document): Investment in related party ( 10,000 )

## NVDA · complete

审查记录：`state/serenity-reviews/NVDA-claudecli-3125230aa3039c464d4d.json`

### supply_chain_map: unknown

证据清晰呈现三层结构：上游为台积电（晶圆）、Kinsus/三星电机（基板）、Amkor/SPIL（先进封装）、富士康（整机制造）；公司产品为Vera Rubin GPU系统、Vera CPU、Spectrum-X网络及CUDA平台；下游客户包括CoreWeave、Google Cloud、Microsoft Azure、Oracle Cloud、Meta、OpenAI等超大规模云厂商，关系均有具体协议或部署记录支撑。

- 支持 [ev_31f917bd900135e4](https://nvidianews.nvidia.com/news/nvidia-expands-commitments-with-supply-chain-partners-to-support-ai-infrastructure-buildout) (primary-feed): Working with Amkor Technology, Foxconn, Kinsus Interconnect Technology, Samsung Electro-Mechanics , Siliconware Precision Industries (SPIL) and TSMC, NVIDIA is expanding manufacturing capacity across substrates, advanced packaging, wafer and contract manufacturing
- 支持 [ev_a24bc3ab83af5791](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027) (primary-document): racks running at partners including CoreWeave, Google Cloud, Microsoft Azure, Oracle Cloud Infrastructure and Nebius
- 缺口：各上游供应商的收入占比与集中度数据
- 缺口：NVIDIA对TSMC先进制程的依赖度量化指标
- 缺口：引用不存在或原文无法匹配
- 证伪条件：若TSMC或关键基板供应商出现重大产能中断且NVIDIA无替代来源，将削弱供应链韧性评级

### chokepoint_evidence: partial

证据显示CUDA生态系统拥有超过1100万开发者，构成较高的软件层切换壁垒；但证据未提供NVIDIA在AI训练/推理算力市场的具体份额数字，也未量化从CUDA迁移至竞争平台的时间成本或替代周期。按照Serenity框架，AI相关性本身不足以判定为卡脖子节点，缺乏市场集中度数据，只能评为partial。

- 支持 [ev_7a9799f5130ef1e4](https://blogs.nvidia.com/blog/20-years-cuda/) (primary-document): more than 11 million developers build on CUDA across the computing stack
- 支持 [ev_3f42693d51e540f2](https://blogs.nvidia.com/blog/20-years-cuda/) (primary-document): With 1,000+ NVIDIA CUDA-X libraries, developers are now reshaping industries
- 缺口：NVIDIA GPU在AI训练/推理市场的全球份额数据
- 缺口：从CUDA迁移至竞争平台的重新认证周期
- 缺口：AMD/Intel/自研芯片替代GPU的技术可行性证据
- 证伪条件：若超大规模云厂商大规模部署自研AI芯片并显著减少NVIDIA采购，则chokepoint地位受到实质威胁

### customer_dependency: unknown

证据中明确点名多个超大规模云厂商和AI原生公司，均有具体产品部署记录，不仅是合作公告。CoreWeave、Google Cloud、Microsoft Azure、Oracle Cloud、Meta、OpenAI、AWS等均作为Vera Rubin或Vera CPU客户被具名披露，客户依赖关系充分。

- 支持 [ev_a24bc3ab83af5791](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027) (primary-document): leading AI natives, cloud providers and neoclouds, including CoreWeave, Meta, Nebius, Nscale, OpenAI and Verda, are building with NVIDIA Vera CPUs
- 缺口：前五大客户的营收集中度（是否有单一客户超过10%）
- 缺口：长期供货协议的具体条款和锁定期
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：若某主要超大规模客户公开宣布将NVIDIA GPU替换为自研芯片并披露时间表，则客户依赖关系出现实质裂缝

### pure_play: unknown

数据中心业务季度收入1076亿美元，占季度总收入1158亿美元约93%，高度集中于AI/加速计算主题；边缘计算（82亿美元，约7%）为次要分部，不构成实质稀释。整体收入结构与AI基础设施主题高度一致。

- 支持 [ev_18276e0fe24d4bae](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027) (primary-document): Data Center revenue of $107.6 billion, up 110% from a year ago
- 支持 [ev_18276e0fe24d4bae](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027) (primary-document): Revenue of $115.8 billion, up 103% from a year ago
- 缺口：数据中心收入内部AI推理vs训练vs其他的细分占比
- 缺口：引用不存在或原文无法匹配
- 证伪条件：若边缘/消费类分部占比大幅提升至30%以上，将削弱纯正AI基础设施标签

### multi_node_control: unknown

证据显示NVIDIA同时控制GPU（Vera Rubin）、CPU（Vera CPU）、网络（Spectrum-X、BlueField DPU）及软件平台（CUDA/CUDA-X），跨越AI工厂供应链中的多个相连节点。然而NVIDIA为无晶圆厂模式，制造节点依赖TSMC等代工，对晶圆制造节点的控制属于设计层面而非实物生产层面。按照rubric对控制的严格定义，partial更为审慎。

- 支持 [ev_a24bc3ab83af5791](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027) (primary-document): leading AI natives, cloud providers and neoclouds, including CoreWeave, Meta, Nebius, Nscale, OpenAI and Verda, are building with NVIDIA Vera CPUs
- 支持 [ev_7a9799f5130ef1e4](https://blogs.nvidia.com/blog/20-years-cuda/) (primary-document): more than 11 million developers build on CUDA across the computing stack
- 缺口：NVIDIA自有或独家控制的物理制造节点证据
- 缺口：网络与GPU节点之间的供应链互锁机制（如捆绑销售协议）
- 缺口：引用不存在或原文无法匹配
- 证伪条件：若客户可在不采购NVIDIA网络设备的情况下单独部署Vera Rubin GPU，则各节点之间的互锁控制不成立

### earnings_validation: partial

Q3 FY2027（截至2026年10月25日）财报提供充分的有日期实际财务数据：季度收入1158亿美元、同比增103%、净利润653亿美元、毛利率74.8%；九个月累计收入2937亿美元。数据来自经审阅的合并利润表，完全支持超高速增长论点。

- 支持 [ev_18276e0fe24d4bae](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027) (primary-document): Revenue of $115.8 billion, up 103% from a year ago
- 支持 [ev_328262b3ee5fcca9](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027) (primary-document): Revenue $ 115,844 $ 57,006 $ 293,681 $ 147,811
- 支持 [ev_328262b3ee5fcca9](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027) (primary-document): Net income $ 65,287 $ 31,910 $ 183,297 $ 77,107
- 支持 [ev_18276e0fe24d4bae](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027) (primary-document): GAAP and non-GAAP gross margins were 74.8% and 74.9%, respectively
- 缺口：自由现金流完整数字（现金流量表在证据中被截断）
- 缺口：通过需要直接相关的原始披露及完整证据
- 证伪条件：若下季度收入指引1300亿美元大幅落空，则增长轨迹论点受损

### counter_thesis: unknown

证据显示一项重要反论：中国市场已被完全排除在收入指引之外，出口管制构成实质性需求侧风险；另外Jensen Huang遭外国情报渗透事件引发治理风险。但证据中未见对竞争性替代路径（AMD GPU、自研ASIC）的系统性审查，也未见对估值风险或需求周期性的压力测试，反论检验不完整，评为partial。

- 支持 [ev_a24bc3ab83af5791](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027) (primary-document): NVIDIA is not assuming any Data Center compute revenue from China in its outlook
- 支持 [ev_79e00ca107c914f4](https://nvidianews.nvidia.com/news/statement-from-nvidia-board-of-directors) (primary-document): The NVIDIA Board is initiating an independent investigation in light of recent reporting that founder and CEO Jensen Huang has been the target of a foreign intelligence effort
- 缺口：AMD/Intel及自研芯片对NVIDIA市场份额的实际侵蚀数据
- 缺口：AI资本支出周期性放缓的情景分析
- 缺口：估值相对盈利增速的合理性论证
- 缺口：引用不存在或原文无法匹配
- 证伪条件：超大规模云厂商公开披露削减NVIDIA采购预算并转向自研芯片；出口管制范围扩大至当前非中国市场

### management_governance: unknown

Jensen Huang已于2026年11月23日恢复CEO职务，但独立调查委员会明确声明调查将继续进行至结论，属于未结案调查。按照rubric规则，存在未结案调查不得评为pass。公司同步新设国家安全及出口管制监督委员会，并启动首席合规官职位搜寻，治理架构持续演变中。

- 支持 [ev_82a475349174de34](https://nvidianews.nvidia.com/news/nvidia-board-reinstates-jensen-huang-as-president-ceo-and-board-director) (primary-document): Jensen Huang has been reinstated as President and Chief Executive Officer and as a member of the Board. The Board of Directors voted unanimously to reinstate Mr. Huang
- 反证 [ev_7096a0a30c7e47b4](https://nvidianews.nvidia.com/news/nvidia-board-reinstates-jensen-huang-as-president-ceo-and-board-director) (primary-document): NVIDIA will continue to cooperate with ongoing government investigations and inquiries
- 缺口：独立调查的具体调查范围与预计完成时间
- 缺口：新任首席合规官的委任进展
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：若独立调查发现实质性违规事项并导致Jensen Huang再次离职，或美国政府调查升级为正式起诉，治理风险将由partial升为fail

## OABI · complete

审查记录：`state/serenity-reviews/OABI-claudecli-e6f2e26a6ffe7efaaadf.json`

### supply_chain_map: partial

证据显示OABI是药物发现平台公司，收入分为许可/里程碑、服务、xPloration和版税四个来源，可以推断上游是抗体发现技术，下游是制药/生物技术客户。但缺乏具体上游供应商和下游客户的披露，无法绘制完整供应链图。

- 支持 [ev_508fc2bea9773f60](https://www.sec.gov/Archives/edgar/data/1846253/000184625326000051/oabi-20260930.htm) (primary-document): License and milestone revenue $ 100 $ 616 $ 21,640 $ 3,879 Service revenue 2,835 1,188 7,415 5,027 xPloration revenue 703 74 1,918 724 Royalty revenue 355 361 862 660
- 支持 [ev_1eb0bef5372738ac](https://www.sec.gov/Archives/edgar/data/1846253/000184625326000046/oabi-20260630.htm) (primary-document): Commission File Number: 001-40720 OMNIAB, INC. (Exact name of registrant as specified in its charter) Delaware 98-1584818
- 缺口：具体上游供应商（实验设备、试剂等）的名称和集中度
- 缺口：具体下游客户（制药公司）的名称和合同详情
- 缺口：供应链各节点的地理分布和替代性分析
- 证伪条件：发现OABI平台技术有多个直接竞争者且客户转换成本低
- 证伪条件：上游关键试剂/设备完全是通用商品无集中风险

### chokepoint_evidence: unknown

证据中没有任何关于供应集中度或替代壁垒的信息。OABI是药物发现平台，属于生物技术服务领域，该领域存在多种替代技术路线（噬菌体展示、人源化小鼠等）。仅凭AI药物发现主题无法认定为瓶颈。

- 缺口：OABI平台技术相对竞争对手（Abcellera、Berkeley Lights等）的不可替代性证据
- 缺口：客户锁定周期或转换成本的定量数据
- 缺口：全球抗体发现市场供应方集中度数据
- 证伪条件：发现主要制药客户同时使用多个抗体发现平台
- 证伪条件：竞争对手技术在关键指标上达到或超越OABI

### customer_dependency: unknown

10-Q报表虽然显示有应收账款和递延收入（表明有活跃客户），但所有证据段落中均未披露任何具体客户名称或合作关系。无法确认下游采用情况。

- 支持 [ev_25c1925d6d5b039d](https://www.sec.gov/Archives/edgar/data/1846253/000184625326000051/oabi-20260930.htm) (primary-document): Accounts receivable, net 2,573 7,390 Prepaid expenses and other current assets 4,195
- 支持 [ev_25c1925d6d5b039d](https://www.sec.gov/Archives/edgar/data/1846253/000184625326000051/oabi-20260930.htm) (primary-document): Current deferred revenue 5,238 3,161
- 缺口：任何具名客户或合作伙伴的披露
- 缺口：客户集中度信息（如前十大客户收入占比）
- 缺口：具体许可协议或里程碑达成的详情
- 证伪条件：发现所有收入来自少数1-2个客户且合同即将到期
- 证伪条件：主要客户终止合作或转向竞争平台

### pure_play: partial

OABI的四个收入来源（许可/里程碑、服务、xPloration、版税）均围绕药物发现平台主题，看起来是纯粹的药物发现公司。但证据中缺乏收入按业务分部的详细披露来确认100%暴露于该主题。XBRL数据提及ReportableSegmentMember但未给出分部名称和收入明细。

- 支持 [ev_508fc2bea9773f60](https://www.sec.gov/Archives/edgar/data/1846253/000184625326000051/oabi-20260930.htm) (primary-document): Total revenue 3,993 2,239 31,835 10,290 Costs and operating expenses: Cost of xPloration revenue 309 29 934 294 Research and development 9,553 10,379
- 支持 [ev_27cf76901546967e](https://www.sec.gov/Archives/edgar/data/1846253/000184625326000046/oabi-20260630.htm) (primary-document): License and milestone revenue $ 9,515 $ 1,242 $ 21,540 $ 3,263 Service revenue 2,473 1,936 4,580 3,839 xPloration revenue 1,161 608 1,215 650 Royalty revenue 266 111 507 299 Total revenue 13,415 3,897 27,842 8,051
- 缺口：业务分部报告确认药物发现平台为唯一报告分部
- 缺口：AI相关收入的具体占比（如果以AI药物发现为投资主题）
- 证伪条件：发现有重大非药物发现收入来源未在证据中体现

### multi_node_control: unknown

证据中未显示OABI控制供应链的多个相连节点。公司提供药物发现平台服务，但没有证据表明其纵向整合了多个瓶颈环节（例如从抗体发现到临床前开发到生产）。

- 缺口：OABI在药物发现价值链中覆盖的具体环节
- 缺口：纵向整合或多节点控制的证据
- 缺口：与Icagen收购相关的能力扩展详情
- 证伪条件：发现OABI仅提供单一环节服务，客户可轻易在各环节拆分供应商

### earnings_validation: partial

有实际财务数据：Q3 2026收入399.3万美元，同比增长78.3%；但Q3许可/里程碑收入仅10万美元（vs Q2的951.5万），收入极度不均。九个月收入3,183.5万vs去年1,029万，增长显著但主要集中在H1。公司仍大幅亏损（Q3净亏1,572.8万），尚不能验证盈利论点。

- 支持 [ev_004cade208a19744](https://data.sec.gov/api/xbrl/companyfacts/CIK0001846253.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 3,993,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-10-30
- 支持 [ev_508fc2bea9773f60](https://www.sec.gov/Archives/edgar/data/1846253/000184625326000051/oabi-20260930.htm) (primary-document): Net loss $ ( 15,728 ) $ ( 16,525 ) $ ( 29,294 ) $ ( 50,600 ) Net loss per share, basic and diluted $ ( 0.12 ) $ ( 0.14 ) $ ( 0.23 ) $ ( 0.46 )
- 支持 [ev_004cade208a19744](https://data.sec.gov/api/xbrl/companyfacts/CIK0001846253.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 2,239,000, a change of +78.3%
- 支持 [ev_004cade208a19744](https://data.sec.gov/api/xbrl/companyfacts/CIK0001846253.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): 8,340,000 for 2026-01-01 to 2026-09-30
- 反证 [ev_508fc2bea9773f60](https://www.sec.gov/Archives/edgar/data/1846253/000184625326000051/oabi-20260930.htm) (primary-document): License and milestone revenue $ 100 $ 616 $ 21,640 $ 3,879 Service revenue 2,835 1,188 7,415 5,027
- 缺口：收入可持续性分析——H1许可/里程碑收入2,154万在Q3骤降至10万的原因
- 缺口：盈利时间表或达到现金流正的路径
- 证伪条件：许可/里程碑收入为一次性事件且未来无类似管线
- 证伪条件：运营亏损持续扩大导致需要额外融资稀释

### counter_thesis: unknown

可从财务数据识别主要风险：(1)收入极度依赖许可/里程碑的波动性；(2)持续大额亏损；(3)现金约6,420万但每季度亏损约1,500万；(4)已有ATM发行和私募融资历史。但缺乏对竞争替代、地缘政治和估值角度的充分压力测试。

- 支持 [ev_508fc2bea9773f60](https://www.sec.gov/Archives/edgar/data/1846253/000184625326000051/oabi-20260930.htm) (primary-document): Loss from operations ( 16,368 ) ( 18,140 ) ( 30,834 ) ( 53,203 ) Other income (expense), net: Interest income 524 462 1,445 1,435
- 支持 [ev_25c1925d6d5b039d](https://www.sec.gov/Archives/edgar/data/1846253/000184625326000051/oabi-20260930.htm) (primary-document): Cash and cash equivalents $ 22,883 $ 25,524 Short-term investments 41,327 28,501
- 反证 [ev_004cade208a19744](https://data.sec.gov/api/xbrl/companyfacts/CIK0001846253.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -15,728,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-10-30
- 反证 [ev_004cade208a19744](https://data.sec.gov/api/xbrl/companyfacts/CIK0001846253.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 22,883,000 for as of 2026-09-30; form 10-Q filed 2026-10-30
- 缺口：竞争格局分析——Abcellera、Twist Bioscience等替代平台的市场份额
- 缺口：估值合理性分析（市值7.37亿 vs 年化收入约1,870万）
- 缺口：生物技术行业融资环境对OABI持续经营的影响
- 缺口：引用不存在或原文无法匹配
- 证伪条件：许可/里程碑收入H1集中为一次性大单，未来管线无法复现
- 证伪条件：竞争对手AI驱动的药物发现平台快速追赶消除OABI差异化
- 证伪条件：现金消耗速度加快迫使在低位增发稀释股东
- 证伪条件：P/S超过39倍（市值737M/收入18.7M年化），估值过高风险
- 证伪条件：关键合作伙伴/客户流失导致收入断崖下跌

### management_governance: unknown

证据段落中未包含任何关于管理层组成、变动、治理结构或调查的信息。10-Q的XBRL和财务报表部分不涉及管理层讨论。无法评估。

- 缺口：管理层名单及任期
- 缺口：近期高管变动或继任计划
- 缺口：董事会独立性和治理评级
- 缺口：任何未决调查或诉讼信息
- 证伪条件：发现关键高管近期离职
- 证伪条件：发现SEC调查或审计意见保留

## ODTX · complete

审查记录：`state/serenity-reviews/ODTX-claudecli-7c0ea3c3708c900c70c0.json`

### supply_chain_map: unknown

证据仅部分揭示供应链关系。XBRL标签提及Pfizer和Janssen合作安排，以及IFM Discovery LLC关系，但缺乏对上游投入（CRO、CMO、原料药供应商）和下游用户（患者群体、支付方）的具体描述。作为临床阶段药企，供应链尚未完全建立。

- 支持 [ev_00db8be00fac9327](https://www.sec.gov/Archives/edgar/data/1882782/000119312526446208/odtx-20260930.htm) (primary-document): us-gaap:CollaborativeArrangementTransactionWithPartyToCollaborativeArrangementMember us-gaap:TransferredOverTimeMember odtx:PfizerIncMember 2026-01-01 2026-09-30
- 支持 [ev_fc5d25138b10f965](https://www.sec.gov/Archives/edgar/data/1882782/000119312526446208/odtx-20260930.htm) (primary-document): odtx:JanssenPharmaceuticaNVMember 2025-01-01 2025-09-30
- 缺口：上游CRO/CMO/原料药供应商的具体名称和关系
- 缺口：下游患者群体、目标适应症市场规模和支付方结构
- 缺口：Pfizer和Janssen合作的具体内容和条款描述
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现公司核心管线的CRO/CMO供应商高度可替代，无任何供应链壁垒

### chokepoint_evidence: unknown

无任何证据表明ODTX在药物发现供应链中占据瓶颈地位。药物发现公司的竞争优势通常来自知识产权和临床数据，而非物理供应集中度。证据中未出现供应集中度或替代壁垒的相关信息。

- 缺口：公司核心技术平台（如TNFR2激动剂）是否具有独占性或难以替代的证据
- 缺口：竞争对手在同一靶点或适应症领域的活跃程度
- 缺口：专利保护范围和持续时间
- 证伪条件：多家竞争对手在TNFR2或相同靶点拥有类似阶段的管线
- 证伪条件：公司技术平台无核心专利保护

### customer_dependency: partial

XBRL标签确认存在Pfizer和Janssen的合作安排及收入确认，表明存在实质性合作关系。但证据仅为会计标签，缺乏合作具体内容（许可、共同开发、里程碑付款等）的描述性文本。Phase 2a临床结果的公布表明管线在推进，但尚无最终用户（患者）的采用证据。

- 支持 [ev_00db8be00fac9327](https://www.sec.gov/Archives/edgar/data/1882782/000119312526446208/odtx-20260930.htm) (primary-document): us-gaap:CollaborativeArrangementTransactionWithPartyToCollaborativeArrangementMember us-gaap:TransferredOverTimeMember odtx:PfizerIncMember 2026-01-01 2026-09-30
- 支持 [ev_d379e7b84d634e43](https://www.sec.gov/Archives/edgar/data/1882782/000119312526446208/odtx-20260930.htm) (primary-document): us-gaap:CollaborativeArrangementTransactionWithPartyToCollaborativeArrangementMember us-gaap:UpFrontPaymentArrangementMember odtx:JanssenPharmaceuticaNVMember 2024-03-29
- 支持 [ev_c58bf5967769618a](https://www.sec.gov/Archives/edgar/data/1882782/000119312526425684/odtx-20261020.htm) (primary-document): Odyssey Therapeutics Presents Completed Phase 2a OD-001 Induction Results Strengthening Clinical Proof of Concept at UEG Week 2026
- 缺口：Pfizer和Janssen合作的具体条款、里程碑金额和权利义务
- 缺口：合作是否涉及核心管线还是非核心资产
- 缺口：任何产品的商业化客户或终端用户采用数据
- 证伪条件：Pfizer或Janssen终止合作协议
- 证伪条件：Phase 2临床试验未达主要终点

### pure_play: partial

ODTX为临床阶段药物发现公司，管线集中于炎症免疫领域（OD-001溃疡性结肠炎Phase 2a、OD-07656 Phase 2招募中、TNFR2激动剂）。从临床试验和研发支出看，公司专注于药物发现，符合纯正标的特征。但证据中缺乏收入分部数据（因无收入），且与AI医学主题的直接关联未在证据中体现。

- 支持 [ev_ef54d5592efe22f5](https://clinicaltrials.gov/study/NCT06850727) (clinicaltrials-gov): Safety and Efficacy of OD-07656 and of Subsequent Vedolizumab Therapy in Moderately to Severely Active Ulcerative Colitis
- 支持 [ev_58da533cad402db9](https://data.sec.gov/api/xbrl/companyfacts/CIK0001882782.json) (sec-companyfacts): R&D expense (ResearchAndDevelopmentExpense): 42,121,000 for 2026-07-01 to 2026-09-30
- 缺口：公司是否使用AI技术进行药物发现的具体证据
- 缺口：业务分部或管线优先级的描述性文本
- 缺口：与AI医学主题的明确关联
- 证伪条件：公司大部分资源投入与核心主题无关的领域

### multi_node_control: unknown

无证据表明ODTX控制供应链中两个或以上相连节点。作为临床阶段生物制药公司，通常依赖外部CRO和CMO进行临床试验和生产，不太可能垂直整合多个供应链节点。

- 缺口：公司是否拥有自有生产设施
- 缺口：公司是否控制从靶点发现到临床开发的完整价值链
- 缺口：技术平台是否覆盖多个治疗节点
- 证伪条件：公司所有临床和生产活动完全外包

### earnings_validation: partial

作为preparation阶段（Phase 2）公司，零收入本身不构成失败理由。XBRL数据提供了真实的、有日期的财务数据：Q3 2026净亏损5306万美元，年初至今运营现金流出1.17亿美元，报告现金8064万美元。结合上下文（总流动性约3.26亿美元含短期投资，月均消耗约1300万美元，跑道约25个月），公司可支撑下一个临床里程碑。但仅凭可引用证据中的现金数字（8064万），与季度约3900万的消耗相比偏紧，需要额外流动性确认。

- 支持 [ev_58da533cad402db9](https://data.sec.gov/api/xbrl/companyfacts/CIK0001882782.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -53,059,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04
- 支持 [ev_58da533cad402db9](https://data.sec.gov/api/xbrl/companyfacts/CIK0001882782.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -117,085,000 for 2026-01-01 to 2026-09-30 (year-to-date total as reported)
- 支持 [ev_58da533cad402db9](https://data.sec.gov/api/xbrl/companyfacts/CIK0001882782.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 80,641,000 for as of 2026-09-30; form 10-Q filed 2026-11-04
- 支持 [ev_58da533cad402db9](https://data.sec.gov/api/xbrl/companyfacts/CIK0001882782.json) (sec-companyfacts): R&D expense (ResearchAndDevelopmentExpense): 42,121,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04
- 缺口：短期投资和总流动性的具体引用数据
- 缺口：管理层对现金跑道的指引
- 缺口：IPO融资金额的具体引用（2026年5月IPO）
- 证伪条件：总流动性（含短期投资）不足以支撑12个月以上的运营
- 证伪条件：消耗速率突然大幅上升超出预期

### counter_thesis: partial

基于可用证据可识别以下主要风险：(1) 临床失败风险——Phase 2a结果已发布但未包含具体数据；(2) 收入为零且前年同期仅9.9万美元（来自合作），高度依赖管线成功；(3) 现金消耗高（季度约3900-5300万），需持续融资；(4) IPO锁定期于2026年11月到期，可能面临抛售压力。跑道约25个月（>12个月），融资风险不高，但证据中缺乏对竞争格局、替代疗法和估值合理性的分析。

- 支持 [ev_58da533cad402db9](https://data.sec.gov/api/xbrl/companyfacts/CIK0001882782.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 0 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04
- 支持 [ev_b985e0ee5e413864](https://news.google.com/rss/articles/CBMi5gFBVV95cUxOcVZzcUJvRlpmUjFiVzcwY2xTOFBmWmt6Zm5SR3JvRXJCMXo2UTlaLXRRd3J3azRCeGtTUGJNTVBNeVEtS2JfdjRvZk01ZjB3OVRTeE00V1F3ZFRnWl9tdk9nbjV5QnRQcmhGakc5RS13ZHpYVk81RWI3Yk5wZnZMTlRpcmFVT1hsRW9sZTRoSXlQdU43V25zeXlPU0h2Q3Ztc3QxTXR2eEhRM0dVR1BmaHY3WlJyeGVBamF2TXVSV0FjMEV4b1lGUHh5eGRmSmN5QWtUYzJ3MG5XOW1LaVZtTTQwVXBDQQ?oc=5) (news-feed): Certain Warrants of Odyssey Therapeutics, Inc. are subject to a Lock-Up Agreement Ending on 4-NOV-2026
- 支持 [ev_58da533cad402db9](https://data.sec.gov/api/xbrl/companyfacts/CIK0001882782.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 99,000, a change of -100.0%
- 反证 [ev_58da533cad402db9](https://data.sec.gov/api/xbrl/companyfacts/CIK0001882782.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -53,059,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04
- 缺口：溃疡性结肠炎和TNFR2靶点的竞争格局分析
- 缺口：Phase 2a具体临床数据和与竞品的对比
- 缺口：估值合理性分析（$920M市值 vs 临床阶段无收入）
- 缺口：地缘政治或监管风险评估
- 证伪条件：Phase 2/3临床试验失败或安全性问题
- 证伪条件：Pfizer或Janssen终止合作
- 证伪条件：竞争对手在同一适应症获批更优疗法
- 证伪条件：现金跑道不足以完成关键临床里程碑
- 证伪条件：IPO后锁定期到期引发大股东减持

### management_governance: partial

证据仅显示CFO Jason Haas签署了2026年11月4日的8-K报告，确认其在职。公司为新兴成长型公司（emerging growth company），在Nasdaq上市。缺乏CEO和其他高管信息、董事会构成、治理结构和领导连续性的证据。

- 支持 [ev_cf0512e0b941dcb4](https://www.sec.gov/Archives/edgar/data/1882782/000119312526446174/odtx-20261104.htm) (primary-document): Odyssey Therapeutics, Inc. Date: November 4, 2026 By: /s/ Jason Haas Jason Haas Chief Financial Officer
- 支持 [ev_c58bf5967769618a](https://www.sec.gov/Archives/edgar/data/1882782/000119312526425684/odtx-20261020.htm) (primary-document): Emerging growth company ☒ If an emerging growth company, indicate by check mark if the registrant has elected not to use the extended transition period
- 缺口：CEO及创始团队背景和在职状态
- 缺口：董事会构成和独立性
- 缺口：高管薪酬结构和激励对齐
- 缺口：是否存在未解决的调查或诉讼
- 证伪条件：发现关键高管近期离职
- 证伪条件：存在SEC调查或重大诉讼
- 证伪条件：治理结构存在严重缺陷（如无独立董事）

## OM · complete

审查记录：`state/serenity-reviews/OM-claudecli-32927753a5a7c9fc2f30.json`

### supply_chain_map: partial

上游：约100家供应商提供泵、电机、阀门、PCBA等关键组件，部分为单一来源供应商；墨西哥和东南亚有合同制造商。产品：Tablo透析系统（主机、耗材滤芯、云服务TabloHub）。下游：美国急性、急性后护理及家庭透析市场，通过直销团队销售。供应链结构基本清晰，但缺少具体供应商名称和地理集中度量化数据。

- 支持 [ev_2169e95214fa6a05](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): The number of suppliers required for Tablo console production is approximately 100 worldwide. We consider a discrete number of these suppliers, located in the United States, Mexico, Europe and Asia, as critical providers of components such as pumps, motors, valves and Printed Circuit Board Assembly (PCBA) boards.
- 支持 [ev_2169e95214fa6a05](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): we continue to utilize a contract manufacturing partner in Southeast Asia, for the production of a small portion of our Tablo cartridges to supplement our in-house manufacturing production
- 支持 [ev_b73f251b255d3f2e](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): We primarily sell our solutions through our direct sales organization, which covers most major metropolitan markets in the United States.
- 缺口：具体供应商名称（泵、电机、阀门、PCBA供应商身份）
- 缺口：供应商地理集中度的量化数据
- 缺口：关键组件的替代周期和成本
- 证伪条件：发现关键组件已实现多源供应，消除单一来源风险
- 证伪条件：主要组件全部为通用商品，无供应链特殊性

### chokepoint_evidence: unknown

Outset Medical是透析设备制造商，不是供应链瓶颈节点。公司明确表示几乎所有材料和组件都存在替代供应商，不具备供应集中度或替代壁垒。33项美国专利提供一定知识产权保护，但无证据表明其在任何供应链节点具有垄断或寡头地位。与AI无明确关联。

- 支持 [ev_bab6cca9049e3663](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): As of December 31, 2025, we had 33 issued U.S. patents, as well as 8 pending U.S. patent applications.
- 反证 [ev_023201a4ba8050c6](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): we believe replacement suppliers exist for all most all materials, components and services necessary to continue manufacturing Tablo
- 缺口：公司在任何供应链节点的市场份额数据
- 缺口：替代产品的转换时间和成本
- 缺口：与AI医疗主题的具体关联证据
- 证伪条件：发现Tablo在某一透析细分市场占据垄断地位
- 证伪条件：发现某一关键AI医疗应用依赖Tablo平台

### customer_dependency: unknown

披露了客户集中度数据：最大客户占收入15%（2025年），两个客户分别占应收账款11%和10%。但未披露任何具体客户名称，无法确认是否有设计锁定或长期合约依赖关系。销售团队占全职员工58%，表明积极的客户开发，但缺乏具体采用案例。

- 支持 [ev_c88f467876eecba2](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): Two customers accounted for 11 % and 10 % of accounts receivable as
- 支持 [ev_b73f251b255d3f2e](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): Our field sales and service teams represent 58% of our total full-time employees as of December 31, 2025.
- 缺口：具体客户名称（医院系统、透析连锁机构）
- 缺口：长期供应合同或采购承诺
- 缺口：客户转换成本或锁定机制的证据
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现主要客户转向竞争对手产品
- 证伪条件：主要医院系统公开选择替代透析方案

### pure_play: partial

公司100%聚焦于Tablo透析系统：主机26%、耗材45%、服务29%（2025年收入）。是透析设备的纯正标的，但无任何证据将其业务与AI医疗主题关联。筛选上下文标记为Imaging & devices，但实际产品为透析设备，不涉及成像或AI。

- 支持 [ev_b73f251b255d3f2e](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): sales of our consoles, which includes Tablo consoles and accessories, accounted for 26%, 26% and 47% of our revenue, respectively
- 支持 [ev_b73f251b255d3f2e](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): sales of our consumables accounted for 45%, 45% and 32% of our revenue, respectively, and sales of service and other accounted for 29%, 29% and 21% of our revenue, respectively.
- 缺口：与AI医疗主题的收入关联证据
- 缺口：AI或机器学习在产品中的应用描述
- 缺口：数字健康或AI辅助诊断相关收入
- 证伪条件：发现Tablo平台集成了AI诊断或治疗优化功能并产生收入
- 证伪条件：公司进入AI驱动的肾病管理领域

### multi_node_control: unknown

公司在透析领域覆盖硬件（主机）、耗材（滤芯）、软件（TabloHub云平台）和服务，但这些是同一产品的不同收入组成部分，不构成对供应链中两个相连节点的控制。无证据表明公司控制上游关键材料或下游分销渠道的瓶颈节点。

- 支持 [ev_b73f251b255d3f2e](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): We generate revenue from the placement of Tablo consoles along with accessories, and shipping and handling charged to customers
- 缺口：对上游关键组件的垂直整合证据
- 缺口：对下游透析服务或患者管理的控制证据
- 缺口：跨供应链节点的竞争优势分析
- 证伪条件：发现公司收购或自产关键组件形成垂直整合
- 证伪条件：发现公司控制透析耗材供应链上游原材料

### earnings_validation: partial

公司有实际收入：2025年全年$119.5M，Q3 2026收入$33.6M同比增长14.2%。但仍在亏损（Q3 2026净亏损$14.7M）。现金及投资合计约$136.6M（上下文），月均消耗约$3.65M，跑道约37个月，短期无融资风险。收入从2023年$130M下降至2024年$114M后恢复增长，趋势需关注。无AI医疗论点可供财务验证。

- 支持 [ev_4563f88ab65a2af2](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): Consoles $ 30,733 $ 29,832 $ 61,331 Consumables 54,075 51,145 42,206 Total product revenue 84,808 80,977 103,537 Service and other revenue 34,668 32,712 26,839 Total revenue $ 119,476 $ 113,689 $ 130,376
- 支持 [ev_bf6bdfca7cc9247b](https://data.sec.gov/api/xbrl/companyfacts/CIK0001484612.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 33,596,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_bf6bdfca7cc9247b](https://data.sec.gov/api/xbrl/companyfacts/CIK0001484612.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 33,942,000 for as of 2026-09-30
- 反证 [ev_bf6bdfca7cc9247b](https://data.sec.gov/api/xbrl/companyfacts/CIK0001484612.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -14,686,000 for 2026-07-01 to 2026-09-30
- 缺口：毛利率趋势和盈利时间表
- 缺口：与AI医疗主题相关的收入或增长动力
- 缺口：Perceptive信贷协议的具体条款和财务约束
- 证伪条件：收入恢复逆转重新下降
- 证伪条件：现金消耗加速导致跑道缩短至12个月以下
- 证伪条件：信贷协议触发违约条款

### counter_thesis: partial

反面论点部分可检验：1）供应端——依赖单一来源供应商，替代需要时间和成本；2）需求端——收入曾从$130M降至$114M，主机收入占比从47%降至26%，增长依赖耗材和服务转化；3）替代——传统透析巨头资源远超OM，可能开发竞品；4）估值——$60M市值对应$134M收入和持续亏损，可能是价值陷阱；5）AI关联——无证据支持AI医疗主题。缺乏竞争对手具体动态的引用数据。

- 支持 [ev_2169e95214fa6a05](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): We rely on third-party suppliers, including in some instances single source suppliers, to provide us with certain components of Tablo.
- 支持 [ev_4563f88ab65a2af2](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): Total revenue $ 119,476 $ 113,689 $ 130,376
- 反证 [ev_023201a4ba8050c6](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): establishing additional or replacement suppliers for any of these materials, components or services could be time-consuming and expensive, may result in interruptions in our operations and product delivery
- 缺口：具体竞争对手的市场份额和产品动态
- 缺口：家庭透析市场渗透率和竞争格局
- 缺口：监管风险（FDA审批、报销政策变化）的具体评估
- 证伪条件：主要竞争对手推出同等功能的便携透析设备
- 证伪条件：CMS透析报销政策变化不利于Tablo经济模型
- 证伪条件：关键单一来源供应商中断导致产品交付失败
- 证伪条件：家庭透析IDE试验未能获得FDA批准

### management_governance: partial

内部控制有效（截至2025年12月31日），经独立审计确认。2026年2月批准关键高管（Renee Gaeta、John Brottem、Marc Nash）一次性现金留任奖金，旨在支持领导层连续性。无10b5-1交易安排变更。但缺乏CEO身份确认、董事会构成、以及近期高管变动情况的详细证据。留任奖金暗示可能存在人才流失风险。

- 支持 [ev_ef1bd35dbdd65844](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): our management concluded that our internal control over financial reporting was effective as of December 31, 2025.
- 支持 [ev_ef1bd35dbdd65844](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): the Compensation Committee (the Compensation Committee) of our Board of Directors of (the Board) approved the payment of one-time special cash retention bonuses for 2026 to certain of our executive officers, namely Renee Gaeta, John L. Brottem and Marc Nash.
- 支持 [ev_ef1bd35dbdd65844](https://www.sec.gov/Archives/edgar/data/1484612/000119312526051278/om-20251231.htm) (primary-document): The retention bonuses are intended to support retention priorities and leadership continuity in key business functions of the Company.
- 缺口：CEO/CFO的任期和背景信息
- 缺口：董事会独立性和构成
- 缺口：近期高管离职或继任情况
- 缺口：留任奖金的具体金额和条件
- 证伪条件：关键高管在留任奖金到期前离职
- 证伪条件：发现未披露的治理问题或调查
- 证伪条件：审计意见从无保留变为保留

## OMDA · complete

审查记录：`state/serenity-reviews/OMDA-claudecli-6b18d0d156a0f7edb44e.json`

### supply_chain_map: partial

证据仅显示Omada是数字健康平台公司，有库存(设备)和商业协议合作伙伴(包括Cigna Ventures关联方)，但缺乏对上游技术输入、数据基础设施依赖和下游用户具体流向的完整供应链映射。

- 支持 [ev_98b23fa9ab73be61](https://www.sec.gov/Archives/edgar/data/1611115/000162828026054840/omda-20260630.htm) (primary-document): Accounts receivable, net (1) 56,573 34,585 Inventory 4,119 4,486 Deferred commissions, current 3,959 3,539
- 支持 [ev_c26173b73cef863b](https://www.sec.gov/Archives/edgar/data/1611115/000162828026054840/omda-20260630.htm) (primary-document): omda:CommercialAgreementsMember omda:CignaVenturesLLCMember us-gaap:RelatedPartyMember 2026-06-30
- 缺口：上游技术供应商和云基础设施依赖关系
- 缺口：下游最终用户(雇主、健康计划)的具体名称和关系
- 缺口：数据来源和临床内容供应链
- 证伪条件：发现Omada严重依赖单一云供应商且无迁移能力
- 证伪条件：关键临床内容或设备供应商被竞争对手收购

### chokepoint_evidence: unknown

Omada Health是数字健康慢病管理平台，不存在物理供应集中或替代壁垒的证据。数字健康领域竞争者众多(Livongo/Teladoc、Virta等)，不符合Serenity方法论要求的瓶颈节点特征。

- 反证 [ev_55b6824c901ac370](https://www.sec.gov/Archives/edgar/data/1611115/000162828026054840/omda-20260630.htm) (primary-document): we operate in a very competitive and rapidly changing environment
- 缺口：供应集中度数据(如全球仅少数供应商)
- 缺口：替代品转换成本或多年替代周期的证据
- 缺口：任何表明Omada控制关键瓶颈节点的文件
- 缺口：反证只是通用风险条款或记录字段，不是针对公司的直接反证
- 证伪条件：发现Omada拥有不可替代的专有临床数据集或FDA独占审批
- 证伪条件：健康计划合同中存在多年排他锁定条款

### customer_dependency: partial

SEC XBRL标签明确显示PartnerA和PartnerB存在客户集中风险(收入和应收账款)，Cigna Ventures为关联方有商业协议。但合作伙伴真实身份未披露(匿名为PartnerA/B)，且缺乏具体收入占比数值。

- 支持 [ev_bc81f3cba8d8811a](https://www.sec.gov/Archives/edgar/data/1611115/000162828026071654/omda-20260930.htm) (primary-document): us-gaap:CustomerConcentrationRiskMember omda:PartnerAMember us-gaap:SalesRevenueNetMember 2026-07-01 2026-09-
- 支持 [ev_579c1144edab465b](https://www.sec.gov/Archives/edgar/data/1611115/000162828026071654/omda-20260930.htm) (primary-document): us-gaap:CustomerConcentrationRiskMember omda:PartnerBMember us-gaap:SalesRevenueNetMember 2026-07-01 2026-09-30
- 支持 [ev_447047af5b20c2d9](https://www.sec.gov/Archives/edgar/data/1611115/000162828026071654/omda-20260930.htm) (primary-document): omda:CommercialAgreementsMember omda:CignaVenturesLLCMember us-gaap:RelatedPartyMember 2026-09-30
- 缺口：PartnerA和PartnerB的真实身份(雇主还是健康计划)
- 缺口：各主要客户的收入占比百分数
- 缺口：合同期限和续约条款细节
- 证伪条件：主要合作伙伴未续约或转投竞争平台
- 证伪条件：客户集中度持续上升至单一客户超50%收入

### pure_play: partial

XBRL标签显示omda:ReportableSegmentMember为单一可报告分部，且10-Q描述围绕Omada Health平台的单一业务模型。但缺乏各产品线(糖尿病预防、高血压、肌肉骨骼等)的收入分拆，无法精确评估AI/数据分析在总收入中的占比。

- 支持 [ev_c26173b73cef863b](https://www.sec.gov/Archives/edgar/data/1611115/000162828026054840/omda-20260630.htm) (primary-document): omda:ReportableSegmentMember 2026-04-01 2026-06-30 0001611115 omda:ReportableSegmentMember 2025-04-01 2025-06-30
- 支持 [ev_5da13c33d412f764](https://www.sec.gov/Archives/edgar/data/1611115/000162828026071654/omda-20260930.htm) (primary-document): any statements relating to our financial and business performance, including with respect to the Omada Health platform
- 缺口：按产品线或疾病领域的收入分拆
- 缺口：AI/数据分析功能对收入的具体贡献比例
- 缺口：与纯AI医疗主题的关联度量化
- 证伪条件：发现大部分收入来自非AI的传统健康教练服务
- 证伪条件：公司收购非相关业务导致主题纯度下降

### multi_node_control: unknown

Omada是数字健康软件平台公司，不存在控制多个相连供应链节点的证据。在Serenity框架下，软件平台本身不构成上下游多节点垂直整合。

- 缺口：上下游垂直整合的证据(如同时拥有硬件设备+软件+数据)
- 缺口：跨供应链节点的独占性控制证据
- 缺口：不通过需要直接反证，缺少证据不能等同失败
- 证伪条件：Omada收购上游传感器/设备公司或下游支付平台形成垂直整合

### earnings_validation: pass

Q3 2026实际财务数据强劲：收入9130万美元同比+34.2%，净利润655万美元(已盈利)，经营性现金流YTD 731万美元为正，现金243百万美元。增长与盈利能力同时验证。

- 支持 [ev_929b534fb59b8cc4](https://data.sec.gov/api/xbrl/companyfacts/CIK0001611115.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 91,306,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_929b534fb59b8cc4](https://data.sec.gov/api/xbrl/companyfacts/CIK0001611115.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 68,030,000, a change of +34.2%
- 支持 [ev_929b534fb59b8cc4](https://data.sec.gov/api/xbrl/companyfacts/CIK0001611115.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 6,551,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_929b534fb59b8cc4](https://data.sec.gov/api/xbrl/companyfacts/CIK0001611115.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): 7,313,000 for 2026-01-01 to 2026-09-30
- 支持 [ev_929b534fb59b8cc4](https://data.sec.gov/api/xbrl/companyfacts/CIK0001611115.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 243,151,000 for as of 2026-09-30
- 证伪条件：收入增速连续两个季度放缓至20%以下
- 证伪条件：净利润转为持续亏损且现金流恶化

### counter_thesis: partial

已识别关键风险：客户高度集中(PartnerA/B)、竞争激烈、监管复杂。但缺乏具体替代品分析、估值压力测试和具体竞争对手对比数据。公司无融资风险(现金充足且已盈利)。

- 支持 [ev_55b6824c901ac370](https://www.sec.gov/Archives/edgar/data/1611115/000162828026054840/omda-20260630.htm) (primary-document): we operate in a very competitive and rapidly changing environment
- 支持 [ev_55b6824c901ac370](https://www.sec.gov/Archives/edgar/data/1611115/000162828026054840/omda-20260630.htm) (primary-document): our ability to comply with the extensive, complex, and evolving legal and regulatory requirements applicable to our business
- 支持 [ev_bc81f3cba8d8811a](https://www.sec.gov/Archives/edgar/data/1611115/000162828026071654/omda-20260930.htm) (primary-document): us-gaap:CustomerConcentrationRiskMember omda:PartnerAMember us-gaap:AccountsReceivableMember 2026-01-01 2026-09-30
- 反证 [ev_929b534fb59b8cc4](https://data.sec.gov/api/xbrl/companyfacts/CIK0001611115.json) (sec-companyfacts): R&D expense (ResearchAndDevelopmentExpense): 15,271,000 for 2026-07-01 to 2026-09-30
- 缺口：具体竞争对手(Livongo/Teladoc、Virta Health等)的市场份额和增速对比
- 缺口：客户流失率和NRR(净收入留存率)数据
- 缺口：估值倍数与同行对比分析
- 缺口：CMS政策变化对数字健康报销的影响评估
- 证伪条件：CMS削减糖尿病预防项目(DPP)报销费率
- 证伪条件：主要健康计划客户(PartnerA或B)不续约
- 证伪条件：大型竞争对手(如Teladoc)以低价抢占市场
- 证伪条件：AI监管收紧导致平台功能受限
- 证伪条件：IPO锁定期到期后内部人大量抛售

### management_governance: unknown

证据中未包含管理层背景、董事会构成或治理结构的具体信息。仅知公司为新兴成长型公司(emerging growth company)、2025年6月IPO，且Cigna Ventures为关联方(暗示可能有董事会席位)。无法评估领导层连续性或治理质量。

- 支持 [ev_59e79975ee3aac7f](https://www.sec.gov/Archives/edgar/data/1611115/000162828026071654/omda-20260930.htm) (primary-document): Emerging growth company x If an emerging growth company, indicate by check mark if the registrant has elected not to use
- 缺口：CEO/CFO背景和任期
- 缺口：董事会独立性和构成
- 缺口：Cigna Ventures关联方对治理的影响
- 缺口：高管薪酬和股权激励详情
- 缺口：任何未决调查或诉讼信息
- 证伪条件：发现关键高管近期离职
- 证伪条件：Cigna作为关联方对董事会有过度控制权
- 证伪条件：存在未披露的监管调查

## PALI · complete

审查记录：`state/serenity-reviews/PALI-claudecli-57b6ed67e87bd6b646d4.json`

### supply_chain_map: partial

上游：公司披露有两家合格的API供应商和第三方合同生产商，但未具名。产品：PALI-2108，口服PDE4抑制剂前药，用于炎症性肠病（UC和CD）。下游：中重度UC和CD患者。供应链基本轮廓可见，但缺乏具体供应商名称和制造商身份。

- 支持 [ev_72c4c27a37ecdb75](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000004/pali-20251231.htm) (primary-document): We depend on two qualified suppliers for the active pharmaceutical ingredient used in the clinical trials of PALI-2108
- 支持 [ev_72c4c27a37ecdb75](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000004/pali-20251231.htm) (primary-document): We do not have, and we do not intend to establish in the foreseeable future, internal manufacturing capabilities
- 支持 [ev_f9dc534c5d4a6272](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000025/pali-ex99_1.htm) (primary-document): PALI-2108 is an investigational, once-daily oral PDE4 inhibitor prodrug designed for localized bioactivation in the terminal ileum and colon
- 支持 [ev_e4f6fb38ab60ec34](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000025/pali-ex99_1.htm) (sec-8k): ASCENTRA-UC is expected to enroll approximately 204 patients with moderately to severely active UC
- 缺口：API供应商具体名称
- 缺口：合同生产商（CMO）具体身份
- 缺口：赋形剂和包装供应商信息
- 缺口：供应商地理分布
- 证伪条件：API供应商被发现已终止合作或不合格
- 证伪条件：CMO产能不足或监管合规问题导致临床供应中断

### chokepoint_evidence: unknown

PALI是标准的外包模式临床阶段药企，无证据显示其在供应链中具有任何供给集中度或替代壁垒。PDE4抑制剂是已知药物类别，不构成卡脖子节点。两家API供应商意味着有替代来源。

- 缺口：PALI-2108 API的全球供应集中度数据
- 缺口：与其他PDE4抑制剂（如apremilast）的差异化壁垒证据
- 缺口：任何专利或配方独占性的具体证据
- 证伪条件：发现PALI-2108的API可从多家供应商获得且无替代壁垒
- 证伪条件：竞争性PDE4抑制剂在IBD适应症取得成功

### customer_dependency: unknown

公司处于临床前商业化阶段，无任何商业客户或已披露的采用情况。与Giiant Pharma的合作是许可引进协议，Giiant是许可方而非客户。唯一的收入为2026年前九个月$500K许可收入，无客户详情。

- 支持 [ev_2e866523e57d884e](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000004/pali-20251231.htm) (primary-document): As of December 31, 2025 and 2024 , the Company does not have any collaborative arrangements with counterparties that are also considered customers
- 缺口：任何商业合作伙伴或潜在客户（如大型药企许可合作）的披露
- 缺口：市场准入或商业化合作协议
- 缺口：支付方或保险覆盖方面的信息
- 证伪条件：潜在合作伙伴拒绝PALI-2108的许可权
- 证伪条件：IBD治疗市场被现有疗法主导使商业前景有限

### pure_play: partial

公司为单一报告分部，唯一在研资产为PALI-2108（IBD适应症）。遗留资产LB1148已于2023年停止开发。公司高度聚焦于单一药物的开发，属于纯粹的IBD管线公司。但尚无收入，无法评估主题收入占比。

- 支持 [ev_02868a3b029c8fa4](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000004/pali-20251231.htm) (primary-document): PALI-2108 program expenses are those expenses directly related with the development of the Company's only asset currently under development, PALI-2108
- 支持 [ev_02868a3b029c8fa4](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000004/pali-20251231.htm) (primary-document): Legacy program expenses are those expenses directly related to its legacy assets, primarily LB1148, which the Company ceased developing in August of 2023
- 支持 [ev_e4f6fb38ab60ec34](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000025/pali-ex99_1.htm) (sec-8k): a clinical-stage biopharmaceutical company developing oral therapies for immune-mediated and fibrotic diseases
- 缺口：收入分部数据（尚为临床前商业化阶段）
- 缺口：与AI医疗主题的关联性证据
- 证伪条件：公司进入与IBD无关的治疗领域导致焦点分散
- 证伪条件：PALI-2108失败后无后续管线

### multi_node_control: unknown

公司完全外包API采购和药品制造，不拥有任何生产设施。Giiant许可协议提供了上游资产，但公司不控制供应链的多个节点。无垂直整合证据。

- 反证 [ev_72c4c27a37ecdb75](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000004/pali-20251231.htm) (primary-document): We do not have, and we do not intend to establish in the foreseeable future, internal manufacturing capabilities
- 缺口：任何自有制造或供应能力
- 缺口：控制供应链多节点的证据
- 证伪条件：公司建立内部制造能力或收购上游供应商

### earnings_validation: unknown

准备阶段公司，无收入属正常。截至2026年9月30日现金$113.6M，9个月运营现金流出$23.25M（约每月$2.58M），估算跑道约44个月。公司明确表示现金足以支持Phase 2关键里程碑，包括ASCENTRA-UC（2027年Q4结果）和ASCENTRA-CD（2028年Q1结果）。财务状况支持下一阶段开发。

- 支持 [ev_f9dc534c5d4a6272](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000025/pali-ex99_1.htm) (primary-document): As of September 30, 2026, the Company had $113.6 million in cash and cash equivalents, which the Company believes will fund operations through key Phase 2 clinical milestones
- 支持 [ev_551ace7111a3227c](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000025/pali-ex99_1.htm) (primary-document): Cash and cash equivalents $ 113,613 $ 133,385
- 支持 [ev_93e66e291d2dd82a](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000025/pali-ex99_1.htm) (primary-document): Net cash used in operating activities (23,252 ) (7,703 )
- 缺口：Phase 3试验预算和资金需求的详细预估
- 缺口：引用不存在或原文无法匹配
- 证伪条件：烧钱速率急剧上升导致跑道缩短至12个月以下
- 证伪条件：Phase 2规模扩大超预算需要额外融资

### counter_thesis: partial

已识别的反面论点：(1)单一资产风险——遗留项目LB1148已终止，若PALI-2108失败则公司无后备；(2)PDE4抑制剂是已有药物类别，面临竞争；(3)内部控制存在重大缺陷（自2021年起未修复）；(4)股权稀释——9个月内流通股从159M增至174M。(5)跑道充裕（44个月），融资风险低，无需将股权稀释列为首要反面路径。缺少具体竞争对手数据和IBD市场格局分析。

- 支持 [ev_77273a5a7f6045b5](https://clinicaltrials.gov/study/NCT05470387) (clinicaltrials-gov): A Study to Evaluate LB1148 for Return of Bowel Function in Subjects Undergoing Bowel Resection. Highest listed phase: Phase 3. Overall status: TERMINATED
- 支持 [ev_b58b92c1c76f732f](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000004/pali-20251231.htm) (primary-document): we identified a material weakness in our internal controls over financial reporting due to a lack of controls in the financial closing and reporting process
- 支持 [ev_551ace7111a3227c](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000025/pali-ex99_1.htm) (primary-document): 174,442,971 and 159,444,017 shares issued and outstanding at September 30, 2026 and December 31, 2025, respectively
- 支持 [ev_380e74526ae438c3](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000025/pali-ex99_1.htm) (primary-document): the risk that prior results, such as signals of safety, clinical response and efficacy, dosing or durability of effect, observed from preclinical or clinical trials with a limited number of patients, will not be replicated
- 缺口：IBD治疗市场竞争格局（已上市PDE4抑制剂、JAK抑制剂、生物制剂）
- 缺口：具体竞争药物的临床数据对比
- 缺口：估值分析（$169M市值对应临床阶段资产是否合理）
- 证伪条件：ASCENTRA-UC Phase 2b未达主要终点
- 证伪条件：ASCENTRA-CD Phase 2a显示安全性问题
- 证伪条件：竞争性PDE4抑制剂在IBD适应症率先获批
- 证伪条件：FDA要求额外临床试验延长开发时间线
- 证伪条件：现金消耗超预期需在不利条件下融资

### management_governance: partial

CEO JD Finley和CMO Mitch Jones（M.D., Ph.D.）有明确披露。但存在严重治理问题：(1)自2021年Q2起存在财务报告内部控制重大缺陷，截至2025年底仍未完全修复；(2)首席执行官同时兼任首席财务官（principal executive officer同时为principal financial officer），职责分离不足。在重大缺陷未修复前无法给予pass。

- 支持 [ev_e4f6fb38ab60ec34](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000025/pali-ex99_1.htm) (sec-8k): said JD Finley, Chief Executive Officer of Palisade Bio
- 支持 [ev_17ec0dde975789d9](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000025/pali-ex99_1.htm) (primary-document): said Mitch Jones, M.D., Ph.D., President and Chief Medical Officer of Palisade Bio
- 反证 [ev_b58b92c1c76f732f](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000004/pali-20251231.htm) (primary-document): our principal executive officer, who is also our principal financial officer, to provide reasonable assurance regarding the reliability of financial reporting
- 反证 [ev_b58b92c1c76f732f](https://www.sec.gov/Archives/edgar/data/1357459/000135745926000004/pali-20251231.htm) (primary-document): we identified a material weakness in our internal controls over financial reporting due to a lack of controls in the financial closing and reporting process, including a lack of segregation of duties
- 缺口：董事会成员完整名单及独立性信息
- 缺口：重大缺陷修复计划的最新进展
- 缺口：是否已聘请独立CFO
- 证伪条件：内部控制重大缺陷导致财务重述
- 证伪条件：SEC或Nasdaq对公司发起调查或处罚
- 证伪条件：关键管理层（CEO或CMO）离职

## PHG · complete

审查记录：`state/serenity-reviews/PHG-claudecli-3a0d5e6425f835bb5139.json`

### supply_chain_map: partial

FDA记录证明飞利浦生产AI超声设备（下游：医院/诊所），XBRL显示多个业务分部（诊断治疗、连接护理、影像引导治疗等），但数据包中无任何上游供应商、关键原材料或具体客户关系的披露。供应链仅能推断产品端，上游和下游均缺乏具体证据。

- 支持 [ev_68747ca1c4ee58b4](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K260667) (fda-ai-device-list): Manufacturer: Philips Ultrasound, LLC. Device: Alturion Series Diagnostic Ultrasound System
- 支持 [ev_f835dba5eb61fe1a](https://www.sec.gov/Archives/edgar/data/313216/000162828026009470/phg-20251231.htm) (primary-document): phg:DiagnosisTreatmentMember ifrs-full:OperatingSegmentsMember 2025-01-01 2025-12-31
- 缺口：上游关键零部件/原材料供应商名称及集中度
- 缺口：下游客户（医院系统、经销商）的具体名称与依赖关系
- 缺口：各供应链节点的地理分布与替代周期
- 证伪条件：若20-F全文披露关键供应商集中度低于预期，则供应链瓶颈论点不成立

### chokepoint_evidence: unknown

数据包中无任何证据表明飞利浦在AI医疗设备供应链中占据不可替代的瓶颈位置。FDA设备审批仅证明产品获批，不能证明供应集中度或替代壁垒。医疗影像设备市场有GE HealthCare、西门子医疗等多家竞争者，飞利浦并非垄断或寡头供应方。

- 缺口：飞利浦在特定AI医疗细分市场的市场份额数据
- 缺口：竞争对手替代产品的可获得性与切换成本分析
- 缺口：任何表明供应集中度>50%的具体证据
- 证伪条件：若飞利浦在某一关键AI诊断子领域市占率超过50%且替代周期超过2年，则可能构成瓶颈

### customer_dependency: unknown

数据包中无任何客户名称、采购协议、设计锁定或客户依赖度的披露。FDA记录仅证明设备获得监管许可，不能证明实际客户采购或部署情况。XBRL标签数据中未出现客户相关的具体信息。

- 缺口：主要医院系统或医疗集团的采购/部署披露
- 缺口：客户集中度数据（前十大客户占收入比例）
- 缺口：AI设备实际装机量或订单积压数据
- 证伪条件：若20-F全文披露单一客户占比超过10%，则存在客户集中风险

### pure_play: unknown

XBRL标签明确显示飞利浦为多元化集团，拥有至少六个业务分部：诊断治疗、连接护理、监测、影像引导治疗、精准诊断、睡眠与呼吸护理、个人健康、企业信息化。AI医疗设备仅为其众多业务之一，远非纯粹的AI医疗投资标的。按Serenity方法论，多元化本身不是否决项，但AI主题收入敞口被严重稀释。

- 支持 [ev_17441b39499c8454](https://www.sec.gov/Archives/edgar/data/313216/000162828026009470/phg-20251231.htm) (primary-document): phg:MonitoringMember 2025-12-31 0000313216 phg:MonitoringMember 2024-12-31 0000313216 phg:ImageGuidedTherapyMember
- 支持 [ev_17441b39499c8454](https://www.sec.gov/Archives/edgar/data/313216/000162828026009470/phg-20251231.htm) (primary-document): phg:SleepRespiratoryCareMember 2025-12-31 0000313216 phg:SleepRespiratoryCareMember 2024-12-31
- 支持 [ev_17441b39499c8454](https://www.sec.gov/Archives/edgar/data/313216/000162828026009470/phg-20251231.htm) (primary-document): phg:PersonalHealthMember 2025-12-31 0000313216 phg:PersonalHealthMember 2024-12-31
- 支持 [ev_17441b39499c8454](https://www.sec.gov/Archives/edgar/data/313216/000162828026009470/phg-20251231.htm) (primary-document): phg:EnterpriseInformaticsMember 2025-12-31 0000313216 phg:EnterpriseInformaticsMember 2024-12-31
- 缺口：各业务分部的收入占比，以量化AI相关收入敞口
- 缺口：AI功能在各分部产品中的渗透率
- 缺口：不通过需要直接反证，缺少证据不能等同失败
- 证伪条件：若AI增强产品线收入占总收入超过60%，则纯粹度判断需修正

### multi_node_control: unknown

数据包中无证据表明飞利浦控制AI医疗供应链中两个或以上相连节点。虽然飞利浦业务覆盖多个医疗领域，但"多产品线"不等于"控制相连供应链节点"。需要证明飞利浦同时控制上游关键技术/部件与下游系统集成，且这些节点具有替代壁垒。

- 缺口：飞利浦自研AI芯片或核心传感器的证据
- 缺口：垂直整合程度（如从算法开发到设备制造到云平台的全链条控制）
- 缺口：各节点的市场集中度数据
- 证伪条件：若飞利浦仅为系统集成商而核心AI芯片/传感器均外购，则不构成多节点控制

### earnings_validation: unknown

XBRL标签数据仅包含会计科目名称和日期标记，未包含可读的实际财务数字（收入、利润、增长率等）。数据包中无法提取任何具体的营收、利润或AI业务贡献的财务结果来验证投资论点。

- 缺口：2025财年各分部收入与利润的具体数字
- 缺口：AI相关产品线的收入增长率
- 缺口：毛利率趋势及AI设备对利润率的贡献
- 缺口：订单积压及管理层对AI业务的前瞻指引
- 证伪条件：若AI设备业务收入增速低于整体业务增速，则AI主题投资论点被削弱

### counter_thesis: partial

可基于现有证据构建部分反论点：飞利浦是高度多元化集团（XBRL证实六个以上业务分部），AI医疗仅为其业务一小部分；FDA审批49个AI设备虽多但不证明商业成功或护城河；$29.7B市值远超Serenity偏好的$400M-$5B甜蜜区。但缺乏竞争格局、估值和地缘政治维度的具体证据来全面压力测试。

- 支持 [ev_68747ca1c4ee58b4](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K260667) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 支持 [ev_17441b39499c8454](https://www.sec.gov/Archives/edgar/data/313216/000162828026009470/phg-20251231.htm) (primary-document): phg:PrecisionDiagnosisMember 2025-12-31 0000313216 phg:PrecisionDiagnosisMember 2024-12-31
- 反证 [ev_80f733085dc7bda8](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K260123) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：GE HealthCare和西门子医疗在AI医疗设备领域的对比数据
- 缺口：飞利浦睡眠呼吸设备召回事件（DreamStation）的持续影响评估
- 缺口：估值倍数与同业对比
- 缺口：欧洲医疗器械法规（MDR）对AI设备审批的潜在影响
- 证伪条件：GE HealthCare或西门子在AI医疗影像市场份额超过飞利浦
- 证伪条件：DreamStation召回诉讼的持续财务拖累导致AI投资不足
- 证伪条件：欧盟MDR合规成本挤压AI研发预算
- 证伪条件：市值$29.7B远超chokepoint方法论偏好范围，机构已充分定价

### management_governance: unknown

数据包中无任何关于管理层构成、CEO任期、董事会独立性、高管变动、薪酬结构或正在进行的调查/诉讼的信息。XBRL标签和FDA审批记录均不涉及治理议题。需要20-F全文中的治理章节才能评估。

- 缺口：CEO及关键高管的任职信息与连续性
- 缺口：董事会独立性与组成
- 缺口：DreamStation召回相关的法律诉讼进展
- 缺口：高管薪酬与绩效指标挂钩情况
- 证伪条件：若存在未披露的监管调查或高管层大规模变动，则治理评估需降级

## PRCT · complete

审查记录：`state/serenity-reviews/PRCT-claudecli-a8b64cfa8a25a1401f5a.json`

### supply_chain_map: partial

证据显示PRCT的产品线（HYDROS机器人系统、手柄耗材、服务）和下游地理分布（美国/国际），但缺乏上游供应商、关键零部件来源的具体披露。仅能从SEC文件推断产品→医院的下游关系，上游输入完全缺失。

- 支持 [ev_c6adc9a5e1203e3f](https://www.sec.gov/Archives/edgar/data/1588978/000158897826000039/prct-20260930.htm) (primary-document): country:US prct:SystemSalesAndLeasesMember 2026-07-01 2026-09-30
- 支持 [ev_c6adc9a5e1203e3f](https://www.sec.gov/Archives/edgar/data/1588978/000158897826000039/prct-20260930.htm) (primary-document): country:US prct:HandPiecesAndOtherConsumablesMember 2026-07-01 2026-09-30
- 支持 [ev_c6adc9a5e1203e3f](https://www.sec.gov/Archives/edgar/data/1588978/000158897826000039/prct-20260930.htm) (primary-document): country:US prct:ServiceRevenueMember 2026-07-01 2026-09-30
- 支持 [ev_22e9714eed59588d](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K251082) (fda-ai-device-list): Device: HYDROS Robotic System (HY1000); HYDROS Handpiece (HH1000); HYDROS TRUS Probe (HU1000)
- 缺口：上游关键零部件供应商名称及集中度
- 缺口：制造环节外包vs自产的披露
- 缺口：关键原材料或芯片来源信息
- 证伪条件：发现PRCT关键部件（如超声探头、机器人执行器）依赖单一供应商且有替代方案

### chokepoint_evidence: unknown

证据中没有任何关于供应集中度或替代壁垒的具体数据。PRCT是手术机器人公司，市场上存在Intuitive Surgical等强劲竞争对手。FDA AI设备清关仅证明产品获批，不构成供应链瓶颈证据。仅有AI相关性不足以通过此门。

- 缺口：PRCT在手术机器人/水刀技术领域的全球市场份额数据
- 缺口：竞争对手替代产品的技术壁垒或转换成本分析
- 缺口：任何表明供应端集中度的定量证据
- 证伪条件：发现水刀前列腺手术技术有多家竞争者提供可直接替代的产品
- 证伪条件：发现医院可以低成本从HYDROS切换到其他机器人平台

### customer_dependency: unknown

证据仅披露了美国和国际两个地理维度的收入分布，没有任何具名客户、医院系统、采购合同或设计锁定的披露。XBRL中存在地理集中度风险标签，但无具体客户层面的依赖数据。

- 支持 [ev_2ba63343a3f09050](https://www.sec.gov/Archives/edgar/data/1588978/000158897826000039/prct-20260930.htm) (primary-document): us-gaap:GeographicConcentrationRiskMember us-gaap:SalesRevenueNetMember country:US 2026-07-01 2026-09-30
- 缺口：前十大客户或超过10%收入的单一客户披露
- 缺口：具名医院系统或医疗集团的采购/部署信息
- 缺口：装机量或活跃使用机构数量数据
- 证伪条件：发现收入高度依赖少数几家医院集团，存在客户集中风险

### pure_play: partial

PRCT所有收入线（系统销售/租赁、手柄耗材、服务）均围绕HYDROS机器人手术平台，属于纯粹的手术机器人公司。但在AI医疗主题下，其AI成分仅体现在FDA AI设备清关记录，实际AI对收入的贡献比例不明。作为手术机器人纯粹标的可pass，但作为AI医疗纯粹标的证据不足。

- 支持 [ev_22e9714eed59588d](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K251082) (fda-ai-device-list): FDA AI-enabled medical-device authorization record. Manufacturer: Procept Biorobotics
- 支持 [ev_c85edb17fa532e6a](https://www.sec.gov/Archives/edgar/data/1588978/000158897826000030/prct-20260630.htm) (primary-document): Cash and cash equivalents $ 227,914 $ 286,503 Accounts receivable, net 107,606 83,533 Inventory 77,061 70,694
- 缺口：AI功能对HYDROS产品差异化定价的具体贡献
- 缺口：AI相关收入占总收入的比例
- 缺口：与非AI手术替代方案（如传统TURP）的竞争定位分析
- 证伪条件：发现HYDROS的核心价值在于水刀技术而非AI，AI仅为辅助功能

### multi_node_control: partial

PRCT运营"刀片+刀架"模式：同时销售机器人系统（资本设备）、一次性手柄耗材和售后服务。这构成设备→耗材→服务的纵向整合，但本质是单一产品平台的商业模式延伸，不等于控制供应链上多个独立节点。缺乏上游材料或核心技术节点的控制证据。

- 支持 [ev_8eb90ccfea541151](https://www.sec.gov/Archives/edgar/data/1588978/000158897826000030/prct-20260630.htm) (primary-document): country:US prct:SystemSalesAndLeasesMember 2026-01-01 2026-06-30
- 支持 [ev_8eb90ccfea541151](https://www.sec.gov/Archives/edgar/data/1588978/000158897826000030/prct-20260630.htm) (primary-document): country:US prct:HandPiecesAndOtherConsumablesMember 2026-01-01 2026-06-30
- 缺口：上游关键技术（如超声、机器人控制）的自研vs外购比例
- 缺口：任何垂直整合至供应链上游节点的证据
- 缺口：专利或技术壁垒构成的多节点控制文件
- 证伪条件：发现PRCT的核心硬件模块全部外购，仅做系统集成

### earnings_validation: partial

有明确的实际财务数据：Q3 2026收入$98.3M（同比+18%），但净亏损$26.5M，YTD经营现金流-$66.4M。公司现金$218M对比年化烧钱约$88M，跑道约2.5年。收入在增长但尚未盈利，无法完全验证投资论点。

- 支持 [ev_ae5937dc1f4c4422](https://data.sec.gov/api/xbrl/companyfacts/CIK0001588978.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 98,291,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_ae5937dc1f4c4422](https://data.sec.gov/api/xbrl/companyfacts/CIK0001588978.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 83,327,000, a change of +18.0%
- 支持 [ev_ae5937dc1f4c4422](https://data.sec.gov/api/xbrl/companyfacts/CIK0001588978.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -26,516,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_ae5937dc1f4c4422](https://data.sec.gov/api/xbrl/companyfacts/CIK0001588978.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 218,369,000 for as of 2026-09-30
- 支持 [ev_ae5937dc1f4c4422](https://data.sec.gov/api/xbrl/companyfacts/CIK0001588978.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -66,363,000 for 2026-01-01 to 2026-09-30
- 反证 [ev_fb2ecf4905f85fd7](https://news.google.com/rss/articles/CBMi4AFBVV95cUxQbEd2UWdSQ29xSlFUNVpMNmdXVHBUNEFzTk5mcV9jaDI3ZkV3RVlQNnhuX2MwVmI3SnZQeDg3TjliQ05IcTdFM3FUR3luRkV4MW5WTV9WY254VVJTZ1hUeW5ncENtSGtpNzdrMi0zTkJXdFZ2Vy1BLWNqbjlDaVlwTEhyRmtYZ2YySmVjVmJqSExaS0pNTmppbnIxampnVXl3Zks3UUVYT3ltd3loNDBBbndfaUUxTXRqbUdXcTZBSVRld0EzdUNtY182V2s0S2tJVWlQS3RJZWM5V2hyOFRCSA?oc=5) (news-feed): PROCEPT BioRobotics Corporation Reports Q3 Revenue $98.3M, vs. FactSet Est of $100.5M
- 缺口：毛利率趋势及盈利路径时间表
- 缺口：装机量增长率与耗材复购率数据
- 缺口：管理层对盈亏平衡时间点的指引
- 证伪条件：收入增速持续放缓至个位数且亏损扩大
- 证伪条件：现金跑道缩短至12个月以下且无融资安排

### counter_thesis: partial

可识别的风险包括：1）Q3收入低于分析师预期（$98.3M vs $100.5M预期）；2）持续亏损且现金消耗较快（YTD -$66M）；3）$51.7M长期债务；4）竞争激烈且快速变化的环境。但缺乏对替代技术、竞争对手定价压力、监管风险的系统性分析。

- 支持 [ev_fb2ecf4905f85fd7](https://news.google.com/rss/articles/CBMi4AFBVV95cUxQbEd2UWdSQ29xSlFUNVpMNmdXVHBUNEFzTk5mcV9jaDI3ZkV3RVlQNnhuX2MwVmI3SnZQeDg3TjliQ05IcTdFM3FUR3luRkV4MW5WTV9WY254VVJTZ1hUeW5ncENtSGtpNzdrMi0zTkJXdFZ2Vy1BLWNqbjlDaVlwTEhyRmtYZ2YySmVjVmJqSExaS0pNTmppbnIxampnVXl3Zks3UUVYT3ltd3loNDBBbndfaUUxTXRqbUdXcTZBSVRld0EzdUNtY182V2s0S2tJVWlQS3RJZWM5V2hyOFRCSA?oc=5) (news-feed): PROCEPT BioRobotics Corporation Reports Q3 Revenue $98.3M, vs. FactSet Est of $100.5M
- 支持 [ev_ae5937dc1f4c4422](https://data.sec.gov/api/xbrl/companyfacts/CIK0001588978.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -26,516,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_c85edb17fa532e6a](https://www.sec.gov/Archives/edgar/data/1588978/000158897826000030/prct-20260630.htm) (primary-document): Moreover, we operate in a very competitive and rapidly changing environment. New risks emer
- 支持 [ev_ae5937dc1f4c4422](https://data.sec.gov/api/xbrl/companyfacts/CIK0001588978.json) (sec-companyfacts): R&D expense (ResearchAndDevelopmentExpense): 20,011,000 for 2026-07-01 to 2026-09-30
- 反证 [ev_ae5937dc1f4c4422](https://data.sec.gov/api/xbrl/companyfacts/CIK0001588978.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 98,291,000 for 2026-07-01 to 2026-09-30
- 反证 [ev_ae5937dc1f4c4422](https://data.sec.gov/api/xbrl/companyfacts/CIK0001588978.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 218,369,000 for as of 2026-09-30
- 缺口：Intuitive Surgical等竞争对手在BPH领域的产品规划
- 缺口：Rezum等替代微创疗法的市场份额趋势
- 缺口：估值倍数与同类公司对比分析
- 缺口：地缘政治或供应链中断对制造的影响评估
- 证伪条件：竞争对手推出等效或更优的水刀/机器人BPH手术方案
- 证伪条件：关键临床数据显示HYDROS长期疗效不优于现有替代方案
- 证伪条件：医保报销政策变化导致医院采购意愿下降
- 证伪条件：收入增长持续低于预期导致现金跑道不足

### management_governance: partial

证据中仅出现首席法务官Alaleh Nouri签署8-K的信息，未发现CEO/CFO变动、调查或治理问题的披露。但也缺乏管理层稳定性、董事会构成、高管变动等正面证据。公司为大型加速申报人，合规义务较完整。

- 支持 [ev_0f72595861e0b1d1](https://www.sec.gov/Archives/edgar/data/1588978/000158897826000036/prct-20261104.htm) (primary-document): By: /s/ Alaleh Nouri Alaleh Nouri Chief Legal Officer and Secretary
- 支持 [ev_dadb12c0c7105b2f](https://www.sec.gov/Archives/edgar/data/1588978/000158897826000039/prct-20260930.htm) (primary-document): Large accelerated filer ☒ Accelerated filer ☐ Non-accelerated filer ☐ Smaller reporting company ☐ Emerging growth company ☐
- 缺口：CEO和CFO身份及任期信息
- 缺口：董事会构成及独立董事比例
- 缺口：高管近期变动或继任计划
- 缺口：内部人交易模式（Form 4数据）
- 证伪条件：发现关键高管近期离职或正在接受调查
- 证伪条件：发现重大内控缺陷或审计意见保留

## PRME · complete

审查记录：`state/serenity-reviews/PRME-claudecli-194836d0c6c5e20d4d31.json`

### supply_chain_map: unknown

上游可识别：Broad Institute的Prime Editing专利许可、第三方合同生产商（CDMO）、中国供应商提供部分原材料。产品为Prime Editing基因编辑疗法（PM359/PM577/PM647），使用LNP递送平台。下游为罕见病患者群体及BMS合作。但缺乏具体CDMO名称、原材料供应商和供应链集中度的量化信息。

- 支持 [ev_624e7a35e0895c0d](https://www.sec.gov/Archives/edgar/data/1894562/000162828026013569/prme-20251231.htm) (primary-document): if we are required to change third party-manufacturers for any reason, we will be required to verify that the new third party-manufacturer maintains facilities and procedures that comply with quality standards
- 支持 [ev_624e7a35e0895c0d](https://www.sec.gov/Archives/edgar/data/1894562/000162828026013569/prme-20251231.htm) (primary-document): the pharmaceutical industry generally, and in some instances we or our collaborators or other third parties on which we rely, depend on China-based suppliers or service providers for certain raw materials
- 支持 [ev_8aad3b4174a4765f](https://www.sec.gov/Archives/edgar/data/1894562/000162828026073372/q320268-kex991xpressrelease.htm) (sec-8k): we are now extending that experience in vivo , beginning with our liver directed programs. Furthermore, the FDA clearance of our IND for PM647 in Alpha-1 Antitrypsin Deficiency further underscores the versatility of our universal liver LNP platform
- 缺口：具体CDMO合作方名称及合同条款
- 缺口：LNP脂质纳米颗粒及关键原材料的供应商和供应集中度
- 缺口：制造成本结构和产能信息
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现关键原材料或CDMO存在单一来源依赖且无替代方案
- 证伪条件：中国供应商因地缘政治被切断且无法替代

### chokepoint_evidence: unknown

Prime Medicine持有Prime Editing专利组合（10项已授权美国专利），但证据明确指出专利强度存在不确定性，且方法专利无法阻止竞争者开发相同产品用于不同适应症。这是一家临床阶段药企，不具备Serenity方法论所定义的物理供应链瓶颈特征。无证据表明供应集中度或替代壁垒。

- 支持 [ev_0ad0a9c811a529ed](https://www.sec.gov/Archives/edgar/data/1894562/000162828026013569/prme-20251231.htm) (primary-document): We and our licensors have filed patent applications intended to specifically cover our Prime Editing technology and uses with respect to treatment of particular diseases and conditions
- 反证 [ev_0ad0a9c811a529ed](https://www.sec.gov/Archives/edgar/data/1894562/000162828026013569/prme-20251231.htm) (primary-document): Method-of-use patents do not prevent a competitor or other third party from developing or marketing an 70 identical product for an indication that is outside the scope of the patented method
- 缺口：Prime Editing相对于CRISPR/Cas9和碱基编辑的技术替代壁垒的量化证据
- 缺口：全球基因编辑技术供应集中度数据
- 缺口：竞争对手技术追赶所需时间的独立评估
- 证伪条件：其他基因编辑平台（如碱基编辑Beam、CRISPR）在相同适应症中展示优越临床数据
- 证伪条件：Broad Institute向竞争对手授权相同核心专利

### customer_dependency: unknown

BMS合作已确认并产生收入（Q3 2026合作收入421.3万美元），BMS是唯一披露的合作伙伴/客户。但终端产品尚无商业化客户，所有管线均处于临床阶段。PM359计划2027上半年提交BLA，PM577a和PM647预计2027年有初步临床数据。尚无已批准产品或商业销售。

- 支持 [ev_dc8f16897ff65d1a](https://www.sec.gov/Archives/edgar/data/1894562/000162828026073372/q320268-kex991xpressrelease.htm) (primary-document): Collaboration revenue — related party $ 4,213 $ 1,179
- 支持 [ev_8aad3b4174a4765f](https://www.sec.gov/Archives/edgar/data/1894562/000162828026073372/q320268-kex991xpressrelease.htm) (sec-8k): Planning for a BLA submission for PM359 in the first half of 2027
- 缺口：BMS合作协议的具体里程碑付款金额和触发条件
- 缺口：除BMS外的其他潜在商业合作伙伴
- 缺口：PM359获批后的商业化计划和目标市场规模
- 缺口：引用不存在或原文无法匹配
- 证伪条件：BMS终止合作协议
- 证伪条件：PM359 BLA被FDA拒绝
- 证伪条件：竞争疗法在CGD、Wilson病或AATD适应症中率先获批

### pure_play: unknown

Prime Medicine是100%纯正的Prime Editing基因编辑疗法公司，单一经营分部，所有收入来自基因编辑合作，所有研发支出集中于Prime Editing管线。无非核心业务分散主题敞口。

- 支持 [ev_cd3ccabbf748d42d](https://www.sec.gov/Archives/edgar/data/1894562/000162828026073372/q320268-kex991xpressrelease.htm) (primary-document): Prime Medicine is a leading biotechnology company dedicated to creating and delivering the next generation of gene editing therapies to patients. The Company is deploying its proprietary Prime Editing platform
- 缺口：引用不存在或原文无法匹配
- 证伪条件：公司进入与Prime Editing无关的业务领域
- 证伪条件：收购非基因编辑资产导致主题敞口稀释

### multi_node_control: unknown

Prime Medicine拥有Prime Editing平台技术和LNP肝脏递送平台，但这些是同一产品开发流程中的技术组件，并非Serenity方法论定义的供应链上下游多节点控制。公司不控制原材料供应或制造环节，依赖第三方CDMO。无证据表明公司控制两个或以上相连的供应链节点。

- 支持 [ev_8aad3b4174a4765f](https://www.sec.gov/Archives/edgar/data/1894562/000162828026073372/q320268-kex991xpressrelease.htm) (sec-8k): the FDA clearance of our IND for PM647 in Alpha-1 Antitrypsin Deficiency further underscores the versatility of our universal liver LNP platform
- 反证 [ev_624e7a35e0895c0d](https://www.sec.gov/Archives/edgar/data/1894562/000162828026013569/prme-20251231.htm) (primary-document): a third party-manufacturer may possess technology related to the manufacture of our product candidate that such third party-manufacturer owns independently. This would increase our reliance on such third party-manufacturer
- 缺口：自有生产设施或关键原材料控制的证据
- 缺口：垂直整合程度的说明
- 证伪条件：公司建立自有制造能力并控制关键原材料供应

### earnings_validation: unknown

临床阶段准备期公司，亏损为预期状态。Q3 2026净亏损3904.3万美元，截至9/30现金仅6115.7万美元（约4.6个月跑道），但2026年11月完成公开发行筹集1.437亿美元总额（净额约1.347亿美元），形式现金约2.095亿美元，跑道延长至2027年底。融资已完成，可支撑下一阶段里程碑（PM359 BLA提交、PM577a/PM647临床数据）。但该融资为稀释性股权发行，确认了融资风险标记。

- 支持 [ev_dc8f16897ff65d1a](https://www.sec.gov/Archives/edgar/data/1894562/000162828026073372/q320268-kex991xpressrelease.htm) (primary-document): Cash, cash equivalents, and investments $ 61,157 $ 177,680
- 支持 [ev_cd3ccabbf748d42d](https://www.sec.gov/Archives/edgar/data/1894562/000162828026073372/q320268-kex991xpressrelease.htm) (primary-document): Prime Medicine expects that its cash, cash equivalents and investments as of September 30, 2026, together with net proceeds from its follow-on public offering of $134.7 million in November 2026, will be sufficient to fund its operating expenses and capital expenditure requirements through 2027
- 支持 [ev_d2784aec1deb62d3](https://www.sec.gov/Archives/edgar/data/1894562/000162828026073372/q320268-kex991xpressrelease.htm) (primary-document): Net Loss: Net loss was $39.0 million for the three months ended September 30, 2026, as compared to $50.6 million for the three months ended September 30, 2025
- 缺口：2027年后的融资计划和预期现金需求
- 缺口：若PM359获批的商业化资金需求估算
- 缺口：引用不存在或原文无法匹配
- 证伪条件：烧钱速度大幅增加导致跑道不足以覆盖2027年里程碑
- 证伪条件：2027年后无法获得额外融资

### counter_thesis: unknown

已识别多个反面论点：（1）融资稀释——尽管11月发行已完成，跑道仅至2027年底，2028年后大概率需要再次融资；（2）IP不确定性——方法专利不阻止竞争者在不同适应症上开发相同产品；（3）Beam仲裁虽已解决，但暴露了IP边界争议风险；（4）依赖第三方制造和中国供应商。但缺乏来自竞争对手管线的具体临床数据比较，无法充分评估替代风险。financingRisk为true，已确认稀释性股权发行。

- 支持 [ev_0ad0a9c811a529ed](https://www.sec.gov/Archives/edgar/data/1894562/000162828026013569/prme-20251231.htm) (primary-document): Method-of-use patents do not prevent a competitor or other third party from developing or marketing an 70 identical product for an indication that is outside the scope of the patented method
- 支持 [ev_624e7a35e0895c0d](https://www.sec.gov/Archives/edgar/data/1894562/000162828026013569/prme-20251231.htm) (primary-document): regional or single-source dependencies may in some cases accentuate these risks. For example, the pharmaceutical industry generally, and in some instances we or our collaborators or other third parties on which we rely, depend on China-based suppliers
- 反证 [ev_0ad0a9c811a529ed](https://www.sec.gov/Archives/edgar/data/1894562/000162828026013569/prme-20251231.htm) (primary-document): The strength of patents in the biotechnology and pharmaceutical field involves complex legal and scientific questions and can be uncertain
- 缺口：竞争对手（Beam、Verve、Intellia等）在相同适应症的管线进展对比
- 缺口：Prime Editing相对碱基编辑和CRISPR的临床优劣比较数据
- 缺口：2028年及以后的融资需求估算和潜在稀释幅度
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：PM359 BLA被拒或需要额外临床试验
- 证伪条件：PM577a或PM647临床试验显示安全性问题或无效
- 证伪条件：竞争性基因编辑疗法在相同适应症率先获批
- 证伪条件：2027年后无法以合理条件获得融资
- 证伪条件：Broad Institute撤销或限制核心专利许可

### management_governance: unknown

治理结构完整：审计委员会（Michael Kelly主席，SEC认定的审计委员会财务专家）、薪酬委员会、提名与公司治理委员会均已设立，全部成员满足Nasdaq独立性要求。CEO Allan Reine, M.D.在位。已通过商业行为和道德准则。但缺乏关于管理层任期、关键人物流失风险、以及CEO/CSO任职时间的详细信息。

- 支持 [ev_80c774f218264046](https://www.sec.gov/Archives/edgar/data/1894562/000162828026013569/prme-20251231.htm) (primary-document): Our board of directors has determined that all of the members of our audit committee satisfy the relevant independence requirements for service on the audit committee set forth in the rules of the SEC and the Nasdaq listing rules
- 支持 [ev_5efbd3c3adb7af9e](https://www.sec.gov/Archives/edgar/data/1894562/000162828026013569/prme-20251231.htm) (primary-document): developing and recommending to our board of directors criteria for our board of directors and committee membership
- 支持 [ev_8aad3b4174a4765f](https://www.sec.gov/Archives/edgar/data/1894562/000162828026073372/q320268-kex991xpressrelease.htm) (sec-8k): said Allan Reine, M.D., Chief Executive Officer of Prime Medicine
- 缺口：CEO及关键高管的任职时间和任期稳定性
- 缺口：关键科学创始人/CSO的留任情况
- 缺口：近期高管层变动记录
- 缺口：引用不存在或原文无法匹配
- 证伪条件：CEO或关键科学负责人离职
- 证伪条件：监管调查或治理丑闻披露
- 证伪条件：董事会独立性受到质疑

## RDNT · complete

审查记录：`state/serenity-reviews/RDNT-claude-68ea39ef2d9a8f3122a0.json`

### supply_chain_map: pass

418 家影像中心，设备供应商分散。

- 支持 [ev_982718e930ed9a0e](https://www.sec.gov/Archives/edgar/data/790526/000162828026013337/rdnt-20251231.htm) (primary-document): 418 imaging centers located in Arizona, California, Delaware, Florida, Maryland, Virginia, New Jersey, Texas and New York.
- 支持 [ev_08ef53d3a6bf6a3c](https://www.sec.gov/Archives/edgar/data/790526/000162828026013337/rdnt-20251231.htm) (primary-document): such firms as GE, Hologic, Key Equipment, Philips, Siemens and Spectrum

### chokepoint_evidence: partial

区域密度与医院合资构成运营优势，但非供应垄断。

- 支持 [ev_a8fa911f0fd4c0bf](https://www.sec.gov/Archives/edgar/data/790526/000162828026013337/rdnt-20251231.htm) (primary-document): We have entered into joint ventures with certain hospitals to both provide and manage their diagnostic imaging services
- 缺口：区域市场份额数据

### customer_dependency: pass

付款方多元，无单一客户依赖。

- 支持 [ev_ed319c761b2bf9a4](https://www.sec.gov/Archives/edgar/data/790526/000162828026013337/rdnt-20251231.htm) (primary-document): Our revenue is derived from a diverse mix of payors, including commercial insurance payors, managed care capitated payors, and government payors such as Medicare and Medicaid

### pure_play: partial

AI 业务约占收入 5%，主体是影像中心运营。

- 缺口：Digital Health 收入占比的年报原文

### multi_node_control: pass

同时控制影像服务与 AI 软件。

- 支持 [ev_a8fa911f0fd4c0bf](https://www.sec.gov/Archives/edgar/data/790526/000162828026013337/rdnt-20251231.htm) (primary-document): We have entered into joint ventures with certain hospitals to both provide and manage their diagnostic imaging services

### earnings_validation: pass

Q3 2026 服务收入 6.383 亿美元，同比增长 22%；同店收入增长 9.6%（季报原文）。

- 支持 [ev_818151b1a490813c](https://www.sec.gov/Archives/edgar/data/790526/000162828026072345/rdnt-20260930.htm) (primary-document): Total service revenue 638,257 522,869 1,836,608 1,492,498
- 支持 [ev_aaf3252796f78775](https://www.sec.gov/Archives/edgar/data/790526/000162828026072345/rdnt-20260930.htm) (primary-document): Our 9.6% increase in Imaging Center same center revenue compared to the same period last year was driven by higher fees per imaging procedure and increased procedure volumes

### counter_thesis: pass

杠杆与医保降价风险已检验。

- 支持 [ev_5f78bddefc4a485d](https://www.sec.gov/Archives/edgar/data/790526/000162828026013337/rdnt-20251231.htm) (primary-document): approximately 6% of our total net revenue from capitation arrangements
- 反证 [ev_cb00d487991f7e49](https://www.sec.gov/Archives/edgar/data/790526/000162828026013337/rdnt-20251231.htm) (primary-document): term loan indebtedness, excluding related discount, was $1,084.9 million
- 反证 [ev_da4d05ee0489c769](https://www.sec.gov/Archives/edgar/data/790526/000162828026013337/rdnt-20251231.htm) (primary-document): Medicare payment and coverage policies in the final rule could result in reimbursement reductions
- 证伪条件：DeepHealth 外部收入增速低于核心业务

### management_governance: pass

按 Serenity 规则：领导层连续，且无未结调查或未定继任。Proxy声明（DEF 14A）确认Berger担任CEO兼董事会主席、Stolper担任CFO均在任，无未结调查或法律程序披露，CEO/CFO/董事长职位均无空缺或未定继任；2026年1月1日生效的职位变更仅涉及下级高管（Forthuber、Hames、Patel），核心领导层未变动。主要持续性治理风险为CEO兼任主席的权力集中、CEO通过BRMG持有加州/亚利桑那几乎所有医疗服务的重大关联交易、关联方审批程序非正式，以及COO Patel 11月公开市场出售股份未使用10b5-1计划。

- 支持 [ev_23f5d928746d2cca](https://www.sec.gov/Archives/edgar/data/790526/000168316826003086/radnet_idef14a.htm) (primary-document): Howard G. Berger, M.D. - President and Chief Executive Officer (our principal executive officer) · Mark D. Stolper - Executive Vice President and Chief Financial Officer (our principal financial officer)
- 支持 [ev_9e84c4c26b3040d4](https://www.sec.gov/Archives/edgar/data/790526/000168316826003086/radnet_idef14a.htm) (primary-document): Our Chairman of the Board of Directors, Dr. Berger, also serves as our Chief Executive Officer.
- 支持 [ev_ec71b4cc364be3cc](https://www.sec.gov/Archives/edgar/data/790526/000168316826003086/radnet_idef14a.htm) (primary-document): None of our current directors or executive officers have been, during the past 10 years, involved in any legal proceedings required to be disclosed pursuant to Item 401(t) of Regulation S-K.
- 支持 [ev_341052c9f1f40de5](https://www.sec.gov/Archives/edgar/data/790526/000168316826003086/radnet_idef14a.htm) (primary-document): There have been no material proceedings to which any director, executive officer or affiliate of the Company, any owner of record or beneficially of more than five percent of any class of voting securities of the Company, or any associate of any such director, executive officer, affiliate of the Company, or security holder is a party adverse to the Company or any of its subsidiaries or has a material interest adverse to the Company or any of its subsidiaries.
- 支持 [ev_3eca75137def773e](https://www.sec.gov/Archives/edgar/data/790526/000168316826003086/radnet_idef14a.htm) (primary-document): three of the above Named Executive Officers had their job titles changed effective as of January 1, 2026 as shown below. Name New Title Stephen Forthuber President and Chief Executive Officer – Eastern Operations Norman Hames President and Chief Executive Officer – Western Operations Mital Patel Executive Vice President and Chief Operating Officer
- 支持 [ev_e7a8ac79c4fd2004](https://www.sec.gov/Archives/edgar/data/790526/000168316826003086/radnet_idef14a.htm) (primary-document): We maintain emergency succession plans for the CEO and other executive committee members.

## RMD · complete

审查记录：`state/serenity-reviews/RMD-claudecli-b2b40ead3e263e55de7e.json`

### supply_chain_map: partial

10-Q披露了两个运营分部（Sleep and Breathing Health及Residential Care Software）及全球制造布局，但未具体列出上游关键供应商名称或下游客户的具体采购关系。仅有XBRL标签暗示存在单一客户集中风险，缺乏完整供应链图谱。

- 支持 [ev_d51314f058cab928](https://www.sec.gov/Archives/edgar/data/943819/000094381926000089/rmd-20260930.htm) (primary-document): Our manufacturing operations are located in Australia, Singapore, Malaysia, France, China and the United States
- 支持 [ev_0c1caeb15e6a7688](https://www.sec.gov/Archives/edgar/data/943819/000094381926000089/rmd-20260930.htm) (primary-document): we have two operating segments, which are the sleep and respiratory disorders sector of the medical device industry, or Sleep and Breathing Health, and the supply of business management SaaS to residential care providers, or Residential Care Software
- 支持 [ev_9bc7f90b799d0fe1](https://www.sec.gov/Archives/edgar/data/943819/000094381926000089/rmd-20260930.htm) (primary-document): Net revenue - Sleep and Breathing Health products $ 1,259,802 $ 1,169,446
- 缺口：上游关键零部件/原材料供应商名称及集中度
- 缺口：下游具体客户名称、采购金额及合同关系
- 缺口：各制造基地的产能分配与角色
- 证伪条件：发现主要零部件存在多家可替代供应商，则无供应链瓶颈
- 证伪条件：下游客户高度分散、无锁定效应

### chokepoint_evidence: unknown

ResMed是睡眠呼吸医疗器械龙头，但证据中未显示其在任何物理输入或关键环节上具备供应集中度（<5家全球供应商）或替代壁垒。FDA AI设备仅证明产品获批，不构成瓶颈证据。AI相关性本身不足以通过此门。

- 反证 [ev_36d245be83bd66ea](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K251657) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：全球睡眠呼吸设备或传感器供应的集中度数据
- 缺口：替代供应商的转换成本或交货周期证据
- 缺口：任何节点的寡头/垄断地位的定量证据
- 缺口：反证只是通用风险条款或记录字段，不是针对公司的直接反证
- 证伪条件：发现Philips、Fisher & Paykel等竞争对手均可提供类似产品
- 证伪条件：关键部件（芯片、传感器、马达）有多家供应商

### customer_dependency: partial

XBRL标签显示存在单一客户营收集中度披露（OneCustomerMember），表明至少一个大客户存在，但证据包中未提供该客户名称、占比或合同细节。无法确认具体采用/依赖关系。

- 支持 [ev_ef941e1849d39830](https://www.sec.gov/Archives/edgar/data/943819/000094381926000089/rmd-20260930.htm) (primary-document): us-gaap:CustomerConcentrationRiskMember rmd:OneCustomerMember us-gaap:RevenueFromContractWithCustomerMember
- 缺口：大客户名称及营收占比
- 缺口：客户合同条款或设计锁定机制
- 缺口：终端用户（医院/保险/患者）的采购依赖证据
- 证伪条件：大客户占比低于10%，不构成依赖
- 证伪条件：客户可轻易切换至Philips或Fisher & Paykel产品

### pure_play: partial

ResMed主营业务高度集中于睡眠呼吸健康（占总营收约89%），另有Residential Care Software分部。作为AI医疗主题，仅有一个FDA批准的AI设备（PTCS），AI营收贡献不明。公司更多是医疗器械公司而非AI纯正标的。MatrixCare业务正在剥离，表明在聚焦主业。

- 支持 [ev_9bc7f90b799d0fe1](https://www.sec.gov/Archives/edgar/data/943819/000094381926000089/rmd-20260930.htm) (primary-document): Net revenue - Sleep and Breathing Health products $ 1,259,802 $ 1,169,446
- 支持 [ev_9bc7f90b799d0fe1](https://www.sec.gov/Archives/edgar/data/943819/000094381926000089/rmd-20260930.htm) (primary-document): Net revenue - Residential Care Software 155,012 166,136
- 支持 [ev_830f99f7e46c020b](https://www.sec.gov/Archives/edgar/data/943819/000094381926000047/rmd-20260630.htm) (primary-document): us-gaap:DiscontinuedOperationsHeldforsaleMember rmd:MatrixCareBusinessMember 2025-07-01 2026-06-30
- 缺口：AI相关产品/功能的营收拆分
- 缺口：数字健康/软件在Sleep and Breathing Health分部中的具体占比
- 缺口：AI产品路线图及未来营收预期
- 证伪条件：AI功能仅嵌入传统硬件，无独立营收贡献
- 证伪条件：竞争对手同样快速部署AI功能，无差异化

### multi_node_control: unknown

证据显示ResMed覆盖设备制造与SaaS软件两个业务，但这并非同一供应链上下游的两个连续节点。无证据表明公司控制了上游关键材料/部件节点并同时控制下游设备节点，不满足'至少控制两个相连供应链节点'的要求。

- 缺口：上游部件自制或垂直整合的证据
- 缺口：从原材料到终端产品的多节点控制证据
- 缺口：专利或技术壁垒形成的节点锁定
- 缺口：不通过需要直接反证，缺少证据不能等同失败
- 证伪条件：关键零部件完全外购，无上游控制力
- 证伪条件：软件与硬件分部服务不同客群，非同一供应链

### earnings_validation: pass

最新季度（截至2026-09-30）实际财务数据强劲：营收$14.15亿（同比+5.9%），净利润$4.18亿，经营现金流$4.22亿，现金$10.1亿。毛利率61.5%，公司盈利能力已得到验证。同时宣布$0.66/股季度股息及大规模回购，财务状况稳健。

- 支持 [ev_4fb65163c1c82250](https://data.sec.gov/api/xbrl/companyfacts/CIK0000943819.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 1,414,814,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_4fb65163c1c82250](https://data.sec.gov/api/xbrl/companyfacts/CIK0000943819.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 418,413,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_4fb65163c1c82250](https://data.sec.gov/api/xbrl/companyfacts/CIK0000943819.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): 422,422,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_9bc7f90b799d0fe1](https://www.sec.gov/Archives/edgar/data/943819/000094381926000089/rmd-20260930.htm) (primary-document): Gross profit 870,567 817,664
- 支持 [ev_8cda6aff298f0e36](https://www.sec.gov/Archives/edgar/data/943819/000094381926000089/rmd-20260930.htm) (primary-document): Purchases of treasury stock ( 936,378 ) ( 150,010 )
- 证伪条件：Sleep and Breathing Health分部增速大幅放缓至负增长
- 证伪条件：毛利率因竞争或关税压力持续下降

### counter_thesis: partial

已识别部分反面论点：1）Levi & Korsinsky律所对管理层信托责任展开调查（治理风险）；2）Residential Care Software营收同比下降（$155M vs $166M）；3）现金从$14.69亿降至$10.1亿（大额回购消耗）；4）GLP-1药物可能减少肥胖相关睡眠呼吸暂停患者群体。但缺乏对替代产品、地缘政治、估值角度的系统性压力测试。

- 支持 [ev_b640d80c79069fc4](https://news.google.com/rss/articles/CBMi4wJBVV95cUxNX25ELXNYeWtYY1dBM0tVdnJpSE5lUFJWNGh3NWdVd0xzZEZDR3F6c1VzSlNyb0ZWMVM5UDM1NmlPWkpnZnk2cWNTcGttczJUNHFFanFVelBBQkJKenQ2NDBKdXl0YjVzdnNzT1V6TDBLeWpiYkFhUFZjUG9laVhiSFVTcWZQbzQ0V1FJS2RSM3JhSjBvMmJZZVI1WXJhcUd5NHVJQnlCdTIxSmprSnNxQnVGM2d0cGJvUzZLeUhQdmhtQ3oxWnlXRmJOSUppcFRfVkNCamJJbzNfazdhTEd5T0Q4ZlNCcnhiSG9NRk9fd28yTWozV2R2Q2JuS3JodWwxUEp6Tkxvb1BvQTFFejZiSS1HS1JuRGpiSmZLUWtyTHFqdjR3clBBVXNxZ0FVUFhCWFVkSmlHaFZORDlLem45QldzTVc5Qk13NU9CUUNhZlFMQ3BvRE5Nb3N1ZURNLUtuM0Jz?oc=5) (news-feed): SHAREHOLDER ALERT: Levi & Korsinsky, LLP Notifies Shareholders of an Investigation Concerning Possible Breaches of Fiduciary Duties by Certain Officers and Directors of ResMed Inc.
- 支持 [ev_9bc7f90b799d0fe1](https://www.sec.gov/Archives/edgar/data/943819/000094381926000089/rmd-20260930.htm) (primary-document): Net revenue - Residential Care Software 155,012 166,136
- 支持 [ev_a1207c7205159749](https://www.sec.gov/Archives/edgar/data/943819/000094381926000089/rmd-20260930.htm) (primary-document): Cash and cash equivalents $ 1,010,742 $ 1,469,234
- 支持 [ev_8cda6aff298f0e36](https://www.sec.gov/Archives/edgar/data/943819/000094381926000089/rmd-20260930.htm) (primary-document): Purchases of treasury stock ( 936,378 ) ( 150,010 )
- 缺口：GLP-1减肥药对OSA患者群体的量化冲击分析
- 缺口：Philips等竞争对手市场份额变动趋势
- 缺口：估值角度的压力测试（$33.7B市值 vs 盈利增速）
- 缺口：地缘政治风险（中国/新加坡制造基地的关税或政策风险）
- 证伪条件：GLP-1药物大幅减少CPAP设备需求
- 证伪条件：Philips召回后份额回归压缩ResMed定价权
- 证伪条件：股东诉讼导致管理层变动或重大赔偿
- 证伪条件：大额回购后杠杆率上升限制未来投资能力

### management_governance: unknown

Levi & Korsinsky律所已公开通知正在调查ResMed管理层可能的信托责任违反行为。这属于'未解决的调查'，根据规则必须保持pending/partial状态。公司已确认Sarbanes-Oxley 404(b)内控审计通过，但该外部调查的结果未知。

- 反证 [ev_b640d80c79069fc4](https://news.google.com/rss/articles/CBMi4wJBVV95cUxNX25ELXNYeWtYY1dBM0tVdnJpSE5lUFJWNGh3NWdVd0xzZEZDR3F6c1VzSlNyb0ZWMVM5UDM1NmlPWkpnZnk2cWNTcGttczJUNHFFanFVelBBQkJKenQ2NDBKdXl0YjVzdnNzT1V6TDBLeWpiYkFhUFZjUG9laVhiSFVTcWZQbzQ0V1FJS2RSM3JhSjBvMmJZZVI1WXJhcUd5NHVJQnlCdTIxSmprSnNxQnVGM2d0cGJvUzZLeUhQdmhtQ3oxWnlXRmJOSUppcFRfVkNCamJJbzNfazdhTEd5T0Q4ZlNCcnhiSG9NRk9fd28yTWozV2R2Q2JuS3JodWwxUEp6Tkxvb1BvQTFFejZiSS1HS1JuRGpiSmZLUWtyTHFqdjR3clBBVXNxZ0FVUFhCWFVkSmlHaFZORDlLem45QldzTVc5Qk13NU9CUUNhZlFMQ3BvRE5Nb3N1ZURNLUtuM0Jz?oc=5) (news-feed): SHAREHOLDER ALERT: Levi & Korsinsky, LLP Notifies Shareholders of an Investigation Concerning Possible Breaches of Fiduciary Duties by Certain Officers and Directors of ResMed Inc.
- 缺口：调查的具体指控内容及涉及的高管
- 缺口：公司对该调查的正式回应
- 缺口：近期高管变动或继任计划信息
- 缺口：引用不存在或原文无法匹配
- 证伪条件：调查升级为正式诉讼或SEC执法行动
- 证伪条件：关键高管因调查离职
- 证伪条件：发现重大会计违规或内控缺陷

## RNA · complete

审查记录：`state/serenity-reviews/RNA-claudecli-4de2708bcd53c49c9ccc.json`

### supply_chain_map: unknown

上游依赖第三方CRO/CMO进行临床前研究、临床试验和生产；公司产品为AOC平台驱动的RNA心脏精准药物（ATR 1072、ATR 1086）；下游为BMS和LLY的合作协议及遗传性心肌病患者群体。但证据中未披露具体供应商名称或原料来源，供应链图谱不完整。

- 支持 [ev_0e673462a48aa245](https://www.sec.gov/Archives/edgar/data/2093101/000119312526442601/d70523dex992.htm) (primary-document): our reliance on third parties for the manufacture of our product candidates
- 支持 [ev_6d2ed96e3a051cf7](https://www.sec.gov/Archives/edgar/data/2093101/000119312526442601/d70523dex992.htm) (primary-document): collaborations with BMS and LLY
- 缺口：具体CMO/CRO供应商名称
- 缺口：原材料（如寡核苷酸、抗体）的供应来源和集中度
- 缺口：生产设施地理位置
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现关键CMO/CRO终止合同或产能不足
- 证伪条件：原材料供应中断导致临床试验延迟

### chokepoint_evidence: unknown

Atrium是临床阶段药物开发公司，专注遗传性心肌病RNA疗法。证据显示该领域目前无已批准的疾病修饰疗法，但这仅表明医疗需求未被满足，不等同于供应链瓶颈或替代壁垒。无证据表明公司控制任何稀缺供应节点。

- 缺口：AOC平台相对于其他RNA递送技术的独占性或专利壁垒证据
- 缺口：心脏靶向递送技术的竞争格局和替代方案分析
- 缺口：任何供应集中度数据
- 缺口：引用不存在或原文无法匹配
- 证伪条件：其他公司开发出类似心脏靶向RNA递送平台
- 证伪条件：通用递送技术证明在心肌组织中同样有效

### customer_dependency: unknown

证据显示与BMS和LLY存在合作协议，并有里程碑付款（BMS于2026年8月13日支付$15M里程碑款），季度合作收入$15.3M。但产品仍在临床阶段，无终端患者使用或商业化客户采纳证据。

- 支持 [ev_6d2ed96e3a051cf7](https://www.sec.gov/Archives/edgar/data/2093101/000119312526442601/d70523dex992.htm) (primary-document): the $15M milestone earned from Bristol Myers Squibb announced on August 13, 2026
- 支持 [ev_8ad0653df1b0b1c5](https://data.sec.gov/api/xbrl/companyfacts/CIK0002093101.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 15,321,000 for 2026-07-01 to 2026-09-30
- 缺口：BMS和LLY合作协议的具体条款和范围
- 缺口：合作收入中BMS与LLY各自占比
- 缺口：终端患者采纳或商业化渠道证据
- 缺口：引用不存在或原文无法匹配
- 证伪条件：BMS或LLY终止合作协议
- 证伪条件：里程碑付款条件未达成导致收入断裂

### pure_play: unknown

公司管线完全聚焦于遗传性心肌病RNA精准疗法：ATR 1072（PRKAG2综合征）、ATR 1086（PLN心肌病）及两个未披露的精准心脏靶点。收入来源为相关合作协议。但无分部收入披露来量化主题敞口比例。

- 支持 [ev_bcce7f1a2240eb93](https://www.sec.gov/Archives/edgar/data/2093101/000119312526442601/d70523dex992.htm) (primary-document): Our vision: To pioneer precision RNA medicines for the heart and profoundly improve the lives of people impacted by cardiac diseases
- 缺口：分部财务数据确认收入全部来自心脏RNA疗法相关活动
- 缺口：合作收入是否包含非心脏适应症的部分
- 缺口：引用不存在或原文无法匹配
- 证伪条件：公司进入与心脏RNA无关的治疗领域导致主题稀释

### multi_node_control: unknown

公司拥有AOC递送平台及基于该平台的多个候选药物，但这属于单一平台驱动的产品线，不构成对供应链中两个相连节点的控制。无证据显示公司同时控制上游原材料/制造和下游分销等相连节点。

- 缺口：公司是否自有生产设施（垂直整合证据）
- 缺口：平台技术是否控制关键上游组件的独家供应
- 缺口：引用不存在或原文无法匹配
- 证伪条件：公司完全依赖外部CMO，不控制任何供应链节点

### earnings_validation: unknown

临床准备阶段公司，合作收入部分抵消研发支出。Q3 2026实际数据：收入$15.3M，净亏损仅$4.3M，研发支出$13.8M。XBRL显示现金$44.6M（不含短期投资），演示文稿披露截至2026年6月现金+投资$264M，另有10月$50M定增。公司声称资金可支撑至2028年底，覆盖2H 2027的POC数据里程碑。但XBRL现金与演示文稿总流动性差异大，完整流动性需依赖投资余额数据。

- 支持 [ev_8ad0653df1b0b1c5](https://data.sec.gov/api/xbrl/companyfacts/CIK0002093101.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 15,321,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_8ad0653df1b0b1c5](https://data.sec.gov/api/xbrl/companyfacts/CIK0002093101.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -4,266,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_8ad0653df1b0b1c5](https://data.sec.gov/api/xbrl/companyfacts/CIK0002093101.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 44,565,000 for as of 2026-09-30
- 支持 [ev_8ad0653df1b0b1c5](https://data.sec.gov/api/xbrl/companyfacts/CIK0002093101.json) (sec-companyfacts): R&D expense (ResearchAndDevelopmentExpense): 13,796,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_6d2ed96e3a051cf7](https://www.sec.gov/Archives/edgar/data/2093101/000119312526442601/d70523dex992.htm) (primary-document): proceeds from the $50M private placement financing announced on October 8, 2026
- 缺口：短期投资余额（解释XBRL现金$44.6M与演示文稿$264M+投资的差异）
- 缺口：完整资产负债表确认总流动性
- 缺口：2026年全年运营现金流预估
- 缺口：引用不存在或原文无法匹配
- 证伪条件：总流动资产（含投资）不足以支撑至2027年POC数据时间点
- 证伪条件：BMS/LLY合作收入突然终止导致现金消耗加速

### counter_thesis: unknown

已识别的反面论点包括：1）临床试验失败风险（Phase 1/2尚无数据，POC数据要到2H 2027）；2）AOC平台从Avidity分拆，技术依赖性存疑；3）PRKAG2综合征为罕见病，市场规模可能极小；4）第三方制造依赖。但证据包中缺乏具体竞争对手的心脏RNA疗法进展数据，无法充分压力测试替代风险。资金面：runway 34.6个月，financingRisk为false，短期无股权稀释压力。

- 支持 [ev_f0bdaf1f78a4ed8a](https://www.sec.gov/Archives/edgar/data/2093101/000119312526442601/d70523dex992.htm) (sec-8k): the design, capability and scalability of our AOC platform, including its ability to efficiently deliver to cardiac tissue
- 支持 [ev_bcce7f1a2240eb93](https://www.sec.gov/Archives/edgar/data/2093101/000119312526442601/d70523dex992.htm) (primary-document): Atrium has made solid progress since our launch in February 2026
- 反证 [ev_0e673462a48aa245](https://www.sec.gov/Archives/edgar/data/2093101/000119312526442601/d70523dex992.htm) (primary-document): the limitations of nonclinical models, which may not fully replicate human disease
- 缺口：具体竞争对手在心脏靶向基因治疗领域的管线进展
- 缺口：Avidity与Atrium分拆后的IP权利边界
- 缺口：PRKAG2综合征确切患者人数和可触达市场规模
- 缺口：地缘政治风险（如中国RNA原料供应链依赖）
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：ATR 1072 Phase 1/2临床试验出现严重安全性信号
- 证伪条件：竞争对手在PRKAG2或PLN适应症获得突破性疗法认定
- 证伪条件：Avidity收回AOC平台关键IP授权
- 证伪条件：BMS或LLY终止合作导致收入和里程碑付款消失
- 证伪条件：PRKAG2综合征患者人群过小无法支撑商业化

### management_governance: unknown

证据显示管理团队具备丰富的罕见病和RNA药物开发经验，多位高管来自Avidity（母公司）。CEO Kath Gallagher有20年以上行业经验，CMO Steve Hughes参与50+临床试验。董事会包含6名成员。但无独立董事比例、审计委员会构成、高管薪酬、内部人交易等治理细节，也无关于分拆后治理独立性的具体信息。

- 支持 [ev_86c2cc9b9a41b8eb](https://www.sec.gov/Archives/edgar/data/2093101/000119312526442601/d70523dex992.htm) (primary-document): Atrium Board Members Troy Wilson Kath Gallagher Sarah Boyce (Chair) Simona Skerjenac Carsten Boess W. Michael Flanagan, Ph.D.
- 缺口：独立董事比例和审计/薪酬委员会构成
- 缺口：高管薪酬和股权激励结构
- 缺口：与Avidity分拆后的关联交易披露
- 缺口：内部人持股和近期交易记录
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现未披露的关联交易或利益冲突
- 证伪条件：关键高管离职（特别是从Avidity带来的核心团队）
- 证伪条件：监管机构对公司治理发起调查

## RXRX · complete

审查记录：`state/serenity-reviews/RXRX-claude-2336196215efaa40167d.json`

### supply_chain_map: pass

按 Serenity 规则：上游投入、公司产品、下游用户均有具体关系的一手证据。通道揭示了RXRX的上游输入（Tempus去识别化临床记录、Takeda授权化合物TAK-733、第三方CDMO药物制造、第三方平台试剂设备供应商）、公司产品（Phenomap生物图谱、TxFM AI模型及REC-4881/REC-1245临床资产）以及下游用户（Sanofi免疫学小分子合作、Roche神经科学Phenomap、Tempus肿瘤学TxFM许可）之间的具体关系。实际财务数据中，2025年全年总收入同比增长27%（7.47亿美元）、Roche 3000万美元Phenomap验收里程碑（2025年第四季度）、Sanofi 1000万美元免疫学候选药物里程碑（2026年第三季度）及TxFM 1200万美元许可费（2026年9月）均与论点"合作里程碑及临床资产提供多种获胜路径"一致，但2026年前九个月运营收入同比下降19%与论点相悖，持续扩大的净亏损（2025年6.45亿美元）与论点无直接关联。

- 支持 [ev_3c47e48a9db71793](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000145/rxrx-20260930.htm) (primary-document): Tempus will also provide the Company with access to a certain number of de-identified pathology records with linked clinical data during the term of the TxFM License Agreement.
- 支持 [ev_a29027d388134e7c](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): we obtained an exclusive (even as to Takeda and its affiliates), worldwide, sublicensable under certain conditions, transferable, royalty-bearing license to certain Takeda patents, know-how and materials related to develop, manufacture and commercialize Takeda’s clinical-stage compound known as TAK-733, a non-ATP-competitive allosteric inhibitor of MEK1 and MEK2
- 支持 [ev_f2bd4d83f8603fea](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): Cost of revenue consists of the Company’s costs to provide services for drug discovery required under performance obligations with partnership customers.
- 支持 [ev_5c9cc242598fca8e](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): the acceptance fee for the completion of a Phenomap for one of our neuroscience performance obligations
- 支持 [ev_f9af4ab25e97f4ed](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000145/rxrx-20260930.htm) (primary-document): the Company granted Tempus a non-exclusive, non-sublicensable, non-transferable, worldwide license to the Company's TxFM Model solely for use within the field of oncology.
- 支持 [ev_8b0af9c428298ce0](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000145/rxrx-20260930.htm) (primary-document): Clinical FAP REC-4881 5,750 2,101 3,649 >100% 12,705 6,925 5,780 83 % RBM39 REC-1245 3,996 1,193 2,803 >100% 9,657 5,643 4,014 71 %
- 支持 [ev_58fa039e1e225d58](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): the increase in revenue compared to the prior year was due to revenue recognized from our partnership with Sanofi.
- 支持 [ev_2ac7a1a89452b02f](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000145/rxrx-20260930.htm) (primary-document): the increase in revenue compared to the prior period was primarily due to our Sanofi partnership, for which the Company achieved a $10.0 million milestone for an immunology small molecule development candidate.
- 支持 [ev_e82d4ded48c79845](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): the increase in revenue compared to the prior year was due to revenue recognized from our partnership with Roche. We recognized revenue related to the acceptance fee for the completion of a Phenomap for one of our neuroscience performance obligations.
- 支持 [ev_9ff4fbd79fa4b366](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000145/rxrx-20260930.htm) (primary-document): the Company granted Tempus a non-exclusive, non-sublicensable, non-transferable, worldwide license to the Company's TxFM Model solely for use within the field of oncology. Permitted uses include diagnostic applications, clinical applications, and Tempus's internal research and development.

### chokepoint_evidence: partial

数据与自动化实验室构成数据壁垒，但不是供应垄断；10-K 自己列出多家竞争者。

- 支持 [ev_0529225fbf9bf737](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): one of the largest relatable data sets in biopharma
- 反证 [ev_d343edefb1063ae5](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): Representative examples include Relay Therapeutics, Isomorphic Labs, Schrodinger, and AbCellera.
- 缺口：没有市场份额或替代周期数据

### customer_dependency: pass

与多家大药企合作并已收到超过 5 亿美元的预付和里程碑付款。

- 支持 [ev_fffc19ee98fc2e58](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): Through our partnerships with leading pharmaceutical companies including Roche and Genentech, Sanofi, Bayer, and Merck KGaA
- 支持 [ev_07d5bb4c371089ed](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): we have secured more than $500 million in upfront and progress-based milestone payments to date

### pure_play: pass

全部业务是 AI 与自动化驱动的药物发现。

- 支持 [ev_d3851337fe1c14a4](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): Our data includes cellular phenomics, captured using brightfield microscopy

### multi_node_control: pass

同时控制实验数据生成、算力（自有超算）与临床管线。

- 支持 [ev_ee77462e9daea5fb](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): our own supercomputer, BioHive-2
- 支持 [ev_54171fe3bfd7cb6c](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): using our automated high throughput labs, which can run over 2 million experiments per week

### earnings_validation: partial

按 Serenity 规则：实际结果有的支持、有的不支持论点。通道揭示了RXRX的上游输入（Tempus去识别化临床记录、Takeda授权化合物TAK-733、第三方CDMO药物制造、第三方平台试剂设备供应商）、公司产品（Phenomap生物图谱、TxFM AI模型及REC-4881/REC-1245临床资产）以及下游用户（Sanofi免疫学小分子合作、Roche神经科学Phenomap、Tempus肿瘤学TxFM许可）之间的具体关系。实际财务数据中，2025年全年总收入同比增长27%（7.47亿美元）、Roche 3000万美元Phenomap验收里程碑（2025年第四季度）、Sanofi 1000万美元免疫学候选药物里程碑（2026年第三季度）及TxFM 1200万美元许可费（2026年9月）均与论点"合作里程碑及临床资产提供多种获胜路径"一致，但2026年前九个月运营收入同比下降19%与论点相悖，持续扩大的净亏损（2025年6.45亿美元）与论点无直接关联。

- 支持 [ev_07abf13fef349093](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): Total revenue 74,681 58,839 44,575 15,842 26.9 % 14,264 32.0 %
- 支持 [ev_e9b6a309b8dd60ed](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000145/rxrx-20260930.htm) (primary-document): the $ 30.0 million variable consideration for the second acceptance fee until the map was accepted, which was during the fourth quarter of 2025.
- 支持 [ev_539b9e08d4320f14](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000145/rxrx-20260930.htm) (primary-document): Total revenue 18,552 5,175 32,694 39,143
- 支持 [ev_2ac7a1a89452b02f](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000145/rxrx-20260930.htm) (primary-document): the increase in revenue compared to the prior period was primarily due to our Sanofi partnership, for which the Company achieved a $10.0 million milestone for an immunology small molecule development candidate.
- 支持 [ev_063432cb068a83ff](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000145/rxrx-20260930.htm) (primary-document): Tempus will pay the Company a non-refundable license fee of $ 12.0 million in two installments of
- 反证 [ev_f911148ff5db62c1](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000145/rxrx-20260930.htm) (primary-document): Operating revenue $ 18,055 $ 4,983 $ 13,072 >100% $ 31,659 $ 38,905 $ (7,246) (19) %
- 缺口：按 Serenity 规则：实际结果有的支持、有的不支持论点

### counter_thesis: pass

稀释与供应链地缘风险已用原文检验；反方成立，不适合高确信度。

- 支持 [ev_535022fa432f7fca](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): our stockholders’ ownership interests will be diluted.
- 反证 [ev_b569305f0e41958b](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): we entered into a sales agreement for an at-the-market offering for the sale of up to $300 million
- 反证 [ev_4cb33424380b5eb5](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): While the BIOSECURE Act as currently proposed would restrict purchasing of services or products from WuXi AppTec
- 证伪条件：REC-4881 注册性试验推迟到 2028 年以后
- 证伪条件：12 个月内再次融资

### management_governance: partial

按 Serenity 规则：继任未定，不能评为通过。CEO（Najat Khan）与CFO（Ben Taylor）经2026年4月21日代理委托书及2026年11月2日10-Q签署确认在任，无开放性调查披露；但董事会主席Gibson不寻求连任且无具名继任人，接任人选待董事会另行任命，构成未决继任问题。

- 支持 [ev_758aec7c922db4ec](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000145/rxrx-20260930.htm) (primary-document): By: /s/ Najat Khan Najat Khan Chief Executive Officer (Principal Executive Officer) By: /s/ Ben Taylor Ben Taylor Chief Financial Officer (Principal Financial and Accounting Officer)
- 支持 [ev_caf1f88f36228cc4](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000065/rxrx-20260430.htm) (primary-document): Name Age Position Najat Khan 42 Chief Executive Officer and President Ben Taylor 48 Chief Financial Officer and President of Recursion UK David Hallett 56 Chief Scientific Officer
- 支持 [ev_a26c6da34310582d](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000065/rxrx-20260430.htm) (primary-document): The following table sets forth information for our executive officers as of April 21, 2026:
- 反证 [ev_0abaa2b30bb04421](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000065/rxrx-20260430.htm) (primary-document): Dr. Gibson is not standing for re-election and his current term will expire at the Annual Meeting.
- 反证 [ev_c5d66dbf69ee3b0a](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000065/rxrx-20260430.htm) (primary-document): Upon Dr. Gibson’s departure from the Board following the Annual Meeting, Dr. Hershberg will continue as Lead Independent Director until such time that the Board appoints a new Chair.
- 反证 [ev_8a8336ae5223c4b3](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000065/rxrx-20260430.htm) (primary-document): We currently expect and intend the positions of Chair of the Board of Directors and Chief Executive Officer to continue to be held by two individuals in the future.
- 缺口：一手材料未证明 CEO、CFO 在任

## RYTM · complete

审查记录：`state/serenity-reviews/RYTM-codex-231dae5b1d67d098f8b2.json`

### supply_chain_map: unknown

包内FDA记录的制造商名称与待审发行人不一致，存在名称碰撞，不能据此建立该公司的产品或供应链关系。

- 反证 [ev_83888b5cd157381c](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K220786) (fda-ai-device-list): FDA AI-enabled medical-device authorization record. Manufacturer: Rhythm Al, Ltd. Device: STAR Apollo Mapping System. Final decision date: 12/01/2022. This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：能够把FDA制造商与发行人法律实体连接起来的原始材料
- 缺口：公司产品、上游输入和下游用户的完整关系
- 证伪条件：官方实体信息确认FDA制造商与发行人无控制或隶属关系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 反证 [ev_83888b5cd157381c](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K220786) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

- 反证 [ev_83888b5cd157381c](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K220786) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：具名客户或经核验的客户数量
- 缺口：付费部署、续约和使用量
- 缺口：客户收入贡献及切换成本
- 证伪条件：客户试点未转为付费部署
- 证伪条件：续约率或实际使用量持续下降
- 证伪条件：客户采用可替代产品且切换成本很低

### pure_play: unknown

公司级财务数据或单个产品记录没有拆分目标主题收入、利润和资产贡献，不能判断业务是否为纯主题暴露。

- 缺口：目标主题收入占比
- 缺口：分部收入和利润
- 缺口：其他业务对总体结果的稀释程度
- 证伪条件：目标主题收入长期低于总收入的10%
- 证伪条件：增长主要来自与目标主题无关的业务

### multi_node_control: unknown

现有材料没有证明公司控制两个相连的供应链节点；多个产品、多个FDA记录或研发支出不等于跨节点控制。

- 缺口：至少两个相连节点的所有权或控制权
- 缺口：节点之间的经济依赖和收入传导
- 缺口：外部客户对两个节点的使用证据
- 证伪条件：关键节点实际由无关联第三方控制
- 证伪条件：所谓多个节点只是同一产品的不同版本

### earnings_validation: partial

SEC一手材料提供了带日期的实际公司级收入、利润、现金或研发数据，但没有把这些结果归因到目标主题或已识别产品，因此只能部分验证财务表现。

- 支持 [ev_05048cf23b466be1](https://data.sec.gov/api/xbrl/companyfacts/CIK0001649904.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for RHYTHM PHARMACEUTICALS, INC.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 92,128,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-03, accession 0001628280-26-069485. Same period a year earlier (2025-07-01 to 2025-09-30): 51,298,000, a change of +79.6%. Net income (loss) (NetIncomeLoss): -41,369,000 for 2026-07-01 to 2026-09-30; form 10-Q fi
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_05048cf23b466be1](https://data.sec.gov/api/xbrl/companyfacts/CIK0001649904.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for RHYTHM PHARMACEUTICALS, INC.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 92,128,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-03, accession 0001628280-26-069485. Same period a year earlier (2025-07-01 to 2025-09-30): 5
- 反证 [ev_05048cf23b466be1](https://data.sec.gov/api/xbrl/companyfacts/CIK0001649904.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -41,369,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-03, accession 0001628280-26-069485. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -44,185,000 for 2026-01-01 to 2026-03-31; form 10-Q filed 2026-05-05, accession 0001628280-26-030549. Cash and equivalents (CashAndCashEquivalentsAtCarryingV
- 缺口：竞争产品和替代路径
- 缺口：客户需求下行情景
- 缺口：监管与估值压力测试
- 缺口：关键假设的量化敏感度
- 证伪条件：收入增长停滞且亏损或现金消耗扩大
- 证伪条件：替代方案显著降低客户切换成本
- 证伪条件：估值隐含增长长期高于可实现增长

### management_governance: unknown

证据包没有董事会、关键管理层连续性、内部控制、关联交易、调查或继任计划材料，不能推定治理通过。

- 缺口：董事会与管理层履历
- 缺口：内部控制与重大缺陷
- 缺口：未决调查、诉讼和继任计划
- 证伪条件：关键高管突然离任且无明确继任安排
- 证伪条件：出现重大内控缺陷、监管调查或利益冲突

## SDGR · complete

审查记录：`state/serenity-reviews/SDGR-claude-f39a866cc56f6fa24c8c.json`

### supply_chain_map: pass

按 Serenity 规则：上游投入、公司产品、下游用户均有具体关系的一手证据。地图：上游为哥伦比亚大学授权IP（嵌入核心物理/AI软件）及第三方CRO与合同制造商（支持药物管线）；产品为计算预测建模平台（Glide、Prime等具名软件）加自有管线SGR-1505/3515；下游以生物制药公司为主，Novartis为代表命名客户。结果对论点基本一致：2025年软件收入1.995亿美元（+11%）、顶级20家药企ACV 8080万美元、商业客户总留存率96%均支持"卖铲子"逻辑，药物发现收入+107%支持管线上行空间；但2026年前三季度软件收入同比下滑（1.063亿 vs 1.169亿）且管理层明确预期近期收入下降，对论点构成压力。

- 支持 [ev_7d97c0f8cbe30418](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): Columbia University granted us and our affiliates an exclusive license (subject to specified non-commercial rights retained by Columbia University, on behalf of itself and other institutions, and any rights of the United States government), under Columbia University’s rights in specified software, or the Licensed Software, and patents, or the Licensed Patents, to develop, make, use, market, license, sell, distribute and otherwise commercially exploit products that
- 支持 [ev_d115eedcaf080e03](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): certain patents, software code, technology, and improvements thereto that we license from Columbia University and that are used in, and integrated into, our software solutions, and our physics-based computational platform
- 支持 [ev_ac9f1e77277933c0](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): agreements with the Bill & Melinda Gates Foundation entered into during the year ended December 31, 2024, aimed to accelerate the expansion of our computational software platform, and the extension of the agreement with Gates Ventures, LLC
- 支持 [ev_f9614471e5b9e6e7](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): our computational predictive modeling technology and enterprise informatics platform
- 支持 [ev_d215d49d588cb962](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): the electronic structure software program PS-GVB v1.0, the IMPACT software program used in the Glide ligand-protein docking program, the PrimeX protein modelling program, the QSite QM/MM program, the Combiglide automated library generation program, the Prime and PrimeX protein modelling programs, the Membrane Permeability model and the products that implement the water site analysis method, or collectively, the Licensed Products
- 支持 [ev_6defd256d5725ab7](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000076/sdgr-20260930.htm) (primary-document): Beyond our planned investments to complete our ongoing Phase 1 dose-escalation clinical trials of SGR-1505 and SGR-3515, we do not intend to initiate additional clinical trials or advance our other proprietary preclinical programs into clinical trials independently.
- 支持 [ev_f046a11a64a812cb](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): We sell our solutions primarily to biopharmaceutical companies, and our sales cycles can be as long as nine t
- 支持 [ev_8b2a6bb1a9a7075a](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): in November 2024, we entered into an expanded, three-year, software agreement with Novartis, which is more fully described in "— Collaboration Agreements ." The three-year agreement substantially increases Novartis' access to our computational predictive modeling technology and enterprise informatics platform to industry-leading scale.
- 支持 [ev_91f74d0dcc63a0fc](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): Our top 20 pharma industry cohort had an ACV of $80.8 million in 2025 compared to $70.0 million in 2024
- 支持 [ev_736d5c4439d4bfb7](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000076/sdgr-20260930.htm) (primary-document): The licenses that our customers purchase from us provide them the ability to perform a certain number of calculations used in the design of molecules for drug discovery or materials science.

### chokepoint_evidence: partial

留存率高，接近工具层事实标准；但 AI 原生竞争者众多。

- 支持 [ev_30e5c6d64af2a165](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): our gross dollar retention rate for our commercial customers was 96%
- 反证 [ev_5dd7c574e5f263f6](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): Insilico Medicine, Inc., Iktos, XtalPi Inc., AbCellera, Inductive Bio, Inc.

### customer_dependency: pass

按 Serenity 规则：一手文件披露了客户采用或使用。SDGR披露了实质性客户采用证据：2025年ACV达1.985亿美元，商业客户群ACV 1.774亿美元，软件客户总留存率96%，20个活跃付费合作药物发现项目；命名合作伙伴仅有Novartis（属合作公告，不单独构成采用证明）。另有客户集中度风险（单一客户曾占应收账款68%）及合同可随时终止的条款风险。

- 支持 [ev_698a39b97d277c4e](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): Our ACV was $198.5 million and $190.8 million for the years ended December 31, 2025 and 2024, respectively.
- 支持 [ev_ccc9c717fc887ccf](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): Our top 20 pharma industry cohort had an ACV of $80.8 million in 2025 compared to $70.0 million in 2024, and our commercial customer cohort had an ACV of $177.4 million in 2025 compared to $165.8 million in 2024.
- 支持 [ev_79713784534d6dcf](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): For the years ended December 31, 2025 and 2024, our gross dollar retention rate for our commercial customers was 96%.
- 支持 [ev_db37bec26f051bc7](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): our net dollar retention rate for our commercial customers was 100% for the year ended December 31, 2025, compared to 113% for the year ended December 31, 2024.
- 支持 [ev_5f6562e2264812d0](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): We are also party to a research collaboration and license agreement with Novartis for the discovery, research and preclinical development of small molecule compounds for targets in certain specified therapeutic areas, which also provides for joint ownership rights to certain intellectual property generated through the collaboration in certain scenarios.

### pure_play: pass

全部业务为计算驱动的药物发现。

- 支持 [ev_b7bcd6372d14612f](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): FEP+ is also able to perform these computations more rapidly than experimental assays.

### multi_node_control: pass

同时是软件供应商与药物开发者。

- 支持 [ev_7051cbfb03a4c7f5](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): We are advancing SGR-1505, our novel MALT1 inhibitor
- 支持 [ev_5c7f1c15dfa4ff2c](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): We are eligible to receive up to $2.272 billion in total milestones across the initial programs

### earnings_validation: partial

按 Serenity 规则：实际结果有的支持、有的不支持论点。地图：上游为哥伦比亚大学授权IP（嵌入核心物理/AI软件）及第三方CRO与合同制造商（支持药物管线）；产品为计算预测建模平台（Glide、Prime等具名软件）加自有管线SGR-1505/3515；下游以生物制药公司为主，Novartis为代表命名客户。结果对论点基本一致：2025年软件收入1.995亿美元（+11%）、顶级20家药企ACV 8080万美元、商业客户总留存率96%均支持"卖铲子"逻辑，药物发现收入+107%支持管线上行空间；但2026年前三季度软件收入同比下滑（1.063亿 vs 1.169亿）且管理层明确预期近期收入下降，对论点构成压力。

- 支持 [ev_bba7837c9bf8ef57](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): Total software products and services 199,500 180,365 19,135 11%
- 支持 [ev_1a6130195bf0a82a](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): Total revenues $ 255,869 $ 207,539 $ 48,330 23%
- 支持 [ev_606fb4af2a7d3981](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): our commercial customer cohort had an ACV of $177.4 million in 2025 compared to $165.8 million in 2024
- 支持 [ev_91f74d0dcc63a0fc](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): Our top 20 pharma industry cohort had an ACV of $80.8 million in 2025 compared to $70.0 million in 2024
- 支持 [ev_30e5c6d64af2a165](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): our gross dollar retention rate for our commercial customers was 96%
- 支持 [ev_e3d7bc88766fa157](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): Our net dollar retention rate for our commercial customers was 100% for the year ended December 31, 2025, compared to 113% for the year ended December 31, 2024.
- 支持 [ev_ed545ecef276fa64](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): Total drug discovery 56,369 27,174 29,195 107%
- 支持 [ev_03a0802e8ef843b0](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): The increase in revenues for drug discovery services during the year ended December 31, 2025 as compared to the year ended December 31, 2024 was primarily due to the Novartis collaboration services that began in November 2024 and the progress of new and existing collaborations.
- 反证 [ev_b69c6d7f3da18cc8](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000076/sdgr-20260930.htm) (primary-document): Total software revenue $ 38,153 $ 35,928 $ 106,257 $ 116,931
- 缺口：按 Serenity 规则：实际结果有的支持、有的不支持论点

### counter_thesis: pass

按 Serenity 规则：供应、需求、替代、地缘、估值均已检验，有证伪条件和有出处的反证（不代表风险消失）。文段显示SDGR的反向论点集中在三点：（1）软件营收结构性转型导致近期收入下滑已被管理层承认；（2）客户高度集中叠加年度可终止合同，使营收可持续性脆弱；（3）AI替代竞争和地缘政治风险（中国CMO依赖、BIOSECURE法案）对药物发现业务形成双重压力。

- 反证 [ev_04836fd92c0de175](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): We do not own or operate manufacturing facilities for the production of any product candidates, nor do we have plans to develop our own manufacturing operations. We rely and expect to continue to rely on third-party contract manufacturers for all of our required raw materials, drug substance, and finished drug product for the preclinical and clinical development of any development candidates we develop ourselves. We do not currently have any agreements with third-party manufacturers for the long-term supply of any of our product candidates.
- 反证 [ev_45a02da8253e1429](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): some of our manufacturers and suppliers are located in China. Trade tensions and conflicts between the United States and China have been escalated in recent years and, as such, we are exposed to the possibility of product supply disruption and increased costs and expenses in the event of changes to the laws, rules, regulations and policies of the governments of the United States or China
- 反证 [ev_f63a1884f35fc6e5](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): In December 2025, as part of the National Defense Authorization Act for FY 2026, President Trump signed into law the BIOSECURE Act, which prohibits, subject to limited exceptions, the direct or indirect use of U.S. federal government contract, grant, and loan funds for purchasing biotechnology equipment and services from certain Chinese biotechnology companies of concern
- 反证 [ev_bbb5bb85ae398946](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): We outsource substantially all of the infrastructure relating to our hosted software solutions to third-party hosting services. Customers of our hosted software solutions need to be able to access our computational platform at any time, without interruption or degradation of performance
- 反证 [ev_7ef51fee9b523db3](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000076/sdgr-20260930.htm) (primary-document): On-premise software $ 13,371 $ 15,928 $ 36,848 $ 57,094 Hosted software 17,239 11,585 44,469 33,585 Software maintenance 4,570 6,826 16,110 20,400 Professional services 2,973 1,589 8,830 5,852 Total software revenue $ 38,153 $ 35,928 $ 106,257 $ 116,931
- 反证 [ev_014cc2546d580275](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): we expect revenue to decline in the near-term as the transition progresses
- 反证 [ev_ee428f00959eb534](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000076/sdgr-20260930.htm) (primary-document): our sales cycles can be as long as nine to twelve months or longer. Further, the length of time that potential customers devote to their testing and evaluation, contract negotiation, and budgeting processes varies significantly, depending on the size of the organization and the nature of their needs
- 反证 [ev_8edd40076feeed26](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000076/sdgr-20260930.htm) (primary-document): Our customers have no obligation to renew their product licenses or subscriptions for our software solutions after the license term expires, which is typically after one year, and many of our contracts may be terminated or reduced in scope either immediately or upon notice.
- 反证 [ev_ff31316740135418](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000076/sdgr-20260930.htm) (primary-document): we are facing increasing competition from companies utilizing AI and other computational approaches for drug discovery. Some of these competitors are involved in drug discovery themselves and/or with partners, and others develop software or other tools utilizing AI which can be used, directly or indirectly, in drug discovery. To the extent these other AI approaches to drug discovery prove to be successful, or more successful, than our approach, the demand for our platform could be adversely affected
- 反证 [ev_549ef7531fa0b865](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): Our software solutions face competition from competitors in the business of selling or providing simulation and modeling software to biopharmaceutical companies. These competitors include BIOVIA, a brand of Dassault Systèmes SE, or BIOVIA, Chemical Computing Group (US) Inc., Cresset Biomolecular Discovery Limited, Cadence Design Systems, Inc., Optibrium Limited, Cyrus Biotechnology, Inc., Molsoft LLC, Insilico Medicine, Inc., Iktos, XtalPi Inc., AbCellera, Inductive Bio, Inc., Chemaxon, Revvity, Inc., and Simulations Plus, Inc.
- 反证 [ev_d46f01c353b17d7e](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): obtaining broad patents in the United States covering software innovations is more challenging than before. In addition to increasing uncertainty with regard to our ability to obtain future patents, this combination of events has created uncertainty with respect to the value of patents, once obtained.
- 反证 [ev_3ba3c8cf039a248c](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): United States $ 152,963 $ 114,869 $ 161,961 APAC 26,181 25,802 24,569 EMEA 75,164 65,650 29,135 Rest of World 1,561 1,218 1,001 $ 255,869 $ 207,539 $ 216,666
- 反证 [ev_0bc36fb180d952fb](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): We have sales operations in the United States, Europe, Japan, India, and South Korea and we also have established distribution channels in other important markets, including China.
- 反证 [ev_35931d1609d25f2b](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000076/sdgr-20260930.htm) (primary-document): the U.S. and China reached a one-year agreement with an expiration of November 10, 2026, that includes the continued suspension of the heightened reciprocal tariffs on China and delayed enforcement of new U.S. export rules targeting affiliates of blacklisted firms
- 反证 [ev_bcfa5e5302fca856](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000076/sdgr-20260930.htm) (primary-document): Sustained uncertainty about, or the further escalation of, trade and political tensions between the United States and China could result in a disadvantageous research and manufacturing environment in China, particularly for U.S. based companies, including retaliatory restrictions that hinder or potentially inhibit our ability to rely on CMOs and other service providers that operate in China.
- 证伪条件：软件总营收连续两个季度同比正增长（扭转2026年前九个月同比下滑趋势）
- 证伪条件：两家头部客户（合计占Q3 2026营收35%）中任一客户不续约或大幅缩减合同规模
- 证伪条件：以AI为基础的竞争对手（如Insilico Medicine、XtalPi）在药物发现准确性基准测试中持续优于Schrödinger平台
- 证伪条件：BIOSECURE法案执行导致公司现有中国CMO合作关系中断，药物发现服务收入下滑
- 证伪条件：托管软件向订阅模式的过渡完成后，年化软件ARR未能弥补在途确认收入的缺口（即2027年及以后软件收入仍未恢复增长）
- 证伪条件：美中贸易协议到期（2026年11月10日）后双方关系重新恶化，中国分销渠道收入显著萎缩
- 证伪条件：公司宣布放弃SGR-1505或SGR-3515合作伙伴谈判，药物发现部门收入来源进一步收窄

### management_governance: pass

按 Serenity 规则：领导层连续，且无未结调查或未定继任。2026年4月代理声明（DEF 14A）确认Ramy Farid现任总裁兼CEO、Richie Jain自2025年5月起任CFO均在职；Porges已于2025年9月依协议离职，Jain在其离职前已就任CFO，继任明确；文件中未披露任何政府、监管或董事会调查；两份Form 4仅记录高管按10b5-1计划的常规期权行权及股票出售，不涉及领导层变动。

- 支持 [ev_0d200d33df6084dc](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000026/sdgr-20260427.htm) (primary-document): Dr. Farid is not an independent director under these rules because he is our president and chief executive officer
- 支持 [ev_10b9c301db29aaa0](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000026/sdgr-20260427.htm) (primary-document): Richie Jain , age 42, has served as our executive vice president and chief financial officer and treasurer since May 2025
- 支持 [ev_42f7be69ec5ccacb](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000026/sdgr-20260427.htm) (primary-document): Ramy Farid $730,000 —% 95% (2) 5% 112,500 (3) 56,250 (4) 112,500 (5) Richie Jain $535,000 —% 55% —% 34,250 (3) 17,130 (4) 34,250 (5)
- 支持 [ev_65f8dc571b28d3be](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000026/sdgr-20260427.htm) (primary-document): Richie Jain , age 42, has served as our executive vice president and chief financial officer and treasurer since May 2025 and previously served as our senior vice president, strategic finance and head of corporate and business development from February 2024 to May 2025.
- 支持 [ev_5504a78b26976507](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000026/sdgr-20260427.htm) (primary-document): On September 5, 2025, we entered into the separation agreement with Dr. Porges, which confirms the terms of his separation from the company.
- 支持 [ev_717bcdb21df7d38c](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000026/sdgr-20260427.htm) (primary-document): Geoffrey Porges(6) — — — — — — —

## SGMT · complete

审查记录：`state/serenity-reviews/SGMT-claudecli-f99aab5113fe918fbb1f.json`

### supply_chain_map: unknown

证据显示SGMT依赖第三方制造商生产药物候选品，并与TAPI签订了resmetirom API许可协议，与Ascletis签订了大中华区许可协议。但缺少具体CMO名称、原料药上游供应商及其集中度信息，供应链地图不完整。

- 支持 [ev_24ba6e513c64fd5f](https://www.sec.gov/Archives/edgar/data/1400118/000110465926026140/sgmt-20251231x10k.htm) (primary-document): We do not own or operate manufacturing facilities for the production of clinical or commercial quantities of our drug candidates, and we lack the resources and the capabilities to do so
- 支持 [ev_2729dd6dda61019a](https://www.sec.gov/Archives/edgar/data/1400118/000110465926026140/sgmt-20251231x10k.htm) (primary-document): the Company entered into a license agreement that became effective in February 2019 with Ascletis BioScience Co. Ltd. (Ascletis), a subsidiary of Ascletis Pharma Inc.
- 缺口：具体CMO（合同生产商）名称
- 缺口：denifanstat原料药上游供应商及其地理分布
- 缺口：供应商集中度和替代供应商信息
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现SGMT已建立自有生产设施
- 证伪条件：发现CMO供应商已公开披露且高度分散

### chokepoint_evidence: unknown

SGMT是一家临床阶段生物技术公司，其核心资产denifanstat是一种FASN抑制剂，具有差异化作用机制，但没有证据表明其在供应链中占据瓶颈位置。新颖的MOA不等于供应集中或替代壁垒。专利不确定性也被广泛披露。无法确认chokepoint地位。

- 支持 [ev_a0009e44cf99d57a](https://www.sec.gov/Archives/edgar/data/1400118/000119312526408224/d96035dex991.htm) (sec-8k): Our lead molecule, denifanstat, is a novel fatty acid synthase (FASN) inhibitor with a differentiated Unique MOA: FASN Inhibition method of action with the potential to target multiple underserved diseases
- 缺口：FASN抑制剂领域竞争对手数量及市场集中度数据
- 缺口：denifanstat相对于其他MOA的不可替代性证据
- 缺口：供应链节点具体集中度指标
- 证伪条件：发现其他FASN抑制剂已进入后期临床试验
- 证伪条件：发现现有痤疮/MASH治疗完全覆盖denifanstat的目标患者群

### customer_dependency: unknown

Ascletis作为大中华区许可合作伙伴已在中国完成Phase 3试验且NDA已被NMPA受理，构成实质性合作关系。但SGMT尚无商业产品，美国市场尚无终端客户或处方采用数据。TAPI仅为API许可方，非下游客户。

- 支持 [ev_5fb3a3295dc637a1](https://www.sec.gov/Archives/edgar/data/1400118/000119312526408224/d96035dex991.htm) (primary-document): Ascletis announced that the denifanstat NDA for the treatment of moderate to severe acne was accepted by the China NMPA in December 2025
- 缺口：美国市场商业客户或处方采用数据
- 缺口：Ascletis的里程碑付款实际收到情况
- 缺口：任何已确认的分销或商业化合作伙伴
- 缺口：引用不存在或原文无法匹配
- 证伪条件：Ascletis NDA被NMPA拒绝
- 证伪条件：Ascletis终止许可协议

### pure_play: pass

SGMT所有管线均围绕FASN抑制这一核心机制：denifanstat用于痤疮和MASH，TVB-3567用于痤疮和肿瘤，外加denifanstat/resmetirom组合。公司不经营其他非相关业务，属于纯正的FASN抑制剂主题敞口。

- 支持 [ev_5fb3a3295dc637a1](https://www.sec.gov/Archives/edgar/data/1400118/000119312526408224/d96035dex991.htm) (primary-document): Our follow-on FASN inhibitor, TVB 3567, received Investigational New Drug (IND) clearance in March 2025
- 支持 [ev_47d18de6ac8bdaaa](https://www.sec.gov/Archives/edgar/data/1400118/000119312526408224/d96035dex991.htm) (primary-document): Identifying FASN-dependent tumor types for Oncology Solid tumors potential FASN inhibitor development
- 支持 [ev_a0009e44cf99d57a](https://www.sec.gov/Archives/edgar/data/1400118/000119312526408224/d96035dex991.htm) (sec-8k): denifanstat, is a novel fatty acid synthase (FASN) inhibitor with a differentiated Unique MOA: FASN Inhibition method of action with the potential to target multiple underserved diseases
- 证伪条件：公司收购或开发非FASN抑制机制的资产
- 证伪条件：非FASN相关收入占比超过50%

### multi_node_control: unknown

SGMT不拥有生产设施，依赖第三方CMO，也不控制上游原料药供应（resmetirom API通过TAPI许可获得）。公司仅控制IP/临床开发节点，不控制制造或分销等连接的供应链节点。无多节点控制证据。

- 反证 [ev_24ba6e513c64fd5f](https://www.sec.gov/Archives/edgar/data/1400118/000110465926026140/sgmt-20251231x10k.htm) (primary-document): we currently rely, and expect to rely for the foreseeable future, on third-party manufacturers to supply our drug candidates
- 缺口：自有生产或分销能力的证据
- 缺口：对上游供应链节点的控制证据
- 证伪条件：SGMT建立自有生产设施
- 证伪条件：SGMT垂直整合API生产

### earnings_validation: partial

SGMT为preparation阶段Phase 3公司，亏损属预期。公司披露截至2026年6月30日现金为2.576亿美元，包括2026年4月完成的1.75亿美元融资，预计资金可支持运营至2028年及Phase 3读数。XBRL数据较旧（2023年9月）。现金充裕、跑道超过12个月（smallCapContext显示约67个月），满足preparation阶段要求，但2028年的资金预测属于前瞻性声明，非已验证的实际财务结果。

- 支持 [ev_5fb3a3295dc637a1](https://www.sec.gov/Archives/edgar/data/1400118/000119312526408224/d96035dex991.htm) (primary-document): $257.6M cash on hand as of 6/30/2026*, including proceeds from the $175M underwritten offering of Series A Common Stock completed in April 2026, and expected to fund current operations through 2028
- 支持 [ev_f44ac1b8b8ab7f9a](https://data.sec.gov/api/xbrl/companyfacts/CIK0001400118.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 101,842,000 for as of 2023-09-30; form 10-Q filed 2023-11-13
- 缺口：2026年Q3季度10-Q中的最新现金和烧钱率数据
- 缺口：具体的Phase 3试验预算披露
- 证伪条件：最新财报显示现金低于12个月烧钱率
- 证伪条件：意外的大额支出导致跑道大幅缩短

### counter_thesis: unknown

反面论点需考虑：1）临床失败风险——美国Phase 3尚在招募中，结果未知；2）竞争风险——痤疮市场已有异维A酸、抗生素、克拉斯特龙等成熟治疗手段；3）专利不确定性——核心专利2032年到期；4）无商业收入，完全依赖临床成功。正面因素包括中国Phase 3已达所有终点且NDA已受理，以及充足现金（约67个月跑道，financingRisk为false）。但缺乏对估值、替代MOA管线、地缘政治风险的深入分析。

- 支持 [ev_8fea2dcabaf45dda](https://www.sec.gov/Archives/edgar/data/1400118/000119312526408224/d96035dex991.htm) (primary-document): Denifanstat Met All Primary and Secondary Endpoints in Acne Phase 3 Clinical Trial (ASC40-303)
- 支持 [ev_5fb3a3295dc637a1](https://www.sec.gov/Archives/edgar/data/1400118/000119312526408224/d96035dex991.htm) (primary-document): Composition of matter patent expected to expire in 2032; potential PTE to 2037
- 支持 [ev_ab49126c7071d82a](https://clinicaltrials.gov/study/NCT07863193) (clinicaltrials-gov): Phase 3 Study of Denifanstat in Participants With Moderate to Severe Acne (AURORA). Highest listed phase: Phase 3. Overall status: RECRUITING
- 反证 [ev_81e44bbc5892bee4](https://www.sec.gov/Archives/edgar/data/1400118/000110465926026140/sgmt-20251231x10k.htm) (primary-document): The patent position of biotechnology and pharmaceutical companies generally is highly uncertain. No consistent policy regarding the breadth of claims allowed in biotechnology and pharmaceutical patents has emerged to date
- 缺口：具体竞争对手FASN抑制剂管线分析
- 缺口：估值与同类biotech公司的对比
- 缺口：美国FDA审批路径的具体风险评估
- 缺口：中国市场地缘政治风险分析
- 缺口：引用不存在或原文无法匹配
- 证伪条件：美国AURORA Phase 3试验未达主要终点
- 证伪条件：FDA要求额外临床试验或拒绝批准
- 证伪条件：竞争对手推出更有效的FASN抑制剂或类似MOA药物
- 证伪条件：Ascletis中国NDA被NMPA拒绝
- 证伪条件：核心专利被无效化

### management_governance: unknown

公司披露了完整的高管团队，每位成员均有20年以上相关经验。CEO Dave Happel、CFO Thierry Chauche、CMO Andreas Grauer等均已命名。内部控制截至2025年12月31日被评估为有效。公司设有分级董事会和反收购条款。但作为EGC（新兴成长型公司），无独立审计师对内控的鉴证报告。缺少具体董事会成员独立性、高管任期和薪酬结构等详细治理信息。

- 支持 [ev_ae20db26f8dac56b](https://www.sec.gov/Archives/edgar/data/1400118/000119312526408224/d96035dex991.htm) (primary-document): Dave Happel President & CEO Elizabeth Rozek Chief Legal & Administrative Officer >20 years of experience in executive leadership in biotech >20 years of legal experience including executive leadership
- 支持 [ev_55b49a9062fadcf8](https://www.sec.gov/Archives/edgar/data/1400118/000110465926026140/sgmt-20251231x10k.htm) (primary-document): our Chief Executive Officer and our Chief Financial Officer have concluded that as of December 31, 2025 our disclosure controls and procedures were effective to provide reasonable assurance
- 支持 [ev_e4342939c8688417](https://www.sec.gov/Archives/edgar/data/1400118/000110465926026140/sgmt-20251231x10k.htm) (primary-document): division of our board of directors into three classes, serving staggered terms of three years each
- 缺口：董事会成员独立性比例
- 缺口：高管具体任期和离职风险
- 缺口：薪酬结构与激励对齐情况
- 缺口：任何未决调查或诉讼详情
- 缺口：引用不存在或原文无法匹配
- 证伪条件：高管突然离职或继任危机
- 证伪条件：内部控制重大缺陷被发现
- 证伪条件：监管调查或股东诉讼

## SOPH · complete

审查记录：`state/serenity-reviews/SOPH-claude-e0f8541e0193d6321370.json`

### supply_chain_map: pass

按 Serenity 规则：上游投入、公司产品、下游用户均有具体关系的一手证据。图谱：上游依赖微软Azure等云服务商及IDT/Qiagen/NEB等消耗品供应商，以及第三方制造商和七家整合访问实验室；产品为SOPHiA DDM云原生多模态AI分析平台及生物制药应用套件；下游覆盖医院、参考实验室和制药/生物技术/CRO客户。结果方面，2025财年平台收入7490万美元（同比+18%）、分析量增长11%、NDR升至115%均与论点一致；但2025年生物制药收入同比小幅下降70万美元，与论点中"支持生物制药项目"的增长含义不符。

- 支持 [ev_4f864bd7c5cada91](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Our platform production environment currently runs on Microsoft Azure. As our platform architecture is vendor-agnostic, we could readily deploy our solutions onto any cloud infrastructure, as well as on-premise if necessary. We have ongoing research and development projects on all major cloud solution providers, including Microsoft Azure, Amazon Web Services and Google Cloud Platform.
- 支持 [ev_0cc27983787ca261](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): we work with Integrated DNA Technologies (“IDT”), Qiagen, New England Biolabs (“NEB”), Watchmaker Genomics, Inc. and others for consumables and hardware equipment.
- 支持 [ev_9f26d4c4b0a5c369](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Our platform is a cloud-native software platform. To deploy our platform, we rely on cloud-based service providers.
- 支持 [ev_9b07d891647fd746](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): These radiomics features can then be aggregated with genomics, clinical and biological data from the same patient.
- 支持 [ev_cb4cb6716d214edc](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Leveraging both our SOPHiA DDM Platform genomic applications and our customers’ own proprietary data through our AI/ML-powered multimodal analytics capabilities, we help customers solve development complexities and bottlenecks across the biopharma value chain.
- 支持 [ev_a5db6e7859130fde](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): we offer four branded applications: SOPHiA Insights, SOPHiA Trial Match, SOPHiA Awareness and SOPHiA CDx, to address the needs of our biopharmaceutical and biotechnology customers, including diagnostic assay development, clinical trial matching and application, drug and therapeutic design optimization, and diagnostic assay deployment.
- 支持 [ev_d8405732c2b84740](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): We also derive revenue from the sale of licenses for our Alamut suite of genomics mutations interpretation software.
- 支持 [ev_aec9b0b791c82e93](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Our clinical customers include academic and non-academic hospitals (including comprehensive cancer centers and children’s hospitals), and reference and specialty laboratories.
- 支持 [ev_d4ffde5af156767d](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): In the biopharma market, we currently serve three types of customers: pharmaceutical companies, biotechnology companies, and CROs.

### chokepoint_evidence: partial

中立分析层有一定粘性，但同类供应商众多。

- 反证 [ev_89316529114e1993](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): There are a number of healthcare technology companies providing bioinformatics analysis solutions, applications, services, and products

### customer_dependency: pass

按 Serenity 规则：一手文件披露了客户采用或使用。披露的采用证据包括：截至2025年12月31日核心基因组客户528家（2024年472家）、平台分析量391,698次、生物制药客户4家；无合作伙伴公告披露。

- 支持 [ev_e083a50e5bd11226](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Core Genomics Customers 528 472
- 支持 [ev_cafc9fa8448e00a7](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Analysis volume increased to 391,698 in the year ended December 31, 2025 from 352,628 in the year ended December 31, 2024.
- 支持 [ev_201c89314bb9114b](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): We served four biopharma customers accross multiple programs during the fiscal year ended December 31, 2025.
- 支持 [ev_749f3cf370d6d90a](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Net dollar retention increased to 115% as of December 31, 2025 from 104% as of December 31, 2024.

### pure_play: pass

全部业务为临床基因组数据分析平台。

- 支持 [ev_e4677ecd16db9297](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): NGS test kits, sequencers and sample materials from different manufacturers

### multi_node_control: partial

控制分析平台与数据网络，不控制检测与报销环节。

- 缺口：节点控制的一手证据

### earnings_validation: partial

按 Serenity 规则：实际结果有的支持、有的不支持论点。图谱：上游依赖微软Azure等云服务商及IDT/Qiagen/NEB等消耗品供应商，以及第三方制造商和七家整合访问实验室；产品为SOPHiA DDM云原生多模态AI分析平台及生物制药应用套件；下游覆盖医院、参考实验室和制药/生物技术/CRO客户。结果方面，2025财年平台收入7490万美元（同比+18%）、分析量增长11%、NDR升至115%均与论点一致；但2025年生物制药收入同比小幅下降70万美元，与论点中"支持生物制药项目"的增长含义不符。

- 支持 [ev_a206f4802b12b922](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Revenue was $77.3 million for the year ended December 31, 2025, compared to $65.2 million for the year ended December 31, 2024.
- 支持 [ev_f52d1b7aa075b602](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): SOPHiA DDM Platform revenue was $74.9 million for the year ended December 31, 2025 compared to $63.5 million for the year ended December 31, 2024.
- 支持 [ev_025dfbeb93997cac](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Analysis volume increased to 391,698 in the year ended December 31, 2025 from 352,628 in the year ended December 31, 2024. We observed an increase in chargeable analysis volume of 11% for the year ended December 31, 2025, as compared to the year ended December 31, 2024.
- 支持 [ev_6f02b44432974081](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Core Genomics Customers increased to 528 as of December 31, 2025 from 472 as of December 31, 2024.
- 支持 [ev_749f3cf370d6d90a](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Net dollar retention increased to 115% as of December 31, 2025 from 104% as of December 31, 2024.
- 反证 [ev_45e25191b318e5bc](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): partially offset by a slight decrease in biopharma revenue of $0.7 million.
- 缺口：按 Serenity 规则：实际结果有的支持、有的不支持论点

### counter_thesis: pass

按 Serenity 规则：供应、需求、替代、地缘、估值均已检验，有证伪条件和有出处的反证（不代表风险消失）。文件证据表明SOPH的反论已被逐维检验：供应端对Azure存在实质依赖且切换成本高，需求端短期合同结构与报销不确定性削弱营收能见度，替代威胁来自资源雄厚的大型企业，地缘政治层面瑞士→美国关税峰值曾达39%并直接冲击毛利率；上述风险已被识别但尚未消除。

- 反证 [ev_c7da2e0dc2fedb5d](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): we currently use Microsoft Corporation (“Microsoft”) and Microsoft Azure Services for a substantial portion of our computing, storage, data processing, networking and other services
- 反证 [ev_8398d22dd0f0f23f](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Any transition to new cloud providers would be difficult to implement and would cause us to incur significant delays and expense.
- 反证 [ev_354f1607c69c35be](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): We rely, and expect that we will continue to rely, on third parties for the manufacturing and supply of our products offered with our SOPHiA DDM Platform
- 反证 [ev_92ce9d3428415a2c](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): third-party manufacturers may fail to deliver the required commercial quantities of materials on a timely basis and at commercially reasonable prices, and we may be unable to find one or more replacement manufacturers capable of production at a substantially equivalent cost in substantially equivalent volumes and quality on a timely basis
- 反证 [ev_12eb01dd1d6550f5](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Our platform production environment currently runs on Microsoft Azure. As our platform architecture is vendor-agnostic, we could readily deploy our solutions onto any cloud infrastructure
- 反证 [ev_c1d5b89055863b80](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): The majority of the platform revenue is derived from contracts with an original expected length of one year or less.
- 反证 [ev_cb21c1ca4493821b](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Revenues from one customer, a distributor for the Company, represented approximately $ 8.7 million and $ 8.2 million of the Company’s total revenues for the fiscal years ended December 31, 2025 and 2024, respectively.
- 反证 [ev_7d5f6d8ba8644d55](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): It is difficult to predict what CMS, state Medicaid programs, and other third-party payors will decide with respect to coverage and reimbursement for novel platforms, applications, products, and services such as ours.
- 反证 [ev_436635fdba34814b](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): We expect to experience pricing pressures in connection with the sale of any products that we develop due to the trend toward managed healthcare, the increasing influence of health maintenance organizations
- 反证 [ev_d9edf812fa925018](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): We also face competition from companies that have developed software analytics platforms for genomics data, such as Agilent, Fabric Genomics, Illumina, Qiagen Digital Insights, Velsera Inc., Congenica Ltd and Thermo Fisher.
- 反证 [ev_e3e1da4907481437](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): our competitors are likely to develop technology, platforms, applications, products, and services that offer features and functionality similar to ours. Improvements in existing competitive technology, platforms, applications, products, and services or the introduction of new competitive technology, platforms, applications, products, and services may make it more difficult for us to compete for sales, particularly if competitors demonstrate better accuracy, reliability, convenience or effectiveness or price their platforms, applications, products, and services less expensively.
- 反证 [ev_9ad315cc2882d7b8](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): under our license agreements with Normandie Valorisation, Normandie Valorisation controls the prosecution, maintenance and defense of the patents licensed to us pursuant to the agreements.
- 反证 [ev_ac26c8aadccac17b](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): loss of competitive advantage if competitors offer superior or more current solutions
- 反证 [ev_7d39ca325f485598](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): An initial 31% tariff was announced on goods imported into the U.S. from Switzerland, where our headquarters are located, which was subsequently increased to 39% by Executive Order on July 31, 2025. On December 10, 2025 Switzerland announced an agreement with the U.S. to reduce the tariffs to 15% retroactive to November 14, 2025.
- 反证 [ev_268bbfbccd2967ea](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): our sale of bundles to the United States are currently subject to additional costs due to the tariffs, leading to increases in our cost of revenue and decreases in our gross margin if we are unable to fully offset such costs by increasing our prices.
- 反证 [ev_34e5b28bc7cacdbd](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): the majority of our bundles assembled at and shipped from our headquarters in Rolle, Switzerland. While the majority of our revenues are generated from the EMEA region and are not directly impacted by these tariffs
- 反证 [ev_6811ae9c6df0500b](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): we are currently defending against patent infringement claims brought by Guardant Health in multiple jurisdictions
- 证伪条件：美国关税恢复至高于15%的水平，导致美国业务（约占总收入17%）毛利率出现可量化的显著下滑
- 证伪条件：Guardant Health专利诉讼在任一司法管辖区胜诉，法院发出禁令迫使公司停售或实质性修改相关产品
- 证伪条件：EMEA地区平台合同年度续约率下降，收入增长停滞或出现绝对值下滑
- 证伪条件：主要分销商客户（单一客户收入约870万美元，占总收入约11%）流失或大幅削减采购
- 证伪条件：重要竞争对手（如Roche、Illumina）推出精度经同行评审验证更高、价格更低的竞争平台并可量化地抢占市场份额
- 证伪条件：CMS或欧洲主要国家医保机构正式拒绝或限制对SOPHiA DDM Platform的覆盖报销
- 证伪条件：微软Azure发生重大服务中断或终止与公司的合同，导致平台大规模、长时间宕机

### management_governance: partial

按 Serenity 规则：一手材料尚未证明领导层连续。2026年11月的6-K引述Ross Muken为CEO，确认其于2026年7月由总裁升任，CEO继任已命名且完成；CFO George Cardoza仅于2026年3月申报的20-F（信息截至2026年2月15日）中出现，当前通道材料无其11月在任确认，连续性不完整；无调查披露，无悬空继任缺位。

- 支持 [ev_be7b6e3566a0664a](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000350/sophiageneticssaex993q32026.htm) (primary-document): said Ross Muken, Chief Executive Officer of SOPHiA GENETICS
- 支持 [ev_37e44de940fc1a2a](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): George Cardoza Chief Financial Officer 64
- 支持 [ev_a9bc5210ea5a74e1](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): Ages are as of February 15, 2026.
- 支持 [ev_0dca9e8ecc5ed3d1](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000350/sophiageneticssaex991q32026.htm) (primary-document): As announced in January 2026, the Company’s President was promoted to CEO in July 2026 and, from that date, assumed the role of CODM.
- 支持 [ev_be7b6e3566a0664a](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000350/sophiageneticssaex993q32026.htm) (primary-document): said Ross Muken, Chief Executive Officer of SOPHiA GENETICS
- 缺口：CFO George Cardoza 在2026年11月的在任状态——仅见于2026年2月15日的20-F，当前6-K（2026年11月）未确认

## TECX · complete

审查记录：`state/serenity-reviews/TECX-claudecli-9dcec462cf9e76939ca3.json`

### supply_chain_map: unknown

上游依赖关系有具体披露：公司依赖CDMO（尤其是WuXi Biologics作为TX45唯一供应商）进行药物生产，依赖Harvard提供专利许可技术。下游用户为HHT和PH-HFpEF患者群体。但公司处于临床阶段，无商业化产品，下游商业关系尚未建立。

- 支持 [ev_143969005c4b4601](https://www.sec.gov/Archives/edgar/data/1681087/000119312526407823/d20857dex991.htm) (primary-document): HHT is a rare, inherited vascular disorder affecting an estimated 75,000 people in the United States. HHT is the second most common inherited bleeding disorder and a disease for which there are currently no approved therapies
- 缺口：具体原材料供应商名称（除WuXi外）
- 缺口：TX2100的CDMO供应商身份
- 缺口：下游商业分销渠道规划
- 缺口：引用不存在或原文无法匹配
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现公司已建立多元化CDMO供应网络
- 证伪条件：发现下游商业合作伙伴或分销协议

### chokepoint_evidence: unknown

Tectonic是临床阶段生物技术公司，专注于GPCR靶向生物制剂。虽拥有专有GEODe™平台和专利组合，但证据中无供应集中度或替代壁垒的具体数据。公司本身不控制任何物理供应链瓶颈节点，其差异化来自知识产权而非供应稀缺性。

- 支持 [ev_c9f25700f0deb07d](https://www.sec.gov/Archives/edgar/data/1681087/000119312526076793/tecx-20251231.htm) (primary-document): Our patent portfolio includes three patent families relating to Fc-relaxin fusion protein compositions (including TX45) and methods of use thereof, consisting of two granted U.S. patents, three pending U.S. non-provisional applications, and approximately 40 pending foreign applications
- 支持 [ev_c7e7005f4a461142](https://www.sec.gov/Archives/edgar/data/1681087/000119312526076793/tecx-20251231.htm) (primary-document): engineering strategies that stabilize pharmacologically relevant receptor conformations, increase cell surface expression, and enable large-scale purification and formulation in the correct conformation for naïve antibody selection
- 缺口：GPCR生物制剂领域竞争格局数据
- 缺口：GEODe™平台相对竞争对手的具体技术壁垒量化
- 缺口：供应集中度或替代时间的证据
- 证伪条件：发现其他公司拥有类似GPCR工程平台且已进入临床
- 证伪条件：HHT领域出现竞争性在研疗法

### customer_dependency: unknown

公司处于临床阶段，无商业化产品，无任何客户收入或产品采用数据。Harvard许可协议和CDMO关系属于上游供应商关系而非下游客户关系。FDA Fast Track认定表明监管路径支持，但不等同于客户采用。

- 缺口：任何商业客户或合作伙伴的产品采用证据
- 缺口：与医疗机构或支付方的商业安排
- 缺口：任何预购或商业合作协议
- 证伪条件：发现已签署商业分销或合作协议
- 证伪条件：发现大型药企合作开发协议

### pure_play: unknown

公司明确为单一经营分部，专注于GPCR靶向蛋白和抗体的发现与开发。符合纯粹暴露的定义。但无收入可衡量主题收入占比，且GPCR靶向生物制剂与AI医疗的关联性未在证据中体现。

- 支持 [ev_0ef2aa9cb797092c](https://www.sec.gov/Archives/edgar/data/1681087/000119312526407823/d20857dex991.htm) (sec-8k): a clinical stage biotechnology company focused on the discovery and development of therapeutic proteins and antibodies that modulate the activity of G-protein coupled receptors (GPCRs)
- 缺口：收入分部数据（临床阶段无收入）
- 缺口：与AI医疗主题的直接关联性证据
- 缺口：引用不存在或原文无法匹配
- 证伪条件：公司进入与GPCR无关的多元化业务领域

### multi_node_control: unknown

公司拥有GEODe™发现平台、Harvard许可技术、自有专利组合以及多个临床候选药物（TX45、TX2100），但这些属于同一研发管线内的能力，不构成对多个供应链节点的控制。公司依赖外部CDMO进行生产，不拥有制造能力。

- 缺口：公司控制多个相连供应链节点的证据
- 缺口：垂直整合或自有制造能力的证据
- 证伪条件：公司收购CDMO或建立自有生产设施
- 证伪条件：公司整合上游原材料供应能力

### earnings_validation: partial

公司为临床前准备阶段（phase 2），无收入为预期状态。10-K报告截至2025年12月31日现金及等价物为$253,798千美元。smallCapContext显示截至2026-09-30现金$234.7M，月烧钱率$6.09M，跑道约38.6个月，足够资助Phase 1b（2026年底启动）和Phase 2（2027年初启动）试验。无融资风险。但缺乏最近季度的详细费用披露。

- 支持 [ev_e83f5eca5b238104](https://www.sec.gov/Archives/edgar/data/1681087/000119312526076793/tecx-20251231.htm) (primary-document): Cash and cash equivalents $ 253,798 $ 141,239 Restricted cash 1,072 587 Cash, cash equivalents and restricted cash 254,870 141,826
- 支持 [ev_0ef2aa9cb797092c](https://www.sec.gov/Archives/edgar/data/1681087/000119312526407823/d20857dex991.htm) (sec-8k): Company plans to initiate an open-label TX2100 Phase 1b clinical trial in patients with hematologic-support dependent HHT by year-end 2026, and initiate a Phase 2 clinical trial in parallel in patients with moderate-to-severe HHT in early 2027
- 缺口：2026年Q3季度详细损益表数据
- 缺口：临床试验预算明细
- 缺口：未来12-24个月资金需求预估
- 证伪条件：烧钱率突然大幅上升导致跑道缩短至12个月以下
- 证伪条件：意外的大额一次性支出

### counter_thesis: partial

已识别多个风险：（1）WuXi Biologics为TX45唯一供应来源，存在供应链单点故障风险；（2）临床试验失败风险——Phase 1a仅证明安全性，尚无疗效数据；（3）HHT为罕见病（美国约75,000患者），市场规模有限；（4）无已批准产品，所有价值依赖临床成功。跑道充足（>12个月），融资风险低，无需标注股权稀释为近期反论点。但缺乏竞争对手具体数据和估值分析。

- 支持 [ev_ad3d375f92efb3a5](https://www.sec.gov/Archives/edgar/data/1681087/000119312526076793/tecx-20251231.htm) (primary-document): We currently have a sole source relationship with WuXi Biologics for our supply of TX45. If there should be any disruption in such supply arrangement or the supply arrangement with our CDMO for TX2100, including any adverse events affecting our sole supplier for TX45, WuXi Biologics, it could have a negative effect on the clinical development of our product candidates
- 支持 [ev_143969005c4b4601](https://www.sec.gov/Archives/edgar/data/1681087/000119312526407823/d20857dex991.htm) (primary-document): HHT is a rare, inherited vascular disorder affecting an estimated 75,000 people in the United States
- 支持 [ev_25d53e80328b1cf9](https://www.sec.gov/Archives/edgar/data/1681087/000119312526407823/d20857dex991.htm) (primary-document): TX2100 is designed as a selective APJ antagonist intended to inhibit disease-associated angiogenic signaling with the goal of providing a more favorable safety profile compared to less selective anti-angiogenic approaches
- 缺口：HHT领域在研竞品的具体管线数据
- 缺口：公司估值与同类临床阶段罕见病公司的比较
- 缺口：WuXi Biologics地缘政治风险的具体评估（中美关系）
- 缺口：Phase 2疗效失败的基准概率
- 证伪条件：TX45 Phase 2试验未达主要终点
- 证伪条件：TX2100 Phase 1b出现严重安全性信号
- 证伪条件：WuXi Biologics因监管原因无法继续供应
- 证伪条件：竞争对手在HHT获得突破性疗法认定或批准
- 证伪条件：现金跑道因试验扩展意外缩短至12个月以下

### management_governance: partial

证据显示：（1）管理层评估截至2025年12月31日内部控制有效；（2）CEO为Alise Reicin医学博士，CMO为Marcella K. Ruddy医学博士；（3）董事Peter McNamara于2025年11月14日采纳10b5-1交易计划（出售最多35,102股）。未发现公开调查或继任危机。但缺乏董事会完整构成、独立董事比例及高管薪酬等详细治理信息。

- 支持 [ev_ae372927601049c0](https://www.sec.gov/Archives/edgar/data/1681087/000119312526076793/tecx-20251231.htm) (primary-document): Based on this assessment, management concluded that our internal control over financial reporting was effective as of December 31, 2025
- 支持 [ev_ae372927601049c0](https://www.sec.gov/Archives/edgar/data/1681087/000119312526076793/tecx-20251231.htm) (primary-document): On November 14, 2025 , Peter McNamara , a member of our Board of Directors , adopted a Rule 10b5-1 trading plan that provides for the sale of up to 35,102 shares of common stock from the exercise of vested stock options
- 支持 [ev_0ef2aa9cb797092c](https://www.sec.gov/Archives/edgar/data/1681087/000119312526407823/d20857dex991.htm) (sec-8k): said Alise Reicin, M.D., President and Chief Executive Officer of Tectonic Therapeutic
- 缺口：董事会完整构成及独立董事比例
- 缺口：高管薪酬结构及与绩效挂钩情况
- 缺口：审计委员会和薪酬委员会详情
- 缺口：关键人物流失风险评估
- 证伪条件：发现未披露的内部调查或SEC执法行动
- 证伪条件：CEO或CMO突然离职
- 证伪条件：内部控制重大缺陷披露

## TEM · complete

审查记录：`state/serenity-reviews/TEM-claude-aaa15fe83f865651bc57.json`

### supply_chain_map: pass

上游测序仪唯一来源 Illumina、云服务 AWS 与 Google；下游医疗机构网络。

- 支持 [ev_716a5c0bca825fb9](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): We rely on Illumina as the sole supplier of the sequencers
- 支持 [ev_3d58eb3c35da4ae7](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): we have cloud agreements with both AWS and Google.
- 支持 [ev_da8219eb1db0ccd1](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): create a network of healthcare institutions that supply us with complex multimodal data

### chokepoint_evidence: partial

数据规模领先，但处在 Illumina 瓶颈下游，且面临 FMI、Guardant 等同类竞争。

- 支持 [ev_fa3c0e570c458eb1](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): we have become one of the largest sequences of cancer patients in the United States in just a few years.
- 反证 [ev_60163a1b9066ec96](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): more in line with other NGS providers who have adopted similar strategies, such as FMI and Guardant.

### customer_dependency: pass

按 Serenity 规则：一手文件披露了客户采用或使用。通道中存在大量已披露的产品实际使用证据：截至2026年9月，逾9,000名医生及250家以上生物科技/制药公司已付费使用，多条产品线收入持续增长，非可撤销多年合同余额达5.14亿美元；同时披露了AstraZeneca主服务协议及Personalis商业化合作协议作为合作公告。

- 支持 [ev_a52cc11f1b7c6953](https://www.sec.gov/Archives/edgar/data/1717115/000119312526442624/tem-20260930.htm) (primary-document): Since our inception, our offerings have been used by more than 9,000 physicians and we have worked with over 250 biotech companies, as well as 19 of the 20 largest public pharmaceutical companies based on 2025 revenue
- 支持 [ev_d2e5642b282e0dfe](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): The Company recognized revenue from Insights products of $ 257.7 million, $ 186.8 million and $ 117.6 million for the years ended December 31, 2025, 2024 and 2023, respectively.
- 支持 [ev_274c898ea064faaf](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): The Company recognized revenue from Trials products of $ 38.5 million, $ 42.4 million and $ 45.6 million for the years ended December 31, 2025, 2024 and 2023, respectively.
- 支持 [ev_3588bef4a6d1339a](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): The Company recognized revenue from Next of $ 20.1 million, $ 12.3 million and $ 5.1 million for the years ended December 31, 2025, 2024 and 2023, respectively.
- 支持 [ev_b9447509c5380c65](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): The Company’s remaining performance obligations related to multi-year contracts was $ 348.1 million as of December 31, 2025
- 支持 [ev_ae30055a56ae2fb2](https://www.sec.gov/Archives/edgar/data/1717115/000119312526442624/tem-20260930.htm) (primary-document): The Company recognized revenue from Insights products of $ 88.9 million and $ 69.0 million for the three months ended September 30, 2026 and 2025, respectively and $ 237.9 million and $ 175.7 million for the nine months ended September 30, 2026 and 2025, respectively.
- 支持 [ev_195ab74679ce578c](https://www.sec.gov/Archives/edgar/data/1717115/000119312526442624/tem-20260930.htm) (primary-document): The Company recognized revenue from Next of $ 9.6 million and $ 3.2 million for the three months ended September 30, 2026 and 2025, respectively and $ 21.6 million and $ 11.6 million for the nine months ended September 30, 2026 and 2025, respectively.
- 支持 [ev_37b6b91572196634](https://www.sec.gov/Archives/edgar/data/1717115/000119312526442624/tem-20260930.htm) (primary-document): The Company recognized Diagnostics revenue for direct bill orders of $ 31.0 million and $ 17.5 million for the three months ended September 30, 2026 and 2025, respectively. The Company recognized Diagnostics revenue for direct bill orders of $ 77.7 million and $ 49.9 million for the nine months ended September 30, 2026 and 2025, respectively.
- 支持 [ev_b9b1108cc7b76675](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): in conjunction with the signing of a November 2021 Master Services Agreement (“the MSA”) with customer AstraZeneca AB (“AstraZeneca”)
- 支持 [ev_ee9200ac7c7bedc8](https://www.sec.gov/Archives/edgar/data/1717115/000119312526442624/tem-20260930.htm) (primary-document): In November 2023, the Company entered into a Commercialization and Reference Laboratory Agreement with Personalis, which was subsequently amended in August 2024 and July 2025. The Company agreed to pay up to $ 12.0 million to Personalis over three years as certain milestones are met, all of which has been paid as of July 2025.

### pure_play: partial

约四分之三收入来自诊断检测，AI 是赋能层而非全部业务。

- 缺口：按统一口径的 AI 收入占比

### multi_node_control: pass

同时控制检测实验室、数据网络与数据授权。

- 支持 [ev_da8219eb1db0ccd1](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): create a network of healthcare institutions that supply us with complex multimodal data
- 支持 [ev_6af2a53068230a8a](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): Pathos will pay us data license fees of $200 million over a three-year period,

### earnings_validation: pass

Q3 2026 总收入 4.115 亿美元，同比增长 23%（季报原文），增长来自肿瘤与遗传检测量和数据交付。

- 支持 [ev_cba6f53043f47e8e](https://www.sec.gov/Archives/edgar/data/1717115/000119312526442624/tem-20260930.htm) (primary-document): Total net revenue $ 411,537 $ 334,206 $ 1,142,139 $ 904,578
- 支持 [ev_85a6aff966b8b9c0](https://www.sec.gov/Archives/edgar/data/1717115/000119312526442624/tem-20260930.htm) (primary-document): was due to increased volume of clinical oncology and hereditary tests performed in Diagnostics and increased data deliveries in our Data and applications product line

### counter_thesis: pass

按 Serenity 规则：供应、需求、替代、地缘、估值均已检验，有证伪条件和有出处的反证（不代表风险消失）。文件中可提取的反论证据集中于三点：Illumina单一供应商集中度极高（供给侧脆弱性）、付款率不足六成且政府正主动压价（需求侧不确定）、多家资金充裕的竞争者已存在（替代威胁）；地缘政治风险目前主要体现在美国国内政策层面，国际收入占比尚可忽略。

- 反证 [ev_49eea2d56f85a914](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): We rely on Illumina as the sole supplier of the sequencers and as the sole provider of maintenance and repair services for these sequencers. Any disruption in operations of Illumina or other sole or limited suppliers or termination or suspension of our relationships with them could materially and adversely impact our supply chain and laboratory operations of our diagnostic testing business and thus our ability to conduct our business and generate revenue.
- 反证 [ev_9392ae83e3a27574](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): Purchases from this supplier accounted for approximately 33%, 39% and 33% of total vendor payments for the years ended December 31, 2025, 2024 and 2023, respectively.
- 反证 [ev_1578eaba9725d715](https://www.sec.gov/Archives/edgar/data/1717115/000119312526442624/tem-20260930.htm) (primary-document): the announcement of substantial new tariffs and other restrictive trade policies, to the extent such current and future tariffs apply to hardware, networking infrastructure or other technology infrastructure used by us or our third-party vendors, could raise costs, constrain supply or affect service reliability.
- 反证 [ev_67beadc84003522a](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): As of December 31, 2025, we had received payment on approximately 55% of our clinical oncology next generation sequencing, or NGS, tests and 50% of our hereditary tests across all payers performed from January 1, 2023 through December 31, 2024.
- 反证 [ev_2f01388ccb7ad046](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): We believe it may take several years to achieve broad coverage and adequate contracted reimbursement with a majority of payers for our tests. However, coverage policies and third-party reimbursement rates may change at any time.
- 反证 [ev_3ee350736b1adceb](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): Such actions and policies may, among other things, significantly reduce U.S. medical device prices, potentially impacting manufacturers’ global pricing strategies and profitability, while increasing their operational costs and compliance risks.
- 反证 [ev_5a05ebf5c8e899b3](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): Payers may resist reimbursement for our tests in favor of less expensive tests, require pre-authorization for our tests, or impose additional pricing pressure on and substantial administrative burden for reimbursement for our tests.
- 反证 [ev_f0e44e4c1da375cf](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): Our competitors with respect to our Applications products include Roche Holdings, Inc., Caris Life Sciences, Guardant Health, Inc., Illumina, Inc., and others, with respect to our TO test, and Myriad Genetics, Inc., Caris Life Sciences, and others, with respect to our HRD test.
- 反证 [ev_ee2a5271ecf0957f](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): Some of our competitors and potential competitors may have longer operating histories; larger customer bases; greater brand recognition and market penetration; substantially greater financial, technological and research and development resources and selling and marketing capabilities; and more experience dealing with third-party payers.
- 反证 [ev_bcb276e46555e524](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): Increased competition and cost-saving initiatives on the part of governmental entities and other third-party payers are likely to result in pricing pressures, which could harm our sales or ability to gain market share.
- 反证 [ev_379ddc5d525fa9b9](https://www.sec.gov/Archives/edgar/data/1717115/000119312526442624/tem-20260930.htm) (primary-document): The majority of our revenue is generated in the United States. Through September 30, 2026, we have generated an insignificant amount of revenues denominated in foreign currencies.
- 反证 [ev_56d2e97a0f62a708](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): The current administration is pursuing policies to reduce regulations and expenditures across government agencies including at the Department of Health and Human Services, the FDA, CMS and related agencies.
- 反证 [ev_201cefed70ab49ef](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): In many countries outside of the United States, reimbursement systems vary significantly by country and by region within some countries, and reimbursement approvals must be obtained on a country-by-country basis and various coverage, pricing and reimbursement approvals are required for our tests to be available to patients in significant volume.
- 证伪条件：Illumina中断供货或大幅涨价，导致Tempus测序产能明显下降
- 证伪条件：CMS或主要商业保险方大幅削减NGS检测报销价格（低于当前$1,600均值）或撤销覆盖
- 证伪条件：付款率（当前肿瘤NGS约55%）在未来报告期出现下滑而非上升
- 证伪条件：Guardant Health、Caris Life Sciences或Myriad Genetics在肿瘤NGS市场赢得规模性份额并显著压低市场价格
- 证伪条件：Data & applications业务净收入留存率（NRR）跌破100%，显示制药客户不续约
- 证伪条件：美国政府通过立法明确削减基因组诊断的Medicare报销额度

### management_governance: pass

按 Serenity 规则：领导层连续，且无未结调查或未定继任。本批通道（四份Form 4及DEF 14A）显示：Lefkofsky仍以"CEO and Chairman"身份提交Form 4（截至2026年11月20日），Rogers经DEF 14A确认持续担任CFO；通道内无任何开放调查或未定继任披露。结构性治理风险包括：Lefkofsky集CEO、董事长、10%以上股东于一身，以及其对346 Long LLC等多个关联实体的控制关系。

- 支持 [ev_bc36a257f372ab47](https://www.sec.gov/Archives/edgar/data/1717115/000202463026000029/xslF345X06/form4-11192026_061107.xml) (primary-document): Chief Financial Officer
- 支持 [ev_a61c31f55632e4a9](https://www.sec.gov/Archives/edgar/data/1717115/000119312526145528/d23945ddef14a.htm) (primary-document): Eric Lefkofsky 56 Chief Executive Officer, Founder and Director
- 支持 [ev_7378b22ab04e98a3](https://www.sec.gov/Archives/edgar/data/1717115/000119312526145528/d23945ddef14a.htm) (primary-document): James Rogers 40 Chief Financial Officer
- 支持 [ev_bd6ff1cb922d867e](https://www.sec.gov/Archives/edgar/data/1717115/000119312526145528/d23945ddef14a.htm) (primary-document): James Rogers has served as our Chief Financial Officer since April 2021.
- 支持 [ev_7fd000fd7fc4eff7](https://www.sec.gov/Archives/edgar/data/1717115/000119312526145528/d23945ddef14a.htm) (primary-document): Each executive officer serves at the discretion of our Board and holds office until the executive officer’s successor is duly elected and qualified or until the executive officer’s earlier resignation or removal.

## TLX · complete

审查记录：`state/serenity-reviews/TLX-claudecli-2b80e066dfbf958d0732.json`

### supply_chain_map: partial

XBRL元数据显示三个运营分部（Precision Medicine、Therapeutics、Manufacturing Solutions）及成本类别（RadiopharmacyOperations、SupplyChainCosts），可推断公司处于放射性药物供应链中。但证据中缺乏叙述性文本，无法具体识别上游放射性同位素供应商、CDMO关系或下游医院/肿瘤中心客户。新闻标题提及ITM合并和Pixclara批准，暗示上游整合意图，但标题级信息不足以构建完整供应链图。

- 支持 [ev_3ea9c54d65d48e54](https://www.sec.gov/Archives/edgar/data/2007191/000162828026009943/tlx-20251231.htm) (primary-document): tlx:PrecisionMedicineMember ifrs-full:OperatingSegmentsMember
- 支持 [ev_3ea9c54d65d48e54](https://www.sec.gov/Archives/edgar/data/2007191/000162828026009943/tlx-20251231.htm) (primary-document): tlx:TherapeuticsMember ifrs-full:OperatingSegmentsMember
- 支持 [ev_3ea9c54d65d48e54](https://www.sec.gov/Archives/edgar/data/2007191/000162828026009943/tlx-20251231.htm) (primary-document): tlx:ManufacturingSolutionsMember ifrs-full:OperatingSegmentsMember
- 支持 [ev_54197b5332b2358f](https://www.sec.gov/Archives/edgar/data/2007191/000162828026009943/tlx-20251231.htm) (primary-document): tlx:RadiopharmacyOperationsMember 2025-01-01 2025-12-31
- 支持 [ev_54197b5332b2358f](https://www.sec.gov/Archives/edgar/data/2007191/000162828026009943/tlx-20251231.htm) (primary-document): tlx:SupplyChainCostsMember 2025-01-01 2025-12-31
- 缺口：上游放射性同位素（如Lu-177、Ac-225）供应商名称及集中度
- 缺口：下游客户（医院、肿瘤中心）的具体名称和地理分布
- 缺口：CDMO/合同制造商关系的叙述性披露
- 缺口：20-F叙述部分（非XBRL元数据）的供应链描述
- 证伪条件：若20-F叙述部分披露了多元化同位素供应来源，则供应链瓶颈假设不成立
- 证伪条件：若制造分部主要为内部服务而非外部客户，则供应链图需修正

### chokepoint_evidence: unknown

证据中没有任何段落描述Telix在放射性药物供应链中拥有供应集中度优势或替代壁垒。XBRL元数据仅显示分部结构，不涉及市场份额、竞争格局或关键同位素供应瓶颈。新闻标题提及ITM合并可能暗示同位素供应整合，但标题信息不足以证明瓶颈控制。放射性药物领域的潜在瓶颈（如Ac-225供应稀缺）需要具体证据支持。

- 缺口：公司在关键放射性同位素（Lu-177、Ac-225等）供应链中的市场份额数据
- 缺口：替代供应商的可用性及切换成本分析
- 缺口：放射性药物生产设施的许可证壁垒和监管护城河证据
- 缺口：与竞争对手（Novartis、Lantheus等）的差异化说明
- 证伪条件：若Lu-177和其他关键同位素有多个供应商，则无瓶颈
- 证伪条件：若Novartis等大型药企已建立完整放射性药物产能，则Telix不构成供应链瓶颈

### customer_dependency: unknown

证据中没有披露任何具体客户名称、采购协议或设计锁定关系。XBRL元数据显示地理收入分布（US、CN、AU及其他国家），但无客户集中度数据。Precision Medicine分部有Commercial和PreCommercial产品分类，说明存在商业化产品销售，但无法确认具体医院系统或分销网络的依赖关系。

- 支持 [ev_0e71a6af1995c937](https://www.sec.gov/Archives/edgar/data/2007191/000162828026009943/tlx-20251231.htm) (primary-document): tlx:PrecisionMedicineMember tlx:CommercialMember 2025-01-01 2025-12-31
- 缺口：前十大客户名称及收入占比
- 缺口：关键分销协议或医院系统合作披露
- 缺口：Illuccix（前列腺癌成像）的具体采用率和覆盖医院数量
- 缺口：保险报销覆盖范围及CMS编码状态
- 证伪条件：若收入高度依赖单一分销商或少数医院系统，则存在集中度风险
- 证伪条件：若保险报销政策变化导致客户流失，则依赖关系脆弱

### pure_play: partial

XBRL分部结构显示三个运营分部均与放射性药物相关：Precision Medicine（诊断成像）、Therapeutics（治疗）、Manufacturing Solutions（生产）。新闻标题确认公司为"Radiopharmaceutical Group"。这表明高度主题集中，但缺乏各分部的具体收入金额和占比数据，无法量化纯粹度。

- 支持 [ev_3ea9c54d65d48e54](https://www.sec.gov/Archives/edgar/data/2007191/000162828026009943/tlx-20251231.htm) (primary-document): tlx:PrecisionMedicineMember ifrs-full:OperatingSegmentsMember 2025-01-01 2025-12-31
- 支持 [ev_3ea9c54d65d48e54](https://www.sec.gov/Archives/edgar/data/2007191/000162828026009943/tlx-20251231.htm) (primary-document): tlx:ManufacturingSolutionsMember ifrs-full:OperatingSegmentsMember 2025-01-01 2025-12-31
- 支持 [ev_9825bf2b8a336144](https://news.google.com/rss/articles/CBMi5wFBVV95cUxNRmYyZktMUnVZVHpHUnNIaTNqY3RoYkRnMDJ4QkpxYklEd1VmZF9MZXQ2eVBWSG5KMnl1NEw3cUxaWVQ5bl82VmtZUWhHUjV6TGcwMU1MdnhBaGtkenY1UnV1VWt2dnkwYWJtZ3dEQUlrdDdoQk0tYzB1Ull2SUs3Q0JQM2Q1SVh5MllFTHdrVkc4TjVqQWN3TTlSNm1jdGlGeWxkZ0hwYTc1NTNOamI4a3dRSy16enBzOUdRODR6WGtsQUhseVM4bFJBcDhnelQwcnJkS1BmUWVwcjF0enZoZ0IyYTg0TjA?oc=5) (news-feed): ITM Merger and Pixclara Approval Mean for the ASX 200 Radiopharmaceutical Group
- 支持 [ev_fcb8bc221d05828c](https://news.google.com/rss/articles/CBMigwFBVV95cUxPc1BzZkZuWXo4bjd4cFhUcVMzdzZBYzRtLTBVSVdPM29ORGotNjBwNm1reXhUa21GaXFLWlZrZUhfQ2dmQlhiWG1OazV0TVNJQm1XNU10WTFqSzZ2M09qd0c1M0t4LU5La3NiN09NVmZZdnp0TWY2dVZQclN5SUdxMlZ3TQ?oc=5) (news-feed): Imaging Built the Business. Can Therapies Drive the Next Leg of Growth
- 缺口：各分部具体收入金额和占比
- 缺口：非放射性药物业务（如果有）的收入贡献
- 缺口：Manufacturing Solutions分部是否有外部第三方客户收入
- 证伪条件：若Manufacturing Solutions主要服务外部非放射性药物客户，则纯粹度降低
- 证伪条件：若收购ITM后业务范围显著扩展至非核心领域

### multi_node_control: partial

分部结构暗示Telix跨越诊断成像（Precision Medicine）、治疗（Therapeutics）和制造（Manufacturing Solutions）三个节点，这在放射性药物供应链中构成上下游连接。但XBRL元数据不足以证明这些节点之间存在真正的垂直整合控制，而非仅仅是多条独立产品线。需要叙述性证据说明制造分部如何为诊断和治疗分部提供内部供应。

- 支持 [ev_3ea9c54d65d48e54](https://www.sec.gov/Archives/edgar/data/2007191/000162828026009943/tlx-20251231.htm) (primary-document): ifrs-full:EliminationOfIntersegmentAmountsMember 2025-01-01 2025-12-31
- 支持 [ev_54197b5332b2358f](https://www.sec.gov/Archives/edgar/data/2007191/000162828026009943/tlx-20251231.htm) (primary-document): tlx:GlobalManufacturingCostsMember 2025-01-01 2025-12-31
- 缺口：分部间交易金额及内部供应链关系的叙述性说明
- 缺口：制造设施是否自主生产关键同位素或仅进行药物合成
- 缺口：ITM合并是否赋予公司上游同位素生产能力
- 缺口：诊断→治疗theranostic平台的具体整合证据
- 证伪条件：若制造分部仅为合同加工而非战略性供应链节点
- 证伪条件：若关键同位素仍完全依赖外部采购，则垂直整合有限

### earnings_validation: partial

证据确认Q3 2026财务业绩已于2026年10月21日发布（6-K报告），但附件中未包含实际财务数据（收入、利润、毛利率等）。XBRL元数据涵盖FY2023-2025期间，但仅为标签和日期，无数值。因此可确认公司有定期财务报告，但无法验证具体财务指标是否支持投资论点。

- 支持 [ev_26cc387a8f0ce546](https://www.sec.gov/Archives/edgar/data/2007191/000162828026066581/q32026resultsannouncement.htm) (primary-document): Telix Reports Third Quarter 2026 Financial Performance
- 支持 [ev_7d8d96a98eab4ff1](https://news.google.com/rss/articles/CBMi_gFBVV95cUxNN0JPRlN3d2tLbWEtQm9Wa2RuOHdkQ0EyNkJQaWMteDE0UFY3Qm01WjRjNGx6czg1TzlBTVdSZnpXVEIxSTJkcDMzTWR6dkY3MHRqYnJzcDJROFBpdWdPbldKaVN4TkF2UnJ0Wl96cWpEYUdRcnFKSWlDbkF2V3NQaHp3aHJON01QOGpnbzhfODlqZTNuUkFiSlJOT19KcHQxel83WFBQLTdCVWxJdGtpR196YWdHa0pDNEpOVTNoblV2UjRXbHByX0s5RndEdjROWF9MejREbXR0cTZFQUVkWnY0cHNrQmVaTkpKOWR0ZFBkNTNuSURHY0tTekowQQ?oc=5) (news-feed): Consensus Price Target of $20.50 According to Brokerages
- 缺口：FY2025或Q3 2026的实际收入、净利润/亏损数据
- 缺口：各分部收入增长率和毛利率趋势
- 缺口：现金余额和烧钱率（对于仍在亏损的生物制药公司尤为关键）
- 缺口：Illuccix商业化收入的具体数字和增长轨迹
- 证伪条件：若公司仍在大幅亏损且现金跑道不足，则财务验证失败
- 证伪条件：若收入增长停滞或低于市场预期

### counter_thesis: partial

可从证据中识别部分风险：公司正在进行大型并购（ITM合并），存在整合风险；有Phase 2和Phase 3临床试验，存在临床失败风险；地理收入涉及中国市场，存在地缘政治风险。但证据不足以全面压力测试供应、需求、替代、地缘政治和估值五个维度。新闻标题暗示竞争格局（Clarity Pharmaceuticals、Racura Oncology），但无详细分析。

- 支持 [ev_0e71a6af1995c937](https://www.sec.gov/Archives/edgar/data/2007191/000162828026009943/tlx-20251231.htm) (primary-document): tlx:TherapeuticsMember tlx:Phase3Member 2025-01-01 2025-12-31
- 支持 [ev_0e71a6af1995c937](https://www.sec.gov/Archives/edgar/data/2007191/000162828026009943/tlx-20251231.htm) (primary-document): tlx:TherapeuticsMember tlx:EarlyStageClinicalCandidatesMember 2025-01-01 2025-12-31
- 支持 [ev_e44d0e9003203f96](https://www.sec.gov/Archives/edgar/data/2007191/000162828026009943/tlx-20251231.htm) (primary-document): tlx:ZircaixMember tlx:PrecisionMedicineMember tlx:PreCommercialMember
- 支持 [ev_c68c3443a0c7def1](https://news.google.com/rss/articles/CBMiogJBVV95cUxPbFRuQ0xSYUU2UGxnWGhsSVNlUGxFMmxKVDM2R1l6SUpZX05IdUhpQVN4VXd6MVZERER4MXFkdDliN2lLOVZrWmFqeUlWRDNrM0E2TVRxak1mb3k2dTRkdWkwWE5aOXRyaXNfUDduWnVwNExkd1R4blB6WjR2OFFUdTFSU3J0NkxaNFN3QndKQlZOZUlwWEd5WUl3TVpYT1dNdXNGUzl5YWF6S3VXcmRRVEVpWl9PaFpOd0NOX1AzUUlPQjdidUtKNW9DeXdPZUJ1czRpbV9mQVF0QUdZX2VYYi10cGh4NGl3OU9EekJKb3pJSXRhSHIzQnU0VjRjT01wVjh3OEZDSEhSbV9NWWsyRUlEaGI1U3plUUZGc1Buc1RfZw?oc=5) (news-feed): Can Telix Pharmaceuticals (ASX:TLX), Clarity Pharmaceuticals (ASX:CU6), and Racura Oncology (ASX:RAC)
- 反证 [ev_9825bf2b8a336144](https://news.google.com/rss/articles/CBMi5wFBVV95cUxNRmYyZktMUnVZVHpHUnNIaTNqY3RoYkRnMDJ4QkpxYklEd1VmZF9MZXQ2eVBWSG5KMnl1NEw3cUxaWVQ5bl82VmtZUWhHUjV6TGcwMU1MdnhBaGtkenY1UnV1VWt2dnkwYWJtZ3dEQUlrdDdoQk0tYzB1Ull2SUs3Q0JQM2Q1SVh5MllFTHdrVkc4TjVqQWN3TTlSNm1jdGlGeWxkZ0hwYTc1NTNOamI4a3dRSy16enBzOUdRODR6WGtsQUhseVM4bFJBcDhnelQwcnJkS1BmUWVwcjF0enZoZ0IyYTg0TjA?oc=5) (news-feed): ITM Merger and Pixclara Approval Mean for the ASX 200 Radiopharmaceutical Group
- 缺口：Novartis Pluvicto等竞争产品的市场份额对比
- 缺口：关键同位素供应中断风险的详细分析
- 缺口：ITM合并的财务条款和整合风险评估
- 缺口：估值倍数与同行对比（Lantheus、Novartis放射性药物业务）
- 缺口：监管风险：FDA/EMA审批失败的历史概率
- 证伪条件：Novartis等大型药企加速放射性药物布局，压缩Telix市场空间
- 证伪条件：Phase 3临床试验失败导致治疗管线价值归零
- 证伪条件：ITM合并整合不利导致运营中断和现金消耗加速
- 证伪条件：关键同位素（如Ac-225）供应短缺限制产能扩张
- 证伪条件：中国市场监管政策变化影响收入
- 证伪条件：$3.1B市值对于仍在证明治疗业务的公司可能偏高

### management_governance: unknown

证据仅显示Group General Counsel Christian Krautkramer签署了多份6-K报告，以及2026年10月30日发布了股东大会通知。缺乏CEO、CFO等关键管理层信息，以及董事会构成、薪酬结构和治理实践的披露。股东大会通知的存在表明基本治理程序在运行，但无法评估领导层连续性或治理质量。

- 支持 [ev_26cc387a8f0ce546](https://www.sec.gov/Archives/edgar/data/2007191/000162828026066581/q32026resultsannouncement.htm) (primary-document): By: /s/ Christian Krautkramer Name: Christian Krautkramer Title: Group General Counsel
- 缺口：CEO（Dr. Christian Behrenbruch）的任期和背景信息
- 缺口：董事会独立性和构成
- 缺口：高管薪酬结构和激励对齐
- 缺口：近期高管层变动或继任计划
- 缺口：内部控制和审计意见
- 缺口：引用不存在或原文无法匹配
- 证伪条件：若近期存在未披露的高管离职或继任危机
- 证伪条件：若存在未解决的监管调查或治理争议
- 证伪条件：若ITM合并引发管理层整合冲突

## WGS · complete

审查记录：`state/serenity-reviews/WGS-claudecli-d03f8b170d3f3b7005d9.json`

### supply_chain_map: partial

XBRL标签揭示了部分供应链结构：上游有SupplierA（诊断试剂盒和材料的关联方采购），公司产品为基因诊断测试，下游有三类付款方（第三方保险、机构客户、自费）。但缺乏具体供应商名称、地理集中度和替代难度的叙述性描述。

- 支持 [ev_ac9412d4be0b900c](https://www.sec.gov/Archives/edgar/data/1818331/000162828026072203/wgs-20260930.htm) (primary-document): us-gaap:SupplierConcentrationRiskMember us-gaap:CostOfGoodsTotalMember wgs:SupplierAMember
- 支持 [ev_ac9412d4be0b900c](https://www.sec.gov/Archives/edgar/data/1818331/000162828026072203/wgs-20260930.htm) (primary-document): wgs:DiagnosticTestThirdPartyInsuranceMember
- 支持 [ev_ac9412d4be0b900c](https://www.sec.gov/Archives/edgar/data/1818331/000162828026072203/wgs-20260930.htm) (primary-document): wgs:DiagnosticTestInstitutionalCustomersMember
- 支持 [ev_047bbe73ed56d9e8](https://www.sec.gov/Archives/edgar/data/1818331/000162828026072203/wgs-20260930.htm) (primary-document): wgs:PurchaseOfDiagnosticTestingKitsAndMaterialsMember us-gaap:RelatedPartyMember
- 缺口：具体供应商名称及其在成本中的占比百分比
- 缺口：供应链各节点的地理分布和集中度数据
- 缺口：替代供应商的可用性和切换时间
- 证伪条件：如果SupplierA占成本比例低于10%，供应链集中度论点不成立

### chokepoint_evidence: unknown

证据包中没有任何关于基因诊断行业供应集中度或替代壁垒的具体数据。虽然存在SupplierConcentrationRisk的XBRL标签，但没有披露具体百分比或说明GeneDx在供应链中是否占据不可替代的瓶颈位置。基因诊断市场有多家竞争者（Invitae、Illumina等），仅凭AI相关性不足以认定为chokepoint。

- 缺口：GeneDx在全基因组测序市场的市场份额数据
- 缺口：供应商集中度的具体百分比
- 缺口：下游客户切换成本或锁定期的证据
- 缺口：与竞争对手的技术差异化证据
- 证伪条件：如果其他基因诊断公司能以相似成本和周转时间提供同等测试，则无chokepoint
- 证伪条件：如果Illumina等测序平台供应商可自由向所有实验室供货，则上游无瓶颈

### customer_dependency: partial

XBRL标签证实存在PayorA和PayorB的客户集中度风险披露（收入和应收账款），以及PayorC的应收账款集中度。这说明有实际付费客户，但证据包中缺乏具体集中度百分比、付款方名称或采用率数据。收入按第三方保险、机构客户和自费三个渠道分类报告。

- 支持 [ev_9b81dbb7079d4a4d](https://www.sec.gov/Archives/edgar/data/1818331/000162828026072203/wgs-20260930.htm) (primary-document): us-gaap:CustomerConcentrationRiskMember wgs:PayorAMember us-gaap:RevenueFromContractWithCustomerMember
- 支持 [ev_9b81dbb7079d4a4d](https://www.sec.gov/Archives/edgar/data/1818331/000162828026072203/wgs-20260930.htm) (primary-document): us-gaap:CustomerConcentrationRiskMember wgs:PayorBMember us-gaap:RevenueFromContractWithCustomerMember
- 支持 [ev_ac9412d4be0b900c](https://www.sec.gov/Archives/edgar/data/1818331/000162828026072203/wgs-20260930.htm) (primary-document): us-gaap:CustomerConcentrationRiskMember wgs:PayorCMember us-gaap:AccountsReceivableMember
- 缺口：PayorA和PayorB各占收入的具体百分比
- 缺口：付款方的具体身份（商业保险还是政府付款方）
- 缺口：客户续约率或测试量增长趋势
- 证伪条件：如果单一付款方占收入超过50%，则存在严重客户集中风险而非健康的依赖关系

### pure_play: partial

所有收入细分均为诊断测试类别（第三方保险、机构客户、自费），且公司收购了Fabric Genomics以增强AI解读能力，显示聚焦于基因组诊断。但证据包中缺乏各细分的具体收入金额或百分比，也无法确认是否100%收入来自基因组诊断主题。

- 支持 [ev_ac9412d4be0b900c](https://www.sec.gov/Archives/edgar/data/1818331/000162828026072203/wgs-20260930.htm) (primary-document): wgs:DiagnosticTestThirdPartyInsuranceMember 2026-07-01 2026-09-30
- 支持 [ev_ac9412d4be0b900c](https://www.sec.gov/Archives/edgar/data/1818331/000162828026072203/wgs-20260930.htm) (primary-document): wgs:DiagnosticTestSelfPayMember 2026-07-01 2026-09-30
- 支持 [ev_76d9b3444ecd3520](https://www.sec.gov/Archives/edgar/data/1818331/000162828026072203/wgs-20260930.htm) (primary-document): wgs:FabricGenomicsInc.Member 2025-04-15 2025-04-15
- 缺口：各收入细分的具体金额和占比
- 缺口：基因组诊断测试占总收入的百分比确认
- 缺口：是否有非诊断业务线（如数据服务、研究服务）
- 证伪条件：如果存在大量非基因组诊断收入（如传统实验室服务），纯度将显著降低

### multi_node_control: unknown

证据包未显示GeneDx控制两个以上相连供应链节点的具体证据。公司进行诊断测试并收购了Fabric Genomics（AI解读），这可能构成'测试执行+AI解读'两个节点，但缺乏关于这两个节点之间的具体控制力和不可替代性的证据。

- 缺口：GeneDx自有测序能力vs外包的具体信息
- 缺口：Fabric Genomics AI平台的独特性和市场地位
- 缺口：从样本采集到报告出具的完整垂直整合证据
- 证伪条件：如果GeneDx的测序和解读均可由第三方轻易替代，则不存在多节点控制

### earnings_validation: partial

XBRL数据提供了实际财务结果：Q3 2026收入$123.1M（同比+5.4%），净亏损$12.3M，YTD经营现金流-$72.0M，现金$96.1M。收入增长但仍在亏损，现金仅覆盖约12个月的消耗。公司有Blackstone贷款融资渠道。财务数据真实但未显示盈利路径，且缺乏与AI药物发现主题直接相关的收入分解。

- 支持 [ev_eb8acd4e71ef5aeb](https://data.sec.gov/api/xbrl/companyfacts/CIK0001818331.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 123,101,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_eb8acd4e71ef5aeb](https://data.sec.gov/api/xbrl/companyfacts/CIK0001818331.json) (sec-companyfacts): Same quarter a year earlier (2025-07-01 to 2025-09-30): 116,743,000, a change of +5.4%
- 支持 [ev_eb8acd4e71ef5aeb](https://data.sec.gov/api/xbrl/companyfacts/CIK0001818331.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -12,327,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_eb8acd4e71ef5aeb](https://data.sec.gov/api/xbrl/companyfacts/CIK0001818331.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 96,139,000 for as of 2026-09-30
- 反证 [ev_eb8acd4e71ef5aeb](https://data.sec.gov/api/xbrl/companyfacts/CIK0001818331.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -71,988,000 for 2026-01-01 to 2026-09-30
- 缺口：毛利率趋势及盈利时间表
- 缺口：AI相关收入或药物发现主题的具体收入贡献
- 缺口：未来12个月的资金充足性管理层讨论
- 证伪条件：如果经营现金流持续为负且无法获得新融资，公司可能在12个月内面临资金短缺
- 证伪条件：如果收入增速持续放缓至低个位数，估值论点难以成立

### counter_thesis: partial

可识别的主要风险：(1) 现金$96M vs YTD经营现金流出$72M（9个月），年化约$96M，现金跑道约12个月，存在融资风险；(2) 供应商集中风险（SupplierA）；(3) 客户集中于少数付款方；(4) 仍在亏损。公司有Blackstone贷款但具体条款不明。证据包缺乏竞争格局、替代威胁和估值分析的数据。

- 支持 [ev_eb8acd4e71ef5aeb](https://data.sec.gov/api/xbrl/companyfacts/CIK0001818331.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 96,139,000 for as of 2026-09-30
- 支持 [ev_eb8acd4e71ef5aeb](https://data.sec.gov/api/xbrl/companyfacts/CIK0001818331.json) (sec-companyfacts): Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -71,988,000 for 2026-01-01 to 2026-09-30
- 支持 [ev_047bbe73ed56d9e8](https://www.sec.gov/Archives/edgar/data/1818331/000162828026072203/wgs-20260930.htm) (primary-document): us-gaap:SecuredDebtMember wgs:BlackstoneLoanAgreementMember 2026-02-27
- 缺口：竞争对手（Invitae、Illumina等）的市场份额和定价对比
- 缺口：保险报销政策变化对收入的潜在影响
- 缺口：AI药物发现领域的替代方案和技术风险
- 缺口：估值倍数与同行对比
- 证伪条件：如果保险公司缩减基因诊断报销范围，收入将大幅下降
- 证伪条件：如果现金跑道不足12个月且无新融资，可能被迫稀释性增发
- 证伪条件：如果Illumina或其他平台商向下游整合提供诊断服务，GeneDx面临替代风险

### management_governance: unknown

证据包中没有关于管理层背景、领导层变动、治理结构或调查事项的任何叙述性信息。XBRL标签和10-Q封面页仅提供公司注册信息，无法评估管理层质量或治理风险。

- 缺口：CEO和关键高管的背景和任期信息
- 缺口：董事会构成和独立性
- 缺口：近期管理层变动或离职
- 缺口：任何未决调查或治理争议
- 证伪条件：如果存在未披露的SEC调查或管理层欺诈，治理评级将立即降为fail

## WRBY · complete

审查记录：`state/serenity-reviews/WRBY-claudecli-bd2bfe5eae35804e3436.json`

### supply_chain_map: unknown

10-K披露了上游依赖有限供应商和合同制造商，下游通过电商和零售渠道销售眼镜、隐形眼镜和服务，但未具体命名上游供应商，供应链地图不完整。

- 支持 [ev_5fc33a6b82538a43](https://www.sec.gov/Archives/edgar/data/1504776/000150477626000006/wrby-20251231.htm) (primary-document): We face risks associated with suppliers from whom our products are sourced and are dependent on a limited number of suppliers.
- 支持 [ev_5fc33a6b82538a43](https://www.sec.gov/Archives/edgar/data/1504776/000150477626000006/wrby-20251231.htm) (primary-document): We rely on a limited number of contract manufacturers and logistics partners for our products.
- 缺口：具体上游供应商名称及各自份额
- 缺口：关键材料（镜片、镜框）的来源国家和替代周期
- 缺口：合同制造商的具体信息
- 缺口：引用不存在或原文无法匹配
- 证伪条件：若上游供应商可轻易替代，则不存在供应链瓶颈价值

### chokepoint_evidence: unknown

Warby Parker是消费眼镜零售商，非AI基础设施供应链的瓶颈节点。证据仅显示其依赖有限供应商，但未证明WRBY本身控制任何稀缺供给或存在替代壁垒。Top 5供应商集中度标签存在但无具体数据支持瓶颈论点。

- 反证 [ev_c75a6c1bd5adcc68](https://www.sec.gov/Archives/edgar/data/1504776/000150477626000006/wrby-20251231.htm) (primary-document): The optical industry is highly competitive, and if we do not compete successfully, our business may be adversely impacted.
- 缺口：任何证据表明WRBY控制稀缺供给
- 缺口：供给集中度数据（市场份额）
- 缺口：替代壁垒或转换成本的证据
- 缺口：反证只是通用风险条款或记录字段，不是针对公司的直接反证
- 证伪条件：光学行业高度竞争，消费者可轻松转向Luxottica/EssilorLuxottica等竞争对手

### customer_dependency: partial

WRBY是面向消费者的B2C公司，无超大规模客户设计导入。10-K提到与Google和Samsung的合作关系，但仅作为前瞻性声明出现，未披露任何具体收入贡献或采用数据。

- 支持 [ev_d183980f24baddb1](https://www.sec.gov/Archives/edgar/data/1504776/000150477626000006/wrby-20251231.htm) (primary-document): including the partnership with Google and Samsung and the development and timing of new products
- 缺口：Google/Samsung合作的具体条款、收入贡献
- 缺口：任何大客户收入集中度披露
- 缺口：设计导入锁定或长期合同的证据
- 证伪条件：合作仅为产品开发意向而非确认的收入驱动关系

### pure_play: unknown

WRBY是消费眼镜和视力服务零售商，收入来自眼镜产品、隐形眼镜和服务。与AI基础设施供应链瓶颈主题无实质关联，不构成主题纯度。

- 缺口：任何AI相关收入分部
- 缺口：与AI供应链瓶颈主题的实质性收入关联
- 缺口：引用不存在或原文无法匹配
- 证伪条件：全部收入来自消费眼镜零售，AI仅作为内部运营工具被提及

### multi_node_control: unknown

证据未显示WRBY控制任何AI供应链的两个或以上相连节点。其垂直整合（零售+电商+视力服务）属于消费零售领域，与AI基础设施瓶颈无关。

- 缺口：控制AI供应链多个节点的任何证据
- 缺口：上游材料或组件的自主生产能力证据
- 缺口：不通过需要直接反证，缺少证据不能等同失败
- 证伪条件：WRBY依赖外部供应商和合同制造商，不控制上游生产节点

### earnings_validation: partial

WRBY有实际财务数据：Q3 2026收入$244.7M同比+10.4%，净利润$5.6M，现金$287.9M。财务状况健康，但这些数据验证的是消费零售增长论点，而非AI瓶颈论点。无法用这些财务数据确认AI主题投资假说。

- 支持 [ev_d7af4cdc07676e87](https://data.sec.gov/api/xbrl/companyfacts/CIK0001504776.json) (sec-companyfacts): Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 244,735,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_d7af4cdc07676e87](https://data.sec.gov/api/xbrl/companyfacts/CIK0001504776.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 5,603,000 for 2026-07-01 to 2026-09-30
- 支持 [ev_d7af4cdc07676e87](https://data.sec.gov/api/xbrl/companyfacts/CIK0001504776.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 287,914,000 for as of 2026-09-30
- 反证 [ev_c75a6c1bd5adcc68](https://www.sec.gov/Archives/edgar/data/1504776/000150477626000006/wrby-20251231.htm) (primary-document): We have a history of losses, and we may be unable to sustain profitability.
- 缺口：与AI主题相关的收入分部或增长驱动因素
- 缺口：Google/Samsung合作的财务贡献
- 证伪条件：盈利能力刚转正且公司自认有亏损历史，持续性存疑

### counter_thesis: partial

10-K风险因素覆盖了竞争、供应商依赖、监管和数据隐私风险，但缺乏对AI主题特有风险（替代路径、地缘政治、估值）的深入分析。作为消费零售公司，核心反面论点是：光学行业高度竞争，无护城河；Google/Samsung合作不确定性大；双重股权结构治理风险。

- 支持 [ev_c75a6c1bd5adcc68](https://www.sec.gov/Archives/edgar/data/1504776/000150477626000006/wrby-20251231.htm) (primary-document): The optical industry is highly competitive, and if we do not compete successfully, our business may be adversely impacted.
- 支持 [ev_c75a6c1bd5adcc68](https://www.sec.gov/Archives/edgar/data/1504776/000150477626000006/wrby-20251231.htm) (primary-document): Disruptions to our supply chain can have a material adverse effect on our business, financial condition, and operating results.
- 支持 [ev_5fc33a6b82538a43](https://www.sec.gov/Archives/edgar/data/1504776/000150477626000006/wrby-20251231.htm) (primary-document): We face risks associated with suppliers from whom our products are sourced and are dependent on a limited number of suppliers.
- 缺口：估值风险分析（$3.4B市值对应的盈利倍数是否合理）
- 缺口：AI主题替代路径和地缘政治风险的具体分析
- 证伪条件：光学行业竞争激烈且进入壁垒低
- 证伪条件：Google/Samsung合作可能终止或未产生实质收入
- 证伪条件：双重股权结构削弱外部股东权利
- 证伪条件：消费支出放缓直接冲击可选消费品类

### management_governance: partial

双重CEO结构（Neil Blumenthal和Dave Gilboa），双重股权结构（A类和B类股），创始人如联合行动可对所有股东投票事项施加重大影响。无未解决的调查或继任危机，但双重股权集中控制权构成治理隐患。

- 支持 [ev_5fc33a6b82538a43](https://www.sec.gov/Archives/edgar/data/1504776/000150477626000006/wrby-20251231.htm) (primary-document): Our Co-Founders and Co-CEOs, Neil Blumenthal and Dave Gilboa, if they choose to act together and if they exercise and/or settle their options, restricted stock units
- 支持 [ev_5fc33a6b82538a43](https://www.sec.gov/Archives/edgar/data/1504776/000150477626000006/wrby-20251231.htm) (primary-document): have the ability to exercise significant influence over all matters submitted to stockholders for approval, including exercising significant control over the outcome of director elections.
- 缺口：董事会独立性和构成细节
- 缺口：高管薪酬与业绩挂钩情况
- 缺口：近期高管变动或继任计划
- 证伪条件：双重股权+双CEO结构可能导致公司治理僵化或决策失误时缺乏有效制衡

## WVE · complete

审查记录：`state/serenity-reviews/WVE-codex-b31231bd24dd8889e1da.json`

### supply_chain_map: unknown

包内FDA记录的制造商名称与待审发行人不一致，存在名称碰撞，不能据此建立该公司的产品或供应链关系。

- 反证 [ev_082793d516612445](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K260402) (fda-ai-device-list): FDA AI-enabled medical-device authorization record. Manufacturer: Wave Neuroscience. Device: MeRT System. Final decision date: 06/03/2026. This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：能够把FDA制造商与发行人法律实体连接起来的原始材料
- 缺口：公司产品、上游输入和下游用户的完整关系
- 证伪条件：官方实体信息确认FDA制造商与发行人无控制或隶属关系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 反证 [ev_082793d516612445](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K260402) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

- 反证 [ev_082793d516612445](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K260402) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：具名客户或经核验的客户数量
- 缺口：付费部署、续约和使用量
- 缺口：客户收入贡献及切换成本
- 证伪条件：客户试点未转为付费部署
- 证伪条件：续约率或实际使用量持续下降
- 证伪条件：客户采用可替代产品且切换成本很低

### pure_play: unknown

公司级财务数据或单个产品记录没有拆分目标主题收入、利润和资产贡献，不能判断业务是否为纯主题暴露。

- 缺口：目标主题收入占比
- 缺口：分部收入和利润
- 缺口：其他业务对总体结果的稀释程度
- 证伪条件：目标主题收入长期低于总收入的10%
- 证伪条件：增长主要来自与目标主题无关的业务

### multi_node_control: unknown

现有材料没有证明公司控制两个相连的供应链节点；多个产品、多个FDA记录或研发支出不等于跨节点控制。

- 缺口：至少两个相连节点的所有权或控制权
- 缺口：节点之间的经济依赖和收入传导
- 缺口：外部客户对两个节点的使用证据
- 证伪条件：关键节点实际由无关联第三方控制
- 证伪条件：所谓多个节点只是同一产品的不同版本

### earnings_validation: partial

SEC一手材料提供了带日期的实际公司级收入、利润、现金或研发数据，但没有把这些结果归因到目标主题或已识别产品，因此只能部分验证财务表现。

- 支持 [ev_fb2ce367a2370f4d](https://data.sec.gov/api/xbrl/companyfacts/CIK0001631574.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for WAVE LIFE SCIENCES, INC.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 13,158,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-10-27, accession 0001193125-26-432714. Same period a year earlier (2025-07-01 to 2025-09-30): 7,608,000, a change of +72.9%. Net income (loss) (NetIncomeLoss): -61,912,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_fb2ce367a2370f4d](https://data.sec.gov/api/xbrl/companyfacts/CIK0001631574.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for WAVE LIFE SCIENCES, INC.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 13,158,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-10-27, accession 0001193125-26-432714. Same period a year earlier (2025-07-01 to 2025-09-30): 7,608
- 反证 [ev_fb2ce367a2370f4d](https://data.sec.gov/api/xbrl/companyfacts/CIK0001631574.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -61,912,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-10-27, accession 0001193125-26-432714. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -59,553,000 for 2026-01-01 to 2026-03-31; form 10-Q filed 2026-04-28, accession 0001193125-26-183587. Cash and equivalents (CashAndCashEquivalentsAtCarryingV
- 缺口：竞争产品和替代路径
- 缺口：客户需求下行情景
- 缺口：监管与估值压力测试
- 缺口：关键假设的量化敏感度
- 证伪条件：收入增长停滞且亏损或现金消耗扩大
- 证伪条件：替代方案显著降低客户切换成本
- 证伪条件：估值隐含增长长期高于可实现增长

### management_governance: unknown

证据包没有董事会、关键管理层连续性、内部控制、关联交易、调查或继任计划材料，不能推定治理通过。

- 缺口：董事会与管理层履历
- 缺口：内部控制与重大缺陷
- 缺口：未决调查、诉讼和继任计划
- 证伪条件：关键高管突然离任且无明确继任安排
- 证伪条件：出现重大内控缺陷、监管调查或利益冲突

## YARW · complete

审查记录：`state/serenity-reviews/YARW-claudecli-b08ff717d848d6b6e209.json`

### supply_chain_map: unknown

上游：YB-101由长春金赛（GenSci）授权许可，API由中国武汉药明康德（WuXi Apptec）生产。公司产品：YB-101抗TSHR单克隆抗体，用于治疗Graves病和甲状腺眼病。下游：美国GD/TED患者群体（估计年发病率34,000–68,000，流行患者约100万）。供应链上游的CMO依赖有限且集中于中国，存在BIOSECURE法案风险，但缺少完整的药物物质/制剂供应链细节。

- 支持 [ev_933b01d6bd69311b](https://www.sec.gov/Archives/edgar/data/1566044/000156604426000002/vyne-20251231.htm) (primary-document): the primary manufacturer of the active pharmaceutical ingredient ("API") in our product candidates is WuXi Apptec, located in China
- 支持 [ev_dca226c541d7e37a](https://www.sec.gov/Archives/edgar/data/1566044/000110465926106699/tm2624937d1_ex99-2.htm) (primary-document): Yarrow estimates an annual incident eligible population of approximately 34,000 to 68,000 patients and a prevalent eligible population of approximately 1,000,000 patients in the United States
- 缺口：完整的药物物质和制剂CMO供应链（除WuXi外的备选供应商）
- 缺口：关键中间体和原料的具体供应商信息
- 缺口：药品包装和分销渠道细节
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现WuXi以外的替代API供应商已签约
- 证伪条件：发现公司已内部化部分制造环节

### chokepoint_evidence: unknown

Yarrow是临床阶段药物开发公司，不控制任何供应链瓶颈节点。YB-101是从GenSci授权的候选药物，API由WuXi生产——公司本身既不是稀缺原料的唯一供应商，也不拥有任何具有高替代壁垒的制造能力。虽然抗TSHR抗体作为GD治疗的机制具有新颖性，但这属于药物差异化，而非Serenity框架定义的供应链集中度或替代壁垒。无证据支持chokepoint。

- 缺口：公司控制稀缺供应节点的证据
- 缺口：替代壁垒或供应集中度数据
- 缺口：独占性制造工艺或原料证据
- 证伪条件：发现YB-101依赖的某关键原料全球仅有极少数供应商
- 证伪条件：发现公司拥有不可替代的专有制造平台

### customer_dependency: unknown

Yarrow处于临床开发阶段（Phase 2a/2b），尚无商业化产品，无法证明客户采用或依赖。现有收入仅为极少量版税（2025年$570K），来自旧业务（VYNE时期的repibresib/VYN202许可），与核心YB-101管线无关。无下游客户（医院、支付方、患者）的采用证据。

- 支持 [ev_32a636e0daf42bae](https://www.sec.gov/Archives/edgar/data/1566044/000156604426000002/vyne-20251231.htm) (primary-document): Royalty revenues $ 570 $ 501
- 缺口：任何客户/支付方对YB-101的采用意向或预购协议
- 缺口：关键意见领袖或医疗机构的背书
- 缺口：保险覆盖或报销路径讨论
- 证伪条件：Phase 2数据公布后出现医疗机构合作或支付方兴趣的披露
- 证伪条件：与大型药企达成商业化合作协议

### pure_play: unknown

公司明确为单一运营部门，专注于自身免疫性甲状腺疾病（GD和TED）。10-K确认单一可报告部门，8-K进一步明确Yarrow转型后完全聚焦于YB-101管线。几乎全部资源投入该治疗领域，主题纯度极高。

- 支持 [ev_d612082406462f32](https://www.sec.gov/Archives/edgar/data/1566044/000156604426000002/vyne-20251231.htm) (primary-document): The Company operates in one operating segment, and therefore one reportable segment, focused on the development of differentiated therapies to treat inflammatory and immune-mediated conditions of high unmet need
- 缺口：引用不存在或原文无法匹配
- 证伪条件：公司收购或开发与自身免疫甲状腺疾病无关的管线
- 证伪条件：旧VYNE管线（repibresib/VYN202）重新成为核心资产

### multi_node_control: unknown

Yarrow不控制供应链中的多个相连节点。药物由GenSci授权、API由WuXi生产——公司角色限于临床开发和未来商业化，未纵向整合制造、原料或分销。无证据表明公司控制两个以上相连的供应链环节。

- 缺口：公司拥有自有制造设施的证据
- 缺口：纵向整合上游原料或下游分销的证据
- 证伪条件：公司收购CMO或建立自有生产线
- 证伪条件：公司获得关键原料的独占供应权

### earnings_validation: partial

临床准备阶段公司，预期无收入。XBRL数据显示2026年6月30日现金$22.9M，H1 2026经营性现金流出$6.1M（年化约$12M），可推算约23个月跑道，超过12个月门槛。研发支出Q2仅$788K，远低于2025年水平（全年约$19.2M），反映管线转型期支出结构变化。smallCapContext显示2026年9月底现金升至$268.9M（不可引用），暗示期间完成大额融资。可引用的财务数据支持公司能资助下一里程碑（Phase 2a数据预计2027年下半年），但缺少2026年Q3后的可引用融资和现金细节。

- 支持 [ev_226027f07032917c](https://data.sec.gov/api/xbrl/companyfacts/CIK0001566044.json) (sec-companyfacts): Cash and equivalents (CashAndCashEquivalentsAtCarryingValue): 22,925,000 for as of 2026-06-30
- 支持 [ev_226027f07032917c](https://data.sec.gov/api/xbrl/companyfacts/CIK0001566044.json) (sec-companyfacts): NetCashProvidedByUsedInOperatingActivities): -6,073,000 for 2026-01-01 to 2026-06-30
- 支持 [ev_226027f07032917c](https://data.sec.gov/api/xbrl/companyfacts/CIK0001566044.json) (sec-companyfacts): ResearchAndDevelopmentExpense): 788,000 for 2026-04-01 to 2026-06-30
- 缺口：2026年Q3后的可引用现金余额和融资详情
- 缺口：Phase 2临床试验的预计总成本
- 缺口：管线转型后的运营费用预算
- 证伪条件：发现可引用的Q3/Q4财务数据显示现金低于12个月烧钱率
- 证伪条件：Phase 2试验成本远超当前现金储备

### counter_thesis: partial

已识别多项风险：(1) 供应风险——API唯一供应商WuXi受BIOSECURE法案威胁；(2) 竞争风险——TED领域已有TEPEZZA和LUMVOA获批，GD领域自1950年来无新药但ATD为标准治疗；(3) 监管风险——GenSci中国临床数据可能不被FDA接受；(4) 临床风险——Phase 2a数据要到2027年下半年才有。但缺少估值角度的反面证据（$219M市值对临床阶段公司是否合理），也缺少具体竞争对手正在开发抗TSHR抗体的直接证据（仅提到K1-70的第三方数据）。

- 支持 [ev_933b01d6bd69311b](https://www.sec.gov/Archives/edgar/data/1566044/000156604426000002/vyne-20251231.htm) (primary-document): the primary manufacturer of the active pharmaceutical ingredient ("API") in our product candidates is WuXi Apptec, located in China. Certain Chinese biotechnology companies, including WuXi Apptec, and contract manufacturing organizations may become subject to trade restrictions, sanctions, and other regulatory requirements by the U.S. government
- 支持 [ev_b4c84cfcd851460f](https://www.sec.gov/Archives/edgar/data/1566044/000110465926106699/tm2624937d1_ex99-2.htm) (primary-document): TEPEZZA®, a humanized monoclonal antibody targeting IGF-1R, is approved in the United States for the treatment of TED and has demonstrated clinical efficacy
- 支持 [ev_b4c84cfcd851460f](https://www.sec.gov/Archives/edgar/data/1566044/000110465926106699/tm2624937d1_ex99-2.htm) (primary-document): LUMVOA™ (veligrotug-vvze) was approved by the FDA for the treatment of TED in June 2026
- 支持 [ev_9149dc43608389bf](https://www.sec.gov/Archives/edgar/data/1566044/000110465926106699/tm2624937d1_ex99-2.htm) (primary-document): there can be no assurance that the clinical data being generated by GenSci in China will be accepted by the FDA or comparable foreign regulatory authorities for purposes of supporting regulatory approval of YB-101 for TED outside of China
- 支持 [ev_dca226c541d7e37a](https://www.sec.gov/Archives/edgar/data/1566044/000110465926106699/tm2624937d1_ex99-2.htm) (primary-document): There have been no new drugs approved for GD in the United States since 1950
- 反证 [ev_159e916e0ea6ad23](https://www.sec.gov/Archives/edgar/data/1566044/000110465926106699/tm2624937d1_ex99-2.htm) (primary-document): Among moderate-to-severe TED patients who are treated with TEPEZZA® (teprotumumab-trbw), approximately 40% experience relapse
- 缺口：其他抗TSHR抗体竞争管线的详细进展
- 缺口：估值合理性的反面分析
- 缺口：GenSci在中国市场的竞争格局
- 缺口：RTW Investments锁定期和退出压力分析
- 证伪条件：Phase 2a数据未达主要终点（FT3/FT4/TSH正常化）
- 证伪条件：WuXi被正式列入BIOSECURE法案受限实体名单且无替代CMO
- 证伪条件：竞争对手的抗TSHR抗体先于YB-101进入Phase 3
- 证伪条件：FDA拒绝接受GenSci中国SAD数据用于后续申报
- 证伪条件：RTW大量减持导致股价崩溃

### management_governance: unknown

证据显示公司有分类董事会（三年交错任期）、反收购条款等标准治理结构。董事会成员包括有丰富生物技术行业经验的Barbari（前Gilead CFO、前InterMune CFO）和Basta（前VYNE前身CEO，现Phathom CEO）。公司声称已组建经验丰富的管理团队。但证据中缺少现任CEO/CFO的具体姓名和背景，无法充分评估领导层连续性。无未决调查或继任危机的证据。

- 支持 [ev_0e18320c1931b66f](https://www.sec.gov/Archives/edgar/data/1566044/000156604426000002/vyne-20251231.htm) (primary-document): From 1998 to 2002, she served in senior financial roles at Gilead Sciences, including as Chief Financial Officer
- 支持 [ev_afff08232bf28422](https://www.sec.gov/Archives/edgar/data/1566044/000156604426000002/vyne-20251231.htm) (primary-document): a classified board of directors with three-year staggered terms, which may delay the ability of stockholders to change the membership of a majority of our board of directors
- 缺口：现任CEO和CFO的具体姓名及完整背景
- 缺口：高管薪酬和激励结构
- 缺口：董事会独立性比例和审计委员会构成
- 缺口：引用不存在或原文无法匹配
- 证伪条件：发现关键高管近期离职或继任计划不明
- 证伪条件：发现未披露的监管调查或诉讼
- 证伪条件：RTW作为控股方存在治理利益冲突
