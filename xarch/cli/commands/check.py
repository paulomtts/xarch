"""xarch check: import rules (rules module) and structure rules (layout module)."""
import typer

from xarch.cli.terminal import DEFAULT_APP, AppPath, ProfileName, fail, profile_for
from xarch.modules.layout.application.controller import LayoutController
from xarch.modules.layout.contract import CheckStructure
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.contract import CheckImports, ImportsChecked, NotADirectory
from xarch.modules.spec.application.controller import SpecController


def register(app: typer.Typer, rules: RulesController, layout: LayoutController, spec: SpecController) -> None:
    @app.command()
    def check(app_path: AppPath = DEFAULT_APP, profile: ProfileName = None) -> None:
        """Report import-rule and structure violations; extra folders and files are ignored."""
        chosen = profile_for(spec, app_path, profile)
        match rules.check(CheckImports(app_path, profile=chosen)):
            case NotADirectory(root):
                raise fail(f"{root} is not a directory")
            case ImportsChecked(violations):
                found = violations + layout.check(CheckStructure(app_path, profile=chosen)).violations
        for violation in found:
            typer.echo(violation)
        if not found:
            typer.echo("OK: no violations")
            return
        files = len({v.file for v in found})
        typer.echo(f"{len(found)} violation(s) in {files} file(s)")
        raise typer.Exit(1)
