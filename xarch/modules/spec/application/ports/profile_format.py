from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol

from xarch.profile_values.checks import WrittenCheck


class ProfileFormat(Protocol):
    """The form a profile file xarch writes takes."""

    def written(self, document: dict[str, Any]) -> bytes:
        """The content of a profile file that holds the document, as xarch writes one."""
        ...

    def renamed(self, text: str, name: str, based_on: str) -> str | None:
        """The text of a profile file with its `name` set to name and `based_on` to based_on, right after it, every
        other line, comment included, as written; None when the text has no top-level `name`."""
        ...

    def checks(self, checks: Mapping[str, WrittenCheck]) -> str:
        """The checks as the `checks` of a profile, each under its id, with its examples when it has any, as the
        format spec reads them is written."""
        ...
