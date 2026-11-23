# FDA 拒批信（CRL）原因分类

> 455 封 openFDA 公开的 CRL（2020 年至今）。分类是规则代理，每条原因附信件原句；严重度：重 = 有效性不足或需要新试验，中 = 安全性或需补药理研究，轻 = 生产、可用性或资料格式。生成时间 2026-11-22。

## 严重度与后来是否获批

| 严重度 | 封数 | 其中后来获批 | 比例 |
|---|---:|---:|---:|
| heavy | 97 | 54 | 56% |
| medium | 42 | 33 | 79% |
| light | 204 | 134 | 66% |
| unknown | 92 | 79 | 86% |
| redacted | 20 | 2 | 10% |

原因出现次数：manufacturing 261，efficacy 103，pharmacology 54，safety 50，usability 34。
要求新试验 60 封；工厂检查未通过 157 封；可对应上市公司 131 封。

## 最近 25 封

| 日期 | 申请 | 公司 | 药物 | 严重度 | 原因 | 新试验 | 后来获批 |
|---|---|---|---|---|---|---|---|
| 2026-11-13 | BLA 761524 | Summit Therapeutics Inc (SMMT) | AK112/SMT112 | heavy | efficacy, safety | 是 | 否 |
| 2026-10-19 | NDA 220054 | Cristcot HCA LLC | hydrocortisone acetate | heavy | efficacy | 是 | 否 |
| 2026-09-09 | BLA 761393 | SEIKAGAKU Corporation | SI-6603 | unknown |  |  | 否 |
| 2026-08-18 | BLA 761494 | SamChunDang Pharm. Co., Ltd | SCD411 | light | manufacturing |  | 否 |
| 2026-08-18 | NDA 216195 | Xspray Pharma AB | ? | light | manufacturing |  | 否 |
| 2026-08-07 | NDA 218705 | ITM Solucin GmbH | MPA | light | manufacturing |  | 否 |
| 2026-07-29 | NDA 220381 | Fresenius Kabi USA, LLC | Glycophos | unknown |  |  | 是 |
| 2026-07-21 | NDA 219107 | Apiject Systems Corp | glycopyrrolate solution | light | usability |  | 否 |
| 2026-07-09 | NDA 216586 | Elevar Therapeutics Inc | rivoceranib tablet | light | manufacturing |  | 否 |
| 2026-07-09 | BLA 761308 | Jiangsu Hengrui Pharmaceuticals Co., Ltd (JNGHF) | the clinical studies/trials | unknown |  |  | 否 |
| 2026-07-02 | NDA 220544 | Ascelia Pharma AB | ? | heavy | efficacy |  | 否 |
| 2026-06-29 | BLA 761311 | Ipsen Biopharm Ltd | ? | light | manufacturing |  | 否 |
| 2026-06-29 | NDA 218607 | Unicycive Therapeutics Inc (UNCY) | oxylanthanum carbonate tablets | light | manufacturing |  | 否 |
| 2026-06-26 | NDA 216900 | Evergreen Theragnostics, Inc | ? | light | manufacturing |  | 否 |
| 2026-06-26 | BLA 761438 | Swedish Orphan Biovitrum AB (publ) | ? | light | manufacturing |  | 否 |
| 2026-06-23 | BLA 761266 | Tanvex BioPharma USA, Inc | TX05 | light | manufacturing |  | 否 |
| 2026-06-20 | NDA 218995 | Achieve Life Sciences, Inc (ACHV) | cytisinicline tablet | light | manufacturing |  | 否 |
| 2026-06-17 | NDA 220748 | Avyxa Holdings, LLC | Cisplatin Injection | light | manufacturing |  | 是 |
| 2026-06-15 | NDA 220138 | Tris Pharma, Inc | oxybate for extended-release powder for oral suspension | light | manufacturing |  | 否 |
| 2026-06-10 | NDA 218600 | Bridge Regulatory Affairs, LLC | ? | light | manufacturing |  | 否 |
| 2026-06-04 | NDA 217644 | Xspray Pharma AB | ? | medium | manufacturing, pharmacology |  | 否 |
| 2026-05-29 | NDA 220283 | Cingulate Therapeutics, LLC (CINGW) | dexmethylphenidate hydrochloride extended-release tablets | light | manufacturing |  | 否 |
| 2026-05-15 | NDA 217363 | Ocuvex Therapeutics, Inc | brimonidine tartrate ophthalmic suspension 0.35% | light | manufacturing |  | 否 |
| 2026-04-23 | NDA 220304 | Grace Therapeutics U.S., Inc (GRCE) | Prescribing Information | light | manufacturing |  | 否 |
| 2026-04-22 | BLA 761459 | AbbVie Inc (ABBV) | AGN-151586 for injection | light | manufacturing |  | 否 |

## FDA 信件 vs 公司 8-K 公告

对比了 25 封有上市公司 8-K 的信：8 封公司公告未提及 FDA 引用的至少一类原因；FDA 要求新试验的信里，3 封公司公告没有用"新试验 / 补做试验"的措辞（通常改说在研试验的数据）。关键词对比只能发现遗漏，不能证明披露完整。

| 日期 | 公司 | 药物 | FDA 原因 | 公司提到 | 公司未提 | FDA 要求新试验：公司措辞 | 8-K |
|---|---|---|---|---|---|---|---|
| 2026-11-13 | Summit Therapeutics Inc (SMMT) | AK112/SMT112 | efficacy, safety | efficacy, safety | — | **未用** | [8-K](https://www.sec.gov/Archives/edgar/data/1599298/000159929826000092/ivonescimabcrlscenariopr.htm) |
| 2026-05-29 | Cingulate Therapeutics, LLC (CINGW) | dexmethylphenidate hydrochloride extended-release tablets | manufacturing | efficacy, manufacturing | — |  | [8-K](https://www.sec.gov/Archives/edgar/data/1862150/000149315226026760/ex99-1.htm) |
| 2026-04-23 | Grace Therapeutics U.S., Inc (GRCE) | Prescribing Information | manufacturing | manufacturing, pharmacology, efficacy, safety | — |  | [8-K](https://www.sec.gov/Archives/edgar/data/1444192/000114036126016324/ef20070593_ex99-1.htm) |
| 2026-04-22 | AbbVie Inc (ABBV) | AGN-151586 for injection | manufacturing | efficacy, safety, manufacturing, pharmacology | — |  | [8-K](https://www.sec.gov/Archives/edgar/data/1551152/000155115226000013/abbv-20260331xexhibit991.htm) |
| 2026-04-10 | Replimune, Inc (REPL) | the treatment of adult patients | efficacy | efficacy, safety, pharmacology | — | **未用** | [8-K](https://www.sec.gov/Archives/edgar/data/1737953/000110465926042141/tm2611633d1_ex99-1.htm) |
| 2026-02-13 | Disc Medicine, Inc (IRON) | ? | efficacy | efficacy | — |  | [8-K](https://www.sec.gov/Archives/edgar/data/1816736/000119312526051504/iron-ex99_1.htm) |
| 2026-02-07 | REGENXBIO, Inc (RGNX) | clemidsogene lanparvovee | efficacy | efficacy, safety | — | 用了 | [8-K](https://www.sec.gov/Archives/edgar/data/1590877/000119312526043342/rgnx-ex99_1.htm) |
| 2026-01-30 | Aquestive Therapeutics Inc (AQST) | dibutepinephrine sublingual film | manufacturing, pharmacology | — | manufacturing, pharmacology |  | [8-K](https://www.sec.gov/Archives/edgar/data/1398733/000139873326000005/q12026-crlmeetingsupplem.htm) |
| 2025-09-22 | Scholar Rock, Inc (SRRK) | SRK-015 | manufacturing | efficacy, safety, manufacturing | — |  | [8-K](https://www.sec.gov/Archives/edgar/data/1727196/000110465925092317/tm2526733d1_ex99-1.htm) |
| 2025-08-18 | PTC Therapeutics, Inc (PTCT) | ? | efficacy, manufacturing | — | efficacy, manufacturing |  | [8-K](https://www.sec.gov/Archives/edgar/data/1070081/000155837025011658/tmb-20250819xex99d1.htm) |
| 2025-07-30 | Regeneron Pharmaceuticals, Inc (REGN) | ? | manufacturing | efficacy | manufacturing |  | [8-K](https://www.sec.gov/Archives/edgar/data/872589/000087258925000017/exhibit991q22025.htm) |
| 2025-07-21 | Replimune, Inc (REPL) | vusolimogene oderparepvec | efficacy | efficacy, safety | — |  | [8-K](https://www.sec.gov/Archives/edgar/data/1737953/000110465925069489/tm2521403d1_ex99-1.htm) |
| 2025-07-09 | Capricor, Inc (CAPR) | deramiocel | efficacy, manufacturing | efficacy, manufacturing, safety | — | **未用** | [8-K](https://www.sec.gov/Archives/edgar/data/1133869/000155837025009186/capr-20250711xex99d1.htm) |
| 2025-07-07 | Ultragenyx Pharmaceutical Inc (RARE) | rebisufligene etisparvovec | manufacturing | manufacturing | — |  | [8-K](https://www.sec.gov/Archives/edgar/data/1515673/000095017025095334/rare-20250711.htm) |
| 2025-06-27 | Unicycive Therapeutics Inc (UNCY) | ? | manufacturing | manufacturing, pharmacology, safety | — |  | [8-K](https://www.sec.gov/Archives/edgar/data/1766140/000121390025059303/ea024746901ex99-1_unicycive.htm) |
| 2025-04-02 | Aldeyra Therapeutics, Inc (ALDX) | ? | efficacy | efficacy, safety | — | 用了 | [8-K](https://www.sec.gov/Archives/edgar/data/1341235/000119312525072424/d946200dex992.htm) |
| 2025-01-15 | Atara Biotherapeutics, Inc (ATRA) | tabelecleucel®) @) | manufacturing | efficacy, manufacturing | — |  | [8-K](https://www.sec.gov/Archives/edgar/data/1604464/000095017025006992/atra-ex99_1.htm) |
| 2024-06-14 | Rocket Pharmaceuticals, Inc (RCKT) | marnetegragene autotemcel manufactured for Rocket Pharmaceuticals | manufacturing | manufacturing, efficacy, safety | — |  | [8-K](https://www.sec.gov/Archives/edgar/data/1281895/000114036124031749/ef20031912_ex99-1.htm) |
| 2024-04-16 | Abeona Therapeutics, Inc (ABEO) | prademagene zamikeracel manufactured at your Cleveland | efficacy, manufacturing, usability | manufacturing | efficacy, usability |  | [8-K](https://www.sec.gov/Archives/edgar/data/318306/000149315224017768/ex99-1.htm) |
| 2024-02-26 | Minerva Neurosciences, Inc (NERV) | ? | efficacy, manufacturing, pharmacology, safety | efficacy, safety, manufacturing, pharmacology | — |  | [8-K](https://www.sec.gov/Archives/edgar/data/1598646/000119312524047110/d795805dex991.htm) |
| 2023-09-19 | ARS Pharmaceuticals, Inc (SPRY) | NEFFY | manufacturing, usability | — | manufacturing, usability |  | [8-K](https://www.sec.gov/Archives/edgar/data/1671858/000119312523241345/d557739dex991.htm) |
| 2023-07-28 | Citius Pharmaceuticals, Inc (CTXR) | LYMPHIR | manufacturing | efficacy, safety | manufacturing |  | [8-K](https://www.sec.gov/Archives/edgar/data/1506251/000121390023061292/ea182624-8kex99i_citius.htm) |
| 2023-01-18 | Eli Lilly and Company (LLY) | KISUNLA | efficacy, manufacturing, safety | — | efficacy, manufacturing, safety |  | [8-K](https://www.sec.gov/Archives/edgar/data/59478/000005947823000025/q422lillysalesandearningsp.htm) |
| 2022-05-23 | Verrica Pharmaceuticals Inc (VRCA) | cantharidin topical solution | manufacturing | manufacturing | — |  | [8-K](https://www.sec.gov/Archives/edgar/data/1660334/000119312522159075/d306825d8k.htm) |
| 2022-04-29 | Coherus BioSciences, Inc (CHRS) | LOQTORZI | manufacturing | — | manufacturing |  | [8-K](https://www.sec.gov/Archives/edgar/data/1512762/000155837022007404/chrs-20220503xex99d1.htm) |
