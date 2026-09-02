#!/usr/bin/env bash
# devcapsule demo: build a throwaway repo with real bug->fix history,
# then run the full pipeline (init -> hook -> backfill -> search).
# Cross-platform: works under Git Bash on Windows and POSIX sh elsewhere.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
DEMO="$HERE/_demo"

echo "== devcapsule demo =="
echo

# 1. fresh demo repo
rm -rf "$DEMO"
mkdir -p "$DEMO"
cd "$DEMO"
git init -q
git config user.email "demo@devcapsule.local"
git config user.name "devcapsule demo"

# 2. a small project with a couple of classic bugs, each fixed in the next commit
cat > app.py <<'PY'
def average(values):
    return sum(values) / len(values)
PY
git add app.py
git commit -q -m "feat: add average() helper"

cat > app.py <<'PY'
def average(values):
    if not values:
        return 0.0
    return sum(values) / len(values)
PY
git add app.py
git commit -q -m "fix: division by zero when average([]) is called"

cat > db.py <<'PY'
import sqlite3


def connect():
    return sqlite3.connect("app.db")
PY
git add db.py
git commit -q -m "feat: add sqlite helper"

cat > db.py <<'PY'
import sqlite3


def connect():
    conn = sqlite3.connect("app.db")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn
PY
git add db.py
git commit -q -m "fix: enable WAL mode to avoid 'database is locked' under concurrency"

echo "built a demo repo with 4 commits (2 bugfixes)"
echo

# 3. install the hook (so future commits auto-capture)
if command -v capsule >/dev/null 2>&1; then
  capsule init
  echo
else
  echo "capsule not on PATH — install it first: pip install devcapsule"
  exit 1
fi

# 4. a live commit so the hook fires
cat > util.py <<'PY'
def parse_port(raw):
    return int(raw)
PY
git add util.py
git commit -q -m "feat: add parse_port()"

cat > util.py <<'PY'
def parse_port(raw):
    port = int(raw)
    if not (1 <= port <= 65535):
        raise ValueError("port out of range")
    return port
PY
git add util.py
git commit -q -m "fix: validate port range before binding"

echo "committed a new bugfix (hook should have captured it live)"
echo

# 5. backfill history + search
capsule backfill --all
echo
capsule search "division by zero" -k 2
echo
capsule search "数据库被锁" -k 2 2>/dev/null || capsule search "database locked" -k 2

echo
echo "== done. inspect the repo at: $DEMO =="
