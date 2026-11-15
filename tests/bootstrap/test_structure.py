"""Tests for the structure rules: every folder and file the layout declares must exist, at any depth, outside the
`each` folder and in each of its instances."""
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
NESTED = ["bootstrap/migrations", "kernel/logic", "cli/commands"]
FULL_MODULE_DIRS = ["modules/docs/contract", "modules/docs/domain", "modules/docs/application/services",
                    "modules/docs/application/logic", "modules/docs/application/ports", "modules/docs/adapters"]


def test_a_complete_skeleton_passes(tmp_path):
    app = make(tmp_path, TOP + NESTED + FULL_MODULE_DIRS, ["modules/docs/application/controller.py"])
    assert check(app) == []


@pytest.mark.parametrize("missing", NESTED)
def test_a_missing_folder_below_a_top_level_folder_is_reported(tmp_path, missing):
    app = make(tmp_path, TOP + [d for d in NESTED if d != missing])
    assert [str(v) for v in check(app)] == [f"app: missing {missing}/"]


def test_a_top_level_folder_with_nothing_in_it_reports_what_the_layout_puts_in_it(tmp_path):
    app = make(tmp_path, ["bootstrap", "kernel", "modules", "platform", "cli"])
    assert [str(v) for v in check(app)] == ["app: missing bootstrap/migrations/", "app: missing kernel/logic/",
                                            "app: missing cli/commands/"]


@pytest.mark.parametrize("missing", TOP)
def test_a_missing_top_level_folder_is_reported(tmp_path, missing):
    app = make(tmp_path, [d for d in TOP + NESTED if d != missing and not d.startswith(f"{missing}/")])
    inside = [f"app: missing {d}/" for d in NESTED if d.startswith(f"{missing}/")]
    assert [str(v) for v in check(app)] == [f"app: missing {missing}/", *inside]


@pytest.mark.parametrize("missing", MODULE_PARTS)
def test_a_missing_module_part_is_reported(tmp_path, missing):
    dirs = [d for d in FULL_MODULE_DIRS if d != f"modules/docs/{missing.rstrip('/')}"]
    files = [] if missing.endswith(".py") else ["modules/docs/application/controller.py"]
    app = make(tmp_path, TOP + NESTED + dirs, files)
    assert [str(v) for v in check(app)] == [f"app/modules/docs: missing {missing}"]


def test_a_module_with_nothing_reports_every_part(tmp_path):
    app = make(tmp_path, TOP + NESTED + ["modules/docs"])
    assert [str(v) for v in check(app)] == [f"app/modules/docs: missing {p}" for p in MODULE_PARTS]


def test_every_module_is_checked(tmp_path):
    app = make(tmp_path, TOP + NESTED + ["modules/a", "modules/b"])
    assert {v.file for v in check(app)} == {"app/modules/a", "app/modules/b"}


def test_package_noise_under_modules_is_not_a_module(tmp_path):
    app = make(tmp_path, TOP + NESTED + ["modules/__pycache__"], ["modules/__init__.py"])
    assert check(app) == []


WEB_TOP = ["bootstrap", "kernel", "modules", "platform", "web"]
WEB_NESTED = ["bootstrap/migrations", "kernel/logic", "web/routes", "web/i18n", "web/ui"]


def test_a_web_tree_without_cli_passes_under_the_web_profile(tmp_path):
    app = make(tmp_path, WEB_TOP + WEB_NESTED + FULL_MODULE_DIRS, ["modules/docs/application/controller.py"])
    assert check(app, "web") == []


def test_a_web_tree_fails_under_the_cli_profile(tmp_path):
    app = make(tmp_path, WEB_TOP + WEB_NESTED)
    assert [str(v) for v in check(app, "cli")] == ["app: missing cli/", "app: missing cli/commands/"]


def test_a_cli_tree_fails_under_the_web_profile(tmp_path):
    app = make(tmp_path, TOP + NESTED)
    assert [str(v) for v in check(app, "web")] == ["app: missing web/", "app: missing web/routes/",
                                                   "app: missing web/i18n/", "app: missing web/ui/"]


@pytest.mark.parametrize("missing", WEB_TOP)
def test_a_missing_top_level_folder_of_the_web_profile_is_reported(tmp_path, missing):
    app = make(tmp_path, [d for d in WEB_TOP + WEB_NESTED if d != missing and not d.startswith(f"{missing}/")])
    inside = [f"app: missing {d}/" for d in WEB_NESTED if d.startswith(f"{missing}/")]
    assert [str(v) for v in check(app, "web")] == [f"app: missing {missing}/", *inside]


@pytest.mark.parametrize("missing", WEB_NESTED)
def test_a_missing_folder_below_a_top_level_folder_of_the_web_profile_is_reported(tmp_path, missing):
    app = make(tmp_path, WEB_TOP + [d for d in WEB_NESTED if d != missing])
    assert [str(v) for v in check(app, "web")] == [f"app: missing {missing}/"]


def test_extra_folders_and_files_are_tolerated(tmp_path):
    extras = ["scripts", "web", "kernel/extra", "modules/docs/utils", "modules/docs/application/extra"]
    files = ["modules/docs/application/controller.py", "main.py", "modules/docs/helpers.py",
             "modules/docs/application/helpers.py", "cli/notes.txt"]
    app = make(tmp_path, TOP + NESTED + FULL_MODULE_DIRS + extras, files)
    assert check(app) == []
