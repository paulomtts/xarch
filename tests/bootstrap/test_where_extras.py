"""`xarch where` and the view of a profile (`xarch profile explain --profile`) say, through the real app, what only
some profiles write: the counterparts that apply to a path, with what each needs there; a part marked `optional`; and
the imports a part's `imports.accepted` accepts in a file. Each is said only when it is set, so the answers of a
profile that writes none of them are as before."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: extras
parts:
  core/:
    role: the rules
    imports:
      accepted:
        - {file: core/rules.py, import: web/page.py, why: the page moves into core next}
  web/:
    role: the web ring
  adapters/sql/:
    <store>/:
      name: store
      role: the sql adapter of one store
  reports/:
    role: the reports
    optional: true
counterparts:
  store-has-tests:
    for: adapters/sql/<store>/
    has: tests/sql/<store>/
"""
FILES = {"app/__init__.py": "", "app/core/__init__.py": "", "app/core/rules.py": "from app.web import page\n",
         "app/web/__init__.py": "", "app/web/page.py": "", "app/adapters/__init__.py": "",
         "app/adapters/sql/__init__.py": "", "app/adapters/sql/cart/__init__.py": ""}


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("extras.yaml").write_text(PROFILE)
    for path, text in FILES.items():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)


def where(path: str) -> tuple[dict[str, str], dict]:
    text = runner.invoke(app, ["where", path, "--profile", "extras.yaml"])
    shown = runner.invoke(app, ["where", path, "--profile", "extras.yaml", "--format", "json"])
    assert text.exit_code == shown.exit_code == 0, text.output
    lines = {line.split(":", 1)[0]: line.split(":", 1)[1].strip() for line in text.output.splitlines()
             if line[:1].isalpha() and ":" in line}
    return lines, json.loads(shown.stdout)


def test_a_path_a_counterpart_applies_to_says_it_and_what_it_needs_there():
    lines, document = where("app/adapters/sql/cart/repo.py")
    assert lines["counterparts"] == "store-has-tests: needs tests/sql/cart/ (for adapters/sql/<store>/)"
    assert document["counterparts"] == [
        {"id": "store-has-tests", "for": "adapters/sql/<store>/", "has": "tests/sql/<store>/",
         "needs": "tests/sql/cart/"}]


def test_a_part_marked_optional_says_so():
    lines, document = where("app/reports/daily.py")
    assert lines["optional"] == "yes: structure does not ask for it"
    assert document["part"]["optional"] is True


def test_a_file_whose_imports_a_part_accepts_lists_each():
    lines, document = where("app/core/rules.py")
    assert lines["accepted"] == "web/page.py: the page moves into core next (parts.core.imports.accepted)"
    assert document["accepted_imports"] == [{"import": "web/page.py", "why": "the page moves into core next"}]


def test_what_is_not_set_is_not_said():
    lines, document = where("app/web/page.py")
    assert not {"counterparts", "optional", "accepted"} & set(lines)
    assert not {"counterparts", "accepted_imports"} & set(document) and "optional" not in document["part"]


def test_the_view_of_the_profile_lists_the_optional_parts_the_counterparts_and_the_accepted_imports():
    text = runner.invoke(app, ["profile", "explain", "--profile", "extras.yaml"])
    assert text.exit_code == 0, text.output
    assert "optional\n  reports/\n" in text.output
    assert "counterparts\n  store-has-tests: adapters/sql/<store>/ has tests/sql/<store>/\n" in text.output
    assert "accepted imports\n  core/rules.py imports web/page.py: the page moves into core next\n" in text.output
    shown = json.loads(runner.invoke(app, ["profile", "explain", "--profile", "extras.yaml", "--format",
                                           "json"]).stdout)
    assert shown["optional"] == ["reports/"]
    assert shown["counterparts"] == [{"id": "store-has-tests", "for": "adapters/sql/<store>/",
                                      "has": "tests/sql/<store>/"}]
    assert shown["accepted_imports"] == [{"part": "core", "file": "core/rules.py", "import": "web/page.py",
                                          "why": "the page moves into core next"}]
