"""The import rules of the bundled profiles, through the wired check on a throwaway tree: each rule of
docs/project/architecture.md section 5, under cli, whose entry point is cli/, and under web, whose entry point is web/.
In the rows, <entry> stands for the entry point's folder of files (<package> for it as a package) and <top> for the
entry part; <other> (<other package>) for the other profile's entry folder, which is just an extra folder here."""
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_controllers
from xarch.modules.rules.contract import CheckImports

ENTRY = {"cli": ("cli/commands", "cli", "web/routes"), "web": ("web/routes", "web", "cli/commands")}
PROFILES = pytest.mark.parametrize("profile", ["cli", "web"])
STRUCTURE = {"modules/__init__.py": "", "modules/a/__init__.py": "", "modules/b/__init__.py": "",
             "modules/a/application/__init__.py": "", "modules/b/application/__init__.py": ""}


def filled(text: str, profile: str) -> str:
    entry, top, other = ENTRY[profile]
    return (text.replace("<entry>", entry).replace("<package>", entry.replace("/", ".")).replace("<top>", top)
            .replace("<other package>", other.replace("/", ".")).replace("<other>", other))


def problems(tmp_path: Path, profile: str, files: dict[str, str]) -> list[str]:
    app = tmp_path / "app"
    for rel, body in {"__init__.py": "", **STRUCTURE, **files}.items():
        path = app / filled(rel, profile)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(filled(body, profile))
    return [str(v) for v in build_controllers().rules.check(CheckImports(app, "app", profile)).violations]


@PROFILES
def test_a_conforming_tree_passes(tmp_path, profile):
    files = {
        "kernel/errors.py": "import dataclasses",
        "kernel/logic/text.py": "from app.kernel import errors",
        "platform/sql.py": "from app.kernel import errors",
        "modules/a/domain/values.py": "from app.kernel import errors",
        "modules/a/domain/doc.py": "from .values import X\nfrom app.kernel.errors import E",
        "modules/a/contract/__init__.py": "from ..domain.values import X\nfrom app.kernel import errors",
        "modules/a/application/ports/repo.py": "from app.modules.a.domain.doc import Doc\nfrom app.kernel import errors",
        "modules/a/application/logic/rule.py":
            "from app.modules.a.domain.doc import Doc\nfrom app.kernel.logic.text import t\nfrom .other import o",
        "modules/a/application/logic/other.py": "from ...domain import values\nfrom app.kernel import errors",
        "modules/a/application/services/svc.py":
            "from ..ports.repo import Repo\nfrom ...domain import doc\nfrom ..logic.rule import r",
        "modules/a/application/controller.py":
            "from .services.svc import Svc\nfrom ..contract import X\nfrom .logic.rule import r",
        "modules/a/adapters/repo.py":
            "from app.platform.sql import S\nfrom ..application.ports.repo import Repo\nfrom app.modules.b.contract import Y",
        "modules/b/contract/__init__.py": "",
        "<entry>/a.py": "from app.modules.a.application.controller import C\nfrom app.modules.a.contract import X\n"
                        "from app.<package> import b\nfrom . import b",
        "<entry>/b.py": "",
        "bootstrap/app.py": "from app.modules.a.adapters.repo import R\nfrom app.<package> import a",
    }
    assert problems(tmp_path, profile, files) == []


def denied(path: str, src: str, dst: str, imported: str) -> str:
    return f"app/{path}:1: {src} may not import {dst} ({imported})"


DOMAIN, CONTRACT, SVC = "modules/a/domain/x.py", "modules/a/contract/__init__.py", "modules/a/application/services/svc.py"
CONTROLLER, PORTS, ADAPTER = ("modules/a/application/controller.py", "modules/a/application/ports/repo.py",
                              "modules/a/adapters/repo.py")
LOGIC, ENTRY_FILE = "modules/a/application/logic/rule.py", "<entry>/a.py"
OF_A, OF_B = " of modules/a", " of modules/b"


@PROFILES
@pytest.mark.parametrize("path, body, expected", [
    pytest.param("kernel/x.py", "from app.platform import sql",
                 denied("kernel/x.py", "kernel/", "platform/", "app.platform"), id="kernel imports only the kernel"),
    pytest.param("kernel/logic/x.py", "from app.modules.a.domain import doc",
                 denied("kernel/logic/x.py", "kernel/", "domain/" + OF_A, "app.modules.a.domain"),
                 id="kernel/logic is the kernel, and imports no module"),
    pytest.param("kernel/logic/x.py", "from app.modules.a.application.logic import rule",
                 denied("kernel/logic/x.py", "kernel/", "logic/" + OF_A, "app.modules.a.application.logic"),
                 id="kernel/logic imports no module's logic"),
    pytest.param(DOMAIN, "from app.modules.b.domain import y",
                 denied(DOMAIN, "domain/" + OF_A, "domain/" + OF_B, "app.modules.b.domain"),
                 id="a domain imports no other module's domain"),
    pytest.param(DOMAIN, "from app.platform import sql", denied(DOMAIN, "domain/" + OF_A, "platform/", "app.platform"),
                 id="a domain imports no platform"),
    pytest.param(DOMAIN, "from ..application.services import svc",
                 denied(DOMAIN, "domain/" + OF_A, "services/" + OF_A, "app.modules.a.application.services"),
                 id="a domain imports none of its application, even relatively"),
    pytest.param(DOMAIN, "import app.platform.sql", denied(DOMAIN, "domain/" + OF_A, "platform/", "app.platform.sql"),
                 id="a plain import statement is checked too"),
    pytest.param(CONTRACT, "from ..domain import doc",
                 denied(CONTRACT, "contract/" + OF_A, "domain/" + OF_A, "app.modules.a.domain"),
                 id="a contract imports only its domain's values"),
    pytest.param(CONTRACT, "from ..domain.valuesx import V",
                 denied(CONTRACT, "contract/" + OF_A, "domain/" + OF_A, "app.modules.a.domain.valuesx"),
                 id="the values path is matched by whole names"),
    pytest.param(CONTRACT, "from ..application.ports import repo",
                 denied(CONTRACT, "contract/" + OF_A, "ports/" + OF_A, "app.modules.a.application.ports"),
                 id="a contract imports no port"),
    pytest.param(SVC, "from ...adapters import repo",
                 denied(SVC, "services/" + OF_A, "adapters/" + OF_A, "app.modules.a.adapters"),
                 id="a service imports no adapter"),
    pytest.param(SVC, "from app.modules.b.contract import Y",
                 denied(SVC, "services/" + OF_A, "contract/" + OF_B, "app.modules.b.contract"),
                 id="a service imports no other module's contract"),
    pytest.param(SVC, "from ..controller import C",
                 denied(SVC, "services/" + OF_A, "controller/" + OF_A, "app.modules.a.application.controller"),
                 id="a service imports no controller"),
    pytest.param(CONTROLLER, "from app.modules.b.application.controller import C",
                 denied(CONTROLLER, "controller/" + OF_A, "controller/" + OF_B, "app.modules.b.application.controller"),
                 id="a controller imports no other module's controller"),
    pytest.param(CONTROLLER, "from app.platform import sql",
                 denied(CONTROLLER, "controller/" + OF_A, "platform/", "app.platform"),
                 id="a controller imports no platform"),
    pytest.param(PORTS, "from ...adapters import repo",
                 denied(PORTS, "ports/" + OF_A, "adapters/" + OF_A, "app.modules.a.adapters"), id="a port imports no adapter"),
    pytest.param(PORTS, "from ...contract import X",
                 denied(PORTS, "ports/" + OF_A, "contract/" + OF_A, "app.modules.a.contract"),
                 id="a port imports not even its own contract"),
    pytest.param(PORTS, "from app.modules.b.contract import Y",
                 denied(PORTS, "ports/" + OF_A, "contract/" + OF_B, "app.modules.b.contract"),
                 id="nor another's"),
    pytest.param(ADAPTER, "from app.modules.b.application.controller import C",
                 denied(ADAPTER, "adapters/" + OF_A, "controller/" + OF_B, "app.modules.b.application.controller"),
                 id="an adapter wraps another module through its contract, never its controller"),
    pytest.param(ADAPTER, "from app.modules.b.domain import d",
                 denied(ADAPTER, "adapters/" + OF_A, "domain/" + OF_B, "app.modules.b.domain"),
                 id="an adapter imports no other module's domain"),
    pytest.param(ADAPTER, "from app.<top> import commands",
                 denied(ADAPTER, "adapters/" + OF_A, "<top>/", "app.<top>"), id="an adapter imports no entry point"),
    pytest.param("platform/sql.py", "from app.modules.a.contract import X",
                 denied("platform/sql.py", "platform/", "contract/" + OF_A, "app.modules.a.contract"),
                 id="platform knows no module"),
    pytest.param(ENTRY_FILE, "from app.modules.a.application.services import svc",
                 denied(ENTRY_FILE, "<top>/", "services/" + OF_A, "app.modules.a.application.services"),
                 id="the entry point calls no service"),
    pytest.param(ENTRY_FILE, "from app.modules.a.domain import doc",
                 denied(ENTRY_FILE, "<top>/", "domain/" + OF_A, "app.modules.a.domain"),
                 id="the entry point imports no domain"),
    pytest.param(ENTRY_FILE, "from app.modules.a.adapters import repo",
                 denied(ENTRY_FILE, "<top>/", "adapters/" + OF_A, "app.modules.a.adapters"),
                 id="the entry point imports no adapter"),
    pytest.param(ENTRY_FILE, "from app.platform import sql", denied(ENTRY_FILE, "<top>/", "platform/", "app.platform"),
                 id="the entry point imports no platform"),
    pytest.param(LOGIC, "from ..services import svc",
                 denied(LOGIC, "logic/" + OF_A, "services/" + OF_A, "app.modules.a.application.services"),
                 id="logic imports no service"),
    pytest.param(LOGIC, "from ..ports import repo",
                 denied(LOGIC, "logic/" + OF_A, "ports/" + OF_A, "app.modules.a.application.ports"),
                 id="logic imports no port"),
    pytest.param(LOGIC, "from ..controller import C",
                 denied(LOGIC, "logic/" + OF_A, "controller/" + OF_A, "app.modules.a.application.controller"),
                 id="logic imports no controller"),
    pytest.param(LOGIC, "from ...contract import X",
                 denied(LOGIC, "logic/" + OF_A, "contract/" + OF_A, "app.modules.a.contract"),
                 id="logic imports no contract"),
    pytest.param(LOGIC, "from app.modules.b.application.logic import rule",
                 denied(LOGIC, "logic/" + OF_A, "logic/" + OF_B, "app.modules.b.application.logic"),
                 id="logic imports no other module's logic"),
    pytest.param(DOMAIN, "from app.modules.a.application.logic.rule import r",
                 denied(DOMAIN, "domain/" + OF_A, "logic/" + OF_A, "app.modules.a.application.logic.rule"),
                 id="a domain imports no logic"),
    pytest.param(SVC, "from app.modules.b.application.logic.rule import r",
                 denied(SVC, "services/" + OF_A, "logic/" + OF_B, "app.modules.b.application.logic.rule"),
                 id="a service imports no other module's logic"),
    pytest.param(ENTRY_FILE, "from app.modules.a.application.logic.rule import r",
                 denied(ENTRY_FILE, "<top>/", "logic/" + OF_A, "app.modules.a.application.logic.rule"),
                 id="the entry point imports no logic"),
    pytest.param(ENTRY_FILE, "from app.modules import a",
                 denied(ENTRY_FILE, "<top>/", "structure/", "app.modules.a"),
                 id="no part but bootstrap imports the structure"),
    pytest.param(DOMAIN, "import sqlalchemy\nfrom uuid import UUID",
                 "app/modules/a/domain/x.py:1: domain/ of modules/a may not import the outside package sqlalchemy "
                 "(libraries.domain)",
                 id="the standard library is always allowed and an unlisted outside package never"),
])
def test_a_forbidden_import_is_reported(tmp_path, profile, path, body, expected):
    assert problems(tmp_path, profile, {path: body}) == [filled(expected, profile)]


@PROFILES
@pytest.mark.parametrize("path, body", [
    pytest.param(SVC, "from app.modules.a.application.logic.rule import r", id="a service imports its own logic"),
    pytest.param(CONTROLLER, "from app.modules.a.application.logic.rule import r",
                 id="a controller imports its own logic"),
    pytest.param("platform/sql.py", "from sqlmodel import SQLModel", id="platform imports sqlmodel"),
    pytest.param(ADAPTER, "import sqlmodel", id="an adapter imports sqlmodel"),
    pytest.param(DOMAIN, "from __future__ import annotations\nimport sys, json", id="the standard library anywhere"),
    pytest.param("modules/a/helpers.py", "from app.platform import sql\nfrom app.modules.a.adapters import r",
                 id="a file in an instance but in no part is not checked"),
    pytest.param("modules/a/application/helpers.py", "from app.platform import sql",
                 id="nor one in the application folder"),
    pytest.param("modules/a/utils/x.py", "from app.platform import sql", id="nor one in a folder the layout lacks"),
    pytest.param("stray.py", "from app.platform import sql", id="nor one at the app's top"),
    pytest.param("scripts/seed.py", "from app.platform import sql", id="nor one in an extra top-level folder"),
    pytest.param("<other>/a.py", "from app.platform import sql", id="another profile's entry point is an extra folder"),
    pytest.param(DOMAIN, "from app.modules.a.helpers import h\nfrom app.modules.a.utils import u\n"
                         "from ..application.helpers import h\nfrom app.scripts import seed\nimport app.<other package>",
                 id="imports into places the profile does not govern are ignored"),
])
def test_an_allowed_or_ungoverned_import_is_not_reported(tmp_path, profile, path, body):
    assert problems(tmp_path, profile, {path: body}) == []


@pytest.mark.parametrize("profile, path, body", [
    pytest.param("cli", "cli/commands/a.py", "from typer import Typer", id="cli imports typer"),
    pytest.param("cli", "bootstrap/app.py", "import typer\nimport sqlmodel", id="cli's bootstrap imports its libraries"),
    pytest.param("web", "web/i18n/en.py", "from app.modules.a.contract import X\nfrom app.web.routes import a",
                 id="web/i18n is the entry point"),
    pytest.param("web", "web/ui/pages/home.py", "from app.modules.a.contract import X", id="so is web/ui"),
    pytest.param("web", "web/ui/primitives/button.py", "from app.web.routes import a", id="at any depth"),
    pytest.param("web", "web/routes/a.py", "from fastapi import APIRouter", id="web imports fastapi"),
])
def test_what_one_profile_allows_its_own_entry_point(tmp_path, profile, path, body):
    assert problems(tmp_path, profile, {path: body}) == []


def test_a_folder_of_the_web_entry_point_is_held_to_its_rules(tmp_path):
    assert problems(tmp_path, "web", {"web/ui/pages/home.py": "from app.modules.a.domain import doc"}) == [
        "app/web/ui/pages/home.py:1: web/ may not import domain/ of modules/a (app.modules.a.domain)"]


TARGETS = {
    "kernel": "app.kernel.t", "kernel/logic": "app.kernel.logic.t", "platform": "app.platform.t",
    "entry": "app.<package>.t", "bootstrap": "app.bootstrap.t", "structure": "app.modules.a",
    **{f"{part}@{m}": f"app.modules.{m}.{path}" for m in "ab" for part, path in [
        ("domain", "domain.t"), ("values", "domain.values"), ("contract", "contract"),
        ("controller", "application.controller"), ("services", "application.services.t"),
        ("logic", "application.logic.t"), ("ports", "application.ports.t"), ("adapters", "adapters.t")]},
}
SOURCES = {"kernel": "kernel/src.py", "domain": "modules/a/domain/src.py", "contract": "modules/a/contract/src.py",
           "controller": "modules/a/application/controller.py", "services": "modules/a/application/services/src.py",
           "logic": "modules/a/application/logic/src.py", "ports": "modules/a/application/ports/src.py",
           "adapters": "modules/a/adapters/src.py", "platform": "platform/src.py", "entry": "<entry>/src.py",
           "bootstrap": "bootstrap/src.py"}
KERNEL = {"kernel", "kernel/logic"}
ALLOWED = {
    "kernel": KERNEL,
    "domain": {*KERNEL, "domain@a", "values@a"},
    "contract": {*KERNEL, "contract@a", "values@a"},
    "controller": {*KERNEL, "controller@a", "services@a", "logic@a", "domain@a", "values@a", "ports@a", "contract@a"},
    "services": {*KERNEL, "services@a", "logic@a", "domain@a", "values@a", "ports@a", "contract@a"},
    "logic": {*KERNEL, "logic@a", "domain@a", "values@a"},
    "ports": {*KERNEL, "ports@a", "domain@a", "values@a"},
    "adapters": {*KERNEL, "adapters@a", "ports@a", "domain@a", "values@a", "platform", "contract@a", "contract@b"},
    "platform": {*KERNEL, "platform"},
    "entry": {*KERNEL, "entry", "controller@a", "controller@b", "contract@a", "contract@b"},
    "bootstrap": set(TARGETS),
}


@PROFILES
def test_every_part_imports_exactly_what_the_bundled_rules_allow(tmp_path, profile):
    """One file per part imports every place, one per line: the lines reported are those the rules forbid."""
    lines = "\n".join(f"import {module}" for module in TARGETS.values())
    found = problems(tmp_path, profile, {path: lines for path in SOURCES.values()})
    names = list(TARGETS)
    assert sorted(problem.split(": ", 1)[0] for problem in found) == sorted(
        f"app/{filled(path, profile)}:{names.index(target) + 1}" for part, path in SOURCES.items()
        for target in names if target not in ALLOWED[part])
