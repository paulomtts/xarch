"""Where an import points, on hand-made imports: below the root the importing file's folder lies in."""
import pytest

from xarch.kernel.logic.source import imported_names
from xarch.kernel.source import Import

FOLDER = ("modules", "docs", "domain")


@pytest.mark.parametrize("imp, folder, taken", [
    pytest.param(Import(1, ("values",), ("x",), relative=True), FOLDER, [(("modules", "docs", "domain", "values"), "x")],
                 id="a relative import from its own folder"),
    pytest.param(Import(1, ("contract",), ("x",), relative=True, up=1), FOLDER, [(("modules", "docs", "contract"), "x")],
                 id="a relative import one folder up"),
    pytest.param(Import(1, ("kernel",), ("x",), relative=True, up=3), FOLDER, [(("kernel",), "x")],
                 id="a relative import up to the root"),
    pytest.param(Import(1, (), ("x",), relative=True, up=3), FOLDER, [((), "x")],
                 id="a relative import of the root itself"),
    pytest.param(Import(1, ("kernel",), ("x",), relative=True, up=4), FOLDER, [],
                 id="a relative import climbing above the root points nowhere"),
    pytest.param(Import(1, ("app", "kernel", "ids")), FOLDER, [(("kernel", "ids"), None)],
                 id="a whole module of the root"),
    pytest.param(Import(1, ("app", "kernel"), ("ids",)), FOLDER, [(("kernel",), "ids")],
                 id="names from a module of the root"),
    pytest.param(Import(1, ("values",), ("Doc",), relative=True), FOLDER,
                 [(("modules", "docs", "domain", "values"), "Doc")], id="names from a module of its own folder"),
    pytest.param(Import(1, ("x",), ("y",), relative=True, up=4), FOLDER, [], id="names from above the root point nowhere"),
    pytest.param(Import(1, ("os",)), FOLDER, [], id="a module outside the root points nowhere below it"),
    pytest.param(Import(1, ("app",)), FOLDER, [((), None)], id="the root itself"),
    pytest.param(Import(1, ("app", "docs")), (), [(("docs",), None)], id="a module taken whole"),
    pytest.param(Import(1, ("app", "docs"), ("a", "b")), (), [(("docs",), "a"), (("docs",), "b")],
                 id="each name it names from a module"),
    pytest.param(Import(1, ("yaml",), ("load",)), (), [], id="nothing outside the root"),
])
def test_an_import_takes_its_module_whole_or_each_name_it_names_from_it_below_the_root_or_nothing(imp, folder, taken):
    assert imported_names(imp, folder, "app") == taken
