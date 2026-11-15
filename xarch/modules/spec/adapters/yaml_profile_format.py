"""A profile xarch writes, as a YAML file that reads as one written by hand."""
from __future__ import annotations

from typing import Any

from xarch.platform.yaml_writer import YamlWriter


class YamlProfileFormat:
    """Satisfies spec's ProfileFormat port."""

    def __init__(self, writer: YamlWriter):
        self._writer = writer

    def written(self, document: dict[str, Any]) -> bytes:
        return self._writer.dump(document).encode("utf-8")
