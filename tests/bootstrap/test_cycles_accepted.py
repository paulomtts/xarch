"""`cycles.accepted` and `cycles.left_out` through the real app: a loop through a composition root that may import
everything (adapters/factories/, named beside adapters/<adapter>/) is left out with its reason, a loop between two
instances is accepted by its nodes, each is named in the enforcement section instead of reported, and an entry that
accepts nothing is a cycles finding."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: loops
parts:
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
cycles:
  accepted:
    - {group: [adapters/mail/, adapters/sms/], why: mail and sms merge into one notifier next}
  left_out:
    - {path: adapters/factories/, why: the composition root wires every adapter}
"""
FILES = {
    "app/__init__.py": "", "app/adapters/__init__.py": "", "app/adapters/web/__init__.py": "",
    "app/adapters/factories/__init__.py": "", "app/adapters/mail/__init__.py": "", "app/adapters/sms/__init__.py": "",
    "app/adapters/web/page.py": "from app.adapters.factories.mail import build\n",
    "app/adapters/factories/mail.py": "from app.adapters.web.page import build\n",
    "app/adapters/mail/send.py": "from app.adapters.sms.text import send\n",
    "app/adapters/sms/text.py": "from app.adapters.mail.send import send\n",
}


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("loops.yaml").write_text(PROFILE)
    for path, text in FILES.items():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)
    Path("tests").mkdir()


def check() -> tuple[int, list[tuple[str, str]], list[tuple[str, str, str]]]:
    result = runner.invoke(app, ["check", "--profile", "loops.yaml", "--format", "json"])
    document = json.loads(result.stdout)
    return (result.exit_code, [(v["file"], v["message"]) for v in document["violations"] if v["rule"] == "cycles"],
            [(item["key"], item["file"], item["why"]) for item in document["enforcement"].get("accepted_findings", ())
             if item["rule"] == "cycles"])


def test_a_composition_root_left_out_and_a_group_accepted_are_named_instead_of_reported():
    assert check() == (0, [], [
        ("cycles.accepted", "app/adapters/sms/text.py", "mail and sms merge into one notifier next"),
        ("cycles.left_out", "app/adapters/factories", "the composition root wires every adapter")])


def test_an_entry_that_accepts_nothing_is_a_cycles_finding():
    Path("app/adapters/sms/text.py").write_text("")
    Path("app/adapters/factories/mail.py").write_text("")
    code, found, accepted = check()
    assert (code, accepted) == (1, [])
    assert found == [
        ("app/adapters/factories", "cycles.left_out leaves out adapters/factories, which is in no cycle "
                                   "(cycles.left_out)"),
        ("app/adapters/mail", "cycles.accepted accepts a cycle of adapters/mail and adapters/sms, and cycles finds "
                              "none (cycles.accepted)")]
