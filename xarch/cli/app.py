"""The typer app, built around the controllers that bootstrap/ hands in."""
import typer

from xarch.cli.commands import check, profile, scaffold, where
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.spec.application.controller import SpecController


def build(rules: RulesController, scaffolding: ScaffoldController, spec: SpecController) -> typer.Typer:
    app = typer.Typer(help="Check and scaffold the architecture a profile describes.", no_args_is_help=True)
    check.register(app, rules, spec)
    scaffold.register(app, scaffolding, spec)
    where.register(app, rules, spec)
    profile.register(app, spec)
    return app
