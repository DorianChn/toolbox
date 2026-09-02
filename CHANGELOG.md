# Changelog

All notable changes to devcapsule are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-09-02

First public release. MVP complete; all core features exercised against
real LLM and real git history.

### Added

- **Capture pipeline** (`capture.py`, `hook.py`): git post-commit hook
  feeds commit subject + diff to a local LLM for classification
  (bugfix / feature / refactor / chore / docs) and capsule extraction.
- **SQLite storage** (`store.py`): 4 tables — commits, capsules,
  embeddings, settings. Append-only commit log keyed by `(repo, hash)`.
- **LLM interface** (`llm.py`): Ollama by default
  (`http://localhost:11434`), any OpenAI-compatible endpoint via env vars.
  Splits **classify** and **extract** models — small model for the cheap
  label task, larger model for the lesson (problem / solution / gotcha).
- **Embedding & search** (`embed.py`, `search.py`): three-tier strategy —
  Ollama embeddings (`bge-m3:latest`) → `sentence-transformers` →
  built-in lexical fallback (256-dim hash). Cosine over capsule text
  (problem + solution + gotcha).
- **Commands** (`cli.py`):
  `init`, `uninit`, `doctor`, `capture`, `backfill`, `list`, `show`,
  `search`, `forget`, `export`, `config (list/get/set/unset)`, `eval`.
- **Config** (`config.py`): persistent settings in `settings.json`;
  env vars override per invocation. `capsule config set` writes,
  `get_setting()` reads with env > settings > default precedence.
- **Eval set** (`eval_set.py`, `eval_runner.py`): 50 labeled examples
  for commit classification, exposed as `capsule eval [--limit N]`
  with per-example progress and a miss report.
- **Tests**: 17 tests, all green, including a regression test that
  empty-text capsules are skipped (would otherwise IndexError on
  Ollama's empty-embeddings response) and 4 hook idempotency tests.
- **Demo assets**: PIL-rendered terminal GIF (`demo-gif/demo.gif`,
  998 frames, 68 KB) showing init → backfill → show → search.
- **Examples** (`examples/`): a `demo.sh` that builds a throwaway repo
  with real bug→fix history and runs the full pipeline in ~60s, plus a
  guide (`examples/README.md`). Verified end-to-end on Windows Git Bash
  (cross-language semantic recall confirmed).
- **CI** (`.github/workflows/test.yml`): test matrix (3.10/3.12/3.13)
  plus a smoke job that builds the wheel, installs it, and runs
  `capsule --version/--help/config list`.

### Fixed

- `OllamaEmbedder` silently fell back when the configured model name
  (`bge-m3`) did not match the actual Ollama tag (`bge-m3:latest`).
  Default corrected.
- `ensure_embeddings` crashed with `IndexError` for chore/docs
  capsules whose problem/solution/gotcha were all blank. Now skips
  empty-text rows; embedder returns `[]` for blank input.
- `backfill` buffered all results and only printed at the end, so users
  had no progress feedback for slow 9b extractions. Now yields per
  commit with `flush=True`.
- `hook.install` was not idempotent: re-running `capsule init` would
  clobber an existing post-commit hook (including a user's own
  additions) instead of skipping. Now detects the devcapsule marker and
  leaves existing content untouched.
- `export --week` hardcoded the repo name "devcapsule" in its heading;
  now derives the label from the actual captured repos.
- README's documented `capsule config` command was unimplemented; now
  has 4 subcommands and persists to `settings.json`.

### Notes

- Verified on real LLM (`qwen3:0.6b` classify / `qwen3.5:9b` extract)
  and real git history (`traceplay` v0.1.0, 9 commits, 10 capsules).
- Cross-language semantic search confirmed: Chinese query
  "如何处理 HTTP 状态码" → English capsule about HTTP status codes
  (cosine 0.55 vs 0.52 for the runner-up).
- `qwen3:0.6b` classify accuracy on the 50-example eval set: ~94-96% (one
  flaky LLM call can drop a run to 47/50).
