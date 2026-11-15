"""The checks of what source files say, wired: on a throwaway web project, each check is run by
`build_controllers().rules.check` on files it reads from disk and reports what it finds. What each check decides is
proven by the unit tests of tests/modules/rules/ on hand-made values; here one case per check shows it is wired."""
import pytest

from tests.bootstrap.project import APP, TABLE, line_of, problems

PUBLISH = "tests/modules/docs/application/test_publish.py"
PORT = "from typing import Protocol\n\n\nclass Repo(Protocol):\n    def get(self) -> int: ...\n"
MOCKED = TABLE + ("from unittest.mock import Mock\n"
                  "from app.modules.docs.application.ports.repo import Repo\n\nMock(spec=Repo)\n")
FIXTURE_MOCKED = TABLE + ("from app.modules.docs.application.ports.repo import Repo\n\n\n"
                          "def test_notify(mocker):\n    mocker.Mock(spec=Repo)\n")
FAKE_REPO = {"fakes/repo.py": "class FakeRepo:\n    def get(self): return 1\n"}
THREE = APP["modules/docs/contract/results.py"].replace("Missing\n", "Missing | Rejected\n")


def test_a_project_following_every_check_passes(tmp_path):
    assert problems(tmp_path) == []


@pytest.mark.parametrize("app, tests, found", [
    pytest.param({}, {"modules/docs/domain/test_document.py": "from app.modules.docs.adapters.db_repo import DbRepo\n"},
                 ["tests/modules/docs/domain/test_document.py:1: a test of domain/ (unit tier) may not import "
                  "adapters/ of modules/docs (app.modules.docs.adapters.db_repo): it imports only what domain/ may "
                  "(parts.domain.may_import)"],
                 id="tiers: a test imports only what the part it mirrors may"),
    pytest.param({}, {"scripts/test_x.py": ""},
                 ["tests/scripts/test_x.py: lies in no tier: no part's folder and no tier's `folder` is mirrored here"],
                 id="tiers: a test in no tier's folder"),
    pytest.param({}, {"web/conftest.py": "from app.modules.docs.application.controller import C\n\nC()\n"},
                 ["tests/web/conftest.py:3: a rendering test uses controller/ of modules/docs only as a type: it "
                  "may not call app.modules.docs.application.controller.C (tiers.rendering.types_only)"],
                 id="types-only: a rendering test calls the controller"),
    pytest.param({"modules/docs/application/controller.py": "def make():\n    ...\n"},
                 {"web/conftest.py": "from app.modules.docs.application.controller import make\n\nmap(make, [])\n"},
                 ["tests/web/conftest.py:3: a rendering test uses controller/ of modules/docs only as a type: it "
                  "may not reference app.modules.docs.application.controller.make, a function "
                  "(tiers.rendering.types_only)"],
                 id="types-only: a rendering test references a function of the controller without calling it"),
    pytest.param({"modules/docs/application/controller.py": "class C: ...\n"},
                 {"web/conftest.py": "from app.modules.docs.application.controller import C\n\nisinstance(1, C)\n"},
                 [], id="types-only: a class of the controller may be referenced"),
    pytest.param({"platform/sql.py": "import requests\n"}, {},
                 ["app/platform/sql.py:1: platform/ may not import the outside package requests (parts.platform.libraries)"],
                 id="libraries: an outside package not listed for the part"),
    pytest.param({"web/routes/docs.py": "from app.modules.docs.contract.results import Published\n"}, {},
                 ["app/web/routes/docs.py:1: contract/ of modules/docs is imported only as a package, never by its "
                  "files (app.modules.docs.contract.results) (package-only)"],
                 id="package-only: a contract imported by its file"),
    pytest.param({"modules/mod/__init__.py": "", "modules/mod/contract/__init__.py": "",
                  "modules/docs/adapters/mod_review.py": "from app.modules.mod.contract import Clean\n",
                  "modules/mod/adapters/docs_review.py": "from app.modules.docs.contract import Published\n"}, {},
                 ["app/modules/docs/adapters/mod_review.py:1: modules/docs → modules/mod → modules/docs import each "
                  "other in a cycle: app/modules/docs/adapters/mod_review.py:1 imports app.modules.mod.contract; "
                  "app/modules/mod/adapters/docs_review.py:1 imports app.modules.docs.contract (cycles)"],
                 id="cycles: two modules import each other"),
    pytest.param({"modules/docs/application/ports/repo.py": PORT}, {},
                 ["app/modules/docs/application/ports/repo.py:4: Repo is a read port with no fake (stand-ins)"],
                 id="stand-ins: a read port with no fake"),
    pytest.param({"modules/docs/application/ports/repo.py": PORT},
                 {"fakes/repo.py": "class FakeRepo:\n    def get(self): return 1\n", "modules/docs/application/test_publish.py": MOCKED},
                 [f"{PUBLISH}:{line_of(MOCKED, 'Mock(spec=Repo)')}: Mock(spec=Repo) stands in for Repo, a read port (stand-ins)"],
                 id="stand-ins: a mock of a read port"),
    pytest.param({"modules/docs/application/ports/repo.py": PORT},
                 {**FAKE_REPO, "modules/docs/application/test_publish.py": FIXTURE_MOCKED},
                 [f"{PUBLISH}:{line_of(FIXTURE_MOCKED, 'mocker.Mock(spec=Repo)')}: mocker.Mock(spec=Repo) stands in "
                  "for Repo, a read port (stand-ins)"],
                 id="stand-ins: a mock a fixture builds, of a read port"),
    pytest.param({"modules/docs/contract/results.py": THREE}, {},
                 [f"{PUBLISH}:{line_of(TABLE, '@pytest.mark.parametrize')}: PublishResult variant Rejected has no row "
                  "in the table and no standalone test naming it (scenario-coverage)"],
                 id="scenario-coverage: a variant with no row, read from the table on disk"),
    pytest.param({}, {"modules/docs/application/test_publish.py": None},
                 ["app/modules/docs/contract/results.py:4: PublishResult has no test file test_publish.py among the "
                  "integration tests of docs (scenario-coverage)"],
                 id="scenario-coverage: a use case with no test file"),
    pytest.param({"modules/docs/domain/document.py": '"""A document."""\nX = 1  # the answer\nimport os  # noqa\n'},
                 {"conftest.py": "# fixtures\n"},
                 ["app/modules/docs/domain/document.py:2: a comment (no-comments)",
                  "tests/conftest.py:1: a comment (no-comments)"],
                 id="no-comments: a comment in the app and the tests, a tool directive left alone"),
    pytest.param({"kernel/bad.py": "def (:\n"}, {}, ["app/kernel/bad.py:1: not valid Python: invalid syntax"],
                 id="a file that does not parse is reported"),
    pytest.param({"examples/modules/docs/domain/x.py": "# x\nfrom app.platform import sql\n",
                  "examples/broken.py": "def (:\n"}, {}, [],
                 id="code in a folder the layout does not hold is never read"),
])
def test_each_check_is_wired(tmp_path, app, tests, found):
    assert problems(tmp_path, app, tests) == found


@pytest.mark.parametrize("where", [
    pytest.param("app/__main__.py", id="a folder in the app whose name ends in .py"),
    pytest.param("tests/modules/docs/domain/test_x.py", id="a folder in the tests whose name ends in .py"),
])
def test_a_folder_named_like_a_source_file_is_not_read_as_one(tmp_path, where):
    (tmp_path / where).mkdir(parents=True)
    assert problems(tmp_path) == []
