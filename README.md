# 🧰 toolbox

> 小而自包含的开发工具合集 —— 每个工具一个独立目录，各自的提交历史完整保留（git subtree 合并）。

## 目录

| 工具 | 一句话 | 技术 |
|------|--------|------|
| [devkit-cli](devkit-cli/) | 零依赖的开发者瑞士军刀 CLI：哈希、UUID、base64、JSON、密码、时间戳 | Node.js |
| [svcboard](svcboard/) | 本机端口速查板：扫出所有监听端口和占用进程，导出 Markdown/JSON | Python + psutil |
| [chat-with-anything](chat-with-anything/) | 一条命令把网页/PDF/目录/仓库变成可对话的 AI 助手（零配置 RAG） | Python |
| [devcapsule](devcapsule/) | 本地优先的开发经验胶囊库：把修过的 bug 变成可检索的答案 | Python |
| [fullstack-todo](fullstack-todo/) | 干净的全栈任务管理 demo：React + TypeScript + Express + 零依赖 JSON 存储 | TypeScript |
| [python-scaffold](python-scaffold/) | Python 项目脚手架：pyproject + venv 约定 + 入口骨架 | Python |

## 说明

- 这些工具原本是独立仓库，2026-09 合并进本仓库统一维护；原仓库已归档并指向这里。
- 每个子目录就是一个完整可独立运行的项目，按其内部 README 使用即可。
- CI 覆盖 `devkit-cli`、`devcapsule`、`fullstack-todo`、`svcboard`、
  `chat-with-anything` 和 `python-scaffold`（改到对应目录才会触发）；另有 CodeQL 扫描。
