"""The README says what the app does: its list of rule ids is the catalogue the violations name, its block of
commands gives every option each command takes, and its table of rules names for each rule keys that feed it."""
import re
from pathlib import Path

import typer
from typer.testing import CliRunner

from xarch.bootstrap.app import app
from xarch.kernel.violations import RULES
from xarch.modules.spec.domain.key_table import KEYS
from xarch.modules.spec.domain.profile_keys import PART_HOLDS

README = (Path(__file__).resolve().parents[2] / "README.md").read_text(encoding="utf-8")


def between(start: str, end: str) -> str:
    """The README's text after start, up to the first end after it."""
    begin = README.index(start) + len(start)
    return README[begin:README.index(end, begin)]


def options(command, path: tuple[str, ...] = ()) -> dict[str, set[str]]:
    """Every command of the app by how it is typed, with the options it takes, its help aside."""
    found = {" ".join(("xarch", *path)): {opt for param in command.params for opt in param.opts
                                          if opt.startswith("--") and opt != "--help"}}
    for name, sub in getattr(command, "commands", {}).items():
        found |= options(sub, (*path, name))
    return found


def test_the_rule_ids_the_json_contract_lists_are_those_a_violation_names():
    listed = re.findall(r"`([a-z-]+)`", between("`rule` is one of:", "or the id of a check"))
    assert sorted(listed) == sorted(RULES)


def test_the_block_of_commands_gives_every_option_of_every_command():
    block = between("## Commands\n\n```\n", "```")
    lines = {line.split("  #")[0].strip() for line in block.splitlines() if line.startswith("xarch")}
    commands = {typed: taken for typed, taken in options(typer.main.get_command(app)).items() if typed != "xarch"}
    shown = {typed: next(line for line in lines if re.match(rf"{re.escape(typed)}( |$)", line)) for typed in commands}
    assert {typed: sorted(opt for opt in taken if opt not in shown[typed]) for typed, taken in commands.items()} == {
        typed: [] for typed in commands}


def keys_named(cell: str, kinds: list[str]) -> list[str]:
    """The keys a Key cell of the rule table names, one holding <kind> once with each kind in its place; none for -."""
    if cell.startswith("-"):
        return []
    return [key.replace("<kind>", kind) for key in re.findall(r"`([^`]+)`", cell)
            for kind in (kinds if "<kind>" in key else [""])]


def rules_of(key: str) -> list[str]:
    """The rules `xarch profile explain` says the key feeds; none for an address that is no key."""
    shown = CliRunner().invoke(app, ["profile", "explain", key])
    enforced = next((line for line in shown.output.splitlines() if line.startswith("  enforced:")), "")
    return re.findall(r"`([a-z-]+)`", enforced) if shown.exit_code == 0 else []


def test_each_key_the_rule_table_names_feeds_that_rule():
    rows = [line for line in between("| Rule id | What it catches | Key |", "\n\n").splitlines()
            if line.startswith("|") and not line.startswith("|---")]
    cells = [[cell.strip() for cell in row.strip("|").split("|")] for row in rows]
    kinds = [key.name for key in KEYS if key.scope == PART_HOLDS]
    named = {row[0].strip("`"): keys_named(row[-1], kinds) for row in cells}
    assert {rule: sorted(key for key in keys if rule not in rules_of(key)) for rule, keys in named.items()} == {
        rule: [] for rule in named}
