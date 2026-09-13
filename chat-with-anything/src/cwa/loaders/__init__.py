"""数据源加载器：把任意输入（URL/文件/目录/GitHub 仓库）统一成文档列表。"""

from __future__ import annotations

from pathlib import Path
from typing import List

from llama_index.core import Document


def _from_url(url: str) -> List[Document]:
    from llama_index.readers.web import SimpleWebPageReader

    docs = SimpleWebPageReader(html_to_text=True).load_data([url])
    return list(docs)


def _from_github(url: str) -> List[Document]:
    from llama_index.readers.github import GithubRepositoryReader

    # url 形如 https://github.com/owner/repo
    parts = url.rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1]
    docs = GithubRepositoryReader(owner=owner, repo=repo).load_data()
    return list(docs)


def _from_dir(path: Path) -> List[Document]:
    from llama_index.core import SimpleDirectoryReader

    docs = SimpleDirectoryReader(input_dir=str(path), recursive=True).load_data()
    return list(docs)


def _from_file(path: Path) -> List[Document]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from llama_index.readers.file import PDFReader

        return list(PDFReader().load_data(file=path))
    if suffix in {".txt", ".md", ".markdown", ".py", ".json", ".csv", ".yaml", ".yml"}:
        from llama_index.core import SimpleDirectoryReader

        return list(SimpleDirectoryReader(input_files=[str(path)]).load_data())
    # 兜底：交给 SimpleDirectoryReader 尝试
    from llama_index.core import SimpleDirectoryReader

    return list(SimpleDirectoryReader(input_files=[str(path)]).load_data())


def load(source: str) -> List[Document]:
    """入口：根据输入类型分派到对应加载器。

    返回统一格式的 Document 列表，供下游切分使用。
    """
    s = source.strip()
    if s.startswith("http://") or s.startswith("https://"):
        if "github.com" in s:
            return _from_github(s)
        return _from_url(s)

    path = Path(s)
    if path.is_dir():
        return _from_dir(path)
    if path.is_file():
        return _from_file(path)

    raise ValueError(f"无法识别数据源: {source!r}（既不是 URL，也不是存在的文件/目录）")
