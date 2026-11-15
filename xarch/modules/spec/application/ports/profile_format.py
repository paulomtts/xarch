from __future__ import annotations

from typing import Any, Protocol


class ProfileFormat(Protocol):
    """The form a profile file xarch writes takes."""

    def written(self, document: dict[str, Any]) -> bytes:
        """The content of a profile file that holds the document, as xarch writes one."""
        ...
