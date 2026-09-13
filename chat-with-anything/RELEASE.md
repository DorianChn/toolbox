# 发布文案与渠道准备

> 供明天上午 11 点第一版发布使用。

---

## 一、仓库信息

- **仓库名**：`chat-with-anything`
- **一句话定位**：一行命令，把任意数据源变成能提问的 AI 助手
- **标签**：`python` `rag` `llm` `cli` `llamaindex` `ai`
- **License**：MIT

---

## 二、标题（各渠道）

### GitHub 仓库描述
```
把任意数据源变成可对话的 AI 助手 —— 一条命令跑通 RAG，零配置
```

### Hacker News
```
Show HN: Chat with anything — one command turns any URL/PDF/repo into a RAG chatbot
```

### V2EX / 掘金 / 少数派
```
我把 RAG 做成了一条命令：cwa ask <任意链接>，零配置开聊
```

---

## 三、首发文案（正文）

```
想给某个网页、PDF 或 GitHub 仓库配个"能提问的 AI"，之前要干的事太多了：
读 LangChain 文档、配 API key、装向量库、调切分参数、写胶水代码……

于是我做了一个东西：chat-with-anything。

一条命令：
    cwa ask https://example.com/article

它会自动：
1. 加载数据源（网页 / PDF / 文档 / 目录 / GitHub 仓库）
2. 切分 + 向量化 + 建索引
3. 进入交互式对话，回答还带引用来源

几个特点：
- 零配置：默认本地 embedding，可离线跑，无需联网注册
- 没配 API key？自动降级到本地 Ollama
- 中文优先：默认 bge-small-zh 中文 embedding
- 索引持久化：建一次，秒开提问

代码开源（MIT），欢迎 star 和提 issue。
GitHub: https://github.com/DorianChn/chat-with-anything
```

---

## 四、demo GIF 脚本（可录制后替换占位图）

1. 终端输入 `cwa ask https://paulgraham.com/avg.html`
2. 展示"已加载 N 个文档片段"进度
3. 展示"索引构建完成"
4. 输入问题 "这篇文章的核心观点是什么？"
5. 展示带引用来源的回答
6. 输入 `:q` 退出

---

## 五、发布前检查清单

- [ ] `cwa --help` 可运行
- [ ] `cwa ask <真实 URL>` 端到端跑通
- [ ] README 前三屏：一句话 + demo + 快速上手
- [ ] 仓库已初始化并推送到 GitHub 公开仓库
- [ ] 打上 topics 标签
- [ ] 各渠道发布链接回填到仓库 README（可选）
