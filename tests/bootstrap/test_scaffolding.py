"""Tests for init and new on a real filesystem: what they create, and what they refuse."""
from pathlib import Path

import pytest

from xarch.bootstrap.wiring import build_controllers
from xarch.modules.layout.contract import CheckStructure
from xarch.modules.rules.contract import CheckImports
from xarch.modules.scaffold.contract import Init, New, Refused, Report, Scaffolded

TOP = ["bootstrap/migrations", "kernel", "kernel/logic", "modules", "platform", "cli/commands"]
MODULE = ["contract", "domain", "application", "application/services", "application/logic", "application/ports",
          "adapters"]


def init(app: Path, profile: str = "cli") -> Report:
    result = build_controllers().scaffold.init(Init(app, profile))
    assert isinstance(result, Scaffolded)
    return result.report


def new_module(app: Path, name: str, profile: str = "cli") -> Scaffolded | Refused:
    return build_controllers().scaffold.new(New(app, "module", name, profile))


def refusal(app: Path, name: str) -> str:
    result = new_module(app, name)
    assert isinstance(result, Refused), result
    return result.reason


def test_init_creates_the_top_level_skeleton_with_packages(tmp_path):
    app = tmp_path / "app"
    init(app)
    for d in ["", *TOP]:
        assert (app / d / "__init__.py").is_file(), d


def test_init_reports_what_it_created(tmp_path):
    report = init(tmp_path / "app")
    assert tmp_path / "app" / "kernel" / "__init__.py" in report.created
    assert report.skipped == []


def test_init_is_idempotent_and_never_overwrites(tmp_path):
    app = tmp_path / "app"
    init(app)
    (app / "kernel" / "__init__.py").write_text("KEEP = 1")
    report = init(app)
    assert report.created == []
    assert app / "kernel" / "__init__.py" in report.skipped
    assert (app / "kernel" / "__init__.py").read_text() == "KEEP = 1"


def test_init_fills_in_only_what_is_missing(tmp_path):
    app = tmp_path / "app"
    (app / "kernel").mkdir(parents=True)
    (app / "kernel" / "__init__.py").write_text("")
    report = init(app)
    assert app / "kernel" / "__init__.py" in report.skipped
    assert app / "platform" / "__init__.py" in report.created


def test_new_module_creates_the_full_skeleton(tmp_path):
    app = tmp_path / "app"
    init(app)
    new_module(app, "documents")
    base = app / "modules" / "documents"
    for d in MODULE:
        assert (base / d / "__init__.py").is_file(), d
    assert (base / "__init__.py").is_file()
    assert (base / "application" / "controller.py").is_file()


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_init_and_new_module_create_the_logic_folders(tmp_path, profile):
    app = tmp_path / "app"
    init(app, profile)
    new_module(app, "documents", profile)
    assert (app / "kernel" / "logic" / "__init__.py").is_file()
    assert (app / "modules" / "documents" / "application" / "logic" / "__init__.py").is_file()


def test_new_module_refuses_an_invalid_name(tmp_path):
    app = tmp_path / "app"
    init(app)
    assert "lowercase" in refusal(app, "my-module")
    assert list((app / "modules").iterdir()) == [app / "modules" / "__init__.py"]


def test_new_module_refuses_an_existing_module(tmp_path):
    app = tmp_path / "app"
    init(app)
    new_module(app, "documents")
    assert "already exists" in refusal(app, "documents")


def test_new_module_needs_modules_folder(tmp_path):
    assert "xarch init" in refusal(tmp_path / "app", "documents")


def test_a_scaffolded_module_has_every_part_the_layout_rules_require(tmp_path):
    app = tmp_path / "app"
    init(app)
    new_module(app, "documents")
    assert build_controllers().layout.check(CheckStructure(app, "app", "cli")).violations == ()


def test_init_for_web_creates_web_with_routes_i18n_and_ui_and_no_cli(tmp_path):
    app = tmp_path / "app"
    init(app, "web")
    for d in ["", "bootstrap/migrations", "kernel", "kernel/logic", "modules", "platform", "web", "web/routes", "web/i18n",
              "web/ui"]:
        assert (app / d / "__init__.py").is_file(), d
    assert not (app / "cli").exists()


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_scaffold_then_check_has_no_violations(tmp_path, profile):
    """Drift guard: what init and new build is exactly what check requires, in every profile."""
    app = tmp_path / "app"
    init(app, profile)
    new_module(app, "documents", profile)
    controllers = build_controllers()
    structure = controllers.layout.check(CheckStructure(app, "app", profile)).violations
    imports = controllers.rules.check(CheckImports(app, "app", profile)).violations
    assert structure + imports == ()


def test_init_and_new_module_leave_pre_existing_extras_alone(tmp_path):
    """A bare module folder is never overwritten, and it alone is reported, never the extras."""
    app = tmp_path / "app"
    extras = {app / "scripts" / "seed.py": "SEED = 1", app / "main.py": "MAIN = 1",
              app / "kernel" / "extra.py": "X = 1"}
    for path, body in extras.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body)
    init(app)
    (app / "modules" / "documents").mkdir()
    assert "already exists" in refusal(app, "documents")
    new_module(app, "other")
    assert {p: p.read_text() for p in extras} == extras
    violations = build_controllers().layout.check(CheckStructure(app, "app", "cli")).violations
    assert {v.file for v in violations} == {"app/modules/documents"}


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_init_writes_each_doc_of_the_profile_with_its_template(tmp_path, profile):
    init(tmp_path / "app", profile)
    docs = build_controllers().spec.docs(profile)
    assert {f.path: (tmp_path / "docs" / "project").joinpath(*f.path).read_text() for f in docs.files} == {
        f.path: f.template for f in docs.files}
