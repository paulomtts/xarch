"""What a key needs of the language is said twice: by spec's table of keys, which `profile explain <key>` shows, and by
the rules the key expands to, worked out from their kinds of fact and the fields their words read, which `profile
explain <key> --rule` shows. For every key the engine expands, in a profile that sets every one of them, the two are
the same facts."""
import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from xarch.bootstrap.app import app

runner = CliRunner()
EVERY_KEY = """name: every-key
testing: pytest
parts:
  core:
    path: core
    role: the rules
    may_import: [api]
    libraries: [yaml]
    uses: {never: pure}
    package_only: true
    holds: {functions: {names: "*"}, records: {names: "*", immutable: true}, exceptions: {names: "*"}}
    types_only: [api]
    must_import: [api]
    tests: unit
  api:
    path: api
    role: the api
    holds: {classes: {names: "*", immutable: true, built_by: [core]}}
    tests: unit
never:
  pure: [time.time]
reserved:
  ast: only the reader reads the language
tiers:
  unit:
    uses: {apply_never: true}
    types_only: [api]
    must_import: [core]
    may_also_import: [api]
  guard:
    folder: architecture
    may_import: [core]
fakes: {folder: fakes, for: [api], prefix: Fake}
guards:
  no-comments: {}
  closed-tree: {}
  dead-code: {untested: true, tests_only: true}
  pass-through: {parts: [core]}
  no-callbacks: {parts: [core]}
  private-imports: {}
"""
"""A profile that sets every key the engine expands to rules, on a part, on a tier and as a guard."""


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


def expanded(profile: Path) -> dict[str, dict]:
    """What `--rule` answers for each key the profile expands to rules, or sets nowhere though the engine would."""
    found = {address: ask(address, "--rule", "--profile", str(profile)) for address in addresses()}
    return {address: shown for address, shown in found.items() if shown["ok"]}


@pytest.fixture
def every_key(tmp_path: Path) -> Path:
    (tmp_path / "every-key.yaml").write_text(EVERY_KEY)
    return tmp_path / "every-key.yaml"


def test_the_profile_sets_every_key_the_engine_expands(every_key):
    assert runner.invoke(app, ["profile", "check", str(every_key)]).exit_code == 0
    assert [address for address, shown in expanded(every_key).items() if not shown["rules"]] == []


def test_what_a_key_needs_of_the_language_is_what_the_rules_it_expands_to_read(every_key):
    differ = {}
    for address, shown in expanded(every_key).items():
        said = {need["fact"] for need in ask(address)["needs"]}
        if said != set(shown["needs"]):
            differ[address] = (sorted(said - set(shown["needs"])), sorted(set(shown["needs"]) - said))
    assert differ == {}
