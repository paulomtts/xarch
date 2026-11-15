"""Rules' Structure read from layout's contract: the check of the structure asked for, its violations as a list."""
from pathlib import Path

from xarch.kernel.violations import Violation
from xarch.modules.layout.contract import CheckStructure, StructureChecked
from xarch.modules.rules.adapters.layout_structure import LayoutStructure

MISSING = Violation("app", 0, "missing kernel/", "structure", "create app/kernel/")


class Layout:
    """Layout's controller as rules' adapter uses it: it records the check it is asked for."""

    def __init__(self):
        self.asked: list[CheckStructure] = []

    def check(self, cmd: CheckStructure) -> StructureChecked:
        self.asked.append(cmd)
        return StructureChecked((MISSING,))


def test_the_structure_is_checked_as_asked_and_its_violations_listed():
    layout = Layout()
    found = LayoutStructure(layout).violations(Path("/src/app"), "app", "cli", Path("/src/tests"))
    assert found == [MISSING]
    assert layout.asked == [CheckStructure(Path("/src/app"), "app", "cli", Path("/src/tests"))]
