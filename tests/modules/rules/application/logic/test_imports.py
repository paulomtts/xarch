"""The import rules on hand-made source files: a file's dotted path, the targets its imports point to inside the app's
package, and the imports between governed places that the profile's rules forbid."""
from dataclasses import replace

import pytest

from tests.modules.rules.builders import PROFILE, imp, source, steps
from xarch.kernel.logic.placement import Target
from xarch.modules.rules.application.logic.imports import dotted, targets, violations


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


@pytest.mark.parametrize("file, fix", [
    pytest.param(source("modules/docs/domain/values.py", imp(3, "app.platform", "sql")),
                 "import only domain/, kernel/ in domain/ of modules/docs (parts.domain.may_import), or move this code to "
                 "adapters/, which may import it", id="the parts the importer may import, and the ones that may import the target"),
    pytest.param(source("modules/docs/__init__.py", imp(1, "app.kernel", "ids")),
                 "drop the import of kernel/, or move this code to domain/, contract/, controller/ or another part that "
                 "may import it", id="a place that may import nothing, and more parts that may import the target "
                                     "than are named"),
    pytest.param(source("kernel/x.py", imp(1, "app.modules.docs.domain", "doc")),
                 "import only kernel/ in kernel/ (parts.kernel.may_import), or move this code to contract/, controller/, services/ or "
                 "another part that may import it", id="more parts that may import the target than are named"),
    pytest.param(source("modules/docs/domain/values.py", imp(1, "app.scripts.x"), imp(2, "app.modules.docs", "x")),
                 "import only domain/, kernel/ in domain/ of modules/docs (parts.domain.may_import), or move this code to a "
                 "part that may import structure/", id="no part names the target's part"),
])
def test_a_violation_says_what_to_do(file, fix):
    assert [v.fix for v in violations([file, *APP], PROFILE, "app")] == [fix]


NARROWED = replace(PROFILE, rules={**PROFILE.rules, "contract": (Target("domain", "own", ("values",), "*Id"),
                                                                  Target("kernel"))})
CONTRACT = "modules/docs/contract/__init__.py"
VALUES = source("modules/docs/domain/values.py")


@pytest.mark.parametrize("imports, expected", [
    pytest.param([imp(1, "app.modules.docs.domain.values", "DocumentId", "OwnerId")], [],
                 id="names that match the pattern"),
    pytest.param([imp(1, "app.modules.docs.domain.values", "DocumentId", "Document")],
                 ["app/modules/docs/contract/__init__.py:1: contract/ of modules/docs may import only *Id from "
                  "domain/ of modules/docs, not Document (app.modules.docs.domain.values.Document)"],
                 id="a name that does not"),
    pytest.param([imp(1, "app.modules.docs.domain", "values")],
                 ["app/modules/docs/contract/__init__.py:1: contract/ of modules/docs may import only *Id from "
                  "domain/ of modules/docs, not the file as a whole (app.modules.docs.domain.values)"],
                 id="the file as a whole"),
    pytest.param([imp(1, "app.modules.docs.domain.values")],
                 ["app/modules/docs/contract/__init__.py:1: contract/ of modules/docs may import only *Id from "
                  "domain/ of modules/docs, not the file as a whole (app.modules.docs.domain.values)"],
                 id="a plain import of the file"),
])
def test_a_target_with_a_name_pattern_allows_only_the_names_it_matches(imports, expected):
    found = violations([source(CONTRACT, *imports), VALUES], NARROWED, "app")
    assert [str(v) for v in found] == expected
    assert {v.fix for v in found} <= {
        "import from domain/ of modules/docs only names that match *Id (parts.contract.may_import), or move what needs "
        "the rest to a part that may import it"}
