"""xarch review: an advisory reading of chosen files against the profile's words (review module), as text or JSON."""
from pathlib import Path
from typing import Annotated

import typer

from xarch.cli.reports.review_report import (
    all_and_others,
    not_sendable,
    nothing_chosen,
    plan_document,
    plan_lines,
    too_many,
)
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
from xarch.modules.review.application.controller import ReviewController
from xarch.modules.review.contract import (
    MAX_FILES,
    AllAndOthers,
    NothingChosen,
    NotSendable,
    Review,
    ReviewPlanned,
    ReviewRefused,
    TooManyFiles,
)
from xarch.modules.spec.application.controller import SpecController

PathsArgument = Annotated[list[Path] | None, typer.Argument(
    show_default=False,
    help="Files to review, or folders for the files below them, given as `xarch where` takes a path.")]
FilesFrom = Annotated[typer.FileText | None, typer.Option(
    "--files-from", help="A file listing the paths to review, one per line; `-` reads the list from stdin, such as "
                         "`git diff --name-only main | xarch review --files-from -`.")]
AllOption = Annotated[bool, typer.Option("--all", metavar="", help="Review every file of the app, and nothing else.")]
DryRun = Annotated[bool, typer.Option(
    "--dry-run", metavar="", help="Send nothing: show what would be sent, the masked text of each file and the "
                                  "question, and what it would cost.")]
MaxFiles = Annotated[int, typer.Option("--max-files", min=1, help="How many files one run judges at most.")]


def register(app: typer.Typer, reviewing: ReviewController, spec: SpecController) -> None:
    @app.command()
    @rewrapped
    def review(paths: PathsArgument = None, files_from: FilesFrom = None, every: AllOption = False,
               dry_run: DryRun = False, app_path: AppPath = None, profile: ProfileName = None,
               tests: TestsPath = None, output: FormatOption = Format.text, max_files: MaxFiles = MAX_FILES) -> None:
        """Show what review would ask a decision model of chosen files: where each belongs, by the litmus tests of
        the profile's parts. Advisory; this version sends nothing, and runs only with --dry-run.

        Never a check: it never changes what `xarch check` finds or its exit code, and its own exit code is never 1.
        It reads only the files it is given: as paths, as a list with --files-from, or every file of the app with
        --all; with none, it refuses and names the ways. Exit 0 when it ran, 2 when it refused."""
        refuse = refusal(output)
        cwd = in_full(Path())
        app_path = app_for(spec, cwd, app_path, refuse)
        chosen, tests_root = selection(spec, app_path, profile, tests, refuse)
        listed = tuple(Path(line.strip()) for line in files_from or () if line.strip())
        match reviewing.review(Review(tuple(paths or ()), listed, every, cwd, app_path, chosen, tests_root, dry_run,
                                      max_files)):
            case NothingChosen():
                raise refuse(nothing_chosen())
            case AllAndOthers():
                raise refuse(all_and_others())
            case TooManyFiles(found, cap):
                raise refuse(too_many(found, cap))
            case NotSendable():
                raise refuse(not_sendable())
            case ReviewRefused(reason):
                raise refuse(reason)
            case ReviewPlanned() as planned:
                echo([plan_document(chosen, planned)] if output is Format.json else plan_lines(planned))
