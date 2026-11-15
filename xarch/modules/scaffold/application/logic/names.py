from __future__ import annotations

from collections.abc import Collection


def valid_name(name: str, reserved: Collection[str]) -> bool:
    return (name.isascii() and name.isidentifier() and name == name.lower() and not name.startswith("_")
            and name not in reserved)
