"""配置管理：零配置默认值 + 可选覆盖，持久化到 ~/.cwa/config.json。"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


def _config_dir() -> Path:
    return Path.home() / ".cwa"


def _config_path() -> Path:
    return _config_dir() / "config.json"


@dataclass
class Config:
    # LLM 接入（OpenAI 兼容接口）
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini"
    # embedding 模型（默认本地，可离线）
    embed_model: str = "BAAI/bge-small-zh-v1.5"
    # 向量库
    vector_store: str = "chroma"
    # 本地 Ollama 降级
    ollama_model: str = "llama3.1"
    # 索引持久化目录
    data_dir: str = field(default_factory=lambda: str(_config_dir() / "indexes"))

    @property
    def configured(self) -> bool:
        return bool(self.api_key.strip())


def load() -> Config:
    path = _config_path()
    if not path.exists():
        return Config()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        known = {k: v for k, v in raw.items() if k in Config.__dataclass_fields__}
        return Config(**known)
    except (json.JSONDecodeError, TypeError):
        return Config()


def save(cfg: Config) -> None:
    _config_dir().mkdir(parents=True, exist_ok=True)
    _config_path().write_text(
        json.dumps(asdict(cfg), ensure_ascii=False, indent=2), encoding="utf-8"
    )


def set_value(key: str, value: str) -> Config:
    cfg = load()
    if key not in Config.__dataclass_fields__:
        raise KeyError(f"未知配置项: {key}")
    setattr(cfg, key, value)
    save(cfg)
    return cfg
