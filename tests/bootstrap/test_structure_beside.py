"""A folder the layout names beside the instances of a repeating folder (`modules/wiring/` beside `modules/<module>/`)
through the real app: it is no instance, so `structure` does not hold it to the parts every instance holds, while an
instance that lacks one is still told so."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: beside
parts:
  modules/:
    wiring/:
      role: the composition root
      untested: a scratch project
      imports:
        may: everything
    <module>/:
      name: module
      role: one module
      untested: a scratch project
      imports:
        may: everything
      application/:
        role: its application
        untested: a scratch project
"""


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("beside.yaml").write_text(PROFILE)
    for path in ["app/__init__.py", "app/modules/__init__.py", "app/modules/wiring/__init__.py",
                 "app/modules/billing/__init__.py", "app/modules/billing/application/__init__.py",
                 "app/modules/mail/__init__.py"]:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text("")
    Path("tests").mkdir()


def test_a_folder_named_beside_the_instances_is_not_held_to_their_parts_but_an_instance_is():
    result = runner.invoke(app, ["check", "--profile", "beside.yaml", "--format", "json"])
    assert [(v["file"], v["message"]) for v in json.loads(result.stdout)["violations"] if v["rule"] == "structure"] == [
        ("app/modules/mail", "missing application/")]
