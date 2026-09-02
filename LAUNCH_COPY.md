# devcapsule — 首发文案包（Launch Kit）

发布平台顺序建议：**Show HN → Reddit (r/ClaudeAI, r/selfhosted, r/cursor) → 中文社区（掘金/V2EX）**，间隔 2–3 天，每处帖按社区调性改写，别复制粘贴。

---

## 1. Show HN

**标题候选**
- `Show HN: devcapsule – turn every fixed bug into a searchable answer`
- `Show HN: I built a local-first "memory" for bugs you've already fixed`
- `Show HN: devcapsule – git hook that writes a searchable "how I fixed it" library`

**正文草稿**

> I got tired of fixing the same class of bug three times — and re-deriving the fix from scratch every time. Nobody writes docs while shipping, so experience just evaporates.
>
> devcapsule is a local-first CLI that watches your git workflow. A post-commit hook feeds each diff to a local LLM (Ollama by default, any OpenAI-compatible API works), classifies what just happened (bugfix/feature/refactor/chore), and — only for the meaningful ones — extracts a structured capsule:
>
> **问题 problem · 方案 solution · 踩坑 gotcha**
>
> Later you just describe the symptom in your own words and it recalls past solutions with semantic search, across all your repos:
>
> `capsule search "sqlite deadlock again"` → ranked past fixes with commit refs.
>
> Data lives in SQLite + local vectors on your machine. No cloud, no telemetry. One command exports a weekly recap or a blog draft.
>
> I checked the "AI devlog" wave from this year (commit-story, devlog-cli…): they all write narrative diary entries. None of them build the **retrieval** layer — a searchable library of lessons, not a diary. That's the gap I'm targeting.
>
> Two design decisions worth flagging:
>
> 1. **Classify and extract use different models.** A small model (`qwen3:0.6b`, cold-starts in ~1s) classifies the commit; a larger one (`qwen3.5:9b`) extracts the lesson. Small models only repeat the commit subject; large ones surface the actual pitfall. You can pick the same model for both, but splitting them is the difference between "diary entry" and "searchable answer."
>
> 2. **Cross-language semantic recall works.** `bge-m3` embeddings are multilingual — Chinese queries find English capsules (and vice versa) without you doing anything special.
>
> Honest status: ~10 weeks in. The full pipeline runs end-to-end on my own repos: capture + backfill + semantic search + export. The 50-example eval set classifies at ~94-96% with `qwen3:0.6b` (run it yourself: `capsule eval`).
>
> Install: `pip install devcapsule && capsule init`
> Repo: github.com/DorianChn/devcapsule (MIT)
>
> Questions I'd love your take on:
> 1. Would you actually review/edit auto-generated capsules, or does "garbage in garbage out" kill it for you?
> 2. Local LLM classification quality — acceptable, or is API accuracy worth the privacy trade-off?

---

## 2. Reddit（分帖改写，勿群发同一文本）

### r/ClaudeAI 或 r/cursor
标题：`I built a git hook that turns fixed bugs into a searchable personal library (local-first)`
正文要点：痛点开场 → 与"AI devlog"的差异（叙事 vs 检索）→ demo 命令截图链接 → 请求反馈。强调与 Cursor/Claude Code 会话互补（v0.4 计划接会话事件）。

### r/selfhosted
标题：`devcapsule – local-first alternative to "AI devlog" tools: your bugs, searchable, no cloud`
正文强调：零外联（除用户配置的 LLM 端点）、SQLite、Ollama 默认、无遥测、MIT。这类用户最吃"数据在你手里"。

### r/programming（可选，风险高）
只在有 demo GIF 后再发，标题：`Show HN-ish: I made my bugs searchable — `capsule search "…"``。此社区对"又一个 AI git 工具"最挑剔，务必自带 criticism FAQ（见下节）。

### 评论区预答批评（先写好备用）
- "这不就是 git log 总结工具吗？" → 差异三点：只抽 bugfix/feature 事件、结构化 问题/方案/踩坑、语义召回。叙事日记你翻不到"上次怎么修的"。
- "LLM 抽卡有噪音怎么办？" → confidence 阈值 + 人工编辑 + forget；评测集在 repo 里可复现。
- "我自己写文档不就行了" → 对，但 90% 的人不写。工具要的是把成本压到接近零。
- "隐私？" → 默认全本地，只有你配置的 LLM/embedding 端点会收到 diff（截断 ≤4k），无遥测。

---

## 3. 中文社区（掘金 / V2EX）

### 掘金正文骨架
标题：《我把修过的每个 bug 变成了能搜到的答案：devcapsule（本地优先，开源）》
- 开场故事：同一个 bug 修三次、每次重新推导 —— 痛点共鸣
- 一句话定位：`git log × 可搜索的个人知识库`，自动生成"问题-方案-踩坑"卡片
- 和"AI devlog"工具的区别表（叙事日记 vs 检索库）
- 演示：`capsule search "sqlite 死锁"` 输出截图
- 技术栈：Python CLI + post-commit hook + Ollama 默认 + SQLite + 本地向量
- 隐私说明 + 开源 MIT + 求反馈
- 结尾抛问题：你们会 review AI 生成的笔记吗？本地小模型抽卡质量够用吗？

### V2EX
标题：《做了个把修过的 bug 自动变成可检索经验库的 CLI，求拍砖》
正文更短、更"求骂"风格：直接贴三条最可能被喷的点请 V2EX 用户锤（质量噪音 / 又是 AI 工具 / 值不值得装 hook）。

---

## 4. 前置资产清单（发布前必须齐）
- [x] demo GIF（`demo-gif/demo.gif`，998 帧，4 幕：init → backfill → show → search）
- [x] README 终稿（含 comparison 表 + anti-goals + 真实 traceplay 案例）
- [x] pip 包可装：`pip install devcapsule`，`capsule doctor` 输出 LLM reachable + store ok
- [x] 评测集 + 94-96% 准确率（可重跑 `capsule eval` 复现）
- [x] 真实案例：`traceplay` v0.1.0 的 9 个 commit → 10 张胶囊，已写进 README "Real-world usage"

## 5. 48 小时探针（可选，若想先试水再决定投入）
在 Phase 0–1 完成后（约第 3 周），先发一个轻量 Show HN：
"500-line post-commit hook that writes a structured fix-library — should this be a real project?"
标题里不带产品名，纯验证需求反应；48h 后看评论/star 再决定是否全力投入。此路径风险最低，若反响差，沉没成本≈3 周。
