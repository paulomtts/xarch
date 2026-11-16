"""xarch review: an advisory reading of chosen files against the profile's words (review module), as text or JSON; exit
0 when it ran, 2 when it refused, 3 when some file judged has no answer, never 1."""
from pathlib import Path
from typing import Annotated

import typer

from xarch.cli.reports.review_report import (
    all_and_others,
    no_key,
    nothing_chosen,
    plan_document,
    plan_lines,
    reading_document,
    reading_lines,
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
    KeyMissing,
    NothingChosen,
    Review,
    ReviewPlanned,
    ReviewReading,
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
Offline = Annotated[bool, typer.Option(
    "--offline", metavar="", help="Send nothing, and read only the answers in the cache; a file whose answer is not "
                                  "there is unanswered, and the run exits 3. Needs no key.")]
CacheFolder = Annotated[Path | None, typer.Option(
    "--cache", help="The folder the answers are kept in. Default: .xarch/cache/review/ in the folder holding the app "
                    "folder, which the project commits.")]
INCOMPLETE = 3
"""The exit code of a review in which some file judged has no answer."""


def register(app: typer.Typer, reviewing: ReviewController, spec: SpecController) -> None:
    @app.command()
    @rewrapped
    def review(paths: PathsArgument = None, files_from: FilesFrom = None, every: AllOption = False,
               dry_run: DryRun = False, offline: Offline = False, cache: CacheFolder = None,
               app_path: AppPath = None, profile: ProfileName = None, tests: TestsPath = None,
               output: FormatOption = Format.text, max_files: MaxFiles = MAX_FILES) -> None:
        """Ask a decision model of chosen files where each belongs, by the litmus tests of the profile's parts, and
        show its reading, ranked: a file below its part's line reads as doubtful there. Advisory.

        It sends the masked text of each file judged whenever the decision model's key is set in the environment:
        the key alone allows it. --dry-run shows what would be sent, needing no key; --offline reads only the answers
        already kept. Never a check: it never changes what `xarch check` finds or its exit code. It reads only the
        files it is given: as paths, as a list with --files-from, or every file of the app with --all; with none, it
        refuses and names the ways. Exit 0 when it ran, 2 when it refused, 3 when some file has no answer."""
        refuse = refusal(output)
        cwd = in_full(Path())
        app_path = app_for(spec, cwd, app_path, refuse)
        chosen, tests_root = selection(spec, app_path, profile, tests, refuse)
        listed = tuple(Path(line.strip()) for line in files_from or () if line.strip())
        kept = cwd / cache if cache is not None else None
        match reviewing.review(Review(tuple(paths or ()), listed, every, cwd, app_path, chosen, tests_root, dry_run,
                                      max_files, offline, kept)):
            case NothingChosen():
                raise refuse(nothing_chosen())
            case AllAndOthers():
                raise refuse(all_and_others())
            case TooManyFiles(found, cap):
                raise refuse(too_many(found, cap))
            case KeyMissing(variable):
                raise refuse(no_key(variable))
            case ReviewRefused(reason):
                raise refuse(reason)
            case ReviewPlanned() as planned:
                echo([plan_document(chosen, planned)] if output is Format.json else plan_lines(planned))
            case ReviewReading() as read:
                echo([reading_document(chosen, read)] if output is Format.json else reading_lines(read))
                if not read.complete:
                    raise typer.Exit(INCOMPLETE)
