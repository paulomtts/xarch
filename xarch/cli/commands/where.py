"""xarch where: what a path is and what code there may do, before it is written (rules module)."""
from pathlib import Path
from typing import Annotated

import typer

from xarch.cli.reports.refusal_report import cannot_run
from xarch.cli.reports.where_report import where_document, where_lines
from xarch.cli.terminal import (
    AppPath,
    Format,
    FormatOption,
    ProfileName,
    TestsPath,
    app_for,
    echo,
    in_full,
    refusal,
    selection,
)
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.contract import CheckRefused, ChecksCannotRun, Locate, Located, Outside
from xarch.modules.spec.application.controller import SpecController

PathArgument = Annotated[Path, typer.Argument(
    help="A file or folder, there or not yet. It may be given from the current folder, from the folder holding the "
         "app folder (the project root), or from the app folder; what exists wins, else the app folder, then the "
         "tests folder, then the project root. Works for the app's paths and for the tests'.")]


def register(app: typer.Typer, rules: RulesController, spec: SpecController) -> None:
    @app.command()
    def where(path: PathArgument, app_path: AppPath = None, profile: ProfileName = None,
              tests: TestsPath = None, output: FormatOption = Format.text) -> None:
        """Say what a path is and what code there may do, before writing it: its part (or that it is in none), the
        part's role and litmus test, what it may import, the outside packages it may import, the names it may not
        use, the tier that tests it and where its test lives; for a test, its tier, the part it mirrors and what
        it may import. Exit 0 for any path in the project, 2 for one outside it or a profile that cannot be used."""
        refuse = refusal(output)
        cwd = in_full(Path())
        app_path = app_for(spec, cwd, app_path, refuse)
        chosen, tests_root = selection(spec, app_path, profile, tests, refuse)
        match rules.locate(Locate(path, cwd, app_path, chosen, tests_root)):
            case Outside(reason) | CheckRefused(reason):
                raise refuse(reason)
            case ChecksCannotRun(problems):
                raise refuse(cannot_run(problems))
            case Located(found):
                echo([where_document(chosen, found)] if output is Format.json else where_lines(found))
