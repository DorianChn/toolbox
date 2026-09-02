"""Markdown export: weekly recap or blog draft."""
from __future__ import annotations

from .store import Store


def export_markdown(store: Store, blog: bool = False, week: bool = False) -> str:
    rows = store.list_capsules(limit=200)
    if not rows:
        return "no capsules to export."

    if week:
        from collections import Counter

        kinds = Counter(r["kind"] for r in rows)
        repos = {r["repo"] for r in rows}
        repo_label = ", ".join(sorted(repos)) if repos else "devcapsule"
        lines = [f"# 本周复盘（{repo_label}）", ""]
        lines.append(f"共捕获 {len(rows)} 张卡：" + "、".join(f"{k}×{v}" for k, v in kinds.items()))
        lines.append("")
        for r in rows[:30]:
            lines.append(f"- [{r['kind']}] {r['problem']}")
        return "\n".join(lines)

    if blog:
        lines = ["# 我修过的那些 bug（devcapsule 导出）", ""]
        for r in rows:
            lines.append(f"## {r['problem'] or '(无标题)'}")
            lines.append("")
            if r["solution"]:
                lines.append(f"**方案**：{r['solution']}")
                lines.append("")
            if r["gotcha"]:
                lines.append(f"**踩坑**：{r['gotcha']}")
                lines.append("")
            lines.append(f"<!-- {r['repo']} {r['hash'][:8]} {r['kind']} -->")
            lines.append("")
        return "\n".join(lines)

    # default: plain list
    lines = ["# devcapsule export", ""]
    for r in rows:
        lines.append(f"## [{r['id']}] {r['kind']} · {r['repo']}")
        lines.append(f"- 问题: {r['problem'] or '-'}")
        lines.append(f"- 方案: {r['solution'] or '-'}")
        lines.append(f"- 踩坑: {r['gotcha'] or '-'}")
        lines.append("")
    return "\n".join(lines)
