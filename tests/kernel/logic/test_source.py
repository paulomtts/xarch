"""Where a relative import points, on hand-made imports: below the root the importing file's folder lies in."""
import pytest

from xarch.kernel.logic.source import relative_target
from xarch.kernel.source import Import

FOLDER = ("modules", "docs", "domain")


@pytest.mark.parametrize("up, module, target", [
    pytest.param(0, ("values",), ("modules", "docs", "domain", "values"), id="from its own folder"),
    pytest.param(1, ("contract",), ("modules", "docs", "contract"), id="one folder up"),
    pytest.param(3, ("kernel",), ("kernel",), id="up to the root"),
    pytest.param(3, (), (), id="the root itself"),
    pytest.param(4, ("kernel",), None, id="climbing above the root points nowhere"),
])
def test_a_relative_import_climbs_from_its_folder_then_takes_its_module(up, module, target):
    assert relative_target(Import(1, module, relative=True, up=up), FOLDER) == target
