# 共享记忆：Claude 与 Codex

这份文件是两个代理共用的项目记忆。Codex 从 AGENTS.md 读到它，Claude 从 CLAUDE.md 读到它。
谁做出新的长期决定，就在“决定记录”里加一行，写上日期和是谁定的。不要写入任何邮箱、API key 或 SEC 联系方式。

## 项目
- AI 医疗投资研究代理，给 Peter 用。只做纸面交易：系统只生成下单建议，每一张都要人工批准，不连接券商。
- 网页：英文 dashboard/dist/top5.html，中文 dashboard/dist/top5.zh.html（由 scripts/translate_page.py 生成）。
- 用户希望用中文汇报。

## 硬规则
1. **Serenity 门槛只按原文评分。** 模型只摘录带引文的事实，由代码按 scripts/serenity_evidence_review.py 里 GATES 的规则文字判分。模型不能自己给门槛打 pass。引文必须在原文里核实（prepare_claude_review.locate），且至少 20 个字符。
2. **SEC 联系方式和 USPTO key 只放在命令行环境变量里**（SEC_USER_AGENT=… / USPTO_API_KEY=…），绝不写进文件、缓存或 git。每日脚本没有 SEC_USER_AGENT 就会停下，不会覆盖已有结果。
3. 不处理 ANTHROPIC_API_KEY；不调用需要付费 API key 的服务。
4. 读取下载文件的 Python 要用 `-I` 运行。
5. 只提交、推送用户要求的内容；Claude 的改动和 Codex 的改动分开提交，提交说明写明是谁的改动。
6. 深审队列只收 AI 公司。新药公司（因 IND 或大药厂合作进入的）留在信号页面，不进队列。
7. TradingAgents 默认关闭（RUN_TRADINGAGENTS_FULL_REVIEW=1 才会运行）。
8. 主目录始终留在 serenity-signals-backtest 分支，不要在这里新建分支或切换分支（流水线和 Claude 的提交都在这个目录里进行）。需要独立分支时，另开一个 git worktree，例如 ../x20-wps-people-signals。

## 分工
- **Claude**：运行每日研究（AGENT_MODE=deep，命令行里带 SEC 联系方式），按规则重评门槛，重建并发布网页，提交并推送。
- **Codex**：在 "Serenity Trade" 会话里接活。任务写在 state/codex-task-inbox.md，结果写到 state/codex-task-results.md。
  Codex 的沙盒不能写 .git，所以由 Claude 代它提交，并标明是 Codex 的改动。
- 同一时间只能有一个进程写 state/serenity-claude-citations.json：各重评脚本都是整份读入、整份写回。流水线运行期间，不要再跑另一条流水线。

## 常用命令
- 测试：`PYTHONPATH=scripts python3 -m pytest -q -p no:cacheprovider scripts/tests`
- 重建：prepare_claude_review.py → finalize_codex_serenity.sh state/serenity-claude-response.json → serenity_review_status.py → build_top5_brief.py → order_tickets.py → candidate_filter.py --no-model → data_freshness.py → build_top5_brief.py → translate_page.py
- 门槛重评脚本（模型只摘事实）：claude_customer_review.py、claude_management_review.py --proxy、claude_chain_review.py、claude_control_review.py、claude_counter_review.py

## 决定记录
- 2026-11-25 用户：深审队列只收 AI 公司。
- 2026-11-26 Claude：每日脚本没有 SEC_USER_AGENT 就停止；TradingAgents 默认关闭。
- 2026-11-26 Claude：卡脖子证据和多环节控制改为按规则重评；所有 claude -p 调用改走 scripts/claude_cli.py（超时后整个进程组一起结束）。
- 2026-11-27 用户：Codex 的 serenity-trade 自动任务改成派活通道，不再跑每日脚本、不再打分；Codex 的改动由 Claude 代为提交并标明。
- 2026-11-27 Codex 审查、Claude 修复：market_share 必须挨着 market 或 share；相连的两个环节，引文要相距 400 个字符以内；只有一条点名协议也要保留。
- 2026-11-27 Codex：多环节控制还必须由原文绑定到同一具体产品/平台/工作流，并按两段引文的实际间隔而不是起点距离计算；已终止协议保留作反证，但点名关系召回时排在有效关系之后。
- 2026-11-27 Codex T1 复核、Claude 修复：市场份额只认两种证据，一是带份额语义的百分比，二是明确的排名；独家许可（exclusive license）不算唯一供应；供应链的点名关系补上 depend on / supplied by / purchase from 等写法。
- 2026-11-27 Codex：瓶颈证据必须区分方向；只有市场或客户依赖该公司（company_controls）才能支持门槛，公司依赖单一供应商、许可方、平台或付款方（company_depends）一律作为反证，不能通过瓶颈门槛。
- 2026-11-27 Codex T2、Claude 复核：卡脖子证据区分方向，只有"市场依赖本公司"（company_controls）才能支持门槛，"公司依赖别人"计入反证；多环节控制要求两个相邻环节属于同一产品、来自同一段落，引文间隔 ≤ 400 字符；已终止的协议在选段落时排在仍有效的关系之后。
- 2026-11-27 Claude：Codex 做 T2 时把主目录切到了 codex/t1-followup-hardening，导致 Claude 的提交落到新分支、推送失败；已把原分支快进到同一提交并切回。由此定下硬规则第 8 条。
- 2026-11-27 Claude：全局 git 配置 core.autocrlf=true，会在工作区里把文件改成 CRLF，导致 sh 读不了每日脚本。本仓库已单独设为 core.autocrlf=input。改完 shell 脚本先跑一次 sh -n run-daily-investment-agent.sh。
- 2026-11-27 Claude：把 Codex 的关键人物信号追踪（4e6ff69，people_signal_tracker.py）合并进主分支，提交为 933c06a。它只生成人工复核队列，不改动门槛。
- 2026-11-27 用户：门槛一律按 Serenity 原文判。财报门槛只要有支持论点的标明日期的实际结果就 pass，反向结果记为反证、不拦门槛；去掉导入时"带反证就降级"的全局规则（只有反方门槛的原文提到反证）。
- 2026-11-28 Claude：外国公司（20-F/40-F）不提交季度高管认证，治理门槛以最新年报名单为准。有核实过的年报原文点名 CFO、并有核实过的原文点名 CEO，就算领导层在任，由代码判断；离职或空缺仍由"继任未定"拦住。治理重评改为读取最近 3 份 6-K。
