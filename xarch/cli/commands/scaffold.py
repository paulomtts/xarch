"""xarch init and xarch new-module (scaffold module)."""
import typer

from xarch.cli.terminal import DEFAULT_APP, AppPath, ProfileName, fail, profile_for
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.scaffold.contract import Init, NewModule, Refused, Report, Scaffolded
from xarch.modules.spec.application.controller import SpecController


def _show(report: Report) -> None:
    for path in report.created:
        typer.echo(f"created {path.as_posix()}")
    for path in report.skipped:
        typer.echo(f"skipped {path.as_posix()}")


def register(app: typer.Typer, scaffold: ScaffoldController, spec: SpecController) -> None:
    @app.command()
    def init(app_path: AppPath = DEFAULT_APP, profile: ProfileName = None) -> None:
        """Create the top-level skeleton of the profile and the project docs beside it; never overwrites."""
        _show(scaffold.init(Init(app_path, profile_for(spec, app_path, profile))).report)

    @app.command("new-module")
    def new_module(name: str, app_path: AppPath = DEFAULT_APP, profile: ProfileName = None) -> None:
        """Create a module with its full skeleton."""
        match scaffold.new_module(NewModule(app_path, name, profile_for(spec, app_path, profile))):
            case Scaffolded(report):
                _show(report)
            case Refused(reason):
                raise fail(reason)
