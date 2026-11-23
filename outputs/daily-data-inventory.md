# 每日运行数据台账

生成时间：2026-11-23T19:56:43.449010+00:00

> 原始运行可以重复保存，但冻结预测按股票和市场日期去重。重复运行不会伪造新的独立预测样本。

## 总览

- 新闻原始记录：**3236** 条
- 冻结预测：**170** 条
- 独立市场日期：**13** 天
- 最新预测对应市场日：**2026-11-23**

## 新闻入库日期

| 发现日期 | 新入库文章 | 来源数 |
|---|---:|---:|
| 2026-11-03 | 1105 | 128 |
| 2026-11-04 | 182 | 96 |
| 2026-11-09 | 279 | 116 |
| 2026-11-10 | 225 | 78 |
| 2026-11-11 | 186 | 66 |
| 2026-11-12 | 102 | 77 |
| 2026-11-13 | 213 | 130 |
| 2026-11-14 | 193 | 61 |
| 2026-11-15 | 60 | 35 |
| 2026-11-16 | 85 | 51 |
| 2026-11-17 | 146 | 54 |
| 2026-11-18 | 78 | 43 |
| 2026-11-19 | 76 | 41 |
| 2026-11-20 | 97 | 51 |
| 2026-11-21 | 49 | 34 |
| 2026-11-23 | 160 | 74 |

## 冻结预测日期

| 市场日期 | 预测数 | 股票数 |
|---|---:|---:|
| 2026-11-02 | 7 | 7 |
| 2026-11-03 | 1 | 1 |
| 2026-11-04 | 12 | 12 |
| 2026-11-09 | 12 | 12 |
| 2026-11-10 | 11 | 11 |
| 2026-11-11 | 16 | 16 |
| 2026-11-12 | 16 | 16 |
| 2026-11-13 | 16 | 16 |
| 2026-11-17 | 16 | 16 |
| 2026-11-18 | 15 | 15 |
| 2026-11-19 | 16 | 16 |
| 2026-11-20 | 16 | 16 |
| 2026-11-23 | 16 | 16 |

## 分主题样本

| 队列 | 冻结记录 | 独立日期 | 股票数 |
|---|---:|---:|---:|
| ai-data-center-power | 11 | 7 | 2 |
| ai-medicine | 123 | 11 | 16 |
| core-biotech | 12 | 6 | 2 |
| robotics-automation | 24 | 6 | 4 |

## 未来表现回填

| 周期 | 已回填样本 | 独立预测日 |
|---:|---:|---:|
| 1 | 154 | 12 |
| 5 | 91 | 8 |

## 原始运行文件

| 队列 | 文件数 | 文件中的市场日期 |
|---|---:|---|
| core-biotech | 13 | 2026-11-02 (4次), 2026-11-04 (2次), 2026-11-09 (1次), 2026-11-10 (1次), 2026-11-11 (3次), 2026-11-12 (2次) |
| robotics-automation | 10 | 2026-11-02 (1次), 2026-11-04 (2次), 2026-11-09 (1次), 2026-11-10 (1次), 2026-11-11 (3次), 2026-11-12 (2次) |
| ai-data-center-power | 11 | 2026-11-02 (1次), 2026-11-03 (1次), 2026-11-04 (2次), 2026-11-09 (2次), 2026-11-10 (1次), 2026-11-11 (4次), 2026-11-12 (2次) |
| ai-medicine | 25 | 2026-11-04 (1次), 2026-11-09 (1次), 2026-11-10 (1次), 2026-11-11 (6次), 2026-11-12 (4次), 2026-11-13 (4次), 2026-11-17 (3次), 2026-11-18 (1次), 2026-11-19 (1次), 2026-11-20 (3次), 2026-11-23 (1次) |

## 主要报告

- ✅ `outputs/daily-investment-agent.md` · 2026-11-23T19:56:42.865590+00:00
- ✅ `outputs/hidden-gems.md` · 2026-11-23T18:22:59.928846+00:00
- ✅ `outputs/market-profile-audit.md` · 2026-11-23T18:22:59.590804+00:00
- ✅ `outputs/ai-medicine-5-10-year-thesis.md` · 2026-11-23T19:56:42.901577+00:00
- ✅ `outputs/serenity-gate-audit.md` · 2026-11-23T19:56:42.818702+00:00
- ✅ `outputs/event-revalidation-queue.md` · 2026-11-23T18:17:07.645523+00:00
- ✅ `outputs/finrobot-event-analysis.md` · 2026-11-13T14:24:31.189055+00:00
- ✅ `outputs/agent-benchmark-validation.md` · 2026-11-23T18:23:04.567548+00:00
- ✅ `outputs/ai-medicine-thesis-memory.md` · 2026-11-23T18:23:27.139194+00:00
- ✅ `outputs/scientific-frontier.md` · 2026-11-23T18:15:30.452202+00:00
- ✅ `outputs/science-commercialization-graph.md` · 2026-11-23T19:22:41.110751+00:00
- ✅ `outputs/technology-ownership.md` · 2026-11-23T18:35:04.145741+00:00
- ✅ `outputs/uspto-assignment-validation.md` · 2026-11-23T18:42:13.881990+00:00
- ✅ `outputs/institutional-ownership.md` · 2026-11-23T18:50:43.308837+00:00
- ✅ `outputs/management-radar.md` · 2026-11-23T18:17:07.083947+00:00
- ✅ `dashboard/dist/data.json` · 2026-11-23T19:56:43.240277+00:00

## 数据完整性规则

- Raw run files preserve every execution, including retries on the same market date.
- Frozen predictions use ticker + market date as the primary key, so retries cannot rewrite the first prediction.
- An execution day is not counted as a new independent prediction day unless the market as_of date changes.
- Future outcomes are stored separately and never overwrite the original prediction.
