"""xarch init and xarch new (scaffold module)."""
from typing import Annotated

import typer

from xarch.cli.reports.scaffold_report import report_lines
from xarch.cli.terminal import AppPath, ProfileName, app_for, fail, profile_for
from xarch.kernel.errors import DomainError
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.scaffold.contract import Init, New, Refused, Scaffolded
from xarch.modules.spec.application.controller import SpecController


def register(app: typer.Typer, scaffold: ScaffoldController, spec: SpecController) -> None:
    @app.command()
    def init(app_path: AppPath = None, profile: ProfileName = None) -> None:
        """Create the top-level skeleton, record the profile (and the app folder, when it is not app/) in pyproject.toml,
        write the docs and files; never overwrites."""
        app_path = app_for(spec, app_path)
        try:
            _echo(report_lines(scaffold.init(Init(app_path, profile_for(spec, app_path, profile))).report))
        except DomainError as e:
            raise fail(e.reason)

    @app.command()
    def new(kind: Annotated[str, typer.Argument(help="The word the profile calls one instance of its repeating folder.")],
            name: Annotated[str, typer.Argument(help="The name of the new folder.")],
            app_path: AppPath = None, profile: ProfileName = None) -> None:
        """Create one instance of the profile's repeating folder, named by its word, with its full skeleton."""
        app_path = app_for(spec, app_path)
        match scaffold.new(New(app_path, kind, name, profile_for(spec, app_path, profile))):
            case Scaffolded(report):
                _echo(report_lines(report))
            case Refused(reason):
                raise fail(reason)


def _echo(lines: list[str]) -> None:
    for line in lines:
        typer.echo(line)
