"""Settings from the [tool.xarch] table of the nearest pyproject.toml at or above the folder holding the app."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from xarch.modules.spec.domain.errors import UnreadableSettings
from xarch.modules.spec.domain.values import Configured
from xarch.platform.filesystem import FileSystem
from xarch.platform.toml import TomlReader


class PyprojectSettings:
    """Satisfies spec's Settings port."""

    def __init__(self, fs: FileSystem, toml: TomlReader):
        self._fs, self._toml = fs, toml

    def configured_profile(self, app: Path) -> Configured | None:
        found = self._setting(app.absolute().parent, "profile")
        return Configured(found[0], found[1]) if found is not None else None

    def configured_tests(self, app: Path) -> Path | None:
        found = self._setting(app.absolute().parent, "tests")
        return found[1].parent / found[0] if found is not None else None

    def configured_app(self, start: Path) -> Path | None:
        found = self._setting(start.absolute(), "app")
        return found[1].parent / found[0] if found is not None else None

    def _setting(self, folder: Path, key: str) -> tuple[str, Path] | None:
        source = self._fs.find_upward(folder, "pyproject.toml")
        if source is None:
            return None
        try:
            document: dict[str, Any] = self._toml.read(source)
        except ValueError as e:
            raise UnreadableSettings(source, str(e)) from e
        table = document.get("tool", {}).get("xarch", {})
        if not isinstance(table, dict) or key not in table:
            return None
        if not isinstance(table[key], str):
            raise UnreadableSettings(source, f"[tool.xarch] {key} must be a string")
        return table[key], source
