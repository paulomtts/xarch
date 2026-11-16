"""xarch init and xarch new (scaffold module)."""
from pathlib import Path
from typing import Annotated

import typer

from xarch.cli.reports.scaffold_report import refused_reason, report_lines
from xarch.cli.terminal import AppPath, ProfileName, app_for, echo, fail, in_full, profile_for, rewrapped
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.scaffold.contract import (
    InitProject,
    InstanceExists,
    KindIsAFolder,
    NewInstance,
    NotInitialized,
    Refused,
    Scaffolded,
)
from xarch.modules.spec.application.controller import SpecController


def register(app: typer.Typer, scaffold: ScaffoldController, spec: SpecController) -> None:
    @app.command()
    @rewrapped
    def init(app_path: AppPath = None, profile: ProfileName = None) -> None:
        """Create the project's top-level skeleton, docs and files from a profile; never overwrites.

        It also records the profile (and the app folder, when it is not app/) in pyproject.toml."""
        cwd = in_full(Path())
        app_path = app_for(spec, cwd, app_path)
        match scaffold.init(InitProject(app_path, profile_for(spec, app_path, profile), cwd)):
            case Scaffolded(report):
                echo(report_lines(report, cwd))
            case Refused(reason):
                raise fail(reason)

    @app.command()
    @rewrapped
    def new(kind: Annotated[str, typer.Argument(help="The word the profile calls one instance of its repeating folder.")],
            name: Annotated[str, typer.Argument(help="The name of the new folder.")],
            app_path: AppPath = None, profile: ProfileName = None) -> None:
        """Create one instance of the profile's repeating folder, named by its word, with its full skeleton."""
        cwd = in_full(Path())
        app_path = app_for(spec, cwd, app_path)
        match scaffold.new(NewInstance(app_path, kind, name, profile_for(spec, app_path, profile))):
            case Scaffolded(report):
                echo(report_lines(report, cwd))
            case KindIsAFolder() | NotInitialized() | InstanceExists() as refused:
                raise fail(refused_reason(refused, cwd))
            case Refused(reason):
                raise fail(reason)
