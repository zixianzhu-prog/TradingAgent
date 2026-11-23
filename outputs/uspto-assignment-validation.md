# USPTO 专利受让独立核验

> 待核验 7 家；已由官方记录核验 0 家；官方记录 0 条。

> SEC 中的专利/许可说法只负责建立队列。只有 USPTO Assignment Center/Open Data Portal 的受让记录才能把独立核验改为通过。

| 公司 | SEC 说法 | USPTO 状态 | 官方检索 |
|---|---:|---|---|
| ALEC · Alector, Inc. | 3 | pending-official-search | [按受让人检索](https://assignmentcenter.uspto.gov/search/intellectualProperty/search) |
| ANTX · AN2 Therapeutics, Inc. | 1 | pending-official-search | [按受让人检索](https://assignmentcenter.uspto.gov/search/intellectualProperty/search) |
| BDSX · BIODESIX INC | 1 | pending-official-search | [按受让人检索](https://assignmentcenter.uspto.gov/search/intellectualProperty/search) |
| HURA · TuHURA Biosciences, Inc./NV | 1 | pending-official-search | [按受让人检索](https://assignmentcenter.uspto.gov/search/intellectualProperty/search) |
| IRD · Opus Genetics, Inc. | 1 | pending-official-search | [按受让人检索](https://assignmentcenter.uspto.gov/search/intellectualProperty/search) |
| PRME · Prime Medicine, Inc. | 1 | pending-official-search | [按受让人检索](https://assignmentcenter.uspto.gov/search/intellectualProperty/search) |
| TECX · Tectonic Therapeutic, Inc. | 1 | pending-official-search | [按受让人检索](https://assignmentcenter.uspto.gov/search/intellectualProperty/search) |

## 导入规则

把官方搜索结果规范化写入 `trend-agent/uspto-assignment-evidence.json`：必须包括 ticker、assignee、assignor、recordedAt、reelFrame、url。
URL 必须来自 USPTO 官方域名；公司网页、Google Patents 或名称相似都不能把状态改为 verified。
