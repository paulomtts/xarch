"""Tests for the structure rules: the top-level folders and each module's full skeleton must exist."""
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_controllers
from xarch.modules.layout.contract import CheckStructure


def check(app: Path, profile: str = "cli"):
    return list(build_controllers().layout.check(CheckStructure(app, "app", profile)).violations)


MODULE_PARTS = ["contract/", "domain/", "application/controller.py", "application/services/",
                "application/logic/", "application/ports/", "adapters/"]


def make(root: Path, dirs: list[str], files: list[str] = ()) -> Path:
    app = root / "app"
    app.mkdir()
    for d in dirs:
        (app / d).mkdir(parents=True)
    for f in files:
        (app / f).parent.mkdir(parents=True, exist_ok=True)
        (app / f).write_text("")
    return app


TOP = ["bootstrap", "kernel", "modules", "platform", "cli"]
FULL_MODULE_DIRS = ["modules/docs/contract", "modules/docs/domain", "modules/docs/application/services",
                    "modules/docs/application/logic", "modules/docs/application/ports", "modules/docs/adapters"]


def test_a_complete_skeleton_passes(tmp_path):
    app = make(tmp_path, TOP + FULL_MODULE_DIRS, ["modules/docs/application/controller.py"])
    assert check(app) == []


@pytest.mark.parametrize("missing", TOP)
def test_a_missing_top_level_folder_is_reported(tmp_path, missing):
    app = make(tmp_path, [d for d in TOP if d != missing])
    assert [str(v) for v in check(app)] == [f"app: missing {missing}/"]


@pytest.mark.parametrize("missing", MODULE_PARTS)
def test_a_missing_module_part_is_reported(tmp_path, missing):
    dirs = [d for d in FULL_MODULE_DIRS if d != f"modules/docs/{missing.rstrip('/')}"]
    files = [] if missing.endswith(".py") else ["modules/docs/application/controller.py"]
    app = make(tmp_path, TOP + dirs, files)
    assert [str(v) for v in check(app)] == [f"app/modules/docs: missing {missing}"]


def test_a_module_with_nothing_reports_every_part(tmp_path):
    app = make(tmp_path, TOP + ["modules/docs"])
    assert [str(v) for v in check(app)] == [f"app/modules/docs: missing {p}" for p in MODULE_PARTS]


def test_every_module_is_checked(tmp_path):
    app = make(tmp_path, TOP + ["modules/a", "modules/b"])
    assert {v.file for v in check(app)} == {"app/modules/a", "app/modules/b"}


def test_package_noise_under_modules_is_not_a_module(tmp_path):
    app = make(tmp_path, TOP + ["modules/__pycache__"], ["modules/__init__.py"])
    assert check(app) == []


WEB_TOP = ["bootstrap", "kernel", "modules", "platform", "web"]


def test_a_web_tree_without_cli_passes_under_the_web_profile(tmp_path):
    app = make(tmp_path, WEB_TOP + FULL_MODULE_DIRS, ["modules/docs/application/controller.py"])
    assert check(app, "web") == []


def test_a_web_tree_fails_under_the_cli_profile(tmp_path):
    app = make(tmp_path, WEB_TOP)
    assert [str(v) for v in check(app, "cli")] == ["app: missing cli/"]


def test_a_cli_tree_fails_under_the_web_profile(tmp_path):
    app = make(tmp_path, TOP)
    assert [str(v) for v in check(app, "web")] == ["app: missing web/"]


@pytest.mark.parametrize("missing", WEB_TOP)
def test_a_missing_top_level_folder_of_the_web_profile_is_reported(tmp_path, missing):
    app = make(tmp_path, [d for d in WEB_TOP if d != missing])
    assert [str(v) for v in check(app, "web")] == [f"app: missing {missing}/"]


def test_extra_folders_and_files_are_tolerated(tmp_path):
    extras = ["scripts", "web", "kernel/extra", "modules/docs/utils", "modules/docs/application/extra"]
    files = ["modules/docs/application/controller.py", "main.py", "modules/docs/helpers.py",
             "modules/docs/application/helpers.py", "cli/notes.txt"]
    app = make(tmp_path, TOP + FULL_MODULE_DIRS + extras, files)
    assert check(app) == []
