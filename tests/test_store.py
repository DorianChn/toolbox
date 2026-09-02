import json

import pytest

from devcapsule.store import Store


@pytest.fixture
def store(tmp_path):
    s = Store(tmp_path / "test.db")
    yield s
    s.close()


def test_add_and_get_commit(store):
    cid = store.add_commit("repo", "abc123", "fix: bug", "2026-01-01")
    row = store.get_commit_by_hash("repo", "abc123")
    assert row is not None
    assert row["subject"] == "fix: bug"


def test_add_and_list_capsule(store):
    cid = store.add_commit("repo", "abc", "feat: x", "2026-01-01")
    store.add_capsule(cid, "feature", "p", "s", "g", 0.9, ["abc"], "2026-01-01")
    rows = store.list_capsules()
    assert len(rows) == 1
    assert rows[0]["kind"] == "feature"
    assert rows[0]["problem"] == "p"


def test_update_capsule(store):
    cid = store.add_commit("r", "h", "fix", "2026-01-01")
    pid = store.add_capsule(cid, "bugfix", "p", "s", "", 0.5, [], "2026-01-01")
    store.update_capsule(pid, problem="fixed", solution="new")
    row = store.get_capsule(pid)
    assert row["problem"] == "fixed"
    assert row["solution"] == "new"


def test_delete_capsule(store):
    cid = store.add_commit("r", "h", "fix", "2026-01-01")
    pid = store.add_capsule(cid, "bugfix", "p", "s", "", 0.5, [], "2026-01-01")
    store.delete_capsule(pid)
    assert store.count() == 0


def test_embedding_roundtrip(store):
    cid = store.add_commit("r", "h", "fix", "2026-01-01")
    pid = store.add_capsule(cid, "bugfix", "p", "s", "", 0.5, [], "2026-01-01")
    store.set_embedding(pid, "model", [0.1, 0.2, 0.3])
    emb = store.get_embedding(pid)
    assert emb["model"] == "model"
    vec = json.loads(emb["vec"])
    assert vec == [0.1, 0.2, 0.3]
