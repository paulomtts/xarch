"""xarch check: what the source says (rules module) and which folders exist (layout module)."""
import typer

from xarch.cli.terminal import DEFAULT_APP, AppPath, ProfileName, TestsPath, fail, selection
from xarch.modules.layout.application.controller import LayoutController
from xarch.modules.layout.contract import CheckStructure
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.rules.contract import CheckImports, ImportsChecked, NotADirectory
from xarch.modules.spec.application.controller import SpecController


def register(app: typer.Typer, rules: RulesController, layout: LayoutController, spec: SpecController) -> None:
    @app.command()
    def check(app_path: AppPath = DEFAULT_APP, profile: ProfileName = None, tests: TestsPath = None) -> None:
        """Report every violation of the architecture in the app and its tests."""
        chosen, tests_root = selection(spec, app_path, profile, tests)
        package = app_path.absolute().resolve().name
        match rules.check(CheckImports(app_path, package, chosen, tests_root)):
            case NotADirectory(root):
                raise fail(f"{root} is not a directory")
            case ImportsChecked(violations):
                found = violations + layout.check(CheckStructure(app_path, package, chosen, tests_root)).violations
        for violation in found:
            typer.echo(violation)
        if not found:
            typer.echo("OK: no violations")
            return
        files = len({v.file for v in found})
        typer.echo(f"{len(found)} violation(s) in {files} file(s)")
        raise typer.Exit(1)
