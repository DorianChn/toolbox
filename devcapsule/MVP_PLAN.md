# devcapsule — MVP 任务拆解（8 周）

> 目标：8 周内发布一个可上 Show HN 的 v0.1（capture 闭环 + search 可 demo）。
> 约束：单人、Python 3.10+、本地优先（Ollama 默认）、无云服务依赖。
> 每个阶段都带**验收标准**——用命令实测通过才算完成，不凭感觉。

## Phase 0 · 脚手架与存储（第 1 周）
- [ ] `pyproject.toml` + `src/devcapsule/` 包结构，CLI 框架（argparse/typer），`capsule --version`
- [ ] 存储层：`~/.devcapsule/` 下 SQLite schema —— 表 `commits(id, repo, hash, ts)`、`capsules(id, commit_id, kind, problem, solution, gotcha, refs_json, created_at, updated_at)`、`embeddings(capsule_id, model, vec)`、`settings(k,v)`
- [ ] `capsule init`：创建目录 + 在当前 git 仓库安装 post-commit hook（幂等、可 `capsule uninit` 卸载）
- [ ] `capsule doctor`：检查 hook 是否生效、LLM 是否可连、embedding 模型是否可用

**验收**：`capsule init && capsule doctor` 在全新临时 git 仓库跑通，SQLite 三表可查询。

## Phase 1 · 事件捕获 + 分类抽卡（第 2–3 周）—— 核心
- [ ] post-commit hook → 收集 `git show --stat` diff（截断 token，默认 ≤4k 字符，可配）
- [ ] LLM 分类（本地 Ollama，OpenAI 兼容切换）：`bugfix / feature / refactor / chore / docs`；非 bugfix/feature 默认丢弃（可配 `--capture-all`）
- [ ] LLM 抽取结构化 JSON：`{problem, solution, gotcha, confidence}` + JSON schema 强校验（坏输出丢弃并计数，不崩溃）
- [ ] 结果落库；`capsule log` 显示最近捕获流水（hook 异步/后台执行，不阻塞 git commit）
- [ ] **评测集 v1**：50 个真实 commit（自己历史 + 开源仓库），人工标注是否该抽卡、卡内容是否准确 —— 后续每次改 prompt 跑一遍，保证召回不退化

**验收**：连续 10 个真实 commit 后 `capsule list` 出现 ≥6 张卡；hook 失败不影响 commit；坏 JSON 率 <10%（记入 `capsule stats`）。

## Phase 2 · 语义检索（第 4 周）
- [ ] embedding：默认本地（sentence-transformers 小模型，如 `paraphrase-multilingual-MiniLM` 或 `bge-small-zh`），可选 API（OpenAI-compatible）
- [ ] `capsule search "<描述>"`：向量召回 top-k（k=5），显示问题/方案摘要 + repo/日期
- [ ] 检索评测：20 条查询 × 期望命中，排序准确率 ≥70%（MRR 记录在 `capsule stats`）

**验收**：对一个两月前修过的 bug，用口语描述能 10 秒内召回对应卡。

## Phase 3 · 导出与编辑（第 5 周）
- [ ] `capsule show <id>` 交互编辑（改内容、标记 wrong）；`capsule forget <id>` 删除
- [ ] `capsule export --blog` / `--week`：md 导出，模板可自定义
- [ ] 隐私默认项核对：无网络请求（除用户显式配置的 LLM/embedding endpoint）、无遥测

**验收**：`capsule export --blog` 产出一篇可直接贴到博客的 md；全程 `netstat` 无未声明外联。

## Phase 4 · 打磨与发布（第 6–8 周）
- [ ] 多仓库支持：`capsule search --all`（默认跨 ~/.devcapsule 下所有已 init 仓库）
- [ ] ignore 规则（.gitignore 式：`capsule ignore "依赖升级"` / 按文件路径）
- [ ] 测试（pytest：存储、分类 schema 校验、检索排序）+ GitHub Actions CI + pip 包发布（名称已确认空闲）
- [ ] README 终稿 + **demo GIF**（录一个 60 秒 search→命中 的循环）+ 截图
- [ ] 上线前竞争复查（生态 8 周内可能变动）+ 名字/域名二次确认

**验收**：`pip install devcapsule` 从零用户路径 5 分钟内跑通；CI 绿；发布物料齐全。

## 风险与对策
| 风险 | 对策 |
|---|---|
| LLM 分类/抽取质量不稳 | 评测集 v1 先行；prompt 每次改动必跑评测；给 confidence 阈值 |
| hook 拖慢 commit | 默认异步后台跑 + diff 截断 + 失败静默 |
| 召回差（中文口语描述） | 双语言 embedding 模型；检索评测 MRR 记分 |
| 名字被抢 | 已查：npm/PyPI 空闲，GitHub 同名仓库均无关小项目（≤2★） |
| 生态窗口（叙事型 devlog 起量） | 心智差异咬死「检索型」；README/首发文案反复强调 |

## 里程碑（外部可见）
- **W3 末**：`capsule search` 对个人历史 commit 首次 demo（自用即验证）
- **W6 末**：pip 可装，README+截图就绪
- **W8 末**：Show HN + Reddit 首发（文案见 LAUNCH_COPY.md）
