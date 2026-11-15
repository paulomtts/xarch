"""A throwaway web project for the wired checks: an app and its tests that follow every check, and the violations
`build_controllers().rules.check` finds once files are added, replaced or (None) removed."""
from pathlib import Path

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


def line_of(text: str, marker: str) -> int:
    """The line of text that holds marker, counted from 1."""
    return next(n for n, line in enumerate(text.splitlines(), 1) if marker in line)
