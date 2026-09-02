import pytest

from devcapsule.embed import capsule_text, cosine


def test_cosine_identical():
    assert cosine([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)


def test_cosine_orthogonal():
    assert cosine([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)


def test_cosine_empty():
    assert cosine([], [1.0]) == 0.0


def test_capsule_text_joins():
    row = {"problem": "p", "solution": "s", "gotcha": "g"}
    assert capsule_text(row) == "p s g"


def test_builtin_embedder_isolated():
    # exercise BuiltinEmbedder directly; it must always work, no network/model
    from devcapsule.embed import BuiltinEmbedder

    emb = BuiltinEmbedder()
    v = emb.encode("sqlite database is locked")
    assert isinstance(v, list) and len(v) == BuiltinEmbedder.DIM
    assert any(x > 0 for x in v)  # non-trivial vector


def test_embedder_fallback_without_ollama(monkeypatch):
    # force no ollama + no sentence-transformers -> builtin fallback
    monkeypatch.setenv("DEVCAPSULE_BASE_URL", "http://127.0.0.1:1")  # unreachable
    monkeypatch.setenv("DEVCAPSULE_EMBED_MODEL", "nonexistent")
    import devcapsule.embed as e

    monkeypatch.setattr(e, "OllamaEmbedder", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("disabled")))
    from devcapsule.embed import Embedder

    emb = Embedder()
    v = emb.encode("some text")
    assert isinstance(v, list) and len(v) > 0
