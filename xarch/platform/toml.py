"""Reading TOML files. Knows no module."""
from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any


class TomlReader:
    def read(self, path: Path) -> dict[str, Any]:
        """The parsed document; raises ValueError if it is not valid TOML."""
        return tomllib.loads(path.read_text())
