"""The README says what the app does: its list of rule ids is the catalogue the violations name, and its block of
commands gives every option each command takes."""
import re
from pathlib import Path

import typer

from xarch.bootstrap.app import app
from xarch.kernel.violations import RULES

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
