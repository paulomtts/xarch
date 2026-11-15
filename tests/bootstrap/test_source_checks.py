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

TABLE = '''"""Use case: publish a document."""
import pytest

from app.modules.docs.application.controller import DocumentController
from app.modules.docs.contract import Missing, Published
from app.modules.docs.domain.document import Document
from tests.fakes.repo import FakeRepo
from tests.modules.docs.builders import a_document


@pytest.mark.parametrize("given, when, then", [
    pytest.param([a_document()], PublishDocument(A_ID), Published(DocumentView(A_ID, "Hello")),
                 id="a document with a title is published"),
    pytest.param([], PublishDocument(A_ID), Missing(), id="a document that does not exist is missing"),
])
def test_publish(given, when, then):
    assert DocumentController(FakeRepo(given)).publish(when) == then
'''

TESTS = {
    "fakes/repo.py": "from app.modules.docs.application.ports.repo import Repo\n",
    "modules/docs/builders.py": "from app.modules.docs.domain.document import Document\n",
    "modules/docs/application/test_publish.py": TABLE,
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
     "tests/modules/docs/domain/test_document.py:1: a test of domain/ (unit tier) may not import controller/ of "
     "modules/docs (app.modules.docs.application.controller): it imports only what domain/ may (rules.domain)"),
    ("modules/docs/domain/test_document.py", "from app.modules.other.domain.x import X\n",
     "tests/modules/docs/domain/test_document.py:1: a test of domain/ (unit tier) may not import domain/ of modules/other "
     "(app.modules.other.domain.x): it imports only what domain/ may (rules.domain)"),
    ("web/test_docs.py", "from app.modules.docs.application.services import s\n",
     "tests/web/test_docs.py:1: a test of web/ (rendering tier) may not import services/ of modules/docs "
     "(app.modules.docs.application.services): it imports only what web/ may (rules.web)"),
    ("architecture/test_rules.py", "from app.kernel import k\n",
     "tests/architecture/test_rules.py:1: a guard test may not import kernel/ (app.kernel)"),
    ("web/conftest.py", "from app.platform import sql\n",
     "tests/web/conftest.py:1: a test of web/ (rendering tier) may not import platform/ (app.platform): it imports only "
     "what web/ may (rules.web)"),
])
def test_a_test_imports_only_what_its_tier_may_touch(tmp_path, path, body, problem):
    assert problems(tmp_path, tests={path: body}) == [problem]


@pytest.mark.parametrize("path, body, problem", [
    ("modules/docs/domain/test_document.py", "from app.modules.docs.adapters.db_repo import DbRepo\n",
     "tests/modules/docs/domain/test_document.py:1: a test of domain/ (unit tier) may not import adapters/ of "
     "modules/docs (app.modules.docs.adapters.db_repo): it imports only what domain/ may (rules.domain)"),
    ("modules/docs/domain/test_document.py", "from app.platform import sql\n",
     "tests/modules/docs/domain/test_document.py:1: a test of domain/ (unit tier) may not import platform/ "
     "(app.platform): it imports only what domain/ may (rules.domain)"),
    ("modules/docs/adapters/test_db_repo.py", "from app.platform import sql\nfrom app.modules.docs.domain import d\n",
     None),
    ("modules/docs/application/test_publish.py",
     TABLE + "from app.modules.docs.application.services import s\nfrom app.kernel import k\n", None),
    ("modules/docs/application/test_publish.py", TABLE + "from app.modules.docs.adapters.db_repo import DbRepo\n",
     "tests/modules/docs/application/test_publish.py:18: a test of controller/ (integration tier) may not import "
     "adapters/ of modules/docs (app.modules.docs.adapters.db_repo): it imports only what controller/ may "
     "(rules.controller)"),
    ("modules/docs/application/services/test_steps.py",
     "from app.modules.docs.application.controller import DocumentController\n",
     "tests/modules/docs/application/services/test_steps.py:1: a test of services/ (integration tier) may not import "
     "controller/ of modules/docs (app.modules.docs.application.controller): it imports only what services/ may "
     "(rules.services)"),
])
def test_a_test_imports_only_what_the_part_it_mirrors_may_import(tmp_path, path, body, problem):
    """Not the union of its tier: a domain test may not import the adapters, though the unit tier also tests them."""
    app = {"modules/docs/application/services/__init__.py": ""}
    assert problems(tmp_path, app, {path: body}) == ([problem] if problem else [])


CONTROLLER = "app.modules.docs.application.controller"


@pytest.mark.parametrize("body, line, called", [
    (f"from {CONTROLLER} import DocumentController\n\nDocumentController(None)\n", 3, "DocumentController"),
    (f"from {CONTROLLER} import DocumentController as C\n\ndef test_x():\n    C()\n", 4, "DocumentController"),
    ("from app.modules.docs.application import controller\ncontroller.DocumentController()\n", 2,
     "DocumentController"),
    (f"import {CONTROLLER} as c\nc.DocumentController.build()\n", 2, "DocumentController.build"),
    (f"import {CONTROLLER}\n{CONTROLLER}.DocumentController()\n", 2, "DocumentController"),
])
def test_a_rendering_test_may_not_call_the_controller(tmp_path, body, line, called):
    assert problems(tmp_path, tests={"web/conftest.py": body}) == [
        f"tests/web/conftest.py:{line}: a rendering test uses controller/ of modules/docs only as a type: it may not "
        f"call {CONTROLLER}.{called} (tiers.rendering.types_only)"]


def test_a_rendering_test_may_name_the_controller_as_a_type_and_call_what_it_is_given(tmp_path):
    body = (f"from {CONTROLLER} import DocumentController\nfrom unittest.mock import Mock\n\n"
            "def build(controller: DocumentController):\n    return controller.publish(1)\n\n"
            "def test_x():\n    build(Mock(spec=DocumentController))\n    isinstance(1, DocumentController)\n")
    assert problems(tmp_path, tests={"web/test_docs.py": body}) == []


PORTS = "modules/docs/application/ports/"
PROTOCOL = "from typing import Protocol\n\n"


def port_problems(tmp_path: Path, ports: dict[str, str], tests: dict[str, str] | None = None) -> list[str]:
    return problems(tmp_path, {PORTS + name: PROTOCOL + body for name, body in ports.items()}, tests)


def test_a_port_is_fire_only_or_read_and_every_read_port_has_a_fake(tmp_path):
    ports = {"repo.py": "class Repo(Protocol):\n    def get(self, id: int) -> str | None: ...\n"
                        "    def __len__(self) -> int: ...\n",
             "notifier.py": "class Notifier(Protocol):\n    def send(self, text: str) -> None: ...\n"
                            "    async def flush(self) -> None: ...\n",
             "values.py": "class Allowed:\n    def why(self): ...\n\nclass Empty(Protocol):\n    size: int\n"}
    fakes = {"fakes/repo.py": "class FakeRepo:\n    def get(self, id): return None\n"}
    assert port_problems(tmp_path, ports, fakes) == []


def test_a_read_port_with_no_fake_is_reported(tmp_path):
    assert port_problems(tmp_path, {"repo.py": "class Repo(Protocol):\n    def get(self) -> int: ...\n"}) == [
        "app/modules/docs/application/ports/repo.py:3: Repo is a read port with no fake: write FakeRepo under "
        "tests/fakes/ (stand-ins)"]


def test_a_port_with_any_method_that_returns_a_value_is_a_read_port_and_needs_a_fake(tmp_path):
    body = ("class Repo(Protocol):\n    def get(self, id: int) -> str | None: ...\n"
            "    def save(self, text: str) -> None: ...\n")
    assert port_problems(tmp_path, {"repo.py": body}, {"fakes/repo.py": "class FakeRepo: ...\n"}) == []
    assert port_problems(tmp_path, {"repo.py": body}) == [
        "app/modules/docs/application/ports/repo.py:3: Repo is a read port with no fake: write FakeRepo under "
        "tests/fakes/ (stand-ins)"]


def test_a_port_method_with_no_return_annotation_is_reported(tmp_path):
    body = "class Repo(Protocol):\n    def get(self, id): ...\n    def __call__(self): ...\n"
    assert port_problems(tmp_path, {"repo.py": body}) == [
        "app/modules/docs/application/ports/repo.py:4: Repo.get has no return annotation: annotate it, since whether "
        "Repo is fire-only or read follows from it (stand-ins)",
        "app/modules/docs/application/ports/repo.py:5: Repo.__call__ has no return annotation: annotate it, since "
        "whether Repo is fire-only or read follows from it (stand-ins)"]


NOTIFIER = {"notifier.py": "class Notifier(Protocol):\n    def send(self, text: str) -> None: ...\n",
            "repo.py": "class Repo(Protocol):\n    def get(self) -> int: ...\n"}
FAKES = {"fakes/repo.py": "class FakeRepo: ...\n"}
MOCKED = TABLE + ("from unittest.mock import Mock, MagicMock as Magic, create_autospec\n"
                   "from unittest import mock\n"
                   "from app.modules.docs.application.ports.notifier import Notifier\n"
                   "from app.modules.docs.application.ports.repo import Repo\n"
                   "import app.modules.docs.application.ports.repo as repos\n\n")


@pytest.mark.parametrize("calls, problem", [
    ("Mock(Notifier)\nMock(spec=Notifier)\nMagic(spec_set=Notifier)\ncreate_autospec(Notifier)\n"
     "mock.AsyncMock(spec=Notifier)\nMock(spec=Other)\nMock(spec=some_var)\nMock(**options)\n", None),
    ("Mock()\n", "24: Mock() names nothing it stands in for: give it a spec, such as Mock(spec=<port>) (stand-ins)"),
    ("Magic(return_value=3)\n",
     "24: MagicMock() names nothing it stands in for: give it a spec, such as Mock(spec=<port>) (stand-ins)"),
    ("mock.create_autospec()\n",
     "24: create_autospec() names nothing it stands in for: give it a spec, such as Mock(spec=<port>) (stand-ins)"),
    ("Mock(spec=Repo)\n", "24: Mock(spec=Repo) stands in for Repo, a read port: use its fake FakeRepo (stand-ins)"),
    ("create_autospec(repos.Repo)\n",
     "24: create_autospec(Repo) stands in for Repo, a read port: use its fake FakeRepo (stand-ins)"),
])
def test_a_mock_in_a_test_of_the_ports_names_a_fire_only_port(tmp_path, calls, problem):
    found = port_problems(tmp_path, NOTIFIER, {**FAKES, "modules/docs/application/test_publish.py": MOCKED + calls})
    assert found == ([f"tests/modules/docs/application/test_publish.py:{problem}"] if problem else [])


def test_a_mock_of_a_port_that_is_written_and_read_back_is_reported(tmp_path):
    ports = {"repo.py": "class Repo(Protocol):\n    def get(self) -> int: ...\n    def save(self, n: int) -> None: ...\n"}
    found = port_problems(tmp_path, ports, {**FAKES, "modules/docs/application/test_publish.py":
                                            MOCKED.replace("notifier import Notifier", "repo import Repo") + "Mock(spec=Repo)\n"})
    assert found == ["tests/modules/docs/application/test_publish.py:24: Mock(spec=Repo) stands in for Repo, a read "
                     "port: use its fake FakeRepo (stand-ins)"]


def test_a_mock_outside_the_tier_that_tests_the_ports_is_not_this_checks_business(tmp_path):
    tests = {**FAKES, "web/test_docs.py": "from unittest.mock import Mock\nMock(publish=lambda cmd: cmd)\n"}
    assert port_problems(tmp_path, NOTIFIER, tests) == []


MODULES = {"modules/mod/__init__.py": "", "modules/mod/contract/__init__.py": "",
           "modules/mod/adapters/docs_review.py": "", "modules/pub/__init__.py": "",
           "modules/pub/contract/__init__.py": "", "modules/pub/adapters/mod_review.py": ""}


def test_modules_that_import_each_other_one_way_pass(tmp_path):
    app = {**MODULES, "modules/docs/adapters/mod_review.py": "from app.modules.mod.contract import Clean\n",
           "modules/mod/adapters/pub_review.py": "from app.modules.pub.contract import Out\n"}
    assert problems(tmp_path, app) == []


def test_two_modules_that_import_each_other_are_a_cycle_reported_once(tmp_path):
    app = {**MODULES,
           "modules/docs/adapters/mod_review.py": "from app.modules.mod.contract import Clean\n"
                                                  "from app.modules.mod.contract import Flagged\n",
           "modules/mod/adapters/docs_review.py": "import os\nfrom app.modules.docs.contract import Published\n"}
    assert problems(tmp_path, app) == [
        "app/modules/docs/adapters/mod_review.py:1: modules/docs → modules/mod → modules/docs import each other in a "
        "cycle: app/modules/docs/adapters/mod_review.py:1 imports app.modules.mod.contract; "
        "app/modules/mod/adapters/docs_review.py:2 imports app.modules.docs.contract (cycles)"]


def test_every_cycle_is_reported_with_its_modules_in_order(tmp_path):
    app = {**MODULES,
           "modules/docs/adapters/mod_review.py": "from app.modules.mod.contract import Clean\n",
           "modules/mod/adapters/pub_review.py": "from ...pub.contract import Out\n",
           "modules/pub/adapters/mod_review.py": "from app.modules.docs.contract import Published\n"
                                                 "from app.modules.mod.contract import Clean\n"}
    assert problems(tmp_path, app) == [
        "app/modules/docs/adapters/mod_review.py:1: modules/docs → modules/mod → modules/pub → modules/docs import "
        "each other in a cycle: app/modules/docs/adapters/mod_review.py:1 imports app.modules.mod.contract; "
        "app/modules/mod/adapters/pub_review.py:1 imports app.modules.pub.contract; "
        "app/modules/pub/adapters/mod_review.py:1 imports app.modules.docs.contract (cycles)",
        "app/modules/mod/adapters/pub_review.py:1: modules/mod → modules/pub → modules/mod import each other in a "
        "cycle: app/modules/mod/adapters/pub_review.py:1 imports app.modules.pub.contract; "
        "app/modules/pub/adapters/mod_review.py:2 imports app.modules.mod.contract (cycles)"]


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


def scenario_problems(tmp_path: Path, body: str | None, results: str | None = None) -> list[str]:
    app = {"modules/docs/contract/results.py": results} if results else {}
    return problems(tmp_path, app, {"modules/docs/application/test_publish.py": body})


THREE = APP["modules/docs/contract/results.py"].replace("Missing\n", "Missing | Rejected\n")
AT = "tests/modules/docs/application/test_publish.py"
ROW = 'pytest.param([], PublishDocument(A_ID), Rejected("no"), id="a document without a title is rejected"),\n    '


def test_a_variant_without_a_row_is_reported_at_the_table(tmp_path):
    assert scenario_problems(tmp_path, TABLE, THREE) == [
        f"{AT}:11: PublishResult variant Rejected has no row in the table and no standalone test naming it "
        "(scenario-coverage)"]


def test_a_variant_with_a_row_is_covered_however_the_then_value_is_written(tmp_path):
    body = TABLE.replace("Missing()", "contract.Missing()").replace(
        "])\ndef", ROW.replace("Rejected(\"no\")", "Rejected") + "])\ndef")
    assert scenario_problems(tmp_path, body, THREE) == []


def test_a_standalone_test_naming_a_variant_stands_for_its_row(tmp_path):
    body = TABLE + "\n\ndef test_a_rejected_review_is_rejected():\n    assert Rejected(\"no\")\n"
    assert scenario_problems(tmp_path, body, THREE) == []


def test_a_table_test_naming_a_variant_in_its_body_is_no_standalone_test(tmp_path):
    body = TABLE.replace("== then", "== then or Rejected()")
    assert scenario_problems(tmp_path, body, THREE) == [
        f"{AT}:11: PublishResult variant Rejected has no row in the table and no standalone test naming it "
        "(scenario-coverage)"]


def test_a_row_without_an_id_is_reported(tmp_path):
    body = TABLE.replace(', id="a document that does not exist is missing"', "")
    assert scenario_problems(tmp_path, body) == [
        f"{AT}:14: row has no id: write pytest.param(..., id=\"<a sentence stating the outcome>\") (scenario-coverage)"]


@pytest.mark.parametrize("id", ['id=""', 'id="  "', "id=NAME", 'id=f"a {x}"'])
def test_an_id_that_is_not_a_non_empty_string_literal_is_reported(tmp_path, id):
    body = TABLE.replace('id="a document that does not exist is missing"', id)
    assert scenario_problems(tmp_path, body) == [
        f"{AT}:14: row has no id: write pytest.param(..., id=\"<a sentence stating the outcome>\") (scenario-coverage)"]


def test_a_bare_tuple_row_is_reported(tmp_path):
    body = TABLE.replace('pytest.param([], PublishDocument(A_ID), Missing(), id="a document that does not exist is missing")',
                         "([], PublishDocument(A_ID), Missing())")
    assert scenario_problems(tmp_path, body) == [
        f"{AT}:14: row is not a pytest.param(...): write pytest.param(..., id=\"<a sentence stating the outcome>\") "
        "(scenario-coverage)"]


def test_a_row_whose_then_names_no_variant_of_the_union_is_reported(tmp_path):
    body = TABLE.replace("Missing()", "Gone()")
    assert scenario_problems(tmp_path, body) == [
        f"{AT}:14: row 'a document that does not exist is missing' has Gone in its then column, which is not a "
        "variant of PublishResult (scenario-coverage)",
        f"{AT}:11: PublishResult variant Missing has no row in the table and no standalone test naming it "
        "(scenario-coverage)"]


def test_a_row_whose_then_is_no_name_is_reported(tmp_path):
    body = TABLE.replace("Missing()", "[]")
    assert scenario_problems(tmp_path, body)[0] == (
        f"{AT}:14: row 'a document that does not exist is missing' names no variant in its then column: use one of "
        "Published, Missing (scenario-coverage)")


@pytest.mark.parametrize("statement, keyword", [
    ("if given:\n        given = []", "if"), ("for item in given:\n        pass", "for"),
    ("while given:\n        break", "while"), ("try:\n        pass\n    except ValueError:\n        pass", "try"),
    ("match given:\n        case _:\n            pass", "match")])
def test_a_branch_in_the_body_of_the_table_test_is_reported(tmp_path, statement, keyword):
    body = TABLE.replace("    assert", f"    {statement}\n    assert")
    assert scenario_problems(tmp_path, body) == [
        f"{AT}:17: test_publish has {'an' if keyword == 'if' else 'a'} `{keyword}` in its body: arrange from given, "
        "act with when, assert == then, and give the odd case its own test (scenario-coverage)"]


def test_a_file_with_no_table_is_reported(tmp_path):
    body = '"""Use case: publish a document."""\n\n\ndef test_a_document_is_published():\n    assert Published()\n    assert Missing()\n'
    assert scenario_problems(tmp_path, body) == [
        f"{AT}:1: no table test: add a parametrized test whose parameters are given, when, then (scenario-coverage)"]


def test_a_table_is_found_by_the_column_names_of_the_profile(tmp_path):
    body = TABLE.replace('"given, when, then"', '"state, command, result"')
    assert scenario_problems(tmp_path, body) == [
        f"{AT}:1: no table test: add a parametrized test whose parameters are given, when, then (scenario-coverage)"]


def test_the_columns_may_be_a_sequence_of_names(tmp_path):
    body = TABLE.replace('"given, when, then"', '["given", "when", "then"]')
    assert scenario_problems(tmp_path, body) == []


def test_the_rows_may_be_a_module_level_list_named_by_the_decorator(tmp_path):
    rows = TABLE.split("pytest.mark.parametrize(\"given, when, then\", ")[1].split(")\ndef")[0]
    body = TABLE.replace(rows, "CASES").replace("@pytest", f"CASES = {rows}\n\n\n@pytest", 1)
    assert scenario_problems(tmp_path, body) == []


def test_rows_that_are_not_a_literal_are_reported_since_they_cannot_be_read(tmp_path):
    body = TABLE.replace("""[
    pytest.param([a_document()]""", "load() + [\n    pytest.param([a_document()]")
    assert scenario_problems(tmp_path, body) == [
        f"{AT}:11: the rows of the table cannot be read: write them as a list, or as the name of a list assigned at "
        "the top of the file (scenario-coverage)"]


def test_a_use_case_without_its_test_file_is_reported(tmp_path):
    assert scenario_problems(tmp_path, None) == [
        "app/modules/docs/contract/results.py:4: PublishResult has no test file test_publish.py among the "
        "integration tests of docs (scenario-coverage)"]


def test_a_use_case_named_in_camel_case_has_a_snake_case_test_file(tmp_path):
    results = APP["modules/docs/contract/results.py"].replace("PublishResult", "MarkReadResult")
    tests = {"modules/docs/application/test_publish.py": None,
             "modules/docs/application/test_mark_read.py": TABLE}
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
