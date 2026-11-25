"""The checks of what source files say, wired: on a throwaway web project, each check is run by the check of the app
(`build_controllers().rules.check_app`) on files it reads from disk and reports what it finds. What each check decides is
proven by the unit tests of tests/modules/rules/ on hand-made values; here one case per check shows it is wired."""
import pytest

from tests.bootstrap.project import APP, TABLE, TESTS, line_of, problems, source_check, write

PUBLISH = "tests/modules/docs/application/test_publish.py"
PORT = "from typing import Protocol\n\n\nclass Repo(Protocol):\n    def get(self) -> int: ...\n"
THREE = APP["modules/docs/contract/results.py"].replace("Missing\n", "Missing | Rejected\n")
LONE = "from app.modules.docs.application.ports.repo import Repo\n\n\ndef size(repo: Repo):\n    return 1\n"


def test_a_project_following_every_check_passes(tmp_path):
    assert problems(tmp_path) == []


@pytest.mark.parametrize("app, tests, found", [
    pytest.param({}, {"modules/docs/domain/test_document.py": "from app.modules.docs.adapters.db_repo import DbRepo\n"},
                 ["tests/modules/docs/domain/test_document.py:1: a test of domain/ (unit tier) may not import "
                  "adapters/ of modules/docs (app.modules.docs.adapters.db_repo): it imports only what domain/ may "
                  "(parts.domain.imports.may)"],
                 id="tiers: a test imports only what the part it mirrors may"),
    pytest.param({}, {"scripts/test_x.py": ""},
                 ["tests/scripts/test_x.py: lies in no tier: no part's folder and no tier's `folder` is mirrored here"],
                 id="tiers: a test in no tier's folder"),
    pytest.param({}, {"web/conftest.py": "from app.modules.docs.application.controller import C\n\nC()\n"},
                 ["tests/web/conftest.py:3: a rendering test uses controller/ of modules/docs only as a type: it "
                  "may not call app.modules.docs.application.controller.C (tiers.rendering.imports.types_only)"],
                 id="types-only: a rendering test calls the controller"),
    pytest.param({"platform/sql.py": "import requests\n"}, {},
                 ["app/platform/sql.py:1: platform/ may not import the outside package requests (parts.platform.imports.libraries)"],
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
    pytest.param({"modules/docs/contract/results.py": THREE}, {},
                 [f"{PUBLISH}:{line_of(TABLE, '@pytest.mark.parametrize')}: PublishResult variant Rejected has no row "
                  "in the table and no standalone test naming it (scenario-coverage)"],
                 id="scenario-coverage: a variant with no row, read from the table on disk"),
    pytest.param({"modules/docs/domain/document.py": '"""A document."""\nX = 1  # the answer\nimport os  # noqa\n'},
                 {"conftest.py": "# fixtures\n"},
                 ["app/modules/docs/domain/document.py:2: a comment (no-comments)",
                  "tests/conftest.py:1: a comment (no-comments)"],
                 id="no-comments: a comment in the app and the tests, a tool directive left alone"),
    pytest.param({"modules/docs/adapters/lone.py": LONE}, {},
                 ["app/modules/docs/adapters/lone.py: adapters/ of modules/docs imports nothing from platform/ or "
                  "contract/ and no outside package, though each of its files must (parts.adapters.imports.must)"],
                 id="must-import: a file of the adapters that imports none of its targets"),
    pytest.param({"kernel/bad.py": "def (:\n"}, {}, ["app/kernel/bad.py:1: not valid Python: invalid syntax"],
                 id="a file that does not parse is reported"),
    pytest.param({"examples/modules/docs/domain/x.py": "# x\nfrom app.platform import sql\n",
                  "examples/broken.py": "def (:\n"}, {},
                 ["app/examples/broken.py: lies in no part and no folder of the layout (closed-tree)",
                  "app/examples/modules/docs/domain/x.py: lies in no part and no folder of the layout (closed-tree)"],
                 id="code in a folder the layout does not hold is never read, only reported by closed-tree"),
])
def test_each_check_is_wired(tmp_path, app, tests, found):
    assert problems(tmp_path, app, tests) == found


def test_a_file_that_is_not_utf_8_is_reported_as_not_read_in_the_app_and_the_tests(tmp_path):
    app, tests = write(tmp_path / "app", APP), write(tmp_path / "tests", TESTS)
    (app / "kernel" / "latin.py").write_bytes(b"\xff\xfe\x00import os\n")
    (tests / "kernel").mkdir()
    (tests / "kernel" / "test_latin.py").write_bytes(b"x = '\xe9'\n")
    assert [str(v) for v in source_check(app, "web", tests).violations] == [
        "app/kernel/latin.py: not UTF-8 text (byte 0xff at offset 0 cannot be decoded), so no check reads it",
        "tests/kernel/test_latin.py: not UTF-8 text (byte 0xe9 at offset 5 cannot be decoded), so no check reads it"]


def test_a_file_that_cannot_be_read_is_reported_as_not_read(tmp_path):
    app, tests = write(tmp_path / "app", APP), write(tmp_path / "tests", TESTS)
    locked = app / "kernel" / "locked.py"
    locked.write_text("import os\n")
    locked.chmod(0)
    assert [str(v) for v in source_check(app, "web", tests).violations] == [
        "app/kernel/locked.py: cannot be read (Permission denied), so no check reads it"]


@pytest.mark.parametrize("where", [
    pytest.param("app/__main__.py", id="a folder in the app whose name ends in .py"),
    pytest.param("tests/modules/docs/domain/test_x.py", id="a folder in the tests whose name ends in .py"),
])
def test_a_folder_named_like_a_source_file_is_not_read_as_one(tmp_path, where):
    (tmp_path / where).mkdir(parents=True)
    assert problems(tmp_path) == []


COPY = "def copy(a):\n    b = a + 1\n    c = b * 2\n    d = c - 3\n    return d\n"


def test_the_same_function_in_two_places_of_the_app_is_reported_at_the_later_one(tmp_path):
    assert problems(tmp_path, {"kernel/a.py": COPY, "kernel/b.py": COPY.replace("copy", "clone")}) == [
        "app/kernel/b.py:1: clone has the same code as copy at app/kernel/a.py:1, whatever the names (no-duplicates)"]


def test_the_same_function_in_two_tests_or_a_test_and_the_app_is_not_compared(tmp_path):
    assert problems(tmp_path, {"kernel/a.py": COPY}, {"modules/docs/domain/test_a.py": COPY + "\n\n" + COPY.replace(
        "copy", "clone"), "modules/docs/domain/test_b.py": COPY}) == []


def test_a_port_no_service_names_and_a_fake_no_test_names_are_reported(tmp_path):
    notifier = "from typing import Protocol\n\n\nclass Notifier(Protocol):\n    def send(self) -> None: ...\n"
    assert problems(tmp_path, {"modules/docs/application/ports/notifier.py": notifier},
                    {"fakes/notifier.py": "class FakeNotifier:\n    def send(self): ...\n"}) == [
        "app/modules/docs/application/ports/notifier.py:4: Notifier is a port that nothing else in the app names (dead-code)",
        "tests/fakes/notifier.py:1: FakeNotifier is a fake that no test names (dead-code)"]
