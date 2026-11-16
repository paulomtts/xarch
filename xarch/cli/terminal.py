"""What every command shares: the --app, --profile, --tests and --format options, choosing the app folder and the
profile, and how a refusal reaches the terminal, as text or as JSON."""
from collections.abc import Callable, Iterable
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from xarch.cli.reports.refusal_report import json_error, reason, text_error
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import (
    AppChosen,
    ChooseApp,
    NoProfileChosen,
    ProfileRefused,
    ProfileSelected,
    SelectProfile,
)

AppPath = Annotated[Path | None, typer.Option(
    "--app", help="The app/ folder to work on. Default: \\[tool.xarch] app in pyproject.toml (`init` records it when it "
                  "is not app/), else app/ in the working folder.")]
ProfileName = Annotated[str | None, typer.Option(
    "--profile", help="The profile: the name of a bundled profile, or a path to a profile file (.yaml or .json). "
                      "Default: \\[tool.xarch] profile in pyproject.toml; with neither, the command fails.")]
TestsPath = Annotated[Path | None, typer.Option(
    "--tests", help="The tests folder to check. Default: \\[tool.xarch] tests in pyproject.toml, else tests/ beside "
                    "the app folder, if there is one.")]


class Format(str, Enum):
    text = "text"
    json = "json"


FormatOption = Annotated[Format, typer.Option(
    "--format", help="text: one line per violation, then a summary (the default); json: one JSON document on stdout, "
                     "described in the README.")]


def fail(message: str) -> typer.Exit:
    typer.echo(text_error(message), err=True)
    return typer.Exit(2)


def json_refusal(message: str) -> typer.Exit:
    typer.echo(json_error(message))
    return typer.Exit(2)


def refusal(output: Format) -> Callable[[str], typer.Exit]:
    """How a refusal reaches the terminal in the format asked for."""
    return json_refusal if output is Format.json else fail


def in_full(path: Path) -> Path:
    """A path given on the command line, read from the working folder when it is relative: the one place xarch reads
    the folder it was started in, which every module is handed as a path in full."""
    return Path.cwd() / path


def app_for(spec: SpecController, app_path: Path | None, refuse: Callable[[str], typer.Exit] = fail) -> Path:
    """The app folder to work on, as spec chooses it from --app and the working folder; a refusal is raised as what
    refuse makes of its reason."""
    match spec.choose_app(ChooseApp(in_full(Path()), app_path)):
        case AppChosen(app):
            return app
        case ProfileRefused(why):
            raise refuse(why)


def profile_for(spec: SpecController, app_path: Path, override: str | None) -> str:
    return selection(spec, app_path, override, None)[0]


def selection(spec: SpecController, app_path: Path, override: str | None,
              tests: Path | None, refuse: Callable[[str], typer.Exit] = fail) -> tuple[str, Path | None]:
    """The architecture in force and the tests root to check, as spec selects them; a refusal is raised as what
    refuse makes of its reason."""
    match spec.select(SelectProfile(in_full(app_path), override, tests)):
        case ProfileSelected(name, chosen):
            return name, chosen
        case NoProfileChosen() | ProfileRefused() as refused:
            raise refuse(reason(refused))


def echo(lines: Iterable[str]) -> None:
    """Each line on the terminal, in order."""
    for line in lines:
        typer.echo(line)
