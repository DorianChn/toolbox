"""Embedding + semantic search.

Local-first, with a three-tier strategy:
  1. Ollama embeddings (e.g. bge-m3) if reachable        -> true semantic
  2. sentence-transformers if installed (devcapsule[local])
  3. builtin lexical hasher                                -> always works
"""
from __future__ import annotations

import json
import math
import os
import re
import urllib.request

DEFAULT_LOCAL_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
DEFAULT_OLLAMA_EMBED_MODEL = "bge-m3:latest"


def _tokenize(text: str) -> list[str]:
    text = (text or "").lower()
    # split CJK into individual chars, latin into words
    tokens = re.findall(r"[\u4e00-\u9fff]|[a-z0-9_]+", text)
    return tokens


class BuiltinEmbedder:
    """Dependency-free lexical embedder (hash-bucket, fixed dimensionality).

    Not truly semantic, but deterministic and dimension-stable so cosine works.
    """

    name = "builtin-tfidf"
    DIM = 256

    def __init__(self, corpus: list[str] | None = None):
        self.corpus = list(corpus or [])

    def encode(self, text: str) -> list[float]:
        toks = _tokenize(text)
        vec = [0.0] * self.DIM
        for t in toks:
            vec[hash(t) % self.DIM] += 1.0
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]


class OllamaEmbedder:
    """Embeddings via a local Ollama server's /api/embed endpoint."""

    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        self.model = model
        self.name = f"ollama:{model}"
        self.base_url = base_url.rstrip("/")

    def encode(self, text: str) -> list[float]:
        if not (text or "").strip():
            # Ollama's /api/embed returns an empty list for blank input.
            return []
        payload = json.dumps({"model": self.model, "input": text}).encode("utf-8")
        req = urllib.request.Request(
            self.base_url + "/api/embed", data=payload, method="POST"
        )
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        emb = data.get("embeddings") or [[]]
        return [float(x) for x in (emb[0] if emb else [])]


class Embedder:
    """Wrapper: Ollama -> sentence-transformers -> builtin fallback."""

    def __init__(self, model: str | None = None):
        from .config import get_setting

        self.model_name = model or DEFAULT_LOCAL_MODEL
        self._st = None
        self._ollama = None
        self.name = "builtin-tfidf"

        # 1) try Ollama embeddings
        ollama_base = (
            os.environ.get("DEVCAPSULE_BASE_URL")
            or get_setting("base_url")
            or "http://localhost:11434"
        )
        ollama_model = (
            os.environ.get("DEVCAPSULE_EMBED_MODEL")
            or get_setting("embed_model")
            or DEFAULT_OLLAMA_EMBED_MODEL
        )
        try:
            probe = OllamaEmbedder(ollama_model, ollama_base)
            probe.encode("ok")  # connectivity + model availability probe
            self._ollama = probe
            self.name = probe.name
        except Exception:
            self._ollama = None

        # 2) fall back to sentence-transformers
        if self._ollama is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._st = SentenceTransformer(self.model_name)
                self.name = self.model_name
            except Exception:
                self._st = None

    @property
    def available(self) -> bool:
        return self._ollama is not None or self._st is not None

    def encode(self, text: str) -> list[float]:
        if self._ollama is not None:
            return self._ollama.encode(text)
        if self._st is not None:
            return [float(x) for x in self._st.encode(text, normalize_embeddings=True)]
        return self._builtin_dense(text)

    def _builtin_dense(self, text: str) -> list[float]:
        return BuiltinEmbedder().encode(text)


def cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def capsule_text(row) -> str:
    return " ".join(
        x for x in (row["problem"], row["solution"], row["gotcha"]) if x
    )
