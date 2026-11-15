"""Every violation names the stable id of the check that found it, and carries the fix its message already states, on
a throwaway web project with one violation planted at a time."""
from pathlib import Path

import pytest

from tests.bootstrap.project import APP, TESTS, write
from xarch.bootstrap.wiring import build_controllers
from xarch.kernel.violations import Violation
from xarch.modules.rules.contract import CheckImports, ImportsChecked

CONTROLLER = "app.modules.docs.application.controller"
MODULES = {"modules/mod/__init__.py": "", "modules/mod/contract/__init__.py": "",
           "modules/docs/adapters/mod_review.py": "from app.modules.mod.contract import Clean\n",
           "modules/mod/adapters/docs_review.py": "from app.modules.docs.contract import Published\n"}
PORT = "from typing import Protocol\n\nclass Repo(Protocol):\n    def get(self) -> int: ...\n"


def found(tmp_path: Path, app: dict[str, str], tests: dict[str, str]) -> list[Violation]:
    result = build_controllers().rules.check(CheckImports(write(tmp_path / "app", {**APP, **app}), "app", "web",
                                                          write(tmp_path / "tests", {**TESTS, **tests})))
    assert isinstance(result, ImportsChecked)
    return list(result.violations)


@pytest.mark.parametrize("app, tests, rule, fix", [
    ({"kernel/x.py": "from app.platform import sql\n"}, {}, "rules", None),
    ({"kernel/x.py": "import requests\n"}, {}, "libraries", None),
    ({"kernel/x.py": "import socket\n"}, {}, "forbidden", "do what needs socket outside kernel/, and hand kernel/ the "
                                                         "result"),
    ({}, {"modules/docs/domain/test_document.py": f"from {CONTROLLER} import C\n"}, "tiers", None),
    ({}, {"misc/test_x.py": ""}, "tiers", "move it to the folder that mirrors its subject's path in the app"),
    ({}, {"web/conftest.py": f"from {CONTROLLER} import DocumentController\nDocumentController(None)\n"},
     "types-only", None),
    (MODULES, {}, "cycles", None),
    ({"web/routes/docs.py": "from app.modules.docs.contract.results import Published\n"}, {}, "package-only",
     "import from app.modules.docs.contract"),
    ({}, {"modules/docs/application/test_publish.py": "def test_publish():\n    assert True\n"},
     "scenario-coverage", "add a table test whose parameters are given, when, then"),
    ({"kernel/x.py": "x = 1  # why\n"}, {}, "no-comments", "say it in a docstring or a name"),
    ({"modules/docs/application/ports/repo.py": PORT}, {}, "stand-ins", "write FakeRepo under tests/fakes/"),
    ({"kernel/x.py": "def (:\n"}, {}, "syntax", None),
])
def test_a_violation_names_its_rule_and_carries_its_fix(tmp_path, app, tests, rule, fix):
    assert [(v.rule, v.fix) for v in found(tmp_path, app, tests)] == [(rule, fix)]


def test_every_violation_of_a_check_names_a_rule(tmp_path):
    body = ("import pytest\n\n@pytest.mark.parametrize('given, when, then', [(1, 2, Published)])\n"
            "def test_publish(given, when, then):\n    if given:\n        pass\n")
    violations = found(tmp_path, {}, {"modules/docs/application/test_publish.py": body})
    assert {v.rule for v in violations} == {"scenario-coverage"}
    assert [v.fix for v in violations] == [
        "arrange from given, act with when, assert == then, and give the odd case its own test",
        'write pytest.param(..., id="<a sentence stating the outcome>")',
        "add a row whose then is Missing, or a standalone test naming it"]
