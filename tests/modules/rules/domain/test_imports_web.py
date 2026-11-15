"""The section 5 rules under the web profile: web/ (routes, i18n, ui) is the entry point instead of cli/.

Ported from project-manager's tests/architecture/test_import_rules.py, which follows the original doc.
"""
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_controllers
from xarch.modules.rules.contract import CheckImports


def build(root: Path, files: dict[str, str]) -> Path:
    app = root / "app"
    for rel, body in {"__init__.py": "", **files}.items():
        path = app / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    return app


def problems(tmp_path: Path, files: dict[str, str]) -> list[str]:
    app = build(tmp_path, files)
    return [str(v) for v in build_controllers().rules.check(CheckImports(app, "app", "web")).violations]


STRUCTURE = {"modules/__init__.py": "", "modules/a/__init__.py": "", "modules/b/__init__.py": "",
             "modules/a/application/__init__.py": "", "modules/b/application/__init__.py": ""}


def test_a_conforming_tree_passes(tmp_path):
    files = {
        **STRUCTURE,
        "kernel/errors.py": "import dataclasses",
        "platform/sql.py": "from app.kernel import errors",
        "modules/a/domain/values.py": "from app.kernel import errors",
        "modules/a/domain/doc.py": "from .values import X\nfrom app.kernel.errors import E",
        "modules/a/contract/__init__.py": "from ..domain.values import X\nfrom app.kernel import errors",
        "modules/a/application/ports/repo.py": "from app.modules.a.domain.doc import Doc\nfrom app.kernel import errors",
        "modules/a/application/services/svc.py": "from ..ports.repo import Repo\nfrom ...domain import doc",
        "modules/a/application/controller.py": "from .services.svc import Svc\nfrom ..contract import X",
        "modules/a/adapters/repo.py": "from app.platform.sql import S\nfrom ..application.ports.repo import Repo\nfrom app.modules.b.contract import Y",
        "modules/b/contract/__init__.py": "",
        "web/routes/a.py": "from app.modules.a.application.controller import C\nfrom app.modules.a.contract import X",
        "bootstrap/app.py": "from app.modules.a.adapters.repo import R\nfrom app.web.routes import a",
    }
    assert problems(tmp_path, files) == []


@pytest.mark.parametrize("path, body", [
    ("kernel/x.py", "from app.platform import sql"),
    ("modules/a/domain/x.py", "from app.modules.b.domain import y"),
    ("modules/a/domain/x.py", "from app.platform import sql"),
    ("modules/a/domain/x.py", "from ..application.services import svc"),
    ("modules/a/contract/__init__.py", "from ..domain import doc"),
    ("modules/a/contract/__init__.py", "from ..application.ports import repo"),
    ("modules/a/application/services/svc.py", "from ...adapters import repo"),
    ("modules/a/application/services/svc.py", "from app.modules.b.contract import Y"),
    ("modules/a/application/services/svc.py", "from ..controller import C"),
    ("modules/a/application/controller.py", "from app.modules.b.application.controller import C"),
    ("modules/a/application/controller.py", "from app.platform import sql"),
    ("modules/a/application/ports/repo.py", "from ...adapters import repo"),
    ("modules/a/application/ports/repo.py", "from ...contract import X"),
    ("modules/a/application/ports/repo.py", "from app.modules.b.contract import Y"),
    ("modules/a/adapters/repo.py", "from app.modules.b.application.controller import C"),
    ("modules/a/adapters/repo.py", "from app.modules.b.domain import d"),
    ("modules/a/adapters/repo.py", "from app.web import routes"),
    ("platform/sql.py", "from app.modules.a.contract import X"),
    ("web/routes/a.py", "from app.modules.a.application.services import svc"),
    ("web/routes/a.py", "from app.modules.a.domain import doc"),
    ("web/routes/a.py", "from app.modules.a.adapters import repo"),
    ("web/routes/a.py", "from app.platform import sql"),
])
def test_a_forbidden_import_is_reported_as_a_dependency_rule(tmp_path, path, body):
    result = problems(tmp_path, {**STRUCTURE, path: body})
    assert len(result) == 1 and path in result[0]
    assert " may not import " in result[0] and "layout" not in result[0]


def test_violations_name_the_web_folder(tmp_path):
    assert problems(tmp_path / "one", {**STRUCTURE, "web/routes/a.py": "from app.platform import sql"}) == [
        "app/web/routes/a.py:1: web/ may not import platform/ (app.platform)"]
    assert problems(tmp_path / "two", {**STRUCTURE, "modules/a/adapters/repo.py": "from app.web import routes"}) == [
        "app/modules/a/adapters/repo.py:1: adapters/ of modules/a may not import web/ (app.web)"]


@pytest.mark.parametrize("path", ["web/i18n/en.py", "web/ui/pages/home.py", "web/ui/primitives/button.py"])
def test_every_part_of_web_is_the_entry_point(tmp_path, path):
    assert problems(tmp_path / "ok", {**STRUCTURE, path: "from app.modules.a.contract import X\nfrom app.web.routes import a"}) == []
    assert len(problems(tmp_path / "bad", {**STRUCTURE, path: "from app.modules.a.domain import doc"})) == 1


def test_a_cli_folder_is_just_an_extra_under_web(tmp_path):
    assert problems(tmp_path, {**STRUCTURE, "cli/commands/a.py": "from app.platform import sql"}) == []
