"""Tests for the import rules themselves: each rule of docs/project/architecture.md section 5 on a throwaway tree."""
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_controllers
from xarch.modules.rules.contract import CheckImports


def check(app: Path):
    return list(build_controllers().rules.check(CheckImports(app, "app", "cli")).violations)


def build(root: Path, files: dict[str, str]) -> Path:
    app = root / "app"
    for rel, body in {"__init__.py": "", **files}.items():
        path = app / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    return app


def problems(tmp_path: Path, files: dict[str, str]) -> list[str]:
    return [str(v) for v in check(build(tmp_path, files))]


STRUCTURE = {"modules/__init__.py": "", "modules/a/__init__.py": "", "modules/b/__init__.py": "",
             "modules/a/application/__init__.py": "", "modules/b/application/__init__.py": ""}


def test_a_conforming_tree_passes(tmp_path):
    files = {
        **STRUCTURE,
        "kernel/errors.py": "import dataclasses",
        "kernel/logic/text.py": "from app.kernel import errors",
        "platform/sql.py": "from app.kernel import errors",
        "modules/a/domain/values.py": "from app.kernel import errors",
        "modules/a/domain/doc.py": "from .values import X\nfrom app.kernel.errors import E",
        "modules/a/contract/__init__.py": "from ..domain.values import X\nfrom app.kernel import errors",
        "modules/a/application/ports/repo.py": "from app.modules.a.domain.doc import Doc\nfrom app.kernel import errors",
        "modules/a/application/logic/rule.py": "from app.modules.a.domain.doc import Doc\nfrom app.kernel.logic.text import t\nfrom .other import o",
        "modules/a/application/logic/other.py": "from ...domain import values\nfrom app.kernel import errors",
        "modules/a/application/services/svc.py": "from ..ports.repo import Repo\nfrom ...domain import doc\nfrom ..logic.rule import r",
        "modules/a/application/controller.py": "from .services.svc import Svc\nfrom ..contract import X\nfrom .logic.rule import r",
        "modules/a/adapters/repo.py": "from app.platform.sql import S\nfrom ..application.ports.repo import Repo\nfrom app.modules.b.contract import Y",
        "modules/b/contract/__init__.py": "",
        "cli/commands/a.py": "from app.modules.a.application.controller import C\nfrom app.modules.a.contract import X",
        "bootstrap/app.py": "from app.modules.a.adapters.repo import R\nfrom app.cli.commands import a",
    }
    assert problems(tmp_path, files) == []


@pytest.mark.parametrize("path, body", [
    ("kernel/x.py", "from app.platform import sql"),
    ("kernel/logic/x.py", "from app.modules.a.domain import doc"),
    ("kernel/logic/x.py", "from app.modules.a.application.logic import rule"),
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
    ("modules/a/adapters/repo.py", "from app.cli import commands"),
    ("platform/sql.py", "from app.modules.a.contract import X"),
    ("cli/commands/a.py", "from app.modules.a.application.services import svc"),
    ("cli/commands/a.py", "from app.modules.a.domain import doc"),
    ("cli/commands/a.py", "from app.modules.a.adapters import repo"),
    ("cli/commands/a.py", "from app.platform import sql"),
])
def test_a_forbidden_import_is_reported(tmp_path, path, body):
    result = problems(tmp_path, {**STRUCTURE, path: body})
    assert len(result) == 1 and path in result[0]


LOGIC = "modules/a/application/logic/rule.py"


@pytest.mark.parametrize("body", [
    "from ..services import svc",
    "from ..ports import repo",
    "from ..controller import C",
    "from ...contract import X",
    "from ...adapters import repo",
    "from app.platform import sql",
    "from app.cli.commands import a",
    "from app.modules.b.domain import d",
    "from app.modules.b.application.logic import rule",
    "from app.modules.b.contract import Y",
])
def test_logic_may_import_only_its_own_domain_and_the_kernel(tmp_path, body):
    result = problems(tmp_path, {**STRUCTURE, LOGIC: body})
    assert len(result) == 1 and result[0].startswith(f"app/{LOGIC}:1: logic/ of modules/a may not import"), result


@pytest.mark.parametrize("path", [
    "modules/a/application/services/svc.py",
    "modules/a/application/controller.py",
])
def test_services_and_controller_may_import_their_own_logic(tmp_path, path):
    assert problems(tmp_path, {**STRUCTURE, path: "from app.modules.a.application.logic.rule import r"}) == []


@pytest.mark.parametrize("path", [
    "modules/a/domain/x.py",
    "modules/a/contract/__init__.py",
    "modules/a/application/ports/repo.py",
    "modules/a/adapters/repo.py",
    "modules/a/application/services/svc.py",
    "platform/sql.py",
    "cli/commands/a.py",
])
def test_no_other_part_may_import_logic(tmp_path, path):
    """From services/, which may import its own module's logic, the import is of another module's logic."""
    other = "b" if "/services/" in path else "a"
    result = problems(tmp_path, {**STRUCTURE, path: f"from app.modules.{other}.application.logic.rule import r"})
    assert len(result) == 1 and f"logic/ of modules/{other}" in result[0], result


def test_plain_import_statements_are_checked_too(tmp_path):
    result = problems(tmp_path, {**STRUCTURE, "modules/a/domain/x.py": "import app.platform.sql"})
    assert len(result) == 1


def test_the_standard_library_is_always_allowed_and_an_unlisted_outside_package_never(tmp_path):
    assert problems(tmp_path, {**STRUCTURE, "modules/a/domain/x.py": "import sqlalchemy\nfrom uuid import UUID"}) == [
        "app/modules/a/domain/x.py:1: domain/ of modules/a may not import the outside package sqlalchemy "
        "(libraries.domain)"]


@pytest.mark.parametrize("path, body", [
    ("platform/sql.py", "from sqlmodel import SQLModel"),
    ("modules/a/adapters/repo.py", "import sqlmodel"),
    ("cli/commands/a.py", "from typer import Typer"),
    ("bootstrap/app.py", "import typer\nimport sqlmodel"),
    ("modules/a/domain/x.py", "from __future__ import annotations\nimport sys, json"),
])
def test_a_part_may_import_the_outside_packages_listed_for_it(tmp_path, path, body):
    assert problems(tmp_path, {**STRUCTURE, path: body}) == []


EXTRAS = [
    "modules/a/helpers.py",
    "modules/a/application/helpers.py",
    "modules/a/utils/x.py",
    "stray.py",
    "scripts/seed.py",
    "web/routes/a.py",
]


@pytest.mark.parametrize("path", EXTRAS)
def test_code_in_places_the_profile_does_not_govern_is_not_checked(tmp_path, path):
    """xarch is a protocol: it requires the profile's parts and ignores everything else. Under cli, another
    profile's entry point (web/) is just an extra folder."""
    assert problems(tmp_path, {**STRUCTURE, path: "from app.platform import sql\nfrom app.modules.a.adapters import r"}) == []


@pytest.mark.parametrize("body", [
    "from app.modules.a.helpers import h",
    "from app.modules.a.utils import u",
    "from ..application.helpers import h",
    "from app.scripts import seed",
    "import app.web.routes",
])
def test_imports_into_places_the_profile_does_not_govern_are_ignored(tmp_path, body):
    assert problems(tmp_path, {**STRUCTURE, "modules/a/domain/x.py": body}) == []


def test_cli_may_import_other_cli_files(tmp_path):
    files = {**STRUCTURE, "cli/commands/a.py": "from app.cli.commands import b\nfrom . import b", "cli/commands/b.py": ""}
    assert problems(tmp_path, files) == []


def test_entry_point_violations_name_the_cli_folder(tmp_path):
    assert problems(tmp_path, {**STRUCTURE, "cli/commands/a.py": "from app.platform import sql"}) == [
        "app/cli/commands/a.py:1: cli/ may not import platform/ (app.platform)"]
