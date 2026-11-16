"""Rules' Structure read from layout's contract: the check of the structure asked for, its violations as a list."""
from pathlib import Path

import pytest

from xarch.kernel.violations import Violation
from xarch.modules.layout.contract import CheckStructure, StructureChecked, StructureRefused, StructureResult
from xarch.modules.rules.adapters.layout_structure import LayoutStructure
from xarch.modules.rules.domain.errors import ProfileUnusable

MISSING = Violation("app", 0, "missing kernel/", "structure", "create app/kernel/")


ASKED = CheckStructure(Path("/src/app"), "app", "cli", Path("/src/tests"))


class Layout:
    """Layout's controller as rules' adapter uses it: it answers the one check it knows, and refuses any other."""

    def check(self, cmd: CheckStructure) -> StructureResult:
        return StructureChecked((MISSING,)) if cmd == ASKED else StructureRefused(f"not asked: {cmd}")


def test_the_structure_is_checked_as_asked_and_its_violations_listed():
    assert LayoutStructure(Layout()).violations(Path("/src/app"), "app", "cli", Path("/src/tests")) == [MISSING]


def test_a_structure_layout_cannot_check_is_refused_with_its_reason():
    with pytest.raises(ProfileUnusable, match="not asked"):
        LayoutStructure(Layout()).violations(Path("/src/app"), "app", "web", None)
