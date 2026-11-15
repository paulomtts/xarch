"""`init --app <folder>` records the app folder in pyproject.toml when it is not the default, and `check`, `new` and
`where` use it when `--app` is not passed; the flag still wins, and no recorded value is ever rewritten."""
import json

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def pyproject(tmp_path) -> str:
    return (tmp_path / "pyproject.toml").read_text()


def init(*arguments: str):
    result = runner.invoke(app, ["init", "--profile", "cli", *arguments])
    assert result.exit_code == 0, result.output
    return result


def test_init_records_an_app_folder_that_is_not_the_default_after_the_profile(tmp_path):
    init("--app", "shop")
    assert pyproject(tmp_path) == '[tool.xarch]\nprofile = "cli"\napp = "shop"\n'


def test_init_records_a_nested_app_folder_relative_to_the_pyproject(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "x"\n')
    init("--app", "services/shop")
    assert pyproject(tmp_path).endswith('[tool.xarch]\nprofile = "cli"\napp = "services/shop"\n')


def test_init_does_not_record_the_default_app_folder(tmp_path):
    init()
    init("--app", "app")
    assert pyproject(tmp_path) == '[tool.xarch]\nprofile = "cli"\n'


def test_a_bare_check_new_and_where_use_the_recorded_app_folder(tmp_path):
    init("--app", "shop")
    assert runner.invoke(app, ["new", "module", "demo"]).exit_code == 0
    assert (tmp_path / "shop/modules/demo/application/controller.py").is_file()
    assert not (tmp_path / "app").exists()
    checked = runner.invoke(app, ["check"])
    assert checked.exit_code == 0, checked.output
    (tmp_path / "shop/kernel/bad.py").write_text("from shop.platform import sql\n")
    assert "shop/kernel/bad.py:1: kernel/ may not import platform/ (shop.platform)" in runner.invoke(
        app, ["check"]).output
    located = json.loads(runner.invoke(app, ["where", "shop/kernel/bad.py", "--format", "json"]).stdout)
    assert (located["kind"], located["part"]["name"]) == ("part", "kernel")


def test_the_recorded_app_folder_is_found_from_a_folder_below_the_project(tmp_path, monkeypatch):
    init("--app", "shop")
    (tmp_path / "below").mkdir()
    monkeypatch.chdir(tmp_path / "below")
    assert runner.invoke(app, ["check"]).exit_code == 0
    assert runner.invoke(app, ["new", "module", "demo"]).exit_code == 0
    assert (tmp_path / "shop/modules/demo").is_dir()


def test_the_flag_wins_over_the_recorded_app_folder(tmp_path):
    init("--app", "shop")
    init("--app", "other/app")
    assert runner.invoke(app, ["check", "--app", "other/app"]).exit_code == 0
    assert runner.invoke(app, ["new", "module", "demo", "--app", "other/app"]).exit_code == 0
    assert (tmp_path / "other/app/modules/demo").is_dir()
    missing = runner.invoke(app, ["check", "--app", "app"])
    assert missing.exit_code == 2 and "app is not a directory" in missing.output


def test_init_never_rewrites_a_recorded_app_folder(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[tool.xarch]\nprofile = "cli"\napp = "shop"\n')
    result = init("--app", "other")
    assert pyproject(tmp_path) == '[tool.xarch]\nprofile = "cli"\napp = "shop"\n'
    assert "skipped pyproject.toml" in result.output


def test_init_without_the_flag_builds_the_recorded_app_folder(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[tool.xarch]\nprofile = "cli"\napp = "shop"\n')
    runner.invoke(app, ["init"])
    assert (tmp_path / "shop/kernel/__init__.py").is_file() and not (tmp_path / "app").exists()


def test_an_unreadable_app_setting_is_a_usage_error(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[tool.xarch]\nprofile = "cli"\napp = 3\n')
    result = runner.invoke(app, ["check"])
    assert result.exit_code == 2
    assert f"cannot read {tmp_path / 'pyproject.toml'}: [tool.xarch] app must be a string" in result.output


def test_an_unreadable_app_setting_is_refused_as_json_when_json_is_asked(tmp_path):
    (tmp_path / "pyproject.toml").write_text('[tool.xarch]\nprofile = "cli"\napp = 3\n')
    result = runner.invoke(app, ["check", "--format", "json"])
    assert result.exit_code == 2
    assert json.loads(result.stdout) == {
        "ok": False, "error": f"cannot read {tmp_path / 'pyproject.toml'}: [tool.xarch] app must be a string"}
