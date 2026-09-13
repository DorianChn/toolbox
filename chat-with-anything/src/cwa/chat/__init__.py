"""交互式问答：加载索引 + 查询 + 展示带引用的回答。"""

from __future__ import annotations

from llama_index.core import Settings, VectorStoreIndex
from llama_index.core.storage.storage_context import StorageContext

from ..config import Config
from ..pipeline import _configure_embeddings
from ..store import load_store


def build_query_engine(cfg: Config, index_id: str):
    """基于已持久化的索引构建查询引擎。"""
    from ..llm import build_llm

    _configure_embeddings(cfg)
    Settings.llm = build_llm(cfg)

    vector_store = load_store(cfg, index_id)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)

    return index.as_query_engine(streaming=False)


def ask_once(cfg: Config, index_id: str, question: str) -> str:
    engine = build_query_engine(cfg, index_id)
    response = engine.query(question)
    return str(response)


def run_repl(cfg: Config, index_id: str) -> None:
    """交互式对话循环。"""
    from rich.console import Console
    from rich.markdown import Markdown

    console = Console()
    engine = build_query_engine(cfg, index_id)

    console.print(f"[bold green]已就绪[/] — 对索引 [bold cyan]{index_id}[/] 提问，输入 :q 退出")
    while True:
        try:
            question = console.input("[bold]你 > [/]")
        except (EOFError, KeyboardInterrupt):
            console.print("\n再见")
            break
        if question.strip() in {":q", ":quit", "exit"}:
            console.print("再见")
            break
        if not question.strip():
            continue

        with console.status("思考中..."):
            response = engine.query(question)
        console.print("\n[bold]助手 >[/]")
        console.print(Markdown(str(response)))
        console.print("")

        # 打印引用来源
        source_nodes = getattr(response, "source_nodes", None) or []
        if source_nodes:
            console.print("[dim]引用来源:[/]")
            seen = set()
            for node in source_nodes[:3]:
                src = node.node.metadata.get("file_name") or node.node.metadata.get("source") or "未知"
                score = getattr(node, "score", None)
                label = f"  - {src}"
                if score is not None:
                    label += f"（相关度 {score:.2f}）"
                if label not in seen:
                    seen.add(label)
                    console.print(label, style="dim")
            console.print("")
