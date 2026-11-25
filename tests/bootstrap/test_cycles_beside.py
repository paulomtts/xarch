"""A folder the layout names beside the instances of a repeating folder (`adapters/web/` beside `adapters/<adapter>/`)
through the real app: it is no instance, yet `cycles` holds it in one graph with them, so a loop through it is found,
and an import that only runs one way is not."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: beside
parts:
  kernel/:
    role: shared primitives
    untested: a scratch project
  adapters/:
    web/:
      role: the web ring
      untested: a scratch project
      imports:
        may: everything
    factories/:
      role: the composition root
      untested: a scratch project
      imports:
        may: everything
    <adapter>/:
      name: adapter
      role: one driven adapter
      untested: a scratch project
      imports:
        may: everything
"""


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("beside.yaml").write_text(PROFILE)
    for path, text in {
        "app/__init__.py": "", "app/kernel/__init__.py": "", "app/kernel/ids.py": "N = 1\n",
        "app/adapters/__init__.py": "", "app/adapters/web/__init__.py": "", "app/adapters/factories/__init__.py": "",
        "app/adapters/mail/__init__.py": "",
        "app/adapters/mail/send.py": "from app.adapters.web.page import render\n",
        "app/adapters/web/page.py": "from app.adapters.factories.mail import build\n\n\ndef render(): ...\n",
        "app/adapters/factories/mail.py": "from app.kernel.ids import N\n\n\ndef build(): ...\n",
    }.items():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)
    Path("tests").mkdir()


def found() -> list[dict]:
    result = runner.invoke(app, ["check", "--profile", "beside.yaml", "--format", "json"])
    return [v for v in json.loads(result.stdout)["violations"] if v["rule"] == "cycles"]


def test_imports_that_run_one_way_through_a_folder_named_beside_the_instances_are_no_cycle():
    assert found() == []


def test_a_loop_from_an_instance_through_folders_named_beside_it_and_back_is_a_cycle():
    Path("app/adapters/factories/mail.py").write_text("from app.adapters.mail.send import render\n\n\ndef build(): ...\n")
    assert [v["message"] for v in found()] == [
        "adapters/factories, adapters/mail and adapters/web import each other in a cycle, through 3 dependencies; "
        "the one to cut: adapters/web → adapters/factories: app/adapters/web/page.py:1 imports "
        "app.adapters.factories.mail (cycles)"]


def test_a_folder_named_beside_the_instances_is_still_its_own_part_for_where():
    result = runner.invoke(app, ["where", "app/adapters/web/page.py", "--profile", "beside.yaml"])
    assert result.exit_code == 0, result.output
    assert "part:           adapters/web/\n" in result.output
