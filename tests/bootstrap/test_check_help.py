"""The help of `xarch check --strict` says everything `--strict` fails on: the litmus of a part, a list of entries
included, a check of the profile's own or a counterpart that reads nothing, and a baseline above the code, but not the
findings a baseline holds back."""
import typer

from xarch.bootstrap.app import app


def strict_help() -> str:
    check = typer.main.get_command(app).commands["check"]
    return " ".join(next(param.help for param in check.params if "--strict" in param.opts).split())


def test_the_help_of_strict_names_the_litmus_lists_and_the_baseline():
    said = strict_help()
    assert "a part that keeps no litmus, or no entry of the litmus list, the compared profile gives it" in said
    assert "checks of the profile's own and counterparts that read nothing" in said
    assert "a baseline (.xarch/baseline.json) that records more than is found" in said
    assert "the violations a baseline holds back are not failed on" in said
    assert "for a chain of profile files, the bundled profile it rests on" in said
