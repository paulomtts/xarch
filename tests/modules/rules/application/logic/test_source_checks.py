"""The checks of what source files say, on a throwaway web project: tier imports, test placement, outside
libraries and the guards package-only, scenario-coverage and no-comments. Each has a case that passes and one that
fails."""
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_controllers
from xarch.modules.rules.contract import CheckImports, ImportsChecked

APP = {
    "__init__.py": "",
    "kernel/__init__.py": "",
    "modules/__init__.py": "",
    "modules/docs/__init__.py": "",
    "modules/docs/domain/document.py": '"""A document."""\n',
    "modules/docs/contract/__init__.py": "from app.modules.docs.contract.results import Published, Missing\n",
    "modules/docs/contract/results.py":
        "class Published: ...\nclass Missing: ...\n\nPublishResult = Published | Missing\n",
    "modules/docs/application/controller.py": "from app.modules.docs.contract import PublishResult\n",
    "modules/docs/application/ports/repo.py": "",
    "modules/docs/adapters/db_repo.py": "from app.modules.docs.application.ports.repo import Repo\n",
    "web/routes/docs.py": "from app.modules.docs.contract import Published\n",
}

HEADER = '''"""Use case: publish a document.

Scenario: a document with a title is published
  Given a document   When it is published   Then the Result is Published
Scenario: a document that does not exist is missing
  Given no document  When it is published   Then the Result is Missing("gone")
"""
from app.modules.docs.application.controller import DocumentController
from app.modules.docs.domain.document import Document
from tests.fakes.repo import FakeRepo
from tests.modules.docs.builders import a_document


def test_a_document_with_a_title_is_published(): ...
def test_a_document_that_does_not_exist_is_missing(): ...
'''

TESTS = {
    "fakes/repo.py": "from app.modules.docs.application.ports.repo import Repo\n",
    "modules/docs/builders.py": "from app.modules.docs.domain.document import Document\n",
    "modules/docs/application/test_publish.py": HEADER,
    "modules/docs/domain/test_document.py": "from app.modules.docs.domain.document import Document\n",
    "modules/docs/adapters/test_db_repo.py": "from app.modules.docs.adapters.db_repo import DbRepo\nimport pytest\n",
    "web/test_docs.py": "from app.web.routes.docs import router\nfrom app.modules.docs.contract import Published\n",
    "web/conftest.py": "from app.modules.docs.application.controller import DocumentController\n",
    "architecture/test_rules.py": "from pathlib import Path\n",
    "conftest.py": "",
}


def write(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(body)
    return root


def problems(tmp_path: Path, app: dict[str, str | None] | None = None,
             tests: dict[str, str | None] | None = None, profile: str = "web") -> list[str]:
    app_files = {k: v for k, v in {**APP, **(app or {})}.items() if v is not None}
    test_files = {k: v for k, v in {**TESTS, **(tests or {})}.items() if v is not None}
    result = build_controllers().rules.check(CheckImports(write(tmp_path / "app", app_files), "app", profile,
                                                          write(tmp_path / "tests", test_files)))
    assert isinstance(result, ImportsChecked)
    return [str(v) for v in result.violations]


def test_a_project_following_every_check_passes(tmp_path):
    assert problems(tmp_path) == []


@pytest.mark.parametrize("path, body, problem", [
    ("modules/docs/domain/test_document.py", "from app.modules.docs.application.controller import C\n",
     "tests/modules/docs/domain/test_document.py:1: a unit test may not import controller/ of modules/docs "
     "(app.modules.docs.application.controller)"),
    ("modules/docs/domain/test_document.py", "from app.modules.other.domain.x import X\n",
     "tests/modules/docs/domain/test_document.py:1: a unit test may not import domain/ of modules/other "
     "(app.modules.other.domain.x)"),
    ("web/test_docs.py", "from app.modules.docs.application.services import s\n",
     "tests/web/test_docs.py:1: a rendering test may not import services/ of modules/docs "
     "(app.modules.docs.application.services)"),
    ("architecture/test_rules.py", "from app.kernel import k\n",
     "tests/architecture/test_rules.py:1: a guard test may not import kernel/ (app.kernel)"),
    ("web/conftest.py", "from app.platform import sql\n",
     "tests/web/conftest.py:1: a rendering test may not import platform/ (app.platform)"),
])
def test_a_test_imports_only_what_its_tier_may_touch(tmp_path, path, body, problem):
    assert problems(tmp_path, tests={path: body}) == [problem]


def test_only_a_tier_that_tests_the_ports_may_import_the_fakes(tmp_path):
    assert problems(tmp_path, tests={"modules/docs/domain/test_document.py": "from tests.fakes.repo import FakeRepo\n"}
                    ) == ["tests/modules/docs/domain/test_document.py:1: a unit test may not import the fakes "
                          "(tests.fakes.repo): only a tier that tests ports may"]


def test_a_test_imports_test_code_only_from_its_own_folder(tmp_path):
    tests = {"modules/other/domain/test_x.py": "from tests.modules.docs.builders import a_document\n",
             "modules/other/__init__.py": ""}
    app = {"modules/other/domain/x.py": ""}
    assert problems(tmp_path, app, tests) == [
        "tests/modules/other/domain/test_x.py:1: a test may import test code only from its own folder "
        "tests/modules/other/ (tests.modules.docs.builders)"]


@pytest.mark.parametrize("path", ["modules/docs/test_loose.py", "test_root.py", "scripts/test_x.py"])
def test_a_test_in_no_tier_s_folder_is_reported(tmp_path, path):
    assert problems(tmp_path, tests={path: ""}) == [
        f"tests/{path}: lies in no tier: no part's folder and no tier's example folder is mirrored here; a test "
        "lives in the folder that mirrors its subject's path in the app"]


def test_an_outside_package_not_listed_for_the_part_is_reported(tmp_path):
    app = {"platform/sql.py": "from sqlmodel import SQLModel\nimport requests\n",
           "web/routes/docs.py": "import fastapi\nfrom sqlmodel import select\n"}
    assert problems(tmp_path, app) == [
        "app/platform/sql.py:2: platform/ may not import the outside package requests (libraries.platform)",
        "app/web/routes/docs.py:2: web/ may not import the outside package sqlmodel (libraries.web)"]


def test_tests_may_import_any_outside_package(tmp_path):
    assert problems(tmp_path, tests={"web/test_docs.py": "import requests\nimport fastapi.testclient\n"}) == []


@pytest.mark.parametrize("app, tests, problem", [
    ({"web/routes/docs.py": "from app.modules.docs.contract.results import Published\n"}, {},
     "app/web/routes/docs.py:1: contract/ of modules/docs is imported only as a package: import from "
     "app.modules.docs.contract (app.modules.docs.contract.results) (package-only)"),
    ({"web/routes/docs.py": "from app.modules.docs.contract import results\n"}, {},
     "app/web/routes/docs.py:1: contract/ of modules/docs is imported only as a package: import from "
     "app.modules.docs.contract (app.modules.docs.contract.results) (package-only)"),
    ({}, {"web/test_docs.py": "import app.modules.docs.contract.results\n"},
     "tests/web/test_docs.py:1: contract/ of modules/docs is imported only as a package: import from "
     "app.modules.docs.contract (app.modules.docs.contract.results) (package-only)"),
])
def test_a_package_only_part_is_never_imported_by_its_files_from_outside(tmp_path, app, tests, problem):
    assert problems(tmp_path, app, tests) == [problem]


def test_a_package_only_part_imports_its_own_files(tmp_path):
    app = {"modules/docs/contract/__init__.py": "from .results import Published\n"
                                                "from app.modules.docs.contract.views import V\n",
           "modules/docs/contract/views.py": ""}
    assert problems(tmp_path, app) == []


def scenario_problems(tmp_path: Path, header: str | None, results: str | None = None) -> list[str]:
    app = {"modules/docs/contract/results.py": results} if results else {}
    return problems(tmp_path, app, {"modules/docs/application/test_publish.py": header})


def test_a_variant_without_a_scenario_is_reported(tmp_path):
    results = APP["modules/docs/contract/results.py"].replace("Missing\n", "Missing | Rejected\n")
    assert scenario_problems(tmp_path, HEADER, results) == [
        "tests/modules/docs/application/test_publish.py:1: PublishResult variant Rejected has no scenario "
        "(scenario-coverage)"]


def test_a_scenario_without_a_test_of_its_name_is_reported(tmp_path):
    header = HEADER.replace("def test_a_document_that_does_not_exist_is_missing", "def test_missing")
    assert scenario_problems(tmp_path, header) == [
        "tests/modules/docs/application/test_publish.py:1: scenario 'a document that does not exist is missing' has "
        "no test test_a_document_that_does_not_exist_is_missing (scenario-coverage)"]


def test_a_scenario_naming_no_variant_or_another_is_reported(tmp_path):
    header = HEADER.replace("Then the Result is Published", "Then it is published").replace(
        'Then the Result is Missing("gone")', "Then the Result is Gone")
    assert scenario_problems(tmp_path, header) == [
        "tests/modules/docs/application/test_publish.py:1: PublishResult variant Published has no scenario "
        "(scenario-coverage)",
        "tests/modules/docs/application/test_publish.py:1: PublishResult variant Missing has no scenario "
        "(scenario-coverage)",
        "tests/modules/docs/application/test_publish.py:1: scenario 'a document with a title is published' names no "
        "variant: end it with `Then the Result is <Variant>` (scenario-coverage)",
        "tests/modules/docs/application/test_publish.py:1: scenario 'a document that does not exist is missing' ends "
        "in Gone, which is not a variant of PublishResult (scenario-coverage)"]


def test_a_use_case_without_its_test_file_is_reported(tmp_path):
    assert scenario_problems(tmp_path, None) == [
        "app/modules/docs/contract/results.py:4: PublishResult has no test file test_publish.py among the "
        "integration tests of docs (scenario-coverage)"]


def test_a_use_case_named_in_camel_case_has_a_snake_case_test_file(tmp_path):
    results = APP["modules/docs/contract/results.py"].replace("PublishResult", "MarkReadResult")
    tests = {"modules/docs/application/test_publish.py": None,
             "modules/docs/application/test_mark_read.py": HEADER}
    assert problems(tmp_path, {"modules/docs/contract/results.py": results}, tests) == []


def test_a_comment_in_the_app_or_the_tests_is_reported(tmp_path):
    app = {"modules/docs/domain/document.py": '"""A document."""\nX = 1  # the answer\n# a note\n'}
    tests = {"conftest.py": "# fixtures\n"}
    assert problems(tmp_path, app, tests) == [
        "app/modules/docs/domain/document.py:2: a comment: say it in a docstring or a name (no-comments)",
        "app/modules/docs/domain/document.py:3: a comment: say it in a docstring or a name (no-comments)",
        "tests/conftest.py:1: a comment: say it in a docstring or a name (no-comments)"]


def test_docstrings_strings_and_tool_directives_are_not_comments(tmp_path):
    body = ('#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n"""Has # in it."""\n'
            'X = "# not a comment"  # type: ignore[assignment]\nimport os  # noqa: F401\n'
            'if X:  # pragma: no cover\n    pass\n')
    assert problems(tmp_path, {"modules/docs/domain/document.py": body}) == []


def test_reference_code_in_a_folder_the_layout_does_not_hold_is_never_read(tmp_path):
    app = {"examples/modules/docs/domain/x.py": "# modules/docs/domain/x.py\nfrom app.platform import sql\n",
           "examples/broken.py": "def (:\n"}
    assert problems(tmp_path, app) == []


def test_a_file_that_does_not_parse_is_reported(tmp_path):
    assert problems(tmp_path, {"kernel/bad.py": "def (:\n"}) == ["app/kernel/bad.py:1: not valid Python: invalid syntax"]
