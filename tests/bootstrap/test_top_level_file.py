"""A file declared at the top level of the layout, such as `__main__.py`, works like one declared deeper: the structure
check requires it as a file, `init` writes it empty, a part may sit on it, the docs tree shows it and `where` places it."""
import json

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app
from xarch.bootstrap.wiring import build_spec

runner = CliRunner()
PROFILE = """xarch: 2
name: shim
parts:
  main:
    path: __main__.py
    role: the python -m entry
    may_import: [core]
    untested: a two-line shim
  core: {path: core, role: the code}
guards:
  closed-tree: {}
docs:
  pages:
    architecture.md: {from: arch.md}
"""
TEMPLATE = "# Architecture\n\n{{tree}}\n"


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "shim.yaml").write_text(PROFILE)
    (tmp_path / "arch.md").write_text(TEMPLATE)


def test_init_writes_the_declared_file_empty_like_a_nested_one(tmp_path):
    result = runner.invoke(app, ["init", "--profile", "shim.yaml", "--app", "shim"])
    assert result.exit_code == 0, result.output
    assert "created shim/__main__.py" in result.output
    assert (tmp_path / "shim/__main__.py").read_text() == ""
    assert (tmp_path / "shim/core/__init__.py").is_file()


def test_check_requires_the_declared_file_as_a_file_and_governs_it(tmp_path):
    runner.invoke(app, ["init", "--profile", "shim.yaml", "--app", "shim"])
    assert runner.invoke(app, ["check"]).exit_code == 0
    (tmp_path / "shim/__main__.py").unlink()
    missing = runner.invoke(app, ["check"])
    assert missing.exit_code == 1 and "shim: missing __main__.py" in missing.output


def test_the_part_on_the_declared_file_is_checked_like_any_part(tmp_path):
    runner.invoke(app, ["init", "--profile", "shim.yaml", "--app", "shim"])
    (tmp_path / "shim/__main__.py").write_text("from shim.core import x\n")
    (tmp_path / "shim/core/y.py").write_text("from shim import __main__\n")
    found = runner.invoke(app, ["check"]).output
    assert "shim/core/y.py:1: core/ may not import main/ (shim.__main__)" in found
    assert "shim/__main__.py:" not in found


def test_where_places_the_declared_file_in_its_part():
    runner.invoke(app, ["init", "--profile", "shim.yaml", "--app", "shim"])
    found = json.loads(runner.invoke(app, ["where", "shim/__main__.py", "--format", "json"]).stdout)
    assert (found["kind"], found["part"]["name"]) == ("part", "main")


def test_the_docs_tree_shows_the_declared_file_beside_the_folders():
    text = {"/".join(f.path): f.template for f in build_spec().docs("shim.yaml").files}["architecture.md"]
    assert "__main__.py" in text and "core/" in text
