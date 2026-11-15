"""`xarch profile migrate` through the real app: a profile of format 1 with its files is converted into a new folder that
loads, nothing is overwritten, and `check` refuses a profile of format 1 saying to migrate it."""
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from xarch.bootstrap.app import app
from xarch.bootstrap.wiring import load_architecture
from xarch.modules.spec.domain.errors import InvalidArchitecture

runner = CliRunner()
OLD = """\
# a comment that is lost
xarch: 1
name: small
layout:
  core: {}
  cli: {}
parts:
  core: {path: core, role: the rules}
  cli: {path: cli, role: the commands}
rules:
  core: []
  cli: [core]
libraries:
  cli: [typer]
examples:
  rule: {part: core, path: core/rule.py, file: ex/rule.py, note: a pure rule}
docs:
  architecture.md: {from: architecture.md}
"""


@pytest.fixture(autouse=True)
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "small.yaml").write_text(OLD)
    (tmp_path / "architecture.md").write_text("see {{example:rule}}\n")
    (tmp_path / "ex").mkdir()
    (tmp_path / "ex" / "rule.py").write_text("X = 1\n")


def test_the_conversion_is_written_to_a_new_folder_beside_the_file_and_loads_in_format_2(tmp_path):
    result = runner.invoke(app, ["profile", "migrate", "small.yaml"])
    assert result.exit_code == 0, result.output
    assert (tmp_path / "small-v2" / "architecture.md").read_text() == "see {{example:core/rule.py}}\n"
    assert (tmp_path / "small-v2" / "examples" / "core" / "rule.py").read_text() == "X = 1\n"
    assert load_architecture(tmp_path / "small-v2" / "small.yaml").parts["cli"].role == "the commands"
    assert yaml.safe_load((tmp_path / "small-v2" / "small.yaml").read_text())["xarch"] == 2


def test_the_output_lists_the_files_what_changed_and_says_comments_are_lost():
    result = runner.invoke(app, ["profile", "migrate", "small.yaml"])
    assert "small-v2/small.yaml" in result.output
    assert "examples/core/rule.py  (from ex/rule.py)" in result.output
    assert "architecture.md  (from architecture.md, 1 example placeholder rewritten)" in result.output
    assert "comments" in result.output


def test_the_original_is_left_as_it_was(tmp_path):
    runner.invoke(app, ["profile", "migrate", "small.yaml"])
    assert (tmp_path / "small.yaml").read_text() == OLD
    assert (tmp_path / "architecture.md").read_text() == "see {{example:rule}}\n"


def test_a_dry_run_writes_nothing(tmp_path):
    result = runner.invoke(app, ["profile", "migrate", "small.yaml", "--dry-run"])
    assert result.exit_code == 0
    assert not (tmp_path / "small-v2").exists()
    assert "dry run" in result.output


def test_running_it_twice_refuses_to_overwrite_and_exits_2(tmp_path):
    runner.invoke(app, ["profile", "migrate", "small.yaml"])
    (tmp_path / "small-v2" / "small.yaml").write_text("mine\n")
    result = runner.invoke(app, ["profile", "migrate", "small.yaml"])
    assert result.exit_code == 2
    assert "already exist" in result.output
    assert (tmp_path / "small-v2" / "small.yaml").read_text() == "mine\n"


def test_out_names_another_folder(tmp_path):
    assert runner.invoke(app, ["profile", "migrate", "small.yaml", "--out", "new"]).exit_code == 0
    assert Path(tmp_path / "new" / "small.yaml").is_file()


def test_what_cannot_be_converted_is_listed_by_name_and_the_exit_stays_0(tmp_path):
    (tmp_path / "small.yaml").write_text(OLD.replace("layout:\n  core: {}", "layout:\n  scripts: {}\n  core: {}"))
    result = runner.invoke(app, ["profile", "migrate", "small.yaml"])
    assert result.exit_code == 0
    assert "by hand" in result.output
    assert "layout 'scripts'" in result.output


def test_check_refuses_a_profile_of_format_1_and_says_to_migrate_it(tmp_path):
    (tmp_path / "app").mkdir()
    result = runner.invoke(app, ["check", "--profile", "small.yaml"])
    assert result.exit_code == 2
    assert "xarch profile migrate small.yaml" in result.output


def test_loading_a_profile_of_format_1_raises_with_the_same_advice():
    with pytest.raises(InvalidArchitecture) as caught:
        load_architecture(Path("small.yaml"))
    assert "xarch profile migrate" in caught.value.reason
