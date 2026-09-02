"""Capture pipeline: turn a commit into a stored capsule."""
from __future__ import annotations

import subprocess
from datetime import datetime

from .llm import LLM, LLMError, is_capture_kind
from .store import Store


def repo_name(cwd: str) -> str:
    """A stable short repo identifier (basename of the git root)."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=cwd, capture_output=True, text=True, timeout=10,
        )
        root = out.stdout.strip()
        if root:
            return root.replace("\\", "/").rstrip("/").split("/")[-1]
    except Exception:
        pass
    return "unknown"


def latest_commit(cwd: str):
    """Return (hash, subject) of HEAD."""
    out = subprocess.run(
        ["git", "log", "-1", "--format=%H%x09%s"],
        cwd=cwd, capture_output=True, text=True, timeout=10,
    )
    line = out.stdout.strip()
    if not line:
        return None, None
    h, _, subject = line.partition("\t")
    return h, subject


def commit_diff(cwd: str, hash_: str | None = None, max_chars: int = 4000) -> str:
    target = hash_ or "HEAD"
    out = subprocess.run(
        ["git", "show", "--stat", "--format=", target],
        cwd=cwd, capture_output=True, text=True, timeout=15,
    )
    diff = out.stdout.strip()
    if not diff:
        out2 = subprocess.run(
            ["git", "show", "--format=", "-U3", target],
            cwd=cwd, capture_output=True, text=True, timeout=15,
        )
        diff = out2.stdout
    return diff[:max_chars]


def recent_commits(cwd: str, limit: int = 50):
    """Return list of (hash, subject) from newest to oldest."""
    out = subprocess.run(
        ["git", "log", f"-{limit}", "--format=%H%x09%s"],
        cwd=cwd, capture_output=True, text=True, timeout=10,
    )
    items = []
    for line in out.stdout.strip().splitlines():
        if not line:
            continue
        h, _, subject = line.partition("\t")
        items.append((h, subject))
    return items


def _analyze_one(cwd, repo, hash_, subject, store, llm, capture_all, now):
    if store.get_commit_by_hash(repo, hash_):
        return "already-seen"
    try:
        diff = commit_diff(cwd, hash_)
        data = llm.analyze_commit(subject or "", diff)
    except LLMError as e:
        return f"llm-error: {e}"

    kind = data["kind"]
    commit_id = store.add_commit(repo, hash_, subject or "", now)

    if is_capture_kind(kind) or capture_all:
        store.add_capsule(
            commit_id=commit_id,
            kind=kind,
            problem=data.get("problem", ""),
            solution=data.get("solution", ""),
            gotcha=data.get("gotcha", ""),
            confidence=data.get("confidence", 0.0),
            refs=[hash_[:8]],
            created_at=now,
        )
        return f"captured:{kind}"
    return f"skipped:{kind}"


def capture_current(cwd: str, store: Store, llm: LLM, capture_all: bool = False):
    """Analyze HEAD and store a capsule if it's a capture kind.

    Returns a status string for logging.
    """
    repo = repo_name(cwd)
    hash_, subject = latest_commit(cwd)
    if not hash_:
        return "no-commit"
    now = datetime.utcnow().isoformat()
    return _analyze_one(cwd, repo, hash_, subject, store, llm, capture_all, now)


def backfill(cwd: str, store: Store, llm: LLM, limit: int = 50, capture_all: bool = False):
    """Backfill all uncaptured commits in the last `limit`, newest first.

    Yields (hash, status) tuples as they are processed, so callers can stream
    progress instead of waiting for the whole batch.
    """
    repo = repo_name(cwd)
    for hash_, subject in recent_commits(cwd, limit):
        now = datetime.utcnow().isoformat()
        status = _analyze_one(cwd, repo, hash_, subject, store, llm, capture_all, now)
        yield hash_, status
