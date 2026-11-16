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
EVERY_KEY = """xarch: 2
name: every-key
testing: pytest
parts:
  core:
    path: core
    role: the rules
    may_import: [api]
    libraries: [yaml]
    forbidden: pure
    package_only: true
    holds: functions
    immutable: true
    types_only: [api]
    no_callbacks: true
    names: "*"
    must_import: [api]
    tier: unit
  api:
    path: api
    role: the api
    built_by: [core]
    holds: classes
    tier: unit
forbidden:
  pure: [time.time]
reserved:
  ast: only the reader reads the language
tiers:
  unit:
    apply_forbidden: true
    types_only: [api]
    must_import: [core]
  guard:
    folder: architecture
    may_import: [core]
fakes: {folder: fakes, for: [api], prefix: Fake}
guards:
  no-comments: {}
  closed-tree: {}
  dead-code: {untested: true, tests_only: true}
  pass-through: {parts: [core]}
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


@pytest.mark.xfail(strict=True, reason="audit 4, engine #1a: spec's profile_keys.NEEDS and the needs of the rules a "
                                       "key expands to disagree: parts.must_import (import.standard in the table, file "
                                       "in the rules), guards.private-imports (import.relative), "
                                       "guards.dead-code.untested (class, file and function in the rules), tiers and "
                                       "tiers.must_import (file in the rules), and the pass-through rules carry "
                                       "guards.pass-through.parts where the table says guards.pass-through; remove "
                                       "this mark once the expansion is the one source of a key's needs, or the two "
                                       "tables agree")
def test_what_a_key_needs_of_the_language_is_what_the_rules_it_expands_to_read(every_key):
    differ = {}
    for address, shown in expanded(every_key).items():
        said = {need["fact"] for need in ask(address)["needs"]}
        if said != set(shown["needs"]):
            differ[address] = (sorted(said - set(shown["needs"])), sorted(set(shown["needs"]) - said))
    assert differ == {}
