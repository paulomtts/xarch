"""The example check: the imports of an architecture's Python examples obey that architecture's own rules."""
from dataclasses import replace


from xarch.modules.spec.application.logic.example_imports import example_problems
from xarch.modules.spec.domain.architecture_file import parse_architecture
from xarch.modules.spec.domain.values import Example


def layered(examples: dict) -> dict:
    return {
        "xarch": 1, "name": "layered",
        "layout": {"src": {"singular": "module", "each": {"api.py": "file", "service": {}, "store": {"sql": {}}}}, "shared": {}},
        "parts": {"shared": {"path": "shared", "role": "code every module uses"},
                  "store": {"path": "src/*/store", "role": "database access"},
                  "sql": {"path": "src/*/store/sql", "role": "queries"},
                  "service": {"path": "src/*/service", "role": "business logic"},
                  "api": {"path": "src/*/api.py", "role": "HTTP handlers"}},
        "rules": {"shared": ["shared"], "store": ["store@own", "sql@own", "shared/text"], "sql": ["sql@own"],
                  "service": ["service@own", "store@own", "api@any"], "api": ["*"]},
        "examples": examples,
    }


def check(**codes: str) -> list[str]:
    """The problems of examples named after their part, each at <part>/x.py in module billing, holding its code."""
    paths = {"shared": "shared/x.py", "store": "src/billing/store/x.py", "sql": "src/billing/store/sql/x.py",
             "service": "src/billing/service/x.py", "api": "src/billing/api.py"}
    examples = {part: {"part": part, "path": paths[part], "file": f"{part}.py"} for part in codes}
    architecture = parse_architecture(layered(examples), "layered.yaml", lambda r: True)
    return example_problems(architecture, codes)


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
        "example service (src/billing/service/x.py): imports app.src.tax.store which service may not import "
        "(rules.service)",
        "example service (src/billing/service/x.py): imports app.shared which service may not import "
        "(rules.service)",
        "example store (src/billing/store/x.py): imports app.shared.other which store may not import (rules.store)",
        "example store (src/billing/store/x.py): imports app.src.billing.service which store may not import "
        "(rules.store)",
        "example sql (src/billing/store/sql/x.py): imports app.src.billing.store.repo which sql may not import "
        "(rules.sql)",
        "example shared (shared/x.py): imports app.src.billing which shared may not import (rules.shared)",
    ]


def test_relative_imports_resolve_from_the_examples_path():
    assert check(service="from .rules import cap\nfrom ..store import Repo\nfrom ...tax.store import T\n") == [
        "example service (src/billing/service/x.py): imports app.src.tax.store which service may not import "
        "(rules.service)"]


def test_an_example_in_no_part_or_not_valid_python_is_reported_and_other_files_are_not_checked():
    architecture = parse_architecture(layered({
        "a": {"part": "service", "path": "src/billing/service/a.py", "file": "a.py"},
        "b": {"part": "service", "path": "src/billing/service/b.py", "file": "b.py"},
        "c": {"part": "service", "path": "src/billing/service/c.sql", "file": "c.sql"}}),
        "layered.yaml", lambda r: True)
    loose = Example("loose", "service", ("src", "billing", "helpers.py"), "loose.py")
    architecture = replace(architecture, examples={**architecture.examples, "loose": loose})
    texts = {"a": "def f(:\n", "b": "", "c": "from app.src.tax.store import x", "loose": ""}
    assert example_problems(architecture, texts) == [
        "example a (src/billing/service/a.py): is not valid Python: invalid syntax (line 1)",
        "example loose (src/billing/helpers.py): lies in no part of the architecture",
    ]
