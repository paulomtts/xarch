"""The import rules on hand-made source files: a file's dotted path, the targets its imports point to inside the app's
package, and the imports between governed places that the profile's rules forbid."""
import pytest

from tests.modules.rules.builders import PROFILE, imp, source, steps
from xarch.modules.rules.domain.imports import dotted, targets, violations


@pytest.mark.parametrize("path, expected", [
    pytest.param("kernel/ids.py", (("kernel", "ids"), False), id="a module drops its .py"),
    pytest.param("kernel/__init__.py", (("kernel",), True), id="a package's __init__ is the package"),
    pytest.param("__init__.py", ((), True), id="the root package's __init__ is the root"),
    pytest.param("kernel/data.txt", (("kernel", "data.txt"), False), id="another file keeps its name"),
])
def test_dotted(path, expected):
    assert dotted(steps(path)) == expected


def test_an_empty_path_is_the_root():
    assert dotted(()) == ((), False)


KNOWN = {("kernel", "ids"), ("modules", "docs", "domain", "doc")}
PACKAGE = ("modules", "docs", "domain")


@pytest.mark.parametrize("imports, expected", [
    pytest.param([imp(1, "app.kernel.ids")], [(1, ("kernel", "ids"))], id="a plain import below the root"),
    pytest.param([imp(1, "app")], [(1, ())], id="a plain import of the root itself"),
    pytest.param([imp(1, "yaml"), imp(2, "yaml", "load"), imp(3, "apps.kernel", "x")], [],
                 id="imports outside the root package are none of its targets"),
    pytest.param([imp(1, "app.kernel", "ids", "other")], [(1, ("kernel", "ids")), (1, ("kernel",))],
                 id="a name that is a known file is that module, any other its package"),
    pytest.param([imp(1, "", "doc", level=1)], [(1, ("modules", "docs", "domain", "doc"))],
                 id="a relative import resolves against the importing package"),
    pytest.param([imp(1, "kernel", "ids", level=4)], [(1, ("kernel", "ids"))],
                 id="each further dot climbs one package"),
    pytest.param([imp(1, "", "x", level=5)], [], id="a relative import above the root is none"),
])
def test_targets(imports, expected):
    assert list(targets(imports, PACKAGE, KNOWN, "app")) == expected


APP = [source(p) for p in ["kernel/ids.py", "modules/docs/domain/doc.py", "platform/sql.py"]]


@pytest.mark.parametrize("file, expected", [
    pytest.param(source("modules/docs/domain/values.py", imp(1, "app.kernel", "ids"), imp(2, "", "doc", level=1)), [],
                 id="imports the rules allow"),
    pytest.param(source("modules/docs/domain/values.py", imp(3, "app.platform", "sql")),
                 ["app/modules/docs/domain/values.py:3: domain/ of modules/docs may not import platform/ "
                  "(app.platform.sql)"], id="an import the rules forbid, named by both places"),
    pytest.param(source("modules/docs/__init__.py", imp(1, "app.kernel", "ids")),
                 ["app/modules/docs/__init__.py:1: structure/ may not import kernel/ (app.kernel.ids)"],
                 id="the structure imports nothing"),
    pytest.param(source("modules/docs/domain/values.py", imp(1, "app.scripts", "seed"), imp(2, "app.modules.docs", "x")),
                 ["app/modules/docs/domain/values.py:2: domain/ of modules/docs may not import structure/ "
                  "(app.modules.docs)"],
                 id="imports into ungoverned places are ignored, into the structure not"),
    pytest.param(source("scripts/seed.py", imp(1, "app.platform", "sql")), [], id="an ungoverned file is not checked"),
])
def test_violations(file, expected):
    assert [str(v) for v in violations([file, *APP], PROFILE, "app")] == expected


def test_a_violation_names_its_rule():
    found = violations([source("kernel/x.py", imp(1, "app.platform", "sql")), *APP], PROFILE, "app")
    assert [v.rule for v in found] == ["rules"]
