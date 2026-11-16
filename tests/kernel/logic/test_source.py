"""Where an import points, on hand-made imports: below the root the importing file's folder lies in."""
import pytest

from xarch.kernel.logic.source import imported_module, imported_names, relative_target
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


@pytest.mark.parametrize("imp, module", [
    pytest.param(Import(1, ("app", "kernel", "ids")), ("kernel", "ids"), id="a whole module of the root"),
    pytest.param(Import(1, ("app", "kernel"), ("ids",)), ("kernel",), id="names from a module of the root"),
    pytest.param(Import(1, ("values",), ("Doc",), relative=True), ("modules", "docs", "domain", "values"),
                 id="names from a module of its own folder"),
    pytest.param(Import(1, ("x",), ("y",), relative=True, up=4), None, id="names from above the root point nowhere"),
    pytest.param(Import(1, ("os",)), None, id="a module outside the root points nowhere below it"),
    pytest.param(Import(1, ("app",)), (), id="the root itself"),
])
def test_an_import_names_a_module_below_the_root_or_none(imp, module):
    assert imported_module(imp, FOLDER, "app") == module


def test_an_import_takes_its_module_whole_or_each_name_it_names_from_it_and_nothing_outside_the_root():
    assert imported_names(Import(1, ("app", "docs")), (), "app") == [(("docs",), None)]
    assert imported_names(Import(1, ("app", "docs"), ("a", "b")), (), "app") == [(("docs",), "a"), (("docs",), "b")]
    assert imported_names(Import(1, ("yaml",), ("load",)), (), "app") == []
