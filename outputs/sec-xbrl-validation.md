# SEC XBRL 财务数字自动核验

> 只比较会计含义匹配的字段。缺失的标准标签不会被判定为失败，系统也不会自动覆盖人工确认的数据。

| 股票 | 状态 | 通过 | 待审 | 无可比标签 |
| --- | --- | ---: | ---: | ---: |
| TEM | verified | 2 | 0 | 2 |
| SDGR | verified | 2 | 0 | 2 |
| RXRX | verified | 3 | 0 | 1 |
| ABCL | verified | 4 | 0 | 0 |
| CERT | verified | 3 | 0 | 1 |
| NTRA | verified | 3 | 0 | 1 |
| SOPH | insufficient-xbrl | 0 | 0 | 4 |
| GH | verified | 2 | 0 | 2 |

## TEM · verified

[SEC Company Facts 原始 JSON](https://data.sec.gov/api/xbrl/companyfacts/CIK0001717115.json)

| 指标 | 本地值 | SEC值 | 差异 | 结果 | XBRL标签 |
| --- | ---: | ---: | ---: | --- | --- |
| 季度收入 | 411.5 | 411.537 | -0.03699999999997772 | pass | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax |
| 季度净利润/亏损 | -14.9 | -14.851 | -0.04899999999999949 | pass | us-gaap:NetIncomeLoss |
| 现金及短期投资 | 854.4 | — | — | unavailable | — |
| 流通股份 | 182401637 | — | — | unavailable | — |

## SDGR · verified

[SEC Company Facts 原始 JSON](https://data.sec.gov/api/xbrl/companyfacts/CIK0001490978.json)

| 指标 | 本地值 | SEC值 | 差异 | 结果 | XBRL标签 |
| --- | ---: | ---: | ---: | --- | --- |
| 季度收入 | 64.5 | 64.491 | 0.009000000000000341 | pass | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax |
| 季度净利润/亏损 | -37.7 | -37.711 | 0.01099999999999568 | pass | us-gaap:NetIncomeLoss |
| 现金及短期投资 | 373.0 | — | — | unavailable | — |
| 流通股份 | 74805628 | — | — | semantic-skip | — |

## RXRX · verified

[SEC Company Facts 原始 JSON](https://data.sec.gov/api/xbrl/companyfacts/CIK0001601830.json)

| 指标 | 本地值 | SEC值 | 差异 | 结果 | XBRL标签 |
| --- | ---: | ---: | ---: | --- | --- |
| 季度收入 | 18.6 | 18.552 | 0.04800000000000182 | pass | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax |
| 季度净利润/亏损 | -119.0 | -119.036 | 0.036000000000001364 | pass | us-gaap:NetIncomeLoss |
| 现金及短期投资 | 748.7 | — | — | unavailable | — |
| 流通股份 | 623367849.0 | 622759259.0 | 608590.0 | pass | dei:EntityCommonStockSharesOutstanding |

## ABCL · verified

[SEC Company Facts 原始 JSON](https://data.sec.gov/api/xbrl/companyfacts/CIK0001703057.json)

| 指标 | 本地值 | SEC值 | 差异 | 结果 | XBRL标签 |
| --- | ---: | ---: | ---: | --- | --- |
| 季度收入 | 10.6 | 10.639 | -0.0389999999999997 | pass | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax |
| 季度净利润/亏损 | -40.8 | -40.758 | -0.041999999999994486 | pass | us-gaap:NetIncomeLoss |
| 现金及短期投资 | 790.0 | 764.424 | 25.576000000000022 | pass | us-gaap:CashCashEquivalentsAndShortTermInvestments |
| 流通股份 | 324047363.0 | 326617896.0 | -2570533.0 | pass | dei:EntityCommonStockSharesOutstanding |

## CERT · verified

[SEC Company Facts 原始 JSON](https://data.sec.gov/api/xbrl/companyfacts/CIK0001827090.json)

| 指标 | 本地值 | SEC值 | 差异 | 结果 | XBRL标签 |
| --- | ---: | ---: | ---: | --- | --- |
| 季度收入 | 94.9 | 94.901 | -0.000999999999990564 | pass | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax |
| 季度净利润/亏损 | 5.592 | 5.592 | 0.0 | pass | us-gaap:NetIncomeLoss |
| 现金及短期投资 | 214.9 | — | — | unavailable | — |
| 流通股份 | 152543402.0 | 152543402.0 | 0.0 | pass | dei:EntityCommonStockSharesOutstanding |

## NTRA · verified

[SEC Company Facts 原始 JSON](https://data.sec.gov/api/xbrl/companyfacts/CIK0001604821.json)

| 指标 | 本地值 | SEC值 | 差异 | 结果 | XBRL标签 |
| --- | ---: | ---: | ---: | --- | --- |
| 季度收入 | 794.0 | 793.981 | 0.019000000000005457 | pass | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax |
| 季度净利润/亏损 | -59.9 | -59.912 | 0.012000000000000455 | pass | us-gaap:NetIncomeLoss |
| 现金及短期投资 | 1097.2 | — | — | unavailable | — |
| 流通股份 | 145004521.0 | 145004521.0 | 0.0 | pass | dei:EntityCommonStockSharesOutstanding |

## SOPH · insufficient-xbrl

[SEC Company Facts 原始 JSON](https://data.sec.gov/api/xbrl/companyfacts/CIK0001840706.json)

| 指标 | 本地值 | SEC值 | 差异 | 结果 | XBRL标签 |
| --- | ---: | ---: | ---: | --- | --- |
| 季度收入 | 24.3 | — | — | unavailable | — |
| 季度净利润/亏损 | -20.3 | — | — | unavailable | — |
| 现金及短期投资 | 93.7 | — | — | unavailable | — |
| 流通股份 | 85658321 | — | — | semantic-skip | — |

## GH · verified

[SEC Company Facts 原始 JSON](https://data.sec.gov/api/xbrl/companyfacts/CIK0001576280.json)

| 指标 | 本地值 | SEC值 | 差异 | 结果 | XBRL标签 |
| --- | ---: | ---: | ---: | --- | --- |
| 季度收入 | 361.0 | 360.975 | 0.024999999999977263 | pass | us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax |
| 季度净利润/亏损 | — | — | — | unavailable | — |
| 现金及短期投资 | 1100.0 | — | — | unavailable | — |
| 流通股份 | 135285975.0 | 135285975.0 | 0.0 | pass | dei:EntityCommonStockSharesOutstanding |
