# svcboard

[![CI](https://github.com/DorianChn/toolbox/actions/workflows/svcboard.yml/badge.svg)](https://github.com/DorianChn/toolbox/actions/workflows/svcboard.yml)

> A local-first service board for your dev machine. See every port your computer is listening on — and which process owns it — in one glance.

`svcboard` scans all listening TCP ports on your machine and shows the owning process, its command line, and a known-service hint. Output as a clean table, Markdown (drop it into a README), or JSON (pipe it anywhere).

## Why

- **Local-first, zero servers.** Everything runs on your machine; nothing leaves it.
- **Cross-platform.** Windows / Linux / macOS via `psutil`.
- **Actually useful when you run many local services** (APIs, dev proxies, model servers…) and keep losing track of "what's on :8100 again?".

## Install

```bash
pip install svcboard
```

Requires Python 3.9+.

## Usage

```bash
# pretty table (default)
svcboard

# Markdown — paste into a status doc / README
svcboard --md

# machine-readable
svcboard --json

# one port only
svcboard --port 8100

# faster: skip process lookup
svcboard --no-process
```

### Example (Markdown)

| Port | Proto | Host | PID | Process | Service | Command |
|-----:|-------|------|----:|---------|---------|---------|
| 8100 | tcp | 127.0.0.1 | 12345 | python.exe | - | `D:\tools\deepseek-web-api\app.py` |
| 8787 | tcp | 0.0.0.0 | 12346 | python.exe | - | `D:\tools\workbench\server.py` |
| 11434 | tcp | 127.0.0.1 | 12347 | ollama.exe | - | `ollama serve` |

## How it works

`psutil.net_connections(kind="tcp")` → filter `LISTEN` → resolve each `pid` to process name + command line. That's it. No `netstat` parsing, no admin-shell gymnastics.

## License

MIT © 山川志
