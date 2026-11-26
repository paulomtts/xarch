"""Rules' Structure read from layout's contract: the check of the structure asked for, its violations, the findings
structure.accepted or a counterpart's accepted waives, each as an accepted finding under its key, and how many sources
each counterpart read."""
from pathlib import Path

import pytest

from xarch.kernel.violations import Violation
from xarch.modules.layout.contract import CheckStructure, StructureChecked, StructureRefused, StructureResult, Waived
from xarch.modules.rules.adapters.layout_structure import LayoutStructure
from xarch.modules.rules.domain.errors import ProfileUnusable
from xarch.modules.rules.domain.outcomes import StructureFound
from xarch.modules.rules.domain.published import Excused

MISSING = Violation("app", 0, "missing kernel/", "structure", "create app/kernel/")
WAIVED = Waived("structure", "app/modules/docs", "missing domain/", "the docs module has no rules yet")
PAIRED = Waived("counterpart", "app/sql/cart", "sql/cart/ has no tests/conformance/cart/ (counterparts.x)", "later",
                "counterparts.x.accepted")


ASKED = CheckStructure(Path("/src/app"), "app", "cli", Path("/src/tests"))


class Layout:
    """Layout's controller as rules' adapter uses it: it answers the one check it knows, and refuses any other."""

    def check(self, cmd: CheckStructure) -> StructureResult:
        return (StructureChecked((MISSING,), (WAIVED, PAIRED), (("x", 2),)) if cmd == ASKED
                else StructureRefused(f"not asked: {cmd}"))


def test_the_structure_is_checked_as_asked_with_its_violations_and_what_it_waives():
    assert LayoutStructure(Layout()).checked(Path("/src/app"), "app", "cli", Path("/src/tests")) == StructureFound(
        (MISSING,), (Excused("structure", "app/modules/docs", 0, "structure.accepted", "missing domain/",
                             "the docs module has no rules yet"),
                     Excused("counterpart", "app/sql/cart", 0, "counterparts.x.accepted", PAIRED.message, "later")),
        (("x", 2),))


def test_a_structure_layout_cannot_check_is_refused_with_its_reason():
    with pytest.raises(ProfileUnusable, match="not asked"):
        LayoutStructure(Layout()).checked(Path("/src/app"), "app", "web", None)
