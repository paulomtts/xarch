"""The features of one round together through the real app, on one small project: a counterpart the layout's
repeating folder binds, with one source accepted; a count of a check of the profile's own with one finding accepted by
name; a baseline written by `xarch baseline write` that holds back what is left (an accepted finding is never
recorded) so `check` reports only what is new; and a part whose litmus is a list of entries, which `xarch where` gives
as that list in JSON."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()

PROFILE = """\
name: together
parts:
  adapters/sql/:
    <store>/:
      name: store
      role: the sql adapter of one store
  core/:
    role: the rules
    litmus:
      - Does it decide what the product does?
      - {ask: "Does it run without I/O?", label: pure, mode: all}
counterparts:
  store-has-tests:
    for: adapters/sql/<store>/
    has: tests/sql/<store>/
    accepted:
      - {path: adapters/sql/legacy/, why: the legacy store is retired with the old checkout}
checks:
  one-port-per-file:
    read: class
    in: {part: core}
    keep: [{named: "*Port"}]
    at_most: 1
    message: "{file} declares {count} interfaces, and {name} at line {line} is one too many"
    fix: "move {name} to a file of its own"
    accepted:
      - {file: core/ports.py, name: CachePort, why: the cache port moves out with the cache}
    examples:
      flagged: {core/ports.py: "class APort: ...\\nclass BPort: ...\\n"}
      clean: {core/ports.py: "class APort: ...\\n"}
"""
FILES = {
    "app/__init__.py": "", "app/core/__init__.py": "",
    "app/core/ports.py": "class StorePort: ...\nclass CachePort: ...\nclass LockPort: ...\n",
    "app/adapters/__init__.py": "", "app/adapters/sql/__init__.py": "",
    "app/adapters/sql/cart/__init__.py": "", "app/adapters/sql/shop/__init__.py": "",
    "app/adapters/sql/legacy/__init__.py": "",
    "tests/sql/shop/test_shop.py": "",
}


@pytest.fixture(autouse=True)
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    Path("together.yaml").write_text(PROFILE)
    for path, text in FILES.items():
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(text)


def run(*args: str):
    return runner.invoke(app, [*args, "--profile", "together.yaml"])


def check() -> tuple[int, list[str], dict]:
    result = run("check", "--format", "json")
    document = json.loads(result.stdout)
    return (result.exit_code, [f"{v['file']}:{v['line'] or 0}: [{v['rule']}]" for v in document["violations"]],
            document["enforcement"])


def test_counterparts_an_accepted_count_a_baseline_and_a_litmus_list_work_together():
    checked = runner.invoke(app, ["profile", "check", "together.yaml"])
    assert checked.exit_code == 0, checked.output

    code, found, enforcement = check()
    assert (code, found) == (1, ["app/adapters/sql/cart:0: [counterpart]", "app/core/ports.py:3: [one-port-per-file]"])
    assert [(item["key"], item["file"], item["line"]) for item in enforcement["accepted_findings"]] == [
        ("checks.one-port-per-file.accepted", "app/core/ports.py", 2),
        ("counterparts.store-has-tests.accepted", "app/adapters/sql/legacy", 0)]
    assert [(item["id"], item["read"]) for item in enforcement["counterparts"]] == [("store-has-tests", 3)]

    written = run("baseline", "write")
    assert written.exit_code == 0, written.stdout
    assert {(item["rule"], item["file"]) for item in json.loads(Path(".xarch/baseline.json").read_text())["findings"]} \
        == {("counterpart", "app/adapters/sql/cart"), ("one-port-per-file", "app/core/ports.py")}
    code, found, enforcement = check()
    assert (code, found, enforcement["baseline"]["baselined"]) == (0, [], 2)

    Path("app/adapters/sql/till").mkdir()
    Path("app/adapters/sql/till/__init__.py").write_text("")
    assert check()[:2] == (1, ["app/adapters/sql/till:0: [counterpart]"])

    where = runner.invoke(app, ["where", "app/core/rules.py", "--profile", "together.yaml", "--format", "json"])
    assert where.exit_code == 0, where.output
    assert json.loads(where.stdout)["part"]["litmus"] == [
        {"ask": "Does it decide what the product does?", "label": "1", "mode": "any"},
        {"ask": "Does it run without I/O?", "label": "pure", "mode": "all"}]
