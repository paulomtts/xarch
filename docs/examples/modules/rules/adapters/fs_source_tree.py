from __future__ import annotations

import ast
from pathlib import Path

from app.kernel.source import Import
from app.modules.rules.domain.errors import SourceUnreadable
from app.platform.filesystem import FileSystem


class FsSourceTree:
    def __init__(self, fs: FileSystem):
        self._fs = fs

    def files(self, root: Path, extension: str) -> list[str]:
        return [path.relative_to(root).as_posix() for path in self._fs.files(root, extension)]

    def imports(self, root: Path, file: str) -> tuple[Import, ...]:
        try:
            tree = ast.parse(self._fs.read_text(root / file), filename=file)
        except SyntaxError as e:
            raise SourceUnreadable(file, e.lineno or 0, e.msg) from e
        found = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                found += [Import(alias.name, node.lineno) for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                found.append(Import(node.module, node.lineno))
        return tuple(sorted(found, key=lambda imp: imp.line))
