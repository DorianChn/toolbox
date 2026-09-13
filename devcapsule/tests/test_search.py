"""End-to-end search test with the builtin (dependency-free) embedder."""
import pytest

from devcapsule.embed import BuiltinEmbedder, capsule_text, cosine
from devcapsule.search import search
from devcapsule.store import Store


class _DeterministicEmbedder:
    """A lexical embedder independent of optional sentence-transformers."""

    name = "test-lexical"

    def __init__(self):
        self._b = BuiltinEmbedder([])

    def encode(self, text: str) -> list[float]:
        return self._b.encode(text)


@pytest.fixture
def store(tmp_path):
    s = Store(tmp_path / "t.db")
    items = [
        ("bugfix", "sqlite database is locked under concurrent writes", "enable wal mode", "do not retry in tight loop"),
        ("feature", "add csv import parser", "use stdlib csv module", ""),
        ("bugfix", "division by zero in stats", "guard denominator", ""),
    ]
    for kind, p, sol, g in items:
        cid = s.add_commit("repo", f"h{len(str(p))}", p, "2026-01-01")
        s.add_capsule(cid, kind, p, sol, g, 0.9, [], "2026-01-01")
    yield s
    s.close()


def _index_all(store, emb):
    from devcapsule.search import ensure_embeddings
    ensure_embeddings(store, emb)


def test_search_finds_relevant(store):
    emb = _DeterministicEmbedder()
    _index_all(store, emb)
    hits = search(store, emb, "database lock problem", k=2)
    assert hits, "expected at least one hit"
    top = hits[0][1]
    assert "lock" in (top["problem"] or "").lower() or "sqlite" in (top["problem"] or "").lower()


def test_ensure_embeddings_skips_empty_capsules(tmp_path):
    """Blank problem/solution/gotcha capsules must not be embedded (Ollama
    returns an empty list for blank input, which used to crash with IndexError)."""
    from devcapsule.search import ensure_embeddings

    s = Store(tmp_path / "t.db")
    cid = s.add_commit("repo", "h-empty", "chore: nothing", "2026-01-01")
    s.add_capsule(cid, "chore", "", "", "", 0.9, [], "2026-01-01")
    emb = _DeterministicEmbedder()
    added = ensure_embeddings(s, emb)
    assert added == 0, "empty capsule should be skipped, not embedded"
    assert s.get_embedding(cid) is None
    s.close()

