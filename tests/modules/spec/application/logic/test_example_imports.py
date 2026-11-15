"""The example check: the imports of an architecture's Python examples obey that architecture's own rules."""
from tests.modules.spec.profiles_v2 import layered as layered_v2
from tests.modules.spec.profiles_v2 import parsed as v2
from xarch.modules.spec.application.logic.example_imports import example_problems

PROFILE = {
    "xarch": 2, "name": "layered",
    "parts": {"shared": {"path": "shared", "role": "code every module uses"},
              "store": {"path": "src/<module>/store", "role": "database access", "may_import": ["sql", "shared/text"]},
              "sql": {"path": "src/<module>/store/sql", "role": "queries"},
              "service": {"path": "src/<module>/service", "role": "business logic",
                          "may_import": ["store", "api@any"]},
              "api": {"path": "src/<module>/api.py", "role": "HTTP handlers", "may_import": "everything"}},
}
PATHS = {"shared": "shared/x.py", "store": "src/billing/store/x.py", "sql": "src/billing/store/sql/x.py",
         "service": "src/billing/service/x.py", "api": "src/billing/api.py"}


def project(texts: dict[str, str]) -> list[str]:
    """The problems of an example project whose files are the paths given, each holding its text."""
    architecture = v2(PROFILE | {"docs": {"examples": ["ex"]}}, folders={"ex": tuple(texts)})
    return example_problems(architecture, texts)


def check(**codes: str) -> list[str]:
    """The problems of examples at <part>/x.py in module billing, each holding the code given for its part."""
    return project({PATHS[part]: code for part, code in codes.items()})


def test_imports_the_rules_allow_pass():
    """Imports outside the app are ignored; api@any reaches another module's api; a module of shared is reached by
    name (shared/text); api's * reaches everything, the structure too."""
    assert check(
        service="import os\nfrom typing import Protocol\nimport yaml\n"
                "from app.src.billing.service.rules import cap\nfrom app.src.billing.store import Repo\n"
                "import app.src.billing.store.repo\nfrom app.src.tax.api import handle\n",
        store="from app.shared.text import slug\nfrom app.src.billing.store.sql import queries\n"
              "from app.shared import text\n",
        sql="from app.src.billing.store.sql.queries import Q\n",
        api="from app.src.tax.store import Repo\nimport app\n",
    ) == []


def test_an_import_the_rules_forbid_is_reported_once_with_its_rule():
    """store@own reaches billing's store, not tax's; shared/text reaches only that path of shared; sql lies deeper
    than store, so it is its own part with its own rules; the structure (app.src.billing) is reached only by *."""
    assert check(
        service="from app.src.tax.store import Repo\nfrom app.src.tax.store import Other\n"
                "from app.shared import x\n",
        store="from app.shared.other import y\nfrom app.src.billing.service import S\n",
        sql="from app.src.billing.store.repo import R\n",
        shared="from app.src import billing\n",
    ) == [
        "example (src/billing/service/x.py): imports app.src.tax.store which service may not import "
        "(parts.service.may_import)",
        "example (src/billing/service/x.py): imports app.shared which service may not import "
        "(parts.service.may_import)",
        "example (src/billing/store/x.py): imports app.shared.other which store may not import (parts.store.may_import)",
        "example (src/billing/store/x.py): imports app.src.billing.service which store may not import "
        "(parts.store.may_import)",
        "example (src/billing/store/sql/x.py): imports app.src.billing.store.repo which sql may not import "
        "(parts.sql.may_import)",
        "example (shared/x.py): imports app.src.billing which shared may not import (parts.shared.may_import)",
    ]


def test_a_part_may_import_itself_in_its_own_instance_and_not_in_another_without_saying_so():
    assert check(
        shared="from app.shared import x\n",
        sql="from app.src.billing.store.sql.queries import Q\nfrom app.src.tax.store.sql import Q\n",
    ) == [
        "example (src/billing/store/sql/x.py): imports app.src.tax.store.sql which sql may not import (parts.sql.may_import)"]


def test_relative_imports_resolve_from_the_examples_path():
    assert check(service="from .rules import cap\nfrom ..store import Repo\nfrom ...tax.store import T\n") == [
        "example (src/billing/service/x.py): imports app.src.tax.store which service may not import "
        "(parts.service.may_import)"]


def test_an_example_in_no_part_or_not_valid_python_is_reported_and_other_files_are_not_checked():
    assert project({"src/billing/service/a.py": "def f(:\n", "src/billing/service/b.py": "",
                    "src/billing/service/c.sql": "from app.src.tax.store import x",
                    "src/billing/helpers.py": ""}) == [
        "example (src/billing/service/a.py): is not valid Python: invalid syntax (line 1)",
        "example (src/billing/helpers.py): lies in no part of the architecture"]


def test_every_python_file_of_an_example_project_is_checked_by_its_path_and_test_code_is_only_parsed():
    files = ("src/billing/api/x.py", "src/billing/store/x.py", "shared/text.py", "tests/src/billing/test_x.py",
             "tests/src/billing/test_y.py", "other/x.py", "notes.md")
    architecture = v2(layered_v2(docs={"examples": ["ex"]}), folders={"ex": files})
    texts = {"src/billing/api/x.py": "from app.src.billing.service import S\n",
             "src/billing/store/x.py": "from app.shared import text\nfrom app.src.billing.api import A\n",
             "shared/text.py": "import os\n",
             "tests/src/billing/test_x.py": "from app.src.billing.api import anything\n",
             "tests/src/billing/test_y.py": "def f(:\n", "other/x.py": "X = 1\n", "notes.md": "not python ("}
    assert example_problems(architecture, texts) == [
        "example (src/billing/store/x.py): imports app.src.billing.api which store may not import "
        "(parts.store.may_import)",
        "example (tests/src/billing/test_y.py): is not valid Python: invalid syntax (line 1)",
        "example (other/x.py): lies in no part of the architecture"]
