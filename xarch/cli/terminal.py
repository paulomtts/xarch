"""What every command shares: the --app, --profile and --tests options, choosing the profile, and how a refusal
reaches the terminal."""
from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer

from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import ProfileRefused, ProfileSelected, SelectProfile

AppPath = Annotated[Path, typer.Option("--app", help="The app/ folder to work on.")]
DEFAULT_APP = Path("app")
ProfileName = Annotated[str | None, typer.Option(
    "--profile", help="The profile: the name of a bundled profile, or a path to a profile file (.yaml or .json). "
                      "Default: \\[tool.xarch] profile in pyproject.toml; with neither, the command fails.")]
TestsPath = Annotated[Path | None, typer.Option(
    "--tests", help="The tests folder to check. Default: \\[tool.xarch] tests in pyproject.toml, else tests/ beside "
                    "the app folder, if there is one.")]


def fail(message: str) -> typer.Exit:
    typer.echo(f"error: {message}", err=True)
    return typer.Exit(2)


def profile_for(spec: SpecController, app_path: Path, override: str | None) -> str:
    return selection(spec, app_path, override, None)[0]


def selection(spec: SpecController, app_path: Path, override: str | None,
              tests: Path | None, refuse: Callable[[str], typer.Exit] = fail) -> tuple[str, Path | None]:
    """The architecture in force and the tests root to check: the chosen one, else tests/ beside the app folder
    when it exists, else None. A refusal is raised as what refuse makes of its reason."""
    match spec.select(SelectProfile(app_path, override, tests)):
        case ProfileSelected(name, chosen):
            if chosen is None and (app_path.absolute().parent / "tests").is_dir():
                chosen = app_path.absolute().parent / "tests"
            return name, chosen
        case ProfileRefused(reason):
            raise refuse(reason)
