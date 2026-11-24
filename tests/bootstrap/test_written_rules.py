"""Every rule a key of a bundled profile expands to, written as a check by `profile explain <key> --rule` and put in a
copy of that profile as checks of its own, finds in the example projects exactly what the built-in check finds, every
finding, its key aside: so every check xarch runs as a rule is one a profile could write, and every example `profile
explain` prints of a word, a rule of a bundled profile, loads and runs. The checks written for the explanation load and
behave as their examples say, so the words no bundled rule uses have examples that run too; and every word has one."""
import json
import re
import tarfile
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()
TESTS_TODO = """
checks:
  no-todo-in-tests:
    read: comment
    in: {files: tests, where: [tiered]}
    may_not: {text: ["*TODO*"]}
    message: "a test of the {tier} tier leaves a note for later: {text}"
    fix: "write the case now, or drop the note"
    examples:
      flagged: {tests/documents/check_notes.py: "# TODO: a case for an empty title\\n"}
      clean: {tests/documents/check_notes.py: "# one case per title\\n"}
"""
"""The second check written for the explanation, which no word's example shows."""
CORPORA = Path(__file__).parent / "corpora"
HAND_WRITTEN = {"cycles", "stand-ins", "scenario-coverage", "no-duplicates", "no-twins", "shared", "structure", "test-tree",
                "syntax"}
"""The rule ids of the checks that are no rule of the engine: hand-written, or with no key (syntax)."""
KEY = re.compile(r"\b(?:parts|tiers|guards|checks)\.[\w.<>-]+")
EXAMPLES = {"flagged": {"x.py": ""}, "clean": {"y.py": ""}}


@pytest.fixture(autouse=True)
def in_tmp(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)


def ask(*args: str) -> dict:
    return json.loads(runner.invoke(app, ["profile", "explain", *args, "--format", "json"]).output)


def addresses() -> list[str]:
    """Every key of the format, as the overview and the keys it holds name them."""
    pending = [shown["key"] for shown in ask()["shape"] if shown["depth"] == 0 and shown["key"] != "checks"]
    found: list[str] = []
    while pending:
        key = pending.pop(0)
        found.append(key)
        pending += [held["key"] for held in ask(key)["keys"]]
    return found


def project(root: Path, entry: str) -> None:
    with tarfile.open(CORPORA / "examples.tar.xz") as archive:
        archive.extractall(root / "examples", filter="data")
    for example in ("shared", entry):
        for file in (root / "examples" / example).rglob("*"):
            relative = file.relative_to(root / "examples" / example)
            if file.is_file():
                into = root / (relative if relative.parts[0] == "tests" else Path("app") / relative)
                into.parent.mkdir(parents=True, exist_ok=True)
                into.write_bytes(file.read_bytes())


def said(item: dict) -> tuple:
    return item["file"], item["line"] or 0, KEY.sub("KEY", item["message"]), KEY.sub("KEY", item["fix"] or "")


@pytest.mark.parametrize("entry", ["cli", "web"])
def test_every_rule_of_a_bundled_profile_written_as_a_check_finds_what_the_key_finds(entry, tmp_path):
    project(tmp_path, entry)
    assert runner.invoke(app, ["profile", "new", "mine", "--from", entry]).exit_code == 0
    location = tmp_path / "architecture" / "mine" / "mine.yaml"
    (tmp_path / "pyproject.toml").write_text(f'[tool.xarch]\nprofile = "{location.as_posix()}"\n')
    built_in = json.loads(runner.invoke(app, ["check", "--format", "json"]).output)
    checks: dict = {}
    for address in addresses():
        shown = ask(address, "--rule")
        if shown["ok"] and shown["rules"]:
            for name, body in yaml.safe_load(shown["checks"])["checks"].items():
                if body not in checks.values():
                    checks[f"{name}-{len(checks)}"] = body
    assert len(checks) > 20
    document = yaml.safe_load(location.read_text())
    document["checks"] = {name: {**body, "examples": EXAMPLES} for name, body in checks.items()}
    location.write_text(yaml.safe_dump(document, sort_keys=False))
    written = json.loads(runner.invoke(app, ["check", "--format", "json"]).output)
    own = set(checks)
    expected = sorted(said(v) for v in [*built_in["violations"], *built_in["enforcement"]["weak"]]
                      if v["rule"] not in HAND_WRITTEN)
    found = sorted(said(v) for v in [*written["violations"], *written["enforcement"]["weak"]] if v["rule"] in own)
    assert found == expected and expected


def test_the_checks_written_for_the_explanation_load_and_behave_as_their_examples_say(tmp_path):
    shown = [ask(address) for address in ("checks", "targets.text", "variables.type_only_fix")]
    written = {}
    for item in shown:
        written |= yaml.safe_load(item["example"]["check"])["checks"]
    written |= yaml.safe_load(TESTS_TODO)["checks"]
    profile = {"name": "worked", "testing": {"files": ["check_*.py"], "declared": [{"function": "check_*"}]},
               "tiers": {"unit": {}}, "parts": {"documents/": {"role": "the documents",
                                                               "tests": "unit"}}, "checks": written}
    (tmp_path / "worked.yaml").write_text(yaml.safe_dump(profile, sort_keys=False))
    checked = runner.invoke(app, ["profile", "check", "worked.yaml"])
    assert checked.exit_code == 0, checked.output
    assert set(written) == {"no-todo", "no-todo-in-tests", "types-stay-types"}


def test_every_word_of_every_category_has_an_example():
    categories = ask("checks")["categories"]
    missing = [f"{category['name']}.{word['name']}" for category in categories for word in category["words"]
               if ask(f"{category['name']}.{word['name']}")["example"] is None]
    assert missing == []
