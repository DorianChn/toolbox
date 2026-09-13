"""Command-line interface."""
from __future__ import annotations

import argparse
import sys

from . import __version__
from .config import db_path, ensure_home
from .store import Store


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="capsule",
        description="devcapsule: turn fixed bugs into searchable answers.",
    )
    p.add_argument("--version", action="version", version=f"devcapsule {__version__}")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("init", help="install git hook + init store")
    sub.add_parser("uninit", help="remove the git hook")
    sub.add_parser("doctor", help="check hook + LLM config")

    c = sub.add_parser("capture", help="capture HEAD commit now")
    c.add_argument("--cwd", default=".", help="repository path")
    c.add_argument("--all", action="store_true", help="capture non-bugfix/feature too")

    b = sub.add_parser("backfill", help="capture recent uncaptured commits")
    b.add_argument("--cwd", default=".", help="repository path")
    b.add_argument("--limit", type=int, default=50)
    b.add_argument("--all", action="store_true", help="capture non-bugfix/feature too")

    l = sub.add_parser("list", help="list capsules")
    l.add_argument("--repo", default=None)
    l.add_argument("--limit", type=int, default=30)

    s = sub.add_parser("show", help="show/edit a capsule")
    s.add_argument("id", type=int)

    q = sub.add_parser("search", help="semantic search")
    q.add_argument("query")
    q.add_argument("-k", type=int, default=5)

    f = sub.add_parser("forget", help="delete a capsule")
    f.add_argument("id", type=int)

    e = sub.add_parser("export", help="export markdown")
    e.add_argument("--blog", action="store_true")
    e.add_argument("--week", action="store_true")

    cfg = sub.add_parser("config", help="get/set persistent settings")
    cfg_sub = cfg.add_subparsers(dest="config_cmd")
    cfg_sub.add_parser("list", help="show current effective settings")
    cg = cfg_sub.add_parser("get", help="read one setting")
    cg.add_argument("key")
    cs = cfg_sub.add_parser("set", help="write one setting")
    cs.add_argument("key")
    cs.add_argument("value")
    cu = cfg_sub.add_parser("unset", help="remove one setting")
    cu.add_argument("key")

    ev = sub.add_parser("eval", help="measure classification accuracy on the eval set")
    ev.add_argument("--limit", type=int, default=0, help="max examples (0 = all)")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd is None:
        build_parser().print_help()
        return 0

    store = Store(db_path())

    if args.cmd == "init":
        ensure_home()
        from .hook import install, is_installed
        cwd = "."
        already = is_installed(cwd)  # check BEFORE install so we can report accurately
        install(cwd)
        print(f"✓ store at {db_path()}")
        print("✓ post-commit hook installed" + (" (already)" if already else ""))

    elif args.cmd == "uninit":
        from .hook import uninstall
        print("removed" if uninstall(".") else "no devcapsule hook found")

    elif args.cmd == "doctor":
        from .hook import is_installed
        from .llm import LLM
        print("store        :", db_path(), "(ok)")
        print("git hook     :", "installed" if is_installed(".") else "NOT installed")
        try:
            llm = LLM()
            llm.chat("reply with the single word: ok")
            print("llm          :", "reachable", f"({llm.model})")
        except Exception as e:
            print("llm          :", "UNREACHABLE", f"- {e}")

    elif args.cmd == "capture":
        from .capture import capture_current
        from .llm import LLM
        llm = LLM()
        status = capture_current(args.cwd, store, llm, capture_all=args.all)
        print(status)

    elif args.cmd == "backfill":
        from .capture import backfill
        from .llm import LLM
        llm = LLM()
        for hash_, status in backfill(args.cwd, store, llm, limit=args.limit, capture_all=args.all):
            print(f"{hash_[:8]}  {status}", flush=True)

    elif args.cmd == "list":
        rows = store.list_capsules(repo=args.repo, limit=args.limit)
        if not rows:
            print("no capsules yet. commit a bugfix/feature, or run `capsule capture`.")
            return 0
        for r in rows:
            print(f"[{r['id']}] {r['kind']:<8} {r['repo']}  {r['created_at'][:10]}")
            print(f"    {r['problem'] or '(no problem)'}")

    elif args.cmd == "show":
        r = store.get_capsule(args.id)
        if r is None:
            print(f"capsule {args.id} not found")
            return 1
        print(f"capsule #{r['id']} · {r['kind']} · {r['repo']} · {r['hash'][:8]}")
        print(f"  问题: {r['problem'] or '-'}")
        print(f"  方案: {r['solution'] or '-'}")
        print(f"  踩坑: {r['gotcha'] or '-'}")

    elif args.cmd == "search":
        from .embed import Embedder
        from .search import ensure_embeddings, search
        emb = Embedder()
        added = ensure_embeddings(store, emb)
        if added:
            print(f"(embedded {added} new capsule(s) with {emb.name})")
        hits = search(store, emb, args.query, k=args.k)
        if not hits:
            print("no matches.")
            return 0
        for score, r in hits:
            print(f"[{r['id']}] {score:.2f} {r['kind']:<8} {r['repo']}")
            print(f"    {r['problem'] or '-'}")

    elif args.cmd == "forget":
        store.delete_capsule(args.id)
        print(f"deleted capsule {args.id}")

    elif args.cmd == "export":
        from .export_md import export_markdown
        text = export_markdown(store, blog=args.blog, week=args.week)
        print(text)

    elif args.cmd == "config":
        from .config import SETTING_KEYS, get_setting, load_settings, set_setting

        if args.config_cmd in (None, "list"):
            data = load_settings()
            if not data:
                print("no settings stored. defaults are in effect.")
            for key, env in SETTING_KEYS.items():
                effective = get_setting(key)
                stored = data.get(key)
                mark = "" if stored is None else "  [stored]"
                print(f"{key:<14} {effective or '(default)'}{mark}  (env: {env})")
        elif args.config_cmd == "get":
            if args.key not in SETTING_KEYS:
                print(f"unknown key '{args.key}'. valid: {', '.join(SETTING_KEYS)}")
                return 1
            print(get_setting(args.key) or "")
        elif args.config_cmd == "set":
            if args.key not in SETTING_KEYS:
                print(f"unknown key '{args.key}'. valid: {', '.join(SETTING_KEYS)}")
                return 1
            set_setting(args.key, args.value)
            print(f"set {args.key} = {args.value}")
        elif args.config_cmd == "unset":
            set_setting(args.key, None)
            print(f"unset {args.key}")
        else:
            from .config import SETTING_KEYS  # noqa: F401
            print(f"usage: capsule config [list|get <key>|set <key> <value>|unset <key>]")
            return 1

    elif args.cmd == "eval":
        from .eval_runner import run_eval
        from .llm import LLM

        llm = LLM()
        print(f"evaluating classification on {llm.model} (extract: {llm.extract_model}) ...")

        def _progress(done, total, expected, got):
            mark = "ok" if expected == got else "MISS"
            print(f"  [{done}/{total}] {expected:<8} -> {got:<8} {mark}", flush=True)

        res = run_eval(llm=llm, limit=args.limit, progress=_progress)
        print(f"accuracy: {res['correct']}/{res['total']} = {res['accuracy']:.1%}  (errors: {res['errors']})")
        if res["misses"]:
            for subject, exp, got in res["misses"]:
                print(f"  expected {exp:<8} got {got:<8} | {subject}")

    store.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
