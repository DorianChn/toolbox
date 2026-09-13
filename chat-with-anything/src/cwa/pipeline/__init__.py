"""RAG 流水线编排：切分 → 向量化 → 建索引。"""

from __future__ import annotations

from typing import List, Optional

from llama_index.core import Document, Settings, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.storage.storage_context import StorageContext

from ..config import Config
from ..store import build_store


def _configure_embeddings(cfg: Config) -> None:
    """配置 embedding：默认 HuggingFace 本地模型；也支持 Ollama（embed_model 设为 `ollama:<模型名>`）。

    `ollama:` 前缀可完全离线（配合本机 Ollama 的 embedding 模型，如 bge-m3），
    无需从 HuggingFace 下载模型。
    """
    if cfg.embed_model.startswith("ollama:"):
        from llama_index.embeddings.ollama import OllamaEmbedding

        Settings.embed_model = OllamaEmbedding(
            model_name=cfg.embed_model.split(":", 1)[1]
        )
        return

    try:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding

        Settings.embed_model = HuggingFaceEmbedding(model_name=cfg.embed_model)
    except Exception:
        # 本地模型下载失败时，不在此处崩溃，交由上层提示
        raise


def build_index(
    documents: List[Document],
    cfg: Config,
    index_id: Optional[str] = None,
) -> str:
    """把文档列表构建成向量索引并持久化，返回 index_id。"""
    if not documents:
        raise ValueError("没有加载到任何文档内容")

    _configure_embeddings(cfg)

    Settings.chunk_size = 512
    Settings.chunk_overlap = 64
    Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=64)

    vector_store = build_store(cfg, index_id)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )

    return index_id or vector_store.collection_name
