"""Sanctioned exceptions to `imports.may` through the real app: an import a part's `imports.accepted` names, with a
reason, is no `may-import` finding and is named in the enforcement section instead; an entry that no longer accepts
anything is itself a `may-import` finding, so the list can only shrink."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: ratchet
parts:
  web/:
    role: the web ring
  adapters/<adapter>/:
    name: adapter
    role: one driven adapter
    imports:
      accepted:
        - file: adapters/mail/send.py
          import: web/i18n.py
          why: the mail copy is translated by the web ring until the i18n port exists
        - file: adapters/n8n/run.py
          import: web/token.py:sign
          why: signing is shared with the web ring
"""


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("ratchet.yaml").write_text(PROFILE)
    for path, text in {
        "app/__init__.py": "", "app/web/__init__.py": "", "app/web/i18n.py": "T = 1\n",
        "app/web/token.py": "def sign(): ...\ndef check(): ...\n",
        "app/adapters/__init__.py": "", "app/adapters/mail/__init__.py": "",
        "app/adapters/mail/send.py": "from app.web import i18n\n",
        "app/adapters/n8n/__init__.py": "", "app/adapters/n8n/run.py": "from app.web.token import sign\n",
    }.items():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)
    Path("tests").mkdir()


def write(path: str, text: str) -> None:
    Path(path).write_text(text)


def check() -> tuple[list[str], dict]:
    result = runner.invoke(app, ["check", "--profile", "ratchet.yaml", "--format", "json"])
    document = json.loads(result.stdout)
    return [f"{v['file']}:{v['line'] or 0}: {v['message']}" for v in document["violations"]], document["enforcement"]


def test_an_accepted_import_is_no_finding_and_is_named_in_the_enforcement_section():
    found, enforcement = check()
    assert found == []
    assert enforcement["accepted"] == [
        {"file": "app/adapters/mail/send.py", "line": 1, "part": "adapter", "import": "web/i18n.py",
         "why": "the mail copy is translated by the web ring until the i18n port exists"},
        {"file": "app/adapters/n8n/run.py", "line": 1, "part": "adapter", "import": "web/token.py:sign",
         "why": "signing is shared with the web ring"}]


def test_the_text_output_names_each_accepted_import_with_its_reason():
    result = runner.invoke(app, ["check", "--profile", "ratchet.yaml"])
    assert ("  accepted:    app/adapters/n8n/run.py:1: imports web/token.py:sign, which "
            "parts.adapter.imports.accepted accepts: signing is shared with the web ring") in result.stdout


def test_an_import_beside_the_accepted_one_is_still_a_finding():
    write("app/adapters/n8n/run.py", "from app.web.token import sign, check\n")
    found, _ = check()
    assert found == ["app/adapters/n8n/run.py:1: adapter/ of adapters/n8n may not import web/ (app.web.token)"]


def test_an_entry_whose_import_is_gone_is_a_finding():
    write("app/adapters/mail/send.py", "")
    found, enforcement = check()
    assert found == ["app/adapters/mail/send.py:0: adapters/mail/send.py no longer imports web/i18n.py, which "
                     "parts.adapter.imports.accepted accepts (parts.adapter.imports.accepted)"]
    assert [item["file"] for item in enforcement["accepted"]] == ["app/adapters/n8n/run.py"]


def test_an_entry_whose_file_is_gone_is_a_finding():
    Path("app/adapters/mail/send.py").unlink()
    found, _ = check()
    assert found == ["app/adapters/mail/send.py:0: adapters/mail/send.py is no file of the app, which "
                     "parts.adapter.imports.accepted accepts an import of (parts.adapter.imports.accepted)"]


def test_a_profile_accepting_nothing_has_no_accepted_list_in_its_enforcement():
    Path("ratchet.yaml").write_text(PROFILE.split("    imports:")[0])
    write("app/adapters/mail/send.py", "")
    write("app/adapters/n8n/run.py", "")
    found, enforcement = check()
    assert found == [] and "accepted" not in enforcement
