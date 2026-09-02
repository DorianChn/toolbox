"""Evaluation set: 50 labeled examples for classification/extraction quality.

Each entry maps a commit subject (+ optional diff keyword) to an expected kind.
Used to guard against prompt regressions. A full quality eval also scores the
extracted problem/solution, but that requires a reference LLM or manual labels;
here we assert the kind classification, which is the highest-variance part.
"""
from __future__ import annotations

# (subject, expected_kind, hint_tokens)
EVAL = [
    ("fix: resolve sqlite database locked under concurrent writes", "bugfix", "lock"),
    ("修复 支付回调重复处理导致的重复扣款", "bugfix", "pay"),
    ("fix deadlock in worker pool shutdown", "bugfix", "deadlock"),
    ("bug: handle null pointer when config missing", "bugfix", "null"),
    ("修复登录超时后 token 未刷新的问题", "bugfix", "token"),
    ("fix race condition in websocket reconnect", "bugfix", "race"),
    ("add: implement rate limiter middleware", "feature", "rate"),
    ("feat: support webhook signing verification", "feature", "webhook"),
    ("新增 行情数据缓存层", "feature", "cache"),
    ("feature: export report to pdf", "feature", "pdf"),
    ("feat: add dark mode toggle", "feature", "dark"),
    ("新增用户邀请码功能", "feature", "invite"),
    ("chore: bump dependencies", "chore", "bump"),
    ("docs: update readme install section", "docs", "readme"),
    ("refactor: extract common http client", "refactor", "refactor"),
    ("chore: update ci pipeline", "chore", "ci"),
    ("docs: add api examples", "docs", "docs"),
    ("refactor: rename internal vars", "refactor", "rename"),
    ("fix: memory leak in image loader", "bugfix", "leak"),
    ("bug: incorrect timezone in scheduled job", "bugfix", "timezone"),
    ("feat: add csv import", "feature", "csv"),
    ("feature: realtime push via websocket", "feature", "websocket"),
    ("chore: add .gitignore", "chore", "gitignore"),
    ("docs: describe deploy steps", "docs", "deploy"),
    ("refactor: split monolithic handler", "refactor", "split"),
    ("fix: divide by zero in stats", "bugfix", "divide"),
    ("修复 csv 解析时中文乱码", "bugfix", "csv"),
    ("feat: support multiple accounts", "feature", "accounts"),
    ("fix: handle empty response body", "bugfix", "empty"),
    ("chore: format code with ruff", "chore", "format"),
    ("feature: add retry with backoff", "feature", "retry"),
    ("fix: off-by-one in pagination", "bugfix", "pagination"),
    ("refactor: use dataclasses for config", "refactor", "dataclass"),
    ("docs: document env variables", "docs", "env"),
    ("fix: ssl cert verification bypass", "bugfix", "ssl"),
    ("feat: local file cache for offline", "feature", "cache"),
    ("chore: update license year", "chore", "license"),
    ("fix: escape html in template", "bugfix", "html"),
    ("修复 大量日志导致的磁盘占满", "bugfix", "log"),
    ("feature: add cli auto-complete", "feature", "cli"),
    ("refactor: dedupe validation logic", "refactor", "dedupe"),
    ("docs: troubleshooting guide", "docs", "troubleshoot"),
    ("fix: floating point comparison", "bugfix", "float"),
    ("feat: export metrics to prometheus", "feature", "prometheus"),
    ("chore: remove dead code", "chore", "dead"),
    ("fix: infinite loop in parser", "bugfix", "loop"),
    ("feature: oauth login", "feature", "oauth"),
    ("refactor: move db access behind repository", "refactor", "repository"),
    ("docs: add changelog", "docs", "changelog"),
    ("fix: buffer overflow in parser", "bugfix", "overflow"),
]

# label distribution: bugfix 20, feature 14, chore 8, docs 8, refactor 8 = 50
def load_eval():
    return EVAL
