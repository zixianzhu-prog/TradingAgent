# Serenity 自动证据审查

审查方式：Claude review; no model API key; FinRobot disabled。每个门槛均关联支持材料、反证和缺口。引用匹配只是可追溯性检查，不保证推论正确。历史手工评分不作为已验证证据。

## ABCL · complete

审查记录：`state/serenity-reviews/ABCL-codex-dc63ad6f87078dc9e952.json`

### supply_chain_map: partial

材料能够定位公司的产品/平台或监管产品，但没有完整覆盖上游关键输入、下游使用者和替代周期，供应链图仍不完整。

- 支持 ev_ba1b07ce075f23cd (local-unverified-notes): {"rank": 8, "ticker": "ABCL", "company": "AbCellera Biologics", "classification": "secondary watchlist", "thesis": "A technology-enabled antibody discovery platform with long-term optionality, but current evidence is weaker than the top thr
- 缺口：补齐上游输入、供应集中度、下游付费用户与替代时间
- 证伪条件：关键上游或下游关系无法由原始材料确认

### chokepoint_evidence: partial

现有材料提出数据、软件或产品组合可能形成卡位，但没有原始证据证明供应集中度、市场份额或多年替代障碍，不能把 AI 相关性当作瓶颈。

- 支持 ev_ba1b07ce075f23cd (local-unverified-notes): {"rank": 8, "ticker": "ABCL", "company": "AbCellera Biologics", "classification": "secondary watchlist", "thesis": "A technology-enabled antibody discovery platform with long-term optionality, but current evidence is weaker than the top thr
- 缺口：需要市场份额、替代成本、重新认证周期或独家数据权利的原始证据
- 证伪条件：竞争者可在较短时间复制数据/模型/产品能力
- 证伪条件：客户可低成本切换或自建同类能力

### customer_dependency: partial

本地研究材料描述了客户或合作方使用场景，但尚缺可独立核验的客户收入、续约率或依赖比例，因此合作关系不能等同客户收入。

- 支持 ev_ba1b07ce075f23cd (local-unverified-notes): {"rank": 8, "ticker": "ABCL", "company": "AbCellera Biologics", "classification": "secondary watchlist", "thesis": "A technology-enabled antibody discovery platform with long-term optionality, but current evidence is weaker than the top thr
- 缺口：补充客户原始披露、续约/扩张及收入贡献
- 缺口：区分合作公告、试用与付费生产使用
- 证伪条件：合作方停止推进项目或不再续约
- 证伪条件：客户增长未带来收入和现金流改善

### pure_play: partial

候选与 AI 医疗主题存在直接业务联系，但当前材料没有以统一口径拆分 AI 医疗收入占比；业务纯度只能暂定为部分验证。

- 支持 ev_ba1b07ce075f23cd (local-unverified-notes): {"rank": 8, "ticker": "ABCL", "company": "AbCellera Biologics", "classification": "secondary watchlist", "thesis": "A technology-enabled antibody discovery platform with long-term optionality, but current evidence is weaker than the top thr
- 缺口：补充按业务线收入、毛利和资本投入的原始分部披露
- 证伪条件：AI 医疗相关收入长期占比很低或被其他业务稀释

### multi_node_control: unknown

材料显示公司覆盖多个产品、数据或工作流环节，但“多产品”不自动等于控制两个相连的供应链节点；控制权和节点间依赖仍需原始材料确认。

- 缺口：证明至少两个相连节点的所有权、定价权或客户切换障碍
- 证伪条件：多个产品之间没有共享数据、客户锁定或经济协同

### earnings_validation: pass

已取得带日期的季度原始财务披露，可验证收入、利润/亏损及现金等实际结果；这只通过财报验证流程，不代表投资结论通过。

- 支持 [ev_ce9ff5fdcf1f0f22](https://data.sec.gov/api/xbrl/companyfacts/CIK0001703057.json) (sec-companyfacts): us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax: 10.639 USD_m; period 2026-07-01 to 2026-09-30; filed 2026-11-09; form 10-Q; accession 0001703057-26-000059. us-gaap:NetIncomeLoss: -40.758 USD_m; period 2026-07-01 to 2026-09-30;
- 证伪条件：后续季度收入或客户增长失速
- 证伪条件：亏损、现金消耗或稀释趋势恶化

### counter_thesis: pass

已用原始财务结果检验增长叙事，并保留需求、替代、现金消耗、稀释和商业化失败等反方路径；通过表示反方已被审查，不表示风险消失。

- 支持 [ev_ce9ff5fdcf1f0f22](https://data.sec.gov/api/xbrl/companyfacts/CIK0001703057.json) (sec-companyfacts): us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax: 10.639 USD_m; period 2026-07-01 to 2026-09-30; filed 2026-11-09; form 10-Q; accession 0001703057-26-000059. us-gaap:NetIncomeLoss: -40.758 USD_m; period 2026-07-01 to 2026-09-30;
- 反证 [ev_ce9ff5fdcf1f0f22](https://data.sec.gov/api/xbrl/companyfacts/CIK0001703057.json) (sec-companyfacts): us-gaap:NetIncomeLoss: -40.758 USD_m; period 2026-07-01 to 2026-09-30; filed 2026-11-09; form 10-Q; accession 0001703057-26-000059. us-gaap:ResearchAndDevelopmentExpense: 43.535 USD_m; period 2026-07-01 to 2026-09-30; filed 2026-11-09; form
- 证伪条件：收入增长不能转化为持续毛利和现金流
- 证伪条件：客户或合作方停止扩张/推进
- 证伪条件：竞争者或客户自建替代能力
- 证伪条件：融资稀释吸收大部分业务增长价值

### management_governance: unknown

证据包没有充分的董事会、关键管理层连续性、内部控制或未决调查材料，不能推定治理通过。

- 缺口：补充最新代理声明、管理层变动、内部控制和重大调查披露
- 证伪条件：出现未解决的领导层继任、内部控制缺陷或监管调查

## ADPT · complete

审查记录：`state/serenity-reviews/ADPT-codex-34715ce748aa390c0369.json`

### supply_chain_map: unknown

证据包没有提供公司产品、上游投入与下游使用者之间的具体关系；财务汇总数字不能替代供应链映射。

- 缺口：具体产品和服务
- 缺口：上游关键输入及供应商
- 缺口：下游客户、工作流和替代周期
- 证伪条件：原始披露显示候选公司与目标主题没有直接产品或服务联系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

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

- 支持 [ev_0476178e188af245](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478320.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for ADAPTIVE BIOTECHNOLOGIES CORPORATION. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 83,902,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04, accession 0001193125-26-447411. Same period a year earlier (2025-07-01 to 2025-09-30): 93,973,000, a change of -10.7%. Net income (loss) (NetIncomeLoss): 2,876,000 for 2026-07-01 to 2026-09-30; form 1
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_0476178e188af245](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478320.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for ADAPTIVE BIOTECHNOLOGIES CORPORATION. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 83,902,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04, accession 0001193125-26-447411. Same period a year earlier (2025-07-01 to 2025-0
- 反证 [ev_0476178e188af245](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478320.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 2,876,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04, accession 0001193125-26-447411. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -9,537,000 for 2026-01-01 to 2026-03-31; form 10-Q filed 2026-05-05, accession 0001193125-26-206546. Cash and equivalents (CashAndCashEquivalentsAtCarryingValu
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

## CAI · complete

审查记录：`state/serenity-reviews/CAI-claude-1dd82ece41c2512acd91.json`

### supply_chain_map: pass

测序仪与试剂依赖少数或单一供应商；收款依赖保险付款方。

- 支持 [ev_08566aafb5d3e243](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): We rely on a limited number of third-party suppliers or, in many cases, sole suppliers, for some of our next-generation sequencers, lab materials, reagents, and supplies
- 支持 [ev_fd592feffffcf113](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000069/cai-20260930.htm) (primary-document): Collection of consideration the Company expects to receive typically occurs within 90 to 120 days of billing.

### chokepoint_evidence: partial

超过 100 万例测序数据与 FDA 伴随诊断批准构成壁垒；但精准肿瘤行业竞争激烈。

- 支持 [ev_fed6f72704f4321d](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): As of December 31, 2025, we have performed sequencing on over 1,000,000 cases.
- 支持 [ev_08fff9b9f63b0152](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): MI Cancer Seek has obtained FDA approval for use as a companion diagnostic device
- 反证 [ev_a8317c192a1d3160](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): The precision oncology industry is intensely competitive.

### customer_dependency: partial

有合作协议，但缺少客户集中度数据。

- 支持 [ev_d3fd14a25d424ab5](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): We have entered into a collaboration agreement with Everlywell to expand access to Caris Detect.
- 缺口：客户与付款方集中度

### pure_play: pass

公司定位为 AI TechBio，新产品以 AI 分析全基因组信号。

- 支持 [ev_eedbe4af3fb117c1](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): We are a leading, patient-centric, next-generation AI TechBio company and precision medicine pioneer.
- 支持 [ev_d27c36a67e8534db](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000069/cai-20260930.htm) (primary-document): Caris Detect utilizes ultra-deep Whole Genome Sequencing, Whole Transcriptome Sequencing and advanced artificial intelligence to analyze molecular and biological signals associated with cancer.

### multi_node_control: pass

检测数据同时支撑数字产品与药企服务。

- 支持 [ev_1aad7b6628af9a8f](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000069/cai-20260930.htm) (primary-document): which now also serves as the foundation for our digital solutions such as Caris MI Clarity
- 支持 [ev_49a4475256af3963](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): Leverage our platform to provide solutions to biopharma companies to drive advances in personalized medicine

### earnings_validation: pass

2025 年收入 8.12 亿美元，增长 97%。

- 支持 [ev_d3a91650d7a15f58](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): Total revenue was $812.0 million for the year ended December 31, 2025, compared to $412.3 million for the year ended December 31, 2024, an increase of $399.8 million, or 97.0%.

### counter_thesis: pass

债务与竞争风险已检验。

- 支持 [ev_e82d3f78f4ee65a9](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): we incurred net losses of $68.1 million and $281.9 million, respectively
- 反证 [ev_1fa894f3f9a8921e](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): we and our subsidiaries had approximately $400.0 million aggregate principal amount of debt outstanding under the 2023 Term Loan
- 反证 [ev_a8317c192a1d3160](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): The precision oncology industry is intensely competitive.
- 证伪条件：收入增速跌破 30%
- 证伪条件：内控缺陷未在下一份年报前整改

### management_governance: partial

公司披露财务报告内部控制存在重大缺陷，正在整改。

- 反证 [ev_fca18591a9107b1c](https://www.sec.gov/Archives/edgar/data/2019410/000201941026000016/cai-20251231.htm) (primary-document): We have identified a material weakness in our internal control over financial reporting.
- 缺口：重大缺陷的整改结果

## CBLL · complete

审查记录：`state/serenity-reviews/CBLL-claude-c95f32aafc1f7ed193fb.json`

### supply_chain_map: pass

头带由中国和越南的合同制造商组装，主要部件有双来源；最终检验在加州完成。

- 支持 [ev_2ebad2122ff639e1](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): Contract manufacturers in China and Vietnam assemble the headbands, with final inspection and labeling completed at our California facilities.
- 支持 [ev_2ebad2122ff639e1](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): We have dual sources for major components of the Wearables.

### chokepoint_evidence: partial

原有瓶颈证据不变（癫痫持续状态首个 510(k)、唯一获许可的谵妄监测设备）。2026-09-16 的新许可 K261712 是实质等同许可，对比器械是竞品 encevis，且功能只是其子集、不含自动癫痫检测，因此不构成新的监管壁垒，维持 partial。

- 支持 [ev_a132a250c32bb0bf](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): became the first device to receive 510(k) clearance from the U.S. Food and Drug Administration
- 支持 [ev_4e14f8075cfd795e](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): the first and only FDA-cleared delirium screening and monitoring device
- 反证 [ev_6755571fe8fc0703](https://www.sec.gov/Archives/edgar/data/1861107/000119312526067238/cbll-20251231.htm) (primary-document): Alternative technologies addressing seizure, non-convulsive status epilepticus, delirium, LVO stroke or other indications we intend to expand into could materially adversely affect our business
- 反证 [ev_8ebe184790963d01](https://www.accessdata.fda.gov/cdrh_docs/pdf26/K261712.pdf) (primary-document): the subject device does not include any automatic seizure or spike detection functions and is claiming a subset of functions compared to the predicate device
- 反证 [ev_95e415d60540b520](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K261712) (primary-document): Decision Substantially Equivalent (SESE)

### customer_dependency: partial

为医院和付款方节省成本，并获得 NTAP 新技术附加支付；缺少医院客户集中度。

- 支持 [ev_06c6aa53d235c72e](https://www.sec.gov/Archives/edgar/data/1861107/000119312526067238/cbll-20251231.htm) (primary-document): We have demonstrated that the Ceribell System can deliver cost savings for hospitals and payers by decreasing the average hospital length of stay
- 支持 [ev_64983a488e53baec](https://www.sec.gov/Archives/edgar/data/1861107/000119312526067238/cbll-20251231.htm) (primary-document): subsequently received a New Technology Add-on Payment
- 缺口：医院客户数量与集中度

### pure_play: pass

核心产品是硬件加 AI 算法的床旁脑电平台。新许可的软件提供定量脑电指标，不涉及 AI 判读，不改变本门槛。

- 支持 [ev_6777218eb43d67eb](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): By combining proprietary, highly portable and rapidly deployable hardware with sophisticated artificial intelligence

### multi_node_control: pass

自管制造、供应链与分销，并拥有 AI 判读算法。

- 支持 [ev_2ebad2122ff639e1](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): We manage all aspects of manufacturing, supply chain, and distribution of the Wearables and recorder from our facilities in Sunnyvale, California.
- 支持 [ev_a132a250c32bb0bf](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): EEG data captured by the recorder is interpreted by our proprietary AI-powered seizure detection algorithms

### earnings_validation: pass

2025 年收入 8,910 万美元，增长 36%，毛利率 88%。

- 支持 [ev_340675d65348b33f](https://www.sec.gov/Archives/edgar/data/1861107/000119312526067238/cbll-20251231.htm) (primary-document): We recognized revenue of $89.1 million for the year ended December 31, 2025, compared to revenue of $65.4 million for the year ended December 31, 2024, representing 36% year-over-year growth.
- 支持 [ev_340675d65348b33f](https://www.sec.gov/Archives/edgar/data/1861107/000119312526067238/cbll-20251231.htm) (primary-document): we recognized a gross margin of 88%

### counter_thesis: pass

亏损扩大、海外制造风险已检验；新增：FDA 摘要显示竞品 encevis 已有更完整的已许可脑电分析功能，替代风险有一手证据。

- 支持 [ev_340675d65348b33f](https://www.sec.gov/Archives/edgar/data/1861107/000119312526067238/cbll-20251231.htm) (primary-document): a net loss of $53.4 million
- 反证 [ev_524a1844a1768d9c](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): Net loss $ ( 60,357 ) $ ( 39,885 )
- 反证 [ev_b201df1be52825f1](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): The Company utilizes contract manufacturers in China and Vietnam to supply key sub-assemblies for its primary products.
- 反证 [ev_8ebe184790963d01](https://www.accessdata.fda.gov/cdrh_docs/pdf26/K261712.pdf) (primary-document): Primary Predicate Device encevis (K240993) Subject Device Ceribell EEG Analysis Software
- 证伪条件：收入增速跌破 25%
- 证伪条件：NTAP 到期后医院使用量下降
- 证伪条件：竞品已获许可的自动癫痫检测功能（如 encevis）进入 ICU 和急诊快速脑电场景并获得报销

### management_governance: partial

向担任董事的联合创始人支付咨询费，属关联交易。

- 反证 [ev_c34e66b839867cf2](https://www.sec.gov/Archives/edgar/data/1861107/000119312526445555/cbll-20260930.htm) (primary-document): The Company paid Dr. Parvizi, a Director and Co-Founder of the Company, for consulting services
- 缺口：管理层变动与内部人交易

## CERT · complete

审查记录：`state/serenity-reviews/CERT-claude-afc2ad29a1ac8b932be4.json`

### supply_chain_map: pass

软件托管依赖第三方云；客户覆盖药企及动物健康、作物科学、医疗器械与公共部门。

- 支持 [ev_908db466aee571e2](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): We rely on third-party providers of cloud-based infrastructure to host our software solutions.
- 支持 [ev_cf5fbd4acc8be4bf](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): Certara serves customers in animal health, crop science, bio science, medical devices, and public sector industries.

### chokepoint_evidence: partial

软件被全球 20 家药品监管机构采用，验证模型构成进入壁垒；但生物模拟软件竞争者众多。

- 支持 [ev_cf5fbd4acc8be4bf](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): our software products are licensed by 20 global drug regulatory agencies, including the FDA
- 支持 [ev_8963cefef9a14d9e](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): presents a significant barrier to new entrants
- 反证 [ev_8963cefef9a14d9e](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): In the biosimulation software market, we compete with other technology companies including Mathworks, Dassault Systemes, Ansys, Simulations Plus, and NONMEM, a division of ICON.

### customer_dependency: pass

客户分散，无单一客户超过 10%，前十大客户占 24%。

- 支持 [ev_cf5fbd4acc8be4bf](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): No single customer accounted for more than 10% of our revenues in 2025. Our ten largest customers accounted for 24% and 27% of revenues for the years ended December 31, 2025 and 2024, respectively.

### pure_play: partial

AI 与机器学习正在融入软件和咨询业务，核心仍是生物模拟。

- 支持 [ev_b6ce57ff4b596a63](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): Native AI and machine learning technologies are being incorporated across our technology and consulting services portfolios
- 缺口：AI 相关收入占比

### multi_node_control: pass

同时提供生物模拟软件、技术服务和数据解决方案。

- 支持 [ev_02bd716b7440cfb9](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): We compete in both the biosimulation software market and technology-enabled services markets
- 支持 [ev_88032f0015d0fffa](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000035/cert-20260930.htm) (primary-document): These data solutions are used internally and industry wide by life sciences companies.

### earnings_validation: partial

2025 年收入增长 3,370 万美元，但缺少 2026 年持续经营业务增速原文。

- 支持 [ev_68880b5de0228bdb](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): The increase in net income was primarily due to a $33.7 million increase in revenue
- 缺口：2026 年持续经营业务增速原文

### counter_thesis: pass

债务与客户研发预算受药价政策压力的风险已检验。

- 支持 [ev_320cfdc614346f79](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): Our ten largest customers accounted for 24% of revenues for the year ended December 31, 2025.
- 反证 [ev_661f37534d062aa1](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): we had $295.5 million in total borrowings under our credit agreement
- 反证 [ev_5ea537e86fb6228b](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): may continue to have an economic impact on the incentive structure related to drug development R&D spending by our customers
- 证伪条件：软件续约率下降
- 证伪条件：监管机构转向开源或自研工具

### management_governance: partial

内控审计按 PCAOB 标准执行；未取得管理层变动材料。

- 支持 [ev_1fd67db884a4d0a1](https://www.sec.gov/Archives/edgar/data/1827090/000182709026000011/cert-20251231.htm) (primary-document): We conducted our audit in accordance with the standards of the PCAOB.
- 缺口：管理层变动与内部人交易

## FRNM · complete

审查记录：`state/serenity-reviews/FRNM-codex-a454d7049bb9f869f377.json`

### supply_chain_map: unknown

证据包没有提供公司产品、上游投入与下游使用者之间的具体关系；财务汇总数字不能替代供应链映射。

- 缺口：具体产品和服务
- 缺口：上游关键输入及供应商
- 缺口：下游客户、工作流和替代周期
- 证伪条件：原始披露显示候选公司与目标主题没有直接产品或服务联系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

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

- 支持 [ev_e2d167121f6eb775](https://data.sec.gov/api/xbrl/companyfacts/CIK0002017526.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for FREENOME, INC.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 183,489,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-12, accession 0002017526-26-000027. Same period a year earlier (2025-07-01 to 2025-09-30): 1,035,000, a change of +17628.4%. Net income (loss) (NetIncomeLoss): 60,110,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_e2d167121f6eb775](https://data.sec.gov/api/xbrl/companyfacts/CIK0002017526.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for FREENOME, INC.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 183,489,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-12, accession 0002017526-26-000027. Same period a year earlier (2025-07-01 to 2025-09-30): 1,035,000, a c
- 反证 [ev_e2d167121f6eb775](https://data.sec.gov/api/xbrl/companyfacts/CIK0002017526.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 60,110,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-12, accession 0002017526-26-000027. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -297,852 for 2026-01-01 to 2026-03-31; form 10-Q filed 2026-05-13, accession 0001140361-26-021083. Cash and equivalents (CashAndCashEquivalentsAtCarryingValue
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

## GEHC · complete

审查记录：`state/serenity-reviews/GEHC-claude-6b92fd32763cb750bb26.json`

### supply_chain_map: partial

有多个尚无替代的单一来源供应商，部分分子影像药物依赖合同生产；文件未点名具体供应商。

- 支持 [ev_bc7ea4b2c6246eda](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): we have multiple single-source or sole-source suppliers with no alternatives yet identified
- 支持 [ev_943aaec6ecb44ea5](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): we rely on contract manufacturing organizations to produce certain of our molecular imaging pharmaceutical products
- 缺口：具体单一来源供应商名称

### chokepoint_evidence: partial

FDA 在 K261623 中一并许可了预定变更控制计划（PCCP），AI 模型后续更新无需每次重新申报，这是运营上的优势；但本次许可的对比器械是其自身上一版本（实质等同，增量更新），且影像设备市场有西门子、飞利浦、联影、迈瑞、佳能等多家竞争，不构成瓶颈。

- 支持 [ev_88a5c770f987c518](https://www.accessdata.fda.gov/cdrh_docs/pdf26/K261623.pdf) (primary-document): FDA's substantial equivalence determination also included the review and clearance of your Predetermined Change Control Plan (PCCP)
- 反证 [ev_03410c43b7e4e668](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): we believe our primary global competitors include Siemens Healthineers, Philips Healthcare, United Imaging, Mindray, and Canon
- 反证 [ev_a93cabc35ec118b8](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K261623) (primary-document): Decision Substantially Equivalent (SESE)
- 缺口：装机份额数据

### customer_dependency: pass

2023–2025 年没有任何单一客户收入占比超过 10%。

- 支持 [ev_3a8c162af6f6efb6](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): No single customer accounted for more than 10% of the Company’s revenues for the years ended December 31, 2025, 2024, or 2023.

### pure_play: partial

AI 是影像设备和软件上的功能（如 EchoPAC 的 AI 多普勒周期检测模型）；另有 29 亿美元的药物诊断业务与 AI 无关。

- 支持 [ev_bef783495eb0e72a](https://www.accessdata.fda.gov/cdrh_docs/pdf26/K261623.pdf) (primary-document): through an AI Doppler Spectrum Cycle Detection model
- 反证 [ev_3a8c162af6f6efb6](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): Total PDx 2,900 2,508 2,306
- 缺口：AI 或软件收入占比

### multi_node_control: pass

同时覆盖影像硬件、影像软件与工作流（收购 Intelerad）以及 PET 放射性药物生产（拟收购 SOFIE）。

- 支持 [ev_300d7b5289efa156](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000059/gehc-20260930.htm) (primary-document): Intelerad is a leading medical imaging software and digital enterprise workflow solutions company
- 支持 [ev_a0b3c2bca45dc7ae](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000059/gehc-20260930.htm) (primary-document): we announced an agreement to acquire SOFIE Biosciences, a U.S.-based contract manufacturing organization for positron emission tomography

### earnings_validation: pass

2025 年收入 206 亿美元（2024 年 197 亿），自由现金流 15 亿美元；增长温和，约 5%。

- 支持 [ev_3a8c162af6f6efb6](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): Total revenues $ 20,625 $ 19,672 $ 19,552
- 支持 [ev_ba2085450ea1ee13](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): Free cash flow* $ 1,505 $ 1,554

### counter_thesis: pass

已检验：95 亿美元优先票据、GE 合并报税期间可能的 IRS 追税、中国市场与关税；FDA 摘要显示本次许可为自身上一版本的增量更新。

- 支持 [ev_ba2085450ea1ee13](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): We have historically generated positive cash flows from operating activities.
- 反证 [ev_e1996a7230aa42b7](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000059/gehc-20260930.htm) (primary-document): $ 9,500 million aggregate principal amount of senior unsecured notes
- 反证 [ev_1e2e30994e6705c7](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000059/gehc-20260930.htm) (primary-document): may assert a material amount of additional taxes and penalties
- 反证 [ev_f3649da393b07c72](https://www.accessdata.fda.gov/cdrh_docs/pdf26/K261623.pdf) (primary-document): have identical clinical indications for use
- 证伪条件：有机收入增长连续两个季度低于 3%
- 证伪条件：中国采购持续下滑
- 证伪条件：AI 和软件收入长期不单独披露、无法验证增长

### management_governance: partial

首席科学与技术官主导 AI 影像战略；但与 GE 的税务协议存在分拆被认定为应税交易时的赔偿风险。

- 支持 [ev_36852a1d5d5ad7ab](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): he is driving advancements in AI-based medical imaging, diagnostics, and health system operational efficiency
- 反证 [ev_a9f04dd526a6dc1b](https://www.sec.gov/Archives/edgar/data/1932393/000193239326000007/gehc-20251231.htm) (primary-document): If the Spin-Off is determined to be a taxable transaction, it could result in significant tax liability to GE and its stockholders

## GENB · complete

审查记录：`state/serenity-reviews/GENB-codex-726e01202df10c99f307.json`

### supply_chain_map: unknown

证据包没有提供公司产品、上游投入与下游使用者之间的具体关系；财务汇总数字不能替代供应链映射。

- 缺口：具体产品和服务
- 缺口：上游关键输入及供应商
- 缺口：下游客户、工作流和替代周期
- 证伪条件：原始披露显示候选公司与目标主题没有直接产品或服务联系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

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

- 支持 [ev_491cddc8d7829376](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Generate Biomedicines, Inc.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 4,220,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-12, accession 0001193125-26-456890. Same period a year earlier (2025-07-01 to 2025-09-30): 9,634,000, a change of -56.2%. Net income (loss) (NetIncomeLoss): -87,657,000 for 2026-07-01 to 2026-09-30; form 10-Q filed
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_491cddc8d7829376](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Generate Biomedicines, Inc.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 4,220,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-12, accession 0001193125-26-456890. Same period a year earlier (2025-07-01 to 2025-09-30): 9,6
- 反证 [ev_491cddc8d7829376](https://data.sec.gov/api/xbrl/companyfacts/CIK0002100782.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -87,657,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-12, accession 0001193125-26-456890. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -80,388,000 for 2026-01-01 to 2026-03-31; form 10-Q filed 2026-05-07, accession 0001193125-26-210059. Cash and equivalents (CashAndCashEquivalentsAtCarryingV
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

## GH · complete

审查记录：`state/serenity-reviews/GH-codex-605c9cad3a410d0899dc.json`

### supply_chain_map: partial

材料能够定位公司的产品/平台或监管产品，但没有完整覆盖上游关键输入、下游使用者和替代周期，供应链图仍不完整。

- 支持 ev_386dd823699061ae (local-unverified-notes): {"rank": 7, "ticker": "GH", "company": "Guardant Health", "classification": "scaled precision-oncology challenger", "thesis": "Guardant controls multiple precision-oncology nodes—advanced cancer testing, recurrence monitoring, screening and
- 缺口：补齐上游输入、供应集中度、下游付费用户与替代时间
- 证伪条件：关键上游或下游关系无法由原始材料确认

### chokepoint_evidence: partial

现有材料提出数据、软件或产品组合可能形成卡位，但没有原始证据证明供应集中度、市场份额或多年替代障碍，不能把 AI 相关性当作瓶颈。

- 支持 ev_386dd823699061ae (local-unverified-notes): {"rank": 7, "ticker": "GH", "company": "Guardant Health", "classification": "scaled precision-oncology challenger", "thesis": "Guardant controls multiple precision-oncology nodes—advanced cancer testing, recurrence monitoring, screening and
- 缺口：需要市场份额、替代成本、重新认证周期或独家数据权利的原始证据
- 证伪条件：竞争者可在较短时间复制数据/模型/产品能力
- 证伪条件：客户可低成本切换或自建同类能力

### customer_dependency: partial

本地研究材料描述了客户或合作方使用场景，但尚缺可独立核验的客户收入、续约率或依赖比例，因此合作关系不能等同客户收入。

- 支持 ev_386dd823699061ae (local-unverified-notes): {"rank": 7, "ticker": "GH", "company": "Guardant Health", "classification": "scaled precision-oncology challenger", "thesis": "Guardant controls multiple precision-oncology nodes—advanced cancer testing, recurrence monitoring, screening and
- 缺口：补充客户原始披露、续约/扩张及收入贡献
- 缺口：区分合作公告、试用与付费生产使用
- 证伪条件：合作方停止推进项目或不再续约
- 证伪条件：客户增长未带来收入和现金流改善

### pure_play: partial

候选与 AI 医疗主题存在直接业务联系，但当前材料没有以统一口径拆分 AI 医疗收入占比；业务纯度只能暂定为部分验证。

- 支持 ev_386dd823699061ae (local-unverified-notes): {"rank": 7, "ticker": "GH", "company": "Guardant Health", "classification": "scaled precision-oncology challenger", "thesis": "Guardant controls multiple precision-oncology nodes—advanced cancer testing, recurrence monitoring, screening and
- 缺口：补充按业务线收入、毛利和资本投入的原始分部披露
- 证伪条件：AI 医疗相关收入长期占比很低或被其他业务稀释

### multi_node_control: partial

材料显示公司覆盖多个产品、数据或工作流环节，但“多产品”不自动等于控制两个相连的供应链节点；控制权和节点间依赖仍需原始材料确认。

- 支持 ev_386dd823699061ae (local-unverified-notes): {"rank": 7, "ticker": "GH", "company": "Guardant Health", "classification": "scaled precision-oncology challenger", "thesis": "Guardant controls multiple precision-oncology nodes—advanced cancer testing, recurrence monitoring, screening and
- 缺口：证明至少两个相连节点的所有权、定价权或客户切换障碍
- 证伪条件：多个产品之间没有共享数据、客户锁定或经济协同

### earnings_validation: pass

已取得带日期的季度原始财务披露，可验证收入、利润/亏损及现金等实际结果；这只通过财报验证流程，不代表投资结论通过。

- 支持 [ev_b5f804beef810b67](https://data.sec.gov/api/xbrl/companyfacts/CIK0001576280.json) (sec-companyfacts): us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax: 360.975 USD_m; period 2026-07-01 to 2026-09-30; filed 2026-11-05; form 10-Q; accession 0001576280-26-000044. us-gaap:NetIncomeLoss: -124.362 USD_m; period 2026-07-01 to 2026-09-30
- 证伪条件：后续季度收入或客户增长失速
- 证伪条件：亏损、现金消耗或稀释趋势恶化

### counter_thesis: pass

已用原始财务结果检验增长叙事，并保留需求、替代、现金消耗、稀释和商业化失败等反方路径；通过表示反方已被审查，不表示风险消失。

- 支持 [ev_b5f804beef810b67](https://data.sec.gov/api/xbrl/companyfacts/CIK0001576280.json) (sec-companyfacts): us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax: 360.975 USD_m; period 2026-07-01 to 2026-09-30; filed 2026-11-05; form 10-Q; accession 0001576280-26-000044. us-gaap:NetIncomeLoss: -124.362 USD_m; period 2026-07-01 to 2026-09-30
- 反证 [ev_b5f804beef810b67](https://data.sec.gov/api/xbrl/companyfacts/CIK0001576280.json) (sec-companyfacts): us-gaap:NetIncomeLoss: -124.362 USD_m; period 2026-07-01 to 2026-09-30; filed 2026-11-05; form 10-Q; accession 0001576280-26-000044. us-gaap:ResearchAndDevelopmentExpense: 100.838 USD_m; period 2026-07-01 to 2026-09-30; filed 2026-11-05; fo
- 证伪条件：收入增长不能转化为持续毛利和现金流
- 证伪条件：客户或合作方停止扩张/推进
- 证伪条件：竞争者或客户自建替代能力
- 证伪条件：融资稀释吸收大部分业务增长价值

### management_governance: unknown

证据包没有充分的董事会、关键管理层连续性、内部控制或未决调查材料，不能推定治理通过。

- 缺口：补充最新代理声明、管理层变动、内部控制和重大调查披露
- 证伪条件：出现未解决的领导层继任、内部控制缺陷或监管调查

## GLUE · complete

审查记录：`state/serenity-reviews/GLUE-codex-f19158b8fac60bf4392f.json`

### supply_chain_map: unknown

证据包没有提供公司产品、上游投入与下游使用者之间的具体关系；财务汇总数字不能替代供应链映射。

- 缺口：具体产品和服务
- 缺口：上游关键输入及供应商
- 缺口：下游客户、工作流和替代周期
- 证伪条件：原始披露显示候选公司与目标主题没有直接产品或服务联系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

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

- 支持 [ev_c8354eef74ca189e](https://data.sec.gov/api/xbrl/companyfacts/CIK0001826457.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Monte Rosa Therapeutics, Inc.. Revenue (RevenueFromContractWithCustomerIncludingAssessedTax): 54,366,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05, accession 0001193125-26-448568. Same period a year earlier (2025-07-01 to 2025-09-30): 12,768,000, a change of +325.8%. Net income (loss) (NetIncomeLoss): 3,063,000 for 2026-07-01 to 2026-09-30; form 10-Q fi
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_c8354eef74ca189e](https://data.sec.gov/api/xbrl/companyfacts/CIK0001826457.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Monte Rosa Therapeutics, Inc.. Revenue (RevenueFromContractWithCustomerIncludingAssessedTax): 54,366,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05, accession 0001193125-26-448568. Same period a year earlier (2025-07-01 to 2025-09-30):
- 反证 [ev_c8354eef74ca189e](https://data.sec.gov/api/xbrl/companyfacts/CIK0001826457.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 3,063,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05, accession 0001193125-26-448568. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -37,369,000 for 2026-01-01 to 2026-03-31; form 10-Q filed 2026-05-07, accession 0001193125-26-210358. Cash and equivalents (CashAndCashEquivalentsAtCarryingVal
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

## GRAL · complete

审查记录：`state/serenity-reviews/GRAL-codex-9f02279a4410e65690fa.json`

### supply_chain_map: unknown

证据包没有提供公司产品、上游投入与下游使用者之间的具体关系；财务汇总数字不能替代供应链映射。

- 缺口：具体产品和服务
- 缺口：上游关键输入及供应商
- 缺口：下游客户、工作流和替代周期
- 证伪条件：原始披露显示候选公司与目标主题没有直接产品或服务联系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

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

- 支持 [ev_3d2b456fde3e8cf3](https://data.sec.gov/api/xbrl/companyfacts/CIK0001699031.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for GRAIL, Inc.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 37,535,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05, accession 0001628280-26-071041. Same period a year earlier (2025-07-01 to 2025-09-30): 36,194,000, a change of +3.7%. Net income (loss) (NetIncomeLoss): -103,568,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05, a
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_3d2b456fde3e8cf3](https://data.sec.gov/api/xbrl/companyfacts/CIK0001699031.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for GRAIL, Inc.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 37,535,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05, accession 0001628280-26-071041. Same period a year earlier (2025-07-01 to 2025-09-30): 36,194,000, a chan
- 反证 [ev_3d2b456fde3e8cf3](https://data.sec.gov/api/xbrl/companyfacts/CIK0001699031.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -103,568,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-05, accession 0001628280-26-071041. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -86,989,000 for 2026-01-01 to 2026-03-31; form 10-Q filed 2026-05-07, accession 0001628280-26-032090. Cash and equivalents (CashAndCashEquivalentsAtCarrying
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

## GSK · complete

审查记录：`state/serenity-reviews/GSK-codex-e6238ddf7ea6fcb83b69.json`

### supply_chain_map: partial

一手材料只能确认公司拥有一个受监管产品节点，尚未给出上游关键输入、制造依赖、下游付费使用者和替代周期，供应链图不完整。

- 支持 [ev_22b9a340187909c2](http://www.fda.gov/drugs/cancer-approvals/fda-expands-endometrial-cancer-indication-dostarlimab-gxly-chemotherapy) (primary-feed): On August 1, 2024, the Food and Drug Administration approved dostarlimab-gxly (Jemperli, GSK) with carboplatin and paclitaxel, followed by single-agent dostarlimab-gxly, for adult patients with primary advanced or recurrent endometrial cancer (EC).
- 缺口：上游关键供应商与集中度
- 缺口：下游付费客户及使用场景
- 缺口：替代供应商和重新认证周期
- 证伪条件：后续原始披露显示公司并不控制该产品或关键生产环节
- 证伪条件：主要客户可在较短周期内切换到替代方案

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

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

SEC一手材料只提供研发费用等有限财务项目，缺少同期收入、利润、现金流及目标主题贡献，不能完整验证投资论点。

- 支持 [ev_740a68a43710854e](https://data.sec.gov/api/xbrl/companyfacts/CIK0001131399.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for GSK plc. R&D expense (ResearchAndDevelopmentExpense): 7,525,000,000 for 2025-01-01 to 2025-12-31; form 20-F filed 2026-03-06, accession 0001131399-26-000004.
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_740a68a43710854e](https://data.sec.gov/api/xbrl/companyfacts/CIK0001131399.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for GSK plc. R&D expense (ResearchAndDevelopmentExpense): 7,525,000,000 for 2025-01-01 to 2025-12-31; form 20-F filed 2026-03-06, accession 0001131399-26-000004.
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

## HIMS · complete

审查记录：`state/serenity-reviews/HIMS-codex-097781917384eca9514c.json`

### supply_chain_map: unknown

证据包没有提供公司产品、上游投入与下游使用者之间的具体关系；财务汇总数字不能替代供应链映射。

- 缺口：具体产品和服务
- 缺口：上游关键输入及供应商
- 缺口：下游客户、工作流和替代周期
- 证伪条件：原始披露显示候选公司与目标主题没有直接产品或服务联系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

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

- 支持 [ev_d07d5ae89ea0d6c2](https://data.sec.gov/api/xbrl/companyfacts/CIK0001773751.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for HIMS & HERS HEALTH, INC.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 890,373,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-09, accession 0001773751-26-000246. Same period a year earlier (2025-07-01 to 2025-09-30): 598,976,000, a change of +48.6%. Net income (loss) (NetIncomeLoss): -33,040,000 for 2026-07-01 to 2026-09-30; form 10-Q file
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_d07d5ae89ea0d6c2](https://data.sec.gov/api/xbrl/companyfacts/CIK0001773751.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for HIMS & HERS HEALTH, INC.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 890,373,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-09, accession 0001773751-26-000246. Same period a year earlier (2025-07-01 to 2025-09-30): 598,
- 反证 [ev_d07d5ae89ea0d6c2](https://data.sec.gov/api/xbrl/companyfacts/CIK0001773751.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -33,040,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-09, accession 0001773751-26-000246. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): 89,356,000 for 2026-01-01 to 2026-03-31; form 10-Q filed 2026-05-11, accession 0001773751-26-000076. Cash and equivalents (CashAndCashEquivalentsAtCarryingVa
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

## HNGE · complete

审查记录：`state/serenity-reviews/HNGE-codex-9d1a5bebea532d2368bb.json`

### supply_chain_map: unknown

证据包没有提供公司产品、上游投入与下游使用者之间的具体关系；财务汇总数字不能替代供应链映射。

- 缺口：具体产品和服务
- 缺口：上游关键输入及供应商
- 缺口：下游客户、工作流和替代周期
- 证伪条件：原始披露显示候选公司与目标主题没有直接产品或服务联系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

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

- 支持 [ev_b912c0f8350cb2b8](https://data.sec.gov/api/xbrl/companyfacts/CIK0001673743.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Hinge Health, Inc.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 234,970,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-09, accession 0001628280-26-072251. Same period a year earlier (2025-07-01 to 2025-09-30): 154,211,000, a change of +52.4%. Net income (loss) (NetIncomeLoss): 57,398,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_b912c0f8350cb2b8](https://data.sec.gov/api/xbrl/companyfacts/CIK0001673743.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Hinge Health, Inc.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 234,970,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-09, accession 0001628280-26-072251. Same period a year earlier (2025-07-01 to 2025-09-30): 154,211,00
- 反证 [ev_b912c0f8350cb2b8](https://data.sec.gov/api/xbrl/companyfacts/CIK0001673743.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 57,398,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-09, accession 0001628280-26-072251. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): 43,083,000 for 2026-01-01 to 2026-03-31; form 10-Q filed 2026-05-07, accession 0001628280-26-032224. Cash and equivalents (CashAndCashEquivalentsAtCarryingVal
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

## HTFL · complete

审查记录：`state/serenity-reviews/HTFL-claude-10d20708762b7ba02257.json`

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

### management_governance: unknown

未取得治理相关一手材料。

- 缺口：董事会与内部人交易材料

## IMTX · complete

审查记录：`state/serenity-reviews/IMTX-codex-163665d453612f41d02c.json`

### supply_chain_map: unknown

证据包没有提供公司产品、上游投入与下游使用者之间的具体关系；财务汇总数字不能替代供应链映射。

- 缺口：具体产品和服务
- 缺口：上游关键输入及供应商
- 缺口：下游客户、工作流和替代周期
- 证伪条件：原始披露显示候选公司与目标主题没有直接产品或服务联系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

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

SEC一手材料只提供研发费用等有限财务项目，缺少同期收入、利润、现金流及目标主题贡献，不能完整验证投资论点。

- 支持 [ev_f2166e01ee55f174](https://data.sec.gov/api/xbrl/companyfacts/CIK0001809196.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Immatics N.V.. R&D expense (ResearchAndDevelopmentExpense): 45,106,000 for 2025-04-01 to 2025-06-30; form 6-K filed 2025-08-13, accession 0001193125-25-179419.
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_f2166e01ee55f174](https://data.sec.gov/api/xbrl/companyfacts/CIK0001809196.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Immatics N.V.. R&D expense (ResearchAndDevelopmentExpense): 45,106,000 for 2025-04-01 to 2025-06-30; form 6-K filed 2025-08-13, accession 0001193125-25-179419.
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

## IQV · complete

审查记录：`state/serenity-reviews/IQV-codex-7789f3991e769b40cdd1.json`

### supply_chain_map: unknown

SEC财务事实未提供数据、临床试验运营和客户之间的具体依赖关系。

- 缺口：数据来源、产品、制药客户和试验网络关系
- 证伪条件：AI只用于内部效率而非客户工作流

### chokepoint_evidence: unknown

缺少数据独占性、替代周期和市场集中度证据。

- 缺口：数据权利、切换成本和竞争份额
- 证伪条件：客户可使用其他CRO或数据平台低成本替代

### customer_dependency: unknown

未取得客户留存、合同依赖或AI代理采用的原始证据。

- 缺口：续约、积压订单转换和AI客户使用
- 证伪条件：AI部署不改善预订、留存或利润率

### pure_play: unknown

合并财务没有拆分AI收入，不能将IQVIA视作纯AI医疗公司。

- 缺口：AI相关收入和分部利润
- 证伪条件：AI商业收入长期不可量化

### multi_node_control: unknown

尚未用原始材料证明公司控制两个相连且不可替代的节点。

- 缺口：数据、软件和临床运营之间的控制证据
- 证伪条件：多项服务不能形成定价权或客户锁定

### earnings_validation: pass

SEC 10-Q XBRL验证2026年第三季度收入、净利润、现金与股本。

- 支持 [ev_b7e376b53d891874](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478242.json) (sec-companyfacts): us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax: 4428.0 USD_m; period 2026-07-01 to 2026-09-30; filed 2026-10-27; form 10-Q;
- 证伪条件：订单转换、利润或现金流显著恶化

### counter_thesis: partial

当前只验证了合并财务，尚未验证AI能否带来增量收入，也未完成杠杆和CRO竞争压力测试。

- 支持 [ev_b7e376b53d891874](https://data.sec.gov/api/xbrl/companyfacts/CIK0001478242.json) (sec-companyfacts): us-gaap:NetIncomeLoss: 350.0 USD_m; period 2026-07-01 to 2026-09-30; filed 2026-10-27; form 10-Q;
- 缺口：净债务、竞争、AI收入归因和情景估值原始证据
- 证伪条件：AI采用增加但预订、增长和利润率无改善

### management_governance: unknown

证据包没有治理和关键管理层材料。

- 缺口：董事会、薪酬和继任材料
- 证伪条件：关键人或治理问题影响执行

## ISRG · complete

审查记录：`state/serenity-reviews/ISRG-claude-f7aa57a0b79407640b75.json`

### supply_chain_map: partial

上游有单一来源供应商和半导体元件，器械主要在墨西哥生产；下游为医院。文件未点名具体单一来源供应商。

- 支持 [ev_0d50e423901fc8cc](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): our reliance on sole- and single-sourced suppliers; extended lead times and price volatility for certain semiconductor components
- 支持 [ev_b586207f4a6a42f4](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): including Mexico, where we currently manufacture a significant majority of our instruments
- 缺口：具体单一来源供应商名称与占比

### chokepoint_evidence: partial

装机量和手术量形成生态壁垒，法院认定机器人与 EndoWrist 器械是独立产品市场；但面临其他机器人系统竞争，中国尤其明显。

- 支持 [ev_67a03ce9e3f68507](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): Approximately 906,000 da Vinci procedures were performed during the three months ended September 30, 2026, a growth of 14%
- 支持 [ev_549d4233cc9e99d5](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): the da Vinci robot and EndoWrist instruments occupy separate product markets for antitrust purposes
- 反证 [ev_0d50e423901fc8cc](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): competition from companies offering alternative surgical approaches or robotic-assisted surgical systems, including domestic competitors in certain geographic markets, such as China
- 缺口：市场份额数据

### customer_dependency: partial

客户是大量医院，2025 年手术量 315 万例、增长 18%，不依赖单一客户；但医院采购取决于手术的医保报销。

- 支持 [ev_b85513e6cd59683f](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): Approximately 3,153,000 da Vinci procedures were performed during the year ended December 31, 2025, an increase of 18%
- 反证 [ev_6afb0ad2697c750a](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): If hospitals are unable to obtain coverage and reimbursement for procedures using our products
- 缺口：客户集中度数据

### pure_play: partial

核心是手术机器人硬件与器械，AI 是功能（如 Ion 导航中的 AI），不是收入来源。

- 支持 [ev_4ae70e53fe20ca64](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): This software release introduces artificial intelligence across Ion’s entire navigational workflow
- 反证 [ev_437b70334681bd1e](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): Systems revenue increased 26% to $2.47 billion in 2025

### multi_node_control: pass

同时控制系统、器械与耗材生产，并从手术延伸到肺部活检诊断。

- 支持 [ev_716d14fc246fd11b](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): Our Ion system extends our commercial offering beyond surgery into diagnostic, endoluminal procedures
- 支持 [ev_b586207f4a6a42f4](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): where we currently manufacture a significant majority of our instruments

### earnings_validation: pass

Q3 2026 收入增长 22% 至 30.5 亿美元；2025 年收入增长 21% 至 101 亿美元。

- 支持 [ev_67a03ce9e3f68507](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): Total revenue increased by 22% to $3.05 billion for the three months ended September 30, 2026
- 支持 [ev_b85513e6cd59683f](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000010/isrg-20251231.htm) (primary-document): Total revenue increased by 21% to $10.1 billion for the year ended December 31, 2025

### counter_thesis: pass

已检验：反垄断和解（4.5 亿美元并附禁令救济，可能放开第三方器械维修）、中国集采与统一定价、其他机器人竞争；另有估值约 14 倍收入（非文件数据）。

- 支持 [ev_67a03ce9e3f68507](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): Approximately 906,000 da Vinci procedures were performed during the three months ended September 30, 2026, a growth of 14%
- 反证 [ev_7ceabab4b1ce220b](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): to settle the case for a one-time payment of $ 450 million and mutually agreed injunctive relief
- 反证 [ev_ebe1c0fd872fb8da](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): including the implementation of a unified national pricing framework in China
- 证伪条件：手术量增速连续两个季度低于装机量增速
- 证伪条件：和解的禁令救济让第三方器械明显挤压器械收入
- 证伪条件：中国统一定价导致海外系统收入下滑

### management_governance: partial

未见内控重大缺陷披露；但反垄断和解与禁令救济涉及商业行为约束。

- 反证 [ev_7ceabab4b1ce220b](https://www.sec.gov/Archives/edgar/data/1035267/000103526726000071/isrg-20260930.htm) (primary-document): The Company recorded a charge of $ 450 million in operating
- 缺口：管理层与董事会治理的一手材料

## MDT · complete

审查记录：`state/serenity-reviews/MDT-codex-3eea2742b8db86af7046.json`

### supply_chain_map: partial

一手材料只能确认公司拥有一个受监管产品节点，尚未给出上游关键输入、制造依赖、下游付费使用者和替代周期，供应链图不完整。

- 支持 [ev_58421c64da0963d6](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K253984) (fda-ai-device-list): FDA AI-enabled medical-device authorization record. Manufacturer: Covidien, LLC. Device: Instrument Exit Point on Touch Surgery Aide. Final decision date: 06/04/2026. This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：上游关键供应商与集中度
- 缺口：下游付费客户及使用场景
- 缺口：替代供应商和重新认证周期
- 证伪条件：后续原始披露显示公司并不控制该产品或关键生产环节
- 证伪条件：主要客户可在较短周期内切换到替代方案

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 反证 [ev_58421c64da0963d6](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K253984) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

- 反证 [ev_58421c64da0963d6](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K253984) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
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

- 支持 [ev_def963a1f9d4459f](https://data.sec.gov/api/xbrl/companyfacts/CIK0001613103.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Medtronic plc. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 9,756,000,000 for 2026-04-25 to 2026-07-31; form 10-Q filed 2026-09-03, accession 0001628280-26-060473. Net income (loss) (NetIncomeLoss): 1,470,000,000 for 2026-04-25 to 2026-07-31; form 10-Q filed 2026-09-03, accession 0001628280-26-060473. Operating cash flow (NetCashProvidedByUsedInOpera
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_def963a1f9d4459f](https://data.sec.gov/api/xbrl/companyfacts/CIK0001613103.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Medtronic plc. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 9,756,000,000 for 2026-04-25 to 2026-07-31; form 10-Q filed 2026-09-03, accession 0001628280-26-060473. Net income (loss) (NetIncomeLoss): 1,470,000,000 for 2026-04-25 to 2
- 反证 [ev_def963a1f9d4459f](https://data.sec.gov/api/xbrl/companyfacts/CIK0001613103.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 1,470,000,000 for 2026-04-25 to 2026-07-31; form 10-Q filed 2026-09-03, accession 0001628280-26-060473. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): 1,793,000,000 for 2026-04-25 to 2026-07-31; form 10-Q filed 2026-09-03, accession 0001628280-26-060473. Cash and equivalents (CashAndCashEquivalentsAtCarry
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

## MRNA · complete

审查记录：`state/serenity-reviews/MRNA-codex-33925e13f9cd064a8ee7.json`

### supply_chain_map: unknown

证据包没有提供公司产品、上游投入与下游使用者之间的具体关系；财务汇总数字不能替代供应链映射。

- 缺口：具体产品和服务
- 缺口：上游关键输入及供应商
- 缺口：下游客户、工作流和替代周期
- 证伪条件：原始披露显示候选公司与目标主题没有直接产品或服务联系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

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

- 支持 [ev_8715e1656e8d67cb](https://data.sec.gov/api/xbrl/companyfacts/CIK0001682852.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Moderna, Inc.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 1,313,000,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-06, accession 0001682852-26-000197. Same period a year earlier (2025-07-01 to 2025-09-30): 1,016,000,000, a change of +29.2%. Net income (loss) (NetIncomeLoss): 162,000,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_8715e1656e8d67cb](https://data.sec.gov/api/xbrl/companyfacts/CIK0001682852.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Moderna, Inc.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 1,313,000,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-06, accession 0001682852-26-000197. Same period a year earlier (2025-07-01 to 2025-09-30): 1,016,000,000
- 反证 [ev_8715e1656e8d67cb](https://data.sec.gov/api/xbrl/companyfacts/CIK0001682852.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 162,000,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-06, accession 0001682852-26-000197. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -630,000,000 for 2026-01-01 to 2026-03-31; form 10-Q filed 2026-05-01, accession 0001682852-26-000060. Cash and equivalents (CashAndCashEquivalentsAtCarrying
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

## NTRA · complete

审查记录：`state/serenity-reviews/NTRA-claude-5a95116a7374f13eb292.json`

### supply_chain_map: pass

依赖少数供应商（含单一来源），与医疗机构和合作实验室协作；收入集中于 Signatera、Panorama、Horizon 三类检测。

- 支持 [ev_7675e30791e81332](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): we rely on a limited number of suppliers or, in some cases, single suppliers, for some of our laboratory instruments and materials
- 支持 [ev_02fc1527388d0ba7](https://www.sec.gov/Archives/edgar/data/1604821/000162828026071145/ntra-20260930.htm) (primary-document): our reliance on collaborators such as medical institutions, contract laboratories, laboratory partners, and other third parties
- 支持 [ev_f6182999e5b3d226](https://www.sec.gov/Archives/edgar/data/1604821/000162828026071145/ntra-20260930.htm) (primary-document): a significant portion of our revenues will be derived from sales of Signatera, Panorama, and Horizon

### chokepoint_evidence: partial

Signatera 获 CMS 的 ADLT 资格，形成报销与证据壁垒；但肿瘤检测领域竞争者众多。

- 支持 [ev_d392a0ffd58f7b3c](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): Signatera has been granted Advanced Diagnostic Laboratory Test, or ADLT, status by the Centers for Medicare & Medicaid Services.
- 反证 [ev_e3ced510d33b526f](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): In the field of oncology, we compete with various companies that offer or seek to offer competing solutions

### customer_dependency: partial

商业保险覆盖政策提供需求支撑，但缺少客户或付款方集中度数据。

- 支持 [ev_d392a0ffd58f7b3c](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): Signatera is also covered under the coverage policies of certain commercial third-party payers
- 缺口：客户或付款方集中度数据

### pure_play: partial

AI 用于 Panorama 检测的结果判定，是诊断业务中的辅助组件，不是核心业务。

- 支持 [ev_542fcc92ed2cee28](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): Panorama leverages artificial intelligence to enable highly accurate results on samples for which a result would otherwise be difficult to determine.
- 缺口：AI 相关收入占比

### multi_node_control: partial

自建实验室并扩张产能，但证据包未显示对上游或数据节点的控制。

- 支持 [ev_02fc1527388d0ba7](https://www.sec.gov/Archives/edgar/data/1604821/000162828026071145/ntra-20260930.htm) (primary-document): our ability to operate our laboratory facilities and meet expected demand, and to successfully scale our operations
- 缺口：节点控制的一手证据

### earnings_validation: pass

2026 年前三季度经营活动现金流为正，约 1.389 亿美元。

- 支持 [ev_9de124c0c8e65367](https://www.sec.gov/Archives/edgar/data/1604821/000162828026071145/ntra-20260930.htm) (primary-document): Net cash provided by operating activities 138,895 141,413

### counter_thesis: pass

持续亏损、股权稀释与 FDA 监管 LDT 的风险已用原文检验。

- 支持 [ev_d1001d83c14f66fc](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): We have incurred net losses each year since our inception in 2003.
- 反证 [ev_ef0a31d0620a5fc6](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): investors in our common stock may be materially diluted.
- 反证 [ev_5aa0d9ebfea39992](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): if the FDA were to begin actively regulating our tests, we could incur substantial costs and delays
- 证伪条件：Signatera 检测量连续两个季度放缓
- 证伪条件：经营现金流转负

### management_governance: partial

2025 年内控有效；存在一笔 1,000 万美元的关联方投资。

- 支持 [ev_0d2d5c0b3c3ac202](https://www.sec.gov/Archives/edgar/data/1604821/000110465926020881/ntra-20251231x10k.htm) (primary-document): we determined that our internal controls over financial reporting were effective as of December 31, 2025
- 反证 [ev_9de124c0c8e65367](https://www.sec.gov/Archives/edgar/data/1604821/000162828026071145/ntra-20260930.htm) (primary-document): Investment in related party ( 10,000 )

## NVDA · complete

审查记录：`state/serenity-reviews/NVDA-codex-43148b6c2b66836e2775.json`

### supply_chain_map: unknown

现有材料主要涉及总体计算平台和公司事件，没有映射医疗算力的上游、产品和医疗客户链。

- 缺口：医疗客户、产品收入和供应关系
- 证伪条件：医疗工作负载不形成实质算力需求

### chokepoint_evidence: unknown

总体AI领导地位不能自动证明医疗行业特定瓶颈。

- 缺口：医疗算力份额、替代方案和切换周期
- 证伪条件：医疗模型可迁移到替代加速器且性能成本接近

### customer_dependency: unknown

未取得医疗客户对NVIDIA平台依赖的直接披露。

- 缺口：医疗客户采用、续约和工作负载证据
- 证伪条件：医疗客户降低NVIDIA平台集中度

### pure_play: unknown

SEC合并收入没有医疗分部归因，因此不能将NVDA作为纯AI医疗标的。

- 缺口：医疗行业收入占比
- 证伪条件：医疗收入对公司总增长长期不具实质性

### multi_node_control: unknown

现有证据没有直接验证医疗领域芯片、软件、模型和分发的跨节点控制。

- 缺口：医疗产品栈及客户采用原始证据
- 证伪条件：医疗软件生态无法带来持续平台锁定

### earnings_validation: pass

SEC 10-Q XBRL验证第二财季收入、净利润、研发和现金，但没有拆分医疗贡献。

- 支持 [ev_cb065d593daad7ba](https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json) (sec-companyfacts): us-gaap:Revenues: 96221.0 USD_m; period 2026-04-27 to 2026-07-26; filed 2026-08-26; form 10-Q;
- 证伪条件：总体增长或现金生成显著下降

### counter_thesis: partial

治理与继任事件构成明确反方风险；医疗收入归因、竞争和估值压力测试仍缺失。

- 支持 [ev_cb065d593daad7ba](https://data.sec.gov/api/xbrl/companyfacts/CIK0001045810.json) (sec-companyfacts): us-gaap:ResearchAndDevelopmentExpense: 7054.0 USD_m; period 2026-04-27 to 2026-07-26; filed 2026-08-26; form 10-Q;
- 反证 [ev_79e00ca107c914f4](https://nvidianews.nvidia.com/news/statement-from-nvidia-board-of-directors) (primary-document): The NVIDIA Board is initiating an independent investigation in light of recent reporting that founder and CEO Jensen Huang has been the target of a foreign intelligence effort.
- 缺口：医疗收入归因、竞争与估值情景
- 证伪条件：继任扰乱客户承诺或产品路线
- 证伪条件：医疗需求对总体收入不具实质贡献

### management_governance: pending

CEO已立即辞职、临时CEO兼任CFO且永久继任者搜索中；独立调查尚未完成，因此不能通过治理门槛。

- 支持 [ev_05d4ecc300e80577](https://nvidianews.nvidia.com/news/nvidia-announces-ceo-transition) (primary-document): Jensen Huang has resigned as President, Chief Executive Officer, and a member of the Board, effective immediately.
- 反证 [ev_79e00ca107c914f4](https://nvidianews.nvidia.com/news/statement-from-nvidia-board-of-directors) (primary-document): A committee of independent directors, assisted by outside independent counsel, will oversee the investigation.
- 缺口：永久CEO任命和独立调查结论
- 证伪条件：继任或调查导致客户、人才或路线图受损

## ODTX · complete

审查记录：`state/serenity-reviews/ODTX-codex-5eebb7c018082a51f1a6.json`

### supply_chain_map: unknown

证据包没有提供公司产品、上游投入与下游使用者之间的具体关系；财务汇总数字不能替代供应链映射。

- 缺口：具体产品和服务
- 缺口：上游关键输入及供应商
- 缺口：下游客户、工作流和替代周期
- 证伪条件：原始披露显示候选公司与目标主题没有直接产品或服务联系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

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

- 支持 [ev_6ff0cae5104a6bed](https://data.sec.gov/api/xbrl/companyfacts/CIK0001882782.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Odyssey Therapeutics, Inc.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 0 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04, accession 0001193125-26-446208. Same period a year earlier (2025-07-01 to 2025-09-30): 99,000, a change of -100.0%. Net income (loss) (NetIncomeLoss): -53,059,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_6ff0cae5104a6bed](https://data.sec.gov/api/xbrl/companyfacts/CIK0001882782.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Odyssey Therapeutics, Inc.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 0 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04, accession 0001193125-26-446208. Same period a year earlier (2025-07-01 to 2025-09-30): 99,000, a ch
- 反证 [ev_6ff0cae5104a6bed](https://data.sec.gov/api/xbrl/companyfacts/CIK0001882782.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -53,059,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04, accession 0001193125-26-446208. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -41,035,000 for 2026-01-01 to 2026-03-31; form 10-Q filed 2026-06-17, accession 0001193125-26-274290. Cash and equivalents (CashAndCashEquivalentsAtCarryingV
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

## PHG · complete

审查记录：`state/serenity-reviews/PHG-codex-57eb96cc85bc2c9b6959.json`

### supply_chain_map: partial

一手材料只能确认公司拥有一个受监管产品节点，尚未给出上游关键输入、制造依赖、下游付费使用者和替代周期，供应链图不完整。

- 支持 [ev_68747ca1c4ee58b4](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K260667) (fda-ai-device-list): FDA AI-enabled medical-device authorization record. Manufacturer: Philips Ultrasound, LLC. Device: Alturion Series Diagnostic Ultrasound System. Final decision date: 06/29/2026. This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：上游关键供应商与集中度
- 缺口：下游付费客户及使用场景
- 缺口：替代供应商和重新认证周期
- 证伪条件：后续原始披露显示公司并不控制该产品或关键生产环节
- 证伪条件：主要客户可在较短周期内切换到替代方案

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 反证 [ev_68747ca1c4ee58b4](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K260667) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

- 反证 [ev_68747ca1c4ee58b4](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K260667) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
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

SEC一手材料只提供研发费用等有限财务项目，缺少同期收入、利润、现金流及目标主题贡献，不能完整验证投资论点。

- 支持 [ev_2de534106acb0ae4](https://data.sec.gov/api/xbrl/companyfacts/CIK0000313216.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for KONINKLIJKE PHILIPS NV. R&D expense (ResearchAndDevelopmentExpense): 1,700,000,000 for 2025-01-01 to 2025-12-31; form 20-F filed 2026-02-19, accession 0001628280-26-009470.
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_2de534106acb0ae4](https://data.sec.gov/api/xbrl/companyfacts/CIK0000313216.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for KONINKLIJKE PHILIPS NV. R&D expense (ResearchAndDevelopmentExpense): 1,700,000,000 for 2025-01-01 to 2025-12-31; form 20-F filed 2026-02-19, accession 0001628280-26-009470.
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

## PRCT · complete

审查记录：`state/serenity-reviews/PRCT-codex-809522e452318cf3da26.json`

### supply_chain_map: partial

一手材料只能确认公司拥有一个受监管产品节点，尚未给出上游关键输入、制造依赖、下游付费使用者和替代周期，供应链图不完整。

- 支持 [ev_22e9714eed59588d](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K251082) (fda-ai-device-list): FDA AI-enabled medical-device authorization record. Manufacturer: Procept Biorobotics. Device: HYDROS Robotic System (HY1000); HYDROS Handpiece (HH1000); HYDROS TRUS Probe (HU1000). Final decision date: 10/10/2025. This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：上游关键供应商与集中度
- 缺口：下游付费客户及使用场景
- 缺口：替代供应商和重新认证周期
- 证伪条件：后续原始披露显示公司并不控制该产品或关键生产环节
- 证伪条件：主要客户可在较短周期内切换到替代方案

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 反证 [ev_22e9714eed59588d](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K251082) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

- 反证 [ev_22e9714eed59588d](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K251082) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
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

- 支持 [ev_045aac9f6409f567](https://data.sec.gov/api/xbrl/companyfacts/CIK0001588978.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for PROCEPT BioRobotics Corporation. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 98,291,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04, accession 0001588978-26-000039. Same period a year earlier (2025-07-01 to 2025-09-30): 83,327,000, a change of +18.0%. Net income (loss) (NetIncomeLoss): -26,516,000 for 2026-07-01 to 2026-09-30; form 10-Q
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_045aac9f6409f567](https://data.sec.gov/api/xbrl/companyfacts/CIK0001588978.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for PROCEPT BioRobotics Corporation. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 98,291,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04, accession 0001588978-26-000039. Same period a year earlier (2025-07-01 to 2025-09-30)
- 反证 [ev_045aac9f6409f567](https://data.sec.gov/api/xbrl/companyfacts/CIK0001588978.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -26,516,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-04, accession 0001588978-26-000039. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -38,127,000 for 2026-01-01 to 2026-03-31; form 10-Q filed 2026-04-30, accession 0001588978-26-000022. Cash and equivalents (CashAndCashEquivalentsAtCarryingV
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

## RDNT · complete

审查记录：`state/serenity-reviews/RDNT-claude-d77ec7d473d705adcb8f.json`

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

### management_governance: partial

采用由管理层成员拥有或控制的专业医疗公司结构。

- 反证 [ev_47a5e5371754fce4](https://www.sec.gov/Archives/edgar/data/790526/000162828026013337/rdnt-20251231.htm) (primary-document): professional corporations owned or controlled by individuals within our senior management

## RMD · complete

审查记录：`state/serenity-reviews/RMD-codex-3520f1b50fdea6175606.json`

### supply_chain_map: partial

一手材料只能确认公司拥有一个受监管产品节点，尚未给出上游关键输入、制造依赖、下游付费使用者和替代周期，供应链图不完整。

- 支持 [ev_36d245be83bd66ea](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K251657) (fda-ai-device-list): FDA AI-enabled medical-device authorization record. Manufacturer: ResMed Corp. Device: Personalized Therapy Comfort Settings (PTCS). Final decision date: 12/05/2025. This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：上游关键供应商与集中度
- 缺口：下游付费客户及使用场景
- 缺口：替代供应商和重新认证周期
- 证伪条件：后续原始披露显示公司并不控制该产品或关键生产环节
- 证伪条件：主要客户可在较短周期内切换到替代方案

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 反证 [ev_36d245be83bd66ea](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K251657) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

- 反证 [ev_36d245be83bd66ea](https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K251657) (fda-ai-device-list): This record supports regulatory product evidence only; it does not establish revenue contribution, customer dependence, competitive moat, or investment returns.
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

- 支持 [ev_722191f2fb8b4b52](https://data.sec.gov/api/xbrl/companyfacts/CIK0000943819.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for ResMed Inc.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 1,414,814,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-10-30, accession 0000943819-26-000089. Same period a year earlier (2025-07-01 to 2025-09-30): 1,335,582,000, a change of +5.9%. Net income (loss) (NetIncomeLoss): 418,413,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-10-
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_722191f2fb8b4b52](https://data.sec.gov/api/xbrl/companyfacts/CIK0000943819.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for ResMed Inc.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 1,414,814,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-10-30, accession 0000943819-26-000089. Same period a year earlier (2025-07-01 to 2025-09-30): 1,335,582,000,
- 反证 [ev_722191f2fb8b4b52](https://data.sec.gov/api/xbrl/companyfacts/CIK0000943819.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): 418,413,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-10-30, accession 0000943819-26-000089. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): 422,422,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-10-30, accession 0000943819-26-000089. Cash and equivalents (CashAndCashEquivalentsAtCarryingV
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

## RXRX · complete

审查记录：`state/serenity-reviews/RXRX-claude-3c8278defa245fc9dc35.json`

### supply_chain_map: pass

10-K 披露了上游（单一来源原料药、外包生产、云）与核心自动化实验室；下游合作方见客户依赖门槛。

- 支持 [ev_d1b984a1f3baa6ab](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): the API used in our drug candidates, are obtained from single-source suppliers.
- 支持 [ev_2c66309189a7721a](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): we have obtained drug substance and drug product for our drug candidates from third party contract manufacturers.
- 支持 [ev_54171fe3bfd7cb6c](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): using our automated high throughput labs, which can run over 2 million experiments per week

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

财报验证了合作研发收入与持续亏损，未验证“平台产出药物”的核心论点。

- 支持 [ev_05feddc7f23f26af](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): To date our operating revenue has primarily been generated through funded research and development agreements
- 反证 [ev_0477b1ddf6fb372b](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): We had an accumulated deficit of $2.1 billion as of December 31, 2025.

### counter_thesis: pass

稀释与供应链地缘风险已用原文检验；反方成立，不适合高确信度。

- 支持 [ev_535022fa432f7fca](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): our stockholders’ ownership interests will be diluted.
- 反证 [ev_b569305f0e41958b](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): we entered into a sales agreement for an at-the-market offering for the sale of up to $300 million
- 反证 [ev_4cb33424380b5eb5](https://www.sec.gov/Archives/edgar/data/1601830/000160183026000039/rxrx-20251231.htm) (primary-document): While the BIOSECURE Act as currently proposed would restrict purchasing of services or products from WuXi AppTec
- 证伪条件：REC-4881 注册性试验推迟到 2028 年以后
- 证伪条件：12 个月内再次融资

### management_governance: partial

新任董事长已任命；内部人交易与治理细节未在一手材料中核实。

- 缺口：董事会与内部人交易材料

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

审查记录：`state/serenity-reviews/SDGR-claude-378839e37fa0de8953f7.json`

### supply_chain_map: pass

下游覆盖学术机构与全部前 20 大药企；平台可扩展到云计算。

- 支持 [ev_f4c3bb2cfdef0862](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): more than 1,750 academic institutions
- 支持 [ev_65f6106d800b8a62](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): ability to scale these calculations to leverage large cloud computing environments

### chokepoint_evidence: partial

留存率高，接近工具层事实标准；但 AI 原生竞争者众多。

- 支持 [ev_30e5c6d64af2a165](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): our gross dollar retention rate for our commercial customers was 96%
- 反证 [ev_5dd7c574e5f263f6](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): Insilico Medicine, Inc., Iktos, XtalPi Inc., AbCellera, Inductive Bio, Inc.

### customer_dependency: pass

前 20 大药企贡献 37% 软件收入。

- 支持 [ev_7335aaf240a1105c](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): $73.7 million, or 37%, of our software revenue

### pure_play: pass

全部业务为计算驱动的药物发现。

- 支持 [ev_b7bcd6372d14612f](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): FEP+ is also able to perform these computations more rapidly than experimental assays.

### multi_node_control: pass

同时是软件供应商与药物开发者。

- 支持 [ev_7051cbfb03a4c7f5](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): We are advancing SGR-1505, our novel MALT1 inhibitor
- 支持 [ev_5c7f1c15dfa4ff2c](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): We are eligible to receive up to $2.272 billion in total milestones across the initial programs

### earnings_validation: partial

软件增长放缓（见备忘录），本证据包未纳入季报原文。

- 缺口：Q3 季报原文

### counter_thesis: pass

大客户数量下降等反方已检验。

- 支持 [ev_eb5e7b5a3b91d35c](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): The average ACV per commercial customer with an ACV of over $1.0 million grew to $3.9 million
- 反证 [ev_262dd4b4de7c4505](https://www.sec.gov/Archives/edgar/data/1490978/000149097826000010/sdgr-20251231.htm) (primary-document): we had 27 commercial customers with an ACV of at least $1.0 million
- 证伪条件：2027 年软件收入增速低于 5%

### management_governance: unknown

未取得治理相关一手材料。

- 缺口：董事会与内部人交易材料

## SOPH · complete

审查记录：`state/serenity-reviews/SOPH-claude-4938ef45189fb0c0e2db.json`

### supply_chain_map: pass

云服务为 Microsoft，平台兼容多家测序仪厂商。

- 支持 [ev_6c0ed12a395095d6](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): we currently use Microsoft Corporation
- 支持 [ev_e4677ecd16db9297](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): NGS test kits, sequencers and sample materials from different manufacturers

### chokepoint_evidence: partial

中立分析层有一定粘性，但同类供应商众多。

- 反证 [ev_89316529114e1993](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): There are a number of healthcare technology companies providing bioinformatics analysis solutions, applications, services, and products

### customer_dependency: partial

客户数与净收入留存率来自季度新闻稿，未纳入本证据包。

- 缺口：客户数与留存率的一手原文

### pure_play: pass

全部业务为临床基因组数据分析平台。

- 支持 [ev_e4677ecd16db9297](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): NGS test kits, sequencers and sample materials from different manufacturers

### multi_node_control: partial

控制分析平台与数据网络，不控制检测与报销环节。

- 缺口：节点控制的一手证据

### earnings_validation: partial

持续亏损，依赖融资。

- 支持 [ev_0643c1781bd8da3c](https://www.sec.gov/Archives/edgar/data/1840706/000162828026052125/soph-20260630_d2.htm) (primary-document): These unaudited interim condensed consolidated financial statements have been prepared on a going concern basis.

### counter_thesis: pass

融资与债务风险已检验。

- 支持 [ev_c77d49738f50e8b6](https://www.sec.gov/Archives/edgar/data/1840706/000162828026052125/soph-20260630_d2.htm) (primary-document): The Company was in full compliance with all covenants contained in the Perceptive Credit Agreement as of June 30, 2026.
- 反证 [ev_b4d80e773306d947](https://www.sec.gov/Archives/edgar/data/1840706/000184070626000006/soph-20251231.htm) (primary-document): pursuant to which we may sell, from time to time, ordinary shares having an aggregate offering price of $50.0 million
- 证伪条件：12 个月内再次融资
- 证伪条件：美国收入增速跌破 20%

### management_governance: unknown

CEO 变更未在一手材料中核实。

- 缺口：管理层变更公告

## TEM · complete

审查记录：`state/serenity-reviews/TEM-claude-eede2bc70941bb8f4342.json`

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

大药企有最低采购承诺。关联方收入见治理门槛。

- 支持 [ev_301169c868e74591](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): AstraZeneca has committed to spend a minimum of $220 million on such products and services
- 支持 [ev_fe9d7fb9829ebbaf](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): GSK has committed to spend a minimum of $180 million on such products and services

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

杠杆、医保与供应商集中风险已检验。

- 支持 [ev_e4009fd2d75ac3e1](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): Approximately 26% of our clinical oncology tests were for Medicare beneficiaries
- 反证 [ev_f11fdab9f02e2d4e](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): $750.0 million outstanding aggregate principal amount of 0.75% Convertible Senior Notes due 2030
- 反证 [ev_be2ff850c1128bb7](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): Purchases from this supplier accounted for approximately 33%, 39% and 33% of total vendor payments
- 证伪条件：扣除 Pathos 后数据业务增速转负
- 证伪条件：Illumina 供应中断

### management_governance: partial

双重股权结构，且数据业务约五分之一来自关联方 Pathos。

- 支持 [ev_2055ff2a5d1f8678](https://www.sec.gov/Archives/edgar/data/1717115/000119312526066961/tem-20251231.htm) (primary-document): The dual class structure of our common stock has the effect of concentrating voting control
- 反证 [ev_d216b0da8b88f30c](https://www.sec.gov/Archives/edgar/data/1717115/000119312526442624/tem-20260930.htm) (primary-document): Includes related party revenue from Pathos AI, Inc. of $ 22,061 and $ 24,907 for the three months ended September 30, 2026 and 2025, respectively.

## TLX · complete

审查记录：`state/serenity-reviews/TLX-codex-f67f2977ed3b7b6234a0.json`

### supply_chain_map: unknown

证据包没有提供公司产品、上游投入与下游使用者之间的具体关系；财务汇总数字不能替代供应链映射。

- 缺口：具体产品和服务
- 缺口：上游关键输入及供应商
- 缺口：下游客户、工作流和替代周期
- 证伪条件：原始披露显示候选公司与目标主题没有直接产品或服务联系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

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

SEC一手材料只提供研发费用等有限财务项目，缺少同期收入、利润、现金流及目标主题贡献，不能完整验证投资论点。

- 支持 [ev_b7961e3f510ca8e0](https://data.sec.gov/api/xbrl/companyfacts/CIK0002007191.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Telix Pharmaceuticals Limited. R&D expense (ResearchAndDevelopmentExpense): 171,249,000 for 2025-01-01 to 2025-12-31; form 20-F filed 2026-02-20, accession 0001628280-26-009943.
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_b7961e3f510ca8e0](https://data.sec.gov/api/xbrl/companyfacts/CIK0002007191.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for Telix Pharmaceuticals Limited. R&D expense (ResearchAndDevelopmentExpense): 171,249,000 for 2025-01-01 to 2025-12-31; form 20-F filed 2026-02-20, accession 0001628280-26-009943.
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

## WGS · complete

审查记录：`state/serenity-reviews/WGS-codex-17f4a1a827bfdd38277a.json`

### supply_chain_map: unknown

证据包没有提供公司产品、上游投入与下游使用者之间的具体关系；财务汇总数字不能替代供应链映射。

- 缺口：具体产品和服务
- 缺口：上游关键输入及供应商
- 缺口：下游客户、工作流和替代周期
- 证伪条件：原始披露显示候选公司与目标主题没有直接产品或服务联系

### chokepoint_evidence: unknown

现有材料没有市场份额、供应集中度、独家数据、认证锁定或多年替代周期证据；产品获批或财务规模不能证明瓶颈。

- 缺口：市场份额或供应商数量
- 缺口：替代所需时间与成本
- 缺口：独家数据、专利或认证锁定证据
- 证伪条件：竞争者能够在12至24个月内提供等效产品
- 证伪条件：公司没有定价权或关键投入并不稀缺

### customer_dependency: unknown

证据包没有披露具体付费客户、部署量、续约率、使用量或客户收入贡献；FDA记录只证明产品记录，不证明采用和依赖。

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

- 支持 [ev_942ca7b583466b69](https://data.sec.gov/api/xbrl/companyfacts/CIK0001818331.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for GeneDx Holdings Corp.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 123,101,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-09, accession 0001628280-26-072203. Same period a year earlier (2025-07-01 to 2025-09-30): 116,743,000, a change of +5.4%. Net income (loss) (NetIncomeLoss): -12,327,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 20
- 缺口：目标主题或产品收入贡献
- 缺口：可比期间利润率和现金流
- 缺口：管理层对关键业务驱动因素的原始解释
- 证伪条件：连续两个报告期收入或使用量恶化
- 证伪条件：增长没有转化为毛利和经营现金流改善
- 证伪条件：现金消耗迫使公司大幅稀释融资

### counter_thesis: partial

财务原始数据允许检查盈利、现金消耗和研发强度，但证据包没有完成需求、替代、竞争、监管、地缘政治和估值的系统反方压力测试。

- 支持 [ev_942ca7b583466b69](https://data.sec.gov/api/xbrl/companyfacts/CIK0001818331.json) (sec-companyfacts): SEC XBRL Companyfacts primary filing evidence for GeneDx Holdings Corp.. Revenue (RevenueFromContractWithCustomerExcludingAssessedTax): 123,101,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-09, accession 0001628280-26-072203. Same period a year earlier (2025-07-01 to 2025-09-30): 116,743
- 反证 [ev_942ca7b583466b69](https://data.sec.gov/api/xbrl/companyfacts/CIK0001818331.json) (sec-companyfacts): Net income (loss) (NetIncomeLoss): -12,327,000 for 2026-07-01 to 2026-09-30; form 10-Q filed 2026-11-09, accession 0001628280-26-072203. Operating cash flow (NetCashProvidedByUsedInOperatingActivities): -32,408,000 for 2026-01-01 to 2026-03-31; form 10-Q filed 2026-05-04, accession 0001818331-26-000041. Cash and equivalents (CashAndCashEquivalentsAtCarryingV
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
