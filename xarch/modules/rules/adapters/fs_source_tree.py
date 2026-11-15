"""SourceTree on the local filesystem: lists the .py files, and parses one with ast and tokenize, never running it."""
from __future__ import annotations

import ast
import io
import tokenize
from pathlib import Path

from xarch.modules.rules.domain.values import Comment, Import, SourceFile, Union
from xarch.platform.filesystem import FileSystem


class FsSourceTree:
    def __init__(self, fs: FileSystem):
        self._fs = fs

    def is_dir(self, root: Path) -> bool:
        return self._fs.is_dir(root)

    def paths(self, root: Path) -> list[tuple[str, ...]]:
        return [f.relative_to(root).parts for f in self._fs.files(root, "*.py")]

    def read(self, root: Path, paths: list[tuple[str, ...]]) -> list[SourceFile]:
        return [_parsed(root.joinpath(*path).relative_to(root.parent).as_posix(), path,
                        self._fs.read_text(root.joinpath(*path))) for path in paths]


def _parsed(name: str, path: tuple[str, ...], text: str) -> SourceFile:
    try:
        tree = ast.parse(text)
        comments = _comments(text)
    except SyntaxError as e:
        return SourceFile(name, path, (), error=(e.lineno or 0, f"not valid Python: {e.msg}"))
    except (tokenize.TokenError, IndentationError) as e:
        return SourceFile(name, path, (), error=(0, f"not valid Python: {e}"))
    return SourceFile(name, path, tuple(_imports(tree)), comments, ast.get_docstring(tree), _functions(tree),
                      tuple(_unions(tree)))


def _imports(tree: ast.AST) -> list[Import]:
    found: list[Import] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [Import(node.lineno, tuple(alias.name.split("."))) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = tuple(node.module.split(".")) if node.module else ()
            found.append(Import(node.lineno, module, node.level, tuple(a.name for a in node.names)))
    return found


def _comments(text: str) -> tuple[Comment, ...]:
    tokens = tokenize.generate_tokens(io.StringIO(text).readline)
    return tuple(Comment(t.start[0], t.string) for t in tokens if t.type == tokenize.COMMENT)


def _functions(tree: ast.Module) -> tuple[str, ...]:
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(node.name)
        elif isinstance(node, ast.ClassDef):
            names += [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    return tuple(names)


def _unions(tree: ast.Module) -> list[Union]:
    found: list[Union] = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name, value = node.targets[0].id, node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.value is not None:
            name, value = node.target.id, node.value
        elif isinstance(node, ast.TypeAlias) and isinstance(node.name, ast.Name):
            name, value = node.name.id, node.value
        else:
            continue
        members = _members(value)
        if members is not None and len(members) > 1:
            found.append(Union(node.lineno, name, members))
    return found


def _members(node: ast.expr) -> tuple[str, ...] | None:
    if isinstance(node, ast.Name):
        return (node.id,)
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        left, right = _members(node.left), _members(node.right)
        return left + right if left is not None and right is not None else None
    return None
