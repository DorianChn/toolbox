"""chat-with-anything 命令行入口。"""

from __future__ import annotations

import typer
from rich.console import Console

from . import __version__
from .config import Config, load, set_value
from .loaders import load as load_source
from .pipeline import build_index
from .store import list_indexes

app = typer.Typer(
    name="cwa",
    help="一行命令，把任意数据源变成可对话的 AI 助手",
    add_completion=False,
    no_args_is_help=True,
)
console = Console()


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"cwa v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False, "--version", "-v", callback=_version_callback, help="显示版本号"
    ),
) -> None:
    pass


@app.command()
def ask(
    source: str = typer.Argument(..., help="数据源：URL / PDF / 文件 / 目录 / GitHub 仓库"),
) -> None:
    """一条命令：从数据源建索引并进入交互式对话。"""
    cfg = load()

    with console.status(f"加载数据源 [cyan]{source}[/] ..."):
        documents = load_source(source)
    if not documents:
        console.print("[red]没有加载到任何内容，请检查数据源[/]")
        raise typer.Exit(code=1)

    console.print(f"[green]已加载 {len(documents)} 个文档片段[/]")

    with console.status("构建向量索引（首次会下载本地 embedding 模型）..."):
        index_id = build_index(documents, cfg)

    console.print(f"[green]索引构建完成: [cyan]{index_id}[/][/]")

    from .chat import run_repl

    run_repl(cfg, index_id)


@app.command()
def index(
    source: str = typer.Argument(..., help="数据源：URL / PDF / 文件 / 目录 / GitHub 仓库"),
) -> None:
    """只建索引，输出 index_id（可稍后用 chat 命令提问）。"""
    cfg = load()

    with console.status(f"加载数据源 [cyan]{source}[/] ..."):
        documents = load_source(source)
    if not documents:
        console.print("[red]没有加载到任何内容[/]")
        raise typer.Exit(code=1)

    with console.status("构建向量索引..."):
        index_id = build_index(documents, cfg)

    console.print(f"[green]索引构建完成: [cyan]{index_id}[/][/]")
    console.print(f"现在可用 `cwa chat {index_id}` 对它提问")


@app.command()
def chat(
    index_id: str = typer.Argument(..., help="索引 ID（由 cwa index 输出）"),
) -> None:
    """对已有索引进行交互式提问。"""
    cfg = load()
    from .chat import run_repl

    run_repl(cfg, index_id)


@app.command("list")
def list_cmd() -> None:
    """列出所有已构建的索引。"""
    cfg = load()
    indexes = list_indexes(cfg)
    if not indexes:
        console.print("[dim]暂无索引，用 `cwa index <数据源>` 创建一个[/]")
        return
    console.print("[bold]已有索引:[/]")
    for name in indexes:
        console.print(f"  - [cyan]{name}[/]")


@app.command()
def config(
    key: str = typer.Argument(..., help="配置项：api_key / base_url / model / embed_model / ollama_model"),
    value: str = typer.Argument(..., help="配置值"),
) -> None:
    """设置配置项（持久化到 ~/.cwa/config.json）。"""
    try:
        cfg = set_value(key, value)
    except KeyError as e:
        console.print(f"[red]{e}[/]")
        raise typer.Exit(code=1)
    console.print(f"[green]已设置 {key} = {value}[/]")


@app.command()
def show_config() -> None:
    """显示当前配置（api_key 脱敏显示）。"""
    cfg = load()
    console.print("[bold]当前配置:[/]")
    for k, v in cfg.__dict__.items():
        if k == "api_key" and v:
            v = v[:6] + "..." + v[-4:]
        elif k == "api_key":
            v = "(未配置)"
        console.print(f"  {k}: {v}")


def main() -> None:
    """CLI 入口：捕获业务异常，干净地显示错误消息（不刷 traceback）。"""
    try:
        app()
    except typer.Exit:
        # 正常退出（如 --version、ask 无内容退出），透传
        raise
    except (RuntimeError, ValueError) as e:
        console.print(f"[red]错误: {e}[/]")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
