"""A profile xarch writes, as a YAML file that reads as one written by hand."""
from __future__ import annotations

import re
from typing import Any

from xarch.platform.yaml_writer import YamlWriter

_NAME = re.compile(r"^name:.*$", re.MULTILINE)
"""The top-level `name` line of a YAML profile."""
_BASED_ON = re.compile(r"^based_on:.*\n", re.MULTILINE)
"""The top-level `based_on` line of a YAML profile, with its line break."""


class YamlProfileFormat:
    """Satisfies spec's ProfileFormat port."""

    def __init__(self, writer: YamlWriter):
        self._writer = writer

    def written(self, document: dict[str, Any]) -> bytes:
        return self._writer.dump(document).encode("utf-8")

    def renamed(self, text: str, name: str, based_on: str) -> str | None:
        without = _BASED_ON.sub("", text)
        if _NAME.search(without) is None:
            return None
        return _NAME.sub(lambda _: f"name: {name}\nbased_on: {based_on}", without, count=1)
