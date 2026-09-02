"""SQLite storage layer.

Tables:
  commits     (id, repo, hash, subject, ts)
  capsules    (id, commit_id, kind, problem, solution, gotcha, confidence, refs, created_at, updated_at)
  embeddings  (capsule_id, model, vec)  -- vec stored as JSON float array
  settings    (key, value)  -- reserved, not yet used
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS commits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo TEXT NOT NULL,
    hash TEXT NOT NULL,
    subject TEXT,
    ts TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_commits_hash ON commits(repo, hash);

CREATE TABLE IF NOT EXISTS capsules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commit_id INTEGER REFERENCES commits(id),
    kind TEXT NOT NULL,
    problem TEXT,
    solution TEXT,
    gotcha TEXT,
    confidence REAL,
    refs TEXT,
    created_at TEXT,
    updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_capsules_kind ON capsules(kind);

CREATE TABLE IF NOT EXISTS embeddings (
    capsule_id INTEGER PRIMARY KEY REFERENCES capsules(id),
    model TEXT NOT NULL,
    vec TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""


class Store:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # ---- commits ----
    def add_commit(self, repo: str, hash_: str, subject: str, ts: str) -> int:
        cur = self.conn.execute(
            "INSERT INTO commits(repo, hash, subject, ts) VALUES(?,?,?,?)",
            (repo, hash_, subject, ts),
        )
        self.conn.commit()
        return cur.lastrowid

    def get_commit_by_hash(self, repo: str, hash_: str):
        return self.conn.execute(
            "SELECT * FROM commits WHERE repo=? AND hash=?", (repo, hash_)
        ).fetchone()

    # ---- capsules ----
    def add_capsule(
        self,
        commit_id: int,
        kind: str,
        problem: str,
        solution: str,
        gotcha: str,
        confidence: float,
        refs: list[str],
        created_at: str,
    ) -> int:
        cur = self.conn.execute(
            "INSERT INTO capsules(commit_id, kind, problem, solution, gotcha, confidence, refs, created_at, updated_at)"
            " VALUES(?,?,?,?,?,?,?,?,?)",
            (
                commit_id,
                kind,
                problem,
                solution,
                gotcha,
                confidence,
                json.dumps(refs or []),
                created_at,
                created_at,
            ),
        )
        self.conn.commit()
        return cur.lastrowid

    def list_capsules(self, repo: str | None = None, limit: int = 50):
        if repo:
            return self.conn.execute(
                "SELECT c.*, cm.repo, cm.hash, cm.subject FROM capsules c"
                " JOIN commits cm ON c.commit_id = cm.id WHERE cm.repo = ?"
                " ORDER BY c.id DESC LIMIT ?",
                (repo, limit),
            ).fetchall()
        return self.conn.execute(
            "SELECT c.*, cm.repo, cm.hash, cm.subject FROM capsules c"
            " JOIN commits cm ON c.commit_id = cm.id ORDER BY c.id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    def get_capsule(self, capsule_id: int):
        return self.conn.execute(
            "SELECT c.*, cm.repo, cm.hash, cm.subject FROM capsules c"
            " JOIN commits cm ON c.commit_id = cm.id WHERE c.id = ?",
            (capsule_id,),
        ).fetchone()

    def update_capsule(self, capsule_id: int, **fields) -> None:
        allowed = {"problem", "solution", "gotcha", "kind", "confidence"}
        sets = []
        vals = []
        for k, v in fields.items():
            if k in allowed:
                sets.append(f"{k}=?")
                vals.append(v)
        if not sets:
            return
        from datetime import datetime, timezone

        sets.append("updated_at=?")
        vals.append(datetime.now(timezone.utc).isoformat())
        vals.append(capsule_id)
        self.conn.execute(
            f"UPDATE capsules SET {', '.join(sets)} WHERE id=?", vals
        )
        self.conn.commit()

    def delete_capsule(self, capsule_id: int) -> None:
        self.conn.execute("DELETE FROM embeddings WHERE capsule_id=?", (capsule_id,))
        self.conn.execute("DELETE FROM capsules WHERE id=?", (capsule_id,))
        self.conn.commit()

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM capsules").fetchone()[0]

    def all_capsules_for_embedding(self):
        """Capsules that may need embeddings (joined with commit meta)."""
        return self.conn.execute(
            "SELECT c.id, c.problem, c.solution, c.gotcha, cm.repo FROM capsules c"
            " JOIN commits cm ON c.commit_id = cm.id ORDER BY c.id"
        ).fetchall()

    # ---- embeddings ----
    def get_embedding(self, capsule_id: int):
        return self.conn.execute(
            "SELECT * FROM embeddings WHERE capsule_id=?", (capsule_id,)
        ).fetchone()

    def set_embedding(self, capsule_id: int, model: str, vec: list[float]) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO embeddings(capsule_id, model, vec) VALUES(?,?,?)",
            (capsule_id, model, json.dumps(vec)),
        )
        self.conn.commit()

    def all_embeddings(self):
        return self.conn.execute(
            "SELECT capsule_id, model, vec FROM embeddings"
        ).fetchall()
