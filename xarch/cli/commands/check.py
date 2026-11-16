"""xarch check: what the source says and which folders exist (rules module), as text or JSON."""
from pathlib import Path
from typing import Annotated

import typer

from xarch.cli.reports.refusal_report import cannot_run, not_a_directory
from xarch.cli.reports.report import check_lines, json_document
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
    rewrapped,
    selection,
)
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.contract import AppChecked, CheckApp, CheckRefused, ChecksCannotRun, NotADirectory
from xarch.modules.spec.application.controller import SpecController
from xarch.modules.spec.contract import Origin, ProfileRefused

StrictOption = Annotated[bool, typer.Option(
    "--strict", metavar="",
    help="Also fail (exit 1) on every finding the enforcement section lists under `strict` (JSON `strict_failures`): "
         "guards left off that the compared bundled profile switches on (every guard, when none is compared), "
         "ungoverned files, missing or changed init files, skipped tests, dynamic imports, checks met to the letter "
         "only (weak), approximate keys, checks of the profile's own that read nothing, and a part redefined without "
         "the litmus the compared profile gives it. Every other way a custom profile differs from the compared one "
         "is shown, never failed on.")]


def register(app: typer.Typer, rules: RulesController, spec: SpecController) -> None:
    @app.command()
    @rewrapped
    def check(app_path: AppPath = None, profile: ProfileName = None, tests: TestsPath = None,
              output: FormatOption = Format.text, strict: StrictOption = False) -> None:
        """Report every violation of the architecture in the app and its tests."""
        refuse = refusal(output)
        cwd = in_full(Path())
        app_path = app_for(spec, cwd, app_path, refuse)
        chosen, tests_root = selection(spec, app_path, profile, tests, refuse)
        match rules.check_app(CheckApp(app_path, chosen, cwd, tests_root, strict)):
            case NotADirectory(root):
                raise refuse(not_a_directory(root))
            case ChecksCannotRun(problems):
                raise refuse(cannot_run(problems))
            case CheckRefused(reason):
                raise refuse(reason)
            case AppChecked() as checked:
                origin = _origin(spec, chosen, refuse)
                echo([json_document(chosen, origin, checked, strict)] if output is Format.json
                     else check_lines(origin, checked, strict))
                if not checked.ok:
                    raise typer.Exit(1)


def _origin(spec: SpecController, chosen: str, refuse) -> Origin:
    """Where the profile in force comes from, which spec works out and the enforcement section shows first."""
    match spec.origin(chosen):
        case Origin() as origin:
            return origin
        case ProfileRefused(reason):
            raise refuse(reason)
