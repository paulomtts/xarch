"""xarch review: an advisory reading of chosen files against the profile's words (review module), as text or JSON; exit
0 when it ran, 2 when it refused, 3 when some file judged has no answer, never 1. `xarch review calibrate` holds the
evals of the profile's own to their examples and records the verdicts: exit 0 when every one passed, 1 when one
failed (a defect of the profile), 2 when it refused, 3 when some example has no answer."""
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from xarch.cli.reports.eval_report import (
    calibration_document,
    calibration_lines,
    calibration_plan_document,
    calibration_plan_lines,
    shown_from,
    unknown_evals,
)
from xarch.cli.reports.review_report import (
    all_and_others,
    all_in_pieces,
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
    IMPORTS,
    MAX_FILES,
    MAX_PIECED,
    NO_CONTEXT,
    PIECE_CHARS,
    SHOWN,
    AllAndOthers,
    AllInPieces,
    Calibrate,
    Calibrated,
    CalibrationPlanned,
    KeyMissing,
    NothingChosen,
    Review,
    ReviewPlanned,
    ReviewReading,
    ReviewRefused,
    TooManyFiles,
    UnknownEvals,
)
from xarch.modules.spec.application.controller import SpecController

PathsArgument = Annotated[list[Path] | None, typer.Argument(
    show_default=False,
    help="Files to review, or folders for the files below them, given as `xarch where` takes a path; or `calibrate` "
         "alone, to hold the evals of the profile's own to their examples (a file named so is written ./calibrate).")]
EvalOption = Annotated[list[str] | None, typer.Option(
    "--eval", show_default=False, help="With calibrate: the eval of the profile's own to hold to its examples, by id; "
                                       "every one when left out. May be given more than once.")]
FilesFrom = Annotated[typer.FileText | None, typer.Option(
    "--files-from", help="A file listing the paths to review, one per line; `-` reads the list from stdin, such as "
                         "`git diff --name-only main | xarch review --files-from -`.")]
AllOption = Annotated[bool, typer.Option("--all", metavar="", help="Review every file of the app, and nothing else.")]
DryRun = Annotated[bool, typer.Option(
    "--dry-run", metavar="", help="Send nothing: show what would be sent, the masked text of each file and the "
                                  "question, and what it would cost.")]
MaxFiles = Annotated[int | None, typer.Option(
    "--max-files", min=1, show_default=False,
    help=f"How many files one run judges at most. Default: {MAX_FILES}, or {MAX_PIECED} with --pieces.")]
Pieces = Annotated[bool, typer.Option(
    "--pieces", metavar="", help=f"Also rank the pieces of each file judged (its functions and classes, a large class "
                                 f"as its methods), inside that file only: the lowest {SHOWN} of those of "
                                 f"{PIECE_CHARS:,} characters or more. Not with --all.")]


class _Context(str, Enum):
    none = NO_CONTEXT
    imports = IMPORTS


ContextOption = Annotated[_Context, typer.Option(
    "--context", help="What is sent before each piece: nothing, or the file's opening lines (those before its first "
                      "piece: for most files its docstring and imports). The numbers of the two never compare.")]
Offline = Annotated[bool, typer.Option(
    "--offline", metavar="", help="Send nothing, and read only the answers in the cache; a file whose answer is not "
                                  "there is unanswered, and the run exits 3. Needs no key.")]
CacheFolder = Annotated[Path | None, typer.Option(
    "--cache", help="The folder the answers are kept in. Default: .xarch/cache/review/ in the folder holding the app "
                    "folder, which the project commits.")]
INCOMPLETE = 3
"""The exit code of a review in which some file judged has no answer."""
FAILED_EXAMPLES = 1
"""The exit code of a calibration in which an eval failed its examples: a defect of the profile."""
CALIBRATE = Path("calibrate")
"""The path word that runs `xarch review calibrate`."""


def register(app: typer.Typer, reviewing: ReviewController, spec: SpecController) -> None:
    @app.command()
    @rewrapped
    def review(paths: PathsArgument = None, files_from: FilesFrom = None, every: AllOption = False,
               dry_run: DryRun = False, offline: Offline = False, cache: CacheFolder = None,
               app_path: AppPath = None, profile: ProfileName = None, tests: TestsPath = None,
               output: FormatOption = Format.text, max_files: MaxFiles = None, pieces: Pieces = False,
               context: ContextOption = _Context.none, evals: EvalOption = None) -> None:
        """Ask a decision model of chosen files where each belongs, by the litmus tests of the profile's parts, and
        show its reading, ranked: a file below its part's line reads as doubtful there. Advisory.

        It sends the masked text of each file judged whenever the decision model's key is set in the environment:
        the key alone allows it. --dry-run shows what would be sent, needing no key; --offline reads only the answers
        already kept. Never a check: it never changes what `xarch check` finds or its exit code. It reads only the
        files it is given: as paths, as a list with --files-from, or every file of the app with --all; with none, it
        refuses and names the ways. With --pieces it also ranks the pieces of each file, inside that file only. An eval
        of the profile's own runs once `xarch review calibrate` has held it to its examples. Exit 0 when it ran, 2 when
        it refused, 3 when some file or piece has no answer.

        `xarch review calibrate [--eval ID ...]` holds the evals of the profile's own to their examples, sending them
        as a review sends files, and records the verdicts in .xarch/calibration.json, which the project commits. Exit
        0 when every eval passed, 1 when one failed, 2 when it refused, 3 when some example has no answer."""
        refuse = refusal(output)
        cwd = in_full(Path())
        app_path = app_for(spec, cwd, app_path, refuse)
        chosen, tests_root = selection(spec, app_path, profile, tests, refuse)
        if paths and paths[0] == CALIBRATE:
            if paths[1:] or files_from is not None or every or pieces:
                raise refuse("calibrate takes no files: it holds the evals of the profile's own to their own examples")
            calibrate(Calibrate(cwd, app_path, chosen, tuple(evals or ()), dry_run, offline,
                                cwd / cache if cache is not None else None), output, cwd)
            return
        if evals:
            raise refuse("--eval names the evals calibrate holds to their examples: write `xarch review calibrate "
                         "--eval <id>`; a review asks every eval that may run")
        listed = tuple(Path(line.strip()) for line in files_from or () if line.strip())
        kept = cwd / cache if cache is not None else None
        match reviewing.review(Review(tuple(paths or ()), listed, every, cwd, app_path, chosen, tests_root, dry_run,
                                      max_files, offline, kept, pieces, context.value)):
            case NothingChosen():
                raise refuse(nothing_chosen())
            case AllAndOthers():
                raise refuse(all_and_others())
            case AllInPieces():
                raise refuse(all_in_pieces())
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

    def calibrate(cmd: Calibrate, output: Format, cwd: Path) -> None:
        refuse = refusal(output)
        match reviewing.calibrate(cmd):
            case UnknownEvals(names, known):
                raise refuse(unknown_evals(names, known))
            case KeyMissing(variable):
                raise refuse(no_key(variable))
            case ReviewRefused(reason):
                raise refuse(reason)
            case CalibrationPlanned() as planned:
                echo([calibration_plan_document(planned)] if output is Format.json else calibration_plan_lines(planned))
            case Calibrated() as done:
                record = shown_from(done.record, cwd) if done.record is not None else ""
                echo([calibration_document(done, record)] if output is Format.json else calibration_lines(done, record))
                if not done.complete:
                    raise typer.Exit(INCOMPLETE)
                if not done.passed:
                    raise typer.Exit(FAILED_EXAMPLES)
