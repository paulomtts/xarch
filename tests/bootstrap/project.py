"""A throwaway web project for the wired checks: an app and its tests that follow every check, and the violations
the check of its source finds once files are added, replaced or (None) removed."""
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest

from xarch.bootstrap.wiring import build_controllers
from xarch.modules.rules.contract import AppChecked, CheckApp
from xarch.modules.spec.application.logic import key_lookup
from xarch.modules.spec.contract import CheckProfile, Explain, KeyExplained, ProfileChecked

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


PURE = ("datetime.datetime.now", "datetime.datetime.utcnow", "datetime.datetime.today", "datetime.date.today",
        "time.time", "time.time_ns", "time.monotonic", "time.perf_counter", "builtins.open", "builtins.print",
        "builtins.input", "sys.stdin", "sys.stdout", "sys.stderr", "os.environ", "os.getenv", "socket", "subprocess",
        "sqlite3", "urllib", "http", "shutil", "pathlib.Path.cwd", "pathlib.Path.absolute", "os.getcwd",
        "os.path.abspath", "os.path.realpath", "pathlib.Path.resolve", "pathlib.Path.home", "pathlib.Path.expanduser",
        "os.path.expanduser", "os.getcwdb", "os.chdir")
"""The names the bundled profiles' list `pure` holds, in the order it writes them."""


def write(root: Path, files: dict[str, str]) -> Path:
    for rel, body in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(body)
    return root


def problems(tmp_path: Path, app: dict[str, str | None] | None = None,
             tests: dict[str, str | None] | None = None, profile: str = "web") -> list[str]:
    app_files = {k: v for k, v in {**APP, **(app or {})}.items() if v is not None}
    test_files = {k: v for k, v in {**TESTS, **(tests or {})}.items() if v is not None}
    result = source_check(write(tmp_path / "app", app_files), profile, write(tmp_path / "tests", test_files))
    return [str(v) for v in result.violations]


LAYOUT = ("structure", "test-tree")
"""The ids of what layout finds of the folders, which `xarch check` adds to what the source says."""


def app_check(root: Path, profile: str, tests: Path | None = None) -> AppChecked:
    """What `xarch check` finds below root, the app, imported as the package its folder names, and below tests: the
    violations, in order of file, line and rule, and the state of the enforcement."""
    result = build_controllers().rules.check_app(CheckApp(root, profile, root.parent, tests))
    assert isinstance(result, AppChecked), result
    return result


def source_check(root: Path, profile: str, tests: Path | None = None) -> AppChecked:
    """What app_check finds, without what layout finds of the folders."""
    result = app_check(root, profile, tests)
    return replace(result, violations=tuple(v for v in result.violations if v.rule not in LAYOUT))


def line_of(text: str, marker: str) -> int:
    """The line of text that holds marker, counted from 1."""
    return next(n for n, line in enumerate(text.splitlines(), 1) if marker in line)


def bundled_profiles() -> tuple[str, ...]:
    """The names of the profiles xarch ships, as `based_on` may name them."""
    found = build_controllers().spec.explain(Explain("based_on"))
    assert isinstance(found, KeyExplained)
    return found.choices


def example_problems(location: str | Path) -> tuple[str, ...]:
    """What `profile check` finds wrong with the examples of the profile at location, which loads."""
    checked = build_controllers().spec.check_profile(CheckProfile(Path("app"), str(location)))
    assert isinstance(checked, ProfileChecked) and all(p.check == "examples" for p in checked.problems), checked
    return tuple(problem.text for problem in checked.problems)


def retiring(monkeypatch: pytest.MonkeyPatch, scope: str, name: str, text: str) -> None:
    """The table of retired names holds one entry, (scope, name, text), for this test alone: a record with the fields
    the lookup reads, since a wired test builds no value of domain/ itself."""
    monkeypatch.setattr(key_lookup, "RETIRED", (SimpleNamespace(scope=scope, name=name, text=text, value=""),))
