"""The typer app, built around the controllers that bootstrap/ hands in."""
from collections.abc import Callable

import typer

from xarch.cli.commands import check, hook, profile, review, scaffold, where
from xarch.modules.review.application.controller import ReviewController
from xarch.modules.rules.application.controller import RulesController
from xarch.modules.scaffold.application.controller import ScaffoldController
from xarch.modules.spec.application.controller import SpecController


def build(rules: RulesController, scaffolding: ScaffoldController, spec: SpecController, reviewing: ReviewController,
          version: Callable[[], str | None]) -> typer.Typer:
    """The app, with version asked for xarch's version only when `--version` is given (None: it is not known)."""
    app = typer.Typer(help="Check and scaffold the architecture a profile describes.", no_args_is_help=True)

    def print_version(show: bool) -> None:
        if show:
            found = version()
            typer.echo(f"xarch {found}" if found is not None else "xarch (version unknown)")
            raise typer.Exit()

    @app.callback()
    def main(
        show_version: bool = typer.Option(
            False, "--version", callback=print_version, is_eager=True, metavar="", help="Print the version and exit."
        ),
    ) -> None:
        """Runs before any command; `--version` is handled by its callback."""

    check.register(app, rules, spec)
    scaffold.register(app, scaffolding, spec)
    where.register(app, rules, spec)
    profile.register(app, spec, rules)
    review.register(app, reviewing, spec)
    hook.register(app)
    return app
