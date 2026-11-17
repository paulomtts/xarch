from __future__ import annotations

from pathlib import Path

import typer
from app.cli.reports.check_report import check_text
from app.modules.rules.application.controller import RulesController
from app.modules.rules.contract import AppChecked, CheckApp


def register(app: typer.Typer, rules: RulesController) -> None:
    @app.command()
    def check(root: Path = typer.Argument(..., help="the app folder, given in full"),
              profile: str = typer.Option("cli", help="a bundled profile, or the path of one"),
              strict: bool = typer.Option(False, help="fail on weak findings too")) -> None:
        result = rules.check(CheckApp(root, profile, strict))
        typer.echo(check_text(result))
        clean = isinstance(result, AppChecked) and not result.violations and not result.cycles
        raise typer.Exit(0 if clean else 1)
