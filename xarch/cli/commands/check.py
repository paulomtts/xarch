"""xarch check: what the source says and which folders exist (rules module), as text or JSON."""
from pathlib import Path
from typing import Annotated

import typer

from xarch.cli.reports.report import enforcement_lines, json_document, text_lines
from xarch.cli.terminal import (
    AppPath,
    Format,
    FormatOption,
    ProfileName,
    TestsPath,
    app_for,
    cannot_run,
    in_full,
    refusal,
    selection,
)
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.contract import AppChecked, CheckApp, ChecksCannotRun, NotADirectory
from xarch.modules.spec.application.controller import SpecController

StrictOption = Annotated[bool, typer.Option(
    "--strict", help="Also fail (exit 1) on what the profile in force leaves unenforced, in the findings of the "
                     "enforcement section: guards a bundled profile switches on but this one leaves off, ungoverned "
                     "files, missing or changed init files, skipped tests, dynamic imports, and checks met to the "
                     "letter only. How a custom profile differs from the closest bundled one is shown, never failed "
                     "on.")]


def register(app: typer.Typer, rules: RulesController, spec: SpecController) -> None:
    @app.command()
    def check(app_path: AppPath = None, profile: ProfileName = None, tests: TestsPath = None,
              output: FormatOption = Format.text, strict: StrictOption = False) -> None:
        """Report every violation of the architecture in the app and its tests."""
        refuse = refusal(output)
        app_path = app_for(spec, app_path, refuse)
        chosen, tests_root = selection(spec, app_path, profile, tests, refuse)
        match rules.check_app(CheckApp(app_path, chosen, in_full(Path()), tests_root, strict)):
            case NotADirectory(root):
                raise refuse(f"{root} is not a directory")
            case ChecksCannotRun(problems):
                raise refuse(cannot_run(problems))
            case AppChecked() as checked:
                if output is Format.json:
                    typer.echo(json_document(chosen, checked, strict))
                else:
                    for line in [*text_lines(checked.violations, checked.hints),
                                 *enforcement_lines(checked.enforcement, strict, checked.hints)]:
                        typer.echo(line)
                if not checked.ok:
                    raise typer.Exit(1)
