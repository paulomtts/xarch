"""xarch init and xarch new (scaffold module)."""
from pathlib import Path
from typing import Annotated

import typer

from xarch.cli.reports.scaffold_report import refused_reason, report_lines
from xarch.cli.terminal import AppPath, ProfileName, app_for, echo, fail, in_full, profile_for
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.scaffold.contract import InitProject, KindIsAFolder, NewInstance, NotInitialized, Refused, Scaffolded
from xarch.modules.spec.application.controller import SpecController


def register(app: typer.Typer, scaffold: ScaffoldController, spec: SpecController) -> None:
    @app.command()
    def init(app_path: AppPath = None, profile: ProfileName = None) -> None:
        """Create the top-level skeleton, record the profile (and the app folder, when it is not app/) in pyproject.toml,
        write the docs and files; never overwrites."""
        app_path = app_for(spec, app_path)
        match scaffold.init(InitProject(app_path, profile_for(spec, app_path, profile), in_full(Path()))):
            case Scaffolded(report):
                echo(report_lines(report))
            case Refused(reason):
                raise fail(reason)

    @app.command()
    def new(kind: Annotated[str, typer.Argument(help="The word the profile calls one instance of its repeating folder.")],
            name: Annotated[str, typer.Argument(help="The name of the new folder.")],
            app_path: AppPath = None, profile: ProfileName = None) -> None:
        """Create one instance of the profile's repeating folder, named by its word, with its full skeleton."""
        app_path = app_for(spec, app_path)
        match scaffold.new(NewInstance(app_path, kind, name, profile_for(spec, app_path, profile))):
            case Scaffolded(report):
                echo(report_lines(report))
            case KindIsAFolder() | NotInitialized() as refused:
                raise fail(refused_reason(refused))
            case Refused(reason):
                raise fail(reason)
