"""xarch init and xarch new (scaffold module)."""
from typing import Annotated

import typer

from xarch.cli.terminal import DEFAULT_APP, AppPath, ProfileName, fail, profile_for
from xarch.kernel.errors import DomainError
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.scaffold.contract import Init, New, Refused, Report, Scaffolded
from xarch.modules.spec.application.controller import SpecController


def _show(report: Report) -> None:
    for path in report.created:
        typer.echo(f"created {path.as_posix()}")
    for path in report.updated:
        typer.echo(f"updated {path.as_posix()}")
    for path in report.skipped:
        typer.echo(f"skipped {path.as_posix()}")


def register(app: typer.Typer, scaffold: ScaffoldController, spec: SpecController) -> None:
    @app.command()
    def init(app_path: AppPath = DEFAULT_APP, profile: ProfileName = None) -> None:
        """Create the top-level skeleton, record the profile in pyproject.toml, write the docs and files; never overwrites."""
        try:
            _show(scaffold.init(Init(app_path, profile_for(spec, app_path, profile))).report)
        except DomainError as e:
            raise fail(e.reason)

    @app.command()
    def new(kind: Annotated[str, typer.Argument(help="A folder of the layout that declares `each:`, by its path.")],
            name: Annotated[str, typer.Argument(help="The name of the new folder.")],
            app_path: AppPath = DEFAULT_APP, profile: ProfileName = None) -> None:
        """Create one folder of a kind (a layout folder that declares `each:`) with its full skeleton."""
        match scaffold.new(New(app_path, kind, name, profile_for(spec, app_path, profile))):
            case Scaffolded(report):
                _show(report)
            case Refused(reason):
                raise fail(reason)
