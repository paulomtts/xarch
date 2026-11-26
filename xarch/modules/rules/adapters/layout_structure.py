"""Structure filled by the layout module: the only file in rules that names layout, and it names only layout's
contract."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from xarch.modules.layout.contract import CheckStructure, StructureChecked, StructureRefused, StructureResult
from xarch.modules.rules.domain.errors import ProfileUnusable
from xarch.modules.rules.domain.outcomes import StructureFound
from xarch.modules.rules.domain.published import Excused


class _Layout(Protocol):
    """The little rules uses of layout's controller."""

    def check(self, cmd: CheckStructure) -> StructureResult: ...


class LayoutStructure:
    """Satisfies rules' Structure port by asking layout to check the structure."""

    def __init__(self, layout: _Layout):
        self._layout = layout

    def checked(self, root: Path, package: str, profile: str, tests: Path | None) -> StructureFound:
        """Raises ProfileUnusable, with layout's reason, when layout cannot check the structure."""
        match self._layout.check(CheckStructure(root, package, profile, tests)):
            case StructureChecked(violations, waived, counterparts):
                return StructureFound(tuple(violations), tuple(Excused(item.rule, item.file, 0, item.key, item.message,
                                                                       item.why) for item in waived), counterparts)
            case StructureRefused(reason):
                raise ProfileUnusable(reason)
