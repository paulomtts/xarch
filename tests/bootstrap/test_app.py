"""Tests for the CLI: exit codes and output, plus the scaffold-then-check drift guard."""
from importlib import metadata

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def test_check_on_a_scaffolded_tree_passes():
    assert runner.invoke(app, ["init", "--profile", "cli"]).exit_code == 0
    assert runner.invoke(app, ["new", "module", "demo"]).exit_code == 0
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output
    assert "no violations" in result.output


def test_check_reports_violations_with_exit_1(tmp_path):
    runner.invoke(app, ["init", "--profile", "cli"])
    runner.invoke(app, ["new", "module", "demo"])
    (tmp_path / "app" / "kernel" / "bad.py").write_text("from app.platform import sql\n")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "app/kernel/bad.py:1: kernel/ may not import platform/" in result.output
    assert "1 violation(s) in 1 file(s)" in result.output.splitlines()
    assert result.output.splitlines().index("enforcement") > result.output.splitlines().index("1 violation(s) in 1 file(s)")


def test_check_reports_structure_violations(tmp_path):
    runner.invoke(app, ["init", "--profile", "cli"])
    (tmp_path / "app" / "modules" / "docs").mkdir()
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "app/modules/docs: missing application/ports/" in result.output


def test_check_with_a_missing_path_is_a_usage_error():
    result = runner.invoke(app, ["check", "--profile", "cli", "--app", "nowhere"])
    assert result.exit_code == 2
    assert "nowhere" in result.output


def test_check_accepts_an_app_path(tmp_path):
    runner.invoke(app, ["init", "--profile", "cli", "--app", "elsewhere/app"])
    assert runner.invoke(app, ["check", "--app", "elsewhere/app"]).exit_code == 0


def test_init_says_what_it_created_then_what_it_skipped():
    first = runner.invoke(app, ["init", "--profile", "cli"])
    assert first.exit_code == 0 and "created app/kernel/__init__.py" in first.output
    second = runner.invoke(app, ["init", "--profile", "cli"])
    assert second.exit_code == 0
    assert "skipped app/kernel/__init__.py" in second.output and "created" not in second.output


def test_new_module_says_what_it_created():
    runner.invoke(app, ["init", "--profile", "cli"])
    result = runner.invoke(app, ["new", "module", "demo"])
    assert result.exit_code == 0
    assert "created app/modules/demo/application/controller.py" in result.output


@pytest.mark.parametrize("name", ["Demo", "my-mod"])
def test_new_module_refuses_a_bad_name_with_exit_2(name):
    runner.invoke(app, ["init", "--profile", "cli"])
    result = runner.invoke(app, ["new", "module", name])
    assert result.exit_code == 2 and "lowercase" in result.output


def test_new_module_refuses_an_existing_module_with_exit_2():
    runner.invoke(app, ["init", "--profile", "cli"])
    runner.invoke(app, ["new", "module", "demo"])
    result = runner.invoke(app, ["new", "module", "demo"])
    assert result.exit_code == 2 and "already exists" in result.output


def write_pyproject(folder, profile):
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "pyproject.toml").write_text(f'[project]\nname = "x"\n\n[tool.xarch]\nprofile = "{profile}"\n')


@pytest.mark.parametrize("command", [["init"], ["check"], ["new", "module", "demo"]])
def test_without_a_profile_a_command_is_a_usage_error_listing_the_profiles_found(tmp_path, command):
    result = runner.invoke(app, command)
    assert result.exit_code == 2
    assert "no profile" in result.output and "the profiles found are cli, web" in result.output
    assert not (tmp_path / "app").exists()


def test_init_with_profile_web_then_check_with_profile_web_passes(tmp_path):
    result = runner.invoke(app, ["init", "--profile", "web"])
    assert result.exit_code == 0 and "created app/web/routes/__init__.py" in result.output
    assert runner.invoke(app, ["new", "module", "demo", "--profile", "web"]).exit_code == 0
    checked = runner.invoke(app, ["check", "--profile", "web"])
    assert checked.exit_code == 0, checked.output


def test_a_web_tree_checked_as_cli_misses_cli():
    runner.invoke(app, ["init", "--profile", "web"])
    result = runner.invoke(app, ["check", "--profile", "cli"])
    assert result.exit_code == 1 and "app: missing cli/" in result.output


def test_init_records_the_profile_so_a_bare_check_uses_it(tmp_path):
    result = runner.invoke(app, ["init", "--profile", "web"])
    assert "created pyproject.toml" in result.output
    assert (tmp_path / "pyproject.toml").read_text() == '[tool.xarch]\nprofile = "web"\n'
    assert runner.invoke(app, ["new", "module", "demo"]).exit_code == 0
    checked = runner.invoke(app, ["check"])
    assert checked.exit_code == 0, checked.output


def test_new_refuses_a_kind_the_profile_does_not_declare_with_exit_2():
    runner.invoke(app, ["init", "--profile", "cli"])
    result = runner.invoke(app, ["new", "features", "demo"])
    assert result.exit_code == 2 and "no kind 'features' in the profile: use module" in result.output


def test_new_refuses_the_folder_of_a_kind_in_place_of_its_word_and_says_what_to_type():
    runner.invoke(app, ["init", "--profile", "cli"])
    result = runner.invoke(app, ["new", "modules", "demo"])
    assert result.exit_code == 2 and "write `xarch new module <name>`" in result.output


def test_a_project_may_check_against_its_own_architecture_file(tmp_path):
    (tmp_path / "layered.yaml").write_text(
        'xarch: 2\nname: layered\n'
        'parts: {lib: {path: lib, role: shared}, api: {path: "modules/<module>/api", role: handlers, may_import: [lib]}}\n')
    write_pyproject(tmp_path, "layered.yaml")
    assert runner.invoke(app, ["init"]).exit_code == 0
    assert runner.invoke(app, ["new", "module", "orders"]).exit_code == 0
    assert (tmp_path / "app" / "modules" / "orders" / "api" / "__init__.py").is_file()
    (tmp_path / "app" / "lib" / "x.py").write_text("from app.modules.orders.api import h\n")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "app/lib/x.py:1: lib/ may not import api/ of modules/orders (app.modules.orders.api)" in result.output


def test_a_bad_architecture_file_is_a_clear_usage_error(tmp_path):
    (tmp_path / "bad.yaml").write_text("xarch: 2\nname: bad\nparts: {x: {path: nowhere}}\n")
    result = runner.invoke(app, ["check", "--profile", "bad.yaml"])
    assert result.exit_code == 2
    assert "error: bad.yaml: parts.x: missing `role`" in result.output
    assert "Traceback" not in result.output


def test_the_profile_comes_from_pyproject(tmp_path):
    write_pyproject(tmp_path, "web")
    assert runner.invoke(app, ["init"]).exit_code == 0
    assert (tmp_path / "app" / "web" / "i18n" / "__init__.py").is_file()
    assert runner.invoke(app, ["new", "module", "demo"]).exit_code == 0
    (tmp_path / "app" / "web" / "routes" / "demo.py").write_text("from app.modules.demo.domain import x\n")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "app/web/routes/demo.py:1: web/ may not import domain/ of modules/demo" in result.output


def test_the_pyproject_is_looked_up_from_the_folder_holding_app(tmp_path):
    write_pyproject(tmp_path / "elsewhere", "web")
    runner.invoke(app, ["init", "--app", "elsewhere/app"])
    assert (tmp_path / "elsewhere" / "app" / "web").is_dir()
    assert runner.invoke(app, ["check", "--app", "elsewhere/app"]).exit_code == 0


def test_profile_option_overrides_pyproject(tmp_path):
    write_pyproject(tmp_path, "web")
    runner.invoke(app, ["init"])
    result = runner.invoke(app, ["check", "--profile", "cli"])
    assert result.exit_code == 1 and "app: missing cli/" in result.output


@pytest.mark.parametrize("command", [["check"], ["init"], ["new", "module", "demo"]])
def test_an_unknown_profile_option_is_a_usage_error(tmp_path, command):
    runner.invoke(app, ["init", "--profile", "cli"])
    result = runner.invoke(app, [*command, "--profile", "mobile"])
    assert result.exit_code == 2
    assert "unknown profile 'mobile': use one of cli, web" in result.output
    assert not (tmp_path / "app" / "modules" / "demo").exists()


def test_an_unknown_profile_in_pyproject_is_a_usage_error(tmp_path):
    write_pyproject(tmp_path, "mobile")
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 2
    assert f"unknown profile 'mobile' in {tmp_path / 'pyproject.toml'}" in result.output
    assert not (tmp_path / "app").exists()


def test_extras_produce_no_violations(tmp_path):
    runner.invoke(app, ["init", "--profile", "cli"])
    runner.invoke(app, ["new", "module", "demo"])
    root = tmp_path / "app"
    extras = {"main.py": "from app.platform import sql", "scripts/seed.py": "from app.modules.demo.adapters import r",
              "modules/demo/helpers.py": "from app.platform import sql", "modules/demo/utils/x.py": "import os",
              "modules/demo/application/helpers.py": "", "modules/demo/domain/x.py": "from ..helpers import h",
              "kernel/sub/y.py": "", "web/routes/a.py": "from app.platform import sql"}
    for rel, body in extras.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(body)
    (root / "README.txt").write_text("notes")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 0, result.output


DOCS = ["docs/project/statement.md", "docs/project/domain.md", "docs/project/design.md",
        "docs/project/architecture.md", "docs/project/testing.md", "docs/project/requirements.md",
        "docs/project/adrs/0000-template.md", "docs/project/artifacts/standards/_template.md",
        "docs/project/artifacts/audits/_template.md", "docs/project/artifacts/taxonomy/_template.md",
        "docs/project/artifacts/modules/_template.md", "docs/project/artifacts/guards/_template.md"]


@pytest.mark.parametrize("profile", ["cli", "web"])
def test_init_lists_the_docs_it_created_then_skips_them(tmp_path, profile):
    first = runner.invoke(app, ["init", "--profile", profile])
    assert first.exit_code == 0
    lines = first.output.splitlines()
    assert lines[-len(DOCS) - 4:] == ["created pyproject.toml", *[f"created {d}" for d in DOCS],
                                      "created tests/architecture/test_rules.py", "created AGENTS.md", "created ruff.toml"]
    assert (tmp_path / "docs/project/adrs/0000-template.md").read_text().startswith("# ADR")
    assert f"| rendering | `{profile}/` |" in (tmp_path / "docs/project/testing.md").read_text()
    second = runner.invoke(app, ["init", "--profile", profile])
    assert second.exit_code == 0 and "created" not in second.output
    assert all(f"skipped {d}" in second.output for d in [*DOCS, "tests/architecture/test_rules.py", "AGENTS.md", "ruff.toml"])


def test_init_keeps_an_existing_doc_and_the_extras_around_it(tmp_path):
    """Drift guard: docs are not app structure."""
    project = tmp_path / "docs" / "project"
    (project / "adrs").mkdir(parents=True)
    (project / ".obsidian").mkdir()
    (project / ".obsidian" / "app.json").write_text("{}")
    (project / "architecture.md").write_text("# Mine\n")
    result = runner.invoke(app, ["init", "--profile", "cli"])
    assert result.exit_code == 0
    assert "skipped docs/project/architecture.md" in result.output
    assert "created docs/project/adrs/0000-template.md" in result.output
    assert (project / "architecture.md").read_text() == "# Mine\n"
    assert (project / ".obsidian" / "app.json").read_text() == "{}"
    assert runner.invoke(app, ["check"]).exit_code == 0


def test_init_puts_the_docs_beside_an_app_given_by_path(tmp_path):
    result = runner.invoke(app, ["init", "--profile", "cli", "--app", "elsewhere/app"])
    assert "created elsewhere/docs/project/statement.md" in result.output
    assert (tmp_path / "elsewhere" / "docs" / "project" / "statement.md").is_file()


def test_new_module_does_not_touch_the_docs(tmp_path):
    runner.invoke(app, ["init", "--profile", "cli"])
    (tmp_path / "docs" / "project" / "statement.md").unlink()
    result = runner.invoke(app, ["new", "module", "demo"])
    assert "docs/" not in result.output
    assert not (tmp_path / "docs" / "project" / "statement.md").exists()


def test_check_reads_imports_by_the_app_folders_own_package_name(tmp_path):
    runner.invoke(app, ["init", "--profile", "cli", "--app", "shop"])
    (tmp_path / "shop" / "kernel" / "bad.py").write_text("from shop.platform import sql\n")
    result = runner.invoke(app, ["check", "--app", "shop"])
    assert result.exit_code == 1
    assert "shop/kernel/bad.py:1: kernel/ may not import platform/ (shop.platform)" in result.output


def test_check_sees_the_tests_beside_the_app(tmp_path):
    runner.invoke(app, ["init", "--profile", "web"])
    (tmp_path / "tests" / "modules" / "nowhere").mkdir(parents=True)
    (tmp_path / "tests" / "modules" / "test_loose.py").write_text("")
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 1
    assert "tests/modules/nowhere: mirrors no folder of the app (app/modules/nowhere)" in result.output
    assert "tests/modules/test_loose.py: lies in no tier" in result.output


def test_the_tests_folder_may_be_given(tmp_path):
    runner.invoke(app, ["init", "--profile", "cli"])
    (tmp_path / "checks").mkdir()
    (tmp_path / "checks" / "conftest.py").write_text("# fixtures\n")
    result = runner.invoke(app, ["check", "--tests", "checks"])
    assert result.exit_code == 1 and "checks/conftest.py:1: a comment" in result.output


def test_a_missing_tests_folder_is_a_usage_error():
    runner.invoke(app, ["init", "--profile", "cli"])
    result = runner.invoke(app, ["check", "--tests", "nowhere"])
    assert result.exit_code == 2 and "nowhere is not a directory" in result.output


def test_init_refuses_a_profile_whose_file_replaces_what_the_skeleton_writes(tmp_path):
    (tmp_path / "guard.tpl").write_text("{{app}}\n")
    (tmp_path / "layered.yaml").write_text(
        "xarch: 2\nname: layered\nparts: {src: {path: src, role: code}}\n"
        "files: {app/__init__.py: {from: guard.tpl}}\n")
    result = runner.invoke(app, ["init", "--profile", "layered.yaml"])
    assert result.exit_code == 2
    assert ("layered.yaml: files.app/__init__.py: 'app/__init__.py' is the package file the skeleton writes"
            in result.output)
    assert not (tmp_path / "app").exists() and not (tmp_path / "pyproject.toml").exists()


def test_version_prints_the_installed_version_and_exits_0():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0, result.output
    assert result.output == f"xarch {metadata.version('xarch')}\n"


def test_version_wins_over_a_command_given_with_it():
    result = runner.invoke(app, ["--version", "check"])
    assert result.exit_code == 0, result.output
    assert result.output == f"xarch {metadata.version('xarch')}\n"
