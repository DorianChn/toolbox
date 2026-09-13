# chat-with-anything

> 一行命令，把任意数据源变成能提问的 AI 助手。
> 网页、PDF、文档、目录、GitHub 仓库，通吃。

```bash
pip install chat-with-anything
cwa ask https://example.com/article   # 立即开始提问
```

---

## 为什么需要它？

想"喂一个文档/网页给 AI 提问"，通常要面对：读半天 LangChain 文档、配 API key、装向量库、调切分参数、写一堆胶水代码。

**cwa 把这些全部藏起来，你只需要一条命令。**

```
数据源 ──加载──▶ 切分 ──▶ 向量化 ──▶ 建索引 ──▶ 交互式问答
                    ↑ 全自动，零配置
```

---

## 快速上手

### 1. 安装

```bash
pip install chat-with-anything
```

### 2. 一条命令开始对话

```bash
# 网页
cwa ask https://example.com/article

# PDF
cwa ask ./report.pdf

# 本地文档目录
cwa ask ./docs/

# GitHub 仓库
cwa ask https://github.com/owner/repo
```

首次运行会自动下载本地 embedding 模型（无需联网注册），之后构建索引并进入交互式对话。

### 3. 配置 LLM（可选，不配也能用本地 Ollama）

```bash
# 使用 OpenAI 兼容接口（OpenAI / DeepSeek / 通义 / 本地 Ollama 均可）
cwa config base_url https://api.deepseek.com/v1
cwa config api_key sk-xxxx
cwa config model deepseek-chat
```

**没配 API key？** 会自动降级到本地 Ollama（需已安装并启动 `ollama serve`）。

### 4. 完全离线跑通（可选）

本机已装 Ollama、且已有 embedding 模型时，可把 embedding 也切到本地，全程不联网（无需下载 HuggingFace 模型）：

```bash
cwa config embed_model ollama:bge-m3     # 用 Ollama 的 embedding 模型
cwa config ollama_model qwen3:0.6b       # 指定本机已有的 LLM 模型
```

> 提示：默认 embedding 模型 `bge-small-zh-v1.5` 首次运行会从 HuggingFace 下载；
> 网络受限环境可设镜像 `HF_ENDPOINT=https://hf-mirror.com`，或用上面的 `ollama:` 方案完全离线。

---

## 命令一览

| 命令 | 说明 |
|---|---|
| `cwa ask <数据源>` | 一条命令：建索引 + 进入对话 |
| `cwa index <数据源>` | 只建索引，输出 index_id |
| `cwa chat <index_id>` | 对已有索引提问 |
| `cwa list` | 列出所有索引 |
| `cwa config <key> <value>` | 配置模型/密钥 |
| `cwa show-config` | 查看当前配置（密钥脱敏） |

---

## 特性

- **零配置**：默认本地 embedding，可离线；未配 key 自动降级 Ollama
- **任意数据源**：网页 / PDF / txt / md / 目录 / GitHub 仓库
- **中文优先**：默认中文 embedding 模型 `bge-small-zh-v1.5`
- **带引用**：回答附带来源和相关度
- **索引持久化**：建一次索引，随时秒开提问

---

## 架构

```
cwa (CLI)
 ├── loaders/    数据源加载（url / pdf / file / dir / github）
 ├── pipeline/   切分 → 向量化 → 建索引
 ├── store/      向量库（Chroma，预留扩展）
 ├── llm/        LLM 客户端（OpenAI 兼容 / Ollama 降级）
 ├── chat/       交互式问答（REPL + 引用来源）
 └── config/     零配置默认值 + 持久化
```

基于 [LlamaIndex](https://github.com/run-llama/llama_index) 生态构建，感谢社区。

---

## 开发

```bash
git clone https://github.com/DorianChn/chat-with-anything.git
cd chat-with-anything
pip install -e ".[dev]"
cwa --help
```

## License

MIT
