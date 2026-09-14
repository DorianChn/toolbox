"""Search: index capsule embeddings and rank by similarity."""
from __future__ import annotations

from .embed import Embedder, _tokenize, capsule_text, cosine
from .store import Store


def ensure_embeddings(store: Store, embedder: Embedder) -> int:
    """Embed any capsules missing a vector for the current model. Returns count added."""
    added = 0
    for row in store.all_capsules_for_embedding():
        existing = store.get_embedding(row["id"])
        if existing and existing["model"] == embedder.name:
            continue
        text = capsule_text(row)
        if not text.strip():
            continue  # chore/docs capsules with no lesson have nothing to search
        vec = embedder.encode(text)
        store.set_embedding(row["id"], embedder.name, vec)
        added += 1
    return added


def search(store: Store, embedder: Embedder, query: str, k: int = 5):
    qvec = embedder.encode(query)
    query_terms = set(_tokenize(query))
    results = []
    for row in store.all_embeddings():
        if row["model"] != embedder.name:
            continue
        vec = _parse_vec(row["vec"])
        score = cosine(qvec, vec)
        cap = store.get_capsule(row["capsule_id"])
        if cap is None:
            continue
        cap_terms = set(_tokenize(capsule_text(cap)))
        overlap = len(query_terms & cap_terms) / len(query_terms) if query_terms else 0.0
        # Embeddings can collide in the dependency-free fallback. A small
        # lexical signal keeps exact user terms as a deterministic tie-breaker.
        score += 0.5 * overlap
        results.append((score, cap))
    results.sort(key=lambda x: x[0], reverse=True)
    return results[:k]


def _parse_vec(s: str) -> list[float]:
    import json

    try:
        return [float(x) for x in json.loads(s)]
    except Exception:
        return []
