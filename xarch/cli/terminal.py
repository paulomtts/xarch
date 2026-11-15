"""What every command shares: the --app, --profile and --tests options, choosing the profile, and how a refusal
reaches the terminal."""
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Annotated

import typer

from xarch.kernel.errors import DomainError
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import NoProfileChosen, ProfileRefused, ProfileSelected, SelectProfile

AppPath = Annotated[Path | None, typer.Option(
    "--app", help="The app/ folder to work on. Default: \\[tool.xarch] app in pyproject.toml (`init` records it when it "
                  "is not app/), else app/ in the working folder.")]
DEFAULT_APP = Path("app")
ProfileName = Annotated[str | None, typer.Option(
    "--profile", help="The profile: the name of a bundled profile, or a path to a profile file (.yaml or .json). "
                      "Default: \\[tool.xarch] profile in pyproject.toml; with neither, the command fails.")]
TestsPath = Annotated[Path | None, typer.Option(
    "--tests", help="The tests folder to check. Default: \\[tool.xarch] tests in pyproject.toml, else tests/ beside "
                    "the app folder, if there is one.")]


def no_profile(known: Sequence[str]) -> str:
    """Why nothing can run without a profile, and how to choose one."""
    return ("no profile: pass --profile, or set `profile` under [tool.xarch] in pyproject.toml; "
            f"the profiles found are {', '.join(known)}")


def fail(message: str) -> typer.Exit:
    typer.echo(f"error: {message}", err=True)
    return typer.Exit(2)


def app_for(spec: SpecController, app_path: Path | None, refuse: Callable[[str], typer.Exit] = fail) -> Path:
    """The app folder to work on: the one given with --app, else the one the project around the working folder records
    under [tool.xarch], else app/. An unreadable setting is raised as what refuse makes of its reason."""
    if app_path is not None:
        return app_path
    try:
        configured = spec.configured_app(Path.cwd())
    except DomainError as e:
        raise refuse(e.reason)
    return configured if configured is not None else DEFAULT_APP


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
        case NoProfileChosen(known):
            raise refuse(no_profile(known))
        case ProfileRefused(reason):
            raise refuse(reason)
