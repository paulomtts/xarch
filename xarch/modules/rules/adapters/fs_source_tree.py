"""SourceTree on the local filesystem: finds the .py files and parses their imports with ast, never running code."""
from __future__ import annotations

import ast
from pathlib import Path

from xarch.modules.rules.domain.values import Import, SourceFile
from xarch.platform.filesystem import FileSystem


class FsSourceTree:
    def __init__(self, fs: FileSystem):
        self._fs = fs

    def is_dir(self, root: Path) -> bool:
        return self._fs.is_dir(root)

    def read(self, root: Path) -> list[SourceFile]:
        return [SourceFile(f.relative_to(root.parent).as_posix(), f.relative_to(root).parts,
                           tuple(_imports(ast.parse(self._fs.read_text(f)))))
                for f in self._fs.files(root, "*.py")]


def _imports(tree: ast.AST) -> list[Import]:
    found: list[Import] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found += [Import(node.lineno, tuple(alias.name.split("."))) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            module = tuple(node.module.split(".")) if node.module else ()
            found.append(Import(node.lineno, module, node.level, tuple(a.name for a in node.names)))
    return found
