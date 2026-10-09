"""Settings from the [tool.xarch] table of the nearest pyproject.toml at or above the folder holding the app."""
from __future__ import annotations

from pathlib import Path

from xarch.modules.spec.domain.errors import UnreadableSettings
from xarch.modules.spec.domain.values import Configured
from xarch.platform.filesystem import FileSystem
from xarch.platform.toml import TomlReader


class PyprojectSettings:                   # satisfies spec's Settings port
    def __init__(self, fs: FileSystem, toml: TomlReader):
        self._fs, self._toml = fs, toml

    def configured_profile(self, app: Path) -> Configured | None:
        source = self._fs.find_upward(app.absolute().parent, "pyproject.toml")
        if source is None:
            return None
        try:
            document = self._toml.read(source)
        except ValueError as e:
            raise UnreadableSettings(source, str(e)) from e
        table = document.get("tool", {}).get("xarch", {})
        if not isinstance(table, dict) or "profile" not in table:
            return None
        if not isinstance(table["profile"], str):
            raise UnreadableSettings(source, "[tool.xarch] profile must be a string")
        return Configured(table["profile"], source)
