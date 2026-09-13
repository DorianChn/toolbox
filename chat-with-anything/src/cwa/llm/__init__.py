"""LLM 客户端：OpenAI 兼容接口，支持 Ollama 本地降级。"""

from __future__ import annotations

from llama_index.core.llms import LLM

from ..config import Config


def _list_ollama_models() -> list[str] | None:
    """返回本机 Ollama 已装模型名列表；服务不可用时返回 None。"""
    try:
        import ollama

        return [m.model for m in ollama.Client().list().models]
    except Exception:
        return None


def build_llm(cfg: Config) -> LLM:
    """按配置构建 LLM。未配 key 时降级到本地 Ollama（若可用）。"""
    if cfg.configured:
        from llama_index.llms.openai_like import OpenAILike

        return OpenAILike(
            model=cfg.model,
            api_base=cfg.base_url,
            api_key=cfg.api_key,
            is_chat_model=True,
        )

    # 无 key：降级到本地 Ollama，先友好地检查服务与模型
    models = _list_ollama_models()
    if models is None:
        raise RuntimeError(
            "未配置 API key，且本地 Ollama 服务不可用。\n"
            "请二选一：\n"
            "  1) 运行 `cwa config api_key sk-xxx` 配置密钥\n"
            "  2) 安装并启动本地 Ollama（https://ollama.com）"
        )
    if cfg.ollama_model not in models:
        raise RuntimeError(
            f"本地 Ollama 没有模型 {cfg.ollama_model!r}。\n"
            f"本机已装模型：{', '.join(models)}\n"
            f"请运行 `cwa config ollama_model <模型名>` 指定一个，"
            f"或用 `ollama pull {cfg.ollama_model}` 拉取。"
        )

    from llama_index.llms.ollama import Ollama

    return Ollama(model=cfg.ollama_model, request_timeout=120.0)
