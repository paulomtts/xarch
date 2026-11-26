"""xarch baseline: records the violations a whole check finds now in .xarch/baseline.json beside the app, which `check`
then holds back, so that a project adopting xarch is told only of new ones; the record may only go down."""
from pathlib import Path
from typing import Annotated

import typer

from xarch.cli.reports.document import document
from xarch.cli.reports.refusal_report import cannot_run, not_a_directory
from xarch.cli.reports.report import baseline_written
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
from xarch.modules.rules.contract import BaselineWritten, CheckRefused, ChecksCannotRun, NotADirectory, WriteBaseline
from xarch.modules.spec.application.controller import SpecController

ResetOption = Annotated[bool, typer.Option(
    "--reset", metavar="",
    help="Write the record afresh from every violation found now, raising it where it is lower; without it, an "
         "existing record is only lowered (a finding no longer found dropped, a count lowered), never raised.")]


def register(app: typer.Typer, rules: RulesController, spec: SpecController) -> None:
    baseline = typer.Typer(help="Record the violations found now, which check then holds back; the record may only go "
                                "down.", no_args_is_help=True)
    app.add_typer(baseline, name="baseline")

    @baseline.command()
    @rewrapped
    def write(app_path: AppPath = None, profile: ProfileName = None, tests: TestsPath = None,
              output: FormatOption = Format.text, reset: ResetOption = False) -> None:
        """Record in .xarch/baseline.json, beside the app, the violations a whole check finds now: with no record,
        every one; with one, the record lowered to what is found (never raised, unless --reset). Commit it: check then
        reports only the violations it does not hold, and says when it can be lowered."""
        refuse = refusal(output)
        cwd = in_full(Path())
        app_path = app_for(spec, cwd, app_path, refuse)
        chosen, tests_root = selection(spec, app_path, profile, tests, refuse)
        match rules.write_baseline(WriteBaseline(app_path, chosen, cwd, tests_root, reset)):
            case NotADirectory(root):
                raise refuse(not_a_directory(root, cwd))
            case ChecksCannotRun(problems):
                raise refuse(cannot_run(problems))
            case CheckRefused(reason):
                raise refuse(reason)
            case BaselineWritten() as written:
                echo([document({"ok": True, "file": written.file, "recorded": written.recorded,
                                "before": written.before, "reset": written.reset})] if output is Format.json
                     else [baseline_written(written)])
