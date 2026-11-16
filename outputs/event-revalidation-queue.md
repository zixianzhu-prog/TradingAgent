# 事件驱动重新验证队列

生成日期：2026-11-15

> 事件只触发重新研究，不会自动改变评级、仓位或创建交易。发布时间、发现时间或as-of不一致的事件会被隔离，不能使Serenity门槛失效。

## 事件日历

| 股票 | 事件 | 日期 | 状态 | 重新检查 |
| --- | --- | --- | --- | --- |
| ABCL | Q3 2026 earnings | 2026-11-09 | evidence-received | earnings_validation, cash_runway, dilution, partner_economics |
| NVDA | Independent board investigation | 2026-11-10 | overdue-awaiting-evidence | management_governance, reputation_risk, counter_thesis |
| NVDA | CEO transition and permanent successor search | 2026-11-12 | evidence-received | management_governance, counter_thesis, earnings_validation |
| NVDA | Q3 FY2027 earnings and management outlook | 2026-11-17 | evidence-received | earnings_validation, valuation, customer_dependency, cash_generation |
| TEM | Personalis shareholder vote | 2026-11-30 | upcoming | integration_execution, data_chokepoint, valuation |
| TEM | Q4/FY 2026 earnings | 待公布 | unscheduled | earnings_validation, valuation, cash_generation |
| SDGR | Q4/FY 2026 earnings | 待公布 | unscheduled | earnings_validation, hosted_margin, cash_runway |
| RXRX | REC-4881 FDA path | 待公布 | unscheduled | clinical_validation, regulatory_path, valuation |
| RXRX | REC-1245 expansion data | 待公布 | unscheduled | clinical_validation, cash_runway, falsifiers |
| ABCL | ABCL575 top-line data | 待公布 | unscheduled | clinical_validation, platform_validation, falsifiers |
| CERT | Q4/FY 2026 earnings | 待公布 | unscheduled | earnings_validation, software_growth, customer_dependency, valuation |
| NTRA | Q4/FY 2026 earnings | 待公布 | unscheduled | earnings_validation, cash_generation, test_volume, valuation |
| NTRA | Diagnostic coverage and regulatory updates | 待公布 | unscheduled | customer_dependency, regulatory_path, falsifiers |
| SOPH | Q4/FY 2026 earnings | 待公布 | unscheduled | earnings_validation, cash_runway, customer_dependency, valuation |
| GH | Q4/FY 2026 earnings | 待公布 | unscheduled | earnings_validation, cash_generation, test_volume, valuation |
| GH | Shield coverage and regulatory updates | 待公布 | unscheduled | customer_dependency, regulatory_path, falsifiers |
| GEHC | FDA AI imaging device additions | 待公布 | unscheduled | chokepoint_evidence, customer_dependency, earnings_validation |
| GEHC | AI product adoption and imaging growth update | 待公布 | unscheduled | earnings_validation, pure_play, customer_dependency |
| RDNT | DeepHealth FDA device additions | 待公布 | unscheduled | chokepoint_evidence, multi_node_control, customer_dependency |
| RDNT | DeepHealth revenue and imaging integration update | 待公布 | unscheduled | earnings_validation, pure_play, cash_generation |
| ISRG | AI-enabled surgical workflow authorization | 待公布 | unscheduled | chokepoint_evidence, multi_node_control, customer_dependency |
| ISRG | procedure growth and recurring instrument revenue | 待公布 | unscheduled | earnings_validation, customer_dependency, valuation |
| IQV | AI clinical-development customer adoption | 待公布 | unscheduled | customer_dependency, chokepoint_evidence, multi_node_control |
| IQV | technology and analytics growth update | 待公布 | unscheduled | earnings_validation, pure_play, valuation |

## 待重新验证任务

### NVDA · 80/100
- [NVIDIA Announces CEO Transition](https://nvidianews.nvidia.com/news/nvidia-announces-ceo-transition)
- 事件类型：earnings, leadership
- 信息可用：2026-11-13T14:14:57.120196+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, valuation
- 触发原因：公司名称直接匹配；股票代码直接匹配；重大事件关键词：earnings, leadership；接近预定事件窗口

### NVDA · 70/100
- [Nvidia CEO Huang resigns amid affair scandals, board names CFO Colette Kress interim CEO - Yahoo Finance](https://news.google.com/rss/articles/CBMi4AFBVV95cUxQZzNYVy04Z1l4VlFPaDZDbW5wb0M2d1RTbFJVaWEwTGdSU0oxZkM5UG1aWlkzaVFIZGE5ZmpnaE5EOWZXdnl3Y3dYWmZrZ3l0Q2ItUU5EU1o4dHhYczFuRElaV2ZhcGNhVWlqTkdiWGIwUzNCVG5yRzR0VXJHMVlFT2xmX3ZzbU9SVEdrYzJBczh1eFZPYnduVXNCY21YOE9SMS1jRUtCdnRIckt4VkttOFRrZzNMLWhFUFRyc1k3dkhHMDJNbUFGLWtldmtOcENSbFpXYkNfSFFjRWFJdTFJVg?oc=5)
- 事件类型：leadership, reputational
- 信息可用：2026-11-14T18:18:28.353469+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；重大事件关键词：leadership, reputational；接近预定事件窗口

### NVDA · 70/100
- [Timeline of a scandal: How Jensen Huang's abrupt resignation unfolded at Nvidia - CBS News](https://news.google.com/rss/articles/CBMihAFBVV95cUxNWTN3bmdNV3NVS2liaHp3a1BkWlQweUhxc0ZQT0Z1RTItR3dLTzd0OXU4SktsZ1lpRmNWMmloVS1NeFZoTFA4Sm5qcUc3MnpZU3hGTjJsUEpDZUlIQlVxTEY3ajlJU2hyX19GU0JFLTdmLXNsRHl1UnFzUmZJSVNVcjJKdE0?oc=5)
- 事件类型：leadership, reputational
- 信息可用：2026-11-14T18:18:28.353666+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；重大事件关键词：leadership, reputational；接近预定事件窗口

### NVDA · 70/100
- [Jensen Huang affair puts Nvidia's future at risk, with no clear successor to the renowned CEO - CNBC](https://news.google.com/rss/articles/CBMif0FVX3lxTE5EcnlNdzFRY2RtTFNiaVYxeFhDSnJIck5qckxaeE4wLVRVYWFFSkZoc2tJNjRmLWxXSGxQMXFuYi1YeHpYbGNjOW5CMy1rNHNTaDlCWEpfUEpvYkprUEVkZjBJTTl6SmZRLWtNd1B3czh3ckl2ejlYcHFUN1FUODTSAYQBQVVfeXFMUHpzWXc5ZVl0T3JVSHlPT3NGUzh2cTFtd1hVbjRqbFNDQm5CclZwSmgtQ0I0akV6WHExSG9iZHptd0MxZ1RTOVhQYjlHbHNid2g3M0docFZBMmVCWGRjSzdIZjlFbFE1V3JjVHkyUmcxQWxFaDNsTHl2UUxHMTVxTlNvcDF2?oc=5)
- 事件类型：leadership, reputational
- 信息可用：2026-11-14T18:18:27.636848+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；重大事件关键词：leadership, reputational；接近预定事件窗口

### NVDA · 65/100
- [Jensen Huang resigned in disgrace from Nvidia. Many in Silicon Valley are still showering him with support - CNN](https://news.google.com/rss/articles/CBMiggFBVV95cUxOdmZKY1NndlFuaHMweHA1ZWpCb1NXc01LcmdNWkc1OHc2Y2ZxSEdzNVo5NzB6Vy15bVExTlpud3FiQmkweGFkRlc4cUhIeldyLUZCd0xXMlV3YThwNXI5djM0Smdkb2dJUVRQaHlFNEthLW5USjgtS2NqbzdjT1BPeFFn?oc=5)
- 事件类型：leadership
- 信息可用：2026-11-15T16:41:42.726777+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance
- 触发原因：公司名称直接匹配；重大事件关键词：leadership；接近预定事件窗口

### NVDA · 65/100
- [Who should run Nvidia? Our picks for Jensen Huang's successor, whether the board likes it or not - GeekWire](https://news.google.com/rss/articles/CBMiwgFBVV95cUxOSVI2UWhIOVhMU0RDVVhvMkxmWVc2Zi1sSTdmNEc5NDN4MkRiQmxOSm8xdjhGT0lheEhsdFNGbDlOSnNxMGMzZ3hETm1vb1l4YWdEMjZBNndkdXNCaW9BRXZCSzBMY2o1R0VWMGxMRU1oRUtlcDFFbGlWZGVqTzhiREpvcDI2V0t3dFZqVnhYWEoyUGNaY2JoMXRLbmE5TG5lR010c1dQaW1NWFF4UDJfcGthN2VJRUYtT3hOSXVUaGttZw?oc=5)
- 事件类型：leadership
- 信息可用：2026-11-15T16:41:42.727275+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance
- 触发原因：公司名称直接匹配；重大事件关键词：leadership；接近预定事件窗口

### NVDA · 65/100
- [I watched Jensen Huang speak 9 days before his resignation. Two things stand out now. - Business Insider](https://news.google.com/rss/articles/CBMingFBVV95cUxNWnVyWWE3N0hkcXhyMkxhcVppeTZ3dnZGazd6Z19IenlDXzlZeVZmM2IwNGo4QkU0dmVVRFByUkJIS0VYU3lTbDhpVEE1dC02aERFVzZqTTRJUjB3VHVXclExcFk3eHZ5dkNRUFlMR09DZmswOVRoN0JtV3hiaWpDdFB1YmhMZXBpUTRkR2NrbUZJV3QxRFdQWXlOdjNkUQ?oc=5)
- 事件类型：leadership
- 信息可用：2026-11-14T18:18:27.637482+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance
- 触发原因：公司名称直接匹配；重大事件关键词：leadership；接近预定事件窗口

### NVDA · 65/100
- [Nvidia Updates: Huang’s Resignation Reverberates Through A.I. Industry - The New York Times](https://news.google.com/rss/articles/CBMiggFBVV95cUxPSWxaN0tPUFI1US1TR2ppVnJqdmVuQTJLWmI0LVNDSDc0YkNOdjgxQUQ2elZjQjRQZzlyVlZuTGU4NndKOFJVT3dUeXBFNUhHV2c0d05lVndNVzZoZHZ6YWVqel8zN2l5Wnc0OXg3M3RxVWIxZ0RuMUptWm13YWRTR0dB?oc=5)
- 事件类型：leadership
- 信息可用：2026-11-14T18:18:27.637740+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance
- 触发原因：公司名称直接匹配；重大事件关键词：leadership；接近预定事件窗口

### NVDA · 65/100
- [Jensen Huang’s Resignation From Nvidia Worries the A.I. Start-Up World - The New York Times](https://news.google.com/rss/articles/CBMikgFBVV95cUxQU0ktRGc4QkFrV3FLTDFENm9CcFBEUEZsQlk4MXlfQzlLRW1iNUxYNnlHb1k2X1NiT2R2Rm5KT2tLUmJUbGxhWGprd1MyNDM4YnNmQVhnSi1hSDIyN1ktUnNUSWdiQWphT0xtczJOcTZlZE9OMGd2Z3lkYjVHdzl3aWlLaWZ1Ukp6cUpkaF9rRVUwZw?oc=5)
- 事件类型：leadership
- 信息可用：2026-11-15T16:41:42.727322+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance
- 触发原因：公司名称直接匹配；重大事件关键词：leadership；接近预定事件窗口

### NVDA · 65/100
- [Jensen Huang’s Bad Week Leading To His Resignation, Explained - Forbes](https://news.google.com/rss/articles/CBMipwFBVV95cUxNTFJDSmUzd0JTcWpDNXB4bXJqZDRCUEliYjFoZl9OcHVIWTlEb195eXdlaTBlY2JWVWxkTmFua3RNck1QcTNQMWc3UWxPS3NJSFJmRzV3dXJnaUd2MDdDQml3QmNRQTg4MjZoanN6d1JWVU5xUGxUc25MekIzX0pLeDNtMDR5cUNkdWZTVjctX0txbGx4ZzZ6T3VTVkw4X04xLVpJdTdRNA?oc=5)
- 事件类型：leadership
- 信息可用：2026-11-14T18:18:27.637916+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance
- 触发原因：公司名称直接匹配；重大事件关键词：leadership；接近预定事件窗口

### NVDA · 65/100
- [Will Washington Cut China’s Access to Nvidia AI Chips After Jensen Huang’s Resignation? - Modern Diplomacy](https://news.google.com/rss/articles/CBMiwAFBVV95cUxPemplcTk1bnRmRkdFWUg1RUVCaGJ4c0JYbTQyQlR3SFlFUDk3NXVtZklKUUw5NURPX295U0lLZ2lLZnF0WUtaNDZiVUJMX2tlcmRhbVJZVkxMNVJNZkIzRkEyTHB1bk15Q0lqSTh3ZmNES1pDQV84QjZxYVhoUVdhWDliODZ5NEtfMmtseEhFMDFYMXRIR3VNQkZ0VUQ0Yk00MTVWSDRjb0ZBY3JJc2MtVndIUGNTaFZIai16aThQeHQ?oc=5)
- 事件类型：leadership
- 信息可用：2026-11-13T14:14:56.845403+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance
- 触发原因：公司名称直接匹配；重大事件关键词：leadership；接近预定事件窗口

### NVDA · 65/100
- [Trump’s Commerce chief Lutnick criticized over chip exports after Nvidia CEO resignation - American Journal of Transportation](https://news.google.com/rss/articles/CBMiswFBVV95cUxPZ25tTDRicUFvbmtoeEtHem13WlFfbWczbHlNa0ItbkRhdXdkd3hBQTJCX19zQnFJVTh6X1FzS2hlWS1jOTIxZ2l3Zzh6Y0tvRl9XWHJKeHZXT1p4NGJVa0I4WnpKaWhsYzAweDY1bHRLRk1ibDgwUXRuSDVnaEI2UDM3RGNQb2xYNkdHLWEyY0hMTTNCWENhMkYtb2lfVkFRdFQwbEp4NlB2RWI5aWNvQkswZw?oc=5)
- 事件类型：leadership
- 信息可用：2026-11-13T14:14:56.847452+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance
- 触发原因：公司名称直接匹配；重大事件关键词：leadership；接近预定事件窗口

### NVDA · 65/100
- [What to Know About Colette Kress, Nvidia’s New Interim Chief Executive - The New York Times](https://news.google.com/rss/articles/CBMiigFBVV95cUxPaGliajlaNEpxWDNkSmtUZzN5dTBVZkFiSHFCRWJQUC0wMk1xdm1nTXdfM1hZT0psZWJ4TF9HWTVqLTd4eUVfQmVleGtwT0lRWEhMWW1NZVkyOGFEVWdlOGJwemtiVUhldm1HQnJtQnlJc0lVUFJQdFQ5Wk9lSGRXc0g0b0xXTU0yZGc?oc=5)
- 事件类型：leadership
- 信息可用：2026-11-15T16:41:42.727520+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance
- 触发原因：公司名称直接匹配；重大事件关键词：leadership；接近预定事件窗口

### NVDA · 65/100
- [Jensen and Lori Huang's Nvidia fortune is jointly controlled. How that makes things complicated now that he's resigned - CNBC](https://news.google.com/rss/articles/CBMiogFBVV95cUxPWGxLNjZNa25ON3VOUTBoQXNEV0hsdlBFaWdsRklhaWVRSHhnR1ZDbFB4LUc4NE9XVmZVbF91bk4ybVJzMVAwZXZCZHJqU3ZxR1gzdjQyYmprYmo4UHJCNERfZDYxaDdLdlBrS01zNEE1Mm9jM0pOOFdlM2FFbGVmREdTTktwV3RHQm1Wd3duWWNVdEliRU04UGJNUjhXUmZDYXfSAacBQVVfeXFMT2pJb0xWQlJDRWQ0dV9TU3dGM3ladWplS2JuT0ptVDFhR1FWaFgtNzlja0tEX2lWY2FuUjJZMkNIbVZwLW5ibUlnd0NBRmc4T2k4ZG1WWC15T3p0b09YaEREeGUzQ0txRUlVRHo3eHY3QWx1UWI2c3NuSEVCU3NVMzl2NGM3YTlnaDRfdHM5U0JyQ25HNlVlQUNLd084dWV6X2VVUEl1TWc?oc=5)
- 事件类型：leadership
- 信息可用：2026-11-14T18:18:27.638085+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance
- 触发原因：公司名称直接匹配；重大事件关键词：leadership；接近预定事件窗口

### NVDA · 65/100
- [CFO Colette Kress to serve as interim leader after Nvidia CEO Jensen Huang resignation | CNN Business - CNN](https://news.google.com/rss/articles/CBMicEFVX3lxTFBVV0ZxeFgzelpIZUV3Ry1ybGhVTnBGMHpIaldZb1hTWkxrb2NJdDNFOFdoVUVTdWctOXpONXBLbVBsWDFWaHpaNTdjMlpjaGFla0FlamEtS21PMGZpbHBBOU5iQ0Nud1c3bkJXVTZBRlE?oc=5)
- 事件类型：leadership
- 信息可用：2026-11-15T16:41:43.578806+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance
- 触发原因：公司名称直接匹配；重大事件关键词：leadership；接近预定事件窗口

### NVDA · 65/100
- [Nvidia stock closes down over 4% after CEO Jensen Huang announces resignation - CNBC](https://news.google.com/rss/articles/CBMigAFBVV95cUxQVFBOVnFZT1F2M3oteUktWm1qb29oLW5DLW9MZ2pBRzhEenlNZWFERC1NRXJlSV9saDN5MmNRZzdzQm0xQ0hWSzVpSktBSy00aDZlUTcyQzd2Vmlia1F1UTlEdE11anNMVE10RDNEVlc4cUlMcW5CRlpxaWFEbDh2Mg?oc=5)
- 事件类型：leadership
- 信息可用：2026-11-14T18:18:27.637009+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance
- 触发原因：公司名称直接匹配；重大事件关键词：leadership；接近预定事件窗口

### NVDA · 65/100
- [Nvidia-Favored Marvell and Lumentum Announce Merger: What Does This Mean for NVDA? - TradingKey](https://news.google.com/rss/articles/CBMi2wFBVV95cUxQbFpyOHl5Wjh4NXVBZzF6WkpLS3VxNjBhcGw5NGFCM05RRDZXa1p6ZTE1WlNCSlZiMWZzTzJtaWk4X1pLRmtxSk4zWHZJRzNUbnEyajlhUVl3VXZhTTJaX0R3QUYxMWtGVVplQ0dJTHFXUUFVMVFMd2psSklhZjhjR0ZXZ0JYcmd2MG9uNVJSdHM0a2M2TGppMVJqd0dIRU02SHRxTlNhTEFKSkEzMW8xRFJkeHhsdUZDbHJTcG14aHY3bENNXzM1Nm1zTTVtWFhvOHU1NVZVb2tNYU0?oc=5)
- 事件类型：integration
- 信息可用：2026-11-03T14:44:58.023943+00:00；最早进入研究：2026-11-04
- 日期校验：verified-ordering
- 重新检查：integration_execution, valuation
- 触发原因：公司名称直接匹配；股票代码直接匹配；重大事件关键词：integration


## 日期异常隔离

当前没有日期异常事件。
