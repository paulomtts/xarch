"""xarch check: what the source says (rules module) and which folders exist (layout module), as text or JSON."""
from enum import Enum
from typing import Annotated

import typer

from xarch.cli.report import enforcement_lines, json_document, json_error, passed, text_lines
from xarch.cli.terminal import DEFAULT_APP, AppPath, ProfileName, TestsPath, fail, selection
from xarch.modules.layout.application.controller import LayoutController
from xarch.modules.layout.contract import CheckStructure
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.contract import CheckImports, ImportsChecked, NotADirectory
from xarch.modules.spec.application.controller import SpecController


class Format(str, Enum):
    text = "text"
    json = "json"


FormatOption = Annotated[Format, typer.Option(
    "--format", help="text: one line per violation, then a summary (the default); json: one JSON document on stdout, "
                     "described in the README.")]


StrictOption = Annotated[bool, typer.Option(
    "--strict", help="Also fail (exit 1) on the findings of the enforcement section: guards a bundled profile switches "
                     "on but this one leaves off, ways a custom profile is looser, ungoverned files, missing or "
                     "changed init files, skipped tests, dynamic imports, and checks met to the letter only.")]


def _json_refusal(reason: str) -> typer.Exit:
    typer.echo(json_error(reason))
    return typer.Exit(2)


def register(app: typer.Typer, rules: RulesController, layout: LayoutController, spec: SpecController) -> None:
    @app.command()
    def check(app_path: AppPath = DEFAULT_APP, profile: ProfileName = None, tests: TestsPath = None,
              output: FormatOption = Format.text, strict: StrictOption = False) -> None:
        """Report every violation of the architecture in the app and its tests."""
        refuse = _json_refusal if output is Format.json else fail
        chosen, tests_root = selection(spec, app_path, profile, tests, refuse)
        package = app_path.absolute().resolve().name
        match rules.check(CheckImports(app_path, package, chosen, tests_root)):
            case NotADirectory(root):
                raise refuse(f"{root} is not a directory")
            case ImportsChecked(violations, enforcement):
                found = violations + layout.check(CheckStructure(app_path, package, chosen, tests_root)).violations
        if output is Format.json:
            typer.echo(json_document(chosen, found, enforcement, strict))
        else:
            for line in [*text_lines(found), *enforcement_lines(enforcement, strict)]:
                typer.echo(line)
        if not passed(found, enforcement, strict):
            raise typer.Exit(1)
