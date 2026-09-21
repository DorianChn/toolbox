"""Git hook installation/removal."""
from __future__ import annotations

import subprocess
from pathlib import Path

HOOK_NAME = "post-commit"
HOOK_SCRIPT = """#!/bin/sh
# devcapsule capture (async, non-blocking)
(capsule capture --cwd "$(pwd)" >/dev/null 2>&1 &)
"""


def git_dir(cwd: str) -> Path | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=cwd, capture_output=True, text=True, timeout=10,
        )
        p = out.stdout.strip()
        if not p:
            return None
        return Path(p).resolve()
    except Exception:
        return None


def install(cwd: str) -> Path:
    gd = git_dir(cwd)
    if gd is None:
        raise RuntimeError("not a git repository: " + cwd)
    hook = gd / "hooks" / HOOK_NAME
    hook.parent.mkdir(parents=True, exist_ok=True)
    if hook.exists() and HOOK_SCRIPT in hook.read_text(encoding="utf-8", errors="ignore"):
        # already installed — idempotent, do not clobber other hooks
        hook.chmod(hook.stat().st_mode | 0o111)
        return hook
    if hook.exists():
        # append our snippet to an existing hook rather than clobber it
        with hook.open("a", encoding="utf-8") as f:
            f.write("\n" + HOOK_SCRIPT)
    else:
        hook.write_text(HOOK_SCRIPT, encoding="utf-8")
    hook.chmod(hook.stat().st_mode | 0o111)
    return hook


def uninstall(cwd: str) -> bool:
    gd = git_dir(cwd)
    if gd is None:
        return False
    hook = gd / "hooks" / HOOK_NAME
    if not hook.exists():
        return False

    text = hook.read_text(encoding="utf-8", errors="ignore")
    if HOOK_SCRIPT not in text:
        return False

    if text == HOOK_SCRIPT:
        hook.unlink()
        return True

    remaining = text.replace("\n" + HOOK_SCRIPT, "", 1).replace(HOOK_SCRIPT, "", 1)
    if remaining.strip():
        hook.write_text(remaining, encoding="utf-8")
    else:
        hook.unlink()
    return True
    return False


def is_installed(cwd: str) -> bool:
    gd = git_dir(cwd)
    if gd is None:
        return False
    hook = gd / "hooks" / HOOK_NAME
    return hook.exists() and HOOK_SCRIPT in hook.read_text(encoding="utf-8", errors="ignore")
