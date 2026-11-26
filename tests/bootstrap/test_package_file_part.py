"""A part written as a folder's package file (application/__init__.py) holds that file only, through the real app: a
stray file beside it lies in no part, so `xarch where` says it is ungoverned and `closed-tree` reports it, while a file
the layout names beside it keeps its own part."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: facade
parts:
  core/:
    application/:
      __init__.py:
        name: application
        role: the facade
      controller.py:
        role: the controller
guards:
  closed-tree: {}
"""
FILES = ("app/__init__.py", "app/core/__init__.py", "app/core/application/__init__.py",
         "app/core/application/controller.py", "app/core/application/pricing.py")


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("facade.yaml").write_text(PROFILE)
    for path in FILES:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text("")


def where(path: str) -> dict:
    result = runner.invoke(app, ["where", path, "--profile", "facade.yaml", "--format", "json"])
    assert result.exit_code == 0, result.output
    return json.loads(result.stdout)


def test_a_stray_file_beside_a_package_file_part_lies_in_no_part_and_closed_tree_reports_it():
    assert where("app/core/application/__init__.py")["part"]["name"] == "application"
    assert where("app/core/application/controller.py")["part"]["name"] == "controller"
    stray = where("app/core/application/pricing.py")
    assert (stray["kind"], stray["part"], stray["closed_tree"]) == ("ungoverned", None, True)

    result = runner.invoke(app, ["check", "--profile", "facade.yaml", "--format", "json"])
    found = [(v["rule"], v["file"]) for v in json.loads(result.stdout)["violations"]]
    assert (result.exit_code, found) == (1, [("closed-tree", "app/core/application/pricing.py")])
