"""Evaluation runner: measure classification accuracy against the eval set."""
from __future__ import annotations

from .eval_set import load_eval
from .llm import LLM, LLMError


def run_eval(llm: LLM | None = None, limit: int = 0, progress=None) -> dict:
    llm = llm or LLM()
    total = correct = errors = 0
    misses = []
    items = load_eval()
    if limit:
        items = items[:limit]
    for i, (subject, expected, _hint) in enumerate(items):
        total += 1
        try:
            data = llm.analyze_commit(subject, "")
            got = data["kind"]
        except LLMError as e:
            errors += 1
            misses.append((subject, expected, "ERROR"))
            got = "ERROR"
        else:
            if got == expected:
                correct += 1
            else:
                misses.append((subject, expected, got))
        if progress:
            progress(i + 1, len(items), expected, got)
    return {
        "total": total,
        "correct": correct,
        "errors": errors,
        "accuracy": correct / total if total else 0.0,
        "misses": misses,
    }


def main() -> None:
    import argparse

    p = argparse.ArgumentParser(prog="eval")
    p.add_argument("--limit", type=int, default=0)
    a = p.parse_args()
    res = run_eval(limit=a.limit)
    print(f"classification accuracy: {res['correct']}/{res['total']} = {res['accuracy']:.1%}")
    print(f"llm errors: {res['errors']}")
    if res["misses"]:
        print("misses:")
        for subject, exp, got in res["misses"]:
            print(f"  expected {exp:<8} got {got:<8} | {subject}")


if __name__ == "__main__":
    main()
