# AI Medicine 论点长期记忆

> 记录系统在每次运行时知道什么、排名如何变化、哪些事件让 Serenity 门槛失效。它是审计轨迹，不是预测能力证明。

覆盖 13 家公司；保留 10 个不同状态快照；本次 3 家发生变化，共 5 个字段变化。

## 本次变化

### RDNT
- `serenityDecision`：`watch` → `revalidate`
- `completenessScore`：`51` → `0`
### ISRG
- `completenessScore`：`12` → `0`
- 关联事件：FDA Provides Clarity to Support Cell and Gene Therapy Development and Quality；影响门槛：cash_runway, chokepoint_evidence, customer_dependency, earnings_validation, falsifiers, multi_node_control, regulatory_path, valuation
- 关联事件：FDA Issues Final Guidance on Prescription Drug Apps and Software；影响门槛：cash_runway, chokepoint_evidence, customer_dependency, earnings_validation, falsifiers, multi_node_control, regulatory_path, valuation
- 关联事件：FDA Approves First Drug to Treat Adults with Primary Membranous Nephropathy；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：Guidance Recap Podcast | Assessing the Effects of Food on Drugs in INDs and NDAs – Clinical Pharmacology Considerations；影响门槛：cash_runway, customer_dependency, earnings_validation, valuation
- 关联事件：Section 804 Importation Program Policies and Authorizations；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：Guidance for Industry: Potency Assurance for Cellular and Gene Therapy Products；影响门槛：cash_runway, customer_dependency, earnings_validation, valuation
- 关联事件：Game Changer Products LLC Issues Voluntary Nationwide Recall of 10 Day Forecast Capsules Due to the Presence of Undeclared Sildenafil and Acetaminophen；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDALabel: Full-Text Search of Drug Product Labeling；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA grants accelerated approval to zanubrutinib for relapsed or refractory follicular lymphoma；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA grants accelerated approval to tucatinib with trastuzumab for colorectal cancer；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA grants accelerated approval to tovorafenib for patients with relapsed or refractory BRAF-altered pediatric low-grade glioma；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA grants accelerated approval to tarlatamab-dlle for extensive stage small cell lung cancer；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA grants accelerated approval to talquetamab-tgvs for relapsed or refractory multiple myeloma；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA grants accelerated approval to retifanlimab-dlwr for metastatic or recurrent locally advanced Merkel cell carcinoma；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA grants accelerated approval to ponatinib with chemotherapy for newly diagnosed Philadelphia chromosome-positive acute lymphoblastic leukemia；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA grants accelerated approval to repotrectinib for adult and pediatric patients with NTRK gene fusion-positive solid tumors；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：Activities Report of the Generic Drug Program | FDARA Title VIII Sections 807 and 805；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA approves pimicotinib for symptomatic tenosynovial giant cell tumor；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：Oncology (Cancer)/Hematologic Malignancies Approval Notifications；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：Recommendations for Reducing the Risk of Transfusion-Transmitted Hepatitis B Virus；影响门槛：cash_runway, customer_dependency, earnings_validation, valuation
- 关联事件：FDA grants accelerated approval to dostarlimab-gxly for dMMR advanced solid tumors；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA grants accelerated approval to Darzalex Faspro for newly diagnosed light chain amyloidosis；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA grants accelerated approval to asciminib for newly diagnosed chronic myeloid leukemia；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA grants accelerated approval to afamitresgene autoleucel for unresectable or metastatic synovial sarcoma；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA expands pediatric indication for entrectinib and approves new pellet formulation；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA expands endometrial cancer indication for dostarlimab-gxly with chemotherapy；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA expands early breast cancer indication for abemaciclib with endocrine therapy；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA approves zanubrutinib for chronic lymphocytic leukemia or small lymphocytic lymphoma；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：Biologics Electronic Reading Room (eFOIA)；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：Drugs@FDA Data Files；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：Early-Phase IND Protocol Recommendations for Solid Tumors; Draft Guidance for Industry；影响门槛：cash_runway, customer_dependency, earnings_validation, valuation
- 关联事件：FDA Approves First Factor Xla Inhibitor to Help Prevent Stroke in Certain Adults at High Risk；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：10-Q - Quarterly report [Sections 13 or 15(d)]；影响门槛：cash_runway, customer_dependency, earnings_validation, valuation
- 关联事件：FDA Roundup: June 4, 2024；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：Patient Listening Session Summaries；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：Stock Market Suffers Ugly Losses In Election Week; Apple, Palantir Led Key Earnings: Weekly Review - Investor's Business Daily；影响门槛：cash_runway, customer_dependency, earnings_validation, valuation
- 关联事件：FDA Grants Accelerated Approval to a New Treatment for Head and Neck Squamous Cell Carcinoma；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：SEC Adopts Amendments to Update Definitions of Small Entity for Investment Companies and Investment Advisers；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA Approves First Plasmid DNA-based Immunotherapy for Adults with Recurrent Respiratory Papillomatosis；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA Launches New Program to Advance Neuroscience Medical Product Development；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA Approves First-of-Its-Kind Chronic Hepatitis B Treatment；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA Approves Once-Weekly Generic Hormone Therapy Patch for Women；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：SEC, FSA Hold Autumn Financial Regulatory Dialogue；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA Approves Immunotherapy That May Allow Certain Patients with Rectal Cancer to Avoid Chemotherapy, Radiation and Surgery；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA Launches the Rare Disease Framework Initiative to Develop a Holistic, Fit-For-Purpose Framework for Rare Disease Drug Development；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA Seeks Public Input to Support Ibogaine Research；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA Approves First Heart Valve Designed to Grow with Children；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA Launches Nationwide Effort to Expand Scientific Expertise and Consumer Voices to Advisory Committees；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA Investigation Leads to Charges Against Two Indian Nationals Involved in Transnational Counterfeit Drug Distribution Scheme；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA Approves First Treatment for MCT8 Deficiency；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA intends to evaluate changes to the PMTA regulatory framework；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：Federal Court Enters Consent Decree Against Gold Star Distribution, Inc. Following Persistent Insanitary Warehouse Conditions；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA Updates Regulations to Advance Innovative Alternatives to Animal Testing；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：FDA Approves First Gene Therapy for Pediatric Patients with Sanfilippo Syndrome Type A；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：Timeline of a scandal: How Jensen Huang's abrupt resignation unfolded at Nvidia - CBS News；影响门槛：counter_thesis, earnings_validation, management_governance, reputation_risk
- 关联事件：NVIDIA Announces CEO Transition；影响门槛：cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, valuation
- 关联事件：Decisions by Discrimination: Differential Evidence for Medical Reasoning；影响门槛：cash_runway, customer_dependency, earnings_validation, partner_economics, valuation
- 关联事件：AI Governance Should Prioritize Control and Knowledge Boundaries Over Limiting Intelligence；影响门槛：counter_thesis, integration_execution, management_governance, reputation_risk, valuation
- 关联事件：The Infrastructure Divide: Analyzing Community Stance on Data Center Development via Reddit；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, partner_economics, regulatory_path
- 关联事件：Aspect-wise Pairwise Tournaments for Test-Time Selection；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, partner_economics, regulatory_path
- 关联事件：2AM: Grounding Agent-Side Memory as Guidance for Steerable Action Models in Long-Horizon Manipulation；影响门槛：cash_runway, customer_dependency, earnings_validation, partner_economics, valuation
- 关联事件：Temporary Authority, Permanent Effects: Commit-Time Authorization for LLM Agents；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, integration_execution, multi_node_control, regulatory_path, valuation
- 关联事件：GitInject: Real-World Prompt Injection Attacks in AI-Powered CI/CD Pipelines；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, integration_execution, multi_node_control, regulatory_path, valuation
- 关联事件：Authenticity Debt and the Synthetic Content Threat Landscape: A Layered Framework for Trust, Provenance, and IP Governance in the Generative AI Era；影响门槛：chokepoint_evidence, counter_thesis, customer_dependency, falsifiers, management_governance, multi_node_control, regulatory_path, reputation_risk
- 关联事件：A Multi-Instance LLM Framework for Rating the Quality of Surgical Feedback；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, integration_execution, multi_node_control, regulatory_path, valuation
- 关联事件：AI-Enabled Question-Answering for Chartered Accountancy: A Retrieval-Augmented Reasoning Framework；影响门槛：chokepoint_evidence, customer_dependency, falsifiers, multi_node_control, partner_economics, regulatory_path
- 关联事件：Prompt Less, Smile More: Semantic Engineering in Lieu of Prompt Engineering；影响门槛：cash_runway, customer_dependency, earnings_validation, integration_execution, valuation
- 关联事件：Component Replacement in LLM Agents: A Critical Scoping Review of Task Benefit and Attribution；影响门槛：clinical_validation, customer_dependency, falsifiers, partner_economics
- 关联事件：Reliability Engineering for AI Systems: Challenges, Methods, and Directions；影响门槛：cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, reputation_risk, valuation
- 关联事件：When No Answer Is Correct: Diagnosing Absent Answer Detection for MLLMs in Video Understanding；影响门槛：cash_runway, customer_dependency, earnings_validation, partner_economics, valuation
- 关联事件：Representational Acquisition Under Bounded Resources；影响门槛：clinical_validation, falsifiers, integration_execution, valuation
- 关联事件：Contrastive Adapter Training and Consensus Knowledge Distillation for Multi-Source-Free Domain Adaptation in Skin Cancer Diagnosis；影响门槛：chokepoint_evidence, clinical_validation, customer_dependency, falsifiers, multi_node_control, regulatory_path
- 关联事件：Getting a Grip: Operating Human-Agent Software Teams Through Governed Messages；影响门槛：chokepoint_evidence, counter_thesis, customer_dependency, falsifiers, management_governance, multi_node_control, regulatory_path, reputation_risk
- 关联事件：SPARQLcirc: Probabilistic Query Evaluation with Provenance Circuits；影响门槛：clinical_validation, customer_dependency, falsifiers, partner_economics
- 关联事件：Evaluating Context Sensitivity of Collaboration Behavior in Multi Party Simulation Frameworks；影响门槛：cash_runway, customer_dependency, earnings_validation, partner_economics, valuation
- 关联事件：Towards a Trustworthy and Governable Internet of Agentics: An Architectural Perspective on Protocols, Systems, and Services；影响门槛：clinical_validation, counter_thesis, falsifiers, management_governance, reputation_risk
- 关联事件：Human-Supervised Artificial Intelligence Researchers in Electric Power Systems: Knowledge, Physics, Simulation, and Governance for Large Language Models；影响门槛：chokepoint_evidence, counter_thesis, customer_dependency, falsifiers, management_governance, multi_node_control, regulatory_path, reputation_risk
- 关联事件：CivicBench: A Benchmark and Memory Framework for Web-Based Civic Data Analytics；影响门槛：cash_runway, customer_dependency, earnings_validation, integration_execution, valuation
- 关联事件：A generative foundation model for computational brain imaging；影响门槛：clinical_validation, customer_dependency, falsifiers, partner_economics
### IQV
- `serenityDecision`：`watch` → `revalidate`
- `completenessScore`：`22` → `0`

## 当前记忆

| 股票 | 排名 | Serenity | 完整度 | 估值 | 融资风险 | 5日环境 |
|---|---:|---|---:|---|---|---:|
| TEM | 1 | revalidate | 0 | growth valuation; requires continued validation | low | +1.71% |
| SDGR | 2 | revalidate | 0 | premium; execution-sensitive | medium | +1.37% |
| CERT | 3 | revalidate | 0 | growth valuation; requires continued validation | low | +1.45% |
| NTRA | 4 | revalidate | 0 | premium; execution-sensitive | low | -1.23% |
| RXRX | 5 | revalidate | 0 | pipeline optionality; revenue multiple not decision-useful | medium | -1.74% |
| SOPH | 6 | revalidate | 0 | growth valuation; requires continued validation | high | +0.23% |
| GH | 7 | revalidate | 0 | premium; execution-sensitive | low | +1.14% |
| ABCL | 8 | revalidate | 0 | pipeline optionality; revenue multiple not decision-useful | medium | +0.76% |
| GEHC | None | revalidate | 0 | not obviously premium on sales; inspect quality and dilution | low | -0.45% |
| RDNT | None | revalidate | 0 | not obviously premium on sales; inspect quality and dilution | low | +1.15% |
| ISRG | None | revalidate | 0 | premium; execution-sensitive | low | +2.01% |
| IQV | None | revalidate | 0 | not obviously premium on sales; inspect quality and dilution | low | +1.30% |
| NVDA | None | revalidate | 0 | premium; execution-sensitive | low | +2.71% |

## 决策引用记忆

- **TEM：** `mem_0efadccc98f2`, `mem_f3047466ac1f`, `mem_4645d21f8a09`, `mem_e040023a3aa2`, `mem_4bc847966f42`
- **SDGR：** `mem_7debd5104108`, `mem_d7409eb7f180`, `mem_1881bdf5663f`, `mem_32090f8aa8e8`, `mem_edb0dda05909`
- **CERT：** `mem_8650dd160818`, `mem_8e7729b470a7`, `mem_9c26e964c49e`, `mem_9d8604a57901`
- **NTRA：** `mem_86caf8dfbd74`, `mem_c72c64a041bb`, `mem_4aa4df572dae`, `mem_ef2228969d1d`
- **RXRX：** `mem_9fabe609c1d3`, `mem_796975290c26`, `mem_4109ca0ee4fa`, `mem_b51f7635c97f`, `mem_96fef5534ae1`
- **SOPH：** `mem_6c8b79a08795`, `mem_67adcf1bce2e`, `mem_9fdd929ccde9`, `mem_dfe7ca75075e`
- **GH：** `mem_4b18f5c021ed`, `mem_f776df745f4f`, `mem_7ca3c4c11e45`, `mem_8e3c57f5d1f6`
- **ABCL：** `mem_e84add9bda71`, `mem_d96018c9348a`, `mem_089b6540b2d3`, `mem_2c3af59bc6fb`, `mem_66ef8cc43b61`
- **GEHC：** `mem_83e431ef75fa`, `mem_62de0a6fe442`, `mem_ed4c4183c556`
- **RDNT：** `mem_603cf457da0c`, `mem_87a3ecb0a0fb`, `mem_962e42552623`
- **ISRG：** `mem_72dc8a08b705`, `mem_c2d0b38e7bdf`, `mem_4437c75c3fc7`, `mem_28c0dde7d9fa`, `mem_7a0525d0414b`, `mem_a041381cb54a`, `mem_5398f661b183`, `mem_e1ddd4e1ae14`, `mem_c37adea38cc1`, `mem_f0bfe2c88f39`, `mem_472410babdc7`, `mem_51c508032c29`, `mem_c20ccea2d172`, `mem_a613061e8d54`, `mem_09380f08e8ae`, `mem_0530da2604cf`, `mem_595c42a66ca4`, `mem_99bbbf9d6434`, `mem_ad3a02a73906`, `mem_8143f7655bf7`, `mem_f2c864394fe0`, `mem_70b6d8fc78eb`, `mem_1ebd8c96a725`, `mem_11db3d20deb3`, `mem_6f9fccc4f749`, `mem_b70b68367e85`, `mem_b5c7af1440c6`, `mem_d00b84c4ca8e`, `mem_a66b06e73195`, `mem_39308b62f637`, `mem_b08ffa144434`, `mem_6aaa7d584172`, `mem_5a896c0e9158`, `mem_a181d97d41e6`, `mem_208469f2705a`, `mem_8abeb0f092f6`, `mem_ecac139b57e1`, `mem_bb4675fecb33`, `mem_d3a49974ba1c`, `mem_97595ee62a79`, `mem_a876d97e3fd4`, `mem_05d8b9dcae96`, `mem_dbc82698049a`, `mem_b8a3a043a36a`, `mem_3ff227085435`, `mem_d4c32224b396`, `mem_63068cabfbcd`, `mem_8cc9ae4a31aa`, `mem_dca376fdc121`, `mem_22fd2486c907`, `mem_d719c8e7fe31`, `mem_ab5e22913706`, `mem_02f6b1476d3d`, `mem_3f601eedf37c`, `mem_9a3459d63ba0`, `mem_8f2b69ab3a43`, `mem_8d88861619aa`, `mem_2e37f3fef3db`, `mem_fe8688402b33`, `mem_77dba0d66245`, `mem_1ad3f9c496c6`, `mem_ea8b81bff20c`, `mem_c8b959fa9f76`, `mem_1756aafa9f88`, `mem_19440cd819f0`, `mem_4f7154b5d2ff`, `mem_786bff490aa5`, `mem_ae9f1bd9ca20`, `mem_9e6b46114801`, `mem_71786e2a2a46`, `mem_1c6cab1ec240`, `mem_290bba90a1d6`, `mem_2f9d7debee0f`, `mem_ef1037f01208`, `mem_3b989b48a6da`, `mem_71b7343b0fe0`, `mem_b190e6994fd6`, `mem_43512e345710`, `mem_fc03c6edcfcc`, `mem_6bd5d980fd98`, `mem_f424565c9687`, `mem_a311f3d530f0`
- **IQV：** `mem_7ccca2e025a2`, `mem_4d092213a4ee`, `mem_6b5d9f20c75b`
- **NVDA：** `mem_2352f2ca1e78`, `mem_4b356174c4a4`, `mem_5ec2b63ee470`, `mem_d04ab0ac0ee9`, `mem_ff485b97c5b0`, `mem_4e75bf386aa9`, `mem_a2217779ed40`, `mem_c22913bf3157`, `mem_baecc76da0cc`, `mem_6935148a453c`, `mem_f4f9d2f052d6`, `mem_a7e4e306660f`, `mem_09f212e7bd2e`, `mem_925e0240d7a1`, `mem_96adf2b18527`, `mem_ec7380b19545`, `mem_d24fcac766ad`, `mem_4bc81127cb95`, `mem_7e88c08b4cad`, `mem_90d4523b3386`, `mem_1f65a21a5dfd`, `mem_6d46d442c2e9`, `mem_51576089a55e`

## 已实现表现反思

| 股票 | 周期 | 实际收益 | 超额 SPY | 超额 XLV | 超额 XBI | 方向正确 |
|---|---:|---:|---:|---:|---:|---|
| TEM | 1 | -5.65% | -5.29% | -6.20% | -5.22% | 是 |
| TEM | 5 | +5.04% | +5.95% | +5.41% | +6.79% | 是 |
| SDGR | 1 | -4.28% | -3.92% | -4.82% | -3.85% | 否 |
| SDGR | 5 | +15.16% | +16.08% | +15.54% | +16.92% | 是 |
| CERT | 1 | -2.77% | -2.41% | -3.32% | -2.34% | 是 |
| NTRA | 1 | -1.19% | -0.83% | -1.74% | -0.76% | 是 |
| RXRX | 1 | -4.35% | -3.99% | -4.90% | -3.92% | 是 |
| RXRX | 5 | -8.18% | -7.27% | -7.81% | -6.43% | 否 |
| SOPH | 1 | +4.45% | +4.82% | +3.91% | +4.88% | 是 |
| GH | 1 | -2.04% | -1.68% | -2.58% | -1.61% | 否 |
| ABCL | 1 | -1.12% | -0.76% | -1.66% | -0.69% | 是 |
| ABCL | 5 | -1.07% | -0.15% | -0.69% | +0.69% | 否 |
| NVDA | 1 | -2.01% | -1.65% | -2.55% | -1.58% | 否 |
| NVDA | 5 | -14.46% | -13.55% | -14.09% | -12.71% | 否 |
