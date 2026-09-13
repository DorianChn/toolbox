"""向量库适配：默认 Chroma，预留扩展。"""

from __future__ import annotations

import uuid
from typing import Optional

from llama_index.core.vector_stores.types import BasePydanticVectorStore

from ..config import Config


def _default_collection() -> str:
    return f"cwa_{uuid.uuid4().hex[:8]}"


def build_store(cfg: Config, index_id: Optional[str] = None) -> BasePydanticVectorStore:
    collection = index_id or _default_collection()

    if cfg.vector_store == "chroma":
        import chromadb

        client = chromadb.PersistentClient(path=cfg.data_dir)
        chroma_collection = client.get_or_create_collection(collection)

        from llama_index.vector_stores.chroma import ChromaVectorStore

        return ChromaVectorStore(chroma_collection=chroma_collection, collection_name=collection)

    raise ValueError(f"不支持的向量库: {cfg.vector_store}")


def load_store(cfg: Config, index_id: str) -> BasePydanticVectorStore:
    """加载已存在的索引。"""
    if cfg.vector_store == "chroma":
        import chromadb

        client = chromadb.PersistentClient(path=cfg.data_dir)
        chroma_collection = client.get_collection(index_id)

        from llama_index.vector_stores.chroma import ChromaVectorStore

        return ChromaVectorStore(chroma_collection=chroma_collection)

    raise ValueError(f"不支持的向量库: {cfg.vector_store}")


def list_indexes(cfg: Config):
    if cfg.vector_store == "chroma":
        import chromadb

        client = chromadb.PersistentClient(path=cfg.data_dir)
        return [c.name for c in client.list_collections()]

    return []
