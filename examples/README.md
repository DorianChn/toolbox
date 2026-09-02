# Examples

A self-contained way to see devcapsule work end-to-end in under a minute.

## 1. `demo.sh` — a fake repo with real bug→fix history

`demo.sh` builds a throwaway git repo in `examples/_demo/` with four
commits that each contain a classic bug followed by its fix. It then:

1. `capsule init` — installs the post-commit hook
2. makes a fifth commit (a new bugfix) so the hook fires live
3. `capsule backfill` — distills the whole history into capsules
4. `capsule search "<query>"` — recalls a fix semantically

Run it:

```bash
bash examples/demo.sh
```

You need `capsule` on your PATH and Ollama running (or any
OpenAI-compatible endpoint configured via `DEVCAPSULE_BASE_URL`).
The demo repo is created fresh each run and left in `examples/_demo/`
for you to inspect (`examples/_demo/` is gitignored).

## 2. What you should see

```text
$ capsule search "division by zero"
[..] 0.xx  bugfix  _demo
     division by zero when the window size is zero
```

The exact scores vary; the point is that the *bugfix* capsule ranks
above the unrelated *feature* capsules, purely from the meaning of your
query — not keyword overlap.

## 3. Try your own repo

The whole point is that this works on *your* history, not a demo:

```bash
cd /path/to/your/repo
capsule init
capsule backfill --all
capsule search "that bug I keep hitting"
```
