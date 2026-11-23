# 事件驱动重新验证队列

生成日期：2026-11-23

> 事件只触发重新研究，不会自动改变评级、仓位或创建交易。发布时间、发现时间或as-of不一致的事件会被隔离，不能使Serenity门槛失效。

## 事件日历

| 股票 | 事件 | 日期 | 状态 | 重新检查 |
| --- | --- | --- | --- | --- |
| ABCL | Q3 2026 earnings | 2026-11-09 | evidence-received | earnings_validation, cash_runway, dilution, partner_economics |
| NVDA | Independent board investigation | 2026-11-10 | evidence-received | management_governance, reputation_risk, counter_thesis |
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
| HTFL | commercial adoption, reimbursement and cash update | 待公布 | unscheduled | earnings_validation, customer_dependency, cash_generation, valuation |
| HTFL | FDA and CPT/reimbursement update | 待公布 | unscheduled | chokepoint_evidence, customer_dependency, counter_thesis |
| CBLL | hospital adoption, recurring revenue and cash update | 待公布 | unscheduled | earnings_validation, customer_dependency, cash_generation, valuation |
| CBLL | FDA and Medicare NTAP update | 待公布 | unscheduled | chokepoint_evidence, customer_dependency, counter_thesis |
| CAI | molecular profiling volume, pharma revenue and cash update | 待公布 | unscheduled | earnings_validation, customer_dependency, cash_generation, valuation |
| CAI | biopharma data and companion diagnostic adoption | 待公布 | unscheduled | customer_dependency, chokepoint_evidence, multi_node_control |

## 待重新验证任务

### NVDA · 85/100
- [NVIDIA Board of Directors Establishes National Security and Export Control Oversight Committee](https://nvidianews.nvidia.com/news/nvidia-board-of-directors-establishes-national-security-and-export-control-oversight-committee)
- 事件类型：leadership, governance
- 信息可用：2026-11-17T21:46:55.510620+00:00；最早进入研究：2026-11-18
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；股票代码直接匹配；重大事件关键词：leadership, governance；官方或监管来源

### NVDA · 75/100
- [NVIDIA Announces Financial Results for Third Quarter Fiscal 2027](https://nvidianews.nvidia.com/news/nvidia-announces-financial-results-for-third-quarter-fiscal-2027)
- 事件类型：earnings, clinical, partnership, financing, integration, leadership
- 信息可用：2026-11-17T21:46:55.510325+00:00；最早进入研究：2026-11-18
- 日期校验：verified-ordering
- 重新检查：cash_generation, cash_runway, clinical_validation, counter_thesis, customer_dependency, dilution, earnings_validation, falsifiers, integration_execution, management_governance, partner_economics, valuation
- 触发原因：公司名称直接匹配；股票代码直接匹配；重大事件关键词：earnings, clinical, partnership, financing, integration, leadership

### NVDA · 70/100
- [NVIDIA Board Reinstates Jensen Huang as President, CEO and Board Director](https://nvidianews.nvidia.com/news/nvidia-board-reinstates-jensen-huang-as-president-ceo-and-board-director)
- 事件类型：leadership, governance
- 信息可用：2026-11-23T18:15:17.000793+00:00；最早进入研究：2026-11-24
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；股票代码直接匹配；重大事件关键词：leadership, governance

### NVDA · 70/100
- [What we learned from Nvidia’s first earnings call without Jensen Huang - SiliconANGLE](https://news.google.com/rss/articles/CBMiqgFBVV95cUxOWFUzTFFzeW1OQi11OGFDaWVXdkhYUzJDXzY4Tk9IWklxU1dXSjcybk5wWkRpQ0UtZk9ZYmRfYjFwMmJBUXloMXlFbDRoSmRWcXlsRE1EaWJkOG45LUhQWWx1WE1kQndhME5sbm1pRFh6SEtZVGYxQ0U1UmdGQy0xa1pPWUpMOGNjWjRoS0lldVhkY2JWMWpxcURFOEQ0OXBJS2dJZkJfV0h3Zw?oc=5)
- 事件类型：earnings
- 信息可用：2026-11-20T20:46:45.158916+00:00；最早进入研究：2026-11-23
- 日期校验：verified-ordering
- 重新检查：cash_generation, cash_runway, customer_dependency, earnings_validation, valuation
- 触发原因：公司名称直接匹配；重大事件关键词：earnings；官方或监管来源

### NVDA · 70/100
- [Ex-CEO Jensen Huang signals interest in returning to Nvidia after resigning amid scandal - PBS](https://news.google.com/rss/articles/CBMiwwFBVV95cUxNY0IwMTh0cnVtSFEtamprcXFCbWJISEc3ZE5EcHBWODdYa1NMOXRCb05za2NDVUVGTHNiR3g4cnBnbE02VkZKMU81dnFMa3pTRmgyWWhXQklJRGh2Um9PZzJRUzFJWjB1RFNzMkx1dEtTVGY2RnRGMkdoU3FqdkFwbkJmcGRLaDZvUnIxeVhTamtNMTh1amZHbFhMMjE4c3J3akNld2lld0ROZ2F0am50WnhwSXhURkpuNTdwdDFFa3FDelU?oc=5)
- 事件类型：reputational
- 信息可用：2026-11-18T22:07:31.593211+00:00；最早进入研究：2026-11-19
- 日期校验：verified-ordering
- 重新检查：counter_thesis, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；重大事件关键词：reputational；官方或监管来源

### NVDA · 70/100
- [Jensen Huang’s Net Worth Is Now Down 16% Since Start Of Last Week’s Affairs Scandal - Forbes](https://news.google.com/rss/articles/CBMi6wFBVV95cUxNWEdFUWJ0eWdGV2Y4VFZrVEt1dE4zejdOQ3BkVVRDLTBwNFkteExzb2M0YzRQbEZXcVFRUzlDQnVWR2JteUdYbmFDaEk1ZmNzeFFLa0RVZC1nbFhhckl4ZlFXRVphdWFFbVU3NWdGZzBxZHFPNkdEUFVHZ0ZzS3NlcWYtaVUxQmY1amNaS01WSTFYUFpGanNxQ0hsTWNmc01yRFNIZ2I2c3B5aUZ3aGVhcUVmZFRWckZVTVlMenRNdmppUXhhNUo2YklXYU5JbFgtYXJQSmdOb1dDclNxUVF6U3ktbldVVW9ZWmhZ?oc=5)
- 事件类型：reputational
- 信息可用：2026-11-17T21:46:55.124008+00:00；最早进入研究：2026-11-18
- 日期校验：verified-ordering
- 重新检查：counter_thesis, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；重大事件关键词：reputational；官方或监管来源

### NVDA · 70/100
- [NVIDIA Announces CEO Transition](https://nvidianews.nvidia.com/news/nvidia-announces-ceo-transition)
- 事件类型：earnings, leadership
- 信息可用：2026-11-13T14:14:57.120196+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, valuation
- 触发原因：公司名称直接匹配；股票代码直接匹配；重大事件关键词：earnings, leadership

### NVDA · 65/100
- [Nvidia (NVDA) CEO Jensen Huang Resigned As The SEC Opened An Accounting Probe - Yahoo Finance](https://news.google.com/rss/articles/CBMimAFBVV95cUxQOXN0TUVMd3I0Sy1tTVg2RkdxSjlaSzRqS0h5VEFab1VmajZ3Z2xTWUhOSjN3TDIzSWZpOGRnclc2NXFaRGdjT25TNzhlZ09pN05KeDF6SEhFMkpXWEI4THRZa2NDc011TjhlRTc1ZENkU3dTTjRNS3RMOTluaUY1MmhIRHRLVnRyVDFUZkhqcGM4YmZMem45cg?oc=5)
- 事件类型：leadership
- 信息可用：2026-11-23T03:55:59.197297+00:00；最早进入研究：2026-11-24
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance
- 触发原因：公司名称直接匹配；股票代码直接匹配；重大事件关键词：leadership

### NVDA · 65/100
- [NVIDIA Expands Commitments With Supply Chain Partners to Support AI Infrastructure Buildout](https://nvidianews.nvidia.com/news/nvidia-expands-commitments-with-supply-chain-partners-to-support-ai-infrastructure-buildout)
- 事件类型：partnership, integration, leadership
- 信息可用：2026-11-18T22:07:32.773155+00:00；最早进入研究：2026-11-19
- 日期校验：verified-ordering
- 重新检查：counter_thesis, customer_dependency, earnings_validation, integration_execution, management_governance, partner_economics, valuation
- 触发原因：公司名称直接匹配；重大事件关键词：partnership, integration, leadership

### NVDA · 65/100
- [Nvidia-Favored Marvell and Lumentum Announce Merger: What Does This Mean for NVDA? - TradingKey](https://news.google.com/rss/articles/CBMi2wFBVV95cUxQbFpyOHl5Wjh4NXVBZzF6WkpLS3VxNjBhcGw5NGFCM05RRDZXa1p6ZTE1WlNCSlZiMWZzTzJtaWk4X1pLRmtxSk4zWHZJRzNUbnEyajlhUVl3VXZhTTJaX0R3QUYxMWtGVVplQ0dJTHFXUUFVMVFMd2psSklhZjhjR0ZXZ0JYcmd2MG9uNVJSdHM0a2M2TGppMVJqd0dIRU02SHRxTlNhTEFKSkEzMW8xRFJkeHhsdUZDbHJTcG14aHY3bENNXzM1Nm1zTTVtWFhvOHU1NVZVb2tNYU0?oc=5)
- 事件类型：integration
- 信息可用：2026-11-03T14:44:58.023943+00:00；最早进入研究：2026-11-04
- 日期校验：verified-ordering
- 重新检查：integration_execution, valuation
- 触发原因：公司名称直接匹配；股票代码直接匹配；重大事件关键词：integration

### NVDA · 60/100
- [Jensen Huang Returns: Timeline Of The Scandal That Led To Resignation And Comeback - Forbes](https://news.google.com/rss/articles/CBMixwFBVV95cUxPVWFXRkhZY2RzUE5maUxaOW11N3NYbXZabWhvZFFiMHdZLUE1aEdPd01uSjNaYjhRazAyVFNWbW0wd28zV2ZlcElaWTZnejJ3SEVNWHBsek9kTEppMjA2REU0ZlhiR1UxZ2NBTWVhZHl4WDFmM3l4MFZqbVZURXdSU2xuU3F5QnE0d3VlVVNqUnNwUEdMc1I4RS1HLXMwRzlwSWV2aTFWSlJlRDliUGsxYmc4UUpZdGlJczdEQjJqcXhSdHM4YnpJ?oc=5)
- 事件类型：leadership, reputational
- 信息可用：2026-11-23T18:15:15.945806+00:00；最早进入研究：2026-11-24
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；重大事件关键词：leadership, reputational

### NVDA · 60/100
- [Nvidia Earnings Live Updates: First Report Since Jensen Huang’s Resignation Beats Expectations - The New York Times](https://news.google.com/rss/articles/CBMihAFBVV95cUxNdFFIYV9qR0U3Q3Q5bFNVM2VscDYtYU01YkxpSDFVRUkxNkYyX0l1NlNDYmRDU25NaHhJR0JvV0tnMDQxRHBvYkx5Y21WaDVwVDA5MjdaNndERWNmZlp2dzVIdm8ySG40RzJRWGVfY1RCdTNkd2NmVlN2Q3JURVpfNWptNDk?oc=5)
- 事件类型：earnings, leadership
- 信息可用：2026-11-20T20:46:45.158669+00:00；最早进入研究：2026-11-23
- 日期校验：verified-ordering
- 重新检查：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, valuation
- 触发原因：公司名称直接匹配；重大事件关键词：earnings, leadership

### NVDA · 60/100
- [Four takeaways from Nvidia’s first earnings report after Jensen Huang scandal | CNN Business - CNN](https://news.google.com/rss/articles/CBMilAFBVV95cUxQX05adF9NVmRmbVFrTEE1NmZfMXhnYkNPbzl6WEd2Q0tfMkY3eEdZNmZDcUJtdlhqYURpRDZXTkQ4eWJBcXpDaFdGRGl0cjhUN010akJOdm1IdDZla2ZmUjZmbkdEOF9BeXY5WXlCbk15VGFud0o5Q0J3WjlOVlRveUpKZlg0VEk0dVlDa0JpTmhXRS1y?oc=5)
- 事件类型：earnings, reputational
- 信息可用：2026-11-23T03:56:00.116038+00:00；最早进入研究：2026-11-24
- 日期校验：verified-ordering
- 重新检查：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, reputation_risk, valuation
- 触发原因：公司名称直接匹配；重大事件关键词：earnings, reputational

### NVDA · 60/100
- [Four takeaways from Nvidia’s first earnings report after Jensen Huang scandal - CNN](https://news.google.com/rss/articles/CBMilAFBVV95cUxQX05adF9NVmRmbVFrTEE1NmZfMXhnYkNPbzl6WEd2Q0tfMkY3eEdZNmZDcUJtdlhqYURpRDZXTkQ4eWJBcXpDaFdGRGl0cjhUN010akJOdm1IdDZla2ZmUjZmbkdEOF9BeXY5WXlCbk15VGFud0o5Q0J3WjlOVlRveUpKZlg0VEk0dVlDa0JpTmhXRS1y?oc=5)
- 事件类型：earnings, reputational
- 信息可用：2026-11-18T22:07:31.600053+00:00；最早进入研究：2026-11-19
- 日期校验：verified-ordering
- 重新检查：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, reputation_risk, valuation
- 触发原因：公司名称直接匹配；重大事件关键词：earnings, reputational

### NVDA · 60/100
- [Jensen Huang Scandal: Timeline That Led To His Resignation—And Potential Comeback - Forbes](https://news.google.com/rss/articles/CBMi1gFBVV95cUxPTGI5aEp1Q2tCeGVvSlZkb2swNnNyRzVHekhQLXp2eGRDU3ZqUDYySHVnQjF2UEdhWEc5b1B3ZE1OaW05c2FNZzhzUGVfa1hPLTlhZjVuQWhqRFN1c0cyY1pBdThHal9BRmd4V0hucW41UnNjWWhEc2dpMjhmSUpGM0dYNWhwazNlWWdCTWVrWEptY3E2SzVlbnRzVW1fQTkwMTUtVGc2Zms5QnNKcEI4RjY3ZXo1V0g1SkZSeEk1dEtlVTQyb05KRDVQZ1k3U0hlQTU0Y2dB?oc=5)
- 事件类型：leadership, reputational
- 信息可用：2026-11-17T21:46:54.451225+00:00；最早进入研究：2026-11-18
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；重大事件关键词：leadership, reputational

### NVDA · 60/100
- [Nvidia to report Q3 earnings amid Huang scandal - Yahoo Finance](https://news.google.com/rss/articles/CBMiqwFBVV95cUxOUGhYaS1ZSloxYlVnRV9hQ0MyWVdfZU44cnI3dmRqRXAwSURBS2VxeGJZcExTV003YUxoMjNrelRscG9mWGVZM19yRmpRN0JhU09OWWc1bUZYZU1vRlBFeG0xM2VfVGRiLXBIS0lwZTZLd0ZBaldWVVJUS05BWU1sQkdFTU1yM3lIaTMzVnh3cVo0MmpRS2s3WDFmbGpTNzhWaVdGdlB0LW9JVUE?oc=5)
- 事件类型：earnings, reputational
- 信息可用：2026-11-19T21:28:31.750119+00:00；最早进入研究：2026-11-20
- 日期校验：verified-ordering
- 重新检查：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, reputation_risk, valuation
- 触发原因：公司名称直接匹配；重大事件关键词：earnings, reputational

### NVDA · 60/100
- [Nvidia stock falls ahead of earnings as company reels from Huang resignation - CNBC](https://news.google.com/rss/articles/CBMiiwFBVV95cUxQUDhQMU5rWGhWemtOTG9CLWY2Q0tCWVVJejRxYU50bXo0U3N5cFE1R0JkQWpPN3RvakZtOERpVk5WSmJIbVlfaVlfTGdZY001TWRqV1ZaTk5yME5TdVQyek81TXVza2REZFNfRnJ5LW9rUmNRT21wNy1FVEZBdUlZaGdINXVqdlkzSzlz0gGQAUFVX3lxTE1hOFNxWkE1WDFjYTgzQVNPNE9MUEIwSmwxazl1QXlpaEo5SGlfSUVJdFJFWjZ4eGF6cXVVQkhoRU5pTmpJVF9jMFJEYjVabW9BMU5Fc0lpNGVXbURhVU4zLTlVQ1E4S0ZRX3hubnRDN0l3QThkS3NienJxZm9oT1BYMUk3M25wZ3lNbDZaY1RTSg?oc=5)
- 事件类型：earnings, leadership
- 信息可用：2026-11-17T21:46:54.451369+00:00；最早进入研究：2026-11-18
- 日期校验：verified-ordering
- 重新检查：cash_generation, cash_runway, counter_thesis, customer_dependency, earnings_validation, management_governance, valuation
- 触发原因：公司名称直接匹配；重大事件关键词：earnings, leadership

### NVDA · 60/100
- [NVIDIA Announces Collaboration With IBM and Fermi National Accelerator Laboratory to Launch Quantum-Classical Codesign Platform, Plus Error-Correction Breakthrough to Advance Practical Quantum Computing](https://nvidianews.nvidia.com/news/nvidia-announces-collaboration-with-ibm-and-fermi-national-accelerator-laboratory-to-launch-quantum-classical-codesign-platform-plus-error-correction-breakthrough-to-advance-practical-quantum-computing)
- 事件类型：partnership, integration
- 信息可用：2026-11-17T21:46:55.511466+00:00；最早进入研究：2026-11-18
- 日期校验：verified-ordering
- 重新检查：customer_dependency, integration_execution, partner_economics, valuation
- 触发原因：公司名称直接匹配；重大事件关键词：partnership, integration

### NVDA · 60/100
- [Nvidia CEO Huang resigns amid affair scandals, board names CFO Colette Kress interim CEO - Yahoo Finance](https://news.google.com/rss/articles/CBMi4AFBVV95cUxQZzNYVy04Z1l4VlFPaDZDbW5wb0M2d1RTbFJVaWEwTGdSU0oxZkM5UG1aWlkzaVFIZGE5ZmpnaE5EOWZXdnl3Y3dYWmZrZ3l0Q2ItUU5EU1o4dHhYczFuRElaV2ZhcGNhVWlqTkdiWGIwUzNCVG5yRzR0VXJHMVlFT2xmX3ZzbU9SVEdrYzJBczh1eFZPYnduVXNCY21YOE9SMS1jRUtCdnRIckt4VkttOFRrZzNMLWhFUFRyc1k3dkhHMDJNbUFGLWtldmtOcENSbFpXYkNfSFFjRWFJdTFJVg?oc=5)
- 事件类型：leadership, reputational
- 信息可用：2026-11-14T18:18:28.353469+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；重大事件关键词：leadership, reputational

### NVDA · 60/100
- [Timeline of a scandal: How Jensen Huang's abrupt resignation unfolded at Nvidia - CBS News](https://news.google.com/rss/articles/CBMihAFBVV95cUxNWTN3bmdNV3NVS2liaHp3a1BkWlQweUhxc0ZQT0Z1RTItR3dLTzd0OXU4SktsZ1lpRmNWMmloVS1NeFZoTFA4Sm5qcUc3MnpZU3hGTjJsUEpDZUlIQlVxTEY3ajlJU2hyX19GU0JFLTdmLXNsRHl1UnFzUmZJSVNVcjJKdE0?oc=5)
- 事件类型：leadership, reputational
- 信息可用：2026-11-14T18:18:28.353666+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；重大事件关键词：leadership, reputational

### NVDA · 60/100
- [Lawmakers Urge Federal Probe Into Jensen Huang Over Affair With Chinese Spy—And Call For His Resignation - Forbes](https://news.google.com/rss/articles/CBMi7wFBVV95cUxOOWNxTEVDLXBfcHVuZXhBc0FOaGtKYmgyOXpPUldsZmhSU3JWQ3JUZGVOOWhQTDRaMjdPZS1KdXZTRm01bGxyTWpvTWdsMlU0UHdTMS1rcHU2dWZkOURsRXNkSEdEVmF4SkEtejlWbkZvcU9oa0ZrZ3ZzVlVYbk9VMm04N1g3b0c5RXczZnBPek5mRkZMQmczcThydXhFVW02Zml0RkRjTC1iV21ZTmwtb0FncHp3S1VwaHBDU0tubmtoTTJ3VjlHbUk2ZTR5VHlhbnI3ZGduMnI3eXFJS2xUVWctaGhnWnRXT25DeFhOUQ?oc=5)
- 事件类型：leadership, reputational
- 信息可用：2026-11-20T20:46:45.823883+00:00；最早进入研究：2026-11-23
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；重大事件关键词：leadership, reputational

### NVDA · 60/100
- [Jensen Huang affair in DC: Resignation calls and moves to tighten Nvidia China exports - CNBC](https://news.google.com/rss/articles/CBMiiAFBVV95cUxPWjJRY2daaGR0MlE5NzU0bndocWZPVF9qODRlRlBzUUVLN1dyNkE2VXlJeUdGanF2NkQ5OGVZMmJTYk9xY244NU9sUHppeFU2dVlHcVRwWFptNG9CSUN6ay1Ic3NVdFJRZTNkY05nQzJJUFJsSVp1N21LRElnSHotZmZyYVR2a25v0gGOAUFVX3lxTE5Ldzk4eUYyX0FWR3NfeDhpME5oOW5oSTZCQmFsUDFyMGUyRjZLSmJsOE0wYVlrRVFsZldKbDEzd0JIUVRTMlkwYXFLZFFBSTl1UXo3c2N2VUJPbjRHeURyRHpKbVpWMHI1d1NHMURuZFJJY1FOM1l2MHlVM2o5Vkl5eU9WSGdZT0piQXBwaWc?oc=5)
- 事件类型：leadership, reputational
- 信息可用：2026-11-20T20:46:45.823627+00:00；最早进入研究：2026-11-23
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；重大事件关键词：leadership, reputational

### NVDA · 60/100
- [Jensen Huang affair puts Nvidia's future at risk, with no clear successor to the renowned CEO - CNBC](https://news.google.com/rss/articles/CBMif0FVX3lxTE5EcnlNdzFRY2RtTFNiaVYxeFhDSnJIck5qckxaeE4wLVRVYWFFSkZoc2tJNjRmLWxXSGxQMXFuYi1YeHpYbGNjOW5CMy1rNHNTaDlCWEpfUEpvYkprUEVkZjBJTTl6SmZRLWtNd1B3czh3ckl2ejlYcHFUN1FUODTSAYQBQVVfeXFMUHpzWXc5ZVl0T3JVSHlPT3NGUzh2cTFtd1hVbjRqbFNDQm5CclZwSmgtQ0I0akV6WHExSG9iZHptd0MxZ1RTOVhQYjlHbHNid2g3M0docFZBMmVCWGRjSzdIZjlFbFE1V3JjVHkyUmcxQWxFaDNsTHl2UUxHMTVxTlNvcDF2?oc=5)
- 事件类型：leadership, reputational
- 信息可用：2026-11-14T18:18:27.636848+00:00；最早进入研究：2026-11-16
- 日期校验：verified-ordering
- 重新检查：counter_thesis, earnings_validation, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；重大事件关键词：leadership, reputational

### NVDA · 60/100
- [Nvidia CEO Jensen Huang’s image tarnished by board investigation and affair, analysts say - Los Angeles Times](https://news.google.com/rss/articles/CBMi5wFBVV95cUxNaGctWjNodnZlbGFEYmQzZGEtN3hCeFhOeG4weUtJTGVsVGI2YUFVeVRfME9OZ3FtUmgtU0RUWGRrOFVBb2dMckhOVjRLY0NDQ09ST0lnZXBzSHdvdTYyeFVCYlltXzA0UWliMmVoelFIejJTZXk0Y1BWYXpLbjNDSXd1XzZOM0k4cjVjVGFSdXFvVDFvVkRRcFR0LWlpV2ZJOTVzcmdFZUxOVDI1cTFfazZEeEdEd0FCVmhLYzJidkRvU2NJd1VmdHNzeVU3Y2NCM0kyb0cyN29NLUVjbWpHMWV3ejlIZW8?oc=5)
- 事件类型：governance, reputational
- 信息可用：2026-11-20T20:46:45.823947+00:00；最早进入研究：2026-11-23
- 日期校验：verified-ordering
- 重新检查：counter_thesis, management_governance, reputation_risk
- 触发原因：公司名称直接匹配；重大事件关键词：governance, reputational


## 日期异常隔离

当前没有日期异常事件。
